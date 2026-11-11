# A-surface review: tools, models, inline, jobs, config, app, resources

## Overview

The surface is tidy in structure (one tool per file, registry-driven description, redaction on errors, run ownership on
resources) but expensive for the consumer agent. Measured with `mcp.list_tools()`: the five tools cost about 48k characters
(roughly 12k tokens) before any call, and 31k of those are output schemas that duplicate what the result text already says.
Every result then repeats the same guidance 3-4 times (`next_step`, `todo` in the JSON, `todo` again as a trailing block,
`work`/`remaining`/`waiting_on`, plus tool description and server instructions) and carries project history
("the fourth development run's agent...") that an agent cannot act on. The most serious defect is in jobs.py: jobs have no owner,
so under `AUTH=oidc` one user can list another user's running jobs and then collect their finished result. There is also a
read-modify-write race on `report.json` between answer calls, follow-up starts and the judge. No false-PASS path was found
inside these files; the one gate weakness is that any calling agent can label its own answer `decided_by: human`. Every config
setting is read somewhere (grepped each name); none is dead by name.

Measured sizes (chars): tool description run_tt_tests 4262, run_status 778, answer_questions 833, read_report 483, explain 685;
input schemas 2470 / 757 / 5165 / 860 / 585; output schemas 9296 / 11197 / 7818 / 3141 / 119; server instructions 2282.
Fixed boilerplate per result: `next_step` about 960, `todo` about 640 (sent twice), disclaimer + untrusted notice + save hint about 370.

---

### A-01 Jobs have no owner: other users' running jobs and finished results are reachable (hosted mode)
- Severity: P1
- Kind: security
- Where: src/tobi508/jobs.py:57-58,98-99 (`_JOBS`, `get`); src/tobi508/tools/run_status.py:62-67 and 75-86; src/tobi508/pipeline.py:1572-1585 (`outstanding`)
- What: `_JOBS` is one process-wide dict and `Job` stores no caller. With `AUTH=oidc`, `tobi_run_status()` with no job_id lists every job still running, for all users, as `{job_id, target, status}`. A second user can then call `tobi_run_status(job_id=...)` and `jobs.wait` returns the other user's `RunResult` (findings, open questions, page text, report_uri) once it finishes. The run folder resources are protected by `may_open`, but the result JSON is not. Finished jobs are filtered only because `outstanding` happens to call `RunRecorder.open`, which checks ownership; running ones are not.
- Evidence: read `jobs.start`/`get`/`wait` (no `caller()` anywhere); `outstanding()` appends to `running` before any ownership check; `RunRecorder.open` is the only guard and is skipped for `j.task` not done. grep "owner" in jobs.py: no hits.
- Fix: store `access.caller()` sub on `Job` at `start`; make `get`, `all_jobs` (and `running`) return only jobs whose owner equals the current caller (or any job when caller is None).
- Confidence: confirmed (by reading; not exercised with a real token)

### A-02 Output schemas ship about 31k characters per session and duplicate the result text
- Severity: P1
- Kind: tokens
- Where: src/tobi508/tools/run_status.py:36-37 (`-> RunResult | RunPending | Outstanding`, 11197 chars), run_tt_tests.py:196 (9296), answer_questions.py (7818), read_report.py (3141); src/tobi508/inline.py:226-251 (`structured_content=...`)
- What: FastMCP derives `outputSchema` from the return annotations. Each schema carries every field description (WORK_DESCRIPTION, SHARED_DESC, the follow_up_calls paragraph twice across RunResult and AnswerResult, and so on). Clients put tool lists in context, so about 8k tokens go on schemas the agent cannot use. `with_pictures` also sends the whole result twice per call: as the JSON text block and again as `structured_content`.
- Evidence: ran `mcp.list_tools()` and measured per-tool inputSchema/outputSchema/description lengths (numbers in the overview). Read `with_pictures`: `ToolResult(content=[TextContent(JSON)...], structured_content=data)`.
- Fix: register with `output_schema=None` and return only the text content (no `structured_content`). In-process callers (tests, evals) use `RunResult` objects directly. Check how test_tools.py reads results before dropping it.
- Confidence: confirmed (sizes); likely (that the client forwards both copies to the model; Claude Code mostly reads the text)

