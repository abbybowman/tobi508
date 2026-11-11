# E: checks 4.A, 4.B, 4.C review (base.py, t4a.py, t4b.py, t4c.py)

(overview at top is filled in at the end)

## Findings

### E-01 4.A: hover cap (HOVER_MAX 40) only adds a note, the page still PASSes
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4a.py:501-507 (cap), :1222-1227 and :1253 (only `st.incomplete` blocks G4; `st.notes` does not); spec specs/rules/4a-keyboard-access.md:101 (G3 "a scan, check or cap was not finished") and :69 (C?)
- What: The hover scan stops after 40 hovered stops and appends the sentence "Only the first 40 elements were checked..." to `st.notes`, not `st.incomplete`. G4 then PASSes, and the PASS text still says "we found nothing a keyboard user would miss". Any page with more than 40 Tab stops (most agency pages) whose hover menu sits on stop 41+ (a footer or side menu, a late mega-menu) is PASSed without that menu ever being looked at. Every other cap in this file (CLICK_MAX, EXECUTE_MAX, ARROW_MAX, REVEAL_REPLAYS, time) goes to `incomplete`; this one is the odd one out. The spec's G3 says a cap not finished means NEEDS REVIEW.
- Evidence: Ran /tmp/.../e/pages/hover45.html (45 links, a mouse-only `div onclick` shown only by `#l45:hover ~ .m`). Result: `4.A PASS ['A3','G4']`, summary contains "Only the first 40 elements were checked for menus that open when the mouse rests on them." and "we found nothing a keyboard user would miss".
- Fix: Append to `st.incomplete` instead of `st.notes` (G3), or hover more stops. If Abby wants a note-only cap, the spec must say so (the spec currently says the opposite).
- Confidence: confirmed

### E-02 4.A M3: a mouse-only link with the same href as any reached link (e.g. "#") PASSes
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4a.py:701-728 (`_k` / `_same_link` compare raw `el.href` strings), :1023-1028 (M3); spec 4a:72 (M3 "whose address is the address of a reached link")
- What: `_same_link` returns the first reached stop whose href string equals the candidate's. Mouse-only widgets very often are `<a href="#" onclick=...>` or `href="javascript:void(0)"`, and a page nearly always has some reached link with the same string (a "#" skip or top link, a `javascript:` link). That candidate is PASSed by M3 as "goes to the same place", although the href is a placeholder and the real function is the click handler. The same applies to a click that navigates to a URL equal to a reached link (line 608), which is the real intent of M3. For a native K, the click is never made (line 599), so no check shows the link really navigates.
- Evidence: Ran pages/samehref.html (`<a href="#">Home</a>` reached; `<a href="#" tabindex="-1" onclick="...show panel...">Open settings</a>`). Result: `4.A PASS ['A3','k1:M3','G4']`, text: ""Open settings" (link) can't be reached with the keyboard, but "Home" (link) goes to the same place and can."
- Fix: For K, ignore hrefs that are `#`-only, empty, `javascript:` or equal the page URL with a fragment; better, require M3 only when the click's observed navigation lands on the same URL (and click native links too), else go to J1. The spec row needs the same wording.
- Confidence: confirmed

