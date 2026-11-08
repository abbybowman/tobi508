# Large pages: results over the client's limit, and slow replays

Round 2 of the agent eval (svs.gsfc.nasa.gov, 2026-11-08) left about 170
cells unanswered for two reasons that the nasa.gov round never showed. Both
were fixed without changing a check, a question or a rubric: only whether a
cell gets answered, never how.

## Results over the client's size limit

**What happened.** Claude Code passes an MCP result to the agent only up to
about 25k tokens (`MAX_MCP_OUTPUT_TOKENS`, default 25,000). A larger one is
saved to a file and the agent gets a notice. An agent with no shell cannot
read it, so `arm-a-g1-1` read the pre-SCRT file instead and never saw 140
open questions. Exactly its three oversized results (469k, 125k and 85k
characters) were the three pages left unanswered; every result that fit was
answered. Across all transcripts, the largest result passed was 71,815
characters and the smallest refused 71,813: the limit counts tokens.

**Why so large.** Measured by field (rebuild the result from the run folder
and print each field's size):
- 4.B sends the page's whole visible text with its question
  (`page_text`): 427k characters on a page listing hundreds of files.
- `page_text` and `shared_inputs` were built for every open question, not
  only the 10 a result shows, so a page of 4.A questions carried 4.B's text.
- 4.B's and 4.A's shared `stops` (every Tab stop, with names) were 58k on
  the galleries page.

**What we do now** (`pipeline.fit`, every RunResult and AnswerResult):
1. Page text and shared inputs only for the questions shown.
2. A result over `RESULT_CHARS` (54k, leaving room for pictures) shows fewer
   questions; `more_questions`, `next_step` and the to-do list say how many
   come next.
3. When one question alone is still too long, its page text is cut to the
   passages around what the question quotes (`EXCERPT_SIDE` each side,
   joined by `[...]`), and strings in its shared inputs over 160 characters
   are cut; the result says so. The question's own input (4.B's `matches`)
   and the report are never cut.

The eval harness pins `MAX_MCP_OUTPUT_TOKENS` at the CLI's default for both
arms and records it (`cli_limits` in each summary). It is not raised: a
hosted server's clients have the default.

**How we know.** `tests/test_models.py::test_a_result_stays_under_the_clients_size_limit`;
the three real results rebuilt with `fit` came to 52k, 33k and 48k
characters, and Home with its 4.B question first to 43k.

## Replays of large recordings time out when loads overlap

**What happened.** `arm-a-g2-1` could not load 14592 and 14194 (95 and 71 MB
recordings, multi-megabyte JPEGs): `Page.goto: Timeout 30000ms exceeded`
on every check of 14194 and on 9.A-9.C's reads wherever they were other
pages. Alone, a replay load took 6-7 s. Four at once took 37 s each and
eight took 79 s: serving large bodies from the recording is the bottleneck,
and two runs with their other-page reads overlap loads.

**What we do now.** Replay contexts wait `replay_navigation_timeout_ms`
(120 s, config; recorded in `run_settings`) instead of the 30 s live
default. A load that never finishes still fails and its tests stay
NEEDS_REVIEW.

**How we know.** `tests/test_browser.py::test_replay_loads_wait_by_their_own_setting`;
four overlapping loads of the two pages through the guard now finish in
about 40 s each.
