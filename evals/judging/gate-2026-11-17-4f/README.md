# Gate 2026-11-17, 4.F 1.11.0: 4.F on all three rounds after its fix

Agent-assisted results, not certified Trusted Tester results. Development
reruns on all three rounds' frozen pages; round 3's pages are development
pages and this never replaces round 3's blind score.

**What ran.** Branch `claude/relaxed-newton-qsekfu-4f-order` (4.F 1.11.0
on `main` after #117). `evals/apijudge_gate.py run --round 1|2|3 --tests
4.F --frozen-mode replay`, the server judge on step 9b's 21 question types
(CLI route), one round at a time (2, then 3, then 1). Every page from the
freeze; no report lists a page fetched live. Each round's `run.json` is
here; page files stay out of git.

**Compared with.** Step 23's rerun ([`gate-2026-11-17-step23`](../gate-2026-11-17-step23/)),
which ran 4.F on `main` before this fix. `compare.py --new
gate-2026-11-17-4f --old gate-2026-11-17-step23 --tests 4.F`; the table
with rows and key comments is [`moved.md`](moved.md).

## 4.F's cells

| Round | Before (step 23 rerun) | After |
| --- | --- | --- |
| 1 (9 pages) | 5 agree, 4 NEEDS REVIEW | 8 agree, 1 NEEDS REVIEW |
| 2 (10 pages) | 2 agree, 4 NEEDS REVIEW, **4 false FAIL** | 4 agree, 4 NEEDS REVIEW, **2 false FAIL** |
| 3 (10 pages) | 4 agree, 4 NEEDS REVIEW, 2 false FAIL | 3 agree, 5 NEEDS REVIEW, 2 false FAIL |

No false PASS and no wrong DOES NOT APPLY in either run. Every moved cell
was decided by the judge's J1 answer: no page reached PASS with no
question asked.

## Every moved cell

| Round | Page | Key | Before | After | Cause |
| --- | --- | --- | --- | --- | --- |
| 1 | p01, p05, p07, p09 | Pass | NEEDS REVIEW (J1 unsure) | PASS, agrees | Fewer signals: S3s from the race gone, and on p01 and p07 the false S4 (a script-made id) too (11 to 7, 16 to 11, 15 to 14, 8 to 4), and the judge answered "preserves" |
| 1 | p06 | Pass | PASS | NEEDS REVIEW (J1 unsure) | The judge, on fewer signals (8 to 7) |
| 2 | p02 help | Pass | **FAIL** | PASS, agrees | **The fix**: 5 signals to 1 (the footer's two columns) |
| 2 | p03 search | Pass | **FAIL** | NEEDS REVIEW | **The fix**: 6 signals to 3 (the date field's misplacement gone); the judge unsure on the facet sidebar, the footer and a real Shift+Tab difference ("Back to top") |
| 2 | p07 | Pass | **FAIL** | NEEDS REVIEW | **The fix**: 11 signals to 1 (footer columns); the judge unsure |
| 2 | p01 home | Pass | NEEDS REVIEW | PASS, agrees | Fewer signals (38 to 27); the judge answered "preserves" |
| 2 | p09 | Pass | NEEDS REVIEW (12 signals) | **FAIL** | The judge, on the 5 signals left in an interactive sky map: it read the map's popup links and panels as reached in a jumbled order. Not a measurement error (the signals are the map's own controls) |
| 3 | p01 | Pass | PASS | NEEDS REVIEW | The judge unsure on the same 8 signals |

Still wrong: round 2's p08 (a tab widget; FAIL in step 9b and step 23's
rerun too) and p09 above; round 3's p04 and p09 (unchanged). These are
the judge on widgets, not signals the fix touched.

**Verified** (commands above): every cell, row and key comment in
`moved.md`; no page fetched live; the counts by each round's scorer; on
round 2's p02, p03, p07 and p10, each signal list the same in two runs
alone, before and after (no judge). **Assumed**: that round 1's p06,
round 2's p09 and round 3's p01 moved by the judge's answer and not by
the fix (their remaining signals are the page's own; not rerun alone).
