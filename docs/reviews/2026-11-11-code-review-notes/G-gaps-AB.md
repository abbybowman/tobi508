# G review: gaps left by the A and B notes (tools, models, jobs, config, app, routes, pipeline, judgment, apijudge)

## Overview

Every assigned file was read line by line (pipeline.py 1-1662, apijudge.py 1-906, models.py 1-975, the rest whole). I found
no new false-PASS path in these files: a time limit, a raising collect or a walk failure all end as NEEDS_REVIEW with the
"could not be performed" note (`_evaluate` lines 775-783, `Finding.not_performed`), and `Finding` defaults to NEEDS_REVIEW.
`fit` never drops an open question without `more_questions` saying so, but it can return an over-size result with no flag
(G-11). The new problems are cost and plumbing: the save instruction cannot be followed with the real report sizes (G-01),
the server judge sends one picture once per question (G-02), `tobi_answer_questions` is the one tool that is not under
`CALL_WAIT_S` (G-03), the time-limit note is wrong for the default no-limit mode (G-04), and the resume path builds a
different `RunContext` than the run (G-05). Follow-up runs that fail are invisible and user-choice follow-ups can never clear
(G-06, G-07). A-16's "container defaults" half is refuted (G-14). Counts: P1 3, P2 6, P3 6.

| file | lines already covered by A/B findings | lines read |
|---|---|---|
| tools/run_tt_tests.py | 34-101 (A-06), 166-185 (A-16) | 1-201 |
| tools/run_status.py | 30-37 (A-02, A-09), 62-86 (A-01), 97-122 (A-09, A-14) | 1-123 |
| tools/answer_questions.py | 40-69 (A-07), 48-52 (A-05, B-09), whole (A-09 annotations) | 1-96 |
| tools/explain.py | none (A-10 covers explain.py the module) | 1-58 |
| tools/read_report.py | 78-92 (A-12) | 1-236 |
| tools/__init__.py | none | 1-32 |
| models.py | 322-424 (A-07), 392 (A-05), 559-584 / 604-612 / 631-715 (A-11, A-12), 757 (A-17) | 1-975 |
| jobs.py | 45-52 (A-15), 57-58 / 98-99 (A-01), 78-95 (A-13, B-04) | 1-164 |
| config.py | 122-140 (A-16), 211 (A-13) | 1-238 |
| app.py | leads only (A-19 55-56) | 1-145 |
| routes.py | lead only | 1-27 |
| pipeline.py | 439-464, 894-907 (B-11); 573-650 (B-18); 748-756 (B-16); 759-806 (B-06); 773-783 (B-13); 894-895, 1104-1108, 1193-1203 (B-07); 939-1032 (B-08); 1208-1209 (B-14); 1214-1215 (B-04); 1316-1440 (A-03, B-12); 1434-1597 (A-04, B-03, B-18); 1553-1560 (A-14) | 1-1662 (most attention on 1-760, 823-1260) |
| judgment.py | 36-98 (B-14), 101-111 / 175-195 (A-05, B-09) | 1-195 |
| apijudge.py | 303-318, 254-260 (B-17); 380-416 (B-01); 478-527 (B-02); 547-564, 675-727, 766-815 (B-05); 622-639 (B-10); 808 (B-18) | 1-906 |
| judge_prompt.md | none | 1-12 |

Checked and found fine (no finding): `record_answers` validates question id, answer kind, choice membership and the picture rule,
and the consumers re-check `element` ranges (`t4a._valid_alt`, `t4b._target`, `t4b._alt_ok`, `t5f.apply_j0`); a later model
answer cannot replace a human one (`current_answer`) nor a server one (`record_answers` 151-161); `judge_prompt.md` rule 5
tells the judge to answer unsure when evidence does not settle it and rule 2 treats tag contents and picture text as data
(the tag-closing hole is B-02, not the wording); config defaults match CLAUDE.md (CALL_WAIT_S 45, MAX_RUN_S 1800, RUN_LIMIT_S
600, OTHER_PAGE_S 20, MOVING_ALLOWANCE_S 45, MAX_CONCURRENT_RUNS 2, BYPASS_CSP on, .gov/.mil).

