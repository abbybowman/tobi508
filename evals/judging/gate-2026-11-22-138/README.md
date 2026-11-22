# Gate 2026-11-22, #138 (site tests): the rerun's inputs

Agent-assisted results, not certified Trusted Tester results. Development
reruns; never in place of a round's blind score.

**In progress (2026-11-22).** Each `roundN-copy-frozen/` is a copy of
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
The added recordings, with their hashes, are listed here when it ends.
Recordings stay out of git (`*.har.zip`).
