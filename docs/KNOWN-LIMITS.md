# Known limits, per test

What each built test cannot do today. The limits that give a PASS or a
DOES NOT APPLY a tester would not are also in the README's "Known wrong
outcomes" table, each with a page that shows it. Everything else here
is NEEDS REVIEW-safe unless it says otherwise. Browser checks still to
run (mostly Windows headed Chrome) are in
[specs/rules/_browser-checks.md](../specs/rules/_browser-checks.md).

A fix removes its line in the same commit. The README's table of
wrong PASS and DOES NOT APPLY outcomes is a short list of the lines
below; fix them there too. When a line was found, and
by which step, is a note at its end, not a heading. Lines marked
**⚑ Check** may be out of date (reorganised 2026-11-17 without
re-testing): confirm and remove, or remove the mark.

## Every test

- **Recordings and replays.**
  - A page that loads code only when it is used may lack it in the
    recording; guard GU then holds a PASS at NEEDS REVIEW
    ([solutions](solutions/recordings-miss-lazy-scripts.md)). The chunk
    store saves such code (the freeze runs it too) up to 10 MB a file, 24
    MB and 300 files a page, 5 levels deep; more stays unrecorded. Round
    3's community pages need about 163 files, two of 6.9 MB and 5.6 MB,
    which the limits before step 25 ([#134](https://github.com/abbybowman/tobi508/issues/134))
    refused, so guard GU held 4.B and 5.D there. Round 3's own freeze
    still lacks them; the rerun uses a copy with them added
    (`evals/judging/gate-2026-11-20-134/`).
  - A frame whose address changes on every load (reCAPTCHA, a lazy
    video embed, an OpenID Connect sign-in frame) is not in a frozen
    copy: its replay asks for an address the recording never saw and is
    aborted. The freeze lists such frames in `freeze.json`
    (`frames_not_recorded`, step 10a). On round 3's community pages the
    app may leave the page when its sign-in frame is missing (not shown
    in the reports).
  - An application that serves the same HTML at every address: since
    step 26 ([#134](https://github.com/abbybowman/tobi508/issues/134)) an
    identical document is the tested page again only at the tested
    page's host and path apart from the query string, so 9.A to 9.C and
    19.A compare such pages once drawn. The cost: 19.A no longer verifies
    an `index.html` alias by its document (round 2's CILab serves
    `/cilab/index.html` as the same file as `/cilab/`, no redirect, key
    Pass), so such a page can be NEEDS REVIEW where a person passes it.
  - A page whose script fails on load shows what a visitor sees, but
    the report does not say so: page script errors are not recorded as
    a note. Round 1's "Was this page helpful?" popup never opens, live
    or recorded ("jQuery is not defined"), except on a replay of a
    heavily loaded machine, where it opened on two pages and changed
    4.C, 4.E, 4.F and 5.D there. Reruns that score a round run one round
    at a time.
  - A stuck page load can run past its time limit. An other page's media
    download once ran 342 s past a 20 s limit (step 6h); that cause is
    gone (other pages no longer record media), the general one is not.
- **Pages drawn after load.** Every load waits until the count of
  elements that take focus has not changed for 2 s (at most 10 s;
  step 23, 4.C 1.17.0), so a page drawn about a second after load is
  read as drawn (round 3's applications, 0.7 to 1.1 s on replay). The
  first load of each address costs 2 s more. When the page more than
  doubled its elements after the walk began (or had no form field and
  then had some), the tests that read the walk decide nothing (row WL,
  step 22: 4.A, 4.C, 4.F, 5.A to 5.D, 5.F). A page still drawing itself
  when the 10 s wait ends (its count changed in the wait's last 2 s) is
  now caught: 4.A, 4.C, 4.F, 5.A to 5.C and 5.F cannot PASS or say DOES
  NOT APPLY on it (guard WL, #134; fixture `walk/drawn-after-wait.html`,
  controls drawn at 11 s: before, 4.A and 4.C PASS and 5.A to 5.F DOES
  NOT APPLY). **Still open:** 5.D does not take the guard yet (#135 and
  #137 hold its spec), nor 4.D, 4.E, 5.G and 5.H. A page whose count
  does not change for its first 2 s and that draws only after the walk's
  recount (at least 3 s after load, later on a long walk) ends the wait
  early and is read as it stood: no guard sees it.
- **Web components and frames** are read by every reader and decided
  on the same rows (step 8). Not read: a closed shadow root, and a
  frame the recording lacks (PASS and DOES NOT APPLY are held,
  `frames_missing`). A frame's fields are pictured with the frame
  opened alone, so the judge does not see text beside the frame on the
  page (round 2: 5.A and 5.B; step 37, [#137](https://github.com/abbybowman/tobi508/issues/137)).
- **Content that opens.** Menus, tabs, accordions and filters are opened
  on a fresh load (`reveal.py`; guards RV and RC), and 4.C and 4.E walk
  what opened (`opened.py`, step 6g). Not opened: a form behind a button
  with no ARIA marker (H-08; its hidden fields keep 5.A to 5.H at NEEDS
  REVIEW through guard CN, and so does an editable text area). 4.A and
  4.C to 4.F do not see the controls inside such a form, so on a page
  whose only form opens from a plain button they can PASS (read, not
  run). 4.D, 5.D and 4.A do not walk or scan opened content yet
  (step 15; 4.D and 5.D in [#135](https://github.com/abbybowman/tobi508/issues/135)).
- **Guard CN matches hidden fields by their place in the page:** a page
  that rebuilds its elements when a section opens can make a field that
  was read look unread, so a test is NEEDS REVIEW when it need not be.
  Abby accepted it on 2026-11-12 "until part D's shared reader gives
  elements a stable identity". **⚑ Check:** part D (step 8) is built;
  whether it gave elements a stable identity is not recorded.
- **Fields hidden from everyone (guard CN; 5.A to 5.H).** Only a hidden
  part of a form shown on load can be out of scope, and only when
  nothing a careful tester does shows it (the reveal pass, every opener
  pressed, a 15 s watch and a scroll, a choice and typing sweep, then
  its buttons pressed with values typed). A field whose whole form is
  hidden on load (a popup, a panel, a mobile copy) stays counted.
  Accepted, each a rare wrong DOES NOT APPLY or PASS: a field shown only
  by typing a particular value, by hovering, after more than 15 s, or by
  leaving the page. The check adds about 17 s a page with hidden fields;
  nothing is decided when the reveal pass did not run, left a trigger
  unopened, or the page has more than 40 openers. Waiting: a mobile copy
  out of scope, by a positive test (a form hidden at the tested window
  and shown on load at a phone-width window). Abby, 2026-11-15.
- **Dialogs that open on some loads only:** the walk confirms a trap on
  a second load ([solutions](solutions/trap-seen-once.md)), but a
  check's own replay can still meet such a dialog. A check that
  verifies where focus arrived goes to NEEDS REVIEW; one that does not
  may read the dialog. Not measured.
- **Words in English only:** 4.B's timing words and 5.H's consequence
  words. No match is PASS in 4.B and DOES NOT APPLY in 5.H, so a page in
  another language can pass (M-03, E-09; step 16). 4.B matches "press
  twice" but not "press Enter twice". Known over-match in
  5.H and the "checked" words: "order" in "tab order" or "in order to".
- **Browsers:** results are for the Chromium the report records.
  Firefox needs its own focus reader (no CDP) and every fixture rerun;
  not planned. CI runs headless Chromium; headed Chrome on Windows is
  checked by hand.
- **A recording freezes network responses, not randomness or time.**
- **The test browser bypasses the page's Content-Security-Policy** so
  that ANDI can run (`BYPASS_CSP`, on by default; the report records it).

## 2.A to 2.D and 3.A: what plays, moves and flashes

- **The watch is 6.5 s.** What starts later is DOES NOT APPLY in 2.A,
  2.B and 3.A (2.C says NEEDS REVIEW); a blink 2.5 times a second can be
  missed; flashing below the first screen that is not an image is not
  measured (N-02 to N-09, W-02, W-09; part J).
- **2.B misses two kinds of motion:** text that blinks by `visibility`
  is filed as updating, never as moving (N-03); and a pair of frames in
  which more than half the screen changed is set aside as a page-wide
  change, so motion that fills most of the screen is not seen (W-07).
  Both give DOES NOT APPLY.
- **2.C's scrolled watch scrolls to the first element only,** so a
  counter that starts when the second of several elements scrolls into
  view gives DOES NOT APPLY (N-07).
- **Images** (2.B 1.5.0, 3.A 1.4.0): up to 300 per page are read, lazy
  ones after a scroll. One the recording lacks, an animated one only the
  scroll found, or one whose frames at the size shown exceed 100 MB
  keeps 2.B and 3.A at NEEDS REVIEW (guard CN or 3.A's A3).
- **2.C's clock check** (2.C 1.2.0, 2.D 1.3.0) clears a timer longer
  than the watch only when one more load sets it again, runs the page's
  clock past it and sees nothing change (five screenshots of the first
  screen, the whole page's text, elements and image sources, a count of
  every change, what is playing). A page with a canvas keeps the timer
  as a sign; a timer longer than a day, or one that asks the server for
  data, keeps the page NEEDS REVIEW.
- **A working mechanism** (a pause button, a key) is NEEDS REVIEW (E3),
  never PASS, until ER 3's shortlist is built (6.A, 7.A, 7.E, 12.D,
  13.A, 13.B, 13.C, 18.A). 2.C J1's wording when the mechanism is page
  text naming a key.
- **Real YouTube and Vimeo embeds** are NEEDS REVIEW in 2.A (A2), 2.B
  (A1) and 3.A. 2.A: audio that does not play from the recording is
  NEEDS REVIEW.
- **3.A:** CSS background animated images are not decoded (only
  `<img>`); H.264 video cannot be decoded in Chromium (NEEDS REVIEW).
  The screencast net varies between runs on some pages (round 2's 5340:
  DOES NOT APPLY in two runs, NEEDS REVIEW in others; the key says Does
  Not Apply). No held-out pages with flashing exist. Optional: the IRIS
  cross-check ([research](research/2026-11-03-3a-flashing.md),
  section 7).

## 4.A to 4.F: keyboard and focus

- **4.C, error states:** a form that sends to the server and gets a new
  page back (its answer, perhaps with the error) is never walked: the
  recording does not hold the answer, since the tool never sends a form
  to the live site, so a trap there is not found; that page is tested as
  a page of its own. An application that draws its results or error at
  another address without loading a page is walked from there (step
  35e, [#134](https://github.com/abbybowman/tobi508/issues/134)).
- **Radio groups:** a group is one element that takes focus, since Tab
  lands on one radio of it; the walk does not visit a group's radios
  one by one (arrow keys are not walked), so how the others look on
  focus is not read (step 6d). **⚑ Check:** this line also said 4.A
  asks whether a group's second radio "works with a mouse but cannot be
  reached"; step 6d's radio fix (PR #59) may have ended that.
- **4.A:** native buttons are never executed, so a page that takes
  Enter only from a native button is not seen; handlers delegated to an
  ancestor are not tied to the child they serve; controls inside content
  that opens are not scanned (step 15). J1 can answer "alternative"
  while its reasons say it is not sure, and M8 passes any effect of
  Enter or Space, even one that is not what the click does (round 3's
  MySearchStory; step 28, [#136](https://github.com/abbybowman/tobi508/issues/136)). Every Drupal page of round 3 was NEEDS
  REVIEW for a hidden share frame, a page-level wheel or touch listener
  and `HOVER_MAX` (40) (step 32, [#136](https://github.com/abbybowman/tobi508/issues/136)). Its caps (`HOVER_MAX`, `CLICK_MAX`,
  `EXECUTE_MAX`) are not calibrated on real pages. A page with embedded
  players or frames is often NEEDS REVIEW.
- **4.C:** traps past the cap of 60 stops have no budget of their own.
  A page whose controls a frame from another site holds can leave the
  walk short of its press limit on a slow machine (the grid's
  `frame-other` page in CI, once; 12 runs under load ended normally):
  NEEDS REVIEW, not wrong. A menu whose controls the Tab key does not
  reach, or that could not be opened, is NEEDS REVIEW (as in 4.E and
  5.D).
- **4.D:** `MIN_CHANGED_PX` is absolute, so about 50 changed pixels pass
  a large image link (round 3's blog; held only by guard RC; step 27, [#135](https://github.com/abbybowman/tobi508/issues/135)). A
  link whose only sign of focus is that its box moved is NEEDS REVIEW
  unless it is shown only on focus (F-02, 4.D 1.8.0); if more than 1 in
  5 of a round's 4.D stops end there, Abby's option B: take the two
  pictures again once the page settles. The judge is often unsure on
  small focus pictures, so many cells wait for a person.
- **4.D and 4.E:** a control that blurs itself as it gets focus is FAIL
  on a plain page and inside a web component, but inside a frame from
  another site the walk never reaches it: NEEDS REVIEW (row WK). 4.E
  also leaves a menu whose controls the Tab key does not reach, or that
  could not be opened, NEEDS REVIEW.
- **4.E:** an address change the page makes on its own soon after load
  was read as caused by focus when it landed on an early key press
  (round 3: 3 false FAILs). Step 23 moved all three (the walk now starts
  after the app has drawn and changed its address), and 1.9.0 (step 24,
  [#134](https://github.com/abbybowman/tobi508/issues/134)) makes the
  control replay wait as long after load as the original step, so a
  change that still lands on a key press is the page's own (M2, fixture
  `4e/f20`). The page stays NEEDS REVIEW: the walk left it. On round 3's
  community pages 4.E is NEEDS REVIEW for another reason: six dialogs
  that open on focus, each "unsure" for the judge (M11), and the seventh
  not confirmed before 4.E's 60 s ran out (17.5 and 22.3 s in the blind
  run; assumed, not measured: each confirmation is now a fresh load and
  draw wait to a late Tab, since the walk reaches all 76 and 91 elements).
- **4.F:** a footer of link columns raises S3 on every page, and a
  dropdown whose options take arrow keys raises S6; J1's order list can
  leave out what the signals name. Step 33, [#136](https://github.com/abbybowman/tobi508/issues/136). (Round 2's p02, p03 and p07,
  unsure in one rerun and a false FAIL in the next, came from elements
  placed out of line while the page scrolled, a sidebar that scrolls by
  itself and a player's new id on each load: fixed in 4.F 1.11.0.) The judge is often
  unsure, so many cells wait for a person.

## 5.A to 5.H: forms

- **5.A to 5.C:** how often nearby text sends a field to J1 is not
  measured on real pages.
- **5.B:** icon-only buttons are left out (pass L has no picture of
  buttons); a field whose only label is an icon button beside it is
  judged by that picture, one whose only cue is its own button's words
  by those words. A field 5.A could not decide makes 5.B NEEDS REVIEW
  when no other field is judged (A2u, 1.10.0); beside other judged
  fields it is not counted, so a PASS there is "in what 5.B judged". Not
  done: opening the panel a magnifier opens, and a magnifier as a label
  (step 29, [#137](https://github.com/abbybowman/tobi508/issues/137)). On a page with no `<form>`, controls are grouped by the
  page's header, navigation regions and footer (step 35a, [#134](https://github.com/abbybowman/tobi508/issues/134)); in the
  rest of the page every control is still one group, so a button there
  joins every field there. A dropdown made of a menu button (SDE home's
  "All" category, which the key judges) is never an item. The judge
  is often unsure, so many cells wait for a person.
- **5.D:** after a retry, a submission that navigates away reads as
  navigation (only the wording differs); a jump forward past a field
  after Tab-away is not detected; on a filter whose request the
  recording lacks, focus landing on the field's own label reads as a
  move (round 3's blog: a false FAIL; step 35b, [#137](https://github.com/abbybowman/tobi508/issues/137)). `FIELD_MAX` (40) and
  `FIELD_SECONDS` (1.1 s) are not calibrated on real pages. A menu or
  section that opens leaves it NEEDS REVIEW (as in 4.C and 4.E).
- **5.F and 5.G:** the browser's own error messages are left for a
  person (5.F 1.13.0, 5.G 1.11.0): the browser shows one field's message
  at a time and its words differ by browser, so a form checked only that
  way is NEEDS REVIEW until Abby decides whether TT 5.F fails it. Text
  with no word (two letters in a row) is not a message (5.F 1.14.0, 5.G
  1.12.0), so a one-character message in Chinese or Japanese is left
  for a person. `time`, `datetime-local`, `month` and `week` fields are
  left as loaded in attempt 2. Error handling done on the server cannot
  be replayed from a recording: a form that is sent is NEEDS REVIEW, as
  is a change that cannot be read as an error.
- **5.F to 5.H:** a form that is only a button (M-02). **⚑ Check:** the
  review marks M-02 fixed in part B (guard CN holds it at NEEDS
  REVIEW), so this may now only be "not tested", not "not seen".
- **5.H** reads hidden forms for applicability only (5.H 1.9.0): one
  that J1 finds consequential and multi-step stays NEEDS REVIEW (it is
  never submitted); a hidden field inside a frame is not read. Since
  1.10.0 the page's own text is read with the hidden forms when pass E
  takes no form.

## 9.A to 9.C: the same site's other pages

- **9.B** compares only navigation outside the main content: a
  breadcrumb or section menu inside `main` that repeats on other pages
  is left out. With one matched component it says NEEDS REVIEW, where
  there is no order to get wrong. Two lists whose comparison table
  passes 6 million cells pair in order, not by alignment (1.7.0), so an
  extra copy of a link could still read as a swap there (not seen on
  any round's pages).
- **9.C** compares less than the TT text covers (read, not run): links
  pair by address only inside the header, menus, search and footer, and
  otherwise by `id`, an equal name or a place outside the main content.
  Two controls in the pages' own content that do the same thing under
  different names are not paired unless they share an `id`, so 9.C can
  PASS or say DOES NOT APPLY without comparing them. Pictures that are
  not controls are not compared (the PDF's how-to is ANDI's focusable
  elements). Step 19b, [#138](https://github.com/abbybowman/tobi508/issues/138).
- **9.A to 9.C and 19.A:** an other page that cannot be read in full, or
  that is the tested page again, is left out and named, and the test
  decides on the rest (step 26; Abby, 2026-11-20: one usable other page
  is enough). With fewer pages, less is seen to repeat: 9.A's DOES NOT
  APPLY rests on the pages that loaded. An other page that draws itself
  after loading is read twice and left out when the reads differ (#134's
  rerun: one read of round 3's community home page lacked part of its
  header, and 9.A said DOES NOT APPLY on the forum where the key fails).
  Two reads that agree but are both incomplete are not caught; 9.C's own
  ANDI read of the other pages is not read twice. 9.B's region match and 9.C's
  same-place pairing are not calibrated on real templates. A page with
  more than 5,000 items is NEEDS REVIEW.

## 19.A: more than one way

- **The site search depends on where the tool runs:** where the results
  page cannot load its scripts, or the container cannot reach the site,
  the search is "not verified" and 19.A stays NEEDS REVIEW where a
  search that loaded would decide (round 2, steps 6h and 9b). A rerun
  served from the freeze has no search at all. A page whose other pages
  have closed menus the tool did not open, and a link to the page under
  another address whose content changes on every load, are NEEDS REVIEW
  too.
- **Breadcrumbs** count as navigation links, the same kind as the
  menus; Abby's round 3 keys count breadcrumbs on child pages as a way
  of their own (a question for Abby, step 34, [#138](https://github.com/abbybowman/tobi508/issues/138)).

## Not limits: kept here until they have a home

- **Fixtures to write:** a late-refocus fixture for 4.C (refocus 600 ms
  after blur, no DOM change) once the xfail in `tests/test_traverse.py`
  is settled; rows no fixture triggers (9.A M2, M6 and the 8-candidate
  cap; 9.B N1, N5; 9.C C2, C5; a page or ANDI that cannot be read; an
  other page that redirects off the host). **⚑ Check:** "run 4.C's f19
  (cross-origin frame), f24 (open shadow root) and f32 (two traps) for
  4.D, and f32 for 4.F" was listed too; the grid of hard pages (step 7)
  may cover the first two.
- **A question for Abby:** a `role="alert"` added together with its
  error text is not counted as a notice (5.F M7 FAIL), though 5.F's
  Terms say "present before the attempt or added with the text".

## Removed on 2026-11-17

- "A walk that stops at a trap, or runs out of time, can still PASS in
  5.D, 5.F and 4.C (H-03, M-05, E-07)": the review marks all three fixed
  (5.D in part B, 5.F to 5.H in step 6b, 4.C's E-07 in part A), and step
  6d's coverage check holds the rest.
- "19.A's site search on real .gov sites" as a calibration to-do: done
  in steps 6h and 9b (the search runs where the site lets it; above).
