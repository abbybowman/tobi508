# Gate 2026-11-22-135b: round 2's two 4.D false FAILs (4.D 1.12.0)

Agent-assisted results, not certified Trusted Tester results. A development
rerun on round 2's frozen pages (Abby's archive, checked as in
`../gate-2026-11-22-135/README.md`); never in place of the round's blind
score. `evals/apijudge_gate.py run --date 2026-11-22-135b --round 2 --pages
5340,14592 --tests 4.D --types 4.D --frozen-mode replay` (the folder was first
written as 2026-11-23-135 by mistake and renamed), the server judge (CLI
route, `claude-sonnet-5-5`), Chromium 157.0.8103.78. Both pages from the
freeze; nothing loaded live.

| Page | Key | Gate 135 (1.11.0) | Now (1.12.0) | Why it failed |
| --- | --- | --- | --- | --- |
| p06 SVS 14592 | Pass | FAIL (3 x M8) | NEEDS REVIEW (`G3`), no FAIL | The video player gets a new id on each load, so P2's copies of its controls were counted as more elements; Shift+Tab left them under the sticky header, where they showed nothing. P1 had pictured the same controls passing (M6). Fixture F31 |
| p08 SVS 5340 | Pass | FAIL (2 x M8) | NEEDS REVIEW (`WK G3`), no FAIL | The "OVERVIEW" tab and a button sit inside a frame, in a scrolling tab list that clips their focus ring; the tab list answers `elementFromPoint` at their centre, which read as covered (M8), not clipped (M4). Fixture F32 |
