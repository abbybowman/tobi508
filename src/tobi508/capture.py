"""Record a page to HAR once, then replay it so every test run sees the same
network responses.

A HAR freezes network responses only. Client-side randomness or the clock can
still vary between replays.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit

from playwright.async_api import Browser, BrowserContext

from tobi508.andi import install_andi_routes
from tobi508.browser import LogFn, NavigationGuard, new_context
from tobi508.config import Settings
from tobi508.count import PLAY_HOOK_JS
from tobi508.egress import EgressProxy
from tobi508.policy import check_url
from tobi508.redact import safe_url
from tobi508.traverse import INIT_JS

MAX_FRAMES_KEPT = 20  # enough to show why; the decision needs only one


@dataclass
class Capture:
    target_url: str
    final_url: str
    har_path: Path
    redirects: list[dict[str, Any]] = field(default_factory=list)
    # Frames on another host than the top page, seen while recording. Their
    # replays run in full Chromium (browser.replay_in_full_chromium).
    cross_site_frames: list[str] = field(default_factory=list)
    # Media saved in full for replay, and files over the cap (media store).
    media: list[dict[str, Any]] = field(default_factory=list)
    # Scripts that recorded scripts name and the recording did not load
    # itself (code split by the page), saved or not (the chunk store).
    chunks: list[dict[str, Any]] = field(default_factory=list)
    frozen: bool = False  # replayed from a frozen pages folder (frozen.py)
    # Every http(s) frame address seen at the end of a live recording, query
    # kept, so the freeze can say which the recording lacks.
    frame_urls: list[str] = field(default_factory=list)


async def record(
    browser: Browser,
    settings: Settings,
    url: str,
    har_path: Path,
    log: LogFn,
    egress: EgressProxy | None = None,
    with_media: bool = True,
) -> Capture:
    """Load `url` live in a fresh context and save every response to `har_path`.
    `with_media` False: no media store. Other pages and 19.A's own loads are
    read only for their links and text (no test plays their media), and on a
    page of large videos the store took 342 s past a 20 s share."""
    ctx = await new_context(
        browser, settings, record_har_path=str(har_path), record_har_mode="full"
    )
    guard = NavigationGuard(settings, live=True, log=log, egress=egress)
    await guard.install(ctx)
    scripts: list[Any] = []  # responses of scripts, for the chunk store
    seen: set[str] = set()

    def note(resp) -> None:
        seen.add(resp.url.split("#", 1)[0])
        ctype = resp.headers.get("content-type", "")
        if resp.ok and (_is_script(resp.url, ctype) or _is_html(ctype)):
            scripts.append(resp)

    ctx.on("response", note)
    try:
        page = await ctx.new_page()
        final_url = await guard.goto(page, url)
        await _extra_wait(page, settings, log)
        await _idle(page, log, 10_000)
        if settings.record_scroll_steps:
            await _scroll_steps(page, log)
            await _extra_wait(page, settings, log)
        # Scroll to the bottom so content loaded on scroll is recorded (4.C spec
        # section 2, Recording).
        for i in range(settings.record_scroll_passes):
            height = await page.evaluate("document.documentElement.scrollHeight")
            await page.evaluate(
                "window.scrollTo(0, document.documentElement.scrollHeight)"
            )
            await page.mouse.wheel(0, 400)
            await _idle(page, log, 3_000)
            grew = await page.evaluate("document.documentElement.scrollHeight") > height
            log("capture_scroll", pass_=i + 1, page_grew=grew)
        frame_urls = [
            f.url for f in page.frames[1:] if f.url.startswith(("http:", "https:"))
        ]
        frames = cross_site_frames(page.url, frame_urls)
        if frames:
            log("capture_cross_site_frames", count=len(frames))
        media = await _fetch_media(ctx, page, settings, log) if with_media else []
        chunks = await _fetch_chunks(ctx, scripts, seen, settings, log)
    finally:
        await ctx.close()  # writes the HAR
    _add_media(har_path, media)
    _add_chunks(har_path, chunks)
    return Capture(
        url,
        final_url,
        har_path,
        guard.redirects,
        frames,
        media=[{k: v for k, v in m.items() if k != "body"} for m in media],
        chunks=[{k: v for k, v in c.items() if k != "body"} for c in chunks],
        frame_urls=frame_urls,
    )


SCROLL_STEP_MAX = 60  # windows scrolled one at a time (a very long page stops)
SCROLL_STEP_WAIT_MS = 250


_SCROLL_STEP_JS = """() => {
  const el = document.scrollingElement || document.documentElement;
  const before = el.scrollTop;
  // "instant" overrides a page's scroll-behavior: smooth (Bootstrap 5),
  // under which scrollBy has not moved yet when it returns (step 10a).
  window.scrollTo({top: before + Math.max(200, innerHeight * 0.9),
                   behavior: "instant"});
  return {before, after: el.scrollTop};
}"""

_SCROLL_END_JS = """() => {
  const el = document.scrollingElement || document.documentElement;
  return {top: el.scrollTop, height: el.scrollHeight, window: innerHeight};
}"""


async def _scroll_steps(page, log: LogFn) -> None:
    """Scroll down one window at a time, waiting briefly at each, then back
    to the top; what came into view has had the chance to load.

    It has reached the end when, after the wait, the window's bottom is at
    the document's full height, measured again then, so content the step
    loaded counts. A step that does not move the page before the end (the
    page itself blocks scrolling) stops the walk and is logged as not at the
    end. The log line gives the last position, the height and the window:
    `reached_end` is the fact a freeze's reader checks."""
    steps, at = 0, {"top": 0, "height": 0, "window": 0}
    reached = stuck = False
    try:
        while steps < SCROLL_STEP_MAX:
            moved = await page.evaluate(_SCROLL_STEP_JS)
            steps += 1
            await page.wait_for_timeout(SCROLL_STEP_WAIT_MS)
            at = await page.evaluate(_SCROLL_END_JS)
            if at["top"] + at["window"] >= at["height"] - 2:
                reached = True
                break
            if moved["after"] <= moved["before"] and at["top"] <= moved["before"]:
                stuck = True
                break
        await _idle(page, log, 5_000)
        await page.evaluate('window.scrollTo({top: 0, behavior: "instant"})')
    except Exception as exc:
        log("capture_scroll_steps", "error", error=type(exc).__name__)
        return
    log(
        "capture_scroll_steps",
        steps=steps,
        cut=steps >= SCROLL_STEP_MAX and not reached,
        reached_end=reached,
        stuck=stuck,
        top=at["top"],
        height=at["height"],
        window=at["window"],
    )


