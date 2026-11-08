# Plan: fixes after agent eval round 2

Status: **proposed 2026-11-08, nothing built yet** except the harness and
delivery fixes made during the round (end). Round 2: 10 pages of
svs.gsfc.nasa.gov, arms A, B and C, scored against Abby's blind SCRT
files. Results: [`evals/judging/round2-armc/abc-score.md`](../../evals/judging/round2-armc/abc-score.md).
Each rule cell reviewed with Abby: [`evals/judging/round2/review-with-tester.md`](../../evals/judging/round2/review-with-tester.md).
Related plan: [2026-11-07-server-judge-pivot.md](2026-11-07-server-judge-pivot.md).

**Rules for every fix here.** A rule change goes through its spec
(principle 2), MINOR version bump, with a fixture (a vendored ACT or
Baseline case first, a custom page only for a gap), the full suite, and
the judge eval when a question, rubric or question input changes
(principle 6). Each fix is checked on round 2's frozen pages before the
next round; round 2's results stay as locked (they measured the code at
its start). Agent-assisted results, not certified Trusted Tester results.

## What round 2 showed

- **No false PASS or false DNA came from a judge's answer**, Agent A's or
  Agent C's. Every one in the tool's results was a rule deciding alone,
  the same cells in every A and C run.
- **The rules' errors outnumber any judge's:** 3 false PASS and 2 missed
  fail cells (plus 3.A's DNA for unplayed video), and 13-15 false FAILs
  per run.
- **Frames are the largest gap.** 5.F skipped 15 fields in 5340's frame;
  4.C and 5.D tested inside frames but missed their traps and focus
  jumps; the key's 1.3.1 and 4.1.2 Fails on the embedded-app pages are
  iframe content (Abby).
- **Agent C (the server judge stand-in)** answered every question, and
  repeatably, but about 45% of the cells its answers decided were false
  FAILs: 4.F J1 on 5-6 pages, 9.C J1 on 2.
- **Agents relayed rule errors faithfully** (A) or made their own (B: 15-19
  false PASSes per run).

## Order

1. **Principle 3 first:** fixes 1-6 (a failure passed, or set aside as
   Does Not Apply).
2. **Frames** (fix 7): they feed fixes 2, 3 and 5 and the 1.3.1 and 4.1.2
   cells.
3. **False FAILs by rule:** fixes 8-11 (5.A alone is 7 cells per run).
   **Fix 9b (testing what interaction reveals) is a principle 3 fix:**
   build it with the frames work (fix 7), and before fix 9 removes any
   FAIL, check the key's failing element is still found.
4. **Questions and pictures** for any judge: fixes 12-14 (before
   ApiJudge is switched on for 4.F or 9.C), and fixes 24-28, which turn
   most unsure answers into decisions or remove the question.
5. **Cross-page and harness:** fixes 15-19.
6. **Process:** fixes 20-23, and CI (fix 29).

## Fixes

### Principle 3: a failure passed or set aside

#### 1. 3.A: video that never played became Does Not Apply
- **Evidence:** 14592. Key: Not Tested, "several videos appear to
  contain flashing content". TOBI: DNA, "Triggers: none. No trigger
  fired, so no capture ran."
- **Fix:** a page with video the capture did not decode is NEEDS REVIEW
  for 3.A, never DNA (no trigger is not evidence of no flashing). Then:
  decode video that does not autoplay (the media store's bytes, as
  flashcap does for media that plays) so it can be counted.
- **Fixture:** a page with a click-to-play video holding a known flash.

#### 2. 4.C: an exit that only moves focus within the trap
- **Evidence:** 5340. Key: Fail, the embedded app (iframe) is a trap.
  TOBI: PASS by M4, "pressing Enter on View timeline lets focus move on",
  but focus stays in the app.
- **Fix:** an exit counts only when focus leaves the looping set of
  stops (here the frame), not when a key moves it within the set.
- **Fixture:** an iframe whose Tab loop has a button that moves focus to
  another control in the same frame.

#### 3. 4.C and 5.F: error states, including JS-only validation
- **Evidence:** 5340. Key: the "year before 1900" error popup is a
  keyboard trap. 5.F's error pass never ran there (frames, fix 7), and it
  types "abc" into every text field.
- **Markup can show where errors are likely, never that there are none:**
  `required`, `pattern`, `min`/`max`, `maxlength`, `type`, `inputmode`,
  `autocomplete`, `aria-invalid`, `aria-errormessage` and
  `aria-describedby` pointing at empty or hidden message containers,
  `role="alert"` and live regions, `novalidate`, validation library
  attributes. A script-built app may show none of these.
- **Fix (Abby):** standard "likely to error" values by field type and
  purpose: names with odd characters; invalid emails and phone numbers;
  numbers and years outside any declared range, or far past and future
  when none is; dates far past and future (`wrong_date` exists). Then,
  in any error message or dialog that appears, a 4.C exit check.
- **Fixture:** a form whose year field shows a JS dialog for years before
  1900, with no `min`.

#### 4. 4.A: click-to-play video
- **Evidence:** CILab. Key: Fail, "cannot play the video on the homepage
  with only the keyboard, but can with a mouse click". TOBI: PASS, its
  pointer scan found nothing.
- **Fix:** treat a `<video>` (or a cover over one) that a click plays and
  no focusable control plays as a pointer-only element. Confirm the page's
  markup first.
- **Fixture:** a video with a click handler and no keyboard control.

#### 5. 5.D: focus after tabbing away from an edited field
- **Evidence:** 5340. Key: Fail, after editing name or year, Tab sends
  focus back to the start of the frame. TOBI: PASS, "none moved focus on
  its own".
- **TT:** 5.D How to test step 3, "Exit (tab away from) the completed form
  element and determine whether there are any instances of an unexpected
  change of context"; step 4 lists a change of focus.
- **Fix:** after each input, one Tab; compare where focus lands with the
  walk's next stop. Elsewhere is a change of focus (unless the page
  says so first, step 4a).
