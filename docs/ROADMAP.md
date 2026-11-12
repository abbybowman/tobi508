# Roadmap

What is left to build, and the one place that says what is scheduled when.
A living list, not a log: delete an item once it is built, and put any
decision it needed into the spec, CLAUDE.md or `docs/solutions/` where it
belongs. Plans in `docs/plans/` hold the detail of an item; they do not
keep their own schedule.

## Where things stand (2026-11-12)

- **22 TT tests are built** (spec 1.0.0 or later, check registered,
  fixtures passing): 2.A-2.D, 3.A, 4.A-4.F, 5.A-5.D, 5.F-5.H, 9.A-9.C and
  19.A. Each spec's `spec_version` is its version of record; the
  [README](../README.md) has a status line per test.
- **Direction** (Abby, 2026-11-07;
  [plan](plans/2026-11-07-server-judge-pivot.md)): the server judges, a
  person reviews, the client agent explains. TOBI becomes a hosted service
  on VAST with its own pinned judge model (ApiJudge), because calling
  agents skipped or guessed at open questions whatever the wording.
- **Evals.** Judge eval runs are in [evals/README.md](../evals/README.md).
  Agent eval rounds 1 (nasa.gov) and 2 (svs.gsfc.nasa.gov) are scored
  against Abby's blind SCRT files
  ([evals/agent/README.md](../evals/agent/README.md),
  [round 2 scores](../evals/judging/round2-armc/abc-score.md)). Round 2:
  no false PASS came from a judge's answer; the rules alone gave 3 false
  PASS, 2 missed fails and 13-15 false FAILs per run, which is what the
  [post-round 2 fixes](plans/2026-11-08-post-round2-fixes.md) are for.
  Both sites are development sites now.
- **The code review** (2026-11-11 and 12;
  [reviews/2026-11-11-code-review.md](reviews/2026-11-11-code-review.md)):
  32 P0 items, 30 of them a wrong PASS or DOES NOT APPLY that a small
  page reproduces. The rows match the specs in all 22 checks; the
  errors are in what the rows are fed, and nothing looks again at a
  PASS or a DOES NOT APPLY. What follows from it is planned in
  [plans/2026-11-12-coverage-second-look-thin-agent.md](plans/2026-11-12-coverage-second-look-thin-agent.md)
  (parts A to J) and slotted into the order of work below.
- **Time.** A run tests the whole page by default and stops only at
  `MAX_RUN_S` (1800 s); `no_time_limit=false` holds it to `RUN_LIMIT_S`
  (600 s). Lessons and measurements:
  [solutions/time-budget.md](solutions/time-budget.md).

## Now: to the Nov 20 demo

Scope (Abby, 2026-11-11): a middle path between the small core and the
full pivot. Reliability comes first: the code review's wrong PASS and
DOES NOT APPLY results, the rules' false FAILs, and the "unsure" answers
that are answerable. Then a check of how far results have moved since
round 2, then as much of the pivot core as steady progress allows. TOBI
is a prototype whose tests keep improving; none of this is a formal gate
(Abby, 2026-11-12). Every change to a test updates its README status
line and the README's "Known wrong outcomes" table in the same commit,
so the README always says what each test can and cannot do today.

### Order of work

**Use the step numbers below.** Plans use other numbers for the same
work: "fix 8" is a post-round 2 fix, "bundle 5" a pivot-plan bundle,
"part A" a part of the plan after the code review, "E-01" a code review
item. They appear only in the last column, to find the detail. Each
step is one thread, started with its prompt in
[reviews/2026-11-11-code-review-fixing.md](reviews/2026-11-11-code-review-fixing.md),
"Starting a thread". Run at most three threads at once: more hit the
5-hour usage limit twice during the review.

| Step | What | Model | When | Detail (other numbers) |
| --- | --- | --- | --- | --- |
| 1 | Quick fixes for wrong PASS and DOES NOT APPLY, and CI | Sonnet | now | Plan part A and part I's CI step; PR #39 |
| 2 | A count of what exists, and the guard that holds DOES NOT APPLY | Opus | now | Plan part B |
| 3 | Server judge and gate fixes; sign-in ownership; a person's answer never through MCP | Opus | now | Review bundle 7 (B-01, B-02, L-02, L-03, G-02, B-04); A-01, S-05; fix 21's first step (A-05) |
| 4 | The rules' false FAILs | Opus | now, or when a thread finishes | Fixes 8, 9c, 9, 10, 11; pivot bundle 5 |
| 5 | "Unsure" answers that are answerable | Sonnet | when a thread finishes | Fixes 12, 13, 14, then 24-27; pivot bundle 4 |
| 6 | The check against round 2 | Opus | when 1 to 5 are merged (about Nov 17) | [Judge build plan](plans/2026-11-08-apijudge-build.md), "What is left", 1 |
| 7 | The pitch: one scored run at the submission commit, rehearsal, fallback video | Abby, with a Sonnet thread for the run | Nov 18-19 | [docs/hackathon/](hackathon/README.md) |
| 8 | If the days allow: the second look's trial | Sonnet | after 6 | Plan part F, "Trial" |
| 9 | If the days allow: sign in on VAST from Claude Code and run one page | Opus | when the admin's answers arrive, after 3 | [Hosted sign-in plan](plans/2026-11-06-hosted-auth.md). The demo for reviewers is recorded (Abby, 2026-11-12), so this is not needed for it |

