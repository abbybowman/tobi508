# Code review, 2026-11-11: what to fix, in order

A triaged list from a line-by-line review of `tobi508`, for Abby to review
and hand to other threads. Nothing here has been fixed; this thread changes
no code.

**Progress.** Phases 0 to 2 are done. Phases
3 and 4 add the files nobody has reviewed yet; phase 5 adds the "if we
started over" section. Each phase is committed when it is checked.

| Phase | Covers | State |
| --- | --- | --- |
| 0 | Leads from the first attempt (tools, pipeline, traverse, 9.B/9.C/19.A, evals) | done |
| 1 | Security files; what an agent receives, measured; the rest of tools and pipeline | done |
| 2 | 4.A-4.F and 5.A-5.D against their specs | done |
| 3 | 5.F-5.H, 9.A, 2.A-2.D, 3.A and the watchers | not started |
| 4 | The rest of the core; tests, CI, Dockerfile, packaging | not started |
| 5 | "If we started over"; final ordering | not started |

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
H 5.A-5.D.

---

## P0

Four give a wrong outcome on any page built with web components
(D-03, D-01, K-01, K-02). Phase 2 added wrong outcomes in single checks
(F-02, F-11 and those after them). Two are security holes that open only
in a mode that is off by default (hosted sign-in, the server judge) but
that the demo plan turns on (A-01, B-01).

### D-03 4.A passes a page whose mouse-only control is in a shadow root

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

### D-01 5.A, 5.B and 5.C say "no form fields" when the form is in a shadow root

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

### K-01 An "other page" that is the tested page under another spelling gives 9.B and 9.C a PASS

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

### K-02 Navigation inside a shadow root or a frame is invisible to 9.B, 9.C and 19.A

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

### E-01 4.A passes without looking for hover menus past the 40th element

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

### E-02 4.A passes a mouse-only `<a href="#">` because another link also has `href="#"`

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

### E-07 4.C passes after skipping its error-state pass for lack of time

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

### E-03 4.A says "nothing can be used with a mouse or keyboard" on a canvas or drag-only page

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

### E-08 4.A passes a button that only answers `mousedown` (needs Abby)

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

### F-02 4.D passes an element with no focus indicator when the page shifts under it

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

### F-11 4.F says "only one element takes focus" when the first element traps Tab

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

### H-01 5.A passes a label whose words nobody can see

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

### H-02 5.C passes any field whose visible text is not in Latin letters

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

### H-03 5.D passes a form it stopped filling at a keyboard trap

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

### H-08 A form behind a plain button is "no form fields" (needs Abby)

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

### N-01 2.A does not hear audio from `new Audio()` or from a shadow root

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
  APPLY.

### N-03 2.B says nothing blinked when text blinks by `visibility`

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

### N-06 A flashing GIF after the 30th image is invisible to 3.A and 2.B

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

### N-08 2.B says nothing moved on a page with an autoplaying YouTube embed

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

### N-02, N-04, N-07, N-09 What starts after the 6.5-second watch is "does not apply"

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
- **Smallest fix:** share 2.C's hints: when there is a hint and nothing
  was found, 2.A, 2.B and 3.A answer NEEDS REVIEW too; add "N more
  elements wait to be scrolled into view" as a hint. Spec changes in
  the safe direction for 2.A, 2.B and 3.A.
- **Checked:** verified (run), four pages: audio started by a 4.5 s
  timer, 2.A DOES NOT APPLY; an animation class added at 7 s, 2.B DOES
  NOT APPLY while 2.C on the same run is NEEDS REVIEW ("a timer of
  7 s"); a strobe started at 9 s, 3.A DOES NOT APPLY; a counter started
  by the second observed element, 2.C DOES NOT APPLY.

### A-01 Hosted mode: one signed-in user can list and collect another user's run

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

### B-01 Server judge: a page can make the server read picture files outside the run

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

## P1

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

### Wrong outcomes

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

### Security and the server judge

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

### The gate that decides `JUDGE_TYPES`

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
- **4.F, for Abby:** the answer "order does not matter" on the page
  question makes the whole test DOES NOT APPLY on the agent's word,
  even when a split form group was the reason for asking. That is what
  rows M8 and G4 say today.
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
- **N-11** The approved key press for 2.A-2.C is for "a key combination
  that page text names". The code holds the other limits (modifiers
  plus one key, never a browser key, one per run, a fresh replay) but
  never checks that the key, or a quote, is in the page text; the spec
  has that guard. The key is whatever the agent's answer says.
  `src/tobi508/mechanism.py:499-539`. Fix: require the combination to
  appear in the element's text.
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
- **2.A-2.D and 3.A follow their specs' tables** in rows and order.
  NOT TESTED comes only from 3.A's row A2, and 3.A's WCAG assessment
  appears only as text in the summary, as principle 2 requires. 3.A
  never returns PASS or FAIL. For the page-named key press the code
  enforces modifiers plus one key, the browser-key list, one
  combination per run and a fresh replay (the missing limit is N-11).
- **5.A-5.D follow their specs' tables** row for row and in order (one
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

## If we started over

Written in phase 5, from the design notes of every phase.
