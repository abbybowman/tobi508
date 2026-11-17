# Status counts behind the README table

Written by `evals/status_table.py`; do not edit. Agent-assisted results, not certified Trusted Tester results. "Agrees" is about our evaluation pages only.

A cell is one page and one test where a Trusted Tester's blind key gives an answer. Columns: agree; PASS or DOES NOT APPLY where the key fails; FAIL or DOES NOT APPLY where the key passes; other mismatch (the key says DOES NOT APPLY or NOT TESTED and the tool gives another outcome); left for a person (NEEDS REVIEW). The status rule, first match: red "passed a page a tester failed" (any PASS or DNA where the key fails); red "wrong more often than right" (wrong cells outnumber agreeing ones, over decided cells); yellow "often fails pages a tester passes" (wrong on more than 1 in 5 decided cells); yellow "mostly left for a person" (fewer than half the cells decided); green "agrees with a tester".

## Runs

- Round 1, www.nasa.gov: rerun on development pages, gate 2026-11-17 (step 23) over gate 2026-11-16 (step 9b).
- Round 2, svs.gsfc.nasa.gov: rerun on development pages, gate 2026-11-17 (step 23) over gate 2026-11-16 (step 9b).
- Round 3, science.data.nasa.gov: rerun on development pages, gate 2026-11-17 (step 23) over the blind round 3 (locked 2026-11-16, kept as the record in evals/judging/round3/score.md).

## Counts