# ── Media store (2.A-2.D plan items 13-14, Q9) ─────────────────────────────
# A large video is fetched in byte ranges; the browser cancels the open
# ended request when it seeks, so the HAR keeps ranges with no body and the
# video never plays on replay. So while recording, each media URL is also
# fetched once in full (within a size and time cap) and stored inside the
# HAR zip; on replay its byte ranges are served from there.

MEDIA_INDEX = "a11y-media.json"
_MEDIA_JS = """(chosenFirst) => {
  const els = Array.from(document.querySelectorAll('video, audio'));
  const all = (m) => [m.currentSrc, m.src,
    ...Array.from(m.querySelectorAll('source')).map((s) => s.src)];
  const list = chosenFirst
    ? [...els.map((m) => m.currentSrc), ...els.flatMap(all)]
    : els.flatMap(all);
  return list.filter((u) => /^https?:/.test(u || ''));
}"""


async def _media_size(ctx, url: str) -> tuple[int | None, str, int | None]:
    """A media file's size without downloading it: Content-Length from a
    HEAD that succeeded, else the total in Content-Range for byte 0 alone
    (a server that ignores ranges sends the file, whose length is the
    size). The third value is the server's error status (404 ...) when it
    refused both, so a missing file is not reported as too large."""
    status: int | None = None
    try:
        head = await ctx.request.head(url, timeout=5000)
        size = head.headers.get("content-length", "")
        if head.ok and size.isdigit():
            return int(size), head.headers.get("content-type", ""), None
    except Exception:
        pass
    try:
        one = await ctx.request.get(url, headers={"Range": "bytes=0-0"}, timeout=5000)
        kind = one.headers.get("content-type", "")
        total = re.search(r"/(\d+)$", one.headers.get("content-range", ""))
        if one.status == 206 and total:
            return int(total.group(1)), kind, None
        if one.ok:
            return len(await one.body()), kind, None
        status = one.status
    except Exception:
        pass
    return None, "", status


