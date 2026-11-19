# Compare 2026-11-19: calling agent vs server judge, round 3's pages, 3 runs each

Development pages; a rerun that never replaces round 3's blind score. Agent-assisted results, not certified Trusted Tester results.

A is the calling agent with TOBI (the client judge answers open questions), B the same model with Playwright MCP only,
C the server judge (`evals/apijudge_gate.py`, 21 test types). All Sonnet 5.5 (`claude-sonnet-5-5`), the CLI route,
prompt `round1-v1`, round 3's 10 frozen pages. A and B ran as 5 groups of 2 pages per run.

## Accuracy per TT test (A and C), against round 3's keys

| Run | Cells | Agree | Unsafe (PASS/DNA, key Fail) | FAIL/DNA, key Pass | Other | Left for a person |
| --- | --- | --- | --- | --- | --- | --- |
| round 3 blind (reference) | 220 | 118 | 3 | 28 | 0 | 71 |
| A run 1 | 220 | 136 | 0 | 7 | 0 | 77 |
| A run 2 | 220 | 135 | 0 | 8 | 0 | 77 |
| A run 3 | 220 | 136 | 0 | 7 | 0 | 77 |
| C run 1 | 220 | 120 | 0 | 11 | 0 | 89 |
| C run 2 | 220 | 119 | 0 | 10 | 0 | 91 |
| C run 3 | 220 | 119 | 0 | 11 | 0 | 90 |
| A, 3 runs | 660 | 407 | 0 | 22 | 0 | 231 |
| C, 3 runs | 660 | 358 | 0 | 32 | 0 | 270 |

### Rule-decided and answer-decided cells apart (3 runs together)

| Who | Decided by | Cells | Agree | Unsafe (PASS/DNA, key Fail) | FAIL/DNA, key Pass | Other | Left for a person |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | rules | 493 | 301 | 0 | 21 | 0 | 171 |
| A | the agent's answers | 167 | 106 | 0 | 1 | 0 | 60 |
| C | rules | 485 | 273 | 0 | 21 | 0 | 191 |
| C | the server judge's answers | 175 | 85 | 0 | 11 | 0 | 79 |

### Per TT test (3 runs together)

| Test | A agree/unsafe/FAIL-vs-Pass/other/left | C agree/unsafe/FAIL-vs-Pass/other/left |
| --- | --- | --- |
| 2.A | 30/0/0/0/0 | 30/0/0/0/0 |
| 2.B | 30/0/0/0/0 | 30/0/0/0/0 |
| 2.C | 20/0/0/0/10 | 21/0/0/0/9 |
| 2.D | 20/0/0/0/10 | 21/0/0/0/9 |
| 3.A | 30/0/0/0/0 | 30/0/0/0/0 |
| 4.A | 6/0/0/0/24 | 0/0/0/0/30 |
| 4.B | 24/0/0/0/6 | 24/0/0/0/6 |
| 4.C | 21/0/0/0/9 | 21/0/0/0/9 |
| 4.D | 9/0/0/0/21 | 9/0/0/0/21 |
| 4.E | 21/0/0/0/9 | 21/0/0/0/9 |
| 4.F | 12/0/0/0/18 | 10/0/5/0/15 |
| 5.A | 12/0/9/0/9 | 6/0/9/0/15 |
| 5.B | 18/0/9/0/3 | 6/0/9/0/15 |
| 5.C | 28/0/0/0/2 | 21/0/3/0/6 |
| 5.D | 3/0/4/0/23 | 3/0/6/0/21 |
| 5.F | 18/0/0/0/12 | 18/0/0/0/12 |
| 5.G | 18/0/0/0/12 | 18/0/0/0/12 |
| 5.H | 27/0/0/0/3 | 27/0/0/0/3 |
| 9.A | 18/0/0/0/12 | 18/0/0/0/12 |
| 9.B | 18/0/0/0/12 | 0/0/0/0/30 |
| 9.C | 18/0/0/0/12 | 18/0/0/0/12 |
| 19.A | 6/0/0/0/24 | 6/0/0/0/24 |

## Accuracy per WCAG 2.0 criterion (the locked agent scorer's weights)

