# W-watchers: review of motion.py, mechanism.py, flash.py, flashcap.py

**Overview.** The four files were read in full; flash.py was run on 28 synthetic sequences, the J2 key parser on 54 strings, and the real pipeline on 21 pages. The counting maths in flash.py is correct against WCAG 2.3.1 everywhere it was tried (Table C), and the capture and probe code is careful about failures that raise: most of those end in NEEDS REVIEW. The weak spot is observations that do not raise but see nothing. Five of them end in a wrong DOES NOT APPLY on pages I could write in minutes: a flash below the first screen (W-02), audio started from `new Audio()` (W-03), audio that appears after the 0 s read (W-05), motion that fills most of the viewport (W-07), and a 2.5 Hz blink (W-09). Two more are P1: the event loop is blocked 15-20 s by flash counting (W-01) and anything that starts after 6.5 s is invisible (W-04). The probe's key handling meets CLAUDE.md principle 5 except that "never a key the browser uses" is a 12-item list (W-14). Time: the scrolled watch fires on any IntersectionObserver (+7.6 s, W-08).

Index: P0 W-02, W-03, W-05, W-07, W-09. P1 W-01, W-04. P2 W-06, W-08, W-10, W-11, W-12, W-15, W-16. P3 W-13, W-14, W-17. Tables A (waits), B (failures), C (flash maths), D (key parser) follow the findings. Findings appear in the order they were confirmed, not by severity.

Method notes: end-to-end runs used `runpage.py` with pages in `scratchpad/w/pages/` (belowfold, late, detachedaudio, domaudio, lateaudio, lateaudio2, lateaudio3, fastload, slowload, slowload7, sandboxed, unsandboxed, fullmove, fullcanvas, fullnoise, blink25, heartbeat, noio, io, fullmove); each result quoted is from that run.

## Findings

### W-01 Event loop blocked 15-20 s by flash counting (synchronous numpy on the loop)
- Severity: P1
- Kind: time
- Where: src/tobi508/checks/t3a.py:291 (`flashcap.analyze_stepped(pngs, mask)` called directly inside `async _measure`); src/tobi508/flash.py:522 (`analyze`), flash.py:56 (`linear`)
- What: The stepped capture's 181 PNGs are decoded and counted synchronously on the event loop. A full-screen flash costs about 15 s of CPU (80 ms per frame at 1024 x 768); a 1 px or 2 px pattern about 18-19 s. While it runs nothing else on the loop moves: the other run in the same server, MCP keep-alives, the job's progress line, the walk if it is still going. CLAUDE.md targets a hosted deployment with `MAX_CONCURRENT_RUNS` 2.
- Evidence: ran `flash.analyze` on 181 synthetic 1024 x 768 frames: 14.6 s (black/white 4 Hz), 18.5 s (1 px checkerboard), 19.0 s (2 px checkerboard). cProfile of 91 frames: 8.0 s total, of which `linear` 2.2 s (a `**2.4` over every pixel of every frame; a 256-entry lookup table does the same), `blocks` mean 2.0 s, `window_counts` 1.5 s, `Hysteresis.step` 0.7 s. `analyze_stepped`, `analyze_image` and `analyze_video` are called without `asyncio.to_thread` (grep in t3a.py).
- Fix: run the three `analyze_*` calls in `asyncio.to_thread`; replace `linear` by a uint8 lookup table (about 10x faster); skip the two red passes when no sampled pixel has R/(R+G+B) >= 0.8 (a cheap check on the first pass over the frames).
- Confidence: confirmed (ran)

