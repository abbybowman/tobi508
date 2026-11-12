# Code review, 2026-11-11: what to fix, in order

A triaged list from a line-by-line review of `tobi508`, for Abby to review
and hand to other threads. Nothing here has been fixed; this thread changes
no code.

**To fix items:** [2026-11-11-code-review-fixing.md](2026-11-11-code-review-fixing.md)
is the prompt for a fresh thread (what to read, how to fix one item, which
model suits which bundle).

**Progress.** All five phases are done. Every file under `src/tobi508/`
was read line by line by a reviewer, and the test suite, CI and image
were reviewed for what they cover. Not read a second time: the small
files the first attempt's interrupted reviewers reported on
(`inline.py`, `explain.py`, the resources, `engine.py`, `rules.py`,
`catalog.py`, `runlog.py`, `versions.py`, `pagecache.py`) and `evals/`.

| Phase | Covers | State |
| --- | --- | --- |
| 0 | Leads from the first attempt (tools, pipeline, traverse, 9.B/9.C/19.A, evals) | done |
| 1 | Security files; what an agent receives, measured; the rest of tools and pipeline | done |
| 2 | 4.A-4.F and 5.A-5.D against their specs | done |
| 3 | 5.F-5.H, 9.A, 2.A-2.D, 3.A and the watchers | done |
| 4 | The rest of the core; tests, CI, Dockerfile, packaging | done |
| 5 | "If we started over"; final ordering | done |

## The short version

- **32 P0 items.** 30 are a false PASS or a wrong DOES NOT APPLY that a
  ten-line page reproduces; 29 of them I reproduced by running the
  page, and one by reading. 2 are security holes in modes that are off
  by default and that the demo plan turns on. The table under "P0"
  lists them one per line.
- **The row tables are right.** In all 22 checks the rows and their
  order match the specs, with small exceptions in 5.C and 9.C (K-06).
  The wrong outcomes come from what the rows
  are fed, and three causes cover most of them: an empty reading and a
  failed reading are the same value; a limit reached is recorded in
  ways that do not hold back an outcome; and the specs define "a
  form", "an error", "a label", "moving" by what the tool can see.
- **The roadmap's "Known limits" line is not true today.** It says
  each limit is NEEDS REVIEW-safe. Shadow roots, forms behind a
  button, English-only word lists and late-starting content each give
  PASS or DOES NOT APPLY.
- **The suite could not have caught these.** It has no shadow-root
  page outside 4.C, no non-Latin text anywhere, and no check but 4.C
  is run on a page with a trap or a time limit (Q-03).
- **One page costs a calling agent about 93,000 tokens to read,** more
  than half of it the two report files it is told to save. On round
  2's real pages those files are too large to save through a client.
- **Security holds where it was designed in.** The allowlist, the
  egress proxy, replay and the owner check on run files were checked
  and hold. The holes are in newer paths: jobs, the server judge's
  picture links, and the stores that fetch what a page names.
- **Decisions only Abby can make** are marked "(needs Abby)" in their
  titles, or say "spec change" in the fix. The main ones: DOES NOT
  APPLY behind the reveal guard (H-08), principle 8's list (E-06),
  native controls in 4.A (E-08), `aria-controls` in 5.D (H-04),
  unnamed pairs in 9.C (K-05), and the word lists (M-03, E-09).

**How each item was checked**

- **Verified (run):** I reproduced it with a test run or a script; the
  item says which.
- **Verified (read):** I read the code and the callers and agree; not run.
- **Reviewer's claim:** a reviewer reported it and I have not checked it.
  All P0 and P1 items are verified one way or the other, or say why not.
- **Refuted:** checked and wrong; listed at the end so nobody chases it
  again.

**Priorities.** P0: a false PASS or a wrong DOES NOT APPLY on real pages,
or a security hole. P1: a wrong result, crash or hang in plausible
conditions, or large waste. P2: moderate waste, or a gap that stays
NEEDS REVIEW. P3: cleanup. Inside a priority, what touches the Nov 20
demo or what a calling agent sees (tokens, time) comes first.

IDs (A-01, D-03 and so on) are handles for other threads to cite. The
letter is the review group: A tools and models, B pipeline and judge,
D the keyboard core, K 9.B/9.C/19.A, L evals, S security, T token
measurement, G the rest of tools and pipeline, E 4.A-4.C, F 4.D-4.F,
H 5.A-5.D, M 5.F-5.H and 9.A, N 2.A-2.D and 3.A, W the motion and
flash watchers, C the rest of the core, Q tests and CI.

The small pages behind the "verified (run)" lines, with the command
for each and what it printed, are in
[2026-11-11-code-review-pages/](2026-11-11-code-review-pages/README.md).

---

## P0

A false PASS or a wrong DOES NOT APPLY on real pages, or a security
hole. Every item was reproduced by a test run or a script unless its
"Checked" line says otherwise. The table lists them in the order
below; "run" means I ran a page and got the outcome shown.

| ID | Test | What the tool says | On what | Checked |
| --- | --- | --- | --- | --- |
| E-01 | 4.A | PASS | a mouse-only hover menu past the 40th Tab stop | run. **Fixed** |
| E-02 | 4.A | PASS | a mouse-only `<a href="#">` beside any other `href="#"` | run |
| N-06 | 3.A, 2.B | DOES NOT APPLY | a flashing GIF after the 30th image | run |
| H-08, M-07 | 5.A, 5.D, 5.F-5.H | DOES NOT APPLY | a form that a plain button opens | run |
| M-01 | 5.F, 5.G | DOES NOT APPLY | a form whose button is `type="button"` | run |
| H-01 | 5.A | PASS | a label whose words are hidden | run |
| C-03 | 5.A and every test behind the reveal guard | PASS | a menu whose trigger is `<a href="#">` | run. **Fixed** |
| N-02, N-04, N-07, N-09 | 2.A, 2.B, 2.C, 3.A | DOES NOT APPLY | sound, motion or flashing that starts after 6.5 s | run |
| W-09 | 2.B | DOES NOT APPLY | a blink or jump 2.5 times a second | run |
| D-03 | 4.A | PASS | a mouse-only control in a shadow root | run |
| D-01 | 5.A, 5.B, 5.C | DOES NOT APPLY | a form in a shadow root | run |
| K-02 | 9.A, 9.B, 9.C, 19.A | DOES NOT APPLY, FAIL | a shared header in a shadow root or frame | run |
| N-01 | 2.A | DOES NOT APPLY | audio from `new Audio()` or in a shadow root | run |
| M-06 | 5.F, 5.G | DOES NOT APPLY | an error shown in a shadow root or on a wrapper | run |
| E-07 | 4.C | PASS | a run that ran out of time before the error-state pass | run |
| H-03, M-05 | 5.D, 5.F | PASS | a form past a keyboard trap | run |
| F-11 | 4.F | DOES NOT APPLY | a page whose first element traps Tab | run |
| F-02 | 4.D | PASS | a link with no focus indicator on a page that shifts | run |
| W-02 | 3.A | DOES NOT APPLY | flashing below the first screen | run |
| W-07 | 2.B | DOES NOT APPLY | motion that fills most of the screen | run |
| N-03 | 2.B | DOES NOT APPLY | text blinking by `visibility` | run |
| N-08 | 2.B | DOES NOT APPLY | an autoplaying YouTube embed | run |
| E-03 | 4.A | DOES NOT APPLY | a page that is only a canvas or drag content | run |
| E-08 | 4.A | PASS | a button that answers only `mousedown` | run |
| C-01 | 4.A | PASS | a mouse-only control whose only effect is `alert()` | run |
| M-02 | 5.H | DOES NOT APPLY | a form that is only a button ("Delete my account") | run |
| M-08 | 5.H | PASS | a multi-step form whose next step says "required" | read |
| M-03 | 5.H, 4.B | DOES NOT APPLY, PASS | a page not in English | run (5.H) |
| H-02 | 5.C | PASS | a field whose visible text is not in Latin letters | run |
| K-01 | 9.B, 9.C (9.A: FAIL or DOES NOT APPLY) | PASS | the tested page named again as the other page | run |
| B-01 | server judge | reads a file outside the run | a page with a crafted `run://` link in its text | script |
| A-01 | hosted sign-in | shows one user another's run | any two signed-in users | read |

Three causes account for most of the table. They are the first three
items of "If we started over" at the end.

1. **"I saw nothing" and "I could not look" are the same value.** A
   reader returns an empty list or `None` either way, and the check
   reads empty as DOES NOT APPLY or PASS.
2. **Limits are recorded in several ways, and only one of them holds
   back an outcome.** A cap, a time limit or a trap is sometimes an
   "incomplete" reason (NEEDS REVIEW), sometimes a note (still PASS),
   sometimes nothing.
3. **The specs define what counts in terms of what the tool can
   see.** Row tables match the specs in every check; the gaps are in
   the specs' "Terms" (what is a form, an error, a label, a moving
   region), so several fixes are spec changes for Abby.

### Reaches most real pages

These need nothing unusual: a long page, a link with `href="#"`, a
gallery, a form behind a button, a script-checked form.

#### E-01 4.A passes without looking for hover menus past the 40th element

- **What is wrong:** the scan for menus that open when the mouse rests
  on something stops after 40 Tab stops. Every other cap in 4.A makes
  the page NEEDS REVIEW. This one only adds a sentence to the summary,
  and the page still passes.
- **Why it matters:** most agency pages have more than 40 Tab stops. A
  mouse-only menu on stop 41 or later (a footer, a side menu) is never
  looked at, and the result reads "we found nothing a keyboard user
  would miss. Only the first 40 elements were checked...". The spec's
  G3 says an unfinished cap is NEEDS REVIEW.
- **Where:** `src/tobi508/checks/t4a.py:501-507` (the cap writes to
  `st.notes`), `1222-1227, 1253` (only `st.incomplete` holds back G4).
- **Smallest fix:** write the cap to `st.incomplete`. One line; one
  fixture with 45 links. If a note-only cap is wanted, the spec has to
  say so.
- **Checked:** verified (run). 45 links, a mouse-only menu shown by
  hovering the 45th: 4.A PASS, rows A3, G4.
- **Fixed:** commit "4.A: the hover cap holds the page back (E-01)",
  no spec change (spec 4.A already says G3). Fixture
  `4a/f18-hover-menu-past-the-cap`: NEEDS REVIEW.

#### E-02 4.A passes a mouse-only `<a href="#">` because another link also has `href="#"`

- **What is wrong:** row M3 passes a control the keyboard cannot reach
  when a reached link "goes to the same place". The test is that the
  two `href` texts are equal. Mouse-only controls are very often
  `<a href="#" onclick=...>` or `href="javascript:void(0)"`, and most
  pages have a reached link with the same placeholder.
- **Why it matters:** a false PASS on the commonest way to build a
  mouse-only control. The same mistake as K-04 in 9.C.
- **Where:** `src/tobi508/checks/t4a.py:701-728` (`_same_link`),
  `1023-1028` (M3).
- **Smallest fix:** for M3, ignore addresses that are empty, `#` alone,
  `javascript:` or the page itself with a fragment; those go to the
  question. The spec row needs the same words.
- **Checked:** verified (run). `<a href="#">Home</a>` and
  `<a href="#" tabindex="-1" onclick=...>Open settings</a>`: 4.A PASS,
  row k1:M3 ("Home goes to the same place").

#### N-06 A flashing GIF after the 30th image is invisible to 3.A and 2.B

- **What is wrong:** the watcher decodes animated images from the first
  30 `<img>` addresses only, and silently skips any file it cannot
  decode (over 5 MB, an unknown type, not in the recording). Nothing
  records what was skipped. Below the first screen the screen capture
  cannot see it either.
- **Why it matters:** a wrong DOES NOT APPLY for flashing, the one test
  where a miss can hurt someone. A gallery or news page easily has more
  than 30 images.
- **Where:** `src/tobi508/motion.py:470-471, 1412-1415`;
  `src/tobi508/checks/t3a.py:113-118`.
