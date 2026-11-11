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