### E-03 4.A A1: a page with only canvas, drag or mousemove content is DOES NOT APPLY; the U signals are dropped
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4a.py:965-969 (A1) and :1184-1201 (A1/A2 return before instances are read); spec 4a:24 (A1) and :46 (M16), :98 (G1 first)
- What: A1 needs zero stops, zero inventory, zero pointer-target `total`. Canvas (>= 50 px), `draggable`, mousemove/touch/wheel listener elements, `object/embed` and unreadable frames are recorded as U instances, but `evaluate` returns "does not apply" at A1 without looking at `st.instances`. A page that is only a canvas game, a drag-and-drop board or a map with mousemove handlers therefore gets DOES NOT APPLY with the text "Nothing on this page can be used with a mouse or keyboard". The spec's G1 rule says the same (so spec and code agree), but it contradicts the spec's own M16 intent ("never a reason to PASS") and principle 3. The same for an unreadable frame (`u0`) on a page with no other content.
- Evidence: Ran pages/canvasonly.html (canvas with a mousemove listener plus `draggable=true` div, nothing focusable). Result: `4.A DNA ['A1','G1']`, summary "Nothing on this page can be used with a mouse or keyboard, so this test does not apply."
- Fix: A1 should also require no U instances (else NEEDS REVIEW via M16); spec A1 must say so (needs Abby's approval: turns a DNA into NEEDS REVIEW only, the safe direction).
- Confidence: confirmed

### E-04 4.A M11: title "available elsewhere" is a plain substring test on the whole page text
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4a.py:659 (`t in text`); spec 4a:44 ("contained in the page's visible text")
- What: A title is PASSed when its normalised text is a substring of the page's whole innerText, with no word boundary and no relation to the element. A title "Open" is "found" inside "Opening hours"; a title "Menu" or "Search" is found anywhere on a page that mentions it once. J2 (essential or not) is then never asked, so a tooltip with real, essential information is PASSed. A very short title (1-2 letters) matches almost any page.
- Evidence: Ran pages/titles.html: `<a href="#t" title="Open">x</a>` with `<p>Opening hours...</p>` gives instance `t2:M11` (PASS), no question. (The `<button title="Save draft">` with glyph text correctly asked J2.)
- Fix: Match on word boundaries and require a minimum length, or ask J2 whenever the title is not the whole text of some element. Spec wording needs the same tightening.
- Confidence: confirmed

### E-05 4.B: only the first 20 timing matches (each cut at 300 characters) go to J1, and nothing says so
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4b.py:117 (`[x[:300] ...][:MAX_MATCHES]`), :25; spec 4b:32 (says every matching sentence "goes out with the questions")
- What: Matches are collected in page order (page text of each frame first, then stop names, then titles), de-duplicated, cut at 300 characters each and then at the first 20. The sentences the agent sees are all it has, so a real instruction after 20 harmless matches ("quickly" and "for 5 seconds" are common words on long pages) is never shown; the agent answers `no_timing` and M3 PASSes. The stop-name/title matches are the first to be dropped because they are appended last. A long sentence (a list with no full stop) is cut at 300 characters and can lose the timing words. Neither cap is mentioned in the finding, the summary or `incomplete`. Page text sent as `page_text` is separate, but J1's rubric tells the agent to judge "the sentences".
- Evidence: Ran pages/manymatch.html (22 paragraphs "we respond quickly to every request", then "press and hold the Space key for 3 seconds on the Confirm button" with a real hold handler). `evidence/4b.json` has `matches` of length 20, last "Section 20 ...", and no sentence containing "hold"; the J1 question was open with exactly those 20. An agent answering from the question alone cannot find the instruction.
- Fix: Never drop silently: rank matches that contain a stop's name or the stronger words (hold, press twice) first, and when the cap or the cut applies add `incomplete` ("N more sentences not shown") so G3 applies; or raise the cap and send only distinct sentence stems.
- Confidence: confirmed (the cut; the PASS follows from an agent `no_timing` answer, not run)

### E-06 Principle 8 list does not allow 4.A J1/J2 or 4.B J1 to settle a PASS by looking, yet they do (M5, M13, M3)
- Severity: P1
- Kind: false-pass-risk
- Where: t4a.py:1042-1047 (M5), :1075-1080 (M13); t4b.py:376 (M3); CLAUDE.md principle 8 list ("4.E J1, 4.F J1, ... 19.A J1" — no 4.A, no 4.B, 4.C see E-?); specs 4a:92 and 4b:88 claim the principle covers them
- What: Principle 8 says an opinion leads to PASS only with a key press or mechanical check, or when the question is on the list. 4.A J1 (alternative -> PASS), 4.A J2 (not_essential -> PASS) and 4.B J1 (no_timing -> PASS) are not on the list and have no mechanical check besides "the named number is a stop" (4.A M5). One agent answer therefore turns a mouse-only control, an essential tooltip, or a real timing instruction into PASS. 4.B J2 and 4.B J1->FAIL do have key-press proofs; 4.B J1 no_timing has none. The spec text of 4.A says J1/J2 "are look-and-decide questions (CLAUDE.md principle 8)" but the CLAUDE.md list does not name them.
- Evidence: Read: instance rows above; CLAUDE.md principle 8 list. No test run (the answer path needs an agent).
- Fix: Either add 4.A J1, 4.A J2 and 4.B J1 to the principle's list (Abby's call, with the "unsure whenever not settled" duty) or add a mechanical check (4.A: press Enter on the named stop and compare its effect with the candidate's click effect, as 4.B's alternative press does; 4.B: none possible, so it is a list entry).
- Confidence: confirmed (by reading); severity depends on Abby's ruling

