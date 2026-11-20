"""Pass T: one fresh load of the recorded page, watched with no input
(2.C spec section 2; shared by 2.A, 2.B, 2.C and 2.D).

Records facts only: frames and the regions whose pixels changed, what each
region's content did (its text, image sources and rendered children at three
reads), DOM changes with their targets and the live region around each,
timers, Web Audio use, animations, media state per frame, dialogs, focus
moves with no key pressed, and polls in the HAR. Which test applies, and its
outcome, is each 2.x check's rules.

Pass T takes an opener (`OpenPage`): a fresh replay load with
`MOTION_INIT_JS` added before page scripts (plan Q7). Which browser that
load runs in is the pipeline's choice (plan Q1 and Q11), not this module's.

This module holds the watch itself (pass_t, _watch, the changed-tile maths)
and the clock check. Beside it: `motion_init.js` (the page script the watch
reads), `motion_models.py` (the facts it records), `motion_media.py` (sound
and animated images decoded from the recording) and `motion_pictures.py`
(crops and states of the regions that moved).

Verified behavior this module depends on (plan "Verified" items; tests in
tests/test_motion.py):
  * Pixel differences classify motion; DOM signals do not (item 6). Tiles
    map to elements by overlap, not by their centre.
  * Timer hooks run before page scripts and see periods longer than the
    watch (item 7).
  * The replay answers every repeat of a request with its first recorded
    response, so polling shows only in the HAR (item 10).
"""

from __future__ import annotations

import asyncio
import io
import json
import re
import statistics
import time
import zipfile
from collections.abc import Awaitable, Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops
from playwright.async_api import BrowserContext, Frame, Page

from tobi508 import count as inventory
from tobi508.browser import AUTOPLAY_ARG, MOTION_BROWSER  # noqa: F401
from tobi508.jslib import JSLIB
from tobi508.motion_media import _loudness, _read_images
from tobi508.motion_models import (
    WATCH_S,
    Animation,
    Change,
    Dialog,
    Element,
    FocusMove,
    LiveRegion,
    Media,
    MotionPass,
    Poll,
    Region,
    Timer,
    TimerCheck,
)
from tobi508.motion_pictures import _crops, _states
from tobi508.observe import DIALOGS_JS
from tobi508.redact import safe_error
from tobi508.site import UNITS_FN
from tobi508.traverse import PATH_JS, screenshot

# Frames alternate 0.35 s and 0.45 s apart (0.4 s on average): at a steady
# 0.5 s, a blink of 0.5 s per state was seen in the same state every frame.
FRAME_STEPS = (0.35, 0.45)
FRAME_S = sum(FRAME_STEPS) / len(FRAME_STEPS)
READS_AT = (0.0, 3.5, 6.5)
TILE = 20
# Bounds that keep one pass small on a busy page; reaching one is recorded.
MAX_COMPONENTS = 30  # changed-tile groups mapped per frame
MAX_REGIONS = 40
MAX_BOXES = 400  # changed-pixel boxes kept per region
FAST_KEPT = 300  # 3.A's fast callbacks kept per frame
# A frame where more than this share of the viewport's tiles changed is a
# page-wide change (a dialog's backdrop, a scroll), noted and not mapped.
PAGE_CHANGE = 0.5


OpenPage = Callable[[], Awaitable[tuple[BrowserContext, Page]]]

# ANDI 29.2.2's live regions (sandi.js): aria-live polite or assertive, and
# roles alert, status, log, marquee and timer (2.D spec, Terms). An element
# whose aria-live is anything else (off) is not one.
LIVE_SELECTOR = (
    "[aria-live],[role=alert],[role=status],[role=log],[role=marquee],[role=timer]"
)
# Carousel containers (2.C spec, Terms): the content is the whole carousel.
CAROUSEL_SELECTOR = (
    "[aria-roledescription~=carousel i],.slick-slider,.splide,.swiper,"
    ".carousel,.glide,.flickity-enabled"
)


def _js(name: str) -> str:
    """A script kept in a .js file beside this module, read once at import.
    Each file is the body of a function this module wraps (see where it is
    used), not a script that runs on its own."""
    return (Path(__file__).parent / name).read_text("utf-8").removesuffix("\n")


# Runs in every frame before page scripts, after traverse.INIT_JS. The body,
# about 470 lines of JavaScript, is in motion_init.js: it records DOM changes,
# timers, Web Audio, media, dialogs and focus moves, and answers pass T's reads
# (window.__a11yMotion).
MOTION_INIT_JS = (
    ("(() => {" + JSLIB + PATH_JS + _js("motion_init.js"))
    .replace("LIVE_SELECTOR", json.dumps(LIVE_SELECTOR))
    .replace("CAROUSEL_SELECTOR", json.dumps(CAROUSEL_SELECTOR))
)


