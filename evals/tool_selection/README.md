# Tool selection eval

Do agents choose TOBI's tools, and their arguments, from the tool
descriptions alone? Evidence for the GSA hackathon's criterion "tool names
and descriptions precise enough for an LLM to select them without
ambiguity". No browser, no page and no grading model: a stub server serves
the real tool list, and a script scores what the agent called.

Agent-assisted results, not certified Trusted Tester results; this eval
tests none of them.

## What runs

- **Cases** (`cases.toml`, written and committed before any run): a
  plain-language request, any earlier turns it needs (`priors/`: abbreviated
  copies of real result shapes, given in the prompt as the conversation so
  far, because the CLI cannot be handed a fabricated tool-call history), and
  the expected answer: the tool the agent's first TOBI call must use (or
  none), the arguments that must be present, absent or equal, and for the
  should-not-call cases a regex the final message must match and no
  certification claim. Expectations found wrong later go in
  `corrections.toml` with the reason; `cases.toml` is not edited.
- **Tool list** (`tools.py`): the real server's, per judge mode
  (`JUDGE_BACKEND=client` and `api`), each built in its own process and read
  through FastMCP's client exactly as an MCP client sees it. The two differ
  only in `tobi_run_tt_tests`' judge paragraph (`tests/test_tool_selection.py`).
- **Stub** (`stub.py`): serves that list word for word (name, title,
  description, input schema, annotations), records every call, returns a
  short canned result, and refuses a URL outside `.gov`/`.mil` as the real
  server does. Not served: the output schema (a client checks results
  against it) and the server's instructions (this measures the descriptions
  alone; a real client also gets the instructions' tool selection guide).
  The stub accepts what the real server would refuse in one case: an answer
  to a question the server's judge already answered.
- **Agent** (`run.py`): Claude Code's own client, `claude -p`, isolated as
  the agent eval's CLI route is (`evals/agent/cli.py`: empty HOME, no
  settings, identifying variables unset), with Claude Code's default system
  prompt, only the stub server and the CLI's MCP resource tools, and at most
  4 turns. One shared empty working folder, so the prompt cache holds
  across runs (a fresh folder name per run cost 3 times as much).
- **Score** (`score.py`, no model): right tool (or rightly none; no
  forbidden call), arguments valid against the tool's `inputSchema`
  (jsonschema), the case's required arguments, and the final-message checks.
  `passed` reads the first TOBI call; `anywhere` (added after the first
  pass) accepts the expected call at any point. `report.py` scores every
  saved run again from its events, as committed and as corrected.

## Commands

```bash
uv run python -m evals.tool_selection.run OUT --label before   # both models, both modes, 3 repeats
uv run python -m evals.tool_selection.run OUT --label after --cases read-what-changed,certify
uv run python -m evals.tool_selection.run OUT --label debrief --repeats 1 --debrief --cases explain-why-fail
uv run python -m evals.tool_selection.report OUT before after > report.md
uv run pytest -n0 tests/test_tool_selection.py                 # the scorer, with a scripted agent
```

`OUT/<label>/` holds `tools-<mode>.json` (what was served), `meta.json`
(commit, models, CLI version), `results.jsonl` (one scored line per run,
with its cost) and `runs/` (each run's CLI events and the stub's call log).
`--debrief` asks one more question after each run's answer is recorded, in
the same session with every tool off (`run.DEBRIEF`: which tools it
considered and why it called what it did; it names no tool as the right
one), saved to `debrief.md` and never scored. The debrief turn has no tool
definitions in context, so it cannot quote a description.

A logged pass is copied to `results/<date>/<label>/`: `results.jsonl`,
`meta.json`, the served tool lists and `runs.zip` (each run's agent
messages and calls, tool results cut to 500 characters, the final result,
the stub's call log and any debrief: what scoring reads). `report.py` reads
`runs.zip` when the run folders are not there; `results/<date>/report.md`
is made from the committed files, and `debriefs.md` collects the debriefs
verbatim (the debrief pass's own run files are not kept: its tool lists
are the after pass's, and its scores are not reported).

Results: `evals/README.md` ("Tool selection").
