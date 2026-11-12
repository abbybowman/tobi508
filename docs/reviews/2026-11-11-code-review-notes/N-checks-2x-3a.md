# N: checks 2.A-2.D and 3.A, code against spec

## Overview

- Reviewed t2a, t2b, t2c, t2d, t3a line by line against their five specs, plus engine.py, base.py and the parts of motion.py/mechanism.py they call. Row tables and first-match order match the specs closely (checked by reading, and `t2b.ROWS` by running); the problems are in what the rows are fed.
- 8 findings are about "nothing observed" being reported as "does not apply" (DNA on real pages, all proven by running a page): N-01 (audio in a shadow root or `new Audio()`), N-03 (text blinking with `visibility`, 2.B), N-06 (flashing GIF after the 30th `<img>`, 3.A and 2.B), N-08 (YouTube autoplay embed, 2.B), N-02/N-04/N-07/N-09 (things that start after 6.5 s, or are scrolled to second).
- PASS is unreachable in 2.A-2.C today (E2 needs 13.A, not built), so no false PASS was found there; 2.D PASS rests on N2 and has loose N3/N4 and unchecked caps. NOT_TESTED comes only from t3a A2, as the principle requires.
- Principle 5's key press: modifiers + one key, browser list, one combination per run, fresh replay are enforced in mechanism.py; the spec guard "key/quote found in the page text" is not (N-11).
- Pattern from the sister reviews recurs: caps and failed reads are recorded (`dropped_changes`, `frames_read`, `regions_capped`) but no check reads them (N-05); English-only matching (N-12, N-15).
- Cost: pass T 6.5 s (+6.5 s scrolled), probes up to about 250 s per content in the worst case; code copied four times between t2a-t2d (`_finding`, `apply_answers`, Check classes).
- Counts: 16 findings. P0 4 (N-01, N-03, N-06, N-08), P1 4 (N-02, N-04, N-07, N-09), P2 6 (N-05, N-10 to N-14), P3 2 (N-15, N-16). Findings are in the order found, not sorted by severity.

## Findings (appended as found; sorted at the end if time allows)

### N-01 Audio in a shadow root, or created with `new Audio()`, is never seen: 2.A says DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk (wrong DOES NOT APPLY)
- Where: src/tobi508/motion.py:392 (`M.media`: `document.querySelectorAll('video, audio')`), consumed by src/tobi508/checks/t2a.py:94-129 (`find_audio`) and :190 (A3)
- What: Pass T finds media only with a light-DOM `querySelectorAll('video, audio')`. Media inside an open shadow root (web components) and media that is never attached to the document (`new Audio(url).play()`, the usual way sites start background music or a sound effect) are invisible to it. Nothing else records that an element played (no hook on `HTMLMediaElement.prototype.play`, the hook list at motion.py:155 covers only `AudioNode.connect`). With no media seen, A3 gives DOES NOT APPLY with the sentence "No audio played by itself for more than 3 seconds". A page that plays loud audio at load with no control is a FAIL in the TT; here it is DNA.
- Evidence: ran pages in the scratchpad. Control `a_ctl.html` (`<audio src=tone.wav autoplay>` in the body, a 440 Hz tone): 2.A FAIL A4, a1:K6, G2. `a_detached.html` (`new Audio('tone.wav').play()` in a script): 2.A DNA A3, G1. `a_shadow.html` (`<audio autoplay>` inside an open shadow root): 2.A DNA A3, G1. The same tone file in each case, so the audio is real. 2.B's video read (`source: video`) uses the same `M.media` and has the same hole for a `<video>` in a shadow root (read of motion.py only).
- Fix: hook `HTMLMediaElement.prototype.play` (and `load`/`autoplay` set) in MOTION_INIT_JS to keep a list of every element that played (detached ones included) and walk open shadow roots in `M.media`; when a page used `play()` on an element the read could not find, give NEEDS REVIEW (A2).
- Confidence: confirmed (ran 3 pages)

### N-02 Audio that starts after 3.5 s is DOES NOT APPLY; the read at 6.5 s is ignored
- Severity: P1
- Kind: false-pass-risk (wrong DOES NOT APPLY), spec gap
- Where: src/tobi508/checks/t2a.py:94-129 (`at = min(reads, key=abs(m.at - READ_AT))`); spec 2a-audio-control.md Terms ("at 3.5 s into pass T")
- What: `find_audio` looks at the one read nearest 3.5 s and decides from it alone. Media is read three times (0, 3.5, 6.5 s) but a clip that is paused at 3.5 s and playing at 6.5 s (a `setTimeout` start, a welcome message after a 4 s delay, audio begun by a script that waits for a user-agent check) is dropped (`not playing -> continue`). The TT asks for audio that "automatically plays ... for more than 3 seconds"; sound that starts at 4.5 s and never stops is exactly that. The spec's definition is the cause, the code follows it; the DNA sentence "No audio played by itself" is then false.
- Evidence: ran `a_late2.html` (`<audio preload=auto src=tone.wav>` started by `setTimeout(..., 4500)`): 2.A DNA A3, G1 ("We watched this page for 6.5 seconds ... No audio played by itself"). A variant that creates the element at 4.5 s gave NEEDS REVIEW only because the file was not in the recording (error), not by design.
- Fix: if any read after the 3.5 s read shows the element playing (not paused, `time` advanced since the previous read) while the 3.5 s read does not, treat it as an unmeasured instance (A2/U1) rather than skipping it. Amend the spec's Terms.
- Confidence: confirmed