### W-02 A flash below the first screen is DOES NOT APPLY even though a trigger fired and the capture ran
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/flashcap.py:249 (`page.screenshot(type="png")`, viewport only), flashcap.py:296 (`analyze_stepped`: "nothing changed" returns an empty `Analysis`); src/tobi508/checks/t3a.py:237-300, t3a.py:587-597 (rows A3/A4); spec specs/rules/3a-flashing.md section 1 A4 ("every trigger was measured")
- What: The stepped capture screenshots only the 1024 x 768 viewport at the top of the page. A trigger from pass T (a timer or rAF callback that changes the DOM, or a flashy animation) can sit anywhere in the document. When the flashing element is below the first screen the capture sees an unchanging picture, the source reads "not flashing", nothing is added to `unmeasured`, and row A4 says DOES NOT APPLY: "Nothing on this page flashes more than three times a second". The tool had positive evidence of a flasher (the trigger) and discards it. The screencast net does not help: it also sees only the viewport. 3.A's only non-review outcomes are DNA and NOT TESTED, so this is the "wrong DNA" the TT warns about (1.D relies on it).
- Evidence: ran the real pipeline on a page with a 1000 x 400 px black/white block toggled every 125 ms by `setInterval`, placed 2500 px down (pages/belowfold.html, `runpage.py belowfold.html 3.A`, 23 s). Result: `3.A DNA ['A4'] Nothing on this page flashes...`. evidence/3a.json: `triggers: [{kind: timer, detail: "8 changes in one second (frame 0)"}]`, `stepped.frames 181`, `sources[0].analysis.general.peak 0`, `unmeasured: []`, `screencast.frames 1`.
- Fix: a trigger is only "measured" when the capture saw it flash. Where a trigger fired and the capture found no flashing, add an `Unmeasured` ("something changed quickly that the capture did not show; it may be below the first screen or hidden") so A3 applies. Better: for timer/rAF/animation triggers give the trigger a location (the changed element's path from `M.fast`/`fastAnims`; `fastAnims` already has `css`) and scroll it into view or screenshot with `full_page=True` and a clip for the capture.
- Confidence: confirmed (ran)

### W-03 Audio played from a script (`new Audio(...).play()`) is invisible to pass T: 2.A says DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/motion.py:392 (`M.media` reads only `document.querySelectorAll('video, audio')`); motion.py:153-160 (only `AudioNode.connect` to a destination is hooked); no hook on `HTMLMediaElement.prototype.play`
- What: An `Audio` object that is never attached to the document is the most common way scripts start background music or a notification sound. Pass T never sees it: it is not in the DOM, and it is not a Web Audio node. Nothing is recorded, so 2.A has no audio instance and returns DOES NOT APPLY with the sentence "No audio played by itself for more than 3 seconds". The same hole covers a `<video>` created with `createElement` and not attached (3.A reads videos the same way), and `speechSynthesis.speak()` (never hooked).
- Evidence: page with `const a = new Audio('tone.wav'); a.loop = true; a.play()` and a real 8 s 440 Hz wav (pages/detachedaudio.html). Standalone Playwright with the project's autoplay flag: `play()` resolved (no rejection) and `document.querySelectorAll('audio').length` was 0. Pipeline `runpage.py detachedaudio.html 2.A`: `2.A DNA ['A3','G1'] We watched this page for 6.5 seconds with autoplay allowed. No audio played by itself for more than 3 seconds`. The same audio as `<audio autoplay loop>` (domaudio.html): `2.A FAIL ['A4','a1:K6','G2']`.
- Fix: in `MOTION_INIT_JS` wrap `HTMLMediaElement.prototype.play` (and set `autoplay` on detached elements via a `WeakSet` of elements seen playing) and keep the elements in `M.media()` next to the DOM ones; hook `speechSynthesis.speak`. When a hook cannot cover a class of audio, 2.A's DNA sentence should say what was not looked for.
- Confidence: confirmed (ran)

### W-04 Content that starts after the 6.5 s watch is DOES NOT APPLY for 3.A, 2.A and 2.B; only 2.C turns the timer hook into a hint
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/motion.py:50 (`WATCH_S = 6.5`), motion.py:131-143 (timer hooks record every `setTimeout`/`setInterval` of 1 s or more in `M.timers`); src/tobi508/checks/t2c.py:86-88 (the only reader of `mp.timers`); src/tobi508/checks/t3a.py:237 (A4 on "no trigger"), flashcap.py:46-47 (`LEAD_MAX_MS = 6000`)
- What: Pass T watches 6.5 s; the flash screencast watches 2 s; the stepped capture covers 3 s of page time starting at most 6 s in (and only when a trigger already fired). A flash, blink or sound that begins later is never seen. The timer hook did record that the page set a 9 s timer, but 3.A, 2.A and 2.B ignore `mp.timers`; 2.C turns it into an A2 "NEEDS REVIEW, a person should watch" hint. The TT text for 3.A has no duration, and 2.A/2.B say "3 seconds" / "5 seconds" of the content, not "within the first 6.5 s of the page".
- Evidence: ran `runpage.py late.html 3.A,2.B` (a block toggled every 125 ms starting from a `setTimeout(..., 9000)`): `3.A DNA ['A4']`, `2.B DNA ['A2','G1'] We watched this page for 6.5 seconds`. `grep -n "\.timers" checks/*.py`: only t2c.py:86.
- Fix: sharing `t2c.hints()`' timer rule as is would turn most pages into NEEDS REVIEW (see W-10: any session or heartbeat timer counts). Better: load the page once on 3.A's paused clock (`flashcap.pause_clock`) and `run_for` 30-60 s of page time in coarse steps with a few screenshots; timers, `requestAnimationFrame` and CSS animations then show what the page does later, in seconds of wall time. Finite animations that ended before 6.5 s are also invisible today (`fastAnims` keeps only `playState === 'running'` at the end of the watch).
- Confidence: confirmed (ran)

### W-05 Audio that appears after the 0 s read is never judged as playing: 2.A says DOES NOT APPLY for loud, looping audio
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/motion.py:55 and :1129-1148 (three reads at 0, 3.5 and 6.5 s, media listed per read); src/tobi508/checks/t2a.py:`find_audio` (`first = reads[0]`, `at = nearest read to 3.5 s`, `playing = ... and at.time > first.time`)
- What: An element that does not exist at the 0 s read (inserted by script after load) first appears in the 3.5 s read. `find_audio` then takes that same read as both `first` and `at`, so `at.time > first.time` is false and the audio counts as "not playing"; the 6.5 s read, which shows it playing for 5 s, is never compared. The watcher delivers the facts (`time` 2.18 s then 5.38 s, not paused, not muted); the consumer discards them because of how the reads are paired. The 3 s rule of 2.A is therefore only applied to media that was already in the DOM at 0 s.
- Evidence: pages/lateaudio3.html: a hidden paused `<audio id=a1 preload=auto src=tone.wav>` (so the file is in the recording) and, from `setTimeout(..., 1500)`, `<audio id=a2 autoplay loop src=tone.wav>` (8 s 440 Hz tone, peak -8.7 dBFS). Pass T's media reads: `#a1 paused` at 0.01/3.66/6.87 s; `#a2 paused=false muted=false time=2.18` at 3.66 s and `time=5.38` at 6.87 s. `runpage.py lateaudio3.html 2.A` gave `2.A DNA ['A3','G1'] ... No audio played by itself for more than 3 seconds`. (Without `#a1` the file is not in the recording and the result is NEEDS REVIEW, which is the safe path; see W-12.)
- Fix: compare against the last read the element appears in (`reads[-1].time > reads[0].time`, with at least 1 s between them) rather than the read nearest 3.5 s; or read media every 0.5 s with the frames, which costs one `evaluate` per frame.
- Confidence: confirmed (ran). The row logic is in t2a.py (another reviewer's file); the sparse reads are this file's design.

### W-06 The stepped capture's lead is measured from a different zero than the capture's clock, and is ignored when the screencast also fired
- Severity: P2
- Kind: bug
- Where: src/tobi508/checks/t3a.py:278-283; src/tobi508/motion.py:1256 (`t = (f["at"] - t0_epoch) / 1000`, with `t0_epoch` from `mark0()` after the load and `read_elements`); src/tobi508/flashcap.py:46-47, :221
- What: `lead = min(fast) * 1000 - 200` takes the time of pass T's first fast callback counted from pass T's mark0 (after the page finished loading). The capture's clock starts paused at the load itself, and timers in a paused clock count from when the script set them, so a page that takes N seconds to load makes the lead N seconds too small. Separately, the lead is used only when no animation or screencast trigger exists; with a timer trigger plus the 2 s screencast also firing (which happens when the flash starts within about 2 s after load, or when the screencast catches the late start of a slow load) the lead stays at 100 ms and the 3 s window never reaches a flash that begins at 5 s of page time.
- Evidence: pages/slowload.html (a 3 s synchronous loop in the body, `setTimeout(start 4 Hz flash, 5000)` in the head): the run recorded `triggers: timer 9 changes in one second` and `screencast 4.5 flashes a second`, `stepped.lead_ms = 100`, stepped analysis peak 0, screencast peak 9. Result `3.A NEEDS_REVIEW ['A3'] ... something that flashed while we watched, which our frame-by-frame capture did not show` (the `unexplained` net caught it, so the outcome is safe; the finding is that flashing was found and not measured, so the page cannot get NOT TESTED with the assessment). Same with a 7 s timer (slowload7.html). A fast page with the same 5 s timer (fastload.html) was measured correctly: `3.A NOT_TESTED ['A2','s1:F2']`.
- Fix: record callback times against `performance.timeOrigin` instead of `mark0`, and use the lead whenever a fast-callback trigger exists, taking the later of the lead and the screencast's need (the capture can start at the smaller of the two only if its 3 s covers both; otherwise capture twice or lengthen to cover).
- Confidence: confirmed (ran) for the outcome; likely for the cause.

### W-07 Movement that fills most of the viewport is thrown away as a "page-wide change": 2.B says DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/motion.py:64 (`PAGE_CHANGE = 0.5`), motion.py:1501-1504 (`_regions`: a frame pair where more than half the tiles changed goes to `out.page_changes` and is not mapped); `page_changes` is read by no check (grep over src/: only motion.py)
- What: The rule exists so that a dialog backdrop or a scroll does not join every region into one. But it also discards a hero banner, a full-width slider, a colour-cycling background or a full-screen canvas, because in every frame pair most tiles differ. When every pair is dropped there are no regions, no `source="pixels"` instances, and the 2.x checks see "nothing moved". The recorded `page_changes` list is never turned into a hint or an A2 NEEDS REVIEW; nothing says "the whole screen changed".
- Evidence: pages/fullnoise.html (a fixed full-viewport `<canvas>`, 320 x 180 scaled up, drawing a slowly cycling gradient from `requestAnimationFrame`, static heading and button over it). `runpage.py fullnoise.html 2.B` gave `2.B DNA ['A2','G1'] We watched this page for 6.5 seconds. Nothing on it moved, blinked or scrolled for more than 5 seconds`. Evidence file: `page_changes` 17 of 18 frames, `regions` 0, `unmapped_tiles` 0. Two controls found the movement only by luck: a CSS-animated hero (found through the animation list in `_extras`) and a striped canvas where 6 of 18 frame pairs happened to change under half the tiles.
- Fix: if more than, say, a third of the frame pairs are page changes, keep them and map the largest changed block of the first and last pair (or treat the whole viewport as one region with source "pixels"); at minimum add "the whole screen changed in N frames" as an A2 hint in 2.B and 2.C. Same remedy for `unmapped_tiles`, which is also never read.
- Confidence: confirmed (ran)

### W-08 A static page with one `IntersectionObserver` pays a second 6.5 s watch (+7.6 s per run)
- Severity: P2
- Kind: time
- Where: src/tobi508/motion.py:1655-1656 (`collect`), motion.py:457-469 (`M.below`: every element passed to `IntersectionObserver.observe` below the first screen), motion.py:1591-1611 (`_scrolled_watch` = a whole second `pass_t`: load, read elements, 6.5 s watch, crops, loudness, long images)
- What: Lazy-loaded images, analytics and ad slots all call `observe()`. Each such page gets a second full pass T that scrolls to the first hint. Failures of that second pass are dropped silently (`if not second.ok: return`, `mp.scrolled_watch` is set either way), and its regions are merged without checking the cap.
- Evidence: static two-paragraph page, 2500 px tall, with one `new IntersectionObserver(...).observe(p)` below the fold (io.html) against the same page without the observer (noio.html), `runpage.py ... 2.C`: 18.7 s against 11.0 s wall, both `DNA ['A3']`.
- Fix: do the scroll inside the first watch's last 3 s (scroll, then keep taking frames) rather than a second load; or skip the second watch when the hinted element is an `img` with `loading=lazy` or a zero-size/ad node. Record when it failed.
- Confidence: confirmed (ran)

### W-09 Frame sampling every 0.35/0.45 s aliases a 2.5 Hz blink (and 5 Hz, 1.25 Hz) to "never changes": 2.B says DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/motion.py:51-54 (`FRAME_STEPS = (0.35, 0.45)`), motion.py:1149-1167 (screenshot, sleep to the next step); consumer: `changed_tiles` of consecutive frames only
- What: The watch decides whether something blinks or moves from about 17 screenshots whose gaps alternate 0.35 s and 0.45 s. The comment says this was chosen so that a blink of 0.5 s per state is not seen in the same state every frame. But the pattern repeats every 0.8 s, so only two sampling phases ever occur. A 50% duty blink of period 0.4 s (2.5 Hz, below 3.A's threshold so only 2.B covers it) is sampled at phases (x, x-0.05 s): both in the same half of the cycle for 75% of start offsets. A 5 Hz blink: 50%. A 1.25 Hz blink: 13%. Real gap jitter is only about 10 ms, so it does not rescue it.
- Evidence: simulated the frame times against a 50% duty blink with random phase (4,000 starts per period, no jitter): miss rate 0.75 at 0.4 s, 0.50 at 0.2 s, 0.13 at 0.8 s, 0 at 0.3/0.5/0.6/1.0 s. Then ran the real pipeline three times on pages/blink25.html (`<p>` toggled `visibility` every 200 ms by `setInterval`, forever, the only motion on the page): `2.B DNA ['A2','G1'] We watched this page for 6.5 seconds. Nothing on it moved, blinked or scrolled for more than 5 seconds` in 3 of 3 runs. The real frame times of an earlier run were exactly 0.01, 0.46, 0.81, 1.26, 1.61 ... (0.45/0.35 steps, jitter about 0.01 s).
- Fix: detect change from a dense source: run a CDP screencast for the whole watch (changed frames only, timestamps, about 55 per second; flashcap.screencast already does it for 2 s) and feed those frames to `changed_tiles`, keeping the 17 screenshots for evidence; or randomise the gaps (for example 0.30-0.50 s from a seeded generator); or use the DOM log as a second detector for `style`/`class` toggles and add its element as a region when it toggles three or more times in the watch. Add the blink band (1-3 Hz, several duty cycles) to tests/test_motion_browser.py.
- Confidence: confirmed (ran)

### W-10 Every long timer is recorded as a hint, so a static page with a heartbeat or a session timeout becomes 2.C NEEDS REVIEW
- Severity: P2
- Kind: bug
- Where: src/tobi508/motion.py:131-143 (`M.timers` takes every `setInterval`/`setTimeout` of 1 s or more, whatever the callback does); src/tobi508/checks/t2c.py:86-88 (hint for any timer over 6.5 s); contrast the fast timers, which are kept only when the callback changed the DOM or drew (`fast()`)
- What: Analytics heartbeats, session-expiry warnings, cookie-banner delays and ad refresh timers are on almost every real page. Each is recorded and 2.C then says "it sets a timer of 60 s, longer than we watched", NEEDS REVIEW, asking a person to watch the page for a minute.
- Evidence: pages/heartbeat.html (static text, `setInterval(noop, 60000)`, `setTimeout(noop, 1800000)`): `runpage.py heartbeat.html 2.C` gave `2.C NEEDS_REVIEW ['A2','G1'] ... it sets a timer of 60 s, longer than we watched`.
- Fix: keep a long timer as a hint only if something shows it matters: its callback is not a no-op can only be known when it fires, so either fast-forward on a paused clock (see W-04) or weigh the hint (a timer period of 7-20 s is a carousel; 60 s or more is not auto-updating content a tester would call a carousel or ticker).
- Confidence: confirmed (ran)

### W-11 Per-frame read failures and every cap are recorded, but no check reads them
- Severity: P2
- Kind: gap
- Where: src/tobi508/motion.py:933-940 (`_each_frame` skips a frame whose `evaluate` throws), :1095 (`frames_read`, counted once at 0 s), :1526-1528 and :1550 (`regions_capped`), :1472 (the `_extras` cap, no flag at all), :1251 (`dropped_changes`), :1549 (`unmapped_tiles`), :1608-1611 (a failed scrolled watch is dropped); grep over src/: `frames_read`, `regions_capped`, `dropped_changes`, `unmapped_tiles`, `page_changes` appear in no other file. Spec specs/rules/2c-auto-updating.md A1: "Pass T could not run or read the page (load, frames or reads failed)".
- What: A frame that fails to answer (navigated, detached, init script missing) gives no media, no facts and no regions, and nothing says so: 2.A reads "no audio", 2.B/2.C read "no motion in that frame". Changed tiles that no element could be found for are counted in `unmapped_tiles` and then ignored. Silent caps: 30 tile groups, 40 regions, 400 boxes per region, 1,500 DOM records and 300 attribute records, 600 fast callbacks, 20 media per frame, 10 extras per frame, 30 images, 10 loudness reads. Only `elements_truncated` reaches an outcome.
- Evidence: read; grep above. Not run (no page found that makes a frame reads fail without also failing the main frame).
- Fix: have `pass_t` set `ok=False` (A1) or add one A2-style hint when `unmapped_tiles > 0`, when a frame's later reads failed (compare `frames_read` with the frames that answered at the end), or when a cap was hit; set the flag in `_extras` too.
- Confidence: confirmed by reading; the impact on real pages is likely.

### W-12 The screencast net fails silently and is not recorded as "not measured"
- Severity: P2
- Kind: gap
- Where: src/tobi508/checks/t3a.py:221-229 (`except Exception: st.screencast = None`, nothing added to `unmeasured`); src/tobi508/flashcap.py:121-122 and :128-129 (fewer than two frames, or frames of unequal size, return an empty `Analysis`); flashcap.py:105-107 (acknowledgements sent by `asyncio.ensure_future`, never awaited)
- What: Spec A3 lists "a capture that failed" as NEEDS REVIEW. The screencast is the only trigger for SMIL, CSS background GIFs and anything the hooks do not see (and the only net behind W-02, W-04, W-06), but when it fails to start or returns under two frames the run carries on as if it had seen a quiet page. A page that paints nothing for 2 s also gives under two frames, so "quiet" and "failed" look the same.
- Evidence: read.
- Fix: put the failure and the frame count in `State3A` (`screencast_ok`, `frames`), and add an `Unmeasured` for an exception; keep a static page's one frame as normal.
- Confidence: confirmed by reading

### W-13 Mechanism probe: spec and code differ on sliders, timers as period, and frame spacing; and the key rules are only partly in code
- Severity: P3
- Kind: gap
- Where: src/tobi508/mechanism.py:156-157 (`slider` gets only `Home`; spec 2c section 2: "Home, then End, then arrow keys"); src/tobi508/motion.py:1215 (`period_s` is only the median pixel gap; spec Terms: "When the timer hooks saw an interval longer than the watch, that interval is used instead"); motion.py:51-53 (frames every 0.35/0.45 s; spec: "every 0.5 s"); mechanism.py:58-72 (see W-14)
- What: A slider that speeds the content up or down may not stop it on `Home` but would on `End`; the probe calls it "no effect" (K6 FAIL if every other control also fails). A content found with one change (period unknown) is watched for the 5.5 s minimum, shorter than its likely period (5-6.5 s), so a control can read "stopped" for want of a change; the focus-only probe then usually reads "stopped" too (K2, NEEDS REVIEW), so this is noise, not a false PASS.
- Evidence: read; `grep -rn period_s src/` shows no use of `mp.timers`.
- Fix: press Home, End and one arrow key for sliders (3 loads, only for sliders), or mark the slider "untried" (K7); give `confirm_s` a floor of the watch length when `period_s` is None.
- Confidence: confirmed by reading

### W-14 J2's key: the "browser keys" rule is a 12-item list, and the key is never compared with the page text
- Severity: P3
- Kind: security
- Where: src/tobi508/mechanism.py:48-72 (`MODIFIERS`, `BROWSER_KEYS`, `_NAMED`), :75-98 (`parse_key`), :499-539 (`press_answered`)
- What: CLAUDE.md principle 5's exception: "modifiers plus one key, never one the browser itself uses, one combination per run, and only to confirm what J2 found". Enforced in code: at least one modifier, no repeated modifier, the last part one alphanumeric character or F1-F12/Escape/Space/Enter/Home/End, one combination per run (`evidence/keys.json`, checked before each press), only for a J2 answer "describes", and `evidence`-recorded. Not enforced: "never one the browser uses" is the 12-item `BROWSER_KEYS` (the spec lists 7; the Meta ones were added). Ctrl+Shift+W/N/T/Q, Ctrl+R, Ctrl+F5, Shift+F5, Ctrl+P, Ctrl+S, Ctrl+O, Ctrl+U all parse and are pressed. `isalnum()` accepts non-ASCII (`Ctrl+Ｗ` fullwidth, `Ctrl+²`, `Ctrl+é`). The string comes from the answer's `key` field, never checked against the element's own text, so page text only has to talk an agent into writing a key; the combination is then limited as above.
- Evidence: called `parse_key` on 54 strings (table below). In headless Chromium (Playwright, project autoplay flag) pressing Control+R, Shift+F5, Control+F5, Control+Shift+W, Control+Shift+N, Control+P, Control+S, Control+W, Alt+Home, F5 left the page alive with its JS state intact (ran, browser 153.0.8010.12), so in the supported headless mode none of these has an effect; not tried headed. The replay context is `route_from_har(..., not_found="abort")`, so a key cannot start a live request.
- Fix: allow a combination only when the element's own text contains it (normalised), and turn `BROWSER_KEYS` into an allow-pattern: Ctrl/Alt/Shift/Meta + a letter, digit or F-key except a short denylist that includes the Shift variants and Ctrl+R/F5/P/S/O/U; restrict `isalnum` to ASCII.
- Confidence: confirmed (ran the parser; ran the key presses headless). Headed behaviour unverified.

### W-15 The walk's "stop waiting on changing content" list arrives only after the scrolled watch, and pass T's full work runs for 4.x-only runs
- Severity: P2
- Kind: time
- Where: src/tobi508/pipeline.py:1058-1075 (pass T starts when any check needs the walk, "It also runs for the walk alone"), pipeline.py:`_watch_then_ignore` (calls `motion.collect`, then `settle_ignore(mp)`); src/tobi508/motion.py:1633-1659 (`collect` = `pass_t` + `_scrolled_watch`)
- What: `settle_ignore` is applied after `collect` returns, i.e. after pass T (about 9 s) and, on pages with an observer below the fold, after the second watch (W-08, another 8 s). Meanwhile the walk's presses wait out the full settle window on the changing content (up to 1.5 s a press). For a run of 4.A-4.F alone the loudness decode, long-image decode, crops and the scrolled watch are work nobody reads (`keep_shots` is false, no 2.x check runs).
- Evidence: read (pipeline.py and motion.py:1633-1659). Not timed on a walk.
- Fix: call `settle_ignore` right after the first `pass_t` (before `_scrolled_watch`), and give `pass_t` a `light=True` mode (frames, regions, no loudness/long images/crops/scrolled watch) for runs with no `uses_motion` check.
- Confidence: confirmed by reading (the saving is likely, not measured)

### W-16 "Gone" counts as "stopped": a control that replaces the content's container is credited with stopping it
- Severity: P2
- Kind: false-pass-risk
- Where: src/tobi508/mechanism.py:228-241 (`_look` returns "gone" when `locator(css).first.is_visible()` is false, which is also false when the selector no longer matches), :263-266, :267-269
- What: After the control's key and a Tab, the watch looks the content up again by its CSS path. If the control's handler re-renders the widget so that path no longer exists (a framework remount, `innerHTML` on the parent) while the new copy keeps running, `is_visible` is false and the result is "stopped". The focus-only probe has no press, so it reads "no_effect" and K3 treats the control as a working mechanism. A content hidden by `display:none` is rightly "stopped"; a missing node is not the same fact.
- Evidence: read. Not reproduced (needs a page with a re-rendering control).
- Fix: distinguish "no node matches" (`locator.count() == 0`: unreliable, or look for the same text elsewhere) from "node present and not visible" (stopped).
- Confidence: speculative

### W-17 Smaller things in these files
- Severity: P3
- Kind: dead-code / design
- Where and what, one line each:
  - src/tobi508/motion.py:54 `FRAME_S` is defined and never used (dead).
  - src/tobi508/motion.py:1383 and flashcap.py:55 both define `IMAGE_MAX_BYTES = 5_000_000`; t3a.py uses `flashcap.`'s, motion.py its own.
  - src/tobi508/checks/t3a.py calls private names of two modules: `motion._image_type`, `motion._secure_tool_page`, `flashcap._frame_boxes`. `_secure_tool_page` makes a new browser context per caller (pass T once, 3.A once more); one shared helper in a `toolpage.py` would do.
  - `motion.Candidate` and `motion.Probe` (motion.py:1567-1588) are the mechanism probe's models, imported back by mechanism.py (`from tobi508.motion import Candidate, ... Probe`).
  - motion.py is 1,659 lines and does nine jobs: a 450-line browser script in a Python string (patched with `.replace`), element reading, the watch loop, region mapping, crops and states, animated-image and loudness decoding, the tool page, the scrolled watch, and the settle rule. Moving the script to `motion_init.js` (read at import, hashed) and the models to `models.py` would make the next change cheaper and let the script be linted.
  - src/tobi508/flashcap.py:516-531 `__all__` re-exports `PATH_JS` and `safe_error`, which are used only through `flashcap.PATH_JS` in t3a.py (an import indirection).
  - src/tobi508/flashcap.py:54 and :320 `IMAGE_MAX_FRAMES = 500`: a longer animated image is cut at 500 frames with no note, and `once` (hence "N s in all") is then computed from the cut list.
  - src/tobi508/motion.py:1057-1075 `_loudness`: an `evaluate` failure (page crash, argument too large) propagates to `pass_t`'s `except`, so one bad audio file sets `ok=False` and every 2.x test becomes NEEDS REVIEW A1; only decode errors inside the script are handled (`null`).
  - src/tobi508/motion.py:1133-1167 and `changed_tiles`/`_states`: per-frame PIL work (decode, difference, a Python loop over 2,880 tiles) runs on the event loop between screenshots, about 50-100 ms per frame in a hosted server with two runs.
  - src/tobi508/mechanism.py:228 and :255-300: the probe samples every 0.5 s plus the screenshot time (about 0.6 s) at a fixed cadence; a blink whose period is close to that cadence reads as "never changes" (the aliasing of W-09, on the probe side); the same fix (jittered gaps) applies.
- Confidence: confirmed by reading (probe aliasing: likely, not run)

## Table A: every fixed wait and observation window

Wall seconds unless "page time". "Needed" = the TT text or the spec asks for it; "padding" = chosen by the build.

| Where | Length | Why | Needed or padding |
| --- | --- | --- | --- |
| motion.py `WATCH_S` | 6.5 s | pass T's single watch; 2.B "more than 5 seconds", 2.A "more than 3 seconds" | needed (>5 s); the 1.5 s margin is a choice |
| motion.py `FRAME_STEPS` | sleep 0.35 / 0.45 s between screenshots (about 17 frames) | pixel-difference sampling | padding, and aliases (W-09) |
| motion.py `READS_AT` | reads at 0, 3.5, 6.5 s (no sleep) | what each region/media showed | 3.5 s serves "3 seconds" (W-05) |
| motion.py `pass_t` `scroll_to` | 0.3 s | let scrolled-to content settle | padding |
| motion.py `_scrolled_watch` | a second full pass T, about 8 s | content that starts when scrolled into view | conditional; fires on any `IntersectionObserver` (W-08) |
| motion.py `CROP_GAP_S` | 1.0 s between two sets of crops (+ up to 12 full-page screenshots) | evidence pictures for J1 | padding (evidence only) |
| motion.py `_long_images`, `_loudness` | no sleep; one new browser context (about 0.3-0.5 s) per call, up to 30 images / 10 audio files | G152, "silent" audio | needed for 2.A/2.B; wasted for 4.x-only runs (W-15) |
| mechanism.py `SETTLE_S` | 0.6 s per try (also audio, also the J2 key) | transitions end after focus leaves | spec |
| mechanism.py `LOOK_S` | 0.5 s poll (+ screenshot about 0.1 s) | compare the content's pixels | padding; alias risk (W-17) |
| mechanism.py `CONFIRM_MIN_S` / `CONFIRM_MAX_S` | 5.5 s min if nothing changes; max(5.5, 1.5 x period) up to 15 s | "stopped" needs a quiet period | spec; 5.5 s also the cut for an unknown period (W-13) |
| mechanism.py `AUDIO_CONFIRM_S` | 3.5 s (+0.6 settle) | "more than 3 seconds" | needed |
| per try (`_reach`/`open_session`/`press`) | one fresh load, settle up to 1.5 s, a re-settle of 1.0 s + 1.5 s after a focus change, per press | replay to the control | design; the 28.7 s note in `_reach` is why top-page controls are focused directly |
| flashcap.py `SCREENCAST_S` | 2.0 s sleep on its own load (about 3-4 s) | the net | spec |
| flashcap.py `LEAD_MS`, `STEP_S` | 0.1 s lead and 3 s of page time = 181 screenshots, 6.6-7.3 s wall (measured `wall_s` 6.60, 6.72, 7.25) | "any one second" needs more than 1 s; 3 s is a choice | 1 s needed; 3 s padding, and it is the whole observation window (W-04) |
| flashcap.py video | 10 s of media at 0.5x = about 20 s wall per video, up to 3 videos; `canplay` timeout 10 s; `wait_for` 40 s | O4 and "every frame" | cap needed (O4); half speed is padding for a 30 fps clip |
| flash.py analysis | 15-19 s CPU per 181 full-screen frames, on the event loop | counting | W-01 |

Worst case per run, from the code (not measured end to end): pass T 9-12 s, 18-24 s with the scrolled watch; mechanism probe: per control one load plus 0.6 s plus 1-2 s when it does not stop the content, 6-7 s when it holds, doubled for the focus-only probe, 8 controls x 3 contents (the caps), so typically 35-40 s per content and a theoretical 260 s; flash capture 3 s + 7 s + 15-19 s analysis + 20 s per video. The 45 s `MOVING_ALLOWANCE_S` pays for about five control tries. One window could be shared: the 2 s screencast and the 3 s stepped capture each load the page again, while pass T has already watched 6.5 s of it (about 4 s per run).

## Table B: what can fail, what the caller sees, what the outcome is

| What can fail | What the caller sees | Outcome |
| --- | --- | --- |
| Page load for pass T fails | `MotionPass.ok = False`, reason | A1 NEEDS REVIEW (safe) |
| A screenshot in the watch fails | exception, `ok = False`, "could not be read" | A1 NEEDS REVIEW (safe) |
| One frame's `evaluate` fails (mark0, snap, media, facts, describe, extras) | nothing: `_each_frame` skips it, `frames_read` is counted once and unused | "nothing there" in that frame: DNA possible (W-11) |
| More than half of the tiles change in a frame pair | `page_changes` list, unused | frame dropped; all dropped = no region = DNA (W-07) |
| Region, component, box, record, callback, image, media caps | `regions_capped`, `dropped_changes` (unused), others unflagged | extra content ignored (W-11) |
| Content starts after 6.5 s, or a finite animation ended before the end of the watch | nothing | DNA (W-04) |
| Media created without a DOM node (`new Audio`), `speechSynthesis` | nothing | 2.A DNA (W-03) |
| Media appears after the 0 s read | reads exist, consumer pairs them wrongly | 2.A DNA (W-05) |
| Blink period near 0.4 s multiples | nothing | 2.B DNA (W-09) |
| Long timers (no-op) | `timers` list | 2.C NEEDS REVIEW noise (W-10) |
| Scrolled watch fails | `scrolled_watch` still set, no error | first pass's result stands (W-08) |
| Loudness decode throws in JS | `loudness[src] = None` | 2.A "could not measure": NEEDS REVIEW (safe) |
| Loudness `evaluate` itself throws | whole pass `ok = False` | A1 NEEDS REVIEW (safe, coarse; W-17) |
| Media file not in the recording (late-created element) | `error: 4`, `media_store` empty | 2.A NEEDS REVIEW "we could not play or measure" (safe; ran lateaudio2.html) |
| Mechanism: page navigated, screenshot failed, exception, content not found with a visible node | `unreliable` | K1 NEEDS REVIEW (safe) |
| Mechanism: node no longer matches the CSS path | `gone` = `stopped` | can credit a control (W-16) |
| Mechanism: confirm window shorter than the content's period | `stopped` | usually K2 NEEDS REVIEW, since focus-only also reads stopped (W-13) |
| Stepped capture: screenshot or load fails, time cut | `Unmeasured` entry | A3 NEEDS REVIEW (safe) |
| Stepped capture: flash below the first screen | trigger recorded, capture sees nothing, `unmeasured` empty | A4 DNA (W-02) |
| Stepped capture: lead too short for a late flash | screencast net may catch it | A3 NEEDS REVIEW if the net fires, else A4 DNA (W-06, W-02) |
| `STEP_JS` fails in one frame | skipped silently, that frame's animations run on the wall clock | mis-timed counts, no note (lead) |
| Screencast fails or returns under two frames | `st.screencast = None` / empty analysis | no trigger from it, no note (W-12) |
| Video: H.264 or undecodable, `play()` rejected, under two frames, over 40 s | `Unmeasured` with the reason | A3 NEEDS REVIEW (safe; read t3a.py:482-506) |
| Video past 10 s, past three videos, over 20 elements | named in `unmeasured` / `partial()` | A3 or the disclosure (safe) |
| Animated image over 500 frames | truncated silently | analysis of the first 500 only (W-17) |
| `analyze` given under two frames | empty `Analysis(frames=n)` | "not flashing"; the callers always pass 100+ (the cut case sets `Stepped.cut`) |

## Table C: synthetic frame sequences against WCAG 2.3.1 (flash.analyze, 60 fps frames unless stated; script `scratchpad/w/synth.py`)

| Sequence | Expected by WCAG 2.3.1 / G19 / G176 | Returned (flashing, general peak = transitions in the busiest 1 s window, area px, over) |
| --- | --- | --- |
| full screen black/white 2 Hz | no flash (2 flashes/s) | False, 4, 0 |
| 3 Hz | no (exactly three) | False, 6, 0 |
| 3.5 Hz | flash (7 transitions, G19) | True, 7, 88,064, over |
| 4 Hz | flash, over the area | True, 8, 88,064, over |
| 10 Hz | flash | True, 20, 88,064, over |
| 100 x 100 CSS px box, 4 Hz | flash, area 10,000 under 21,824: allowed | True, 8, 10,000, not over |
| 144 x 144 box (20,736) / 148 x 148 box (21,904) | under / over the 21,824 limit | not over / over |
| 336 x 256 box (86,016) | over | over |
| 400 x 200 CSS box at 4 Hz | box wider than 341: the rectangle holds 344 x 200 | area 68,800 (clipped to the best 341 x 256 field), over |
| red/black 4 Hz | red flash and general flash | red peak 8 over, general peak 8 over |
| red (255,0,0) / green (0,128,0) 4 Hz | red flash only (luminance change 0.06) | general 0, red 8 over |
| smooth triangle fade 4 Hz | opposing changes of 10%+ count | True, 8 |
| triangle fade 1 Hz | no | False, 2 |
| 250/255 at 4 Hz | no (change under 0.1) | False |
| 235/255 at 4 Hz (darker state L = 0.83) | no (darker state not below 0.80) | False |
| 150/255 at 4 Hz (L 0.31 / 1.0) | flash | True, 8 |
| 128/140 at 4 Hz | no | False |
| 4 Hz with irregular timestamps (8-25 ms gaps) | flash | True, 9 (window by real time) |
| a 1 s burst of exactly 3 flashes | no | False, 6 |
| 30 Hz sampled at 60 fps | flash | True, 60 |
| 30 Hz sampled at 10 fps | (a 10 fps source cannot show it) | False, 0 (aliasing, nothing says so; it applies only to the real-time screencast) |
| 1 or 2 frames | no information | False, empty `Analysis` (the stepped path always has about 181) |
| 1 px / 2 px checkerboard inverting every 2-4 frames | fine pattern (F1) | `fine = True`, 196,608 sampled pixels; 14-19 s to analyse |

The maths (sRGB 0.03928/12.92/2.4 and 0.2126/0.7152/0.0722, 0.1 change, darker state under 0.80, more than six transitions in [t, t + 1 s) at every frame, 341 x 256 field, 21,824 px, linear-RGB red rule with R/(R+G+B) >= 0.8 and (R-G-B) x 320 > 20, "no more than" at the limit) agrees with WCAG 2.0 in every row above; nothing wrong was found in flash.py's counting. The 341 x 256 field is applied in CSS px whatever the viewport; the capture forces 1024 x 768 at DPR 1, so the two agree for the stepped capture; video and image frames are scaled to the same field (stated in the spec).

## Table D: J2 key parser (mechanism.parse_key), selected calls

| Input | Returns | Browser-key block |
| --- | --- | --- |
| `Ctrl+W`, `ctrl + w`, `\nCtrl+W`, `Command+W`, `Cmd+Q`, `Alt+F4`, `Option+Home` | `Control+W`, `Control+W`, `Control+W`, `Meta+W`, `Meta+Q`, `Alt+F4`, `Alt+Home` | blocked |
| `F5`, `a b`, `Enter Enter`, `Control+Shift+Delete`, `Alt+Left`, `Ctrl+Tab`, `Ctrl+Alt+Delete`, `Ctrl+K+L`, `Ctrl+aaaa...` (500), `Ctrl+F13`, `Ctrl++` | None | n/a |
| `Ctrl+Alt+Shift+K` | `Control+Alt+Shift+K` | pressed |
| `Ctrl+Shift+W`, `Ctrl+Shift+N`, `Ctrl+Shift+T`, `Ctrl+Shift+Q` | same with Control | pressed |
| `Ctrl+R`, `Ctrl+F5`, `Shift+F5`, `Ctrl+P`, `Ctrl+S`, `Ctrl+O`, `Ctrl+U` | same | pressed |
| `Ctrl+Ｗ` (fullwidth), `Ctrl+²`, `Ctrl+é` | `Control+Ｗ`, `Control+²`, `Control+É` | pressed |
| `Ctrl+W` with a trailing zero-width space, `Ｃtrl+W` | None | n/a |
| `Ctrl+W ; Ctrl+T`, `Ctrl,Shift+K` | None | n/a |

## Unverified leads

- Probe-side aliasing (W-17, last bullet): a blink whose period is near the probe's 0.6 s sampling cadence could read as "stopped" for both the key press and the focus-only try; not run.
- `flashcap.stepped` skips a frame whose `STEP_JS` throws; an animation in a cross-site iframe that cannot be stepped then runs on the wall clock and is timed as if it were 60 fps; not run (fixture f14 covers the working case).
- Video frames come from `requestVideoFrameCallback` at half speed; under CPU load (two runs plus the analysis of W-01 on one loop) frames may be skipped and the count under-reads; not run.
- `M.below` and `M.io` take any observed element: confirmed to trigger the second watch (W-08); whether the second watch ever finds anything the first missed on real pages is unmeasured.
- A flash that is a finite CSS animation starting between 2 s and 6.5 s: read to be missed by the screencast (0-2 s), by `fastAnims` (needs `running` at 6.5 s) and by the timers; not run (the 9 s timer of late.html is the same class, run).
- `speechSynthesis`, `<audio>` in a closed shadow root and media in sandboxed frames: only the first (not hooked) is reasoned; none run (a sandboxed spinner was found, as a control).
- Headed Chrome (`TEST_HEADED`) may let accelerators such as Ctrl+Shift+W through `Input.dispatchKeyEvent`; only headless was tried (W-14).
- `READS_AT[1] = 3.5` is fixed while the 2.A rule is "more than 3 seconds": a clip of 3.2 s that was in the DOM from 0 s reads `left = duration - first.time` and is excluded as intended; a clip that starts at 1.0 s would need a later read; not run.