- **Fixture:** a field whose change handler, on blur, focuses the first
  control of its container.

#### 6. 9.A-9.C: other pages from another template
- **Evidence:** CILab and 14592 were each other's only other page (our
  pairing), different templates, so 9.A was DNA where the key fails (no
  skip link), and 9.B and 9.C DNA where it passes.
- **Fix, now:** when the other pages share almost nothing with the
  tested page, 9.A-9.C are NEEDS REVIEW ("the other pages may be another
  part of the site"), not DNA. **Later (service):** VAST keeps a
  site-wide record of templates with example pages; a page matching one
  inherits its 9.A-9.C context, a page matching none says so (Abby).
- **Fixture:** two pages of different templates as each other's only
  other page.

### 7. Frames, as TT tells a person to test them
- **Evidence:** fixes 2, 3 and 5; 5.F "15 form field(s) are inside
  frames, which this test does not check yet"; 5.C's spec reads no
  frames yet (a NEEDS REVIEW note, never an absence, as it should).
- **TT:** a tester runs ANDI inside the iframe's own context (Appendix
  D, iFrame workaround: switch the console into the frame and run ANDI
  there); Abby opens the frame in its own window and reruns ANDI.
- **Fix:** every 5.x test reads fields in frames: same-origin frames in
  place; cross-origin frames by loading the frame's URL as its own page
  (its own recording, ANDI injected there), with findings located by
  frame chain. Then 4.x checks that already enter frames reuse it.
  Reported location: "in the frame <title or URL>".
- **Fixtures:** the vendored ACT and Baseline frame cases, and 5340's
  shape (a form in a cross-origin frame).

### False FAILs by rule

#### 8. 5.A: an icon button in the same input group is a visible label
- **Evidence:** 7 pages per run. The search field's placeholder
  "Search..." plus a magnifier submit button ("Search!") and a clear
  button, in one Bootstrap `input-group` (shared border: the field has
  `border-end-0`, the buttons `border-start-0`), inside
  `<form role="search">`. Key: Pass ("has visual labels/instructions").
- **TT and WCAG (Abby):** icon-only visible labels are acceptable for
  commonly understood functions (search, menu, download).
