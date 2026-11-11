# The agent eval: harness and scoring

What cost time building and reading agent eval rounds. How to run one: `evals/agent/README.md`.

## The agent eval harness: what cost time

`evals/agent/` runs Agent A (this server) and Agent B (Playwright MCP) on a
frozen round. Plan: `docs/plans/2026-10-31-agent-eval.md`. Runbook:
`evals/agent/README.md`.

- **Frozen tested pages, live rest of the site.** A frozen search results
  page answers only the one search the freeze made, so 19.A (and an
  agent's own routes) needs the live site; the tested pages must still be
  the copies the key was made on. `FROZEN_PAGES_DIR` (`frozen.py`) is a
  server setting: "record_missing" records a URL and adds it (the freeze),
  "tested_frozen" requires the tested page to be frozen and records other
  same-host pages live (Agent A), "replay" refuses anything not frozen.
  Agent B's init-page applies the same split in its browser, logs each
  live page, and its connections go through `egress.py`, as Agent A's do.
- **Init-page route order.** Playwright runs the most recently registered
  route first. The rule for what no recording answers (live, refused or
  aborted) is registered first, so it runs last; every HAR then uses
  `notFound: "fallback"`.
- **Playwright MCP 0.0.83 writes automatic page snapshots to a file**
  (`[Snapshot](…yml)`), not into the tool result. Agent B has no file
  tools, so it must call `browser_snapshot`, which returns the snapshot
  inline (`tests/test_agent_freeze.py`). Claude Code users would read the
  file instead.
- **Playwright MCP's defaults differ from ours.** It turns Chromium's
  sandbox on (this fails as root in a container) and exposes tools that a
  page registers itself (WebMCP). Agent B runs with `--no-sandbox` (our
  server's Playwright default) and `--no-webmcp`, because page content
  must never choose a tool.
- **Its HAR replay needs care.** With several HARs on one page, none may
  use `notFound: "abort"`: later routes run first, so an aborting HAR
  would hide the others and the live rule. Requests that
  failed while recording (status -1) must be failed again, or the replay
  waits forever (`egress-proxy.md`). Its HAR zips use data descriptors, so
  the init-page reads the zip's central directory.
- **An MCP client is more than tool calls.** The tool links screenshots
  as `run://` resources. Claude Code offers a read-resource tool; a bare
  API loop does not. Both arms get `read_mcp_resource`, and both get the
  same `ask_helper` tool (a helper with its parent's tools, one level
  deep).
- **Subprocess environment.** MCP servers start with only what a browser
  and Python need (`arms._base_env`). `PLAYWRIGHT_BROWSERS_PATH` is among
  them; without it, Playwright looks in `~/.cache` and finds no browser.
- **Errors inside MCP sessions surface as "unhandled errors in a
  TaskGroup".** `run._describe` unwraps them to the first real cause.
- **The leak check asks for JSON fields,** not free text. "No, 'a11y'
  does not appear" would otherwise trip a substring check.
- **The Claude Code CLI route** (`cli.py`) leaked the user's email until
  `HOME` was an empty folder and the session variables were unset (plan
  section 7.2). In `-p` mode, `--tools` sets the built-in tools (the helper
  shows as `Task` in the start-up event, `Agent` to the model), and
  `--allowedTools mcp__<server>` allows a server's tools without prompts.
  The stream has a `message_start` and a `message_stop` for every model
  call, subagents included (`parent_tool_use_id`), which give per-call
  times and tokens. `rate_limit_event` rows give the account's 5-hour and
  7-day use and reset times. `stdin` must be closed, or the CLI waits 3 s
  for input.
- **Recordings stay out of git; reports go in.** `.gitignore`'s `runs/`
  matched every Agent A run folder, so round 1's tool reports were never
  committed (the first lock covered files only one cloud session had), and
  the frozen recordings made the repository too large to clone (about
  200 MB of 56 MB packed). Now `.gitignore` keeps a round's
  `runs/*/report.json`, `pre-scrt.json` and `steps.jsonl` and drops every
  `*.har.zip`, `*.png` and `runs/*/evidence/` under `evals/judging/`; the
  rest goes in an archive outside git, with a SHA-256 manifest
  (`evals/judging/round1/results/ARCHIVE.md`). Before a lock, check that
  `git status --ignored` shows nothing the score reads.
- **A cloud container re-signs direct connections.** `egress.py` connects to
  the address it checked; in a cloud session that connection gets a
  certificate from an egress gateway Chromium does not trust
  (`ERR_CERT_AUTHORITY_INVALID`), while the container's `HTTPS_PROXY`
  gives the site's real certificate. The top-level page still loads (the
  navigation guard fetches it another way), so the failure is silent: live
  pages, and anything frozen there, have HTML but no CSS, fonts or scripts
  (status -1). Round 1's search page frozen in the container and its live
  19.A searches had this. Fix: `UPSTREAM_PROXY="$HTTPS_PROXY"`. Check a
  recording made in a new environment: its CSS and scripts must be status
  200.
- **One recording's failed copy of a shared file.** Pages of a site share
  CSS and scripts. Playwright consults the newest-registered HAR route
  first, so a recording holding a failed entry (status -1) for a shared
  file served it on every page (round 1's first Agent B run: 58-107
  console errors per page). The init-page now routes cleaned copies of the
  recordings without their failed entries.
- **The CLI cuts an MCP tool call off at 60 s by default.** Round 1's first
  Agent A attempt (2026-11-04) timed out on every `tobi_run_tt_tests` call
  with other pages, which takes minutes. `cli.py` sets `MCP_TOOL_TIMEOUT` to
  one hour (checked with a 70 s tool). The CLI's MCP log (in its `HOME`,
  under `.cache/claude-cli-nodejs/*/mcp-logs-<server>/`) shows timeouts the
  step log cannot: the step log records a result's size, not its text.
