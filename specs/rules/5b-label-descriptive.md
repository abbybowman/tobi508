---
tt_test: 5.B
tt_name: 2.4.6-label-descriptive
spec_version: 1.13.0
guards: reveal, drawn-past-wait
count: fields.shadow, fields.frames, fields_hidden, contenteditable, frames_missing
source: DHS Section 508 Conformance Test Process for Web (Trusted Tester) v5.1.3, April 2024
owner: Abby Bowman
---

# Rules spec: Test 5.B (2.4.6-label-descriptive)

The tool gives each page one 5.B outcome: PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW. It never emits NOT TESTED (p. 6).

**Citations.** Printed pages 25–26 of TT 5.1.3 (text also in `tt://5.1.3/tests/5.B`). Forms Identify Content, p. 25 (as 5.A). Applicability, p. 25: DNA "if the page does not have form elements, if all form elements are disabled, or if no visual labels are provided for form elements". HtT 1–2, p. 26: review the visual labels and instructions for each component; determine whether they "sufficiently describe the purpose and applicable data requirements (date formats, required fields, data type, etc.)". ER, p. 26: each visual form label is "sufficiently clear and descriptive, so users know what input data is expected" (ER 1) and each visual button label "so users know its function" (ER 2). Notes, p. 26: an error message is not enough to communicate the expected format; a label can be graphical or textual; labels that change automatically or by interaction are included.

**Other sources.** [Understanding 2.4.6](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html): labels "do not need to be lengthy. A word, or even a single character, may suffice"; the criterion "does not require headings or labels", only that labels provided are descriptive; a control can have a good accessible name and still fail if its label is not descriptive. [G131](https://www.w3.org/WAI/WCAG22/Techniques/general/G131): for each component with a label, identify its purpose and "Check that each label makes the component's purpose clear". W3C ACT [cc0f0a](https://www.w3.org/WAI/standards-guidelines/act/rules/cc0f0a/): each visible label, "together with its visual context, describes the purpose"; visible headings are context (repeated "Name"/"Street" under visible "Shipping" and "Billing" pass; the same under off-screen headings fail); "Menu" or "Info:" fail. DHS scored 14 of its 16 current cases (7 PASS, 5 FAIL, 2 DNA); ours follow the visual reading, as DHS's do (DHS passed the case whose visible label is hidden from assistive technology, which ACT calls inapplicable). ICT Testing Baseline 3.1 10.B-FormDescriptiveLabel: labels "describe purpose, inform users what input data is expected and, if applicable, what format is required". No Baseline Alignment case for 10.B.

**Terms.** *Pass L*, *component*, *data-entry field*, *visible label*: [5a-label-provided.md](5a-label-provided.md) Terms and [5c-programmatic-label.md](5c-programmatic-label.md) section 2. From 5.A 1.1.0, a radio button or checkbox in a set does not take the set's legend as its label; the legend is the item's `group`, and its near text leaves the legend out (1.1.0). An *item* is a data-entry field with a visible label or visible text near it (its pass L reads), or with an icon button in its input group or search form (5.A section 2 and row M2i: a graphic label, TT p. 26 Note 2; 1.5.0, Abby 2026-11-13; post-round 2 fix 8b: svs.gsfc.nasa.gov's search box, key 5.B Pass on Help, Galleries, 14194, 14592), or whose only cue is its own button's words: a button in its input group or search form, or, in a form of one field, the form's button beside it (5.A 1.8.0; the button's words are the field's near text; 1.6.0), or whose label 5.A found to be a picture (5.A's J1 = graphic with its reasons, M4: a graphic label, TT p. 26 Note 2; 1.10.0, Abby, 2026-11-17, step 29: round 3's Drupal search box, where the magnifier is the label), or a button with visible text that acts on a form's data: its form (or "none") has a field that is an item, and it is not a menu or disclosure button (`aria-expanded`, or `aria-haspopup` other than false). A site header's menu buttons are not form controls, and buttons alone are not a form (Abby, 2026-11-04; post-round 1 fix 14: NASA's "Explore" and "News & Events" were judged as a form, and 5.B passed where the tester found nothing to judge; 1.2.0). A field with none of these is not an item: it has no visual label to judge (Applicability), when 5.A found it unlabelled (its rule M2o or M3, or its J1 = not_labeled, M5: 5.A FAILs it). A field 5.A *left undecided* (M1, J1 not answered or not run, or M6: unsure or a quote not found; or M4 with a label 5.B does not read) is not known to be unlabelled, and is not an item either: it is A2u (1.10.0). 5.B only reads 5.A's rows and answers; it never decides them. A component's *form* is its form owner (or "none"); fields of one form are judged together, with their group labels (legends) and headings as context (cc0f0a).

## 1. Applicability

| # | Evidence | Outcome | Source |
| --- | --- | --- | --- |
| A1 | Pass L found no enabled, rendered form component | DOES NOT APPLY | p. 25 Applicability |
| A2 | Components exist, but none is an item (no visual labels), and pass L read every field (when pass L is incomplete, NEEDS REVIEW: unread fields may have labels to judge, 1.1.0), and 5.A found every field that is not an item unlabelled, by its rule M2o or M3 or its J1 = not_labeled M5 (1.10.0) | DOES NOT APPLY | p. 25 Applicability ("no visual labels are provided") |
| A2u | As A2, but 5.A left a field that is not an item undecided (M1, J1? or M6; also when 5.A was not part of the run), or found a label 5.B does not read (1.10.0; step 29: round 3's Drupal pages, where the search box sits in a panel the magnifier opens, 5.A's J1 was unsure and 5.B said no field has a visible label; the key passes) | NEEDS REVIEW, not performed: "The label test could not tell whether a form field on this page has a label people can see, so there may be a label to judge here" | Spec rule; Abby, 2026-11-17 |
| A3 | Pass L did not run | NEEDS REVIEW | Spec rule |
| A4 | Otherwise | Applies; go to section 3 | |


**Row WL: a page that drew itself after the walk began** (1.11.0; step 22, plan after round 3 cause 2; moves PASS, DOES NOT APPLY and FAIL only toward NEEDS REVIEW). The walk's elements are counted again when P2 ends, no sooner than 3 s after its load (`walk.COUNT_AFTER_S`; 4.C section 2), and the *count after the walk* is the largest of the counts at the start and at each pass's end (`KeyboardWalk.inventory_after`, `fields_after`). Round 3's community pages (an application drawn after load) had 1 element when the walk began and 76 and 90 later. 5.B reads pass L (5.A's row WL): a pass L that found no data-entry field while the walk counted fields after the walk is incomplete, so never DOES NOT APPLY. Its sentence: "The page drew <N> form field(s) after it loaded, after we had read its labels, so they were not checked." **Narrowed (step 22's first rerun, 2026-11-17):** "the page drew itself after the walk began" needs the count after the walk to be more than twice the count when the walk began (as 4.C's sign of a page that grew), or, for form fields, no field when it began and some after; only then do coverage rows count against the later count. Round 2's home page counted 145 elements, then 146 (one late link): that is not a page drawn late, and its 4.C and 4.E keep their outcomes.

