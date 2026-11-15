# Roadmap

What is left to build, and the one place that says what is scheduled when.
A living list, not a log: delete an item once it is built, and put any
decision it needed into the spec, CLAUDE.md or `docs/solutions/` where it
belongs. Plans in `docs/plans/` hold the detail of an item; they do not
keep their own schedule.

## Where things stand (2026-11-14)

- **22 TT tests are built:** 2.A-2.D, 3.A, 4.A-4.F, 5.A-5.D, 5.F-5.H,
  9.A-9.C and 19.A. The [README](../README.md) has a status line per
  test and the wrong outcomes known today; what each cannot do is in
  [KNOWN-LIMITS.md](KNOWN-LIMITS.md).
- **Direction** ([plan](plans/2026-11-07-server-judge-pivot.md)): the
  server judges, a person reviews, the client agent explains, as a
  hosted service on VAST.
- **On real pages** ([evals/README.md](../evals/README.md)): rounds 1
  (www.nasa.gov) and 2 (svs.gsfc.nasa.gov) were blind judging rounds
  against Abby's SCRT files. Later runs on their frozen pages are
  development reruns: they show what a change did, and are not blind
  results. The latest, step 9a (2026-11-14, before step 8's readers):
  no wrong PASS or DOES NOT APPLY on either site; false FAILs 6 on
  round 2's pages and 12 on round 1's; decided cells 91 of 220 on
  round 2's pages (68 in step 6, about 132 in the blind round).
- **Where NEEDS REVIEW comes from** (step 9a, 223 cells over both
  sites): menus and sections that open and were not walked, about 45;
  guard CN (a hidden form, more than 30 images), 44; the judge unsure,
  29; frames, 28; 2.C and 2.D's timer, 20; 19.A, 12. The keys fail
  few of them. Steps 6e, 6g and 8 are aimed at these.
- **Hosting:** sign-in, run ownership and audit lines are built and
  tested against a stand-in provider; nothing has run on VAST yet
  (step 12).
- What each finished step covered and decided:
  [archive](archive/2026-11-14-roadmap-to-the-demo.md).

## Now: to the Nov 20 demo

**The cut** is the end of Nov 17: from Nov 18 only the deck and the
presentation. What is not merged by then waits. Every change to a test
updates its README status line and the "Known wrong outcomes" table in
the same commit.

### Order of work

**Use the step numbers below.** Each step is one thread, started with
its prompt in
[reviews/2026-11-11-code-review-fixing.md](reviews/2026-11-11-code-review-fixing.md),
"Starting a thread"; a prompt is removed from that file when its step
is merged. At most three threads at once. Each thread branches from
`main` and merges `main` before a spec version or a README table edit.

| Step | What | Model | When |
| --- | --- | --- | --- |
| 1-7, 9a | Done: PRs #39 to #63 ([archive](archive/2026-11-14-roadmap-to-the-demo.md)) | | |
| 8 | One library for reading the page: web components and frames | Opus | readers 1 to 3 merged; 4 to 8 in PR #64; the form error tests in frames next |
| 6e | Guard CN on real pages; 2.C and 2.D's timer | Opus | now |
| 6f | 9.C's "Home" pairs; 19.A on CILab; 9.B's budget | Sonnet | now |
| 6g | 4.C and 4.E read the content that menus and sections open | Opus | when PR #64 is merged |
| 10 | Round 3: a blind judging round on a site not used before | Sonnet | when PR #64 is merged |
| 12 | Hosted on VAST | Opus | 12a now; 12b when the environment exists |
| 9b | Rerun of rounds 1 and 2's pages after the steps above | Sonnet | Nov 17, by midday |
| 10b | Round 4, a second blind round, if Abby keys one | Sonnet | Nov 17, at 9b's commit |
| 11 | If the days allow: the second look's trial | Sonnet | |
| 13 | The pitch: one scored run at the submission commit, rehearsal, fallback video | Abby; Sonnet for the run | Nov 18-19 |

### What each open step covers

- **8** (plan part D). Every reader uses one `jslib`; web components
  and same-site frames are read in place, and a frame is opened as a
  page of its own for the tests that use ANDI. Left: PR #64, then 5.F
  to 5.H in frames. Not expected before the cut: two edge cases of
  5.F's error read (a red border on a wrapper; a message gone in
  150 ms).
