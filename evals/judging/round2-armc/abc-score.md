# Round 2: Agents A, B and C, scored

svs.gsfc.nasa.gov, 10 pages, scored 2026-11-08 against Abby's blind SCRT
files (`round2/keys/`, committed after both locks) with the locked scorer
(`evals/agent/score.py`, weights: agree +1, needs review 0, false PASS and
missed fail -3, other errors -1). Agent-assisted results, not certified
Trusted Tester results. Files: `round2/agent-score.md` and `.json` (arms A
and B), `round2-armc/agent-score.md` and `.json` (arm C); C's tool per TT
test from the scorer's `_server` function, which the scorer runs only for
`arm-a*` folders.

- **A:** the agent with TOBI (Sonnet 5.5, CLI route). Run 1 tested two
  groups of 5 pages per conversation, before the result-size and replay
  fixes; run 2 tested pairs, after them. Each row sums a run's
  conversations over the 10 pages.
- **B:** the same model with Playwright MCP, same prompt and pages.
- **C:** a stand-in for the planned server judge: TOBI's first-round open
  questions (182; 194 with follow-ups) answered one call per question by
  Sonnet 5.5 with a fixed prompt, applied through the tool's guards;
  results rolled up by code. Three repeats from the same first round.

### Per WCAG 2.0 criterion

| Run | Scored | False PASS | Missed fail (DNA) | Agree (of decided) | False FAIL | Other | Needs review | Weighted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A run 1 (2 x 5 pages) | 199 | 3 | 0 | 74/92 | 12 | 3 | 107 | 50 |
| A run 2 (5 x 2 pages) | 199 | 4 | 1 | 87/108 | 14 | 2 | 91 | 56 |
| B run 1 | 199 | 19 | 1 | 117/144 | 0 | 7 | 55 | 50 |
| B run 2 | 199 | 15 | 2 | 99/124 | 0 | 8 | 75 | 40 |
| C repeat 1 | 199 | 4 | 2 | 84/127 | 29 | 8 | 72 | 29 |
| C repeat 2 | 199 | 4 | 2 | 84/126 | 28 | 8 | 73 | 30 |
| C repeat 3 | 199 | 4 | 2 | 84/125 | 27 | 8 | 74 | 31 |

### The tool per TT test

| Run | Scored | False PASS | Missed fail (DNA) | Agree (of decided) | False FAIL | Other | Needs review | Weighted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A run 1 (2 x 5 pages) tool | 220 | 3 | 0 | 80/102 | 14 | 5 | 118 | 52 |
| A run 2 (5 x 2 pages) tool | 220 | 4 | 2 | 97/129 | 17 | 9 | 91 | 53 |
| C repeat 1 tool | 220 | 4 | 2 | 93/134 | 26 | 9 | 86 | 40 |
| C repeat 2 tool | 220 | 4 | 2 | 93/133 | 25 | 9 | 87 | 41 |
| C repeat 3 tool | 220 | 4 | 2 | 93/132 | 24 | 9 | 88 | 42 |


### What the scores say

1. **No false PASS or false DNA came from a judge's answer, in A or C.**
   Every false PASS and missed fail in the tool's results was decided by a
   rule alone, and the same cells in every A and C run:
   - 4.A on CILab (2.1.1), 4.C on 5340 (2.1.2), 5.D on 5144 and 5340
     (3.2.2): false PASS;
   - 9.A on CILab and 14592 (2.4.1): Does Not Apply where the key fails.

   Agent A's criterion-level false PASSes are these, relayed; A added none
   of its own this round. B's 15-19 false PASSes are its own (2.4.1 on
   most pages, 1.3.1 and 4.1.2 on the embedded-app pages, 2.4.5).
2. **C answers everything, and its answers decide more cells, but about
   45% of those are wrong, all toward FAIL.** Cells whose outcome rested
   on a judge's answer: C 27-29 per repeat, 16 agree and 11-13 false FAIL;
   A run 2 14 (12 agree, 2 false FAIL), A run 1 7 (6 and 1). C's wrong
   answers are mostly one question type: 4.F J1 (focus order preserves
   meaning) answered "does not preserve" on 5-6 pages where the key
   passes, then 9.C J1 "inconsistent" (2), 4.A (1-2), 4.D, 5.A, 5.B.
   Its right ones include 4.B and 5.H (5 pages each), 5.C, 5.D and 2.B.
3. **The weighted scores reward leaving cells open.** A scores higher
   (50-56) because its unanswered questions stay needs review (weight 0);
   C's extra answers cost -1 each when wrong. Per TT test, the tool with
   A's answers scores 52-53, with C's 40-42.
4. **The rules' own errors are larger than any judge's:** 13-15 false
   FAILs by rule alone in every run (13 in each C repeat), mostly 5.A on 7 pages (the key passes the
   search field's label), 5.C (3), 19.A (2) and 4.D (1); and the 6 false
   PASS or missed fail cells above.
5. **C is repeatable.** Its three repeats agree on 194 of 200 criterion
   cells; the 6 others are Fail in one repeat and needs review in another
   (2.4.3 from 4.F on 4 pages; 2.1.1 and 2.4.6 on Search), never Pass
   against Fail. A's runs differ by which pages the agent answered at all.

### C's answers and tokens

| Repeat | Answered | Unsure (pictures / text) | Failed calls | Input tokens | Output tokens |
| --- | --- | --- | --- | --- | --- |
| 1 | 194 of 194 | 62 (49 of 140 / 13 of 54) | 0 | 1.71M | 72k |
| 2 | 194 of 194 | 63 (47 / 16) | 0 | 1.71M | 72k |
| 3 | 194 of 194 | 62 (46 / 16) | 0 | 1.71M | 71k |

Input tokens per page (cached or not; the same in every repeat): Home
794k (63 questions, about 12.6k each: the shared stop list and full-page
pictures), Search 382k (53), 5340 179k (21), Galleries 117k (26), 14592
99k (8), 5144 54k (11), 14194 53k (5), Help 22k (4), 4914 9k (3), CILab
none. About 8.8k input tokens per question overall, 7-8 minutes per
repeat at 3 calls at a time.

### What to fix next (post-round 2)

- **Rules:** the 4 false PASS cells (4.A CILab, 4.C 5340, 5.D 5144 and
  5340) and 9.A's missed fails come first (principle 3), then 5.A's
  false FAIL on the search field (7 pages), 5.C, 19.A and 4.D.
- **Judge:** 4.F J1 before ApiJudge is switched on for it: run it through
  the judge eval with these pages' order pictures; the research note's
  crop work applies (Abby, 2026-11-08: review cropping post-round 2).
- **Scoring:** report judge-driven cells apart from rule-driven ones, as
  above, so a judge is not credited or blamed for a rule's outcome.