### E-07 4.C: pass E (error states) is skipped without a note when the run is out of time, and the page can still PASS
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4c.py:820 (`if not ctx.out_of_time():` with no else); `RunContext.out_of_time` base.py:116-123 only sets `ctx.timed_out`; spec 4c:113 (G4 "every P7 error state was Tabbed through") and :73
- What: Every other 4.C phase that skips work for time goes through `Collector.out_of_time`, which also appends "The run time limit was reached..." to `st.incomplete` (G3). The P7 gate uses the context's `out_of_time`, which does not. When P1/P2/P3/P4 finish and the deadline passes before P7, the error pass and its Tab walks never run, `st.incomplete` is empty, and G4 gives PASS ("We moved through the whole page ... never got trapped"). The only trace is a run-level `errors` string, which the pipeline writes as "what was not finished is NEEDS REVIEW" while this finding says PASS. The same gap exists when no trap or widget exists: `p3/p4` loops never run, so nothing records the late deadline. 4.A, 4.B and the other collectors have the same two out_of_time helpers; only 4.C's P7 gate lacks the note.
- Evidence: Ran pages/errform.html with `run_limit_s` 17 (runpage2.py): `errors: ['The run reached its time limit (17 s) before every test finished; what was not finished is NEEDS REVIEW ...']` and `4.C PASS ['A3','G4']`. With 13 s the walk itself ran out and gave NEEDS_REVIEW; with 21 s and 120 s the same page PASSes with no error. That P7 was the skipped step is likely (4.C `collected` cost is 4 loads in all runs; I did not trace the exact call), not proven.
- Fix: Use the Collector's `out_of_time()` (or append to `incomplete`) at line 820; better, one `out_of_time` helper that always records, used by every check. `apply_guards` or the pipeline could also turn any PASS into NEEDS_REVIEW when `ctx.timed_out` is set.
- Confidence: confirmed (symptom), likely (cause)

### E-08 4.A: a native button or link that only reacts to mousedown/mouseup/pointerdown PASSes (F54)
- Severity: P1
- Kind: false-pass-risk
- Where: t4a.py:615-620 (customs excludes `reason == native`), spec 4a:42 ("Native controls are not executed") and :160 (edge case "missed")
- What: A `<button onmousedown=...>` (or `a[href]` with a mousedown handler and `href="#"`) is a native stop, so it is never executed, and it is never a K candidate because the walk reaches it. Enter and Space fire `click`, not `mousedown`, so a keyboard user cannot use it: this is WCAG failure F54, the exact thing 4.A exists to find. The finding says "pressed Enter or Space on each custom control ... found nothing a keyboard user would miss". The spec lists only the keydown-cancelled case in its edge table, not this one. The own-listener data is already collected (`reason` "listener" is set only when no other reason applies, line 262-265, so the information is discarded for native controls).
- Evidence: Ran pages/mousedown.html (`<button onmousedown="...show panel...">Open panel</button>`): `4.A PASS ['A3','G4']`.
- Fix: For native stops that have a click-family listener that is not `click` (CDP listener list, already read for non-reasoned stops), run the execute check (Enter, then Space) or ask NEEDS REVIEW. Needs a spec change (Abby): it turns a PASS into a FAIL or a review.
- Confidence: confirmed