---

### G-01 The "save report_uri and pre_scrt_uri" instruction cannot be followed at real report sizes, and the report triples question inputs
- Severity: P1
- Kind: tokens
- Where: src/tobi508/models.py:709-712 (`SAVE_HINT`), 424-427 (`RecordedAnswer.question`), 579-585 (`Report.questions` / `open_questions` / `answers`); src/tobi508/pipeline.py:1426 (todo: "Save report_uri and pre_scrt_uri before expires_at"), 1338
- What: every result tells the consumer agent to read both resources and save them in the user's repository. The only way a client does that is to pull the file through its own context (read the resource, then write it out). On archived real runs the report is 430-620 KB and the pre-SCRT file 2.5 MB. That is 100-150k tokens for the report and several hundred thousand for the pre-SCRT, over Claude Code's 25k-token MCP result limit that pipeline.py:497-505 itself documents, so the client truncates or saves a preview and the agent saves a cut file without knowing it. About 35% of the report is the same question inputs stored three times: `questions`, `open_questions` (identical before any answer) and `answers[].question` (a full copy per answer, again per re-answer).
- Evidence: measured `evals/judging/round2/results/arm-a-g1-1/runs/20261108T013747Z-67aa10`: report.json 618,788 bytes, pre-scrt.json 2,529,153 bytes; `questions` and `open_questions` 192,684 chars each; in `arm-a-pair2-2/.../20261108T032546Z-b57eba`, `questions` 150,624 plus `answers` 173,633 chars (53 answers, each embedding its question). Read `record_answers` (appends `RecordedAnswer(question=q, ...)`).
- Fix: store `RecordedAnswer.question_id` (and the question's id list), keep `open_questions` as ids, and give the client a small saved form (findings, answers, versions) while the evidence stays a resource; or offer a server-side save (hosted download link) instead of asking the agent to relay megabytes. Say in `save_hint` which file is large.
- Confidence: confirmed (sizes, duplication); likely (that clients cannot relay the full files; not tried with a real client)

### G-02 The server judge sends the same picture once per question, and slices and encodes pictures on the event loop
- Severity: P1
- Kind: time
- Where: src/tobi508/apijudge.py:403-416 (`pictures_of`), 567-597 (`build_requests`), 547-564 (`split`), 388-400 (`_slices`)
- What: `pictures_of(q)` is called per question and returns that question's slices, with no sharing across questions. Several questions of one test name the same screenshot, so one request carries it again for each. The copies count against `MAX_PICTURES` (40) and `MAX_BYTES` (24 MB), which forces more requests (each repeating the shared block), and every copy is billed as image tokens. All of it (PIL decode, crop, PNG re-encode, base64) is synchronous, runs on the event loop and is done again for each missing question in `again(q)`, stalling every other job's browser callbacks and progress.
- Evidence: in the archived reports one screenshot is named by up to 19 questions (`arm-a-pair4-2`: 4 links, 18 duplicate uses; `arm-a-pair2-2` and `arm-a-g1-1`: 55 links, 36 duplicates, max 14; `arm-a-pair1-2`: 41 links, 53 duplicates, max 18). Ran `build_requests(None, {}, tmp, "focus", 19 questions naming one 800x600 PNG)`: 1 request with 19 pictures, 52,953 picture bytes (19 copies).
- Fix: collect pictures per request by link (one attachment per link, questions point to its number in the listing), slice once per link per run (cache in a dict), and run `build_requests` through `asyncio.to_thread`.
- Confidence: confirmed

### G-03 tobi_answer_questions is not under CALL_WAIT_S and has no run limit: one call can replay pages for 10-30 minutes
- Severity: P1
- Kind: bug
- Where: src/tobi508/tools/answer_questions.py:88-95; src/tobi508/pipeline.py:1450-1474 (`resume` loop, no `_bounded`), 1458 (`_soft_deadline` per call)
- What: CLAUDE.md says one tool call returns within `CALL_WAIT_S` and a longer piece goes on as a job. `tobi_run_tt_tests` does that; `tobi_answer_questions` awaits `answer_pipeline` directly. Applying an answer replays the page (4.A/4.B proofs, 5.F J0 re-runs, 4.C) per answer, one check after another, with only the checks' own soft deadline (`run_limit_s` 600 s, or `max_run_s` 1800 s for a no-limit run, starting fresh at every call) and no hard `_bounded`. A client that times out at 60 s drops the call, the work goes on in the server, the result is lost, and the agent re-sends the same answers while the first call still writes report.json (A-04 race). The server judge makes this call too (B-18), so the judge phase inherits it.
- Evidence: read `answer_questions.py` (no `jobs.start`) and `pipeline.answer_questions` (`await REGISTRY[t].resume(...)` with no timeout). Not measured: how long a resume takes on a large page.
- Fix: run the answer pipeline as a job like a run (same `jobs.wait` with `call_wait_s`, result via `tobi_run_status(job_id)`), and wrap each `resume` in `_bounded` with a hard limit that adds the "not finished" error to the report.
- Confidence: likely (by reading; replay time not measured)

### G-04 TIME_NOTE tells a default (no-limit) run it hit "600 s" and to rerun with no_time_limit=true
- Severity: P2
- Kind: bug
- Where: src/tobi508/pipeline.py:86-92 (`TIME_NOTE`), 1187-1192
- What: the note is formatted with `_limit(settings, len(others)) + allowance[0]` whatever the mode. By default (`no_time_limit_default` True) the stop is `max_run_s` (1800 s, soft deadline 1790 s). A page that hits it reports "reached its time limit (600 s)" (wrong number) and advises "run again with no_time_limit=true", which it already was. An agent that follows the advice repeats a 30-minute run for the same result.
- Evidence: read; `_soft_deadline` and `hard` use `max_run_s` when `no_time_limit`, `TIME_NOTE.format` does not.
- Fix: two wordings: for a no-limit run say "the server's longest run time (N min); test a smaller page or fewer tests"; format with the limit that applied.
- Confidence: confirmed (by reading)

### G-05 The resume path builds a different RunContext: `selected`, `requested_url`, `record_live` and the cache are missing
- Severity: P2
- Kind: bug
- Where: src/tobi508/pipeline.py:1453-1466 (answer path) vs 1047-1057 (run path); consumer src/tobi508/checks/t5f.py:413 (`_shot`), t4f.py:354
- What: `run_tt_tests` sets `ctx.selected`, `ctx.requested_url`, `ctx.record_live`, `ctx.cache[...]`; `answer_questions` creates the context with `_context(...)` and sets only `no_time_limit`, `pages` and `plan`. 5.F's `_shot` returns None unless `ctx.selected` holds 5.F, 5.G or 5.H, so the J0 re-run `rerun_with` called from `resume` takes no pictures, and the 5.F/5.G/5.H questions that follow have no evidence pictures for that attempt. The checks that read `selected` in `collect` work today only because resume does not call those paths; the next check that reads it in `resume` fails the same way, silently.
- Evidence: grep `ctx.selected` in checks (t2a/t2b/t2c `collect`, t4f.py:354, t5f.py:413); read both context builds. Not run end to end.
- Fix: build the context in one function used by both paths and set `selected = frozenset(report.tests)` and `requested_url = report.target` in resume (both are in the report).
- Confidence: confirmed (by reading); likely (the effect on 5.F pictures)

### G-06 A follow-up run that fails or is refused is invisible, and its call is marked "made" for good
- Severity: P2
- Kind: gap
- Where: src/tobi508/pipeline.py:1586-1587 (`outstanding`), 1553-1560 (`take_follow_ups`), 1477-1483 (`made` filter), 1564-1569; src/tobi508/tools/run_status.py:95-115
- What: with `finish=true` the server removes a 19.A follow-up call from the report, starts a job and records it as made. If that run raises (a suggested page not allowed, cannot load, a crash), `outstanding` does `continue` on any job whose task has an exception: the job is not listed under `runs`, `running` or `done`, and the original run no longer lists the call. The next `tobi_run_status()` says "Nothing is left: every run of this session is finished", while the 19.A test is still NEEDS_REVIEW and no one was told the follow-up failed (the error shows only to a caller who also passes that job's `job_id`). Rebuilding the calls in `answer_questions` then drops it again because `c not in made`.
- Evidence: read `outstanding`, `take_follow_ups`, `answer_questions` (`made`); `_start_follow_ups` waits on the tasks but never reads their outcome.
- Fix: in `_start_follow_ups` await the tasks and put each failure (`safe_error`) into `out.started` and into `report.follow_ups_made[...]["error"]`; list failed jobs in `Outstanding` (a `failed` list) and leave a failed call in `follow_up_calls`.
- Confidence: confirmed (by reading)

### G-07 A follow-up call the user declines can never clear, while every result says to repeat until nothing is left
- Severity: P2
- Kind: gap
- Where: src/tobi508/pipeline.py:1477-1483 (`kept`), 1594 (`not report.follow_up_calls`), 1416-1419 and 1305-1313 (`todo`, `FINISH`)
- What: a test left out over a cap (5.D with `no_time_limit`) is a `no_time_limit` follow-up call; `answer_questions` keeps every such call in the report for good (`kept`). `outstanding` counts a run with any follow-up call as not done and `for_the_user` lists it each time. The text sent every call says "repeat until it lists nothing left" and "your work is finished only when tobi_run_status lists nothing left". If the user says no (a 20-minute run), the loop cannot end, and an agent that obeys the text keeps asking or reports "not finished" forever. Running the call separately does not clear it either (it is a new run, nothing links it back).
- Evidence: read; no code removes a `no_time_limit` call except a re-evaluation that no longer skips the test, which `_evaluate(run, report, states)` in the answer path (no `skipped`) cannot produce.
- Fix: let the caller dismiss a user-choice call (a `declined` list in the report written by `tobi_run_status`), and make the finish text say a declined call counts as left for the user, not for the agent.
- Confidence: confirmed (by reading)

### G-08 Non-FAIL summaries are cut to their first sentence, which for 56% of the long NEEDS_REVIEW ones is the generic headline
- Severity: P2
- Kind: gap
- Where: src/tobi508/models.py:614-624 (`_first_sentence`), 664-688 (`FindingView.of`); pipeline.py:1336 and 1326 (agents are told to "relay each finding's summary")
- What: a summary over 400 characters is cut to its first sentence. Checks start NEEDS_REVIEW summaries with `REVIEW_HEAD` ("We could not finish this test, so a person needs to check it.") or, while questions are open, `waiting_head(n)`, and put the reason after it. The result then carries only the headline plus "(More: tobi_explain.)". The agent relays "a person needs to check it" without the reason, or calls `tobi_explain` for every such test (the tokens the cut was meant to save). A long PASS or DNA summary with a caveat is cut the same way. Safe (NEEDS_REVIEW stays NEEDS_REVIEW), but it removes what the user needs to act.
- Evidence: measured on the 216 NEEDS_REVIEW findings in `evals/judging/round2/results/*/runs/*/report.json`: 82 summaries exceed 400 characters; 46 of those cut to `REVIEW_HEAD`/`waiting_head` alone (example 5.D: the "volume slider" sentence is dropped).
- Fix: cut after the headline, not at it: keep headline plus the first reason sentence (up to the 240-character view), or put the reason in the `note`/`waiting_on` line that is always sent.
- Confidence: confirmed

### G-09 Jobs queue without a limit per caller, and the run as a whole has no wall-clock stop
- Severity: P2
- Kind: gap
- Where: src/tobi508/jobs.py:68-92 (`start`, `go`); src/tobi508/tools/run_tt_tests.py:176-190; src/tobi508/pipeline.py:894-912, 1205-1243
- What: (a) `jobs.start` accepts any number of jobs; only `MAX_CONCURRENT_RUNS` run, the rest wait on the semaphore holding a coroutine, and each finished one keeps its `RunResult` and `Report` for `job_keep_s` (A-13). With `AUTH=oidc`, one signed-in caller can queue hundreds of runs (the URL allowlist is the only input check) and starve everyone else's runs. (b) MAX_RUN_S is applied only to some phases through `_bounded` (record, walk, reveal, each collect); browser launch, `measure_display`, `_evaluate`, `scrt.write_for_run` and the judge phase (B-04) are not, and `go()` has no overall `asyncio.wait_for`, so CLAUDE.md's "stops only at MAX_RUN_S" is a sum of phase limits.
- Evidence: read `start`/`go`; grep `wait_for` in jobs.py: none.
- Fix: refuse a start when the caller has N jobs queued or running (store the owner on `Job`, A-01), and wrap `run(...)` in `asyncio.wait_for(..., max_run_s + judge_cap_s)` that records the error.
- Confidence: confirmed (a, by reading); likely (b)

### G-10 A request with no implemented test still launches Chrome and loads the page live
- Severity: P3
- Kind: time
- Where: src/tobi508/pipeline.py:861-935 (`checks` empty is not checked before `launch_browser` and `obtain`)
- What: `tests` may hold any TT id. If none has a check in `REGISTRY`, the run still starts the proxy and Chrome, measures the display, records the page live (10-45 s, an external request) and only then writes "No rules exist for this test yet" for each test. A page that cannot load becomes a tool error, so the caller learns nothing about the tests that would not have run anyway.
- Evidence: read; no early return for `not checks`.
- Fix: when `checks` is empty, skip the browser and recording and go straight to `_evaluate` (findings are all `not_performed`).
- Confidence: confirmed (by reading)

### G-11 `fit` can return an over-size result with no flag, and its excerpt note can be untrue
- Severity: P3
- Kind: gap
- Where: src/tobi508/pipeline.py:573-650 (`fit`, final `return out`), 523-552 (`_excerpt`), 617-622
- What: after the last step (`keep=60`, one question) `fit` returns the result even if it is still over `RESULT_CHARS`, with no field saying so. Findings, `errors`, `evidence` and `walk` are never cut, so a page with many long FAIL summaries (each up to 1,500 characters) or long `errors` can pass the 50 KB point where Claude Code saves the result to a file (pictures lost, pipeline.py:497-505). Also when no quote is found in the page text `_excerpt` returns the text's start, but the note still says "these are the passages around what the open questions quote".
- Evidence: read; no test builds an oversize findings list.
- Fix: after the loop, if still over, drop `evidence` and shorten `errors`, and add a `cut` note; make the excerpt note say "the start of the text" when `spans` is empty.
- Confidence: confirmed (by reading); speculative (that real pages reach it)

### G-12 Server judge re-asks missing questions one by one, each time rebuilding its request
- Severity: P3
- Kind: time
- Where: src/tobi508/apijudge.py:712-726 (`for q in missing` awaits `_call` serially), 790-794 (`again`)
- What: a 20-question request in which several answers are missing or invalid is followed by one single-question call per missing one, awaited in sequence (the semaphore allows 3 at once, unused here), and each rebuilds the shared block and re-slices the pictures (G-02). Seconds per call add up serially; B-05 covers the cost cap, not the lost concurrency.
- Evidence: read.
- Fix: `asyncio.gather` the single re-asks, and build each single request from the already prepared pictures.
- Confidence: confirmed

### G-13 Small dead and half-wired pieces on the surface
- Severity: P3
- Kind: dead-code
- Where: src/tobi508/jobs.py:156-158 (`running()`); src/tobi508/tools/run_status.py:50-60 (`finish` with a `job_id`); src/tobi508/models.py:261 (`Finding.confidence`, as A-11)
- What: `jobs.running()` is read only by tests/test_tools.py:293 (`all_jobs` is the real listing). `finish=true` together with a `job_id` is accepted and silently ignored (the description says "Without a job_id only"). Neither is wrong; both cost a reader's time.
- Evidence: grep `jobs.running`, read `run_status`.
- Fix: delete `running()` (test uses `all_jobs`); reject `finish` with `job_id` with a ToolError.
- Confidence: confirmed

### G-14 Corrects A-16: container defaults are already set in the Dockerfile
- Severity: P3
- Kind: gap
- Where: Dockerfile:25-35, 46-52 (vs A-16's "headless defaults to False ... hosted container needs both overridden")
- What: the image sets `BROWSER_CHANNEL=chromium`, `HEADLESS=true`, `RUNS_DIR=/data/runs`, and refuses to start without OIDC on a public host (`app.http_options`). So A-16's speculative half is refuted; the wording half stands. What remains: the wheel cannot be used without a checkout, because `REPO_ROOT = parents[2]` points `rules_dir`, `third_party_dir` and `runs_dir` into the checkout, and `[tool.hatch.build.targets.wheel]` packages only `src/tobi508` (no `specs/`, `third_party/`). `uvx tobi508` from a wheel would fail at the first spec or ANDI read.
- Evidence: read config.py:19-23, pyproject.toml:24-25, Dockerfile.
- Fix: note "run from a checkout or the image" in the README, or add `force-include` for specs and third_party.
- Confidence: confirmed (by reading); the wheel failure not built

### G-15 Answer text fields and list sizes have no upper bound and go into report.json and the pre-SCRT file
- Severity: P3
- Kind: gap
- Where: src/tobi508/models.py:386-421 (`Answer.rationale`, `J1Answer.quote/keys/source_url`, `J2Answer.fields`, `J2Field.value/basis_quote`), src/tobi508/tools/answer_questions.py:34-38 (`answers` has `min_length=1`, no max)
- What: `ChoiceAnswer.reasons` has `max_length=500` and `seen` 300, but `rationale`, `j1.quote`, `j2.fields[*]` and the number of answers are unbounded. They are copied into `report.answers`, rewritten into report.json at every answer call, shown by `tobi_explain` and written to the pre-SCRT file. A calling agent (or page-steered text it copied) can bloat a run's report to megabytes.
- Evidence: read the models; the `max_length` appears only on the `ChoiceAnswer` fields.
- Fix: `max_length` on `rationale` (1,000, as `to_answer` already cuts to), `quote` (500), `fields` (50) and `answers` (200).
- Confidence: confirmed (by reading)

## Unverified leads

- `apijudge._lines` (line 432) writes `n role "name" href` from page-controlled accessible names with no escaping of quotes or newlines; a name with a newline could forge a stop line ("7 button Skip to content") and the judge's `element` number. Chrome normally collapses whitespace in accessible names, so not tried.
- `pipeline._compact` rounds every float in a question input to one decimal (line 656-658); no current question input appears to carry a threshold-sensitive number (grepped t2b/t2c/t2d/t3a), but a ratio or seconds value added later would round across its threshold without notice.
- `pipeline.fit`/`build` recomputes `size(build(n))` inside `build(n, keep)` (line 605) and loops up to about 30 builds, each dumping the page text; with a 100 KB+ page text for 4.B this is seconds of CPU on the event loop per result (not timed).
- `read_report.read_report` is a sync tool parsing up to 40M characters; FastMCP 4.0.11 may or may not run it in a thread (A's lead; not checked).
- After `TooManyItems` the run path removes the skipped check but leaves `ctx.selected` (set at line 1052 before the walk loop) holding its id, so a check that reads `selected` believes the skipped test ran (only 4.F/2.x read it today; not exercised).
- `answer_questions` records resume errors in the result only (`errors` local list, line 1449), never in `report.errors`; a failed key press during resume is visible once and then lost from the saved report (the finding then depends on the check treating the missing proof as NEEDS_REVIEW; not checked for each check).
- `Outstanding.done` counts a run as done while questions the server's judge answered unsure still wait for a person (documented as "does not make the work incomplete"); the user-facing story of who answers them is the roadmap item "A person's answer only from TOBI's own UI", which does not exist yet.
- config: `oidc_audience` unset skips the audience check and `required_groups` empty admits any signed-in user (documented in the comments; worth a startup warning when `AUTH=oidc`).
