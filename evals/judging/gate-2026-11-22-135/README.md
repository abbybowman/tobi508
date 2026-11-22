# Gate 2026-11-22-135, #135 step 27: 4.D 1.11.0 on all three rounds

Agent-assisted results, not certified Trusted Tester results. A development
rerun on the rounds' frozen pages; it never replaces any round's blind score.

## What ran

This branch with 4.D 1.11.0 (a change counts toward M6 only when confirmed
both ways, against a before picture; otherwise J1 looks with the before
picture as image D; the region 16 px) and `main` (#153) merged in.
`evals/apijudge_gate.py run --date 2026-11-22-135 --round 3|2|1 --tests 4.D
--types 4.D --frozen-mode replay`, the server judge (CLI route,
`claude-sonnet-5-5`), this container's Chromium 157.0.8103.78 (not the
pinned 153, #142), one round at a time.

- The freezes are Abby's archives, each checked before use: round 1's zip
  `768b8f5f…` and round 3's `2ce3446a…` match their `ARCHIVE.md`, round 3's
  files its `frozen-MANIFEST.sha256`; round 2's 12 parts and rejoined zip
  `8115fde0…` its `SHA256SUMS.txt` and manifest. Not #134's round 3 copy
  with p07's and p08's added code (not in this container): those two pages
  stay NEEDS REVIEW by guard GU, as in gate 9c.
- Every page came from the freeze; nothing was loaded live.
- The pages that need replays for before pictures (round 2 p01, p06 to p10;
  round 1 p01, p02, p06) were run again with the final code (replays at most
  5 and 60 s a page, each bounded by the test's time; commits 044f493,
  77b4b23), so every cell here is from that code. Each `run.json` is the
  last call's record. Round 1 p07 (NACA at 110) ran out of 4.D's 120 s once,
  under load, and finished in 55 s when run again (FAIL, as the key);
  not reproduced since.
- Results and runs stay out of git; the reports are in the round folders
  locally.

## Compared with

Gate 2026-11-17-9c's real run, by each round's own key and scorer:
`compare.py`, every moved cell in `moved.md` (`moved.json`).

## What moved

One cell, and it now agrees with the key. No PASS against a FAIL key, in
any round.

| Round | Page | Key | 9c | Now | Rows now |
| --- | --- | --- | --- | --- | --- |
| 3 | p02 blog | Fail | NEEDS REVIEW (`G4 RC`: every instance M6, held only by guard RC) | **FAIL** (agree) | 10 x `M10` (the "Image" links), 71 x `M6`, `G2` |

The 10 "Image" links: 46-60 strongly changed px each, none changed both
ways; J1 (server judge) "no" on each: "Dashed outline only in A, so it
belongs to the next element. B and D look the same." The alt-text links,
whose faint dashed outline the key does not fail, keep M6.

Rounds 1 and 2: no cell moved. Round 2's two 4.D false FAILs (14592, 5340)
are gate 9c's, unchanged (#135 lists them; not in step 27).

4.D now: round 3 agree 4, needs review 6; round 2 agree 1, false FAIL 2,
needs review 7; round 1 agree 3, needs review 6.

Judge eval for J1's new input: `../../README.md` run 42, results in
`judge-eval-4d/`.
