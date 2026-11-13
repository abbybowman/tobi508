# Drafts for step 6b: K-01 and the five decisions (2026-11-13)

For Abby to read before anything is built. Part 1 (M-05, C-01, M-10, H-02,
M-08) is built and committed on `claude/cool-brown-4bbipr`. These six are
not. Answers are from [the decisions](2026-11-13-spec-decisions.md):
M-01 A, E-08 A, F-02 A (with a note for B), C-07 A, K-05 B.

What was read for each: the TT text (`tt.json`, read today), the current
spec rows and the code that decides them (read today). The W3C techniques
are cited from memory and not re-fetched today; the one marked "check" is
one I could not confirm from the repository. ACT and Baseline cases:
the ones named are the vendored ones the spec already cites.

**Two things to decide first** (marked ⚠ below):

1. **M-01 can turn a DOES NOT APPLY into a PASS**, not only into NEEDS
   REVIEW or FAIL: a form whose `type="button"` control, once pressed,
   shows a described error is a correct PASS under TT 5.F. Your rule says
   to stop and ask if a fix goes that way anywhere. The draft limits it
   as far as I can see how (below). Say yes or no.
2. **K-05 B can turn a PASS into a DOES NOT APPLY** when the unnamed pair
   is the only pair. I suggest NEEDS REVIEW for that case. Your call.

---

## K-01: the tested page again, with a query string (9.A, 9.B, 9.C, 19.A)

**Today.** Spec A2 sends an other page to NEEDS REVIEW when its recorded
document is byte-for-byte the tested page's. A server that changes the
page on every request (a timestamp, a token) gives different bytes, so
`page.html` against `page.html?x=1` passes 9.B and 9.C by comparing the
page with itself (review K-01, M-11; `v/site-a.html`).