# Elements (2.C Terms, plan Q6): what a screen reader reads
# as one unit, in reading order. site.UNITS_FN's units (as 9.A-9.C and 19.A
# read them), with three rules of its own: a label on the same line as its
# control is one element with it, content inside aria-hidden="true" is not an
# element, and an iframe's content is read in its own frame and counted at
# the iframe's place (pass_t splices it in). Images without alt text are
# already skipped by UNITS_FN; each table cell's own text is its own unit.
# The function's body is in motion_elements.js.
ELEMENTS_CAP = 600
ELEMENTS_JS = "(cap) => {" + UNITS_FN + _js("motion_elements.js")


async def read_elements(page: Page) -> tuple[list[Element], bool, dict]:
    """Elements of every frame, inline at each iframe's place. Returns the
    elements, whether a cap cut them short, and (frame index, local index)
    -> element index, for `inside`."""
    out: list[Element] = []
    where: dict[tuple[int, int], int] = {}
    truncated = False

    async def visit(frame: Frame, depth: int) -> None:
        nonlocal truncated
        try:
            got = await frame.evaluate(ELEMENTS_JS, ELEMENTS_CAP)
        except Exception:
            truncated = True
            return
        truncated = truncated or got["truncated"]
        index = page.frames.index(frame) if frame in page.frames else -1
        for j, u in enumerate(got["elements"]):
            if u["kind"] == "frame":
                child = None
                if depth < 3:
                    try:
                        h = await frame.query_selector(u["css"])
                        child = await h.content_frame() if h else None
                    except Exception:
                        child = None
                if child is not None:
                    await visit(child, depth + 1)
                else:
                    truncated = True  # a frame not read: its content is missing
                continue
            if len(out) >= ELEMENTS_CAP:
                truncated = True
                return
            where[(index, j)] = len(out)
            out.append(
                Element(
                    i=len(out), frame=index, frame_url=frame.url if index else "", **u
                )
            )

    await visit(page.main_frame, 0)
    return out, truncated, where


_DIALOG_FACTS_JS = (
    "(css) => {"
    + JSLIB
    + """
  const d = J.find(css);
  if (!d) return null;
  const f = 'a[href], button, input:not([type=hidden]), select, textarea, [tabindex]:not([tabindex^="-"])';
  return { role: d.getAttribute('role') || (d.tagName === 'DIALOG' ? 'dialog' : ''),
    text: (d.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 300),
    keyboard: d.contains(J.active()) || !!d.querySelector(f) };
}"""
)


# A video player from another site that streams its video: no recording can
# play it (2.A, 2.B and 3.A all say NEEDS REVIEW, spec A1, A2 or A3). One
# pattern for all three so one test cannot say "nothing moved" while another
# says "could not play". `STREAMING_AUTOPLAY` is the player told to start on
# its own (2.A and 2.B ask about what plays by itself); 3.A looks at any.
STREAMING_PLAYER = re.compile(
    r"^https?://(www\.)?(youtube(-nocookie)?\.com/embed|player\.vimeo\.com)/",
    re.IGNORECASE,
)
STREAMING_AUTOPLAY = re.compile(
    STREAMING_PLAYER.pattern + r".*autoplay=1", re.IGNORECASE
)
STREAMING_WHY = "it is a streaming video player that we cannot play from a recording"


def streaming_players(mp: "MotionPass", autoplay_only: bool = True) -> list[str]:
    """Sources of the page's streaming video players (iframes, every frame)."""
    pat = STREAMING_AUTOPLAY if autoplay_only else STREAMING_PLAYER
    return [src for src in mp.iframes if pat.match(src)]


def changed_tiles(
    a: Image.Image, b: Image.Image, tile: int = TILE
) -> dict[tuple[int, int], list[int]]:
    """(column, row) of every tile with any pixel different between frames,
    with the bounding box of its changed pixels (x0, y0, x1, y1, viewport
    pixels)."""
    diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v else 0)
    if diff.getbbox() is None:
        return {}
    w, h = diff.size
    cols, rows = -(-w // tile), -(-h // tile)
    # Pad to whole tiles, then a box reduce: any changed pixel makes the
    # tile's mean non-zero.
    padded = Image.new("L", (cols * tile, rows * tile))
    padded.paste(diff, (0, 0))
    px = padded.reduce(tile).load()
    out: dict[tuple[int, int], list[int]] = {}
    for y in range(rows):
        for x in range(cols):
            if px[x, y]:
                x0, y0 = x * tile, y * tile
                bb = padded.crop((x0, y0, x0 + tile, y0 + tile)).getbbox()
                if bb:
                    out[(x, y)] = [x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3]]
    return out


