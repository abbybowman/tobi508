# M: code review of checks 5.F, 5.G, 5.H, 9.A

## Overview

- Files: t5f.py, t5g.py, t5h.py, t9a.py against specs 5f 1.5.0, 5g 1.3.0, 5h 1.2.0, 9a 1.1.0. Code follows the spec rows closely: every row has code, the order matches, and no outcome is decided outside the spec (tables at the end).
- The danger is in the spec's own definitions: "no error seen" and "no form found" become DOES NOT APPLY, and the reads behind them have blind spots. I proved each with a small page and the real pipeline.
- 22 findings: 7 P0, 6 P1, 6 P2, 3 P3. 12 are confirmed by running a page.
- Worst (false DNA, found by running): a form whose button is `type=button` (M-01); a form that is only a button or is hidden behind a button (M-02, M-07); error text in a shadow root, a red wrapper, or a message gone in 60 ms (M-06); a Spanish payment page in 5.H (M-03).
- Worst (false PASS, found by running): a keyboard trap before the second form lets 5.F PASS (M-05); a wizard's next step with the word "required" passes 5.H (M-08); a no-op button passes 9.A when the URL has a `#fragment` (M-10).
- 9.A also accepts the tested page as its own "other page" under another spelling (M-11), and misses a header in a shadow root (M-12).
- 5.G does not narrow J1's text to the field as its spec says (M-13). Questions are asked per field and per attempt with repeated text (M-19).
- Time: no waste beyond the spec's budget (M-22); pass E is cached across 5.F, 5.G, 5.H.
- Existing fixtures (tests/fixtures/5f, 5h, 9x) cover none of the branches above.

## Findings (written as found)

### M-01 Form whose only button is `type=button` (JS validation) is never pressed: false DOES NOT APPLY in 5.F and 5.G
- Severity: P0
- Kind: false-pass-risk (wrong DNA)
- Where: src/tobi508/checks/t5f.py:160-161 (`isSubmit`), :173 (`Array.from(form.elements).filter(isSubmit)`), :641 (`btns` kept only if P1 stop), :946-951 (`j0_needed`); spec specs/rules/5f-error-identification.md "Submit control" (same rule)
- What: Inside a `<form>`, only `button` with no type or `type=submit` and `input type=submit|image` count as submit controls. A `<button type="button" onclick="validate()">Submit</button>` (very common for JS-only validation) is not offered. With two or more text fields and no submit button, "Enter in the last field" does not submit (browsers only do implicit submission with one blocking field or a submit button), so nothing happens, no error shows, and the test reports DNA "the page did not check for errors". J0 (the agent asks which control sends the form) never fires because `form.buttons` is empty, so the agent can not rescue it.
- Evidence: ran a page with two text fields and `<button type=button onclick=v()>` that writes "Email: enter a valid email address" into a `role=alert` div: `5.F DNA ['A5','A3','G1']`, `5.G DNA ['A5','A1','G1']`, no open question (run via runpage.py, page mf_btn.html). Code and spec agree, so this is a spec gap; the outcome is still wrong on a real page.
- Fix: Offer every visible button inside the form (not only submit types) as a candidate; keep the "submit words" order, and ask J0 when the first press shows nothing. Never reach DNA for a form whose Enter press could not have submitted it (no submit button and more than one field): NEEDS_REVIEW.
- Confidence: confirmed

### M-02 5.H: a form with no fields (for example "Delete my account") is invisible: false DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk (wrong DNA)
- Where: src/tobi508/checks/t5h.py:311-325 (`not st.forms` -> A1 DNA); forms only come from P1 field stops (src/tobi508/forms.py:141-177 `_fields`, t5f.py:694,702,589-664)
- What: Pass E builds forms from form FIELDS the walk reached. A form that is only a button (`<form method=post action=/delete-account><button>Delete my account</button></form>`, a "Confirm purchase" or "Submit exam" button with hidden inputs) has no fields, so pass E has no form, and 5.H says "This page has no form to submit" (A1). That is exactly the kind of form 5.H exists for (delete, financial, test submission). Spec A1 reads "Pass E found no form with a submit control", which this page does have.
- Evidence: ran mh_delete.html (h1 "Your account", form with one button "Delete my account"): `5.H DNA ['A1','G1']` "This page has no form to submit"; 5.F also `DNA A1`.
- Fix: 5.H needs its own form list: every `form` element (and button groups outside a form) with a submit control, whatever its fields; hint-check and J1 on those. At least NEEDS_REVIEW when the DOM has a visible `form` that pass E did not take.
- Confidence: confirmed

### M-03 5.H: consequence hint is English only: a Spanish checkout is DOES NOT APPLY
- Severity: P1
- Kind: false-pass-risk (wrong DNA)
- Where: src/tobi508/checks/t5h.py:29-35 (`HINT`), :118-127; spec specs/rules/5h-error-prevention.md Terms and A3
- What: A3 is decided by a regex of English words (pay, purchase, order, ...). A page in another language never matches, so a real payment form gets DNA with no question to the agent. The spec's own list is English, so spec and code agree.
- Evidence: ran mh_es.html (`lang=es`, "Finalizar compra", "Numero de tarjeta", button "Pagar ahora"): `5.H DNA ['A3','G1']` "No form on this page looks like it makes a payment...".
- Fix: do not use a word list to reach DNA. Ask J1 for every form (cheap when pages are small), or at least reach NEEDS_REVIEW when the page language is not English. Keep the list only to order questions.
- Confidence: confirmed