async def _fetch_media(
    ctx, page, settings: Settings, log: LogFn
) -> list[dict[str, Any]]:
    urls: list[str] = []
    for frame in page.frames:
        try:
            for u in await frame.evaluate(_MEDIA_JS, settings.media_chosen_first):
                # Requests never carry the #fragment (#t=8,10): keyed without
                # it, so the range route matches and the media can seek.
                u = u.split("#", 1)[0]
                if u not in urls:
                    urls.append(u)
        except Exception:
            continue
    cap_mb, cap_s = settings.media_cap_mb, settings.media_cap_s
    left = None if cap_mb is None else int(cap_mb * 1_000_000)
    deadline = None if cap_s is None else time.monotonic() + cap_s
    out: list[dict[str, Any]] = []
    for n, url in enumerate(urls[:20]):
        entry: dict[str, Any] = {"url": url, "file": None, "size": None, "type": ""}
        out.append(entry)
        entry["size"], entry["type"], refused = await _media_size(ctx, url)
        if refused is not None and refused >= 400:
            entry["status"] = refused  # not there: never "over the cap"
            continue
        if left is not None and (entry["size"] is None or entry["size"] > left):
            entry["over_cap"] = True  # unknown size counts as over a cap
            continue
        remaining = None if deadline is None else deadline - time.monotonic()
        if remaining is not None and remaining <= 0:
            entry["over_cap"] = True
            continue
        try:
            got = await ctx.request.get(
                url, timeout=int(1000 * remaining) if remaining else 0
            )
            body = await got.body()
        except Exception as exc:
            entry["over_cap"] = True  # too slow within the cap, or failed
            log("media_store", "error", n=n, error=type(exc).__name__)
            continue
        if not got.ok:
            entry["status"] = got.status
            continue
        if left is not None and len(body) > left:
            entry["over_cap"] = True
            continue
        if left is not None:
            left -= len(body)
        entry.update(
            file=f"a11y-media-{n}.bin",
            size=len(body),
            type=got.headers.get("content-type", entry["type"]),
            body=body,
        )
        log("media_store", n=n, bytes=len(body))
    return out


def _add_media(har_path: Path, media: list[dict[str, Any]]) -> None:
    if not media:
        return
    with zipfile.ZipFile(har_path, "a") as z:
        for m in media:
            if m.get("body") is not None:
                z.writestr(m["file"], m["body"])
        z.writestr(
            MEDIA_INDEX,
            json.dumps([{k: v for k, v in m.items() if k != "body"} for m in media]),
        )


def media_index(har_path: Path) -> list[dict[str, Any]]:
    """The media store's index in a recording ([] when it has none)."""
    try:
        with zipfile.ZipFile(har_path) as z:
            return json.loads(z.read(MEDIA_INDEX))
    except (KeyError, OSError, ValueError, zipfile.BadZipFile):
        return []


REDIRECT_HOPS = 3


def document_type(har_path: Path, url: str) -> str:
    """The media type of the document a recording loaded at `url` (its
    final address), lower case without parameters; "" when unknown. 19.A
    1.14.0: a suggested page that is not HTML (an API's JSON, XML) is not a
    page."""
    url = url.split("#", 1)[0]
    try:
        with zipfile.ZipFile(har_path) as z:
            name = next(n for n in z.namelist() if n.endswith(".har"))
            entries = json.loads(z.read(name))["log"]["entries"]
    except (KeyError, OSError, ValueError, StopIteration, zipfile.BadZipFile):
        return ""
    for e in entries:
        if e["request"]["url"].split("#", 1)[0] != url:
            continue
        r = e["response"]
        if r.get("status") != 200:
            continue
        mime = r.get("content", {}).get("mimeType") or next(
            (
                h["value"]
                for h in r.get("headers", [])
                if h["name"].lower() == "content-type"
            ),
            "",
        )
        return mime.split(";", 1)[0].strip().lower()
    return ""


