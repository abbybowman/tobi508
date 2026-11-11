# L-evals: review of evals/ (judge_eval, judging, scoring, time_budget, apijudge_gate, snapshot, agent/*)

## Overview

The scoring core (`scoring.py`: `verdict`, `rollup`, `rates`, `WEIGHTS`) is small and mostly sound. A false PASS is
its own verdict and weighs -3, NEEDS_REVIEW costs 0, and skipped pages are listed in the output. The weak points
are around that core:

- **Scoring is not pinned to what was asked.** `agent/score.py` rebuilds the criteria list from today's
  `checks.REGISTRY`. Nothing in the lock pins that list.
- **The gate that decides when ApiJudge types may be switched on is the loosest part.** It has no minimum sample,
  and it ignores two verdicts that are wrong in the unsafe direction.
- **"Validated catch" can absorb a PASS against a key FAIL.**
- **Duplication is heavy:**
  - `judge_c.py` re-implements most of `src/tobi508/apijudge.py`.
  - `per_test.py` re-implements `score.tool_files`.
  - Three copies of the `DROP` env list exist.
- **Rounds are run wastefully.** The judge eval and the gate re-run the whole browser pipeline for every repeat.
  Only the model call needs repeating.
- **Dead or one-off code:** `snapshot.py`, the API route (`providers.py` plus `Agent` in `run.py`), and `judge_c.py`'s
  hardcoded round-2 run ids.
- **`evals/judging/` size:** it is 248 MB on disk with about 253 MB tracked (803 files, repo pack 107 MB). Roughly
  half is repeated copies of the same run. See L-16.

Verified by running: `evals.agent.prompt.criteria()` now returns 20 criteria. Round 1's `agent-score.json` has 17.
Lock hashes for round1, round1-answers and round2 no longer match the current code. See L-01 and L-11.

---

### L-01 Scorer rebuilds the criteria list from today's registry, so re-scoring a locked agent round can invent NO_ANSWER rows
- Severity: P1
- Kind: bug (wrong result)
- Where: evals/agent/score.py:158 (`cs = criteria()`), evals/agent/prompt.py:36-64 (`criteria()` reads `checks.REGISTRY`), evals/judging.py:59-70 (`CODE`)
- What: A round's score takes the criteria from `criteria()` at scoring time. `criteria()` is computed from whatever tests are built right now. The lock hashes the file `prompt.py`, but not the registry contents it reads. Build one more TT test after a round and the round's lock still verifies, because the `.py` files are unchanged. Re-scoring then adds the new criterion for every page. The arm's RESULT line cannot contain it, so it scores `NO_ANSWER` at -1 ("scored as wrong"), for a question the agent was never asked. Agent A and Agent B both get this penalty, and the figures shift silently.
- Evidence: Round 1's `agent-score.json` lists 17 criteria. `criteria()` today returns 20 (adds 1.4.2, 2.2.2, 2.3.1). Round 2 happens to match today's 20, so it re-scores cleanly only by luck. Each arm's `summary.json` records `task_sha256` and the page list but not the criteria. `score()` never reads `task_sha256`.
- Fix: Record the criteria ids in the arm's `summary.json` when the run starts (`run.py:_run_arm`). In `score()`, use the arm's recorded list and refuse, or ignore the arm, when it is missing. Optionally recompute `task_sha256` from the stored page list and compare.
- Confidence: confirmed (reading plus running `criteria()`)

### L-02 Gate has no minimum number of decided cells; one clean cell passes a type
- Severity: P1
- Kind: false-pass-risk (process)
- Where: evals/apijudge_gate.py:62-85 (`passes`)
- What: A type passes when it has zero wrong PASSes and few wrong FAILs. The check is `if row["cells"] and ...` and nothing requires `cells >= N`. A type with 1 or 2 decided cells passes if they agree, or if a judge answered "unsure". The output then lists the type in `judge_types_if_approved` as if it were evidence the type is safe to switch on in the hosted server. `unsure` cells also count as "cells" while carrying no information.
- Evidence: Read `passes()`. `tests/test_gate.py::test_the_gate_rule` only uses `row(cells=10)`, so the small-sample case is untested.
- Fix: Add `MIN_DECIDED` (counting agree plus wrong_*, not unsure). Add the reason "too few cells to judge" to `why_not` when `cells - unsure < MIN_DECIDED`.
- Confidence: confirmed