**Guard WL: a page still drawing when the wait for it ended** (1.13.0; front matter `guards: drawn-past-wait`; defined in [_template.md](_template.md); #134). A load of the tested page waits for the page to draw itself, at most 10 s (`traverse.DRAW_MAX_S`; 4.C section 2, "Waiting for the page to draw"). When that wait ended at its ceiling with the count of elements that take focus changed in its last 2 s (`Report.drawn_past_wait`), the page was still drawing when the walk and the readers began, and a walk that ends in under 3 s can read the page as it stood then. A reading from such a load decides nothing: a page outcome of PASS or DOES NOT APPLY becomes NEEDS REVIEW with "This test could not be performed" and the plain sentence "The page was still drawing itself 10 seconds after it loaded, when we began to check it, so we may have checked it before it was finished." Trace row `WL`. FAIL is unchanged. Fixture `walk/drawn-after-wait.html`: a status link comes and goes every 400 ms and the controls appear 11 s after load (before the guard: 4.A and 4.C PASS, 5.A to 5.F DOES NOT APPLY, "no form fields").

## 2. Evidence to collect

Nothing of its own: pass L (shared with 5.A and 5.C; components now record their form). For each item: kind, type, the visible label text, up to three strings of visible text near it, its group label, required, placeholder (shown apart: not a label), the 5.A image of a field, a button's visible text.

**Time budget:** none beyond pass L (measured 0.0 s on both budget pages, 2026-11-02).

## 3. Mechanical checks

Each item is an instance.

**3a. Instance rules (first match wins)**

| # | Evidence pattern | Instance outcome | Source |
| --- | --- | --- | --- |
| J1? | Its form's J1 not answered | NEEDS REVIEW | Open question (Abby, 2026-11-02: one question per form) |
| M1 | J1 = all_descriptive | PASS | p. 26 ER 1, 2 |
| M2 | J1 = some_not_descriptive and the item is named | FAIL | p. 26 ER 1, 2; cc0f0a |
| M3 | J1 = some_not_descriptive, valid numbers, the item not named | PASS | p. 26 ER 1, 2 |
| M4 | Anything else (unsure, or numbers missing or not in the list) | NEEDS REVIEW | Spec rule |

**3b. Page outcome (first match wins)**

| # | Evidence pattern | Page outcome |
| --- | --- | --- |
| G1 | Section 1 gives DOES NOT APPLY or NEEDS REVIEW | That outcome |
| G2 | Any instance is FAIL | FAIL, listing each item |
| G3 | Any instance is NEEDS REVIEW, or pass L is incomplete | NEEDS REVIEW, with the note "This test could not be performed" and the reason (p. 5) |
| G4 | Every instance is PASS | PASS |

**Plain-language sentences.**

| Row | Sentence |
| --- | --- |
| Page PASS | "Each form field's and button's label says what it is for." |
| Page FAIL | "Some labels do not say what to enter or what the button does: <items>." |
| A1 | "This page has no form fields, so this test does not apply." |
| A2 | "No form field on this page has a label people can see, so there is no label to judge here (a missing label is reported by the label test)." |
| A2u | "The label test could not tell whether a form field on this page has a label people can see, so there may be a label to judge here. A person should look at it." ("N form fields ... have ... at them" for more than one) |

**Opened content is read like content at load** (fix 9b; Abby, 2026-11-09). Every state `reveal.py` opens is read with ANDI like the page as loaded, and when opened content holds sets of check boxes or radio buttons, up to two options of each (at most 3 sets) are chosen together with Space on a fresh load and the page is read again, because choosing can add controls (a filter that adds a remove button for each choice). Components found this way are tested like any other and say how they were reached.

**Guard RV: something that opens was not opened** (front matter `guards: reveal`; defined in [_template.md](_template.md); Abby, 2026-11-09, fix 9b). The menus, tabs, accordions and filters the keyboard walk found (a collapsed control, `aria-haspopup`, `aria-controls`, a tab that is not selected, a closed `<summary>`) are each opened on a fresh load (`reveal.py`, `Report.reveal`; at most 20, Enter first and a click when Enter showed nothing). When one was not opened (it showed nothing, could not be found again, failed to run, was over the limit or out of time) or what it opened could not be read, a page outcome of PASS becomes NEEDS REVIEW with the plain sentence "The page has menus or sections that open, and some could not be opened or read (...), so what is inside them was not checked." Trace row `RV`. FAIL and DOES NOT APPLY are unchanged: the guard only moves a would-be PASS toward review.

**Guard CN: form fields pass L could not read** (1.4.0; front matter `count:`; defined in [_template.md](_template.md); Abby, 2026-11-12; review D-01, H-08). The page's inventory (`count.py`, `Report.counts`) counts form fields inside web components (open shadow roots) and inside frames, form fields in the page but hidden when it loads (`display: none`, `hidden`, a closed `<details>`), and editable text areas (`contenteditable`). Pass L reads the page's own document and the web components inside it (1.10.0 for 5.A and 5.C, 1.7.0 for 5.B; plan 2026-11-12 part D: `fields.shadow` is the fields it read there, counted as the inventory counts them), and its frames, each opened as a page of its own on the replay and read the same way, ANDI included (1.11.0 for 5.A and 5.C, 1.8.0 for 5.B; Abby, 2026-11-14: ANDI inside an embedded frame is not accurate; TT 12.D "test in new tab"; `fields.frames` is the fields it read there), but no editable area, and a hidden field only when an opened section showed it (matched by its path; `labels.what_was_read`). When the inventory has more of any of these than pass L read, a page outcome of PASS or DOES NOT APPLY becomes NEEDS REVIEW with "This test could not be performed" and one plain sentence per gap ("2 form fields inside web components were not checked", "1 form field is hidden until something opens it, and was not checked"). Hidden fields count only when the page has something that could show them (a button, a disclosure, a same-page or script link, an inline click handler); on a page with none, a hidden field is hidden from everyone and holds nothing, as DHS's Baseline cases TC10.A-ic-dna-1 and -2 expect (Abby, 2026-11-12). A frame shown on the page whose page the recording does not have (its request failed while recording, or was never made) is `frames_missing`: "1 frame on this page was not recorded, so what is inside it was not checked" (Abby, 2026-11-14). Trace row `CN`. FAIL is unchanged. A hidden form behind a plain button, which the reveal pass does not open, therefore ends NEEDS REVIEW, not DOES NOT APPLY. Hidden fields nothing a careful tester does shows are hidden from everyone and not counted (1.9.0; Abby, 2026-11-15; the steps and limits are guard CN's in [_template.md](_template.md)).