def components(tiles: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
    """Tiles that touch one another (8 neighbours), largest first."""
    left, out = set(tiles), []
    while left:
        start = left.pop()
        group, todo = {start}, [start]
        while todo:
            x, y = todo.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in left:
                        left.remove(n)
                        group.add(n)
                        todo.append(n)
        out.append(group)
    return sorted(out, key=len, reverse=True)


def polls_in_har(har: Path) -> list[Poll]:
    """GET requests repeated to one address, media and byte ranges excluded
    (a video fetched in ranges is not polling)."""
    try:
        with zipfile.ZipFile(har) as z:
            name = next(n for n in z.namelist() if n.endswith(".har"))
            entries = json.loads(z.read(name))["log"]["entries"]
    except Exception:
        return []
    seen: dict[str, list[str]] = {}
    for e in entries:
        req, res = e.get("request", {}), e.get("response", {})
        if req.get("method") != "GET":
            continue
        headers = {h.get("name", "").lower() for h in req.get("headers", [])}
        if "range" in headers:
            continue
        mime = (res.get("content", {}).get("mimeType") or "").lower()
        if mime.startswith(("image/", "font/", "video/", "audio/", "text/css")):
            continue
        seen.setdefault(req.get("url", ""), []).append(e.get("startedDateTime", ""))
    out = []
    for url, times in seen.items():
        if len(times) < 2 or not url:
            continue
        gap = None
        try:
            ts = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times)
            gaps = [(b - a).total_seconds() * 1000 for a, b in zip(ts, ts[1:])]
            gap = round(statistics.median(gaps)) if gaps else None
        except ValueError:
            pass
        out.append(Poll(url=url[:500], count=len(times), gap_ms=gap))
    return sorted(out, key=lambda p: -p.count)[:20]


async def _each_frame(page: Page, js: str, *args: Any) -> list[tuple[int, Frame, Any]]:
    out = []
    for i, frame in enumerate(page.frames):
        try:
            out.append((i, frame, await frame.evaluate(js, *args)))
        except Exception:
            continue
    return out


async def _map(frame: Frame, boxes: list[list[int]], depth: int = 0):
    """Regions for one tile group: a list of (Frame, info), where info["idx"]
    lists the group's boxes in that region. Follows iframes."""
    try:
        got = await frame.evaluate(
            "(b) => window.__a11yMotion ? window.__a11yMotion.regionsAt(b) : null",
            boxes,
        )
    except Exception:
        return []
    out = []
    for item in got or []:
        if "frame" not in item:
            out.append((frame, item))
            continue
        if depth >= 3:
            continue
        try:
            handles = await frame.query_selector_all("iframe, frame")
            child = await handles[item["frame"]].content_frame()
        except Exception:
            child = None
        if child is None:
            continue
        dx, dy = item["dx"], item["dy"]
        sub = [boxes[i] for i in item["idx"]]
        moved = [[b[0] - dx, b[1] - dy, b[2] - dx, b[3] - dy] for b in sub]
        for f, info in await _map(child, moved, depth + 1):
            info["idx"] = [item["idx"][i] for i in info["idx"]]
            out.append((f, info))
    return out


def _kinds(r: Region) -> list[str]:
    seen = [s for s in r.sigs]
    updated = len({s for s in seen if s is not None}) > 1 or (
        any(s is None for s in seen) and any(s is not None for s in seen)
    )
    r.updated = updated or any(c.kind in ("text", "children", "src") for c in r.changes)
    kinds = []
    if r.updated:
        kinds.append("updating")
    if (not r.updated and r.changed_at) or r.children_moved:
        kinds.append("moving")
    return kinds


async def pass_t(
    open_page: OpenPage,
    har: Path | None = None,
    shots: Path | None = None,
    rel: Path | None = None,
    watch_s: float = WATCH_S,
    scroll_to: str | None = None,
    prefix: str = "2t",
) -> MotionPass:
    """Watch one fresh load for `watch_s` with no input. Never raises: a load
    or read that fails gives `ok=False` with the reason (2.C A1).
    `scroll_to`: the scrolled watch (plan Q3), with that element scrolled
    into view first; `prefix` names its frames."""
    out = MotionPass(watch_s=watch_s)
    if har is not None:
        out.polls = polls_in_har(har)
    try:
        context, page = await open_page()
    except Exception as exc:
        out.ok, out.error = False, f"the page could not be loaded: {safe_error(exc)}"
        return out
    try:
        if scroll_to:
            await page.evaluate(
                "(css) => {"
                + JSLIB
                + " const e = J.find(css); if (e) e.scrollIntoView({ block: 'center' }); }",
                scroll_to,
            )
            await page.wait_for_timeout(300)
        await _watch(page, out, shots, rel, watch_s, har, prefix)
        if shots is not None:
            try:
                await _crops(page, out, shots, rel, prefix, every=bool(scroll_to))
            except Exception:
                pass  # evidence for a question only; the frames still stand
        if har is not None:
            from tobi508.capture import media_index

            out.media_store = media_index(har)
            await _loudness(context, har, out)
            if not scroll_to:
                try:
                    await _late_images(page, har, out)
                except Exception:
                    pass  # images left unread: guard CN holds 2.B and 3.A
    except Exception as exc:  # recorded, never raised (A1)
        out.ok, out.error = False, f"the page could not be read: {safe_error(exc)}"
    finally:
        await context.close()
    return out