def media_body(har_path: Path, url: str) -> bytes | None:
    """A media file's bytes: from the media store, else the HAR's own body,
    following redirects the recording holds (at most REDIRECT_HOPS; 2.B
    1.5.0: an avatar answered with a 302 on round 1's max-power page)."""
    url = url.split("#", 1)[0]
    try:
        with zipfile.ZipFile(har_path) as z:
            for m in media_index(har_path):
                if m["url"] == url and m.get("file"):
                    return z.read(m["file"])
            name = next(n for n in z.namelist() if n.endswith(".har"))
            entries = json.loads(z.read(name))["log"]["entries"]
            for _ in range(REDIRECT_HOPS + 1):
                nxt = None
                for e in entries:
                    if e["request"]["url"] != url:
                        continue
                    status = e["response"].get("status")
                    c = e["response"].get("content", {})
                    if status == 200 and c.get("_file"):
                        return z.read(c["_file"])
                    if status in (301, 302, 303, 307, 308) and nxt is None:
                        loc = e["response"].get("redirectURL") or next(
                            (
                                h["value"]
                                for h in e["response"].get("headers", [])
                                if h["name"].lower() == "location"
                            ),
                            "",
                        )
                        if loc:
                            nxt = urljoin(url, loc).split("#", 1)[0]
                if nxt is None or nxt == url:
                    return None
                url = nxt
    except (KeyError, OSError, ValueError, StopIteration, zipfile.BadZipFile):
        return None
    return None


def document_sha(har_path: Path, final_url: str) -> str | None:
    """SHA-256 of the main document's bytes in a recording (None when it
    cannot be read). Two recordings of the same page have the same hash;
    used to tell an other page that is the tested page again (K-01)."""
    import hashlib

    body = media_body(har_path, final_url)
    return hashlib.sha256(body).hexdigest() if body else None


# ── Chunk store (2026-11-09: a fourth exception to principle 5) ──────
# A page may load code only when it is used (`import("./chunk.js")`, code
# splitting), so a recording made from a load never holds it, and on replay
# the page's handlers silently do nothing: 5340's year popup and focus jump
# were invisible (docs/solutions/recordings-miss-lazy-scripts.md). While
# recording, scripts that recorded scripts name by a string literal, relative
# to the script's own address, are fetched once and stored inside the HAR zip
# beside the media. Page code does choose these fetches, so the limits are
# tight: same host as the script that names it, allowlisted (checked here and
# by the egress proxy), a script, a count and size cap, `CHUNK_ROUNDS` deep.
# Each is recorded as its own entry; one that could not be stored is listed
# with the reason, and `unrecorded_code` reports it.

CHUNKS_INDEX = "a11y-chunks.json"
MAX_CHUNKS = 300  # 150 before 2026-11-20 (#134: round 3 needs about 163)
CHUNK_CONCURRENCY = 8
CHUNK_STORE_S = 40  # the whole chunk store for one page
# Raised from 3 MB and 12 MB (Abby, 2026-11-20; #134 step 25): round 3's
# community pages load a post editor and an icon set of 5.6 MB and 6.9 MB
# when used, 13.8 MB with the rest of their chunks.
MAX_CHUNK_BYTES = 10_000_000
MAX_CHUNKS_TOTAL_BYTES = 24_000_000
CHUNK_ROUNDS = 5  # levels; 3 before 2026-11-20 (#134: round 3 needs 4)
# `import("./x.js")`, `from"./x.js"` and `import"./x.js"` with a string
# literal that is a relative or root path to a .js/.mjs file.
_REF = re.compile(
    r"""(?:\bimport\s*\(\s*|\bfrom\s*|\bimport\s*)["'](\.{0,2}/[^"'\s?#]+?\.m?js)["']"""
)


class _InlineScripts(HTMLParser):
    """The text of a page's inline scripts (those with no `src`), read by the
    standard HTML parser, which follows the HTML rules for script end tags
    (`</script >`, attributes, case) that a regular expression gets wrong."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self._in: bool | None = None  # None: not in a script; True: inline

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "script":
            self._in = not any(k == "src" for k, _ in attrs)
            if self._in:
                self.parts.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._in = None

    def handle_data(self, data: str) -> None:
        if self._in:
            self.parts[-1] += data


def _inline_scripts(html: str) -> str:
    p = _InlineScripts()
    try:
        p.feed(html)
        p.close()
    except Exception:
        pass  # what was read is kept
    return "\n".join(p.parts)


def _is_html(content_type: str) -> bool:
    return "html" in content_type.lower()


def _code_of(text: str, content_type: str) -> str:
    """The code to scan: a script as it is; a page's inline scripts joined."""
    if _is_html(content_type):
        return _inline_scripts(text)
    return text


