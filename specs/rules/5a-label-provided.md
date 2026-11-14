---
tt_test: 5.A
tt_name: 3.3.2-label-provided
spec_version: 1.9.0
guards: reveal
count: fields.shadow, fields.frames, fields_hidden, contenteditable
source: DHS Section 508 Conformance Test Process for Web (Trusted Tester) v5.1.3, April 2024
owner: Abby Bowman
---

# Rules spec: Test 5.A (3.3.2-label-provided)

The tool gives each page one 5.A outcome: PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW. It never emits NOT TESTED (p. 6).

**Citations.** Printed pages of TT 5.1.3 (text also in `tt://5.1.3/tests/5.A`). Forms Identify Content, p. 25: identify form elements with ANDI focusable elements ("buttons, text fields, radio buttons, checkboxes, read-only fields, and multi-select lists") and their instructions and cues; exclude disabled elements; none: DOES NOT APPLY to 5.A–5.H. 5.A, p. 25: DNA if no form elements or all disabled (Applicability); "determine if each form element provides visual labels or instructions" (HtT 1); PASS if "visual labels or instructions are provided for each form element" (ER 1). Notes: the label or instruction "must be visible when the form field has focus"; it "can be graphical or textual"; accuracy is 5.B; programmatic association is 5.C.

**Other sources.** [Understanding 3.3.2](https://www.w3.org/WAI/WCAG22/Understanding/labels-or-instructions.html): labels or instructions identify the controls so users know what input is expected; each option of a radio group or checkbox set needs its own label; instructions may appear only while the control has focus; images may be labels; the criterion "does not apply to links or other controls (such as an expand/collapse widget ...) that are not associated with data entry"; an `aria-label` alone can pass 4.1.2 and still fail 3.3.2 ("if the labels or instructions aren't presented to all users"). Sufficient techniques G131 with H44 (the label element "must be visible" for 3.3.2), G89, G162, G167 (an adjacent button labels a field), H71, H90. Failure [F82](https://www.w3.org/WAI/WCAG22/Techniques/failures/F82) (a set of phone number fields with no visible text label near the set and no instructions). No ACT rule; no DHS ACT data. ICT Testing Baseline 3.1 [10.E-FormHasLabel](https://ictbaseline.access-board.gov/web-baselines/10Forms/): form components "associated with data entry", not `visibility:hidden` or `display:none`; "each form component has visible label(s) or instructions while the form component has focus". Baseline Alignment cases TC10.E (four) and, for the visual side, TC10.A (section 5).

**Terms.** *Stop*, P1 and the walk: [4c-no-keyboard-trap.md](4c-no-keyboard-trap.md). *Field* and a field's kinds: [5d-on-input.md](5d-on-input.md) Terms. *Pass L* (one fresh load after the walk; the form-component inventory; reads per component): [5c-programmatic-label.md](5c-programmatic-label.md) section 2; 5.A and 5.C share it. A *data-entry field* is an inventory component that takes input: a field of any 5.D kind, enabled and not read-only (Understanding 3.3.2 and Baseline 10.E: not buttons, links or disclosure widgets; read-only fields take no input). A *visible label* is text of the field's `<label>` (for or wrapping), its `aria-labelledby` elements, or its group's `<legend>` / group label (for a radio button or checkbox, only when it is the only option under that legend or group label: with two or more options the legend asks the question and names none of the answers, Understanding 3.3.2 "each option must have an appropriate label so that users know what they are actually selecting", H71; Abby, 2026-11-02; 1.1.0), that is rendered and readable while the field has focus: `checkVisibility`, a box at least 4 × 4 px, not clipped to 1 px (the "visually hidden" pattern), opacity above 0.1, and inside the pass L image of the field.

## 1. Applicability

| # | Evidence | Outcome | Source |
| --- | --- | --- | --- |
| A1 | The inventory has no form component that is enabled and rendered | DOES NOT APPLY | p. 25 Identify Content, Applicability; TC10.A-ic-dna-1, -2 |
| A2 | Components exist but none is a data-entry field (buttons only) | DOES NOT APPLY: buttons label themselves, and their wording is 5.B | Understanding 3.3.2 (data entry); Baseline 10.E |
| A3 | Pass L did not run or the inventory could not be read | NEEDS REVIEW | Spec rule |
| A4 | Otherwise | Applies; go to section 3 | |

## 2. Evidence to collect

Nothing of its own: pass L ([5c-programmatic-label.md](5c-programmatic-label.md) section 2). For each data-entry field it records, with the field focused (`el.focus()` on pass L's load, so focus-only instructions and floating labels show): its visible-label candidates and whether each is visible; its placeholder and whether the field is empty; its `aria-label` and `title` (never visible text); the visible text within the image (at most 400 characters, nearest first; for a radio button or checkbox, only its own row's: text in a block that holds a link or another radio button or checkbox and not this option is that block's, not the option's, so result cards that script adds inside a filter form ("ID: 15116") are left out while a question in a block of its own stays; the block is the largest element around the text that does not hold the option; 1.6.0, post-round 2 fix 9c); the text of buttons in the image that act on the field's form (in the field's form, or in no form when the field has none; not a menu or disclosure button: `aria-expanded`, or `aria-haspopup` other than false; 1.2.0); the number of those buttons that have no text (an icon button: a magnifier, a clear button) and sit in the field's input group (the field's own parent element) or in its search form (`role=search` or `<search>` on the form or around it; 1.5.0), and the words of those with text there (a search box's "Go"; 1.8.0) and, for an option in a set, the visible text without the legend and whether a picture is near it (1.1.0); and one image: the field's box grown by 240 px left, 120 px up and 160 px right and down, clipped to the viewport after scrolling the field into view (`traverse.screenshot()`).

**Time budget:** one focus, a few DOM reads and one clipped image per data-entry field, about 0.1 s each, on pass L's load.

## 3. Mechanical checks

Each data-entry field is an *instance*; each radio button and checkbox is its own instance (Understanding 3.3.2: each option needs a label). A *set* is two or more radio buttons or checkboxes under one `fieldset` or `role=group`/`radiogroup`, whatever their names (1.1.0). Parts of a multi-part field (F82: a phone number in three boxes) are instances, and a visible label for the set counts for each part (J1's rubric).

**3a. Instance rules (first match wins)**

| # | Evidence pattern | Instance outcome | Source |
| --- | --- | --- | --- |
| M1 | The field could not be focused or read, or its image is missing | NEEDS REVIEW | Spec rule |
| M2 | A visible label with text | PASS | p. 25 ER 1; H44 |
| M2o | A radio button or checkbox in a set with no visible label of its own, no visible text near it apart from the legend (text in any script counts, 1.9.0, review H-02: a Cyrillic or Japanese label beside an option is text), and no picture near it | FAIL: a person cannot tell which choice it is (1.1.0) | Understanding 3.3.2 (each option needs a label); H71; Abby, 2026-11-02 |
| M2i | No visible label of its own (not an option in a set), and a button sits in the field's input group or search form (section 2), with a picture (1.7.0) or words such as "Go" (1.8.0): it is part of the field, so a label is provided, whatever it shows or says (Abby, 2026-11-13; ACT cc0f0a Failed Example 5, where "Go" labels the field and fails 2.4.6, is 5.B's FAIL). Whether it describes the field (a magnifier on a search box does; a tree, a logo or an envelope does not) is 5.B's | PASS (1.7.0) | p. 25 ER 1; Notes 2 ("can be graphical or textual") and 3 ("only determines whether visual labels or instructions are provided, regardless of accuracy"); Abby, 2026-11-13 |
| M3 | No visible label; the only text shown for the field is its placeholder, and no button's text is beside it (a "Search" button labels the box beside it, G167: J1; 1.1.0). Only buttons that act on the field's form count (section 2): a site header's menu button beside its search box does not (Abby, 2026-11-04; post-round 1 fix 10: NASA's "Explore" kept M3 from firing on 9 pages; 1.2.0), and no icon button sits in the field's input group or search form (such a field is M2i; Abby, 2026-11-08, post-round 2 fix 8: svs.gsfc.nasa.gov's "Search..." box with a magnifier submit button and a clear button in one input group, key Pass on 7 pages; a menu button with an icon still does not count; 1.5.0) | FAIL: a placeholder is not a label; it disappears as soon as the user types, so the field is no longer labelled while it still has focus (Abby, 2026-11-01) | p. 25 Note 1 ("visible when the form field has focus"), Note 2 ("can be graphical or textual"); W3C forms tutorial, [Placeholder text](https://www.w3.org/WAI/tutorials/forms/instructions/#placeholder-text) ("not a replacement for labels"); [w3c/wcag#4918](https://github.com/w3c/wcag/issues/4918) (placeholder alone "would fail 3.3.2"; it does provide an accessible name, so 5.C is not affected: TC10.A-all-pass-1) |
| J1? | Otherwise, J1 not answered | NEEDS REVIEW | Open question |
| M4 | J1 = labeled, its quote found in the visible text of the image (as written, or its words in one piece of text: a label's colon can be a piece of its own, 1.1.0), or J1 = graphic | PASS | p. 25 ER 1, Note 2 |
| M5 | J1 = not_labeled | FAIL | p. 25 ER 1; Understanding 3.3.2 (`aria-label` alone); TC10.E-1-fail-1 |
| M6 | J1 = unsure, or a quote not found | NEEDS REVIEW | Spec rule |

**3b. Page outcome (first match wins)**

| # | Evidence pattern | Page outcome |
| --- | --- | --- |
| G1 | Section 1 gives DOES NOT APPLY or NEEDS REVIEW | That outcome |
| G2 | Any instance is FAIL | FAIL, listing every instance |
| G3 | Any instance is NEEDS REVIEW, or a field was not read (cap, time) | NEEDS REVIEW, with the note "This test could not be performed" and the reason (p. 5) |
| G4 | Every instance is PASS | PASS |

**Plain-language sentences.**

| Row | Sentence |
| --- | --- |
| Page PASS | "Each form field has a label or instructions people can see when they are on it." |
| Page FAIL | "Some form fields have no label or instructions people can see, so a person may not know what to enter." |
| Page NEEDS REVIEW | "We could not finish this test, so a person needs to check it." |
| A1 | "This page has no form fields, so this test does not apply." |
| A2 | "This page's only form controls are buttons, which carry their own text, so this test does not apply." |
| M2o | "<field> is one of several choices under the same question, and nothing beside it says which choice it is, so a person cannot tell the choices apart. Give each choice its own label." |
| M3 | "<field>'s only label is the gray example text inside it, which disappears as soon as someone starts typing. Add a label that stays visible. To see it, load the page and move to the field." |
| M5 | "<field> has no label or instructions people can see (screen readers may still announce a name). To see it, load the page and move to the field." |
| M6, M1 | "We could not tell whether <field> has a label people can see. Please look at it." |

**Opened content is read like content at load** (fix 9b; Abby, 2026-11-09). Every state `reveal.py` opens is read with ANDI like the page as loaded, and when opened content holds sets of check boxes or radio buttons, up to two options of each (at most 3 sets) are chosen together with Space on a fresh load and the page is read again, because choosing can add controls (a filter that adds a remove button for each choice). Components found this way are tested like any other and say how they were reached.

**Guard RV: something that opens was not opened** (front matter `guards: reveal`; defined in [_template.md](_template.md); Abby, 2026-11-09, fix 9b). The menus, tabs, accordions and filters the keyboard walk found (a collapsed control, `aria-haspopup`, `aria-controls`, a tab that is not selected, a closed `<summary>`) are each opened on a fresh load (`reveal.py`, `Report.reveal`; at most 20, Enter first and a click when Enter showed nothing). When one was not opened (it showed nothing, could not be found again, failed to run, was over the limit or out of time) or what it opened could not be read, a page outcome of PASS becomes NEEDS REVIEW with the plain sentence "The page has menus or sections that open, and some could not be opened or read (...), so what is inside them was not checked." Trace row `RV`. FAIL and DOES NOT APPLY are unchanged: the guard only moves a would-be PASS toward review.

**Guard CN: form fields pass L could not read** (1.4.0; front matter `count:`; defined in [_template.md](_template.md); Abby, 2026-11-12; review D-01, H-08). The page's inventory (`count.py`, `Report.counts`) counts form fields inside web components (open shadow roots) and inside frames, form fields in the page but hidden when it loads (`display: none`, `hidden`, a closed `<details>`), and editable text areas (`contenteditable`). Pass L reads the page's own document only: nothing inside web components or frames and no editable area, and a hidden field only when an opened section showed it (matched by its path; `labels.what_was_read`). When the inventory has more of any of these than pass L read, a page outcome of PASS or DOES NOT APPLY becomes NEEDS REVIEW with "This test could not be performed" and one plain sentence per gap ("2 form fields inside web components were not checked", "1 form field is hidden until something opens it, and was not checked"). Hidden fields count only when the page has something that could show them (a button, a disclosure, a same-page or script link, an inline click handler); on a page with none, a hidden field is hidden from everyone and holds nothing, as DHS's Baseline cases TC10.A-ic-dna-1 and -2 expect (Abby, 2026-11-12). Trace row `CN`. FAIL is unchanged. A hidden form behind a plain button, which the reveal pass does not open, therefore ends NEEDS REVIEW, not DOES NOT APPLY.

## 4. Judgment questions

J1 is settled by looking (CLAUDE.md principle 8): its labeled answer leads to PASS only with a quote found in the image's visible text, or the graphic answer naming what the graphic shows; the agent answers unsure whenever the image does not settle it.

### J1. Can people see a label or instructions for this field?

**Question:** "Image A shows the field named in input.field while it has focus, with what is around it. Is there visible text or a picture next to it that tells the user what the field is for or what to enter? Answer labeled (copy the words into quote), graphic (describe it in reasons), not_labeled or unsure."

**Input:** image A; the field's kind and type; its placeholder, if any (shown separately: it does not count); `labels_of_neighbouring_fields`: the visible labels of other fields in the image (a set of fields may share one label, F82; the rubric counts one only when this field is part of the set it labels) (its accessible name is not shown: a name people cannot see is not a visual label); `text`: the visible text in the image, nearest first, labelled as untrusted page data (for an option in a set, without the legend); `question_of_the_set`: the legend, for an option in a set (1.1.0); `buttons_next_to_it`: the text of buttons in the image (1.1.0).

**Output:** `{choice: labeled|graphic|not_labeled|unsure, quote, reasons}`.

**Rubric.** A quote may come from `text`, `buttons_next_to_it` or `labels_of_neighbouring_fields`. For a radio button or checkbox, `question_of_the_set` does not label it: the option needs its own words or picture (1.1.0). labeled: text people can see, beside, above or inside the field while it has focus, that goes with it as its label or instructions, accurate or not (TT p. 25 Note 3) ("First Name:" next to it, a column heading over a grid of fields, "(555) 555-5555" as the set's label for three phone boxes, a button beside a box, G167). A button counts, whatever its words, when it belongs with this field: the box's own button, beside it or just under it in a form of one field ("Subscribe" under a lone email box); a form's submit button below a form of several fields labels none of them (1.8.0, Abby 2026-11-13; this replaces 1.1.0's rule that "Go", "Find", "Submit", "Subscribe", "Send" or "Continue" do not label a field: whether their words describe it is 5.B's). graphic: a picture that plainly labels it (a magnifier on a search box, an envelope on an email field). not_labeled: nothing visible relates to the field (an empty label, text far away about something else). A placeholder inside the empty field does not count: it disappears when the user types (M3). unsure: anything else. Whether the label is clear or accurate is not asked (5.B).

| Example | Answer |
| --- | --- |
| "First Name:" text before the box, not associated in code (TC10.A-1-fail-1) | labeled, "First Name:" |
| An empty `<label>`, nothing else (TC10.E-1-fail-1) | not_labeled |
| "The sky is blue" as the label (TC10.E-1-pass-1) | (M2: a visible label; not asked) |
| A box with only a magnifier icon and a Go button in a search form | (M2i: PASS; not asked) |
| A lone email box with only a "Subscribe" button under it | labeled, "Subscribe" (5.B judges it) |
| The last of three fields, with only the form's "Continue" button below | not_labeled |
| A box whose only text is its placeholder "Search" | (M3: FAIL; not asked) |
| A box whose only text is its placeholder "Search...", with a magnifier submit button and a clear button in its input group (post-round 2 fix 8) | (M2i: PASS; not asked; 5.B judges the icon) |
| A logo or other picture near the box but outside its form | (not counted by pass L: M3 FAIL; not asked) |

**Use:** M4–M6.

## 5. Edge cases

| Case | Rule |
| --- | --- |
| Floating label that moves on focus | Read with focus: visible, M2 (a `<label>` that stays visible after typing, unlike a placeholder) |
| Placeholder and a visible label | M2 PASS; the placeholder is extra help |
| Instructions shown only while focused (a tip) | Read with focus: in the image text, J1 |
| Label hidden with the visually-hidden pattern | Not visible: J1 (Understanding 3.3.2: `aria-label` or hidden text alone fails) |
| Field in a table, labelled by its column header | J1 (the header is visible text in the image) |
| Hidden at load, revealed by interaction | Read on the replay that revealed it (5.C section 2) |
| Field inside a frame or a shadow root | Read in its own document; frames the tool cannot read are M1 |

## 6. What a FAIL records

Location (URL, frame chain, CSS path, kind), image A, the visible text read, the J1 answer, and how to reach the field ("Tab 6 times").
