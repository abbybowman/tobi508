# Fixes after agent eval round 1: index

All 20 fixes were built on 2026-11-05 and 2026-11-06 (PR #14 and after).
Code, specs and tests cite them as "post-round 1 fix N"; this index says
what each number was and where it lives now. The evidence and the long
form are in git history (this file before 2026-11-11) and in the rounds'
own records (`evals/judging/round1*/`).

| Fix | Problem round 1 showed | What was built, and where |
| --- | --- | --- |
| 1 | A detached frame crashed a run | A frame that detaches is counted as unreachable; a walk that fails is an error in the result, not a crash (`traverse.dom_inventory`, `pipeline.py`) |
| 2 | MCP clients time a tool call out | Option C: a call waits `CALL_WAIT_S` (45 s), the run goes on as a job and `tobi_run_status` waits again (`jobs.py`). Rejected: documenting client settings (A), always returning at once (B) |
| 3 | CI skipped Agent B's browser tests | `npm ci --prefix evals/agent/node` in `ci.yml` |
| 4 | The agent chose not to answer open questions | Every result carries `next_step` (`pipeline.next_step`) |
| 5 | Pages that need more than the time limit | `RUN_LIMIT_S` 600 s, `MAX_CONCURRENT_RUNS` 2 (`config.py`); since 2026-11-07 no limit by default |
| 6 | Agent A asked for a shell | Nothing to fix |
| 6b | A result too large for the client | `question_texts`, shortened summaries and row lists (`pipeline.fit`) |
| 7 | A freeze did not check its own recordings | `freeze.check_recording` marks a page `suspect` |
| 8 | No efficiency figures in the score | Tokens, cost and wall time per run (`evals/agent/score.py`) |
| 9 | What Agent A would have answered | Done another way: the answering runs (`evals/judging/round1-answers/`) |
| 10 | 5.A row M3 counted any button beside the field | 5.A spec |
| 11 | 4.D row M8: false FAILs at 0 px | 4.D spec, `t4d.py` |
| 12 | A refused page was never tested fully | Over 5.D's field cap the run leaves out only 5.D and names the call that tests it (5.D spec 1.1.0) |
| 13 | The scorer: split calls, "not performed" against "needs review", page keys | `evals/agent/score.tool_files`, `Finding.not_performed`, `compare.page_key` |
| 14 | 5.B on pages with no visible label; header menu buttons | 5.B spec 1.2.0 |
| 15 | Many identical open questions | One question per set of like fields (`t5d.j1_groups`, 5.D spec 1.1.0) |
| 16 | 4.F: a card grid, a filter list, a dropdown taken for a dialog | 4.F spec, `t4f.py` |
| 17 | 5.F and 5.G on a site search form | 5.F spec row A3s |
| 18 | 19.A was never decided | The agent may add pages; suggested pages and `follow_up` (19.A spec 1.1.1) |
| 19 | Visual questions were answered without the picture | Option 3: the pictures a result's questions name are attached to it (`inline.py`) |
| 20 | A round's lock missed files git ignores | `evals/judging.py lock`; [how to run a round](../how-to/run-a-judging-round.md) |

Still open from this work: job state is in memory, so a hosted server
with several workers needs shared job state (on [the roadmap](../ROADMAP.md)).
