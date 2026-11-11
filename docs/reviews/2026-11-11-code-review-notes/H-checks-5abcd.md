# H - Checks 5.A, 5.B, 5.C, 5.D (t5a.py, t5b.py, t5c.py, t5d.py) vs their specs

## Overview

- Files: `checks/t5a.py` (330 lines), `t5b.py` (375), `t5c.py` (591), `t5d.py` (1175), read in full with specs 5a/5b/5c/5d, `_template.md`, `base.py`, `engine.py`, `labels.py`, `forms.py`, and the parts of `observe.py`, `reveal.py` and `pipeline.py` they depend on.
- Row order and row conditions match the specs closely (tables below). Every deviation I found is in what the evidence readers feed the rows, not in the row tables themselves.
- Three confirmed false-PASS paths (ran real pages): 5.A passes labels whose text is not visible (H-01); 5.C passes any non-Latin visible text as "announced" (H-02); 5.D passes after a keyboard trap with fields never filled (H-03).
- Two more confirmed wrong-PASS paths: 5.D lets page markup (`aria-controls`) mask a content replacement (H-04); 5.B silently drops fields that could not be read and can PASS without judging them (H-05).
- Check order is fine: `pipeline.py:877` sorts by `-shares`; 4.D/4.F/19.A/9.x = 1-2, 5.D = 0, 5.A/5.B/5.C = -1, so 5.A-5.C collect after 4.F and 5.D (the "cache before revealed reads arrive" worry does not apply to the normal order). The revealed reads of 5.D only cover its last live session (H-07).
- Cost: pass L is one load, but every revealed state (up to 20 triggers plus up to 60 set loads) repeats the full read with screenshots and a 500 ms ANDI sleep; 5.D spends at least about 1.5 s of fixed waits per field plus a wasted screenshot per field (H-13, H-14).
- Totals: P0 3, P1 4, P2 7, P3 3 (17 findings, see list).

Page content below is untrusted data; test pages are in `/tmp/claude-0/-home-user-tobi508/e409d852-9211-5ad4-9dc1-79e7dbd3df61/scratchpad/h/pages/`.

## Findings (most severe first)

### H-01 5.A M2 passes a label whose text people cannot see
- Severity: P0
- Kind: false-pass-risk
- Where: `src/tobi508/labels.py:40` (`txt` uses `innerText`), `labels.py:188-189` (label `shown` = the label box is rendered and in region), `t5a.py:40-46` (`_shown_label`)
- What: M2 ("a visible label with text") is true when the label element has a rendered box inside the image region and any non-empty `innerText`. `innerText` includes text hidden by the usual visually-hidden clip pattern and by `text-indent`, and for a wrapping label it includes the text of a `<select>`'s options. So a label whose only visible part is a "*" (the words are in an `sr-only` span), a `<label>` that wraps a `<select>` and holds no words, and a label pushed off with `text-indent:-9999px` all give 5.A PASS (M2) with no question to the agent. The spec says a visible label is text that is "rendered and readable while the field has focus", not clipped to 1 px.
- Evidence: ran `a1.html` with 5.A,5.C: `5.A PASS ['A4','c1:M2','c2:M2','c3:M2',...,'G4']`. c1 = `<label for=e><span class=sr>Email address</span><span aria-hidden>*</span></label>`; c2 = `<label><select>...options...</select></label>`; c3 = label with `text-indent:-9999px`. All three have no text a sighted user can read. (The same run showed 5.C correctly sends c1 to J1 and fails c2.)
- Fix: measure the text, not the box: take the label's text from its text nodes that pass `shown()` (as `near` does at `labels.py:212-225`), skip `select`/`option`/`textarea` descendants, and treat a label whose visible text nodes are empty as not shown (NEEDS REVIEW via J1).
- Confidence: confirmed