| Test | Site | Cells | Agree | PASS or DNA, key fails | FAIL or DNA, key passes | Other mismatch | Left for a person |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2.A | R1 www.nasa.gov | 0 | 0 | 0 | 0 | 0 | 0 |
| 2.A | R2 svs.gsfc.nasa.gov | 10 | 7 | 0 | 0 | 0 | 3 |
| 2.A | R3 science.data.nasa.gov | 10 | 10 | 0 | 0 | 0 | 0 |
| **2.A** | **all: ✅ agrees with a tester** | 20 | 17 | 0 | 0 | 0 | 3 |
| 2.B | R1 www.nasa.gov | 0 | 0 | 0 | 0 | 0 | 0 |
| 2.B | R2 svs.gsfc.nasa.gov | 10 | 4 | 0 | 0 | 0 | 6 |
| 2.B | R3 science.data.nasa.gov | 10 | 10 | 0 | 0 | 0 | 0 |
| **2.B** | **all: ✅ agrees with a tester** | 20 | 14 | 0 | 0 | 0 | 6 |
| 2.C | R1 www.nasa.gov | 0 | 0 | 0 | 0 | 0 | 0 |
| 2.C | R2 svs.gsfc.nasa.gov | 10 | 4 | 0 | 0 | 0 | 6 |
| 2.C | R3 science.data.nasa.gov | 10 | 6 | 0 | 0 | 0 | 4 |
| **2.C** | **all: ✅ agrees with a tester** | 20 | 10 | 0 | 0 | 0 | 10 |
| 2.D | R1 www.nasa.gov | 0 | 0 | 0 | 0 | 0 | 0 |
| 2.D | R2 svs.gsfc.nasa.gov | 10 | 4 | 0 | 0 | 0 | 6 |
| 2.D | R3 science.data.nasa.gov | 10 | 6 | 0 | 0 | 0 | 4 |
| **2.D** | **all: ✅ agrees with a tester** | 20 | 10 | 0 | 0 | 0 | 10 |
| 3.A | R1 www.nasa.gov | 0 | 0 | 0 | 0 | 0 | 0 |
| 3.A | R2 svs.gsfc.nasa.gov | 10 | 6 | 0 | 0 | 1 | 3 |
| 3.A | R3 science.data.nasa.gov | 10 | 10 | 0 | 0 | 0 | 0 |
| **3.A** | **all: ✅ agrees with a tester** | 20 | 16 | 0 | 0 | 1 | 3 |
| 4.A | R1 www.nasa.gov | 9 | 0 | 0 | 0 | 0 | 9 |
| 4.A | R2 svs.gsfc.nasa.gov | 10 | 2 | 0 | 1 | 0 | 7 |
| 4.A | R3 science.data.nasa.gov | 10 | 2 | 0 | 0 | 0 | 8 |
| **4.A** | **all: ⚠️ mostly left for a person** | 29 | 4 | 0 | 1 | 0 | 24 |
| 4.B | R1 www.nasa.gov | 9 | 9 | 0 | 0 | 0 | 0 |
| 4.B | R2 svs.gsfc.nasa.gov | 10 | 9 | 0 | 0 | 0 | 1 |
| 4.B | R3 science.data.nasa.gov | 10 | 8 | 0 | 0 | 0 | 2 |
| **4.B** | **all: ✅ agrees with a tester** | 29 | 26 | 0 | 0 | 0 | 3 |
| 4.C | R1 www.nasa.gov | 9 | 6 | 0 | 0 | 0 | 3 |
| 4.C | R2 svs.gsfc.nasa.gov | 10 | 9 | 0 | 0 | 0 | 1 |
| 4.C | R3 science.data.nasa.gov | 10 | 7 | 0 | 0 | 0 | 3 |
| **4.C** | **all: ✅ agrees with a tester** | 29 | 22 | 0 | 0 | 0 | 7 |
| 4.D | R1 www.nasa.gov | 9 | 3 | 0 | 0 | 0 | 6 |
| 4.D | R2 svs.gsfc.nasa.gov | 10 | 1 | 0 | 2 | 0 | 7 |
| 4.D | R3 science.data.nasa.gov | 10 | 3 | 0 | 0 | 0 | 7 |
| **4.D** | **all: ⚠️ often fails pages a tester passes** | 29 | 7 | 0 | 2 | 0 | 20 |
| 4.E | R1 www.nasa.gov | 9 | 7 | 0 | 0 | 0 | 2 |
| 4.E | R2 svs.gsfc.nasa.gov | 10 | 8 | 0 | 0 | 0 | 2 |
| 4.E | R3 science.data.nasa.gov | 10 | 6 | 0 | 3 | 0 | 1 |
| **4.E** | **all: ✅ agrees with a tester** | 29 | 21 | 0 | 3 | 0 | 5 |
| 4.F | R1 www.nasa.gov | 9 | 3 | 0 | 0 | 0 | 6 |
| 4.F | R2 svs.gsfc.nasa.gov | 10 | 1 | 0 | 1 | 0 | 8 |
| 4.F | R3 science.data.nasa.gov | 10 | 2 | 0 | 2 | 0 | 6 |
| **4.F** | **all: ⚠️ often fails pages a tester passes** | 29 | 6 | 0 | 3 | 0 | 20 |
| 5.A | R1 www.nasa.gov | 9 | 9 | 0 | 0 | 0 | 0 |
| 5.A | R2 svs.gsfc.nasa.gov | 10 | 6 | 0 | 1 | 0 | 3 |
| 5.A | R3 science.data.nasa.gov | 10 | 2 | 0 | 3 | 0 | 5 |
| **5.A** | **all: ✅ agrees with a tester** | 29 | 17 | 0 | 4 | 0 | 8 |
| 5.B | R1 www.nasa.gov | 9 | 0 | 0 | 1 | 0 | 8 |
| 5.B | R2 svs.gsfc.nasa.gov | 10 | 6 | 0 | 2 | 0 | 2 |
| 5.B | R3 science.data.nasa.gov | 10 | 3 | 0 | 3 | 0 | 4 |
| **5.B** | **all: ⚠️ often fails pages a tester passes** | 29 | 9 | 0 | 6 | 0 | 14 |
| 5.C | R1 www.nasa.gov | 9 | 1 | 0 | 1 | 0 | 7 |
| 5.C | R2 svs.gsfc.nasa.gov | 10 | 10 | 0 | 0 | 0 | 0 |
| 5.C | R3 science.data.nasa.gov | 10 | 7 | 0 | 1 | 0 | 2 |
| **5.C** | **all: ✅ agrees with a tester** | 29 | 18 | 0 | 2 | 0 | 9 |
| 5.D | R1 www.nasa.gov | 9 | 1 | 0 | 2 | 0 | 6 |
| 5.D | R2 svs.gsfc.nasa.gov | 10 | 3 | 0 | 0 | 0 | 7 |
| 5.D | R3 science.data.nasa.gov | 10 | 1 | 0 | 2 | 0 | 7 |
| **5.D** | **all: ⚠️ often fails pages a tester passes** | 29 | 5 | 0 | 4 | 0 | 20 |
| 5.F | R1 www.nasa.gov | 9 | 0 | 0 | 0 | 0 | 9 |
| 5.F | R2 svs.gsfc.nasa.gov | 10 | 3 | 0 | 0 | 0 | 7 |
| 5.F | R3 science.data.nasa.gov | 10 | 4 | 0 | 0 | 0 | 6 |
| **5.F** | **all: ⚠️ mostly left for a person** | 29 | 7 | 0 | 0 | 0 | 22 |
| 5.G | R1 www.nasa.gov | 9 | 0 | 0 | 0 | 0 | 9 |
| 5.G | R2 svs.gsfc.nasa.gov | 10 | 3 | 0 | 0 | 0 | 7 |
| 5.G | R3 science.data.nasa.gov | 10 | 4 | 0 | 0 | 0 | 6 |
| **5.G** | **all: ⚠️ mostly left for a person** | 29 | 7 | 0 | 0 | 0 | 22 |
| 5.H | R1 www.nasa.gov | 9 | 6 | 0 | 0 | 0 | 3 |
| 5.H | R2 svs.gsfc.nasa.gov | 10 | 9 | 0 | 0 | 0 | 1 |
| 5.H | R3 science.data.nasa.gov | 10 | 8 | 0 | 0 | 0 | 2 |
| **5.H** | **all: ✅ agrees with a tester** | 29 | 23 | 0 | 0 | 0 | 6 |
| 9.A | R1 www.nasa.gov | 9 | 8 | 0 | 0 | 0 | 1 |
| 9.A | R2 svs.gsfc.nasa.gov | 10 | 10 | 0 | 0 | 0 | 0 |
| 9.A | R3 science.data.nasa.gov | 10 | 6 | 0 | 0 | 0 | 4 |
| **9.A** | **all: ✅ agrees with a tester** | 29 | 24 | 0 | 0 | 0 | 5 |
| 9.B | R1 www.nasa.gov | 9 | 9 | 0 | 0 | 0 | 0 |
| 9.B | R2 svs.gsfc.nasa.gov | 10 | 9 | 0 | 0 | 0 | 1 |
| 9.B | R3 science.data.nasa.gov | 10 | 0 | 0 | 6 | 0 | 4 |
| **9.B** | **all: ⚠️ often fails pages a tester passes** | 29 | 18 | 0 | 6 | 0 | 5 |
| 9.C | R1 www.nasa.gov | 9 | 9 | 0 | 0 | 0 | 0 |
| 9.C | R2 svs.gsfc.nasa.gov | 10 | 4 | 0 | 0 | 0 | 6 |
| 9.C | R3 science.data.nasa.gov | 10 | 6 | 0 | 0 | 0 | 4 |
| **9.C** | **all: ✅ agrees with a tester** | 29 | 19 | 0 | 0 | 0 | 10 |
| 19.A | R1 www.nasa.gov | 9 | 4 | 0 | 0 | 0 | 5 |
| 19.A | R2 svs.gsfc.nasa.gov | 10 | 2 | 0 | 0 | 0 | 8 |
| 19.A | R3 science.data.nasa.gov | 10 | 2 | 0 | 0 | 0 | 8 |
| **19.A** | **all: ⚠️ mostly left for a person** | 29 | 8 | 0 | 0 | 0 | 21 |