- **Agent B never gets `browser_run_code_unsafe`** (it runs any code in
  Playwright's process: the live site, this machine's files), and its
  WebFetch is refused on the tested site's hosts with the CLI rule
  `WebFetch(domain:<host>)`, with and without `www.` (checked 2026-11-04:
  the rule refuses that domain and allows others). Search results show
  snippets of any site; only fetching the tested pages is blocked.
- **After 120 s the CLI moves an MCP call to the background, and a `-p`
  session can lose it.** If the agent then ends its turn to wait, the
  headless session ends, and the call is killed with it (round1-answers,
  2026-11-04: Missions, NACA and KSC lost, no RESULT line). `cli.py` sets
  `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` to one hour.
  `CLAUDE_CODE_DISABLE_MCP_TASK_BACKGROUND=1` did not stop the move.
  - **How it was found:** the setting names come from the CLI binary
    (`grep -a`), then a 12 s FastMCP tool with the threshold at 3 s (moved
    to the background, then lost) and at 60 s (answered).
  - **The CLI step log's call durations include the 120 s hold.** Calls
    sent together show 120, 239, 359 s… That looks like a queue, but it is
    not. Read each run's start time in the server's own `steps.jsonl`
    (`run_start`) before calling anything queued.
- **The helper tool can fan out.** Both arms get the CLI's subagent tool
  (`Agent`, shown as `Task`). Told to finish every test, Agent A started 9
  subagents at once, each running the tool. The 4-CPU container reached a
  load average of 51 with 310 Chrome processes, and checks failed with
  `Page.goto` timeouts. Such results measure the machine, not the tool.
  - `cli.py` caps helpers at one at a time
    (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=1`; the CLI's default is 20).
    Checked with the real CLI: asked for three in parallel, one ran and
    two were refused. The cap holds whatever the model decides, including
    when page text steers it (a security review flagged the uncapped
    default on PR #11).
  - Development runs can also drop the helper (`--no-subagents`).
  - Watch a long run's load (a Monitor on `/proc/loadavg`), and stop it
    by hand if it climbs.
  - Kill the CLI process, then the `tobi508.app` servers, by PID: a
    `pkill -f` whose pattern appears in the shell's own command line kills
    that shell too.
  - Record a stopped run under `attempts/` with a README.

### Round 2 (2026-11-08)

- **Pause a round blind, not scored, when it is broken.** Round 2's first
  runs lost most cells to delivery problems (results over the client's
  limits, slow replays; `tool-output-size.md`). Both were
  visible without the keys, so the round was paused unscored, fixed,
  rerun into the same round, and the first runs kept and scored beside
  the later ones. Scoring first would have unblinded the fix.
- **Read the debrief and the transcript before blaming the agent.**
  "The agent skipped 140 questions" was three results the CLI had saved
  to a file. Count `exceeds maximum allowed tokens` and `Output too
  large` in `transcript.json` for every Agent A run.
- **Smaller conversations, same prompt.** Pairs (`--group-size 2`)
  instead of groups of 5. Give cross-page tests pages of the same
  template: pairing CILab with 14592 (different templates) turned 9.A's
  Fail into Does Not Apply.
- **A first-round state exists only while no one has answered.**
  Answering rewrites each check's evidence file (`resume` writes state),
  so a run's questions as first asked can be reused only from a run with
  no `answers_recorded` in its `steps.jsonl`. Keep one unanswered run per
  page if a later arm (Agent C) may need it, or plan a fresh run.
- **Archive sets that reference each other.** A repeat that copies an
  earlier folder repeats its evidence; the archive leaves out any file
  over 100 kB identical to one in a reference folder and names its twin
  (`same_as`), so sets are restored in order (`results/ARCHIVE.md`).
  Info-ZIP's split mode (`zip -s`) produced a bad CRC on rejoin; one zip
  cut with `split` and checked after rejoining did not.
- **Debriefs for both arms** (`--debrief`, a neutral question): Agent B
  said it marked criteria PASS it never tested, "because of cost and
  time"; Agent A said it stopped "after the first batch" of a large page.

## Scoring and reading an agent eval round: what cost time

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

### Round 2 (2026-11-08)

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
