# Handoff: starting a thread on a roadmap step

The roadmap's "Order of work" (`docs/ROADMAP.md`) lists the steps to the
demo. Start each step in a new session with its prompt below. Most send
the thread to the instructions below the line (how to fix one item, the
working rules).

**A prompt is removed from this file when its step is merged,** so what
is listed here is what is left to start or still running.

**Done:** steps 1 to 5 (PRs #39 to #44), step 6 (PR #46; results in
`evals/README.md`, "Gate 2026-11-13"), step 6b (PR #53), step 7
(PRs #48, #50), and step 6c's read cap, 19.A search row and freeze
(PRs #49, #51, #52).

**Order to start them** (at most three threads at once): 8 now (the
grid it is tested on is merged); 6c's two remaining items in its
running thread; 9 after 8; 10 when the keys are in place.

## Starting a thread

**Step 6c, Opus: what is left of it** (running)

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow its "Working rules". Your work is what is left of step 6c
> of `docs/ROADMAP.md` "Order of work", each its own pull request.
>
> (1) A time budget per test inside the run limit, so a test that runs
> long is NEEDS REVIEW ("ran out of its time") and the tests after it
> still run. Show me the budgets before building. Also find why 3.A's
> stepped capture took 17 min on 14194 against 55 s in the dry run.
> Update CLAUDE.md "Hosting, time and concurrency" and the README's
> "How long it takes" in the same commit.
>
> (2) 9.B and 9.C on CILab are DOES NOT APPLY where my key passes
> (round 2's review item 13): row A3o does not fire because
> `has_own_navigation()` is false there (7 units, no labelled region).
> Look at CILab's units in the run's evidence and tell me why its top
> navigation is not counted, and why 9.A found repeated content on the
> same run. Then propose either a fix to the read, or A3o in 9.A, 9.B
> and 9.C holding whenever every other page shares almost nothing and
> the tested page has any link or control. Show me the spec wording
> before building. It moves DOES NOT APPLY to NEEDS REVIEW only; add
> CILab's shape as a fixture and the nearest page that stays DOES NOT
> APPLY.

**Step 8, Opus: one library for reading the page, frames included** (now)

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow it. Your work is step 8 of `docs/ROADMAP.md` "Order of
> work": part D of
> `docs/plans/2026-11-12-coverage-second-look-thin-agent.md`, which
> absorbs fix 7 of `docs/plans/2026-11-08-post-round2-fixes.md`. First
> a short design note in the plan's part D (what `jslib` exports, how
> a reader names an element across shadow roots and frames, how a
> frame from another site is recorded, loaded and located) and the
> spec wording for the three decisions the roadmap lists under step 8.
> Show me both before code: this step turns NEEDS REVIEW into PASS
> inside web components and frames, and I decide that. Then 8a, reader
> by reader in the plan's order, one pull request per reader with its
> fixtures and step 7's grid rerun: a grid cell may move from NEEDS
> REVIEW to an outcome only when the page's content was really read,
> and for every cell that becomes PASS add the nearest page that must
> still FAIL. Then 8b, the frame from another site. Guard CN stays; it
> stops firing where the readers and the count agree. Update each
> test's README status line and the "Known wrong outcomes" table in
> the commit that changes it. Merge `main` before every spec version.
> Whatever is not merged by the end of Nov 17 stops there: leave
> `main` whole and write down where you stopped.

**Step 9, Sonnet: the second check** (after step 8, or on Nov 16 with whatever of it is merged)

> Read `CLAUDE.md`, then `docs/plans/2026-11-08-apijudge-build.md`
> ("The gate"), the docstring of `evals/apijudge_gate.py`, and step 6's
> write-up in `evals/README.md` ("Gate 2026-11-13") with its folder
> `evals/judging/gate-2026-11-13/` (`compare.py` is the comparison to
> reuse). Your work is step 9 of `docs/ROADMAP.md` "Order of work":
> step 6 again, on `main`'s head (record the commit), on round 2's 10
> frozen pages and round 1's, with the server judge answering every
> question type, scored with the same scorer.
>
> Before anything else, check and tell me if either fails: the frozen
> recordings of both rounds are restored (`evals/judging/round2/frozen`,
> `evals/judging/round1/frozen`; they are not in git, so stop and ask
> me for the archives, never fetch the pages live), and the browser in
> this container trusts the egress proxy (step 6's six 19.A false
> FAILs were the container's). The gate script reads only round 2's
> pages today: give it a round option. Use the CLI route (`claude -p`)
> unless I tell you Luna is configured. Run `--dry` first and tell me
> the request and token estimate before the real run. Write into a new
> folder under `evals/judging/`; never rewrite a locked round or step
> 6's folder.
>
> Report, beside step 6's figures and round 2's: false PASS, missed
> fails (wrong DOES NOT APPLY), false FAILs, NEEDS REVIEW and decided
> cells, per test and in all; every cell that moved from NEEDS REVIEW
> to an outcome since step 6, with whether my key agrees; guard CN's
> cells on round 1's pages apart from the rest, and whether it held
> back any failure there; and for each question type, on both rounds'
> cells together, whether it meets the thresholds under "The gate".
> Run the gate's test-page half for the types that are near. Do not
> change `JUDGE_TYPES`: I choose the types from your report.
>
> Put the result in `evals/README.md`. Then rewrite each README status
> line from this run: one short line per test, and remove a caveat
> only where this run or a grid cell shows it is gone. Keep the "Known
> wrong outcomes" table as it is. Do not fill any [FILL] in
> `docs/hackathon/`. Last, give me the path of each page's
> `pre-scrt.json` beside the path of its key.

**Step 10, Sonnet: round 3's run** (when I have put my SCRT files for the pages in place)

> Read `docs/how-to/run-a-judging-round.md` and
> `evals/agent/README.md`. Before the run, do scorer fixes 15, 16 and
> 17 of `docs/plans/2026-11-08-post-round2-fixes.md`, each with its
> test. Then run a round on the pages I name, with the server judge
> answering, exactly as the how-to describes: freeze, run, lock, then
> score against my keys. Never open my keys before the lock. Report
> per test and in all, and list apart the cells that are inside a web
> component or a frame.

**Step 11, Sonnet: the second look's trial** (if the days allow)

> Read `CLAUDE.md`, then part F of
> `docs/plans/2026-11-12-coverage-second-look-thin-agent.md`, "Trial".
> Build `evals/second_look.py` and run it on round 2's 10 frozen pages
> with the rules as they were at round 2's lock commit, three repeats,
> through the judge's CLI route. It is a measurement, not a gate: write
> what it caught of the known wrong cells, what it missed, and what it
> flagged that my keys say is right, with tokens and time per page,
> into the plan's part F and `evals/README.md`. Stop there; the guard is
> a later step.

**Step 13, Sonnet: the scored run for the pitch** (Nov 18-19, when I say the submission commit is fixed)

> Read `CLAUDE.md` and `docs/hackathon/README.md`. I have fixed the
> submission commit: <commit>. Run the scored suite once at that commit
> as `docs/hackathon/README.md` describes, and fill every [FILL] in
> `docs/hackathon/evaluation.md` and `deck.md` from that one run, with
> its commit, date and environment. Remove a [PENDING] marker only
> where the work exists and is checked. Never describe a tested page as
> certified or compliant. Show me the filled figures before you commit.

---

You are working on one step of `docs/ROADMAP.md` "Order of work"; your
prompt names it. Most steps fix items from a finished code review of
this codebase (`tobi508`); steps 4 and 5 fix items from the
post-round 2 plan, and the same way of working applies.

## Read first, in this order

1. `CLAUDE.md`: the eight principles and the rules for specs, fixtures
   and docs. They bind every fix.
2. `docs/reviews/2026-11-11-code-review.md`: "The short version", the P0
   table, then the full entry of each item in your bundle (what is wrong,
   where, the smallest fix, how it was checked).
3. `docs/reviews/2026-11-11-code-review-pages/README.md`: the page and the
   command that reproduce each item, and what it printed.
4. For a check (2.A to 19.A): its spec in `specs/rules/`, and the reviewer's
   row-by-row table of spec against code in
   `docs/reviews/2026-11-11-code-review-notes/` (files E, F, H, M, N, K).
   The other raw notes hold measurements (T, W) and test coverage (Q).
   Severities in the raw notes were changed in the triage: the review file
   wins.

File and line numbers in the review are as of commit `e4d4165`. Lines
move: find the function by name.

## How to fix one item

1. **Reproduce it first.** Run the item's command from the pages README
   and see the outcome it lists. If it no longer reproduces, say so and
   stop on that item.
2. **Decide whether the spec changes.** The spec is the only source of
   outcome logic (principle 2).
   - The code does not do what the spec already says (E-01, E-07, F-15,
     H-03, N-08, K-06): fix the code, no spec change.
   - The spec's own rows or Terms give the wrong outcome (most items
     marked "spec change" or "(needs Abby)"): draft the spec change
     first, as a MINOR version, with the research CLAUDE.md asks for (TT
     text from `catalog.py`, the W3C Understanding page and techniques,
     ACT rules, the Baseline test). Show me the draft before building.
     `specs/rules/` needs my review (CODEOWNERS).
   - Every fix in the review moves a PASS or a DOES NOT APPLY toward
     NEEDS REVIEW or FAIL, or removes a wrong FAIL. If yours would turn a
     NEEDS REVIEW into a PASS, or remove a FAIL an answer key confirms,
     ask me first.
3. **Make the page a fixture.** Copy the reproducing page into
   `tests/fixtures/<test>/` under the folder's naming, with its expected
   outcome and rows in the test file, never in the page. Prefer an ACT or
   Baseline case when one covers the rule. Write the test, see it fail,
   then fix.
4. **Fix at the shared place when the item says so.** Several items are
   one cause seen in many checks (fragment-only address changes: C-03,
   F-06, H-11; "trap counts as complete": H-03, M-05, F-11; light-DOM
   reads: D-01, D-03, K-02, N-01, M-06). Fix the shared function and add
   a fixture per check it changes.
5. **Run what could have moved:** the check's own fixture file, its ACT
   and Baseline cases, and any other check that uses the function you
   changed. Not only the new test. For a long run, keep one line per test
   in a log (CLAUDE.md, "Commands").
6. **If a question, its rubric or its input changed,** run the judge eval
   for it (`docs/solutions/judge-eval.md`). Scripted answers in `tests/`
   test the rules, not the questions.
7. **Update with the fix, in the same commit:** the spec's `spec_version`;
   the README's status line for the test and its row in the README's
   "Known wrong outcomes" table (remove the case you fixed; add any new
   one you find), so the README says what the test can and cannot do
   today (Abby, 2026-11-12); `docs/hackathon/evaluation.md`
   and the matching slide when a spec version, evaluation method or
   security control changes; `docs/ROADMAP.md` "Known limits" when a limit
   is removed or newly stated.
8. **Mark the item in the review file:** add a line `- **Fixed:** <commit>,
   spec <id> <version>` (or `- **Not fixed:** <why>`) under the item's
   "Checked" line, and change its row in the P0 table to say fixed.
9. **Report what you verified and what you assumed,** separately
   (principle 6).

## Working rules

- One bundle or part per thread, on its own branch from `main`. Open a
  pull request every few items rather than one at the end, so other
  threads see the changes; do not start a second bundle.
- Several threads run at once and some change the same checks and
  specs. Before you bump a spec version, rebase on `main` and take the
  next free version. Keep each commit to one item so a conflict is
  small.
- Commit after each item, so a session that is cut off loses nothing.
- At most 3 subagents at a time, and only for separable work (writing
  fixtures from the pages, running fixture files). The first review hit
  the 5-hour usage limit with 18 at once, and this one hit it twice with 3.
- Do not rewrite `evals/judging/`.
- Do not delete `docs/reviews/2026-11-11-code-review-pages/` or the notes
  folder until every item that cites them is fixed.

## Which model for which bundle

From what this review showed: the Sonnet reviewers found and reproduced
problems reliably (every page of theirs that was run again gave the same
outcome), and were less reliable on how serious a problem was and on
claims they had not run (three leads were refuted, one test page proved
less than it claimed). So Sonnet where the item names the line and has a
reproducing page; Opus where the fix needs a decision across spec, code
and tests, or touches security.

| Bundle | Model | Why |
| --- | --- | --- |
| 1. One-line and one-function fixes | Sonnet | Each has a page, a named function and no spec decision |
| 2. Shadow roots | Opus | One shared reader replaces reads in five modules; every fixture must be rerun |
| 3. Spec decisions | Opus, with Abby | Research and a spec draft per item; the code follows the decision |
| 4. Traps and limits (the coverage record) | Opus for the design and the first two readers; Sonnet to carry it through the remaining checks | The pattern is the hard part; applying it is mechanical |
| 5. The watchers | Opus | Timing, sampling and what "observed" means; easy to fix one page and break another |
| 6. What the agent receives | Sonnet | The cuts are listed and measured; `tool_sizes.py` and the reviewer's method check the result |
| 7. The server judge and its gate | Opus | Security (B-01, B-02) and the evaluation method (L-02, L-03) |
| 8. Before VAST | Opus | Sign-in, ownership and the stores that fetch what a page names |
| 9. CI and tests | Sonnet for Q-01, Q-02, Q-08; Opus to design the grid of hard pages (Q-03), Sonnet to fill it | |