### E-09 4.B: the timing-word regex misses common instructions, so no match gives PASS (M1)
- Severity: P1
- Kind: false-pass-risk
- Where: t4b.py:30-35 (`TIMING`); spec 4b:32 (the word list), :46 (M1 "No match -> PASS")
- What: M1 PASSes when no sentence matches the list. The list is narrow: "press twice" matches but "Press Enter twice", "press the key twice" and "press Enter 2 times in a row" do not; "within 2 secs", "for 3s", "double-click" and "tap twice" do not; numerals only ("for three seconds" matches only because of "hold"). The text scanned is the loaded page text plus names and titles of Tab stops: no `aria-label`/`aria-description` of non-stops, no placeholder, no text in opened menus or dialogs. A page that tells users to "Press Enter twice to confirm" gets PASS and J1 is never asked.
- Evidence: Ran the compiled regex on sample sentences: no match for "Press Enter twice to confirm", "press the key twice", "Press the key 3 times within 2 secs", "Keep pressing Enter for 3s", "Double-click to open", "tap twice", "Press Enter 2 times in a row"; match for "Press and hold Space" and "Hold the key for three seconds". (Page text read: not run.)
- Fix: Widen the list in the spec (any verb of pressing plus "twice", "2-5 times", "again within", "N s/sec/secs") and let the miss go to NEEDS_REVIEW rather than PASS when the page has custom key handlers; the spec is the owner of the list (needs Abby).
- Confidence: confirmed (regex); the page-level outcome follows from M1

### E-10 4.A: `_describe_hidden` costs one fresh page load per hover-revealed target, uncapped
- Severity: P1
- Kind: time
- Where: t4a.py:559-563 (loop over `ks` of one stop, each calls `_describe_hidden`), :731-750; spec 4a:38 and :59 ("one fresh replay per hovered stop")
- What: The spec budgets one replay per hovered stop that revealed something (cap REVEAL_REPLAYS 10). The code does one Tab-and-Enter replay per stop (OK) but then, for every revealed target that neither focus nor Enter revealed, a further `open_session` + hover + full scan to get its name, role and href. A mega-menu with 30 items revealed by one stop costs 30 extra loads (about 3 s each) with no cap and no `incomplete` note; `out_of_time` is not checked in that loop. The data it fetches is the same for all targets of one stop (one hover, one full scan).
- Evidence: Read. Spec time budget vs code. Not run.
- Fix: One `_describe_hidden` per stop returning every target's description; check `_out_of_time` before each load.
- Confidence: confirmed (read)

