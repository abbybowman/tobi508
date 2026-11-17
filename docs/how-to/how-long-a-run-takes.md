# How long a run takes

The README gives the short version. This page has the detail: the time
limits, the settings that change them, and what we measured.

## One run

- **Default:** a run takes as long as the page needs, up to 30 minutes
  (`MAX_RUN_S`). A large page can take several minutes. While it runs,
  each result says what the run is doing and for how long.
- **With `no_time_limit=false`:** a run is held to 10 minutes
  (`RUN_LIMIT_S`, 600 s), plus 20 s for each other page you name
  (`OTHER_PAGE_S`), plus 45 s when something on the page keeps changing by
  itself, such as a ticker or a carousel (`MOVING_ALLOWANCE_S`). A page too
  large for that is refused.
- **Measured:** on www.nasa.gov, runs with 3 other pages took 2-3 minutes.
  Round 2's ten pages took 17 s to 15.5 min each with every test (66 min
  in all; 2026-11-13, judge off).
- A test that does not finish in time comes back NEEDS REVIEW, with the
  reason.

## One test

Each test also has its own time for collecting evidence: its budget (60 s
for most tests, up to 10 minutes for 5.D; set with `TEST_BUDGETS_S`) or
half of what is left of the run, whichever is smaller. The budgets are
provisional: about twice the longest time seen on round 2's pages.

- A test that runs out of its time is NEEDS REVIEW ("ran out of its
  time"). The tests after it still run, cheapest first.
- The report lists each test's time (`test_times`).
- The longest single tests on round 2's pages were 5.D on a page with 98
  form fields (8 min) and 4.F on a long page (4.5 min).

## One call

A tool call returns within 45 s (`CALL_WAIT_S`), under common MCP client
timeouts. A run not done by then keeps going in the server. The result
says `"status": "running"` with a `job_id`, and `tobi_run_status` waits for
it again until `"status": "done"`.

So you do not need to raise your client's tool timeout (Claude Code's is
60 s, `MCP_TOOL_TIMEOUT`), and Claude Code's move of calls longer than
120 s to the background (`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`) does not
apply.

## Large pages

- A page with too many stops to Tab through is refused at once.
- A page with more than 40 form fields is tested without 5.D. 5.D's
  finding gives the call that runs it: call again with `no_time_limit:
  true` and expect 15-20 minutes of `tobi_run_status` calls.

## Answering questions

Recording answers with `tobi_answer_questions` takes under a second,
unless the server has to press a key in the recorded page to check an
answer.

## Several runs at once

The server tests 2 pages at a time (`MAX_CONCURRENT_RUNS`). More wait in a
queue, and a run's time limit starts only when it leaves the queue. Each
run gets its own browser, plus a second, headless one that watches the page
for Test 2. On a 4-CPU machine, 3 runs at once ran normally and 12 at once
timed out (measured before the second browser was added).