**TT.** 9.A-9.C compare *other pages of the set* (9.B: "Identify
Content: ... the same navigation on the web pages"; page not checked). A page
against itself is not a set of pages. No TT text says how near is too
near, so the line below is ours and a NEEDS REVIEW, never a FAIL.

**Proposed rule (the draft).** An other page is a *near copy of the
tested page* when both hold:

1. Its final address is the tested page's apart from the query string
   (host, port, path equal after `same_address`'s normalising; at least
   one of the two has a query).
2. At least 90 % of the text keys of the two pages' units are shared:
   |A ∩ B| / |A ∪ B| ≥ 0.9, over the units `site.py` already reads
   (text, heading, control and image units with a non-empty text key;
   frames and the frame units apart). `NEAR_COPY = 0.9`.

A near copy is treated exactly as a byte-identical one is today: 9.A,
9.B, 9.C and 19.A are NEEDS REVIEW, not performed, naming the page and
the reason ("it is nearly the same page as the tested page, so comparing
them would compare the page with itself"). The byte-identical case stays
as it is (it is the 1.0 end of the same rule).

**Where.** One function in `site.py` (`near_copies(site, pages)`) beside
`kin`; `site_read` sets `identical` from it as well as from
`same_content_as_tested`; 9.C reads it from `site_read` instead of from
the byte flag only (it collects before the site read today, so its order
changes). Spec: A2 in 9.A, 9.B, 9.C, 19.A, a MINOR each (9.A 1.4.0, 9.B
1.4.0, 9.C 1.6.0, 19.A 1.6.0, or the next free numbers when I merge).

**Measurement (2026-11-13, Abby asked for it).** The share is |A ∩ B| /
|A ∪ B| over the units' text keys, as `site.read_page` reads them. Live
pages loaded in Chromium, waiting for the page's scripts, search by each
site's own search field (`svs.gsfc.nasa.gov/search?search=...`,
`www.nasa.gov/?search=...`):

| Pair | Share |
| --- | --- |
| svs: hubble / glacier / solar eclipse, each pair | 0.19, 0.20, 0.21 |
| svs: hubble against hubble with `&x=1` (same page) | 1.00 |
| svs: hubble against the home page | 0.05 |
| www: hubble / volcano / artemis moon crew, each pair | 0.41, 0.44, 0.42 |
| www: hubble against hubble with `&x=1` (same page) | 1.00 |
| www: search against `/missions/`, `/about/`; `/missions/` against `/about/` | 0.16, 0.18, 0.13 |

Whole-page and main-only shares agree. The highest pair that is not a
copy is 0.44; every copy is 1.00. So a bar anywhere from about 0.6 to
0.95 separates them on these pages; **0.9 stays**, as Abby proposed.
Two things the run showed that the draft must say:

- **What the tool's own recording sees is different.** The search
  results load by script, and a recording holds the page before them, so
  the recorded read of any search term is the empty shell: svs gave 1.00
  for different terms, and www's recorded documents are byte-for-byte the
  same for different terms (today's A2 already fires there). So two
  recorded search pages are near copies and NEEDS REVIEW. That is
  right: the tool cannot see what differs.
- **The case K-01 exists for is real.** svs served byte-different shells
  for the same page under two query strings (the byte rule did not catch
  it; the unit share, 1.00, does).

Scripts are in the session scratchpad only (live loads are a
measurement, not a test; no test fetches the network). Fixtures:
the review's `site-a.html` and `site-a.html?x=1` with a visible
timestamp (must be NEEDS REVIEW), and `a1-home` against `a2-benefits` on
the same address with different queries (must still compare).

**Direction.** PASS (and FAIL, 19.A) → NEEDS REVIEW. A real "page 2" of
a listing (`?page=2`, nearly the same chrome and different items) could
also be caught; that is a NEEDS REVIEW on a page the caller chose, and I
think the cost is right. Say if you want the address test to be only
"the same path" with no unit test (simpler, catches more).

**Decided (Abby, 2026-11-13):** 0.9, applies to 9.A-9.C and 19.A only.

---

## M-01: a form whose button is `type="button"` (5.F, 5.G; option A)

**Today** (5.F spec section 2, Submit control): only `button` without a
type or `type=submit`, `input type=submit|image` count. A form with
`<button type="button" onclick="validate()">` has no submit control; with
no button at all the tool presses Enter in the last text field, which
does nothing there; A3 says DOES NOT APPLY, "the page did not check for
errors".

**TT** (5.F, p. 28): "Attempt to submit the form and/or move to the
next page", with no limit on how the page's control is built. Applicability
is DNA "if the form element does not have automatic error detection".
A form that checks in script *has* detection. The Baseline TC10.D
cases are the vendored ones (TC10.D-ic-dna-1 is a form with no detection
at all, which stays DNA).

**Draft change to the Submit control paragraph.** The form's buttons are
its submit buttons as now **and** (1.7.0) every visible `button`,
`input type=button` and `[role=button]` inside the form or, for fields
with no form owner, after the group's last field as now. `SKIP_WORDS` as
now. Choice as now: first `SUBMIT_WORDS` match, else the first. J0 can
name another (as now).

**Draft change to A3.** DOES NOT APPLY requires that the control pressed
was a real send control: a submit button, or Enter in a form with one
text field (implicit submission). A form whose pressed control could not
have sent it (no submit button, more than one field) with no error
indicator is **NEEDS REVIEW, never DOES NOT APPLY**, with the sentence
"We pressed <button>, but it may not be the one that sends this form;
please check how the form reports errors." Same for 5.G (A1 reads 5.F's
section 1).

**Decided (Abby, 2026-11-13): DNA → PASS is fine when appropriate.** Direction: DNA → NEEDS REVIEW or FAIL in most pages. DNA → PASS
only if the pressed control is a `type=button` that really runs the
page's check and the error that appears is identified and described in
text (rows M2/M6 with J1 "described", as for any form). Pressing a
control that is not the send control and showing nothing gives
NEEDS REVIEW (the A3 change), never PASS or DNA. If you do not want any
DNA → PASS, I would keep the new buttons for pressing but make a form
that has no submit-type button NEEDS REVIEW at best (an extra clause in
G3), which is your option B with the pressing kept. Not needed: Abby chose the first.

**Fixtures.** `5f/f26`: `type=button` + `validate()` with an inline error
(PASS with J1 described, or NEEDS REVIEW under the stricter clause);
`5f/f27`: the nearest page that must not become a PASS: a `type=button`
"Add another" row button that shows nothing (NEEDS REVIEW); and the old
form with no detection at all still DNA (an existing fixture covers it).

---

## E-08: a native button that answers only `mousedown` (4.A; option A)

**Today.** A native control is "functional by definition" and never
pressed (Execute check). A `<button>` whose only handler is `onmousedown`
does nothing on Enter or Space, and 4.A says PASS.

**TT** (4.A, p. 19 HtT 2): "access (e.g., tab to) the element and
execute (e.g., press Enter with focus on the element)". W3C: WCAG
failure F54 ("using only pointer-specific event handlers", `onmousedown`,
`onmouseup`; Understanding 2.1.1). ACT: "Element with a pointer-only
listener is keyboard accessible" is not a vendored rule here (check:
`tests/fixtures/act/manifest.json` has no case for it).

**Draft.** Add to the pointer scan's marks: a *pointer-only native
control* is a native control (not a plain link with an address, whose
Enter follows the address) with a `mousedown`, `mouseup`, `pointerdown`
or `pointerup` listener of its own and no `click` listener of its own.
It is a stop that gets the Execute check (Enter, then Space, then a
click on a fresh replay), with rows as for custom controls: M8 (a key
has an effect) PASS; M10 (the click has an effect and neither key does)
FAIL; M9 (nothing has an effect) no instance. A `click` listener added
on an ancestor (delegation) works from the keyboard too, so Enter has the
effect and the control passes M8. Spec 4.A 1.10.0 (Terms: *pointer-only
native control*; section 2, Execute check; row notes).

**Your risk, stated.** A control with a mouse-down ripple (a DOM change)
and a click handler registered some other way that Enter does reach
passes M8; one whose click is simply the ripple and does nothing real
reads as "the click has an effect, keys do not" and FAILs. That is the
false FAIL you said you would take; the fixture records it.

**Fixtures.** `4a/f26`: `<button onmousedown>` that shows a message (FAIL,
M10); `4a/f27`: `<button onmousedown>` plus `onclick` (PASS, M8; the
nearest case that must not FAIL); `4a/f28`: a link with a `mousedown`
tracking listener and an `href` (PASS: Enter follows it).