- **6e.** Guard CN made 58 cells NEEDS REVIEW on 19 real pages and the
  keys fail none. First a table of those cells by cause; then, per
  cause, the smallest change that decides the cell without guessing,
  each approved by Abby before it is built. The same for the timer
  that holds 2.C and 2.D on every svs page. Done: the timer (2.C 1.2.0,
  the clock check; 8 of round 2's cells decided, all agreeing with the
  key). Done: the images (2.B 1.5.0, 3.A 1.4.0; 6 of round 2's cells
  decided, all agreeing with the key). Done: 5.H reading hidden forms
  (5.H 1.9.0; 8 cells decided, all agreeing with the key). To research: fields hidden from everyone (honeypots, reCAPTCHA).
- **6f.** The judge fails "Home" against "NASA, return to the
  homepage" in 9.C on 8 of round 1's pages, and the key passes them:
  the pairing or the rubric. 19.A's FAIL on CILab, not yet looked at.
  9.B's budget from 60 s to 180 s.
- **6g.** Guard RC holds a PASS when a menu or section opened and the
  test did not walk it. 4.F's pass R already opens each trigger and
  Tabs through it, so 4.C and 4.E read that pass (30 of the 45 cells).
  The wording and the moved cells go to Abby first. 4.D and 5.D only
  if the days allow.
- **10 and 10b.** A blind round is run by
  [the how-to](how-to/run-a-judging-round.md): keys locked before the
  tool runs, the run locked before the keys are opened. Until a
  round's run is locked, its page list, keys and freeze stay off
  `main`, on an unmerged branch, and no other thread is told the
  pages. Scorer fixes 15 to 17 come first.
