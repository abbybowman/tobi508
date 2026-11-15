# Roadmap, "Where things stand" and "Now", as of 2026-11-14 (archive)

Cut from `docs/ROADMAP.md` on 2026-11-14 when it was shortened. It is a
record of what each step to the demo covered, what was decided and what
was built, in the words of the time. The roadmap is the status of
record; nothing here is kept up to date.

## Where things stand (2026-11-13)

- **22 TT tests are built** (spec 1.0.0 or later, check registered,
  fixtures passing): 2.A-2.D, 3.A, 4.A-4.F, 5.A-5.D, 5.F-5.H, 9.A-9.C and
  19.A. Each spec's `spec_version` is its version of record; the
  [README](../../README.md) has a status line per test.
- **Direction** (Abby, 2026-11-07;
  [plan](../plans/2026-11-07-server-judge-pivot.md)): the server judges, a
  person reviews, the client agent explains. TOBI becomes a hosted service
  on VAST with its own pinned judge model (ApiJudge), because calling
  agents skipped or guessed at open questions whatever the wording.
- **Steps 1 to 5 of the first order of work are merged** (2026-11-12 and
  13; PRs #39 to #44): the quick fixes and CI, the count and guard CN,
  the server judge, gate and sign-in fixes, the rules' false FAILs, and
  the answerable "unsure" questions. They were planned to take until
  about Nov 17 and took two days, so the order below pulls work up.
- **Step 6, the check against round 2** (2026-11-13;
  [results](../../evals/README.md#gate-2026-11-13-round-2s-10-pages-again-the-server-judge-on-every-type-roadmap-step-6)):
  wrong PASS and wrong DOES NOT APPLY fell from 5 to 0 and false FAILs
  from 24-26 to 11 (6 of them the container's, not the rules'), but
  decided cells fell from about 132 to 68 of 220: NEEDS REVIEW rose
  from 86 to 152, and the keys fail 21 of those. The tool stopped
  guessing; it now decides too little. Steps 6c, 8 and 9 win decided
  cells back, with no wrong PASS or DOES NOT APPLY returning. For the
  pitch (Abby, 2026-11-13): no target share of NEEDS REVIEW; the three
  figures side by side, the rise in NEEDS REVIEW named as the cost, and
  where the lost cells went.
- **Step 9a, the second check** (2026-11-14; one repeat, at commit
  `8854a4f`, so before step 8's readers and step 6d; results in
  `evals/README.md`, "Gate 2026-11-14", once its branch is merged).
  Round 2: still no wrong PASS or DOES NOT APPLY, false FAILs 11 to 6,
  decided cells 68 to 91 of 220 (the read cap gave back 26). Round 1,
  first time with the judge: no wrong PASS or DOES NOT APPLY, 12 false
  FAILs (8 of them one cause: the judge calls "Home" and "NASA, return
  to the homepage" inconsistent in 9.C), 59 decided. What it showed:
  - **Guard CN is now the largest single cost.** 58 cells over the two
    rounds (44 on round 1), and the keys fail none of them: mostly
    5.F, 5.G and 5.H on a form hidden until opened, and 2.B and 3.A on
    more than 30 images. Step 6e.
  - **2.C and 2.D are NEEDS REVIEW on all 10 of round 2's pages,** as
    in step 6 (the page sets a timer longer than the watch). Step 6e.
  - **Outcomes repeat.** Of 325 cells no judge answer decided, none
    differs in outcome between the dry run and the real run, so 9b is
    one repeat too.
  - **4.B meets the whole gate** (6 of 6 on real pages; the test-page
    half clean three times). No other type does yet.
  - **Budgets:** only 5.D ran out (594 of 600 s, once); 9.B came close
    to its 60 s.
- **Evals.** Judge eval runs are in [evals/README.md](../../evals/README.md).
  Agent eval rounds 1 (nasa.gov) and 2 (svs.gsfc.nasa.gov) are scored
  against Abby's blind SCRT files
  ([evals/agent/README.md](../../evals/agent/README.md),
  [round 2 scores](../../evals/judging/round2-armc/abc-score.md)). Round 2:
  no false PASS came from a judge's answer; the rules alone gave 3 false
  PASS, 2 missed fails and 13-15 false FAILs per run. Both sites are
  development sites now.
- **The code review** (2026-11-11 and 12;
  [reviews/2026-11-11-code-review.md](../reviews/2026-11-11-code-review.md)):
  32 P0 items, 30 of them a wrong PASS or DOES NOT APPLY that a small
  page reproduces. Parts A and B of
  [the plan after it](../plans/2026-11-12-coverage-second-look-thin-agent.md)
  are built; parts C to J are slotted into the order of work below. The
  README's "Known wrong outcomes" table lists what still reproduces.
- **Time.** A run tests the whole page by default and stops only at
  `MAX_RUN_S` (1800 s); `no_time_limit=false` holds it to `RUN_LIMIT_S`
  (600 s). Lessons and measurements:
  [solutions/time-budget.md](../solutions/time-budget.md).

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
[reviews/2026-11-11-code-review-fixing.md](../reviews/2026-11-11-code-review-fixing.md),
"Starting a thread"; a prompt is removed from that file when its step
is merged. Run at most three threads at once: more hit the
5-hour usage limit twice during the review.

The "When" column is a target, not an estimate: the sizes in the plans
ran three to four times longer than the work took.

| Step | What | Model | When | Detail (other numbers) |
| --- | --- | --- | --- | --- |
| 1-5 | Quick fixes and CI; the count and guard CN; judge, gate and sign-in fixes; false FAILs; answerable "unsure" | | done: PRs #39 to #44 | Plan parts A and B; review bundle 7; fixes 8 to 14 and 24 to 27 |
| 6 | The check against round 2: the baseline before the readers change | Opus | done Nov 13: [results](../../evals/README.md#gate-2026-11-13-round-2s-10-pages-again-the-server-judge-on-every-type-roadmap-step-6) | [Judge build plan](../plans/2026-11-08-apijudge-build.md), "What is left", 1 |
| 6b | Single-test fixes for the README's known wrong outcomes | Sonnet | done Nov 13: PR #53 | Eleven review items (M-05, C-01, M-10, H-02, M-08, K-01, M-01, E-08, F-02, C-07, K-05); each is marked fixed in [the review](../reviews/2026-11-11-code-review.md) and decided in its spec |
| 6c | Win back decided cells: the read cap, 19.A's unverified search, a fuller freeze, a time budget per test, 9.B and 9.C on a page whose own navigation matches nothing | Opus | done Nov 13-14: PRs #49, #51, #52, #54, #55 | This file, "What each step covers"; [time budgets](../solutions/time-budget.md) |
| 6d | One shared check that the keyboard walk reached every element, for the tests that read it | Sonnet | phase 1 done Nov 14: PRs #59, #63 | Phase 2 (4.A, 4.B, 4.F past a forward trap) is step 14c, after the demo |
| 6e | Guard CN on real pages, and 2.C and 2.D's timer: the two largest causes of NEEDS REVIEW that hide no failure | Opus | Nov 15-16 | Step 9a's results; this file, "What each step covers" |
| 6f | 9.C's "Home" pairs (8 false FAILs on round 1), 19.A on CILab, 9.B's budget | Sonnet | Nov 15-16 | Step 9a's results |
| 6g | The keyboard tests read content that menus and sections open: 4.C and 4.E first, from the pass 4.F already makes | Opus | Nov 16-17, after PR #64 | Step 15's phase 2, its first part; guard RC |
| 7 | The grid of hard pages | Sonnet | done Nov 13: PRs #48, #50 | Plan part I; `tests/test_fixtures_grid.py` |
| 8 | One library for reading the page: web components and frames | Opus | readers 1 to 3 done Nov 14 (PRs #58, #60 to #62); readers 4 to 8 in PR #64; the form error tests in frames next | Plan part D; fix 7 |
| 9a | The second check: round 2's and round 1's frozen pages after 6b and 6c, before the readers change | Sonnet | done Nov 14; its branch waits to merge (see "Where things stand") | `evals/README.md`, "Gate 2026-11-14" |
| 9b | The third check: the same pages after 8, 6d, 6e and 6f | Sonnet | Nov 17, started by midday | As 9a, a new folder, one repeat |
| 10 | Round 3: a formal blind judging round, like rounds 1 and 2, on a NASA site not used before. Abby's keys are locked (2026-11-14) | Sonnet | when PR #64 is merged | Scorer fixes 15 to 17 first; [how-to](../how-to/run-a-judging-round.md) |
| 10b | Round 4, if Abby has the time to key it: a second blind round, run last | Abby's keys; Sonnet | frozen the day it is keyed; run on Nov 17 at 9b's commit | As step 10 |
| 11 | If the days allow: the second look's trial | Sonnet | after 6, beside 8 | Plan part F, "Trial" |
| 12 | If the days allow: sign in on VAST from Claude Code and run one page | Opus | when the admin's answers arrive | [Hosted sign-in plan](../plans/2026-11-06-hosted-auth.md). The demo for reviewers is recorded (Abby, 2026-11-12), so this is not needed for it |
| 13 | The pitch: the submission commit fixed on Nov 17, one scored run, rehearsal, fallback video | Abby, with a Sonnet thread for the run | Nov 18-19 | [docs/hackathon/](../hackathon/README.md) |

**Merging.** Step 8 changes readers the grid tests. Each
thread branches from `main`, opens a pull request every few items, and
before it bumps a spec version or edits the README tables it merges
`main` and takes the next free version. Step 8 merges reader by reader,
so a half-finished step 8 on Nov 17 still leaves `main` whole.

**The cut** is the end of Nov 17: from Nov 18 only the deck and the
presentation (Abby, 2026-11-13). Whatever of steps 6e to 12 is not
merged by then waits until after the demo. The pitch says what is measured and
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
     wrong PASS ([results](../../evals/README.md#read-cap-2026-11-13-9a-9c-on-round-2s-10-pages-with-the-cap-at-5000-roadmap-step-6c-item-1)).
   - **A time budget per test** inside the run limit, so a test that
     runs long costs its own cell: 3.A's capture took 17 min on 14194
     (55 s in the dry run) and cost 5.A-5.H there. Find the cause as
     well as adding the budget.
     **Built 2026-11-14:** budgets as settings (60 s to 600 s, about twice
     the longest seen on round 2's pages, provisional until step 9), each
     capped at half of what is left of the run, cheapest first; each
     report records every test's time (`test_times`). The cause was
     seen once more (3.A on 14194 ran 1,178 s against its 240 s
     budget): a cancelled test's cleanup waited on a page still
     running script, and 3.A's flash counting never yielded. A test
     past its budget is now abandoned, not awaited, and the counting
     runs off the event loop (`docs/solutions/time-budget.md`).
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
   - **9.B and 9.C when nothing matches** (found when the cap was
     lifted; round 2's review item 13): CILab was DOES NOT APPLY where
     the key passes. Its navigation was read; what blocked row A3o was
     a filter label on the search page that happened to name it, so
     that page did not "share almost nothing".
     **Built 2026-11-14:** nothing matches and the tested page has
     navigation of its own is A3o, NEEDS REVIEW, whatever the other
     pages share (9.A 1.6.0, 9.B 1.5.0, 9.C 1.8.0); with none of its
     own it stays DOES NOT APPLY.
6d. **The walk was complete, checked in one place** (Abby,
   2026-11-14). A walk that ends in a trap, a loop, a cap or out of
   time has been handled test by test (5.D, 5.F; 4.D and 4.F by guard
   CN). One shared
   answer, "the walk reached every stop it could have, or here is what
   it did not reach", read by every test that uses the walk (4.A-4.F,
   5.A-5.H): PASS or DOES NOT APPLY on an incomplete walk becomes
   NEEDS REVIEW with the sentence. It is the first conversion of step
   14 (part C), pulled up; the coverage record for the other readers
   stays there. It touches `walk.py` and the checks, not the readers
   step 8 replaces.
   **Decided 2026-11-14 (Abby):** "complete" is coverage, not how a pass
   ended: every element the test checks was reached by some pass the
   test may read (P1, P2; P6's stops only once a test has its readings on
   them, item 14b), counted when the last pass ended. A trap, loop, cap
   or time limit matters only through what it left unreached. A radio
   group, a date input and an entered frame count once. 4.D's loop page
   (7 of 7 reached by the two passes) stays PASS; so does the grid's
   trap page for 4.E. `walk.walk_coverage` is the one answer.
   **Built 2026-11-14:** the function and 4.E 1.5.0 (the grid's NEW-3
   is withdrawn: its trap page reached 7 of 7; the new fixture 4e/f13
   leaves an element unreached), then 4.D 1.9.0 (guard CN stays beside
   it) and 4.A 1.11.0. What Tab should land on leaves out a radio group's
   other radios and whatever an open modal dialog covers. 5.D 1.7.0 (by fields,
   `walk.field_coverage`; guard CN stays). 5.F 1.8.0, 5.G 1.6.0 and 5.H 1.6.0 (they
   read 5.F's list). Phase 1 is built; phase 2 (4.A, 4.B, 4.F, 5.x reading
   the union of the passes) is step 14c, after the demo (Abby,
   2026-11-14: step 9a's NEEDS REVIEW cells name no forward trap, so
   it would move no measured cell; step 6g is where those cells are). 4.B, 4.C and 4.F keep their own decisions. Left open by
   the step: the grid's `frame-other` test failed once without a
   cause found, and the modal-dialog rule is not yet in `jslib`
   (step 8's thread).
6e. **Guard CN on real pages, and the timer** (Abby, 2026-11-14;
   each change turns NEEDS REVIEW into an outcome, so Abby approves
   each before it is built). Step 9a: 58 guard CN cells on 19 real
   pages and no failure among them.
   - First a table from 9a's reports: every CN cell by the sentence
     that made it (a form hidden until opened; a form that is only a
     button; more than 30 images; the rest), with the key beside it.
   - Then, per cause, the smallest change that decides the cell
     without guessing. Candidates: 5.H reads a hidden form's own
     fields and words to say whether it is the kind of form 5.H is
     about (it does not need to fill it); 5.F and 5.G test a form that
     phase 1 of "opening everything" already opened; the 30-image cap
     measured and raised as the 600-item cap was.
   - 2.C and 2.D: what the timer on round 2's pages is, and whether
     advancing the page's clock past it (the stepped clock 3.A's
     capture already has) shows that nothing visible changes.
   - Every change comes with the nearest page that must stay NEEDS
     REVIEW, and the grid rerun: its hidden-form and late-start pages
     are the guard's own cases.
6f. **Three smaller findings of step 9a** (Abby, 2026-11-14):
   - **9.C:** on 8 of round 1's 9 pages the judge fails the pair
     "Home" and "NASA, return to the homepage", and the key passes
     all 8. Find whether the pair should have been made at all (a
     logo and a menu link that go to one address are two components,
     not one named two ways) or whether the rubric is wrong; a judge
     eval either way.
   - **19.A on CILab** is FAIL by rule where the key passes; not yet
     looked at.
   - **9.B's budget** is 60 s and its longest run was 41.5 s (51.6 s
     in a dry run, where it ran out): 180 s, as 9.A and 9.C.
6g. **Opened content in 4.C and 4.E** (Abby, 2026-11-14: the largest
   cause of NEEDS REVIEW in step 9a). Guard RC holds a PASS whenever a
   menu or section opened to show controls the test did not walk: 45
   cells over the two rounds (4.C 14, 4.E 16, 5.D 9, the rest 4.D,
   5.A and 5.C), and the keys pass 44 of them. 4.F's pass R already
   opens each trigger on a fresh replay and Tabs through what it
   shows, for the first six triggers. 4.C and 4.E read that pass: a
   trap inside the opened content, and a change of context on focus
   there, by their own rows. Guard RC then holds only what pass R did
   not open (past six triggers, or a trigger that did not open). It is
   the first part of step 15's phase 2, pulled up; 4.D (it needs
   pictures) and 5.D (it must fill fields) follow only if the days
   allow. It turns NEEDS REVIEW into PASS, so the spec wording and
   the moved cells go to Abby first.
7. **The grid of hard pages** is built (`tests/test_fixtures_grid.py`,
   nine pages by 22 tests; one recording per fixture page). It is the
   test for step 8: a cell marked as a known wrong outcome fails the
   suite when it stops being wrong, so each fix updates its cell. It
   found four cases the review has no item for (`UNFILED` in the test
   file; the wrong outcomes are in the README's table): 4.B does not
   read instructions inside a web component, and 4.A and 4.C-4.F pass a
   page whose only form opens from a plain button. (A third, "4.E passes
   after a keyboard trap", was withdrawn in step 6d: the page's two
   passes reached every element, so the PASS was right.)
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
9. **The second and third checks.** Step 6 again, on round 2's pages
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
   It runs twice (Abby, 2026-11-14). **9a** is done: one repeat at
   the commit of its dry count, before step 8's readers. **9b** runs
   on `main` after steps 8, 6d, 6e and 6f, one repeat (9a's dry and
   real runs differed in no outcome), started by midday on Nov 17 so
   that it finishes inside the cut. A gate run's reports and pre-SCRT
   files stay out of git (about 70 MB a run with their screenshots);
   the scores, the comparison and the README sections go in.
10. **Rounds 3 and 4** (Abby, 2026-11-14).
    - **Round 3 is a formal judging round,** as valid as rounds 1 and
      2: a site the tool was never developed against, Abby's blind
      SCRT files locked before the tool ran, the run locked before the
      keys are opened, scored by the how-to. Its score is a blind
      result for the commit it ran at, and it may be the last blind
      round before Nov 20, so it is reported as one. It runs as soon
      as PR #64 is merged. Once it is scored, what it shows may change
      the code, as rounds 1 and 2 did; from then its pages are
      development pages for any later run, and a later run on them is
      reported as a rerun, never in place of the blind score.
    - **Round 4,** if Abby has the time to key it: a second blind
      round, frozen the day she keys it and run once, last, on Nov 17
      at 9b's commit. It would show whether the fixes made after round
      3 hold on pages they were not made from.
    - **Keeping a round blind to the threads.** Until a round's run is
      locked, its page list, keys and freeze stay off `main`: the
      freeze is made on a branch that is not merged, and no other
      thread is told the pages. Threads do visit live NASA pages while
      they work (step 6b set a bar from live search pages), so a page
      list on `main` could be read or probed by one of them.
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

