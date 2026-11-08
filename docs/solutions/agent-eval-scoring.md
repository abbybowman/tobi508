# Scoring and reading an agent eval round: what cost time

Round 1 (2026-11-04) was the first round scored against real SCRT keys.
Results: `evals/agent/README.md` ("Results"). The answering runs:
`evals/judging/round1-answers/README.md`.

- **The lock covers the scorer and the prompt.** `lock.json`'s `code`
  includes `evals/agent/score.py`, `evals/scoring.py`, `compare.py`,
  `scrt.py` and `evals/agent/prompt.py`. `score` refuses to run if any of
  them changed ("score with the code at commit …"); it does not just
  record the change.
  - A scorer fix found after a lock is for the next round (post-round 1
    plan, fix 13).
  - Analysis beyond the scorer goes in a separate script that imports the
    scorer's own functions (`verdict`, `rollup`, `compare`), so there is no
    second copy of the verdict logic.
  - Development prompt versions live in `evals/agent/prompt_dev.py`
    (`--prompt`). Never edit `prompt.py` after a lock.
- **"Not performed" in `agent-score.md` is mostly "needs review".** The
  checks put the note "This test could not be performed" on every
  NEEDS_REVIEW, including ones that only wait for an answer. Sort them by
  the finding's summary instead:
  - "did not complete" / "time limit": cut short;
  - "question … open": waiting for an answer;
  - anything else: could not be performed.
- **An agent can split a page's tests across calls.** In round 1,
  `arm-a-2` ran Missions as six tests, then 9.A alone. Merge per TT test,
  taking each test from the latest finished run whose `tests` included it.
  The locked scorer takes only the latest run.
- **`page_key` drops the query.** `/?search=artemis` scores as the home
  page. A round with both would collide.
- **Rerunning a locked round's pages.** A locked round refuses new runs.
  Use a development folder (`evals/judging/<round>-<name>/`) with the
  round's `pages.txt` and frozen index; `.gitignore` already keeps its
  recordings out.
  - The rerun needs only the frozen `*.har.zip` files from the archive.
    Each is about 16-24 MB, under the 30 MB chat upload limit; the whole
    zip (176 MB) is not.
  - Check each recording against `lock-1.json`'s `files` hashes. The
    manifest is not needed.
- **Check usage before every run.** A one-line
  `claude -p --output-format stream-json --verbose` call prints a
  `rate_limit_event` with the 5-hour and 7-day windows. Round 1's Agent A
  runs cost 1-2% of the 7-day window each, the answering runs about 1% each.
  The cloud session's own work uses the same account.
- **Cost per run is in `summary.json`** (`cost_usd_list_price`,
  `usage_windows` first and last). Cache writes and output cost the most;
  cache reads are cheap. Agent A's 2-4 minute tool results are mostly
  cache writes.
- **Many identical open questions overwhelm the agent.** Missions asked
  152 questions, 96 of them the same 5.D question per checkbox. The CLI
  saved the result to a file the agent read only in part, and the agent
  reran the page six times in smaller pieces rather than answer (fix 15).
- **Per-test numbers come from `evals/agent/per_test.py`.** It merges a
  run's split calls, leaves out pages a run is not scored on, and prints
  a Markdown table (one row per TT test). The README now gives a takeaway
  per test instead of these numbers. For round 1 it
  counts one false FAIL more than the locked score (A-2's split Missions
  call).
- **Check a disputed finding on the frozen recording before asking the
  tester.** Replay the page's `*.har.zip` with Playwright's
  `route_from_har` (`not_found="abort"`) and look:
  - read the element's attributes;
  - press the keys in the finding's steps;
  - list the dialogs open after each step.

  Round 1's "Tab leaves the Internships dialog" was a dropdown
  (`aria-expanded`) beside a hidden Popup Maker overlay with
  `role="dialog"`. The Missions "jumps back up" signals were a card grid
  and checkbox boxes out of line with their labels. Both took minutes, and
  neither needed the tester's time.

## Round 2 (2026-11-08)

- **Ask who decided each wrong cell.** For every cell the tool got wrong,
  check whether any answer fed its finding (the report's `answers` for
  that test) or a rule decided alone. In round 2 every false PASS and
  missed fail was a rule alone, the same in every run; the judges' errors
  were all false FAILs. Without that split, the judge is blamed for the
  rules (fix 17 builds it into the scorer).
- **Weighted scores reward leaving questions open.** Open is 0, a wrong
  answer -1: Agent C answered everything and scored lowest. Report the
  judge-decided cells' accuracy beside the weighted score.
- **The locked scorer applies an adjudication to the tool's per-TT score
  only,** not to the arms' per-criterion rows (round 1 and 2).
- **Keys can slip.** 5144's 5.D row said Fail with a pass comment (the
  SCRT template carried an earlier outcome down when child rows were
  deleted). A comment that contradicts its result is worth checking before
  any rule change; keys should give a reason for a Pass too.
- **A tool Fail the key lacks may be a catch, a scope difference or an
  error.** Look at the evidence before deciding: round 2's unnamed
  carousel buttons were aria-hidden and outside the Tab order (not a
  failure); 5340's OVERVIEW tab showed no focus change at all (a likely
  catch, being retested).
- **A cell that agrees may still miss a failing element.** Home's 5.C
  agreed with the key (Fail) on the filter headings, but the key also
  failed X buttons that appear only after a filter is chosen, which TOBI
  never saw. Before changing a rule that removes a FAIL, read the key's
  comment for that cell and check that the elements it names are still
  found (post-round 2 fix 9b).
- **Most unsure answers had causes in our rules or questions,** not in the
  pages (post-round 2 plan, "Unsure answers"): read each unsure answer's
  reasons against the key before calling it an edge case.
