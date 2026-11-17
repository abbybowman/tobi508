# Gate 2026-11-17: the rerun for steps 21, 36 and 22

Agent-assisted results, not certified Trusted Tester results. Development
reruns on all three rounds' frozen pages; round 3's pages are development
pages and this never replaces round 3's blind score
([`round3/score.md`](../round3/score.md)).

**What ran.** `main` after #109 (steps 21, 36), #110 (step 22) and #111
(step 22 narrowed), before step 23. `evals/apijudge_gate.py run --round
1|2|3 --frozen-mode replay`, the server judge on step 9b's 21 question
types (CLI route, `claude-sonnet-5-5`), tests 4.A, 4.C, 4.D, 4.E, 4.F,
5.A, 5.B, 5.C, 5.D, 5.F, 5.G, 5.H. Every page and other page was served
from the freeze ("replay" mode: a URL with no recording is a tool error,
never fetched live); no report lists a live page. The three rounds ran at
once in one container. Page files stay out of git (`.gitignore`); each
round's `run.json` is here.

**Compared with.** Rounds 1 and 2: step 9b (`gate-2026-11-16`,
`sides.real`, `main` at `ece881b`). Round 3: the locked blind run
(`round3/results`). Between those and this run, `main` also merged steps
31 (9.B) and 29's small part (5.B), so a 5.B cell can move for step 29.
Verdicts by each round's own keys and scorer (`compare.py`, which reuses
`gate-2026-11-16/compare.py`'s `side()`). The table is
[`moved.md`](moved.md) (`moved.json`).