### H-02 5.C `words()` keeps only ASCII letters and digits, so non-Latin text is "covered"
- Severity: P0
- Kind: false-pass-risk
- Where: `src/tobi508/checks/t5c.py:34-35` (`words`), used at `t5c.py:153-163` (`covered`, M5), `t5c.py:107-110` (`heading_announced`, M3s), `t5c.py:353` (`_only_set_label`); also `t5a.py:55` (`_blank_option`, M2o), `t5a.py:70-71`
- What: `words(t)` = `re.findall(r"[0-9a-z]+|\*", t.lower())`. Cyrillic, Greek, Arabic, Hebrew, Chinese, Japanese, Korean (and the accented part of Latin words) produce no words. M5 is `seen <= prog`; with `seen` empty it is vacuously true, so 5.C PASSes a field whose visible label or instruction is entirely in another script whatever ANDI announces (even "f1"). The same blind spot makes M3s never fire for a non-Latin heading and makes 5.A M2o (`not any(words(t) for t in c.nearby_own)`) FAIL an option that has non-Latin text right beside it (false FAIL, likely, not run).
- Evidence: ran `a1.html`: field `<label for=r>Имя пользователя</label><input aria-label="f1">` and `<label for=j>必須の住所を入力してください</label><input aria-label="x1">` gave `c4:M5`, `c5:M5` and page `5.C` rows included only M5 for them (the page FAILed on other fields; these two were passed, not asked). The same field with an English label goes to J1.
- Fix: tokenise with `\w` on a Unicode-normalised string (`re.findall(r"\w+|\*", t.casefold(), re.UNICODE)`); and make M5 not pass when visible text is non-empty but yields no words.
- Confidence: confirmed (5.C); likely (5.A M2o, M3s)

### H-03 5.D PASSes after a keyboard trap; fields past the trap are never filled
- Severity: P0
- Kind: false-pass-risk
- Where: `src/tobi508/checks/t5d.py:1086` (`if st.p1["end"] not in ("wrap", "stuck", "loop")`), `t5d.py:1090-1094` (`missing` only counts fields P1 reached), spec 5d section 3b G3
- What: the spec's G3 says NEEDS REVIEW when "P1 is incomplete ... or ended in a trap before the last field". The code lists `stuck` and `loop` (the trap endings, `walk.py:30 TRAP_ENDS`) as complete walks. Fields after the trap are not in `st.fields`, so `missing` is empty and nothing compares the DOM inventory count (`st.inventory_fields`) with the fields filled. A page with a field, a trap, then a second field whose blur navigates away gives PASS "We filled in each of the 1 form fields".
- Evidence: ran `d2.html` (field "First", link whose keydown handler blocks Tab, field "Second" with `onblur` navigation) with 5.D,4.C: `5.D PASS ['A3','G4'] ... filled in each of the 1 form fields ...` while `4.C` says focus got stuck. (A trap on a field itself gives M6/J1 instead: `d1.html`.)
- Fix: treat `stuck` and `loop` like any other incomplete end (add the message, G3), and add "inventory_fields > fields completed" as an incomplete reason ("N form field(s) the keyboard walk did not reach").
- Confidence: confirmed

### H-04 5.D "own widget" lets the page's own `aria-controls` hide a content replacement
- Severity: P1
- Kind: false-pass-risk (page content steers an outcome, CLAUDE.md principle 5)
- Where: `src/tobi508/forms.py:20-39` (`_OWN_JS`: `aria-controls`, `aria-owns`, `list`, `aria-describedby`, `aria-errormessage`), `forms.py:107-123` (`SIG_FN` skips everything in `own`), spec 5d Terms
- What: any element the field names in `aria-controls` is excluded from the "did the page change" signature, wherever it is and however large. A select with `aria-controls="main"` that replaces the whole main content ("Apply" becomes "Payment ... Pay now") reads as "no effect": M14 PASS with no J2. The spec defines own widget this way, but the page chooses which region is exempt, which is the page deciding an outcome.
- Evidence: ran `e2.html`: `5.D PASS ['A3','G4']` for a select that replaced `<div id=main>` content, with `aria-controls=main`. The same page without the attribute reaches J2 (e1 variant reached J1 because the select was destroyed). 
- Fix: cap what an `aria-controls`/`aria-owns` target can exempt (for example only when its text is a small share of the page, or never exempt a landmark or `main`), or still run the signature on it and send a large change to J2.
- Confidence: confirmed (spec-conform, so a spec decision for Abby)

