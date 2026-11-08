# Round 2, Agent C: what is in git and what is in the archive

Agent C's first round (copies of Agent A's unanswered tool runs, and three
fresh TOBI runs) and its three repeats, with their recordings, screenshots
and evidence, are in archive sets Abby keeps (2026-11-08), made before the
lock and before any answer key.

Each set is one zip cut into parts of 25 MB or less (`<set>.zip.001`,
`.002`, ...), with `SHA256SUMS.txt` (each part and the rejoined zip) and
`MANIFEST-<set>.json` (the SHA-256 of every file in it). Rejoin the parts
(`copy /b <set>.zip.0* <set>.zip` on Windows, `cat` elsewhere, or open
`.001` in 7-Zip) and unzip at the repository root: files land at their
paths. Parts were checked before handing over: the rejoined zip matches its
hash and passes `unzip -t`.

To keep the sets small, a file over 100 kB that is byte-identical to one in
an earlier set is left out and listed in the manifest's `same_as` with the
path of its twin (`reference_dirs` names where they were looked for): copy
that file to restore it. `_page_cache/` folders (the server's cache of
recordings) are left out entirely. So restore in this order.

1. round 2's sets first (`evals/judging/round2/results/ARCHIVE.md`): the
   first round's copies of Agent A's runs point there;
2. `round2-armc-first-round`;
3. the three `round2-armc-arm-c-*` sets: each repeat started from a copy of
   the first round, so most of its evidence points there.

| Set | Parts | Size | SHA-256 of the rejoined zip | SHA-256 of its manifest |
| --- | --- | --- | --- | --- |
| `round2-armc-first-round` | 4 | 84 MB | `ef49146186308bc4a6c9a8e81fcd88795db42d91476f14aed38ba46374a7a7b2` | `8e19aba4376c0c6bcc4b1c79fb37f62bf1d9928e5ff2057364b5d052ff2fbdb0` |
| `round2-armc-arm-c-1` | 3 | 66 MB | `33ebc107735fca4a19952e3d6547ee2f8b7f6904cb9eedff684a15b0756c35a1` | `14ba0251aa12f2fd3b38e09c94336f4d29f4862e54a41ba63feb85f24d663533` |
| `round2-armc-arm-c-2` | 3 | 64 MB | `63ba0db59fc058a9e5534402a5ec1560ad11d75635fb2ec96bd5919a91eb0595` | `194c31b0b96433ec2b872eedd4e7bf938f10acccdd235e9a6370290ec155afd8` |
| `round2-armc-arm-c-3` | 3 | 63 MB | `453e0828ee5a959a43246aee6393fd3b1fa4e9c99e34b494d71d3e7ae705a7a6` | `28f05b4af91f1fa2e02eb9c2a605815ecf64c2c3829139bf2f4ebf33b55dd129` |
