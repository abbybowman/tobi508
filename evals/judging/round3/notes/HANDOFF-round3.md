# Handoff: round 3 (roadmap step 10), continue from here

Read `docs/how-to/run-a-judging-round.md`, `evals/agent/README.md` and the
step 10 prompt in `docs/reviews/2026-11-11-code-review-fixing.md`. This is
round 3, a formal blind judging round with the server judge answering:
freeze, run, lock, then score against Abby's keys. Never open the keys
before the lock. Change no code yourself, and change nothing between the
freeze the run uses and the lock.

## Where things stand (2026-11-16)

- Pages: `evals/judging/round3/pages.txt` on `main` (10 pages on
  science.data.nasa.gov, p01-p10 in file order).
- Merged: scorer fixes 15-17 (#73); the freeze's scroll fix and frame
  report (#95); the replay answer to a silent sign-in check (#96).
  `main` head when handed off: 2045185.
- Round branch: `claude/round3-run` (unmerged, no PR until the lock). It
  holds `evals/judging/round3/frozen/index.json` and `freeze.json` (commit
  247d4a4, frozen with #95's code). The recordings are git-ignored: restore
  them from `round3-frozen-2026-11-16.zip` (unzip into
  `evals/judging/round3/`, so it makes `frozen/`), and check every file
  against `round3-frozen-MANIFEST.sha256` (`cd evals/judging/round3/frozen
  && sha256sum -c MANIFEST`) and the zip against its `.sha256`.

## Decisions Abby made

- Server judge answers (JUDGE_BACKEND=api, JUDGE_ROUTE=cli, model
  claude-sonnet-5-5, all 21 types it can take, as gate 9a; 4.C stays with
  the client). Questions it leaves unsure, and 4.C's, stay NEEDS REVIEW
  with a note: no second judge, no fresh agent. To let `judging.py lock`
  accept the pages, apply an empty answers file (`[]`) for each open page
  until `judging.py apply` marks it done (at most 3 rounds); check first on
  one page that an empty list is accepted, and record in the round's notes
  what you did.
- No home page as an extra other page: the site's home page is p01, so
  `judging.py`'s own other pages (the round's pages on the host) cover it.
  19.A loads further pages itself.
- Run in tested_frozen mode: FROZEN_PAGES_DIR=<abs path>/evals/judging/round3/frozen,
  FROZEN_PAGES_MODE=tested_frozen. In this cloud container also set
  UPSTREAM_PROXY="$HTTPS_PROXY", BROWSER_CHANNEL=chromium, HEADLESS=true.
- Keep each page's report.json and pre-scrt.json out of git: add
  `evals/judging/round3/results/p*/` (and `packets/`) to `.gitignore` on the
  round branch before the lock, and zip results/ with a SHA-256 manifest as
  the how-to says.

## What the freeze found (reported to Abby)

- All 10 pages and 18 site searches recorded, HTTP 200; all 28 recordings
  open and match their index; every page's scroll reached the end.
- The Data Governance pages (p07 /data-governance-community/home, p08
  /forum) scroll inside the app, so the document is one window (900 px):
  the freeze's window scroll never reached content inside the app.
- Frames not recorded: the sign-in check on p07 and p08
  (auth.sciencecloud.nasa.gov ... openid-connect/auth, "differs between two
  loads"). #96 now answers it in a replay.
- Replay vs live, first 30 s (`compare_live.py`): p01-p06, p09, p10 show the
  same text and height, no popup, banner, dialog or player; replay-only
  failures are Google analytics and gtag (not visible).
- p07 and p08 replayed blank before #96. With #96 (scratch check on the
  same recordings): p08 draws 130 lines (live 123); p07 only 27 of ~126,
  because its recording lacks a site script (chunk-YJNSFNI6.js), images,
  fonts and the app's data requests.
- crazyegg's analytics script fails on every portal page and every
  recorded search: crazyegg answers 403 to a HeadlessChrome user agent
  (Chromium blocks it as ORB). So 19.A's search cannot FAIL here (row W4,
  "not verified"); 19.A goes NEEDS REVIEW unless two ways are found.

## Next steps

1. `git fetch origin && git checkout claude/round3-run && git merge origin/main`
   (brings #96). Restore the zip and check the manifest.
2. Refreeze p07 and p08 only. The freeze records every page in
   pages.txt that has no recording (record_missing mode): remove p07's and
   p08's entries from `frozen/index.json` (and their HARs 007, 008) and
   rerun `uv run python -m evals.agent.freeze evals/judging/round3`. Check
   that the other 8 recordings and 18 searches are byte-identical to the
   manifest afterwards; report anything that changed.
3. Compare one replay of p07 and p08 with the live page again
   (`compare_live.py <outdir>`, run from the repo root with
   UPSTREAM_PROXY set). Tell Abby the result. If p07 still draws
   incompletely, ask her: leave it out (not scored, with the reason) or
   test it as is.
4. Tell Abby the exact `main` commit before the run (9b runs at the same
   one); the round branch must equal `main` plus only round files.
5. Run: `uv run python evals/judging.py scan evals/judging/round3` with the
   settings above, then the empty-answer applies, then zip results/,
   `judging.py lock`, commit and push the lock. Only then may Abby add keys.
6. After the keys: `judging.py score`. Report per test and in all; list
   apart the cells inside a web component or a frame; list every NEEDS
   REVIEW and wrong cell by cause, as findings for the other threads.
