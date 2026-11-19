# Handoff: starting a thread on a roadmap step

Prompts for the roadmap steps that are not GitHub issues, and the
instructions for fixing an item of the 2026-11-11 code review (below the
line). Work that is a GitHub issue starts from the issue's own prompt and
[docs/how-to/work-an-issue.md](../how-to/work-an-issue.md).

**A prompt is removed from this file when its step is merged,** so what
is listed here is what is left to start or still running.

**Done:** steps 1 to 10, 6b to 6h, 9b, 9c, 10a, 10c, 10d, 12a, 21, 22, 23, 29's
small part, 31 and 36, and 4.F 1.11.0 (PRs #39 to #121, and 9c's;
`docs/archive/`). Round 3 is scored.

**Order to start them:** 41 (the status page) touches no test or spec, so
it can run beside the issues below.

## Starting a thread

**The after-demo rows are GitHub issues.** Each issue holds its scope, the
cells it should move, the decisions it waits on and its agent prompt, and
sends the thread to [docs/how-to/work-an-issue.md](../how-to/work-an-issue.md)
for the steps every thread shares, the rerun included:

- [#134](https://github.com/abbybowman/tobi508/issues/134) Applications (steps 24, 25, 26, 35a, 35e; the late-drawing guard)
- [#135](https://github.com/abbybowman/tobi508/issues/135) 4.D and 5.D on what opens (step 27, then step 15's 4.D and 5.D part; the plain-button form)
- [#136](https://github.com/abbybowman/tobi508/issues/136) 4.A and 4.F (steps 28, 33, 32)
- [#137](https://github.com/abbybowman/tobi508/issues/137) Forms (35b to 35d, 37, the rest of 29, 30; 5.D's wording after a retry)
- [#138](https://github.com/abbybowman/tobi508/issues/138) Site tests (CILab, W4, 34, other pages from the freeze, 19b)

Order: #134 first; then #135 and #136 side by side; #137 once #135's 5.D
change and #134's step 35a are merged; #138 once #134's step 26 is merged.

**Step 41, Opus: the live status page** (after the demo; beside the test rows, since it touches no test or spec)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (step 41 and Abby's decision of
> 2026-11-17 above "Known limits"), `docs/how-to/get-started.md`,
> `docs/how-to/deploy-on-vast.md` (sections 4, 6a and 9),
> `src/tobi508/jobs.py`, `src/tobi508/routes.py`, `src/tobi508/app.py`
> (`http_options`), `src/tobi508/tools/run_tt_tests.py` and
> `run_status.py`, and `demo/prescrt-viewer/README.md`. Then plan with
> me before building; one pull request.
>
> **Why.** Using TOBI from Claude Code, I saw the run's progress only
> while a tool call was open: after `CALL_WAIT_S` the call returns a
> job and the progress line goes, and between `tobi_run_status` calls
> only my agent spoke. I want a page in the browser that keeps showing
> what the server is doing while I chat with my agent. A status line
> in Claude Code is out: too hard for our users to install.
>
> **What.** A read-only page served by the server over HTTP (way 3 of
> get-started, and hosted), refreshing itself: each run the server
> holds, with the page tested, its tests, state, the progress step and
> message, and times; when a run is done, its outcome per test and a
> way to open its pre-SCRT file in the viewer (`viewer.html`) in the
> browser. Each tool result that starts or waits on a run carries the
> page's address (one short field; keep tool output small), and the
> agent is told to give it to the user.
>
> **Decided:** the MCP endpoint keeps sign-in; this page is open
> without it, as `/health` is, on a server with `AUTH=oidc`, and shows
> every person's runs, URLs and results (my decision, recorded in the
> roadmap). Without sign-in the server still listens on loopback only:
> never change that rule (`app.http_options`).
>
> **Scope.** Only what the server holds now: jobs in memory
> (`jobs.py`) and run folders until they expire (`RUN_TTL_HOURS`).
> Nothing that outlives a restart or the 24 hours: that is the store,
> step 17. Over stdio there is no HTTP server, so no page; say so in
> get-started.
>
> **Rules to keep.** Read-only: GET only; it starts, answers and
> changes nothing. Page content is untrusted (`CLAUDE.md`, principle
> 5): every URL, title, message and file value is shown as text, never
> HTML, on the page and in the viewer (test it with a page title and a
> URL holding markup and script). No outside scripts, styles or
> requests; a strict Content-Security-Policy. The disclaimer on every
> view; never "certified" or "compliant". The page copies outcomes and
> decides none. The viewer today opens a file the user picks and makes
> no requests; how it gets a run's file (embedded by the server, or a
> same-origin fetch with its CSP changed to allow only that) is a
> choice to bring me with its trade-offs.
>
> **Tests:** the page answers without a token while `/mcp` answers
> 401; it shows a running job's progress and a finished run's
> outcomes; markup in page values is escaped; a POST is refused; the
> result field is present and small. Run it once by hand over way 3
> and show me a screenshot. Update the how-tos, `SECURITY.md` (an
> unauthenticated route).

---

You are fixing an item of the 2026-11-11 code review of this codebase
(`tobi508`); your prompt names it. For a GitHub issue, follow
[docs/how-to/work-an-issue.md](../how-to/work-an-issue.md) instead.

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
   in a log (`tests/CLAUDE.md`, "Commands").
6. **If a question, its rubric or its input changed,** run the judge eval
   for it (`docs/solutions/judge-eval.md`). Scripted answers in `tests/`
   test the rules, not the questions.
7. **Update with the fix, in the same commit:** the spec's `spec_version`;
   the README's "Known wrong outcomes" list (remove the case you fixed;
   add any new one you find), so the README says what the test can and
   cannot do today; `docs/KNOWN-LIMITS.md` when a limit is removed or
   newly stated. The README's status table is generated
   (`evals/status_table.py --write`).
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
