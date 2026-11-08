# Round 2: attempts stopped before they finished

Not results and never scored (the scorer reads `results/` only). Kept so the
round's history is complete.

## arm-a-g1-2-stopped (2026-11-08, started 02:30 UTC, stopped about 02:40 UTC)

Agent A, group 1, second run, on the same code and prompt as `arm-a-g1-1`.
Stopped early on purpose (Abby, 2026-11-08): run 1 showed two problems that
leave most cells unanswered, unrelated to how questions are answered:

- `arm-a-g1-1`: the agent answered the open questions of 1 of 5 pages and
  left about 140 (Home 73, Search 53, Galleries 14, Help 1).
- `arm-a-g2-1`: the agent answered every question, but the tool could not
  load the two pages with the largest frozen recordings (14592, 95 MB;
  14194, 71 MB): `Page.goto: Timeout 30000ms exceeded`. Every finding on
  14194 and 33 findings across the group are NEEDS_REVIEW for that reason.

The round is paused, unscored and unlocked, while these are fixed; only
changes that affect whether a cell gets answered, not how it is answered.
Files: `steps.jsonl`, `runs/` (no final message or summary).
