"""What an action changes: a snapshot of the page before and after it, and
the effect between them (4.A spec, Terms: effect). Shared by 4.A (click,
Enter and Space on controls), 4.B (key-press proof) and 5.D (completing a
field and tabbing away). Records facts only; what an effect means for an
outcome is each check's rules.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from tobi508.traverse import PATH_JS, Session, _read_logs, settle, submissions


def without_fragment(url: str) -> str:
    """An address without its #fragment. A change of fragment only is the same
    page (spec 4.E and 5.D Terms), so no check compares addresses with it."""
    return url.split("#", 1)[0]


# Paths of every element rendered in the top document, shadow roots included,
# with 4.A's own path builder and visibility test, so 4.A can match its keys
# (4.F's Enter presses: what they show, for 4.A's hover check).
SHOWN_JS = (
    "(() => {"
    + PATH_JS
    + """
  const out = [];
  const walk = (root) => { for (const el of root.querySelectorAll('*')) {
    const v = el.checkVisibility
      ? el.checkVisibility({ visibilityProperty: true })
      : el.getClientRects().length > 0;
    if (v) out.push(path(el));
    if (el.shadowRoot) walk(el.shadowRoot); } };
  walk(document);
  return out;
})()"""
)


async def shown(s: Session) -> set[str] | None:
    """SHOWN_JS in the top frame's isolated world; None when it fails."""
    try:
        got = await s.traversal.reader.evaluate_top(SHOWN_JS)
    except Exception:
        return None
    return set(got) if isinstance(got, list) else None


# Open dialogs (4.E's walk extra; 2.D's pass T). The path is the dialog's
# identity across steps: a path cut short let two
# dialogs share one, so the second never counted as new (f09).
DIALOGS_JS = (
    "() => {"
    + PATH_JS
    + """
  const vis = (el) => el.checkVisibility
    ? el.checkVisibility({ visibilityProperty: true })
    : el.getClientRects().length > 0;
  const sel = 'dialog[open], [role=dialog], [role=alertdialog]';
  // How much of the window its box covers, and whether it is modal (a
  // dialog opened with showModal(), or aria-modal="true"): 4.E J1 and 5.D
  // J2's covering guard (4.E 1.2.0, 5.D 1.2.0).
  const vw = innerWidth, vh = innerHeight;
  const share = (el) => {
    const r = el.getBoundingClientRect();
    const w = Math.max(0, Math.min(vw, r.right) - Math.max(0, r.left));
    const h = Math.max(0, Math.min(vh, r.bottom) - Math.max(0, r.top));
    return vw && vh ? Math.round((w * h) / (vw * vh) * 100) / 100 : 0;
  };
  const modal = (el) => {
    try { if (el.matches(':modal')) return true; } catch (e) {}
    return el.getAttribute('aria-modal') === 'true';
  };
  return Array.from(document.querySelectorAll(sel)).filter(vis)
    .map((el) => ({ css: path(el), name: el.getAttribute('aria-label') || '',
      share: share(el), modal: modal(el) }));
}"""
)

# Positioned layers over a quarter of the window or more (5.D J2's covering
# guard, 1.2.0): a panel laid over the page need not be a dialog, and white
# on white changes few pixels. Visible ones only; the path is their identity.
OVERLAYS_JS = (
    "() => {"
    + PATH_JS
    + """
  const vw = innerWidth, vh = innerHeight, out = [];
  if (!vw || !vh || !document.body) return out;
  for (const el of document.body.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (!['fixed', 'absolute', 'sticky'].includes(cs.position)) continue;
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (Number(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect();
    const w = Math.max(0, Math.min(vw, r.right) - Math.max(0, r.left));
    const h = Math.max(0, Math.min(vh, r.bottom) - Math.max(0, r.top));
    const share = (w * h) / (vw * vh);
    if (share < 0.25) continue;
    out.push({ css: path(el), share: Math.round(share * 100) / 100, modal: false });
  }
  return out;
}"""
)

# "Most of the window" (4.E J1, 5.D J2): a dialog or change covering more
# than this share of the viewport, or a modal one, is never content_only.
COVER_MOST = 0.5


