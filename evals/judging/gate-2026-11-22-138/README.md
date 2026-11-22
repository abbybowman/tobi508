# Gate 2026-11-22, #138 (site tests): the rerun's inputs

Agent-assisted results, not certified Trusted Tester results. Development
reruns; never in place of a round's blind score.

**Done (2026-11-22).** Each `roundN-copy/frozen/` is a copy of
Abby's frozen archive for round N, checked before copying (round 1's zip
`768b8f5f…` and round 3's `2ce3446a…` match their `ARCHIVE.md`; round 3's
30 files its `frozen-MANIFEST.sha256`; round 2's 12 parts and rejoined
zip `8115fde0…` the zip's own `SHA256SUMS.txt`, its 12 files the zip's
manifest; each `index.json` was git's). Round 3's copy starts from the
original freeze, not #134's copy with the added code files (not in the
archive folder; 9.A to 9.C and 19.A do not use them). The originals are not
touched.

19.A (1.21.0) is being run alone on every page in `record_missing` mode,
which records live (2026-11-22) and adds to the copy only what the freeze
lacks: suspected aliases, suggested pages, listed pages and the searches.
Every recording 19.A added, with its SHA-256, is in [`ADDED.md`](ADDED.md);
every recording in the three copies was checked intact (zip test). Round 1
p07 was run a second time (its first run's browser closed after 19.A had
collected). With these, a replay rerun decides 19.A on everything the
2026-11-22 runs loaded, the searches included, from the copy. Recordings
stay out of git (`*.har.zip`).

## The rerun (#138's "Done when")

**What ran.** This branch after all of #138's steps (19.A 1.21.0, 9.A
1.10.0, 9.B 1.11.0, 9.C 1.14.0) with `main` (#152) merged in.
`evals/apijudge_gate.py run --round 3|2|1 --tests 9.A,9.B,9.C,19.A
--frozen-mode replay --frozen-dir gate-2026-11-22-138/roundN-copy`, the
server judge on gate 9c's 21 types (CLI route, `claude-sonnet-5-5`), one
round at a time. Every page came from the freeze copies; nothing was loaded
live. 19.A's searches, suggested pages, listed pages and aliases were served
from what the copies recorded live on 2026-11-22 (`ADDED.md`), so the mode
Abby chose (replay, with a `tested_frozen` run of 19.A alone for the search
cells) collapsed into one replay: the copy holds those live loads. Browser:
this container's Chromium 157.0.8103.78, not the pinned 153 #134's rerun
used (#142). Round 1 ran twice: its first run paired search-filter
checkboxes by first word (9.C on p02 and p05, NEEDS REVIEW where the key
passes), steps 5 and 6 were narrowed to buttons, and round 1 ran again;
rounds 2 and 3 had no pair from those steps, so they stand.

**Compared with** gate 2026-11-17-9c's real run (`compare-roundN.json`,
`sides.real`), by each round's own keys and scorer: `compare.py`; every
moved cell, with #134's rerun beside it, in `moved.md` (`moved.json`).
Page reports stay out of git.

**Every cell of 9.A, 9.B, 9.C and 19.A, now against gate 9c.** No PASS or
DOES NOT APPLY where a key fails, in any round.

| Round | Agree | Left for a person | Wrong FAIL |
| --- | --- | --- | --- |
| 3 | 14 → **29** | 26 → 11 | 0 → 0 |
| 2 | 33 → **35** | 6 → 5 | 1 → **0** (CILab) |
| 1 | 30 → **31** | 6 → 5 | 0 → 0 |

**Moved: 20 cells, 19 toward the key.**
- Round 3 (15, all toward the key): 9.B p01 to p10 PASS (microsite pages
  left out as another part of the site; each microsite compared within
  itself, as the key's comments say); 19.A p01, p02 (breadcrumbs), p03 (a
  content link on a page the search by the menus' name lists), p04 (topic
  tags to other searches of the results page) and p07 PASS.
- Round 2 (4): 19.A p05 CILab FAIL → PASS (the `index.html` alias by its
  drawn text; the icon row compared around the link); 9.C p07 and p10
  NEEDS REVIEW → PASS; **9.C p09 PASS → NEEDS REVIEW**: two "Go to this
  page" links paired by name (step 3, unchanged here), different
  descriptions, the judge unsure this time (gate 9c and #134 decided
  them): the judge's variation, not a rule.
- Round 1 (1): 19.A p09 (the KSC history gallery) NEEDS REVIEW → PASS
  (the search, recorded in the copy, and its links).

**Round 3's application pages** (p07 to p10) ran from the original freeze,
not #134's copy with the code files the community pages load when used
(not in the archive folder). Their 9.A and 9.C cells did not move; 9.C on
MySearchStory says DOES NOT APPLY on this freeze (key Pass), also on `main`:
the app does not draw its navigation without that code. Not comparable
with #134's rerun for those cells.
