# The server judge (ApiJudge) and its stand-in

What to know before changing `apijudge.py`, and what Agent C showed on real pages in round 2.

## ApiJudge: what to know before changing it

The server answers its own open questions (`src/tobi508/apijudge.py`,
`judge_prompt.md`; plan `docs/plans/2026-11-08-apijudge-build.md`).

- **Rules decide, the model answers.** Answers go through
  `pipeline.answer_questions` like an agent's: `record_answers`' guards, the
  spec's rows. `answered_by` is `server:<model>`. A client answer (even
  `decided_by: human` through MCP) to a question the server answered is
  refused; a person answers on TOBI's own page (not built yet: ROADMAP).
- **Off until the gate.** `JUDGE_TYPES` is empty by default; with
  `JUDGE_BACKEND=client` nothing changes. Any change to the prompt, the
  request, the groups table or a question's rubric or input needs a new gate
  run (`docs/plans/2026-11-08-apijudge-build.md`), and the judge eval for the changed types.
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
- **The gate scripts exist** (2026-11-10): `judge_eval.py answer OUT --backend
  api [--dry] [--repeat N] [--cases A,B] [TESTS]` (the real judge on the eval's
  cases; a PASS where the expected outcome is not PASS, or the outcome a
  trick-text page asks for, is listed first) and `evals/apijudge_gate.py run |
  score` (round 2's frozen pages, scored against the keys on the cells a server
  answer decided: `scoring.split_cells`). A run on fewer than all 10 pages or
  fewer than 3 repeats is a trial and passes nothing. The gate writes the list
  of passing types; the server's default stays empty until Abby approves it.
- **What the first real calls showed** (a trial on 2 trick-text pages and 2
  frozen pages, 4.A and 5.B only): the CLI route works end to end (structured
  output, `answered_by` `server:claude-sonnet-5-5`); both models answered the
  trick pages correctly and said the injected text was page text, not an
  instruction; CILab's demo reel row was answered no-alternative and the page
  scored Fail, as the key. The CLI adds about 3-4k cached input tokens a call
  (its own prompt); 14592's one request cost 52k because of its page picture.
- **A cell the judge answered "unsure" is not performed**, not a mismatch:
  `scoring.GATE_WORDS` counts it as unsure.
- **Gate runs are slow on pages with many other pages:** 14592 and CILab took
  8 minutes together, almost all of it the tests, not the judge. Keep
  `--pages` to the cells you need; the recordings of a run are not kept
  (`_keep` copies the report and pre-SCRT file only), and `runs/` is ignored.
- **Not built yet:** judging questions an agent's answers raise inside
  `tobi_answer_questions` (a job), a test of the 19.A follow-up path, the
  gate's comparison beside Agent C's answers, and `judge_types`' default from
  `gate.json` (deliberately left to Abby).

## A server judge on real pages (Agent C, round 2)

What a model answering TOBI's questions on the server does, measured on
round 2's 10 pages (`evals/agent/judge_c.py`; results in
`evals/judging/round2-armc/abc-score.md`). Agent-assisted results, not
certified Trusted Tester results.

**What happened.** Sonnet 5.5, one call per question, fixed system prompt,
the question's data in one untrusted block, every picture the input names
at native resolution (tall ones in 1,400 px slices), choices as an enum,
applied through `answer_questions`. 194 of 194 answered in each of 3
repeats, 0 failed calls, about 32% unsure; repeats agree on 194 of 200
criterion cells. No false PASS or false DNA from its answers; its errors
were false FAILs, mostly 4.F J1 (5-6 pages) and 9.C J1 (2).

**What we do now.**
- **Fix the question before blaming the model.** C's reasons named the
  cause: 4.F's rubric let "differs from the visual order" stand for "does
  not preserve meaning"; its order picture drew boxes for stops nobody can
  see; 9.C paired unrelated content links and its rubric called different
  words inconsistent. Read the model's `reasons` and `seen` per wrong
  cell.
- **Switch the server judge on per question type,** behind the judge eval
  with real-page packets (`round2-armc/first-round/`).
- **Put a page's shared inputs first and send its questions together.**
  The Tab-stop list and page text repeat in every question of a page
  (Home: 63 questions, 794k input tokens); a warm prompt cache made a
  repeat cost a fifth as much.
- **Small crops can be too small:** 4.D's on and off pictures were 48 x 47
  px for a button. Native resolution does not help a picture that shows
  too little (the cropping review, post-round 2 plan).
- **The CLI route works as a stand-in** (`claude -p`, `--system-prompt`,
  `--tools ""`, `--json-schema`, stream-json input with base64 images;
  the only tool the model sees is the CLI's StructuredOutput). Temperature
  cannot be set there.

**How we know.** `evals/judging/round2-armc/abc-score.md`;
`tests/test_agent_judge_c.py` (schema, answers never defaulted, gate
order, request blocks and slices).