def cover(dialogs: list[dict[str, Any]]) -> dict[str, Any]:
    """The largest share of the window the given dialogs cover, and whether
    any is modal (DIALOGS_JS items). Facts; the checks' rows read them."""
    return {
        "share": max((float(d.get("share") or 0) for d in dialogs), default=0.0),
        "modal": any(bool(d.get("modal")) for d in dialogs),
    }


def changed_share(a: Path, b: Path, delta: int = 8) -> float | None:
    """Share of the pixels that differ (any channel by `delta` or more)
    between two pictures of the same viewport; None if they cannot be
    compared. 5.D J2's covering guard for a change that is not a dialog."""
    from PIL import Image, ImageChops

    try:
        x = Image.open(a).convert("RGB")
        y = Image.open(b).convert("RGB")
    except Exception:
        return None
    if x.size != y.size:
        return None
    r, g, bl = ImageChops.difference(x, y).split()
    mx = ImageChops.lighter(ImageChops.lighter(r, g), bl)
    changed = mx.point(lambda v: 255 if v >= delta else 0).histogram()[255]
    return round(changed / (x.size[0] * x.size[1]), 2)


# Before the action, the page is watched this long; DOM changes in it are
# page noise (animation), so an effect of only DOM changes is unreliable.
NOISE_MS = 300

# A browser call that has not answered by then is abandoned (headed Chrome can
# leave one waiting when the action navigates the page); the page count then
# decides alone, as before.
CDP_TIMEOUT_S = 2.0


# Which audio and video elements are playing, in document order (shadow roots
# included). Read in TOBI's isolated world, per frame (4.A, media start).
MEDIA_JS = """() => {
  const out = [];
  const walk = (root) => {
    for (const m of root.querySelectorAll('audio,video'))
      out.push(!m.paused && !m.ended);
    for (const el of root.querySelectorAll('*'))
      if (el.shadowRoot) walk(el.shadowRoot);
  };
  walk(document);
  return out;
}"""


async def playing_media(s: Session) -> set[tuple[str, int]]:
    """(frame, index) of every audio or video element that is playing, in
    every frame TOBI can read. A frame it cannot read contributes nothing."""
    out: set[tuple[str, int]] = set()
    r = s.traversal.reader
    try:
        frames = await r.frames()
    except Exception:
        return out
    for fid, sess, ctx in frames:
        try:
            states = await r.call_in(sess, ctx, MEDIA_JS)
        except Exception:
            continue
        out |= {(fid, i) for i, on in enumerate(states) if on}
    return out


class Effect(BaseModel):
    kinds: list[str] = Field(default_factory=list)
    mutations: int = 0
    noise: int = 0
    url: str | None = None  # where a navigation (or a fragment change) went

    @property
    def any(self) -> bool:
        return bool(self.kinds)

    @property
    def unreliable(self) -> bool:
        return self.noise > 0 and self.kinds == ["dom"]


async def snapshot(s: Session, media: bool = False) -> dict[str, Any]:
    page = s.page
    focus = None
    try:
        st, _ = await s.traversal.reader.read()
        focus = st.path_key
    except Exception:
        pass
    try:
        dialogs = await page.evaluate(
            "() => Array.from(document.querySelectorAll("
            "'dialog[open],[role=dialog],[role=alertdialog]'))"
            ".filter((e) => e.checkVisibility()).length"
        )
    except Exception:
        dialogs = None
    return {
        "url": page.url,
        "frames": sorted(f.url for f in page.frames),
        "pages": len(s.traversal.context.pages),
        "focus": focus,
        "dialogs": dialogs,
        "media": await playing_media(s) if media else set(),
    }


