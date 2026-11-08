# A server judge on real pages (Agent C, round 2)

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
