# Gate 2026-11-21, #136 (4.A and 4.F): the rerun

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the rounds' pages; it never replaces any round's blind score.

## What ran

The branch after #136's four steps: 4.A 1.17.0 (step 28's execute check, the
smooth-scroll fix, step 32's hover scan and hidden helpers) and 4.F 1.14.0
(steps 33a, 33b and 33c). `evals/apijudge_gate.py run --date 2026-11-21-136
--round 3|2|1 --tests 4.A,4.F --types 4.A,4.F --frozen-mode replay`, the
server judge (CLI route, `claude-sonnet-5-5`), Playwright's Chrome
153.0.8010.12 (the pinned build; this container's own is 157, #142). One
round at a time, each exited 0.

- Round 3 from its original freeze (`../round3/frozen/`), not #134's
  `round3-copy/`: this rerun's pages (p09, p10) were never short of code.
- Every page came from the freeze; nothing was loaded live.
- Each round's `run.json` is here; `results/` and `runs/` stay out of git.

## Compared with

Gate 2026-11-17-9c's real run, by each round's own key and scorer:
`compare.py`, every moved cell in `moved.md` (`moved.json`).

## What moved

No PASS against a FAIL key, in any round.

| Round | Page | Test | Key | 9c | Now | Rows now |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | p01 | 4.F | Pass | NEEDS REVIEW | PASS | `o1:M7[S3 x6] G5` |
| 3 | p02 | 4.F | Pass | NEEDS REVIEW | PASS | `o1:M7[S3 x2] G5` |
| 3 | p04 | 4.F | Pass | FAIL | NEEDS REVIEW | `o1:M7[S3 x3] r6:M9[S6] G3` |
| 2 | p01 | 4.F | Pass | NEEDS REVIEW | PASS | `o1:M7[S3 x25, S4] r1-r4:M4 G5` |
| 2 | p02 | 4.F | Pass | FAIL | PASS | `o1:M4 r1:M4 G5` |
| 2 | p04 | 4.F | Pass | NEEDS REVIEW | PASS | `o1:M7[S3] G5` |
| 2 | p10 | 4.F | Pass | NEEDS REVIEW | PASS | `o1:M4 G5` |
| 2 | p03 | 4.A | Pass | NEEDS REVIEW | **FAIL** | `t12:M14`, see below |

The 4.F moves are steps 33a to 33c together (the order question now shows
every stop its signals name and says an odd order that keeps meaning
preserves it; footer columns and arrow-key menus are no signal). Which step
moved which cell was not traced. Round 3 p04 keeps one arrow-key widget
open (`r6:M9[S6]`).

Round 1: no cell moved.

**Round 3 p10 (4.A, key Fail)** did not move: it was FAIL before by other
rows. It now also fails on "Submit Your Story" and "SEARCH" (`x3`, `x4`:
M10g): a click opens the story form and the search results, while the
carousel takes their Enter and Space. Round 3 p09 (key Fail) stays NEEDS
REVIEW, never PASS: the judge answered "unsure" whether anything Tab
reaches does what "Search Stories" does (`k2:M7`). The key's other 4.A
row, the "All" dropdown's options, is inside opened content, which 4.A
does not read yet (step 15).

**Round 2 p03 (4.A, key Pass) is a new wrong FAIL.** 9c ran out of time
before the hover scan reached the sort button; with step 32's budget it
reaches it. The button's `title` is "Toggle sort direction", its accessible
name "Toggle order; currently descending order". The title check counts a
title as available elsewhere only when it equals the name or is in the
page's text, so J2 was asked, and the judge answered "essential" ("the
button shows only a sort icon; the tooltip is its only visible label"):
M14, FAIL. The title says the same thing as the name in other words. A rule
or rubric change for that needs Abby's decision and a judge eval; it is not
in #136's scope and is left open (reported on #136).

Unchanged wrong FAILs: round 2 p01 4.A (the home page's category icon
links; Abby retests it) and round 2 p08 4.F (as in 9c).

## Later (2026-11-22)

- Round 2 p01 4.A: Abby's retest found the key's Pass a slip (the category
  icon links); recorded in round 2's `adjudications.json`, so the tool's
  Fail now scores as agreeing.
- Round 2 p03 4.A (the sort button) and p08 4.F: fixed on this branch; see
  `../gate-2026-11-22-136b/README.md` and `../gate-2026-11-22-136d/README.md`.