- **Fix:** M3 does not fail a placeholder-only field when an icon button
  sits in its input group or search form; it asks J1, the graphic case
  (settled by looking, principle 8). 5.B then has a visible label to
  judge (the 4 DNA cells follow).

#### 9. 5.C: controls that are aria-hidden and outside the Tab order
- **Evidence:** carousel scroll buttons on 14592, 14194, Galleries:
  `aria-hidden`, never reached by Tab (ANDI: "focusable but … aria-hidden",
  so `tabindex="-1"`), and Tab alone reaches every card. Key: Pass.
- **Fix:** 5.C skips such controls (they are in neither the Tab order nor
  the accessibility tree; ACT 6cfa84 concerns sequential focus
  navigation). Still fail aria-hidden controls that Tab reaches.

#### 9b. Test what interaction reveals, as a person does (principle 3)
- **Evidence:** Home. Key: 5.C Fail, "inside the card feed filter options,
  all of the X buttons for each category/page type have the same title,
  making it impossible to know which category/page type you are
  excluding". Those X buttons (each named "Remove filter from selection")
  appear only after a filter is chosen; TOBI never saw them. (TOBI's Fail
  on Home was right on other elements: the filter headings, fix 9c.)
- **Why it matters beyond 5.C (Abby):** a person opens everything on the
  page (menus, accordions, tabs, filters, dialogs, "show more") and runs
  every test on what appears, not only on the state at load. TT says so
  for several tests: changes after interaction are included (4.A ER
  Note 1; 5.C Notes). Today TOBI opens the first 6 menus or disclosures
  (4.F's pass R, `REVEAL_MAX`) and reads fields that appear while 5.D
  fills a form (`labels.read_revealed`); 5.C's summary says "others a
  person may reveal are not covered", but that note does not stop a PASS.
- **Fix:** a reveal pass shared by every test: open each disclosure,
  menu, tab, accordion, filter option and dialog trigger (bounded, each
  on a fresh replay), record what appeared, and run the tests that read
  components or focus (4.A, 4.D, 4.F, 5.A-5.D, 2.x where relevant) on it.
  Where the bound stops it, or a trigger cannot be opened, a test that
  would PASS is NEEDS REVIEW with that reason, never PASS.
- **Fixtures:** a filter whose checked options add "remove" buttons with
  one shared name; an accordion holding an unlabeled field.

#### 9c. 5.C: card text leaks into a checkbox's visible text; filter headings
- **Evidence:** Home's 36 filter checkboxes (3 filter forms, two sets
  each: "NASA Science category" and "Page type"). Each form wraps its
  section's result cards, which script adds, so card text such as
  "ID: 15116" sits inside the form and lands in each checkbox's nearby
  text. That breaks the set merge (5.C 1.2.0 asks one question per set
  only when the option's announced text holds every word shown beside
  it): 36 questions instead of 6. It also confused the judge ("ID: 15116
  belongs to the video, not this"), whose answers then differed within
  one set (20 missing, 7 complete, 9 unsure).
- **Decision (Abby, 2026-11-08):** a heading over a set of filter
  checkboxes is the question the set answers. Shown only visually, it
  passes the visual tests (5.A, 5.B) and fails 5.C when it is not
  programmatically connected (a fieldset and legend, or a group labelled
  by it): TT p. 27 Note 4, as on www.nasa.gov's Missions filters (round
  1, 5.C 1.3.0, M3s). So the judge's "missing" answers on Home were right.
- **Fix:** nearby text for an option is the text of its own row: within
  the nearest container that holds the option and its label but no other
  option or link (5.A section 2, which pass L shares with 5.A and 5.B;
  judge eval after). And widen M3s: a heading directly over a set (no
  other content between them) whose options do not announce it fails
  without a question, as several headings over one field name do now;
  a heading further away stays J1's (Note 5, section titles).

#### 10. 19.A: the site search's own results page
- **Evidence:** Search. Key: Pass, top-nav search is one way, tag links
  that open a filtered search are a second (content links). TOBI: FAIL,
  only links.
- **Fix:** a page that is the site search form's target counts as
  reachable by search.

