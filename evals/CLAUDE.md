# evals

Evaluations: the judge eval (`judge_eval.py`), the server judge's gate
(`apijudge_gate.py`), time budgets (`time_budget.py`), scored rounds on real
pages against a certified tester's blind SCRT files (`judging.py`, rounds in
`judging/`) and the agent eval (`agent/`). `README.md` logs every run's
results.

## Records

- Never rewrite `judging/`: its runs, transcripts and `lock.json` hashes are
  records of what ran, and a locked round is scored with the code at its
  lock commit. (The locked rounds keep old names and paths: `a11y_assist`,
  `docs/rules/`.)
- Every judging round's folder has the same layout
  (`docs/how-to/run-a-judging-round.md`, "The round's folder"): no per-round
  `.gitignore` lines, no working papers in it, `ARCHIVE.md` at its root, and
  nothing added to `results/` after the lock.
- A rerun on a round's pages is development evidence; it never replaces the
  round's blind score.

## The judge eval

After changing an open question, its rubric or its input, run the judge
eval: a fresh agent answers from the tool's output alone
(`docs/solutions/judge-eval.md`).

## Commands

```bash
uv run python evals/judge_eval.py prepare /tmp/eval   # judge eval packets ...
uv run python evals/judge_eval.py apply /tmp/eval     # ... after one agent answers them
uv run python evals/judge_eval.py answer /tmp/eval --backend api --dry   # the server judge: size first, no model call
uv run python evals/time_budget.py budget/agency-home.html   # where a run's time goes
uv run python evals/judging.py scan evals/judging/<round>   # then apply, lock, score (README.md)
uv run python -m evals.agent.freeze evals/judging/<round>   # agent eval: then run --arm a|b, lock, score
```