async def _watch(
    page: Page,
    out: MotionPass,
    shots: Path | None,
    rel: Path | None,
    watch_s: float,
    har: Path | None = None,
    prefix: str = "2t",
) -> None:
    out.elements, out.elements_truncated, where = await read_elements(page)
    starts = await _each_frame(
        page, "() => window.__a11yMotion ? window.__a11yMotion.mark0() : null"
    )
    top = next((v for i, _, v in starts if i == 0 and v), None)
    if top is None:
        raise RuntimeError("pass T's hook did not run")
    t0_epoch = top["t0"]
    out.frames_read = sum(1 for _, _, v in starts if v)
    for i, _, v in starts:
        for lr in (v or {}).get("live", []):
            out.live_regions.append(LiveRegion(frame=i, **lr))
        out.carousels += [f"{i}|{c}" for c in (v or {}).get("carousels", [])]
    try:
        out.dialogs_at_start = sorted(
            {d["css"] for d in await page.evaluate(DIALOGS_JS)}
        )
    except Exception:
        pass
    asked: dict[str, list[float]] = {}

    def on_request(req) -> None:
        try:
            if req.method == "GET" and req.resource_type in (
                "fetch",
                "xhr",
                "eventsource",
            ):
                asked.setdefault(req.url, []).append(time.monotonic())
        except Exception:
            pass

    page.on("request", on_request)
    vp = page.viewport_size or {}
    out.viewport = [vp.get("width", 0), vp.get("height", 0)]
    if shots is not None:
        shots.mkdir(parents=True, exist_ok=True)

    regions: dict[str, Region] = {}
    frames_by_key: dict[str, Frame] = {}
    pairs: list[tuple[float, dict[tuple[int, int], list[int]]]] = []
    pngs: list[bytes] = []  # every frame, for each region's states
    reads = list(READS_AT[:-1]) + [watch_s]
    start = time.monotonic()
    prev: Image.Image | None = None
    n = 0
    while True:
        t = time.monotonic() - start
        if reads and t >= reads[0] - 0.05:
            reads.pop(0)
            await _each_frame(
                page, "() => window.__a11yMotion ? window.__a11yMotion.snap() : null"
            )
            out.reads.append(round(time.monotonic() - start, 2))
            for i, fr, media in await _each_frame(
                page, "() => window.__a11yMotion ? window.__a11yMotion.media() : []"
            ):
                at = round(time.monotonic() - start, 2)
                url = fr.url[:500] if i else ""
                out.media += [
                    Media(frame=i, frame_url=url, at=at, **m) for m in media or []
                ]
        shot_t = round(time.monotonic() - start, 2)
        png = await screenshot(page)
        img = Image.open(io.BytesIO(png)).convert("RGB")
        out.frames.append(shot_t)
        if shots is not None:
            path = shots / f"{prefix}-{n:02d}.png"
            path.write_bytes(png)
            out.shots.append(str(path.relative_to(rel)) if rel else str(path))
        if prev is not None and prev.size == img.size:
            pairs.append((shot_t, changed_tiles(prev, img)))
        pngs.append(png)
        prev = img
        n += 1
        if time.monotonic() - start >= watch_s and not reads:
            break
        step = FRAME_STEPS[n % len(FRAME_STEPS)]
        wait = step - (time.monotonic() - start - shot_t)
        if wait > 0:
            await asyncio.sleep(wait)

    page.remove_listener("request", on_request)
    for url, times in asked.items():
        if len(times) >= 2:
            gaps = [b - a for a, b in zip(times, times[1:])]
            out.polls.append(
                Poll(
                    url=url[:500],
                    count=len(times),
                    gap_ms=round(statistics.median(gaps) * 1000),
                    source="watch",
                )
            )
    await _regions(page, pairs, regions, frames_by_key, out)
    long_images = await _long_images(page, har, out) if har is not None else {}
    await _extras(page, regions, frames_by_key, long_images)
    for key, r in regions.items():
        frame = frames_by_key[key]
        try:
            d = await frame.evaluate(
                "(css) => window.__a11yMotion ? window.__a11yMotion.describe(css) : null",
                r.css,
            )
        except Exception:
            d = None
        if not d:
            continue
        epoch0 = t0_epoch
        r.live_off = bool(d.get("live_off"))
        r.sigs = d["sigs"]
        r.colors = d["colors"]
        r.transforms = d["transforms"]
        r.children_moved = bool(d["moved"])
        r.text = d["text"]
        r.connected = d["connected"]
        r.attr_changes = d["attrs"]
        r.attr_list = [
            Change(**{**c, "t": round((c.pop("at") - epoch0) / 1000, 2)})
            for c in d["attr_list"]
        ]
        r.focus_in = [round((t - epoch0) / 1000, 2) for t in d["focus_in"]]
        r.changes = [
            Change(**{**c, "t": round((c.pop("at") - epoch0) / 1000, 2)})
            for c in d["changes"]
        ]
        r.animations = [Animation(**a) for a in d["anims"]]
        gaps = [b - a for a, b in zip(r.changed_at, r.changed_at[1:])]
        r.period_s = round(statistics.median(gaps), 2) if gaps else None
        r.kinds = _kinds(r)
        if r.source not in ("pixels", "dom") and "moving" not in r.kinds:
            r.kinds.append("moving")
        try:
            got = await frame.evaluate(
                "(css) => window.__a11yMotion ? window.__a11yMotion.inside(css) : null",
                r.css,
            )
        except Exception:
            got = None
        local = (got or {}).get("inside", [])
        r.elements = sorted(where[(r.frame, j)] for j in local if (r.frame, j) in where)
        nxt = (got or {}).get("next")
        if not r.elements and nxt is not None:
            here = sorted(i for (f, j), i in where.items() if f == r.frame and j >= nxt)
            r.next_element = here[0] if here else len(out.elements)
    _states(pngs, regions)
    known = [r.css for r in regions.values() if r.frame == 0]
    try:
        out.below = await page.evaluate(
            "(k) => window.__a11yMotion ? window.__a11yMotion.below(k) : []", known
        )
    except Exception:
        out.below = []
    out.regions = sorted(regions.values(), key=lambda r: (r.box[1:2], r.box[0:1]))

    try:
        got = await inventory.played(page)
    except Exception:
        got = None
    if got is not None:
        out.played, out.played_listed = got
    for i, _, facts in await _each_frame(
        page, "() => window.__a11yMotion ? window.__a11yMotion.facts() : null"
    ):
        if not facts:
            continue
        out.audio_connects += facts["audio"]
        out.blink_markup = out.blink_markup or bool(facts.get("blink"))
        out.audio_states += facts.get("audio_states", [])
        out.iframes += facts.get("iframes", [])
        out.dropped_changes += facts["dropped"]
        for f in facts.get("fast", [])[:FAST_KEPT]:
            out.fast_callbacks.append(
                {
                    "frame": i,
                    "t": round((f["at"] - t0_epoch) / 1000, 3),
                    "kind": f["kind"],
                }
            )
        out.fast_animations += [{"frame": i, **a} for a in facts.get("fast_anims", [])]
        counts: dict[tuple[str, int], int] = {}
        for tm in facts["timers"]:
            counts[(tm["kind"], tm["ms"])] = counts.get((tm["kind"], tm["ms"]), 0) + 1
        out.timers += [
            Timer(frame=i, kind=k, ms=ms, count=c)
            for (k, ms), c in sorted(counts.items())
        ]
    try:
        now_dialogs = await page.evaluate(DIALOGS_JS)
        for d in now_dialogs:
            if d["css"] in out.dialogs_at_start:
                continue
            facts = await page.evaluate(_DIALOG_FACTS_JS, d["css"]) or {}
            out.dialogs_opened.append(Dialog(css=d["css"], name=d["name"], **facts))
    except Exception:
        pass
    try:
        fl = await page.evaluate(
            "() => ({ f: window.__a11yLog ? window.__a11yLog.f : [], origin: performance.timeOrigin })"
        )
        for e in fl["f"]:
            at = (fl["origin"] + e["t"] - t0_epoch) / 1000
            if at >= 0 and e["type"] == "focusin":
                out.focus_moves.append(FocusMove(t=round(at, 2), css=e.get("css")))
    except Exception:
        pass


