# How to run a judging round

For certified Trusted Testers who want to check tobi508 against their
own work and contribute the results. You test some pages in SCRT as usual.
The tool tests the same pages, and a script scores the tool against your
files test by test.

Results are agent-assisted. A round measures the tool; it is never a
certified Trusted Tester result for the pages.

**Status:** `evals/judging.py` (scan, apply, lock, score) is tested on
fixture pages (`tests/test_judging.py`). No outside tester has run a round
on real pages yet. Round 1 used the agent eval instead
(`evals/agent/README.md`). If a step does not work as written, say so in
your pull request.

## Why the steps are in this order: commit and reveal

The tool and its developers must not see your answers before the tool's
results are fixed. So:
1. you commit your page list with a hash of each SCRT file (not the files);
2. the tool tests the pages;
3. its results are locked (hashed) and committed;
4. only then do you add your SCRT files.

The score checks every hash and refuses anything that changed after the
lock.

## What you need

- **Certification:** you are a DHS-certified Trusted Tester with SCRT.
- **The repository:** a fork of this repository, cloned, with the setup in
  the [README](../../README.md#use-it) done (`uv sync --group dev`, Chrome).
- **An AI agent** to answer the tool's questions, for example Claude Code.
- **Time:** your usual testing time, plus about 10-30 minutes of machine
  time per page.

## 1. Choose the pages

- **How many:** 5-10 pages on `.gov` or `.mil` sites.
- **At least 2 pages from each site**, ideally 3 or more. The tool compares
  each page with the round's other pages on the same host for 9.A-9.C and
  19.A; a page alone on its site leaves those NEEDS REVIEW.
- **A mix:** a home page, an article, a form, a search or listing page.
- **Not nasa.gov:** it is the project's development site. Also skip any
  site named in `evals/judging/*/pages.txt`.
- **Choose before you run the tool on anything,** so the set is not limited
  to failures the tool already catches.

## 2. Test the pages in SCRT

- **Scope:** the tests in the [README's table](../../README.md#tt-tests-in-scope),
  or a subset. Tests you leave blank are not scored.
- **Product location:** set `P_Location` to the exact URL you tested. The
  score checks that it names the same page as your page list.
- **Comments:** describe each failure's element in your tester comment, so
  its location can be compared with the tool's.
- **Save each page's SCRT JSON file, and don't re-save it after hashing.**
  The hash pairs it with its page.

Keep the files to yourself until step 7.

## 3. Commit the page list (the start of the round)

Pick a round name, for example `smith-2026-11-20`. Then:

```bash
mkdir -p evals/judging/smith-2026-11-20
sha256sum path/to/scrt/*.json    # PowerShell: Get-FileHash path\to\scrt\*.json
```

Write `evals/judging/smith-2026-11-20/pages.txt`, one page per line: its URL
and its SCRT file's hash.

```
https://www.example.gov/                    3f2a…(64 hex characters)
https://www.example.gov/contact/            9b10…
# comments are allowed
```

Commit and push it to a branch in your fork. Do this before step 4: the
commit's time shows the list existed before the tool saw the pages.

## 4. Scan, on the same day you tested

Pages change, so run the tool soon after your own testing:

```bash
HEADLESS=true uv run python evals/judging.py scan evals/judging/smith-2026-11-20
```

- **What it does:** runs every implemented test on each page, live, with
  no time limit. It gives each page the round's other pages on the same
  host.
- **How long:** expect a few minutes per page, and up to 20 minutes for a
  large page (many form fields).
- **Its record:** each page's recording is kept with its results, so later
  questions about a page can be checked on exactly what the tool saw.
- **A page that cannot be tested** (it fails to load, or is not allowed) is
  recorded as such and counted apart.

## 5. Answer the open questions

The scan writes each page's questions to
`packets/pNN/round1/questions.json`, with the page text and screenshots
copied into the same folder.

Start **one fresh agent session** (not this repository's usual one, and no
subagents) in the round's `packets/` folder, and give it this prompt:

> Each folder under this one holds `questions.json` from an accessibility
> test run. For every `questions.json`, answer each question by its rubric,
> using only the files in that folder, and write the answers to
> `answers.json` in the same folder, in the format `answer_format` gives.
> Open nothing outside this folder. Do not start subagents. When done, list
> every file you opened.

Then apply the answers:

```bash
uv run python evals/judging.py apply evals/judging/smith-2026-11-20
```

If `apply` writes follow-up questions (`round2/`, at most 3 rounds), run
the same prompt again on those folders, then `apply` again. Repeat until
every page is done.

Check the agent's list of opened files: if it opened anything outside the
packets, the round is not blind. Note it in your pull request.

## 6. Keep the recordings, then lock

The recordings (`*.har.zip`) and screenshots never go in git; they are
too large. Each page's `report.json` and `pre-scrt.json` do (about 1 MB a
page). Settle the folder first (see "The round's folder" below), then zip
the round's results before locking, and keep the zip:

```bash
R=evals/judging/smith-2026-11-20
uv run python -m zipfile -c smith-2026-11-20-results.zip $R/results
sha256sum smith-2026-11-20-results.zip > smith-2026-11-20-results.sha256
# write $R/ARCHIVE.md now (round 3's is the example), then:
uv run python evals/judging.py lock $R
git add $R && git commit -m "smith-2026-11-20: lock (before any answer key)"
git push
```

`lock` hashes every result file, `pages.txt` and the scoring code. Commit
it before any SCRT file is in the repository.

## The round's folder: the same in every round

Rounds 1 and 2 (agent eval) and round 3 (scan, formal) ended up with
different layouts, and round 3 lost time to it (2026-11-16). From round 3 on,
every round, scanned or agent-driven, has this one layout.

| Path | In git? | What it is |
| --- | --- | --- |
| `pages.txt` | yes | the page list and the key hashes (step 3) |
| `state.json` | yes | a scanned round's progress; the lock reads it (agent rounds have none) |
| `frozen/index.json`, `frozen/freeze.json` | yes | the frozen set's index and its freeze log |
| `frozen/pages/*.har.zip` | no | the frozen recordings |
| `frozen-MANIFEST.sha256` | yes | `sha256sum` of every file in `frozen/`, made from inside it (`find . -type f \| LC_ALL=C sort \| xargs sha256sum`) |
| `results/pNN/report.json`, `pre-scrt.json` (agent rounds: `results/arm-*/runs/*/`) | yes | each run's report and pre-SCRT |
| `results/**/*.har.zip`, `*.png`, `evidence/` | no | recordings, screenshots, evidence |
| `results/lock.json` | yes | the lock |
| `ARCHIVE.md` | yes | what is in the archive zips: each zip's size, SHA-256 and how to restore it, plus what was done (freeze, run settings, lock). At the round's root: the lock covers `results/`, so a new file there fails the scorer |
| `keys/`, `score.md`, `score.json`, `adjudications.json` | yes | after the lock: the reveal, the score, the adjudication |
| `attempts/` (agent rounds only) | yes | stopped or retried runs, as in rounds 1 and 2 |

Rules:
- **No per-round `.gitignore` lines.** The global rules (`*.har.zip`,
  `*.png`, `evidence/`) are the whole policy. Rounds 1 and 2 kept reports
  and pre-SCRT files in git; round 3 first ignored them by mistake and had to
  lock twice.
- **The lock sorts files by `.gitignore`.** It stores files git keeps and
  files git ignores apart, and `score` sorts them again. A `.gitignore`
  change, or any new file in `results/`, after the lock makes `score` stop
  with "Result files changed after the lock". So before you lock: finish
  `.gitignore`, write `ARCHIVE.md`, make the zips, and put nothing more in
  `results/`.
- **No working papers in a round's folder.** A handoff, a one-off script or a
  scratch comparison goes in the session's own space, or `docs/reviews/`
  if it is worth keeping. They are linted and reviewed like code, and a
  round's folder is a record of what ran.
- **Keep the old rounds as they are.** Rounds 1 and 2 keep their layout
  (`results/ARCHIVE.md`); never rewrite `evals/judging/`.

### A formal round with the server judge, in order

1. **Freeze** (`uv run python -m evals.agent.freeze <round>`; `evals/agent/README.md`).
   For each page compare one replay with the live page, first 30 s: the same
   text and height, no popup, dialog or player. A page that fetches its data
   late (a single-page app) records short: set `RECORD_EXTRA_WAIT_MS=30000`
   and refreeze that page only (remove its entry and recording from
   `frozen/index.json`; the freeze records every page that has none). Make
   `frozen-MANIFEST.sha256` and a zip of `frozen/`.
2. **Run** `scan` in `tested_frozen` mode with the server judge. In a cloud
   container: `FROZEN_PAGES_DIR=<abs>/frozen FROZEN_PAGES_MODE=tested_frozen
   UPSTREAM_PROXY="$HTTPS_PROXY" BROWSER_CHANNEL=chromium HEADLESS=true
   JUDGE_BACKEND=api JUDGE_ROUTE=cli JUDGE_MODEL=claude-sonnet-5-5
   JUDGE_TYPES=<the types> RUN_TTL_HOURS=720`. `apply` only if a page is
   left open. State which code (`main` at which commit) the freeze and the run
   used: both should be on `main` before the run.
3. **Archive, then lock:** zip `results/`, write `ARCHIVE.md`, lock, commit,
   push, open the pull request. Only then may the keys come.
4. **Reveal and score** as in step 7.

## 7. Reveal and score

Copy your SCRT files into `evals/judging/smith-2026-11-20/keys/` (any
names: they are matched to pages by hash). Then:

```bash
git add $R/keys && git commit -m "smith-2026-11-20: answer keys" && git push
uv run python evals/judging.py score $R
git add $R/score.md $R/score.json && git commit -m "smith-2026-11-20: score" && git push
```

You can score on any clone. The lock checks the files git keeps on every
clone, and the recordings (which git ignores) only where they are present:
a clone without the zip scores, and one with it restored checks each
recording against the lock.

`score.md` lists, test by test:
- agreement;
- false PASS (the worst error) and false FAIL;
- NEEDS REVIEW;
- tests the tool does not perform, counted apart;
- the cells an answer to an open question decided (the server's judge or
  the agent's), apart from the cells the rules decided alone, so a judge
  is neither credited nor blamed for a rule;
- your Pass and Fail cells that carry no comment. Give the reason for a
  Pass as well as a Fail, above all where it was a judgment call; the
  list is for you, and the score does not change.

Where you confirm after the reveal that the tool was right and your file
was not, write it in the round's `adjudications.json` (round 2's is an
example); never edit the key. It counts as a validated catch per TT test
and, in an agent round, per WCAG criterion.

## 8. Contribute it

Open a pull request from your fork with the round folder:
- `pages.txt`, `results/`, `keys/` and `score.md`;
- in the description: the agent you used for step 5, anything unusual (a
  page that changed between your testing and the scan, files the agent
  opened outside its packets), and where the zip can be fetched if asked.

Keep the zip and its `.sha256`. It is the only copy of what the tool saw.

## What a round measures, and what it does not

- **It measures the tool's results with the questions answered.** The
  answering agent gets every screenshot as a file in its packet.
- **It does not measure a real user's agent.** A real agent gets
  screenshots as `run://` links and opens few of them, so it answers fewer
  visual questions (`docs/solutions/judge-eval.md`). The agent eval
  (`evals/agent/README.md`) measures that path, with a model driving the
  tool beside a Playwright MCP baseline.
- **Your SCRT files are the reference, not ground truth.** If you think the
  tool found something you missed, say so in the pull request rather than
  editing your file.