#### 11. 19.A: quoted search and the whole first page of results
- **Evidence:** 14592. The site answered "No results for:" the unquoted
  heading (recorded reply: an empty list). Abby found it searching with
  quotation marks.
- **Fix:** when the plain search finds nothing, search again with the
  heading in quotation marks (still one search request per form, so two
  at most); read the whole first page of results.

### Questions and pictures (any judge)

#### 12. 4.F J1: different from the visual order is not "does not preserve"
- **Evidence:** Agent C answered "does not preserve" on 5-6 pages where
  the key passes. Its reasons: carousel cards reached right to left,
  Download before its copy-link button, sidebar sub-items, "Shift+Tab is
  not a clean mirror".
- **Fix:** the rubric says the question is meaning and operation (TT 4.F),
  not matching the visual order; examples that preserve meaning
  (carousels, a card's own buttons, a sidebar's sub-list). Judge eval on
  these pages' order pictures before ApiJudge answers 4.F.

#### 13. 4.F's order picture draws stops nobody can see
- **Evidence:** C saw "empty boxes 28, 30 and 32", "badges 19, 20, 21
  overlap boxes 16, 17, 18", "27 on an empty box".
- **Fix:** draw only stops with a visible box; list hidden or off-screen
  stops in text instead. Part of the cropping review (Abby: whether we
  should crop more pictures than we do today).

#### 14. 9.C: pair repeated components, not every link with one destination
- **Evidence:** Home and Help. Body links to the same address with
  different words ("search page", "See more recently released
  visualizations") were paired, and the rubric calls different words
  "inconsistent". Key: Pass.
- **Fix:** 3.2.4 is about the same component repeated across pages.
  Pair within the repeated blocks (header, nav, footer, search) or the
  same role in the same region; leave content links in different
  contexts unpaired.

### Cross-page and harness

#### 15. Answer keys: a reason for every Pass
- 5144's 5.D key row was Fail with a pass comment (a slip the SCRT
  template made when child rows were deleted); adjudicated Pass. Keys
  should give the reason for a Pass as well as a Fail, above all for
  judgment calls (Abby).

#### 16. The scorer: adjudications per criterion
- The locked scorer applies an adjudication to the tool's per-TT score
  only, not to the arms' per-criterion rows. Apply it to both before
  round 3's lock.

#### 17. The scorer: judge-decided cells apart from rule-decided cells
- Round 2's split (which cells an answer decided) was computed outside
  the scorer. Build it in, so a judge is neither credited nor blamed for
  a rule.

