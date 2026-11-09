# ApiJudge: what to know before changing it

The server answers its own open questions (`src/tobi508/apijudge.py`,
`judge_prompt.md`; plan `docs/plans/2026-11-08-apijudge-build.md`).

- **Rules decide, the model answers.** Answers go through
  `pipeline.answer_questions` like an agent's: `record_answers`' guards, the
  spec's rows. `answered_by` is `server:<model>`. A client answer (even
  `decided_by: human` through MCP) to a question the server answered is
  refused; a person answers on TOBI's own page (bundle 6).
- **Off until the gate.** `JUDGE_TYPES` is empty by default; with
  `JUDGE_BACKEND=client` nothing changes. Any change to the prompt, the
  request, the groups table or a question's rubric or input needs a new gate
  run (bundle 1 builder note 4), and the judge eval for the changed types.
- **Page data stays in one `<untrusted_page_data>` block**: the shared block
  (Tab stops as lines, page-text excerpts) and each question's block. Never
  put page text in the system prompt.
- **Unsure is never retried** and waits for a person
  (`Remaining.waiting_for_person`, not agent work). A failed call is tried
  once more, then the question stays with the calling agent. A missing or
  invalid answer inside a good reply is asked again once, alone.
- **Dry mode first.** `apijudge.dry(settings, [run_id, ...], types)` builds
  every request and counts characters, pictures and bytes: no model call.
  Say how many requests and roughly how many tokens before any model run.
- **The CLI route is a development route** (billed to the Claude Code plan,
  `--json-schema`, an empty `HOME`, no tools). Production is the Messages
  route: temperature 0, the answer as a forced tool call. The key is only put
  in the request header; errors carry the status code, never the body.
- **Tests use `Scripted`**, which tests the plumbing, not the model: after any
  change to a question, rubric or input, run the judge eval and (later) the
  gate, where real pages show what fixtures miss.
- **Not built yet:** the gate scripts (`evals/apijudge_gate.py`, trick-text
  pages), judging questions an agent's answers raise inside
  `tobi_answer_questions` (a job), and the 19.A follow-up path is judged only
  because it calls `run_tt_tests` too (not tested on its own).