def _is_script(url: str, content_type: str) -> bool:
    path = urlsplit(url).path.lower()
    return path.endswith((".js", ".mjs")) or "javascript" in content_type.lower()


def script_refs(text: str, base_url: str) -> list[str]:
    """Addresses of the scripts a script names by a string literal, resolved
    from its own address (fragment dropped, in order, once each)."""
    out: list[str] = []
    seen: set[str] = set()  # a list's `in` made a large script quadratic (S-01)
    for m in _REF.finditer(text):
        ref = urljoin(base_url, m.group(1)).split("#", 1)[0]
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


async def _fetch_chunk(
    ctx, entry: dict[str, Any], sem: asyncio.Semaphore
) -> bytes | None:
    """Fetch one chunk into `entry` (its body, or why it is missing)."""
    ref = entry["url"]
    async with sem:
        try:
            got = await ctx.request.get(ref, timeout=10_000)
            body = await got.body()
        except Exception as exc:
            entry["missing"] = f"could not be fetched ({type(exc).__name__})"
            return None
    ctype = got.headers.get("content-type", "")
    if not got.ok:
        entry["missing"] = f"answered {got.status}"
    elif not _is_script(ref, ctype):
        entry["missing"] = "not a script"
    elif len(body) > MAX_CHUNK_BYTES:
        entry["missing"] = "over the size limit"
    else:
        entry.update(size=len(body), type=ctype or "text/javascript")
        return body
    return None


