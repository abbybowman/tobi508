"""Sound and animated images, decoded from the page's recording.

Two questions pass T cannot answer by watching pixels: is a media file's sound
audible (its peak loudness), and does an animated image (GIF, APNG, animated
WebP) play for more than 5 seconds. Both are answered from the bytes in the
recording (the HAR), decoded with the browser's own decoders in a blank tool
page of the same browser, never in the tested page, so no page script runs.
Also here: which of the page inventory's image addresses were read, for the
guard that holds 2.B and 3.A while images are left unread. Pass T (motion.py)
calls these; flashcap.py and checks/t3a.py reuse the tool page and the image
type sniffing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext

from tobi508.motion_models import MotionPass

# Loudness (2.A spec Terms; plan item 4): ACT's own "silent" video has a real
# audio track (-91 dB), so a track's presence is not sound. Decoded with
# OfflineAudioContext in a blank tool page of the same browser, never the
# tested page; audible is a peak above -40 dBFS.
LOUDNESS_MAX_BYTES = 20_000_000
_LOUDNESS_JS = """async (b64) => {
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const ctx = new OfflineAudioContext(1, 1, 44100);
  try {
    const buf = await ctx.decodeAudioData(bytes.buffer);
    let peak = 0;
    for (let ch = 0; ch < buf.numberOfChannels; ch++) {
      const d = buf.getChannelData(ch);
      for (let i = 0; i < d.length; i++) { const v = Math.abs(d[i]); if (v > peak) peak = v; }
    }
    return peak > 0 ? 20 * Math.log10(peak) : -200;
  } catch (e) { return null; }
}"""


async def _loudness(context: BrowserContext, har: Path, out: MotionPass) -> None:
    import base64

    from tobi508.capture import media_body

    srcs = sorted({m.src for m in out.media if m.src.startswith(("http:", "https:"))})
    if not srcs:
        return
    tool = await context.new_page()  # about:blank: no page script runs here
    try:
        for src in srcs[:10]:
            body = media_body(har, src)
            if body is None or len(body) > LOUDNESS_MAX_BYTES:
                out.loudness[src] = None
                continue
            got = await tool.evaluate(_LOUDNESS_JS, base64.b64encode(body).decode())
            out.loudness[src] = None if got is None else round(float(got), 1)
    finally:
        await tool.close()


TOOL_URL = "http://localhost/a11y-tool"


async def _secure_tool_page(page):
    """A blank page in its own fresh context of the same browser, at
    http://localhost (a secure context: ImageDecoder exists only there, not
    on about:blank), answered by a route: no network, no page script."""
    ctx = await page.context.browser.new_context()
    await ctx.route(
        TOOL_URL,
        lambda r: r.fulfill(
            status=200,
            content_type="text/html",
            body="<!doctype html><title>tool</title>",
        ),
    )
    tool = await ctx.new_page()
    await tool.goto(TOOL_URL)
    return ctx, tool


# G152 (2.B Terms): an animated image's frames, delays and loop count, from
# its recorded bytes, decoded with ImageDecoder in a blank tool page.
_IMAGE_JS = """async ([b64, type]) => {
  if (!window.ImageDecoder) return null;
  const bytes = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  try {
    const d = new ImageDecoder({ data: bytes, type });
    await d.tracks.ready;
    const t = d.tracks.selectedTrack;
    const n = t.frameCount;
    let once = 0, min = null;
    for (let i = 0; i < n && i < 500 && n > 1; i++) {
      const r = await d.decode({ frameIndex: i });
      once += (r.image.duration || 0) / 1000;
      // Chrome shows a frame of 10 ms or less for 100 ms (3.A).
      const ms = (r.image.duration || 0) / 1000;
      const shown = ms <= 10 ? 100 : ms;
      min = min === null ? shown : Math.min(min, shown);
      r.image.close();
    }
    return { frames: n, once_ms: Math.round(once), reps: t.repetitionCount === Infinity ? -1 : t.repetitionCount, min_ms: min === null ? null : Math.round(min) };
  } catch (e) { return null; }
}"""
IMAGE_MAX_BYTES = 5_000_000
MOVING_IMAGE_MS = 5000  # TT: "more than 5 seconds"


def _image_type(body: bytes) -> str | None:
    if body[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if body[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if body[:4] == b"RIFF" and body[8:12] == b"WEBP":
        return "image/webp"
    return None


# At most this many image addresses are read per page (was 30).
# Most are known not to animate from their first bytes and cost a zip read;
# only GIFs and animated PNG or WebP files are decoded.
IMAGE_READ_MAX = 300


def _png_animated(body: bytes) -> bool:
    """A PNG is animated (APNG) when an `acTL` chunk comes before the first
    `IDAT`. A file that cannot be walked counts as animated (it is decoded,
    or left unread when too large)."""
    i = 8
    while i + 8 <= len(body):
        n = int.from_bytes(body[i : i + 4], "big")
        kind = body[i + 4 : i + 8]
        if kind == b"acTL":
            return True
        if kind == b"IDAT":
            return False
        i += 12 + n
    return True


def _webp_animated(body: bytes) -> bool:
    """A WebP is animated when its extended header sets the animation flag
    or it has an `ANIM` chunk; a simple (VP8 or VP8L) file is not."""
    if body[12:16] in (b"VP8 ", b"VP8L"):
        return False
    if body[12:16] == b"VP8X":
        return bool(body[20] & 0x02) or b"ANIM" in body[:4096]
    return True


def _can_animate(body: bytes) -> str | None:
    """The type to decode when the file may animate, else None: JPEG, SVG
    and the like, a PNG with no `acTL` and a WebP with no animation are done
    from their first bytes, whatever their size (2.B 1.5.0: a 14 MB JPEG was
    skipped on 8 of round 1's pages for its size alone)."""
    kind = _image_type(body)
    if kind == "image/png" and not _png_animated(body):
        return None
    if kind == "image/webp" and not _webp_animated(body):
        return None
    return kind


async def _read_images(
    page, har: Path, out: MotionPass, srcs: list[str], late: bool = False
) -> dict[str, str]:
    """Read each address once: from the recording (redirects followed), done
    when its type cannot animate, decoded in a tool page otherwise. Returns
    the animated images that play for more than 5 s in all (G152), with the
    figures as a detail, and records every decoded one in
    `out.animated_images`. `late`: read after the end-of-pass scroll, when no
    region can be made for an image: one that plays more than 5 s is then
    left unread, so guard CN holds 2.B and 3.A for it."""
    import base64

    from tobi508.capture import media_body

    found: dict[str, str] = {}
    tool = tool_ctx = None
    try:
        for src in srcs:
            if src in out.image_srcs_read or len(out.image_srcs_read) >= IMAGE_READ_MAX:
                continue
            body = media_body(har, src)
            if not body:
                continue  # not in the recording: unread (guard CN)
            kind = _can_animate(body)
            if kind is None:
                out.image_srcs_read.append(src)
                continue
            if len(body) > IMAGE_MAX_BYTES:
                continue  # may animate, too large to decode: unread
            if tool is None:
                tool_ctx, tool = await _secure_tool_page(page)
            got = await tool.evaluate(
                _IMAGE_JS, [base64.b64encode(body).decode(), kind]
            )
            if got is None:
                continue  # could not be decoded: unread
            if got["frames"] < 2:
                out.image_srcs_read.append(src)
                continue
            total = None if got["reps"] < 0 else got["once_ms"] * (got["reps"] + 1)
            out.animated_images.append({"src": src[:500], **got, "total_ms": total})
            long = total is None or total > MOVING_IMAGE_MS
            if long and late:
                continue  # no region for it: unread
            out.image_srcs_read.append(src)
            if long:
                found[src] = f"animated image, {got['frames']} frames, " + (
                    "loops forever" if total is None else f"{total / 1000:g} s in all"
                )
    finally:
        if tool_ctx is not None:
            await tool_ctx.close()
        out.images_read = len(out.image_srcs_read)
    return found


def match_inventory(ctx: Any, mp: MotionPass) -> None:
    """How many of the inventory's image addresses pass T read:
    guard CN compares that, not pass T's own count, so addresses pass T read
    that the inventory never saw cannot stand in for ones it did."""
    count = getattr(ctx, "cache", {}).get("count")
    srcs = getattr(count, "image_srcs", None)
    if not srcs:
        return
    # An address the inventory saw that pass T's page never showed (a slide
    # never shown, an image another browser loads sooner): read from the
    # recording. A type that cannot animate is done from its first bytes; one
    # that can is left unread, so guard CN holds the page.
    har = getattr(ctx, "rel", None)
    har = har / "evidence" / "page.har.zip" if har is not None else None
    if har is not None and har.exists():
        from tobi508.capture import media_body

        for src in srcs:
            if src in mp.image_srcs_read or len(mp.image_srcs_read) >= IMAGE_READ_MAX:
                continue
            body = media_body(har, src)
            if body and _can_animate(body) is None:
                mp.image_srcs_read.append(src)
        mp.images_read = len(mp.image_srcs_read)
    mp.inventory_images_read = len(set(srcs) & set(mp.image_srcs_read))


def images_read(mp: MotionPass) -> int:
    """Image addresses read, for guard CN: of the inventory's when matched."""
    return (
        mp.images_read if mp.inventory_images_read is None else mp.inventory_images_read
    )