### A-03 Every result repeats the same instructions 3-4 times, and carries project history
- Severity: P1
- Kind: tokens
- Where: src/tobi508/pipeline.py:1316-1440 (`next_step`, `FINISH`, `_calls_text`, `todo`); src/tobi508/inline.py:211-251 (the "TO DO" block); src/tobi508/models.py:631-697 (`work`, `remaining`, `waiting_on`, `unconfirmed`, `confirmed`)
- What: one result says "answer the open questions" in `next_step`, again in `todo[0]`, and `todo` is sent twice (inside the JSON, since `model_dump_json(exclude={"report"})` keeps it, and again as the trailing "TO DO" text block). "Call tobi_run_status with finish=true" appears in `next_step` (via `_calls_text`) and in `todo`; "save report_uri" appears in `next_step`, `todo`, `save_hint` and `pre_scrt_uri`'s description; "report NEEDS_REVIEW as needs review" appears in `next_step`, `todo`, the tool description and the explain task. `FINISH` and `_calls_text` embed history an agent cannot use: "the fourth development run's agent ended with questions...", "(the development runs' agents made almost none)". Measured: `next_step` about 960 chars and `todo` about 640 chars (x2) on a trivial result, so 2.2k+ chars (about 550 tokens) of fixed text per call.
- Evidence: ran `pipeline.next_step`/`todo` on a stub report; read `with_pictures` (todo goes into `end` while still in `model_dump_json`).
- Fix: keep one channel. Either `next_step` (short, one sentence on state) or `todo`, and emit it once; exclude `todo` from the JSON dump if the trailing block is kept. Remove run-history parentheticals from `FINISH`/`_calls_text`/`looks`.
- Confidence: confirmed

### A-04 Race: report.json is read, awaited on, then written back, with no per-run lock
- Severity: P2
- Kind: bug
- Where: src/tobi508/pipeline.py:1449-1520 (`answer_questions`), 1536-1569 (`take_follow_ups`, `record_follow_up`); called from src/tobi508/tools/answer_questions.py:90 and run_status.py:113-117; the judge calls the same pipeline
- What: `answer_questions` loads `report.json`, records answers, then awaits browser replays (seconds) and writes the whole report back. If two answer calls overlap (two subagents answering batches, which the run_tt_tests description recommends), or `tobi_run_status(finish=true)` runs meanwhile, the later write drops the other's answers or restores follow-up calls that `take_follow_ups` had removed, so the same follow-up run can start twice. Lost answers fail safe (the question reopens), but the duplicate follow-up run wastes minutes and a browser slot.
- Evidence: grep "Lock" in pipeline.py/jobs.py/judgment.py: none. Read the three functions; there is an `await` (resume loop) between read and write.
- Fix: one `asyncio.Lock` per run_id (dict in jobs.py or pipeline.py) around load-modify-write in `answer_questions`, `take_follow_ups` and `record_follow_up`.
- Confidence: likely

### A-05 `decided_by: "human"` is self-asserted by the calling agent and skips the picture gate
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/tools/answer_questions.py:48-52 (description invites it); src/tobi508/judgment.py:103-105,175-180 (`_picture_problem` and `viewed` apply only to `DecidedBy.MODEL`); src/tobi508/models.py:392
- What: the tool tells the agent that 'human' "records a person's override, which wins". Nothing checks that a person said it; only the `answered_by` field is forced to "client". An agent that skipped looking at a picture (the failure the `seen` gate was added for) can set `decided_by: human` and send no `seen`. The gate is skipped and `not_viewed` stays False. How much a "human" answer then counts is decided in specs, but any spec that treats human answers as authoritative gains a bypass. Only the server judge's answers are locked against it.
- Evidence: read `_picture_problem` (returns None unless decided_by is MODEL) and `record_answers`. The tool wrapper sets `answered_by="client"` only.
- Fix: apply the `seen`/`picture_error` rule to every answer with `answered_by == "client"` regardless of `decided_by`, and word the description so an agent only uses 'human' when relaying a user's explicit words (quote them in `rationale`).
- Confidence: likely

### A-06 tobi_run_tt_tests description is about 4.3k characters and mixes history, deployment trivia and advice the agent cannot act on
- Severity: P2
- Kind: tokens
- Where: src/tobi508/tools/run_tt_tests.py:34-101
- What: loaded in every session. It says the same thing the next result's `next_step` says (answer questions, call run_status, never start again; the last appears in the description, in `RunPending.next_step` and in server instructions). It points to "the explain prompt" although CLAUDE.md records that agents cannot call prompts; `tobi_explain` exists. It states the server's concurrency ("runs N pages at once"), an exact timeout paragraph with five numbers, and an example about 4.B's follow-up question. The `limit_text` branch embeds a plan to "ask the user whether to call again with no_time_limit", which CLAUDE.md says agents never do. The implemented-tests list also appears in the server instructions and the input schema default (the `tests` default serializes every test id), so it is paid for three times.
- Evidence: measured description length 4262 chars; read the f-string.
- Fix: cut to the essentials (what it does, the allowlist, `other_pages` is caller-chosen, statuses and the poll loop, disclaimer, untrusted data) at about 1.2k chars; the rest is already in `next_step`. Drop the list from the `tests` default or the instructions.
- Confidence: confirmed

### A-07 Answer input schema is 5.1k characters and its description restates the model fields
- Severity: P2
- Kind: tokens
- Where: src/tobi508/tools/answer_questions.py:40-69; src/tobi508/models.py:322-424 (`ChoiceAnswer`, `Answer`)
- What: the long `answers` description re-lists choice/j1/j2 sub-fields that the Answer, ChoiceAnswer, J1Answer and J2Answer schemas already describe field by field. The agent-visible schema also exposes server-owned fields (`answered_by`, `not_viewed`, "Set by the server... Do not set it") and the unused-by-most `elements`, `value`, `quote`, `presses`, `duration_ms`. The agent must also write both `rationale` (required, min 1) and `choice.reasons`, two justification texts per answer; `explain._waiting_for_person` uses one or the other.
- Evidence: measured 5165 chars; grep `not_viewed` shows it is only set in judgment.py:179; `answered_by` is overwritten by the tool.
- Fix: put `answered_by`/`not_viewed` on a server-side subclass (`Answer` for the wire keeps only agent fields), shorten the tool description to the rules the schema cannot express, and drop `choice.reasons` or `rationale`.
- Confidence: confirmed

### A-08 Pictures already attached are re-sent whenever their question comes back, and encoding blocks the event loop
- Severity: P2
- Kind: time
- Where: src/tobi508/inline.py:99-155 (`pictures`), 158-196 (`attached`, `_note_attached`)
- What: `pictures()` dedupes only within one result. `attached()` records which pictures went out but is used only to hold answers to them, never to skip re-sending. A rejected answer, or the `more_questions` paging, brings the same questions back, so the same up to 8 pictures (up to about 20k tokens, 1.5 MB) are attached again. Separately, `_encode` (PIL open, resize, `optimize=True` PNG, possible JPEG) runs synchronously on the event loop for up to 8 images while Playwright runs of other jobs share that loop, stalling them and their progress reports.
- Evidence: read `pictures` (`seen` is local) and `with_pictures` (never calls `attached` to filter). No `to_thread`/executor in inline.py.
- Fix: skip links in `attached(run_dir)` (the caption can say "already sent earlier") and run `pictures()` via `asyncio.to_thread` from the async tool functions.
- Confidence: likely (re-send); likely (blocking)

### A-09 tobi_run_status is annotated read-only/idempotent/closed-world but can start runs and write files
- Severity: P2
- Kind: design
- Where: src/tobi508/tools/run_status.py:30-34; run_status.py:62-66, 109-122
- What: with `finish=true` it starts new test runs (live page loads, `openWorldHint` should be true) and rewrites `report.json` (`take_follow_ups`, `record_follow_up`). Clients may auto-approve `readOnlyHint` tools and retry `idempotentHint` ones. Even without `finish`, `with_pictures` writes `attached-pictures.json`. In the same vein, `tobi_answer_questions` replays pages in a browser but is `openWorldHint: False` (acceptable as the page is a recording), and its browser is not counted by `max_concurrent_runs`, so answers during busy runs can exceed the CPU budget the config comment warns about.
- Evidence: read the annotations and `_start_follow_ups`.
- Fix: set `readOnlyHint=False`, `idempotentHint=False`, `openWorldHint=True` for tobi_run_status (or split `finish` into its own tool); have `answer_questions` take a `jobs._slots` slot around its browser use.
- Confidence: confirmed (annotations); likely (slot bypass)

### A-10 tobi_explain with a run_id has no size cap
- Severity: P2
- Kind: tokens
- Where: src/tobi508/explain.py:106-132, 177-237
- What: with a run and no `about`, it emits for every test the full summary, rationale, every instance description and the rule trail. `FULL_TEXT_LIMIT` only limits the TT text. A FAIL on a large page lists every instance (the model has no cap here), which can pass the roughly 50 KB / 25k-token point where Claude Code saves the result to a file (documented at pipeline.py:497). The result is unstructured `str`, so nothing downstream shortens it.
- Evidence: read `_finding_section`: `lines += [f"- {i.description}" for i in f.instances]` and `f.rationale` unbounded.
- Fix: cap instances (for example 20 with "N more in report_uri") and the whole text, ordered by outcome so FAILs survive the cut.
- Confidence: likely

### A-11 Results serialize defaults and nulls, and carry fields that say the same thing
- Severity: P2
- Kind: tokens
- Where: src/tobi508/models.py:559-584 (`FindingView`), 631-697 (`RunResult`), 700-715 (`RunPending`), inline.py:219,236 (`model_dump_json` without `exclude_none`/`exclude_defaults`)
- What: per finding the JSON always contains `note: null`, `confirmed: null` (or true), `unconfirmed: 0`, `waiting_on: []`. `confirmed` is true for every FAIL and null otherwise, so it only restates `outcome`; `unconfirmed` is the same count as the "N open question(s)" entry of `waiting_on`. `wcag_sc` and `test_name` repeat per finding the TT catalogue text. In `RunResult`: `work` and `remaining` and `next_step` and `todo` all describe the same state; `tests` repeats the finding ids; `evidence` lists every `evidence/*.json` URI (about 25 x 60 chars) when `report_uri` already reaches them; `walk` is rarely actionable; `final_url`, `errors: []`, `more_questions: 0`, `page_text: []`, `question_texts: {}`, `shared_inputs: {}`, `follow_up_calls: []` are present even when empty. `RunPending` has `seconds_waiting`, `seconds_running` and `progress`, the last already stating the elapsed time, plus a `disclaimer` on a message that holds no finding. `Finding.confidence` is never set anywhere in src (grep): dead.
- Evidence: read models; grep `confidence=`/`.confidence` outside models.py returns nothing.
- Fix: dump with `exclude_none=True, exclude_defaults=True` (disclaimer kept explicitly per principle 1), drop `confirmed`/`unconfirmed`/`evidence`/`walk`/the seconds fields, and remove `Finding.confidence`.
- Confidence: confirmed

### A-12 Boilerplate strings repeated in every result
- Severity: P3
- Kind: tokens
- Where: src/tobi508/models.py:604-612 (`UNTRUSTED_NOTICE`, `SAVE_HINT`, `SHARED_DESC`), result classes `RunResult`, `AnswerResult`, `Outstanding`, `RunPending`, `ReadResult` (read_report.py:78-92)
- What: `disclaimer` is required by principle 1, but the `untrusted_content_notice` (141 chars) and `save_hint` (117 chars) are fixed text, repeated in every result and already stated in the tool description, server instructions and `todo`. `ReadResult` carries `tester_named` and `tt_number_given`, flags a reader agent has no use for.
- Evidence: read.
- Fix: keep one copy of the untrusted notice (instructions or per-result), fold the save hint into the single `next_step` line, remove the two ReadResult flags unless a spec uses them.
- Confidence: confirmed

### A-13 Job holds the full RunResult (with the Report) in memory for 24 hours
- Severity: P3
- Kind: time
- Where: src/tobi508/jobs.py:78-95, config.py:211 (`job_keep_s=86400`)
- What: `Job.task` keeps the finished `RunResult`, whose excluded `report` is the whole `Report` (questions with inputs, answers, findings). Every finished job holds it until `job_keep_s`. Meanwhile `outstanding()` and `take_follow_ups()` only use `res.run_id` and then re-read and re-validate `report.json` from disk for every kept job on each `tobi_run_status()` call (synchronous, on the event loop).
- Evidence: read both functions (`res = j.task.result()` then `RunRecorder.open` and `model_validate_json`).
- Fix: store `run_id` on the Job when the run ends and let the task result be dropped after first delivery; cache or limit the report re-reads.
- Confidence: likely

### A-14 A follow-up call with no tests is silently dropped after being removed from the report
- Severity: P3
- Kind: gap
- Where: src/tobi508/tools/run_status.py:97-101 vs pipeline.py:1553-1560
- What: `take_follow_ups` deletes the server-makeable calls from `report.follow_up_calls` before `_start_follow_ups` runs. If a call has an empty `tests`, `_start_follow_ups` does `continue` without recording it, so it vanishes from both lists. A `TestId(t)` ValueError on a bad id would likewise abort the loop after other calls were already removed.
- Evidence: read both functions.
- Fix: filter invalid calls in `take_follow_ups` before removal, or record them under `follow_ups_made` with a reason.
- Confidence: likely (data comes from the server's own checks, so rare)

### A-15 Progress callbacks are awaited inside the run with no timeout
- Severity: P3
- Kind: bug
- Where: src/tobi508/jobs.py:45-52
- What: `Job.progress` awaits each waiter's `report_progress` inside the run's own coroutine (the pipeline's `say`). A client whose stream stalls without erroring blocks the pipeline at that step. Only exceptions remove a waiter.
- Evidence: read; not reproduced.
- Fix: wrap in `asyncio.wait_for(w(...), 2)` and drop the waiter on timeout, or fire progress as a separate task.
- Confidence: speculative

### A-16 Config and surface wording for run limits is stale or misleading
- Severity: P3
- Kind: gap
- Where: src/tobi508/tools/run_tt_tests.py:166-185 (`other_pages` description); config.py:122-140
- What: the field says "Up to 5 other pages (up to 50 with no_time_limit=true)", and "each page adds 20 s to the run limit", but with the default (`no_time_limit_default=True`) the server accepts up to 50 and applies no limit, so the agent is told to stay at 5 when it need not. The `no_time_limit` description also tells the agent to ask the user, which CLAUDE.md says never happens. `headless` defaults to False and `browser_channel` to "chrome", so a hosted container needs both overridden; the hosted-first rule suggests container-safe defaults or a startup failure when `mcp_transport=streamable-http` and no display exists.
- Evidence: read `check_other_pages` (pipeline.py:289-310) and config defaults.
- Fix: describe the cap as "5 when no_time_limit=false", and drop the "ask the user" wording.
- Confidence: confirmed (wording); speculative (container defaults)

### A-17 Follow-up call state is a loose dict with string keys, parsed in five places
- Severity: P3
- Kind: design
- Where: src/tobi508/models.py:560-575 (`_waiting_on`), 757 (`Remaining.of`), src/tobi508/explain.py:116, run_status.py:97-103, pipeline.py `server_may_make` and `follow_ups`; also `Report.reveal`, `Report.judge`, `Versions.run_settings` as `dict[str, Any]`
- What: `[str(t) for t in c.get("tests") or []]` is written three times, and `url`/`tests`/`other_pages`/`no_time_limit` keys are read by name across modules. A rename or a new key is a silent miss. RunResult and AnswerResult also copy about 14 identical fields (and their descriptions) instead of sharing a base.
- Evidence: grep `"tests") or`.
- Fix: a `FollowUpCall` Pydantic model with a `tests_ids()` and `server_may_make` property, and a `ResultBase` for the shared result fields (which also shrinks the output schemas).
- Confidence: confirmed

### A-18 Run resource serves any file in the run folder whole, including HARs and media
- Severity: P3
- Kind: tokens
- Where: src/tobi508/resources/runs.py:49-66
- What: any file under the run (HAR recordings of tens of MB, the chunk store, `steps.jsonl`, `owner`) is read fully into memory and returned as text or base64 blob. No size cap and no allowlist of evidence file types. `read_report.load` also reads a run:// link whole. Ownership is enforced; this is memory and token cost, and a way for an agent to pull a 90 MB blob into its context.
- Evidence: read `run_evidence`; `mimetypes.guess_type("x.har")` is None so it falls to `read_bytes`.
- Fix: refuse or truncate beyond a limit (for example 2 MB), and refuse `owner`, `.har` and chunk-store paths unless asked by exact name.
- Confidence: likely

### A-19 prompts/explain.py duplicates the tobi_explain tool and is advertised to agents
- Severity: P3
- Kind: dead-code
- Where: src/tobi508/prompts/explain.py, src/tobi508/tools/run_tt_tests.py:68 ("the explain prompt"), src/tobi508/app.py:55-56
- What: CLAUDE.md records that agents cannot call prompts; the tool replaced it. The prompt remains for users and is mentioned in the tool description and server instructions, costing tokens for an interface agents do not use. Its two fields repeat the tool's field descriptions.
- Evidence: read.
- Fix: keep the prompt for humans if wanted, but drop all mentions from agent-facing text.
- Confidence: confirmed

## Unverified leads

- jobs.wait: if a task is cancelled (server shutdown), `task.result()` raises `CancelledError`, which the tools' `except Exception` does not catch; the call is cancelled instead of returning an error.
- app.http_options adds `AuditMiddleware` every time it is called; a second call (tests, reload) would double-audit.
- routes `/version` is outside the OIDC gate (FastMCP custom routes); low-value information disclosure.
- config: list-typed settings (`allowed_domains`, `egress_ports`) need JSON in env vars while `judge_types` is comma-separated; a user writing `ALLOWED_DOMAINS=.gov,.mil` gets a startup error, not a silent default (not verified).
- read_report is a sync tool parsing up to 40M characters; whether FastMCP runs it in a thread (otherwise it blocks the loop) was not checked.
- with_pictures counts image tiles as pictures in its "The N pictures" note (n = blocks / 2), over-counting tall screenshots.
