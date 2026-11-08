# Round 2: what is in git and what is in the archive

Page recordings (`*.har.zip`), screenshots (`*.png`) and tool evidence
(`runs/*/evidence/`) are not in git. They are in archive sets Abby keeps
(2026-11-08), made before the lock and before any answer key.

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

1. `round2-frozen` (the frozen pages);
2. the `round2-results-*` sets and `round2-attempts`, in any order;
3. then Agent C's sets (`evals/judging/round2-armc/ARCHIVE.md`).

| Set | Parts | Size | SHA-256 of the rejoined zip | SHA-256 of its manifest |
| --- | --- | --- | --- | --- |
| `round2-frozen` | 12 | 301 MB | `8115fde06a0af0b078e4145219a1a80a37cbd53da8481cc83c141e33989ff111` | `1a885833704065ff2fac4edb3e855ccbdbe6f08df55843371eaea07fadb89b38` |
| `round2-results-arm-a-g1-1` | 7 | 180 MB | `de28bed36997bbfbf495da5835b2e96fd516af18aaf770115d72cce9d23935aa` | `b0bf85967647df9cba6835e4470c6d0f3779380a13af70b58ed28bc9278be719` |
| `round2-results-arm-a-g2-1` | 4 | 79 MB | `4811d11d813f1ccbe72c993a3bb21c8e36a4cd7a84aedf426d48208ad3a6a722` | `9c5dde5b20c6c5f4299833572b0a68a3cd7fd56ff077bf3f161099b18a518abc` |
| `round2-results-arm-a-pair1-2` | 3 | 59 MB | `444f13a29999de314932329b43ccf5c48d1e742b4ac5c6327041aa7ead00d514` | `ec34363c69d594784e7b2cdb7527a2ba522a712bb408cfd669decf0f31acc053` |
| `round2-results-arm-a-pair2-2` | 5 | 130 MB | `5f6a62e8560c4965bdac8a004259bd6b8d225ea0368297d1eb0318c7525fc7ff` | `06d28126da0cd4294f96e97a14efbde4c4010f3e7f7cabbfaffb75e9ff361d09` |
| `round2-results-arm-a-pair3-2` | 3 | 60 MB | `bddd9091927956a42896b2fbed00fc290eff0e5038e60c9d9edda713c57297b5` | `0c09ee52b14475e5cc2a5bb77782d6b9df046b0a837ba0c6aa9d8b2b3286101e` |
| `round2-results-arm-a-pair4-2` | 2 | 44 MB | `9293f8a11fceaaf4b527a8fd14fc97af44a658eaceed1cf6062e18d4d5cc5adf` | `a709e855c31665e3840012593b3c65edb697d1c309f3ccd70d4f8a91e2404512` |
| `round2-results-arm-a-pair5-2` | 2 | 41 MB | `30612d096fe32748fb9ba0c7178383f01a7d8d6bc73bfbe8d6db3842f9a83bef` | `89b0189dfafeeb16130a91b6bac0b58a8b7a5f29e6e3fae843953dce7f12e85a` |
| `round2-results-arm-b-g1-1` | 1 | 2 MB | `622fe6f8e50bdb06f17fc7a16d0aaaff82c60c6c1a08e79761d2ce50e2250793` | `88fbf923315bbd6221ff8eb1372c66944538db4d0c985ae35cacafce01d90b23` |
| `round2-results-arm-b-g2-1` | 1 | 0 MB | `ad5d98e0e2b785fa0d3ebdcaa662f03fdcc69ce4149d174026b9917b7917c33c` | `e784d3da50f3afa0305d97b89ce3f199ab6d5bb430663b7cec2880b97ca69fab` |
| `round2-results-arm-b-pair1-2` | 1 | 0 MB | `d6dd504f31916eca36cbfe1060f0d7e65ca40ce9889d02a865d7d2a0e244f742` | `76d49987e1fa8a455526543ecb9e71a1ab7196ca0747b7ab791d907625fc944d` |
| `round2-results-arm-b-pair2-2` | 1 | 0 MB | `b4c9193c588558027655b9a1f9952f82bbc8b2620de25929ebb914c6c8f2ff22` | `b60d9dae9deac4c17a1aa620c95d72934c65a2d4972da4054c46a1907039e344` |
| `round2-results-arm-b-pair3-2` | 1 | 7 MB | `f5480d336e36db9483ad721ba1d0008c420b12ce4a3bcf3f3cac746bbea7ea7e` | `9d8e4086f05b359b80ec07446545424a5eba5a6a04d5ca58797bf0fe7d44449f` |
| `round2-results-arm-b-pair4-2` | 1 | 0 MB | `4f95db7c585d8664c69b73011bd2c32d84fa2f9ac2491ce37cf6673faf7245a0` | `97571378f09b30c4d3f73a2275ec47622e88969e625c1beff44fed5fb7c340c9` |
| `round2-results-arm-b-pair5-2` | 1 | 0 MB | `d49c3da7b4308f251f388f41fd13ca63540bba20d07c8bacd767f3303e9c1919` | `22dd3f0de4009bfe37c0b77bb1ea1e874f0832d907641346a63fc9eb55862cdb` |
| `round2-attempts` | 7 | 160 MB | `1f84c07121f9116391e97e07545327931e5b174b40f2cf92eab64bccf95ea590` | `155c4078bf555ddd8ce57ccb7fcf8b06fa426e2d5b72800ef8ed904e85564752` |

What stays in git is what scoring and an audit read: each arm's
transcript, step log, summary, final message and debrief; each tool run's
`report.json`, `pre-scrt.json` and `steps.jsonl`; the frozen index; and,
after it, the lock.
