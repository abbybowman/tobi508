# Tool output: keeping it small, and large pages

What a consumer agent can take in one result, and what large pages do to results and replays.

## Keep tool output small: links and shared evidence

**Problem.** A Test 4 run on a two-link page returned about 20,000
characters (5,000 tokens), 60% of it the full report repeated after the
findings, and each 4.A question repeated the whole stop list (on a real page
with ten candidates, ten copies).

**What we do.** `RunResult.report` and `AnswerResult.report` stay on the
Python object (pipeline, tests and evals use them) but are `exclude=True`, so
the client gets `report_uri` (a `run://` resource) instead and reads it only
to save it. Evidence several questions use goes once in `shared_inputs` (a
check's optional `shared_inputs(state)`, like `page_text(state)`), and each
question lists the keys it uses in `shared`. 4.A and 4.B share one `stops`
key, so it goes once when both run. Same run: 8,300 characters (−59%).
Covered by `tests/test_tools.py` (`test_shared_evidence_is_sent_once`, the
report-link assertions).

**2026-11-07, the result refactor.** Findings are one line each in
results (a FAIL keeps its summary up to 1500 characters; a summary of 400
characters or less is kept whole). Answer results carry only the findings
that changed. Open questions come 10 at a time. The detail is in
`tobi_explain`. Measured on the realistic pages: first results 39.5k and
49.5k characters became 30.4k and 36.1k; new context per answering run
fell 35-40%. What is left is mostly question evidence. See
[agent-follow-through.md](agent-follow-through.md).

## Large pages: results over the client's limit, and slow replays

Round 2 of the agent eval (svs.gsfc.nasa.gov, 2026-11-08) left about 170
cells unanswered for two reasons that the nasa.gov round never showed. Both
were fixed without changing a check, a question or a rubric: only whether a
cell gets answered, never how.

### Results over the client's size limit

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

**A second, lower limit.** The first fix aimed at 54k characters, and the
next run lost Home's 62 questions to a 51 KB result: the CLI (2.1.319) also
saves any MCP result over about 50 KB of text to a file and shows a 2 KB
"Output too large" preview (37 KB passed). The agent read the file with
`Read`, which carries no pictures, and gave up on the picture questions (its
debrief). A server can raise this per tool (`_meta`
`anthropic/maxResultSizeChars`), but only Claude Code reads it; the tool
stays under the default instead.

**What we do now** (`pipeline.fit`, every RunResult and AnswerResult), by
steps until the result is under `RESULT_CHARS` (45k, leaving room for
pictures):
1. Page text and shared inputs only for the questions shown (up to 10).
2. Fewer questions, down to `MIN_UNCUT` (5).
3. Then cut: the page text to the passages around what the shown questions
   quote (`EXCERPT_SIDE` each side, joined by `[...]`, within 80% of the
   room left, since JSON escaping lengthens text), and strings in shared
   inputs to 160, then 60 characters (`SHORT_STRINGS`), each time with 10
   questions down to one. Each cut says so in the result. The questions'
   own inputs (4.B's `matches`) and the report are never cut.

`more_questions`, `next_step` and the to-do list say how many come next.
Shared stop lists stay in their format (a question's input changes would
need the judge eval): 145-153 stops are 18-30k characters even cut, so
Home gets 10 questions only with names cut to 160 characters.

The eval harness pins `MAX_MCP_OUTPUT_TOKENS` at the CLI's default for both
arms and records it (`cli_limits` in each summary). It is not raised: a
hosted server's clients have the default.

**How we know.** `tests/test_models.py::test_a_result_stays_under_the_clients_size_limit`;
round 2's real results rebuilt with `fit`: Home 44k (10 questions, names
cut), Search 33k (10, uncut), Galleries 44k (1: 4.B with an excerpt of its
page text), Help 30k.

### Replays of large recordings time out when loads overlap

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
