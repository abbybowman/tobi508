# tests

## Fixtures

- Use a vendored W3C ACT test case (or a Section 508 Baseline Alignment
  case) when one covers the rule; write a custom page only for a gap. Never
  edit an ACT page.
- Expected outcomes live in `fixtures/act/manifest.json` or the test files,
  never in a page (pages are evidence an agent may read).
- Tests never fetch from the network.
- `fixtures/inject/` holds pages whose text tries to steer the judge;
  `fixtures/budget/` holds timing pages.

## What the tests prove

Scripted answers here (`harness.py`) test the rules, not the questions:
after changing an open question, its rubric or its input, run the judge eval
in `evals/` (`docs/solutions/judge-eval.md`). `drafts.py` registers
draft-spec checks for tests only; `scoring.py` prints DHS and ACT agreement
after every run.

## Commands

```bash
uv run pytest                    # Playwright Chromium, headless, one worker per CPU
uv run pytest -n 8               # tests mostly wait, so 2x CPUs is faster
uv run pytest -n0 tests/test_fixtures_4e.py -k f03   # one fixture while building
uv run pytest -m slow            # long fixtures
TEST_BROWSER_CHANNEL=chrome TEST_HEADED=1 uv run pytest   # installed Chrome, visible
# Agents: for long runs, keep one line per test in a log and report progress
# from it (done of total, failures by name), never only the final -q summary:
uv run pytest -n 4 -v -p no:cacheprovider > "$TEMP/pytest.log" 2>&1   # then:
grep -cE " (PASSED|FAILED|ERROR|SKIPPED|XFAIL)" "$TEMP/pytest.log"; grep -E "FAILED|ERROR" "$TEMP/pytest.log"
cat runs/test-progress.txt       # any run: done of total, elapsed, rough ETA, failures
```