**Merging.** Steps 1 to 5 change some of the same checks, specs and
README rows. Each thread branches from `main`, opens a pull request
every few items, and before it bumps a spec version or edits the
README tables it merges `main` and takes the next free version. A
thread that started before another's pull request merged carries on and
merges `main` at its next pause.

### What each step covers

1. **Quick fixes and CI.** One line or one function each, no spec
   decision except two rows reworded: 4.A's hover cap, 4.C passing after
   it ran out of time, a `#fragment` read as navigation (4.E, 5.D, menus
   opened by `<a href="#">`), 4.D's arrow loop, 2.B's missing row for
   players, 2.A's late audio, placeholder addresses in 4.A and 9.C, the
   tested page given again as an other page. CI: the inject tests run in
   CI, docs-only means `docs/`, job timeouts.
2. **The count and the guard.** About ten of the wrong DOES NOT APPLY
   results (forms in web components or behind a button, a form that is
   only a button, a header in a web component, audio from a script,
   more than 30 images, a canvas page) become NEEDS REVIEW with a
   sentence that says what was not checked. Abby agreed on 2026-11-12
   that a guard may move DOES NOT APPLY; the template and CLAUDE.md
   principle 3 change with it. **Built, 2026-11-12, waiting for Abby's
   review of the spec changes:** `count.py`, the play hook, guard CN,
   and `count:` in 16 specs; the review's pages are fixtures in
   `tests/test_fixtures_count.py`. Left open: DHS's Baseline cases
   TC10.A-ic-dna-1 and -2 (a field hidden with nothing that opens it),
   19.A's FAIL on a header in a web component (a guard never moves a
   FAIL), and the keys for 2.B's players, canvases and web-component
   media and for 2.C.
3. **Server judge, gate, sign-in.** Before step 6's figures are used:
   the gate asks for a minimum number of decided cells and counts a
   wrong DOES NOT APPLY; picture links only through the guarded reader;
   page text cannot close the untrusted block; one picture once a
   request; judging outside the browser slot. `decided_by: "human"`
   through MCP is recorded as the calling agent's. Jobs carry their
   caller; a token with no `sub` is refused.
4. **False FAILs by rule,** largest first: fix 8 (5.A, an icon button
   labels the search field: 7 cells a run), 9c and 9 (5.C option rows
   and hidden controls), 10 and 11 (19.A's search page and quoted
   search). Each is one spec change (MINOR), one fixture, the suite.
   They turn a FAIL into PASS, the direction where a false PASS can
   creep in, so each comes with a fixture of the near case that must
   still FAIL.
5. **Answerable "unsure",** largest first: fix 12 and 13 (4.F: the
   rubric and the order picture; the server judge's wrong FAILs on 5-6
   pages), 14 (9.C pairs repeated components), then 24-27 (4.A carousel
   arrows and destinations, 4.D pictures, 2.B still regions). A judge
   eval for each changed question.
6. **The check against round 2.** Rerun round 2's 10 frozen pages once,
   with that day's rules and the server judge answering (CLI route, or
   Luna if its endpoint is ready; count the requests with `--dry`
   first), and score with the same scorer beside round 2's locked rows,
   judge-decided cells apart from rule-decided ones. It gives the
   before-and-after figures for the pitch (a development site, said so)
   and shows which question types Abby can switch on (`JUDGE_TYPES`).
   A new round folder; the locked rounds are never rewritten.
7. **The pitch,** with the last two days kept for it: the [FILL]
   figures from one scored run at the submission commit, a rehearsal
   and the recorded demo.
8. **The second look's trial:** one request per frozen round 2 page,
   with the rules as they were at round 2's lock, asking the server's
   model to look again at the rules' PASS and DOES NOT APPLY results.
   It measures; it changes no outcome. It can wait until after the demo.
9. **VAST end to end,** for the hosted story; the reviewers see a
   recording.

