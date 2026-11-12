# Q: tests, CI, Dockerfile and packaging review (2026-11-11)

## Overview

- The suite is large (1204 tests collected, 1203 by default; one `slow`) and its rule tests are good in one way: each fixture folder has an EXPECTED table, a `test_every_fixture_is_listed` guard, and expected outcomes live in tests, not pages. Hash checks on ACT, Baseline and vendored files are strict (set equality).
- Safety rules (allowlist, egress, redirects, leakage, hosted sign-in, frozen pages) have direct tests. Principle 5's page-steering tests (`test_fixtures_inject.py`) never run in CI: the CI file groups skip them (Q-01).
- CI can skip the whole suite for a change to `src/tobi508/judge_prompt.md` or a vendored `LICENSE.md` because the docs-only filter is `*.md` (Q-02).
- Wrong-outcome classes the reviewers found (shadow roots, frames, caps, late starters, non-Latin text) are almost untested outside 4.C and the walk: no non-Latin text exists in any fixture, shadow roots appear only in 4.C fixtures (Q-03, Q-04).
- Time: every end-to-end run costs about 4.5-11 s serial (measured), about 590 such runs; each launches its own Chromium, records a HAR and walks twice. Savings are in sharing recordings, not in the browser fixture (Q-07).
- Image carries 247 MB of `evals/judging`, tests and docs; no HEALTHCHECK; base images by tag. Wheel ships no specs or third_party and cannot run (Q-09, Q-10).
- Findings: P1 x4, P2 x8, P3 x5. Nothing in this file was fixed; no repo file edited.

## Findings

### Q-01 CI never runs tests/test_fixtures_inject.py
- Severity: P1
- Kind: gap
- Where: .github/workflows/ci.yml:69-84 (matrix `args`)
- What: The four groups name `test_fixtures_4*`, `5*`, `9*`, `19a`, `2*`, `3a`; the `rest` group ignores every `tests/test_fixtures_*.py`. `test_fixtures_inject.py` matches none of the named globs and is excluded from `rest`, so its 7 tests (the only ones for principle 5, page text steering the judge, and the plumbing that keeps trick text inside the untrusted block) run nowhere in CI. The comment promises "a new test file is never left out"; the `ignore-glob` breaks that promise for any new `test_fixtures_<other>.py`.
- Evidence: I collected each group with its exact args and diffed against the full collection: 1196 of 1204 collected; missing are the 7 inject tests plus `f34-600-links` (slow, expected).
- Fix: Add `tests/test_fixtures_inject.py` to a group, or make `rest` ignore only the named globs (`test_fixtures_[0-9]*`), and add a CI step that fails when collected-in-groups differs from the full collection.
- Confidence: confirmed (collect-only diff)