### M-04 5.F/5.G keep the form field in A2 but 5.H says DNA when the walk reaches no field (tabindex=-1 field)
- Severity: P1
- Kind: false-pass-risk (wrong DNA)
- Where: src/tobi508/checks/t5h.py:311-325 versus src/tobi508/checks/t5f.py:1125-1126 (`applicability`: `field_stops == 0 and inventory_fields > 0` -> A2)
- What: 5.F turns "the DOM has form fields but no stop is a field" into NEEDS_REVIEW (A2). 5.H calls `incomplete_of(ps)`, which does not contain that condition, so with `forms == []` and an empty incomplete list it says DNA. Same test data, two different answers.
- Evidence: ran mf_tabindex.html (a card field with `tabindex=-1`, button "Pay now"): `5.F NEEDS_REVIEW ['A2','G1']`, `5.H DNA ['A1','G1']`.
- Fix: put the A2 condition (field_stops == 0 and inventory_fields > 0) into `incomplete_of` or into PassE, so every reader of pass E gets it.
- Confidence: confirmed

### M-05 5.F: a keyboard trap before a form hides the form after it; the page still PASSes
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t5f.py:1233 (`ps.p1["end"] not in ("wrap", "stuck", "loop")`); fields come from P1 stops only (src/tobi508/forms.py:141-177); spec 5.F G3 ("P1 incomplete before the last field")
- What: `incomplete_of` treats a walk that ended in `stuck` or `loop` (a keyboard trap) as a complete walk. Fields after the trap are not in `ps.fields`, so they are never tried, and the page can PASS (G4: at least one instance, all PASS) or reach DNA although a later form is broken. The DOM inventory count (`inventory_fields`) is read but never compared with the number of fields the walk reached.
- Evidence: ran two pages that differ only by one trap widget (`tabindex=0` div that cancels Tab) between form 1 (native `required`) and form 2 (page sets `aria-invalid=true` and no text on submit): without the trap `5.F FAIL ['A5','a1-f1:M2','a3-f3:M3','a4-f3:M3','G2']`; with the trap `5.F PASS ['A5','a1-f1:M2','G4']` (pages mf_notrap2.html and mf_trap2.html). 4.C asked a question about the trap, but 5.F said PASS with no note.
- Fix: in `incomplete_of`, add a note (so G3 NEEDS_REVIEW) when the walk ended in `stuck`/`loop` and `inventory_fields` is greater than the number of distinct fields in `ps.fields` (or simply whenever `end` is `stuck`/`loop`).
- Confidence: confirmed