async def _page_images(page) -> list[str]:
    srcs: list[str] = []
    for _, _, got in await _each_frame(
        page, "() => window.__a11yMotion ? window.__a11yMotion.images() : []"
    ):
        srcs += [s for s in got or [] if s not in srcs]
    return srcs


async def _long_images(page, har: Path, out: MotionPass) -> dict[str, str]:
    """Animated images on the page at the end of the watch that play for
    more than 5 s in all (G152), by URL. Recorded in `out.animated_images`."""
    return await _read_images(page, har, out, await _page_images(page))


# The late read's scroll: one window at a time, jumping (a page with smooth
# scrolling did not move before the next read, so the recorder's own scroll
# stopped after one step on round 2's home page), then a wait for loads.
LATE_SCROLL_STEPS = 60
LATE_SCROLL_WAIT_MS = 150
LATE_SCROLL_SETTLE_MS = 1500
_SCROLL_DOWN_JS = """async ([steps, wait]) => {
  for (let i = 0; i < steps; i++) {
    const before = window.scrollY;
    window.scrollTo({ top: before + Math.max(200, innerHeight * 0.9), behavior: 'instant' });
    await new Promise((r) => setTimeout(r, wait));
    if (window.scrollY === before) break;
  }
}"""


async def _late_images(page, har: Path, out: MotionPass) -> None:
    """After every other read of pass T: scroll down the page one window at
    a time, as the recording did, so lazy images load from the recording,
    then read the addresses not read yet (2.B 1.5.0: on round 2's galleries
    page 23 images were on the page at load and 119 after a scroll)."""
    await page.evaluate(_SCROLL_DOWN_JS, [LATE_SCROLL_STEPS, LATE_SCROLL_WAIT_MS])
    await page.wait_for_timeout(LATE_SCROLL_SETTLE_MS)
    await _read_images(page, har, out, await _page_images(page), late=True)


