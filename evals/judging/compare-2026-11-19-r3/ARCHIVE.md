# Compare 2026-11-19: what is in git and what is not

Development pages (round 3's 10 science.data.nasa.gov pages); a rerun that never
replaces round 3's blind score. Agent-assisted results, not certified Trusted Tester
results. The figures are in `compare.md` and `compare.json`; `compare.py` makes both
from the files below (`uv run python evals/judging/compare-2026-11-19-r3/compare.py`),
and `tests/test_compare_r3.py` checks that the committed `compare.json` is what it
computes.

## In git

| Path | What |
| --- | --- |
| `pages.txt`, `frozen-MANIFEST.sha256`, `frozen/index.json`, `frozen/freeze.json` | round 3's page list and freeze records, copied from `evals/judging/round3/` (read only there). `pages.txt` SHA-256 `752b14e4…` equals round 3's. |
| `results/c/r1`, `r2`, `r3`: `results/pNN/report.json`, `timing.json` | the server judge's three repeats, one report per page (`run.json` has the settings). `pre-scrt.json` is **not** kept (30 MB, derivable): `compare.py` rebuilds it from `report.json` with `scrt.from_report`; only the report hash line and the inlined pictures differ from the file the run wrote (checked on r1 p01: 2,590 of 2,591 lines identical). |
| `results/arm-a-gG-R`, `results/arm-b-gG-R` (G = group 1-5 of 2 pages, R = run 1-3) | each group's `summary.json`, `final.md`, `debrief.md`, `steps.jsonl`; arm A also `runs/<id>/report.json` and `pre-scrt.json` (the tool's own output per page). |
| `transcripts-no-images.zip` (2.2 MB, SHA-256 `3f62540d…`) | all 30 `transcript.json` with each picture's base64 bytes replaced by a marker (the tool calls, results text and image-block counts `compare.py` reads are unchanged: the stats are identical from the zip and from the full files). |
| `restarts.md` | every container restart, what was in flight, and what was redone. |

## Not in git, and not archived anywhere durable

These are on the container this ran in and nowhere else. **Abby: say where to keep them
if you want them** (I cannot write to your Drive).

| Set | Size | Needed to |
| --- | --- | --- |
| full `transcript.json` for the 30 groups (pictures included) | 78 MB (55 MB zipped) | re-read exactly what each agent was shown |
| arm A and B evidence (`runs/*/evidence`, screenshots, `browser-files`) | about 1.3 GB | look at a picture an answer named |
| the server judge's per-page run folders (`results/c/rN/runs`, `results/pNN/evidence`) | about 1.8 GB | re-read a recording; not needed to re-score (each `report.json` has the findings) |
| `frozen/pages/*.har.zip` (40 MB) | | rerun anything: restore from Abby's Drive `round3-frozen-2026-11-16b.zip` (SHA-256 `2ce3446a…`, see `evals/judging/round3/ARCHIVE.md`), then `sha256sum -c frozen-MANIFEST.sha256` in `frozen/` |

## How it ran

Code: `main` at `63bc397`, unchanged in `src/`, `specs/`, `third_party/`, `pyproject.toml`
and `uv.lock` through every run (`git diff --stat 63bc397 HEAD -- src specs third_party
pyproject.toml uv.lock` is empty). The only code changes are in `evals/` (the gate's
`--out`, `--from-repeat` and per-page `timing.json`; arm A's env pins
`JUDGE_BACKEND=client`; both with `tests/test_gate_out.py`). A's `summary.json` files
name 13 different `code_commit` values: they are this branch's checkpoint commits during
the runs, with the same `src/` and `specs/`.

- **C:** `evals/apijudge_gate.py run --round 3`, 21 types
  (2.A 2.B 2.C 2.D 3.A 4.A 4.B 4.D 4.E 4.F 5.A 5.B 5.C 5.D 5.F 5.G 5.H 9.A 9.B 9.C 19.A),
  `tested_frozen`, 3 fresh repeats at this commit. Judge model
  `claude-sonnet-5-5`, CLI route, prompt SHA-256
  `e8320f2c1a18385ea55c4f61cd6e5f96687be573755cf0b7b0b573bda263a56d` in all 30 reports.
- **A:** `evals.agent.run --arm a --route cli --no-subagents --debrief`, prompt `round1-v1`,
  groups of 2 pages (5 per run), 3 runs, server judge off. All 309 recorded answers say
  `answered_by: client` (checked in `compare.json` and by the test).
- **B:** same, `--arm b`. Its one tool server is `browser` (Playwright MCP: headless,
  isolated, no-sandbox, `--no-webmcp`, the frozen-init page, the egress proxy, Chromium
  1243). The list is identical to round 2's `arm-b-*` runs once output paths and proxy
  ports are set aside (checked: all 15 summaries here against round 2's 7 `arm-b-*` folders).
- `UPSTREAM_PROXY` was set from the container's `HTTPS_PROXY` for every run and again
  after each restart.

## What to know before reading the numbers

- Arm A and B groups are named `g<group>-<run>`, not a single label per run (one label
  cannot hold five groups).
- **Three of B's 15 final messages have an unparseable `RESULT:` line** (the outer brace is
  missing: `arm-b-g3-1`, `g3-2`, `g5-1`). The locked scorer reads that as no answer, so
  `compare.md` gives its reading first and a labelled sensitivity view (brace added).
- **19.A on p01-p03:** NEEDS REVIEW with row W4 in all three repeats and in 9c: the search
  results page asked for an analytics script that Chromium blocks, and W4 counts any failed
  script. Not a failed live load; no rerun would change it. It is logged as a 19.A
  refinement for after the demo (`docs/ROADMAP.md`, "Site tests"). No page's live 19.A
  load failed otherwise (all suggested pages and searches loaded in every repeat), so no
  page was rerun alone.
- Four container restarts; the cause is probably the session going idle (see
  `docs/solutions/environment.md`). Each is in `restarts.md`.
- Arm B's chain wrote its per-group stdout logs over arm A's under `/tmp` (outside the
  repo); the results and summaries are unaffected.