| Run | Scored | False PASS | Missed fail (DNA) | Agree (of decided) | False FAIL | Other | Needs review | No answer | Weighted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A reported, run 1 | 200 | 0 | 0 | 120/125 | 2 | 3 | 75 | 0 | 115 |
| A reported, run 2 | 200 | 0 | 0 | 120/126 | 3 | 3 | 74 | 0 | 114 |
| A reported, run 3 | 200 | 0 | 0 | 118/125 | 2 | 5 | 75 | 0 | 111 |
| B reported, run 1 | 200 | 1 | 0 | 41/46 | 2 | 2 | 74 | 80 | -46 |
| B reported, run 2 | 200 | 0 | 0 | 53/65 | 3 | 9 | 95 | 40 | 1 |
| B reported, run 3 | 200 | 0 | 0 | 86/107 | 5 | 16 | 93 | 0 | 65 |
| B if the brace were added, run 1 | 200 | 1 | 0 | 84/106 | 5 | 16 | 94 | 0 | 60 |
| B if the brace were added, run 2 | 200 | 0 | 0 | 77/89 | 3 | 9 | 111 | 0 | 65 |
| B if the brace were added, run 3 | 200 | 0 | 0 | 86/107 | 5 | 16 | 93 | 0 | 65 |
| A tool, run 1 | 200 | 0 | 0 | 117/124 | 2 | 5 | 76 | 0 | 110 |
| A tool, run 2 | 200 | 0 | 0 | 117/125 | 3 | 5 | 75 | 0 | 109 |
| A tool, run 3 | 200 | 0 | 0 | 117/124 | 2 | 5 | 76 | 0 | 110 |
| C tool, run 1 | 200 | 0 | 0 | 100/112 | 7 | 5 | 88 | 0 | 88 |
| C tool, run 2 | 200 | 0 | 0 | 99/110 | 6 | 5 | 90 | 0 | 88 |
| C tool, run 3 | 200 | 0 | 0 | 99/111 | 7 | 5 | 89 | 0 | 87 |

B's final messages with an unparseable RESULT line (the outer brace missing), which the scorer reads as no answer: arm-b-g3-1, arm-b-g3-2, arm-b-g5-1. The rows 'if the brace were added' are a sensitivity view, not the scorer's reading.

## Completeness

| Run | Run folders | Asked | Answered | Unsure | Unanswered | Answered by | seen recorded | picture_error | not_viewed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A run 1 | 10 | 105 | 86 | 19 | 0 | {'client': 105} | 63 | 9 | 9 |
| A run 2 | 10 | 103 | 80 | 20 | 3 | {'client': 100} | 60 | 8 | 8 |
| A run 3 | 10 | 104 | 85 | 19 | 0 | {'client': 104} | 62 | 9 | 9 |
| C run 1 | 10 | 110 | 77 | 33 | 0 | {'server:claude-sonnet-5-5': 110} | 98 | 13 | 0 |
| C run 2 | 10 | 109 | 74 | 35 | 0 | {'server:claude-sonnet-5-5': 109} | 108 | 12 | 0 |
| C run 3 | 10 | 108 | 76 | 32 | 0 | {'server:claude-sonnet-5-5': 108} | 101 | 10 | 0 |

### What A did with the tools (from transcript.json)

| Run | tobi_run_tt_tests | tobi_answer_questions | tobi_run_status | …with no job_id | finish=true | tobi_explain | run:// reads | pictures attached to results |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A run 1 | 10 | 21 | 37 | 1 | 0 | 0 | 4 | 92 |
| A run 2 | 10 | 18 | 35 | 2 | 0 | 0 | 2 | 92 |
| A run 3 | 10 | 21 | 36 | 1 | 0 | 0 | 5 | 99 |

### Debrief quotes (verbatim; checked against the files)

- run1, `results/arm-a-g1-1/debrief.md`: "I answered "preserves" and explained those jumps as mega-menu sections, but I never checked that. That PASS is weaker than it looks."
- run1, `results/arm-a-g3-1/debrief.md`: "My `seen` text overstated what I had checked."
- run1, `results/arm-a-g5-1/debrief.md`: "I did not actually open the run:// images."
- run2, `results/arm-a-g1-2/debrief.md`: "Some `seen` entries described what I assumed rather than what I had checked."
- run2, `results/arm-a-g3-2/debrief.md`: "I never called it, because I did not think I needed it."
- run2, `results/arm-a-g5-2/debrief.md`: "It conflicts with my own NEEDS_REVIEW for 1.3.1 on the same page, and it is the kind of wrong PASS I should have avoided."
- run3, `results/arm-a-g1-3/debrief.md`: "I opened only two of the 5.D images"
- run3, `results/arm-a-g3-3/debrief.md`: "I did not think it would change the results, and I wanted to finish."
- run3, `results/arm-a-g5-3/debrief.md`: "the tool said each page's "other page" had the same content as the tested page, so it compared nothing."

## Consistency across the 3 runs

