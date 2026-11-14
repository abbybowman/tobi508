# Roadmap

What is left to build, and the one place that says what is scheduled when.
A living list, not a log: delete an item once it is built, and put any
decision it needed into the spec, CLAUDE.md or `docs/solutions/` where it
belongs. Plans in `docs/plans/` hold the detail of an item; they do not
keep their own schedule.

## Where things stand (2026-11-13)

- **22 TT tests are built** (spec 1.0.0 or later, check registered,
  fixtures passing): 2.A-2.D, 3.A, 4.A-4.F, 5.A-5.D, 5.F-5.H, 9.A-9.C and
  19.A. Each spec's `spec_version` is its version of record; the
  [README](../README.md) has a status line per test.
- **Direction** (Abby, 2026-11-07;
  [plan](plans/2026-11-07-server-judge-pivot.md)): the server judges, a
  person reviews, the client agent explains. TOBI becomes a hosted service
  on VAST with its own pinned judge model (ApiJudge), because calling
  agents skipped or guessed at open questions whatever the wording.
- **Steps 1 to 5 of the first order of work are merged** (2026-11-12 and
  13; PRs #39 to #44): the quick fixes and CI, the count and guard CN,
  the server judge, gate and sign-in fixes, the rules' false FAILs, and
  the answerable "unsure" questions. They were planned to take until
  about Nov 17 and took two days, so the order below pulls work up.
- **Step 6, the check against round 2** (2026-11-13;
  [results](../evals/README.md#gate-2026-11-13-round-2s-10-pages-again-the-server-judge-on-every-type-roadmap-step-6)):
  wrong PASS and wrong DOES NOT APPLY fell from 5 to 0 and false FAILs
  from 24-26 to 11 (6 of them the container's, not the rules'), but
  decided cells fell from about 132 to 68 of 220: NEEDS REVIEW rose
  from 86 to 152, and the keys fail 21 of those. The tool stopped
  guessing; it now decides too little. Steps 6c, 8 and 9 win decided
  cells back, with no wrong PASS or DOES NOT APPLY returning. For the
  pitch (Abby, 2026-11-13): no target share of NEEDS REVIEW; the three
  figures side by side, the rise in NEEDS REVIEW named as the cost, and
  where the lost cells went.
- **Evals.** Judge eval runs are in [evals/README.md](../evals/README.md).
  Agent eval rounds 1 (nasa.gov) and 2 (svs.gsfc.nasa.gov) are scored
  against Abby's blind SCRT files
  ([evals/agent/README.md](../evals/agent/README.md),
  [round 2 scores](../evals/judging/round2-armc/abc-score.md)). Round 2:
  no false PASS came from a judge's answer; the rules alone gave 3 false
  PASS, 2 missed fails and 13-15 false FAILs per run. Both sites are
  development sites now.
- **The code review** (2026-11-11 and 12;
  [reviews/2026-11-11-code-review.md](reviews/2026-11-11-code-review.md)):
  32 P0 items, 30 of them a wrong PASS or DOES NOT APPLY that a small
  page reproduces. Parts A and B of
  [the plan after it](plans/2026-11-12-coverage-second-look-thin-agent.md)
  are built; parts C to J are slotted into the order of work below. The
  README's "Known wrong outcomes" table lists what still reproduces.
- **Time.** A run tests the whole page by default and stops only at
  `MAX_RUN_S` (1800 s); `no_time_limit=false` holds it to `RUN_LIMIT_S`
  (600 s). Lessons and measurements:
  [solutions/time-budget.md](solutions/time-budget.md).

## Now: to the Nov 20 demo

Scope (Abby, 2026-11-13): hands off the keyboard on **Nov 18**; from
then only the deck and the presentation. Until then, in this order of
importance: measure where steps 1 to 5 left us (step 6), bring web
components and frames into scope so their caveats leave the README
(steps 7 and 8), measure again, and try the tool on a site it has not
seen. TOBI is a prototype whose tests keep improving; none of this is a
formal gate (Abby, 2026-11-12). Every change to a test updates its
README status line and the README's "Known wrong outcomes" table in the
same commit, so the README always says what each test can and cannot do
today.

### Order of work

**Use the step numbers below.** Plans use other numbers for the same
work: "fix 8" is a post-round 2 fix, "bundle 5" a pivot-plan bundle,
"part A" a part of the plan after the code review, "E-01" a code review
item. They appear only in the last column, to find the detail. Each
step is one thread, started with its prompt in
[reviews/2026-11-11-code-review-fixing.md](reviews/2026-11-11-code-review-fixing.md),
"Starting a thread"; a prompt is removed from that file when its step
is merged. Run at most three threads at once: more hit the
5-hour usage limit twice during the review.

The "When" column is a target, not an estimate: the sizes in the plans
ran three to four times longer than the work took.

| Step | What | Model | When | Detail (other numbers) |
| --- | --- | --- | --- | --- |
| 1-5 | Quick fixes and CI; the count and guard CN; judge, gate and sign-in fixes; false FAILs; answerable "unsure" | | done: PRs #39 to #44 | Plan parts A and B; review bundle 7; fixes 8 to 14 and 24 to 27 |
| 6 | The check against round 2: the baseline before the readers change | Opus | done Nov 13: [results](../evals/README.md#gate-2026-11-13-round-2s-10-pages-again-the-server-judge-on-every-type-roadmap-step-6) | [Judge build plan](plans/2026-11-08-apijudge-build.md), "What is left", 1 |
| 6b | Single-test fixes for the README's known wrong outcomes | Sonnet | Nov 13-16, beside 7 and 8 | [Spec decisions](plans/2026-11-13-spec-decisions.md): M-05, C-01, M-10, H-02, M-08, K-01; then M-01, E-08, F-02, C-07, K-05 as Abby answers |
| 6c | Win back decided cells: the 600-item read cap, a time budget per test, 19.A's unverified search, a fuller freeze | Opus | Nov 14, before 8 reaches the site read | Step 6's results; this file, "What each step covers" |
| 7 | The grid of hard pages, its shadow-root and frame pages first | Sonnet | Nov 13-14 | Plan part I |
| 8 | One library for reading the page: shadow roots and same-origin frames (8a), then a frame from another site as its own page (8b) | Opus | 8a Nov 14-15; 8b Nov 15-16 | Plan part D; fix 7 |
| 9 | The second check: round 2's and round 1's frozen pages again, after 8 | Sonnet | Nov 16-17 | As step 6, a new folder |
| 10 | Round 3, small: a NASA site not used before, with web components if Abby finds one | Abby's keys; Sonnet for the run | pages chosen by Nov 15; run Nov 16-17 | Scorer fixes 15 to 17 first; [how-to](how-to/run-a-judging-round.md) |
| 11 | If the days allow: the second look's trial | Sonnet | after 6, beside 8 | Plan part F, "Trial" |
| 12 | If the days allow: sign in on VAST from Claude Code and run one page | Opus | when the admin's answers arrive | [Hosted sign-in plan](plans/2026-11-06-hosted-auth.md). The demo for reviewers is recorded (Abby, 2026-11-12), so this is not needed for it |
| 13 | The pitch: the submission commit fixed on Nov 17, one scored run, rehearsal, fallback video | Abby, with a Sonnet thread for the run | Nov 18-19 | [docs/hackathon/](hackathon/README.md) |

**Merging.** Steps 7 and 8 touch the same readers and fixtures. Each
thread branches from `main`, opens a pull request every few items, and
before it bumps a spec version or edits the README tables it merges
`main` and takes the next free version. Step 8 merges reader by reader,
so a half-finished step 8 on Nov 17 still leaves `main` whole.

**The cut.** Whatever of steps 8 to 12 is not merged by the end of
Nov 17 waits until after the demo. The pitch says what is measured and
what is planned.

### What each step covers

6. **The check against round 2.** Rerun round 2's 10 frozen pages once,
   with that day's rules and the server judge answering (CLI route, or
   Luna if its endpoint is ready; count the requests with `--dry`
   first), and score with the same scorer beside round 2's locked rows,
   judge-decided cells apart from rule-decided ones. It gives the
   before-and-after figures for the pitch (a development site, said so)
   and shows which question types Abby can switch on (`JUDGE_TYPES`).
   It is also part B's measurement (Abby, 2026-11-12): list the NEEDS
   REVIEW cells that guard CN made (row `CN`) apart from the rest, so
   step 8 can tell which of them a real reading would settle. It runs
   before step 8 so that the effect of steps 1 to 5 and the effect of
   the new readers are measured apart. A new round folder; the locked
   rounds are never rewritten.
6b. **Single-test fixes** (Abby, 2026-11-13). The rows of the README's
   "Known wrong outcomes" table that one spec and one fixture can
   remove. Six need no decision; five wait for Abby's answer in
   [plans/2026-11-13-spec-decisions.md](plans/2026-11-13-spec-decisions.md).
   Each moves a PASS or a DOES NOT APPLY toward NEEDS REVIEW or FAIL.
6c. **Win back decided cells** (Abby, 2026-11-13), ranked by the
   failures the keys say are hidden, then by cells won back for the
   work. In this order:
   - **The 600-item read cap** (9.A-9.C; `site.py` `UNIT_CAP`): it
     holds 30 cells and hides 10 failures (the keys fail 9.A on every
     page). Lifting it is approved (Abby, 2026-11-13), though it moves
     NEEDS REVIEW back to an outcome: the cap is what held round 2's
     two wrong 9.A PASSes (CILab, 14592). Done only when those two
     cells FAIL with the keys and no 9.A-9.C cell passes where the key
     fails. It merges before step 8 replaces the site read.
     **Built 2026-11-13:** the cap is 5,000 (9.A 1.4.0, 9.C 1.6.0, 19.A
     1.6.0), and a page over it is 9.A row A2. Round 2's pages: 9.A 10 of
     10 FAIL with the keys, 9.B 9 of 10, 9.C 4 of 10 (5 NEEDS REVIEW), no
     wrong PASS ([results](../evals/README.md#read-cap-2026-11-13-9a-9c-on-round-2s-10-pages-with-the-cap-at-5000-roadmap-step-6c-item-1)).
   - **A time budget per test** inside the run limit, so a test that
     runs long costs its own cell: 3.A's capture took 17 min on 14194
     (55 s in the dry run) and cost 5.A-5.H there. Find the cause as
     well as adding the budget.
     **Built 2026-11-14:** `checks/base.TEST_BUDGET_S` (60 s to 600 s,
     about twice the longest seen on round 2's pages); the 17 min was not
     reproduced (3.A on 14194: 56 s, 117 s with its stepped capture
     forced; `docs/solutions/time-budget.md`).
   - **19.A: a search whose results page did not finish** (its own
     scripts failed to load) is "search not verified" (row W4, NEEDS
     REVIEW), not a search that found nothing (W3, FAIL).
     **Built 2026-11-13:** 19.A 1.7.0 reads the results page's recording
     for scripts that did not load; on 14194 in this container (its
     search's 13 scripts refused) it is W4, NEEDS REVIEW, where step 6
     gave FAIL.
   - **A fuller freeze** for step 10 and later rounds: the freeze
     scrolls the page so lazy images load, and records media and
     19.A's search results, so a run does not depend on the container.
     Round 2's and round 1's frozen pages cannot be recorded again (the
     keys describe the pages as they were), so for step 9 the fix is
     the container: a browser that trusts the egress proxy.
     **Built 2026-11-13:** the freeze scrolls window by window, stores each
     player's chosen file first (500 MB a page) and records 19.A's
     searches; in a cloud container, `UPSTREAM_PROXY` in `.env`
     (`docs/solutions/environment.md`).
7. **The grid of hard pages** (part I): nine shared pages (a shadow
   root, a frame, more than a cap, a trap, a late start, text not in
   English, hidden text, a form behind a button, a failed reading) run
   against every check, never PASS and DOES NOT APPLY only with a
   reason. It is the test for step 8, so the shadow-root page and the
   two frame pages (same site, another site) come first and are merged
   on their own; the other pages follow. With it: one recording and one
   walk per fixture page, which is most of the suite's time.
8. **One library for reading the page, frames included** (part D).
   - **8a:** one `jslib` in front of every script; shadow roots and
     same-origin frames are read in place by every reader, in the
     plan's order (labels, the site read, media, 5.F's text, dialogs,
     forms, reveal). This turns guard CN's "not checked" sentences for
     web components into real results in 5.A-5.H, 9.A-9.C, 19.A and
     2.A, and closes 4.A's mouse-only control in a web component and
     5.F's error shown in one.
   - **8b:** a frame from another site is loaded as its own page from
     its own recording, with ANDI run there, and its findings are
     located by frame chain (fix 7; TT Appendix D).
   - **What Abby decides first,** because the direction is NEEDS REVIEW
     to PASS: that a result read inside a web component or a frame may
     PASS on the same rows as the rest of the page; the spec changes
     that say so (`count:` keys, the Terms that define a field and a
     frame), as one MINOR version per spec; and whether a recording
     that lacks a frame's page holds the test at NEEDS REVIEW (proposed:
     yes).
9. **The second check.** Step 6 again after step 8, on round 2's pages
   and on round 1's (the gate script reads only round 2's pages
   today, so it gains a round option): what moved from
   NEEDS REVIEW to an outcome, and whether any of it is wrong against
   the keys. The working goal: at least round 2's decided cells (about
   132 of 220) with still no wrong PASS or DOES NOT APPLY. It also
   measures guard CN on round 1's pages before its calibration is
   judged (on round 2's it cost 14 agreements and held back no
   failure; an image the recording lacks stays "unread", and the
   fuller freeze is the fix), and it is where `JUDGE_TYPES` is decided,
   on both rounds' cells and the gate's test-page half. Then each README status line is rewritten from it, and the
   caveats step 8 removed go.
10. **Round 3, small.** A site the tool has not been developed against;
    Abby looks for NASA sites built with web components. Three to five
    pages, Abby's blind SCRT files first, then the tool, then the score.
    Abby's time for the keys decides its size. The scorer fixes (15 to
    17) come first. If no such site is found by Nov 15, round 3 waits
    and step 9 stands in.
11. **The second look's trial:** one request per frozen round 2 page,
    with the rules as they were at round 2's lock, asking the server's
    model to look again at the rules' PASS and DOES NOT APPLY results.
    It measures; it changes no outcome.
12. **VAST end to end,** for the hosted story; the reviewers see a
    recording.
13. **The pitch,** with the last two days kept for it: the [FILL]
    figures from one scored run at the submission commit, a rehearsal
    and the recorded demo.

**Not before the demo:** the plan's parts C, E, G and H (steps 14 to 20
below), the review UI and WebAuthn, opening everything phases 2 and 3.
For the pitch, say what the review found and what is planned.

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

- **The judge's endpoint for step 6.** The CLI route (`claude -p`, as
  round 2's Agent C) works today. If Luna is to be used: its API shape
  (Anthropic Messages or another), base URL, auth header, vision input
  limits, structured output, rate limits and token quota. Ask Sage has
  no tokens this month.
- **Publishing the repository.** GSA asks for a GitHub repository;
  SECURITY.md says NASA's release review comes before the code is
  public. Which comes first for the submission (step 13).
- **Windows headed Chrome** was last run on 2026-11-02, before most of
  today's specs. Run it again before the scored submission run, or state
  the limit ([browser checks](../specs/rules/_browser-checks.md)).
- **`JUDGE_TYPES`:** the question types to switch on, after step 9, on
  round 1's and round 2's cells together and the gate's test-page half
  (not run in step 6). 4.B is nearest (5 of 5 agree, 6 cells needed);
  4.A, 4.D and 4.F stay off (they gave the judge's wrong FAILs in both
  rounds).
- **Five spec decisions** for step 6b:
  [plans/2026-11-13-spec-decisions.md](plans/2026-11-13-spec-decisions.md),
  part 2.
- **Step 8's direction** (NEEDS REVIEW to PASS inside web components
  and frames): the three points under step 8, before its first spec
  change.
- **Round 3's site and pages** (step 10), by Nov 15, and how many pages
  Abby can key.
- **The VAST admin's answers** (step 12 only): pulling the image, a
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