### M-06 5.F/5.G: "no error seen" becomes DOES NOT APPLY, but the read has blind spots (error text in a shadow root, error shown on a wrapper element, error that disappears in under about 200 ms)
- Severity: P0
- Kind: false-pass-risk (wrong DNA)
- Where: src/tobi508/checks/t5f.py:93-115 (TreeWalker over light DOM only), :124-136 (look read from the field element only), :437-450 (settle plus a fixed 150 ms, then one read), :1376-1382 (A3 DNA when no instance); same in t5g.py:293-299
- What: A3 (and 5.G's "A1") says "the page did not check for errors" whenever the reads found no new text, `aria-invalid`, native message, or change of the field's own look. Pages that DO check, but where the read cannot see it, get DNA with a sentence that says the page did not check. Three seen: (1) the error text lives in a shadow root (web component error summary): TreeWalker does not enter shadow roots; (2) the error is a red border/background on a wrapper div around the input (Material-style) with the input itself unstyled: only the input's computed style is read; (3) a toast/message removed within about 60-150 ms (one read, after settle plus 150 ms; the first-Tab reads are only in attempt 2).
- Evidence: ran three pages (mf_shadowerr.html: `<div role=alert>Error.</div>` inside a shadow root; mf_wrapper.html: wrapper class `bad` with red border; mf_toast.html: text removed after 60 ms): each gave `5.F DNA ['A5','A3','G1']`, no open question. The spec's definition of "error indicator" is the same as the code, so spec and code agree; it is a spec gap.
- Fix: When an attempt shows ANY DOM mutation or style change that was not read as an indicator (a MutationObserver counting added/removed nodes and attribute changes, shadow roots included, that fired during the press), do not call it DNA: NEEDS_REVIEW. Also walk open shadow roots in the text read and read the look of the field's nearest bordered ancestor.
- Confidence: confirmed

### M-07 5.F, 5.G and 5.H have no `reveal` guard: a form behind a plain button is DOES NOT APPLY
- Severity: P0
- Kind: false-pass-risk (wrong DNA)
- Where: front matter of specs/rules/5f-error-identification.md:5, 5g-error-suggestion.md:5, 5h-error-prevention.md:5 (`guards: unrecorded-code` only; 4.A, 4.D, 4.E, 5.D also list `reveal`); t5f.py:1125 (A1), t5h.py:320-325
- What: A form in a closed `<details>`, a tab panel, a dialog or a `hidden` div opened by a button has no visible fields, so no walk stop is a field and the DOM inventory counts none. 5.F says A1 DNA ("no form fields"), 5.G the same, 5.H "no form to submit". The reveal guard (RV) is not declared by these three specs, and RV only moves PASS to NEEDS_REVIEW anyway, never DNA.
- Evidence: ran mf_hidden.html (a "Pay your bill" button that un-hides a payment form whose submit writes "Error." into an `output`): `5.F DNA ['A1','G1']`, `5.G DNA ['A1','G1']`, `5.H DNA ['A1','G1']`.
- Fix: When the reveal pass found something it could open (`report.reveal` has triggers) and A1 would apply, give NEEDS_REVIEW ("the page has menus or sections that open"); better, make pass E use the opened state. Add `reveal` to the three specs' guards for the PASS side.
- Confidence: confirmed

### M-08 5.H: "checked" is decided by English words in any new text, so a wizard's next step passes
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t5h.py:36-39 (`ERROR`), :105-116 (`stayed` and `checked`), :148 (M1 PASS before J2); spec Terms "Checked" ("a next step's 'required' text is not a check", 1.1.0)
- What: `stayed` is true when the form was not sent and each field element can still be found by `querySelector` (hidden step-1 fields are still in the DOM). Any new text matching `error|invalid|required|must|incorrect|missing|please enter...` then sets `checked`, and M1 gives PASS without asking J2. A client-side wizard whose step 2 simply contains "Card number is required to pay." (or "You must agree to the terms", or a cookie notice that says "must") passes 3.3.4 although no review or reversal exists. Also `a.invalid > 0` counts cancelled invalid events as a check.
- Evidence: ran mh_wizard.html (Step 1 of 2 with Next; Next un-hides "Step 2 of 2: payment ... Card number is required to pay."): evidence 5h.json shows `"checked": true`; with J1 = multi_step, `evaluate()` returned `PASS ['A6','f1:M1','G4']` "The form checks what was entered and lets people fix mistakes before it is sent." (called `evaluate` on the saved state).
- Fix: Require that the field the error is about was empty/wrong, that the visible fields are the same as before the press (visibility, not existence), and that the text is tied to a field (description, live region or field-level `aria-invalid`); otherwise leave it to J2.
- Confidence: confirmed

### M-09 5.H: untested forms (frames, over FORM_MAX, cut walk, time limit) are ignored once any hint exists, so J1 on the rest gives DOES NOT APPLY or PASS
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/checks/t5h.py:70 (`incomplete=incomplete_of(ps)`), :326-335 (incomplete is read only when no form is hinted), :343-379; spec A2/A3 and edge "Several hinted forms ... the others are not tested"
- What: Pass E's incomplete list (a payment form inside an iframe, forms 6 and up, fields past a trap, run limit) only matters when NO form is hinted. The hint comes from the page's whole text (`all_text`), which on most pages holds "terms", "order", "change" or "apply" somewhere (footer), so forms are hinted; J1 then sees only the forms that WERE tested (newsletter, search) and says not_consequential: DNA A4, or a single tested form passes. The consequential form that was never tested is not mentioned.
- Evidence: read, and called `evaluate()` on `State5H(incomplete=["1 form field(s) are inside frames, which this test does not check yet."], forms=[Form5H(hint=True)], j1={'choice':'not_consequential','element':1})`: `DNA ['A4','G1']` with no mention of the frame.
- Fix: any non-empty `incomplete` should turn DNA (A3, A4) and PASS into NEEDS_REVIEW, and J1 should be told which forms were not tested.
- Confidence: confirmed (logic); the "hint in footer" premise is likely, not run

### M-10 9.A: a no-op button before the main content passes when the tested URL carries a `#fragment`
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t9a.py:62-67 (`LANDING_JS`: if focus did not move, landing = `document.querySelector(':target')`), :395 (M7); spec section 2 "the element the URL fragment targets (`:target`)"
- What: The landing is "the element the URL fragment targets" whenever focus stays on the candidate. That element exists from the first load if the tested URL already has a fragment (`page#main`, `page#content`), whether or not the candidate did anything. Any button (menu toggle, language switch, cookie "OK", "noop") before the main content then "lands" on the fragment target at or before M: M7 "works", covers its jump, and the page PASSes with the sentence that the button "lets keyboard users skip it". The tool does not compare the target before and after the press.
- Evidence: ran n_d1.html (a `button` that does nothing, then header/nav, then `<main id=main>`) against another page: with URL `n_d1.html#main` `9.A PASS ['A5','c1:M7','G2']` ("the "noop" button lets keyboard users skip it"); with `n_d1.html` `9.A FAIL ['A5','c1:M5','G5']`.
- Fix: record `:target` (and `location.hash`) right before the press and count a target as the landing only if it changed by the press; or load the page with the fragment removed.
- Confidence: confirmed

### M-11 9.A: the tested page given again as the "other page" under another spelling is not refused
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/pipeline.py:320 (`u.split("#")[0] == url.split("#")[0]`, string comparison before redirects); t9a.py collect (no check)
- What: `?x=1`, a trailing slash, `index.html`, other case or scheme all slip through. 9.A then compares the page with itself, so every unit is "repeated". With a `<main>` landmark the block is everything before main, and the test behaves as if a real site had been compared (a PASS or FAIL about the page's own header). Without a `main` landmark M is never found (all units repeated, no unique unit) and the result is DNA A4 "only content after the main content is repeated".
- Evidence: ran n_a1nomain.html with other page `n_a1nomain.html?x=1`: `9.A DNA ['A4','G1']`; ran n_a1.html with `n_a1.html?x=1`: `9.A FAIL ['A5','G5']`, no warning in either.
- Fix: refuse (or at least note, and give NEEDS_REVIEW) when an other page's final URL after redirects equals the tested page's final URL ignoring query, fragment and trailing slash, or when its units equal the tested page's.
- Confidence: confirmed

### M-12 9.A: a header and menu inside a shadow root is invisible: DOES NOT APPLY when the page has no other landmark
- Severity: P1
- Kind: false-pass-risk (wrong DNA)
- Where: src/tobi508/site.py:124-162 (`walk` follows `el.children`, never `shadowRoot`), t9a.py:662-668 (A3)
- What: Units and regions are read from the light DOM only. A site whose header, menu and footer are web components yields no repeated unit, so 9.A says A3 "Nothing on this page appears on the other pages". The kinship guard (A3o) only rescues the case where the tested page has some navigation of its own (a footer landmark was enough to make it NEEDS_REVIEW in my run).
- Evidence: ran n_s1.html/n_s2.html (shadow header + light footer): `9.A NEEDS_REVIEW ['A3o','G1']`; n_s3.html/n_s4.html (same without the footer): `9.A DNA ['A3','G1']`. Frames: a frame is only a `frame` unit and its content is not read (spec: NEEDS_REVIEW only when a frame sits in B, and a frame is in B only if it matches by text or region).
- Fix: read open shadow roots in `units()` (as the focus walk does), and when the page has custom elements or frames that were not entered, treat "nothing repeated" as NEEDS_REVIEW.
- Confidence: confirmed

### M-13 5.G: J1 is given all new text of the attempt, not the text tied to the field (spec says 5.F's J1 quotes); quote check is satisfied by any text
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/checks/t5g.py:152-156 (`errors = ... t5f.error_inputs(ps, a)`), :71-78 (`_quote_ok` looks in all errors plus the instructions); spec 5g section 4 Input ("the error text tied to the field by 5.F (its J1 quotes, or all new text when 5.F's J1 is not answered yet)")
- What: Code always sends every new text of the attempt. For a form with a summary of several errors, field B (whose error says only "Invalid") sees field A's text "Phone must be 10 digits"; a `guides` answer with that quote passes N4 for field B because the quote is "found in the error text". The same happens for page-level text unrelated to the field. The spec's narrowing by 5.F's answers (reading `5.F-<id>-J1` quote) is not implemented.
- Evidence: read (t5g.py:140-196 never reads 5.F's J1 answers; `st.j` holds only 5.G ids; `resume` copies only J0 from 5.F). Not run (needs agent answers).
- Fix: when 5.F's J1 for the same instance has a quote, send only the entry that contains it; else fall back to all text and mark it "not tied to this field", and require the 5.G quote to be inside that tied text.
- Confidence: likely

### M-14 9.A: FAIL for a block that has nothing to tab through, and for toggles that are not link or button
- Severity: P2
- Kind: bug (wrong FAIL)
- Where: src/tobi508/checks/t9a.py:152-163 (`_is_candidate`: link to the same page, button, summary only), :336-337 (`_applies` never asks whether the block holds a stop), :741-764 (G5)
- What: (1) A repeated block of static text (a banner of two sentences, no link or button) is a block of 4 or more words, so A5 applies; no candidate exists; G5 FAIL "Add a Skip to main content link" although a keyboard user has nothing to tab through. (2) `role=switch|checkbox|menuitem|tab` toggles and checkbox-hack menu toggles are not candidates, so a page whose only method is one of these gets FAIL "no keyboard method" (TT HtT 2.a lists "hide options, collapse menu"). (3) Every candidate gets Enter only; a `role=button` toggle that listens for Space only is judged "did nothing" (M5). Wrong FAIL is the safe direction for a false PASS, but it is a wrong finding with advice.
- Evidence: ran n_t1.html/n_t2.html (repeated header of two static paragraphs, then main): `9.A FAIL ['A5','G5']` "we found no keyboard way to skip past it". (2) and (3) read only.
- Fix: add to A4: "no unit of B is a walk stop" (DNA, nothing to bypass); widen candidates to toggles by role; press Space as well for non-native buttons.
- Confidence: confirmed (1); likely (2, 3)

### M-15 9.A: a key the page "documents" is pressed from the top; validation of the agent's key is syntax only
- Severity: P2
- Kind: security
- Where: src/tobi508/checks/t9a.py:584-598 (`apply_answers`), :248-260 (`try_key`); CLAUDE.md principle 5 (four approved exceptions; 9.A's key is not among them)
- What: Page text (through the agent) chooses a key press. The guard is `[A-Za-z0-9+]{1,30}` plus a quote of at least 3 characters that appears in the page's key snippets; the key itself need not appear in the quote or the page text, and "never one the browser itself uses" (the limit CLAUDE.md puts on the 2.A-2.C key) is not applied (`F5`, `Control+R`, `Enter`, `Tab`, `Escape` pass). In headless Playwright these do little harm, but a key that moves focus (for example `Tab`) lands on the first control and can make M7 "work" for a block that has no control to tab through.
- Evidence: read.
- Fix: require the key's last token to appear (case-insensitively) inside the quote, refuse keys with Tab/Enter/F-keys or Control/Meta, and list this exception in CLAUDE.md principle 5 (or drop it).
- Confidence: likely

### M-16 5.H: J2 `review_step`/`reversible` gives PASS even when nothing could be seen
- Severity: P2
- Kind: false-pass-risk
- Where: src/tobi508/checks/t5h.py:152-153 (M2 has no `not f.left` or empty-`after` guard), :90-96 (`left`), spec edge "Submitting leaves the page ... J2 unsure, NEEDS REVIEW (M4)"
- What: Only the agent's rubric keeps the answer at unsure when `after_submit` is empty. If the form left the page (or the after-read failed), a hallucinated `review_step` passes. J2 is one of the questions a careful tester settles by looking, but then the evidence has to show something.
- Evidence: read.
- Fix: M2 requires `not f.left` and a non-empty `f.after` (or alerts); otherwise M4.
- Confidence: likely

### M-17 5.F: a failed after-submit read is not an "incomplete" reason, and a failed Tab read is ignored
- Severity: P2
- Kind: false-pass-risk (DNA)
- Where: src/tobi508/checks/t5f.py:217-221 (`_top` swallows every exception), :384-386 (`failed=True`), :1229-1256 (`incomplete_of` flags only `a.base.failed`), :450-452
- What: If the read after the submit press (or after a Tab) fails without the URL changing (execution context destroyed by a client-side reload, a page crash, an evaluate error), the read is stored as `failed`, `last` falls back to an older read, and with no instance the result is A3 DNA "the page did not check for errors". Spec G3 lists only "the page could not be read before an attempt", but M1 says "a read was ... unresolved".
- Evidence: read; not reproduced (needs a page that breaks the context after the press).
- Fix: in `incomplete_of`, flag any `r.failed` read of an attempt that is not already `sent`.
- Confidence: likely

### M-18 5.F: spec and code differ on the pressing key and the word lists
- Severity: P2
- Kind: gap
- Where: src/tobi508/checks/t5f.py:436 (always `Enter`), :50-59; spec 5.F section 2 "Enter on a button; Space on a role button", SKIP_WORDS and SUBMIT_WORDS lists
- What: A `role=button` that only answers Space is pressed with Enter (no error, DNA). Code SKIP_WORDS adds `prev`, `logout`; SUBMIT_WORDS adds `login`; the spec lists differ. The words are English only; a non-English page falls back to "the first button", which is a safe default.
- Evidence: read.
- Fix: press Space for non-native buttons; make the spec list match the code (or the reverse).
- Confidence: confirmed (read)

### M-19 5.F/5.G: J1 is asked per field and per attempt, each with the same error list
- Severity: P2
- Kind: tokens
- Where: src/tobi508/checks/t5f.py:1001-1026 (one J1 per instance), :959-960 (`error_inputs`: every new text, up to 200 pieces of 300 characters, in each question's `input`), t5g.py:144-174
- What: Attempt 1 makes every field of the form an instance when one page-level message appears, and attempt 2 does it again for the typed fields: a 5-field form gives 10 J1 questions in 5.F and 10 in 5.G, each carrying the full `errors` list in its own input (the pipeline shares question and rubric text, not inputs). Up to 5 forms and 40 fields: hundreds of questions in the worst case.
- Evidence: read (pipeline._question_view dedupes only question and rubric).
- Fix: one J1 per attempt with a list of fields (or `shared_inputs` for `errors`), and ask attempt 2 only for fields where attempt 1 gave no answer.
- Confidence: likely

### M-20 Dead code and duplicates
- Severity: P3
- Kind: dead-code
- Where: t5f.py:303 and t5f.py:1348, t5g.py:261 (`PassE.notes` is read, never appended); t5f.py:46 (`FIELD_MAX = 40` duplicated from t5d.py:61, comment says "as 5.D"); t5f.py:93-115 vs forms.py:77-90 and forms.py:113-118 (three visible-text TreeWalkers); t5h.py:147 (`INSTANCE` lambda with `noqa`, rebuilt per call)
- What: small duplicates that must be changed together (a cap, a text walker).
- Evidence: grep.
- Fix: import `FIELD_MAX` from one place, remove `notes`.
- Confidence: confirmed

### M-21 Weak quote check for J1 (5.F, 5.G) allows one-character quotes
- Severity: P3
- Kind: false-pass-risk
- Where: src/tobi508/checks/t5f.py:1092-1094 (`quote_in`: any non-empty substring), versus t9a.py:586-588 (quote of at least 3 characters)
- What: A `described` or `guides` answer with quote "a" is "found" in any error text and leads to PASS (5.F M6, 5.G N4). The mechanical check is meant to prove the agent read the text.
- Evidence: read.
- Fix: minimum length (as 9.A: 3) and the quote must hold a word of the field's label for 5.F.
- Confidence: confirmed (read)

---

# Spec versus code, row by row

"Same?" means the same condition; "order" means first-match order. All line numbers are in the check's file unless a path is given.

## 5.F (spec 1.5.0, src/tobi508/checks/t5f.py)

| Spec row | Code | Same condition? | Same order? |
| --- | --- | --- | --- |
| A1 no field stop, inventory 0 | :1125-1126 (`field_stops == 0`, `inventory_fields == 0`) | yes | yes (first). But see M-01, M-06, M-07: the inventory counts what the walk and DOM see only |
| A2 no field stop, inventory > 0 | :1126 | yes | yes |
| A3 pass E in full, nothing sent, no instance -> DNA | :1376-1382 (after the instance loop; needs `not results and not incomplete and not pending_j0`) | looser than "an error indicator": the indicator read has blind spots (M-06); "in full" misses a trap (M-05) | spec lists A3 in section 1, code decides it after the instance rows (no outcome difference) |
| A3s site search sent -> DNA | :1373-1375, `site_search` :1112-1119, `FORMS_JS` :180-199 | yes (one field, text or search kind, no limits, marked as search) | before A3, as spec |
| A4 form sent, no indicator -> NEEDS_REVIEW | :1127-1130 (`a.sent` and no instance of that attempt, not a search); `sent` :444-449 | yes; "sent" ignores a `#fragment` change (correct) | A4 before instance rows (spec G1 first), yes |
| A5 otherwise | :1131 | yes | yes |
| Pass E attempt 1 (as loaded, submit control, else Enter in last text field) | :466-489, :573 | button: only submit-type buttons (M-01); `[role=button]`: Enter, not Space (M-18) | n/a |
| Pass E attempt 2 (wrong values, Tab after each, then submit) | :508-575 | yes; date fields typed; selects etc. left | n/a |
| Wrong value table | `wrong_value` :319-349 | yes (email, tel, year, number, name, other; cut to maxlength) | order as spec |
| Submit control choice (SKIP_WORDS, SUBMIT_WORDS, first one) | `_choose` :376-381, words :50-59 | code adds `prev`, `logout`, `login` (M-18) | yes |
| J0 (agent names the sending control) | `j0_needed` :940-952, `questions_for` :974-998, `apply_j0` :1077-1085 | condition: no sent, no new text, no invalid event, no instance, other buttons untried; but the list of buttons is submit buttons only (M-01) | n/a |
| Run limits: frames, unread field, FORM_MAX 5, FIELD_MAX 40, `ctx.out_of_time()` | :597-664, :694-701, :676-681 | yes, each goes to `incomplete` (G3) | n/a |
| M1 unreached / unsettled | not reached -> `incomplete_of` :1237-1241; unsettled -> row M1 :1167 and :1246-1251 | yes; a failed after-read is not flagged (M-17) | M1 first in code, but `is_none` (M4 and J1 no_error) is applied before the table; harmless because unsettled instances get no questions |
| M2 native validation PASS | row :1168-1173, `Inst5F.native` :837-840 | per-field `validationMessage` is taken for every invalid field once any `invalid` event was not cancelled, not only the field the browser focused; same as spec wording | yes |
| M3 aria-invalid / look + J2 error -> FAIL | rows :1174-1185 (two M3 rows) | yes | yes |
| M4 J2 not_error -> no instance | `is_none` :1222-1226 | yes | applied before M1..M3 (spec has it after M3); no outcome effect because J2 is asked only when no M3 row matched |
| M5 J2 unsure / unanswered | row :1186 (`not i.page_text`) | yes | yes |
| J1? | row :1187-1192 | yes | yes |
| M6 described, quote found, notice -> PASS | row :1193-1200, `notice` :787-800 | yes; quote check is any substring (M-21) | yes |
| M7 described, quote found, no notice -> FAIL | row :1201-1206 | yes | yes |
| M8 not_identified / not_described -> FAIL | row :1207-1212 | yes | yes |
| M9 unsure or quote not found | row :1213-1218 (`J1 != no_error`) | yes | yes |
| G1 | :1329-1346 | yes | yes |
| G2 any FAIL | :1383 | yes | yes |
| G3 NEEDS_REVIEW conditions | :1386, `incomplete_of` :1229-1256 | all listed conditions present except "P1 incomplete before the last field" for `stuck`/`loop` (M-05) and the A2-type case for 5.H (M-04) | yes |
| G4 PASS | :1388 (`elif results`) | yes | yes |
| G5 anything else | :1391 | yes | yes |
| Guard GU | applied by the pipeline from the front matter | not read here | after G rows |
| J2 question and images | :1027-1048 | yes | n/a |

Code that decides an outcome with no spec row: none found in t5f.py. Spec row with no code: none. The spec A3/A4/M2 definitions are the source of M-01, M-06 and M-07 (spec gaps).

## 5.G (spec 1.3.0, src/tobi508/checks/t5g.py)

| Spec row | Code | Same condition? | Same order? |
| --- | --- | --- | --- |
| A1 (5.F section 1 gives DNA or NEEDS_REVIEW) | t5g.py:242-259 (A1, A2, A4 via `t5f.applicability`), :290-299 (DNA "A1" when no instance; also 5.F's A3s) | yes (inherits M-01, M-05, M-06, M-07) | yes |
| A2 applies | :260 | yes | yes |
| N1 unsettled | row :87-92 | yes | yes (first) |
| N2 password -> DNA for the field | row :93, `is_none` :133-134 | yes | before N3, as spec |
| N3 no text and aria-invalid, or look and J2 error -> FAIL | rows :94-100 | yes | yes |
| J2? | row :101-103 (`not _has_text`) | yes | yes |
| J1? | :104-109 | yes | yes |
| N4 guides + quote in error text or instructions -> PASS | row :110-115, `_quote_ok` :75-78 | quote may come from any new text of the attempt, not only the text tied to the field (M-13) | yes |
| N5 no_guidance -> FAIL | :116-121 | yes | yes |
| N6 not_knowable -> NEEDS_REVIEW | :122-127 | yes | yes |
| N7 anything else | :128 | yes | yes |
| G1-G6 | :242-323 | yes (G4 all DNA, G5 PASS, G6 else) | yes |
| J1 input: error text tied to the field by 5.F's J1 quotes | :152-156 | NO: always all new text (M-13) | n/a |
| Guard GU | pipeline | n/a | n/a |

No outcome decided outside the spec found. 5.G J0 runs only when 5.F was not collected in the same call (`standalone`, :345); order follows `TestId`, so 5.F always collects first when both are selected.

## 5.H (spec 1.2.0, src/tobi508/checks/t5h.py)

| Spec row | Code | Same condition? | Same order? |
| --- | --- | --- | --- |
| A1 pass E found no form with a submit control -> DNA | :311-325 (`not st.forms`) | NO: pass E forms are forms with FIELDS (M-02, M-07); and a form with fields but no submit control is not DNA in code (stricter) | A1 before A2 in spec; code puts "not ran" and "no forms with incomplete" first |
| A2 pass E not run / incomplete and no hint -> NEEDS_REVIEW | :303-319, :326-335 | `incomplete_of` lacks the "fields exist but none reached" case (M-04); incomplete ignored when a hint exists (M-09) | yes |
| A3 no hint, read in full -> DNA | :336-342, `HINT` :29-35 | English words only (M-03); hint also read from the page's whole text, which makes hints more likely (safe) | yes |
| J1? hint and J1 open | :343-347, `questions_for` :221-239 | yes | yes |
| A4 J1 not_consequential or one_page -> DNA | :348-354 | yes (agent opinion decides DNA; spec allows) | yes |
| A5 J1 unsure -> NEEDS_REVIEW | :355-359 (`j1 != multi_step or f is None`) | also NEEDS_REVIEW when `element` names no form | yes |
| A6 multi_step -> applies | :360 | yes | yes |
| M1 checked -> PASS | `INSTANCE` row :148, `checked` :105-116 | looser than the spec's "(not sent, fields still there, ... a next step's required text is not a check)": existence of the field element, not visibility; English word list; counts cancelled invalid events (M-08) | M1 first, as spec |
| J2? | :149 | yes | yes |
| M2 J2 review_step / reversible -> PASS | :150-155 | no guard for "page left, nothing seen" (M-16) | yes |
| M3 J2 none -> FAIL | :156-161 (`and not f.left`) | stricter than spec (spec: none -> FAIL); falls to M4 when left: safe | yes |
| M4 anything else -> NEEDS_REVIEW | :162 | yes | yes |
| G1-G4 | :362-379 | yes (single chosen form; other hinted forms untested, as spec edge) | yes |
| Guard GU | pipeline | n/a | n/a |

Code deciding an outcome with no spec row: DNA at :311-325 for `not st.forms` is the spec's A1 by name only (see M-02). Everything else maps to a row.

## 9.A (spec 1.1.0, src/tobi508/checks/t9a.py, with src/tobi508/site.py)

| Spec row | Code | Same condition? | Same order? |
| --- | --- | --- | --- |
| A1 no other pages -> NEEDS_REVIEW not performed | :264-265, :643-648 | yes | yes (first) |
| A2 page could not be read | :271-272, :649-652 | yes (`read_page` errors) | yes |
| A3o all other pages share almost nothing and tested page has navigation -> NEEDS_REVIEW | :276-277, :654-661; `site.kinship` | as spec; but a shadow-root header gives no "navigation of its own" (M-12) | before A3, as spec |
| A3 no unit repeated -> DNA | :662-668 | yes; units are the light DOM only (M-12); a page truncated at 600 units is not checked here (spec: "a page over the cap is incomplete") | yes |
| A4 repeated units but B empty or small -> DNA | `_applies`, `_small` :327-337, :669-680 | `_small` same as spec; M never found (all repeated, or truncated page) gives an empty B and DNA (M-11, and see "Unverified leads" for the 700-link page) | yes |
| A5 applies | :681 | yes | yes |
| Candidate (link to same page, role link with no address, non-submit button, summary; at most 8) | `_is_candidate` :152-163, `candidates` :166-193 | yes; `javascript:` links also count (extra, harmless); no switch/checkbox/tab roles (M-14) | walk order |
| Candidate replay: Enter, landing, hidden, nav, one Tab | `try_candidate` :228-245, `_read_after` :196-226, `LANDING_JS` :55-85 | landing falls back to `:target` without comparing before and after (M-10); `!e` (element gone after a re-render) counts as hidden (see leads) | n/a |
| Early stop once bypassed; untried count noted | :296-312 | yes | n/a |
| Documented keys (J1 then fresh load) | `try_key` :248-260, `apply_answers` :567-598 | key validation is syntax only (M-15) | n/a |
| M1 not reached or reads failed -> NEEDS_REVIEW | row :361-365 | yes | yes |
| M2 navigation -> does not work | :366 | yes (ignores `#fragment`, correct) | yes |
| M3 every B unit after the candidate hidden -> works | :367-372 | yes | yes |
| M4 some hidden -> works in part | :373-378 | yes; coverage rule `bypassed` :415-430 makes "in part" matter | yes |
| M5 no landing or not after candidate -> does not work | :379-384 | yes | yes |
| M6 next Tab before the landing -> does not work | :385-394 | yes | yes |
| M7 landing at or before M -> works | :395 | yes | yes |
| M8 landing past M and M is main/h1 -> does not work | :396 | yes | yes |
| J2? / M9 / M10 / M11 | :397-402, `questions_for` :508-553 | yes | yes |
| Coverage (first working candidate F, every B unit after F covered, at most 2 block stops before F) | `bypassed` :415-430 | yes | n/a |
| G1 | :643-680 | yes | yes |
| G2 bypassed -> PASS | :692-708 | yes | G2 before G3 |
| G3 instance NR / J open / capped / time out -> NEEDS_REVIEW | :714-732 | yes; `st.incomplete` (truncated page, frame in B, walk missing, time) reaches G3 only after A3/A4/G2 | yes |
| G4 documented key bypasses -> PASS | :733-740 | yes | yes |
| G5 not bypassed, all decided, J1 no or not asked -> FAIL | :741-764 | yes (see M-14 for wrong FAIL) | yes |
| G6 anything else | :765-772 | yes | yes |
| Guards | 9.A declares none; it presses Enter on candidates and runs page handlers | GU would only affect PASS; a skip link that depends on unrecorded code gives a FAIL, not touched by the guard | n/a |

No outcome decided outside the spec found in t9a.py.

---

# Time cost (lower priority)

### M-22 Replays and sleeps per form (worst case per run)
- Severity: P3
- Kind: time
- Where: t5f.py:589-595 (`_forms`: 1 replay), :667-682 (`run_attempts`: 2 replays per form), :710-719 (J0: 2 more per newly named button), :436-439 (settle plus a fixed 150 ms after each submit press), :533-540 (a settle and a full-page text read after each Tab in attempt 2); t9a.py:228-245 (one replay per candidate, at most 8, plus one for a documented key), site.py:285-293 (one load per page)
- What: 5.F/5.G/5.H together: at most 1 + 5 forms x 2 = 11 replays, 21 with J0 per form; 150 ms x at most 10 submit presses = 1.5 s of fixed sleep; per text field in attempt 2 one arrive (Tab presses with the settle rule), one `FIELD_FN`, one type, one Tab and one text read that walks every text node (`READ_JS`), up to 40 fields. 9.A: at most 8 + 1 replays and N + 1 page loads. No extra live page loads. The cost is as the spec's time budget; nothing is repeated between 5.F, 5.G and 5.H (pass E is cached, `5f-pass`).
- Evidence: read; the run with a 700-link menu (see leads) took more than 2 minutes in the walk, which is shared with all keyboard tests.
- Fix: none needed beyond M-19.
- Confidence: confirmed (read)

---

# Unverified leads

- 9.A: tested page with a very large repeated menu (over 600 units before the main content): `UNIT_CAP` 600 cuts the units, M may never be found (every unit read is repeated), B is empty and A4 DNA "comes after the main content" could follow (spec says a truncated page is incomplete, but `st.incomplete` is read only after A3/A4/G2, t9a.py:662-680). I ran n_big1.html (700 links + main) with n_big2.html; the walk did not finish within 2 minutes, so no result (see the end of this file if it later completed).
- 9.A `LANDING_JS` (t9a.py:78-82): `!e` (selector not found after the press) counts a block unit as hidden; a toggle that re-renders the header (framework re-mount) would be M3 "hides the block". Not tried.
- 9.A: skip links written as `href="/page#main"` or `href="index.html#main"` when the tested URL differs only by a default document are not candidates (`norm_href` compares the base with the page URL as loaded), so the page can get a wrong FAIL. Not tried.
- 5.F: `i.page_text` is page-wide, so an unrelated new text (clock, carousel, cookie notice) makes every field's attempt a "page-level message" instance and sends J1 questions; a field marked only by `aria-invalid` then goes through J1 and `no_error` removes it (is_none), so the aria-invalid FAIL (M3) is lost. Read only (t5f.py:858-864, :1224-1226).
- 5.F: J0 `none` or `unsure` leaves A3 DNA ("the page did not check for errors"): an agent's opinion about button names decides DNA. Spec-conform; read only.
- 5.F M2: native validation PASS is applied to every invalid field with a message once any `invalid` event was not cancelled, although the browser only shows the first; and a `setCustomValidity("Error.")` message counts as an identifying message. Read only (t5f.py:837-840).
- 5.F `new_texts` and 5.H `collect` compare texts by (path, text); a page that re-renders the error region at another DOM position on each press is still found, but a message that already existed visibly (same path, same words) before the press is never new. Not tried.
- 5.H: `after_submit` can hold up to 60 pieces of 300 characters per attempt and form, and J2 repeats it; `page_text` is 60 x 200 characters. A large SPA step could cost thousands of tokens per call. Not measured.
- 5.H: a GET form that navigates to a recorded page makes `a.sent` true with a successful read of the NEW page; `after_submit` is then that page's text and J2 could answer `review_step` on a different page. Not tried.
