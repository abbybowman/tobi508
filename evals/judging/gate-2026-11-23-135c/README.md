# Gate 2026-11-23-135c, #135: 4.D 1.13.0 on all three rounds

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the rounds' frozen pages; it never replaces any round's blind score.

## What ran

This branch with 4.D 1.12.0 (a P2 stop that P1 reached under another path is
P1's; an element its own container clips is not covered) and 1.13.0 (step 15:
the stops inside opened content are instances, guard RC narrowed to
`reveal-walk`, J1's image B marked). `evals/apijudge_gate.py run --date
2026-11-23-135c --round 3|1|2 --tests 4.D --types 4.D --frozen-mode replay`,
the server judge (CLI route, `claude-sonnet-5-5`), Chromium 157.0.8103.78
(not the pinned 153, #142), one round at a time. The freezes are Abby's
archives, checked as in `../gate-2026-11-22-135/README.md`; every page came
from the freeze, nothing was loaded live. No page ran 4.D out of its time.

## Compared with

Gate 2026-11-17-9c's real run (`compare.py`, `moved.md`, `moved.json`), and
step 27's rerun (`../gate-2026-11-22-135/`, with `../gate-2026-11-22-135b/`
for round 2's p06 and p08).

## What moved against gate 9c

No PASS against a FAIL key, in any round.

| Round | Page | Key | Gate 9c | Now | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | p02 search | Pass | NEEDS REVIEW (`G4 RC`) | **PASS** (agree) | The header menu's opened items pass (34 M6; 5 with no before picture, J1 yes) |
| 1 | p03 accounts form | Pass | NEEDS REVIEW (`G4 RC`) | **PASS** (agree) | The same |
| 2 | p06 SVS 14592 | Pass | FAIL (false) | NEEDS REVIEW | 1.12.0: the video player's controls are no longer counted twice |
| 2 | p08 SVS 5340 | Pass | FAIL (false) | NEEDS REVIEW | 1.12.0: a tab its own tab list clips is M4, not covered |

Against step 27's rerun, also: **round 3 p02 (the blog, key Fail) FAIL to
NEEDS REVIEW.** The 10 "Image" links are the same (none changed both ways);
the judge answered all 10 "unsure" this time ("B shows no change; dashed
outline only in A ... Unclear whose it is"), where step 27's rerun had "no".
Run once more (outside this folder, 2026-11-23) it answered "no" to all 10:
FAIL, as the key. A judge variation, safe either way (never PASS). A rubric
line making "no change in B" a "no" was weighed and not made: round 2's
"unsure" answers include stops whose picture is not where 4.D measured the
element ("the magenta box is over the video area, not on the button", SVS
14592; "blank area below the button", SVS 4914), which that line would turn
into FAILs on pages the key passes.

Round 3 p03 to p05 (key Pass) stay NEEDS REVIEW, now by their own instances
rather than guard RC: the header menu's 19 items whose 1 px dashed outline
the dropdown clips (M4) and 5 J1 "unsure" (a menu that closes when focus
leaves gives no before picture, and its last item's off picture shows the
page under it).

4.D now: round 3 agree 3, needs review 7; round 2 agree 1, needs review 9;
round 1 agree 5, needs review 4.

Judge eval for J1's new input (image B marked): `../../README.md` run 43,
results in `judge-eval-4d/`.