**Direction.** PASS → FAIL; no case moves the other way.

---

## F-02: a page that shifts as focus moves (4.D; option A)

**Today.** Row M6 passes on "a style signal and at least
`MIN_CHANGED_PX` of changed pixels", and "the element's box moved" is a
style signal (`e["moved"]`, `t4d.py` around line 934; meant for skip
links that appear on focus). When something shifts the page between the
two pictures, every element "moved" and a link with `outline: none`
passes.

**TT** (4.D, p. 22): "a visible indication of focus on the element".
W3C: Understanding 2.4.7; failure F78 ("styling that removes the focus
outline"); technique G149/C15. ACT: `oj04fd` ("Element in sequential
focus order has visible focus"), already cited by M6; DHS scored none of
this case.

**Draft (1.7.0).** In the style signal, "moved" counts only when the
element is *shown only on focus*: its unfocused box is empty, hidden or
off screen (a skip link). Any other moved element is read by pixels
alone: with at least `MIN_CHANGED_PX` changed pixels and no other
signal, it is not M6; it falls to M4, "no clear view" (the page moved
under the pictures), NEEDS REVIEW with the existing sentence ("it moved
on the page while we took the pictures"). M7/J1 is unchanged for the
ordinary case where nothing moved.

**Note for B (as you asked).** "If many pages settle late and end at
this NEEDS REVIEW, build B: take the two pictures once more after the
page settles before giving up." The note goes into the spec's 4.D
section as an *Open* line, and into `docs/ROADMAP.md` "Known limits" with
the trigger: more than 1 in 5 of round 2's 4.D stops ending at M4 for
this reason (step 6's figures give the rate; the number is mine, change
it).

**Fixtures.** `4d/f..`: a page whose banner loads late and shifts
everything, with a link with `outline: none` (NEEDS REVIEW; PASS
before); the nearest case that must still PASS: a skip link that is
off screen until focus (M6 through "shown only on focus").

**Direction.** PASS → NEEDS REVIEW (or FAIL where J1 says no on a stop
that did not move).

---

## C-07: an element a script moves focus off at once (4.D; option A)

**Today.** When a script moves focus away as it arrives, that element
is never a stop of the walk. 4.D checks the others and says PASS "each of
the 10 elements we could reach" on a page with 11. Row M3 (focus dropped
on focus, WCAG failure F55, Abby 2026-10-31) only fires for an element
the walk did reach.

**TT** (4.D "Continue from Test 4.C" and Identify Content: "all interface
components"). W3C: F55 ("using script to remove focus when focus is
received"; fails 2.1.1, 2.4.7, 3.2.1). That failure is a FAIL for the
element itself; I propose only NEEDS REVIEW here because the tool cannot
tell this case from an element the walk simply did not reach for another
reason.

**Draft (1.7.0, as 4.F's guard).** A new guard row after the stop count:
when the count of focusable elements (guard CN's inventory,
`count.py`) is larger than the stops 4.D checked, a page outcome of PASS
becomes NEEDS REVIEW, "This test could not be performed", with one plain
sentence: "The page has 11 elements that take focus; 4.D checked 10. A
person should check the other one: a script may move focus off it at
once." Same wording shape as 4.F's `focusable@dna` row. Front matter
`count:` gets `focusable` (4.D currently lists none). FAIL unchanged.

**Fixtures.** `4d/f..`: 11 focusable links, one whose `onfocus` calls
`blur()` or focuses another (NEEDS REVIEW; PASS before). The nearest case
that must still PASS: 11 links, all reached (PASS).

**Direction.** PASS → NEEDS REVIEW.

---

## K-05: a pair of controls with no name on either page (9.C; option B)

**Today.** Row C1 is "names agree": two empty names agree, so a pair of
unnamed icon buttons passes, and the summary says they "have the same
names for screen reader users".

**TT** (9.C): "The accessible name and description is
consistent for components that perform the same function." An unnamed
control has no name to be consistent; naming is 5.C's (and the name
tests'): 5.C row M3 FAILs "no name at all".

**Draft (9.C 1.6.0).** A pair in which both names are empty is not
compared: it is left out of 9.C with a note ("N pairs of controls have
no name on either page; 5.C reports them. They are not compared here").
9.C's outcome comes from the other pairs; with none, DOES NOT APPLY.

⚠ **Direction.** PASS → PASS (other pairs agree) in most pages;
PASS → DOES NOT APPLY when the unnamed pair is the only pair. A DNA says
"no such components", which is not true of the page: there are
components, and they were not compared. **I suggest NEEDS REVIEW for
that case only** ("the only controls shared between the pages have no
name, so nothing could be compared"), still never PASS. **Decided (Abby, 2026-11-13): B with this NEEDS REVIEW.**

**Fixtures.** `9x/` the review's `un-a` and `un-b` (the pair alone:
NEEDS REVIEW or DNA by your answer); the same pages with one named pair
beside them that agree (PASS); and one that disagrees (FAIL, row C4,
unchanged).
