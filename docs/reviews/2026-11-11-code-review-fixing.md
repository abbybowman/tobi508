# Handoff: starting a thread on a roadmap step

The roadmap's "Order of work" (`docs/ROADMAP.md`) lists the steps to the
demo. Start each step in a new session with its prompt below. Most send
the thread to the instructions below the line (how to fix one item, the
working rules).

**A prompt is removed from this file when its step is merged,** so what
is listed here is what is left to start or still running.

**Done:** steps 1 to 10, 6b to 6h, 10a's freeze fix and 12a (PRs #39
to #101; `docs/archive/2026-11-14-roadmap-to-the-demo.md`). Round 3
is scored. Step 9b's thread is running.

**Order to start them:** 10c now; 10d when 9b is done; 12b when the
VAST environment exists; round 4 (step 10b) if I key one.

## Starting a thread

**Step 10c, Opus: what round 3 showed** (now; plans and prompts, no code)

> Read `CLAUDE.md`, `docs/ROADMAP.md` and `docs/KNOWN-LIMITS.md`,
> then round 3: `evals/judging/round3/score.md` and `score.json`, the
> ten pages' `results/pNN/report.json` and `pre-scrt.json`, and my
> keys in `evals/judging/round3/keys/` (the round is locked and
> scored, so the keys are open). Round 3 was a blind round on
> science.data.nasa.gov, a site the tool was not developed on. Your
> work is step 10c of the roadmap: say what it showed and plan what to
> do about it. Change no code, spec or test. Never fetch the pages
> live: everything you need is in the reports; ask me for the frozen
> archive only if a report cannot answer a question.
>
> The score: 149 of 220 cells decided, 118 agree. Wrong: 2 PASS where
> my key fails (5.F and 5.G on p03, the contact page), 1 DOES NOT
> APPLY where it fails (4.F on p08), 18 FAIL where it passes (9.B on
> six pages, each against the first other page, row N3; 4.A on p07 and
> p08, about 45 controls each on row M16; 4.E on p07, p08 and p10;
> 4.F, 5.A, 5.B, 5.C, 5.D), 10 DOES NOT APPLY where it passes (5.B on
> five pages; 5.D on three). 71 cells were left for a person (19.A on
> 8 pages, 4.A and 4.D on 7).
>
> First, a table of every wrong cell and every cell left for a
> person: the page, the test, my key and its comment, the tool's
> outcome, rows and sentence, and the cause in one line, from the
> report's evidence (not a guess: where the report does not show the
> cause, say so). Then group the cells by cause. For each cause:
> - what the tool did and what I did as the tester, in plain words;
> - whether it is the rule (the spec decides wrongly), the reading
>   (the page was not read as it is), the judge (an answer was wrong
>   or unsure where the evidence settles it), the recording, or my
>   key (say so plainly if you think a key cell is wrong, and why);
> - whether rounds 1 and 2 show the same cause (their latest reruns:
>   `evals/judging/gate-2026-11-14/` and, for round 1,
>   `gate-2026-11-16/` on branch `claude/elegant-lamport-7noqy0`), or
>   whether it is new with this site (its pages p07 to p10 are
>   applications built with a script framework; say what about them
>   the tool was not built for);
> - the smallest fix, the spec row it changes, the fixture it needs
>   and the nearest page that must keep its outcome, its size, and
>   whether it turns NEEDS REVIEW into an outcome or removes a FAIL my
>   key confirms (those need my approval first).
> Also look at 19.A on round 2's CILab page: it passed in step 6h's
> rerun and FAILs in step 6g's (`evals/README.md`, the 2026-11-15
> reruns) though both of my key's ways are on the live site. Say what
> the two reruns gave it and which is right.
>
> Rank the causes: a PASS or DOES NOT APPLY where my key fails first
> (a false PASS is the worst error), then by cells. Say which, if any,
> is small and safe enough to do before the Nov 17 cut; assume the
> rest is after the demo.
>
> Write it up as `docs/plans/2026-11-16-after-round3.md` (the table,
> the causes, the ranked plan), add one entry per piece of work to
> "Next: after the demo" in `docs/ROADMAP.md` with its step number,
> and add a prompt for each under "Starting a thread" in
> `docs/reviews/2026-11-11-code-review-fixing.md`, written so a fresh
> thread can start from it alone. Add each wrong outcome that
> reproduces to the README's "Known wrong outcomes" table and each
> new limit to `docs/KNOWN-LIMITS.md`; do not touch the README's
> status table (step 10d has it). Round 3's pages are development
> pages from now on: say in the plan that a later run on them is a
> rerun, never in place of this score. Show me the ranked list of
> causes before you write the prompts.

**Step 10d, Sonnet: the README's status table, made by a script** (when step 9b is done)

> Read `README.md` ("TT tests in scope"), `tests/test_readme.py`,
> `evals/judging/round3/score.json`, and step 9b's results for rounds
> 1 and 2 (`evals/judging/gate-2026-11-16/`). The README's status
> table has grown into a list of results per round. It is to be a
> very high-level view: one colour and at most a few words per test.
>
> Write `evals/status_table.py`. It reads the latest scored result of
> each site (round 3's blind score; step 9b's reruns of rounds 1 and
> 2) and, per test, counts over all three: agree, PASS or DOES NOT
> APPLY where the key fails, FAIL or DOES NOT APPLY where the key
> passes, and left for a person. One rule gives the colour and the
> words, first match:
> - red, "passed a page a tester failed": any PASS or DOES NOT APPLY
>   where the key fails;
> - red, "wrong more often than right": more wrong than agreeing
>   among decided cells;
> - yellow, "often fails pages a tester passes": wrong on more than 1
>   in 5 decided cells;
> - yellow, "mostly left for a person": fewer than half the cells
>   decided;
> - green, "agrees with a tester": otherwise.
> Show me the table this gives and the counts behind it before you
> change the README: I may move a threshold.
>
> Then: the README table has the columns ID, test name, spec (version
> and link, as now) and status (the colour and those words, nothing
> else), with one line above it saying what the colours mean, which
> results it is from and that the counts are in `evals/STATUS.md`.
> The script writes the rows between two marker comments in the
> README, and writes `evals/STATUS.md`: per test and site, the counts,
> and which run each is from (round 3 blind; rounds 1 and 2 reruns on
> development pages). `tests/test_readme.py` fails when the README's
> rows are not what the script writes. Everything the old rows said
> about what a test reads or cannot do is already in
> `docs/KNOWN-LIMITS.md` or the specs: check each sentence you remove
> is there, and add the ones that are not. Never write "certified",
> "compliant" or "conformant" about a page; "agrees with a tester"
> is about our evaluation pages only, and the line above the table
> says so.

**Step 10b, Sonnet: round 4, a second blind round, if I key one** (the freeze the day I key the pages, then the run)

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
