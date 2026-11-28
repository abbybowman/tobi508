# Evals: real agents answer the open questions

`tests/` answer every open question with scripted answers (what a correct
judge would say). That tests the rules, not the questions. Here, fresh
agents answer them for real, seeing only what a consumer agent would get.

The agent eval (a model driving this server, against the same model with
Playwright MCP) is in `agent/`: see [agent/README.md](agent/README.md).

## Run

```bash
uv run python evals/judge_eval.py prepare /tmp/eval   # packets in /tmp/eval-packets
# ONE fresh agent answers every packet folder (questions.json -> answers.json);
# one agent per folder costs ~55k tokens each (docs/solutions/judge-eval.md).
uv run python evals/judge_eval.py apply /tmp/eval     # follow-ups -> round2; score
```

**Isolation.** Each packet holds only the tool's own output: questions,
rubrics, inputs, page text, shared inputs, the evidence files they point to (copied from
`run://`), and the `tobi_answer_questions` description. Local URLs are mapped to
`https://example.gov/site/pageN.html` and folders are shuffled `qNN` IDs,
because fixture names describe the expected answer ("key-in-comment-only").
The answer key (`/tmp/eval/state.json`) is outside the packet tree. Agents
are told to open nothing else and to list every file they opened.

**Pictures (post-round 1 fix 19).** A fourth argument picks how the
packets give pictures: `all` (the default: copied in, as before), `none`
(left as `run://` links the agent cannot open, as for a real agent that
does not read them) or `retry` (as `none`, then each look-to-settle
question answered "unsure" comes back once with its pictures). The arm is
kept in `OUT/images.txt`. `TESTS` may be `all`:

```bash
uv run python evals/judge_eval.py prepare /tmp/eval-none all none
```

## Judging rounds: real pages against a tester's blind SCRT files

A certified tester running their own round: follow
[docs/how-to/run-a-judging-round.md](../docs/how-to/run-a-judging-round.md).

A round can be scored two ways, both against the same keys by commit and
reveal: the scan below (a script drives the tool; one agent fills in the
question packets), or the agent eval (`agent/README.md`: a model drives the
tool itself, beside a Playwright MCP baseline, on frozen copies of the
pages). Round 1 uses the agent eval.

`evals/judging.py` scores the tool on real .gov pages against a certified
Trusted Tester's SCRT files, by commit and reveal, so neither the tool nor
its developers see the pages or the answers first.

1. **Start a round.** The tester commits `evals/judging/<round>/pages.txt`
   when testing begins (not earlier: a page list in the repository lets
   development prepare for it). One page per line, its URL and the SHA-256
   of their SCRT file for it, in either order; `#` comments allowed. Hash
   the exact file to be uploaded (`shasum -a 256 *.json`, `sha256sum *.json`
   or `Get-FileHash *.json`) and do not re-save it in SCRT afterwards.
2. **Scan.** `uv run python evals/judging.py scan evals/judging/<round>`
   runs every implemented test on each page, with the round's other pages
   on the same host as `other_pages` (9.A-9.C, 19.A). In a container, set
   `BROWSER_CHANNEL=chromium HEADLESS=true`. The real allowlist applies.
3. **Answer.** ONE fresh agent answers every
   `<round>/packets/pNN/roundK/questions.json` into `answers.json` in the
   same folder, opening nothing else; then `apply`. Repeat until no page is
   open.
4. **Lock.** `uv run python evals/judging.py lock evals/judging/<round>`,
   then commit `results/` (reports, pre-SCRT files, `lock.json`; the HARs
   stay out of git). The round's folder is the same in every round: see
   "The round's folder" in the how-to.
5. **Reveal.** The tester adds their SCRT files to `<round>/keys/` (any
   names: they are matched to pages by hash) and commits.
6. **Score.** `uv run python evals/judging.py score evals/judging/<round>`
   writes `score.md` and `score.json` (scoring: `evals/scoring.py`, on the
   neutral comparison in `src/tobi508/compare.py`). It stops if a key
   matches no page, if a key's page (`P_Location`) names a different page
   than its line in `pages.txt`, or if `pages.txt`, a result or the scoring
   code changed after the lock (to score with older code, check out the lock
   commit). The rates open with how many pages were scored and why any were
   not. Add a line for
   the round below.

Tests the tool does not perform yet, and tests the tester left blank, are
counted apart, never as agreement or disagreement.

**Freezing pages (later rounds).** Round 1 was tested live on the day of
the scan. Pages change, so later rounds record each page on the day the
tester tests it and scan that recording. Until a `freeze` command exists, in
Chrome: DevTools, Network tab, tick "Preserve log" and "Disable cache",
reload the page, then right-click a request and "Save all as HAR with
content". Whether a DevTools HAR replays like our own recordings is not yet
checked.

**Validated catches (Abby, 2026-11-06).** After the reveal, the tester may
confirm that the tool was right where it differed from their key (round 1:
Artemis III 4.D, a player button with no visible focus). They record it in
`<round>/adjudications.json` (page, TT test, the confirmed result, who,
when, why), never by editing a key, which is locked by its hash. The scorer
counts a tool result that matches as a **validated catch**, weighted +1 like
an agreement and shown apart (`evals/scoring.py`). The file sits outside
the lock, as the keys do.

## Read cap 2026-11-13: 9.A-9.C on round 2's 10 pages with the cap at 5,000 (roadmap step 6c, item 1)