### L-03 Gate and scorer ignore wrong_dna and the "key DNA, tool PASS" mismatch; validated catches count as "agree"
- Severity: P1
- Kind: false-pass-risk
- Where: evals/apijudge_gate.py:72-85; evals/scoring.py:104 (`verdict` falls through to OTHER), :206-217 (`GATE_WORDS`), :263
- What: Three wrong-direction results never block a type:
  1. **Tool DNA, key Fail (`wrong_dna`).** It is counted and printed but `passes()` never reads it. A judge that turns a failure into "does not apply" is exactly the "missed fail" the weights call as bad as a false PASS (-3).
  2. **Tool PASS, key DNA.** `verdict()` calls this `OTHER`, and the gate drops it into the "other" bucket, which is also never read. A judge that answers PASS where the tester said nothing applies is arguably a wrong PASS (wrong DNA to PASS).
  3. **A validated catch** is mapped to "agree" by `GATE_WORDS`. See L-04.
- Evidence: `passes()` reads only `wrong_pass`, `wrong_fail`, `cells` and `eval_ok`. Reading the verdict ladder shows `key DNA, tool PASS -> OTHER`.
- Fix: Gate on `wrong_dna == 0` as well. Split `OTHER` into "tool PASS vs key DNA" and the rest, and gate on the former. Decide the rule in the plan, since CLAUDE.md principle 3 is about false PASS but the weights already treat missed fails the same.
- Confidence: confirmed (read). Whether the omission is intended is a spec question.

### L-04 VALIDATED_CATCH can absorb a tool PASS against a key FAIL and then disappears from the false-PASS line
- Severity: P2
- Kind: false-pass-risk (reporting)
- Where: evals/scoring.py:125-144 (`score`), :20-26, :155-179 (`rates`); `Score.disagreements` (:119)
- What: Any non-agree, non-skipped verdict becomes `VALIDATED_CATCH` if the tester's `adjudications.json` equals the tool's result. That includes `FALSE_PASS` (tool PASS, key FAIL, tester later agreed PASS). It then counts +1, is dropped from `disagreements()`, and the "false PASS" line shows 0. The comment says the case was a tool FAIL against key PASS (a catch of a real problem). Nothing restricts it to that. A tool PASS that the tester "confirms" after seeing it is the one case where hindsight bias is most likely. It is also the cell a reader most needs to see.
- Evidence: Read `one()` inside `score()`. There is no check on `v` or on the tool result. `rates()` has one "validated catches" count with no split by tool result.
- Fix: Either never convert `FALSE_PASS` (list it as "false PASS, tester later agreed" in its own line), or split the catch count by tool result and always list catches in the per-page disagreements.
- Confidence: confirmed (logic); likely harmless today, since only one adjudication (4.D) exists.

### L-05 Judge eval, gate and judge reruns repeat the whole browser pipeline once per repeat
- Severity: P2
- Kind: time
- Where: evals/judge_eval.py:611-664 (`answer_api`), evals/apijudge_gate.py:132-169 (`run`, serial over pages and repeats, all tests)
- What:
  - `answer_api` re-runs `run_tt_tests` from scratch (record, walk, all checks) on every case, for every `--repeat`. The prepared run for the same case already exists in `state.json`.
  - The gate runs every page over `tests = all of REGISTRY` once per repeat (3 for a real gate), serially, each possibly up to 1800 s. Only the cells a judged type decided are scored (`split_cells`).
  - `judge_c.py` already did the right thing: copy a first-round run, then answer it N times. `apijudge.dry` already works on saved run ids.
- Evidence: Read `run()` in the gate: `tests = [t for t in TestId if t in REGISTRY]` and `await run_tt_tests(...)` inside `for k in range(1, repeat+1)`. Read `answer_api`: `one()` calls `run_tt_tests` per case per repeat.
- Fix: Make one judge-off run per page or case (limited to `--types` and their `with:` dependencies for the gate). Copy that run folder per repeat and call the judge loop on the copy (the `apijudge.judge_run` path). Run pages in a gather capped by `MAX_CONCURRENT_RUNS`.
- Confidence: likely (that an `apijudge.judge_run` on a saved run is usable this way: not run)

