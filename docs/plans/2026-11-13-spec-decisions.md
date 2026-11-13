# Spec decisions for the README's known wrong outcomes (2026-11-13)

For Abby to answer. Each item below is one row of the README's "Known
wrong outcomes" table that one test's spec can fix, with one fixture.
All were run again on 2026-11-13 and still give the outcome shown. The
fix thread is step 6b of [the roadmap](../ROADMAP.md); it builds part 1
without waiting and part 2 as each answer arrives.

The evidence and the "smallest fix" for each come from
[the code review](../reviews/2026-11-11-code-review.md) (find the item
by its ID). The recommendations are the review's, read against the
spec; the W3C and ACT research CLAUDE.md asks for is done by the thread
in each spec draft, which Abby reviews before it is built.

Every change here moves a PASS or a DOES NOT APPLY toward NEEDS REVIEW
or FAIL. None turns a NEEDS REVIEW into a PASS.

## Part 1: no decision needed

The spec already says the right thing, or the fix is in how the page is
read. The thread fixes these; Abby sees any spec wording in the pull
request.

| Item | Test | Today | Fix |
| --- | --- | --- | --- |
| M-05 | 5.F (5.G and 5.H read the same pass) | PASS on a form after a keyboard trap | A walk that ends in a trap is not complete, as the spec says and as 5.D now does |
| C-01 | 4.A | PASS when a mouse-only control's only effect is `alert()`, `confirm()` or a download | The observer records a dialog or a download as an effect |
| M-10 | 9.A | PASS for a do-nothing button when the tested address ends in `#main` | The address's target counts only if the press changed it |
| H-02 | 5.C (and 5.A's option row) | PASS for a field whose visible label is not in Latin letters | Split words in any script; a label that yields no words never passes M5 |
| M-08 | 5.H | PASS for a multi-step form whose next step says "required" (read, not run) | "Still on the form" needs the same fields to be visible, as the spec says |
| K-01 | 9.A-9.C | PASS when the tested page is given again with a query string and the server changes the page on every request | Open: the review fixed the byte-identical case only. The thread proposes a rule (for example, the same address apart from its query string and nearly the same content is NEEDS REVIEW) and shows it to Abby first |

## Part 2: decisions

Write the answer on the "Abby:" line (a letter is enough), or say it in
a thread.

### 1. M-01: a form whose button is `type="button"` (5.F, 5.G)

- **Today:** only a submit-type button counts as the control that sends
  a form. A form checked by script with
  `<button type="button" onclick="validate()">` is never pressed, and
  5.F and 5.G say DOES NOT APPLY, "the page did not check the form for
  errors".
- **Why it matters:** a very common way to build a form.
- **Options:**
  - **A (recommended):** offer every visible button inside the form as
    the control to press, submit words first. A form whose press could
    not have sent it (no submit button, more than one field) is NEEDS
    REVIEW, never DOES NOT APPLY.
  - **B:** only the second half: such a form is NEEDS REVIEW, and no
    other button is pressed.
- **Risk of A:** pressing a button that is not the send button ("Clear",
  "Add another") and reading what it does as the form's answer. The
  open question that lets the judge name the right button already
  exists; A lets it be asked.
- **Abby:**

### 2. E-08: a button that answers only `mousedown` (4.A)

- **Today:** a native button or link is reached by Tab, so 4.A never
  presses it. One that acts on `mousedown` or `pointerdown` alone does
  nothing on Enter or Space, and 4.A says PASS. This is WCAG failure
  F54.
- **Options:**
  - **A (recommended):** a native stop with a mouse-down or
    pointer-down listener and no click listener gets the Enter and
    Space check the mouse-only candidates get: FAIL when the keys do
    nothing and the mouse does something, PASS when they do the same.
  - **B:** such a stop is NEEDS REVIEW, with no key press.
- **Risk of A:** a control with both a mouse-down effect (a ripple) and
  a real click handler added another way; the "no click listener"
  condition is meant to keep those out, and the fixture of the near
  case covers it.
- **Abby:**

### 3. F-02: a page that shifts as focus moves (4.D)

- **Today:** 4.D compares a picture of each element with and without
  focus. The element's box having moved counts as a sign of a focus
  style (meant for skip links that appear on focus). When anything
  shifts the page between the two pictures, every element "moved", and
  a link with `outline: none` passes.
- **Options:**
  - **A (recommended):** a move counts only when the element is shown
    only on focus (its unfocused box is empty, hidden or off screen).
    Any other moved element with changed pixels is "no clear view":
    NEEDS REVIEW.
  - **B:** as A, and take the two pictures again once after the page
    settles before giving up, so fewer elements end at NEEDS REVIEW.
- **Risk:** more NEEDS REVIEW in 4.D on pages with late banners. Step 6's
  figures show how often an element moves on round 2's pages; B is
  worth its time only if that is often.
- **Abby:**

### 4. C-07: an element a script moves focus off at once (4.D)

- **Today:** when a script moves focus away the moment it arrives, that
  element is never a stop. 4.D checks the others and says PASS, "each
  of the 10 elements we could reach" on a page with 11.
- **Options:**
  - **A (recommended):** when the count of focusable elements (guard
    CN's inventory) is larger than the stops 4.D checked, 4.D is NEEDS
    REVIEW and names how many were not checked. 4.F already does this.
  - **B:** leave 4.D, and treat it as 4.C or 4.E's matter (focus that
    cannot rest is a focus-order or on-focus problem, not a missing
    indicator).
- **Abby:**

### 5. K-05: a pair of controls with no name on either page (9.C)

- **Today:** row C1 is "names agree". Two controls with no name at all
  agree, so a pair of unnamed icon buttons is a PASS, and the summary
  says they "have the same names for screen reader users".
- **The question:** is an unnamed pair a 9.C matter, or only 4.1.2's
  (TT 5.C and the name tests)?
- **Options:**
  - **A (recommended):** a row before C1: both names empty is NEEDS
    REVIEW, with a sentence that the controls have no name to compare.
  - **B:** the pair is left out of 9.C with a note, and 9.C's outcome
    comes from the other pairs (DOES NOT APPLY if there are none).
  - **C:** FAIL, since an unnamed control is not identified at all.
- **Abby:**

## Not here

Decisions from the review that are not rows of the README table stay in
the roadmap's "Decisions waiting for Abby": a form behind a plain
button (H-08), a title as a control's only label (E-13),
`aria-controls` as a field's own widget (H-04), and 4.F's "order does
not matter". The rows that wait for larger work are not single-test
fixes: web components and frames (step 8), the 6.5-second watch (the
paused clock), and the word lists (meaning goes to the judge).