### N-03 Text that blinks by toggling `visibility` (or opacity) is "auto-updating", so 2.B says DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk (wrong DOES NOT APPLY)
- Where: src/tobi508/checks/t2b.py:77-85 (`moving`: needs kind "moving" or `children_moved`), src/tobi508/motion.py:976-987 (`_kinds`), motion.py:215 (`self = ... visibility !== 'hidden'`: hidden text drops out of the hash)
- What: `<span>` text toggled with `visibility:hidden/visible` (the standard way to emulate `<blink>`, WCAG failures F16/F50-style) changes the region's visible-text hash between reads, so pass T labels it "updating", never "moving". 2.B's `moving()` accepts only moving regions (or updating ones whose children move), so 2.B finds no moving region and gives DOES NOT APPLY ("Nothing on it moved, blinked or scrolled"). 2.C does report the same content (FAIL K6), so the page is not clean, but the TT requires 2.B to FAIL here and the tool says DNA. The existing fixture `t-color-toggle` covers a colour toggle only.
- Evidence: ran `b_blink.html` (a 30 px span toggled every 500 ms via `style.visibility`): 2.B DNA A2/G1; 2.C FAIL A5, r1:K6, G2. Region data (evidence/2c.json): `kinds: ['updating']`, `changed_at` 0.8 ... 6.87 s (13 changes), `colors` differ, `states: 2`, mapped to `html > body`.
- Fix: in `moving()` also accept an updating region whose pixels change in the final seconds and whose reads return to an earlier state (few distinct `sigs`, `states` small), or exclude `visibility`/opacity-hidden text from `sigs` so it becomes a colour-only style change. Add a fixture with `visibility` and one with `opacity` toggles.
- Confidence: confirmed (ran page)