### L-06 `judge_c.py` re-implements apijudge.py; the file is a finished one-off with hardcoded run ids
- Severity: P2
- Kind: design / dead-code
- Where: evals/agent/judge_c.py:197-217 (`_links`, `_slices`), :220 (`schema`), :284-371 (`call`), :374-393 (`to_answer`), :242 (`build`); src/tobi508/apijudge.py:380-419, :190-283 (`ClaudeCli.call`), :622-640, :442 (`schema_for`), :567
- What: `_links`, `_slices`, `to_answer` and the CLI `call` are copies, with small differences. Example: apijudge's `to_answer` tolerates a non-dict `s`, and its `pictures_of` survives a missing picture. judge_c's does not. When ApiJudge's schema, slicing or answer handling changes, `judge_c` and `tests/test_agent_judge_c.py` silently stay on the old behaviour. `judge_c.py` was written as a stand-in ("Agent C", 2026-11-08, not touched since). `SOURCES` and `FRESH` hardcode round 2's run ids and URLs, so it cannot run on any other round. The ApiJudge it stood in for now exists and is the thing gated.
- Evidence: Side-by-side read of the two files. Only `tests/test_agent_judge_c.py` and docs reference `judge_c`. The one runtime import is `final_md`/`tool_files` use by itself.
- Fix: If round 2 will not be re-run, move `judge_c.py` (plus its test and `judge_c_prompt.md`) to `docs/` or an archive path. If it will, import `_links`, `_slices`, `to_answer` and the CLI call from `tobi508.apijudge` and keep only the round-2 orchestration.
- Confidence: confirmed

### L-07 `per_test.py` duplicates the tool-file merge and the exclusion logic; its table hides missed fails and ignores adjudications
- Severity: P2
- Kind: design / gap
- Where: evals/agent/per_test.py:35-81 (`merged`, `scored_pages`) vs evals/agent/score.py:83-117 (`tool_files`) and :176-184; per_test.py:93, :101-116
- What: `merged` is `tool_files` re-typed. `scored_pages` re-types the summary/not_scored exclusion from `score()`. Differences that will diverge over time: per_test passes no `adjudicated` map to `score()` (so catches show as errors), and `Other` quietly lumps `missed_fail` (-3 severity), `no_answer` and `validated_catch` together. A reader of that table sees "False PASS 0 / Other 3" and cannot tell a missed Fail from a Pass-vs-DNA. The locked scorer prints them separately.
- Evidence: Read both. Only `tests/test_agent_per_test.py` uses it.
- Fix: Call `score.tool_files` (extend it to take several arm dirs) and expose the exclusion logic as a function in `score.py`. Give the table a "Missed fail" column and pass adjudications.
- Confidence: confirmed

### L-08 `judge_eval.py apply` hides bad-answer cases from its tally and loses state on an exception
- Severity: P2
- Kind: bug (denominator) / gap
- Where: evals/judge_eval.py:505-510, :518, :555-559
- What:
  - A case whose `answers.json` fails validation is set to `"bad_answers"` with `results[name] = {"error": ...}`. The closing line is `scored N: M match`, where N counts only rows with `"match"`. So an eval run with 3 unanswerable cases prints "scored 40: 40 match".
  - `answer_questions` is called with no try/except. A transient exception ends the loop before `state.json` and `results.json` are written. Answers already recorded in earlier cases' run folders are then re-sent on the next `apply`. `judging.py:apply` does handle this and saves per page.
- Evidence: Read lines 497-559. Compare with `judging.apply`.
- Fix: Print `bad_answers` and `errors` counts beside "scored". Wrap the call, set `c["error"]`, and save state after each case.
- Confidence: confirmed

### L-09 Per-criterion server scoring turns "not performed" into "needs review"; review reasons are sniffed from comment text
- Severity: P2
- Kind: bug (classification)
- Where: evals/agent/score.py:270-276 and :142-151 (`review_reason`)
- What:
  - **Collapsed verdicts.** `tv = rollup([side[t].result if side[t].performed else None ...])` then `verdict(kv, tv, True)`. A test the tool did not perform (which per CLAUDE.md principle 2 is NEEDS_REVIEW with a "could not be performed" note) is reported under needs-review. The per-TT block distinguishes the two, so the rate lines "not performed by the tool: 0" and "needs review" are not comparable between the two blocks.
  - **Brittle classifier.** `review_reason` classifies by lower-casing the comment and searching for "not finished yet"+"question" and "time limit". The default is "could not be performed", the very text reserved for not-performed. A wording change in `models.py:37` or the time-limit note silently relabels open-question reviews as "could not be performed".
- Evidence: Read. The strings are in `models.py:37` and `models.py:27`.
- Fix: Use `Side.source` fields (`performed`, outcome rows) rather than comment text. Keep a distinct verdict for not-performed in the criterion rollup, or state in the report that the figures are not comparable.
- Confidence: confirmed (collapse); likely (wording fragility)