## 4. Judgment questions

J1 is settled by looking (CLAUDE.md principle 8); the agent answers unsure whenever the evidence does not settle it.

### J1. Do these labels describe their fields and buttons?

**Question:** "input.items are the fields and buttons of one form, in page order, with the label people see for each (label), text near it (near), its group's label (group) and, for fields, a picture (image). Taken with what is around them, does each label make clear what to enter (including any format the field needs, such as a date) or what the button does? Answer all_descriptive, some_not_descriptive (put the numbers of the ones that are not in elements) or unsure."

**Input:** per form: items (number, kind, type, label, near, group, required, placeholder, image, and for a field labelled by icon buttons their number, `icon_buttons_beside_it`, 1.5.0; and for a field whose label 5.A found to be a picture, 5.A's description of it, `label_is_a_picture`, 1.10.0), and the form's headings and legends.

**Output:** `{choice: all_descriptive|some_not_descriptive|unsure, elements: [numbers], reasons}`.

**Rubric.** descriptive: names what to enter or do, even in one word ("First name", "Search" next to a search box, a magnifier icon on a search button, "Name" under a visible "Billing address" heading). not descriptive: unrelated or empty of meaning ("Menu", "Info", "The sky is blue", "Field 1"), the same label on several fields with nothing visible to tell them apart, a date or number field whose required format appears only in an error message. A placeholder is not a label. A button's words beside a field say what to enter only when they name it ("Search" beside a search box); words that say only what the button does ("Submit", "Send", "OK") do not (1.6.0). A field whose only label is the picture on a button beside it (`icon_buttons_beside_it`; look at the image): descriptive when the picture is a symbol commonly understood for what to enter (a magnifier on a search box, an envelope on an email field, a calendar on a date field); not descriptive when it is unrelated to the field or names something else (a flower or a company logo on a search box, a telephone on an email field) (1.5.0). A field with no words and `label_is_a_picture` (a picture the label test found near it; look at the image) is judged the same way: descriptive when the picture is a commonly understood symbol for what to enter, not descriptive when it is unrelated, unsure when the picture does not clearly belong to the field (1.10.0). The rubric's examples are on no fixture page (docs/solutions/judge-eval.md). unsure: whenever the picture or text does not settle it.

| Example | Answer |
| --- | --- |
| "First name:", "Date of birth:" (date field) | all_descriptive |
| "Menu" on a text field | some_not_descriptive, [1] |
| "Name", "Street" twice, section headings off screen | some_not_descriptive, all four |
| "The sky is blue" on a text field | some_not_descriptive, [1] |
| A search box whose only label is a flower on the button beside it | some_not_descriptive, [1] |
| A field with no words and `label_is_a_picture` "a magnifier icon to the left of the field" (image shows a magnifier) | all_descriptive |

**Use:** M1–M4.

## 5. Edge cases

| Case | Rule |
| --- | --- |
| A field labelled only by a placeholder, with no icon (round 1's nasa.gov search box) | Not an item (A2 when it is the only field: 5.A FAILs it by M3) |
| A search box in a panel a magnifier button opens, 5.A unsure (its picture showed the magnifier, not the field) | A2u: NEEDS REVIEW (1.10.0). When 5.A's J1 = graphic it is an item, judged by its picture, in a form of its own after the others |
| A field labelled by an adjacent button ("Go") | The button's text is its near text; J1 judges it |
| Icon-only button | Not an item itself: no visible text to judge, and pass L takes no picture of buttons (Abby, 2026-11-02). The field it sits beside, in one input group or search form, is an item judged by its picture (1.5.0) |
| A picture near a field but outside its form (a site logo) | Not the field's label: the field is not an item (5.A FAILs it, M3) |
| Fields revealed by interaction | Read where 4.F or 5.D revealed them (pass L) |

## 6. What a FAIL records

Each item named (its label, near text, kind, form) and the J1 answer with its reasons.
