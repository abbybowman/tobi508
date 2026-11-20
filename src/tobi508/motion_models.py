"""What pass T records: the data shapes of the motion watch.

Pass T (motion.py) loads the recorded page once and watches it with no input;
these Pydantic models are the facts it writes down: the page's elements in
reading order, the regions whose pixels changed and what changed in each, DOM
changes, timers, media, dialogs, focus moves and polls, the clock check's
result, and the mechanism probe's evidence (filled by mechanism.py). They hold
facts only, never an outcome: the 2.A-2.D and 3.A checks read them and their
rules decide. Kept apart from the code that collects them so a check, a test
or a reader can see the whole record without reading the browser code.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from tobi508.models import Part

# TT: "more than 5 seconds" (2.B) and "more than 3 seconds" (2.A); the
# watch is 6.5 s at the top of the page (plan Q3).
WATCH_S = 6.5


class Element(BaseModel):
    i: int  # position in reading order, iframe content inline
    frame: int  # index in page.frames
    kind: str  # text | heading | image | control
    role: str = ""
    name: str = ""
    css: str
    box: list[int] = Field(default_factory=list)  # page x, y, width, height
    stop: bool = False  # natively tabbable or tabindex >= 0
    href: str | None = None  # a link's href attribute as written
    frame_url: str = ""  # "" in the top page


class Change(BaseModel):
    """One DOM change inside a region during the watch (2.D spec, Terms)."""

    t: float  # seconds from the start of the watch
    kind: str  # text | children | src
    attr: str | None = None
    css: str = ""  # the changed element ("" once it left the page)
    before: str = ""
    after: str = ""
    live: str | None = None  # the live region around it when it changed
    live_at_start: bool = False  # that live region was there at 0 s


class Animation(BaseModel):
    css: str = ""
    name: str = ""
    infinite: bool = False
    iterations: float = 0
    duration_ms: int = 0
    state: str = ""


class Region(BaseModel):
    """Tiles that changed together, mapped to the smallest element covering
    them (2.C spec, Terms). `kinds` follows the Terms: "updating" when what
    it shows changed between reads, "moving" when its pixels changed but
    what it shows did not, or its children moved."""

    key: str  # "<frame>|<css>"
    frame: int  # index in page.frames (0: the top page)
    frame_url: str = ""
    css: str
    tag: str = ""
    content_css: str  # what the mechanism windows are counted around
    carousel: bool = False  # the region is a carousel (2.C Terms)
    parts: list[str] = Field(default_factory=list)  # elements merged into it
    covered: bool = True  # an element covered every changed tile
    box: list[int] = Field(default_factory=list)  # page x, y, width, height
    changed_at: list[float] = Field(default_factory=list)  # frame times
    tiles: int = 0
    sigs: list[int | None] = Field(default_factory=list)  # per read
    colors: list[int | None] = Field(default_factory=list)  # per read (2.B)
    transforms: list[int | None] = Field(default_factory=list)  # per read
    states: int = 0  # distinct looks of its box over the frames (top page; capped)
    # Most pixels of its box that differ visibly (by VISIBLE_DELTA or more)
    # between two frames; None when its box was not read (not the top page).
    visible_px: int | None = None
    # pixels (changed in the frames), or what showed motion the frames could
    # not: animation (over 5 s of active time), marquee or video (2.B Terms),
    # or dom: content the DOM log saw keep changing off screen (2.C)
    source: str = "pixels"
    source_detail: str = ""
    updated: bool = False
    children_moved: bool = False
    kinds: list[str] = Field(default_factory=list)
    text: str = ""  # its text at the end, capped
    connected: bool = True
    changes: list[Change] = Field(default_factory=list)
    attr_changes: int = 0
    attr_list: list[Change] = Field(default_factory=list)  # class and other attributes
    focus_in: list[float] = Field(default_factory=list)  # focus moved into it, s
    animations: list[Animation] = Field(default_factory=list)
    period_s: float | None = None  # median time between pixel changes
    scrolled: bool = False  # found by the scrolled watch (plan Q3)
    live_off: bool = False  # inside or holding aria-live="off" (2.D note)
    elements: list[int] = Field(default_factory=list)  # Element.i inside it
    # With no element inside: the first element after it in reading order
    # (len(elements) when none follows), so its windows can still be counted.
    next_element: int | None = None
    # Its changed pixels over the watch, one box per 20 px tile (x0, y0, x1,
    # y1 in the top page's viewport), capped: which elements really changed.
    changed_boxes: list[list[int]] = Field(default_factory=list)
    # Two pictures cut around it, about CROP_GAP_S apart (run-folder paths),
    # when no frame shows it whole: below the first screen, or found by the
    # scrolled watch (judge eval run 16).
    crops: list[str] = Field(default_factory=list)


class LiveRegion(BaseModel):
    frame: int
    css: str
    role: str = ""
    live: str = ""


class Timer(BaseModel):
    frame: int
    kind: str  # interval | timeout
    ms: int
    count: int = 1


class Media(BaseModel):
    frame: int
    frame_url: str = ""  # "" in the top page; the probe finds the frame by it
    at: float  # read time, seconds from the start of the watch
    css: str
    tag: str
    shadow: bool = False  # inside a web component (an open shadow root)
    paused: bool
    muted: bool
    volume: float
    time: float
    duration: float | None = None
    loop: bool = False
    autoplay: bool = False
    controls: bool = False
    error: int | None = None
    decoded: int | None = None
    src: str = ""
    urls: list[str] = Field(default_factory=list)
    total: int = 0  # audio and video elements in the frame (the read lists 20)


class Poll(BaseModel):
    """Requests repeated to one address: in the HAR, or made during pass T
    (item 10: the replay answers every repeat with the first response, so
    the page cannot show new data). Recording stops once the network is
    idle, so a page polling every second may show only once in the HAR."""

    url: str
    count: int
    gap_ms: int | None = None  # median gap between repeats
    source: str = "har"  # har (while recording) | watch (requests in pass T)


class FocusMove(BaseModel):
    t: float
    css: str | None = None
    type: str = "focusin"


class Dialog(BaseModel):
    css: str
    name: str = ""
    role: str = ""
    text: str = ""
    keyboard: bool = False  # focus is in it, or it holds a focusable element


class TimerCheck(BaseModel):
    """The clock check (2.C spec 1.2.0, section 2): timers longer than the
    watch, run past on one more fresh load with the page's clock installed.
    Facts only; 2.C's hints read `cleared`."""

    ran: bool = False
    # True only when every long timer pass T saw was set again, the clock ran
    # past the longest, no request was made, and nothing on the page changed.
    cleared: bool = False
    why: str = ""  # plain words: why the timers stay a sign ("" when cleared)
    timers_ms: list[int] = Field(default_factory=list)  # pass T's, run past
    advanced_ms: int = 0
    requests: int = 0
    changed: list[str] = Field(default_factory=list)  # screen, text, ...
    seconds: float = 0.0