**Not before the demo:** the plan's parts C, D, E, G and H (steps 11 to
17 below), the review UI and WebAuthn, opening everything phases 2 and
3. For the pitch, say what the review found and what is planned.

## Next: after the demo

Steps continue from "Now", in this order unless a judging round says
otherwise; whatever of steps 1 to 8 was not reached comes first. Parts
are those of
[plans/2026-11-12-coverage-second-look-thin-agent.md](plans/2026-11-12-coverage-second-look-thin-agent.md);
fix numbers are the
[post-round 2 fixes](plans/2026-11-08-post-round2-fixes.md); bundles are
the [pivot plan's](plans/2026-11-07-server-judge-pivot.md). Model:
Opus unless the plan's part says where Sonnet suffices (filling the
grid's pages, the token cuts, carrying a pattern Opus has set through
the remaining checks).

10. **A grid of hard pages** (part I; 2 to 3 days): nine shared pages (a
   shadow root, a frame, more than a cap, a trap, a late start, text not
   in English, hidden text, a form behind a button, a failed reading)
   run against every check, never PASS and DOES NOT APPLY only with a
   reason. It is the test for steps 11 and 12. With it: one recording and
   one walk per fixture page, which is most of the suite's time.
11. **Every reading reports what it covered** (part C; about two weeks,
   reader by reader). One coverage record from each reader and one rule
   in the engine: no PASS or DOES NOT APPLY on a reading that is not
   complete. It replaces each check's own "incomplete" list. The
   checks' shared base goes in with it (one finding builder, one "out
   of time" helper), which is what "Tidy the checks" was. Every outcome
   stays the same except where a gap now holds one back.
12. **One library for reading the page, frames included** (part D; 4 to
   5 days). Shadow roots and same-origin frames are read by every
   reader; a cross-origin frame is loaded as its own page. This is
   fix 7 (bundle 3) and more: it is also what turns part B's "not
   checked" sentences into real results.
13. **Opening everything, phases 2 and 3.** Phase 1 is built (`reveal.py`;
   guards RV and RC). Phase 2: 4.A, 4.C, 4.D and 4.E (and 4.F past its
   first six triggers) walk the keyboard through opened content, which
   removes guard RC. Phase 3: 5.D fills fields in opened content. Also
   nested triggers, a combobox's list, buttons that need a key other than
   Enter, and phase 1's caps (20 triggers, 3 sets). From the review: a
   trigger is "opened" only by what appears in the region it controls
   (C-02), and a plain button with no ARIA marker opens nothing today
   (H-08; part B holds the outcome meanwhile).
14. **Meaning goes to the judge, not to a word list** (part E): 5.H's
   consequence and "checked" words, 4.B's timing words, the "pause"
   words in 2.x. One spec change and one judge eval each. Then the
   spec decisions the review marks "(needs Abby)".
15. **The store, a thin MCP surface, one writer per run** (part H;
   bundle 7, moved ahead of the review UI, which needs it). The server
   keeps the report; the agent gets a short result and a link; tools
   have no output schema; a job has an owner; answers run as a job.
   Target: about a third of today's 93,000 tokens a page. The rest of
   bundle 7 as planned: run index, answers kept by content hash and
   spec version so a question about the same image or media is answered
   once per site, retention and the disk check, job state that survives
   a restart. Plan first: what is stored, for how long, and who may see
   answers from another user's runs.
16. **A person's answer only from TOBI's own UI** (the rest of bundle 6):
   Trusted Tester and reviewer roles, WebAuthn on submit, the evidence
   page. Design and options in the pivot plan; decide the review view
   there before building one. Added by part G: the whole page beside
   every crop, the list of what was not looked at, a sample of PASS and
   DOES NOT APPLY results for a Trusted Tester to confirm, and every
   dispute turned into a fixture.
17. **The second look as a guard** (part F), shaped by its trial (not a
   gate: Abby, 2026-11-12). Its README line says what the trial caught
   and missed.
18. **Round 3** on a site not used before, after the scorer fixes (15-17)
   and the gate fixes (L-02 to L-04, L-13).
19. **SCRT files, phases 2 and 3**
    ([plan](plans/2026-11-02-scrt-io.md)): TT review, merging a partial
    file (which is also how to verify a fix: `verify_fix` on
    `tobi_run_tt_tests`, taking a saved report), export to the real SCRT,
    site roll-up. Fix advice for a read report is a separate, optional
    tool.

The review's other items (its P1 to P3 lists, and bundles 5, 7 and 8 of
its "How this could be handed out") are taken from the review file
itself, one bundle a thread; they are not repeated here.

