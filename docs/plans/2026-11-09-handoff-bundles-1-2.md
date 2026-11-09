# Handoff: build bundles 1 and 2 (2026-11-09)

For a fresh session. You build the parts of two plans that are already
decided, test them, and keep the plans' status current. Abby (the
repository owner, tester and decision maker) reviews each pull request.

## Read first, in this order

1. `CLAUDE.md`. Its principles are non-negotiable: never claim
   certification; outcomes come only from `docs/rules/` specs; a false
   PASS is the worst error; say what you verified and what you assumed.
2. `docs/plans/2026-11-08-rules-principle3-build.md` (bundle 2: rule
   fixes). The top half says what and why; "Builder notes" says how.
3. `docs/plans/2026-11-08-apijudge-build.md` (bundle 1: the server
   answers its own questions). Same layout.
4. Only when a builder note sends you there: the code it names, the spec
   you are changing, `docs/plans/2026-11-08-post-round2-fixes.md`, and
   `docs/solutions/` (read its README).

The plans' decisions are final for this work. Do not reopen them; if
something you find contradicts one, stop and ask (below).

## Getting started

- The plans are on branch `claude/fervent-pascal-l32198` (fetch it if
  `main` does not have them yet).
- Abby gives you round 2's frozen pages (archive set `round2-frozen`,
  zip parts). Restore them at the repository root as
  `evals/judging/round2/results/ARCHIVE.md` describes, check every file
  against the manifest's SHA-256, and never change or commit them (the
  HARs are git-ignored). Never edit anything else under
  `evals/judging/round2*/`.
- `uv sync --group dev`. Tests: see `CLAUDE.md` "Commands" (keep a log,
  report progress from it).

## Order of work (one pull request per item, each from `main`)

| # | Item | Plan | Needs model calls? |
| --- | --- | --- | --- |
| 1 | Step 1: the four checks on the frozen pages (CILab's video, 5.D on 5340, "View timeline", the year popup) | bundle 2 | No |
| 2 | 4.C and 5.D on 5340 (fixes 2, 5) | bundle 2 | No |
| 3 | 9.A-9.C templates (fix 6) | bundle 2 | No |
| 4 | Videos (fixes 1, 4) | bundle 2 | Judge eval for 4.A only |
| 5 | ApiJudge: module, server wiring, dry mode, tests (builder notes 1-3) | bundle 1 | No (tests use `Scripted`) |
| 6 | ApiJudge: gate scripts and trick-text test pages (builder note 4), built and tried on 2 pages only | bundle 1 | A small CLI trial |
| 7 | Opening everything, phase 1 (fix 9b) | bundle 2 | Judge eval for 5.A-5.C |
| 8 | Error values (fix 3), top-level forms only | bundle 2 | Judge eval for 5.F, 4.C |

Item 1 writes its findings into the bundle 2 plan before items 2 and 4
use them. Items 2-4 touch different files; item 5 is independent of
them. Item 7 waits for 2 and 4 to merge; item 8 for 7. If a pull request
is waiting for review, start the next independent item.

## How to build each item

- Spec first: change the rows, bump `spec_version` (MINOR), record the
  decision with Abby's name and date as the plan gives it. No outcome
  logic outside the spec.
- A test page for each behaviour, expected outcomes in the test files,
  never in a page. Never edit a vendored ACT or Baseline page.
- Run the fast checks, then the full suite. A test that fails only under
  load: rerun it alone and say so; never skip or weaken a test.
- Check the item on round 2's frozen pages, and compare with Abby's key
  for that cell (`evals/judging/round2-armc/keys/`). Before any change
  removes a FAIL, read the key's comment for that cell and confirm its
  elements are still found.
- Same commit as a spec version: `docs/hackathon/evaluation.md` and the
  matching slide in `docs/hackathon/deck.md` (never fill a [FILL]).
- Commit messages say what changed and why; no model names in commits,
  code or docs.

## Tokens: be careful

Model calls use the Claude Code CLI (`claude -p`) in this container, not
any API key. Run them only for: the judge eval of the question types an
item changes (not the whole eval), and item 6's trial on 2 pages. Do not
run the full ApiJudge gate (three repeats on 10 pages): it runs once,
later, when Abby says. Before any model run, use the dry mode (item 5) or
the eval's packet count to say how many calls and roughly how many tokens
it will take; after, record the measured tokens in the plan.

## Keep the plans current

After each item, add or update a **Status** section at the top of its
plan (one line per item):

```
- Fix 2 (4.C exit): built, PR #NN. Verified: test_fixtures_4c.py (f37,
  f38 and all existing), full suite 1234 passed; 5340 frozen page: 4.C
  FAIL by M12, key Fail. Assumed: none.
```

Say "verified" only for what a command or test showed; anything else is
"assumed". Record anything that cost time in `docs/solutions/` (one
short entry). Update `docs/ROADMAP.md` when an item is done or moved.

## Stop and ask Abby when

- a test page or a frozen page gives a result the plan did not expect;
- a change would remove a FAIL the key confirms, or turn a NEEDS REVIEW
  into a PASS anywhere;
- a question comes up that the plans, TT text and specs do not answer;
- an item would need more model calls than the plan says;
- the 5340 year popup check (item 1) shows a keyboard user can get back
  to the field: item 8's expected outcome then changes.

Ask with what you found, the options, and your recommendation. Carry on
with other independent items while you wait.

## Done means

Each item merged or in review with its status line, the full suite
passing, and the plans saying plainly what is built, what is tested on
which pages, and what is left.