- **Smallest fix:** when there are more than 30 images or one was
  skipped, record it as "not measured" (3.A's A3, NEEDS REVIEW) and as
  a hint for 2.B. Better: decode every image file in the recording
  that has an animated-format signature.
- **Checked:** verified (run). A strobing GIF below a spacer with 31
  small images before it: 3.A DOES NOT APPLY and 2.B DOES NOT APPLY.
  The reviewer's control with one image before it gave 3.A NOT TESTED
  (8.5 flashes a second).

#### H-08, M-07 A form behind a plain button is "no form fields" (needs Abby)

- **What is wrong:** the tests list form fields that are rendered when
  the page loads. A form that a button or link shows is found only if
  the control carries a marker the reveal pass looks for
  (`aria-expanded`, `aria-haspopup`, `aria-controls`, a tab, a
  `<summary>`). Behind a plain button it is never opened. The reveal
  guard holds back a PASS only: the spec says FAIL and DOES NOT APPLY
  are unchanged (Abby, 2026-11-09).
- **Why it matters:** a wrong DOES NOT APPLY on a common pattern (a
  "Sign up" or "Log in" button that opens a form), and 5.C can PASS
  without the hidden field. `contenteditable` boxes are not fields at
  all, by the spec's choice.
- **Where:** `src/tobi508/labels.py:28, 53-59`;
  `src/tobi508/engine.py:115-134` (guard RV); A1 in specs 5.A-5.D.
- **Smallest fix:** a spec decision. One option: when the page has
  hidden form fields in its DOM (`display: none` or `hidden` ancestors),
  DOES NOT APPLY becomes NEEDS REVIEW with "N form fields are hidden
  until something opens them". Counting them is one query.
- **Checked:** verified (run). A button with a click handler that
  unhides a form with an email field: 5.A DOES NOT APPLY ("only form
  controls are buttons"), 5.D DOES NOT APPLY, 5.C PASS.
- **Also in 5.F, 5.G and 5.H (M-07):** their specs do not list the
  reveal guard at all. The reviewer's run of a "Pay your bill" button
  that unhides a payment form gave DOES NOT APPLY for all three.

#### M-01 5.F and 5.G say "the page did not check for errors" when the form's button is `type="button"`

- **What is wrong:** only submit-type buttons count as the control that
  sends a form. A form checked by script usually has
  `<button type="button" onclick="validate()">`. That button is never
  pressed; with two or more fields, Enter does not submit either; and
  the question that lets the agent name the right button is never
  asked, because the list of buttons is empty.
- **Why it matters:** a wrong DOES NOT APPLY on a very common way to
  build a form, with a sentence that is untrue. Spec and code agree,
  so the spec has the gap.
- **Where:** `src/tobi508/checks/t5f.py:160-161` (`isSubmit`), `173`,
  `641`, `946-951`.
- **Smallest fix:** offer every visible button inside the form, submit
  words first; a form whose press could not have sent it (no submit
  button, more than one field) is NEEDS REVIEW, never DOES NOT APPLY.
- **Checked:** verified (run). Two fields and a `type="button"` whose
  handler writes "Email: enter a valid email address" into a
  `role="alert"`: 5.F and 5.G DOES NOT APPLY, no question.

#### H-01 5.A passes a label whose words nobody can see

- **What is wrong:** row M2 ("a visible label with text") is true when
  the label element has a box near the field and any text. The text is
  read with `innerText`, which includes words hidden with the usual
  screen-reader-only CSS, words pushed off screen with `text-indent`,
  and the options of a `<select>` that the label wraps.
- **Why it matters:** a false PASS with no question asked. A label that
  shows only "*" while its words are in a hidden span is a common
  pattern. The spec says a visible label is text "rendered and readable
  while the field has focus".
- **Where:** `src/tobi508/labels.py:40` (`txt`), `188-189`;
  `src/tobi508/checks/t5a.py:40-46`.
- **Smallest fix:** take a label's text from its text nodes that pass
  the visibility test (as the nearby-text reader already does at
  `labels.py:212-225`), leaving out `select` and `option`; a label with
  no visible text goes to the question.
- **Checked:** verified (run). Three fields: a label of a hidden span
  plus "*", an empty label wrapping a select, a label with
  `text-indent: -9999px`. 5.A PASS, all three on row M2.

#### C-03 A menu opened by `<a href="#">` is dropped unread, and the page still passes

- **What is wrong:** the reveal pass presses Enter on each menu trigger
  and reads what opens. A trigger written as `<a href="#"
  aria-haspopup="true">` also adds `#` to the address. The observer
  compares whole addresses, calls that "navigation", and the reveal
  pass stops without reading the menu. A "navigated" trigger is not in
  the list the reveal guard reads, so nothing holds the PASS back.
- **Why it matters:** `<a href="#">` is one of the commonest ways to
  write a menu trigger. Whatever is inside that menu is unchecked, with
  no note, in every test that relies on the reveal pass (5.A to 5.D,
  4.A, 4.D, 4.E).
- **Where:** `src/tobi508/observe.py:302`;
  `src/tobi508/reveal.py:316, 328-330, 169, 183`. The walk's own
  navigation test ignores the fragment (`traverse.py:980`); this one
  does not. F-06 and H-11 are the same mistake in 4.E and 5.D.
- **Smallest fix:** compare addresses without their fragment in
  `observe` (one function, used by 4.E, 5.D and reveal); a trigger is
  "navigated" only on a real navigation or a new page.
- **Checked:** verified (run). A link trigger with a hidden, unlabelled
  field in its menu: 5.A PASS. The reviewer's control with a
  `<button>` trigger: NEEDS REVIEW, field found.
- **Fixed:** commit "Fragment-only address changes are not navigations
  (C-03, F-06, H-11)", no spec change (the 4.E and 5.D Terms already
  say the fragment is ignored). `observe.without_fragment` is used by
  `observe()`; 4.E's navigation hook skips a fragment-only change.
  Fixtures `5a/f25-hash-link-opens-menu` (5.A FAIL M2 M5, as the
  accordion page f23), `4e/f11-hash-change-on-focus`,
  `4e/f12-pushstate-on-focus`, `5d/f22-hash-change-on-blur`.

#### N-02, N-04, N-07, N-09 What starts after the 6.5-second watch is "does not apply"

- **What is wrong:** the page is watched for 6.5 s. 2.C treats "a timer
  longer than the watch" as a hint and answers NEEDS REVIEW. 2.A, 2.B
  and 3.A have no such path, though the same timers are in the
  evidence. 2.A decides from the one reading at 3.5 s. For content
  that starts when scrolled into view, only the first such element is
  scrolled to, and 2.C says nothing about the rest.
- **Why it matters:** audio that a script starts at 4.5 s, an animation
  that starts at 7 s, a strobe that starts at 9 s, and a counter on
  the second scroll-in element each give DOES NOT APPLY with a
  sentence that claims nothing happened.
- **Where:** `src/tobi508/checks/t2a.py:94-129`;
  `src/tobi508/checks/t2b.py:177`; `src/tobi508/checks/t3a.py:213-238`;
  `src/tobi508/motion.py:1591-1611, 1655`; 2.C's `hints` at
  `src/tobi508/checks/t2c.py:73-100`.
- **Also (W-05):** an `<audio autoplay loop>` that a script inserts
  1.5 s after load is DOES NOT APPLY too. The watcher has it playing at
  3.5 s and at 6.5 s; 2.A compares the 3.5 s reading with the first
  reading the element appears in, which is the same one, and concludes
  it is not advancing. Verified (run). Fix: compare with the last
  reading (`t2a.py`, `find_audio`).
- **Smallest fix:** share 2.C's hints: when there is a hint and nothing
  was found, 2.A, 2.B and 3.A answer NEEDS REVIEW too; add "N more
  elements wait to be scrolled into view" as a hint. Spec changes in
  the safe direction for 2.A, 2.B and 3.A. One caution from the
  watchers reviewer: 2.C's hint fires on any timer of a second or
  more, including a 60 s analytics heartbeat (W-10, below), so shared
  as it is it would send most real pages to NEEDS REVIEW. Weigh the
  hint first (a period of 7 to 20 s looks like a carousel; 60 s does
  not), or run the page forward 30 to 60 s on 3.A's paused clock.
- **Checked:** verified (run), four pages: audio started by a 4.5 s
  timer, 2.A DOES NOT APPLY; an animation class added at 7 s, 2.B DOES
  NOT APPLY while 2.C on the same run is NEEDS REVIEW ("a timer of
  7 s"); a strobe started at 9 s, 3.A DOES NOT APPLY; a counter started
  by the second observed element, 2.C DOES NOT APPLY.

#### W-09 2.B misses a blink or jump at 2.5 times a second

- **What is wrong:** the watch compares about 17 screenshots taken at
  gaps of 0.35 s and 0.45 s in turn. That pattern repeats every 0.8 s,
  so content with a period of 0.4 s is caught in the same state in
  both pictures for three starts in four (the reviewer's simulation;
  one in two at 0.2 s).
- **Why it matters:** a wrong DOES NOT APPLY on fast blinking, which is
  below 3.A's threshold, so 2.B is the only test that covers it.
- **Where:** `src/tobi508/motion.py:51-54` (`FRAME_STEPS`),
  `1149-1167`.
- **Smallest fix:** vary the gaps (a seeded 0.30 to 0.50 s), or take
  change from a screen recording of the whole watch. Add 1 to 3 Hz
  blinks to `tests/test_motion_browser.py`.
- **Checked:** verified (run). A box that jumps 200 px sideways every
  200 ms, forever: 2.B DOES NOT APPLY in 2 of 2 runs. (The reviewer's
  own page blinked by `visibility`, which N-03 also explains; mine
  does not.)

### Pages built with web components

One cause: most readers use `document.querySelectorAll` or
`el.children`, which do not enter shadow roots. The keyboard walk
does enter them, so the tool reaches these controls and then loses
them.

#### D-03 4.A passes a page whose mouse-only control is in a shadow root

- **What is wrong:** 4.A finds mouse-only controls by asking Chrome for
  the click handlers in the document. The request does not look inside
  shadow roots, so a control with a click handler inside a web component
  is never seen.
- **Why it matters:** a false PASS. The same control in the ordinary DOM
  raises a question; inside a shadow root the test says "we found nothing
  a keyboard user would miss". Design systems built on web components
  put every control in a shadow root.
- **Where:** `src/tobi508/traverse.py:515-518` (`getEventListeners` with
  `pierce: False`); used by `src/tobi508/checks/t4a.py:391-401`.
- **Smallest fix:** also read listeners from each open shadow root (or
  `pierce: True`, keeping only this frame's nodes). Until then, when the
  page has any shadow root, add a coverage note so 4.A cannot PASS.
  Fixture: one clickable `<span>` in a shadow root.
- **Checked:** verified (run). Two one-control pages, same handler: in
  the ordinary DOM, 4.A is NEEDS REVIEW with question `4.A-k1-J1`; in a
  shadow root, 4.A is PASS (rows A3, G4).

#### D-01 5.A, 5.B and 5.C say "no form fields" when the form is in a shadow root

- **What is wrong:** the label pass lists form fields with a plain
  `document.querySelectorAll`, which does not enter shadow roots. Fields
  in frames get a "not checked" note; fields in shadow roots get nothing.
  With no fields and no note, the three tests return DOES NOT APPLY.
- **Why it matters:** a wrong DOES NOT APPLY on any page whose inputs are
  web components. `docs/ROADMAP.md` ("Known limits") says this case is a
  NEEDS REVIEW note; for shadow roots it is not.
- **Where:** `src/tobi508/labels.py:53` (`comps()`), `labels.py:361-380`
  (only frames add a note); `src/tobi508/checks/t5a.py:238-243` and the
  same branch in `t5b.py` and `t5c.py`.
- **Smallest fix:** in `read_session`, count fields inside open shadow
  roots (the walk's inventory already does) and add an "N form fields
  inside web components were not checked" note, as for frames. Reading
  them properly is the second step.
- **Checked:** verified (run). A page with a text field, an email field
  and a button in an open shadow root: 5.A, 5.B and 5.C all DOES NOT APPLY
  ("This page has no form fields"). On the same page 5.D sees the two
  fields, and 5.F, 5.G and 5.H are NEEDS REVIEW ("2 form field(s) could
  not be read"), which is the safe answer.

#### K-02 Navigation inside a shadow root or a frame is invisible to 9.B, 9.C and 19.A

- **What is wrong:** the site read walks `el.children` only. A header or
  menu built as a web component, or placed in a frame, yields nothing.
- **Why it matters:** 9.B and 9.C answer DOES NOT APPLY ("no navigation
  on this page appears on the other pages") and 19.A answers FAIL ("no
  way to reach this page") for a site whose shared header is plainly
  there. Nothing in the result says content was skipped. 9.A has a frame
  guard; these three have none.
- **Where:** `src/tobi508/site.py:124-162` (`walk`); the DNA and FAIL
  branches at `checks/t9b.py:200-214`, `checks/t9c.py:471-477`,
  `checks/t19a.py:422-438`.
- **Smallest fix:** count shadow roots and frames while reading each page
  and, when there are any, make these DNA and FAIL branches NEEDS REVIEW
  with the count (the way the cap rule N1 works). Walking open shadow
  roots is the second step.
- **Checked:** verified (run) for shadow roots: two pages sharing a
  `<site-header>` web component with a three-link menu gave 9.B DNA,
  9.C DNA and 19.A FAIL. Frames: verified (read) only.
- **Also 9.A (M-12):** it uses the same read. The reviewer's run of a
  shadow-root header with no other landmark gave 9.A DOES NOT APPLY.

#### N-01 2.A does not hear audio from `new Audio()` or from a shadow root

- **What is wrong:** the watcher finds media with
  `document.querySelectorAll('video, audio')`. Audio a script starts
  with `new Audio(url).play()`, the usual way to play background sound,
  is never in the document. Audio inside a web component is in a
  shadow root. Neither is seen, and nothing else records that
  something played.
- **Why it matters:** a wrong DOES NOT APPLY ("No audio played by
  itself") on a page that plays sound at load with no control, which
  is a FAIL in the TT.
- **Where:** `src/tobi508/motion.py:392` (`M.media`);
  `src/tobi508/checks/t2a.py:94-129, 190`.
- **Smallest fix:** in the watcher's start-up script, hook
  `HTMLMediaElement.prototype.play` and keep every element that
  played; walk open shadow roots. An element that played and could not
  be read is NEEDS REVIEW.
- **Checked:** verified (run). The same tone file three ways: a plain
  `<audio autoplay>` is 2.A FAIL; `new Audio('tone.wav').play()` is
  DOES NOT APPLY; `<audio autoplay>` in a shadow root is DOES NOT
  APPLY. The watchers reviewer found the same independently (W-03)
  and adds that `speechSynthesis.speak()` is not hooked either.

#### M-06 5.F and 5.G read "no error seen" as "the page did not check"

- **What is wrong:** an error counts when the tool sees new text,
  `aria-invalid`, a browser message or a change in the field's own
  look. It does not see error text inside a shadow root, a red border
  on a wrapper around the field, or a message that is gone within about
  150 ms (there is one reading, after the page settles).
- **Why it matters:** each of those is DOES NOT APPLY, "the page did
  not check for errors", with no question to the agent.
- **Where:** `src/tobi508/checks/t5f.py:93-115, 124-136, 437-450,
  1376-1382`; `src/tobi508/checks/t5g.py:293-299`.
- **Smallest fix:** if anything in the page changed during the press
  that was not read as an error (the change counter already exists),
  the answer is NEEDS REVIEW. Then read shadow roots and the field's
  nearest bordered ancestor.
- **Checked:** verified (run) for two of the three: error text in a
  shadow root, and a red border on a wrapper, both 5.F DOES NOT APPLY.
  The 60 ms message is the reviewer's run.

### A walk cut short by a trap or the clock

One cause: "did not finish" is recorded in different ways by
different checks, and some of those ways do not hold back an outcome.

#### E-07 4.C passes after skipping its error-state pass for lack of time

- **What is wrong:** there are two "out of time" helpers. The one inside
  4.C's collector also records "the run time limit was reached", which
  makes the page NEEDS REVIEW. The one on the run context only sets a
  flag. The gate before 4.C's error-state pass uses the second, with no
  `else`.
- **Why it matters:** the run's error line says "what was not finished
  is NEEDS REVIEW" while the finding says PASS. It happens whenever the
  deadline falls after the walk and before that pass: with
  `no_time_limit=false`, or at `MAX_RUN_S` on a large page.
- **Where:** `src/tobi508/checks/t4c.py:820`;
  `src/tobi508/checks/base.py:116-123`; `t4c.py:242-250`.
- **Smallest fix:** use the recording helper at line 820. Better: one
  helper for every check, and a pipeline rule that a test whose
  collector ran out of time cannot PASS.
- **Checked:** verified (run). A small form page with the run limit set
  to 17 s: the run reported the time-limit error and 4.C PASS (rows A3,
  G4). At 22 s and 28 s the same page passes with no error.
- **Fixed:** commit "4.C: out of time before the error pass is never PASS (E-07)",
  no spec change. `RunContext.out_of_time(record)` adds the one shared
  reason to the check's `incomplete`; the gate uses it. Test
  `test_f44_out_of_time_before_the_error_pass_is_never_pass` forces the
  time (a real limit is machine-dependent): PASS before, NEEDS REVIEW
  after. Other checks still call `out_of_time()` with no record: moving
  them onto it is part C's "one out of time helper".

#### H-03, M-05 5.D and 5.F pass a form they stopped testing at a keyboard trap

- **What is wrong:** the spec says NEEDS REVIEW when the walk "ended in
  a trap before the last field". The code counts the two trap endings
  as a complete walk. Fields after the trap were never reached, so they
  are not in the list of fields to complete, and nothing compares that
  list with the number of fields on the page.
- **Why it matters:** a false PASS: "We filled in each of the 1 form
  fields" on a form with two, the second of which navigates away on
  blur.
- **Where:** `src/tobi508/checks/t5d.py:1086, 1090-1094`; spec 5.D
  section 3b, G3.
- **Smallest fix:** treat a trap ending like any other unfinished walk,
  and add "N form fields the keyboard walk did not reach" whenever the
  page has more fields than were completed.
- **Checked:** verified (run). A field, a link that swallows Tab, a
  second field with `onblur` navigation: 5.D PASS, rows A3, G4.
- **Also in 5.F (M-05):** the same list of "complete" endings is at
  `src/tobi508/checks/t5f.py:1233`. Verified (run): a form, a trap,
  then a second form with a broken error message: 5.F PASS. Without
  the trap the same page is FAIL. 5.G and 5.H read the same pass.

#### F-11 4.F says "only one element takes focus" when the first element traps Tab

- **What is wrong:** 4.F's DOES NOT APPLY row counts the distinct stops
  the walk reached. When the first element traps Tab, the walk reaches
  one. The row is tested before the row that says "the forward pass
  did not finish, so the order is unknown".
- **Why it matters:** a wrong DOES NOT APPLY, with a sentence that is
  untrue of the page. 4.C does catch the trap on the same page, so the
  page is not clean overall, but 4.F's own line is wrong.
- **Where:** `src/tobi508/checks/t4f.py:597-600` (`distinct`),
  `744-749` (A3), `843-858` (A3 returns before the G3 check).
- **Smallest fix:** A3 applies only when both passes ended in a wrap (or
  the same trap); otherwise fall through to NEEDS REVIEW.
- **Checked:** verified (run). Four links, the first swallowing Tab:
  4.F DOES NOT APPLY ("The page has only one element that takes
  keyboard focus"); 4.C on the same run asked its trap question.

### Particular content

#### F-02 4.D passes an element with no focus indicator when the page shifts under it

- **What is wrong:** 4.D compares a picture of each element with focus
  and without. Row M6 passes when there is a "style signal" and at
  least 12 strongly changed pixels. The element's box having moved
  between the two pictures counts as a style signal. If anything shifts
  the page between them (a banner, a spacer, late content), the box
  moves, the two pictures show different things, and the pixels differ.
- **Why it matters:** a false PASS: "every one showed where focus was"
  for a link with `outline: none`. The spec means the moving box for
  skip links that appear on focus; the code applies it to any move.
- **Where:** `src/tobi508/checks/t4d.py:826-827` (`_style_signal`),
  `929-934` (M6), `325-326` (`moved`).
- **Smallest fix:** count a move as a signal only when the element is
  shown only on focus (its unfocused box is empty, hidden or off
  screen); otherwise a moved element with changed pixels is "no clear
  view" (M4, NEEDS REVIEW). This turns a PASS into NEEDS REVIEW, so it
  needs Abby and a MINOR spec change. One fixture.
- **Checked:** verified (run). Three links, the first with
  `outline: none`; focusing the second grows a spacer above them. 4.D
  PASS, rows d1:M6, d2:M6, d3:M6, G4.

#### W-02 3.A says nothing flashes when the flashing is below the first screen

- **What is wrong:** the frame-by-frame capture photographs the top
  1024 x 768 of the page. When the watcher has seen a fast timer
  changing the page (a "trigger") and the capture then sees a still
  picture, the source is recorded as "not flashing" and as measured.
- **Why it matters:** a wrong DOES NOT APPLY for flashing on a page
  where the tool itself recorded "8 changes in one second". The safety
  net (a 2 s screen recording) also sees only the first screen.
- **Where:** `src/tobi508/flashcap.py:249, 296`;
  `src/tobi508/checks/t3a.py:237-300, 587-597`; spec 3.A, row A4
  ("every trigger was measured").
- **Smallest fix:** a trigger counts as measured only when the capture
  saw it change; otherwise add "something changed quickly that the
  capture did not show", which is row A3, NEEDS REVIEW. Then scroll the
  changed element into view for the capture.
- **Checked:** verified (run). A 1000 x 400 block switching black and
  white every 125 ms, 2,500 px down the page: 3.A DOES NOT APPLY.

#### W-07 2.B says nothing moved when most of the screen moves

- **What is wrong:** a pair of frames in which more than half the
  screen changed is set aside as a "page-wide change" (meant for a
  dialog backdrop or a scroll) and not mapped to any region. No check
  reads the set-aside list. A full-width slider, a colour-cycling
  background or a full-screen canvas changes most of the screen in
  every pair.
- **Why it matters:** a wrong DOES NOT APPLY on the largest moving
  content a page can have.
- **Where:** `src/tobi508/motion.py:64` (`PAGE_CHANGE = 0.5`),
  `1501-1504`.
- **Smallest fix:** when a third or more of the frame pairs are
  page-wide changes, treat the viewport as one moving region, or at
  least add "the whole screen changed in N frames" as a NEEDS REVIEW
  hint in 2.B and 2.C.
- **Checked:** verified (run). A fixed full-viewport canvas drawing a
  slowly cycling gradient: 2.B DOES NOT APPLY.

#### N-03 2.B says nothing blinked when text blinks by `visibility`

- **What is wrong:** text switched between `visibility: hidden` and
  `visible` (the usual stand-in for `<blink>`) changes the region's
  visible text, so the watcher files it as "updating", never "moving".
  2.B looks only at moving regions.
- **Why it matters:** a wrong DOES NOT APPLY ("Nothing on it moved,
  blinked or scrolled") on blinking text. 2.C does report the same
  content, so the page is not clean overall.
- **Where:** `src/tobi508/checks/t2b.py:77-85` (`moving`);
  `src/tobi508/motion.py:215, 976-987`.
- **Smallest fix:** count an updating region as blinking when it keeps
  returning to an earlier state (few distinct states, still changing
  after 5 s). Fixtures for `visibility` and `opacity`.
- **Checked:** verified (run). A span toggled every 500 ms: 2.B DOES NOT
  APPLY, rows A2, G1.

#### N-08 2.B says nothing moved on a page with an autoplaying YouTube embed

- **What is wrong:** 2.B's spec row A1 names three ways a video "could
  not play from the recording": an error, a streaming player, a file
  over the cap. The code has the first only. 2.A and 3.A do have all
  three, each with its own pattern.
- **Why it matters:** on one page 2.A and 3.A say NEEDS REVIEW ("a
  streaming video player that we cannot play from a recording") and
  2.B says DOES NOT APPLY ("Nothing on it moved").
- **Where:** `src/tobi508/checks/t2b.py:114-115, 170-175`; spec 2.B,
  A1; compare `t2a.py:92-112`, `t3a.py:149-157`.
- **Smallest fix:** one shared "media we could not play" helper, used
  by 2.A, 2.B and 3.A.
- **Checked:** verified (run). A `youtube-nocookie.com/embed/...
  ?autoplay=1` frame: 2.A NEEDS REVIEW, 2.B DOES NOT APPLY.

#### E-03 4.A says "nothing can be used with a mouse or keyboard" on a canvas or drag-only page

- **What is wrong:** 4.A records canvases, draggable elements and
  mouse-move handlers as "could not be tested, a person must look".
  The DOES NOT APPLY row is tested first and does not look at them.
- **Why it matters:** a wrong DOES NOT APPLY on a page that is a map, a
  drawing or a drag-and-drop board, which is the content 4.A matters
  most for. Spec row A1 says the same as the code, against the spec's
  own "never a reason to PASS" for these.
- **Where:** `src/tobi508/checks/t4a.py:965-969, 1184-1201`.
- **Smallest fix:** A1 also requires that nothing of that kind was
  recorded; otherwise NEEDS REVIEW. A spec change in the safe direction.
- **Checked:** verified (run). A canvas with a mouse-move handler and a
  draggable box, nothing focusable: 4.A DOES NOT APPLY.

#### E-08 4.A passes a button that only answers `mousedown` (needs Abby)

- **What is wrong:** a native `<button>` or link is reached by Tab, so
  it is not a mouse-only candidate, and native controls are never
  pressed. One that acts on `mousedown` or `pointerdown` alone does
  nothing on Enter or Space.
- **Why it matters:** a false PASS on WCAG failure F54, the thing 4.A
  exists to find. The spec says native controls are not executed; the
  listener types are already read and then thrown away for them.
- **Where:** `src/tobi508/checks/t4a.py:615-620, 262-265`.
- **Smallest fix:** a native stop with a mouse-down listener and no
  click listener gets the Enter-and-Space check, or NEEDS REVIEW. It
  turns a PASS into a FAIL or a review, so it needs Abby and a spec row.
- **Checked:** verified (run). `<button onmousedown=...>Open panel
  </button>`: 4.A PASS, rows A3, G4.

#### C-01 4.A passes a mouse-only control whose only effect is `alert()`

- **What is wrong:** to decide whether a click does anything, the
  observer compares the page before and after. It does not listen for
  JavaScript dialogs, which the browser closes at once when nobody
  listens. A control whose click shows `alert()` or `confirm()` reads
  as "no effect", so it is not counted as mouse-only. A download reads
  the same way.
- **Why it matters:** a false PASS for help text, confirmations and
  downloads that only a mouse can get.
- **Where:** `src/tobi508/observe.py:266-320`. Only `checks/t5f.py:463`
  listens for dialogs.
- **Smallest fix:** in `observe`, listen for `dialog` (and `download`)
  during the action and record it as an effect. One fixture.
- **Checked:** verified (run). A `<div onclick="alert('Help text')">`
  beside one link: 4.A PASS, row k1:M2. The reviewer's control, where
  the click unhides a paragraph, is NEEDS REVIEW.

#### M-02 5.H cannot see a form that is only a button

- **What is wrong:** forms are built from the form fields the walk
  reached. `<form method="post" action="/delete-account"><button>Delete
  my account</button></form>` has none.
- **Why it matters:** "This page has no form to submit" for a delete,
  pay or submit-exam button, which is what 5.H exists for. Spec row A1
  says "no form with a submit control", which this page has.
- **Where:** `src/tobi508/checks/t5h.py:311-325`;
  `src/tobi508/forms.py:141-177`.
- **Smallest fix:** 5.H lists every `form` element with a submit
  control, whatever its fields; at least NEEDS REVIEW when the page has
  a visible form that was not taken.
- **Checked:** verified (run): 5.H DOES NOT APPLY, rows A1, G1.

#### M-08 5.H passes a multi-step form when the next step contains the word "required"

- **What is wrong:** row M1 passes a form that "checked" the entry.
  "Checked" is true when the form was not sent, its fields still exist
  in the DOM (hidden counts), and any new text matches error, invalid,
  required, must, incorrect or missing.
- **Why it matters:** a wizard whose step 2 says "Card number is
  required to pay" passes 5.H with no review step and no question. The
  spec says a next step's "required" text is not a check; the code's
  test for "still on the form" does not hold that.
- **Where:** `src/tobi508/checks/t5h.py:36-39` (`ERROR`), `105-116`,
  `148` (M1 before the question).
- **Smallest fix:** "stayed" needs the same fields to be visible, not
  merely present; text that is not tied to a field goes to the
  question.
- **Checked:** verified (read): the rule is as described. The reviewer
  ran a two-step page, saw `checked: true` in the evidence, and got
  PASS from `evaluate` on the saved state.

#### M-03 English word lists decide DOES NOT APPLY in 5.H and PASS in 4.B

- **What is wrong:** 5.H asks about a form only if the page has an
  English word such as pay, order, agree or delete. 4.B asks about
  timing only if the page has an English timing phrase, and no match is
  PASS. A page in Spanish matches neither.
- **Why it matters:** a Spanish payment page is DOES NOT APPLY for 5.H,
  and a Spanish page that requires a held key passes 4.B. Federal
  sites publish Spanish pages. The roadmap lists "English only" as a
  known limit and calls it NEEDS REVIEW-safe; it is not.
- **Where:** `src/tobi508/checks/t5h.py:29-35, 118-127`;
  `src/tobi508/checks/t4b.py:30-35`.
- **Smallest fix:** when the page's language is not English, the
  word-list rows give NEEDS REVIEW (or ask the question for every
  form). A spec change in the safe direction.
- **Checked:** verified (run) for 5.H: a `lang="es"` page with "Numero
  de tarjeta" and "Pagar ahora" is DOES NOT APPLY. The 4.B half follows
  from row M1 and is not run.

#### H-02 5.C passes any field whose visible text is not in Latin letters

- **What is wrong:** 5.C compares the words people see with the words
  a screen reader announces. Its word splitter keeps only `a-z` and
  `0-9`. Cyrillic, Greek, Arabic, Hebrew, Chinese, Japanese and Korean
  text yields no words, and "every visible word is announced" is then
  true of nothing.
- **Why it matters:** a false PASS on translated pages, whatever the
  field announces. The same splitter makes 5.A's row M2o treat
  non-Latin text beside an option as no text (a wrong FAIL; not run).
- **Where:** `src/tobi508/checks/t5c.py:34-35` (`words`), `153-163`
  (M5), `107-110`; `src/tobi508/checks/t5a.py:55, 70-71`.
- **Smallest fix:** split on Unicode word characters, and never let M5
  pass when there is visible text that yields no words.
- **Checked:** verified (run). Fields labelled "Имя пользователя" and
  "必須の住所を入力してください" with `aria-label="f1"` and `"x1"`:
  both on row M5 (pass), not asked.

### What the caller passes in

#### K-01 An "other page" that is the tested page under another spelling gives 9.B and 9.C a PASS

- **What is wrong:** the tool refuses an other page only when its text
  equals the tested page's text. A query string, a trailing slash, http
  for https, or a URL that redirects to the tested page all get through.
  After loading, only the host is compared.
- **Why it matters:** the page is compared with itself. Everything
  matches in the same order with the same names, so 9.B and 9.C PASS on
  no evidence. An agent that passes `https://x.gov` and `https://x.gov/`
  gets there without meaning to.
- **Where:** `src/tobi508/pipeline.py:319` (text comparison) and about
  line 1000 (after recording, host only).
- **Smallest fix:** after recording, refuse an other page whose final URL
  (fragment dropped, trailing slash and scheme ignored) equals the tested
  page's final URL, and drop duplicates among the other pages the same
  way. One fixture.
- **Checked:** verified (run). Tested page `site-a.html`, other page
  `site-a.html?x=1`: 9.B PASS (row N6), 9.C PASS (eight pairs, all C1).
- **Also 9.A (M-11):** the same input makes 9.A treat everything as
  repeated; the reviewer's runs gave FAIL with a `main` landmark and
  DOES NOT APPLY without one. One fix covers all three tests.

### Security, in modes the demo plan turns on

Both are off by default (`AUTH=none`, `JUDGE_BACKEND=client`).
The round 2 check uses the server judge; the VAST step uses sign-in.

#### B-01 Server judge: a page can make the server read picture files outside the run

- **What is wrong:** the server judge collects every `run://...png` it
  finds anywhere in a question's input and opens it as a path under the
  run folder. Question inputs hold page text (names, labels, links). A
  page that puts `run://x/../../other.png` in a link's name makes the
  server open that file and send it to the judging model. The run id in
  the link is ignored.
- **Why it matters:** page content chooses a file the server reads
  (principle 5), and in hosted mode it reaches another user's
  screenshots, past the owner check. Only `.png` files, and only when
  `JUDGE_BACKEND=api` with a type switched on, which is what the round 2
  check in the demo plan does. The pictures attached to agent results go
  through the guarded reader and are not affected.
- **Where:** `src/tobi508/apijudge.py:380-416` (`_links`, `pictures_of`).
- **Smallest fix:** resolve each link with `resources.runs.run_file` (it
  already refuses `..`, other runs and other owners) and require the
  link's run id to be this run. Better: take links only from input
  values that are exactly a link, as `inline._links` does, never from a
  search of the text.
- **Checked:** verified (run). `pictures_of` with input
  `run://r1/../r2/evidence/other.png` returned run r2's picture;
  `run://r1/../../secret.png` returned a file two folders up.

---

#### A-01 Hosted mode: one signed-in user can list and collect another user's run

- **What is wrong:** jobs are kept in one list for the whole server, with
  no owner. `tobi_run_status` with no `job_id` lists every job still
  running, for every user, with its job id and URL. Anyone can then wait
  on that job id and receive the finished result. Run folders are
  protected by an owner check; the job's result is not.
- **Why it matters:** with `AUTH=oidc` this leaks which pages another
  person is testing and their findings and page text. It is the first
  thing to close before the VAST step of the demo plan.
- **Where:** `src/tobi508/jobs.py:57-58, 98-99`;
  `src/tobi508/tools/run_status.py:75-96`;
  `src/tobi508/pipeline.py:1572-1585` (`outstanding`).
- **Smallest fix:** store `access.caller()` on the job when it starts;
  `get`, `all_jobs` and `running` return only the caller's jobs. A test
  beside `tests/test_access.py`.
- **Checked:** verified (read). `Job` has no owner field; `outstanding`
  adds running jobs to its list before any owner check. Not exercised
  with two real tokens.

---

## P1

A wrong result, crash or hang in plausible conditions, or large waste.

### What a calling agent pays

Measured in phase 1 on `tests/fixtures/budget/agency-home.html` (default
tests: 22 findings, 10 open questions, 2 answer rounds), through an
in-process MCP client. Tokens are characters divided by 4.

| Step | Tokens |
| --- | --- |
| Tool list and server instructions, before any call | 12,700 |
| Run result (8,500 text, about 2,100 for 8 pictures) | 10,600 |
| Two answer results | 5,500 |
| `tobi_run_status` | 150 |
| `tobi_explain` for the whole run | 9,500 |
| Reading `report.json` to save it | 37,100 |
| Reading `pre-scrt.json` to save it | 17,400 |
| **What the agent reads** | **about 93,000** |
| Writing both files into the user's repository, if the model copies them | 54,500 more, as output |
| If the client also passes on `structured_content` | 21,800 more |

A one-control page (`no_trap.html`) reads about 50,000, so roughly
30,000 of every session is fixed cost.

#### T-01, T-02, T-03, G-01 Saving the two report files is more than half the session

- **What is wrong:** every result tells the agent to read `report_uri`
  and `pre_scrt_uri` and save them. An MCP client has no "save this
  resource" step, so both files pass through the model, in and then out.
  `pre-scrt.json` is 62,000 to 70,000 characters for any page, even a
  one-test run: 61 rows of fixed catalogue text, with the page's own part
  under 5,000. `report.json` is written indented (148,000 characters
  where 97,000 would do) and stores every answered question twice, once
  in `questions` and again inside each answer.
- **Why it matters:** about 55,000 tokens to read and the same again to
  write, on a page that costs 28,000 for everything else. The output
  half is the slow and costly kind. On real pages it cannot be done at
  all: the 27 saved runs of round 2 (svs.gsfc.nasa.gov, an earlier
  version of the code) have reports averaging 169,000 characters (the
  largest 619,000) and pre-SCRT files averaging 720,000 (the largest
  5.6 million). A client cuts a file that size, and the agent saves a
  cut file without knowing.
- **Where:** `src/tobi508/models.py:709-712` (`SAVE_HINT`) and the `todo`
  line; `src/tobi508/runlog.py:56-63` (indent 2);
  `src/tobi508/models.py` (`RecordedAnswer` holds the whole question);
  `src/tobi508/scrt.py` (`write_for_run`).
- **Smallest fix:** ask the agent to save `report.json` only, and offer
  the pre-SCRT file when the user wants it; write `report.json` compact
  and keep only the question id in each answer (check the readers in
  `scrt.py` and `compare.py` first). Expected: about 18,000 tokens to
  read where it is 54,500 now. A way to save without the model (a
  download link when hosted) is the larger fix.
- **Checked:** verified (run) for the sizes, against the run folders of
  my own test runs: `report.json` 148,364 characters indented and 97,466
  compact on agency-home; `pre-scrt.json` 62,557 for a one-test run.
  The round 2 sizes are from `evals/judging/round2/results/` (G-01).
  That the model copies the files out is likely, not measured with a
  real client.

#### A-02, T-04 The tool list costs 12,700 tokens, most of it output schemas, and every result is sent twice

- **What is wrong:** the five tools cost 48,400 characters before any
  call. Output schemas are 31,600 of that (`tobi_run_status` 11,200,
  `tobi_run_tt_tests` 9,300, `tobi_answer_questions` 7,800). They repeat
  every field description, and an agent cannot use them. Each result is
  also sent as JSON text and again, identical, as `structured_content`
  (32,045 and 32,056 characters on the run above).
- **Why it matters:** about 8,000 tokens per session buy nothing, and a
  client that passes on both copies pays for every result twice
  (21,800 tokens on this page).
- **Where:** return annotations in `src/tobi508/tools/run_status.py:36`,
  `run_tt_tests.py:196`, `answer_questions.py`, `read_report.py`;
  `src/tobi508/inline.py:222-251`.
- **Smallest fix:** register the tools with no output schema and return
  text content only. Check how `tests/test_tools.py` reads results first.
- **Checked:** verified (run): schema sizes from `mcp.list_tools()`; the
  two copies compared by the phase 1 reviewer. Whether a given client
  shows the model both copies is not measured.

#### A-03, T-07 Every result gives the same instructions three times

- **What is wrong:** "answer the open questions", "call `tobi_run_status`
  with finish=true", "save `report_uri`" and "report NEEDS REVIEW as
  needs review" each appear in `next_step`, in `todo`, and in `todo`
  again as the closing "TO DO" block (four of its five lines are exact
  repeats), as well as in the tool description. Some of the text is
  project history an agent cannot act on ("the fourth development run's
  agent..."). When nothing is left, `next_step` still explains what to
  do while work is incomplete.
- **Why it matters:** 3,049 characters of instructions on the run result
  (`next_step` 1,553, `todo` 741, the block 755) and about as much on
  each answer result: some 1,900 tokens over a three-call session, of
  which 1,200 are repeats.
- **Where:** `src/tobi508/pipeline.py:1316-1440` (`next_step`, `FINISH`,
  `_calls_text`, `todo`); `src/tobi508/inline.py:211-237`.
- **Smallest fix:** keep one channel (the closing checklist), leave
  `todo` out of the JSON, cut `next_step` to one sentence on the state,
  and remove the history.
- **Checked:** verified (read) that `todo` is in the JSON and in the
  closing block; sizes measured by the phase 1 reviewer.

### The server judge and its gate (demo plan, steps 3 and 4)

The round 2 check runs with the server judge answering and decides
which question types to switch on. These are what to settle before
its figures are used. B-01 (P0) belongs with them.

#### L-02 and L-03 A question type passes the gate on one clean cell, and wrong DOES NOT APPLY never counts

- **What is wrong:** the gate passes a type that has no wrong PASS and
  few wrong FAILs. It asks for no minimum number of cells, counts
  "unsure" as a cell, never reads the wrong DOES NOT APPLY count, and
  puts "tool PASS where the key says DOES NOT APPLY" in a bucket it
  never reads.
- **Why it matters:** the gate's output is the list of types Abby would
  switch on. A type judged on one page, or one that turns failures into
  DOES NOT APPLY, shows as passing.
- **Where:** `evals/apijudge_gate.py:62-85` (`passes`);
  `evals/scoring.py:104, 206-217`.
- **Smallest fix:** a minimum of decided cells (agree plus wrong, not
  unsure) with "too few cells to judge" as a reason; fail a type on any
  wrong DOES NOT APPLY; count PASS against a DOES NOT APPLY key
  separately. Decide the numbers in the plan.
- **Checked:** verified (run). `passes()` returned "passes" for a type
  with one cell, and for a type with 6 wrong DOES NOT APPLY in 10 cells.

#### B-02 Server judge: page text can close the "untrusted data" block

- **What is wrong:** page data goes to the judging model as JSON between
  `<untrusted_page_data>` tags. JSON leaves `<`, `>` and `/` as they are,
  so page text containing `</untrusted_page_data>` ends the block, and
  whatever follows reads as instructions.
- **Why it matters:** the judge can only pick one of a question's
  choices, but principle 8 lets some answers lead to PASS on the judge's
  word. No test page tries this.
- **Where:** `src/tobi508/apijudge.py:478-484` (`_tag`).
- **Smallest fix:** escape `<`, `>` and `&` in the JSON (`<` and so
  on), and add a page to `tests/fixtures/inject/` that contains the
  closing tag.
- **Checked:** verified (run) for the mechanism: `_tag` leaves the
  closing tag intact inside the data. Whether the model then obeys is
  not tested.

#### A-05 "A person decided this" is the calling agent's own claim (roadmap Now, item 4)

- **What is wrong:** an agent may send `decided_by: "human"`. Nothing
  checks it. Such an answer skips the rule that a picture question needs
  `seen`, and outranks every other agent answer.
- **Why it matters:** the picture rule exists because agents answered
  without looking; this is the way round it. No check turns "human" into
  a PASS by itself.
- **Where:** `src/tobi508/tools/answer_questions.py:48-52`;
  `src/tobi508/judgment.py:103-105, 175-180, 191-195`.
- **Smallest fix:** as the roadmap says: record every answer arriving
  through MCP as the agent's (`decided_by` model), and apply the picture
  rule to all of them.
- **Checked:** verified (read).

#### G-02 Server judge: one screenshot is attached once for every question that names it

- **What is wrong:** pictures are gathered per question and joined with
  no check for repeats. Several questions of one test name the same
  screenshot, so one request carries it many times. Cutting and
  encoding them runs on the event loop, and again for each question
  asked a second time.
- **Why it matters:** every copy is paid for as picture tokens and
  counts against the 40-picture limit, which splits the work into more
  requests. In round 2's saved reports one picture is named by up to 19
  questions.
- **Where:** `src/tobi508/apijudge.py:403-416` (`pictures_of`),
  `567-597` (`build_requests`).
- **Smallest fix:** one attachment per link in a request; cut each
  picture once per run; build requests in a thread.
- **Checked:** verified (read): `build_requests` joins each question's
  pictures as they come. The reviewer built a request for 19 questions
  naming one picture and got 19 copies.

#### B-04 Server judge: judging holds a browser slot and sits outside every time limit

- **What is wrong:** the judge phase runs inside the same slot as the
  browser work, after the browsers have closed, for up to `JUDGE_CAP_S`
  (900 s).
- **Why it matters:** with the default of two slots, two runs being
  judged block every other run for up to 15 minutes while no browser is
  in use, and a job can run past `MAX_RUN_S`.
- **Where:** `src/tobi508/pipeline.py:1214-1215`;
  `src/tobi508/jobs.py:78-83`.
- **Smallest fix:** release the slot before judging (run the judge from
  the job wrapper, after the browser part returns).
- **Checked:** verified (read).

### Hangs and waste

#### G-03 `tobi_answer_questions` is the one tool with no time limit

- **What is wrong:** CLAUDE.md says a tool call returns within
  `CALL_WAIT_S` (45 s) and longer work goes on as a job. A run does
  that. An answer call does not: it waits for the whole answer step,
  which replays the page for each answer that names a key or a field
  (4.A, 4.B, 4.C, 5.F), one check after another, with no hard stop.
- **Why it matters:** a client that gives up at 60 s drops the call; the
  work goes on in the server, its result is lost, and the agent sends
  the same answers again while the first call is still writing the
  report (the lost-update race, B-03). The server judge uses the same
  path.
- **Where:** `src/tobi508/tools/answer_questions.py:88-95`;
  `src/tobi508/pipeline.py:1450-1474`.
- **Smallest fix:** run the answer step as a job, as a run is, and give
  each check's resume a hard limit that records "not finished".
- **Checked:** verified (read). How long a resume takes on a large page
  is not measured.

#### W-01 Counting flashes stops the whole server for 15 to 19 seconds

- **What is wrong:** 3.A decodes and counts its 181 captured frames
  with numpy on the event loop.
- **Why it matters:** while it runs, the other run in the server, its
  progress line and every client connection stand still. With two runs
  at once on a hosted server this is a visible stall.
- **Where:** `src/tobi508/checks/t3a.py:291`;
  `src/tobi508/flash.py:56` (`linear`), `522` (`analyze`).
- **Smallest fix:** call the three `analyze_*` functions through
  `asyncio.to_thread`; replace the per-pixel power in `linear` with a
  256-entry table (about ten times faster).
- **Checked:** the reviewer timed `flash.analyze` on 181 frames of
  1024 x 768: 14.6 s to 19.0 s. Verified (read) that the call is made
  directly from the async function; I did not repeat the timing.

#### E-10 4.A loads the page once for every item a hover reveals

- **What is wrong:** the spec budgets one replay for each stop whose
  hover revealed something, at most 10. The code then loads the page
  again for each revealed item, to read its name and address, with no
  cap and no time check.
- **Why it matters:** a menu of 30 items behind one stop costs 30 more
  loads, about 3 s each, to fetch what one load would give.
- **Where:** `src/tobi508/checks/t4a.py:559-563, 731-750`.
- **Smallest fix:** one load per stop that describes every item; check
  the deadline before each.
- **Checked:** verified (read) by the reviewer; not timed.

#### E-11 4.B and 4.C each send the whole page text, with no cap

- **What is wrong:** when both have open questions, the full text of
  every frame goes out twice (two loads of the same page), unbounded.
  4.B's 20 sentences are in it a third time.
- **Why it matters:** tens of thousands of characters on a long page,
  in every result that still has those questions.
- **Where:** `src/tobi508/checks/t4b.py:498-499`;
  `src/tobi508/checks/t4c.py:1505-1506`;
  `src/tobi508/pipeline.py:727-736`.
- **Smallest fix:** send one copy; cap it and say so; for 4.B send the
  sentences with a little context.
- **Checked:** verified (read) by the reviewer; not measured on a page.

### Wrong outcomes

A wrong FAIL or NEEDS REVIEW, or a PASS or DOES NOT APPLY that needs
a narrower page or an agent's wrong answer than the P0 items do.

#### E-06 Three questions settle a PASS on the agent's word and are not on principle 8's list (needs Abby)

- **What is wrong:** principle 8 lists the questions a careful tester
  settles by looking. 4.A's "is there another way to do this" (PASS,
  row M5), 4.A's "is this tooltip essential" (PASS, M13) and 4.B's "is
  timing required" (PASS, M3) each pass on one answer with no key press
  to confirm, and none is on the list. The 4.A and 4.B specs say
  principle 8 covers them.
- **Why it matters:** one agent answer turns a mouse-only control or a
  real timing instruction into PASS. Either CLAUDE.md or the checks are
  out of date.
- **Where:** `src/tobi508/checks/t4a.py:1042-1047, 1075-1080`;
  `src/tobi508/checks/t4b.py:376`; CLAUDE.md principle 8.
- **Smallest fix:** your call: add the three to the list, or add a
  check for 4.A's M5 (press Enter on the stop the agent names and
  compare what it does with the mouse-only control).
- **Checked:** verified (read) against CLAUDE.md's list.

#### E-05, E-09 4.B shows the agent 20 sentences at most, and misses "press Enter twice"

- **What is wrong:** 4.B finds sentences with timing words and asks the
  agent about them. Only the first 20 are sent, each cut at 300
  characters, with no note. And the word list is narrow: "press twice"
  matches; "Press Enter twice", "within 2 secs", "double-click" and
  "tap twice" do not. No match at all is PASS (row M1).
- **Why it matters:** a page that says "quickly" 20 times before "press
  and hold Space for 3 seconds" gives the agent 20 harmless sentences,
  and "no timing" is PASS. A page that says "Press Enter twice to
  confirm" passes with no question.
- **Where:** `src/tobi508/checks/t4b.py:25, 30-35, 117`; spec 4.B
  section 2 (the word list).
- **Smallest fix:** when the cut applies, add "N more sentences were
  not shown" as an unfinished reason; put sentences with the stronger
  words first. Widening the list is a spec change.
- **Checked:** E-05 verified (read): line 117 cuts to 300 characters
  and 20 entries; the reviewer's run showed 20 matches, none with
  "hold". E-09: the reviewer ran the pattern on seven sentences.

#### E-04, E-13 4.A's "the tooltip's text is also on the page" is too easy to meet

- **What is wrong:** a `title` passes without a question when its text
  is "available elsewhere". Two tests do that. One is a plain substring
  of the whole page text: the title "Open" is found in "Opening
  hours". The other is equality with the control's accessible name:
  for an icon button whose only label is its `title`, the name comes
  from the title, so they are always equal.
- **Why it matters:** the question "is this tooltip essential" is never
  asked for the case its own rubric gives as essential ("the only
  label of an icon-only control").
- **Where:** `src/tobi508/checks/t4a.py:659`; spec 4.A, row M11 and the
  J2 rubric.
- **Smallest fix:** match whole words with a minimum length, and
  compare the title with the visible text or `aria-label` only. Spec
  wording to match.
- **Checked:** verified (run). A link with `title="Open"` beside
  "Opening hours": row t2:M11, no question. A button with only an icon
  and `title="Delete all records"`: 4.A PASS, row t1:M11.

#### F-06 4.E fails a page that only changes the `#fragment` on focus

- **What is wrong:** 4.E counts every "frame navigated" event as the
  page going somewhere. Chrome also reports that event when a script
  sets `location.hash` or calls `pushState`. The spec says a change of
  fragment only is not a change of context.
- **Why it matters:** a wrong FAIL ("the page goes to another address")
  on tab lists and section menus that update the address as focus
  moves.
- **Where:** `src/tobi508/checks/t4e.py:77-81, 92-95, 176-177`.
- **Smallest fix:** count a navigation only when the address without
  its fragment changed, or the document reloaded.
- **Checked:** verified (run). A link whose focus handler sets
  `location.hash`: 4.E FAIL, rows e1:M4, G2.
- **Fixed:** with C-03 above. A second cause was behind it:
  `traverse._focus_events` counted focus events per frame address
  including the fragment, so after a fragment change every earlier event
  was read again and 4.E said "focus jumps" (M6). It now counts by the
  address without its fragment. The review's page prints 4.E PASS.

#### F-01 4.D is NEEDS REVIEW for any menu with seven or more items

- **What is wrong:** inside a menu or tab list, 4.D presses the arrow
  key six times and then stops on the seventh item without the closing
  step, so that item has no "after" picture and counts as "could not
  be compared". The spec says the first five items stand for the rest.
- **Why it matters:** a clean page with an ordinary navigation menu
  never gets a 4.D PASS.
- **Where:** `src/tobi508/checks/t4d.py:675-686` (the loop),
  `619-620`.
- **Smallest fix:** after the loop, press the opposite arrow once and
  judge only the first five items.
- **Checked:** verified (run). A menubar of 8 items, each with a clear
  outline: 4.D NEEDS REVIEW, naming "Item 7".

#### F-12 4.F treats an element it could not measure as "no order problem"

- **What is wrong:** 4.F's order signals need each stop's position and
  place in the page. When that reading fails for a stop, the stop is
  skipped by every signal, and the "unreliable" flag is only looked at
  for stops a signal names, which a skipped stop never is.
- **Why it matters:** a page whose stops could not be measured has no
  signals, and "no signals" is PASS.
- **Where:** `src/tobi508/checks/t4f.py:129-147, 208-221, 234-278,
  621-625, 762`.
- **Smallest fix:** when any forward stop has no measurements, mark the
  page instance unreliable (row M1, NEEDS REVIEW).
- **Checked:** verified (read). Not reproduced on a page: neither the
  reviewer nor I found a cheap page with an unreadable stop.

#### F-15 4.F shows the agent only the first 60 stops and does not say so

- **What is wrong:** the spec says a page with more than 60 stops gets
  one order picture per 60. The code makes one picture with the first
  60 numbered and lists only those. Signals are still computed on all
  stops, so a signal at stop 120 reaches the agent as words with no
  badge and no row, under a caption that says the picture shows "the
  whole page".
- **Why it matters:** the agent's "the order makes sense" is a PASS
  (principle 8 allows it for 4.F), given here on evidence that leaves
  out the stops in question. The rubric's "answer unsure if the
  picture does not show them" is the only guard.
- **Where:** `src/tobi508/checks/t4f.py:472, 549-553, 661-680,
  700-705`; spec 4.F, "Order image".
- **Smallest fix:** build the pictures the spec describes, or, when a
  signal's stop is past 60, add a "stops after 60 were not shown"
  reason, which makes the page NEEDS REVIEW.
- **Checked:** verified (read): four places cut at `BADGE_MAX` and the
  spec line is there. No fixture has more than 60 stops.

#### C-02 The reveal pass credits a trigger with whatever appeared meanwhile

- **What is wrong:** "opened" means any element visible after the press
  that was not visible before, anywhere on the page. On a page with a
  live feed, a ticker or a late banner, a trigger that does nothing is
  recorded as opened; its real content is never read, and the reveal
  guard sees nothing wrong. The pass also never checks that the
  trigger took focus before pressing Enter (C-04).
- **Why it matters:** a PASS with unread content on any self-updating
  page.
- **Where:** `src/tobi508/reveal.py:312-331, 400-403, 306-312`.
- **Smallest fix:** count only what is new inside the region the
  trigger controls, or after `aria-expanded` flipped; a trigger that
  did not take focus is "not found".
- **Checked:** verified (run). A do-nothing trigger, a hidden
  unlabelled field, and a list growing every 300 ms: 5.A PASS.

#### K-05 9.C passes pairs where neither side has a name (needs Abby)

- **What is wrong:** row C1 is "names agree". Two controls with no name
  at all agree, so a pair of unnamed icon buttons is a PASS, and the
  summary says they "have the same names for screen reader users".
- **Why it matters:** a PASS resting on no names. Whether an unnamed pair
  is a 9.C matter or only a 4.1.2 one is a spec decision; today the code
  decides it silently.
- **Where:** `src/tobi508/checks/t9c.py:285-298`; spec 9.C section 3a,
  rows C1 and C2.
- **Smallest fix:** a row before C1: both names empty is NEEDS REVIEW (or
  the pair is left out with a note). A MINOR spec change.
- **Checked:** verified (run). Two pages, each with the same nameless
  icon button and nameless icon link in the header: 9.C PASS, four pairs,
  all C1.

#### K-04 9.C pairs every `javascript:` link with every other, and FAILs unrelated controls

- **What is wrong:** links are paired "by destination" on their href
  text. `javascript:void(0)` on two pages is the same text, so two
  unrelated controls pair, and a name on one side only is a FAIL.
- **Why it matters:** a wrong FAIL on a common pattern, in a test where
  the roadmap is already cutting false FAILs.
- **Where:** `src/tobi508/checks/t9c.py:131, 203`;
  `src/tobi508/site.py:314-323` (`norm_href`).
- **Smallest fix:** give a link a destination only when it is http, https
  or file; the rest fall through to id, name and place.
- **Checked:** verified (run). An unnamed `javascript:void(0)` icon link
  on the tested page and a "Close alert" link on the other: 9.C FAIL
  ("has a name screen readers announce on one page and none on other
  page 1").

#### K-03 9.C reads "ANDI named nothing" as "nothing to compare"

- **What is wrong:** after injecting ANDI the code waits a fixed half
  second and reads its output. An empty list counts as "ANDI ran". Every
  control then has no ANDI name, all are dropped, and the result is DOES
  NOT APPLY. Controls ANDI skips one by one (not focusable) vanish
  without a count.
- **Why it matters:** a wrong DOES NOT APPLY if ANDI is slow on a heavy
  page, and silent loss of controls otherwise.
- **Where:** `src/tobi508/checks/t9c.py:141-153, 173-174, 471-477`;
  `src/tobi508/andi.py:126-136`.
- **Smallest fix:** if a page has marked controls and ANDI named none of
  them, return the existing "ANDI did not run" NEEDS REVIEW; say in the
  summary how many controls ANDI left out.
- **Checked:** verified (read). Not reproduced: I did not find a page
  where ANDI is still working after 500 ms, so how often this happens is
  unknown.

#### D-02 A script error while reading the page looks like "nothing found"

- **What is wrong:** `evaluate_top` returns the value of a script and
  never looks at whether it threw. An error comes back as `None`, and
  callers treat `None` as an empty result. For the label pass that is
  "no form fields", the DOES NOT APPLY branch of D-01. `reader.call`
  does the same for "could not reach the element".
- **Why it matters:** any bug in one of these scripts, or a page that
  breaks one, turns into DOES NOT APPLY or an empty label with no error
  anywhere. The sister helper `call_in` does raise.
- **Where:** `src/tobi508/traverse.py:539-546`; callers
  `src/tobi508/labels.py:362, 403`, `src/tobi508/observe.py:42` and nine
  more.
- **Smallest fix:** raise on `exceptionDetails`, as `call_in` does. The
  label pass already turns an exception into a "could not be read" note.
- **Checked:** verified (read). The reviewer ran `evaluate_top("throw
  new Error('x')")` and got `None`; I did not repeat it. No real page is
  known to trigger it.

#### M-10 9.A passes a button that does nothing when the tested address has a `#fragment`

- **What is wrong:** after pressing a possible skip control, 9.A takes
  where focus went. If focus did not move, it takes the element the
  address's fragment points to. When the tested address already ends in
  `#main`, that element is there before any press.
- **Why it matters:** any button before the content (a menu toggle, a
  cookie "OK") then "skips to main" and 9.A passes.
- **Where:** `src/tobi508/checks/t9a.py:62-67` (`LANDING_JS`), `395`.
- **Smallest fix:** count the fragment's target only if it changed with
  the press, or load the page without its fragment.
- **Checked:** verified (run). A do-nothing button, a header, then
  `<main id="main">`: with `#main` on the address 9.A PASS ("the noop
  button lets keyboard users skip it"); without it, FAIL.

#### M-04, M-09 5.H forgets the forms it could not test

- **What is wrong:** 5.F answers NEEDS REVIEW when the page has form
  fields the walk reached none of; 5.H, reading the same pass, says
  "no form to submit". And the list of what was not tested (a form in
  a frame, forms past the fifth, a cut walk) is read only when no form
  has a consequence word. Most pages have "terms" or "order" somewhere,
  so the list is ignored and the agent is asked about the tested forms
  only.
- **Why it matters:** DOES NOT APPLY or PASS for 5.H while a payment
  form in a frame was never looked at.
- **Where:** `src/tobi508/checks/t5h.py:70, 311-335, 343-379`.
- **Smallest fix:** anything in the "not tested" list turns DOES NOT
  APPLY and PASS into NEEDS REVIEW, and the question names the forms
  that were not tested.
- **Checked:** M-04 verified by the reviewer's run (a `tabindex="-1"`
  card field: 5.F NEEDS REVIEW, 5.H DOES NOT APPLY). M-09 verified
  (read); the reviewer called `evaluate` on a built state.

#### M-13 5.G shows the agent every new text on the page, not the text for the field

- **What is wrong:** the spec says 5.G's question gets "the error text
  tied to the field by 5.F". The code sends all new text of the
  attempt, and accepts a quote found anywhere in it.
- **Why it matters:** in a form with an error summary, field B (whose
  own error is just "Invalid") passes on a quote of field A's helpful
  message.
- **Where:** `src/tobi508/checks/t5g.py:71-78, 152-156`; spec 5.G
  section 4.
- **Smallest fix:** when 5.F's answer for the same field has a quote,
  send that text only and require 5.G's quote to be inside it.
- **Checked:** verified (read) by the reviewer; not run (it needs
  agent answers).

#### H-04 5.D: the page's own `aria-controls` can hide a change of content (needs Abby)

- **What is wrong:** 5.D ignores changes inside a field's "own widget",
  which includes anything the field names in `aria-controls`,
  `aria-owns`, `list` or `aria-describedby`, however large.
- **Why it matters:** a select with `aria-controls="main"` that replaces
  the whole main content reads as "no effect" and passes with no
  question. The spec defines the own widget this way; the effect is
  that the page chooses which region is exempt.
- **Where:** `src/tobi508/forms.py:20-39` (`_OWN_JS`), `107-123`.
- **Smallest fix:** never exempt a landmark or `main`, or send a large
  change inside an exempt region to the "is this a change of context"
  question. A spec change.
- **Checked:** verified (run). A select with `aria-controls="main"`
  replacing "Apply for a benefit" with "Payment ... Pay now": 5.D PASS.

#### H-05, H-07 5.B leaves out fields that could not be read, and opened states lose their "not checked" notes

- **What is wrong:** when a field's reading fails (it vanished, or the
  read returned nothing), 5.A and 5.C send it to NEEDS REVIEW. 5.B
  counts it as "has no label, not an item" and drops it, with no note.
  Separately, each opened menu or tab is read with its own cap, time
  check and frame count, and those notes are thrown away when the
  reads are merged, so a partly read opened state looks fully read.
- **Why it matters:** 5.B can PASS, or say DOES NOT APPLY, on the
  fields that happened to be readable.
- **Where:** `src/tobi508/checks/t5b.py:74-118, 289-306`;
  `src/tobi508/labels.py:402-407, 508-525`.
- **Smallest fix:** in 5.B, a field that was not read sets NEEDS
  REVIEW, as in 5.A; merge each opened state's notes into the pass's.
- **Checked:** H-05 verified (run): a field hidden by its neighbour's
  focus handler is row M1 in 5.A and absent from 5.B's one question.
  H-07 verified (read).

#### H-06 5.D reads "the page changed" as "visible text or the number of dialogs changed"

- **What is wrong:** the spec's row M7 is "a dialog appeared or the DOM
  changed outside the field's own widget". The code compares visible
  text and a dialog count. A change of pictures, a canvas, a frame's
  content or layout is "no effect". If either reading fails, the
  comparison is skipped and the result is also "no effect".
- **Why it matters:** missing evidence ends in PASS (row M14).
- **Where:** `src/tobi508/forms.py:107-123`;
  `src/tobi508/checks/t5d.py:352-354, 411-413, 487-504`.
- **Smallest fix:** a failed reading makes the field unreliable (M1);
  count a large number of DOM changes outside the widget as a change.
- **Checked:** verified (read) by the reviewer; I did not run it.

### The tests and CI

None of the wrong outcomes in this review was caught by the suite of
1,204 tests. These five say why, and what the suite costs.

#### Q-01 CI never runs the tests for page text that tries to steer the judge

- **What is wrong:** CI splits the suite into four groups by file name.
  Three name `test_fixtures_4*`, `5*`, `9*`, `19a`, `2*` and `3a`; the
  fourth takes "the rest" but ignores every `test_fixtures_*` file.
  `tests/test_fixtures_inject.py` is in none of them.
- **Why it matters:** its 7 tests are the only ones for principle 5
  (page text as instructions). They can break without CI noticing. The
  comment in the workflow says a new test file is never left out; any
  new `test_fixtures_<name>.py` would be.
- **Where:** `.github/workflows/ci.yml:86-102`.
- **Smallest fix:** add the file to a group; make "the rest" ignore
  only `test_fixtures_[0-9]*`; add a step that fails when the groups
  together collect fewer tests than the whole suite.
- **Checked:** verified (read) in the workflow. The reviewer collected
  each group and found 1,196 of 1,204: the 7 inject tests and the one
  slow test are missing.
- **Fixed:** CI commit below ("CI: every test file in a group"):
  "rest" ignores only `test_fixtures_[0-9]*`, and a `groups` job
  (`scripts/ci_groups_check.py`) fails when the groups collect fewer
  tests than the suite. Run against the old glob it lists the 7 inject
  tests as missing; now 1,203 of 1,203.

#### Q-02 A change to the judge's prompt skips CI altogether

- **What is wrong:** the "docs only" filter treats any `*.md` outside
  `README.md` and `specs/` as documentation. `src/tobi508/
  judge_prompt.md` (the server judge's fixed prompt, hashed into every
  report) and `third_party/andi/LICENSE.md` (a hashed vendored file)
  are Markdown.
- **Why it matters:** a pull request that changes only the judge's
  prompt runs no lint and no tests, and the required check passes.
- **Where:** `.github/workflows/ci.yml:43-49`.
- **Smallest fix:** skip only `docs/*`; everything else is code.
- **Checked:** verified (read): the `case` puts `docs/*|*.md` after
  `README.md|specs/*`, and `*` matches a path with slashes.
- **Fixed:** CI commit below: only `docs/*` is docs-only.

#### Q-03 The hard cases have no fixtures

- **What is wrong:** shadow roots appear in two fixtures, both for 4.C.
  No fixture anywhere has non-Latin text. Frames are missing for 4.A,
  4.B, 4.E, 4.F, 5.A, 5.C, 5.F, 5.G, 9.x and 19.A. Caps and time limits
  are tested end to end only in 4.C. No check other than 4.C is ever
  run on a page with a trap. A form behind a button is missing for
  5.A-5.C and 5.F-5.H.
- **Why it matters:** this is the map of the P0 table. Each class with
  no fixture is a class where the review found wrong outcomes.
- **Where:** `tests/fixtures/`; the reviewer's table of class against
  check is carried into "If we started over", item 3.
- **Smallest fix:** one shared page per class, run against every check,
  asserting "never PASS, never DOES NOT APPLY". The pages in
  [2026-11-11-code-review-pages/](2026-11-11-code-review-pages/README.md)
  are a start.
- **Checked:** the reviewer's greps over `tests/fixtures`; I did not
  repeat them.

#### Q-07 Each end-to-end test costs 5 to 11 seconds, and there are about 590

- **What is wrong:** nearly every rule test calls the whole pipeline,
  which starts its own Chromium, records the page and walks it twice.
  Tests of one page with different answers record and walk it again
  each time.
- **Why it matters:** about 70 CPU-minutes for the suite; four CI jobs
  of 15 to 20 minutes with no timeout set.
- **Where:** `tests/harness.py`, `tests/conftest.py`,
  `src/tobi508/pipeline.py`.
- **Smallest fix:** keep one recording and one walk per fixture page
  (keyed by the file's hash) and let tests that only change answers
  reuse them; move rows that need no page to `evaluate()` on stored
  evidence, as some 4.A, 5.D and 5.H tests already do (10 ms each).
- **Checked:** the reviewer timed four files one at a time: 5.H 8 tests
  in 53 s, inject 7 in 33 s, browser 8 in 12 s, 2.B 15 in 161 s. The
  suite total is an estimate from those.

#### Q-04 Nothing makes anyone rerun the judge eval after a question changes

- **What is wrong:** tests answer every open question with a scripted
  answer, so they test what the rules do with an answer, never whether
  the question and its evidence let a reader answer correctly.
  Principle 6 says to rerun the judge eval after changing a question,
  rubric or input. Nothing checks that it was done.
- **Why it matters:** the items above where the agent is shown the
  wrong evidence (E-05, F-15, M-13) are invisible to the suite by
  design.
- **Where:** `tests/harness.py:40-70`; `evals/judge_eval.py`.
- **Smallest fix:** the eval writes a hash of each question and rubric
  it ran; a fast test fails when the live hash differs.
- **Checked:** verified (read) for the harness; the rest is the
  reviewer's reading.

### Hosted sign-in (demo plan, step 6)

A-01 (P0) belongs here too.

#### S-05 Hosted mode: a sign-in token with no `sub` claim opens every run

- **What is wrong:** the owner check asks "who is calling" and treats
  "nobody" as a local server with one user, where every run is open. A
  signed-in caller whose token has no `sub` claim also comes back as
  "nobody".
- **Why it matters:** under `AUTH=oidc` such a caller can read and change
  every user's runs, and the runs it starts get no owner. It needs a
  token without `sub`; whether VAST's Keycloak always sends one is a
  thing to confirm with the admin, since nothing at startup requires it.
- **Where:** `src/tobi508/access.py:44-55` (`caller`), `76-86`
  (`may_open`).
- **Smallest fix:** under `AUTH=oidc`, a token with no `sub` is refused;
  "nobody" stays open only when sign-in is off. One test in
  `tests/test_access.py`.
- **Checked:** verified (read). Not exercised with a real token.

---

## P2

Shorter entries. Unless marked, these are a reviewer's claim that I have
not checked.

### What a calling agent pays (tokens, time)

- **A-06** `tobi_run_tt_tests`' description is 4,300 characters: it
  repeats what `next_step` says, names "the explain prompt" (agents
  cannot call prompts), gives five timeout numbers and a plan to "ask the
  user" about `no_time_limit` that CLAUDE.md says never happens. The test
  list is paid three times (description, instructions, the `tests`
  default). `tools/run_tt_tests.py:34-101`. Fix: cut to about 1,200
  characters. Sizes verified (run).
- **A-07** The answer tool's input schema is 5,200 characters; its
  description re-lists what the schema says, and the schema shows fields
  the server sets (`answered_by`, `not_viewed`). The agent writes two
  justifications per answer (`rationale` and `choice.reasons`).
  `tools/answer_questions.py:40-69`, `models.py:322-424`. Fix: keep
  server fields off the wire model; drop one of the two texts. Size
  verified (run).
- **A-11, T-08** Results serialize empty and default fields (108 of
  them in the run result above: `note: null`, `unconfirmed: 0`,
  `errors: []` ...) and fields that restate others: `confirmed`,
  `tests`, the 25 `evidence` links (1,228 characters), `final_url` equal
  to `target`, and the TT name and WCAG text on every finding (1,362
  characters). About 900 tokens on a run result and 500 on each answer
  result. `Finding.confidence` is never set. `models.py:559-715`. Fix:
  dump with `exclude_none` and `exclude_defaults`, keeping the
  disclaimer; drop the restating fields.
- **A-10, T-05, T-10** `tobi_explain` for a whole run is 9,500 tokens
  on the page above and has no cap. More than half is text that is the
  same on every run (what the tool does for each test, the TT condition
  and requirements) or that an agent cannot use: 5,500 characters are
  rule codes ("x1:M8; x2:M9", "[M15 NEEDS_REVIEW]") and "technical
  reasoning, for your reference only", which principle 8 says stay in
  the evidence trace. One test (4.D) lists 81 places, because 4.D
  records every stop as an instance, PASS ones included, where its
  spec says PASS instances appear only as a count (F-19,
  `checks/t4d.py:1066-1092`).
  `explain.py:106-132, 177-237`. Fix: per finding, the places and one
  link; cap the places ("N more in the report"); keep the codes in
  `report.json`.
- **A-08, T-06** An answer result sends again what the agent already
  has: the questions still open, in full; their shared texts; and their
  pictures. On the page above the first answer result was 42% repeats
  and re-attached all 7 of its pictures. About 2,500 tokens per answer
  round with questions open. Encoding the pictures also blocks the
  event loop while other runs share it. `inline.py:99-196`;
  `pipeline.py:1494-1522`. Fix: list an unchanged question by id only;
  skip pictures already attached; encode in a thread.
- **M-19** 5.F and 5.G ask one question per field and per attempt,
  each carrying the same list of error texts (up to 200 pieces of 300
  characters): a 5-field form with one page-level message gives 10
  questions in 5.F and 10 in 5.G. `checks/t5f.py:959-1026`,
  `checks/t5g.py:144-174`. Fix: one question per attempt with a list
  of fields, the error list sent once.
- **T-09** One 4.F question is 7,900 characters, 45% of all question
  text on the page above: its `order` list carries every item, each
  with an empty `page_box`. Five 4.A questions are the same question
  with a different element (574 characters each).
  `checks/t4f.py`, `checks/t4a.py`. Fix: list only the items whose
  order differs, with a count; ask the five as one question with a
  list. 4.F also repeats the whole list in every question (the page
  question plus up to six for opened menus, about 6,800 characters
  each), where `shared_inputs` would send it once (F-17,
  `t4f.py:661-707`).
- **B-08** Other pages are recorded one after another before the walk
  starts: 5 pages can add 100 s, 50 pages 1,000 s. `pipeline.py:939-1032`.
  Fix: record them beside the walk, two or three at a time.
- **K-08** 19.A repeats its live site search on every follow-up run (up
  to 20 s each). `checks/t19a.py:217-218, 483-493`. Fix: carry the
  earlier result into the follow-up.
- **K-09** 9.C loads every page twice (once for ANDI, once for the site
  read) plus a fixed half second per page. `checks/t9c.py:262-269`.
  Fix: build the site read from the ANDI load.
- **K-11** 9.B stores every out-of-order pair (about n²/2 for a reversed
  menu) and 9.C writes one sentence per failing pair, with no cap; the
  agent sees 5. `checks/t9b.py:115-126`, `checks/t9c.py:490-505`. Fix:
  a count plus the first 20.
- **B-18** Each judge round rebuilds the whole agent-facing result (every
  check resumed, every evidence file rewritten, the workbook
  regenerated, `fit()` run) and throws it away. `apijudge.py:808`.
  Fix: split "apply answers" from "build the result".
- **D-07** Each Tab press costs about 8 Chrome round trips to read focus,
  then 3 or 4 more per frame. The walk's presses are most of a run.
  `traverse.py:564-752`. Fix: cache the top frame id; one call for
  focus, URL and description.
- **D-12** The label pass does fields × elements × other fields work:
  2.4 s for 60 fields on a modest page (the reviewer timed it).
  `labels.py:160-277`. Fix: test the cheap region check first.
- **D-13** A fixed half-second sleep after every ANDI injection,
  repeated for every opened state (tens of seconds in the worst case).
  `labels.py:445`. Fix: poll for ANDI's rows.
- **H-13, H-14** The label pass is one load, but every opened state
  (up to 20 triggers plus 3 sets each, 80 loads at worst) repeats the
  full read: a scan and a screenshot per field, ANDI, the half-second
  sleep. 5.D spends about 1.5 s of fixed waits per field (a 300 ms
  noise window per action, a 1,000 ms second look after every Tab),
  writes a "before" picture for every field though only a content
  change uses it, and after each change of context refills every
  earlier field. `labels.py:160-277, 423-445`; `checks/t5d.py:301-302,
  374, 515-535`.
- **W-08, W-15** Any `IntersectionObserver` below the first screen
  (lazy images, analytics) triggers a second full 6.5 s watch: 18.7 s
  against 11.0 s on a static page (the reviewer's run). For a run of
  4.x tests only, the watcher still decodes audio and animated images
  and makes crops that nothing reads, and the walk does not get its
  "stop waiting on this content" list until both watches end.
  `motion.py:1591-1659`, `pipeline.py:1058-1075`. Fix: scroll inside
  the first watch; a light mode when no 2.x test is selected.
- **D-14** The reveal pass computes a path for every element three or
  more times per trigger, and once more only to read the frame chain.
  Its cap of 6,000 elements is silent. `reveal.py:81-91, 267-330`.
- **D-15** Every replay and reveal load runs a whole-page inventory that
  only the walk reads. `traverse.py:1022-1037`. Fix: make it optional.
- **D-06, D-08** Reading focus opens a Chrome session for every frame
  on each miss and never closes them; the settle rule counts 50 ms per
  poll whatever the poll took, so a busy page waits well past its 1.5 s
  limit. `traverse.py:390-411, 835-851`.

### Outcomes and gaps (each stays NEEDS REVIEW or needs a narrow case)

- **B-03 and A-04** Two calls that change one run at the same time lose
  work: each reads `report.json`, waits on the browser, and writes the
  whole file back. Two overlapping answer calls drop the first one's
  answers after telling the agent they were accepted; an answer call
  overlapping `tobi_run_status(finish=true)` can start the same
  follow-up run twice. `pipeline.py:1443-1483, 1536-1569`. Fix: one lock
  per run id around read-change-write; write to a temporary file and
  rename. Verified (read). See "Refuted" for the half-written-file part.
- **B-06** An exception in one check's rules ends the whole call with a
  tool error, no findings for any test, and a run folder left behind.
  In the answer path the answers just given are lost. `pipeline.py:759-806`
  has no handler. Fix: catch per test and return "could not be
  evaluated" for that test. Verified (read).
- **K-12** 9.B counts a plain `<header>` and `<footer>` as matched
  navigation, which can be enough to reach PASS. The spec says such
  regions "do not match". `checks/t9b.py:92-99, 149`. I tried one
  different-template pair and got NEEDS REVIEW (the kinship rule caught
  it); a pair sharing two or three texts is not tried. Fix: leave
  position-only regions out.
- **K-06** 9.C differs from its spec in two places: same-address pairs
  ignore the region, and "dropped" (C5) is decided before the table, so
  it can win over C2. `checks/t9c.py:203-222, 316-321`.
- **K-10** The site read reads the page straight after load, with no
  settle step; a menu drawn just after load is missing, which gives DNA
  or FAIL (see K-02 for the same effect). `site.py:248-256`.
- **D-10** When Enter opens nothing, the reveal pass clicks at
  coordinates measured inside the trigger's frame but applied to the top
  page, so it clicks the wrong thing for triggers in frames.
  `reveal.py:96-108, 319-327`.
- **D-04** Changes inside server-rendered shadow roots (`<template
  shadowrootmode>`) are invisible to the settle rule and to "what did
  this action change". `traverse.py:110-113`. The reviewer confirmed it
  with a script.
- **D-16** Two failed reads compare as equal, so an action that could
  not be observed reads as "no effect"; dialogs in frames or shadow
  roots are not counted; `#nav` matches `#nav-link`.
  `observe.py:162-218, 301-320`.
- **D-05, D-09** After a frame navigates, its cached Chrome context is
  stale and the frame silently contributes nothing; focus events are
  keyed by frame URL, so two frames with one URL lose events (4.E reads
  them). `traverse.py:390-437, 775-784`.
- **D-11** Reading a field calls `checkValidity()`, which fires the
  page's own `invalid` handlers and can make error text appear before
  anything is submitted. `forms.py:92-93`. Fix: read `validity.valid`.
- **D-17** Reveal tries 3 sets and 2 options per set and says nothing
  about the rest; the label cap of 60 counts buttons with fields, so
  many buttons before a form hide its fields. `reveal.py:40-41, 428-450`,
  `labels.py:21, 389-393`.
- **B-13** After an answer call, a test left out over a cap loses its
  "run again with no time limit" reason and shows an unrelated error
  list. `pipeline.py:1475`. Still NEEDS REVIEW.
- **B-07** On refusal the run folder is deleted while the motion watcher
  is still writing into it, which can recreate it; a browser that fails
  to start leaves the folder. `pipeline.py:894-895, 1104-1108, 1193-1203`.
- **2.x and 3.A gaps (N-05, N-10, N-14)** The watcher records its own
  limits and no check reads them: frames it could not read, the change
  log stopping at 1,500 records, 40 regions, unmapped tiles. 2.D can
  PASS on the changes that were recorded (`motion.py:166-181, 933-940`;
  `t2d.py:62-72`). 2.A ignores media past the 20th element and treats
  an embedded player as audio only when its address has `autoplay=1`
  (`motion.py:392`, `t2a.py:44-47`). In 2.D, any dialog or any focus
  move during the watch counts as "with the change", so an unrelated
  cookie dialog sends a silent ticker to a question where FAIL was due
  (`t2d.py:53-76`).
- **Watchers (W-06, W-10, W-12, W-16)** The capture's start time is
  counted from a different zero than the watcher's, and is ignored when
  the screen recording also saw something, so a flash on a slow page
  is found but not measured (NEEDS REVIEW where NOT TESTED with an
  assessment was due; `t3a.py:278-283`). Every timer of a second or
  more is a 2.C hint, so a static page with a 60 s heartbeat is 2.C
  NEEDS REVIEW ("a timer of 60 s, longer than we watched"; the
  reviewer's run; `motion.py:131-143`, `t2c.py:86-88`). A screen
  recording that fails leaves no "not measured" entry
  (`t3a.py:221-229`). In the mechanism probe, content whose CSS path no
  longer matches after a control re-renders it counts as "stopped",
  which credits the control (`mechanism.py:228-241`; not reproduced).
- **2.x, English only (N-12, N-15)** A text is offered to the agent as
  a possible "how to pause" instruction only if it contains an English
  word such as pause, stop or mute; a Spanish page's instruction counts
  as "no", and the result can be FAIL "no way to pause"
  (`t2c.py:38-46, 191-198`). 2.B's check that "essential" is not just
  "loading" searches the agent's reason for the word "load".
- **2.x, no guard on FAIL (N-13)** PASS cannot be reached in 2.A-2.C
  today, because row E2 needs test 13.A, which is not built; that is
  what keeps "a working mechanism is NEEDS REVIEW" true. The guard for
  recordings that lack code holds back a PASS only, so a pause button
  that needs code the recording lacks gives FAIL "no way to pause".
- **4.A-4.C gaps (E-12, E-14, E-15, E-16)** In 4.A a frame whose scan
  throws counts as scanned, a stop that cannot be located is not
  hovered, and targets past 200 in a frame are dropped, all without a
  note (`t4a.py:164, 409-414, 513-515`). In 4.C, `aria-modal="true"` on
  any ancestor turns "Enter gets out" into PASS, so page markup picks
  the row (`traverse.py:269`, `t4c.py:977-981`); and a page whose focus
  cycles forever passes once the agent answers "no" (row M10). 4.B's
  key-press proof never checks the deadline (up to 30 s past the
  limit) and a frame whose text cannot be read leaves no trace
  (`t4b.py:156-257`).
- **4.D gaps (F-03, F-05, F-20)** A dropped-focus FAIL skips the
  "unreliable step" check that 4.E applies to the same step, so 4.D can
  FAIL where 4.E says NEEDS REVIEW (`t4d.py:565-586`). The second pass
  does not re-read stops whose first reading was later rejected, so
  they stay NEEDS REVIEW (`t4d.py:369-376`). When neither arrow key
  moves inside a widget, its items are not tested and nothing says so,
  and the page can PASS (`t4d.py:658-708`).
- **4.E gaps (F-07, F-08, F-09)** The control replay waits a fixed 2 s
  where the spec says "as long as the original step took", so a slow
  timed redirect is blamed on focus; each dialog costs a full replay
  and uses up the limit of 10 (`t4e.py:34, 282-356`). Dialogs in frames
  or shadow roots, or built without a dialog role, are not seen, and a
  failed dialog read is taken as "none" (`observe.py:51-77`,
  `t4e.py:86-88`). An unreliable step with no signal found does not
  hold back a PASS; that follows the spec, and is a question for Abby.
- **4.F gaps (F-13, F-14, F-16)** A backward pass that gets stuck is not
  "incomplete", so the backward order goes unchecked
  (`t4f.py:597-606`). In the dialog check, focus landing on the page
  body counts as staying inside the dialog (`t4f.py:440-455`). A
  replay that fails in `_reveal` is outside the `try` and ends the
  whole check (`t4f.py:341`).
- **5.D gaps (H-09, H-11)** When a before or after screenshot fails,
  the "covers more than half the window" guard is silently off and
  "content only" passes (`t5d.py:267-274, 416-450`). A field that only
  changes the `#fragment` is reported as navigation, the same mistake
  as F-06 (`observe.py:302`). The second look after leaving a field
  re-reads focus only, so a navigation 1.2 s after blur is missed. The
  spec's "unsettled step" in M1 has no code.
- **5.A-5.C silent caps (H-12)** Nearby text is cut at 400 characters,
  neighbours at 6, the scan at 3,000 elements, none reported; 5.C then
  compares only what was kept. `labels.py:24, 234-268`.
- **5.F-5.H and 9.A gaps (M-14, M-16, M-17, M-18)** 9.A FAILs a
  repeated block that holds nothing to tab through (two static
  sentences) with "add a skip link", ignores toggles that are not a
  link or button, and presses Enter only (`t9a.py:152-163, 336-337`;
  the first is the reviewer's run). 5.H's "there is a review step"
  answer passes even when the form left the page and nothing could be
  seen (`t5h.py:152-153`). A failed reading after the submit press is
  not an "unfinished" reason, so it ends as "the page did not check"
  (`t5f.py:217-221, 1229-1256`). 5.F presses Enter on a `role="button"`
  where its spec says Space, and its word lists differ from the spec's
  (`t5f.py:50-59, 436`).
- **4.F, for Abby:** the answer "order does not matter" on the page
  question makes the whole test DOES NOT APPLY on the agent's word,
  even when a split form group was the reason for asking. That is what
  rows M8 and G4 say today.
- **Core gaps (C-05, C-06, C-07)** The reveal summary lists triggers
  that did not open but not options that could not be chosen or read,
  so the guard cannot see them (`reveal.py:177-200, 442-462`). A replay
  does not say when it landed on a different element than the walk
  did; 4.A, 4.B, 5.D and 9.A check for themselves, 4.E's control replay
  and "before" picture do not (`traverse.py:1166-1206`). When a script
  moves focus off an element the moment it arrives, that element is
  never a stop and 4.D passes the rest: 10 of 11 links, verified (run),
  while 4.E and 4.A on the same page do object (`traverse.py:906-962`).
  Whether an element Tab can never rest on belongs in 4.D is a spec
  question.
- **G-04** A run stopped at the default limit (1,800 s) is told it
  "reached its time limit (600 s)" and to "run again with
  no_time_limit=true", which it already was; an agent that obeys
  repeats a 30-minute run. `pipeline.py:86-92, 1187-1192`. Fix: word the
  note for the limit that applied.
- **G-06** A follow-up run the server starts itself (19.A's suggested
  pages) can fail without anyone hearing: the call is already removed
  from the report and marked made, the failed job is skipped in the
  list, and the next `tobi_run_status` says "Nothing is left".
  `pipeline.py:1553-1560, 1586-1587`. Fix: list failed follow-ups and
  put the call back.
- **G-07** A follow-up call that needs the user's choice (run again with
  no time limit) can never clear: it stays in the report whatever the
  user says, and every result tells the agent to repeat "until nothing
  is left". `pipeline.py:1477-1483, 1594`. Fix: let the caller mark it
  declined.
- **G-08** A long summary is cut to its first sentence. For NEEDS REVIEW
  that sentence is the fixed opening ("We could not finish this test,
  so a person needs to check it."), so the reason is lost: 46 of 82
  long NEEDS REVIEW summaries in round 2's reports (the reviewer's
  count). The agent relays no reason, or calls `tobi_explain` for each.
  `models.py:614-624, 664-688`. Fix: keep the opening and the first
  reason.
- **G-05** The answer step builds its own run context and leaves out
  what the run sets (`selected`, `requested_url`, `record_live`, the
  cache). 5.F takes no pictures when it re-runs after an answer, so the
  5.F to 5.H questions that follow have none. `pipeline.py:1453-1466`
  against `1047-1057`; `checks/t5f.py:413`. Fix: one function builds
  the context for both.
- **G-09** Any number of runs can be queued by one caller, and the
  whole run has no single stop: `MAX_RUN_S` bounds the record, walk,
  reveal and collect steps one by one, not browser start, evaluation or
  the judge. `jobs.py:68-92`. Fix: a per-caller limit (needs A-01's
  owner); one outer timeout.
- **A-09** `tobi_run_status` is marked read-only and idempotent, but
  with `finish=true` it starts runs and rewrites reports. A client may
  auto-approve or retry it. `tools/run_status.py:30-34`. Verified (read).

### Security hardening

- **B-10** The judge's (or the agent's) answer can name any key, and 4.B
  presses it in the replayed page with no list of allowed keys
  ("Control+W", "F5"). CLAUDE.md allows page-named keys only for
  2.A-2.C under limits. `checks/t4b.py:121-129`, `apijudge.py:622-639`.
  Verified (read) that `_key` passes any string through.
- **M-15** 9.A presses a key the page "documents", named by the
  agent. This key press is not among CLAUDE.md's four approved
  exceptions. The key need not appear in the quote or the page, and
  browser keys are not refused (`Tab`, `Enter`, `F5` pass); `Tab` can
  make the skip "work". `src/tobi508/checks/t9a.py:248-260, 584-598`.
  Fix: require the key in the quote, refuse browser keys, and either
  list the exception in principle 5 or drop it.
- **N-11, W-14** The approved key press for 2.A-2.C is for "a key
  combination that page text names". The code holds the other limits
  (modifiers plus one key, one per run, a fresh replay) but never
  checks that the key, or a quote, is in the page text; the spec has
  that guard. The key is whatever the agent's answer says. "Never a
  key the browser uses" is a list of 12: `Ctrl+Shift+W`, `Ctrl+R`,
  `Ctrl+P`, `Ctrl+S` and full-width letters all parse and are pressed
  (the reviewer ran the parser on 54 strings; in headless Chromium
  none of them did anything; headed Chrome is not tried).
  `src/tobi508/mechanism.py:48-98, 499-539`. Fix: require the
  combination to appear in the element's text; ASCII only; widen the
  refused list.
- **H-10** 5.D types the agent's suggested value as given: a line
  break in it presses Enter and submits the form, which 5.D then
  records as "sent the form". The value comes from an agent that read
  page text. `checks/t5d.py:283-311, 652-669`. Fix: refuse control
  characters. The reviewer confirmed the mechanism with a snippet.
- **K-07** 19.A's live search compares host only, not scheme or port, and
  "one search per run" holds only because one caller calls it once.
  `pipeline.py:281-287, 328-368`. Fix: compare scheme and port; refuse a
  second call.
- **K-15** 19.A puts page-chosen URLs, query string and all, into text
  the agent reads, with "you need not ask the user first".
  `checks/t19a.py:171-193, 403-413`. Fix: suggest scheme, host and path
  only.
- **S-02, S-03** The store for scripts a page loads later (principle 5's
  fourth exception) does not hold every limit CLAUDE.md states. The host
  and allowlist checks apply to the named address only, and the fetch
  then follows up to 20 redirects to any public host (the reviewer saw
  this with a counting proxy). The 40 s limit is checked before a round
  of fetches, not during it (150 files at 10 s each, 8 at a time, is
  about 190 s). The 3 MB limit is checked after the whole file is read.
  "A script" cannot fail, because the address always ends in `.js`.
  "Same host" ignores the port. The 150-file, 12 MB and 3-level limits
  hold. `src/tobi508/capture.py:326-328, 342-409`. Fix: no redirects for
  these fetches; check the deadline inside each fetch; require a
  JavaScript content type. Verified (read).
- **S-04** The media store downloads up to 20 addresses taken from the
  page's `<video>` and `<audio>` elements, with no allowlist check and
  redirects followed. This is not one of the four approved exceptions,
  though the browser has already loaded the same files as part of the
  page. With `no_time_limit=true` the size and time caps are lifted
  and each file is read whole into memory. `capture.py:118-208`. Fix:
  keep a hard ceiling even when the caps are lifted; decide whether the
  allowlist applies and write the rule into CLAUDE.md. Verified (read).
- **S-01** A script that names very many other scripts stalls the whole
  server: the scan keeps a list and searches it for each name. 40,000
  names (750 KB of script) took 6.2 s here, and the time grows with the
  square, so a 3 MB script is over a minute with every other run and
  the proxy stopped. `capture.py:331-339, 386-409, 515-518`. Fix: a set
  beside the list; stop listing after the 150-file limit. Verified
  (run): timed `script_refs` at 5,000, 20,000 and 40,000 names. Honest
  pages do not look like this; it takes a crafted script on an allowed
  site.
- **S-08** A redirect chosen by the tested site (`Location: data:text/
  plain,<any text>`) is quoted in the tool error the agent reads, up to
  200 characters and unmarked. Redaction also leaves `ftp://user:pass@`
  whole and stops at `)`. `src/tobi508/redact.py:23-36`,
  `src/tobi508/browser.py:244-269`. Fix: errors name the scheme and host
  of a blocked target only. The reviewer ran `safe_url` and `scrub`.
- **S-06, S-07** `tobi_read_report` returns the page and product names
  of an untrusted file at any length (comments are clipped, these are
  not), has no cap on rows (a 40 MB file is about 2 million rows), and a
  malformed file raises a generic error where "not an SCRT file" is
  meant. `src/tobi508/tools/read_report.py:122-195`,
  `src/tobi508/scrt.py:222-290`. Fix: clip the four fields; refuse more
  than a few thousand rows; turn parse errors into `NotAReport`.
- **B-05** The judge's time cap is checked once per round only; one bad
  round can run far past it and fire dozens of extra calls. Requests are
  not split by text size. Retries repeat errors that cannot succeed.
  `apijudge.py:547-564, 675-727`.

### Tests, CI and the image

- **Q-06** Baseline cases and ACT cases for 4.A, 4.C, 4.D, 5.B and 9.A
  compare the outcome only, not the rows, so a PASS reached by the
  wrong row passes the test (K-01's self-comparison would). 9.B and
  9.C's row table is optional and has 8 entries for 14 cases. ACT
  cases for 2.x never expect PASS, so 2.A-2.C have no positive
  control. `tests/test_baseline_cases.py:119-130`,
  `tests/test_act_cases.py:100-110`, `tests/test_fixtures_9x.py:145-149`.
- **Q-05** No test would fail for: the `MAX_RUN_S` stop; a
  "certified" or "compliant" claim in output text; `trusted_tester`
  in a tool name; Playwright pinned with `==`; a page link being
  followed outside the approved exceptions; the tested page given
  again as an other page (the existing test even uses `?0` to `?5` as
  distinct pages).
- **Q-08** CI jobs have no `timeout-minutes` (the default is six
  hours), no cancel of superseded runs and no cache; `uv sync` is not
  `--locked`; actions are pinned to moving tags.
  `.github/workflows/*.yml`.
  **Partly fixed:** timeouts, cancel of superseded runs and
  `uv sync --locked` are in. Not fixed: caching and pinning actions to
  commit hashes (the hashes need a network lookup; left for a later
  change).
- **Q-09** On a push to main the image is published without waiting
  for the tests, so a commit that fails tests still ships as
  `:latest`. The smoke test runs one 4.C run in dev mode and never
  goes through sign-in or the proxy to a real host.
  `.github/workflows/container.yml`.
- **Q-10** The image copies everything tracked: 247 MB of
  `evals/judging`, plus tests and docs, and `chown -R` then doubles it
  in a second layer. No `HEALTHCHECK`, though `/health` exists. Base
  images are tags, not digests. `Dockerfile:27, 43`, `.dockerignore`.
  What is right: non-root, Playwright pinned exactly, container
  defaults set, and a public host without sign-in is refused.
- **Q-12** CODEOWNERS covers `specs/`, `.github/` and `evals/judging/`
  but not `src/tobi508/checks/`, the fixture manifests that hold
  expected outcomes, `third_party/`, the Dockerfile or the lock file.
- **Q-13** One `xfail(strict)` test records a trap the tool misses (a
  page that takes focus back 600 ms after it leaves reads as a loop of
  two, not a stuck element). It is on the roadmap's list for 4.C.
  `tests/test_traverse.py:139-152`.

### Evals

- **L-01** Scoring an agent round builds its criteria from today's test
  list. Round 1 was scored on 17 criteria; today's code gives 20, and
  the three new ones would count as wrong answers. CLAUDE.md's rule
  (score a locked round with the code at its lock commit) avoids it, and
  the lock check already refuses today's code (L-11).
  `evals/agent/score.py:158`. Fix: record the criteria in each arm's
  summary. Verified (read).
- **L-11** The lock hashes live source files, so any edit to
  `scoring.py` or `catalog.py` makes every locked round unscoreable with
  current code; rounds 1 and 2 already are. `evals/judging.py:59-70,
  372-383`. Fix: have `score` read the files from the lock commit.
- **L-04** A tool PASS against a key FAIL becomes a "validated catch"
  (+1) if the tester later agrees, and leaves the false-PASS line.
  `evals/scoring.py:125-144`. Fix: never convert a false PASS; list it
  on its own line.
- **L-05** The judge eval and the gate rerun the whole browser pipeline
  for every repeat; only the model call needs repeating.
  `evals/judge_eval.py:611-664`, `evals/apijudge_gate.py:132-169`.
- **L-13** The gate runs on round 2's pages and keys, which the prompt
  and rubrics were tuned on. It measures repeat noise more than new
  pages. Say so in its output.
- **L-08** `judge_eval.py apply` leaves cases with bad answers out of
  its tally ("scored 40: 40 match" with 3 unanswerable) and loses state
  on an exception. `evals/judge_eval.py:505-559`.
- **L-09** The per-criterion score reports "not performed" as "needs
  review", and sorts review reasons by searching comment wording.
  `evals/agent/score.py:142-151, 270-276`.
- **L-10** `freeze.py` skips its own check for a URL with a fragment,
  and "freeze again" cannot replace a bad recording.
  `evals/agent/freeze.py:152, 186-188`.
- **L-12** A CLI arm has no overall time or spend cap, and its child
  processes inherit the whole environment minus 12 names.
  `evals/agent/cli.py:109-133, 189-251`.
- **L-06, L-07** `judge_c.py` is a finished one-off that copies most of
  `apijudge.py`; `per_test.py` copies the scorer's merge and hides
  missed fails under "Other".

---

## P3

Cleanup. All reviewers' claims unless marked.

- **Wording and stale text:** `other_pages` says "up to 5" when the
  default allows 50, and tells the agent to ask the user (A-16); the
  explain prompt is advertised to agents that cannot call it (A-19);
  `time_budget.py` says the limit is 120 s, `prompt_dev.py` and
  `arms.py` still say "a11y" (L-17).
- **`tobi_run_status` with nothing left** says `status: "outstanding"`
  beside "Nothing is left"; an agent that reads the status word may
  poll again (T-11).
- **Fixed text in every result:** the untrusted-data notice and the save
  hint repeat in each result; `ReadResult` has two flags no agent uses
  (A-12).
- **Dead code:** the `Judge`, `ClientJudge` and `ApiJudge` classes do
  nothing (`report.open_questions = result.pending` assigns a list to
  itself, `pipeline.py:1208-1209`; verified (read)); four functions find
  picture links three different ways, one of them the cause of B-01
  (B-14); `evals/snapshot.py`, the unused API route in `evals/agent/`
  (L-17).
- **Loose data:** follow-up calls are plain dicts read by key in five
  places; `RunResult` and `AnswerResult` copy about 14 fields (A-17).
- **Memory and disk:** a finished job holds its whole report for 24
  hours and `tobi_run_status` re-reads every report from disk on each
  call (A-13); the page cache never evicts and can hand out a
  half-copied recording (B-15); `evals/judging/` tracks about 250 MB,
  half of it repeated copies of one run (L-16).
- **`run://` resource:** serves any file in the run folder whole, with
  no size cap: a HAR of tens of MB, the `owner` file (A-18). The owner
  check does apply.
- **More small gaps (phase 1):** a request for tests that are not built
  still starts Chrome and loads the page before saying so (G-10); a
  result still too long after every cut is returned with no flag, and
  the note on page-text excerpts can be untrue (G-11); the judge asks
  missed questions again one at a time (G-12); `jobs.running()` is used
  only by a test, and `finish=true` with a `job_id` is silently ignored
  (G-13); `rationale`, quotes and the number of answers have no upper
  size and go into the report (G-15); the wheel holds `src/tobi508`
  only, with no `specs/` or `third_party/`, so the package works from a
  checkout or the image and nowhere else (G-14).
- **Small gaps:** a follow-up call with no tests vanishes (A-14);
  progress callbacks are awaited with no timeout (A-15); guards read
  cached global settings, and a check with no spec file gets no guards
  silently (B-16); the judge's HTTP client follows redirects with the
  API key header, the CLI process is killed without being waited for
  (B-17, L-14); `formmethod` on a submit button is ignored and the first
  search form is taken even when a later one is on the host (K-14);
  eval packets copy evidence files without scrubbing fixture names
  (L-15); smaller scoring table gaps (L-18).
- **Security edges:** the early allowlist check accepts four address
  forms Chrome reads differently (`https://evil.com\.gov/` and three
  more); the second check on Chrome's own form of the address blocks
  them, so the browser is safe, but any use of `check_url` that does not
  go through a navigation inherits the gap (S-09; the reviewer ran 23
  trick addresses). Nothing caps the size of a recording or the number
  of "refused" log lines a page can cause (S-10). The ANDI rule covers
  `https://www.ssa.gov/` exactly, not `http://` or `ssa.gov`, and a
  tested page on www.ssa.gov loses its own requests (S-11). The egress
  proxy accepts any process on the machine (S-12).
- **Core:** the same small rules (what is a field, what is visible, what
  is tabbable, how to walk shadow roots) are written out in five files
  and have drifted: reveal's field list lacks slider, searchbox and
  spinbutton (D-19). Scripts are templated with `str.replace("UP", ...)`
  over the whole text (D-20). Field reads use the document, not the
  shadow root, for id lookups (D-21). A menu trigger that opens a new
  page is counted as a link (D-22). The 300 ms noise window and a Chrome
  session are repeated per action (D-23, D-24). Past 20 nested frames
  focus reads as "body" instead of "unknown" (D-25).
- **4.A-4.C cleanup:** the specs give "exact wording" for the questions
  and the code words them differently; 4.C's rows J1? and J2? are not
  in its spec table (E-17). `_label`, `_norm` and the key-text helper
  are copied between `t4a.py` and `t4c.py`; `t4b.py` imports seven
  private names from `t4a.py`; `keys_of` is unused (E-18). Worst case
  per run: 4.A about 70 loads, 4.C about 340 replays; the same page
  text is loaded three times (4.A, 4.B, 4.C) (E-19).
- **4.D-4.F cleanup:** 4.D's "why it could not be compared" reasons
  are written to a dict after Pydantic has copied it, so the summary
  always says "the images could not be compared" (F-04, confirmed by a
  snippet). 4.E's instance identity leaves out the frame, so the same
  path in two frames merges (F-10). 4.F scans every node of the page
  once per stop (F-18), and 4.D reads a whole computed style, about
  350 properties, twice per stop (F-21). About 100 lines of
  applicability rows, labels, key text and trap bookkeeping are copied
  in `t4d.py`, `t4e.py` and `t4f.py` and have drifted; the `notes`
  fields are never written (F-22). 4.D gets its "focus dropped" FAIL
  by calling 4.E's whole classifier (F-23). Worst case per run: 4.D up
  to 20 widget replays, 4.E up to 20 loads and 20 s of fixed waits,
  4.F up to 19 loads.
- **Watchers cleanup (W-13, W-17):** the probe presses only Home on a
  slider where the spec says Home, End, then arrows; frames are 0.35
  and 0.45 s apart where the spec says 0.5 s. `FRAME_S` is unused;
  `IMAGE_MAX_BYTES` is defined twice; `t3a.py` calls three private
  names of `motion.py` and `flashcap.py`; an animated image is cut at
  500 frames with no note. `motion.py` is 1,659 lines doing nine jobs,
  one of them a 450-line browser script held in a Python string and
  patched with `.replace`.
- **5.F-5.H cleanup:** `PassE.notes` is read and never written;
  `FIELD_MAX = 40` is defined in `t5f.py` and `t5d.py`; there are three
  walkers for visible text (M-20). A quote of one character satisfies
  the "quote found in the error text" check in 5.F and 5.G; 9.A asks
  for three (M-21). No time is wasted beyond the spec's budget; the
  error pass is shared by 5.F, 5.G and 5.H.
- **2.x and 3.A cleanup:** `_finding`, `apply_answers`, the "not
  performed" blocks, three sentences and the five-method check classes
  are copied in `t2a.py` to `t2d.py`, about 250 lines (N-05's cost
  section). A clip of 3.0 to 3.5 s has ended by the 3.5 s reading and
  is not counted (N-16). Module docstrings of 2.B, 2.D and 3.A give an
  older spec version than the spec files. Worst-case time: the watch
  is 6.5 s (13 s with the scrolled watch); the mechanism probe is up
  to about 250 s per moving content (8 controls, a load and up to 15 s
  each, twice), three contents about 12 minutes.
- **5.A-5.D cleanup:** a field inside `<fieldset disabled>` is counted
  as enabled, and the four tests then disagree about one page (H-15,
  confirmed by a run; fix: `el.matches(':disabled')`). `_finding` is
  copied in 13 check files and the words "This test could not be
  performed" are typed 27 times though a constant exists; 5.A and 5.C
  share one skeleton; each of 5.A, 5.B and 5.C saves its own copy of
  the whole label pass (H-16). Question and rubric sizes: 5.A 370 and
  1,278 characters, 5.C 580 and 972, with one 5.A question and picture
  per field, up to 60 (H-17). 5.C tests M3o before M3s where the spec
  lists M3s first; both are FAIL.
- **Core cleanup (C-08, C-09, C-10):** a page with nothing focusable
  is walked 50 presses each way before it is called empty (about 3 s).
  The inventory that sets the walk's cap is read before the page
  settles. A frame that cannot be evaluated is not counted among
  "fields in frames not checked".
- **Tests cleanup (Q-11, Q-14, Q-15, Q-16):** `tests/test_server.py`
  is mostly template leftovers and one test fails if `MCP_TRANSPORT`
  is set in the developer's environment. The Baseline manifest pins no
  upstream version, and expected outcomes sit in the same file as the
  page hashes. Fixture titles and file names name the defect, which
  matters only where an agent sees them. There is no socket-level
  network guard; two tests launch their own browser outside the
  proxy. One test compares every default setting and fails on any new
  one.
- **9.x duplication:** `_finding`, the "not performed" block and the
  cache-or-read pattern are copied in 9.B, 9.C and 19.A (K-13).

---

## Checked, and it holds

So nobody reviews these again without a reason. From the security
reviewer (phase 1); I read the summary, not every line behind it.

- **The allowlist** is enforced on every top-level navigation and every
  redirect hop, with a second check on Chrome's own form of the address.
  Userinfo, trailing dots, upper case, `.gov.evil.com`, IP literals,
  `data:`, `javascript:`, `blob:` and `file://` outside dev mode are all
  refused; popups and meta refresh take the same route; service workers
  are blocked. Frames and subresources are checked by the egress proxy
  only, not the allowlist. That matches the code's own notes, but
  CLAUDE.md does not say it.
- **The egress proxy** resolves a name once, checks every address and
  connects to the address it checked, which defeats DNS rebinding.
  Metadata, link-local, IPv4-mapped, NAT64, 6to4 and Teredo addresses
  are refused. Every error path closes the connection. WebRTC is held to
  the proxy.
- **Replay never goes live:** a request not in the recording is aborted.
  File names inside a recording are never chosen by the page.
- **Run ownership** is checked by the tools and by `run://` resources
  alike (but see A-01 for jobs and S-05 for a token with no `sub`).
- **Report files:** JSON only, so no zip or XML tricks; a hosted server
  never reads its own disk for `tobi_read_report`.
- **ANDI** is never loaded from ssa.gov.
- **In `pipeline.py`, no time limit, failed walk or failed check turns
  into PASS or DOES NOT APPLY:** a test that did not run ends as NEEDS
  REVIEW with "This test could not be performed", and `Finding`
  defaults to NEEDS REVIEW (the reviewer read all of `pipeline.py` and
  `models.py`). This does not hold inside the checks: a check that ran
  but skipped part of its work can still PASS (E-01, E-07).
- **Answers are checked** against their question: id, kind, the choice
  list and the picture rule; element numbers are re-checked by the
  checks. A later agent answer cannot replace a person's or the server
  judge's.
- **4.A to 4.F follow their specs' tables** row for row, in
  order and in thresholds; the constants in `t4d.py` equal the spec's.
  The problems found are in the evidence fed to the tables (F-02,
  F-11, F-12), not in the tables. The questions that may settle a PASS
  by looking do so only as principle 8 allows.
- **The walk itself held up:** wrap, a loop confirmed on a second load,
  a cross-origin frame and a page with nothing focusable all behaved
  in the core reviewer's runs.
- **What the suite does well:** every fixture folder has an expected
  table and a "every fixture is listed" guard; expected outcomes are
  in tests, never in pages; the hash checks on ACT, Baseline and
  vendored files compare whole sets; the allowlist, egress, redirects,
  leakage, sign-in and frozen pages each have direct tests.
- **The flash arithmetic matches WCAG 2.3.1.** The reviewer ran
  `flash.py` on 28 built frame sequences (black and white at 2, 3,
  3.5, 4 and 10 Hz; small and large boxes around the 341 x 256 limit;
  red flashes; fades; irregular timestamps; exactly three flashes in a
  second) and every result agreed: the luminance formula, pairs of
  opposing changes, the sliding one-second window, the area limit and
  the red rule. The misses in 3.A are in what gets captured (W-02,
  N-06), not in the counting.
- **Failures that raise end in NEEDS REVIEW** in the watchers: a failed
  load, a failed screenshot, a video that cannot be decoded (H.264),
  a cut capture. The wrong outcomes come from observations that
  succeed and see nothing.
- **2.A-2.D and 3.A follow their specs' tables** in rows and order.
  NOT TESTED comes only from 3.A's row A2, and 3.A's WCAG assessment
  appears only as text in the summary, as principle 2 requires. 3.A
  never returns PASS or FAIL. For the page-named key press the code
  enforces modifiers plus one key, the browser-key list, one
  combination per run and a fresh replay (the missing limit is N-11).
- **5.A-5.H and 9.A follow their specs' tables** row for row and in order (one
  harmless swap in 5.C). As with 4.D-4.F, the problems are in what the
  readers feed the tables.
- **The judge prompt** tells the judge to answer "unsure" when the
  evidence does not settle a question.
- **Config defaults** match CLAUDE.md (45 s, 1,800 s, 600 s, 20 s, 45 s,
  2 runs, `.gov` and `.mil`).

## Refuted

- **B-03, the half-written file.** The claim: `tobi_run_status` can read
  `report.json` while another call is writing it, fail to parse it, and
  say "nothing is left". Inside one server process this cannot happen:
  both the write (`Path.write_text`) and the read run to completion on
  the one event-loop thread, and jobs live in one process. The bare
  `except Exception: continue` at `pipeline.py:1589-1593` is still worth
  narrowing, and the lost-update half of B-03 is real (see P2).

- **D-18, the label pass caching too early.** The claim: 5.A-5.C might
  run before 4.F or 5.D and miss fields those reveal. The order is
  fixed: `pipeline.py:877` sorts checks by `shares`, and 5.A, 5.B and
  5.C have `shares = -1`, so they always collect last. Verified (read).

- **A-16, the container half.** The claim: `headless` and the browser
  channel default to values a container cannot use. The Dockerfile sets
  `HEADLESS=true` and `BROWSER_CHANNEL=chromium`, and the server refuses
  to start on a public host without sign-in (G-14). The wording half of
  A-16 stands (P3).

## Leads nobody has checked

One line each, from the reviewers' "unverified" lists; none is counted
above.

- A cancelled job (server shutdown) raises `CancelledError` through
  `tobi_run_status`, which only catches `Exception`.
- `/version` is outside the sign-in gate.
- `ALLOWED_DOMAINS=.gov,.mil` (not JSON) may fail at startup;
  `JUDGE_TYPES` with a typo ("4.a") silently switches nothing on.
- `tobi_read_report` is a synchronous tool parsing up to 40 M
  characters; whether it blocks the event loop is not checked.
- The walk runs while the motion watcher is still setting the list of
  changes to ignore, so two runs of one page can settle differently.
- Same-named radio groups in two forms are counted as one field.
- `bypass()` clicks a text spot after a trap; an ancestor with a click
  handler would run page code.
- A second walk pass after a trap doubles the walk time on a long page.
- 9.C's place pairing uses `regions[-1]`, which may be `main`.
- No test covers a live search that goes off host or off port.
- 4.B and 4.C: a page whose only content is in a frame the inventory
  cannot read may be DOES NOT APPLY.
- 4.C: a focus loop of more than about 12 stops inside an error popup
  is not detected in 24 presses; any failed request during the walk
  (one analytics call) makes the "page loads more content" rule apply.
- 4.A: a hover menu opened by something that is not a Tab stop is not
  hovered (the spec says stops only).
- 4.D and 4.E accept "stuck going forward, wrapped going back" as a
  complete walk; the spec says "wrap or the same trap".
- 4.F: a dialog open at load whose focus escapes to a stop seen
  earlier is not noticed; 4.E: a popup that opens and closes within
  one step is not seen.
- 4.D passes any text field with a caret colour that is not
  "transparent", including one equal to the background.
- A page that shows a dialog on every second load (a survey, a cookie
  banner) could send a replay to a different element (C-06); not run.
- A download, the clipboard and `window.print()` are effects the
  observer cannot see, like `alert()` (C-01); not run.
- Whether "Require review from Code Owners" is switched on cannot be
  seen from the repository.
- 3.A: a frame whose step script fails is skipped, so an animation in
  it runs on the wall clock and is mis-timed; video frames may be
  skipped under CPU load and under-count.
- A finite CSS animation that starts between 2 s and 6.5 s and ends
  before the watch does is missed by all three of 3.A's sources.
- 2.B: a video over the recording cap that raises no error is DOES NOT
  APPLY (no code for that part of row A1; needs a file over 50 MB to
  try). 3.A: a screen capture that fails or is skipped for time leaves
  no "not measured" entry.
- A `<video>` in a shadow root is missed by 2.B and 3.A the same way
  audio is (read only). Animated AVIF and APNG files whose type is not
  recognised are skipped.
- 5.C adds "required" to the announced words whenever the field is
  required, without checking ANDI announces it.
- 5.A: a real label more than 240 px left of its field (wide tables)
  is not "shown", so a placeholder field can FAIL.
- 5.D: a field in a frame whose change alters the parent page reads as
  "no effect"; a failed refill of an earlier field is skipped silently.
- In the judge's request a Tab stop is written as one line with the
  element's name unescaped; a name holding a line break could forge a
  stop line. Chrome usually collapses such names; not tried.
- An error while applying an answer is returned once and never saved in
  the report.
- Whether Claude Code and other clients pass `structured_content` to
  the model as well as the text is not measured; picture token figures
  are estimates from pixel counts.
- With the default settings, sign-in checks no audience and requires no
  group, so any user of the realm can sign in: confirm the deployment
  sets `OIDC_AUDIENCE` and `REQUIRED_GROUPS`.
- A stored media file whose address has a query string may not be found
  on replay (exact match on the address).
- The audit log records the caller's email on every call: intended, but
  confirm it fits the retention policy.

## How this could be handed out

Bundles that one thread can take without stepping on another. Each
names the items and the files it would touch. What is scheduled when is
in [the roadmap](../ROADMAP.md); the structural work ("If we started
over", below) is planned in detail in
[plans/2026-11-12-coverage-second-look-thin-agent.md](../plans/2026-11-12-coverage-second-look-thin-agent.md).

1. **One-line and one-function fixes, no spec change:** E-01 (hover
   cap to `incomplete`), E-07 (the recording "out of time" helper),
   C-03 with F-06 and H-11 (ignore the fragment in `observe`), F-01
   (4.D's arrow loop), N-08 (2.B's missing A1 cases), W-05 (2.A's
   pairing of readings), K-04 and E-02 (placeholder addresses), K-01
   with M-11 (final address equal to the tested page), F-04, H-15.
   Files: `observe.py`, `t4a.py`, `t4c.py`, `t4d.py`, `t2a.py`,
   `t2b.py`, `t9c.py`, `pipeline.py`. Each with a fixture from the
   pages folder.
2. **Shadow roots:** D-03, D-01, K-02 with M-12, N-01, M-06, D-04,
   F-08. First the notes that turn DOES NOT APPLY and PASS into NEEDS
   REVIEW (small), then the shared reader ("If we started over",
   item 2). Files: `traverse.py`, `labels.py`, `site.py`, `motion.py`,
   `t5f.py`.
3. **Spec decisions for Abby, then their code:** H-08 with M-07, E-03,
   E-06, E-08, E-13, H-04, K-05, M-01, M-02, M-03 with E-09, M-08,
   F-02, N-02 to N-09, C-07. One MINOR spec change each.
4. **Traps and limits:** H-03 with M-05, F-11, F-13, M-04, M-09, E-12,
   N-05 with W-11, H-05, H-07, F-12, F-15, E-05. This is "If we
   started over", item 1, done check by check.
5. **The watchers:** W-02, W-07, W-09, N-03, N-06, W-01, W-06, W-08,
   W-10, W-12. Files: `motion.py`, `flashcap.py`, `t3a.py`.
6. **What the agent receives:** T-01 to T-03 with G-01, A-02 with
   T-04, A-03 with T-07, then the P2 token items. Files: `models.py`,
   `inline.py`, `pipeline.py` (the text builders), `explain.py`,
   `runlog.py`, `scrt.py`, the tools.
7. **Before the server judge's figures are used (roadmap Now, 3 and
   4):** B-01, B-02, L-02 with L-03, A-05, G-02, B-04, then B-05,
   B-10, B-18. Files: `apijudge.py`, `judgment.py`,
   `evals/apijudge_gate.py`, `evals/scoring.py`.
8. **Before VAST (roadmap, 6):** A-01, S-05, G-09, G-03, B-03, then
   S-02 to S-04, S-08, Q-09, Q-10. Files: `jobs.py`, `access.py`,
   `tools/`, `capture.py`, `Dockerfile`.
9. **CI and tests:** Q-01 and Q-02 first (minutes each), then Q-03
   (the grid of hard pages), Q-06, Q-07, Q-08.

## If we started over

Seven changes, in the order I would make them. The first three would
have prevented most of the P0 table. Costs are my estimates for one
thread with the suite as its safety net; none is measured.

### 1. Every reading says what it covered

- **Today:** a reader returns a list, a dict or `None`. Whether it
  entered the shadow roots and frames, hit a cap, ran out of time or
  failed is in a note, a flag on the run, a counter nobody reads, or
  nowhere. Each check decides for itself what "nothing" means, and 22
  checks have decided it 22 ways.
- **Instead:** every reading (the walk, the label pass, the site read,
  the watcher, the form pass, the reveal pass) returns its data with
  one small record of coverage: what it did not enter and how much was
  there, which caps it reached, whether time cut it, which reads
  failed. The engine, not the check, refuses DOES NOT APPLY and PASS
  when coverage is incomplete and gives NEEDS REVIEW with the reason.
  The spec template gains one sentence: an A row or a PASS needs a
  complete reading.
- **Would have prevented:** D-01, D-02, D-03, K-02, K-03, E-01, E-03,
  E-07, E-12, F-11, F-12, F-15, H-03, H-05, H-07, M-04, M-05, M-06,
  M-09, N-05, N-06, W-02, W-07, W-11, C-05.
- **Cost:** the record and the engine rule, 1 day. Filling it in the
  readers (`traverse.py`, `labels.py`, `site.py`, `motion.py`,
  `forms.py`, `reveal.py`, `flashcap.py`), 3 to 4 days. Passing it
  through 22 checks in place of their own `incomplete` lists,
  mechanical, 3 days. A MINOR bump of every spec. About two weeks in
  all, and it can be done reader by reader, the walk and the label
  pass first.

### 2. One library for reading the page

- **Today:** what is a field, what is visible, what is tabbable, how
  to walk into shadow roots and how to name an element are written out
  in `traverse.py`, `observe.py`, `reveal.py`, `labels.py`, `forms.py`,
  `site.py`, `motion.py`, `t4a.py` and `t5f.py`, as JavaScript in
  Python strings, and the copies disagree (D-19). Most use
  `document.querySelectorAll`, which is why shadow roots are missed in
  some places and not others.
- **Instead:** one `jslib` string put in front of every script, as
  `PATH_JS` already is: a walk that enters open shadow roots and
  same-origin frames, visible text, the field and tabbable tests, the
  path. One `evaluate` helper that raises when the script throws.
- **Would have prevented:** D-01, D-03, K-02, N-01, M-06, H-01, D-04,
  D-19, D-21, F-08, and it makes the next test cheaper.
- **Cost:** one new module of about 400 lines moved, not written; nine
  files edited; 4 to 5 days including a rerun of every fixture.

### 3. A grid of hard pages that every check must survive

- **Today:** each check has fixtures for its own rules. No fixture
  asks "what does this check do on a page it cannot fully see". The
  review found the P0 items by writing about a hundred small pages,
  one suspicion each.
- **Instead:** nine shared pages (a shadow root, a frame, more items
  than the cap, a trap in mid-page, something that starts late,
  non-English text, hidden text, a form behind a button, a reading
  that fails) run against all 22 checks, with one assertion: never
  PASS, and DOES NOT APPLY only where the table says the page truly
  has nothing for that test. A cell is a fixture or a written reason.
- **Cost:** the pages mostly exist in the pages folder; the table and
  the parametrised test, 2 to 3 days. With shared recordings (below)
  about 200 short runs.
- **With it:** share one recording and one walk per fixture page
  across tests (Q-07), which is where most of the suite's 70
  CPU-minutes go.

### 4. One base for the checks

- **Today:** `_finding` is copied in 13 check files; "This test could
  not be performed" is typed 27 times; the A1 and A2 blocks, labels,
  key text and trap bookkeeping are copied per family and have
  drifted; there are two "out of time" helpers and E-07 is the
  difference between them.
- **Instead:** `checks/common.py` with the finding builder, the
  not-performed finding, the page outcome, the text helpers and one
  "out of time" that always records.
- **Cost:** 2 to 3 days, mechanical; several hundred lines removed.

### 5. A smaller surface for the agent

- **Today:** about 93,000 tokens to read for one page (measured);
  instructions in three channels; every result sent twice; the report
  saved by passing it through the model.
- **Instead:** tools with no output schema and text results only; one
  short instruction block; an unchanged question listed by id; the
  report written compact with each question stored once; the server
  saves the report (a download link when hosted) and builds the
  pre-SCRT file on request.
- **Expected:** about 30,000 to 35,000 tokens for the same page (tool
  list 5,000, run result 8,000, answers 3,000, explain 4,000, report
  not through the model or 18,000 if it is). An estimate from the
  measured parts.
- **Cost:** 3 days and the changes to `tests/test_tools.py`.

### 6. Run state with one owner and one writer

- **Today:** `pipeline.py` is 1,662 lines and five jobs; `run_tt_tests`
  is one function of 420 lines; `report.json` is read, changed and
  rewritten by answer calls, follow-ups and the judge with no lock;
  jobs have no owner; the answer tool is the one call with no limit;
  the judge runs inside a browser slot.
- **Instead:** a small `runs` module that owns a run's files (one lock
  per run, write to a temporary file and rename); jobs that carry
  their caller; answers applied as a job like a run; the judge after
  the slot is released; the run's phases as functions over one state
  object.
- **Covers:** A-01, B-03, B-04, B-06, B-07, B-11, G-03, G-05, G-06,
  G-07, G-09.
- **Cost:** 4 to 5 days.

### 7. One gate for what an answer makes the tool do

- **Today:** an answer can name a key to press or a value to type in
  five places, each with its own filter: 4.B none (B-10), 2.A-2.C a
  list of twelve keys (W-14), 9.A syntax only (M-15), 5.D's typed
  value raw (H-10), 4.C a quote check. Page text reaches the judge
  through a hand-built tag (B-02) and picture links through a search
  of the text (B-01).
- **Instead:** one `actions` module: parse a key, refuse browser keys,
  require it in the page text, strip control characters from typed
  values; one serialiser for untrusted text; picture links only
  through the guarded reader. CLAUDE.md's principle 5 then lists 9.A's
  key beside the others, and principle 8's list is brought in line
  with the checks (E-06).
- **Cost:** 1 to 2 days.

### What I would keep as it is

- The specs as the only source of outcomes: the row tables matched in
  every check.
- Replay from a recording, the allowlist with its second check on
  Chrome's own address, and the egress proxy.
- The flash arithmetic, and the walk's settle-and-confirm design.
- Expected outcomes in tests and never in pages, and the hash checks
  on vendored cases.

### Worth a trial, not before the demo

- **One watch on a paused clock** for 2.A-2.D and 3.A. Today the page
  is watched for 6.5 real seconds, then loaded again for a 2 s
  recording, then again for a stepped capture. Running the page
  forward 30 to 60 s of its own time on 3.A's paused clock would see
  what starts late (N-02 to N-09), remove the sampling problem (W-09)
  and cost less wall time. It is a larger change to `motion.py`, one
  to two weeks, and video and audio do not follow the paused clock.
