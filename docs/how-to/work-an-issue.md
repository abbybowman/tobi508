# How to work an issue

One GitHub issue is one row of the roadmap's "Next" table and one thread
(one session, one branch, one or more pull requests). The issue is the
scope: its body, then its comments. Where the issue and a plan disagree,
the issue wins; say so in your report. Every issue's agent prompt sends
you here for the parts that are the same in every issue.

## Before you start

1. Read `CLAUDE.md` (the eight principles bind every change), the issue,
   and the plan sections it links.
2. **Check what is left.** An issue's "Where it stands now" is from a
   gate run on a given date and commit. Run each cell it names (or the
   fixture that stands for it) on current `main` and see the outcome
   the issue states. If a cell no longer reproduces, say so and stop on
   that step.
3. **Check the overlaps.** The issue lists the TT tests it changes and
   the other open issues that change the same tests. Do not change a
   test another thread holds; if you must, say so in the issue first.

## How to fix one step

1. **Decide whether the spec changes.** The spec is the only source of
   outcome logic (principle 2).
   - The code does not do what the spec says: fix the code, no spec
     change.
   - The spec's rows or Terms give the wrong outcome: draft the change
     first, as a MINOR version, with the research `CLAUDE.md` asks for
     (TT text from `catalog.py`, the W3C Understanding page and
     techniques, ACT rules, the Baseline test). Show Abby the draft
     before building; `specs/rules/` needs her review (CODEOWNERS).
   - A change that turns a NEEDS REVIEW into a PASS, FAIL or DOES NOT
     APPLY, or removes a FAIL an answer key confirms, waits for Abby's
     yes on the spec text. The issue marks these steps "approval".
2. **Make a fixture first.** Expected outcome and rows go in the test
   file, never in the page. Use an ACT or Baseline case when one
   covers the rule. Write the test, see it fail, then fix. Add the
   issue's "must keep" fixtures to what you run.
3. **Run what could have moved:** the check's own fixture file, its
   ACT and Baseline cases, and every check that calls a function you
   changed. For a long run keep one line per test in a log
   (`tests/CLAUDE.md`, "Commands").
4. **A question, its rubric or its input changed:** run the judge eval
   ([judge-eval.md](../solutions/judge-eval.md)). Scripted answers in
   `tests/` test the rules, not the questions.
5. **Same commit as the fix:**
   - the spec's `spec_version`: rebase on `main`, take a number `main`
     has not used, run `uv run python -m tobi508.rules lock`;
   - the README's "Known wrong outcomes" list and the line in
     `docs/KNOWN-LIMITS.md` (remove what you fixed, add what you found);
     the README's status table is generated (`evals/status_table.py
     --write`), and its "see known wrong outcomes below" note follows the
     list's test ids;
   - `SECURITY.md` when a security control changes;
   - the issue's row in `docs/ROADMAP.md`.
6. **Report verified (test or command) apart from assumed** (principle
   6), in the pull request and in a comment on the issue.

## The rerun, at the end

Every issue that changes a test reruns it on all three rounds' frozen
pages before it closes.

1. **Get the archives.** Ask Abby for the three rounds' frozen archives
   (she holds them). Check their hashes against each round's
   `ARCHIVE.md` or manifest before you use them, as gate 9c did.
2. **Run** the tests you changed, and the tests that read what you
   changed, with the server judge on every type as gate 9c ran it:

   ```bash
   uv run python evals/apijudge_gate.py run --date <date> --round 1 --tests <ids> --frozen-mode replay
   ```

   once per round (`--round 1`, `2`, `3`; `--frozen-dir` when the
   unpacked archive is not where the round's folder expects it), writing under
   `evals/judging/gate-<date>/`, never under a locked round's folder
   (`evals/judging/round3/` is locked). `--frozen-mode replay` serves
   every page from the freeze, other pages too; say if any page was
   loaded live, and why. 19.A's live site search cannot run in replay
   mode: an issue that changes it says which mode to use.
3. **Score** each round with its own keys and scorer, against the
   latest gate (today
   [gate 2026-11-17-9c](../../evals/judging/gate-2026-11-17-9c/),
   `compare-roundN.json`).
4. **Show Abby every cell that moved, beside her key and its comment:**
   old outcome, new outcome and the rows that decided it, round by
   round. A cell on round 1 or 2 that moved gets its own line and a
   reason. Round 3's pages are development pages: this is a rerun, never
   in place of round 3's blind score.
5. **Update** the README's "Known wrong outcomes" list and
   `docs/KNOWN-LIMITS.md` for what you fixed, in the same commit (not
   the README's status table, which is generated).

## Working rules

- One issue per thread, on its own branch from `main`. Commit after each
  step, so a session that is cut off loses nothing; open a pull request
  every few steps, so other threads see the changes.
- Before you bump a spec version, rebase on `main` and take the next free
  version. Keep each commit to one step, so a conflict is small.
- At most 3 subagents at a time, and only for separable work (writing
  fixtures, running fixture files).
- Never rewrite `evals/judging/`: its runs and locks are records of what
  ran.
- Never write "certified", "compliant" or "Section 508 conformant" about
  a tested page, in code, docs, issues or pull requests.
