# Handoff: starting a thread on a roadmap step

The roadmap's "Order of work" (`docs/ROADMAP.md`) lists the steps to the
demo, numbered 1 to 9. Start each step in a new session with its prompt
below. Steps 1 to 5 send the thread to the instructions below the line
(how to fix one item, the working rules); steps 6 to 8 stand alone.

## Starting a thread

**Step 1, Sonnet: quick fixes and CI** (done: PR #39)

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

**Step 2, Opus: the count of what exists, and the guard on DOES NOT APPLY** (running)

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

**Step 3, Opus: server judge, gate and sign-in fixes**

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow it. Your work is step 3 of `docs/ROADMAP.md` "Order of
> work". In this order, one commit and one test each: L-02 with L-03
> (the gate in `evals/apijudge_gate.py` asks for a minimum number of
> decided cells, not counting unsure, and fails a type on any wrong
> DOES NOT APPLY; count a tool PASS against a key DOES NOT APPLY apart);
> B-01 (picture links in a judge request only through
> `resources.runs.run_file`, and only links that are a whole input
> value); B-02 (page text cannot close the untrusted block: escape
> `<`, `>` and `&`, and add a page with the closing tag to
> `tests/fixtures/inject/`); G-02 (one attachment per picture per
> request); B-04 (the judge runs after the browser slot is released);
> A-05 (an answer that arrives through MCP is the calling agent's,
> whatever `decided_by` says, and the picture rule applies to it); A-01
> (jobs carry the caller who started them; `get`, `all_jobs` and
> `running` return only theirs); S-05 (under `AUTH=oidc`, a token with
> no `sub` is refused). Each item's entry in
> `docs/reviews/2026-11-11-code-review.md` says where and how. Step 6
> waits on the first five, so open a pull request when they are done.
> These are security and evaluation fixes: no spec changes, and no
> outcome should move.

**Step 4, Opus: the rules' false FAILs** (done: PR #44)

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow its "How to fix one item" and "Working rules". Your work
> is step 4 of `docs/ROADMAP.md` "Order of work": post-round 2 fixes 8,
> 9c, 9, 10 and 11, in that order, as written in
> `docs/plans/2026-11-08-post-round2-fixes.md` (each has its evidence,
> the TT text and the fix). Each removes a FAIL that my round 2 answer
> key says is wrong; each is a spec change (MINOR), a fixture (a
> vendored ACT or Baseline case first) and the check's own tests. These
> turn a FAIL into a PASS or NEEDS REVIEW, the direction where a false
> PASS can creep in, so for each one also add a fixture of the nearest
> case that must still FAIL, and stop for me if a fix would remove a
> FAIL the key confirms. Show the spec change in each pull request's
> description. When a fix is merged, mark it built in the post-round 2
> plan's status table and update the README status line.

**Step 5, Sonnet: "unsure" answers that are answerable** (built 2026-11-13)

> Read `docs/reviews/2026-11-11-code-review-fixing.md` below the line
> and follow its "How to fix one item" and "Working rules". Your work
> is step 5 of `docs/ROADMAP.md` "Order of work": post-round 2 fixes 12,
> 13 and 14, then 24, 25, 26 and 27, as written in
> `docs/plans/2026-11-08-post-round2-fixes.md`. Each changes a
> question, its rubric or its evidence, so each needs the judge eval
> (`docs/solutions/judge-eval.md`; run it through the CLI route) before
> and after, with both results in `evals/README.md`. Fixes 12 and 13
> (4.F) and 14 (9.C) are why the server judge stays off those two
> tests: say in the pull request whether their eval is now clean. Never
> make a rubric push toward PASS; when the evidence does not settle a
> question, the answer must stay "unsure". Mark each fix built in the
> post-round 2 plan's status table and update the README status line.

**Step 6, Opus: the check against round 2** (when steps 1 to 5 are merged)

> Read `CLAUDE.md`, then `docs/plans/2026-11-08-apijudge-build.md`
> ("The gate" and "What is left", item 1) and `evals/README.md`. Your
> work is step 6 of `docs/ROADMAP.md` "Order of work": rerun round 2's
> 10 frozen pages once with today's rules and the server judge
> answering every question type, and score them with the same scorer
> beside round 2's locked rows, judge-decided cells apart from
> rule-decided ones. Use the CLI route (`claude -p`) unless I tell you
> Luna is configured. Count the requests with `--dry` first and tell me
> the estimate before the real run. Write into a new round folder under
> `evals/judging/`; never rewrite a locked round. Report: false PASS,
> missed fails (wrong DOES NOT APPLY), false FAILs and NEEDS REVIEW,
> beside round 2's figures, per test and in all, and for each question
> type whether it meets the thresholds under "The gate" (read against
> them, they do not block). Put the result in `evals/README.md`. The
> README's status table says what real pages showed: update each row
> from this run, and keep its "Known wrong outcomes" table as it is.
> Do not fill any [FILL] in `docs/hackathon/`.

**Step 7, Sonnet: the scored run for the pitch** (Nov 18-19, when I say the submission commit is fixed)

> Read `CLAUDE.md` and `docs/hackathon/README.md`. I have fixed the
> submission commit: <commit>. Run the scored suite once at that commit
> as `docs/hackathon/README.md` describes, and fill every [FILL] in
> `docs/hackathon/evaluation.md` and `deck.md` from that one run, with
> its commit, date and environment. Remove a [PENDING] marker only
> where the work exists and is checked. Never describe a tested page as
> certified or compliant. Show me the filled figures before you commit.

**Step 8, Sonnet: the second look's trial** (if the days allow; it can wait until after the demo)

> Read `CLAUDE.md`, then part F of
> `docs/plans/2026-11-12-coverage-second-look-thin-agent.md`, "Trial".
> Build `evals/second_look.py` and run it on round 2's 10 frozen pages
> with the rules as they were at round 2's lock commit, three repeats,
> through the judge's CLI route. It is a measurement, not a gate: write
> what it caught of the known wrong cells, what it missed, and what it
> flagged that my keys say is right, with tokens and time per page,
> into the plan's part F and `evals/README.md`. Stop there; the guard is
> a later step.

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
