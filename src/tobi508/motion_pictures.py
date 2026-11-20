"""Pictures of the regions that moved during pass T.

After the watch, pass T (motion.py) needs two kinds of picture evidence for
each region whose pixels changed: crops, two screenshots cut from the whole
page around a region the viewport frames do not show whole, a second apart,
for an open question a person or judge looks at; and states, how many
distinct looks a region's box had across the frames and how many pixels
visibly differed, which 2.B's rules read (two states blink). Image work only;
it decides nothing.
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageChops
from playwright.async_api import Page

from tobi508.motion_models import MotionPass, Region
from tobi508.traverse import screenshot

CROP_PAD = 40  # CSS px around a region in its crop
CROP_MIN = (320, 200)  # a crop's least size, for some context around it
CROP_GAP_S = 1.0  # between a region's two crops, as between J1's two frames
CROP_REGIONS = 6


async def _crops(
    page: Page, out: MotionPass, shots: Path, rel: Path | None, prefix: str, every: bool
) -> None:
    """Two pictures cut from the whole page around each top-page region the
    frames do not show whole (or, after the scrolled watch, `every` region),
    CROP_GAP_S apart and with animations running. Coordinates:
    region boxes are in the viewport as read, so the scroll is added."""
    vw, vh = (out.viewport + [0, 0])[:2] if out.viewport else (0, 0)

    def whole(b: list[int]) -> bool:
        return b[0] >= 0 and b[1] >= 0 and b[0] + b[2] <= vw and b[1] + b[3] <= vh

    todo = [
        r
        for r in out.regions
        if r.frame == 0
        and len(r.box) == 4
        and r.box[2] > 0
        and r.box[3] > 0
        and (every or not whole(r.box))
    ][:CROP_REGIONS]
    if not todo:
        return
    sx, sy = await page.evaluate("() => [scrollX, scrollY]")
    clips = []
    for r in todo:
        x, y, w, h = r.box
        cw, ch = max(w + 2 * CROP_PAD, CROP_MIN[0]), max(h + 2 * CROP_PAD, CROP_MIN[1])
        cx = max(0, x + sx + w / 2 - cw / 2)
        cy = max(0, y + sy + h / 2 - ch / 2)
        clips.append((r, {"x": cx, "y": cy, "width": cw, "height": ch}))
    for k in range(2):
        if k:
            await page.wait_for_timeout(CROP_GAP_S * 1000)
        for i, (r, clip) in enumerate(clips):
            path = shots / f"{prefix}-crop{i + 1}-{'ab'[k]}.png"
            await screenshot(page, path=str(path), clip=clip, full_page=True)
            r.crops.append(str(path.relative_to(rel)) if rel else str(path))


MAX_STATES = 10


VISIBLE_DELTA = 8  # of 255 in a channel: a change smaller than this is not seen


def _visible_px(a: Image.Image, b: Image.Image) -> int:
    """Pixels whose colour differs between two same-size pictures by at least
    VISIBLE_DELTA in some channel."""
    r, g, bl = ImageChops.difference(a, b).split()
    mx = ImageChops.lighter(ImageChops.lighter(r, g), bl)
    return mx.point(lambda v: 255 if v >= VISIBLE_DELTA else 0).histogram()[255]


def _states(pngs: list[bytes], regions: dict[str, Region]) -> None:
    """How many distinct looks each top-page region's box had over the
    frames (2.B: two states blink; three or more is C1), and the most pixels
    of its box that differ visibly between two frames (`visible_px`: from the
    first frame, or the frame before; 2.B 1.3.0)."""
    boxes = {
        k: r.box
        for k, r in regions.items()
        if r.frame == 0 and len(r.box) == 4 and r.box[2] > 0 and r.box[3] > 0
    }
    if not boxes or not pngs:
        return
    seen: dict[str, set[bytes]] = {k: set() for k in boxes}
    first: dict[str, Image.Image] = {}
    last: dict[str, Image.Image] = {}
    visible: dict[str, int] = {}
    for png in pngs:
        img = Image.open(io.BytesIO(png)).convert("RGB")
        w, h = img.size
        for k, (x, y, bw, bh) in boxes.items():
            crop = (max(0, x), max(0, y), min(w, x + bw), min(h, y + bh))
            if crop[0] >= crop[2] or crop[1] >= crop[3]:
                continue
            part = img.crop(crop)
            if len(seen[k]) <= MAX_STATES:
                seen[k].add(part.tobytes())
            for other in (first.get(k), last.get(k)):
                if other is not None and other.size == part.size:
                    visible[k] = max(visible.get(k, 0), _visible_px(other, part))
            first.setdefault(k, part)
            visible.setdefault(k, 0)
            last[k] = part
    for k, s in seen.items():
        regions[k].states = len(s)
        if k in visible:
            regions[k].visible_px = visible[k]
