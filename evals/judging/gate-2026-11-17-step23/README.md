# Gate 2026-11-17, step 23: the rerun after the page is drawn

Agent-assisted results, not certified Trusted Tester results. Development
reruns on all three rounds' frozen pages; round 3's pages are development
pages and this never replaces round 3's blind score
([`round3/score.md`](../round3/score.md)).

**What ran.** `main` after #112 (step 23: every load waits for the page to
draw) and #113. `evals/apijudge_gate.py run --round 1|2|3 --frozen-mode
replay`, the server judge on step 9b's 21 question types (CLI route,
`claude-sonnet-5-5`), tests 4.A to 4.F, 5.A to 5.D, 5.F to 5.H, 9.A to 9.C
and 19.A (step 23 also changes what the site read and 4.B see). One round
at a time (round 3, then 2, then 1), never side by side: the first rerun
showed that three rounds at once move cells by load alone. Every page and
other page was served from the freeze ("replay" mode); 19.A's searches
are listed in `live_pages` with `frozen: true`, and no entry was fetched
live. Page files stay out of git; each round's `run.json` is here.

**Compared with.** For the first rerun's tests (4.A, 4.C to 4.F, 5.A to
5.D, 5.F to 5.H): the first rerun, [`gate-2026-11-17`](../gate-2026-11-17/),
so a move here is step 23's, the judge's, or load. For 4.B, 9.A to 9.C and
19.A, which the first rerun did not run: rounds 1 and 2, step 9b
(`gate-2026-11-16`, `sides.real`); round 3, the locked blind run. Those
also carry step 31 (9.B, the other thread). Verdicts by each round's own
keys and scorer (`gate-2026-11-17/compare.py --new gate-2026-11-17-step23
--old gate-2026-11-17`). The full table is [`moved.md`](moved.md)
(`moved.json`).

## Every moved cell, with its cause

### Round 1 (9 pages): 10 moved, none from step 23

| Page | Test | Key | Old | New | Cause |
| --- | --- | --- | --- | --- | --- |
| p04 careers | 4.C | Pass | PASS (first rerun, under load) | NEEDS REVIEW (A3 G4 RC) | Load in the first rerun: the popup opened there. Back to step 9b's and the page-alone outcome (RC: "NASA Force" and 3 more not reached) |
| p04 careers | 4.E | Pass | PASS (first rerun, under load) | NEEDS REVIEW (RC) | The same: back to 9b's and the page-alone outcome |
| p04 careers | 4.F | Pass | NEEDS REVIEW (o1:M9, under load) | PASS (o1:M7), agrees | The same: back to 9b's and the page-alone outcome |
| p06 artemis-iii | 5.D | Pass | FAIL (f1:M9, under load) | NEEDS REVIEW (RC) | The same: the first rerun's false FAIL under load is gone; back to 9b's outcome |
| p01 spot-the-station | 4.C | Pass | NEEDS REVIEW (i1:M1) | PASS, agrees | The open question i1 was not raised this run, so no judge answer held it; why it was not raised was not traced |
| p06 artemis-iii | 4.F | Pass | NEEDS REVIEW (o1:M9) | PASS (o1:M7), agrees | The judge answered "preserves" this time |
| p01, p04, p06, p08 | 19.A | Pass | PASS (step 9b: W2, the live search) | NEEDS REVIEW (W8 W9 W4) | The run's setting, not step 23: step 9b ran round 1's site search and suggested pages live ("tested_frozen"); this rerun serves every page from the freeze ("replay", as asked), and round 1's freeze holds no copy of them ("no saved copy of it was available to load", in each report) |

### Round 2 (10 pages): 8 moved, none from step 23

| Page | Test | Key | Old | New | Cause |
| --- | --- | --- | --- | --- | --- |
| p02 | 4.F | Pass | NEEDS REVIEW (o1:M9) | FAIL (o1:M6) | The judge: J1 "unsure" in the first rerun, "does not preserve" now, on the same kind of footer S3 signals (one of six dropped) |
| p03 | 4.F | Pass | NEEDS REVIEW (o1:M9) | FAIL (o1:M6) | The judge, the same way (step 9b also had this cell FAIL) |
| p07 | 4.F | Pass | NEEDS REVIEW (o1:M9) | FAIL (o1:M6) | The judge: the signals are the same eleven both times; only J1's answer changed |
| p10 | 4.F | Pass | NEEDS REVIEW (o1:M9) | PASS (o1:M7), agrees | The judge answered "preserves" this time |
| p09 | 5.B | Pass | FAIL (f2:M2, M3) | NEEDS REVIEW (f2:M4), safer | The judge answered "unsure" on the pulsar catalog's "Click to Select" and slider |
| p01 | 9.C | Pass | PASS (step 9b) | NEEDS REVIEW (p3-*, p5-* to p9-*: C6) | The judge answered "unsure" on same-name links ("Go to this page") that lead to different items |
| p08, p09 | 9.C | Pass | NEEDS REVIEW (step 9b) | PASS (C1, C3), agrees | The judge answered "consistent" on the same kind of pairs |

### Round 3 (10 pages): 18 moved

| Page | Test | Key | Old | New | Cause |
| --- | --- | --- | --- | --- | --- |
| p07 home | 4.E | Pass | FAIL (e1:M4, e3:M12) | NEEDS REVIEW (M11, R?) | **Step 23**: with the app drawn before the walk, its own address change no longer lands on the first key press (plan, cause 14) |
| p08 forum | 4.E | Pass | FAIL (e1:M4, e5:M12) | NEEDS REVIEW (M11, R?) | **Step 23**, the same |
| p10 MySearchStory | 4.E | Pass | FAIL (e1:M4, e2:M3) | PASS, agrees | **Step 23**, the same |
| p07 home | 5.F, 5.G | Does Not Apply | NEEDS REVIEW (A5 G3) | DOES NOT APPLY (A3s; A1), agrees | **Step 23**: the walk reaches the drawn header search, which 5.F reads as a site search |
| p08 forum | 5.F, 5.G | Does Not Apply | NEEDS REVIEW (A2) | DOES NOT APPLY (A3s; A1), agrees | **Step 23**, the same |
| p08 forum | 5.H | Does Not Apply | NEEDS REVIEW (A2) | DOES NOT APPLY (A4), agrees | **Step 23**: the drawn form is read whole |
| p01 to p06 | 9.B | Pass | FAIL (N3, the locked run) | NEEDS REVIEW (N5, N6) | Step 31 (9.B 1.7.0, the other thread): this run is the first round 3 run of 9.B since |
| p01, p10 | 4.F | Pass | NEEDS REVIEW (o1:M9) | PASS (o1:M7), agrees | The judge answered "preserves" this time |
| p04 | 5.A | Pass | NEEDS REVIEW (c1:M6) | PASS (c1:M4), agrees | The judge answered on the search field's label this time |
| p09 SDE | 4.A | Fail | FAIL (k2:M6), agrees | NEEDS REVIEW (k2:M7, x1:M8) | The judge: J1 found another keyboard way this time, and x1 still needs a person; safer, not wrong |

On p07 and p08 the walk now reaches 76 of 76 and 91 of 91, and row WL
(step 22's "drawn late") no longer appears.

## Unsafe cells and false FAILs

No cell in either rerun is a PASS or DOES NOT APPLY that the key fails.
False FAILs on the first rerun's tests:

| Round | First rerun | Step 23 rerun | Why |
| --- | --- | --- | --- |
| 1 | 4 | 3 | -1 5.D (the first rerun's load) |
| 2 | 7 | 9 | +3 4.F (the judge), -1 5.B (the judge) |
| 3 | 9 | 6 | -3 4.E (step 23) |

**Verified** (commands above): every cell, row and key comment in
`moved.md`; that no page was fetched live; the false FAIL counts (each
round's scorer on both reruns); that p07's 4.F signals are the same in
both reruns while J1's answer differs (the two reports); that round
1's four 19.A moves come from the freeze holding no search or suggested
page (each report's sentence, and step 9b's "tested_frozen" runs in
`evals/README.md`).
**Not traced**: why round 1's p01 4.C raised no i1 this run. **Assumed**: that round 1's p06 4.F, and round 2's 4.F, 5.B and 9.C moves are the judge's
answers varying and not step 23 (the reports keep the answers, not the
question packets, so the judge's inputs were not compared byte for
byte; p02's and p03's signal lists differ by one jump each); that round
3's 4.E moves come from the address change no longer falling on the
first press (the WL rows are gone and e1 moved from M4, but the address
trace was not read press by press).