async def _extras(
    page, regions: dict[str, Region], frames_by_key, long_images=None
) -> None:
    """Regions for motion the frames could not show (2.B Terms)."""
    for i, frame in enumerate(page.frames):
        known = [r.css for r in regions.values() if r.frame == i]
        try:
            got = await frame.evaluate(
                "([k, li]) => window.__a11yMotion ? window.__a11yMotion.extras(k, li) : []",
                [known, long_images or {}],
            )
        except Exception:
            continue
        for e in got or []:
            key = f"{i}|{e['css']}"
            if key in regions or len(regions) >= MAX_REGIONS:
                continue
            regions[key] = Region(
                key=key,
                frame=i,
                frame_url=frame.url[:500] if i else "",
                css=e["css"],
                tag=e["tag"],
                content_css=e["css"],
                box=e["box"],
                source=e["source"],
                source_detail=e["detail"][:200],
            )
            frames_by_key[key] = frame


async def _regions(page, pairs, regions, frames_by_key, out: MotionPass) -> None:
    """Regions from the whole watch (2.C Terms): every tile that changed in
    any frame, with the union of its changed pixels, grouped and mapped once
    at the end. Mapping each frame on its own split one region in two when
    its changed pixels moved (a spinning square, slides taking turns), and a
    frame where most of the page changed (a dialog's backdrop, a scroll) would
    join every region into one, so such frames are noted, not mapped."""
    total = 0
    if pairs:
        w, h = out.viewport or [0, 0]
        total = max(1, -(-w // TILE) * -(-h // TILE))
    union: dict[tuple[int, int], list[int]] = {}
    kept = []
    for t, tiles in pairs:
        if len(tiles) > total * PAGE_CHANGE:
            out.page_changes.append(t)
            continue
        kept.append((t, tiles))
        for k, b in tiles.items():
            u = union.get(k)
            union[k] = (
                list(b)
                if u is None
                else [
                    min(u[0], b[0]),
                    min(u[1], b[1]),
                    max(u[2], b[2]),
                    max(u[3], b[3]),
                ]
            )
    owner: dict[tuple[int, int], str] = {}
    for group in components(set(union))[:MAX_COMPONENTS]:
        ordered = sorted(group)
        hits = 0
        for frame, info in await _map(page.main_frame, [union[t] for t in ordered]):
            index = page.frames.index(frame) if frame in page.frames else -1
            key = f"{index}|{info['css']}"
            if key not in regions:
                if len(regions) >= MAX_REGIONS:
                    out.regions_capped = True
                    continue
                regions[key] = Region(
                    key=key,
                    frame=index,
                    frame_url=frame.url[:500] if index else "",
                    css=info["css"],
                    tag=info["tag"],
                    content_css=info["css"],
                    carousel=info["carousel"],
                    covered=info["covered"],
                    box=info["box"],
                )
                frames_by_key[key] = frame
            r = regions[key]
            if info.get("part") and info["part"] not in r.parts:
                r.parts.append(info["part"])
            for i in info["idx"]:
                owner[ordered[i]] = key
                if len(r.changed_boxes) < MAX_BOXES:
                    r.changed_boxes.append(union[ordered[i]])
            hits += len(info["idx"])
        out.unmapped_tiles += len(group) - hits
    if len(components(set(union))) > MAX_COMPONENTS:
        out.regions_capped = True
    for t, tiles in kept:
        counts: dict[str, int] = {}
        for k in tiles:
            if k in owner:
                counts[owner[k]] = counts.get(owner[k], 0) + 1
        for key, n in counts.items():
            regions[key].changed_at.append(t)
            regions[key].tiles = max(regions[key].tiles, n)


async def _scrolled_watch(ctx: Any, mp: MotionPass, har: Path, keep: bool) -> None:
    """Plan Q3: one more watch, with the first hint below the first screen
    scrolled into view (content that starts only when seen). New regions
    join pass T's, marked scrolled."""
    target = mp.below[0]
    second = await pass_t(
        ctx.open_motion,
        har if har.exists() else None,
        ctx.shots if keep else None,
        ctx.rel,
        scroll_to=target,
        prefix="2s",
    )
    mp.scrolled_watch = target
    if not second.ok:
        return
    have = {r.key for r in mp.regions}
    for r in second.regions:
        if r.key not in have:
            r.scrolled = True
            mp.regions.append(r)


SETTLE_IGNORE_FROM_S = 5.0  # still changing then: it keeps changing


def settle_ignore(mp: MotionPass) -> dict[str, list[str]]:
    """Regions still changing by themselves at the end of the watch, by frame
    ("" for the top page, else the frame's URL), for the settle rule to stop
    waiting on (T1 (b)). Only content that keeps changing: a change that
    ends (a late load) is waited for as before."""
    out: dict[str, list[str]] = {}
    if not mp.ok:
        return out
    for r in mp.regions:
        if r.source != "pixels" or (
            r.changed_at and r.changed_at[-1] >= SETTLE_IGNORE_FROM_S
        ):
            out.setdefault(r.frame_url if r.frame else "", []).append(r.css)
    return out


async def collect(ctx: Any, keep_shots: bool = True) -> MotionPass:
    """Pass T once per call, shared by the 2.x checks (ctx.cache["motion"])."""
    if "motion" in ctx.cache:
        return ctx.cache["motion"]
    started = ctx.cache.get("motion_task")  # the pipeline's, beside the walk
    if started is not None and started is not asyncio.current_task():
        # Shielded: a test that runs out of its own time budget while it waits
        # must not cancel the pass the other 2.x tests and 3.A share.
        return await asyncio.shield(started)
    if getattr(ctx, "open_motion", None) is None:
        mp = MotionPass(ok=False, error="the page could not be watched in this run")
    elif ctx.out_of_time():
        mp = MotionPass(
            ok=False,
            error="the run reached its time limit before the page could be watched",
        )
    else:
        har = ctx.rel / "evidence" / "page.har.zip"
        mp = await pass_t(
            ctx.open_motion,
            har if har.exists() else None,
            ctx.shots if keep_shots else None,
            ctx.rel,
        )
        if mp.ok and mp.below and not ctx.out_of_time():
            await _scrolled_watch(ctx, mp, har, keep_shots)
    mp.browser = getattr(ctx, "motion_browser", "")
    ctx.cache["motion"] = mp
    return mp


# ── The clock check (2.C spec 1.2.0, section 2) ───────────────────────────
# A timer longer than the watch is a sign the page may update (A2). The
# check runs the page's clock past it on one more fresh load and looks at
# what changed. Abby, 2026-11-15: round 2's long timers
# were analytics heartbeats that change nothing on screen.

# The page settles on the paused clock before the first look.
CLOCK_SETTLE_MS = 3000
# A timer pass T saw counts as set again within 5% of its length (Parse.ly
# adds up to 2.5 s of jitter to 150 s).
CLOCK_MATCH = 0.05
# No timer longer than a day is run past: such a timer stays a sign.
CLOCK_MAX_MS = 86_400_000
# After the jump, the clock runs 1 s more in uneven steps, with a screenshot
# after each, so a change that repeats cannot look like none (the grid's
# late page: a flash every 125 ms toggled an even number of times in 1 s);
# then the real wait lets paints and requests show.
CLOCK_AFTER_STEPS_MS = (170, 230, 290, 310)
CLOCK_AFTER_MS = sum(CLOCK_AFTER_STEPS_MS)
CLOCK_REAL_WAIT_MS = 500

# Every change to a document after the hook starts, attributes and styles
# too: any change after the jump keeps the timers a sign.
MUTATION_COUNT_JS = """(() => {
  if (window.__tobiMutations !== undefined) return;
  window.__tobiMutations = 0;
  new MutationObserver((recs) => { window.__tobiMutations += recs.length; })
    .observe(document, { subtree: true, childList: true, attributes: true, characterData: true });
})();"""

# Added after the page's clock is installed (pipeline open_clock), so it
# wraps the clock's own timers: every timer of 1 s or more, per document.
TIMER_HOOK_JS = """(() => {
  if (window.__tobiTimers) return;
  const L = (window.__tobiTimers = []);
  for (const [name, kind] of [['setTimeout', 'timeout'], ['setInterval', 'interval']]) {
    const orig = window[name];
    window[name] = function (fn, ms, ...rest) {
      const v = Number(ms) || 0;
      if (v >= 1000 && L.length < 200) L.push({ kind, ms: Math.round(v) });
      return orig.call(this, fn, ms, ...rest);
    };
  }
})();"""

_CLOCK_STATE_JS = """() => ({
  mutations: window.__tobiMutations || 0,
  canvases: document.getElementsByTagName('canvas').length,
  playing: Array.from(document.querySelectorAll('video, audio')).filter((m) => !m.paused).length,
  text: document.body ? document.body.innerText : '',
  nodes: document.getElementsByTagName('*').length,
  images: Array.from(document.images).map((i) => i.currentSrc || i.src || ''),
  timers: window.__tobiTimers || [],
})"""


def slow_timers(mp: MotionPass) -> list[Timer]:
    """Timers longer than the watch (2.C A2's timer sign)."""
    return [t for t in mp.timers if t.ms > mp.watch_s * 1000]


async def _clock_state(page: Page) -> list[dict[str, Any]]:
    out = []
    for frame in page.frames:
        try:
            out.append(await frame.evaluate(_CLOCK_STATE_JS))
        except Exception:
            out.append({"error": True})
    return out


async def _mutation_count(page: Page) -> int:
    n = 0
    for frame in page.frames:
        try:
            n += int(await frame.evaluate("() => window.__tobiMutations || 0"))
        except Exception:
            continue
    return n


def _and_list(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _same_screen(a: bytes, b: bytes) -> bool:
    ia = Image.open(io.BytesIO(a)).convert("RGB")
    ib = Image.open(io.BytesIO(b)).convert("RGB")
    return ia.size == ib.size and ImageChops.difference(ia, ib).getbbox() is None


async def timer_check(open_page: OpenPage, mp: MotionPass) -> TimerCheck:
    """Run the page's clock past the long timers pass T saw.
    Never raises; anything that goes wrong leaves the timers a sign."""
    t0 = time.monotonic()
    want = slow_timers(mp)
    out = TimerCheck(timers_ms=sorted({t.ms for t in want}))
    try:
        context, page = await open_page()
    except Exception as exc:
        out.why = f"the page could not be loaded again ({safe_error(exc)})"
        return out
    requests: list[str] = []
    try:
        await page.clock.run_for(CLOCK_SETTLE_MS)
        before = await _clock_state(page)
        shot_a = await page.screenshot()
        seen = [
            (t["kind"], t["ms"])
            for f in before
            for t in f.get("timers", [])
            if t["ms"] > mp.watch_s * 1000
        ]
        missing = [
            t
            for t in want
            if not any(
                k == t.kind and abs(ms - t.ms) <= CLOCK_MATCH * t.ms for k, ms in seen
            )
        ]
        if missing:
            out.why = (
                f"the timer of {missing[0].ms / 1000:g} s was not set again when we "
                "loaded the page again, so we could not run past it"
            )
            return out
        if any(f.get("canvases") for f in before):
            out.why = (
                "the page draws on a canvas, and we cannot read a canvas for "
                "changes when the page's clock runs"
            )
            return out
        longest = max(ms for _, ms in seen)
        if longest > CLOCK_MAX_MS:
            out.why = f"a timer of {longest / 1000:g} s is longer than we run the clock"
            return out
        context.on("request", lambda r: requests.append(r.url))
        out.ran = True
        out.advanced_ms = longest + CLOCK_AFTER_MS
        # Changes are counted only while the clock runs: a screenshot alone
        # made a real page change two attributes (round 2's help page).
        counted = 0

        async def run(step) -> None:
            nonlocal counted
            m0 = await _mutation_count(page)
            await step
            counted += await _mutation_count(page) - m0

        before = await _clock_state(page)
        await run(page.clock.fast_forward(longest + CLOCK_AFTER_STEPS_MS[0]))
        shots = [await page.screenshot()]
        for step in CLOCK_AFTER_STEPS_MS[1:]:
            await run(page.clock.run_for(step))
            shots.append(await page.screenshot())
        await run(page.wait_for_timeout(CLOCK_REAL_WAIT_MS))
        after = await _clock_state(page)
        shots.append(await page.screenshot())
        out.requests = len(requests)
        if counted:
            out.changed.append("content")
        if not all(_same_screen(shot_a, s) for s in shots):
            out.changed.append("screen")
        for key, name in (
            ("text", "text"),
            ("nodes", "elements"),
            ("images", "images"),
            ("playing", "media"),
        ):
            if len(before) != len(after) or any(
                a.get(key) != b.get(key) for a, b in zip(before, after)
            ):
                out.changed.append(name)
        if out.changed:
            out.why = (
                "when we ran the page's clock past it, the page's "
                + _and_list(list(dict.fromkeys(out.changed)))
                + " changed"
            )
        elif out.requests:
            out.why = (
                "when we ran the page's clock past it, the page asked its server "
                "for something, and our copy of the page cannot show what the "
                "server would send"
            )
        else:
            out.cleared = True
    except Exception as exc:
        out.cleared = False
        out.why = f"the clock could not be run ({safe_error(exc)})"
    finally:
        out.seconds = round(time.monotonic() - t0, 1)
        try:
            await context.close()
        except Exception:
            pass
    return out


async def timer_check_shared(ctx: Any, mp: MotionPass) -> None:
    """The clock check once per run, shared by 2.C and 2.D: sets
    `mp.timer_check`. The checks decide when it is worth running."""
    if mp.timer_check is not None:
        return
    task = ctx.cache.get("timer_check_task")
    if task is None:
        opener = getattr(ctx, "open_clock", None)
        if opener is None or ctx.out_of_time():
            mp.timer_check = TimerCheck(
                why="there was no time left in this run to run the page's clock"
                if opener is not None
                else "the page's clock could not be run in this run",
                timers_ms=sorted({t.ms for t in slow_timers(mp)}),
            )
            return
        task = asyncio.ensure_future(timer_check(opener, mp))
        ctx.cache["timer_check_task"] = task
    # Shielded: a test out of its own time must not cancel the shared check.
    mp.timer_check = await asyncio.shield(task)
