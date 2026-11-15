# Known limits, per test

What each built test cannot do today, beyond the wrong outcomes the
README lists ("Known wrong outcomes"). Moved out of `docs/ROADMAP.md`
on 2026-11-14; a fix removes its line here in the same commit.

**Not every limit is NEEDS REVIEW-safe today.** The code review's P0
table lists 30 cases that give PASS or DOES NOT APPLY, each with a page
that shows it; the ones that are a stated limit are marked below. Until
parts A to D land, a PASS or a DOES NOT APPLY means "in what the tool
looked at". Browser checks still to run (mostly Windows headed Chrome)
are in [specs/rules/_browser-checks.md](../specs/rules/_browser-checks.md).

- **4.D, a page that shifts as focus moves (F-02, 4.D 1.8.0):** a link
  whose only sign of a focus style is that its box moved is NEEDS REVIEW,
  not PASS, unless it is shown only on focus (a skip link). If many pages
  that settle late end there (more than 1 in 5 of a round's 4.D stops),
  build option B: take the two pictures again once after the page
  settles (Abby, 2026-11-13).
- **Radio groups (4.A-4.F, step 6d):** a radio group is one element that
  takes focus, since Tab lands on one radio of it. The walk does not visit
  the radios of a group one by one (arrow keys are not walked), so what
  the other radios look like on focus is not read. 4.A must not ask about
  a radio Tab cannot land on: today it asks whether a group's second
  radio "works with a mouse but cannot be reached", which Tab never
  could.
- **Web components (shadow roots):** the keyboard walk enters them; the
  label pass, the site read, the media read, 4.A's handler scan and
  5.F's error read do not. Since part B's inventory and guard CN
  (2026-11-12), a form, navigation or sound inside one is NEEDS REVIEW
  in 5.A-5.H, 9.A-9.C and 2.A, not DOES NOT APPLY (D-01, K-02, M-12,
  N-01). Still open: 4.A can PASS with a mouse-only control inside one
  (D-03), 5.F and 5.G miss an error shown in one (M-06), and 19.A fails
  a page whose shared header is one (K-02; a guard never moves a FAIL;
  accepted until part D, Abby 2026-11-12). Part D reads them.
- **Content that opens:** a form behind a button with no ARIA marker is
  never opened; since guard CN its hidden fields make 5.A-5.H NEEDS
  REVIEW, not DOES NOT APPLY (H-08, M-07), and so does an editable text
  area (`contenteditable`). Then "Opening everything". (A menu whose
  trigger is `<a href="#">` is read now: C-03, fixed.)
- **Guard CN matches hidden fields by their place in the page:** a page
  that rebuilds its elements when a section opens can make a field that
  was read look unread, so a test is NEEDS REVIEW when it need not be
  (never PASS). Accepted until part D's shared reader gives elements a
  stable identity (Abby, 2026-11-12).
- **The watch is 6.5 seconds:** what starts later is DOES NOT APPLY in
  2.A, 2.B and 3.A (2.C says NEEDS REVIEW); a blink 2.5 times a second
  can be missed; flashing below the first screen and an animated image
  past the 30th are not measured (N-02 to N-09, W-02, W-09); an
  animated image past the 30th now makes 2.B and 3.A NEEDS REVIEW
  (N-06, guard CN). Parts C and J.
- **2.C's clock check (2.C 1.2.0, 2.D 1.3.0)** clears a timer longer
  than the watch only when one more load sets it again, runs the page's
  clock past it, and sees nothing change: the screen in five
  screenshots, the text, the elements, the image sources, a count of
  every change to the page and what is playing. It sees only the first
  screen in its screenshots (elements and text are read for the whole
  page); a page with a canvas keeps the timer as a sign; a timer longer
  than a day, or one that asks the server for data, keeps the page NEEDS
  REVIEW.
- **A walk that stops at a trap, or runs out of time,** can still PASS
  in 5.D, 5.F and 4.C (H-03, M-05, E-07). Parts A and C.

- **Real government pages:** calibrate 4.A's `HOVER_MAX`, `CLICK_MAX`
  and `EXECUTE_MAX` and 5.D's `FIELD_MAX` (40) and `FIELD_SECONDS`
  (1.1 s); how often nearby text sends a 5.A/5.C field to J1; 5.H's
  consequence words and the error words for "checked" (known over-match:
  "order" in "tab order" or "in order to"; narrowing is a MINOR change);
  9.B's region match and 9.C's same-place pairing; 19.A's site search on
  real .gov sites.
- **Dialogs that open on some loads only:** the walk confirms a trap on a
  second load ([solutions/trap-seen-once.md](solutions/trap-seen-once.md)),
  but a check's own replay can still meet such a dialog. A check that
  verifies where focus arrived goes to NEEDS REVIEW; one that does not
  may read the dialog. Not measured.
- **4.A:** controls inside content that opens only on click or Enter are
  not scanned (phase 2 above). Handlers delegated to an ancestor are not
  tied to the child they serve.
- **4.B:** timing the page does not describe in words is not found; the
  timing words are English only, and no match is PASS, so a page in
  another language passes (M-03, E-09; part E).
- **4.C:** a late-refocus fixture (refocus 600 ms after blur, no DOM
  change) once the xfail in `tests/test_traverse.py` is settled; traps
  past the cap of 60 stops have no budget of their own.
- **4.D and 4.F:** run 4.C's f19 (cross-origin frame), f24 (open shadow
  root) and f32 (two traps) for 4.D, and f32 for 4.F.
