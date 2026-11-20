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