### E-11 4.B and 4.C each put the whole page text in the result; two tests asking means it is sent twice and unbounded
- Severity: P1
- Kind: tokens
- Where: t4b.py:498-499, t4c.py:1505-1506 (`page_text` returns `state.texts` untrimmed); pipeline.py:727-736 (`_page_text` appends every asking test's text; `asking` is a set)
- What: When 4.B and 4.C both have open questions in one result, the full `innerText` of every frame (same page, two separate loads) goes out twice, with no size cap. A long page is tens of thousands of characters per copy. 4.B's J1 also gets the 20 matches (up to 6,000 characters), all of which are repeated inside page_text. 4.C also adds text revealed by Enter presses. Order of the copies is the iteration order of a set.
- Evidence: Read the three places. Not measured on a real page.
- Fix: Dedupe identical `{source, text}` entries in `_page_text`, cap total characters (and say so), and for 4.B send matches with a little context instead of the whole page.
- Confidence: likely

### E-12 4.A and the walk hook: silent failures that cut evidence without a note
- Severity: P2
- Kind: false-pass-risk
- Where: t4a.py:409-414 (`_scan`: `except Exception: continue`; the caller counts frames attempted, not frames scanned, so `unread` at :473 stays 0), :513-515 (`_point` None: stop silently not hovered, not counted), SCAN_FN :164 (`unreached.length >= 200` break, no note), :256-266 (`StopHook`: `reader.call` None gives `info None`, so no reason, no title, no X, no T for that stop), :284-285 (`_own_listener_types` swallows any error and returns no listeners)
- What: Each of these drops part of the evidence and the page can still PASS: a frame whose scan script throws counts as scanned; a stop that cannot be located is never hovered; more than 200 unreached targets in one frame are not looked at; a stop whose info read fails is neither executed nor title-checked; a listener read error makes a custom control look like a plain element. The `reader.call` None and `evaluate_top` points are already known; the others are new detail. (The 200-target cap cannot by itself give PASS because the first 200 are K instances, but the rest is unreported.)
- Evidence: Read.
- Fix: Count scanned frames and compare to the readable frames; add each failure to `st.incomplete` (G3).
- Confidence: likely (not provoked)

### E-13 4.A M11: an icon-only control whose only label is its `title` PASSes, so J2's own example is unreachable
- Severity: P1
- Kind: false-pass-risk
- Where: t4a.py:659 (`t == _norm(sr.name)`); spec 4a:44 (title is available elsewhere when it equals the stop's accessible name), :148 (J2 rubric: "essential: ... the only label of an icon-only control")
- What: For a control with no other label, the accessible name is computed from the title, so the equality is always true and M11 PASSes without asking J2. The J2 rubric lists exactly this case as essential. A sighted keyboard user never sees a title (V2: Chrome shows none on focus). Spec and code agree, but the spec contradicts itself.
- Evidence: Ran pages/icontitle.html (`<button title="Delete all records"><svg/></button>`): `4.A PASS ['A3','t1:M11','G4']`, no question.
- Fix: Compare the title to the visible text or the aria-label only, not to a name that was derived from the title; spec wording change (Abby).
- Confidence: confirmed

### E-14 4.C: `aria-modal="true"` markup alone turns "Enter exits" into PASS (M4), against the spec's own sentence that modal never changes the outcome
- Severity: P2
- Kind: false-pass-risk
- Where: traverse.py:269 (`modal` = `<dialog>:modal` or `aria-modal="true"` on any `role=dialog` ancestor, no check that the rest of the page is inert); t4c.py:346 (`modal=any(...)` over `trap_steps`, which for a stuck element are the last 6 steps), :977-981 (M4); spec 4c:128 ("the label never changes the outcome") vs :88 (M4 needs a modal dialog) and :18
- What: M4 PASS and M4d/M4o differ only by `inst.modal`. A page can mark any container `role="dialog" aria-modal="true"` (page markup steering an outcome); a real trap whose Enter on a control moves focus on, but that is not advertised, becomes PASS instead of M4d (NEEDS REVIEW) or M4o/FAIL. For a stuck element, `trap_steps` is the last six steps, so a preceding dialog's stops can mark an unrelated stuck element modal.
- Evidence: Read; not run.
- Fix: Take `modal` only from the members' own container and require `inert`/backdrop behaviour or leave it at M4d; reconcile the two spec sentences.
- Confidence: likely

### E-15 4.C M10: a whole-page cycle is PASS, so a page whose only focusable content is a trap passes once J1 is answered "no"
- Severity: P2
- Kind: false-pass-risk
- Where: t4c.py:1096-1107 (M10); spec 4c:96 and :102
- What: When Tab and Shift+Tab both cycle through every stop (never reaching OUT) and the loop holds at least as many stops as the inventory, the outcome is PASS "not a trap, but unusual". A small login or kiosk page with a focus-trap script on the document is exactly that. This is the spec's decision, but it is a PASS that no key press confirms. In code J1? comes before M10, so the PASS needs only an agent "no" to J1.
- Evidence: Ran pages/wholetrap.html (3 buttons, document-level Tab/Shift+Tab cycle): `4.C NEEDS_REVIEW ['A3','i1:J1?','G3']`, J1 open; M10 would apply after any non-"yes" answer. Not run to PASS (needs an answer).
- Fix: Make M10 NEEDS_REVIEW (or require J1 = no and a person's confirmation) unless the page's pass end shows a real wrap.
- Confidence: likely

### E-16 4.B proof and alternative press have no time check and `_confirmed` ignores an unreliable normal press; unreadable frames are skipped in page text
- Severity: P2
- Kind: gap
- Where: t4b.py:156-201 (`prove`: three replays plus a hold of up to 10.3 s each, no `ctx.out_of_time()`), :214-242 (`alt_press`), :245-257 (`_confirmed`: `n.unreliable` not checked; spec M5 names only the timed effect), traverse.py:1294-1303 (`page_text` skips any frame that throws, then `st.text_read = True`)
- What: Spec section 2 says to call `ctx.out_of_time()` before each replay (base.py docstring step 4); `resume` calls neither. A proof can take about 30 s past the limit. A normal press with only a flaky DOM change counts as "no effect", which helps confirm timing. A frame whose text cannot be read leaves no trace, so M1 can PASS on a partial text.
- Evidence: Read.
- Fix: Check the deadline before each replay in `prove`/`alt_press` and record it; add `n.unreliable` to `_confirmed`; have `page_text` report skipped frames.
- Confidence: likely

### E-17 Spec and code drift (wording, rows)
- Severity: P3
- Kind: gap
- Where: specs 4a:140/146 and 4c:132/154 give "exact wording" of J1/J2; code t4a.py:206-241 and t4c.py:80-105 word them differently (4.A J1 481 characters plus a 553-character rubric; 4.A J2 305+356; 4.B J1 484+354, J2 369+222; 4.C J1 235+385, J2 236+456). 4.C code rows J1? and J2? (t4c.py:1068, 1076) are not in the 4.C table 3a. 4.C spec A4 has no row (covered by A1 by effect). Template says "Question: exact wording"; the spec no longer matches.
- What: The template says the spec decides the question text. Question and rubric text are sent once (deduped by the pipeline), so token cost is moderate, but two sources of wording will drift further.
- Fix: Make the spec quote the code's constants, or generate the spec section from them; add J1?/J2? rows to the 4.C table.
- Confidence: confirmed

### E-18 Duplicated or dead code
- Severity: P3
- Kind: dead-code
- Where: `_label` t4a.py:1123 vs t4c.py:1300 (same function, 4.C without `_TAG_ROLE`); `_norm` t4a.py:337 vs t4c.py:914; `_keys_text` t4a.py:1132 vs `_steps_text` t4c.py:1451; `Collector.out_of_time` t4c.py:242 vs `RunContext.out_of_time` base.py:116 (the root of E-07); t4a.py `_replay` (:421) and `_out_of_time` (:425) are one-line wrappers of ctx methods; `keys_of` (t4a.py:445, `del keys_of` :665) is unused; `stop_hook(pass_name, prior)` ignores `prior` (:288); `APPLICABILITY` A3 rows give `Outcome.PASS` that nothing reads (t4a.py:978, t4b.py:342); t4b.py imports private names of t4a (`_stop_list`, `_replay`, `_label`, `_stops_input`, `_keys_text`, `StopRef`, `HOOK`).
- What: The next check will copy these again; the E-07 bug exists because of the two out_of_time helpers.
- Fix: One `checks/common.py` with label, norm, key text, stop list and the single recording out_of_time.
- Confidence: confirmed

### E-19 Page loads and rounds trips per run (worst case) and fixed waits
- Severity: P2
- Kind: time
- Where: 4.A t4a.py:462 (1 load), 559 (up to 10 replays), `_describe_hidden` (E-10), 586 (up to 5 probes), 606 (up to 10 clicks), 632 (up to 10 X, 1-2 replays each), 645 (1 load for text), plus the walk's. Hover scan :501-523 does, per stop, `mouse.move`, `settle` (at least 2 frames and `quiet_ms`), one `_scan` (a `getComputedStyle` call for every visible element, in every frame), `mouse.move(0,0)`, another `settle`. 4.B t4b.py:102 (1 load) plus at most 3 replays (proof) and 2 (alt). 4.C t4c.py:761 (1 load, only to read `keyboard_unreachable` and page text) plus up to `MAX_INSTANCES` (20) times (1 + 4 + 1 + 10) probes (each a fresh replay) plus 20 P4 replays plus 6 P7 states.
- What: three separate loads for the same page text (4.A titles, 4.B, 4.C); the hover scan costs O(stops x elements) style reads and two settles per stop, where the spec budgets 0.1 s per stop; 4.C's load for `keyboard_unreachable` could come from the walk's inventory. Worst case for 4.C is about 340 replays; for 4.A about 70 loads.
- Evidence: Read; not timed.
- Fix: Share page text through `ctx.cache`; skip the second settle and re-scan unless the first scan found something new; store `keyboard_unreachable` on `PassResult`.
- Confidence: likely