### L-10 Re-lock paths: `freeze.py` skips its own check for URLs with a fragment, and "freeze again" cannot refresh a bad recording
- Severity: P2
- Kind: bug
- Where: evals/agent/freeze.py:152 (`load(folder).get(url)`), :186-188 (message), vs src/tobi508/frozen.py:36-37 (`_key` strips the fragment), :82-83
- What:
  - `obtain` stores recordings under `urldefrag(url)[0]`, but freeze looks up `load(folder).get(url)` with the URL as typed. A pages.txt URL with `#...` gets `rec=None`, so `check_recording` never runs. A 404 or CSS-less page is reported "frozen".
  - On a second run `obtain` finds the existing entry and copies it. It does not re-record. The error text "Check them, freeze again" cannot fix a suspect recording, and the same bad copy passes through `check_recording` again. The user must delete the index entry and file by hand, and nothing says so.
- Evidence: Read `obtain` (frozen.py:79-94: hit returns before any live fetch) and `freeze`.
- Fix: Use `_key(url)` for the lookup. When a page is suspect (or a `--refresh` flag is given), delete its index entry before calling `obtain`.
- Confidence: confirmed (by reading); not run

### L-11 The lock hashes live source files, so ordinary edits to scoring code make locked rounds unscoreable
- Severity: P2
- Kind: design
- Where: evals/judging.py:59-70 (`CODE`), :372-383 (`_verify`)
- What: A `score` verifies the round against hashes of `judging.py`, `scoring.py`, `compare.py`, `scrt.py`, `catalog.py`, `tt.json`, `agent/score.py` and `agent/prompt.py`. `scoring.py` was edited on 2026-11-10 (`GATE_WORDS`, `decided_tests`, `split_cells`, i.e. gate code unrelated to the round). Checked today: round1 and round1-answers are already unscoreable (hashes of `judging.py`, `scoring.py`, `compare.py`, `catalog.py`, `tt.json`, `score.py` and `prompt.py` differ; paths still say `a11y_assist`). Round 2 fails on `judging.py`, `scoring.py`, `catalog.py` and `tt.json`. Only the instruction "score with the code at the lock commit" saves it. The idea (no moving the goalposts after the reveal) is right. The mechanism makes every harmless change to a shared file fatal and invites re-locking or editing `lock.json`.
- Evidence: Computed each lock's `code` hashes against the files on disk: round1, round2 and round2-armc all report "CHANGED/MISSING" for several entries.
- Fix: Keep what is hashed small and frozen: copy `scoring.py` and the `verdict` and `rollup` logic into a versioned file, or let the lock store `code_commit` and have `score` read the files with `git show <commit>:path` (or check out into a temp dir). Put gate helpers (`GATE_WORDS`, `decided_tests`, `split_cells`) in `apijudge_gate.py`, not in the locked `scoring.py`.
- Confidence: confirmed

