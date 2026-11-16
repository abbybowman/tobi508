# Round 3: what is in git and what is in the archive

Round 3 is a formal blind round on 10 pages of science.data.nasa.gov, run
with the server judge answering. Agent-assisted results, not a certified
Trusted Tester result for the pages.

Page recordings (`*.har.zip`) are not in git. Each page's `report.json` and
`pre-scrt.json` are, as in rounds 1 and 2. This file sits at the round's root,
not in `results/`, so that the lock (which covers `results/`) stays as it was
made. The recordings are in two zips Abby keeps, with their SHA-256 here.

| Set | Size | SHA-256 | Restore |
| --- | --- | --- | --- |
| `round3-frozen-2026-11-16b.zip` (the frozen pages the run used) | 39 MB | `2ce3446ab1a4ab1d25b8b7dad5b595ffea2550cb70fa5ba8c239ede0f20a708c` | unzip into `evals/judging/round3/` (it makes `frozen/`); then, from inside `frozen/`: `sha256sum -c ../frozen-MANIFEST.sha256` |
| `round3-results-2026-11-16.zip` (what the tool saw: 142 recordings, plus each page's report and pre-SCRT) | 250 MB | `01414e0e3223c0e8626c26c98e4d6fd2702ed2508f6417942c00d74ba036b35a` | unzip at the repository root: files land at their paths; `judging.py score` checks every recording against `results/lock.json` |

The first freeze's zip (`round3-frozen-2026-11-16.zip`, SHA-256
`2a1b1bfb628a58eb39d8f2aeceb8e58a511647a9151ff3c67f262d77563f9e00`) is
superseded: its p07 and p08 recordings replayed incompletely. Its manifest is
in commit 9966927, its `freeze.json` in 247d4a4.

## What was done

Code: `main` at ece881b (#98, #97) merged into `claude/round3-run`. The
branch holds only round files.

1. **First freeze** (247d4a4): 10 pages and 18 site searches, all HTTP 200.
   p07 (`/data-governance-community/home`) and p08 (`/forum`) replayed
   incompletely: p07 21 of 152 live lines, p08 130 of 149. Their recordings
   stopped before the app had fetched its data.
2. **Refreeze** of p07 and p08 only, with #96 (p07 still 27 of 152 lines), then
   with `record_extra_wait_ms=30000` (#98, 9bd8d6a, Abby approved the code
   change). Replay against live, first 30 s: p07 127 lines both, identical;
   p08 123 both, two tag labels differ (live: Open Data Act, SMD Governance
   Thesaurus; replay: Earthdata Search (EDS), Science Discovery Engine (SDE)).
   No failed request, popup, dialog, frame or media on either side. The other
   8 pages and 18 searches are byte-identical to the first freeze.
3. **Run:** `uv run python evals/judging.py scan evals/judging/round3` with
   FROZEN_PAGES_DIR=`<repo>/evals/judging/round3/frozen`,
   FROZEN_PAGES_MODE=tested_frozen, UPSTREAM_PROXY=$HTTPS_PROXY,
   BROWSER_CHANNEL=chromium, HEADLESS=true, JUDGE_BACKEND=api,
   JUDGE_ROUTE=cli, JUDGE_MODEL=claude-sonnet-5-5, RUN_TTL_HOURS=720 and
   JUDGE_TYPES=2.A,2.B,2.C,2.D,3.A,4.A,4.B,4.D,4.E,4.F,5.A,5.B,5.C,5.D,5.F,5.G,5.H,9.A,9.B,9.C,19.A
   (the 21 types of gate 9a; 4.C stays with the client). All 10 pages done in
   round 1, none open. The server judge (prompt SHA-256 `e8320f2c1a18…`)
   answered 132 questions in 41 calls: no failed, invalid, rejected or
   left-open call; 18 it was unsure of stay NEEDS REVIEW. No packets were
   written, no agent opened anything, and no empty answers file was applied
   (`judging.py apply` found no open page). No second judge, no fresh agent.
4. **Lock:** first at 18701fc, then again (d51f7ef) so that each page's report
   and pre-SCRT could be committed like earlier rounds (Abby approved; no key
   existed). Every file hash equals the first lock's; only the split between
   files git keeps and files it ignores changed.

The keys were not opened before the lock.