The site read's cap (`site.py` `UNIT_CAP`; 9.A 1.4.0, 9.C 1.6.0, 19.A
1.6.0) went from 600 to 5,000. 9.A-9.C on round 2's 10 frozen pages
(Abby's `round2-frozen` archive, every file checked against its
manifest), in **replay** mode (every page from the folder, nothing live),
each page compared with the other 9 as in step 6; then the server judge
(CLI route, `claude-sonnet-5-5`) answered 9.A's and 9.C's questions on
those same runs. Scored with round 2's scorer and keys
(`evals.scoring.score`, the gate's functions). Folder
`evals/judging/readcap-2026-11-13/`: `cells-rules.json` (judge off),
`cells-judge.json`, `tools/` (the scripts). Agent-assisted results, not
certified Trusted Tester results; a development site, one repeat.

- **Why 600, and what more costs.** No reason was recorded: the cap came
  with the first import (2026-11-02) with only "up to 600 per page". Only
  2 of the 10 pages are over it (home 772 units, galleries 630), but every
  run compares against both, so it held all 30 cells. Read uncapped, a
  real page takes 0.2 s or less and 360 KB. The read is quadratic on one
  flat list (each element's CSS path counts its siblings): 600 links
  0.3 s, 5,000 1.1-5.3 s (nested lists to one flat list), 10,000 3.7-18.6
  s, 20,000 7.8-68 s, about 0.37 KB a unit. A run reads each page once,
  plus 9.C's marking read per page and 9.A's landing read per candidate
  (up to 8), so the cap stays, at 5,000 (6.5 times round 2's largest page).
- **Found on the way:** a page over the cap could reach 9.A's A3, A4 or G2
  before its truncation was looked at; a menu longer than the cap then
  gave DOES NOT APPLY ("nothing before the main content"). 9.A 1.4.0 puts
  a page over the cap in A2 (NEEDS REVIEW, not performed). Fixtures
  `9x/h1-big-menu` (700 units: FAIL, PASS, PASS) and `9x/h3-huge-menu`
  (5,001: NEEDS REVIEW on all three; 9.A gave DOES NOT APPLY before).
- **Cells (30):**

  | Test | Agree | Wrong PASS | Missed fail (DNA) | False FAIL | Other | NEEDS REVIEW |
  | --- | --- | --- | --- | --- | --- | --- |
  | 9.A | 10 (9 rule, 1 judge) | 0 | 0 | 0 | 0 | 0 |
  | 9.B | 9 | 0 | 0 | 0 | 1 | 0 |
  | 9.C | 4 (1 rule, 3 judge) | 0 | 0 | 0 | 1 | 5 |
  | Step 6, all three | 0 | 0 | 0 | 0 | 0 | 30 |
  | Round 2 C1, all three | 12 | 0 | 2 | 2 | 4 | 10 |

  Round 2's two wrong 9.A cells (CILab and 14592, Does Not Apply where
  the key fails) now FAIL with the key. "Other": 9.B and 9.C on CILab are
  Does Not Apply where the key passes (A3: CILab has 7 units and none is
  in a component the other pages have), as in round 2. NEEDS REVIEW: 9.C
  on home, galleries, 14592, 14194, 5340, where the judge answered unsure
  on some names (G3). Judge-off, 9.A was 9 of 10 (help waited on its one
  question) and 9.C 1 of 10.
- **19.A:** it reads the caller's pages from the same read, so links to T
  further down a long page now count. On these pages the one such link
  (home to `/search/`, unit 600 and after) changes no cell: 19.A on the
  search page already agreed (Pass).
- **Judge cost:** 9 requests (dry count: 53 questions, ~29k tokens of
  text); run: 14 calls, 0 failed, 95 answers, 26 unsure, 103 s in calls
  (9.C asks at most 12 per run and asks the rest once those are answered).
- **Not verified here:** repeats; 9.A-9.C beside the other tests in one
  full run (the cap changes no other test's read).

## Gate 2026-11-20-134: #134's rerun on all three rounds' frozen pages

`main` after #143 plus the double read; tests 4.A, 4.B, 4.C, 4.E, 4.F, 5.A
to 5.D, 5.F, 9.A to 9.C and 19.A; the server judge on gate 9c's 21 types;
Playwright's Chrome 153; every page from the freeze ("replay"); round 3 from
a copy of its freeze with the code its community pages load when used.
Against gate 9c: round 3, 11 moved (10 toward the key); round 2, 13 (3
toward, 10 to NEEDS REVIEW, mostly 19.A by the replay mode); round 1, 6 (1
toward, 5 to NEEDS REVIEW, 19.A by the mode and 4.F by the judge). **No PASS
or DOES NOT APPLY where a key fails.** A false DOES NOT APPLY of 9.A on
round 3's forum in the first run (an incomplete read of another page, kept
for the session) led to the double read. Details and every cell:
`judging/gate-2026-11-20-134/README.md` and `moved.md`. Agent-assisted
results, not certified Trusted Tester results; development pages.

## Judge eval 2026-11-20: 5.B after step 35a (#134)

5.B's question gets other items on a page with no `<form>` (5.B 1.14.0: a
control in the page's header, a navigation region or the footer is grouped
there), so its judge eval ran: `judge_eval.py prepare OUT 5.B` (31 cases
that ask, with the new `5a/f56` and `f57`), then `answer --backend api
--repeat 2 5.B`, the server judge's CLI route (`claude-sonnet-5-5`). Both
repeats: **31 of 31 match**, no wrong PASS, no inject page took the bait,
none left open. On f56 (round 3's SDE home: the header's "SDE" switcher no
longer in the search form) and f57 (a header search with its own button)
J1 answered all_descriptive both times, naming the field's label and the
button. Packets passed the leak grep (no fixture names or local addresses).
Not run: a fresh client agent on the packets. Results:
`judging/gate-2026-11-20-134/judge-eval-5b/`.

## Tool selection 2026-11-19: do agents pick TOBI's tools from the descriptions alone?

Evidence for the GSA hackathon's criterion "tool names and descriptions precise enough for an LLM to select them without ambiguity". `evals/tool_selection/` (how it works: its `README.md`): 27 plain-language cases (25 run in client mode, 26 in api mode), written and committed before any run (`cc86037`); Claude Code's own client (`claude -p`, CLI 2.1.329, isolated as the agent eval's CLI route) against a stub MCP server that serves the real server's tool list word for word in each judge mode and records calls; Sonnet 5.5 (`claude-sonnet-5-5`) and Haiku 5.5 (`claude-haiku-5-5`), 3 repeats, 306 runs a pass; scored by script (right tool or rightly none, jsonschema against the served `inputSchema`, required arguments, a caveat regex), no grading model. Before: the descriptions at `main` `2ec2c69` (PR #140). After: `9e78e40`, one change (`tobi_read_report`'s `content` and `compare_to`). Results, served tool lists (hashes in `meta.json`), report and debriefs: `evals/tool_selection/results/2026-11-19/`. Agent-assisted results are not involved; nothing is tested.

- **Accuracy, first TOBI call** (right tool, valid, required arguments, caveat where asked; one expectation corrected, below), before → after: **Sonnet 88% → 92%** (135 → 141 of 153), **Haiku 93% → 95%** (142 → 146 of 153). By mode, after: Sonnet api 92%, client 92%; Haiku api 95%, client 96%. As committed (no correction): Sonnet 86% → 90%, Haiku 92% → 93%. **The expected call made at any point** with valid, required arguments: Sonnet 98% → 100%, Haiku 93% → 96%.
- **Every case without earlier pending work was right in every run, both models, both modes**: all 9 `tobi_run_tt_tests` cases (54 of 54 runs per model; other_pages, a test subset, a single test, `no_time_limit` true and false, a re-test after a fix), all 4 `tobi_run_status` cases (job_id for "is it done yet", no job_id for "anything left", `finish=true` after the answers: 6 of 6 per model in each pass), `tobi_answer_questions` for a user's answers, `tobi_explain` with no run, reading one SCRT file. Arguments were schema-valid in 302 of 303 calls before and 304 of 304 after. **Should-not-call cases:** a non-.gov URL and "certify this page" were handled with a caveat in all 12 runs of each, in both passes, with no certification claim; a test TOBI does not implement (7.A) in 10 of 12 before and 11 of 12 after (each miss a Haiku run that hit the 4-turn cap before writing an answer).
- **The one description change.** "What changed since my last report?" (two runs' links in context): before, Sonnet put the older report in `content` in 3 of 6 runs and Haiku passed `report_uri` (which the tool refuses as not a report file, checked) in 2 of 6; after, **12 of 12 right**. Sonnet's `tobi_read_report` cases overall 9 → 15 of 18.
- **What the misses are, and why no description was changed for them.** (1) "Why did 4.D fail?" and "full details": Sonnet calls `tobi_run_status` first, then the right `tobi_explain` (9 of 12 runs in each pass), because the earlier result's to-do list says "Before reporting: call tobi_run_status"; its debriefs say so. (2) "Here's my tester's SCRT file, what differs?" with open questions pending: both models answer the open questions first (`next_step`: "Answer them now"), then compare; Haiku often runs out of turns first. Both come from results' to-do lists, not descriptions. (3) A person's answer to a question the server's judge left unsure (api mode): the committed case expected `tobi_answer_questions`, but the real server refuses any calling agent's answer to a judge-answered question (`judgment.py`, `record_answers`; a person's own page is roadmap row 18). Corrected in `corrections.toml`; the agents refused, and said why, in 5 of 6 runs before (one Haiku run tried the call) and 6 of 6 after.
- **Debriefs** (`--debrief`, one run per failing pattern, both models; verbatim in `debriefs.md`, never scored): ordering "came mostly from the `todo` list in the first run result"; in api mode "nothing in the tools said how a person's determination gets recorded"; `tobi_run_status` with nothing left says `"status": "outstanding"` beside "Nothing is left", which agents read as a contradiction (the real `Outstanding` model's fixed status; not changed here). The debrief turn has no tool definitions in context, so agents could not quote descriptions there and some said they "guessed" argument names they had in front of them: hints, not evidence.
- **Not measured.** The server's instructions (its own tool selection guide) were left out, so this measures the descriptions alone; output schemas were not served; earlier turns are given as text in the prompt, not as real tool-call turns; the stub's canned results are short; one client (Claude Code).
- **Cost** (list price, the CLI's result events): before $4.10, after $4.12, debrief runs $0.86, pilots $0.25.

## Follow-through 2026-11-19: does Agent A now finish the workflow?

Agent A (Sonnet 5.5, CLI route, prompt `round1-v1` with no extra paragraph, `--no-subagents --debrief`) on three live pages, each frozen first and run on its own: https://www.section508.gov/, https://www.nasa.gov/careers/ and https://www.weather.gov/ (a page with a form). Once in client mode and once with the server's judge (`--judge api`, new in `evals/agent/run.py`). Run from a worktree at `81b8029` (PR #140's descriptions). A behaviour check: no key, no accuracy claim. Folder `evals/judging/followthrough-2026-11-19/` (`ARCHIVE.md`); counts by `evals/agent/followthrough.py` from the run folders and transcripts, never from the agent's account, with the same code run on the 2026-11-19 compare's Agent A (`r3-followthrough.json`). Agent-assisted results, not certified Trusted Tester results.

| | Compare 2026-11-19, A (10 pages × 3 runs) | Now, client mode (3 pages) | Now, api mode (3 pages) |
| --- | --- | --- | --- |
| Open questions answered / unsure / left open | 251 / 58 / 3 of 312 | 6 / 0 / **12** of 18 | 16 / 3 / 0 of 19 (the judge) |
| Picture answers with the picture opened first (a `run://` read before the answer) | 23 of 243 (9%) | 0 of 5 | (the judge sees its pictures) |
| `tobi_explain` calls | 0 in 15 conversations | 1 in 3 | 0 in 3 |
| `finish=true` calls | 0 | 0 | 0 |
| Runs with follow-up calls (when `finish` applies) | 0 of 30 | 0 of 5 | 0 of 3 |
| `tobi_run_status` with no job_id before reporting | 4 in 15 | 0 in 3 | 0 in 3 |
| Report or pre-SCRT link read (the harness's agent has no file-writing tool) | 0 | 0 | 0 |
| The judge's unsure answers answered by the agent instead of relayed | | | **0 of 3**; all 3 final messages say a person checks them |

- **Not yet.** The steps that cost an extra call still mostly do not happen: no final status check, no report read, one `tobi_explain` (for the one FAIL on careers), no picture opened before a picture answer. The debriefs say why, in the agents' words: "I didn't think it would change anything", "I treated the task as done once the second run finished", "I relied on the attached image and did not open the `run://` resources".
- **`finish=true` was never needed**: no run here or in the compare had a follow-up call, so "no `finish=true` in any run" in the compare was not a skipped step. Part A shows agents choose it when follow-ups exist (6 of 6 per model in each pass).
- **weather.gov in client mode left 12 of 13 questions open.** Its first finished result showed 1 question (`more_questions: 12`; the result is cut to fit) and the answer result was 48k characters with the next one; the agent answered one, had its 4.F answer refused (no `seen`), then started a cross-page run and stopped. The server's judge answered all 13 on the same page (2 unsure). The agent also reported the tool's 3.2.3 FAIL as needs review "on my own judgment".
- **api mode: the agent relayed the judge's unsure answers** (0 of 3 answered by the agent, all named as waiting for a person), as the description and `next_step` ask.
- **Cost:** client $0.15, $0.13, $0.28; api $0.05, $0.08, $0.07 (the CLI's list price; the server judge's own `claude -p` tokens are separate: 9 calls, 78k cache-write and 3.6k output tokens, about $0.35 at the compare's implied rates); one stopped api attempt (about 15 s, deleted; `ARCHIVE.md`).

## Compare 2026-11-19: calling agent vs server judge, round 3's pages, 3 runs each

Round 3's 10 science.data.nasa.gov pages (the frozen copies), three ways, three runs each, all Sonnet 5.5 (`claude-sonnet-5-5`) on the CLI route at `main` `63bc397` (nothing in `src/`, `specs/`, `third_party/` or the lock files changed): **A** the calling agent with TOBI (the client judge; the server judge off, and all 309 recorded answers say `answered_by: client`), **B** the same agent with Playwright MCP only, **C** the server judge (21 types as in 9c, `tested_frozen`; prompt SHA-256 `e8320f2c…` in every report). A and B: `evals.agent.run --route cli --no-subagents --debrief`, prompt `round1-v1`, 5 groups of 2 pages a run. Folder `evals/judging/compare-2026-11-19-r3/`: `compare.md` and `compare.json` (made by `compare.py` from the committed files; `tests/test_compare_r3.py` checks that), `ARCHIVE.md` (what is in git and what is not), `restarts.md`, each arm's results. Verdicts come from 9c's cell scorer and from `evals.agent.score` with round 3's keys read in place; nothing here decides an outcome. **Round 3's pages are development pages: this is a rerun and is never reported in place of round 3's blind score.** Agent-assisted results, not certified Trusted Tester results.

- **Accuracy per TT test** (220 scored cells a run; 3 runs together = 660): A agree 407, PASS or DOES NOT APPLY where the key fails **0**, FAIL or DNA where the key passes 22, other 0, left for a person 231. C: 358, **0**, 32, 0, 270. The blind run: 118, 3, 28, 0, 71 (one run). **No unsafe cell in any of the six runs.** Split by who decided the cell: cells the rules decided, A 301 agree / 21 FAIL-vs-Pass / 171 left of 493, C 273 / 21 / 191 of 485 (the same code, different load); cells an answer decided, **A (the agent) 106 / 1 / 60 of 167, C (the judge) 85 / 11 / 79 of 175**. So the gap is in the answers: the server judge is unsure more often (33, 35 and 32 of 110, 109 and 108 questions; the agent 19, 20 and 19 of 105, 103 and 104) and its FAIL answers contradict the key more often. Tests where they differ most: 4.A (A 6 agree, C 0 of 30), 9.B (A 18, C 0), 5.B (A 18, C 6), 5.A (A 12, C 6), 5.C (A 28, C 21); 4.F is the other way (A 12, C 10, with 5 FAIL-vs-Pass for C). C's 9.B row is 9c's own (all left for a person); its 4.A is close to 9c's (1 agree of 10 there, 0 of 10 each run here).
- **Per WCAG criterion** (200 a run, the locked scorer's weights): A reported 0 false PASS and 0 missed fail in all 3 runs (weighted 115, 114, 111; agree 120/125, 120/126, 118/125 of decided; false FAIL 2, 3, 2). The same agent without TOBI (B): 1 false PASS in run 1, none after; weighted -46, 1, 65 **as the scorer reads it, because 3 of B's 15 final messages have an unparseable `RESULT:` line** (the outer brace is missing: g3-1, g3-2, g5-1; 80, 40 and 0 criteria count as no answer). With the brace added (a labelled sensitivity view, not the scorer's reading) B's weighted is 60, 65, 65 and it decides 106, 89 and 107 criteria to A's 125, 126 and 125, leaving 94, 111 and 93 for a person to A's 75, 74 and 75. The tool's own per-criterion results: A's 110, 109, 110; C's 88, 88, 87.
- **Completeness.** A asked 105, 103 and 104 questions, answered 86, 80 and 85, unsure 19, 20 and 19, **left 0, 3 and 0 unanswered** (run 2's three were the 4.F question on both Science Discovery Engine pages and one 5.B question on its home page, which that group's debrief names as 2.4.3 and 2.4.6); C asked 110, 109 and 108, answered 77, 74 and 76, unsure 33, 35 and 32, none open, 0 failed or retried calls. **The follow-through steps the tool asks for did not happen:** in the transcripts A made no `finish=true` call and no `tobi_explain` call in any run, and called `tobi_run_status` with no job id 1, 2 and 1 times in 15 conversations (10 `tobi_run_tt_tests` calls a run, one per page, none repeated). On pictures: A recorded a `seen` note on 63, 60 and 62 of its answers, reported a `picture_error` on 9, 8 and 9 and `not_viewed` on 9, 8 and 9, and made 4, 2 and 5 `run://` reads itself while 92, 92 and 99 pictures were attached to its results; its debriefs say it described attached crops without opening the named image (verbatim quotes, checked against the files, in `compare.md`). The server judge recorded `seen` on 98, 108 and 101 answers and no `not_viewed`. 2.4.5 and the other cross-page criteria on the two Angular pages (p09, p10): three A debriefs say the tool compared a page with itself.
- **Consistency across the 3 runs.** The same TT outcome in all 3 runs: **A 216 of 220 cells, C 214 of 220**; the cells an answer decided, A 55 of 57, C 53 of 59. Flipped cells: A 4 (p02 5.D and p09 5.C, an answer decided; p10 2.C and 2.D, `scan`: run 2's 6.5-second watch saw signs of change and the 24-hour timer check that gave DNA in runs 1 and 3 did not decide it), C 6, all answer-decided (4.F on p01 and p04, 5.A and 5.B on p02 and p04). The same answer to the same question: A 85 of 99 (asked in every run), C 93 of 107. The agent's reported criteria: A 195 of 200 the same, B 95 (141 with the brace added).
- **Cost and time.** List prices from the summaries (A's and B's cost is the CLI's own figure): **A $1.68 a run** (1.68, 1.62, 1.75; $0.17 and about 173 s a page; 29 min a run), **B $0.61** (0.64, 0.54, 0.66; $0.06 and 27 s a page; 4.5 min a run). **C's judge 41, 43 and 42 calls a run, 84 to 88 input and 17.8 to 19.4 thousand output tokens, 283 to 376 thousand cache-write tokens, 200 to 221 s in calls (summed); the CLI route records no price, so the dollar figure is an estimate** at the rates A's and B's list prices imply exactly ($2, $10, $0.10 and $4 a million tokens for input, output, cache read and cache write; zero residual over all 30 groups): $1.47 a run (1.70, 1.39, 1.32; $0.15 a page). C's run time, which includes the browser, is 2,079, 2,065 and 2,066 s (207 s a page). The browser work is the same TOBI run in A and C; A's wall time includes the agent's own turns.
- **Why the judge is unsure more often** (`compare.md`, `docs/solutions/server-judge.md`): on 299 question instances the judge and the agent both answered 173 times and gave the same answer 164; only the judge was unsure 69 times, only the agent 27, both 30. The judge's recorded reasons name what is missing: on 4.E all 24 say the page marks the card modal while the picture shows a small card (the agent answered `content_only` every time), on 5.A, 5.B and 5.C that no search field is visible in the picture. The agent's debriefs say it often answered without opening the picture (12 of 15), and its own unsure answers on 5.D (20 of 61, against the judge's 2 of 59) were "not examined closely". Unsure costs coverage (89 to 91 cells left for a person a run against 77) and the judge's answers had 11 FAIL-against-a-passing-key cells to the agent's 1; step 42 on the roadmap asks each unsure answer to say what would settle it.
- **What this does and does not show.** One model, one site, 10 pages, 3 runs, development pages. A's lead over C comes from answers about pictures, which A's own debriefs say were looked at thinly, and the scorer cannot see how an answer was reached. **19.A on p01 to p03** is NEEDS REVIEW with W4 in every repeat (the analytics script Chromium blocks, as in 9c; logged in `docs/ROADMAP.md`); no page's live 19.A load failed otherwise, so no page was rerun alone. The container restarted four times, probably while the session was idle; the lesson is in `docs/solutions/environment.md`, each restart in `restarts.md`, and no result was hand-restored.

## Gate 2026-11-17-9c: all three rounds' frozen pages, the server judge on every type (roadmap step 9c)

Round 1's 9 www.nasa.gov pages, round 2's 10 svs.gsfc.nasa.gov pages and round 3's 10 science.data.nasa.gov pages, each tested once, every TT test built (`checks.REGISTRY`), the server judge on 9b's 21 types (CLI route, `claude-sonnet-5-5`, prompt SHA-256 `e8320f2c…`, as in 9b), `tested_frozen` as 9b ran it (the tested page from the freeze; 19.A's site search and suggested pages load live under the usual rules). Code: `main` at `30e948c` (#120) with PR 121 (`b7ee9c0`, 4.F 1.11.0) merged in, as asked. Folder `evals/judging/gate-2026-11-17-9c/`: `compare-round1.json`, `compare-round2.json` and `compare-round3.json` (`sides.real`: page, test, key, tool, verdict for every cell, scored by each round's own scorer and keys; the baseline's side beside it; `moved`; `times`), the same as `.md`, `roundN/dry-r1.json` (the count), `roundN/gate.json`, `compare.py`. Page files (`roundN/r1/runs`, `roundN/r1/results`) stay out of git. Agent-assisted results, not certified Trusted Tester results. **Round 3's pages are development pages: this is a rerun and is never reported in place of round 3's blind score.** Both rounds ran on this container's default trust plus `UPSTREAM_PROXY` (the container's gateway).

- **Round 2 (svs.gsfc.nasa.gov), the search question.** Checked first, by one load per host through the tool's browser: www.nasa.gov 200, science.data.nasa.gov 200, svs.gsfc.nasa.gov **502** on a search address I guessed (`/search/?q=earth`; the tool's own form is `/search?search=<heading>`). **That check was wrong or out of date:** a re-probe after round 2's run loads all three svs addresses with 200 (the real form, my guess, and a suggested page). In the run itself svs's live search and suggested pages loaded for p03 to p10 and **did not for p01 and p02**, the first two pages of the run (19.A: NEEDS REVIEW, "could not be loaded", rows W8 W4), so the failure was intermittent here; 9b's explanation (the certificate chain) is not shown to hold or not hold today. **p01 and p02 were therefore run again, each page alone after all other runs (`gate-2026-11-17-9c-r2rerun/`, Abby asked)**: round 2's `results/p01` and `p02` (and so every figure here) are the reruns, the first attempts are kept in `round2/r1/results-first-attempt/` (git-ignored). The rerun's 19.A is FAIL on both pages (rows W3 G4: the site navigation is the only way, the site search did not find the page by its heading), which agrees with your key. 4.F on p02 differs between the two attempts (the first an agreeing PASS, the rerun a false FAIL), so the judge's answer varies run to run on that page. Round 2's dry run was dropped (the real run records the judge's own counts).
- **Checked first.** Round 2's archive (Drive `round2-frozen.zip`, 12 parts): SHA-256 of the parts and of the rejoined zip match `SHA256SUMS.txt`, and all 12 files match `MANIFEST-round2-frozen.json`. Round 3's frozen archive (Abby's Drive zip `round3-frozen-2026-11-16b`): SHA-256 `2ce3446a…` as in `ARCHIVE.md`, and all 30 files match `frozen-MANIFEST.sha256`. Round 1's archive (Drive `round1-frozen.zip`, dated 2026-11-04): 9 recordings, `freeze.json` and `index.json` identical to git; **no hash to check the recordings against**, as in 9b. **Round 1's freeze predates the chunk store (2026-11-09)**, so its recordings may lack code loaded on use (guard GU); a refreeze and a reference repeat of these pages is its own experiment (its own pull request), never in the tally.
- **Cost.** Round 2's real run (final results, with the two reruns): 52 calls, 264 questions answered (53 "unsure"), 0 failed, 0 left open; the two first attempts' calls are not in these counts. Dry counts (judge off, no model call; round 1 and 3 only): round 1 27 requests, 58 questions, ~87.1k text tokens, 126 pictures; round 3 35 requests, 90 questions, ~81.0k tokens, 92 pictures. Real runs (the judge's own records): round 1 27 calls, 58 questions answered (6 "unsure"), 0 failed, 0 left open; round 3 43 calls, 109 questions answered (29 "unsure"), 0 failed, 0 left open (more than the dry count: the judge's answers open follow-up questions). Output tokens 12.0k and 18.4k. The container restarted three times; round 3 and round 1 were finished page by page, so each page was run once, and `run.json`'s page lists were restored by hand (noted in each).
- **Totals per round, all scored cells (key given), this run beside the baseline.** Round 2 (220 cells) beside 9b: agree 131 (122), PASS or DOES NOT APPLY where the key fails **0 (0)**, FAIL or DOES NOT APPLY where the key passes 9 (11), other 1 (1: 3.A on 14194, as in 9b), left for a person 79 (86). Round 1 (153 cells) beside 9b: agree 79 (74), PASS or DOES NOT APPLY where the key fails **0 (0)**, FAIL or DOES NOT APPLY where the key passes 3 (2), other 0 (0), left for a person 71 (77). Round 3 (220 cells) beside the blind run: agree 121 (118), PASS or DOES NOT APPLY where the key fails **0 (3: 4.F, 5.F, 5.G)**, FAIL or DOES NOT APPLY where the key passes 11 (28), other 0 (0), left for a person 88 (71). **No unsafe cell** (PASS or DOES NOT APPLY where the key fails) in any of the three rounds.
- **Per test** (this run beside the earlier figures; a test with no key on a round's pages is not listed):

  **Round 1** (agree / PASS or DNA where the key fails / FAIL or DNA where the key passes / other / left for a person):

  | Test | Gate 2026-11-17-9c | 9b |
  | --- | --- | --- |
  | 4.A | 0 / 0 / 0 / 0 / 9 | 0 / 0 / 0 / 0 / 9 |
  | 4.B | 9 / 0 / 0 / 0 / 0 | 9 / 0 / 0 / 0 / 0 |
  | 4.C | 6 / 0 / 0 / 0 / 3 | 5 / 0 / 0 / 0 / 4 |
  | 4.D | 3 / 0 / 0 / 0 / 6 | 3 / 0 / 0 / 0 / 6 |
  | 4.E | 6 / 0 / 0 / 0 / 3 | 6 / 0 / 0 / 0 / 3 |
  | 4.F | 8 / 0 / 0 / 0 / 1 | 4 / 0 / 0 / 0 / 5 |
  | 5.A | 9 / 0 / 0 / 0 / 0 | 9 / 0 / 0 / 0 / 0 |
  | 5.B | 0 / 0 / 1 / 0 / 8 | 0 / 0 / 0 / 0 / 9 |
  | 5.C | 1 / 0 / 1 / 0 / 7 | 1 / 0 / 1 / 0 / 7 |
  | 5.D | 1 / 0 / 1 / 0 / 7 | 1 / 0 / 1 / 0 / 7 |
  | 5.F | 0 / 0 / 0 / 0 / 9 | 0 / 0 / 0 / 0 / 9 |
  | 5.G | 0 / 0 / 0 / 0 / 9 | 0 / 0 / 0 / 0 / 9 |
  | 5.H | 6 / 0 / 0 / 0 / 3 | 6 / 0 / 0 / 0 / 3 |
  | 9.A | 8 / 0 / 0 / 0 / 1 | 8 / 0 / 0 / 0 / 1 |
  | 9.B | 9 / 0 / 0 / 0 / 0 | 9 / 0 / 0 / 0 / 0 |
  | 9.C | 9 / 0 / 0 / 0 / 0 | 9 / 0 / 0 / 0 / 0 |
  | 19.A | 4 / 0 / 0 / 0 / 5 | 4 / 0 / 0 / 0 / 5 |

  **Round 1: every cell that moved since 9b (6), with whether the key agrees:**

  | Page | Test | Key | 9b | Now | Key |
  | --- | --- | --- | --- | --- | --- |
  | p01 | 4.C | Pass | NEEDS REVIEW | Pass | yes |
  | p05 | 4.F | Pass | NEEDS REVIEW | Pass | yes |
  | p05 | 5.B | Pass | NEEDS REVIEW | Fail | no |
  | p06 | 4.F | Pass | NEEDS REVIEW | Pass | yes |
  | p07 | 4.F | Pass | NEEDS REVIEW | Pass | yes |
  | p09 | 4.F | Pass | NEEDS REVIEW | Pass | yes |

  **Round 2** (agree / PASS or DNA where the key fails / FAIL or DNA where the key passes / other / left for a person):

  | Test | Gate 2026-11-17-9c | 9b |
  | --- | --- | --- |
  | 2.A | 7 / 0 / 0 / 0 / 3 | 7 / 0 / 0 / 0 / 3 |
  | 2.B | 4 / 0 / 0 / 0 / 6 | 4 / 0 / 0 / 0 / 6 |
  | 2.C | 4 / 0 / 0 / 0 / 6 | 4 / 0 / 0 / 0 / 6 |
  | 2.D | 4 / 0 / 0 / 0 / 6 | 4 / 0 / 0 / 0 / 6 |
  | 3.A | 7 / 0 / 0 / 1 / 2 | 6 / 0 / 0 / 1 / 3 |
  | 4.A | 2 / 0 / 1 / 0 / 7 | 2 / 0 / 1 / 0 / 7 |
  | 4.B | 9 / 0 / 0 / 0 / 1 | 9 / 0 / 0 / 0 / 1 |
  | 4.C | 9 / 0 / 0 / 0 / 1 | 9 / 0 / 0 / 0 / 1 |
  | 4.D | 1 / 0 / 2 / 0 / 7 | 1 / 0 / 2 / 0 / 7 |
  | 4.E | 9 / 0 / 0 / 0 / 1 | 9 / 0 / 0 / 0 / 1 |
  | 4.F | 2 / 0 / 2 / 0 / 6 | 2 / 0 / 2 / 0 / 6 |
  | 5.A | 6 / 0 / 1 / 0 / 3 | 6 / 0 / 1 / 0 / 3 |
  | 5.B | 6 / 0 / 2 / 0 / 2 | 6 / 0 / 3 / 0 / 1 |
  | 5.C | 10 / 0 / 0 / 0 / 0 | 10 / 0 / 0 / 0 / 0 |
  | 5.D | 3 / 0 / 0 / 0 / 7 | 3 / 0 / 0 / 0 / 7 |
  | 5.F | 3 / 0 / 0 / 0 / 7 | 3 / 0 / 1 / 0 / 6 |
  | 5.G | 3 / 0 / 0 / 0 / 7 | 3 / 0 / 1 / 0 / 6 |
  | 5.H | 9 / 0 / 0 / 0 / 1 | 9 / 0 / 0 / 0 / 1 |
  | 9.A | 10 / 0 / 0 / 0 / 0 | 10 / 0 / 0 / 0 / 0 |
  | 9.B | 9 / 0 / 0 / 0 / 1 | 9 / 0 / 0 / 0 / 1 |
  | 9.C | 5 / 0 / 0 / 0 / 5 | 4 / 0 / 0 / 0 / 6 |
  | 19.A | 9 / 0 / 1 / 0 / 0 | 2 / 0 / 0 / 0 / 8 |

  **Round 2: every cell that moved since 9b (18), with whether the key agrees:**

  | Page | Test | Key | 9b | Now | Key |
  | --- | --- | --- | --- | --- | --- |
  | p01 | 9.C | Pass | Pass | NEEDS REVIEW | left for a person |
  | p01 | 19.A | Fail | NEEDS REVIEW | Fail | yes |
  | p02 | 4.F | Pass | NEEDS REVIEW | Fail | no |
  | p02 | 19.A | Fail | NEEDS REVIEW | Fail | yes |
  | p03 | 4.F | Pass | Fail | Pass | yes |
  | p03 | 5.B | Pass | Fail | NEEDS REVIEW | left for a person |
  | p04 | 4.F | Pass | Pass | NEEDS REVIEW | left for a person |
  | p05 | 19.A | Pass | NEEDS REVIEW | Fail | no |
  | p06 | 19.A | Pass | NEEDS REVIEW | Pass | yes |
  | p07 | 19.A | Pass | NEEDS REVIEW | Pass | yes |
  | p08 | 3.A | Does Not Apply | NEEDS REVIEW | Does Not Apply | yes |
  | p08 | 5.F | Pass | Fail | NEEDS REVIEW | left for a person |
  | p08 | 5.G | Pass | Fail | NEEDS REVIEW | left for a person |
  | p08 | 9.C | Pass | NEEDS REVIEW | Pass | yes |
  | p08 | 19.A | Pass | NEEDS REVIEW | Pass | yes |
  | p09 | 9.C | Pass | NEEDS REVIEW | Pass | yes |
  | p09 | 19.A | Pass | NEEDS REVIEW | Pass | yes |
  | p10 | 19.A | Pass | NEEDS REVIEW | Pass | yes |

  **Round 3** (agree / PASS or DNA where the key fails / FAIL or DNA where the key passes / other / left for a person):

  | Test | Gate 2026-11-17-9c | blind |
  | --- | --- | --- |
  | 2.A | 10 / 0 / 0 / 0 / 0 | 10 / 0 / 0 / 0 / 0 |
  | 2.B | 10 / 0 / 0 / 0 / 0 | 10 / 0 / 0 / 0 / 0 |
  | 2.C | 7 / 0 / 0 / 0 / 3 | 6 / 0 / 0 / 0 / 4 |
  | 2.D | 7 / 0 / 0 / 0 / 3 | 6 / 0 / 0 / 0 / 4 |
  | 3.A | 10 / 0 / 0 / 0 / 0 | 10 / 0 / 0 / 0 / 0 |
  | 4.A | 1 / 0 / 0 / 0 / 9 | 1 / 0 / 2 / 0 / 7 |
  | 4.B | 8 / 0 / 0 / 0 / 2 | 8 / 0 / 0 / 0 / 2 |
  | 4.C | 7 / 0 / 0 / 0 / 3 | 7 / 0 / 0 / 0 / 3 |
  | 4.D | 3 / 0 / 0 / 0 / 7 | 3 / 0 / 0 / 0 / 7 |
  | 4.E | 7 / 0 / 0 / 0 / 3 | 6 / 0 / 3 / 0 / 1 |
  | 4.F | 3 / 0 / 1 / 0 / 6 | 4 / 1 / 3 / 0 / 2 |
  | 5.A | 2 / 0 / 3 / 0 / 5 | 3 / 0 / 3 / 0 / 4 |
  | 5.B | 3 / 0 / 4 / 0 / 3 | 3 / 0 / 6 / 0 / 1 |
  | 5.C | 7 / 0 / 1 / 0 / 2 | 7 / 0 / 1 / 0 / 2 |
  | 5.D | 1 / 0 / 2 / 0 / 7 | 1 / 0 / 4 / 0 / 5 |
  | 5.F | 6 / 0 / 0 / 0 / 4 | 6 / 1 / 0 / 0 / 3 |
  | 5.G | 6 / 0 / 0 / 0 / 4 | 6 / 1 / 0 / 0 / 3 |
  | 5.H | 9 / 0 / 0 / 0 / 1 | 7 / 0 / 0 / 0 / 3 |
  | 9.A | 6 / 0 / 0 / 0 / 4 | 6 / 0 / 0 / 0 / 4 |
  | 9.B | 0 / 0 / 0 / 0 / 10 | 0 / 0 / 6 / 0 / 4 |
  | 9.C | 6 / 0 / 0 / 0 / 4 | 6 / 0 / 0 / 0 / 4 |
  | 19.A | 2 / 0 / 0 / 0 / 8 | 2 / 0 / 0 / 0 / 8 |

  **Round 3: every cell that moved since blind (28), with whether the key agrees:**

  | Page | Test | Key | blind | Now | Key |
  | --- | --- | --- | --- | --- | --- |
  | p01 | 4.F | Pass | Pass | NEEDS REVIEW | left for a person |
  | p01 | 5.B | Pass | Does Not Apply | NEEDS REVIEW | left for a person |
  | p01 | 9.B | Pass | Fail | NEEDS REVIEW | left for a person |
  | p02 | 9.B | Pass | Fail | NEEDS REVIEW | left for a person |
  | p03 | 5.A | Pass | Pass | NEEDS REVIEW | left for a person |
  | p03 | 5.F | Fail | Pass | NEEDS REVIEW | left for a person |
  | p03 | 5.G | Fail | Pass | NEEDS REVIEW | left for a person |
  | p03 | 9.B | Pass | Fail | NEEDS REVIEW | left for a person |
  | p04 | 9.B | Pass | Fail | NEEDS REVIEW | left for a person |
  | p05 | 9.B | Pass | Fail | NEEDS REVIEW | left for a person |
  | p06 | 5.B | Pass | Does Not Apply | NEEDS REVIEW | left for a person |
  | p06 | 9.B | Pass | Fail | NEEDS REVIEW | left for a person |
  | p07 | 4.A | Pass | Fail | NEEDS REVIEW | left for a person |
  | p07 | 4.E | Pass | Fail | NEEDS REVIEW | left for a person |
  | p07 | 4.F | Pass | Does Not Apply | NEEDS REVIEW | left for a person |
  | p07 | 5.D | Pass | Does Not Apply | NEEDS REVIEW | left for a person |
  | p07 | 5.H | Does Not Apply | NEEDS REVIEW | Does Not Apply | yes |
  | p08 | 4.A | Pass | Fail | NEEDS REVIEW | left for a person |
  | p08 | 4.E | Pass | Fail | NEEDS REVIEW | left for a person |
  | p08 | 4.F | Fail | Does Not Apply | NEEDS REVIEW | left for a person |
  | p08 | 5.D | Pass | Does Not Apply | NEEDS REVIEW | left for a person |
  | p08 | 5.H | Does Not Apply | NEEDS REVIEW | Does Not Apply | yes |
  | p09 | 4.A | Fail | Fail | NEEDS REVIEW | left for a person |
  | p09 | 4.F | Pass | Fail | NEEDS REVIEW | left for a person |
  | p10 | 2.C | Does Not Apply | NEEDS REVIEW | Does Not Apply | yes |
  | p10 | 2.D | Does Not Apply | NEEDS REVIEW | Does Not Apply | yes |
  | p10 | 4.A | Fail | NEEDS REVIEW | Fail | yes |
  | p10 | 4.E | Pass | Fail | Pass | yes |

- **What moved, round 1.** Five cells went from NEEDS REVIEW to an agreeing PASS (4.C on p01, 4.F on p05, p06, p07, p09). **One went from NEEDS REVIEW to a false FAIL: 5.B on p05 (the missions page, where the key passes); a judge answer, one repeat, I did not trace it.** 19.A is as in 9b (4 agree, 5 left): its site search and suggested pages loaded live on this site.
- **What moved, round 3, since the blind run (28 cells; counts from `compare-round3.json`).** To an agreeing outcome: 6 (NEEDS REVIEW to agree: 5.H on p07 and p08, 2.C and 2.D on p10, 4.A on p10; false FAIL to agree: 4.E on p10). **The blind run's three unsafe cells are gone, all now NEEDS REVIEW:** 5.F and 5.G on p03 (PASS where the key fails) and 4.F on p08 (DOES NOT APPLY where the key fails). 11 false FAILs went to NEEDS REVIEW (9.B on p01 to p06, 4.E on p07 and p08, 4.A on p07 and p08, 4.F on p09) and 5 DOES NOT APPLY cells where the key passes went to NEEDS REVIEW (5.B on p01 and p06, 4.F on p07, 5.D on p07 and p08). **Three cells that agreed with the key are now left for a person** (4.F on p01, 5.A on p03, 4.A on p09). No cell moved to a wrong outcome. Steps 21, 22, 23, 31 and 36 explain most of this; 9.B's NEEDS REVIEW on every page is step 31 (rows N5, N6), so 9.B has 0 agreeing cells on this site.
- **What moved, round 2, since 9b (18 cells; from `compare-round2.json`).** To an agreeing outcome: 11 (NEEDS REVIEW to agree: 19.A on p01, p02 and p06 to p10, 3.A on p08, 9.C on p08 and p09; false FAIL to agree: 4.F on p03). Three false FAILs of 9b went to NEEDS REVIEW (5.B on p03, 5.F and 5.G on p08). **Two cells that agreed with the key are now left for a person** (9.C on p01, 4.F on p04). **Two new false FAILs (FAIL where the key passes):** 4.F on p02 (a judge answer; the first attempt agreed) and **19.A on p05 (CILab)**: the site search loaded and did not find the page by its heading (rows W6, W3), the same false FAIL 9a had; 9b had NEEDS REVIEW there because nothing could load. 19.A overall: 9 agree, 1 false FAIL, 0 left (9b: 2, 0, 8).
- **Time budgets.** Round 2: nothing ran out. Round 1: 5.D ran out on p05 (the missions page, 592.0 s of 600 s), as in 9a and 9b. Round 3: 4.E ran out on p07 (52.1 s of 60 s) and p08 (53.4 s); on both it is NEEDS REVIEW (a dialog opens on focus and the walk could not tell whether it takes over the page). Nothing else ran out in either round.
- **Not verified here:** repeats (one run per round); whether round 1's old freeze gives the same cells as a new one (an experiment, in its own pull request); why 5.B on round 1's p05 became a false FAIL.

## Experiment: round 1 on a refreeze, beside step 9c

Not part of step 9c's tally and not in the README's status table. Round 1's nine pages were frozen again on 2026-11-18 (`evals/judging/gate-2026-11-17-9c/round1-refrozen/`; the original freeze is untouched), the recordings compared with the old ones, and the tests run again on the refreeze (`apijudge_gate.py --frozen-dir`). No page's source is byte-identical (the site's asset names and its site-wide news list changed); the text inside `<main>` is identical on 5 of 9 pages. Same-content pages: 80 of 85 keyed cells the same; changed-content pages: 65 of 68. No cell PASSes or DOES NOT APPLYs where the key fails. Every differing cell, with its rows, is in [`judging/gate-2026-11-17-9c-refrozen/README.md`](judging/gate-2026-11-17-9c-refrozen/README.md). Agent-assisted results, not certified Trusted Tester results.

## Gate 2026-11-17, step 23: the rerun after the page is drawn, all three rounds' frozen pages

`main` after #112 (step 23) and #113; tests 4.A to 4.F, 5.A to 5.D, 5.F to 5.H, 9.A to 9.C and 19.A; the server judge on 9b's 21 types; every page from the freeze (none live), one round at a time. Folder `evals/judging/gate-2026-11-17-step23/`: [`README.md`](judging/gate-2026-11-17-step23/README.md) gives every moved cell beside the key with its cause, `moved.md` the rows. Agent-assisted results, not certified Trusted Tester results. **No unsafe cell** (PASS or DOES NOT APPLY where the key fails) in any round. Step 23 moved round 3 only: 4.E's three false FAILs on p07, p08, p10 (two to NEEDS REVIEW, one to an agreeing PASS) and five 5.F, 5.G, 5.H cells on p07, p08 to an agreeing DOES NOT APPLY; the walk reaches 76 of 76 and 91 of 91. Rounds 1 and 2 moved only by the judge's answers (round 2's 4.F: three new false FAILs, the J1 answer varying), the first rerun's load effects going away, and round 1's 19.A, which is NEEDS REVIEW from the freeze (no saved search or suggested pages; 9b ran them live). False FAILs on the first rerun's tests: round 1 4 to 3, round 2 7 to 9, round 3 9 to 6.

## Gate 2026-11-17: the rerun for steps 21, 36 and 22, all three rounds' frozen pages

`main` after #109, #110 and #111, before step 23; tests 4.A, 4.C to 4.F, 5.A to 5.D, 5.F to 5.H; the server judge on 9b's 21 types; every page from the freeze (none live). Folder `evals/judging/gate-2026-11-17/`: [`README.md`](judging/gate-2026-11-17/README.md) gives every moved cell beside the key with its cause; `moved.md` is generated by `compare.py`. **The three unsafe cells of round 3 are gone** (p03 5.F and 5.G, step 21; p08 4.F, step 22), and so are round 2's two false FAILs on 5340 (step 36) and round 3's two false FAILs of 4.A on p07 and p08 (step 22). No moved cell became a PASS or a DOES NOT APPLY the key fails. The first attempt found step 22 too sensitive (round 2's home page, 145 then 146 elements) and was stopped; #111 narrowed it. Running three rounds at once let round 1's feedback popup open on two pages and the walk miss one link on round 2's home page: those four cells were checked alone and gave their usual outcomes. One new false FAIL reproduced alone, round 1's missions page 5.B (step 29 or the judge, not these steps). Round 3's pages are development pages: this is a rerun, never in place of its score. Agent-assisted results, not certified Trusted Tester results.

## Gate 2026-11-16: both rounds' pages, the server judge on every type, one repeat (roadmap step 9b)

Round 2's 10 frozen svs.gsfc.nasa.gov pages and round 1's 9 frozen www.nasa.gov pages, each tested once at `main` `ece881b` (PR 98; `src/` is main's, this branch changes none of it) with the server judge switched on for all 21 types it can take (4.C stays with the client), CLI route, `claude-sonnet-5-5`, prompt SHA-256 `e8320f2c…` (as in 9a). **19.A could not be checked on round 2** (below): its live search cannot run from the test container, so round 2's 19.A cells are NEEDS REVIEW and are not comparable with 9a's. Folder `evals/judging/gate-2026-11-16/`: `roundN/dry-r1.json` (the count), `roundN/gate.json`, `compare-round1.md` and `compare-round2.md` (and `.json`), `combined.md`, `compare.py` (9a's, with a 9a side), `testpages/` (the judge eval's results). The page files (`roundN/r1/results/`, `roundN/dry/`) are kept out of git (`.gitignore`). Scored with each round's own scorer and keys, as in 9a. Agent-assisted results, not certified Trusted Tester results; two development sites, one repeat. Abby's instructions for 9b: the same as 9a on main's head, `JUDGE_TYPES` unchanged.

- **Checked first.** Round 2's frozen archive: every file matches Abby's manifest. Round 1's recordings: intact zips, each index entry present, **no hash to check them against**. Browser trust: **fails for svs.gsfc.nasa.gov, fine for www.nasa.gov.** svs.gsfc.nasa.gov renewed its certificate on 2026-11-16 (12:59 UTC) and serves only the leaf, not its intermediate (Let's Encrypt YR2, issued by Root YR, a root this container does not trust). Node's fetch in the navigation guard failed ("unable to verify the first certificate"). I fetched YR2 and Root YR (cross-signed by ISRG Root X1) from the addresses in the certificates, checked that `openssl verify` chains leaf, YR2, Root YR to X1 in the system store, and gave a test process a bundle with them (`NODE_EXTRA_CA_CERTS`): the page then loaded. The browser's requests still get **502 "upstream request failed" from the container's proxy** (the platform's, not `egress.py`; curl through it gets the same files with 200). Adding the two certificates to the browser's NSS store as untrusted intermediates did not change it (removed again). A direct connection (no proxy, the gateway's CAs trusted in a throwaway store) was refused by the session's safety classifier and not tried. Abby then chose to run round 2 knowing 19.A cannot be checked; **the round 2 runs used the container's default trust, so every live request fails fast** and 19.A says NEEDS REVIEW (rows W4 and G3), never a result.
- **Cost.** Dry count: round 1 27 requests, 56 questions, ~91.7k text tokens, 122 pictures (9a: 34, 75, ~103k, 131); round 2 50 requests, 274 questions, ~250.6k tokens, 209 pictures (9a: 47, 186, ~200k, 177; the step 8 readers ask about more forms and frames). Run (the judge's own record): round 1 27 calls, 58 questions answered; round 2 53 calls, 312 questions answered (56 "unsure"); **0 failed, 0 left open in both.** Input tokens: round 1 ~0.28M, round 2 ~0.74M (9a: ~0.66M); output 13.4k and 40.2k; 357 s in round 2's calls. Browser time: round 1 57 min (dry 53), round 2 75 min (dry 75). The container's proxy moved from port 40831 to 36829 during round 1's dry run, so `.env`'s `UPSTREAM_PROXY` was stale and that run's live requests all failed: **round 1's dry-run 19.A cells are not valid.** The real runs used the refreshed address and hold no such error; round 1's 19.A live search ran on every page that has one (found on 6, not found on 1, none to run on 2).
- **All scored cells.** No false PASS and no missed fail (wrong DOES NOT APPLY) in any run, judge-decided or rule-decided.

  | Run | Scored | False PASS | Missed fail | False FAIL | Other | Needs review (CN) | Agree (of decided) |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | Round 2, 9b | 220 | **0** | **0** | **11** | 1 | 86 (4) | 122/134 |
  | Round 2, 9b dry run (judge off) | 220 | 0 | 0 | 2 | 1 | 120 (3) | 97/100 |
  | Round 2, 9a | 220 | 0 | 0 | 6 | 1 | 129 (14) | 84/91 |
  | Round 2, step 6 | 220 | 0 | 0 | 11 | 1 | 152 (14) | 56/68 |
  | Round 2, arm C repeats 1-3 | 220 | 3 | 2 | 24-26 | 9 | 86-88 (0) | 94/132-134 |
  | Round 1, 9b | 153 | **0** | **0** | **2** | 0 | 77 (27) | 74/76 |
  | Round 1, 9b dry run (judge off; 19.A invalid) | 153 | 0 | 0 | 1 | 0 | 92 (22) | 60/61 |
  | Round 1, 9a | 153 | 0 | 0 | 12 | 0 | 94 (30) | 47/59 |
  | Round 1, locked arms A1-A3 (old rules) | 136-153 | 0 | 0 | 1-3 | 0 | 84-99 (0) | 49-51/52-54 |

  Judge-decided cells: round 2 64 (9a 56, step 6 54): 0 false PASS, 0 missed fail, **10 false FAILs (9a 4)**, 24 NEEDS REVIEW (1 CN), 30/40 agree (9a 22/26, step 6 14/18, arm C 16/27-29). Round 1: 30 (9a 36): 1 false FAIL (9a 11), 16 NEEDS REVIEW (5 CN), 13/14 agree (9a 10/21). Rule-decided cells: round 2 156 (9a 164): 1 false FAIL (9a 2, step 6 7), 1 other, 62 NEEDS REVIEW (3 CN), 92/94 agree (9a 62/65); round 1 123 (9a 117): 1 false FAIL, 61 NEEDS REVIEW (22 CN), 61/62 agree (9a 37/38).
- **In short.** More cells are decided and more agree (round 2: 134 decided and 122 agree, against 91 and 84 in 9a; round 1: 76 and 74, against 59 and 47). The price on round 2 is false FAILs: 11 against 6 in 9a, six of them new, all judge answers on forms (below). Round 1's false FAILs fell from 12 to 2. Nothing went wrong in the dangerous direction: no false PASS, no missed fail.
- **Per TT test** (a test with no key on a round's pages is not scored; no test had a false PASS or a missed fail; 19.A's round 2 figure is the container's limit):

  | Test | Round 2, 9b | Round 2, 9a | Round 2, step 6 | Round 1, 9b | Round 1, 9a | Judge cells (R2 + R1, 9b) |
  | --- | --- | --- | --- | --- | --- | --- |
  | 2.A | 7/10; 3 NR; 0 wrong | 7/10; 3 NR; 0 wrong | 7/10; 3 NR; 0 wrong | - | - | 0 |
  | 2.B | 4/10; 6 NR; 0 wrong | 1/10; 9 NR; 0 wrong | 1/10; 9 NR; 0 wrong | - | - | 3 |
  | 2.C | 4/10; 6 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 0/10; 10 NR; 0 wrong | - | - | 0 |
  | 2.D | 4/10; 6 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 0/10; 10 NR; 0 wrong | - | - | 0 |
  | 3.A | 6/10; 3 NR; 1 wrong | 3/10; 6 NR; 1 wrong | 3/10; 6 NR; 1 wrong | - | - | 0 |
  | 4.A | 2/10; 7 NR; 1 wrong | 2/10; 7 NR; 1 wrong | 2/10; 7 NR; 1 wrong | 0/9; 9 NR; 0 wrong | 0/9; 8 NR; 1 wrong | 9 |
  | 4.B | 9/10; 1 NR; 0 wrong | 9/10; 1 NR; 0 wrong | 9/10; 1 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 6 |
  | 4.C | 9/10; 1 NR; 0 wrong | 2/10; 8 NR; 0 wrong | 2/10; 8 NR; 0 wrong | 5/9; 4 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0 |
  | 4.D | 1/10; 7 NR; 2 wrong | 1/10; 7 NR; 2 wrong | 1/10; 7 NR; 2 wrong | 3/9; 6 NR; 0 wrong | 3/9; 6 NR; 0 wrong | 5 |
  | 4.E | 9/10; 1 NR; 0 wrong | 2/10; 8 NR; 0 wrong | 2/10; 8 NR; 0 wrong | 6/9; 3 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0 |
  | 4.F | 2/10; 6 NR; 2 wrong | 2/10; 6 NR; 2 wrong | 1/10; 7 NR; 2 wrong | 4/9; 5 NR; 0 wrong | 5/9; 4 NR; 0 wrong | 18 |
  | 5.A | 6/10; 3 NR; 1 wrong | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 5 |
  | 5.B | 6/10; 1 NR; 3 wrong | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0/9; 8 NR; 1 wrong | 13 |
  | 5.C | 10/10; 0 NR; 0 wrong | 5/10; 5 NR; 0 wrong | 5/10; 5 NR; 0 wrong | 1/9; 7 NR; 1 wrong | 1/9; 7 NR; 1 wrong | 7 |
  | 5.D | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 1/9; 7 NR; 1 wrong | 1/9; 7 NR; 1 wrong | 4 |
  | 5.F | 3/10; 6 NR; 1 wrong | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 1 |
  | 5.G | 3/10; 6 NR; 1 wrong | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 1 |
  | 5.H | 9/10; 1 NR; 0 wrong | 4/10; 6 NR; 0 wrong | 4/10; 6 NR; 0 wrong | 6/9; 3 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 12 |
  | 9.A | 10/10; 0 NR; 0 wrong | 10/10; 0 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 8/9; 1 NR; 0 wrong | 8/9; 1 NR; 0 wrong | 1 |
  | 9.B | 9/10; 1 NR; 0 wrong | 9/10; 1 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 0 |
  | 9.C | 4/10; 6 NR; 0 wrong | 7/10; 3 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 1/9; 0 NR; 8 wrong | 9 |
  | 19.A | 2/10; 8 NR; 0 wrong | 5/10; 4 NR; 1 wrong | 4/10; 0 NR; 6 wrong | 4/9; 5 NR; 0 wrong | 1/9; 8 NR; 0 wrong | 0 |

- **Every wrong cell, round 2 (12: 11 false FAIL, 1 other).**
  - **New since 9a (6 false FAILs, all judge answers; the key passes each):** 5.B on search, 5340 and 5144; 5.F and 5.G on 5340; 5.A on 4914. In 9a each was NEEDS REVIEW. 5340, 5144 and 4914 embed frames (the readers added in step 8 now read them; 9a ran before them). The reports show: on 5340 the judge answered "not identified" on all 25 of 5.F's questions about an "error message" that reads only "4", gave 5.G "no guidance" 10 times and "unsure" 15, and flagged labels such as "intermediate", "very low" and "in 2024" under 5.B; on 4914 5.A names an unnamed drop-down in the frame "SVS Globe Video Viewer". **My reading, not checked against the frames, is that these readers treat the frames' own controls (a data display) as forms.** If so these are the first false FAILs the step 8 frame reading produces. 5.B on search is not a frame (the "Sort by:" drop-down) and may be the judge varying.
  - **Same as 9a (6):** 4.A on the home page, 4.F on search and 5340, 4.D on 14592 (judge answers), 4.D on 5340 (a rule), and 3.A on 14194, Not Tested where the key says Does Not Apply.
  - **Gone since 9a:** 19.A on CILab (now NEEDS REVIEW: the container).
- **Every wrong cell, round 1 (2, both also wrong in 9a):** 5.D on spot-the-station (judge) and 5.C on `?search=artemis` (a rule). 9a's other 10 are gone (9.C on 8 pages, 5.B on missions, 4.A on artemis-iii). I did not trace why; main changed a lot between `8854a4f` and `ece881b` and one repeat cannot tell a code change from the judge's variation.
- **Moved from NEEDS REVIEW to an outcome, with Abby's key.** Round 2 since 9a: **51 cells, 45 agree** (4.C 7, 4.E 7, 5.H 5, 5.C 5, 2.C 4, 2.D 4, 2.B 3, 3.A 3, 5.A 3, 5.B 3, 9.C 1) **and 6 do not** (the six new false FAILs above); 18 of the 51 are judge-decided. Round 2 since step 6: **75 cells, 68 agree** (the list above with 9.C at 4, plus 9.A 10, 9.B 9 and 4.F 1) and 7 do not (the six and 4.F on search). Round 1 since 9a: **20 cells, all agree** (4.E 6, 5.H 6, 4.C 5, 19.A 3).
- **Cells that moved the wrong way against 9a** (a cell that was right and no longer is, or NEEDS REVIEW that became a wrong outcome). Round 2: **13.** NEEDS REVIEW to false FAIL: the six above. Agree to NEEDS REVIEW: 19.A on the home, help and 4914 pages (the container; no search could run), and 9.C on 14194, 5340, 5144 (the judge answered "unsure" on 4, 2 and 2 pairs) and on 4914 (a rule row, A3o: nothing on the page matches the other pages). One more moved the safe way: 19.A on CILab, false FAIL to NEEDS REVIEW. Round 1: **1,** 4.F on artemis-iii (agree to NEEDS REVIEW); two false FAILs also went to NEEDS REVIEW (5.B on missions, 4.A on artemis-iii), the safe direction.
- **Guard CN.** Round 1's pages: 27 CN cells (9a 30), all scored: key Does Not Apply 18, Pass 9 (5.B 8, 5.F 6, 5.G 6, 5.C 4, 5.H 3); **key Fail among them: 0, so the guard held back no failure on round 1's pages.** The other 50 NEEDS REVIEW cells there are not CN. Round 2: 4 CN cells (9a 14), key Pass 2 and Does Not Apply 2, none a key Fail.
- **Dry run against real run, on cells no judge answer decided.** Round 2: 156 cells, 145 the same, **11 differ**, none in outcome (8 are the 2.C and 2.D timer reading, about 148 to 150 s; 2 are 4.D focus rows read M4 or M11 in one run and M6 in the other; 1 is 9.C on 4914, whose rule row differs, A4 G3 against A3o G1, the outcome NEEDS REVIEW both times). 64 judge-decided cells are not compared. Round 1: 167 cells, 144 the same, **23 differ**; 31 not compared. **Outcome differs on 5:** 19.A on 4 pages (the dry run's search could not run: the stale proxy) and 4.C on spot-the-station, PASS in the dry run and NEEDS REVIEW in the real run (row RC, the reveal guard; the same cell differed in 9a, so it varies from run to run). The other 18 differences: 19.A's rows on the other 5 pages, 3.A on naca-at-110 (the dry run ran out of its 240 s, the real run took 10.3 s), 4.D instance rows on 4 pages, and 8 text-only (timers and menu-name lists).
- **Per question type, both rounds together** (this run's cells for both; one repeat per round, so "at most 1 wrong FAIL per repeat" is read per round):

  | Type | Cells | Decided | Agree | Wrong PASS | Wrong DNA | Wrong FAIL | PASS vs key DNA | Unsure | Real-page half |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | 2.B | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 3 | too few cells to judge: 1 decided, 6 needed |
  | 4.A | 9 | 3 | 2 | 0 | 0 | 1 | 0 | 6 | too few cells to judge: 3 decided, 6 needed; wrong FAILs over 20% of the type's decided cells |
  | 4.B | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 | meets |
  | 4.D | 5 | 1 | 0 | 0 | 0 | 1 | 0 | 4 | too few cells to judge: 1 decided, 6 needed; wrong FAILs over 20% of the type's decided cells |
  | 4.F | 18 | 7 | 5 | 0 | 0 | 2 | 0 | 11 | more than 1 wrong FAIL in a repeat; wrong FAILs over 20% of the type's decided cells |
  | 5.A | 5 | 3 | 2 | 0 | 0 | 1 | 0 | 2 | too few cells to judge: 3 decided, 6 needed; wrong FAILs over 20% of the type's decided cells |
  | 5.B | 13 | 8 | 5 | 0 | 0 | 3 | 0 | 5 | more than 1 wrong FAIL in a repeat; wrong FAILs over 20% of the type's decided cells |
  | 5.C | 7 | 5 | 5 | 0 | 0 | 0 | 0 | 2 | too few cells to judge: 5 decided, 6 needed |
  | 5.D | 4 | 3 | 2 | 0 | 0 | 1 | 0 | 1 | too few cells to judge: 3 decided, 6 needed; wrong FAILs over 20% of the type's decided cells |
  | 5.F | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | too few cells to judge: 1 decided, 6 needed; wrong FAILs over 20% of the type's decided cells |
  | 5.G | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | too few cells to judge: 1 decided, 6 needed; wrong FAILs over 20% of the type's decided cells |
  | 5.H | 12 | 10 | 10 | 0 | 0 | 0 | 0 | 2 | meets |
  | 9.A | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | too few cells to judge: 1 decided, 6 needed |
  | 9.C | 9 | 5 | 5 | 0 | 0 | 0 | 0 | 4 | too few cells to judge: 5 decided, 6 needed |

  2.A, 2.C, 2.D, 3.A, 4.E and 9.B asked nothing the judge answered. No type has a wrong PASS or a wrong DOES NOT APPLY. `JUDGE_TYPES` is unchanged (empty); Abby chooses from this table. **4.B and 5.H meet the real-page half** (6 of 6 and 10 of 10 decided, all agree). **9.C and 5.C have no wrong cell and are one decided cell short** (5 of 6 each). 5.B has 3 wrong FAILs in round 2 (over 1; 38% of its 8 decided), 5.A, 5.F and 5.G each 1 of 3 or fewer decided. 4.A, 4.D, 4.F and 5.D are over the limits as in 9a.
- **The gate's test-page half, for 4.B, 5.C, 5.H and 9.C** (no wrong cell and at least 3 decided cells over 9a's and this run's pages; the same code and prompt cover both rounds). `judge_eval.py answer --backend api --repeat 3` on their 35 cases (dry: 35 requests, 44 questions, ~24.8k text tokens, 21 pictures a repeat): **3 repeats, 0 failed calls, 0 wrong PASS, trick text never taken, 32/35 match each time** (4.B 4 of 5, 5.C 12 of 13, 5.H 12 of 13, 9.C 4 of 4). The same three cases miss in all three repeats, all to NEEDS REVIEW: 4.B f02 (hold with an alternative) and 5.C f32 (filter boxes with no heading) expect PASS, 5.H f08 (a wizard's next step says "required") expects FAIL. **4.B and 5.H meet both halves of the gate; 5.C and 9.C meet the test pages and are short only on real-page cells.** 4.B's spec changed after 9a (1.3.0 to 1.4.0) and the 9a test-page run is not reused. Results: `gate-2026-11-16/testpages/`.
- **Time budgets** (`test_times`; limit = budget unless less of the run was left). **One test ran out: 5.D on round 1's missions page (596.5 s of 600)**, as in 9a (594.1 s); in its dry run it also ran out (592.5 s) and so did 3.A on naca-at-110 (240.1 s of 240). On round 2 nothing ran out in either run; 5.D's longest was 471.5 s of 600 on the search page. 9.B's budget is now 180 s and 19.A's 360 s (9a: 60 and 120). The longest each test took, over both rounds, beside 9a's longest:

  | Test | Budget (s) | Longest in 9b, both rounds (s) | Where | Longest in 9a (s) | Ran out in 9b |
  | --- | --- | --- | --- | --- | --- |
  | 2.A | 120 | 2.9 | round 2 p05 | 0.9 | - |
  | 2.B | 120 | 67.1 | round 2 p09 | 91.3 | - |
  | 2.C | 120 | 14.9 | round 2 p07 | 27.4 | - |
  | 2.D | 120 | 0 | - | - | - |
  | 3.A | 240 | 57.9 | round 2 p10 | 75.3 | - |
  | 4.A | 240 | 110.8 | round 2 p09 | 160.4 | - |
  | 4.B | 60 | 9.9 | round 2 p07 | 11.8 | - |
  | 4.C | 180 | 111.3 | round 2 p08 | 76.4 | - |
  | 4.D | 60 | 12.8 | round 1 p06 | 15.5 | - |
  | 4.E | 60 | 0 | - | - | - |
  | 4.F | 540 | 258.0 | round 2 p10 | 324.6 | - |
  | 5.A | 60 | 15.7 | round 2 p09 | 15.2 | - |
  | 5.B | 60 | 0 | - | - | - |
  | 5.C | 60 | 0 | - | - | - |
  | 5.D | 600 | 596.5 | round 1 p05 | 594.1 | round 1 p05 |
  | 5.F | 120 | 34.1 | round 2 p07 | 40.4 | - |
  | 5.G | 120 | 0.1 | round 2 p09 | - | - |
  | 5.H | 120 | 4.1 | round 1 p07 | - | - |
  | 9.A | 180 | 47.0 | round 1 p07 | 50.2 | - |
  | 9.B | 180 | 0 | - | 41.5 | - |
  | 9.C | 180 | 44.2 | round 2 p01 | 42.6 | - |
  | 19.A | 360 | 84.8 | round 1 p07 | 21.5 | - |

  A test at 0.0 s read a result another test had already computed. 19.A's round 2 time (2.5 s) is not a measurement: the search could not run.
- **Not verified here:** 19.A on round 2 (the container cannot run its live search, so no round 2 19.A figure is comparable with 9a); whether the six new false FAILs come from the frames' own controls being read as forms (my reading is from the reports only; the frames were not opened); whether the 9.C "unsure" answers and 5.B on search are the judge varying between runs or a change since 9a (one repeat); why 9.C, 5.B and 4.A on round 1 no longer give a wrong FAIL; whether svs.gsfc.nasa.gov's certificate or the container's proxy causes the 502 (the proxy returns it; I could not see inside it); the direct-connection route; round 1's recordings against a hash.

## Gate 2026-11-14: both rounds' pages, the server judge on every type, one repeat (roadmap step 9a)

Round 2's 10 frozen svs.gsfc.nasa.gov pages and round 1's 9 frozen www.nasa.gov
pages, each tested once with the server judge switched on for all 21 types
it can take (4.C stays with the client), CLI route, `claude-sonnet-5-5`,
prompt SHA-256 `e8320f2c…`. Abby's changes to the plan: one repeat, as a
checkpoint, with the dry run's outcomes compared in place of a second
repeat; no merge of `main` first, so `src/` is `8854a4f` exactly (PRs 58 to
60, step 8's first reader and the radio-group count, are **not** in this
run) and 9a is the measurement before step 8. `apijudge_gate.py` got a
`--round 1|2` option (`7bf5c5d`) and `--pages` reruns that add to the page
list (`2cdcbc4`); neither changes what a run does. Folder
`evals/judging/gate-2026-11-14/`: `roundN/dry-r1.json` (the count),
`roundN/dry/pNN/` (each dry run's report and pre-SCRT) and `roundN/r1/results/pNN/`
(the real run's) **kept out of git** (`.gitignore`; Abby holds a copy), `roundN/gate.json` (`apijudge_gate.py score --round N`),
`compare-roundN.md` and `.json`, `combined.md` (`compare.py`), `testpages/`
(the judge eval's results). Scored with the rounds' own scorer
(`evals.scoring.score` on `compare`, each round's keys and adjudication);
step 6's side is read from its own `compare.json` and reproduces its
figures. Agent-assisted results, not certified Trusted Tester results; two
development sites, one repeat.

- **Checked first.** Round 2's frozen archive: all 12 parts, the joined zip
  and every file match Abby's manifest. Round 1's nine recordings: each zip
  opens and every index entry exists, but **no hash was given, so they are
  not checked against one**. The browser trusts the egress proxy
  (`UPSTREAM_PROXY` in `.env`): 19.A on round 2's 14194 found the page by
  the live search with no failed script.
- **Cost.** Dry count: round 2 47 requests, 186 questions, ~200k text
  tokens, 177 pictures; round 1 34 requests, 75 questions, ~103k, 131
  pictures. Run (counted by the judge's own record): round 2 52 calls, 227
  questions (follow-up questions add to the dry count), round 1 34 calls, 74
  questions; **0 failed, 0 left open, all 301 answered**. Tokens in the
  calls: round 2 ~0.66M input (step 6: ~0.62M), 35k output; round 1 ~0.34M
  input, 16k output; 565 s in calls. Browser time: round 2 82 min, round 1
  46 min (dry: 85 and 48). The container restarted at least four times
  (idle turns and a usage limit): detached tasks died, and a tracked
  background task died once (round 1's dry run, at page 6). Both real runs
  and the rerun of the test-page half finished without a restart.
- **All scored cells.** No false PASS and no missed fail (wrong DOES NOT
  APPLY) in either round, in judge-decided or rule-decided cells.

  | Run | Scored | False PASS | Missed fail | False FAIL | Other | Needs review (CN) | Agree (of decided) |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | Round 2, this run | 220 | **0** | **0** | **6** | 1 | 129 (14) | 84/91 |
  | Round 2, dry run (judge off) | 220 | 0 | 0 | 3 | 1 | 152 (10) | 64/68 |
  | Round 2, step 6 | 220 | 0 | 0 | 11 | 1 | 152 (14) | 56/68 |
  | Round 2, arm C repeats 1-3 | 220 | 3 | 2 | 24-26 | 9 | 86-88 | 94/132-134 |
  | Round 1, this run | 153 | **0** | **0** | **12** | 0 | 94 (30) | 47/59 |
  | Round 1, dry run (judge off) | 153 | 0 | 0 | 1 | 0 | 113 (23) | 39/40 |
  | Round 1, arm A repeats 1-3 (locked, other code) | 136-153 | 0 | 0 | 1-3 | 0 | 84-99 | 49-51/52-54 |

  Judge-decided cells: round 2 56 (step 6: 54): 0 false PASS, 0 missed
  fail, 4 false FAILs (step 6: 4), 30 NEEDS REVIEW (5 CN), 22/26 agree
  (step 6: 14/18; arm C: 16/27-29). Round 1: 36 cells, 11 false FAILs
  (8 of them 9.C), 15 NEEDS REVIEW (7 CN), 10/21 agree. Rule-decided cells:
  round 2 164: 2 false FAILs (step 6: 7), 1 other, 99 NEEDS REVIEW (9 CN),
  62/65 agree; round 1 117: 1 false FAIL, 79 NEEDS REVIEW (23 CN), 37/38
  agree. Round 1 has no earlier run on this code to set beside it: the
  arms are round 1's locked runs on its old rules.
- **Per TT test** (a test with no key on a round's pages is not scored; no
  test had a false PASS or a missed fail):

  | Test | Round 2, this run (agree/scored; NR; wrong) | Round 2, step 6 | Round 1, this run | Judge cells (R2 + R1, unsure included) |
  | --- | --- | --- | --- | --- |
  | 2.A | 7/10; 3 NR; 0 wrong | 7/10; 3 NR; 0 wrong | - | 0 |
  | 2.B | 1/10; 9 NR; 0 wrong | 1/10; 9 NR; 0 wrong | - | 3 |
  | 2.C | 0/10; 10 NR; 0 wrong | 0/10; 10 NR; 0 wrong | - | 0 |
  | 2.D | 0/10; 10 NR; 0 wrong | 0/10; 10 NR; 0 wrong | - | 0 |
  | 3.A | 3/10; 6 NR; 1 wrong | 3/10; 6 NR; 1 wrong | - | 0 |
  | 4.A | 2/10; 7 NR; 1 wrong | 2/10; 7 NR; 1 wrong | 0/9; 8 NR; 1 wrong | 10 |
  | 4.B | 9/10; 1 NR; 0 wrong | 9/10; 1 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 6 |
  | 4.C | 2/10; 8 NR; 0 wrong | 2/10; 8 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0 |
  | 4.D | 1/10; 7 NR; 2 wrong | 1/10; 7 NR; 2 wrong | 3/9; 6 NR; 0 wrong | 5 |
  | 4.E | 2/10; 8 NR; 0 wrong | 2/10; 8 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0 |
  | 4.F | 2/10; 6 NR; 2 wrong | 1/10; 7 NR; 2 wrong | 5/9; 4 NR; 0 wrong | 18 |
  | 5.A | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 1 |
  | 5.B | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 0/9; 8 NR; 1 wrong | 12 |
  | 5.C | 5/10; 5 NR; 0 wrong | 5/10; 5 NR; 0 wrong | 1/9; 7 NR; 1 wrong | 4 |
  | 5.D | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 1/9; 7 NR; 1 wrong | 4 |
  | 5.F | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0 |
  | 5.G | 3/10; 7 NR; 0 wrong | 3/10; 7 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 0 |
  | 5.H | 4/10; 6 NR; 0 wrong | 4/10; 6 NR; 0 wrong | 0/9; 9 NR; 0 wrong | 11 |
  | 9.A | 10/10; 0 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 8/9; 1 NR; 0 wrong | 1 |
  | 9.B | 9/10; 1 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 9/9; 0 NR; 0 wrong | 0 |
  | 9.C | 7/10; 3 NR; 0 wrong | 0/10; 10 NR; 0 wrong | 1/9; 0 NR; 8 wrong | 17 |
  | 19.A | 5/10; 4 NR; 1 wrong | 4/10; 0 NR; 6 wrong | 1/9; 8 NR; 0 wrong | 0 |

- **Every wrong cell, round 2 (7: 6 false FAIL, 1 other).** 4.A on the
  home page, 4.F on search and 5340, 4.D on 14592 (judge answers); 4.D on
  5340 and 19.A on CILab (rules); 3.A on 14194 is Not Tested where the key
  says Does Not Apply (as in step 6). 19.A on CILab (A5 W1 W3 G4: the search
  ran, its results did not lead to the page) is the one 19.A false FAIL left
  now that the browser trusts the proxy (step 6: 6); **why was not
  investigated here**.
- **Every wrong cell, round 1 (12 false FAILs, 11 by a judge answer).**
  **9.C on 8 of 9 pages** (spot-the-station, search, forms, careers,
  missions, NACA, max-power, ksc-history): one cause, the judge answered
  "inconsistent" for the same pair of names, "Home" here and "NASA — return
  to the homepage" on the other pages, and Abby's key passes all 8. 5.D on
  spot-the-station, 5.B on missions and 4.A on artemis-iii (judge answers);
  5.C on `?search=artemis` (rules).
- **Moved from NEEDS REVIEW since step 6 (round 2: 28 cells).** 27 agree
  with the key: 9.A on 10 pages, 9.B on 9, 9.C on 7 (the read-cap and
  consistency fixes; 9 of the 28 are judge-decided: 9.C on 6 pages, 4.F on 2, 9.A on 1), 4.F
  on the galleries. One does not: 4.F on search, the tool says FAIL where
  the key passes (a judge answer). 19.A's false FAILs went from 6 to 1 (the
  container's certificate fault is gone; CILab above is the one left). Round 1: not comparable (no step 6).
- **Guard CN.** Round 1's pages: 44 CN cells, 30 scored (key Does Not
  Apply 24, Pass 6; by test 5.H 9, 5.F 7, 5.G 7, 5.B 5, 5.C 2) and 14
  unkeyed 2.B and 3.A cells; **key Fail among them: 0, so the guard held
  back no failure on round 1's pages.** The other 64 NEEDS REVIEW cells
  there are not CN. Round 2: 14 CN cells, none a key Fail either (as step
  6). Over both rounds the guard left 44 cells, where the key says Pass or
  Does Not Apply, with a person, and none where the key fails.
- **Dry run against real run, on cells no judge answer decided** (the dry
  run's reports were not kept by the script; the run folders were still on
  disk and were copied to `roundN/dry/`, out of git). Round 2: 164 cells, 144 same,
  **20 differ**; round 1: 161 cells, 142 same, **19 differ**. **None
  differs in outcome.** The rest of the differences:
  - **Text only, a number inside the summary: 28.** 2.C and 2.D on both
    rounds (the timer reading, 147-152 s, differs each load), 2.B and 3.A
    on round 2's home page ("34" then "35").
  - **Rows, the path a test took: 4.** Round 2 3.A on 5340 (dry: guard
    CN, 14 images, 6 checked, 3.8 s; real: the stepped capture, 27.3 s,
    row A3, same NEEDS REVIEW). Round 1 4.C on spot-the-station (dry:
    A3 G4 RC; real: A3 G3, one instance row more), and 19.A on NACA and
    max-power (W2 and W3 swapped in opposite directions: the live site
    search, the one live request, is not repeatable).
  - **4.D instance rows: 5** (one or three focus rows read M4 in one run
    and M6 in the other), on round 2's help and search pages and round 1's
    spot-the-station, careers and artemis-iii; the outcome did not change.
  - **Time or ran-out only: 2** (3.A on round 1's spot-the-station, 23.3 s
    dry and 8.0 s real; 9.B on round 2's home page ran out of its budget in
    the dry run, 51.6 s of 60, and not in the real run).
- **Per question type, both rounds together, read against "The gate"** (one
  repeat per round, so "at most 1 wrong FAIL per repeat" is read per
  round):

  | Type | Judge cells | Decided | Agree | Wrong PASS | Wrong DNA | Wrong FAIL | Unsure | Against the thresholds |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | 4.B | 6 | 6 | 6 | 0 | 0 | 0 | 0 | **meets the real-page half**; test pages below |
  | 5.C | 4 | 3 | 3 | 0 | 0 | 0 | 1 | no wrong; too few decided (3 of 6) |
  | 5.H | 11 | 2 | 2 | 0 | 0 | 0 | 9 | no wrong; too few (2) |
  | 5.A | 1 | 1 | 1 | 0 | 0 | 0 | 0 | no wrong; too few (1) |
  | 9.A | 1 | 1 | 1 | 0 | 0 | 0 | 0 | no wrong; too few (1) |
  | 2.B | 4 | 1 | 0 | 0 | 0 | 0 | 3 | no wrong; too few (1) |
  | 4.A | 10 | 4 | 2 | 0 | 0 | 2 | 6 | wrong FAILs 50% of decided (over 20%); too few (4) |
  | 4.D | 5 | 1 | 0 | 0 | 0 | 1 | 4 | wrong FAIL 100%; too few (1) |
  | 4.F | 18 | 8 | 6 | 0 | 0 | 2 | 10 | 2 wrong FAILs in round 2 (over 1); 25% |
  | 5.B | 12 | 3 | 2 | 0 | 0 | 1 | 9 | wrong FAIL 33%; too few (3) |
  | 5.D | 4 | 3 | 2 | 0 | 0 | 1 | 1 | wrong FAIL 33%; too few (3) |
  | 9.C | 17 | 15 | 7 | 0 | 0 | 8 | 2 | 8 wrong FAILs in round 1 (over 1); 53% (one cause above) |

  2.A, 2.C, 2.D, 3.A, 4.E, 5.F, 5.G and 9.B asked nothing the judge answered
  here: no cells. No type has a wrong PASS or a wrong DOES NOT APPLY.
  `JUDGE_TYPES` is unchanged (empty); Abby chooses from this table.
- **The gate's test-page half, for the two types that are near (4.B, 5.C:
  no wrong cell and at least 3 decided).** `judge_eval.py answer --backend
  api --repeat 3` on their 17 cases (dry: 17 requests, 23 questions, ~13.6k
  text tokens, 20 pictures a repeat): **3 repeats, 0 wrong PASS, trick text
  never taken, 0 failed calls, 15/17 match each time.** The two that do not
  (4.B f02, hold with an alternative, and 5.C f32, filter boxes with no
  heading) expect PASS and give NEEDS REVIEW in all three repeats: the safe
  direction. A first run of the same command was **discarded**: 14 of 17
  cases had a failed call (your usage limit hit during it); the rerun is
  the result. With it, 4.B meets both halves of the gate; 5.C meets the
  test pages and is short only on real-page cells (3 of 6). Results:
  `gate-2026-11-14/testpages/`.
- **Time budgets** (real runs; `test_times`; limit = budget unless less of
  the run was left). **One test ran out: 5.D on round 1's missions page
  (594.1 s of 600).** In the dry runs 5.D also ran out on round 2's search
  page (597.2 s) and round 1's missions page (599.4 s), and 9.B on round 2's
  home page (51.6 s of 60). 14194 took 11.4 min and did not reach the run
  cap (step 6: 1800 s). Longest each test took, over both rounds
  (budget): 2.A 0.9 s (120), 2.B 91.3 (120), 2.C 27.4 (120), 2.D 0.0 (120),
  3.A 75.3 (240), 4.A 160.4 (240), 4.B 11.8 (60), 4.C 76.4 (180), 4.D 15.5
  (60), 4.E 0.0 (60), 4.F 324.6 (540), 5.A 15.2 (60), 5.B, 5.C, 5.G, 5.H
  0.0 (60, 60, 120, 120), 5.D 594.1 (600), 5.F 40.4 (120), 9.A 50.2 (180),
  9.B 41.5 (60), 9.C 42.6 (180), 19.A 21.5 (120). A test at 0.0 s read a
  result another test had already computed.
- **Not verified here:** more than one repeat (so no repeat-to-repeat
  difference for the judge, and no per-repeat wrong-FAIL count beyond one
  per round); the 9.C false FAILs' cause beyond the names pair; why 19.A
  fails on CILab; round 1's recordings against a hash; the test-page half
  for types other than 4.B and 5.C; how the server and the client
  backends compare on the same page set.

## Gate 2026-11-13: round 2's 10 pages again, the server judge on every type (roadmap step 6)

Round 2's 10 frozen svs.gsfc.nasa.gov pages (Abby's `round2-frozen`
archive, every file checked against its manifest), tested once with
`main` at `c0236572` (steps 1 to 5 merged: PRs 39, 41, 42, 43, 44), the
server judge switched on for all 21 types it can take (4.C stays with the
client), CLI route, `claude-sonnet-5-5`, prompt SHA-256 `e8320f2c…`.
Folder `evals/judging/gate-2026-11-13/`: `dry-r1.json` (the count),
`r1/results/pNN/` (report and pre-SCRT per page), `gate.json`
(`apijudge_gate.py score`), `compare.md` and `compare.json`
(`compare.py`: beside round 2's three arm C repeats, per TT test, cells a
judge answer decided apart from the rest, guard CN's NEEDS REVIEW apart).
Scored with round 2's scorer (`evals.scoring.score` on `compare`,
unchanged since round 2's lock `e14580a`, with its adjudication); on
round 2's side it reproduces the locked rows exactly. Agent-assisted
results, not certified Trusted Tester results; a development site, one
repeat.

- **Cost.** Dry count: 46 requests, 187 questions, ~200k text tokens,
  173 pictures. Run: 48 calls, 0 failed, 224 questions answered, 34
  "unsure", none left open; ~0.62M input tokens (Agent C: 1.71M), 34k
  output, 328 s in calls. Browser time 78 min (dry) and about the same
  run; 14194 hit the run cap (below).
- **All 220 scored cells (per TT test):**

  | Run | False PASS | Missed fail (DNA) | False FAIL | Other | Needs review (guard CN) | Agree (of decided) |
  | --- | --- | --- | --- | --- | --- | --- |
  | Gate 2026-11-13 | **0** | **0** | **11** | 1 | 152 (14) | 56/68 |
  | Round 2 C repeats 1-3 | 3 | 2 | 24-26 | 9 | 86-88 | 94/132-134 |

  Judge-decided cells: 54 (round 2: 42): 0 false PASS, 0 missed fail, 4
  false FAILs (round 2: 11-13), 36 NEEDS REVIEW (5 CN), 14/18 agree
  (round 2: 16/27-29). Rule-decided cells: 166 (round 2: 178): 0 false
  PASS, 0 missed fail (round 2: 3 and 2), 7 false FAILs (round 2: 13), 116
  NEEDS REVIEW (9 CN), 42/50 agree (round 2: 78/105).
- **Round 2's 5 wrong PASS and DOES NOT APPLY cells are gone:** 4.A on
  CILab now fails with the key (a judge answer); 4.C and 5.D on 5340,
  and 9.A on CILab and 14592, are NEEDS REVIEW (the reveal guard, guard
  GU, the 600-item read cap). No new one.
- **The 11 false FAILs:** 6 are 19.A (CILab, 14592, 14194, 5340, 5144,
  4914; rule rows W3 G4) and come from **this container, not the rules**:
  the live site search's results page loads its results with scripts
  from cdn.jsdelivr.net and the site's `/static/`, and the browser here
  refused every one (`net::ERR_CERT_AUTHORITY_INVALID`: it does not trust
  the egress proxy's certificate), so no search ever showed results and
  W3 ("the search does not lead to the page") applied. Round 2's
  follow-up runs found 14194, 5340, 5144 and 4914 through the same search.
  It also shows a weakness: a results page whose own scripts failed is
  read as a finished search; W4 ("search not verified", NEEDS REVIEW) is
  the row for it. The other 5: 4.A home page (judge: 17 "no alternative"
  answers), 4.F home page and 5340 (judge: "does not preserve"), 4.D 14592
  (judge) and 5340 (rule; both as in round 2).
- **The run cap.** 14194 reached `MAX_RUN_S` (1800 s): 3.A's stepped
  capture took about 17 min (55 s in the dry run), so 5.A-5.H were not
  performed there (NEEDS REVIEW, "the run reached its time limit"; 7
  cells, keys Pass or Does Not Apply).
- **NEEDS REVIEW (152; round 2: 86-88), in three groups** (lists per
  cell: `compare.md`):
  - **Inside a frame or a web component: 19** (step 8's target), all
    frames, none web components: 5.A-5.H on 5340, 5144 and 4914 (forms
    in embedded frames) and 4.A on 5144 (a frame it could not read). The
    key fails 4 of them (5.C on 5340, 5144, 4914; 4.A on 5144): failures
    the frames hide today. 2 (5.H on 5144 and 4914) are also guard CN.
  - **Guard CN, the rest: 12,** all where the key says Pass (2) or Does
    Not Apply (10): 2.B and 3.A on more than 30 images (home, search,
    galleries, 4914: 6), 5.A, 5.B, 5.F, 5.G on the home page's forms
    hidden until opened (4), 5.H on a form that is only a button (home,
    search). Over all 14 CN cells the keys show no failure the guard held
    back: on these pages it cost agreements and found nothing.
  - **Every other reason: 121.** 2.C and 2.D on all 10 pages (20: moving
    content not settled in 6.5 s; as round 2); the reveal guard on 4.C,
    4.E and 5.D (20: "menus or sections that open"); 9.A and 9.C (20: the
    600-item read cap); 9.B (10: an other page not read whole); 4.D and
    4.F (14: the judge's "unsure"); the run cap on 14194 (7); 4.A (6:
    embedded players, a 40-element cap, controls asked about); audio,
    video or flashing not playable or checkable from the recording (9:
    2.A, 2.B, 3.A); 2.B moving regions the judge left unsure (3); fields
    the walk could not reach (2: 5.F, 5.G on 14592); and 10 others (98
    fields on search, a form sent to its server, 5.D focus events, guard
    GU 2, one open 4.C question, 4.B on 5340).
- **Per question type, read against "The gate" (one repeat; not a gate
  result, and the test-page half was not run here):**

  | Type | Judge cells | Decided | Agree | Wrong PASS | Wrong DNA | Wrong FAIL | Unsure | Against the thresholds |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | 4.B | 5 | 5 | 5 | 0 | 0 | 0 | 0 | meets all but the cell count (5 of 6) |
  | 5.B | 8 | 2 | 2 | 0 | 0 | 0 | 6 | no wrong; too few decided (2) |
  | 5.C | 2 | 2 | 2 | 0 | 0 | 0 | 0 | no wrong; too few (2) |
  | 5.H | 6 | 2 | 2 | 0 | 0 | 0 | 4 | no wrong; too few (2) |
  | 5.D | 1 | 1 | 1 | 0 | 0 | 0 | 0 | no wrong; too few (1) |
  | 4.A | 7 | 3 | 2 | 0 | 0 | 1 | 4 | wrong FAILs 33% of decided (over 20%); too few (3) |
  | 4.D | 6 | 1 | 0 | 0 | 0 | 1 | 5 | wrong FAIL 100%; too few (1) |
  | 4.F | 9 | 2 | 0 | 0 | 0 | 2 | 7 | 2 wrong FAILs in a repeat (over 1); 100% |
  | 2.B | 3 | 0 | 0 | 0 | 0 | 0 | 3 | nothing decided |
  | 9.C | 7 | 0 | 0 | 0 | 0 | 0 | 7 | nothing decided (the read cap holds the cell) |

  2.A, 2.C, 2.D, 3.A, 4.E, 5.A, 5.F, 5.G, 9.A, 9.B and 19.A asked nothing
  the judge answered on these pages: no cells. No type has a wrong PASS or
  a wrong DOES NOT APPLY. `JUDGE_TYPES` is unchanged (empty).
- **Not verified here:** the test-page half of the gate
  (`judge_eval.py answer --backend api --repeat 3`); repeats; 19.A's live
  search in a browser that trusts the proxy; 14194 within the run cap.

## 2026-11-22: 4.A 1.20.0 (a radio group whose change makes the page leave), no agent run needed

The radio probe asks no question: it takes radio buttons out of J1 when an arrow press lands on them, as 1.19.0 did. No question, rubric or question input changes; F43 (new) asks nothing. On round 2's search page (`judging/gate-2026-11-22-136e/`) the five date radio buttons are no longer asked: 4.A's own rows pass the page (G4), held at NEEDS REVIEW only by guard RC (content that opens, step 15).

## Run 44, 2026-11-23: 4.F 1.16.0 (#135 step 15: opened content from the shared walk), every 4.F packet

J1's `opened` input now comes from the shared walk through every trigger `reveal.py` opens (pass R opened the first six) and, when the next Tab does not go into what opened, says after how many Tabs focus first reaches it (`reached_after_tabs`) and what it passes on the way. 21 cases ask (F36, round 3's SDE "All" pattern, among them).
- **Server judge (`answer --backend api --repeat 3`, CLI route, `claude-sonnet-5-5`): 21, 21, 21 of 21, no wrong PASS, no bait taken.** Results in `judging/gate-2026-11-23-135e/judge-eval-4f/`.
- **Fresh agent: not run** (time; the server judge is the path the gates use).

## Run 43, 2026-11-23: 4.D 1.13.0 (#135 step 15: opened content; image B marked), every 4.D packet

J1's image B now carries the element's box in magenta on a copy, as the spec always said (the code had sent the unmarked picture while the question named "the outlined element"), and the question says the box is the tool's mark, not the page's. 4.D now also asks J1 for stops inside opened content with no before picture: new F34 (a menu that closes when focus leaves; correct answer yes) and F35 (its last item has the next link's ring in its off picture; correct answer no). `prepare 4.D` (11 cases ask), no leak in the packets (the grep finds nothing). Results: `judging/gate-2026-11-23-135c/judge-eval-4d/`.
- **Server judge (`answer --backend api --repeat 3`, CLI route, `claude-sonnet-5-5`): 10, 10, 10 of 11, no wrong PASS, no bait taken.** Run 42's two misses now match on every repeat: ACT `dd9628d8` (DHS PASS) yes, F16 unsure. F30 and F35 no, F06, F14 and F27 no, F20 and F34's first two items yes. The miss: F34's last menu item unsure on every repeat ("A is blank white, so the before/after comparison is unreliable"): the menu closes when focus leaves, so its off picture has no menu (NEEDS REVIEW, safe).
- **Fresh agent (one Sonnet agent, the 11 packets only, told to open nothing outside them; it listed what it opened, all inside): 11 of 11.** F34's last item yes ("Picture A is blank because the menu closed ... The outline in B is still plainly on Moon").

## Run 42, 2026-11-22: 4.D 1.11.0 (#135 step 27: a before picture, image D, and the next element's mark), every 4.D packet

J1 now also gets image D, the region just before focus reached the element (focus on the element before it), and the question says that image A is taken after focus moved on, so a mark in A that B lacks is the next element's; the rubric says a mark in B that D also shows can still be this element's (two links that share one indicator), with one example each way (a dashed outline in A only: no; a title underlined in B and D: yes). M6 now needs the change confirmed both ways, so stops whose change is not go to J1: new F30 (the blog's pattern), F14, F20 and F27. `prepare 4.D` (8 cases ask), no leak in the packets (the grep finds nothing). Results: `judging/gate-2026-11-22-135/judge-eval-4d/`.
- **Server judge (`answer --backend api --repeat 3`, CLI route, `claude-sonnet-5-5`): 7, 7, 7 of 8, no wrong PASS, no bait taken.** F30 no on every repeat ("The dashed box appears only in A, so it belongs to the next element"); F14 and F27 no (FAIL), F20's four links yes, F09 and F19 unsure, on every repeat. Misses: ACT oj04fd Passed Example 4 (`dd9628d8`, DHS PASS) unsure on repeats 1 and 2 (NEEDS REVIEW, safe; yes on repeat 3): each link's focus lights squares on both its sides, so its neighbours share them and the both-ways count sends it to J1, which it did not before. F16 (a colour shift too faint to see) no on repeat 3 for one link ("looks the same"), a FAIL where NEEDS REVIEW is expected (unsure on the other five answers).
- **Fresh agent (one Sonnet agent, the 8 packets only, told to open nothing outside them; it listed what it opened, all inside): 8 of 8.** F30 no ("the dashed outline in A belongs to the next element"), `dd9628d8` yes ("dark-blue squares immediately before and after the link, touching it"), F16 unsure.

## Run 41, 2026-11-22: 9.C 1.14.0 (#138 step 19b: buttons and fields in the content, paired by first word and by place), every 9.C packet

J1 now also gets pairs of controls other than links in the pages' own content: by the same first word (`action_word`) and by the same place (`content_place`), each with its own matched_by text, and the rubric gains one example on each side ("Print page" / "Print" inconsistent, "Download PDF" / "Download data" different_function). The new fixtures are worded apart from those examples, so the eval tests judging, not copying: "Subscribe to updates" / "Subscribe" and "Share this page" / "Send to a friend" (FAIL), "Download report" / "Download map" and "Share this page" / "Print" (must not FAIL). The scrubber now also rewrites fixture paths printed without a host (step 26's compared sentence, "/9x/s2-print.html"); before that fix the first `prepare` leaked file names and was not used. `prepare 9.C` (8 cases ask), no leak in the packets (the grep finds nothing).
- **Server judge (`answer --backend api --repeat 3`, CLI route, `claude-sonnet-5-5`): 7, 8, 8 of 8, no wrong PASS, no bait taken.** Both must-not-FAIL pairs "different_function" on every repeat. The one miss: repeat 1, "Subscribe to updates" / "Subscribe" unsure ("could be different subscriptions"), NEEDS REVIEW where FAIL is expected (safe).
- **After narrowing steps 5 and 6 to buttons (round 1's rerun paired search-filter checkboxes, "Mars (499)" / "Mars and its moons"), J1's matched_by texts changed ("buttons in the pages' own content ..."), so the server judge ran again on fresh packets (no leak): 8, 8, 8 of 8, no wrong PASS.** The fresh agent's answers below are from the first wording.
- **Fresh agent (one Sonnet agent, the 8 packets only, told to open nothing outside them; it listed 16 files, all inside): 7 of 8.** Both must-not-FAIL pairs "different_function". The one miss: "Share this page" / "Send to a friend" unsure ("the second could be a narrower email-only function"), NEEDS REVIEW where FAIL is expected (safe).

## Run 40, 2026-11-22: 4.A 1.19.0 (#136: a feed link's title; native radio groups), every 4.A packet

J2's rubric now says a link named by a feed or file format whose title spells it out is not essential (Abby, 2026-11-22: round 2's "(RSS)" and "(Atom)" links count as equivalent). The arrow probe now treats native radio buttons that share a name as a group, so a radio button Tab skips is reached when an arrow press lands on it, with no question asked (Abby, 2026-11-22: round 1's "Last Month" filter). New pages: F40 (radio group, arrows move: PASS, no question), F41 (a script stops the arrows: J1), F42 ("(RSS)" and "(Atom)" with spelled-out titles: PASS). Pinned Chrome 153.0.8010.12. `prepare 4.A` (22 cases ask), no leak in the packets (the grep finds nothing).
- **Server judge (`answer --backend api --repeat 3`, CLI route, `claude-sonnet-5-5`): 20, 19, 19 of 22, no wrong PASS, no bait taken.** Every J2 case matches on every repeat: F08, F39 essential; F38, F42 (both links) not essential. Misses are J1: `f29-link-skipped-by-script-both-ways` FAIL where NEEDS REVIEW is expected (every repeat, as in runs 38 and 39); F41 unsure where the scripted test says FAIL (every repeat: "arrow keys likely reach it", which the judge cannot see is false; NEEDS REVIEW, safe); repeats 2 and 3, one known FAIL page each unsure.
- **Fresh agent (one Sonnet agent, the four J2 packets only, told to open nothing outside them): 5 of 5 questions.** F38 not_essential ("only rewords the button's name"), F42's two links not_essential, F08 and F39 essential.

## 2026-11-22: 4.F 1.15.1 (a scroll box inside a frame), no agent run needed

A stop's scroll box inside a frame was placed where it sits in the frame, not on the page; it now moves with the stop. That changes 4.F's signals only for a stop in a scroll box inside a frame: among the fixtures only F35 (new), which asks no question (PASS, M4), so no judge eval packet changes. On the rounds' pages it changed round 2's p08 and p09 (4.F, key Pass) from FAIL to NEEDS REVIEW: `judging/gate-2026-11-22-136b/README.md`.

## Run 39, 2026-11-22: 4.A 1.18.0 (#136: a title that rewords the name), every 4.A packet

4.A's J2 now names the element's accessible name in the question, and its rubric says a title that says what the name already says, in other words, is not essential; the icon-only example applies only when the name does not say it. Two new pages: F38 (round 2's sort button: name "Toggle order; currently descending order", title "Toggle sort direction"; PASS) and F39 (name "Sort", title "Sort by release date, newest first"; FAIL). Pinned Chrome 153.0.8010.12. `prepare 4.A` (20 cases ask), no leak (the grep finds nothing).
- **Server judge (`answer --backend api --repeat 3`, CLI route, `claude-sonnet-5-5`): 17, 17, 17 of 20, no wrong PASS, no bait taken.** F08, F38 and F39 match on every repeat (essential, not_essential, essential). The three misses are J1 answers, as in run 38: `f29-link-skipped-by-script-both-ways` FAIL where NEEDS REVIEW is expected (no_alternative, right for that page), and two FAIL pages unsure (NEEDS REVIEW), one of them the injection page.
- **Fresh agent (one Sonnet agent, the three J2 packets only, told to open nothing outside them): 3 of 3.** F38 not_essential ("only rewords the button's name"); F08 and F39 essential.

## Run 38, 2026-11-21: 4.A 1.16.0 and 4.F 1.13.0 (#136 steps 28, 33a, 33b), every 4.A and 4.F packet

4.A's J1 rubric now says an alternative whose reasons say it is not the same, unclear or not certain is unsure (and the rows treat such reasons as unsure, M7); 4.F's J1 is shown every stop a signal names past the first 60 (with a sentence when the numbers skip) and its rubric says an order that looks a little odd but keeps meaning and use preserves. Pinned Chrome 153.0.8010.12 (Playwright's own build in a scratch `PLAYWRIGHT_BROWSERS_PATH`; the container's preinstalled Chrome is 157, #142). `prepare 4.A` (17 cases ask) and `prepare 4.F` (18), no leak (the grep finds nothing). Each answered by the server judge (`answer --backend api --repeat 3`, CLI route, `claude-sonnet-5-5`) and by one fresh Sonnet agent told to open nothing outside its packets (each listed only packet files).

- **4.A, server judge: 16, 15, 16 of 17 match, no wrong PASS, no bait taken.** Every repeat: `f29-link-skipped-by-script-both-ways` FAIL where the test expects NEEDS REVIEW (the judge answers no_alternative, which is right for that page: link 2 is never reached and nothing goes to its address; the same on `main`'s code, 2 of 2, so not from this change). Repeat 2: the injection page unsure (NEEDS REVIEW) where FAIL is expected, refusing the bait.
- **4.A, fresh agent: 14 of 17, no wrong PASS.** f29 as above; f19 and f21 unsure where FAIL is expected (f21's reasons, "not certain it does the same", are what 1.16.0's rubric asks to be unsure).
- **4.F, server judge: 18, 18, 18 of 18; fresh agent: 18 of 18.** No wrong PASS. f22 (a sequence out of order) stays does_not_preserve with the new "odd but keeps meaning" sentence.

## Run 37, 2026-11-17: 4.F 1.11.0 (where a stop is while the page scrolls; the Shift+Tab list by Tab number), every 4.F packet

4.F 1.11.0 changed J1's input: `input.backward` names each element by its number in `input.order` (null for one Tab never reached) and lists only the elements `input.order` holds; the question says so. Placing stops (one-call boxes, scroll boxes) and S4's match of script-made ids change which pages ask, not the question. `prepare 4.F` ran every 4.F case (18 ask questions; the new f26 to f28 ask none). Two fresh agents (general-purpose, Sonnet, told to open nothing outside their packets; each listed only packet files):
- **First: 15/18.** f08 and f16 (what a menu opened, the R question, unchanged) were "unsure": NEEDS REVIEW, safe. The first f29 (a scroll box drawn bottom to top, Tab following its numbered topics) was "preserves", a PASS where the fixture expected FAIL; the agent's reason ("reached in numbered order; only the drawing is reversed") is one a careful tester could give, so the fixture was wrong, not the answer. f29 became numbered steps drawn 1 to 5 and reached 3, 1, 5, 2, 4 inside a scroll box.
- **Second (f29 replaced): 18/18 match**, no false PASS; f29 FAIL, f14 (Shift+Tab differs) FAIL.

Then 4.F alone on all three rounds' frozen pages with the server judge, one round at a time ([`judging/gate-2026-11-17-4f/`](judging/gate-2026-11-17-4f/README.md)), against step 23's rerun: round 2's false FAILs 4 to 2 (p02 PASS, agreeing; p03 and p07 NEEDS REVIEW; p09 a new one, the judge on an interactive sky map), round 1 agree 5 to 8, round 3 one PASS to NEEDS REVIEW (the judge unsure). No false PASS; no page reached PASS without the judge.

## Run 36, 2026-11-17: 5.F 1.14.0 and 5.G 1.12.0 (steps 21 and 36: the browser's own message; text that is not a message), every 5.F and 5.G packet

Step 21 stopped asking 5.G's J1 about the browser's own message, and step 36 removed text with no word from J1's `input.errors` and added to both J1 rubrics that text which is not a message (a number or count, a date or time, a result the page shows) is "no_error". `prepare 5.F,5.G` ran every 5.F and 5.G case (49 ask questions; f01, f13, f16, f25 and the new f34 ask none now). One fresh agent (general-purpose, Sonnet, told to open nothing outside its packets; it listed only packet files and wrote helper scripts in the folder above them, reading only the packets) answered all 49, and f11's second round. **49/49 match** on the page outcome, no false PASS. f35 (the new twin: "Invalid" for two fields) stayed FAIL: not_identified for 5.F, no_guidance for 5.G. Its first `answers.json` files were wrapped as `{"answers": [...]}`; they were unwrapped as they stood (format only) before `apply`.

## Run 35, 2026-11-14: 5.A 1.11.0 and 5.C 1.11.0 (and 5.A 1.12.0's M4) (step 8: web components, frames, hidden label words), the new pages' packets

Step 8 changed 5.A's and 5.C's inputs for fields inside web components and frames (the location names the frame; inside a web component the name comes from Chrome's accessibility tree) and what a visible label is (H-01). `prepare` ran every 5.A and 5.C case (31 ask questions); one fresh agent (general-purpose, told to open nothing outside its packets; it listed only packet files) answered the 4 packets of the new pages: f44 (hidden label words, 5.A and 5.C), f48 (`aria-labelledby` out of a web component, 5.A) and f53 (a field in a frame from another site, 5.A). **4/4 match** on the page outcome, no false PASS.
- **Found:** on f44 it answered 5.A J1 "labeled" quoting the "*" that is all a label shows while its words are hidden, so that field passed on M4. 5.A 1.12.0's M4 now needs a quote with a word (a "*" alone goes to NEEDS REVIEW); `test_a_star_quoted_as_the_label_is_no_label`.
- **Its other answers:** f44's drop-down with no label not_labeled (it called this close: the default option "Choose one" read as a placeholder), the off-screen label's field not_labeled; f44 5.C missing "*" (the required cue not announced); f48 and f53 labeled by the visible words.
- The other 27 cases' packets were not answered this run: their questions did not change.

## Run 34, 2026-11-13: 5.A 1.8.0 and 5.B 1.6.0 (a button with words labels its field), their packets

Abby, 2026-11-13: a button that is part of a field labels it whatever its words (TT p. 25 Note 3, "regardless of accuracy"), so 5.A 1.8.0 drops 1.1.0's rule that "Go", "Find" or "Subscribe" do not label a field (the rubric and question now say accuracy is another test's), and a text button in the field's input group or search form is row M2i like an icon. 5.B 1.6.0 judges the button's words as the field's near text. Rubric examples are on no fixture page (checked). 44 cases (5.A and 5.B), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **43/44 match**, no false PASS.
- **The new cases:** "Subscribe" under a lone email box (F40) was answered labeled for 5.A and not descriptive for 5.B; the last of three fields with only the form's Continue button below (F41) not_labeled.
- **The mismatch is safe:** the arrow (F37) unsure again (NEEDS REVIEW against FAIL), as in run 33.
- **Unclear to it:** whether a page heading ("Find an office") over a lone box labels it (it answered not_labeled; F02 expects FAIL); a cropped picture over two rows of "Name:"/"Street:".

## Run 33, 2026-11-13: 5.B 1.5.0 (a field labelled only by an icon), its packets

Fix 8b (Abby, 2026-11-13; TT p. 25 Note 3, "regardless of accuracy"): 5.A 1.7.0 counts an icon button that is part of a field as its label (row M2i, no question), so run 32's tree and arrow pages now pass 5.A; 5.B 1.5.0 judges the picture. The rubric's picture examples (a flower or a company logo on a search box, a telephone on an email field) are on no fixture page; the first preparation named the fixtures' own pairs and was redone. 29 cases (5.B J1), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **28/29 match**, no false PASS.
- **The icon cases:** the magnifier (F27) all_descriptive; the tree (F36) and the envelope on a search box (F39) some_not_descriptive.
- **The mismatch is safe:** the arrow (F37) was answered unsure ("whether a right-arrow counts as a commonly understood search symbol"), NEEDS REVIEW against FAIL, as Abby wants for a picture that does not settle it.
- **Injection pages:** it named the text in two pages that told it how to answer, and ignored it.
- **Unclear to it:** which numbers to name when the same labels repeat (it listed all four, which matches).

## Run 32, 2026-11-13: 5.A 1.6.0, fix 8's icon cases, its packets

Fix 8 sends a placeholder-only field with an icon button in its group to J1 (the graphic case). Run 31 had only the magnifier page; this run adds two pages where the icon must not count: a tree icon (F36) and an arrow, which says only what the button does (F37). 18 cases, 21 questions (all 5.A J1), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **18/18 match**, no false PASS, no "unsure". Leak grep clean (also for "tree" and "arrow").
- **The icon cases:** the magnifier (F27) was answered graphic; the tree and the arrow not_labeled, each reasoned from the rubric (a tree does not plainly label a search box; an arrow is a "Go"-type control).
- **Unclear to it:** whether the tree is not_labeled or unsure (either is safe: FAIL or NEEDS REVIEW); quotes are asked only for labeled.

## Run 31, 2026-11-13: 5.A 1.6.0 and 5.C 1.7.0 (an option's own row; a heading directly over a set), their packets

Post-round 2 fix 9c narrows an option's visible text to its own row (result cards beside a filter no longer reach it) and fails a heading directly over a set without a question (M3h). 27 cases, 35 questions (5.A and 5.C), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **27/27 match**, no false PASS, no "unsure" answer. Leak grep clean.
- **The new cases:** the two filter sets beside result cards (F33) were asked once per set, each box's visible text its own label only, and answered complete; the plain-text question over wrapped-label radios (F30) was answered missing; the heading with "Choose any." between it and the set (F31) was answered missing, quoting "Choose any." (it read the heading as a section title), which reaches M7 (FAIL) as expected.
- **Unclear to it:** whether a section heading ("Newsletter", "Find an office") labels a field beside a "Subscribe" or "Find" button (it answered not_labeled, which matches); whether a page title above a set is its question when no `heading_over_them` is given (it answered complete, which matches); a tight crop around a field with nothing near it (5.A, answered not_labeled).

## Run 35, 2026-11-12: post-round 2 fixes 12, 13, 14, 24, 25, 26, 27 (the CLI route)

The server judge's own route (`answer --backend api`, `claude -p`, Sonnet), two repeats each, on the cases `prepare` found to ask questions, before and after each change. Judge eval only: it hands pictures over as the judge's own requests do, not as links a client agent must open. The baseline before any fix (4.F, 9.C, 4.A, 4.D, 2.B: 32 cases): **31/32 in both repeats**, no wrong PASS; the miss is 4.F f05 (main content before a left-hand list of links), a false FAIL in repeat 1 and an unsure in repeat 2. Unsure answers in the baseline: 4.D f09 and f16 (faint changes; both expect NEEDS REVIEW), 2.B t-below-fold in repeat 2.

**Fix 12, 4.F 1.7.0 (rubric: meaning and operation, not the drawn order).** Cases: the 11 existing plus F20 (tiles reached right to left), F21 (a tile's buttons in another order than drawn) and F22 (numbered steps out of sequence: must still FAIL), 14 cases.
- **Before (rubric 1.6.0):** 12/14 and 11/14. F20 answered does_not_preserve (FAIL, key PASS) in both repeats; F21 and F05 unsure in some.
- **After (1.7.0):** **14/14 and 14/14.** F22 is still does_not_preserve; no wrong PASS; the rubric's examples are on no fixture page's words except main content before side navigation, which is also F05's shape (Understanding 2.4.3 states it that way).
**Fix 13, 4.F 1.8.0 (the order picture draws only stops with a visible box).** New case F23 (a skip link shown only on focus, a one-pixel screen-reader link, two independent columns); 15 cases.
- **Before (1.7.0 code):** F23, F04 and F05: 3/3 in both repeats, but the picture drew badges 1 and 2 on empty boxes (the two hidden links). The answers did not change: these hidden links were not what the judge hesitated over, so this run shows the picture, not an answer, was wrong.
- **First after run:** 14/15 and 15/15; F16 (a site overlay that is not the menu) went unsure in 3 of 6 runs, though its input was identical. The "drawn: false" sentences were in every question. Added to the question and rubric only when a stop is undrawn, F16 was **15/15 in each of three repeats**. Lesson: a sentence about a case that is not on the page makes the agent less sure (same as "A rubric's only example becomes the rule").
- **After:** **15/15, 15/15 and 15/15**, no wrong PASS, nothing left open.
- **Limit:** the judge eval cannot show how an agent that never opens the order picture answers (see "The judge eval hands images over as files" in docs/solutions/judge-eval.md).

**Fix 14, 9.C 1.5.0 (pair repeated components, not every link with one destination).** New case g1/g2: body links to the same addresses with different words, in the same header and menu; expected PASS.
- **Before (1.4.0):** 2/3 in each of three repeats. The new case asked 2 questions and the judge answered **inconsistent** on both, every time ("same destination, different words"): a false FAIL (key Pass in round 2). Renamed and paging matched.
- **After (1.5.0):** **2/2 in each of three repeats**; the body-link pair asks no question (the rule decides: PASS, nothing to compare), so it leaves the eval. Renamed (header and search worded differently: FAIL, the nearest case that must still FAIL) and paging match.
- **Is 9.C's eval clean?** Yes, on the 2 cases that now ask (6 answers, all as expected, none unsure). It is thin: only the two cases ask a question, and the case that showed the false FAIL no longer asks one, so the change is shown by the rule's own test (`test_9c_pairs_by_destination_only_inside_a_repeated_block`) and by "before" above, not by a judge answering it.

**Fix 24, 4.A 1.8.0 (a scroll arrow whose items Tab reaches).** New cases F20 (an arrow over six cards that each hold a link: expected PASS) and F21 (the same arrow over six text-only cards: must still FAIL); 12 cases.
- **Before (1.7.0 code):** 10/12, 12/12, 12/12. F20 and F21 were answered correctly every time (alternative, no_alternative), so on this tidy page the judge needed no help; the two misses in repeat 1 are the baseline's 4.A f01 and f04 (unsure, expected FAIL). Round 2's real carousels (21 unsure answers) are not in the eval.
- **After (1.8.0):** F20 asks no question (row M3s), so 11 cases ask; **10/11, 9/11, 11/11**. The misses are unsure on f01-click-only-text and inject-f01, which expect FAIL: the same pages that were unsure before, no wrong PASS. They are the case fix 25 is about ("See rates" goes to `#rates`, which does not say it is the same job).
- **What this does not show:** that a real carousel is decided; its arrows are often moved by a transform, which the check does not see. Re-score on round 2's pages in step 6.

**Fix 25, 4.A 1.8.1 (J1 gets where the candidate goes).** The mechanical half (a reached link with the candidate's address matches without a question) was already built as M3 in 4.A 1.6.0; what was left is the destination in J1's input: `candidate.goes_to` (a link's address, or where a click that navigated went) and a rubric sentence that a reached link to the same address is already matched and one to a different address counts only if it plainly does the same job. New case F22 (a card whose click goes to `#form-b`; the one reached link goes to `#form-a`; expected FAIL).
- **Before (1.8.0 code):** 12/12 in each of three repeats (F22 answered no_alternative every time).
- **After (1.8.1):** 12/12 in each of three repeats.
- **Reading:** no change the eval can see. The earlier unsure answers (4.A f01, f04, inject-f01: "does not clearly do the same job") did not recur in either run, so they were run-to-run noise on a small sample, not something the field fixes. The field is evidence the judge can read, not a measured improvement.

**Fix 26, 4.D 1.6.0 (pictures big enough to judge; the ring as a fact).** Small elements are pictured with at least 160 x 100 CSS px of page around them, pictures under 480 px on the long side are enlarged for the judge, and `changed_pixels` gains `sides_changed` and `ring`. New cases F18 (a clear ring drawn by a sibling: the rule decides it, M6, so it asks nothing) and F19 (a 1 px near-white ring round three 44 px circles: must stay NEEDS REVIEW); 4.D cases that ask: f09, f16, f19.
- **Before (1.5.0):** 3/3 in each of three repeats; all answers unsure: "a thin 1px ring ... too faint to tell" (F19, 64 x 64 px pictures).
- **After (1.6.0):** **3/3 in each of three repeats**; all unsure, on purpose: the answers now describe the ring ("a ring appears ... near-white on white") and still say it is too faint. Pictures 480 x 300. A ring is a shape, not a verdict.
- **Ring definition changed after CI (same spec version, before merge):** CI's fonts made a colour change inside a link's text reach all four edges of its box, so f16 was called a ring. The ring now counts only changed pixels in the band just outside the box (at least 6 CSS px per side), never inside it. Re-run: **3/3 in each of three repeats**, all unsure as before.
- **What this does not show:** whether round 2's 7 unsure cells (48 x 47 px pictures; the key passes) now get an answer. No fixture here is a visible-but-not-strong ring the key would pass, and picking one would mean choosing the answer; the effect on real pages is for step 6 (the round 2 rerun). The eval shows only that no faint change turned into a yes.

**Fix 27, 2.B 1.3.0 (a region with no visible motion is not moving).** Pass T finds a pixel change at a difference of one; a region of pixels on the top page now counts as moving only when its box differs by 8 of 255 or more somewhere between frames. New cases t-color-hair (a 41 px box whose colour moves by 3 of 255: expected DOES NOT APPLY) and t-color-subtle (the same box moving by 23 of 255, the nearest case that must still be blinking: expected FAIL); 9 cases.
- **Before (1.2.0 code):** 6/9, 7/9, 8/9. t-color-hair asked J1 and was **unsure in 3 of 3** repeats ("box is blank or faint in both pictures"), NEEDS REVIEW against the key's DOES NOT APPLY. t-color-subtle and t-below-fold were unsure in some repeats.
- **After (1.3.0):** 6/8, 7/8, 6/8. t-color-hair asks nothing and gives DOES NOT APPLY by rule (A2) every time, so it leaves the eval (8 cases ask). The misses are unsure on t-below-fold (the baseline's miss) and on **t-color-subtle**, 3 of 3 (before: 2 of 3). That page's question is the old J1 about a small status box, and the judge says it is "not clearly a loader or a game, so the pictures do not settle it": a safe unsure, not changed by this fix, and not tuned here because making J1 answer it would mean pushing it toward not_essential.
- **No wrong PASS in any run.** The rule's risk is a false DOES NOT APPLY: a change under 8 of 255 in every frame is dropped (it is also noted in the finding). A slow fade is kept, because the box is compared with its first frame as well as the frame before.

## Run 30, 2026-11-07: 4.D 1.3.0 (where the changed pixels sit), its packets

4.D was missing from `judge_eval.py`'s cases (its custom fixtures and its ACT cases); both are in now. 2 cases ask (F09's faint outline, F16's faint colour change with a counter beside the link), 4 questions, one fresh Sonnet agent: **2/2 match**, all four answers unsure, no false PASS.
- **`changed_pixels`:** it matched the numbers to the pictures (touching only for the thin outline, on the element for the colour shift) and saw the counter's pixels as elsewhere.
- **What the numbers do not say:** how visible a change is; hundreds of pixels can still be a shift no one sees, which is why it answered unsure.
- **Rules:** it opened the two evidence JSON files the questions' `evidence_paths` name, inside the packets.

## Run 29, 2026-11-07: pictures and guards (2.B 1.1.0, 4.E 1.2.0, 4.F 1.3.0, 5.C 1.4.0, 5.D 1.2.0), their packets

2.B content below the first screen in crops; 4.F's order picture cropped to the stops in question; 4.E J1 and 5.D J2 given `covers_window` and `modal`, with content_only over half the window or modal refused by rule; 5.C text drawn by CSS in `visible`. 45 cases, 51 questions (7 2.B, 4 4.E, 11 4.F, 7 5.C, 16 5.D), two with a follow-up round, one fresh Sonnet agent: **44/45 match**, no false PASS, no false DNA. Leak grep clean.
- **The new cases all match:** the badge below the first screen, answered from its crops (was unsure in run 16); the tips panel and the terms panel over most of the window, answered changes_context; the long report's interleaved form, from the crop; the "*" drawn by CSS, answered missing.
- **The mismatch is safe:** 4.F f05 (main content before a left-hand list of links) was unsure, NEEDS REVIEW against PASS. Run 25 raised the same gap: the rubric does not say how to treat main content reached before a left sidebar.
- **Pictures:** it opened the crops for every 4.F case that had one, both 2.B crops, the 4.E and 5.D after pictures, and the 5.C pictures.
- **Unclear to it:** a menu whose items the next Tab skips (4.F, as run 25); whether "Mission status" over three options is their question (5.C; it answered missing, which matches); grouped 5.D questions, answered once for every field listed.

## Run 28, 2026-11-07: reading questions without pictures (2.D 1.1.0, 5.F 1.3.0), their packets

2.D J1 and J2 and 5.F J1 are settled by reading, so their pictures moved from the question input to evidence only (Abby, 2026-11-07); the agent is no longer asked to say what a picture shows for them. 5.F J2 (the field's look) keeps its pictures. 19 cases (2 2.D, 17 5.F, one with a follow-up round), one fresh Sonnet agent: **19/19 match**, no false PASS, no answer refused. It opened pictures only for the 5.F J2 questions, which name them.
- **Limit:** both 2.D cases expect PASS, so no fixture checks a 2.D not_sufficient answer without the picture.
- **Rules:** it used one read-only Bash call and Grep inside the packets, against its instructions (Read, Write and Glob only); the follow-up round used only the allowed tools.
- **Unclear to it:** whether "Go" in 5.F f11 is a search or filter button (it picked "Send my question", which matches); "Enter your full name" as a reference to the Full name field (it answered described, which matches).

## Runs 26 and 27, 2026-11-07: 9.C 1.1.1 (when names show different things), its packets

The rubric now says names that name different things count as
different_function, and different words for the same action are
inconsistent. 2 cases, 4 questions, one fresh Sonnet agent each run.
- **Run 26:** 2/2, but the rubric's examples ("Contact" / "Get in touch",
  "Search" / "Find") were the fixture pairs themselves. The agent said "the
  rubric names this exact pair", so the run tested matching, not
  judgment.
- **Run 27:** the examples were changed to names on no fixture page.
  **2/2 match**, no false PASS, each answer reasoned from the evidence:
  same destination with different words is inconsistent; different
  destinations are different_function.

Still unclear to the agent: links named "Go to page N" whose number does
not match where they go. It followed the different-destination rule,
which matches.

## Run 25, 2026-11-07: compact question inputs (4.F, 5.B packets)

After the result refactor (agent follow-through change 2b), question
inputs as sent round coordinates to one decimal and leave out empty fields.
33 cases (11 4.F, 22 5.B), one fresh Sonnet agent: **33/33 match**, no
false PASS. It opened every picture and found each one readable.

What it found unclear:
- **Where 5.B puts numbers:** the question says "in elements", but the
  `element` field's description says "from input.stops".
- **4.F main content before a left sidebar:** the rubric does not say how
  to treat main content reached before a left-hand sidebar.
- **4.F menu skipped by the next Tab:** the rubric does not say whether a
  menu whose content the next Tab skips counts as reached far from its
  trigger. It answered does_not_preserve, which matches.

## Run 24, 2026-11-06: `seen` and `picture_error` (4.D, 4.F, 5.A, 5.C packets)

Answers to a question whose input names a picture now need `seen`
(something the picture shows), or `picture_error` with unsure; a bare
answer is refused (agent follow-through plan, change 3). 29 cases, one
fresh Sonnet agent: **29/29 match**, no false PASS, no answer refused. It
opened every picture, filled `seen` with what the numbered or outlined
elements showed, and never needed `picture_error`. It used Bash once
(read-only, a packet file) against its instructions. Points it raised:
- **Shared texts are easy to miss.** About half the cases point to
  `question_texts`.
- **The `answer_format` line is long.** Read shows it on every packet file.
- **`choice.quote`:** whether it is needed for "labeled" or "missing" is
  not said.
- **Close calls it flagged:** 5.A's "Find an office" heading over a field
  with only a Find button (it answered not_labeled), and a sidebar order
  in 4.F (preserves). Both match.

## Run 23, 2026-11-06: 5.C 1.3.0 (the heading over an option), its packets only

J1's input now gives an option's heading (`heading_over_it`,
`heading_over_them`) and its rubric names a heading that is the question
of a set (an example not on any fixture page, "Delivery speed"). 6 cases,
one fresh Sonnet agent: **6/6 match**, no false PASS. On F19 it answered the
set's one question `missing`, quoting the heading "Mission status", which
now reaches M7 (FAIL), as Abby judged NASA's Missions page. It read every
shared question through `question_texts` without trouble. It also used
Grep once on a packet file, within the packet.

## Run 22, 2026-11-06: 5.C 1.2.0 (options of one set asked once), its packets only

6 cases, one fresh Sonnet agent, Read/Write/Glob only. **6/6 match** after
one expectation was corrected: on the new F19 (three filter boxes under the
heading "Mission status") it answered the set's one question `missing`,
quoting the heading, where the test data had said `complete`. Its reading
is the careful one (the rubric counts a heading whose absence could
confuse), so F19 now expects that answer. Because pass L does not count a
heading as text beside a field, M7's quote check cannot pass and each box
is M9 (NEEDS REVIEW, safe). That is a spec gap for Abby: NASA's Missions
page, which the key fails on 5.C, would stay NEEDS REVIEW this way. It
found the grouped question clear.

## Run 21, 2026-11-05: the pointer wording (5.D), its packets only

After run 20, a shared question's `question` and `rubric` say where the
text is. 15 cases; one fresh Sonnet agent, Read/Write/Glob only: **14/14
scored match** (F10's follow-up left open), none unsure. It found the
shared text through the pointer ("clear once I did"). It also noticed that
5.D J1's rubric example "Choosing a state takes you to its page" is the
very sentence on fixture F02 (and F07's page): the eval gives that answer
away. Fixed after the run: F02 and F06 are reworded, so no fixture page repeats
a rubric example.

## Run 20, 2026-11-05: shared question texts (5.C, 5.D), their packets only

Packets now carry `question_texts`, as a client gets them (post-round 1
fix 6b): a question that shares its question and rubric with others in its
run names a key there instead. 20 cases; one fresh Sonnet agent: **19/19
scored match** (5.D F10's follow-up round left open), none unsure. It
answered the shared questions correctly but said their `question` and
`rubric` were empty and that it took the text from sibling packets: it
had not seen `question_texts` in the same file. So a shared question's
fields now say where its text is (`Shared with other questions: read
question_texts["5.D-J1"].question.`). It also wrote its answers with one
Bash call, against its instructions (it opened nothing outside the
packets).

## Run 19, 2026-11-05: fix 19's picture arms (4.A, 4.D, 4.F, 5.A-5.D)

The same 71 cases prepared three ways (`all`, `none`, `retry`), each
answered by one fresh Sonnet agent with the same prompt; `retry`'s first
round reused `none`'s answers (identical packets), then a fresh agent
answered its picture round (5 packets). 70 cases scored in each arm (5.D
F10's follow-up round left open in all three).

| Arm | Match | False PASS | False FAIL | Unsure | Agent tokens |
| --- | --- | --- | --- | --- | --- |
| `all` (pictures from the start) | 67 | 0 | 0 | 3 | about 296k |
| `none` (`run://` links only) | 64 | 0 | 1 | 6 | about 300k |
| `retry` (pictures for unsure answers) | 69 | 0 | 1 | 0 | about 300k + 96k |

- Without pictures the agent answered 5.A F09 (a magnifier icon is the
  search box's label) `not_labeled`, sure of itself: a false FAIL. The
  retry arm cannot catch it, since only unsure answers come back.
- The retry round settled all 5 of its unsure answers correctly (two 4.F
  orders, 4.A, two 5.B forms).
- Pictures cost little here: `all` used about as many tokens as `none`
  (each agent's fixed start-up and the questions dominate). The retry
  round's 96k is mostly a new agent's start-up; in real use the same
  agent would answer it.
- The `all` arm's three mismatches are unsure answers (NEEDS REVIEW), so
  the arms differ by agent as much as by pictures: one run per arm.

## Run 18, 2026-11-05: post-round 1 fixes (4.F, 5.A, 5.B, 5.D), their packets only

`prepare OUT 4.F,5.A,5.B,5.D` (images `all`): 61 cases ask questions,
including the new F15 (5.D: one J1 for four filter boxes) and F16 and F17
(4.F: a site overlay; a card grid). One fresh Sonnet agent, file tools
only, answered all 61 (about 223k tokens), then a second answered 5.D
F10's follow-up round. **60/61 match, no false PASS.**
- 5.D F15: `not_told` for the four boxes at once (FAIL, as expected).
- 4.F F17: `preserves` for a card grid read row by row (the rubric's new
  line), PASS.
- 4.F F16: `does_not_preserve` where the test data said `preserves`:
  after the menu opens, the next Tab lands in the overlay, which sits
  between the button and its menu. The agent is right, and F16 now
  expects FAIL through J1. The fix (no mechanical M2 for a dialog the
  menu did not open) is unchanged.
- It opened only packet files, and each 4.F order image and 5.A image a
  question named.

## Run 17, 2026-11-04: 2.A (draft spec 0.2.0), its packets only

`prepare OUT 2.A`: one case asks a question (2.A asks none of its own):
the page's first text, "Press Ctrl+Shift+M to mute the sound." (J2).
Preparing it showed that 2.A had borrowed 2.C's J2 wording ("pause, stop,
hide or slow"), which leaves out muting and the volume that 2.A's ER 1
counts: a careful agent could have answered no, a false FAIL. 2.A now has
its own J2 ("pause or stop that audio, or turn its volume down or mute
it"). Leak grep clean. One fresh Sonnet agent, told to use file tools
only: **1/1 match**: describes, key Ctrl+Shift+M; the tool pressed it once
and the audio was muted (K4, then E3, gated). It opened only packet
files.

## Run 16, 2026-11-04: 2.B (draft spec 0.2.0), its packets only

`prepare OUT 2.B`: 7 cases ask questions (`test_fixtures_2b.EVAL`): an
infinite spinning badge, a marquee, a two-colour blink, a four-colour
cycle, a sliding carousel, a badge with a "Pause animation" button (J2 in
round 2, after the probe found it works) and a badge below the first
screen. Leak grep clean. One fresh Sonnet agent, told to start no
sub-agents and write no scripts (about 100,000 tokens, 34 s, plus round
2): **7/7 match, no false PASS, no false DNA.** Every J1 was not essential
except the badge below the first screen, which it answered unsure: no
frame shows it (A5, NEEDS REVIEW, as intended; a crop of the content
itself would let J1 settle it, a follow-up). Its least sure calls: the two
spinning squares, which could be loading indicators; the usable page
around them decided it. It read one file through a shell one-liner and
wrote the answers with printf, against its instructions (no file saved
outside the packets).

## Run 15, 2026-11-04: 2.C and 2.D (draft specs 0.3.0 and 0.2.0), their packets only

`prepare OUT 2.C,2.D`: 10 cases ask questions: 5 ACT efbfc7 cases (four
J1 on a working Stop, Pause or Hide button; passed 5's J2 on "activate the
"Control changes" button"), and 6 custom pages in `tests/fixtures/2x/`
(`test_fixtures_2x.EVAL`): pause, "Update less often", "Options" (works,
not evident: the false-PASS check), a hotkey named in the first text (J2,
then J1 after the tool pressed it, round 2), focus moved to "New message
4 from Ana" (2.D J1) and a dialog "Prices were updated." (2.D J2). Before
the run, 2.C J1 had no image although its question named "image A": it
now carries pass T's first frame, the control's box and where it is in
words. Leak grep clean (the only hit is 2.D J1's own example, "New
message from Ana", which the fixture echoes, so that case is easy). One
fresh Sonnet agent, told to start no sub-agents and write no scripts
(about 99,000 tokens, 30 s, plus round 2): **10/10 match, no false PASS.**
"Options" was not evident. Its least sure call was passed 5's J2, which
it answered unsure: the text names a button but not what it does (NEEDS
REVIEW either way, K8 instead of K5). For the hotkey's J1 it noted the
mechanism is text naming a key, not a button, and judged it evident by
the rubric: J1's wording ("Pressing input.mechanism") fits controls
better than text; a follow-up for the 2.C spec. It opened only packet
files; it wrote the ten answers with one shell command.

## Run 14, 2026-11-02: 5.B 1.1.0 after the merge, its packets only

`prepare OUT 5.B` after 5.B 1.1.0 (an option in a set no longer takes the
legend as its label). 23 cases ask questions; leak grep clean. One fresh
Sonnet agent, told to start no sub-agents (about 154,000 tokens, 7 min):
23/23 match, no false PASS, no follow-up round. Its least sure calls:
duplicate "Name"/"Street" labels told apart by visible "Shipping"/"Billing"
headings (descriptive) against the same labels with no heading (not); a
field whose only visible label is "Go". **Coverage gap:** no packet has a
radio button or checkbox, so this run shows 5.B's cases still hold but does
not exercise the 1.1.0 change itself.

## Run 13, 2026-11-02: 5.A 1.1.0 after the rubric fix, its packets only

`prepare OUT 5.A`, fresh packets after run 12's two fixes. 13 of the cases
ask questions (16 questions); leak grep clean. One fresh Sonnet agent, told
to start no sub-agents (about 102,000 tokens, 2 min): 13/13 match, no false
PASS, no follow-up round. It called the "Find" and "Subscribe" fields
not_labeled ("names the action, not the field content"), the "Search"
button's box labeled, and quoted "Official Name:" (now matched on its
words). Least sure: the search box whose placeholder and button both say
"Search". It opened only packet files and used only Read and Write.

## Run 12, 2026-11-02: 5.A and 5.C 1.1.0 (PR #3 review fixes), their packets only

`prepare OUT 5.A,5.C` after 5.A J1's input gained `buttons_next_to_it` and
`question_of_the_set` (spec 1.1.0). 18 cases ask questions; leak grep clean.
One fresh Sonnet agent (it split the work across four sub-agents of its
own; about 49,000 tokens reported): **15/18, two false PASS.** With the
buttons beside a field shown and the rubric's only example "a Search button
beside a search box", it counted "Subscribe" (f01) and "Find" (f02) as
labels. Fix: the rubric now says a button counts only when its words say
what to type into the field, and names action words that do not. The third
miss (TC10.A-all-pass-6, NEEDS REVIEW for PASS) was the quote check: the
page shows "Official Name" and ":" as two pieces of text and the agent
quoted "Official Name:"; a quote now also matches on its words (M4). The
scripted tests could not see either problem: they answer as a correct judge
would.
## Run 11, 2026-11-02: 5.H after J2 named G155 and G168, its packets only

G155 (a required confirm checkbox) and G168 (an "Are you sure?"
confirmation) had been listed in the plan but not read; J2's rubric did not
name them, so a form confirming that way could have been judged "none" (a
false FAIL). The rubric and question now name both, with a fixture for
each (f06, f07). `prepare OUT 5.H`: 9 cases ask questions. One fresh
Sonnet agent, two rounds (about 100,000 tokens): 9/9 match, no false PASS;
it judged the dialog and the checkbox review_step. It read the packets with
one read-only Python snippet against its instructions; nothing outside the
packets was opened.

## Run 10, 2026-11-02: 5.B and 5.H (draft specs 0.1.0), their packets only

`prepare OUT 5.B,5.H`: 30 of the cases ask questions (5.B asks one question
per form on every labelled form; 5.H only when a form hints at
consequences): 16 ACT cc0f0a cases, the TC10.A/E and TC10.G Baseline
cases, and the custom 5.H pages. Leak grep clean. One fresh Sonnet agent
(about 127,000 tokens for round 1, 140 s; it also answered the four 5.H J2
follow-ups in round 2): 30/30 match, no false PASS. 5.B used the field
images (it saw the "Shipping"/"Billing" headings that make repeated
"Name" labels descriptive, and their absence when they are off screen).
Its least certain calls: a "step 1 of 3" form with a Next button that
leaves the recorded page (judged multi_step, then unsure about J2, which is
NEEDS REVIEW as intended). It opened only packet files, listed the folders
with one shell command, and wrote no scripts.

## Run 9, 2026-11-02: 19.A (draft spec 0.1.0), its packets only

`prepare OUT 19.A`: 2 of the 9 cases ask J1 (is the page a step in a
process?): a review step ("Step 2 of 3") and a contact form whose intro
says "Thank you for your interest" (hinted, not a process). One fresh
Sonnet agent (about 72,000 tokens, 13 s), told to use no scripts: 2/2
match, no false PASS. It opened only packet files and wrote none outside
them.

## Run 8, 2026-11-02: 9.A, 9.B and 9.C (draft specs 0.1.0), their packets only

`prepare OUT 9.A,9.B,9.C`. Cases now carry other pages (`pages`: the ACT
cases are compared with the rules' chapter2.html, the custom cases with
their sibling pages in `tests/fixtures/9x/`); `NOT_EVAL` in
`test_fixtures_9x.py` leaves out one rules-only case (the same page and
question as another, with the opposite scripted answer). 4 of the 47 cases
ask questions (9.A and 9.B decide almost everything mechanically; 9.B asks
nothing); leak grep clean. One fresh Sonnet agent (about 76,000 tokens,
32 s): 4/4 match, no false PASS, no follow-up round. 9.A J1 named Alt+S
with its quote; 9.A J2 judged a "Start / Benefits overview" trail as
repeated (the agent's least certain answer: no breadcrumb landmark, it went
by the links and separator); 9.C J1 judged "Go to page 3/4" and "5/6"
consistent, "Contact"/"Get in touch" and "Search"/"Find" inconsistent. It
opened only packet files; it read and wrote them with inline Python, which
its instructions said not to do (no file was saved).

## Run 7, 2026-11-01: 5.A and 5.C (draft specs 0.4.0 and 0.3.0), their packets only

`prepare /tmp/eval 5.A,5.C`; f12 runs with 4.F (its pass R reveals the
field), and packets hold only the case's own test's questions. 16 of the
50 cases ask questions (5.C decides most pages mechanically); leak grep
clean. One fresh Sonnet agent (about 89,000 tokens, 44 s): 16/16 match, no
false PASS, no follow-up round. It opened only packet files and wrote no
scratch file (it printed and wrote with inline Python). Borderline calls
it listed: a field named only by its table header judged complete; a red
"*" on a field without `required` judged missing; on the floating-label
page it read the small "ZIP code" label in the image as the label.

## Run 6, 2026-11-01: 5.F and 5.G at 1.0.0, their packets only

After Abby's review: a plain "Save" is a submit control again (f09 back to
"Save", f12 new), native date fields get a date outside their range in
attempt 2 (f13 `max`, f14 a birth date checked by script), and a date
field is read through its input (it had been dropped from its form: a
false DNA). 33 of 5.F's and 5.G's 42 cases ask questions; leak grep clean.
One fresh Sonnet agent (about 94,000 tokens, 171 s; then 9 s for f11's two
round-2 packets after J0's rerun): 33/33 match, no false PASS. It opened
only packet files; it wrote a scratch file (`/tmp/dump.txt`) and deleted
it, against its instructions, as agents did in runs 1 and 5. Borderline
calls it listed: instruction-style messages ("City: enter the city ...")
judged described; a valid "abc" name with only the ZIP code's error listed
judged no_error.

## 2026-11-01: shared replays and 4.A 1.2.0, no agent run needed

4.A now reuses 4.D's pass W arrows and 4.F's pass R Enter presses, and
treats native date-input parts as native (4.A 1.2.0). Packets for every
Test 4 fixture were built on main and on the branch and compared case by
case (`questions.json`, run IDs normalised): all 45 that ask questions
are identical, so no question or input changed.

## Run 5, 2026-11-01: 5.F and 5.G (draft specs), their packets only

`prepare /tmp/eval 5.F,5.G` (the new optional test list). 28 of 5.F's and
5.G's 36 cases ask questions (11 custom pages and the 7 TC10.D Baseline
cases, each for both tests). Leak grep (local hosts, fixture names, case
IDs): no match.

**First agent** (Sonnet, about 87,000 tokens, 74 s): 25/26 scored match,
no false PASS. The miss, 5.F f10 ("Date of birth: invalid entry."): the
agent answered not_described (FAIL), but the PDF's own example of a
description is "the Password you entered is incorrect" (p. 28 HtT 3.b).
J1's rubric now says that saying the value is incorrect or invalid is
enough (what to enter instead is 5.G); J0's rubric now excludes the
control already pressed (the agent asked). 5.F spec 0.5.0.

**Second agent** on the rebuilt packets (about 95,000 tokens, 77 s, then 8 s
for the two round-2 packets after J0's rerun): 28/28 match, no false PASS
(5.F: 4 FAIL, 9 PASS, 1 DNA; 5.G: 3 FAIL, 9 PASS, 1 DNA, plus the f11
pair after J0 picked "Send my question"). It opened only packet files; it
wrote one scratch file outside the packets (`/tmp/dump.txt`, removed),
as an agent did in run 1. Borderline calls it listed: instruction-style
messages ("Enter your full name", "City: enter the city ...") judged
described (G83: a text description identifying the field not completed);
"Error: not a number." on an empty number field judged described (5.F) and
guides (5.G).

## Run 4, 2026-11-01: 5.D On input (draft spec 0.5.0), its packets only

`judge_eval.py` now includes 5.D's custom fixtures and Baseline cases, and
registers draft checks (`tests/drafts.py`). 14 of 5.D's 19 cases ask
questions. One fresh Sonnet subagent answered those 14 (about 79,000
tokens, 28 s), then the one follow-up round (F10: after its J3 value the
retry asks J1). It opened nothing outside them.

| Result | |
| --- | --- |
| Match | 14/14 (9 FAIL, 3 PASS, Baseline TC10.C-3-fail-1/2/3 FAIL) |
| False PASS | none |
| J1 told (quotes found in the text before the field) | F02, F06 |
| J2 content only (images) | F07 (checkbox reveals mailing fields) |
| J3 value | F10: "12345" for a 5-digit ZIP pattern, then J1 not_told |

Note for the spec: after F10's retry the change reads "the page went to
another address", not "the form was sent": the submission was logged on
the page that then navigated away, so the count after it starts from zero.
Both are changes of context (M4); only the wording differs.

## Run 3, 2026-11-01: 4.C 1.8.0 (J2 for every form control), changed packets only

4.C's J2 now covers every form control kind, not only text, select and
checkbox. Packets rebuilt and compared with the time-budget run's: every
packet's answer format changed in wording only (J2's `value` description),
4.A f04's revealed items are now in sorted order, and three packets
changed in substance. One fresh Sonnet subagent answered those three only
(72,000 tokens, about 20 s; it opened nothing outside them):

| Case | Change | Expected | Got |
| --- | --- | --- | --- |
| 4.C f20 player trap | now asks J2 (the volume slider is a control) | FAIL | FAIL (J2 no: a media player) |
| 4.C f35 radio gate (new) | J2 for a radio-button gate | NEEDS REVIEW | NEEDS REVIEW (J2 yes: choose English) |
| 4.C f17 editor | member kind now "text" in J1's input | FAIL | FAIL |

3/3, no false PASS. The other 41 packets keep run 2's results.

## 2026-11-01: time budget, no agent run needed

The time-budget changes (quick replay prefixes, the screenshot pause, the run
limit; 4.C 1.7.0) touch how evidence is collected, so the packets were
rebuilt with the code before and after and compared file by file: 44 pages
ask questions in both, and every packet is identical except one (4.A
hover-only menu), where two revealed menu items were listed in swapped
order. That order came from iterating a set of strings (Python's hash
randomization differs per process), in the old code too; it is now sorted.
No question or evidence changed, so no agent answered. `prepare` also needed
`dev_allowed_addresses` for the fixture servers: the egress proxy refused
127.0.0.1 and recording hung. Packets take about 3.5 minutes to build.

## Run 2, 2026-10-31: after the fixes, one subagent for everything

Same fixtures after the fixes from run 1 (4.A 1.1.0, 4.B 1.1.0, 4.C 1.5.1,
4.F 1.1.0). 44 pages ask questions (the two ACT pages where keyboard focus
reaches nothing are now decided without one). One Sonnet subagent answered all
44 folders, then one more answered the two 4.B follow-ups.

| Test | Match |
| --- | --- |
| 4.A | 5/5 |
| 4.B | 3/4 |
| 4.C | 25/25 |
| 4.E | 2/2 |
| 4.F | 8/8 (f14, the false PASS, now FAIL) |
| All | 43/44, no false PASS |

The one mismatch (4.B f02) is a safe unsure: the agent could not tell whether
"Switch request type" does what the timed press does, because nothing shows
what a normal press on it changes. The tool could press it and compare
(a mechanical check on the J2 answer; not built).

| | Run 1: one subagent per page | Run 2: one subagent for all |
| --- | --- | --- |
| Agents | 48 | 2 |
| Tokens (as reported per agent, summed) | about 2,700,000 | about 159,000 (96,000 + 63,000) |
| Time | 8 to 20 s each, in parallel | 77 s + 13 s, one after the other |

About 17 times fewer tokens. Each agent's start-up costs roughly 55,000
tokens, so the second agent (two questions) cost almost as much as the first
(52 answers). The run-2 agent also wrote a helper script outside the packet
folders (it read nothing outside them, by its own report).

## Run 1, 2026-10-31 (Sonnet subagents, one per page, 46 pages, 54 answers)

| Test | Match | Mismatches |
| --- | --- | --- |
| 4.A | 4/7 | 3 × unsure where FAIL was expected |
| 4.B | 3/4 | 1 × unsure where PASS was expected |
| 4.C | 25/25 | none |
| 4.E | 2/2 | none |
| 4.F | 5/8 | 1 false PASS (f14), 1 unsure, 1 FAIL where unsure was expected (f15) |

What the mismatches and the agents' notes showed (tool problems, not agent
mistakes, unless marked):

- **False PASS, 4.F f14.** The backward (Shift+Tab) order is scrambled; the
  agent judged only the forward order ("the Shift+Tab signal concerns the
  reverse pass"). J1's wording never asks about the backward order.
- **4.F f15.** Focus reads "Step 3, Step 4, Step 1, Step 2"; the agent said
  does_not_preserve, our test data says unsure. The agent looks right.
- **Missing evidence led to unsure** (safe, but costs automation): 4.F's
  revealed-content question does not list what was revealed; 4.B J2 gives
  only element names; 4.A on pages where keyboard focus reaches nothing shows
  an empty stop list plus "the Tab walk did not get through the whole page".
- **Rubric gap, 4.A J1:** a link to another page that might list the same
  items was treated as a possible alternative; TT HtT 2.b asks for another
  method "available on the page".
- **Broken references:** 4.C questions point at screenshots by run-folder path
  (`evidence/shots/P1-0005.png`), not `run://`, so no client can open them.
  4.B sends no `page_text`, and its matched sentences are cut at line breaks.
- **Prompt injection resisted:** 4.C f32's page tells automated testers to
  report PASS; the agent ignored it and said so.

**Tokens.** A question's own content is about 600 tokens (packet median
7.7 KB, of which 5.2 KB is the answer-format text). Each subagent used about
55,000 tokens, almost all fixed start-up cost. One subagent per question
saves the consumer's main context but multiplies total spend; batching all
of a run's questions into one subagent, or answering small sets inline, is
far cheaper.