### Q-02 Docs-only filter skips CI for judge prompt and vendored licence edits
- Severity: P1
- Kind: gap
- Where: .github/workflows/ci.yml:36-41
- What: Any `*.md` outside `README.md` and `specs/` counts as docs. `src/tobi508/judge_prompt.md` (the server judge's fixed prompt, hashed into every report, read by `apijudge.py`), `evals/agent/judge_c_prompt.md` and `third_party/andi/LICENSE.md` (a file `test_third_party.py` hashes) are Markdown. A change to only one of them runs no lint, no tests and the required check "CI" passes.
- Evidence: Ran the `case` statement on those paths: all print SKIPPED. `git ls-files '*.md'` shows them.
- Fix: Treat `src/*`, `third_party/*`, `evals/agent/*` and `tests/*` as code before the `*.md` rule; or skip only `docs/*`.
- Confidence: confirmed

### Q-03 No fixture exercises shadow roots for any check but 4.C
- Severity: P1
- Kind: gap
- Where: tests/fixtures/* (only 4c/f24, f25 and tests/test_traverse.py); tests/test_fixtures_4a.py:209
- What: D-03, D-01, K-02 (shadow-root false PASS/DNA) went unseen because the suite has no shadow-root page for 4.A, 4.B, 4.D-4.F, 5.A-5.H, 9.A-9.C or 19.A. `test_shadow_and_frame_stops_are_reached` for 4.A uses `no_trap.html`, whose shadow button is keyboard-reachable and has no click handler, so it tests the walk, not the mouse-only scan.
- Evidence: `grep attachShadow|shadowrootmode` across fixtures: only 2 pages, both 4.C; tests: only `tests/browser/test_v_checks.py` once.
- Fix: One shared "web component" page per check family (mouse-only span, input, nav) with expected NEEDS_REVIEW or the right outcome; this is the cheapest regression net for four P0s.
- Confidence: confirmed

### Q-04 Principle 6 and the "answers from the tool's output" boundary is held by convention only
- Severity: P1
- Kind: gap
- Where: tests/harness.py:40-70, evals/ (manual)
- What: `run_check` answers every open question with a scripted choice (`seen="scripted: the picture was not opened"`), so tests assert rule mapping (answer -> outcome), never that the question or its evidence lets a reader answer correctly. The judge eval is manual and not in CI; nothing fails when a question, rubric or evidence input changes without a re-run. `test_apijudge` records the prompt SHA but nothing compares it to a last-evaluated value.
- Evidence: read harness.py; grep of tests for `judge_eval` finds no CI link; ci.yml has no eval step.
- Fix: Record the hash of (rubric + question text) in a file the eval writes, and a fast test that fails when the live hash differs from the last eval's. Cheap, and makes "run the eval" enforced.
- Confidence: likely

### Q-05 Several safety/limit rules have no failing test
- Severity: P2
- Kind: gap
- Where: see the principle table below
- What: No test for: `MAX_RUN_S` hard stop under no-time-limit; "never write 'certified/compliant' about a page" (no scan of src or prompts); "no `trusted_tester` in tool names"; Playwright pinned with `==` and lock in sync; CODEOWNERS covers `/src/tobi508/checks` (it does not, see Q-12); a page link is never followed except the approved exceptions (no page whose links/forms try to steer another URL, other than 19.A search); other-page-is-the-tested-page spelled differently (K-01): `test_other_pages_are_checked_before_anything_runs` tests only `#top` and even uses `?0..?5` variants as distinct pages.
- Evidence: grep of tests for each term returned nothing.
- Fix: Add small unit tests: tool-name scan, `pyproject` playwright `==`, banned-word scan over src/ strings and judge prompt, MAX_RUN_S with a monkeypatched clock.
- Confidence: confirmed (grep)

### Q-06 Outcome-only assertions in rule-bearing tests
- Severity: P2
- Kind: gap
- Where: tests/test_baseline_cases.py:119-130; tests/test_fixtures_9a.py:36; tests/test_fixtures_9x.py:145-149; tests/test_act_cases.py:100-110; tests/test_fixtures_2a.py:50-53; tests/test_act_2a.py, test_act_2c.py
- What: Baseline cases, ACT cases for 4.A/4.C/4.D/5.B/9.A compare the outcome only (not the rows), so a PASS reached by the wrong row (K-01's N6 on a self-comparison, M9 where M5 was due) passes. 9.B/9.C's `ROWS` is optional: `consistent-site` PASS for 9.B and 9.C asserts no rows. 2.A's row check is "some row ends with X". ACT 2.x never expects PASS (ER 3 gate), so there is no positive control for 2.A-2.C at all.
- Evidence: read the tests; `ROWS` has 8 entries for 14 cases x up to 3 tests.
- Fix: Record rows in the manifests (or EXPECTED) for every PASS, and assert them; make the optional `ROWS` mandatory.
- Confidence: confirmed

### Q-07 Where the suite's time goes
- Severity: P1
- Kind: time
- Where: tests/conftest.py (fixtures), pyproject.toml addopts, src/tobi508/pipeline.py
- What: Almost every rule test calls `run_tt_tests`, which launches its own Chromium, records a HAR, then walks the page twice (see the walk cost `loads == 2` in test_tools). About 590 tests do this; the `browser` fixture (function scoped, with its own EgressProxy) is used by only 40 low-level tests, so a session-scoped browser would save little. Measured serial (-n0, shared 4-CPU box, another reviewer running): test_fixtures_5h 8 tests 53 s (6.3-7.5 s per run, even the trivial DNA page 6.8 s); test_fixtures_inject 7 tests 33 s; test_browser 8 tests 12 s; test_fixtures_2b 15 tests 161 s (10.7 s, media pages). Estimate: ~590 runs x ~7 s = ~70 CPU-min, ~18 min at 4 workers, plus 114 ACT load tests (~1-2 s each) and the rest. The pyproject comment records 3m51s at -n 8 and 20m17s serial for an earlier, smaller suite; CI splits into 4 jobs of ~15-20 min each (no job timeout set).
- Evidence: timed runs above; collect counts per file; `grep` of fixture use.
- Fix (three biggest): (1) A per-test fixed cost of ~5 s is record+walk: share one recording and one walk per fixture page across tests of the same page (several tests hit the same page with different checks: 9x runs 3 checks in one call, but 4.A/4.B/4.D/4.F and 5.A-5.C pages are re-recorded per file); a session cache of `HAR + walk` keyed by file hash would cut it to near zero for rules tests that only change answers. (2) Move rows that need no page into the existing unit style (`_state(...)` + `evaluate`, as 4a/5d/5h do): each such test is 10 ms not 7 s; most `EXPECTED` entries whose rows are pure functions of recorded evidence could use stored evidence JSON. (3) Mark the 114 ACT `test_case_loads_with_every_asset` and long media tests (2x, 3a) as `slow`/nightly or run once per fixture refresh (the manifest hash test already guards drift); and run `--dist loadfile` or per-check groups so xdist workers do not split a file and rebuild its servers.
- Confidence: confirmed for measurements, likely for the estimate

### Q-08 CI jobs have no timeout, cache or concurrency control; install runs unlocked
- Severity: P2
- Kind: gap
- Where: .github/workflows/ci.yml, container.yml, time-budget.yml
- What: No `timeout-minutes` (default 360) so a hung Chromium burns six hours per matrix job; no `concurrency` cancel, so every push re-runs; no cache for uv, Playwright browsers (each of 4 jobs downloads Chromium and apt libs) or npm. `uv sync --group dev` is not `--locked`, so a stale `uv.lock` is silently re-resolved in CI (lock is in sync today: `uv lock --check`). Actions are pinned to moving tags (`@v4`, `@v3`, `@v6`), `runs-on: ubuntu-latest`. Test job does not depend on lint (parallel; fine). `fail-fast: false` is right.
- Evidence: read all three workflows.
- Fix: `timeout-minutes: 45`, `concurrency` with cancel-in-progress, `uv sync --locked`, cache `~/.cache/ms-playwright`, pin actions to SHAs.
- Confidence: confirmed

### Q-09 Container workflow: image publishes in parallel with tests, smoke test is thin
- Severity: P2
- Kind: gap
- Where: .github/workflows/container.yml
- What: On a push to main the image is published (`:latest` and SHA) independently of the CI test jobs: a commit that fails tests still ships. The smoke test runs one 4.C run on `no_trap.html` through `DEV_MODE=true` and checks the public-host refusal; good for plumbing, but it never runs pytest in the image and does not test the sign-in path. `packages: write` is granted at workflow level for pull_request runs too (fork PRs get a read-only token, so low risk). Hosted run with `DEV_MODE=true` smoke uses `file://`; the image's egress proxy to a real allowlisted host is untested.
- Evidence: read workflow.
- Fix: Make publish depend on the CI workflow (`workflow_run` or `needs`), scope `packages: write` to the publish step's job.
- Confidence: confirmed

### Q-10 Image carries 247 MB of eval records and has no healthcheck; wheel cannot run
- Severity: P2
- Kind: design
- Where: Dockerfile:22-23, 38-41, .dockerignore, pyproject.toml:27-28
- What: `.dockerignore` excludes root `runs/` only. `COPY . .` copies tracked `evals/judging` (247 MB, 803 files), `tests`, `docs`, `.github`. The following `chown -R app /app /data` duplicates all of /app (venv plus these) into a second layer, so the image roughly doubles that content. No `HEALTHCHECK`, though `/health` exists. Base `python:3.11-slim-bookworm` and `uv:0.11.32` are tags, not digests. Positive: non-root uid 1000, Playwright pinned `==1.63.0` and locked, Chromium installed by the locked Playwright, hosted defaults `BROWSER_CHANNEL=chromium`, `HEADLESS=true`, `RUNS_DIR=/data/runs`; public host without `AUTH=oidc` refused (tested in test_access.py and container.yml). Dev group (pytest, ruff) is installed in the runtime image by design.
  Wheel: `uv build --wheel` ships only `tobi508/` (74 py files plus `judge_prompt.md`); no `specs/`, `third_party/`, TT text; `config.py` resolves `REPO_ROOT = parents[2]`, so an installed wheel looks for specs in site-packages' parent and fails. Nothing in CI installs the wheel.
- Evidence: built a wheel to scratch and listed it; `du`/`git ls-files` for sizes; read Dockerfile.
- Fix: `.dockerignore`: `evals/`, `docs/`, `tests/` (keep `tests/container_smoke.py` and `no_trap.html` or copy them separately), `.github`; use `COPY --chown=app`; add HEALTHCHECK on /health; pin digests; either drop the wheel claim or include specs/third_party via `force-include`.
- Confidence: confirmed

### Q-11 test_server.py is template leftovers; env-sensitive assertion
- Severity: P3
- Kind: gap
- Where: tests/test_server.py:1-50
- What: "Smoke tests for the example MCP server"; most only check import/registration does not raise. `test_default_transport_is_stdio` reads `settings` and fails if `MCP_TRANSPORT` is set in the developer's environment or `.env` (Dockerfile avoids setting it image-wide for this reason).
- Evidence: read.
- Fix: Build `Settings(_env_file=None)` in the test; keep the instruction test, drop the rest.
- Confidence: confirmed

### Q-12 CODEOWNERS covers specs, .github and evals/judging only
- Severity: P2
- Kind: gap
- Where: .github/CODEOWNERS
- What: Principle 2 says the rules spec is the only outcome logic, but `src/tobi508/checks/`, `tests/fixtures/*/manifest.json` (expected outcomes) and `tests/fixtures/act` have no owner; Dockerfile/pyproject/uv.lock are not covered (the `.github/` line does not cover them). Whether "Require review from Code Owners" is on cannot be seen from the repo.
- Evidence: read file.
- Fix: Add `/src/tobi508/checks/`, `/tests/fixtures/*/manifest.json`, `/third_party/`, `/Dockerfile`, `/pyproject.toml`, `/uv.lock`.
- Confidence: confirmed (file); speculative (branch protection)

### Q-13 xfail(strict) late-refocus test documents an unfixed trap miss
- Severity: P2
- Kind: gap
- Where: tests/test_traverse.py:139-152
- What: A page that refocuses 600 ms after blur reads as a 2-stop loop, not a stuck element; the test expects `end == "stuck"` and is `xfail(strict=True)`. This is the "something that starts late" class, and the known miss is parked, not reported to users.
- Evidence: read; reason text in the marker.
- Fix: Decide the rule (spec question) or keep, but list it in ROADMAP Known limits and in the 4.C spec.
- Confidence: confirmed

### Q-14 Third-party hash test is good; ACT/Baseline pins are weaker than they look
- Severity: P3
- Kind: gap
- Where: tests/fixtures/act/manifest.json, tests/fixtures/baseline/manifest.json
- What: `test_third_party` compares the whole directory (excluding NOTICE) to PROVENANCE, so every vendored file, SCRT included, is covered. ACT and Baseline manifests hash every vendored page (equality of file sets; only the sync scripts are unhashed), which enforces "never edit an ACT page". But the ACT manifest pins the source JSON hash and not a commit; Baseline pins no upstream version at all, and the `expected` values sit in the same manifest as the hashes, so an owner can change an expected outcome without any hash noticing.
- Evidence: python check of manifest keys vs files on disk.
- Fix: Split `expected` (ours) from the vendored-source record, and record a commit or date for Baseline.
- Confidence: confirmed

### Q-15 Fixture names and titles hint the answer; no global network guard
- Severity: P3
- Kind: gap
- Where: tests/fixtures/4c/f04-field-swallows-tab.html (`<title>Fixture: simple keyboard trap`), 2x/t-css-infinite.html, tests/conftest.py:74
- What: No outcome words in comments (grepped), but titles and file names name the defect; matters only where an agent sees pages (agent eval, frozen pages). Network blocking is per component (egress resolver monkeypatch, `MAP cdnjs ~NOTFOUND`); tests that launch their own `pw.chromium.launch()` (test_scrt_tool.py:30, test_andi.py:28) are not covered, and no socket-level guard exists. Today none fetches externally (SCRT page has no external refs).
- Evidence: greps.
- Fix: Add an autouse socket guard (allow loopback only) that wraps `socket.connect`.
- Confidence: confirmed (greps), likely (risk)

### Q-16 Test timing assumptions and helper file naming
- Severity: P3
- Kind: gap
- Where: tests/conftest.py:183 (`time.sleep(16)` handler), tests/test_tools.py:97-109
- What: `/slow.html` sleeps 16 s in a thread; `run_settings` equality in test_tools hard-codes every default and fails on any new setting (change detector, not a rule test). `tests/.act_scores` is written into the source tree.
- Evidence: read.
- Fix: assert only the keys that matter; write scores under `runs/`.
- Confidence: confirmed

## Tables

### Table 1. Time (measured serial, -n0, shared machine)

| File | Tests | Wall | Per test |
| --- | --- | --- | --- |
| test_fixtures_5h.py | 8 | 53 s | 6.6 s (6.3-7.5 s each) |
| test_fixtures_inject.py | 7 | 33 s | 4.7 s |
| test_browser.py | 8 | 12 s | 1.5 s (low-level, `browser` fixture) |
| test_fixtures_2b.py | 15 | 161 s | 10.7 s |

Largest files by count: test_act_cases 135, test_fixtures_4c 75, test_egress 56, 5f 53, 4a 52, test_tools 36, test_judging 36, baseline 36, 5d 35. About 510 tests are in `test_fixtures_*`; ~590 do a full run. Parallelism: pytest-xdist `-n auto` (cgroup-aware hook in conftest), `-m 'not slow'`; one slow test (`f34-600-links`). Function-scoped: `settings`, `server` (thread HTTP server per test), `browser` (+EgressProxy); session-scoped: `act_server`, `baseline_server`. `runs/test-progress.txt` absent, no durations file.

### Table 2a. Source modules with no direct test (by import/grep)

Checks via fixtures only (no unit test): t2a, t2b, t2d, t4f, t5a, t5c, t9a (all have fixture files by test id). No test at all by name: `forms.py` (only through 5.D/5.F-5.H runs), `mechanism.py` (only through 2.x runs), `explain.py` and `prompts/explain` (via test_tools only), `resources/tt.py` (one test), `tools/answer_questions.py`/`explain.py` (via tool calls). Everything else has a named test file (access, andi, apijudge, browser, capture, compare, config, egress, engine, flash, flashcap, frozen, inline, jobs, judgment, labels, models, motion, observe, pagecache, pipeline, policy, redact, reveal, rules, runlog, scrt, site, traverse, versions, walk).

### Table 2b. Principles and rules to the test that fails if broken

| Rule | Test | Gap |
| --- | --- | --- |
| P1 no certification claim | test_models `report_cannot_claim_certification`, disclaimer asserts in test_tools, scrt tool | No scan for "certified/compliant" in output text |
| P2 outcomes only in specs | test_rules (spec versions vs registry), EXPECTED tables | No test that scans src for outcome logic outside checks/ |
| P2 NEEDS_REVIEW note; NOT_TESTED only 3.A | `assert_note` in every harness run; test_tools `no_test_is_reported_not_tested` | ok |
| P3 false PASS | test_models `finding_defaults_to_needs_review`; guard GU tests | Class gaps in Table 3 |
| P4 pin versions | test_third_party; test_tools asserts versions recorded | Nothing checks `==` pin or lock sync |
| P5 untrusted content | test_fixtures_inject (not run in CI, Q-01), 4c f32 | No test that links are not followed |
| P6 verify vs assume | manual evals | Q-04 |
| P7 proportionate to PDF | none possible | n/a |
| P8 plain language, overridable | `assert_plain` on all fixture summaries; test_models | ok |
| Allowlist/redirects/file:// | test_policy, test_browser, test_egress, test_tools | ok |
| ANDI never from ssa.gov | test_andi (missing file aborted) | ok |
| CSP bypass recorded | test_andi, test_tools `run_settings` | ok |
| HAR replay, full Chromium for iframes | test_browser, test_full_chromium | ok |
| Other pages, 19.A search/suggested | test_site, test_fixtures_19a, test_pagecache | self-spelling (K-01) |
| Frozen pages | test_frozen | ok |
| Tool names/prefix/one per file | test_tools `tools_are_listed`, `descriptions_follow_registry` | no `trusted_tester` scan |
| Small output | test_models (size, shared inputs), test_tools (shared texts, pictures) | ok |
| CALL_WAIT_S, concurrency, run expiry | test_tools | ok |
| MAX_RUN_S, RUN_LIMIT_S/OTHER_PAGE_S, moving allowance | test_time_budget, test_tools, test_motion_browser | MAX_RUN_S none |

### Table 3. Wrong-outcome classes against fixtures

| Class | Fixtures that exercise it | Checks with none |
| --- | --- | --- |
| Shadow roots | 4c f24, f25; test_traverse; test_v_checks | all except 4.C walk |
| Frames | 2x (4 pages), 3a, 4c (9), 4d, 5d (f09, f20); 5b/5h unit notes | 4.A, 4.B, 4.E, 4.F, 5.A, 5.C, 5.F, 5.G, 9.x, 19.A (no frame page) |
| Cap or time limit | 4c f29, f34 (slow), test_traverse, 9x unit, test_site, test_reveal | 4.A, 4.B, 4.D-4.F, 5.x end-to-end |
| Walk ended in a trap | 4c (47 pages) | other checks run after a trap: none |
| Starts late (timers) | 2x, 4c f36/f41, 5d f17-f19, lazy chunks | 4.A, 4.E, 5.A-5.C, 9.A-9.C (9x has delays only in tests) |
| Non-English/non-Latin text | none anywhere (non-ASCII in only 3 fixtures: punctuation) | all |
| Hidden text | 4a, 4e, 5a, 5h, 2x, 4c (display none/aria-hidden) | 9.x, 19.A, 5f |
| Form behind a button | 5d f07, f16; test_reveal; 4c f13 | 5.A-5.C, 5.F-5.H |
| Failed read | unit tests of `incomplete` for 4.A, 5.B, 5.H, 9.C | page-level failure for 4.B, 4.E, 4.F, 5.D |

### Table 4. Spec rows with no EXPECTED entry naming them (heuristic: row ID text not found in the check's tests)

Heuristic caveat: `instance_rows` returns only M/N/C rows, so A and G rows are implicit; they are listed only when a test names none of them.
- 4.A (25 rows): M12 (T row asking J2; the following M13-M15 are named). A1-A3, G1-G5 implicit.
- 5.D (23 rows): M4, M5, M6, M7, M12 (they route to J1/J2; `test_rows_on_recorded_evidence` covers J-branching, not these routes by ID).
- 9.B (16 rows): N2, N5, N1/N2o are named only in comments; N6 is PASS with no row assertion in `consistent-site` (Q-06). A1, A2 (page could not be read), A3, A4 unnamed.

## Unverified leads

- test_agent_run/test_agent_freeze use Node Playwright MCP (`npm ci`); I did not check whether they need a second browser download in CI.
- Whether the container image needs `evals/` at all (a `--no-cache` size comparison was not done).
- xdist `--dist` mode: default `load`; I did not measure whether `loadfile` would save fixture startup.
- Branch protection / Require Code Owners state is not visible from the repo.
- ACT/Baseline vendored pages: external references in the HTML were checked only for cdnjs.

## If we started over: tests

1. A recorded-evidence layer: keep one frozen recording and walk per fixture page (hash-keyed cache), and let rule tests run `evaluate()` on stored evidence; keep a small set (about 40) true end-to-end runs. Cost: a cache format and a regeneration command; saves most of the ~70 CPU-min.
2. A page-class matrix: one table of {shadow, frame, cap, late start, non-Latin, hidden, behind-button, failed read} x every check, each cell a fixture or an explicit "not applicable" with reason, enforced by a test. Cost: about 8 shared pages plus a table; catches the P0 class directly.
3. CI that cannot miss a file: one job computes the collection, shards it evenly (`pytest --collect-only` + split), fails if any test is unassigned, and the docs filter lists code paths by directory. Cost: a small script.
4. Row-level expectations everywhere: expected rows (not only outcome) in manifests for ACT/Baseline, mandatory `ROWS`, and the question/rubric hash tied to the last judge-eval result. Cost: filling manifests once (rows are printed by the existing scoring).