class _Opened:
    """Pages the tested page opens, as the browser creates them. Counting
    context.pages after the settle can miss one on Windows, where a new page
    joins the list later or not at all; page script cannot spoof the
    browser's own event. `ok` is False when discovery did not start, and
    then only the page count decides."""

    def __init__(self, s: Session):
        self._s = s
        self._cdp: Any = None
        self.ids: set[str] = set()
        self.ok = False

    async def __aenter__(self) -> _Opened:
        def wait(call: Awaitable[Any]) -> Awaitable[Any]:
            return asyncio.wait_for(call, CDP_TIMEOUT_S)

        try:
            cdp = await wait(self._s.traversal.context.new_cdp_session(self._s.page))
            self._cdp = cdp
            info = await wait(cdp.send("Target.getTargetInfo"))
            own = info["targetInfo"]["targetId"]

            def created(ev: dict) -> None:
                info = ev.get("targetInfo", {})
                if info.get("type") == "page" and info.get("openerId") == own:
                    self.ids.add(info["targetId"])

            cdp.on("Target.targetCreated", created)
            await wait(cdp.send("Target.setDiscoverTargets", {"discover": True}))
            # Pages that already exist are reported before this answer; after
            # a timeout they could arrive late and read as new.
            self.ok = True
        except Exception:
            pass  # the page count below still applies
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._cdp is not None:
            try:
                await asyncio.wait_for(self._cdp.detach(), CDP_TIMEOUT_S)
            except Exception:
                pass


async def observe(
    s: Session,
    quiet_ms: int,
    act: Callable[[], Awaitable[None]],
    own: str | None,
    submits: bool = False,
    noise_ms: int = NOISE_MS,
    media: bool = False,
    popups: bool = False,
) -> Effect:
    """What an action changes (spec: Terms, effect). `own` is the path key of
    the element acted on: focus moving onto it (a click) is not an effect.
    `submits` (5.D) also records form submissions as the effect "submit";
    off for 4.A and 4.B, whose specs do not read it. `noise_ms` 0 skips the
    noise window (5.D's leave step reuses the one its completion measured).
    `media` (4.A only, spec term *media start*) also records "media_start":
    an audio or video element that was not playing before the action and is
    after it. Off elsewhere, so 4.B and 5.D keep the effect they cite.
    `popups` (4.A only, C-01) also records "js_dialog" (alert, confirm,
    prompt: the browser closes one at once when nobody listens, so the
    before/after read never saw it) and "download"."""
    page = s.page
    await settle(page, quiet_ms)
    before = await snapshot(s, media)
    sub0 = len(await submissions(page)) if submits else 0
    m0, *_ = await _read_logs(page)
    if noise_ms:
        await page.wait_for_timeout(noise_ms)
    m1, *_ = await _read_logs(page)
    popped: list[str] = []

    async def on_dialog(d: Any) -> None:
        popped.append("js_dialog")
        try:
            await d.dismiss()  # what the browser does with no listener
        except Exception:
            pass

    def on_download(_d: Any) -> None:
        popped.append("download")

    if popups:
        page.on("dialog", on_dialog)
        page.on("download", on_download)
    try:
        async with _Opened(s) as opened:
            # Enabling discovery reports pages that already exist; only pages
            # created after this point are the action's.
            earlier = set(opened.ids)
            await act()
            await settle(page, quiet_ms)
            after = await snapshot(s, media)
            sub1 = len(await submissions(page)) if submits else 0
            m2, *_ = await _read_logs(page)
            new_windows = opened.ids - earlier if opened.ok else set()
    finally:
        if popups:
            page.remove_listener("dialog", on_dialog)
            page.remove_listener("download", on_download)
    e = Effect(mutations=max(0, m2 - m1), noise=max(0, m1 - m0))
    if without_fragment(after["url"]) != without_fragment(before["url"]):
        e.kinds.append("navigation")
        e.url = after["url"]
    elif after["url"] != before["url"]:
        # Only the #fragment changed: the same page (4.E, 5.D, reveal ignore
        # it), but it is something a click did (4.A: a card that jumps to a
        # section is functional, C-03 regression found by 4a/f07).
        e.kinds.append("fragment")
        e.url = after["url"]
    elif [without_fragment(u) for u in after["frames"]] != [
        without_fragment(u) for u in before["frames"]
    ]:
        e.kinds.append("frame_navigation")
    if sub1 > sub0:
        e.kinds.append("submit")
    if new_windows or after["pages"] > before["pages"]:
        e.kinds.append("new_page")
    if after["dialogs"] != before["dialogs"]:
        e.kinds.append("dialog")
    for k in ("js_dialog", "download"):
        if k in popped:
            e.kinds.append(k)
    f = after["focus"]
    if f != before["focus"] and not (own and f and f.startswith(own)):
        e.kinds.append("focus")
    if after["media"] - before["media"]:
        e.kinds.append("media_start")
    if e.mutations > 0:
        e.kinds.append("dom")
    return e
