# Known limits, per test

What each built test cannot do today, beyond the wrong outcomes the
README lists ("Known wrong outcomes"). Moved out of `docs/ROADMAP.md`
on 2026-11-14; a fix removes its line here in the same commit.

**Not every limit is NEEDS REVIEW-safe.** The ones that give a PASS or
a DOES NOT APPLY are in the README's "Known wrong outcomes" table, each
with a page that shows it. Browser checks still to run (mostly Windows
headed Chrome) are in
[specs/rules/_browser-checks.md](../specs/rules/_browser-checks.md).

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
- **Web components and frames** are read by every reader since step 8
  (2026-11-15), and a test decides content inside them on the same
  rows. Not read: a closed shadow root, and a frame the recording
  lacks (PASS and DOES NOT APPLY are held, `frames_missing`). The
  lines below name what is still open inside them.
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
  can be missed; flashing below the first screen that is not an image is
  not measured (N-02 to N-09, W-02, W-09). Images (2.B 1.5.0, 3.A
  1.4.0): up to 300 per page are read, lazy ones after a scroll; one the
  recording lacks, an animated one only the scroll found (no region can be
  made for it), or one whose frames at the size shown exceed 100 MB keeps
  2.B and 3.A at NEEDS REVIEW (guard CN or 3.A's A3). Parts C and J.
- **5.H reads hidden forms for applicability only (5.H 1.9.0):** a
  hidden form is never submitted, so one that J1 finds consequential and
  multi-step stays NEEDS REVIEW (no after-submit view, M4). A hidden field
  inside a frame is not read (the inventory's paths are the page's own
  document). (Since 1.10.0 the page's own text is read with the hidden
  forms when pass E takes no form.)
- **Fields hidden from everyone (guard CN; 5.A to 5.H, Abby 2026-11-15):**
  only a hidden part of a form shown on load can be out of scope, and only
  when nothing a careful tester does shows it (the reveal pass, every
  opener pressed, a 15 s watch and a scroll, a choice and typing sweep of
  its form, then its buttons pressed with values typed). A field whose
  whole form is hidden on load (a popup, a panel, a mobile copy) stays
  counted. Accepted limits, each a rare wrong DOES NOT APPLY or PASS: a
  field shown only by typing a particular value, by hovering, after more
  than 15 s, or by leaving the page. Waiting for a positive test (Abby's
  decision that a mobile copy is out of scope, built when a test reads the
  popup): a form hidden at the tested window and shown on load at a
  phone-width window. The check adds about 17 s a page with hidden fields;
  nothing is decided when the reveal pass did not run (a run with none of
  5.A to 5.C, 4.x), left a trigger unopened, or the page has more than 40
  openers.
- **Round 1's "Was this page helpful?" popup never opens, live or
  recorded** (checked live 2026-11-15, full Chromium): the page loads
  jQuery in `defer` bundles but Popup Maker's `site.js` as a blocking
  script at the end of the body, so it runs first and throws "jQuery is
  not defined". The run's report does not say so: guard GU sees no
  unrecorded code, and page script errors are not recorded as a note.
- **A frame whose address changes on every load is not in a frozen
  copy** (reCAPTCHA, a lazy video embed): its replay asks for an address
  the recording never saw, and it is aborted. The freeze lists such frames
  in `freeze.json` (`frames_not_recorded`, step 10a); it does not record
  them.
- **3.A's screencast net varies between runs on some pages:** on round
  2's 5340 the same code gave DOES NOT APPLY in two runs and NEEDS REVIEW
  (row A3: flashing the capture did not show) in another; `main` gave A3
  twice. The key says Does Not Apply, so no run is wrong, but the cell is
  not stable. Not yet looked into.
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
- **4.D and 4.E, focus dropped on focus inside a frame from another
  site:** a control that blurs itself as it gets focus is M3 (4.D) and M7
  (4.E) FAIL on a plain page and, since step 8 (4.D 1.10.0, 4.E 1.7.0),
  inside a web component; inside a frame from another site the walk never
  reaches it, so both are NEEDS REVIEW there (row WK). Safe, not a decided
  FAIL.
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
- **A stuck download can run past its time limit.** An other page's
  media download once ran 342 s past a 20 s limit (step 6h). The cause
  there is gone (other pages no longer record media), but a time limit
  still cannot always stop a page load that is stuck.
- **19.A's site search depends on where the tool runs.** Where the
  results page cannot load its scripts, the search is "not verified"
  and 19.A stays NEEDS REVIEW where a search that loaded would decide
  (round 2's two keyed FAILs, in one container).
- **9.C compares less than the TT text covers** (read against the TT
  text, 2026-11-15; not run). TT: "components that have the same
  functionality within a set of web pages", whatever they look like or
  link to. The spec pairs links by address only inside the header,
  menus, search and footer, and otherwise by `id`, by an equal name, or
  by place outside the main content. So two controls in the pages' own
  content that do the same thing under different names (a "Download"
  button on one page, "Get the file" on another) are not paired
  unless they share an `id`, and 9.C can PASS or say DOES NOT APPLY
  without comparing them. Pictures that are not controls (a status
  icon) are not compared either: the PDF's how-to is ANDI's focusable
  elements. Roadmap, "Next".
- **9.B compares only navigation outside the main content.** A
  breadcrumb or section menu inside `main` that repeats on other pages
  is left out as content. With one matched component it says NEEDS
  REVIEW, where there is no order to get wrong.
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

**Found in round 3** (science.data.nasa.gov, 2026-11-16; causes and
fixes in [the plan after round 3](plans/2026-11-16-after-round3.md),
roadmap steps 21 to 35):

- **Applications that draw themselves after load** (Angular and the
  like): the walk, pass L and the site read can start before the page
  has drawn its controls. On round 3's community pages the forward walk
  found one link of 76 and 90, and 4.F, 4.A, 5.A, 5.D and 5.F to 5.H
  decided on that (README, "Known wrong outcomes"). Steps 22 and 23.
- **One document at every address:** an application that serves the
  same HTML shell at every path makes another page's recording byte for
  byte the tested page's, so 9.A to 9.C and 19.A read it as the tested
  page again (K-01) and are not performed. On such a site 19.A's alias
  check would also verify `/index.html` as the tested page because its
  shell is the same (not run; a PASS risk). Step 26.
- **A sign-in check in a frame** (an OpenID Connect `auth` frame whose
  address changes on every load) is not in a frozen recording (as the
  frames above); on round 3's community pages the app may leave the
  page when it is missing (not shown in the reports).
- **4.E: an address change the page makes on its own** soon after load
  is read as caused by focus when it lands on the first key press: the
  control replay waits only as long as the step took. A false FAIL
  (round 3: 3). Step 24.
- **5.F and 5.G read the browser's own messages as Chrome words them,**
  every field's at once, though the browser shows one at a time and
  another browser's words differ (README). Step 21.
- **4.D's `MIN_CHANGED_PX` is absolute:** about 50 changed pixels pass a
  large image link (README). Step 27.
- **4.A:** J1 can answer "alternative" while its reasons say it is not
  sure, and M8 passes any effect of Enter or Space, even one that is not
  what the click does (round 3's MySearchStory: Enter advanced a
  carousel; NEEDS REVIEW there only because of another answer). Native
  buttons are never executed, so a page that takes Enter from a native
  button is not seen. Step 28. Round 3 also held 4.A at NEEDS REVIEW on
  all six Drupal pages for a hidden share frame, a page-level wheel or
  touch listener and `HOVER_MAX` (40) (step 32).
- **9.B pairs equal links in order:** when one page has an extra copy
  of a repeated link (a breadcrumb "Home" in the same region as the
  others), the pairs cross and 9.B FAILs where nothing moved (round 3:
  6). Step 31.
- **4.F:** a footer of link columns raises S3 on every page (Tab goes
  down one column and up to the next), and a dropdown whose options take
  arrow keys raises S6; J1's order list can leave out what the signals
  name. Step 33.
- **Controls with no `<form>`:** every control's form is "none", so a
  header's menu button joins a search field's form in 5.B. Step 35.
- **5.D on a filter whose request the recording lacks:** the replay
  shows the site's own error, and focus landing on the field's own label
  reads as a move (round 3's blog: a false FAIL). Step 35.
- **The freeze does not run the chunk store:** code an application loads
  when used is missing from a frozen recording, so guard GU holds 4.B
  (round 3's community pages). Step 25.
- **19.A counts a breadcrumb as a navigation link,** the same kind as
  the menus; Abby's round 3 keys count breadcrumbs on child pages as a
  way of their own. A question for Abby (step 34).

