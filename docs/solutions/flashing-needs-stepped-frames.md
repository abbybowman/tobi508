# Flashing needs stepped frames, not screenshots (3.A)

**What happened.** Real-time screenshots of a strobe that changes every animation frame read 1-2.5 flashes a second instead of about 30 ([research section 4](../research/2026-11-03-3a-flashing.md)): screenshots arrive at 27-28 a second and alias a fast alternation down to a slow one. A reading under 3 a second looks like no flashing, a false DOES NOT APPLY. A CDP screencast is better (about 55 frames a second) but drops frames and sends nothing while the page is still, so it can say "something flashes" but never "nothing does".

**What we do now** (`flashcap.py`, spec [3a-flashing.md](../../specs/rules/3a-flashing.md) section 2):

- **The page's own clock is stepped.** A fresh load with Playwright's clock installed and paused before the page loads (`pause_clock`, the pipeline opener's `paused_clock`). Each step runs the clock (timers, `requestAnimationFrame`, `Date`), sets every Web Animation's `currentTime` and every SMIL document's time, and takes one screenshot. 60 steps a second of page time, in whole milliseconds (17, 16, 17), so frame times are exact and every run is the same. Animations that run at the first step started with the load; later ones start at the step that first sees them. Never the wall clock: an animation's own `currentTime` at discovery depends on how long the load took.
- **Real-time media are decoded, not stepped.** Video, animated images and `<marquee>` play by the wall clock, so they are masked out of stepped frames. Images are decoded with `ImageDecoder` at the size the page shows them; video is played at 0.5× with `requestVideoFrameCallback` (every frame, the first 10 s). A marquee cannot be stepped or decoded: NEEDS REVIEW.
- **Triggers first.** Stepping costs about 6-7 s of wall time, so it runs only when pass T saw something fast (fast animations, effectful fast callbacks, short image frames, a video) or the screencast saw flashing. A page with none costs only the screencast.
- **Counting is separate and pure** (`flash.py`, unit-tested on numpy frames in `tests/test_flash.py` with no browser). Most of the coverage lives there; the 16 browser fixtures each run once.

**Things that cost time:**

- `ImageDecoder` reports a GIF frame's raw duration (10 ms reads as 10 ms); Chrome shows frames of 10 ms or less for 100 ms, so the tool applies that rule itself.
- Two plays of a 200 ms GIF are 0.4 s, which never fills a one-second window: images are analyzed over two plays and at least 2 s.
- A transition's time is not the frame of the new state's peak: noise on a plateau moves the peak by up to half a period and put a third change into a one-second window. The time is the frame after the last one still within half the threshold of the old state.
- The screencast's real-time frames jitter by about one transition: a steady 3 a second can read 7. It only escalates to NEEDS REVIEW when it saw more than one transition more than every measurement explains.
- A fine 2 px checkerboard averages out in 4 px cells and in the screencast's small frames; only a pixel sample sees it. Background-position animations had to become a trigger for it.
- `page.screenshot` works with the clock paused; the paused clock reaches out-of-process iframes (full Chromium).

**How we know.** Fixtures f01-f15 and 2.B's marquee page (`tests/test_fixtures_3a.py`), V1-V10 in [_browser-checks.md](../../specs/rules/_browser-checks.md#3a).
