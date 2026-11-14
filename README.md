# Section 508 TOBI — Tester-Oriented Browser Inspector

TOBI (`tobi508` in code) is an MCP server that helps people test web pages
with the DHS Trusted Tester 5.1.3 process for Section 508. The name follows
the tradition of ANDI, SSA's Accessible Name & Description Inspector, which
TOBI runs inside the browser. TOBI is independent of DHS and SSA.

> **Not a certified Trusted Tester result.** This tool produces agent-assisted
> findings only. Its output is not a DHS Trusted Tester certified test result
> and must not be reported, cited or relied on as one. A certified Trusted
> Tester must perform any test that counts for Section 508 conformance.

**Why it exists.** Automated accessibility scanners read a page's code.
They miss failures you only find by using the page: a keyboard trap, focus
you can't see, a field whose only label disappears when you type, no way
to skip the header.

TOBI finds those failures for site owners and Trusted Testers. It
runs the hands-on parts of the DHS Trusted Tester 5.1.3 process in a real
Chrome browser, does the repetitive tabbing and comparing, and asks your AI
agent the judgment questions. Clear failures surface early, and certified
testers can spend their time on the cases that need a person.

**What you get:** PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW for each TT
test, with plain-language explanations, evidence, and a pre-SCRT file: the
same rows as DHS's SCRT report, plus where each result came from and
which rows need a person. DHS's SCRT does not open it (by design: it is
not a Trusted Tester's record); [demo/prescrt-viewer/](demo/prescrt-viewer/)
shows one beside an SCRT file.
- **Outcomes** come only from the rules specs in [specs/rules/](specs/rules/),
  one per TT test, checked against the TT 5.1.3 PDF.
- **When the tool can't decide,** it says NEEDS REVIEW. It never guesses
  PASS.

## How it works

![A developer's AI agent asks the TOBI MCP server to test a page. The server records the page once, and its rules specs decide each Trusted Tester test. When a rule asks an open question, the server's judge model answers by rubric: a sure answer goes back to the rule, an unsure one goes to a signed-in person. Results are written to a pre-SCRT file, which a Trusted Tester can certify into their own SCRT record. The results and a link to the report go back to the agent, which explains them.](docs/hackathon/diagrams/tobi-flow.png)

The diagram is the planned flow
([plan](docs/plans/2026-11-07-server-judge-pivot.md)). Today:

- **Built:** recording and replay, the rules specs and checks, the
  pre-SCRT file, and the server judge.
- **Off by default:** the server judge (`JUDGE_BACKEND=api`, one question
  type at a time in `JUDGE_TYPES`). Until a type is switched on, its
  open questions go to the calling agent, by the same rubric.
- **Not built yet:** the hosted service, the page where a signed-in
  person answers, and the export to a Trusted Tester's SCRT record.

## TT tests in scope

The table lists each implemented test's rules spec and what our tests on
real pages showed. Every other active TT 5.1.3 test comes back NEEDS
REVIEW, "This test could not be performed".