- **4.D, focus dropped on focus inside a web component or a frame:** a
  control that blurs itself as it gets focus is M3 (FAIL) on a plain page
  (`4d/f11`), but inside a web component or a frame the walk never reaches
  it, so 4.D is NEEDS REVIEW there (row WK; found in step 8, 2026-11-15).
  Safe, not a decided FAIL.
- **The walk on a page with a frame from another site, on a slow CI
  runner:** once (PR #64's CI, 2026-11-15) the walk on the grid's
  `frame-other` page reached all 7 stops but never saw focus wrap back to
  the first within its press limit (50 presses), so 4.C-4.F and 5.D were
  NEEDS REVIEW (an incomplete walk, step 6d) and the grid failed; the rerun
  passed. Not reproduced here: 12 runs of 4.C on that page under heavy CPU
  load all ended normally (2026-11-15). Safe (NEEDS REVIEW), not wrong. If
  it recurs, keep the failing run's `steps.jsonl` to see the stop keys
  after the last stop (`traverse.detect_p1_end` needs OUT, then the first
  stop's key).
- **5.A-5.C, 5.F-5.H:** read fields inside web components and frames
  since step 8 (5.A 1.11.0, 5.C 1.11.0, 5.F 1.10.0); a frame the recording
  lacks holds PASS and DOES NOT APPLY (`frames_missing`). Found in step
  8: a `role="alert"` added together with its error text is not counted as
  a notice (M7 FAIL), though 5.F's Terms say "present before the attempt
  or added with the text"; the same on a plain page, so not new. For Abby. 5.F and 5.G leave `time`,
  `datetime-local`, `month` and `week` fields as loaded in attempt 2.
- **5.F, 5.G, 5.H:** a form that is only a button is not seen (M-02);
  5.H's consequence words are English only, and no match is DOES NOT
  APPLY (M-03). Error handling done on the server cannot be replayed
  from a recording: 5.F answers NEEDS REVIEW when a form is sent, and
  that stays.
- **5.B:** icon-only buttons are left out (pass L has no picture of
  buttons); a field whose only label is an icon button beside it is
  judged by that picture, and a field whose only cue is its own button's
  words by those words (fix 8b).
- **5.D:** after a retry, a submission that navigates away reads as
  navigation (both M4; only the wording differs). A jump forward past a
  field after Tab-away is not detected.
- **9.x:** rows no fixture triggers (9.A M2, M6 and the 8-candidate cap;
  9.B N1, N5; 9.C C2, C5; a page or ANDI that cannot be read, end to
  end; an other page that redirects off the host). Add fixtures for
  whatever real templates show.
- **2.A-2.D:** a working mechanism is NEEDS REVIEW (E3), never PASS,
  until ER 3's shortlist is built (6.A, 7.A, 7.E, 12.D, 13.A, 13.B, 13.C,
  18.A). 2.C J1's wording when the mechanism is page text naming a key.
  Real YouTube and Vimeo embeds are NEEDS REVIEW in 2.A (A2), 2.B (A1)
  and 3.A.
- **3.A:** CSS background animated images are not decoded (only `<img>`);
  H.264 video cannot be decoded in Chromium (NEEDS REVIEW). No held-out
  pages with flashing exist. Optional: the IRIS cross-check
  ([research](research/2026-11-03-3a-flashing.md), section 7).
- **Recordings:** a page that loads code only when used may lack it in
  the recording; guard GU then holds a PASS at NEEDS REVIEW
  ([solutions/recordings-miss-lazy-scripts.md](solutions/recordings-miss-lazy-scripts.md)).
- **Browsers:** results are for the Chromium the report records. Firefox
  needs its own focus reader (no CDP) and every fixture rerun; not
  planned.

