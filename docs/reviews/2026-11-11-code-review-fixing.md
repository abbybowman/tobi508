# Handoff: starting a thread on a roadmap step

The roadmap's "Order of work" (`docs/ROADMAP.md`) lists the steps to the
demo. Start each step in a new session with its prompt below. Most send
the thread to the instructions below the line (how to fix one item, the
working rules).

**A prompt is removed from this file when its step is merged,** so what
is listed here is what is left to start or still running.

**Done:** steps 1 to 7, 6b, 6c, 6d's phase 1, 6f, 6h, 8, 9a and 12a
(PRs #39 to #89; `docs/archive/2026-11-14-roadmap-to-the-demo.md`).
The threads of 6e and 6g are running (their prompts are no longer
needed here).

**Order to start them:** round 3 (step 10) and 9b when 6e and 6g are
merged; 12b when the VAST environment exists; round 4 (step 10b) if I
key one.

## Starting a thread

**Step 9b, Sonnet: the third check** (at round 3's commit)

> Read `CLAUDE.md`, then `docs/plans/2026-11-08-apijudge-build.md`
> ("The gate"), the docstring of `evals/apijudge_gate.py`, and step 6's
> write-up in `evals/README.md` ("Gate 2026-11-13") with its folder
> `evals/judging/gate-2026-11-13/` (`compare.py` is the comparison to
> reuse). Your work is step 9 of `docs/ROADMAP.md` "Order of work"
> (this is 9b): step 9a again
> (`evals/judging/gate-2026-11-14/`, its `compare.py` and the gate
> script's `--round` option), on `main`'s head (record the commit),
> on round 2's 10 frozen pages and round 1's, one repeat, with the
> server judge answering every question type, scored with the same
> scorer. Keep each page's report and pre-SCRT file out of git (about
> 70 MB a run): check `.gitignore` covers the folder you write to
> before your first commit, and commit only the scores, the
> comparison and the write-up.
>
> Before anything else, check and tell me if either fails: the frozen
> recordings of both rounds are restored (`evals/judging/round2/frozen`,
> `evals/judging/round1/frozen`; they are not in git, so stop and ask
> me for the archives, never fetch the pages live), and the browser in
> this container trusts the egress proxy (step 6's six 19.A false
> FAILs were the container's). Use the CLI route (`claude -p`)
> unless I tell you Luna is configured. Run `--dry` first and tell me
> the request and token estimate before the real run. Write into a new
> folder under `evals/judging/`; never rewrite a locked round or step
> 6's folder.
>
> Report, beside step 6's figures and round 2's (and, for 9b, beside
> 9a's): false PASS, missed
> fails (wrong DOES NOT APPLY), false FAILs, NEEDS REVIEW and decided
> cells, per test and in all; every cell that moved from NEEDS REVIEW
> to an outcome since step 6, with whether my key agrees; guard CN's
> cells on round 1's pages apart from the rest, and whether it held
> back any failure there; and for each question type, on both rounds'
> cells together, whether it meets the thresholds under "The gate".
> From each report's `test_times`, list every test that ran out of its
> budget and the longest time each test took, so the provisional
> budgets can be set.
> Run the gate's test-page half for the types that are near. Do not
> change `JUDGE_TYPES`: I choose the types from your report.
>
> Put the result in `evals/README.md`. Then rewrite each README status
> line from this run: one short line per test, and remove a caveat
> only where this run or a grid cell shows it is gone. Keep the "Known
> wrong outcomes" table as it is. Do not fill any [FILL] in
> `docs/hackathon/`. Last, give me the path of each page's
> `pre-scrt.json` beside the path of its key.

**Step 10, Sonnet: round 3, a formal blind judging round** (the freeze and the run in one thread, when steps 6e and 6g are merged; I give the pages then)

> Read `docs/how-to/run-a-judging-round.md` and
> `evals/agent/README.md`. This is round 3, a formal judging round
> like rounds 1 and 2, on the pages I give you in this thread, with
> the server judge answering, exactly as the how-to describes:
> freeze, run, lock, then score against my keys. Never open my keys
> before the lock. Work on your own branch and do not open a pull
> request or merge anything of the round until the run is locked:
> no other thread has seen the page list, and none may before then.
> Keep each page's report and pre-SCRT file out of git.
>
> The freeze (the fuller freeze of PR #52). Check each recording
> against its manifest. Then, for each page, compare one replay with
> the live page before you run any test: the requests that fail in
> the replay, and anything a visitor sees in the first 30 s that the
> replay does not show (a popup, a banner, a player). On round 1's
> pages a feedback popup that opens at 5 s never opened in the
> replay. Tell me what you find before the run; do not change the
> freeze yourself.
>
> The run. On `main`'s head, after steps 6e and 6g are merged; tell
> me the commit before you start, since 9b runs at the same one. Run
> in tested_frozen mode, each page with the round's other pages on
> its host and the site's home page as other pages (19.A loads
> further pages itself). Before the run, check that the site's own
> search loads in your container: run one search by hand through the
> tool's browser and tell me if its results page fails to load any
> script (19.A cannot FAIL where it does not). Report per test and in all; list apart
> the cells inside a web component or a frame; and list every NEEDS
> REVIEW and wrong cell by cause, as findings for the other threads.
> Change no code yourself, and change nothing between the freeze and
> the lock: the score is the blind result for that commit.

**Step 10b, Sonnet: round 4, a second blind round, if I key one** (two threads: the freeze the day I key the pages, the run on Nov 17)

> The freeze. Read `docs/how-to/run-a-judging-round.md`. Freeze the
> pages I give you in this thread with the fuller freeze, check each
> recording against its manifest, and tell me anything that did not
> record. Do not run the tool on the pages, do not open my keys, and
> keep your branch unmerged with no pull request: no other thread may
> see the page list.

> The run, on Nov 17. Read the how-to and `evals/agent/README.md`.
> Run round 4 once on `main`'s head (record the commit; it should be
> 9b's), with the server judge answering: run, lock, then score
> against my keys. Never open my keys before the lock. Report per
> test and in all, and list apart the cells inside a web component or
> a frame. Keep each page's report and pre-SCRT file out of git.
> Change no code from what you find: list it for after the demo.

**Step 12b, Opus: the first deployment** (when the VAST environment exists)

> Read `docs/how-to/deploy-on-vast.md` and follow it with me: I run
> the VAST commands and paste what they print. Deploy, sign in from
> Claude Code, run `scripts/smoke_hosted.py` against the app's
> address, then one real page. Record what differed from the how-to
> and fix the how-to. Only when the smoke test passes on VAST, remove
> the two [PENDING] markers about the end-to-end sign-in
> (`docs/hackathon/evaluation.md`, `docs/hackathon/deck.md`) and
> update `SECURITY.md`'s status.

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