### N-04 2.B has no "could not watch long enough" path: motion that starts after the watch is DOES NOT APPLY
- Severity: P1
- Kind: false-pass-risk (wrong DOES NOT APPLY), spec gap
- Where: src/tobi508/checks/t2b.py:177 (A2 `not p.regions` -> DNA), spec 2b A2; compare 2.C `hints()` at src/tobi508/checks/t2c.py:73-100 and A2
- What: 2.C turns "a timer longer than the watch", polling and unchanged carousels into hints and answers NEEDS REVIEW. 2.B has nothing alike: no moving region means DNA, with the sentence "Nothing on it moved ... for more than 5 seconds". An infinite animation or marquee that a script starts at 7 s, a GIF inserted at 8 s, or a ticker that starts after a consent click timer is invisible in the 6.5 s watch. The spec's A2 states no hint, so code and spec agree; both are wrong about what was observed.
- Evidence: ran `b_late.html` (a rotating box whose animation class is added by `setTimeout(..., 7000)`): 2.B DNA A2/G1; the same run gives 2.C NEEDS REVIEW A2 ("it sets a timer of 7 s, longer than we watched"), so the evidence of the late timer exists in `mp.timers` and 2.B ignores it.
- Fix: 2.B A2: when `hints(mp)` (2.C's, shared) is non-empty and there is no moving region, NEEDS REVIEW with the same note. Amend the 2.B spec A2.
- Confidence: confirmed

### N-05 Pass T failures are swallowed per frame and caps are only recorded, so DNA/PASS can rest on unread frames or a full mutation log
- Severity: P2
- Kind: false-pass-risk, gap
- Where: src/tobi508/motion.py:933-940 (`_each_frame`: `except Exception: continue`), motion.py:166-181 (REC_MAX 1500 / ATTR_MAX 300: `M.dropped++`), motion.py:1095, 1251, 1527-1551 (`frames_read`, `dropped_changes`, `regions_capped`, `unmapped_tiles`); none is read by t2a/t2b/t2c/t2d/t3a (grep: the fields are only written)
- What: a frame whose `evaluate` throws (navigating, detached, a frame in the middle of loading) simply drops out of the media read, the facts read and the live-region read. Media in it is never seen (2.A DNA), its live regions are missing (2.D FAIL rather than PASS, safe) and its Web Audio contexts are missing. The mutation log stops at 1500 records and 300 attribute changes; 2.D N1 ("the changes ... are incomplete") only tests `not changes(region)`, so a region with some recorded live-region changes and many dropped non-live ones is PASS (N2). `regions_capped` (40 regions) and `unmapped_tiles` do not reach any outcome either. This is the pattern already found in sister checks (cap recorded as a note, page still passes).
- Evidence: read (grep of consumers). Not run: a dashboard page with >1500 DOM mutations in 6.5 s was not built.
- Fix: put `frames_read < len(page.frames)`, `dropped_changes > 0`, `regions_capped` and `unmapped_tiles > 0` into A1/N1 (NEEDS REVIEW, not performed, naming the cap) so a cut-short watch can never become DNA or PASS.
- Confidence: likely (consumers grepped; behaviour on a real overflow not run)

### N-06 Only the first 30 `<img>` are decoded for animated images: a flashing GIF after them is invisible to 3.A and 2.B (both DOES NOT APPLY)
- Severity: P0
- Kind: false-pass-risk (wrong DOES NOT APPLY), silent cap
- Where: src/tobi508/motion.py:470-471 (`M.images`: `.slice(0, 30)`), motion.py:1412 (`srcs[:30]`), motion.py:1415 (`continue` for an unknown type, or a body over `IMAGE_MAX_BYTES` 5 MB or missing), consumed by src/tobi508/checks/t3a.py:113-118 (image triggers) and t2b `moving()` (G152 regions)
- What: pass T decides which images may be animated by reading at most 30 distinct `<img>` addresses, and silently skips any file it cannot decode (type other than GIF/PNG/WebP, over 5 MB, not recorded). Nothing records the skip: no `Unmeasured` entry, no hint. 3.A's A3 list names "a capture that failed" and media caps, but this one is not on it, so A4 gives DOES NOT APPLY ("every trigger was measured"). Below the first screen the 2 s screencast and the stepped capture cannot see it either. A gallery or news page with more than 30 images and an animated, strobing GIF is therefore reported as nothing flashing and nothing moving. Animated AVIF and CSS-background GIFs are also not decoded (the screencast is the only net, and only for the first screen).
- Evidence: ran two pages with the same strobing GIF (black/white, 60 ms frames, infinite loop) below a 2000 px spacer. `g_one.html` (1 other image): 3.A NOT_TESTED A2 s1:F2 ("An animated image below the first screen: 8.5 flashes per second ..."), 2.B NEEDS REVIEW (moving found). `g_many.html` (31 small images before it): 3.A DNA A4, 2.B DNA A2. Only the count changed.
- Fix: when a page has more than 30 images, or a candidate image is skipped (type, size, not recorded), record it as unmeasured (3.A A3) and as a hint for 2.B (NEEDS REVIEW); better, decode every distinct image file that the HAR has with a GIF/WebP/APNG/AVIF signature, not only the first 30 `<img>` tags.
- Confidence: confirmed (ran 2 pages)

### N-07 3.A: strobing that starts after the 6.5 s watch (or a failed or skipped screencast) is DOES NOT APPLY
- Severity: P1
- Kind: false-pass-risk (wrong DOES NOT APPLY)
- Where: src/tobi508/checks/t3a.py:213-236 (`collect`: screencast `except Exception: st.screencast = None`; skipped silently when `ctx.open_motion is None` or `ctx.out_of_time()`), :237-238 (no trigger -> A4)
- What: Triggers are what pass T saw in 6.5 s plus a 2 s screencast. A strobe started by a script at 9 s is never seen, and the page is A4: "Nothing on this page flashes more than three times a second". Separately, a screencast that raises, is skipped for time or lacks a browser leaves no `Unmeasured` entry, although spec A3 lists "a capture that failed or that time cut short" and calls the screencast "the net"; A4 then rests on the net that never ran. (Pass T's own `mp.timers` already holds the 9 s timer, as in N-04.)
- Evidence: ran `f_late.html` (a 500x400 box toggled black/white every 80 ms by an interval created in `setTimeout(..., 9000)`): 3.A DNA A4. Control `f_now.html` (same, starts at once): NOT_TESTED A2 F2, 6.5 flashes per second. The screencast failure paths: read only (not run).
- Fix: add an `Unmeasured("a screencast ...")` in the three silent branches; treat a timer or `fast` hint longer than the watch (as 2.C's `hints`) as A3 for 3.A too.
- Confidence: confirmed for the late strobe (ran); likely for the screencast branches (read)

### N-08 2.B: a streaming player or over-cap video is DOES NOT APPLY; spec A1 has no code
- Severity: P0
- Kind: false-pass-risk (wrong DOES NOT APPLY), spec row with no code
- Where: src/tobi508/checks/t2b.py:114-115 (`video_failed`: only `m.error` on a `<video>`), :170-175 (A1); spec 2b A1 ("a streaming player such as YouTube or Vimeo, or media over the recording cap -> NEEDS REVIEW"); compare t2a.py:92-112 and 130-141, t3a.py:149-157 which do implement it
- What: 2.B's A1 spec text names three ways a video "could not play from the recording": an error, a streaming player, media over the cap. The code implements the first only. A page whose only motion is an autoplaying YouTube/Vimeo iframe (or a large looping background video over the 50 MB / 15 s store cap that does not raise `error`) has nothing moving in the replay, so 2.B says DNA with "Nothing on it moved" while 2.A and 3.A on the same page say NEEDS REVIEW.
- Evidence: ran `y_embed.html` (`<iframe src="https://www.youtube-nocookie.com/embed/abc123?autoplay=1&loop=1">`): 2.A NEEDS REVIEW A2 (streaming player), 3.A NEEDS REVIEW A3 (video player from another site), 2.B DNA A2/G1, 2.C DNA A3. grep: no `STREAMING`, `over_cap`, `iframes` or `blob:` in t2b.py, t2c.py, t2d.py. Over-cap path: read only, not run (needs a >50 MB video).
- Fix: share one `unmeasured_media(mp)` (2.A, 2.B and 3.A each keep their own regex today, see N-10) and use it in 2.B's A1.
- Confidence: confirmed for the streaming iframe (ran); likely for over-cap (read)

### N-09 2.C: only the first of several "starts when scrolled into view" elements is scrolled to; the others leave no hint and 2.C says DOES NOT APPLY
- Severity: P1
- Kind: false-pass-risk (wrong DOES NOT APPLY), silent cap
- Where: src/tobi508/motion.py:1591-1611 (`_scrolled_watch`: `target = mp.below[0]`), motion.py:1655 (one scrolled watch only), `M.below` returns up to 10 (motion.py ~455); src/tobi508/checks/t2c.py:73-100 (`hints` has no entry for the unscrolled elements); spec 2c "Scrolled watch" says "the first one is scrolled to"
- What: pages often observe several elements with one `IntersectionObserver` (lazy images, reveal-on-scroll blocks, counters). Pass T scrolls to the first only; a counter or ticker that starts when the second or third comes into view is never watched, and `hints()` does not mention the leftover elements (only carousels, timers, polling, walk), so 2.C is A3 DOES NOT APPLY and 2.B/2.D follow. Understanding 2.2.2 says starting on scroll counts as starting automatically.
- Evidence: ran `s_io.html` (IO observes `#a` at 1500 px and `#b` at 4600 px; only `#b` starts a 1 s counter): 2.C DNA A3, 2.B DNA A2. Control `s_io1.html` (same, `#a` not observed): 2.C FAIL A5, r1:K6 with "Visitors 7". Only the number of observed elements changed.
- Fix: scroll to every `below` element (each its own short watch or one pass that scrolls in steps) or at least add "N more elements wait to be scrolled into view" to `hints()` so A2 gives NEEDS REVIEW.
- Confidence: confirmed (ran page and control)

### N-10 2.A media cap and three different "streaming player" patterns
- Severity: P2
- Kind: gap, design
- Where: src/tobi508/motion.py:392 (`slice(0, 20)`; `total` is kept in `Media.total`), src/tobi508/checks/t2a.py:44-47 (needs `autoplay=1`), src/tobi508/checks/t3a.py:34-37 (any embed), t2b none (N-08), motion.py:445-449 (`iframes ... .slice(0, 30)`)
- What: (a) 2.A ignores every audio/video element after the 20th in a frame; 3.A names it ("audio and video elements past the first 20", t3a.py:138-148) but 2.A does not use `Media.total`, so a podcast or media-library page whose 21st `<audio autoplay>` plays is DNA. (b) 2.A treats an iframe as streaming only when the URL has `autoplay=1`; a YouTube embed started through the JS API (`enablejsapi=1`, no parameter), Vimeo `autoplay=true`, or any other player host (Wistia, JW Player, Brightcove, SoundCloud) is not an instance, so DNA. 3.A treats every YouTube/Vimeo embed as unmeasured regardless. (c) Only the first 30 iframes are listed.
- Evidence: read (regexes and slices). `y_embed.html` (N-08) exercised the matching path only.
- Fix: one shared helper in `motion.py`/`engine.py` used by 2.A, 2.B, 3.A: unmeasured when `Media.total > 20`, when any iframe is a known player host (not only with `autoplay=1`: it can be started by script), or when iframes were cut at 30.
- Confidence: likely

### N-11 J2's key is not checked against the page text (spec guard missing); 2.A-2.C press whatever key the answer names
- Severity: P2
- Kind: security (principle 5 limit), spec row with no code
- Where: src/tobi508/mechanism.py:499-539 (`press_answered`: `parse_key(a.get("key"))`), src/tobi508/checks/t2a.py:387-402, t2b.py:537-553, t2c.py:602-618 (the answer's `quote` is not stored), src/tobi508/mechanism.py:58-71 (`BROWSER_KEYS`), spec 2c section 4 J2 ("Guard: the quote must be found in input.text, and a key must parse as modifiers plus one key; else NEEDS REVIEW")
- What: principle 5 allows a key press only for "a key combination that page text names". The code checks the other limits (modifiers plus one key, `parse_key`; not in `BROWSER_KEYS`; one combination per run through `evidence/keys.json`; fresh replay `open_session`; only when `choice == "describes"`) but never that the combination, or a quote, occurs in the text. The apply_answers copies drop `quote`; nothing compares `key` with `mp.elements[c.element].name`. The key therefore comes from the agent's answer, not from the page: a hallucinated or injected-prompt-steered answer (the agent reads untrusted text) presses any modifier+key combination once. The effect is limited (one press, one combination, no PASS reachable, see N-13), so P2.
- Evidence: read (grep for `quote`/`.key` in checks and mechanism: only t4c.py:925 and t5* check quotes). Not run.
- Fix: in `press_answered`, normalise `parse_key(key)` and require the normalised combination to appear in the normalised element text (or the answer's `quote` to be a substring of it), else `cannot_try`.
- Confidence: confirmed (read)

### N-12 J2 is asked only when the text matches an English-only word list: non-English instructions become "no", so K6 FAIL
- Severity: P2
- Kind: bug (false FAIL), English-only matching
- Where: src/tobi508/checks/t2c.py:38-46 (`MENTION`) and :191-198 (`Inst.j2_choice`: "no" mechanically when `MENTION` does not match), used by t2a.py:366, t2b.py:494 and K6 at t2c.py:253-264
- What: a text candidate is only sent to J2 when its text contains `pause|stop|hide|freeze|turn off|control|button|mute|volume|sound|audio|+|hotkey|shortcut`. A Spanish page ("Presione P para pausar", "Detener", "silenciar") or any non-English text is answered "no" with no question, so if the controls also give no effect K6 gives FAIL ("no way to pause") on a page that says how. None of the English stems match "pausa", "detener" or "arrêter". Federal sites publish Spanish pages, so this is plausible.
- Evidence: read (regex); not run.
- Fix: ask J2 for every text candidate in the top/before/after windows (at most 9 per content) or, if tokens are the concern, treat a non-matching text as "unsure" (NEEDS REVIEW) when the page language is not English.
- Confidence: confirmed (read); behaviour on a Spanish page not run

### N-13 PASS is unreachable in 2.A-2.C (E2 needs 13.A, not built); K6 FAIL has no guard for unrecorded code
- Severity: P2
- Kind: design / gap (not a false PASS)
- Where: src/tobi508/checks/t2c.py:282-306 (`er3_tests` always appends "13.A"; `er3_missing` lists tests not registered), E2 at :316-321; spec 2c 3c; engine.py:93-110 `apply_guards`, spec front matter of 2a/2b/2c has no `guards:`
- What: Principle "a working mechanism is NEEDS REVIEW, never PASS" holds, and holds only because 13.A is not built: `er3_missing` is never empty, so E2 never matches. The E2 branch, `E2` sentences and the G4 PASS path are dead until 13.A, 6.A, 7.A, 7.E, 12.D, 13.B, 13.C, 18.A are built (all appended by rule). Separately, these tests press keys and conclude "no mechanism" (K6 FAIL, 2.A/2.B/2.C) by watching what a replay does; the GU guard (recording lacks code the page loads when used) only moves a PASS to NEEDS REVIEW, so with unrecorded code a working pause button that needs lazily loaded code gives K6 FAIL, a false FAIL. The spec says tests that press keys cannot PASS while the recording lacks code; it says nothing about FAIL.
- Evidence: read (REGISTRY listing of checks/ has no t13a; grep `unrecorded_code` use in apply_guards). Not run.
- Fix: say in the spec that PASS is not yet reachable; add GU to K6 (move FAIL to NEEDS REVIEW when `unrecorded_code_count > 0`).
- Confidence: confirmed (read)

### N-14 2.D N3 and N4 are not tied to the change; N1 does not test completeness
- Severity: P2
- Kind: gap (looser than spec)
- Where: src/tobi508/checks/t2d.py:53-58, 60-76 (`dialog()` = any dialog opened during pass T that holds focus or a focusable element; `focus_in` = any time focus entered the region); spec 2d N3 ("a dialog opened *with it*") and N4 ("focus moved into the changed content *with it*")
- What: an unrelated dialog (a cookie or survey dialog opening at 2 s) or an autofocus into the carousel at load satisfies N3/N4, so a ticker that is not in a live region goes to J2/J1 instead of N5 FAIL. The agent then judges a dialog or focus move that has no relation with the change; J1/J2 "sufficient" can then PASS by looking (allowed by principle 8). Time correlation (`Change.t` against `Dialog` and `FocusMove.t`) is not used; `Dialog` has no time at all. N1 ("changes or live-region reads are incomplete") only tests `not changes(region)`; see N-05 for `dropped_changes`.
- Evidence: read.
- Fix: record `t` on `Dialog`, keep only focus moves and dialogs within about 1 s after one of the region's changes, and add the dropped/unread-frame conditions to N1.
- Confidence: likely

### N-15 2.B `essential()` guard is English-only and edge-fragile
- Severity: P3
- Kind: gap
- Where: src/tobi508/checks/t2b.py:120-139 (`LOADING = \bload`, `game|simulat|video|demonstrat`, `late = changed_at[-1] >= 6.0`)
- What: spec J1 guard: "essential is accepted only with a reason other than loading" when a region still moves at 6.5 s on a page with usable controls. The code checks the agent's free-text `reasons` for the word "load". "progress indicator", "waiting", "spinner", other languages and the word "video" in "not a video" slip through; `late` needs a change at or after 6.0 s, which a 1.5-2 s period can miss with the 0.35/0.45 s frame steps. Result: a false DNA (A4) on the agent's word only.
- Evidence: read.
- Fix: guard by evidence, not words: a region with a change after 5 s on a page with a control is never "loading only"; do not accept essential then.
- Confidence: likely

### N-16 2.A edge: a clip of 3.0-3.5 s is not an instance; detached `audio_watch` baseline
- Severity: P3
- Kind: gap
- Where: src/tobi508/checks/t2a.py:114-124
- What: the decision uses the single read at 3.5 s; a clip 3.2 s long has ended (`paused` true) at that read and is skipped as "not playing", but it played for more than 3 s, which the TT counts. The window is about 0.5 s of clip lengths. Also `mechanism.audio_watch` (mechanism.py:318-346) returns "stopped" when the media is simply paused for 3.5 s without checking it was playing at the start of the watch; the K2 focus-only probe covers it when the audio never starts in the replay (both probes "stop"), so this is covered.
- Evidence: read.
- Fix: for `ended` media use `duration - first.time` (already computed) and treat ended-with-`left > 3` as an instance.
- Confidence: likely (not run)

## Spec against code, row by row

Legend: same = same condition; order = same first-match order. "2c rows" are `t2c.INSTANCE_ROWS` (t2c.py:212-278), reused by 2.A and 2.B.

### 2.A (spec 1.0.0, t2a.py)

| Spec row | Code | Same condition? | Order |
| --- | --- | --- | --- |
| Terms: not paused, not muted, volume > 0 | t2a.py:115-117 | same, at the one read nearest 3.5 s | n/a |
| Terms: advancing (`currentTime` grew since 0 s) | t2a.py:118 (`at.time > first.time`) | same | n/a |
| Terms: audible, peak above -40 dBFS | t2a.py:125-128 (`<= -40` is skipped) | same; None -> unmeasured (A2) | n/a |
| Terms: plays more than 3 s (duration from start, or loop) | t2a.py:122-124 | same; ended clip of 3.0-3.5 s missed (N-16) | n/a |
| Terms: Web Audio, node connected to destination and context `running` | t2a.py:142-150 (`"running" in audio_states`, set by the connect hook, motion.py:155-159) | same; always unmeasured (A2) | n/a |
| Terms: media in any frame | `_each_frame` (motion.py:933) | looser than text: frames that throw are skipped, media in shadow roots/detached `Audio` not seen (N-01, N-05) | n/a |
| Terms: at 3.5 s only | t2a.py:95 | same as spec text, wrong for late audio (N-02) | n/a |
| A1 pass T could not run | t2a.py:183, 270-277 | same | 1st |
| A2 error / streaming / over cap / Web Audio | t2a.py:107-112, 130-150, 184-189, 278-290 | partly: over-cap only when paused or not advancing (an over-cap file that plays is "could not measure loudness", also A2, fine); the A2 note does not give file size/length nor offer the no-limit run (spec: "the note gives each file's size and length"; not in t2a.py, may be in pipeline: not checked); streaming only with `autoplay=1` (N-10) | 2nd |
| A3 no auto-playing audio | t2a.py:190, 291-299 | same | 3rd |
| A4 otherwise | t2a.py:191 | same | 4th |
| K1-K8 (2c rows, top window only, slowed = no effect) | t2c.py:212-278 via `instance_outcome(_inst(st, a), st.selected, INSTANCE_ROWS, E_ROWS)`; top window: mechanism.py:416-417; slowed: `slowed_counts=False` t2a.py:209 | same | same as 2.C |
| (code only) U1: unmeasured instance -> NEEDS REVIEW | t2a.py:303-304 | spec A2 says "the unmeasured media is a NEEDS REVIEW instance": same outcome, row id U1 not in spec | before K rows |
| E2 PASS | t2a.py:196 | same text; unreachable because 13.A is not built (N-13) | 1st of E |
| E3 NEEDS REVIEW | t2a.py:197 | same | 2nd |
| G1-G5 | engine.py:46-77 via t2a.py:320-324, `incomplete=[]`, `complete_for_pass=True` | G3 "or time ran out" not passed in; K7 covers skipped probes | same |
| J2 (text in the top window) | t2a.py:342-384 (questions), mechanism.press_answered | question asked only when `MENTION` matches (N-12); key not checked against text (N-11) | n/a |
| Note (tab mute) | t2a.py:49-52, appended only on the instance path (t2a.py:329) | same | n/a |
| Guards in front matter | none declared | spec none | n/a |

### 2.B (spec 1.1.0, t2b.py; spec file header says 1.1.0, the module docstring says 1.0.0)

| Spec row | Code | Same condition? | Order |
| --- | --- | --- | --- |
| Terms: moving region = moving kind or updating with children moving, still moving (change after 5 s, >= 3 frames) or non-pixel source | t2b.py:63-85 | same text; blinking by `visibility` classified updating so never moving (N-03); `source == "dom"` excluded (spec silent) | n/a |
| Terms: colour-only change | t2b.py:91-111 | same | n/a |
| A1 pass T failed | t2b.py:173 (`not mp.ok`) | same | 1st |
| A1 video error | t2b.py:114-115, 173 | same | 1st |
| A1 streaming player, media over the cap | no code | MISSING (N-08) | |
| A2 no moving region -> DNA | t2b.py:177 | same; no "not watched long enough" path (N-04, N-06, N-09) | 2nd |
| A3 every moving region covers all elements | t2b.py:163-167, 179 | stricter (adds box overlap with changed pixels): safe | 3rd |
| A4 every moving region essential (J1) -> DNA | t2b.py:123-139, 180-184 | spec guard on `essential` implemented by regex over the agent's `reasons` (N-15) | 4th |
| A5 J1 unsure, no other region applies | t2b.py:185-187 | same | 5th |
| A6 otherwise | t2b.py:188 | same | 6th |
| K1-K8 with 2.B's stopped | t2b.py:200-208 (`ROWS`: INSTANCE_ROWS with C1 and K6 inserted before K7), `slowed_counts=False` | same | same as spec (C1 before K6); ran `t2b.ROWS`: K1 K2 K3 K4 K5 C1 K6 K7 K8 |
| C1 colour-only, 3+ states, K6 evidence -> NEEDS REVIEW | t2b.py:195-198, 203 | same condition | see order note |
| E1-E4 reading 2.B's J2 | t2b.py:217 (`j1=st.j2`), 2c E_ROWS | same | same |
| G1-G5 | t2b.py:384-394, `incomplete` = pending J1 only | G3 "time ran out" via K7 | same |
| Note `<blink>` | t2b.py:297-304 | same | n/a |
| Guards in front matter | none declared | spec none | n/a |

Order of C1/K6 (t2b.py:200-208): verified by running `t2b.ROWS`: K1 K2 K3 K4 K5 C1 K6 K7 K8, as the spec asks.

### 2.C (spec 1.0.0, t2c.py)

| Spec row | Code | Same condition? | Order |
| --- | --- | --- | --- |
| A1 pass T could not run | t2c.py:146 | same | 1st |
| A2 no instance but a hint | t2c.py:147-152, hints at 73-100 | hint list: walk unsettled (>= 3), polling, timer longer than watch, carousel unchanged, region stopped before 5 s. MISSING from `hints`: the elements waiting for scroll (N-09), cut-short scrolled watch, dropped/unread things (N-05) | 2nd |
| A3 no instance | t2c.py:153 | same | 3rd |
| A4 every element inside an instance and overlapping changed pixels | t2c.py:116-135, 154 | same (frame elements: inside is enough, spec silent) | 4th |
| A5 otherwise | t2c.py:155 | same | 5th |
| O1 instance only if still changing at 5 s | t2c.py:34, 60-70 | same (`changed_at[-1] < 5.0` = stopped early) | n/a |
| K1 reads failed, or none held and one unreliable | t2c.py:213-224 | same | 1st |
| K2 held and focus-only also held | t2c.py:225-234 | same | 2nd |
| K3 held and focus-only no effect | t2c.py:235-245 | same | 3rd |
| K4 key combination from J2 held | t2c.py:246-251 | same, but key not verified against text (N-11) | 4th |
| K5 cannot try | t2c.py:252 | same | 5th |
| K6 every control no effect, J2 no, nothing untried -> FAIL | t2c.py:253-264 | also accepts `not_operable` as no effect (spec: a link that goes somewhere "counts with no effect": same); zero candidates also FAIL (vacuous; spec "or there are none" covers texts only) | 6th |
| K7 not probed / untried / unreachable | t2c.py:265-276 | same | 7th |
| K8 anything else | t2c.py:277 | same | 8th |
| E1 not evident -> FAIL | t2c.py:310-315 | same | 1st |
| E2 evident and nothing missing -> PASS | t2c.py:316-321 | same; unreachable (N-13) | 2nd |
| E3 evident otherwise | t2c.py:322-327 | same | 3rd |
| E4 unsure/unanswered | t2c.py:328 | same | 4th |
| G1-G5 | t2c.py:483-491 | `incomplete=[]` always | same |
| 3c ER 3 table | t2c.py:282-299 | 7.A/7.E for kind image **or control** (spec: "is, or contains, an image or icon"): looser = more NEEDS REVIEW, safe; `12.D` when `region.frame > 0`, not "mechanism inside an iframe" (uses the content's frame, spec: the mechanism's) | n/a |
| J1, J2 questions | t2c.py:524-599 | J2 asked only on `MENTION` words (N-12) | n/a |
| Guards | none declared | spec none | n/a |

### 2.D (spec 1.1.0, t2d.py; module docstring says 1.0.0)

| Spec row | Code | Same condition? | Order |
| --- | --- | --- | --- |
| A1 2.C section 1 gives NEEDS REVIEW | t2d.py:171-184 (row ids "A1", "2.C-A1/A2") | same | 1st |
| A2 2.C gives DNA | t2d.py:185-196 | same (finding rows say "A2" while the code's own variable names are A3/A4) | 2nd |
| A3 otherwise | t2d.py:197 | same | 3rd |
| N1 changes or live reads incomplete | t2d.py:62-66 (`not changes(region)`) | stricter-text missing: dropped log, unread frames not tested (N-05, N-14) | 1st |
| N2 every change in a live region -> PASS | t2d.py:67-72 (`not unlive()`: `live_at_start` false) | same | 2nd |
| N3 change not live, dialog opened with it holding focus -> J2 | t2d.py:73 | looser: any dialog in pass T (N-14) | 3rd |
| N4 change not live, focus moved into it with it -> J1 | t2d.py:74 | looser: any focus entry into the region (N-14) | 4th |
| N5 none -> FAIL | t2d.py:75 | same | 5th |
| J1/J2 sufficient -> PASS; not sufficient -> FAIL | t2d.py:85-91 | same; only "sufficient" by looking (allowed, principle 8) | after N3/N4 |
| N6 anything else -> NEEDS REVIEW | t2d.py:92 | same | last |
| G1-G5 | t2d.py:213-217 | same, `incomplete=[]` | same |
| Terms: changes = text/src/children records; attributes when none | t2d.py:38-42 | same | n/a |
| Terms: live region present and rendered at 0 s | motion.py:187-198 (`mark0`, `vis`) | same | n/a |
| Notes (timer/marquee, live off) | t2d.py:136-144, 104-112 | same | n/a |

### 3.A (spec 1.1.0, t3a.py; module docstring says 1.0.0)

| Spec row | Code | Same condition? | Order |
| --- | --- | --- | --- |
| A1 pass T could not run -> NEEDS REVIEW | t3a.py:216-218, 588, 793-796 | same | 1st |
| A2 flashing found in any source -> NOT TESTED | t3a.py:589, 813-829; `Page.flashing` = sources with `analysis.flashing` (t3a.py:789) | same; screencast alone is not a source (-> A3 `unexplained`) as the spec's list of sources says | 2nd |
| A3 not measured: streaming, over cap/not recorded, undecodable/no file video, > 3 videos, > 20 media, > 10 s, marquee, capture failed/cut, screencast saw more than measured | t3a.py:138-167 (20, streaming, marquee), 403-416 (3 videos), 434-507 (video reasons), 549-569 (> 10 s), 307-313/326-332 (stepped cut/failed), 572-584 (`unexplained`) | all present except: screencast failed/skipped (N-07); images skipped in pass T (N-06); images "not shown at this size" silently skipped (spec edge case allows) | 3rd |
| A4 no flashing, everything measured -> DNA | t3a.py:596 | same; late start not observed (N-07) | 4th |
| F2, F3, F1, F4, F5 assessment | t3a.py:630-643 (`assess`: F2, F3, F1, F4, F5) | same order | order same |
| WCAG 2.2 red note | t3a.py:649-659 | same | n/a |
| Page assessment fails > cannot > passes | t3a.py:725-729 | same | n/a |
| NOT_TESTED only for A2; assessment only in the summary | t3a.py:813-829; grep of `NOT_TESTED` outside t3a: none in checks | same | n/a |

Checked and fine: `Outcome.NOT_TESTED` is produced in `t3a.py` only (grep), through A2 only; the WCAG assessment is only text in `summary`; 3.A never returns PASS or FAIL.

## Cost and size (lower priority)

- Fixed waits: pass T watches 6.5 s (reads at 0, 3.5, 6.5 s, motion.py:41-43) plus the scrolled watch another 6.5 s and a load when something below the first screen is observed (motion.py:1655-1656). Probe per content: per candidate one fresh load, 0.6 s settle, then the confirm time (min 5.5 s, up to 15 s, `mechanism.confirm_s`) when nothing changes, shorter when it changes; a candidate that held costs a second load and watch (focus-only). Worst case per content: 8 controls x (load + 15 s) + 8 x focus-only = about 250 s, three contents about 12 min, bounded by `RUN_LIMIT_S`/`MAX_RUN_S`. 2.A uses a 3.5 s watch (`AUDIO_CONFIRM_S`), so about 4-5 s per tried control and no `MAX_INSTANCES` cap (t2a.py:411-414 probes every audio, each with up to 3 candidates; the cache `probe_shared` is per region key). 2.D: no waits. 3.A: one more load plus 2 s screencast (about 3 s), stepped capture about 6-7 s, each of up to 3 videos up to 20 s, images under a second each (spec section 2 "Time budget"); worst case about 75 s.
- Loads (worst case): pass T 1 (+1 scrolled), 3.A screencast 1 + stepped 1, probes up to 3 x 8 x 2 = 48 for 2.B/2.C together (shared) and for 2.A up to 3 per audio, key press 1 per run.
- Shared across 2.A-2.D: `motion.collect` (cached in `ctx.cache["motion"]`), `probe_shared`, `INSTANCE_ROWS`, `E_ROWS`, `instance_outcome`, `Inst`, `POSITION`, `MENTION`, J2 text. 2.D shares nothing else; 3.A reuses pass T (`keep_shots=False`) but loads twice more.
- Repeated: each check recomputes `applicability(mp)` in `collect`, `evaluate`, `questions_for` (t2c.py:625, 435, 555; t2d.py:171, 273) and `instances(mp)`; cheap but easy to cache on the state.
- Copied code between t2a/t2b/t2c/t2d: `_finding` (t2a.py:250-264, t2b.py:280-294, t2c.py:403-417, t2d.py:147-161: same body, only `TestId` differs); `apply_answers` (t2a.py:387-402, t2b.py:537-553, t2c.py:602-618, t2d.py:323-337); `_images` (t2c.py:519-521, t2d.py:267-269, also t2b `_two_frames` style); the `A1`/`A2` not-performed blocks (t2a.py:270-290, t2b.py:311-322, t2c.py:436-451, t2d.py:172-184); the E3 sentence (t2a.py:222-228, t2b.py:245-251, t2c.py:374-380); the K6 and K2 sentences (t2a.py:229-243, t2b.py:252-271, t2c.py:381-392); the five-method `Check*` class bodies (t2a.py:418-448, t2b.py:571-606, t2c.py:642-671, t2d.py:346-374). A shared `RowsCheck` helper in `t2c` would cut about 250 lines.
- Text sent to the agent: J1 (2.C) question 511 chars + rubric 328; 2.B J1 question about 640 + rubric about 470 and 2 pictures per region (or 2 crops); 2.B J2 evident question about 440 + 1 picture; 2.C J1 1 picture; J2 (2.C/2.B) question about 270 + rubric 210 per text candidate (up to 3 per content per window; `question_texts` shares the text); 2.A J2 about 420 + 230 per text candidate; 2.D question about 330 + rubric about 270 each, pictures are evidence only (no inline picture). Summaries: one sentence per instance (K6 sentence about 330 chars) repeated for every audio element or region, plus `TAB_MUTE_NOTE` (about 140 chars) on every 2.A instance finding; 2.C appends all hints (one sentence each) to every finding. `Instance.description` repeats the row trace that is already in `rows`. None of this is large; the 2.A and 2.C K6 sentences repeated per instance are the biggest avoidable part for a page with many audio elements.
- Silent caps: 20 media per frame (2.A, N-10), 30 images (N-06), 30 iframes (motion.py:449), 10 loudness sources (motion.py:1067; this one is reported as "could not measure", fine), 1500 mutation records / 300 attribute changes (N-05), 40 regions (N-05), first scrolled-to element (N-09), `MAX_COMPONENTS` 30 changed-tile groups per frame (motion.py:42, not read further).

## Unverified leads

- Over-cap video in 2.B: no code (N-08); not run, since it needs a >50 MB video.
- 2.D with more than 1500 mutations in 6.5 s (a busy dashboard): N2 PASS on recorded live changes while later non-live ones were dropped (N-05); not run.
- 3.A `screencast` raising or `ctx.out_of_time()` before it: branches silent (N-07); not run.
- `_long_images` skips APNG/animated AVIF that Chrome plays when the type sniff fails (`_image_type` knows GIF, PNG, WebP only); not run.
- A `<video>` in a shadow root for 2.B/3.A (same `querySelectorAll` as N-01): read only.
- Hover-only content and content started by a first user gesture (a carousel that starts on the first mouse move): no probe, no hint; TT's own text also does not ask, left as is.
- 2.C `changed()` for elements in an iframe returns True when merely inside the region (t2c.py:123-124): a page whose only content is a changing iframe plus other static elements in the top page is fine (those are not in `r.elements`), but an iframe with static and changing parts inside an instance region makes A4 DNA more likely; not run.
- 2.A: clip played from `#t=` fragment and `at.time > first.time` on replays where the first read is delayed (slow load) could see `first.time` already advanced; fixture `t-audio-short`/80f0bf cover the normal case only.