async def _fetch_chunks(
    ctx, scripts: list[Any], seen: set[str], settings: Settings, log: LogFn
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    named: set[str] = set()
    total = 0
    deadline = time.monotonic() + CHUNK_STORE_S
    sem = asyncio.Semaphore(CHUNK_CONCURRENCY)
    level: list[tuple[str, str]] = []  # (script address, its text)
    for r in scripts:
        try:
            code = _code_of(await r.text(), r.headers.get("content-type", ""))
            level.append((r.url.split("#", 1)[0], code))
        except Exception:
            continue
    for _ in range(CHUNK_ROUNDS):
        todo: list[dict[str, Any]] = []
        fresh: list[dict[str, Any]] = []  # entries made this round
        for base, text in level:
            for ref in script_refs(text, base):
                if ref in seen or ref in named:
                    continue
                named.add(ref)
                entry: dict[str, Any] = {
                    "url": ref,
                    "file": None,
                    "size": None,
                    "referenced_by": safe_url(base),
                }
                out.append(entry)
                fresh.append(entry)
                if _host(ref) != _host(base):
                    entry["missing"] = "another host than the script that names it"
                elif not check_url(
                    ref, settings.allowed_domains, settings.dev_mode
                ).allowed:
                    entry["missing"] = "not allowed by the allowlist"
                elif len(todo) + sum(1 for e in out if e.get("size")) >= MAX_CHUNKS:
                    entry["missing"] = "more than the chunk limit"
                elif time.monotonic() > deadline:
                    entry["missing"] = "the time limit for the chunk store passed"
                else:
                    todo.append(entry)
        bodies = await asyncio.gather(*[_fetch_chunk(ctx, e, sem) for e in todo])
        level = []
        for entry, body in zip(todo, bodies, strict=True):
            if body is None:
                continue
            if total + len(body) > MAX_CHUNKS_TOTAL_BYTES:
                entry["missing"], entry["size"] = "over the size limit", None
                continue
            total += len(body)
            n = sum(1 for e in out if e.get("file"))
            entry.update(file=f"a11y-chunk-{n}.js", body=body)
            level.append((entry["url"], body.decode("utf-8", "replace")))
        for e in fresh:
            log(
                "chunk_store",
                "ok" if e.get("file") else "info",
                url=safe_url(e["url"]),
                bytes=e.get("size"),
                missing=e.get("missing"),
            )
        if not level:
            break
    return out


def _add_chunks(har_path: Path, chunks: list[dict[str, Any]]) -> None:
    if not chunks:
        return
    with zipfile.ZipFile(har_path, "a") as z:
        for c in chunks:
            if c.get("body") is not None:
                z.writestr(c["file"], c["body"])
        z.writestr(
            CHUNKS_INDEX,
            json.dumps([{k: v for k, v in c.items() if k != "body"} for c in chunks]),
        )


def chunk_index(har_path: Path) -> list[dict[str, Any]]:
    """The chunk store's index in a recording ([] when it has none)."""
    try:
        with zipfile.ZipFile(har_path) as z:
            return json.loads(z.read(CHUNKS_INDEX))
    except (KeyError, OSError, ValueError, zipfile.BadZipFile):
        return []


async def _serve_chunks(ctx: BrowserContext, har_path: Path) -> None:
    """Answer requests for stored chunks (after route_from_har)."""
    stored = {c["url"]: c for c in chunk_index(har_path) if c.get("file")}
    if not stored:
        return
    with zipfile.ZipFile(har_path) as z:
        bodies = {u: z.read(c["file"]) for u, c in stored.items()}

    async def serve(route) -> None:
        u = route.request.url.split("#", 1)[0]
        await route.fulfill(
            status=200,
            headers={"Content-Type": stored[u].get("type") or "text/javascript"},
            body=bodies[u],
        )

    await ctx.route(lambda url: url.split("#", 1)[0] in stored, serve)


def unrecorded_code(har_path: Path) -> list[str]:
    """Scripts that scripts in the recording name by a string literal, on
    the same host, that the recording does not hold (not in the HAR with a
    response and not in the chunk store): code the page loads when it is
    used, which a replay cannot run. Read from the recorded files only; no
    address is fetched. Works for recordings made before the chunk store."""
    try:
        with zipfile.ZipFile(har_path) as z:
            name = next(n for n in z.namelist() if n.endswith(".har"))
            entries = json.loads(z.read(name))["log"]["entries"]
            held = {
                e["request"]["url"].split("#", 1)[0]
                for e in entries
                if e["response"].get("status", 0) > 0
            }
            held |= {c["url"] for c in chunk_index(har_path) if c.get("file")}
            texts: list[tuple[str, str]] = []
            for e in entries:
                c = e["response"].get("content", {})
                url = e["request"]["url"].split("#", 1)[0]
                mime = c.get("mimeType", "")
                if e["response"].get("status") != 200 or not (
                    _is_script(url, mime) or _is_html(mime)
                ):
                    continue
                if c.get("_file"):
                    raw = z.read(c["_file"]).decode("utf-8", "replace")
                else:
                    raw = c.get("text") or ""
                if raw:
                    texts.append((url, _code_of(raw, mime)))
            for ch in chunk_index(har_path):
                if ch.get("file"):
                    texts.append(
                        (ch["url"], z.read(ch["file"]).decode("utf-8", "replace"))
                    )
    except (StopIteration, KeyError, OSError, ValueError, zipfile.BadZipFile):
        return []
    out: list[str] = []
    for base, text in texts:
        for ref in script_refs(text, base):
            if ref not in held and _host(ref) == _host(base) and ref not in out:
                out.append(ref)
    return out


async def _serve_media(ctx: BrowserContext, har_path: Path) -> None:
    """Answer byte-range requests for stored media (after route_from_har)."""
    stored = {m["url"]: m for m in media_index(har_path) if m.get("file")}
    if not stored:
        return
    cache: dict[str, bytes] = {}

    async def serve(route) -> None:
        m = stored[route.request.url]
        if m["url"] not in cache:
            with zipfile.ZipFile(har_path) as z:
                cache[m["url"]] = z.read(m["file"])
        body = cache[m["url"]]
        total = len(body)
        headers = {"Accept-Ranges": "bytes", "Content-Type": m.get("type") or ""}
        rng = route.request.headers.get("range", "")
        hit = re.match(r"bytes=(\d*)-(\d*)", rng)
        if hit and (hit.group(1) or hit.group(2)):
            a = int(hit.group(1)) if hit.group(1) else max(0, total - int(hit.group(2)))
            b = int(hit.group(2)) if hit.group(1) and hit.group(2) else total - 1
            b = min(b, total - 1)
            if a > b:
                await route.fulfill(
                    status=416, headers={"Content-Range": f"bytes */{total}"}
                )
                return
            headers["Content-Range"] = f"bytes {a}-{b}/{total}"
            await route.fulfill(status=206, headers=headers, body=body[a : b + 1])
            return
        await route.fulfill(status=200, headers=headers, body=body)

    await ctx.route(lambda url: url in stored, serve)


def _host(url: str) -> str:
    try:
        return (urlsplit(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""


def cross_site_frames(top_url: str, frame_urls: list[str]) -> list[str]:
    """Frame URLs (query and fragment dropped) on another host than the top
    page. Another host is wider than Chrome's "site" (same registrable
    domain), so a same-site subdomain also counts: that only costs a slower
    replay, never a different one. about:blank, data: and srcdoc frames share
    the parent's process and are skipped."""
    top = _host(top_url)
    out = {
        safe_url(u)
        for u in frame_urls
        if u.startswith(("http:", "https:")) and _host(u) not in ("", top)
    }
    return sorted(out)[:MAX_FRAMES_KEPT]


def _failed_urls(har_path: Path) -> set[str]:
    """URLs the HAR recorded with no response (status -1)."""
    with zipfile.ZipFile(har_path) as z:
        name = next(n for n in z.namelist() if n.endswith(".har"))
        entries = json.loads(z.read(name))["log"]["entries"]
    return {e["request"]["url"] for e in entries if e["response"].get("status", 0) < 0}


def failed_scripts(har_path: Path) -> list[str]:
    """Scripts the recording asked for that did not load: no response (-1,
    e.g. refused) or an error status. Facts only; 19.A row W4 decides."""
    with zipfile.ZipFile(har_path) as z:
        name = next(n for n in z.namelist() if n.endswith(".har"))
        entries = json.loads(z.read(name))["log"]["entries"]
    return [
        e["request"]["url"]
        for e in entries
        if e.get("_resourceType") == "script"
        and not 0 <= e["response"].get("status", 0) < 400
    ]


async def _extra_wait(page, settings: Settings, log: LogFn) -> None:
    """`record_extra_wait_ms`: a pause for pages that fetch late; the
    network-idle check that follows catches what it started."""
    if settings.record_extra_wait_ms:
        await page.wait_for_timeout(settings.record_extra_wait_ms)
        await _idle(page, log, 10_000)


async def _idle(page, log: LogFn, timeout_ms: int) -> None:
    try:
        await page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        log("capture_networkidle_timeout", "info", timeout_ms=timeout_ms)


@dataclass
class Replay:
    context: BrowserContext
    guard: NavigationGuard
    andi_aborted: list[str] | None  # None when ANDI routes are not installed


async def replay_context(
    browser: Browser,
    settings: Settings,
    har_path: Path,
    log: LogFn,
    with_andi: bool = False,
    init_scripts: tuple[str, ...] = (),
    viewport: dict[str, int] | None = None,
) -> Replay:
    """A fresh context that answers only from the HAR (unknown URLs abort).

    `init_scripts` run in every frame after INIT_JS and before page scripts
    (pass T's hooks, motion.py; plan Q7): INIT_JS stays the same for every
    other load. `viewport`: another window than the configured one (3.A's
    flash capture, 1024 x 768)."""
    ctx = await new_context(
        browser, settings, **({"viewport": viewport} if viewport else {})
    )
    # Loads from the recording wait longer than live loads (config).
    ctx.set_default_navigation_timeout(settings.replay_navigation_timeout_ms)
    await ctx.add_init_script(INIT_JS)  # focus and mutation log (settle rule)
    # Media that played, in the document or not (count.py; guard CN, N-01).
    await ctx.add_init_script(PLAY_HOOK_JS)
    for script in init_scripts:
        await ctx.add_init_script(script)
    await ctx.route_from_har(str(har_path), not_found="abort")
    failed = _failed_urls(har_path)
    if failed:
        # Requests that failed while recording (refused by the egress proxy,
        # DNS errors) are saved with status -1, and Playwright's HAR replay
        # waits on them forever. Fail them, as they failed live. Registered
        # after route_from_har, so it runs first.
        async def fail(route) -> None:
            await route.abort("failed")

        await ctx.route(lambda url: url in failed, fail)
    await _serve_media(ctx, har_path)  # after route_from_har: runs first
    await _serve_chunks(ctx, har_path)
    await _serve_signin_answers(ctx, har_path, log)
    andi_aborted = None
    if with_andi:
        andi_aborted = await install_andi_routes(ctx, settings.third_party_dir)
    guard = NavigationGuard(settings, live=False, log=log)
    await guard.install(ctx)  # last registered runs first
    return Replay(ctx, guard, andi_aborted)


# ── Silent sign-in checks (round 3) ────────────────────────
# Some apps draw nothing until a hidden frame asks their sign-in server
# whether the visitor is signed in (keycloak-js check-sso: `prompt=none`).
# The question carries a state value made on each load, so a replay asks an
# address the recording never saw, the frame is aborted and the page stays
# blank. When the recording holds that check answered "not signed in"
# (`error=login_required`), the replay gives the same answer to the new
# load: the recorded redirect address, served from the recording, with only
# `state` replaced by the new request's own (the protocol echoes it). This
# is the one place a replay makes up part of a response; each one is logged
# (`replay_signin_answer`). Nothing is fetched live, no other address is
# used, and a main-frame request is never answered.

_SIGNIN_JS = "<!doctype html><meta charset=utf-8><script>location.replace({})</script>"


def _location(entry: dict) -> str:
    for h in entry["response"].get("headers", []):
        if h.get("name", "").lower() == "location":
            return urljoin(entry["request"]["url"], h.get("value", ""))
    return ""


def signin_answers(har_path: Path) -> dict[str, str]:
    """Silent sign-in checks the recording holds answered "not signed in":
    the check's address without its query -> the recorded redirect address.
    Only GET document requests with `prompt=none`, answered by a redirect
    whose address carries `error=login_required` and a `state`."""
    with zipfile.ZipFile(har_path) as z:
        name = next(n for n in z.namelist() if n.endswith(".har"))
        entries = json.loads(z.read(name))["log"]["entries"]
    out: dict[str, str] = {}
    for e in entries:
        req, status = e["request"], e["response"].get("status", 0)
        u = urlsplit(req["url"])
        if req.get("method") != "GET" or not 300 <= status < 400:
            continue
        if parse_qs(u.query).get("prompt") != ["none"]:
            continue
        loc = _location(e)
        answer = parse_qs(urlsplit(loc).fragment or urlsplit(loc).query)
        if answer.get("error") == ["login_required"] and "state" in answer:
            out[urlunsplit((u.scheme, u.netloc, u.path, "", ""))] = loc
    return out


def signin_location(recorded: str, request_url: str) -> str | None:
    """The recorded "not signed in" redirect with its `state` replaced by
    the request's own; None when the request is not a silent check with
    one state. Nothing else of either address is changed or added."""
    q = parse_qs(urlsplit(request_url).query)
    if q.get("prompt") != ["none"] or len(q.get("state", [])) != 1:
        return None
    r = urlsplit(recorded)
    part = "fragment" if r.fragment else "query"
    pairs = [
        (k, q["state"][0] if k == "state" else v)
        for k, vs in parse_qs(getattr(r, part), keep_blank_values=True).items()
        for v in vs
    ]
    return urlunsplit(r._replace(**{part: urlencode(pairs)}))


async def _serve_signin_answers(ctx, har_path: Path, log: LogFn) -> None:
    answers = signin_answers(har_path)
    if not answers:
        return
    with zipfile.ZipFile(har_path) as z:
        name = next(n for n in z.namelist() if n.endswith(".har"))
        recorded = {
            e["request"]["url"].split("#")[0]
            for e in json.loads(z.read(name))["log"]["entries"]
        }

    def key(url: str) -> str:
        u = urlsplit(url)
        return urlunsplit((u.scheme, u.netloc, u.path, "", ""))

    async def answer(route) -> None:
        req = route.request
        rec = answers.get(key(req.url))
        new = signin_location(rec, req.url) if rec else None
        # A frame's navigation only, to an address the recording holds.
        if (
            new is None
            or not req.is_navigation_request()
            or req.frame.parent_frame is None
            or new.split("#")[0] not in recorded
        ):
            await route.fallback()
            return
        log("replay_signin_answer", url=safe_url(req.url), to=safe_url(new))
        body = _SIGNIN_JS.format(json.dumps(new).replace("</", "<\\/"))
        await route.fulfill(status=200, content_type="text/html", body=body)

    # The recording answers an address it holds exactly; this only the rest.
    await ctx.route(
        lambda url: key(url) in answers and url.split("#")[0] not in recorded,
        answer,
    )