### L-12 CLI arms have no overall wall-clock or spend cap, and the child environment is a denylist
- Severity: P2
- Kind: gap / time / security
- Where: evals/agent/cli.py:189-251 (`_stream`, `_env` :109-133, `DROP` :36-49); run.py:41 (`MAX_TURNS` applies to the API route only)
- What:
  - **No cap.** A `claude -p` arm is read until the process ends. `MCP_TOOL_TIMEOUT` is one hour per tool call, there is no limit on turns or on total time, and no `--max-budget-usd`-style flag. A model loop, or a tool that waits for a job, runs until someone kills it. Costs are only seen afterwards in `agent-score.md`. `MAX_TURNS=400` and `HELPER_TURNS` guard only the API route's `Agent.converse`.
  - **Env denylist.** `_env` copies all of `os.environ` minus a 12-name list and hands it to `claude`, whose MCP children (Agent A's server, Playwright MCP) inherit it. In a session with `AGENT_API_KEY`, a GitHub token or a Claude token, those reach the arm's processes (Agent B's browser is driven by page content). `arms._base_env()` already uses an allowlist, but only for the servers' `env` field.
  - **Same list copied.** The same `DROP` is copied in `src/tobi508/apijudge.py:67`, and `judge_c.py` imports it from `cli.py`. Three places to update when a new CLAUDE_CODE_* variable appears.
- Evidence: Read `_stream` (no timeout) and `_env`.
- Fix: Add a hard wall-clock timeout around the arm (kill and record `ended="timeout"`). Build the child env from an allowlist plus the one auth variable the CLI needs. Define `DROP` once (put it in `tobi508` and import it in `evals`).
- Confidence: confirmed (no cap); likely (inheritance by MCP children: not tested)

### L-13 The gate is run against pages and keys the project has already seen
- Severity: P2
- Kind: gap (method)
- Where: evals/apijudge_gate.py:52-53 (`SRC`, `KEYS` = round 2), :1-32
- What: Round 2's keys and adjudications were revealed and discussed (`review-with-tester.md`). The judge prompt, rubrics and fixtures were then tuned. The gate scores the same pages against the same keys, so "zero wrong PASS in three repeats" mostly measures repeat noise, not generalisation, and the decided-cell counts per type are small (L-02). The docstring says "any change to the prompt ... needs a new gate run", which means the gate is re-run after every tuning step on the same data.
- Evidence: Read `KEYS`; the CLAUDE.md principle 6 note says scripted tests cannot find false PASS the eval did.
- Fix: Say so in the gate output (`note`), and prefer a fresh round (new pages, blind keys) before a type is switched on in a hosted server.
- Confidence: likely (this is methodology, not a code error)

### L-14 `providers.py`: API key forwarded on redirects, `.env` re-read on every lookup
- Severity: P3
- Kind: security
- Where: evals/agent/providers.py:98-115 (`_post`), :53-65 (`_dotenv`/`env`)
- What:
  - `urllib.request.urlopen` follows redirects and re-sends the request headers, including `x-api-key`, to the redirect target. A misconfigured or hostile `AGENT_API_BASE` redirect would receive the key. `AGENT_API_BASE` is not required to be https either.
  - `env()` reads and parses the entire `.env` for every variable and every call. Reading `.env` is otherwise fine: the key is read only for the API route, kept out of `steps.jsonl` and the summary, and not put in the `servers` env lists.
- Evidence: Read; CPython's `HTTPRedirectHandler.redirect_request` copies request headers except content-length/type.
- Fix: Refuse non-https bases (except localhost) and install an opener that refuses redirects. Cache `_dotenv()`.
- Confidence: likely (library behaviour from memory, not run)

### L-15 Packet scrubbing covers `*.json` only; evidence files copied raw
- Severity: P3
- Kind: security (answer-key leakage)
- Where: evals/judge_eval.py:309-361 (`write_packet` copies `run://` evidence into `evidence/`), :431-446 (`scrub` rewrites only `*.json`)
- What: Fixture names describe the expected answer (the scrub comment says so). `scrub` replaces local URLs in JSON files only. Evidence files the questions link to (today mostly PNG, but any run:// file counts) are copied unchanged, with names built from run paths. An evidence file containing `http://127.0.0.1:PORT/4c/f03-key-trap...` text would reach the answering agent. `expected` itself stays out of the packet (`state.json` is outside `-packets`), and the packet folder names are shuffled ids (correct).
- Evidence: Read. Not proven: I did not open a real packet to see whether any non-PNG evidence is ever linked.
- Fix: After the copy, scan every packet file for `127.0.0.1:` and fail the `prepare` step if one is found (or scrub text files too).
- Confidence: speculative

### L-16 `evals/judging/` tracks about 253 MB; much of it repeated copies of one run
- Severity: P3
- Kind: design
- Where: evals/judging/round2-armc/results/arm-c-{1,2,3}/runs/ (each repeat copies the whole first round), evals/judging/round2/results/arm-a-*/transcript.json (up to 6 MB each)
- What: Not reviewing contents. On disk it is 248 MB (round2-armc 91 MB, round2 67 MB, round1 57 MB); `git ls-files` gives 803 files, about 253 MB tracked before compression, repo pack 107 MB. The same page's `pre-scrt.json` (about 5.5 MB) is stored in each of the three arm-c repeats, plus the first round copy. 24 transcripts and 132 pre-SCRT files are tracked, and 47 `.log` files. Page recordings are correctly git-ignored (`evals/judging/**/*.har.zip`).
- Evidence: `git ls-files evals/judging | xargs du -k`, sorted.
- Fix: For future rounds, store each repeat's answers and report only, and reference the shared first-round run (as the gate's `_keep` does: report and pre-SCRT only). Consider why `pre-scrt.json` is 5 MB per page. That is a src question.
- Confidence: confirmed (sizes)

### L-17 One-offs and stale code
- Severity: P3
- Kind: dead-code
- Where:
  - **evals/snapshot.py** (131 lines, 2026-11-06): its stated use was "before and after the result refactor, change 2b". Nothing imports or documents it beyond its own docstring. Importing `judge_eval` for `settings` also pulls every `tests.test_fixtures_*` module. Remove it or move it under `tests/` if kept.
  - **evals/agent/providers.py** and the `Agent` loop in `run.py` (~250 lines): the API route, `Scripted`, `ContextExceeded`, `READ_RESOURCE`/`HELPER`. The agent README says nothing has run on the Ask Sage route, and every real round used `--route cli`. Keep, but mark it unrun, or drop until used.
  - **evals/agent/prompt_dev.py**: one development version (`answers-v1`) whose text says "The a11y tools" (the renamed server). It is a wrapper over `prompt.py` for development runs only. Fine, but update the name (the agent sees it).
  - **evals/time_budget.py**: docstring says `--limit` "default 120, the tool's own", but `RUN_LIMIT_S` is 600 since 2026-11-05. It is used by CI (`.github/workflows/time-budget.yml`) and CLAUDE.md, so keep it.
  - **cli.py**: `self.stderr` is stored on the provider and never cleared, so a leak-check process's stderr can be reported as the arm's `stderr` in the summary.
  - **arms.py**: server names `a11y` and env `A11Y_FROZEN_DIR` are leftovers from the rename (the CLI tool names the agent sees are `mcp__a11y__tobi_*`).
  - **run.py** `model_calls`: counted by substring `'"type": "model"'` in `steps.jsonl` lines. Model text containing that string would be miscounted (the CLI route has its own count).
  - **run.py** does not check that `keys/` is empty before running an arm (`judge_c.py` does with `_no_keys`). Locking requires no keys, but an arm run after keys were added and before lock would see them in the round folder.
- Evidence: grep for references and git log dates.
- Fix: Delete or move `snapshot.py`; fix the stale strings; add `_no_keys` to `run_arm` and `freeze`.
- Confidence: confirmed

### L-18 Smaller scoring and plumbing observations
- Severity: P3
- Kind: gap
- Where: evals/scoring.py:93-97, evals/judging.py:497-516, evals/apijudge_gate.py:168-181, :192-199
- What:
  - **Per-test table misses columns.** The markdown per-test table in `judging._markdown` has no "validated catch" or "no answer" column, so a test with only catches shows as a row of zeros.
  - **`performed` hides multi-row failures.** `Side.performed` is `all(rows performed)`, and `verdict()` returns NOT_PERFORMED before looking at the tool's result. A multi-row test (parent Fail plus a child the tool did not perform) is reported as not performed even if a Fail row exists. Rare, but it hides a possible Fail.
  - **Gate `run.json` is overwritten.** Each `run` call overwrites `run.json`, but result folders are overwritten per page. Two `run` calls in one `gate-DATE` folder (a `--pages` retry, a second `--types`) produce `gate.json` metadata that does not describe the mix of result files.
  - **Gate `eval_by_type`.** It accepts any `api-results-*.json` in the folder without requiring three repeats for the full gate.
  - **Scanning is serial.** `judging.scan` runs pages one at a time with `no_time_limit=True` (each up to 1800 s) while the server allows 2 concurrent runs.
  - **Gate `score` is silent about unscored pages.** A missing `pre-scrt.json` or key skips the page without saying so; `judging.score` lists skipped pages.
- Evidence: Read.
- Fix: Add the missing columns; write a `skipped` list into `gate.json`; fail the gate when pages are missing (it already marks a trial, but does not list which); record repeat and type sets per result folder.
- Confidence: confirmed (by reading)

---

## Unverified leads

- `cli.py`: whether the `Read(/{home}/.claude/projects/**)` allow rule really limits the Read tool to that folder on the `-p` route (the double slash is deliberate; I did not test the CLI).
- `judge_eval.py:cases()` ACT/baseline cases: whether fixture page titles or visible text describe the expected outcome to the answering agent (policy says no; not checked on the vendored pages).
- `judging.apply` re-sends round-N answers if the process dies after `answer_questions` but before the state save (the code saves state per page, so the window is small; not reproduced).
- Whether `shared_inputs`/`page_text` in a packet can include text from other tests' evidence when `with:` tests run (judge_eval `_write_packet` filters questions to one test, but passes the whole `res.shared_inputs`).
- `agent/node/` (Playwright MCP, `frozen-init.cjs`) was out of scope; whether it enforces the live-page logging that `egress_refused` summarizes.