- **12. Hosted on VAST** ([plan](plans/2026-11-06-hosted-auth.md)).
  - **12a, built 2026-11-15** (how-to, smoke test, the smoke test in CI
    against Keycloak; what it found is in the how-to's section 8): a deployment guide
    (`docs/how-to/deploy-on-vast.md`: the one-line Containerfile, every
    setting, where runs are stored, what to check); a smoke test that
    signs in, runs one page, reads its report and shows a second
    person cannot; and that smoke test run in CI against the built
    image and a real Keycloak, not the stand-in.
  - **12b, when the environment exists:** deploy, sign in from Claude
    Code, run one page, confirm the audit lines; then the [PENDING]
    markers go.
  - **Hosted without a gateway,** open questions go to the calling
    agent (`JUDGE_BACKEND=client`); the server judge on VAST waits for
    Luna or another gateway.
  - **Not before the demo:** a store that outlives a restart, the page
    where a signed-in person answers, network-level egress rules,
    NASA's security review.
- **9b.** As step 9a, one repeat, on `main` as it stands. A gate run's
  per-page reports and pre-SCRT files stay out of git.
- **11** (plan part F, "Trial"). One request per frozen page asking the
  server's model to look again at the rules' PASS and DOES NOT APPLY
  results. It measures; it changes no outcome.
- **13.** The [FILL] figures from one scored run at the submission
  commit ([docs/hackathon/](hackathon/README.md)).

## Next: after the demo

Steps continue from "Now", in this order unless a judging round says
otherwise; whatever of steps 8 to 12 was not reached comes first. Parts
are those of
[plans/2026-11-12-coverage-second-look-thin-agent.md](plans/2026-11-12-coverage-second-look-thin-agent.md);
fix numbers are the
[post-round 2 fixes](plans/2026-11-08-post-round2-fixes.md); bundles are
the [pivot plan's](plans/2026-11-07-server-judge-pivot.md). Model:
Opus unless the plan's part says where Sonnet suffices (filling the
grid's pages, the token cuts, carrying a pattern Opus has set through
the remaining checks).

14. **Every reading reports what it covered** (part C; about two weeks,
   reader by reader; sized before the pace of steps 1 to 5 was known). The grid
   of hard pages (step 7) is its test. One coverage record from each reader and one rule
   in the engine: no PASS or DOES NOT APPLY on a reading that is not
   complete. It replaces each check's own "incomplete" list. The
   checks' shared base goes in with it (one finding builder, one "out
   of time" helper), which is what "Tidy the checks" was. Every outcome
   stays the same except where a gap now holds one back.
14c. **Past a forward trap in 4.A, 4.B and 4.F** (step 6d's phase 2;
   approved in principle, Abby 2026-11-14). They read only the forward
   walk and so give up at a forward trap; they read what the other
   passes reached instead. A proposal first, with a two-trap page per
   test, the nearest page that must stay NEEDS REVIEW and the cells
   that move. 4.C's outcome is untouched, and 4.F does not PASS on the
   backward walk alone where a forward trap whose only exit is the
   opposite direction was logged for it. Opus: it is a design, not a
   pattern to carry through.
14b. **P6's stops to 4.D and 4.E** (from step 6d, 2026-11-14). 4.C's mouse
   bypass (P6) reaches stops that neither the Tab nor the Shift+Tab walk
   reached when the two end in different traps, and 4.C's spec said they
   are "tagged so 4.D and 4.E can still test them". They are not passed
   today: 4.D and 4.E are NEEDS REVIEW for that part of the page (4.C
   1.13.1 says so). Build: share P6's steps with 4.D and 4.E, run their own
   readings (focus pictures, focus-event check) on them, and only then
   count them as reached (step 6d's walk-coverage rule).
15. **Opening everything, phases 2 and 3.** Phase 1 is built (`reveal.py`;
   guards RV and RC). Phase 2: 4.A, 4.C, 4.D and 4.E (and 4.F past its
   first six triggers) walk the keyboard through opened content, which
   removes guard RC. Phase 3: 5.D fills fields in opened content. Also
   nested triggers, a combobox's list, buttons that need a key other than
   Enter, and phase 1's caps (20 triggers, 3 sets). From the review: a
   trigger is "opened" only by what appears in the region it controls
   (C-02), and a plain button with no ARIA marker opens nothing today
   (H-08; part B holds the outcome meanwhile).
16. **Meaning goes to the judge, not to a word list** (part E): 5.H's
   consequence and "checked" words, 4.B's timing words, the "pause"
   words in 2.x. One spec change and one judge eval each. Then the
   spec decisions the review marks "(needs Abby)".
17. **The store, a thin MCP surface, one writer per run** (part H;
   bundle 7, moved ahead of the review UI, which needs it). The server
   keeps the report; the agent gets a short result and a link; tools
   have no output schema; a job has an owner; answers run as a job.
   Target: about a third of today's 93,000 tokens a page. The rest of
   bundle 7 as planned: run index, answers kept by content hash and
   spec version so a question about the same image or media is answered
   once per site, retention and the disk check, job state that survives
   a restart. Plan first: what is stored, for how long, and who may see
   answers from another user's runs.
18. **A person's answer only from TOBI's own UI** (the rest of bundle 6):
   Trusted Tester and reviewer roles, WebAuthn on submit, the evidence
   page. Design and options in the pivot plan; decide the review view
   there before building one. Added by part G: the whole page beside
   every crop, the list of what was not looked at, a sample of PASS and
   DOES NOT APPLY results for a Trusted Tester to confirm, and every
   dispute turned into a fixture.
19. **The second look as a guard** (part F), shaped by its trial (not a
   gate: Abby, 2026-11-12). Its README line says what the trial caught
   and missed.
20. **SCRT files, phases 2 and 3**
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

- **VAST** (step 12): whether the tobi-508 environment exists, and the
  admin's answers to questions 4 and 5 (2 and 3 answered, 2026-11-15)
  ([hosted sign-in plan](plans/2026-11-06-hosted-auth.md), "Open
  questions for the VAST admin").
- **The judge on VAST** (step 12): the CLI route is not in the image.
  Luna or another gateway needs its API shape, base URL, auth header,
  picture limits and quota; without one the hosted server leaves open
  questions to the calling agent.
- **Publishing the repository.** GSA asks for a GitHub repository;
  SECURITY.md says NASA's release review comes before the code is
  public. Which comes first for the submission (step 13).
- **Windows headed Chrome** was last run on 2026-11-02. Run it again
  before the scored submission run, or state the limit
  ([browser checks](../specs/rules/_browser-checks.md)).
- **`JUDGE_TYPES`:** 4.B alone meets the gate in step 9a; decided after
  9b.
- **Each change of steps 6e and 6g** that turns NEEDS REVIEW into an
  outcome, shown before it is built.

**After the demo: each shapes a step of "Next".**

- **Spec decisions from the review:** a form behind a plain button
  (H-08), a page that is only a canvas (E-03), a title that is a
  control's only label (E-13), `aria-controls` as a field's "own
  widget" (H-04), a form that is only a button (M-02), 4.F's "order
  does not matter" making the test DOES NOT APPLY. (Decided and built
  in step 6b, 2026-11-13: E-08, K-05, M-01, F-02, C-07.)
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

Moved to [KNOWN-LIMITS.md](KNOWN-LIMITS.md) (2026-11-14).

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
