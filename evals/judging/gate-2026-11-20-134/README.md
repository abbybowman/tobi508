# Gate 2026-11-20, #134 (Applications): the rerun's inputs

Agent-assisted results, not certified Trusted Tester results. Development
reruns; round 3's pages are development pages and this never replaces
round 3's blind score ([`round3/score.md`](../round3/score.md)).

## Round 3's freeze with the missing code added (step 25)

`round3-copy/frozen/` is a copy of `../round3/frozen/` (Abby's
`round3-frozen-2026-11-16b.zip`, SHA-256 `2ce3446a…`, every file checked
against `../round3/frozen-MANIFEST.sha256` before copying). The original is
not touched. Abby, 2026-11-20: add only the missing files.

Only p07's and p08's recordings changed. Their chunk stores had refused two
files as "over the size limit" (the 3 MB limit before step 25). Both were
fetched live on 2026-11-20 under the chunk store's rules (same host as the
script that names them, allowlisted, a script, no redirect, within the new
10 MB and 24 MB limits) and added to the copy, each listed in the
recording's `a11y-chunks.json` with its SHA-256 and `added`. The names
carry a build hash, so the files under them are taken to be the ones the
app used on 2026-11-16 (assumed, not verifiable).

| Recording | Page | Original SHA-256 | This copy's SHA-256 |
| --- | --- | --- | --- |
| `pages/029.har.zip` | p07 `/data-governance-community/home` | `3005f2ea62c0d713362436a3e5fd24cbf25fa52ff89ab25fe350cdfe58c23ff3` | `34e95dbc7da283d7ccaa03bc2444f3ad6e598ffe462faef86ceeefbeceb0adc2` |
| `pages/030.har.zip` | p08 `/data-governance-community/forum` | `0e2e6b93ff4112055d40662294b6364245e531936ed3ad26559b171211c4d8c4` | `26cb20bb54553d47645d14a5ae417c96165f70bbf3cbb9ef83d3581f579b7abd` |

| File added | Bytes | SHA-256 (first 16) |
| --- | --- | --- |
| `chunk-HH7OQO3D.js` | 6,878,283 | `051ef36efdece707` |
| `chunk-GCKNKALH.js` | 5,597,547 | `58d0c8080eae03d4` |

**The files those name** (Abby, 2026-11-20: raise the file and depth
limits to 300 and 5). The two files name 101 more and those one more,
fetched the same way and added level by level: p07 now holds 161 code files
(19.9 MB), p08 165 (19.9 MB), and `capture.unrecorded_code` lists none on
either. Each added file is in `a11y-chunks.json` with its SHA-256. The
recordings stay out of git (`*.har.zip`).

## The rerun (#134's "Done when")

**What ran.** `main` after #143 (steps 24, 25, 26, 35a, 35e and guard WL),
then the double read (9.A 1.9.0, 9.B 1.9.0, 9.C 1.12.0, 19.A 1.17.0) for
round 3's site tests. `evals/apijudge_gate.py run --round 3|2|1
--frozen-mode replay`, tests 4.A, 4.B, 4.C, 4.E, 4.F, 5.A to 5.D, 5.F, 9.A
to 9.C and 19.A, the server judge on gate 9c's 21 types (CLI route,
`claude-sonnet-5-5`, prompt `e8320f2c…`), Playwright's Chrome 153.0.8010.12
(the pinned build; this container's own is 157, #142). One round at a time.
Round 3 from `round3-copy/` (above); its 9.A to 9.C and 19.A again, with the
double read, into `round3-site/`. Every page and other page came from the
freeze; nothing was loaded live. Round 1 ran in two launches (a job time
limit after p02), and p05, p06, p07 and p09 again after their judge calls
failed (14 questions left open; none failed the second time).

**Compared with** gate 2026-11-17-9c's real run (`compare-roundN.json`,
`sides.real`), by each round's own keys and scorer: `compare.py`, every
moved cell in `moved.md` (`moved.json`). Gate 9c ran "tested_frozen" (19.A's
search and suggested pages live); this rerun ran "replay", which has
neither, so 19.A moves on rounds 1 and 2 are the mode, as in step 23's rerun.

**No cell anywhere is a PASS or DOES NOT APPLY where the key fails.**

| Round | Moved | Toward the key | Away from it (to NEEDS REVIEW) | Why |
| --- | --- | --- | --- | --- |
| 3 | 11 | 10 (9 from NEEDS REVIEW, 1 false FAIL) | 1 (5.B p04: judge unsure) | #134: 4.B p07, p08 (step 25), 5.B p09 and 5.C p09, p10 (35a), 19.A p07 and 9.B p10 (26); the judge: 4.F p01, 5.A p04, 5.B p05 |
| 2 | 13 | 3 (9.C p01, p07; 4.F p02 false FAIL) | 10 (19.A p01, p02, p05 to p10; 9.C p03, p06) | 19.A: the replay mode (no search, no suggested pages; CILab's alias has no saved copy); 9.C and 4.F: the judge (C6 unsure, M7) |
| 1 | 6 | 1 (4.C p05) | 5 (19.A p01, p04, p06, p08; 4.F p07) | 19.A: the replay mode; 4.F: the judge (M9) |

**Round 3's cells the issue names, now.** 4.B p07, p08: PASS (key Pass).
5.B p09, 5.C p09, p10: PASS (key Pass). 19.A p07: PASS; 9.B p10: PASS (key
Pass). 9.A p07 to p10, 9.B p07 to p09, 9.C p07 to p10, 19.A p08 to p10:
NEEDS REVIEW, no longer A2: the skip-link question (9.A M1, M5), only one
shared control (9.B N5), nothing shared with the main site's pages (9.C
A3o), closed menus and no search in the freeze (19.A W8, W9, W4). 4.C p07 to
p09: NEEDS REVIEW by guard RC (a menu the walk did not finish: "User menu
for Guest User", "All"), no longer "did not finish (navigation)". 4.E p07,
p08: NEEDS REVIEW (M11 and R?: profile cards marked modal, row M12's ground,
and the time budget).

**Found and fixed on the way.** The first round 3 run said DOES NOT APPLY
for 9.A on the forum (p08) where the key fails: one read of the community
home page, as another page, lacked part of its header and was kept for the
session. Rerun alone five times it was NEEDS REVIEW each time. The double
read (an other page drawn late is read twice and left out when the reads
share less than 90% of their texts) fixed it: NEEDS REVIEW in `round3-site/`.
A first version that required identical reads left the forum out (its tag
cloud shows two more tags on one load) and cost p07's 19.A its PASS.

Files: `compare.py`, `moved.md`, `moved.json`, `roundN/run.json`,
`roundN/gate.json`, `round3-site/run.json`; page reports stay out of git.
