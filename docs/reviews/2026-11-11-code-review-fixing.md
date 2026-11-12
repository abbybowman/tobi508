# Handoff: fixing what the code review found

Start a thread with one of the prompts under "Starting a thread"; each
sends the thread to the part below the line. For a bundle with no prompt
of its own, paste everything below the line and name the bundle.

## Starting a thread

Open a new session on this repository and paste one of these. Each
thread reads the rest of this file itself.

**Thread A, Sonnet: quick fixes and CI**

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow it. Your work is part A of
> `docs/plans/2026-11-12-coverage-second-look-thin-agent.md` (the quick
> fixes) and then the first step of its part I (CI: Q-01, Q-02, Q-08).
> Do CI first: it takes an hour and protects everything else. Then the
> part A items in the plan's table, in its order, one commit and one
> fixture each. Two of them (E-02, K-04) change which row a control
> lands on: draft the spec wording and stop for me before building
> those two. Ask me before anything that turns a NEEDS REVIEW into a
> PASS.

**Thread B, Opus: the count of what exists, and the guard on DOES NOT APPLY**

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow it. Your work is part B of
> `docs/plans/2026-11-12-coverage-second-look-thin-agent.md`. I agreed on
> 2026-11-12 that a guard may move DOES NOT APPLY to NEEDS REVIEW: write
> that into `specs/rules/_template.md` and CLAUDE.md principle 3 in the
> commit that builds the guard. Start with a short design note in the
> plan's part B (the `Count` fields, where it is read, how a check
> reports what it read, the guard's sentences) and show it to me before
> code. Then the count, the play hook, the guard, and the specs' `count:`
> keys one test family at a time, with the eleven pages the plan lists
> as fixtures. Stop and report before part C; it is not yours.

**Thread C, Opus: the server judge and sign-in, then the second look's trial**

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow it. Your work is the review's bundle 7 (the server judge and
> its gate: B-01, B-02, L-02 with L-03, G-02, B-04; and A-05 if
> `docs/ROADMAP.md` "Now", item 4, is not done yet), then A-01 and S-05
> from bundle 8, then the trial in part F of
> `docs/plans/2026-11-12-coverage-second-look-thin-agent.md`. The gate
> and judge fixes come first: the roadmap's round 2 rerun waits on them.
> The trial is a measurement, not a gate: write down what it caught,
> missed and wrongly flagged, and stop before building the guard.

---

You are fixing items from a finished code review of this codebase
(`tobi508`). Take **one bundle** from "How this could be handed out" in
`docs/reviews/2026-11-11-code-review.md`, or **one part** (A to J) of
`docs/plans/2026-11-12-coverage-second-look-thin-agent.md`; I (Abby)
will say which. `docs/ROADMAP.md` says what is scheduled when.

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