#### 18. Pairing pages for an agent's conversation
- Give cross-page tests pages of the same template, or all the round's
  pages (fix 6 is the tool's side).

#### 19. Three tests failed once under load
- `test_fixtures_4d.py::test_fixture[f10-100-links]`,
  `test_fixtures_5f.py::test_outcome[f20-slow-check]`,
  `test_time_budget.py::test_more_fields_than_5d_checks_leaves_out_only_5d`
  failed in a full run beside other work and passed alone. Watch main's
  CI; make them load-tolerant if they fail there.

### Unsure answers: what would decide them

Agent C answered "unsure" on 62 of 194 questions (repeat 1). Against the
key, about 50 have a cause in our rules or questions, and about 30 would
not be asked at all:

| Test | Unsure | Key | Why unsure | Decided by |
| --- | --- | --- | --- | --- |
| 4.A | 21 | Pass 17, Fail 4 | Carousel scroll arrows; category and globe icon links: "does a reached stop do the same thing?" | Fixes 24, 25 |
| 5.C | 15 | Fail | Home's filter checkboxes, one by one, with card text mixed in | Fix 9c: decided by rule (a heading directly over the set), else 6 questions, not 36 |
| 9.C | 13 | Pass | Generic "Go to this page" card links paired across pages | Fix 14 (not asked) |
| 4.D | 7 | Pass | 48 x 47 px crops, "a faint ring" | Fix 26 |
| 2.B | 4 | Does Not Apply | A loader animation (a real judgment); a region whose two pictures do not differ | Fix 27 |
| 4.F | 2 | Pass | Order picture with empty boxes | Fixes 12, 13 |

Left as real judgments: the Search page's loader animation, and perhaps
the globe icon category links. Fixing 9c and 14 alone removes about half
of a page set's unsure answers, the people's queue the pivot plan counts
(about 62 per 10 pages).

#### 24. 4.A: a scroll arrow whose items Tab reaches
- A pointer-only arrow (often aria-hidden, `tabindex="-1"`) that scrolls a
  container whose items the Tab walk reaches already has a keyboard way
  (Abby's carousel reading, fix 9). Decide it mechanically from the walk:
  every item the arrow reveals is a stop.

#### 25. 4.A J1: give the candidate's destination
- For a pointer-only link or control that navigates, put its destination
  and any reached stop with the same destination in J1's input; a
  same-destination stop is a mechanical match (no question).

#### 26. 4.D: pictures big enough to judge, and the ring as a fact
- Crop with context around small elements and scale up for the judge;
  give "the changed pixels form a ring around the element" as a measured
  fact in the input. Part of the cropping review.

#### 27. 2.B: a region with no visible motion
- A pass T region whose before and after pictures show no difference is
  not presented as moving (5340's 41 px box at the top).

#### 28. Judge requests: the page's shared inputs once
- See the pivot plan: put a page's shared inputs first and send its
  questions together, for the prompt cache.

### Process

#### 20. A list of the rules' judgment calls
- One document of the calls the specs make where another Trusted Tester
  might reasonably differ, with the posture behind them ("pass
  conservatively, fail liberally", and "what leads to clearly better
  UX?"). Agencies and their Section 508 coordinators can fork the specs
  and change those calls for their context (Abby).

#### 21. A person's answer only from TOBI's own UI
- Close MCP's `decided_by: "human"` path (an agent can claim it today);
  see the pivot plan's "Human answers".

#### 22. 4.D OVERVIEW tab on 5340 (unconfirmed)
- TOBI: FAIL, 0 px change with focus (its pictures are identical); key:
  Pass. Abby is retesting from her laptop. If confirmed, record it in
  `adjudications.json` as a validated catch.

#### 23. Archive and harness notes
- Archive sets leave out files identical to an earlier set's
  (`same_as` in the manifest), and are restored in order;
  `ARCHIVE.md` in each round folder.

#### 29. CI: skip docs-only changes, run in parallel
- A docs-only push runs the whole suite (about 20 minutes on #26-#28).
  Skip the test, container and CodeQL jobs when only `docs/**` and
  `**/*.md` change (`paths-ignore`, or a paths-filter job the others need);
  split the suite across a job matrix by test-file group (Abby,
  2026-11-08).
- **Built (`.github/workflows/ci.yml`):** a `changes` job diffs against the
  base; docs-only means every changed file is under `docs/` or is `*.md`,
  except `README.md`, `docs/rules/**` and `docs/sources/**`, which tests
  read (the specs are outcome logic). Then `lint` and a four-group `test`
  matrix (keyboard 4.x, forms-and-site 5.x/9.x/19.A, motion-and-cases 2.x/3.A/ACT/baseline,
  rest = everything unnamed, so a new test file is never dropped) run;
  otherwise they are skipped. `CI` is the one check to require (skipped
  counts as passed). Container image already filters by path. CodeQL is not
  a workflow file in the repo (GitHub's default setup): its path filter is
  a repository setting for Abby. Group balance is untimed: check the first
  runs and move files between groups.

## Done during round 2 (delivery and harness, not rules)

- **Results fit the client's limits** (`pipeline.fit`, 45k characters;
  `docs/solutions/large-pages-results-and-replays.md`).
- **Replays of large recordings wait 120 s** (`replay_navigation_timeout_ms`).
- **Harness:** `--group`, `--group-size`, `--debrief` for either arm, the
  CLI's result limit pinned and recorded.
- **`Answer.answered_by`**, set by the server.
- **Agent C** (`evals/agent/judge_c.py`, `judge_c_prompt.md`): the first
  draft of ApiJudge's prompt and request.