class MotionPass(BaseModel):
    ok: bool = True
    error: str = ""
    watch_s: float = WATCH_S
    browser: str = ""  # the browser that ran pass T (browser.MOTION_BROWSER)
    frames: list[float] = Field(default_factory=list)  # times of each frame
    shots: list[str] = Field(default_factory=list)  # run-folder paths
    reads: list[float] = Field(default_factory=list)  # times of the reads
    viewport: list[int] = Field(default_factory=list)  # width, height
    regions: list[Region] = Field(default_factory=list)
    regions_capped: bool = False
    page_changes: list[float] = Field(default_factory=list)  # most of it changed
    unmapped_tiles: int = 0  # changed tiles with no element (a frame not read)
    live_regions: list[LiveRegion] = Field(default_factory=list)  # at 0 s
    dialogs_at_start: list[str] = Field(default_factory=list)
    dialogs_opened: list[Dialog] = Field(default_factory=list)
    focus_moves: list[FocusMove] = Field(default_factory=list)
    timers: list[Timer] = Field(default_factory=list)
    audio_connects: int = 0
    media: list[Media] = Field(default_factory=list)
    # Media that played on this load, attached to a document or not (the play
    # hook, count.py), and how many of them `media` lists (guard CN, N-01).
    played: Part | None = None
    played_listed: Part = Field(default_factory=Part)
    # Image addresses the animated-image read examined (at most
    # IMAGE_READ_MAX, each in the recording, and decoded or known not to
    # animate), for guard CN; `image_srcs_read` lists them, and
    # `inventory_images_read` is how many of the inventory's addresses are
    # among them (set by 2.B and 3.A once the inventory exists).
    images_read: int = 0
    image_srcs_read: list[str] = Field(default_factory=list)
    inventory_images_read: int | None = None
    polls: list[Poll] = Field(default_factory=list)
    carousels: list[str] = Field(default_factory=list)  # "<frame>|<css>" at 0 s
    blink_markup: bool = False  # <blink> or text-decoration: blink (2.B note)
    # Below the first screen, not in a region (plan Q3): observed for
    # scrolling into view, or carousels. The scrolled watch looks at the first.
    below: list[str] = Field(default_factory=list)
    # Walk steps whose DOM never settled (2.C A2's walk cross-check), set by
    # the checks from ctx.cache["walk_unsettled"] once the walk has run.
    walk_unsettled: int = 0
    scrolled_watch: str | None = None  # what the scrolled watch scrolled to
    # G152: each animated image's frames, one play-through, loops (-1:
    # forever) and total (None: forever), decoded from the recording.
    animated_images: list[dict[str, Any]] = Field(default_factory=list)
    audio_states: list[str] = Field(default_factory=list)  # Web Audio contexts
    iframes: list[str] = Field(default_factory=list)  # iframe sources, every frame
    # Peak level of each media source's recorded bytes, in dBFS, decoded in a
    # tool page (never the tested page); None when it could not be decoded.
    loudness: dict[str, float | None] = Field(default_factory=dict)
    # The media store's index from the recording (capture.media_index):
    # url, size, type, file (None when not stored) and over_cap.
    media_store: list[dict[str, Any]] = Field(default_factory=list)
    dropped_changes: int = 0
    frames_read: int = 0  # document frames read (the top page included)
    elements: list[Element] = Field(default_factory=list)  # at 0 s
    elements_truncated: bool = False
    # 3.A's triggers (3.A spec section 2): callbacks of timers under 334 ms
    # and of requestAnimationFrame that changed the page or drew on a canvas
    # (frame, t in s from the start of the watch, kind), capped; and running
    # animations whose colour, opacity, visibility or filter changes more
    # than 3 times a second.
    fast_callbacks: list[dict[str, Any]] = Field(default_factory=list)
    fast_animations: list[dict[str, Any]] = Field(default_factory=list)
    # The clock check, when it ran: set by timer_check_shared.
    timer_check: TimerCheck | None = None


# ── Mechanism probe evidence (2.C spec section 2; 2.A and 2.B use it) ──────
# Filled by mechanism.probe; an instance it did not reach has
# `probed=False`, and the checks' rows say so (K7).


class Candidate(BaseModel):
    element: int  # Element.i
    window: str  # top | before | after | inside
    kind: str  # control | text
    # stopped | slowed | no_effect | unreliable | unreachable | untried, or not
    # pressed: field (needs a value, K5) | not_operable (a link that goes
    # somewhere: following it is not pausing)
    result: str = "untried"
    focus_only: str | None = None  # the focus-only probe's result, if run
    key: str | None = None  # a key combination from J2 that was pressed
    keys: str = ""  # how to reach it ("Tab 4 times, then Enter")


class Probe(BaseModel):
    """The mechanism probe for one content (an instance)."""

    probed: bool = False
    candidates: list[Candidate] = Field(default_factory=list)
    reads_failed: bool = False
    untried: int = 0  # controls not tried (time, or the per-content cap)
    cannot_place: bool = False  # no element inside the content: windows unknown
    cannot_try: str = ""  # K5: a mechanism the tool may not try, named