### H-05 5.B drops fields that were not read, so it can PASS or say DOES NOT APPLY without judging them
- Severity: P1
- Kind: false-pass-risk
- Where: `src/tobi508/checks/t5b.py:74-118` (`items_of`: `no_label += 1; continue` for a field with no label and no near text), `t5b.py:289-306` (A2 uses only `lp.incomplete`), `labels.py:402-407` (a failed per-field read is `continue`d, not recorded as incomplete)
- What: spec A2 says DOES NOT APPLY only when "pass L read every field". When a field's focus read returns nothing or the field is gone/hidden when its turn comes, `c.focused`/`c.image` stay None and its label and nearby text are empty. 5.A turns that into M1 and 5.C into M1 (NEEDS REVIEW), but 5.B counts it as "no visual label" and leaves it out: the field is never judged and `lp.incomplete` is empty, so 5.B can PASS on the other fields or give DNA.
- Evidence: ran `f1.html` (field two is hidden by field one's `onfocus`): `5.A NEEDS_REVIEW [c1:M2, c2:M1]` but `5.B` had only `f1.1:J1?`, one item, the second field absent; an `all_descriptive` answer would PASS. 
- Fix: in `items_of`, treat a field with `focused is not True` (or `image is None`) as unread: add it to an `unread` list that sets NEEDS REVIEW (and blocks A2), as 5.A does.
- Confidence: confirmed

### H-06 5.D reads "the DOM changed outside the field's own widget" as "visible text or dialog count changed"
- Severity: P1
- Kind: false-pass-risk
- Where: `src/tobi508/forms.py:107-123` (`SIG_FN`: text and dialog count only), `t5d.py:352-354, 411-413` (`outside_changed` only if both signatures are non-None), `t5d.py:487-504` (`change_of`: the `dom` effect kind and `mutations` are ignored), spec M7
- What: spec M7 is "a dialog appeared or the DOM changed outside the field's own widget". The code asks J2 only when visible text outside the widget differs or the visible dialog count differs. A change made only of pictures, canvas, `iframe` content, ARIA state or layout reads as "no effect" (M14 PASS). If either `reader.call(SIG_FN)` returns None (frame detached, error), the comparison is skipped and the result is silently "no change" (missing evidence leading to PASS). A field inside an iframe only sees its own frame's document.
- Evidence: read (`change_of` never looks at `Effect.mutations`/`dom`; `Effect.kinds` includes `dom` at `observe.py:318-319` but is not consumed by 5.D except `_unreliable`). Not run.
- Fix: also count a large number of mutations outside the own widget, or visible image/iframe changes, as `content`; make a None signature an M1 (unreliable) instead of no change.
- Confidence: likely

### H-07 Fields found in opened states lose their "incomplete" notes, and 5.D reads only its last live session
- Severity: P1
- Kind: gap
- Where: `src/tobi508/labels.py:508-525` (merge appends `extra.components` only; `extra.incomplete`, `extra.notes`, `extra.andi_ran` are dropped), `labels.py:389-393` (cap per state), `labels.py:461-478` (`read_revealed`), `t5d.py:636-645` (read only on the final `s`), `t5d.py:570-573` (sessions closed on a context change are not read)
- What: each opened state is read with `read_session`, which has its own 60-component cap, run-time break, frame count and ANDI failure note. Those messages go into a `LabelsPass` that `labels_pass` discards, so a revealed state with 80 fields, an out-of-time read or fields in a frame is silently partial; 5.B sees unread fields as "no label" (H-05). Components from such a state with `andi` None only give 5.C M2, but 5.A/5.B get no signal. 5.D calls `read_revealed` only on the last open session; fields revealed on a replay that was closed because of a change of context are never read.
- Evidence: read.
- Fix: merge `extra.incomplete` (prefixed with how the state was reached) into `lp.incomplete`, and `extra.notes` into `lp.notes`.
- Confidence: confirmed (read)

### H-08 DOES NOT APPLY when the only forms are hidden or are `contenteditable`; the reveal guard cannot help
- Severity: P2
- Kind: gap
- Where: `labels.py:28, 53-59` (`SEL` has no `[contenteditable]`; `vis(el)` drops anything not rendered), `engine.py:115-134` (guard RV only turns a PASS into NEEDS REVIEW), spec 5a A1, 5b A1, 5c A1, 5d A1
- What: a form in `display:none` that a plain link or `div` opens (nothing the walk marks as a collapsed control) is invisible to the inventory, and `contenteditable` regions are not fields (spec 5d section 5 says so on purpose). Then 5.A, 5.B, 5.C, 5.D all say "This page has no form fields, so this test does not apply" with no note that something was hidden. Guards leave DNA unchanged by design.
- Evidence: ran `b2.html`: all four tests `DNA ['A1','G1']` (hidden form behind a link plus a `contenteditable` box).
- Fix: when `reveal` found triggers that did not open (or the page has `[contenteditable]`), turn DNA into NEEDS REVIEW with the reason (a new line in the A1 rows, needs Abby's approval as it changes DNA).
- Confidence: confirmed

### H-09 5.D J2's covering guard (M15) is silently off when a screenshot fails
- Severity: P2
- Kind: false-pass-risk
- Where: `t5d.py:267-274` (`_shot` returns None on any exception), `t5d.py:416-428` (`changed` is None unless both shots exist), `t5d.py:444-450` (`covering`), `observe.py:118-134`
- What: if either screenshot fails or sizes differ, `changed_share` is None, only the DOM layer share is used, and J2 `content_only` then gives M11 PASS even for a whole-window replacement that opened no dialog. J2 is also asked with `image_a_before`/`image_b_after` None, and nothing forces `unsure` in that case.
- Evidence: read; spec M15 says the larger of pixel share and layer share.
- Fix: when `a.shot_before` or `a.shot_after` is missing for a content change, route M11 to NEEDS REVIEW (like M15), and do not ask J2 without both images.
- Confidence: likely

### H-10 5.D J3 value is typed raw: a newline submits the form
- Severity: P2
- Kind: security
- Where: `t5d.py:283-311` (`keyboard.type(a.value)`), `t5d.py:652-669` (`inst.j3["value"]` used unchanged), `models.py:375-376` (only `max_length=200`)
- What: J3's value comes from an agent that read page text (untrusted). Playwright's `keyboard.type` presses Enter for `\n`. A value with a newline submits a one-text-field form, which 5.D then records as "sent the form" (M4) and can FAIL; a page can steer that by what its labels say. No control-character filter, and the value is not cut to `maxlength` by the check (the browser does).
- Evidence: ran a snippet: `keyboard.type("x\ny")` into a single-input form fires its `submit` handler. `\t` is typed as text, not a Tab.
- Fix: strip control characters from J3 values (reject any with `\n`, `\r`, `\t`) before use; record the cleaned value.
- Confidence: confirmed (mechanism); the page-steering path is likely

### H-11 5.D change-of-context details that differ from the spec
- Severity: P2
- Kind: bug
- Where: `observe.py:302` (`after["url"] != before["url"]`, includes the fragment) vs `traverse.py:978-980` (fragment ignored) and spec 5d Terms ("the top URL changes (ignoring the fragment)"); `t5d.py:374-399` (the 1,000 ms second read looks at focus only); `t5d.py:507-512` (M1 "unsettled step" not read)
- What: (1) a field that only changes `location.hash` is reported as `navigation`, J1 asks, and an agent answering not_told gives a false FAIL (spec says ignore). (2) After leaving a field the second read re-reads focus only; a handler that navigates or opens a window 1.2 s after blur is not seen as that field's effect. (3) Spec M1's "a step was unsettled or unresolved" has no code: `_unreliable` is true only for a content change with noise, so an unsettled, noisy step with no other effect still reaches M14 PASS.
- Evidence: read (1) `observe()` compares full `page.url`; (2) (3) read, not run.
- Fix: strip the fragment in `observe`; recheck URL, pages and submissions after the second settle; record `unsettled` on `Effect` and use it in M1.
- Confidence: confirmed (1); likely (2), (3)

### H-12 Silent caps and truncations that can turn a missing cue into a PASS
- Severity: P2
- Kind: gap
- Where: `labels.py:24, 411-417` (`nearby` cut at 400 characters), `labels.py:266-268` (`nearby_other` 6, `nearby_buttons` 6, `nearby_css` 6), `labels.py:234-236` (stops after 3000 elements, silently), `t5b.py:15` (`NEAR_MAX = 3`), `t5b.py:112-117` (label 200 chars, near 200)
- What: 5.C M5 compares only the kept `nearby` text with what is announced, so a "*" or format hint past the first ~400 characters (nearest first) is never compared; 5.A M3 uses `not c.nearby` and the cut text. None of these caps is reported in a finding. The 60-component cap is reported (`incomplete`), but it counts buttons together with fields (already known).
- Evidence: read.
- Fix: record a note ("text near N fields was cut") when any cap bites, or raise the character cap for the M5 comparison only.
- Confidence: likely

### H-13 Pass L cost: per-field full-document scans, per-state full re-reads
- Severity: P2
- Kind: time
- Where: `labels.py:160-277` (`FOCUS_JS` per field: a tree walk over all text nodes, `others` list rebuilt, `querySelectorAll('*')` up to 3000 with two `getComputedStyle(p, pseudo)` each, nested `els` loops), `labels.py:445` (`wait_for_timeout(500)` per read), `labels.py:423-432` (one screenshot per field), `reveal.py:39-41, 414, 452` (20 triggers + 3 sets each)
- What: one run for 5.A-5.C is one load for the page as loaded, but each opened trigger (up to 20) and each chosen set (up to 3 per trigger) is a fresh load with a full `read_session`: inventory, one focus call and one screenshot per entry field, ANDI injection and a fixed 500 ms. Worst case 20 + 60 = 80 extra loads, each with up to 60 fields. Per field, `FOCUS_JS` is O(page size x fields); the CSS-pseudo scan (needed only by 5.C) runs even when only 5.A is selected.
- Evidence: read (counts from `reveal.py` constants). No timing run.
- Fix: run the pseudo-element scan only when 5.C is selected; poll for ANDI's rows instead of sleeping 500 ms; skip screenshots in revealed states unless a question needs them.
- Confidence: likely

### H-14 5.D fixed waits and wasted work per field
- Severity: P2
- Kind: time
- Where: `observe.py:139, 289` (300 ms noise window per action), `t5d.py:374` (`settle(page, 1000, 2500)` after every leave), `t5d.py:301-302, 416-418` (a before screenshot and two dialog scans per field), `t5d.py:515-535` (`_session_for` refills all earlier fields)
- What: per field at least a 300 ms noise window, the settle quiet windows around each action (about four per field), and a 1,000 ms re-read after every Tab that did not already navigate; a radio group does this for each of up to 9 presses. A "before" PNG is written for every field even though only a content change uses it. After a change of context (or J3), the replay re-fills every earlier field: O(n^2) fields refilled in the worst case (40 fields with a change of context each: about 40 replays plus several hundred refills).
- Evidence: read; the spec quotes about 1.1 s per field.
- Fix: take the before picture lazily (only when `outside_changed` is seen, from a retry) or as a cheap clip; skip the 1,000 ms re-read when the page has no event handlers on blur (cannot know) or run it once per group of fields.
- Confidence: likely

### H-15 Disabled elements are not excluded when disabled by a `fieldset`
- Severity: P3
- Kind: bug
- Where: `labels.py:57` (`el.disabled` is only the element's own attribute; an input in `<fieldset disabled>` has `el.disabled === false`)
- What: TT excludes disabled elements. A field in a disabled fieldset is counted: 5.A and 5.C give NEEDS REVIEW (the focus fails), 5.B DNA (A2) and 5.D DNA, an inconsistent answer for one page. Safe direction (no PASS or FAIL), only noise.
- Evidence: ran `c1.html`: `5.A NR [c1:M1]`, `5.B DNA [A2]`, `5.C NR [c1:M1]`, `5.D DNA [A1]`.
- Fix: use `el.matches(':disabled')`.
- Confidence: confirmed

### H-16 Copied code, and a dependency that points the wrong way
- Severity: P3
- Kind: design
- Where: `_finding` copies in `t2a.py:250, t2b.py:280, t2c.py:403, t2d.py:147, t3a.py:771, t5a.py:216, t5b.py:246, t5c.py:481, t5h.py:286, t9a.py:625, t9b.py:154, t9c.py:409, t19a.py:323` (13); the literal "This test could not be performed" appears 27 times in `src/` although `models.TEST_NOT_PERFORMED_NOTE` exists; `t5a.evaluate` (235-297) and `t5c.evaluate` (500-556) are the same skeleton (trace, G2/G3/G4, ordered sentences, notes); `t5c.norm` (38) = `t5d._norm` (862); `t5b` imports `in_set` from `t5a` and `rel_images` from `t5c`, and `t5a` imports `how_to_reach`, `label_of`, `quote_in`, `words` from `t5c`; each of `State5A/5B/5C` embeds the whole `LabelsPass` and each is written to its own evidence file (three copies of every component).
- What: the next label-like test would copy these again; a change to the note wording or the page-outcome skeleton needs 13 edits.
- Fix: one `checks/common.py` with `finding()`, `page_outcome()` and the text helpers; keep `LabelsPass` in `ctx.cache` and let each state hold only its answers.
- Confidence: confirmed

### H-17 Text sent to the calling agent (sizes)
- Severity: P3
- Kind: tokens
- Where: `t5a.py:120-150`, `t5b.py:149-170`, `t5c.py:282-335`, `t5d.py:100-163`
- What: characters: 5.A question 370, rubric 1,278; 5.B 457 and 546; 5.C question 580 (set 567, buttons 591), rubric 972; 5.D J1 324 and 436 (group), rubric 526; J2 594 and 584; J3 232 and 210. `question_texts` dedupes these across questions (`pipeline.py:628`). Per question the `input` is not deduped: 5.A one question and one image per entry field (up to 60), each with `text` up to about 400 characters plus `labels_of_neighbouring_fields` (6) and `buttons_next_to_it` (6); 5.C `visible` carries nearby text and CSS text for every field. The 5.A rubric repeats the spec's rubric nearly word for word and so do the 5.C and 5.D rubrics; the J1 "labeled" quote sources are listed in both the question and the rubric (5.A) and the "unsure" instruction twice (rubric end and question).
- Evidence: measured with `len()` on the constants.
- Fix: ask one 5.A question per form like 5.B does when fields share the same unlabeled pattern; drop sentences repeated between question and rubric.
- Confidence: confirmed (sizes)