**Checked alone.** Three rounds at once loaded the container; four cells
were checked by running the page again on its own:
`gate-2026-11-17-alone/round1` (round 1's p04 to p06), and round 2's p01
twice on this code and twice on the code before step 22 (commit `41dcb01`;
scratch runs, not kept).

## Every moved cell, with its cause

### Round 1 (9 pages): 5 moved, none from steps 21, 36 or 22

| Page | Test | Key | Old | New | Cause |
| --- | --- | --- | --- | --- | --- |
| p04 careers | 4.C | Pass | NEEDS REVIEW (A3 G4 RC) | PASS | Load: the "Was this page helpful?" popup opened in this run and its own Tab loop replaced guard RC's opened content. Alone: NEEDS REVIEW (RC), as in 9b |
| p04 careers | 4.E | Pass | NEEDS REVIEW (RC) | PASS | The same popup run. Alone: NEEDS REVIEW (RC), as in 9b |
| p04 careers | 4.F | Pass | PASS | NEEDS REVIEW (o1:M9) | The same popup run: its Tab loop raised order signals and the judge was unsure. Alone: PASS, as in 9b |
| p05 missions | 5.B | Pass | NEEDS REVIEW (A4 G3) | FAIL (M3 on the "Earth's Moon" filter labels) | Reproduced alone. Not steps 21, 36 or 22 (pass L found the filters; step 22 touches 5.B only when it found no field). Step 29's 5.B 1.10.0 or the judge's answer: for the thread that owns 5.B |
| p06 artemis-iii | 5.D | Pass | NEEDS REVIEW (RC) | FAIL (f1:M9: focus moved to the popup after typing in Search) | Load: the popup opened mid-replay. Alone: NEEDS REVIEW (RC), as in 9b |

### Round 2 (10 pages): 6 moved

| Page | Test | Key | Old | New | Cause |
| --- | --- | --- | --- | --- | --- |
| p08 5340 | 5.F | Pass | FAIL (judge: "4" not identified) | NEEDS REVIEW (a1-f*:M10) | **Step 36**: "4" holds no word, so it is not a candidate message |
| p08 5340 | 5.G | Pass | FAIL | NEEDS REVIEW (N9) | **Step 36** |
| p01 home | 4.E | Pass | PASS | NEEDS REVIEW (WK: 144 of 145) | Load: the walk missed "Earth Information Center". Alone, two runs on this code and two on the code before step 22: PASS, 145 of 145 |
| p03 | 4.F | Pass | FAIL (judge) | NEEDS REVIEW (o1:M9) | The judge answered unsure this time (4.F's question did not change) |
| p03 | 5.B | Pass | FAIL (judge) | NEEDS REVIEW (M1 rows) | Not steps 21, 36 or 22; step 29 or the judge |
| p04 | 4.F | Pass | PASS | NEEDS REVIEW (o1:M9) | The judge answered unsure this time |

(The first attempt of this rerun, before #111, also moved round 2 p01's
4.C to NEEDS REVIEW by row WL on 145 then 146 elements; #111 narrowed
step 22 and that cell no longer moves.)

### Round 3 (10 pages): 20 moved

| Page | Test | Key | Old | New | Cause |
| --- | --- | --- | --- | --- | --- |
| p03 contact | 5.F | Fail | **PASS** (M2) | NEEDS REVIEW (M2) | **Step 21**: an unsafe cell made safe |
| p03 contact | 5.G | Fail | **PASS** (N4) | NEEDS REVIEW (N8) | **Step 21**: an unsafe cell made safe |
| p08 forum | 4.F | Fail | **DOES NOT APPLY** (A3) | NEEDS REVIEW (WL) | **Step 22**: an unsafe cell made safe |
| p07 home | 4.A | Pass | FAIL (u*:M16) | NEEDS REVIEW (WK WL) | **Step 22** (the walk began before the page drew) |
| p08 forum | 4.A | Pass | FAIL | NEEDS REVIEW (WK WL) | **Step 22** |
| p07 home | 4.F | Pass | DOES NOT APPLY (A3) | NEEDS REVIEW (A4 G3, WL's sentence) | **Step 22** |
| p07 home | 5.D | Pass | DOES NOT APPLY (A1) | NEEDS REVIEW (A3 G3) | **Step 22**, with the walk: this run's walk reached the search field before the page finished drawing |
| p08 forum | 5.D | Pass | DOES NOT APPLY (A1) | NEEDS REVIEW (A2) | **Step 22**: fields counted after the walk |
| p07 home | 5.F, 5.G | Does Not Apply | DOES NOT APPLY (A1, agreeing by luck) | NEEDS REVIEW (A5 G3) | **Step 22**: the key's DNA is for another reason (plan, cause 2) |
| p08 forum | 5.F, 5.G | Does Not Apply | DOES NOT APPLY (A1, by luck) | NEEDS REVIEW (A2) | **Step 22** |
| p07 home | 5.H | Does Not Apply | NEEDS REVIEW (A2) | DOES NOT APPLY (A4), agrees | The walk reached the drawn page's search field this run, so pass E read it; 5.H decided on the form as drawn |
| p10 MySearchStory | 4.A | Fail | NEEDS REVIEW (k1:M5 k2:M7 x1:M8) | FAIL (k1, k2: M6), agrees | The judge answered "no other keyboard way" this time (4.A's question did not change) |
| p01, p10 | 4.F | Pass | PASS (M7) | NEEDS REVIEW (M9) | The judge answered unsure this time |
| p01, p06 | 5.B | Pass | DOES NOT APPLY (A2) | NEEDS REVIEW (A2u) | Step 29's small part (5.B 1.10.0), the other thread |
| p05 verifier | 5.B | Pass | FAIL (judge) | NEEDS REVIEW | Step 29 or the judge |
| p03 contact | 5.A | Pass | PASS (c1:M4) | NEEDS REVIEW (c1:M6) | The judge answered unsure on the search field's label this time |

**Unsafe cells.** Before: 3 on round 3 (p03 5.F, p03 5.G, p08 4.F), 0 on
rounds 1 and 2. After: 0 on all three. No moved cell became a PASS or a
DOES NOT APPLY that the key fails. New wrong FAILs: round 1 p05 5.B
(reproduced alone; step 29 or the judge), and p06 5.D and p04's cells
only under load (not reproduced alone).

**Verified** (commands above): every cell, row and key comment in
`moved.md`; that no page was loaded live (`live_pages` empty in every
report); the four load-only moves, by running the page alone.
**Assumed**: that the popup opens under load because a heavy machine
changes when nasa.gov's scripts run (KNOWN-LIMITS); not traced.
