# src/tobi508: server code

Rules for the server's code. The root `CLAUDE.md` holds the principles; this
file holds their detail for code that loads pages, shapes output or keeps
time. Map of the modules: `docs/ARCHITECTURE.md`.

## Page content may shape a request only in these six cases

Principle 5: page content never chooses a URL to visit, a tool to call or an
outcome. These six exceptions are approved, each with exactly these limits.

1. **19.A's live site search** is the only live request a page's content
   shapes. It runs only when the caller's pages show fewer than two kinds of
   way; at most two per run (the heading, then, only when that finds
   nothing, the name the site's navigation gives the page when it differs,
   else the heading in quotation marks; #138); a GET form whose action
   passes the allowlist and is on the tested page's host (every redirect
   hop checked); each recorded as its own HAR. After each search, while
   fewer than two kinds are found, the first pages its results list (at
   most 5 a run, on the tested page's host, pages only) are checked as the
   suggested pages below are: the one case where the search's results
   choose pages to load (#138, Abby 2026-11-22).
2. **19.A's suggested pages**: the site map a page read links to, the tested
   page's parent (one level up, from its own address), up to 2 child pages
   (links on it under its own directory; none for a page at the site root),
   its previous and next pages (links on it so named, at most 2), up to 3
   other links in its content, and the home page; on the tested page's host;
   at most 10. While fewer than two kinds of way are found, 19.A loads them
   itself, one at a time, and stops at two. Each is loaded exactly as a
   caller's other page is (`pipeline.capture_other`): allowlisted, on the
   tested page's host before and after redirects, its own HAR. One that
   cannot be loaded leaves 19.A at NEEDS REVIEW, never FAIL. No other URL
   found on a page is visited.
3. **19.A's suspected aliases**: while the pages read show fewer than two
   kinds of way, a link on another page the test read whose address differs
   from the tested page's only by a last segment named `index.*` or
   `default.*` (either way round), its scheme or a leading `www.`, on the
   same host, is loaded to see whether it is the tested page under another
   address: at most 3 a run, each loaded exactly as a caller's other page is
   (`pipeline.capture_other`: the allowlist on every hop, the tested page's
   host after redirects, its own HAR, the page cache). It is the same page
   when it ends at the tested page's address, or when its document is the
   tested page's byte for byte and the page as drawn shares at least 90% of
   its text (#138; an identical document alone is not enough: an
   application can send one document for every address; #134 step 26); any
   other one is "not verified" (NEEDS REVIEW), never a FAIL or a match. It
   is read only for its text; its links are never read or followed. A link that differs only
   by its query string is not an alias.
4. **A key combination that page text names** as a way to stop moving
   content or audio (2.A-2.C J2): on a fresh replay, modifiers plus one key,
   never one the browser itself uses, one combination per run, and only to
   confirm what J2 found.
5. **Scripts that recorded scripts name by a string literal** (code the page
   loads when it is used, so that a replay can run the page's handlers):
   relative to the script's own address, same host as that script,
   allowlisted, a script, at most 300 files, 10 MB each and 24 MB in all, 5
   levels deep, 40 s, each saved in the recording's chunk store. One not
   saved is reported, and a test that presses keys or types cannot PASS
   while the recording lacks code the page loads (guard GU, in the spec's
   front matter `guards:`).
6. **A frame opened as a page of its own** (TT 12.D "test in new tab", for
   the tests that use ANDI): on a replay, never live, the address of a frame
   the tested page's replay showed (so its recording holds it), at most 10 a
   run (`NavigationGuard.allow_frame_page`); no other address.

## Pages and URLs

- A page that is never tested (not allowed, cannot load, bad input) is a
  tool error (`ToolError`, isError), not a finding, and leaves no run
  folder.
- **Other pages of the same site** (`other_pages`; 9.A-9.C, 19.A) come only
  from the caller: allowlisted, on the tested page's host before and after
  redirects, each its own HAR. Never follow the tested page's links. A
  run of 9.A-9.C with neither `other_pages` nor `no_other_pages=true` is
  refused before anything loads, so the agent asks the user first
  (`tools/run_tt_tests._check_other_pages`; after a run: #154).
- **Names for people.** Results, explanations and report reads give each
  test a `name` (`catalog.display_name`: "Keyboard access (WCAG 2.1.1
  Keyboard; TT 4.A)"); agents are told to lead with it, not the ID.
- **Frozen pages** (`FROZEN_PAGES_DIR`, evals only) are a server setting,
  never a tool input. In "replay" mode every page a run loads comes from the
  folder, and a URL with no recording is a tool error, never fetched live.
  In "tested_frozen" mode (the agent eval) the tested page must come from
  the folder, and other pages of its host (other pages, 19.A's search) load
  live under the usual rules.

## Browser

- `andi.install_andi_routes` serves ANDI from `third_party/` and aborts any
  other www.ssa.gov request.
- Content-Security-Policy is bypassed in every browser context
  (`BYPASS_CSP`, default on) so ANDI's injected script runs; the report
  records it (`run_settings`). Any other CSP change needs explicit approval.
- Replays of pages with cross-site iframes run in full Chromium, never the
  headless shell (`docs/solutions/full-chromium-iframes.md`).

## Tools and their output

- One tool per file in `tools/`, registered in `tools/__init__.py`. Tools are
  broad and outcome-based, not one per step:
  - `tobi_run_tt_tests`: run tests on a page.
  - `tobi_run_status`: wait for a run its call left running; with no
    `job_id`, list the work left across the session's runs; with
    `finish=true`, also make the follow-up calls the server may make itself.
  - `tobi_cancel_run`: stop one of the caller's own runs (queued or
    running), on the user's word or for a duplicate; nothing is kept. The
    server's admin cancels anyone's from inside the container
    (`admin.py`, `tobi508-admin`), never through MCP.
  - `tobi_answer_questions`: record the calling agent's answers to open
    questions, when the server has no judge model of its own or its judge
    could not be reached (`pipeline._judge_phase` leaves them open).
  - `tobi_explain`: a test's explanation, or a run's full findings, from
    `explain.py`, which the `explain` prompt shares (agents cannot call
    prompts and seldom read resources; results keep one line per finding).
    After a run it is brief by default: results, summaries and fix links
    first, only the places that are not PASS (`Instance.outcome`), the rest
    counted; `detail="full"` adds every place, TT text and rule trail.
  - `tobi_read_report`: read an SCRT or pre-SCRT file and list what changed
    against another.
- Tool inputs are Pydantic-validated with precise descriptions. The
  implemented-test list in `tobi_run_tt_tests`' description and its default
  come from `checks.REGISTRY`; never hardcode them. A description says what
  the tool is for and what it returns; step-by-step instructions for the
  agent go in the result's `next_step` and to-do list.
- Planned (`docs/plans/2026-11-02-scrt-io.md`): `verify_fix` (an option on
  `tobi_run_tt_tests` that takes a saved report), merging a partial SCRT
  file, TT review and export, and fix advice for a read report (its own
  optional tool). Other guidance goes in resources or a prompt, not a tool.
- **Keep tool output small.**
  - The full report is a `run://` resource (`report_uri`), never inline.
  - Evidence several questions share goes once in `shared_inputs`
    (questions name their keys in `shared`); a question and rubric several
    questions share go once in `question_texts`.
  - A long summary or row list is shortened (the report keeps it whole).
  - Screenshots and files in a question are `run://` links, never run-folder
    paths. The pictures a result's open questions name are also attached to
    it, downscaled and capped (`inline.py`): without them an agent answered a
    visual question wrongly and sure.

## Hosting, time and concurrency

- Hosted deployment is the target; stdio is fine for now. Build nothing that
  only works locally: evidence must be reachable without the server's file
  paths, and run state is short-lived (results belong in the user's
  codebase: the client reads `pre_scrt_uri` and `report_uri` and saves both
  before `expires_at`).
- One tool call returns within `CALL_WAIT_S` (default 45 s, under common MCP
  client timeouts and HTTP proxies). A run not done by then goes on as a job
  (`jobs.py`) and `tobi_run_status` waits for it again; each still-running
  result carries a progress line in three parts (reading the page, testing,
  finishing), done of total with a percentage that covers only the part it
  names (`progress.py`).
- By default a run is not held to a time limit (`NO_TIME_LIMIT_DEFAULT`): it
  tests the whole page and stops only at `MAX_RUN_S` (default 1800 s),
  because agents never put the `no_time_limit` choice to the user.
- A caller passing `no_time_limit=false` gets `RUN_LIMIT_S` (default 600 s),
  plus `OTHER_PAGE_S` (default 20 s) for each other page it names, plus
  `MOVING_ALLOWANCE_S` (default 45 s) once pass T finds content that keeps
  changing by itself. `no_time_limit=true` also lifts the media store's
  caps.
- Each test has its own time for collecting its evidence: its budget
  (`TEST_BUDGETS_S`, defaults in `config.TEST_BUDGETS_DEFAULT`) or
  `TEST_BUDGET_SHARE` (half) of what is left of the run, whichever is
  smaller. Past it the test is NEEDS REVIEW, not performed ("ran out of its
  time"), and the tests after it still run; `ctx.out_of_time()` stops work a
  little before, without calling it the run's limit. Tests run cheapest
  budget first, after the tests whose replays they read
  (`checks.base.AFTER`). Each report records every test's budget, time
  given, seconds taken and whether it ran out (`test_times`). Work that
  never yields (numpy counting) runs off the event loop
  (`asyncio.to_thread`), or a budget cannot stop it.
- At most `MAX_CONCURRENT_RUNS` (default 2) runs use a browser at once; a
  queued run's limit starts when it starts.

## Checks

Adding a TT test: follow the steps at the top of `checks/base.py`. Reuse the
walk, its extras and existing collectors; put shared logic where the next
check can call it.