Status is from one run on 2026-11-13: round 2's 10 svs.gsfc.nasa.gov pages (frozen copies) tested again with that day's rules and the server judge answering the open questions, scored against a certified Trusted Tester's blind SCRT files (one development site, one repeat). Counts are of the 10 pages. Details and the figures beside round 2: [evaluation results](evals/README.md#gate-2026-11-13-round-2s-10-pages-again-the-server-judge-on-every-type-roadmap-step-6). Every test's limits: [Known limits, per test](docs/ROADMAP.md#known-limits-per-test).

| ID | TT test name | WCAG 2.0 | Spec | Status on real pages |
| --- | --- | --- | --- | --- |
| 2.A | 1.4.2-audio-control | 1.4.2 | [1.1.0](specs/rules/2a-audio-control.md) | 🟢 7 of 10 agree, no wrong outcome, 3 NEEDS REVIEW. Caveat: audio that does not play from the recording is left for a person |
| 2.B | 2.2.2-blinking-moving-scrolling | 2.2.2 | [1.3.0](specs/rules/2b-blinking-moving-scrolling.md) | 🟢 No wrong outcome; 1 of 10 agree, 9 NEEDS REVIEW. Caveat: more than 30 images is NEEDS REVIEW (guard CN) |
| 2.C | 2.2.2-auto-updating | 2.2.2 | [1.0.0](specs/rules/2c-auto-updating.md) | 🟢 No wrong outcome; NEEDS REVIEW on all 10. Caveat: moving content not settled in 6.5 s is left for a person |
| 2.D | 4.1.2-change-notify-auto | 4.1.2 | [1.1.0](specs/rules/2d-change-notify-auto.md) | 🟢 No wrong outcome; NEEDS REVIEW on all 10. Caveat: as 2.C |
| 3.A | 2.3.1-flashing | 2.3.1 | [1.2.1](specs/rules/3a-flashing.md) | 🟢 No wrong PASS or Does Not Apply; 3 of 10 agree, 1 Not Tested where the key says Does Not Apply, 6 NEEDS REVIEW. Caveat: more than 30 images is NEEDS REVIEW (guard CN) |
| 4.A | 2.1.1-keyboard-access | 2.1.1 | [1.10.0](specs/rules/4a-keyboard-access.md) | ⚠️ 2 agree, 1 FAIL the key passes (a judge answer), 7 NEEDS REVIEW; round 2's PASS on CILab now fails with the key. Caveat: often undecided with embedded players and frames |
| 4.B | 2.1.1-no-keystroke-timing | 2.1.1 | [1.3.0](specs/rules/4b-no-keystroke-timing.md) | 🟢 9 of 10 agree, no wrong outcome, 1 NEEDS REVIEW |
| 4.C | 2.1.2-no-keyboard-trap | 2.1.2 | [1.13.1](specs/rules/4c-no-keyboard-trap.md) | ⚠️ No wrong PASS (round 2's on 5340 is now NEEDS REVIEW); 2 agree, 8 NEEDS REVIEW. Caveat: menus or sections that open leave it for a person |
| 4.D | 2.4.7-focus-visible | 2.4.7 | [1.8.0](specs/rules/4d-focus-visible.md) | ⚠️ 1 agree, 2 FAILs the key passes (as in round 2), 7 NEEDS REVIEW. Caveat: the judge is often unsure on small focus pictures |
| 4.E | 3.2.1-on-focus | 3.2.1 | [1.4.0](specs/rules/4e-on-focus.md) | 🟢 No wrong outcome; 2 agree, 8 NEEDS REVIEW. Caveat: menus or sections that open leave it for a person |
| 4.F | 2.4.3-focus-order-meaning | 2.4.3 | [1.8.0](specs/rules/4f-focus-order-meaning.md) | ⚠️ 1 agree, 2 FAILs the key passes (judge answers; round 2: 6), 7 NEEDS REVIEW. Caveat: the judge is often unsure |
| 5.A | 3.3.2-label-provided | 3.3.2 | [1.9.0](specs/rules/5a-label-provided.md) | 🟢 No wrong outcome (round 2: 8 FAILs the key passes); 3 agree, 7 NEEDS REVIEW. Caveat: fields inside frames are not checked yet |
| 5.B | 2.4.6-label-descriptive | 2.4.6 | [1.6.0](specs/rules/5b-label-descriptive.md) | 🟢 No wrong outcome (round 2: 5 wrong); 3 agree, 7 NEEDS REVIEW. Caveat: the judge is often unsure |
| 5.C | 1.3.1-programmatic-label | 1.3.1, 4.1.2 | [1.9.0](specs/rules/5c-programmatic-label.md) | 🟢 No wrong outcome (round 2: 3 FAILs the key passes); 5 agree, 5 NEEDS REVIEW. Caveat: fields inside frames are not checked yet (3 of the key's FAILs are there) |
| 5.D | 3.2.2-on-input | 3.2.2 | [1.6.0](specs/rules/5d-on-input.md) | 🟢 No wrong PASS (round 2's on 5340 is now NEEDS REVIEW); 3 agree, 7 NEEDS REVIEW. Caveat: menus or sections that open leave it for a person |
| 5.F | 3.3.1-error-identification | 3.3.1 | [1.7.0](specs/rules/5f-error-identification.md) | 🟢 No wrong outcome; 3 agree, 7 NEEDS REVIEW. Caveat: fields inside frames are not checked yet |
| 5.G | 3.3.3-error-suggestion | 3.3.3 | [1.5.0](specs/rules/5g-error-suggestion.md) | 🟢 No wrong outcome; 3 agree, 7 NEEDS REVIEW. Caveat: as 5.F |
| 5.H | 3.3.4-error-prevention | 3.3.4 | [1.5.0](specs/rules/5h-error-prevention.md) | 🟢 No wrong outcome; 4 agree, 6 NEEDS REVIEW. Caveat: a form that is only a button is NEEDS REVIEW (guard CN) |
| 9.A | 2.4.1-bypass-function | 2.4.1 | [1.6.0](specs/rules/9a-bypass.md) | 🟢 10 of 10 agree (FAIL; round 2: 2 Does Not Apply where the key fails). Caveat: a page with more than 5,000 items is left for a person |
| 9.B | 3.2.3-consistent-navigation | 3.2.3 | [1.5.0](specs/rules/9b-consistent-navigation.md) | 🟢 9 of 10 agree; CILab NEEDS REVIEW (1.5.0; it was Does Not Apply where the key passes, as in round 2). Caveat: as 9.A |
| 9.C | 3.2.4-consistent-identification | 3.2.4 | [1.8.0](specs/rules/9c-consistent-identification.md) | ⚠️ 4 of 10 agree, no wrong PASS or FAIL (round 2: 2 FAILs the key passes); 6 NEEDS REVIEW: CILab (1.8.0; it was Does Not Apply where the key passes) and 5 the judge was unsure on. Caveat: as 9.A |
| 19.A | 2.4.5-multiple-ways | 2.4.5 | [1.8.0](specs/rules/19a-multiple-ways.md) | ⚠️ 4 of 10 agree; 6 FAILs the key passes, all from a site search whose results page's scripts did not load in the test container: since 1.7.0 that is NEEDS REVIEW (checked on 14194). Caveat: a search page that cannot load its own scripts is left for a person |

## Known wrong outcomes

The status above is what real pages showed. A code review on 2026-11-11
then wrote small test pages aimed at each test's blind spots and found
these wrong PASS and Does Not Apply results. Each was reproduced by a
run unless marked "(read)", and each row was run again on 2026-11-13,
after the fixes of 2026-11-12 and 13: three cases were fixed and left
the table. Eleven more were fixed on 2026-11-13 (a keyboard trap, an `alert()`
or download, a `#main` address, non-Latin labels, a multi-step form, a near
copy of the tested page, a `type="button"` form, a `mousedown`-only button, a
page that shifts, a script that moves focus off, unnamed pairs) and left it; the
rest still give the outcome shown. Until they are fixed, read a PASS or a Does
Not Apply as "in what the tool looked at". The full list, with the page
for each, is [the code review](docs/reviews/2026-11-11-code-review.md);
the fixes are planned in
[the plan after the review](docs/plans/2026-11-12-coverage-second-look-thin-agent.md).
A fix removes its line here in the same commit.

| Test | Gives | On a page with |
| --- | --- | --- |
| 2.A | Does Not Apply | audio that a script starts after about 4.5 s (audio that starts by itself at 3.5 s is now found) |
| 2.B | Does Not Apply | text that blinks by `visibility`; a blink or jump about 2.5 times a second; motion that fills most of the screen; motion that starts after 6.5 s |
| 2.C | Does Not Apply | a counter that starts when the second of several elements scrolls into view |
| 3.A | Does Not Apply | flashing below the first screen; flashing that starts after 6.5 s |
| 4.A | PASS | a mouse-only control inside a web component |
| 4.B | PASS | timing instructions not in English, or worded "press Enter twice" (read); timing instructions inside a web component (found by the grid of hard pages, 2026-11-13) |
| 4.E | PASS | elements after a keyboard trap (grid) |
| 4.A, 4.C-4.F | PASS | a page whose only form opens from a plain button, for the controls inside it (grid; 5.A-5.H say NEEDS REVIEW) |
| 5.A | PASS | a label whose words are hidden (a screen-reader-only span, `text-indent`) |
| 5.F, 5.G | Does Not Apply | an error shown in a web component or as a red border on a wrapper |
| 5.H | Does Not Apply | a payment form not in English |
| 19.A | FAIL | a site header built as a web component (9.A-9.C now say NEEDS REVIEW; 19.A waits for part D) |

## Tools

| Tool | What it does | Main inputs |
| --- | --- | --- |
| `tobi_run_tt_tests` | Tests one page. It records the page once, runs the chosen TT tests on the recording, and returns findings, open questions for your agent, and links to the full report and pre-SCRT file. | `url` (`.gov` and `.mil` by default); `tests` (default: all implemented); `other_pages` (1-5 pages of the same site, for 9.A-9.C and 19.A); `no_time_limit` |
| `tobi_answer_questions` | Records answers to the open questions and decides again by the spec. Every answer sent here is recorded as the calling agent's; a person's answer, which overrides it, is to come from TOBI's own page. | `run_id`; `answers` (one per question) |
| `tobi_run_status` | Waits for a run that was still going when its call returned, and gives its result. Without `job_id`: what is left across the session's runs (open questions, follow-up calls, runs still going); with `finish=true` it also makes the follow-up calls the server may make itself. | `job_id` (optional); `finish` |
| `tobi_explain` | Explains tests in plain language: what a test checks, or, with a `run_id`, what that run found and why (full summaries, the reasoning, the places on the page, what can still change a result, and the W3C links for fixing it). Results carry one line per finding; this holds the detail. | `about` (test IDs, a WCAG criterion or words); `run_id` |
| `tobi_read_report` | Reads an SCRT or pre-SCRT file: what failed and what still needs a person. With `compare_to`, it lists every test whose result differs between two files (for example, before and after a fix). | `content`; `compare_to` |

**Also:**
- **Resources:** `run://{run_id}/...` (a run's files, kept 24 hours) and
  `tt://5.1.3/...` (the TT text).
- **Prompt:** `explain` (a test or a result in plain language; the same
  material as `tobi_explain`, as a command for the user).

## How long it takes

- **One run:** by default as long as the page needs, up to 30 min
  (`MAX_RUN_S`); a large page can take several minutes, and each
  still-running result says what the run is doing and for how long. With
  `no_time_limit=false` a run is held to 10 min (`RUN_LIMIT_S`, 600 s),
  plus 20 s for each other page, plus 45 s when something on the page
  keeps changing by itself (a ticker, a carousel), and a page too large
  for that is refused. On www.nasa.gov, runs with 3 other pages took 2-3
  minutes. Tests not finished in time come back NEEDS REVIEW, with the
  reason.
- **One test:** each test also has its own time for collecting its
  evidence: its budget (60 s for most, up to 10 min for 5.D; provisional,
  about twice the longest seen on round 2's pages; setting
  `TEST_BUDGETS_S`) or half of what is left of the run, whichever is
  smaller. A test that runs out of its time is NEEDS REVIEW ("ran out of
  its time") and the tests after it still run, cheapest first. The report
  lists each test's time (`test_times`). Round 2's ten pages took 17 s to
  15.5 min each with every test (66 min in all; 2026-11-13, judge off);
  the longest single tests were 5.D on a page with 98 form fields (8 min)
  and 4.F on a long page (4.5 min).
- **One call:** at most 45 s (`CALL_WAIT_S`), under common MCP client
  timeouts. A run not done by then goes on in the server: the result says
  `"status": "running"` with a `job_id`, and `tobi_run_status` waits for it
  again until `"status": "done"`. So you no longer need to raise your
  client's tool timeout (Claude Code's is 60 s, `MCP_TOOL_TIMEOUT`), and
  Claude Code's move of calls longer than 120 s to the background
  (`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`) no longer applies.
- **Large pages:** a page with too many stops to Tab through is refused at
  once; one with more than 40 form fields is tested without 5.D, and 5.D's
  finding gives the call that runs it. Call again with `no_time_limit:
  true` and expect 15-20 minutes of `tobi_run_status` calls.
- **Answering:** under a second, unless the server has to press a key in
  the recorded page to check an answer.
- **Batches:** the server tests 2 pages at a time (`MAX_CONCURRENT_RUNS`);
  more wait in a queue, and a run's time limit starts only when it leaves
  the queue. Each run gets its own browser, and a second, headless one
  that watches the page for Test 2. On a 4-CPU machine, 3 at once ran
  normally and 12 at once timed out (measured before the second browser).

## Use it

**Setup (Windows, Git Bash).** Run natively on Windows, not in WSL2, so
the browser can be shown. You need [uv](https://docs.astral.sh/uv/) and
Google Chrome.

```bash
cp .env.example .env
uv sync --group dev
TEST_BROWSER_CHANNEL=chrome TEST_HEADED=1 uv run pytest -v   # checks it in real Chrome
```

While it runs, keep the screen unlocked and don't click in the test
windows ([what the first Windows runs found](docs/solutions/windows-chrome-results.md)).

**Connect to Claude Code.** Add to `.mcp.json` in your project:

```json
{
  "mcpServers": {
    "tobi508": {
      "command": "uv",
      "args": ["--directory", "C:/path/to/your/clone", "run", "tobi508"]
    }
  }
}
```

**Examples.** Ask in plain words, and your agent makes calls like these.
`tests/test_readme.py` checks each one against the tool's schema and runs
the last pair end to end.

"Check https://www.section508.gov/ for keyboard, focus and form problems":

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "https://www.section508.gov/"}}
```

"Also compare it with two other pages of the site" (for 9.A-9.C and 19.A):

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "https://www.section508.gov/", "other_pages": ["https://www.section508.gov/manage/", "https://www.section508.gov/test/"]}}
```

"Is there a keyboard trap, and is focus visible?":

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "https://www.section508.gov/", "tests": ["4.C", "4.D"]}}
```

A local page and its open question. With `DEV_MODE=true`, this fixture's
three links pass focus among themselves forever:

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "file:///ABSOLUTE/PATH/TO/CLONE/tests/fixtures/4c/f06-script-loop.html", "tests": ["4.C"]}}
```

4.C comes back NEEDS REVIEW and asks whether the page names a key that
gets out. The agent answers from the page text:

<!-- example -->
```json
{"tool": "tobi_answer_questions", "arguments": {"run_id": "<run_id from the result>", "answers": [{"question_id": "4.C-i1-J1", "decided_by": "model", "rationale": "The page text names no key that moves focus out of the three looping links.", "seen": "three links in a row and no instructions", "j1": {"documented": "no"}}]}}
```

4.C is now FAIL: "Keyboard focus gets trapped on this page…".

**Example output** from a real run on 2026-11-04 (NASA's accounts
receivable form, the 17 tests built then, 10 questions answered):
- [report.json](evals/judging/round1-answers/results/arm-a/runs/20261104T200634Z-d02d2f/report.json):
  findings, questions and answers, and every version used;
- [pre-scrt.json](evals/judging/round1-answers/results/arm-a/runs/20261104T200634Z-d02d2f/pre-scrt.json):
  SCRT's 61 rows, screenshots inline, rows for a person flagged.

Save the report in your repository: a run's files expire after 24 hours.

## Configuration and safety

**Settings** come from the environment or `.env` (`.env.example`):
- `ALLOWED_DOMAINS`, `NO_TIME_LIMIT_DEFAULT` (default true), `MAX_RUN_S`,
  `RUN_LIMIT_S` and `OTHER_PAGE_S`;
- `CALL_WAIT_S` and `MAX_CONCURRENT_RUNS`;
- `PAGE_CACHE_S` (default 1800): how long an other page's recording, and
  its reads, are reused by later calls of the same server session;
- `BROWSER_CHANNEL` and `HEADLESS`;
- `DEV_MODE` (allows `file://` pages);
- `JUDGE_BACKEND` (default `client`: the calling agent answers open
  questions; `api`: the server's own model answers the question types
  in `JUDGE_TYPES`), with `JUDGE_ROUTE` and `JUDGE_MODEL`;
- `UPSTREAM_PROXY`, for containers that re-sign TLS.

**Safety:**
- Every navigation and redirect is checked against the allowlist.
- Chrome connects through a local proxy that refuses private and
  cloud-metadata addresses.
- ANDI is served from a vendored copy.
- Page content is treated as data: it never chooses a URL, a tool or an
  outcome.
- Every report records all versions.

Details: [docs/hackathon/evaluation.md](docs/hackathon/evaluation.md).

**Known limits:**
- A recording freezes network responses, not randomness or time.
- The test browser bypasses the page's Content-Security-Policy so that ANDI
  can run (`BYPASS_CSP`, on by default; the report records it).
- CI runs headless Chromium; headed Chrome on Windows is checked by hand.

## Contribute

- **Testers:** certified Trusted Testers can run their own judging round
  and contribute it: [docs/how-to/run-a-judging-round.md](docs/how-to/run-a-judging-round.md).
- **Developers:** read [CLAUDE.md](CLAUDE.md), then [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT (see [LICENSE](LICENSE)), from the GSA-TTS
[mcp-hackathon-template](https://github.com/GSA-TTS/mcp-hackathon-template).
Third-party software (see [NOTICE](NOTICE)):

- **ANDI 29.2.2**, Copyright Social Security Administration, Apache License 2.0
  ([third_party/andi/NOTICE](third_party/andi/NOTICE),
  [LICENSE.md](third_party/andi/LICENSE.md)). Unmodified copy; use does not
  imply SSA endorsement.
- **jQuery 3.7.1**, Copyright OpenJS Foundation and other contributors, MIT
  ([third_party/jquery/LICENSE.txt](third_party/jquery/LICENSE.txt)).
- **SCRT 5.2.0**, Copyright Department of Homeland Security, MIT
  ([third_party/scrt/LICENSE](third_party/scrt/LICENSE)). Its test rows
  are read as a template; its pages are used in tests, and
  [demo/prescrt-viewer/](demo/prescrt-viewer/) reuses its stylesheet.
  Use does not imply DHS endorsement.
