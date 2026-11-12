# W-watchers: review of motion.py, mechanism.py, flash.py, flashcap.py

(Overview and unverified leads are added at the end. Findings are appended as they are confirmed. Reviewer notes: all four files read in full; flash.py functions run on synthetic frames; end-to-end runs listed per finding.)

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
- Fix: share `t2c.hints()`' timer rule (and the poll rule) with 2.A, 2.B and 3.A: when no instance is found and the page set a timer longer than the watch, the outcome is NEEDS REVIEW with the same A2 wording, not DNA.
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