| What | Cells | Same in all 3 runs | Flipped |
| --- | --- | --- | --- |
| A tool outcome per TT test (all cells) | 220 | 216 | 4 |
| A tool outcome, answer-decided cells only | 57 | 55 | 2 |
| C tool outcome per TT test (all cells) | 220 | 214 | 6 |
| C tool outcome, judge-decided cells only | 59 | 53 | 6 |
| A reported, per criterion | 200 | 195 | 5 |
| B reported, per criterion (scorer's reading) | 200 | 95 | 105 |
| B reported, per criterion (brace added) | 200 | 141 | 59 |
| A answers to the same question | 99 | 85 | 14 |
| C answers to the same question | 107 | 93 | 14 |

### A: every flipped TT cell and its source

| Page | Test | Key | Run 1 | Run 2 | Run 3 | Source |
| --- | --- | --- | --- | --- | --- | --- |
| p02 | 5.D | Pass | NEEDS REVIEW | Fail | NEEDS REVIEW | judge |
| p09 | 5.C | Pass | NEEDS REVIEW | Pass | NEEDS REVIEW | judge |
| p10 | 2.C | Does Not Apply | Does Not Apply | NEEDS REVIEW | Does Not Apply | scan |
| p10 | 2.D | Does Not Apply | Does Not Apply | NEEDS REVIEW | Does Not Apply | scan |

### C: every flipped TT cell and its source

| Page | Test | Key | Run 1 | Run 2 | Run 3 | Source |
| --- | --- | --- | --- | --- | --- | --- |
| p01 | 4.F | Pass | Pass | NEEDS REVIEW | NEEDS REVIEW | judge |
| p02 | 5.A | Pass | NEEDS REVIEW | Pass | Pass | judge |
| p02 | 5.B | Pass | Pass | NEEDS REVIEW | NEEDS REVIEW | judge |
| p04 | 4.F | Pass | Fail | NEEDS REVIEW | Fail | judge |
| p04 | 5.A | Pass | Pass | NEEDS REVIEW | NEEDS REVIEW | judge |
| p04 | 5.B | Pass | NEEDS REVIEW | Pass | Pass | judge |

`source`: `judge` = an answer (the agent's for A, the server judge's for C) decided the cell in at least one run; `scan` = only the rules' own evidence changed between loads.

## Cost and time

| Run | List price $ | Tokens in / out / cache read / cache write | Wall s | Model calls | Per page $ | Per page s |
| --- | --- | --- | --- | --- | --- | --- |
| A run 1 | 1.6809 | 102 / 32780 / 1524971 / 300092 | 1792.6 | 51 | 0.1681 | 179.3 |
| A run 2 | 1.6162 | 88 / 32957 / 1275900 / 289722 | 1640.8 | 44 | 0.1616 | 164.1 |
| A run 3 | 1.7503 | 106 / 33141 / 1756030 / 310762 | 1767.1 | 53 | 0.175 | 176.7 |
| B run 1 | 0.6412 | 82 / 21528 / 685340 / 89316 | 294.7 | 41 | 0.0641 | 29.5 |
| B run 2 | 0.5389 | 68 / 18448 / 528922 / 75353 | 256.9 | 34 | 0.0539 | 25.7 |
| B run 3 | 0.6565 | 80 / 21668 / 699117 / 92433 | 266.3 | 40 | 0.0656 | 26.6 |

C's judge, per run (the CLI route records tokens, not a price; the dollar figure is an estimate at the rates A's and B's own list prices imply, residual 0.0 over 30 groups: {'input_tokens': 2.0, 'output_tokens': 10.0, 'cache_read_input_tokens': 0.1, 'cache_creation_input_tokens': 4.0} $/Mtok):

| Run | Judge calls | Failed/retried | Questions | Answered | Unsure | Left open | Tokens in / out / cache read / cache write | Judge s (summed) | Call wall s (browser + judge) | Est. judge $ | Per page est. $ | Per page wall s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C run 1 | 41 | 0/0 | 110 | 110 | 33 | 0 | 84 / 19116 / 31781 / 375616 | 207.4 | 2078.8 | 1.697 | 0.1697 | 207.9 |
| C run 2 | 43 | 0/0 | 109 | 109 | 35 | 0 | 88 / 19422 / 142955 / 295365 | 221.2 | 2065.1 | 1.3902 | 0.139 | 206.5 |
| C run 3 | 42 | 0/0 | 108 | 108 | 32 | 0 | 84 / 17824 / 110947 / 282898 | 200.3 | 2065.5 | 1.3211 | 0.1321 | 206.5 |