## Decisions waiting for Abby

**Soon: each holds up a step of "Now".**

- **The judge's endpoint for step 6.** The CLI route (`claude -p`, as
  round 2's Agent C) works today. If Luna is to be used: its API shape
  (Anthropic Messages or another), base URL, auth header, vision input
  limits, structured output, rate limits and token quota. Ask Sage has
  no tokens this month.
- **Publishing the repository.** GSA asks for a GitHub repository;
  SECURITY.md says NASA's release review comes before the code is
  public. Which comes first for the submission (step 7).
- **Windows headed Chrome** was last run on 2026-11-02, before most of
  today's specs. Run it again before the scored submission run, or state
  the limit ([browser checks](../specs/rules/_browser-checks.md)).
- **`JUDGE_TYPES`:** the question types to switch on, after the check against
  round 2 (step 6).
- **The VAST admin's answers** (step 9 only): pulling the image, a
  Chromium service in the namespace, `sub` and groups in access tokens
  ([hosted sign-in plan](plans/2026-11-06-hosted-auth.md), "Open
  questions for the VAST admin"). Also whether NASA's Keycloak can ask
  for a security-key touch on one action rather than at sign-in: to try
  on VAST.

**After the demo: each shapes a step of "Next".**

- **Spec decisions from the review:** a form behind a plain button
  (H-08), a page that is only a canvas (E-03), native controls that
  answer only `mousedown` (E-08), a title that is a control's only
  label (E-13), `aria-controls` as a field's "own widget" (H-04), 9.C
  pairs with no name on either side (K-05), a form whose button is
  `type="button"` (M-01) or that is only a button (M-02), 4.D's "moved"
  signal (F-02), an element Tab can never rest on (C-07), 4.F's "order
  does not matter" making the test DOES NOT APPLY.
- **CLAUDE.md's lists:** principle 8 does not name 4.A J1 and J2 or
  4.B J1, which settle a PASS by looking (E-06); principle 5 does not
  name 9.A's key press (M-15) or the media store's fetches (S-04).
- **Is `tobi_answer_questions` offered on a hosted server** with the
  judge on, or only locally (part H).
- **4.F has guard RV but not RC** (its pass R already Tabs through what
  its first six triggers open): confirm, or put RC back.
- **9.A as a candidate for guard GU** (it presses Enter on skip links).
- **2.B: content whose changes are random can be DOES NOT APPLY.** A
  region that changed at a steady pace until 4 s, and after 5 s only
  repeated what it had shown (random colours: about 1 load in 16), is
  "not still moving". Option: such a region whose last change is within
  about one period of the 5 s mark is NEEDS REVIEW
  ([solutions/environment.md](solutions/environment.md), "A test that
  fails only on a busy machine").
- **The settle rule can call a page settled before it reacts.** It waits
  two animation frames, then 150 ms with no DOM change. A page whose
  first change comes later (a submit handler on a timer, a reply to a
  request) reads as quiet: 5.F can miss an error shown late, and with no
  other indicator the page would be DOES NOT APPLY. Options: a minimum
  wait after a submit press, or a second read when an attempt shows
  nothing. Every test uses the rule, so it is a 4.C spec decision. The
  review reproduced the same miss three other ways (M-06: an error in
  a shadow root, on a wrapper, or gone in 60 ms); "something changed
  that was not read as an error" should be NEEDS REVIEW (part C).
- **A second browser.** Whether a Firefox replay matters for the pitch,
  or the documented limit is enough (the report records its browser).
- SECURITY.md's two [TO CONFIRM] items (the reporting route; how long
  `runs/` is kept on NASA machines).

**Answered** (Abby, 2026-11-12; recorded in the
[pivot plan](plans/2026-11-07-server-judge-pivot.md)): who may answer
which question, accounts outside NASA, the extension's distribution, who
confirms a Trusted Tester, live page or recorded copy for a final SCRT,
a data-handling note for public screenshots (none needed), and reviewers'
access to the hackathon demo (a recording).

## Known limits, per test

**Not every limit is NEEDS REVIEW-safe today.** The code review's P0
table lists 30 cases that give PASS or DOES NOT APPLY, each with a page
that shows it; the ones that are a stated limit are marked below. Until
parts A to D land, a PASS or a DOES NOT APPLY means "in what the tool
looked at". Browser checks still to run (mostly Windows headed Chrome)
are in [specs/rules/_browser-checks.md](../specs/rules/_browser-checks.md).

- **Web components (shadow roots):** the keyboard walk enters them; the
  label pass, the site read, the media read, 4.A's handler scan and
  5.F's error read do not. Since part B's inventory and guard CN
  (2026-11-12), a form, navigation or sound inside one is NEEDS REVIEW
  in 5.A-5.H, 9.A-9.C and 2.A, not DOES NOT APPLY (D-01, K-02, M-12,
  N-01). Still open: 4.A can PASS with a mouse-only control inside one
  (D-03), 5.F and 5.G miss an error shown in one (M-06), and 19.A fails
  a page whose shared header is one (K-02; a guard never moves a FAIL).
  Part D reads them.
- **Content that opens:** a form behind a button with no ARIA marker is
  never opened; since guard CN its hidden fields make 5.A-5.H NEEDS
  REVIEW, not DOES NOT APPLY (H-08, M-07), and so does an editable text
  area (`contenteditable`). Then "Opening everything". (A menu whose
  trigger is `<a href="#">` is read now: C-03, fixed.)
- **The watch is 6.5 seconds:** what starts later is DOES NOT APPLY in
  2.A, 2.B and 3.A (2.C says NEEDS REVIEW); a blink 2.5 times a second
  can be missed; flashing below the first screen and an animated image
  past the 30th are not measured (N-02 to N-09, W-02, W-09); an
  animated image past the 30th now makes 2.B and 3.A NEEDS REVIEW
  (N-06, guard CN). Parts C and J.
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
- **5.A, 5.C, 5.F, 5.G:** fields in frames are not read (a NEEDS REVIEW
  note; fix 7, now part D). Fields in shadow roots are not read either
  and get no note (above). 5.F and 5.G leave `time`,
  `datetime-local`, `month` and `week` fields as loaded in attempt 2.
- **5.F, 5.G, 5.H:** a form whose button is `type="button"` is never
  submitted (M-01); a form that is only a button is not seen (M-02);
  5.H's consequence words are English only, and no match is DOES NOT
  APPLY (M-03). Error handling done on the server cannot be replayed
  from a recording: 5.F answers NEEDS REVIEW when a form is sent, and
  that stays.
- **5.B:** icon-only buttons are left out (pass L has no picture of
  buttons).
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

## Later

- **The next tests: the visual-versus-code cluster** (10.x, 14.x, 15.A,
  18.A, 13.C; ANDI is the core evidence for most). Research, with two
  decisions to make in the specs (13.C: ANDI compares contrast after
  rounding, so 4.495 passes; 18.A: which windows, real browser zoom
  through our own extension, a second walk's time):
  [per test](research/2026-11-07-visual-cluster-per-test.md),
  [visual judgment](research/2026-11-07-visual-judgment-and-apijudge.md),
  [coverage map](research/2026-10-31-tt-coverage-map.md). Before 7.C and
  16.B, fix their `tt.json` steps from the printed pages (each repeats
  the previous test's "How to Test").
- **ANDI output beyond forms, and scanners.** Only ANDI's
  focusable-elements module runs today; contrast and image output are
  next (7.x, 13.C). axe-core or HTML_CodeSniffer, if used, are vendored
  with hashes and run on their own fresh load; a clean scan never means
  PASS ([solutions/andi-output.md](solutions/andi-output.md)).
- **Section 508 Baseline Alignment cases** for each new test: vendor with
  `tests/fixtures/baseline/sync_baseline.py` and load each in Chrome
  first.
- **Testing a batch of pages:** each page tested in full in its own call,
  the multi-page tests run once at the end, pages added to an existing
  run. Plan it with the store (Next, 4).
- **A "test a page" prompt** for operators who are not Trusted Testers.
- **The local runner** (part J; the pivot plan's decision 6): the
  browser on the user's machine for pages that are not public, the
  judge and the store on the host.
- **One watch on a paused clock** for 2.A-2.D and 3.A (part J), in
  place of 6.5 real seconds and two more loads.
- **Deployment:** network-level egress rules behind the egress proxy;
  browser calls with no time limit of their own (headed runs stalled
  when the screen locked); two egress tests that installed Chrome on
  Windows never exercises
  ([solutions/windows-chrome-results.md](solutions/windows-chrome-results.md)).
- **Only if time matters again:** more shared replays (4.C's widget check
  with 4.D's pass W; 4.C reading 4.F's pass R; 5.D and 5.F both filling
  fields); merging fixture pages (a merged page keeps every FAIL tied to
  its own instance and row).

## Dropped

- A separate results service and dashboard on Databricks (2026-11-11:
  the store on VAST replaces it).
- OpenACR export (2026-11-11: ACRs are product level, not page level).
- The agent eval's wording judge, seeded faults, GPT, Gemini and Ask Sage
  routes and DHS training pages (2026-11-11: the server is the judge).
