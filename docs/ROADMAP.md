# Roadmap

What is left to build, and the one place that says what is scheduled when.
A living list, not a log: delete an item once it is built, and put any
decision it needed into the spec, CLAUDE.md or `docs/solutions/` where it
belongs. Plans in `docs/plans/` hold the detail of an item; they do not
keep their own schedule.

## Where things stand (2026-11-11)

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
- **Time.** A run tests the whole page by default and stops only at
  `MAX_RUN_S` (1800 s); `no_time_limit=false` holds it to `RUN_LIMIT_S`
  (600 s). Lessons and measurements:
  [solutions/time-budget.md](solutions/time-budget.md).

## Now: to the Nov 20 demo

Scope (Abby, 2026-11-11): a middle path between the small core and the
full pivot. Reliability comes first: the rules' false FAILs and the
"unsure" answers that are answerable. Then a check of how far results
have moved since round 2, then as much of the pivot core as steady
progress allows. TOBI is a prototype whose tests keep improving, with
each test's status in the [README](../README.md); the check measures our
work and is not a formal gate.

**Committed, in this order**

1. **False FAILs by rule** (bundle 5), largest first: fix 8 (5.A, an icon
   button labels the search field: 7 cells a run), 9c and 9 (5.C option
   rows and hidden controls), 10 and 11 (19.A's search page and quoted
   search). Each is one spec change (MINOR), one fixture, the suite.
2. **"Unsure" answers that are answerable** (bundle 4), largest first:
   fix 12 and 13 (4.F: the rubric and the order picture; the server
   judge's wrong FAILs on 5-6 pages), 14 (9.C pairs repeated components),
   then 24-27 (4.A carousel arrows and destinations, 4.D pictures, 2.B
   still regions). Judge eval for each changed question.
3. **The check against round 2.** Rerun round 2's 10 frozen pages once,
   after 1 and 2, with today's rules and the server judge answering (CLI
   route; count the requests with `--dry` first), and score with the same
   scorer beside round 2's locked rows. It gives the before-and-after
   figures for the pitch (a development site, said so) and shows which
   question types are sound enough for Abby to switch on (`JUDGE_TYPES`).
   Plan: [plans/2026-11-08-apijudge-build.md](plans/2026-11-08-apijudge-build.md).
4. **Close the MCP path for a person's answer:** `decided_by: "human"`
   arriving through MCP is recorded as the client agent's (fix 21, first
   step; `judgment.py`). Hours, not days.
5. **The pitch,** with the last two days kept for it: one scored run at
   the submission commit for the [FILL] figures, a rehearsal and a
   fallback video ([docs/hackathon/](hackathon/README.md)).

**If the days allow, in this order**

6. **VAST: sign in from Claude Code and run one page end to end**
   ([plan](plans/2026-11-06-hosted-auth.md)), when the admin's answers
   arrive. Verify the code review's security leads first. Fallback: a
   recorded demo from a local server.

**Alongside, in its own thread:** the code review
([reviews/2026-11-11-code-review-notes/](reviews/2026-11-11-code-review-notes/README.md)),
in phases, security and false-PASS leads first.

**Not before the demo:** frames (fix 7), the store, the review UI and
WebAuthn, opening everything phases 2 and 3.

## Next: after the demo

In this order unless a judging round says otherwise. Fix numbers are the
[post-round 2 fixes](plans/2026-11-08-post-round2-fixes.md); bundles are
the [pivot plan's](plans/2026-11-07-server-judge-pivot.md).

1. **Frames** (fix 7; bundle 3): every 5.x test reads fields in frames,
   and the frame leftovers under "Known limits" below.
2. **Opening everything, phases 2 and 3.** Phase 1 is built (`reveal.py`;
   guards RV and RC). Phase 2: 4.A, 4.C, 4.D and 4.E (and 4.F past its
   first six triggers) walk the keyboard through opened content, which
   removes guard RC. Phase 3: 5.D fills fields in opened content. Also
   nested triggers, a combobox's list, buttons that need a key other than
   Enter, and phase 1's caps (20 triggers, 3 sets).
3. **A person's answer only from TOBI's own UI** (the rest of bundle 6):
   Trusted Tester and reviewer roles, WebAuthn on submit, the evidence
   page. Design and options in the pivot plan; decide the review view
   there before building one.
4. **The store** (bundle 7): run index, answers kept by content hash and
   spec version so a question about the same image or media is answered
   once per site, retention and the disk check; job state that survives a
   restart and works with several workers. Plan first: what is stored, for
   how long, and who may see answers from another user's runs.
5. **Round 3** on a site not used before, after the scorer fixes (15-17).
6. **SCRT files, phases 2 and 3**
   ([plan](plans/2026-11-02-scrt-io.md)): TT review, merging a partial
   file (which is also how to verify a fix: `verify_fix` on
   `tobi_run_tt_tests`, taking a saved report), export to the real SCRT,
   site roll-up. Fix advice for a read report is a separate, optional
   tool.
7. **Tidy the checks,** with the code review. Every outcome stays the
   same (rerun the judge eval when question text changes); share only
   what means the same thing; each check keeps its spec constants and the
   conditions that feed its rows. Known items: the "could not be
   performed" note typed by hand in many checks
   (`models.TEST_NOT_PERFORMED_NOTE`); 5.G imports 5.F's private helpers
   (error pass E could be its own module, like `labels.py`); `forms.py`
   exports underscore names; `RunContext.cache` keys are bare strings;
   findings, plain text, question and replay code repeated per check;
   base.py's steps say to copy a check.

## Decisions waiting for Abby

- **`JUDGE_TYPES`:** the question types to switch on, after the check against
  round 2 (Now, 3).
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
  nothing. Every test uses the rule, so it is a 4.C spec decision.
- **Publishing the repository.** GSA asks for a GitHub repository;
  SECURITY.md says NASA's release review comes before the code is
  public. Which comes first for the submission.
- **Windows headed Chrome** was last run on 2026-11-02, before most of
  today's specs. Run it again before the scored submission run, or state
  the limit ([browser checks](../specs/rules/_browser-checks.md)).
- **A second browser.** Whether a Firefox replay matters for the pitch,
  or the documented limit is enough (the report records its browser).
- The pivot plan's and the ApiJudge plan's own open questions (Keycloak
  and WebAuthn, who confirms a Trusted Tester, a recorded copy for a
  final SCRT, the gateway and its token quota, reviewers' access).
- SECURITY.md's two [TO CONFIRM] items (the reporting route; how long
  `runs/` is kept on NASA machines).

## Known limits, per test

None blocks an outcome: each is NEEDS REVIEW-safe today. Browser checks
still to run (mostly Windows headed Chrome) are in
[specs/rules/_browser-checks.md](../specs/rules/_browser-checks.md).

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
  timing words are English only.
- **4.C:** a late-refocus fixture (refocus 600 ms after blur, no DOM
  change) once the xfail in `tests/test_traverse.py` is settled; traps
  past the cap of 60 stops have no budget of their own.
- **4.D and 4.F:** run 4.C's f19 (cross-origin frame), f24 (open shadow
  root) and f32 (two traps) for 4.D, and f32 for 4.F.
- **5.A, 5.C, 5.F, 5.G:** fields in frames and shadow roots are not read
  (a NEEDS REVIEW note; fix 7). 5.F and 5.G leave `time`,
  `datetime-local`, `month` and `week` fields as loaded in attempt 2.
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
  Real YouTube and Vimeo embeds are NEEDS REVIEW (2.A A2).
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
