# Section 508 TOBI — Tester-Oriented Browser Inspector

TOBI (`tobi508` in code) is an MCP server that helps people test web pages with the DHS Trusted Tester 5.1.3 process for Section 508. The name follows the tradition of ANDI, SSA's Accessible Name & Description Inspector, which TOBI runs inside the browser. TOBI is independent of DHS and SSA.

> **Not a certified Trusted Tester result.** This tool produces agent-assisted findings only. Its output is not a DHS Trusted Tester certified test result and must not be reported, cited or relied on as one. A certified Trusted Tester must perform any test that counts for Section 508 conformance.

**Why it exists.** Automated accessibility scanners read a page's code. They miss failures you only find by using the page: a keyboard trap, focus you can't see, a field whose only label disappears when you type, no way to skip the header.

TOBI finds those failures for site owners and Trusted Testers. It runs the hands-on parts of the DHS Trusted Tester 5.1.3 process in a real Chrome browser, does the repetitive tabbing and comparing, and asks your AI agent the judgment questions. Clear failures surface early, and certified testers can spend their time on the cases that need a person.

**What you get:** PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW for each TT test, with plain-language explanations, evidence, and a pre-SCRT file: the same rows as DHS's SCRT report, plus where each result came from and which rows need a person. DHS's SCRT does not open it (by design: it is not a Trusted Tester's record). To read one, open `/viewer` on a hosted TOBI server, or download [viewer.html](demo/prescrt-viewer/viewer.html) and open it in a browser. Either way it reads only the file you pick, in your own browser, and sends nothing anywhere; a second file can be loaded beside it ([how to use it](demo/prescrt-viewer/README.md)).
- **Outcomes** come only from the rules specs in [specs/rules/](specs/rules/), one per TT test, checked against the TT 5.1.3 PDF.
- **When the tool can't decide,** it says NEEDS REVIEW: a person should look at that row, usually the largest group in a report. It never guesses PASS. (3.A can say NOT TESTED, as the TT text requires, when it finds flashing.)

## How it works

![A developer's AI agent asks the TOBI MCP server to test a page. The server records the page once, and its rules specs decide each Trusted Tester test. When a rule asks an open question, the server's judge model answers by rubric: a sure answer goes back to the rule, an unsure one goes to a signed-in person. Results are written to a pre-SCRT file, which a Trusted Tester can certify into their own SCRT record. The results and a link to the report go back to the agent, which explains them.](docs/diagrams/tobi-flow.png)

The diagram is the planned flow ([plan](docs/plans/2026-11-07-server-judge-pivot.md)). Today:

- **Built:** recording and replay, the rules specs and checks, the pre-SCRT file, the server judge, and hosted sign-in with per-user runs (running on a VAST dev environment; not yet a finished service).
- **On whenever it has a model:** the server judge answers every test's open questions with a pinned model and prompt once a Messages API gateway's URL and key are set (`JUDGE_BASE_URL`, `JUDGE_API_KEY`; Abby, 2026-11-18). Without them, open questions go to the calling agent, by the same rubric.
- **Not built yet:** the page where a signed-in person answers, and the export to a Trusted Tester's SCRT record.

## TT tests in scope

TT 5.1.3 has 61 active tests. TOBI performs 22 of them, listed below with their rules spec and how each did on our evaluation pages. The other 39 come back NEEDS REVIEW, "This test could not be performed".

Status describes 29 evaluation pages on three NASA sites, scored against a Trusted Tester's blind SCRT files. It says nothing about any other page.
- ✅ **green:** agrees with the tester.
- ⚠️ **yellow:** often fails pages the tester passes, or leaves most cells for a person.
- ❌ **red:** passed a page the tester failed, or was wrong more often than right.

Counts and the run each comes from: [evals/STATUS.md](evals/STATUS.md). What each test can't do: [KNOWN-LIMITS.md](docs/KNOWN-LIMITS.md).

<!-- status-table:start -->
| ID | TT test name | Spec | Status |
| --- | --- | --- | --- |
| 2.A | 1.4.2-audio-control | [1.2.0](specs/rules/2a-audio-control.md) | ✅ agrees with a tester |
| 2.B | 2.2.2-blinking-moving-scrolling | [1.5.0](specs/rules/2b-blinking-moving-scrolling.md) | ✅ agrees with a tester |
| 2.C | 2.2.2-auto-updating | [1.2.0](specs/rules/2c-auto-updating.md) | ✅ agrees with a tester |
| 2.D | 4.1.2-change-notify-auto | [1.3.0](specs/rules/2d-change-notify-auto.md) | ✅ agrees with a tester |
| 3.A | 2.3.1-flashing | [1.4.0](specs/rules/3a-flashing.md) | ✅ agrees with a tester |
| 4.A | 2.1.1-keyboard-access | [1.14.0](specs/rules/4a-keyboard-access.md) | ⚠️ often fails pages a tester passes |
| 4.B | 2.1.1-no-keystroke-timing | [1.4.0](specs/rules/4b-no-keystroke-timing.md) | ✅ agrees with a tester |
| 4.C | 2.1.2-no-keyboard-trap | [1.17.0](specs/rules/4c-no-keyboard-trap.md) | ✅ agrees with a tester |
| 4.D | 2.4.7-focus-visible | [1.10.0](specs/rules/4d-focus-visible.md) | ⚠️ often fails pages a tester passes |
| 4.E | 3.2.1-on-focus | [1.8.0](specs/rules/4e-on-focus.md) | ✅ agrees with a tester |
| 4.F | 2.4.3-focus-order-meaning | [1.11.0](specs/rules/4f-focus-order-meaning.md) | ✅ agrees with a tester |
| 5.A | 3.3.2-label-provided | [1.15.0](specs/rules/5a-label-provided.md) | ✅ agrees with a tester |
| 5.B | 2.4.6-label-descriptive | [1.12.0](specs/rules/5b-label-descriptive.md) | ⚠️ often fails pages a tester passes |
| 5.C | 1.3.1-programmatic-label | [1.14.0](specs/rules/5c-programmatic-label.md) | ✅ agrees with a tester |
| 5.D | 3.2.2-on-input | [1.12.0](specs/rules/5d-on-input.md) | ⚠️ often fails pages a tester passes |
| 5.F | 3.3.1-error-identification | [1.16.0](specs/rules/5f-error-identification.md) | ⚠️ mostly left for a person |
| 5.G | 3.3.3-error-suggestion | [1.12.0](specs/rules/5g-error-suggestion.md) | ⚠️ mostly left for a person |
| 5.H | 3.3.4-error-prevention | [1.10.0](specs/rules/5h-error-prevention.md) | ✅ agrees with a tester |
| 9.A | 2.4.1-bypass-function | [1.7.0](specs/rules/9a-bypass.md) | ✅ agrees with a tester |
| 9.B | 3.2.3-consistent-navigation | [1.7.0](specs/rules/9b-consistent-navigation.md) | ✅ agrees with a tester |
| 9.C | 3.2.4-consistent-identification | [1.10.0](specs/rules/9c-consistent-identification.md) | ✅ agrees with a tester |
| 19.A | 2.4.5-multiple-ways | [1.15.0](specs/rules/19a-multiple-ways.md) | ✅ agrees with a tester |

<!-- status-table:end -->

## Known wrong outcomes

A code review on 2026-11-11 built small pages aimed at each test's blind spots and found wrong PASS and DOES NOT APPLY results. These are the ones still unfixed (checked against the code on 2026-11-17). Each was reproduced by a run unless marked "(read)". Until they are fixed, read a PASS or DOES NOT APPLY as "in what the tool looked at".

The pages are in [the code review](docs/reviews/2026-11-11-code-review.md); fixes are planned in [the plan after the review](docs/plans/2026-11-12-coverage-second-look-thin-agent.md) and, for the rows naming round 3 (the blind round on science.data.nasa.gov, 2026-11-16), [the plan after round 3](docs/plans/2026-11-16-after-round3.md). A fix removes its row in the same commit.

| Test | Gives | On a page with |
| --- | --- | --- |
| 2.A | Does Not Apply | audio that a script starts after about 4.5 s (audio that starts by itself at 3.5 s is now found) |
| 2.B | Does Not Apply | text that blinks by `visibility`; a blink or jump about 2.5 times a second; motion that fills most of the screen; motion that starts after 6.5 s |
| 2.C | Does Not Apply | a counter that starts when the second of several elements scrolls into view |
| 3.A | Does Not Apply | flashing below the first screen; flashing that starts after 6.5 s |
| 4.B | PASS | timing instructions not in English, or worded "press Enter twice" (read) |
| 4.A, 4.C-4.F | PASS | a page whose only form opens from a plain button, for the controls inside it (grid; 5.A-5.H say NEEDS REVIEW) |
| 5.H | Does Not Apply | a payment form not in English |
| 9.C | PASS or Does Not Apply | controls in the pages' own content that do the same thing under different names on different pages, unless they share an `id` (read) |
| 4.A, 4.C, 4.F, 5.A-5.D, 5.F-5.H | PASS or Does Not Apply | a page that draws its controls more than 10 s after it loads, and more than doubles them after a walk that took less than 3 s: every load waits up to 10 s for the page to draw (step 23), and the walk counts the page again 3 s after its last load (step 22) (read) |
| 4.D | PASS | a large linked image whose focus shows only a faint mark: about 50 changed pixels pass, whatever the element's size (round 3's blog page, held at NEEDS REVIEW there only by guard RC) (read) |

## Tools

| Tool | What it does | Main inputs |
| --- | --- | --- |
| `tobi_run_tt_tests` | Tests one page. It records the page once, runs the chosen TT tests on the recording, and returns findings, open questions for your agent, and links to the full report and pre-SCRT file. | `url` (`.gov` and `.mil` by default); `tests` (default: all implemented); `other_pages` (1-5 pages of the same site, for 9.A-9.C and 19.A); `no_time_limit` |
| `tobi_answer_questions` | Records answers to the open questions and decides again by the spec. Every answer sent here is recorded as the calling agent's; a person's answer, which overrides it, is to come from TOBI's own page. | `run_id`; `answers` (one per question) |
| `tobi_run_status` | Waits for a run that was still going when its call returned, and gives its result. Without `job_id`: what is left across the session's runs (open questions, follow-up calls, runs still going); with `finish=true` it also makes the follow-up calls the server may make itself. | `job_id` (optional); `finish` |
| `tobi_explain` | Explains tests in plain language: what a test checks, or, with a `run_id`, what that run found and why (full summaries, the reasoning, the places on the page, what can still change a result, and the W3C links for fixing it). Results carry one line per finding; this holds the detail. | `about` (test IDs, a WCAG criterion or words); `run_id` |
| `tobi_read_report` | Reads an SCRT or pre-SCRT file: what failed and what still needs a person. With `compare_to`, it lists every test whose result differs between two files (for example, before and after a fix). | `content`; `compare_to` |

**Also:**
- **Resources:** `run://{run_id}/...` (a run's files, kept 24 hours) and `tt://5.1.3/...` (the TT text).
- **Prompt:** `explain` (a test or a result in plain language; the same material as `tobi_explain`, as a command for the user).

## How long it takes

- **A run takes minutes, not seconds.** By default it takes as long as the page needs, up to 30 minutes. Each still-running result says what the run is doing.
- **A call returns within 45 s.** If the run isn't done, the result says `"status": "running"` with a `job_id`, and `tobi_run_status` waits for it. You don't need to raise your client's timeout.
- **Anything that doesn't finish in time is NEEDS REVIEW,** with the reason, and the other tests still run.
- **Very large pages** are refused, or tested without 5.D (which reads every form field); the finding says how to run it.

Time limits, per-test budgets, measured timings and running several pages at once: [how long a run takes](docs/how-to/how-long-a-run-takes.md).

## Use it

**[Get started](docs/how-to/get-started.md)** covers Windows, macOS and Linux, from a clone or from the container image, and connecting Claude Code. No sign-in is needed to run it yourself. The short version, from a clone with [uv](https://docs.astral.sh/uv/) and Google Chrome:

```bash
cp .env.example .env && uv sync
claude mcp add tobi508 -- uv --directory /full/path/to/tobi508 run tobi508
```

Or with only Docker:

```bash
claude mcp add tobi508 -- docker run -i --rm -e MCP_TRANSPORT=stdio ghcr.io/abbybowman/tobi508:latest
```

**Examples.** Ask in plain words, and your agent makes calls like these. `tests/test_readme.py` checks each one against the tool's schema.

"Run the Trusted Tester tests TOBI can on https://www.nasa.gov/mission/artemis-iii/":

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "https://www.nasa.gov/mission/artemis-iii/"}}
```

"Compare it with two other pages of the site" (for 9.A-9.C and 19.A):

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "https://www.nasa.gov/mission/artemis-iii/", "other_pages": ["https://www.nasa.gov/careers/", "https://www.nasa.gov/gallery/ksc-history/"]}}
```

"Is there a keyboard trap, and is focus visible?":

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "https://www.nasa.gov/mission/artemis-iii/", "tests": ["4.C", "4.D"]}}
```

"Explain what failed, what's left for a person, and what TOBI can't check here":

<!-- example -->
```json
{"tool": "tobi_explain", "arguments": {"run_id": "<run_id from the result>"}}
```

The run takes minutes: until it is done, each result says `"status": "running"` and what it is doing (`"progress": "Walking the page with Tab and Shift+Tab (45 s so far)"`), and the agent waits with `tobi_run_status`.

<details>
<summary>An open question, end to end, on a local test page (for contributors)</summary>

With `DEV_MODE=true`, this fixture's three links pass focus among themselves forever (the test suite runs this pair):

<!-- example -->
```json
{"tool": "tobi_run_tt_tests", "arguments": {"url": "file:///ABSOLUTE/PATH/TO/CLONE/tests/fixtures/4c/f06-script-loop.html", "tests": ["4.C"]}}
```

4.C comes back NEEDS REVIEW and asks whether the page names a key that gets out. The agent answers from the page text:

<!-- example -->
```json
{"tool": "tobi_answer_questions", "arguments": {"run_id": "<run_id from the result>", "answers": [{"question_id": "4.C-i1-J1", "decided_by": "model", "rationale": "The page text names no key that moves focus out of the three looping links.", "seen": "three links in a row and no instructions", "j1": {"documented": "no"}}]}}
```

4.C is now FAIL: "Keyboard focus gets trapped on this page…".

</details>

**Example output.** The second example above, run live on 2026-11-18 (about 10.5 minutes), before the agent answered its open questions. One line per finding; `tobi_explain` gives the rest:

```text
5.A FAIL   "Search" (text field)'s only label is the gray example text inside it, which
           disappears as soon as someone starts typing. Add a label that stays visible.
           To find it, press Tab 2 times.
9.A FAIL   This page starts with content repeated on the other pages you gave (for
           example "Explore"), and we found no keyboard way to skip past it. [...] Add a
           "Skip to main content" link as the first thing on the page.
4.B PASS   Nothing on this page asks you to press keys at a certain speed, hold a key
           down, or press a key several times quickly.
9.B PASS   The navigation this page shares with the other pages you gave appears in the
           same order on each of them.
19.A PASS  This page can be found in more than one way: links from other pages and the
           site search.
2.A, 5.H   DOES NOT APPLY
4.D        NEEDS REVIEW: 2 questions about it are still open. (The "Hide player
           controls" button's focus ring is near black on black: a careful agent
           answers "unsure", and it stays for a person.)
...        NEEDS REVIEW for the other 14 built tests, and "This test could not be
           performed" for the 39 not built.
```

A certified Trusted Tester's blind SCRT file for this page (2026-11-02) fails the same two. These are agent-assisted findings, not a certified Trusted Tester result, and www.nasa.gov is one of our development sites.

Files from a run, from round 3's blind evaluation (the home page of science.data.nasa.gov, 2026-11-16, the 22 built tests):
- [pre-scrt.json](evals/judging/round3/results/p01/pre-scrt.json): the SCRT rows, with rows for a person flagged. Download it and open it in the [viewer](demo/prescrt-viewer/viewer.html) to read it as a table.
- [report.json](evals/judging/round3/results/p01/report.json): findings, questions and answers, and every version used.

Save your own reports in your repository: a run's files expire after 24 hours.

## Configuration and safety

**Settings** come from the environment or `.env`. `.env.example` lists them all with comments. The ones you are most likely to change:
- `ALLOWED_DOMAINS`: the pages TOBI may test (default `.gov` and `.mil`);
- `DEV_MODE=true`: also allows `file://` pages;
- `JUDGE_BASE_URL` and `JUDGE_API_KEY`: a Messages API gateway (such as Luna); with both set, the server's own model answers every test's open questions (`JUDGE_TYPES`, default `all`). `JUDGE_BACKEND=client` sends them to your agent instead.

**Safety:**
- Every navigation and redirect is checked against the allowlist.
- Chrome connects through a local proxy that refuses private and cloud-metadata addresses.
- ANDI is served from a vendored copy.
- Page content is treated as data: it never chooses a URL, a tool or an outcome.
- Every report records all versions.

Details: [evals/README.md](evals/README.md). What TOBI can't do yet, test by test (and in general, such as replays not freezing randomness or time): [KNOWN-LIMITS.md](docs/KNOWN-LIMITS.md).

## Contribute

- **Testers:** certified Trusted Testers can run their own judging round and contribute it: [docs/how-to/run-a-judging-round.md](docs/how-to/run-a-judging-round.md).
- **Developers:** set up with [Get started](docs/how-to/get-started.md), then read [CLAUDE.md](CLAUDE.md) and [docs/ROADMAP.md](docs/ROADMAP.md). Run the tests with `uv sync --group dev`, then `uv run pytest`. On Windows, `TEST_BROWSER_CHANNEL=chrome TEST_HEADED=1` checks it in real Chrome; run natively, not in WSL2, keep the screen unlocked and don't click in the test windows ([what the first Windows runs found](docs/solutions/windows-chrome-results.md)).

## License

MIT (see [LICENSE](LICENSE)), from the GSA-TTS [mcp-hackathon-template](https://github.com/GSA-TTS/mcp-hackathon-template). Third-party software (see [NOTICE](NOTICE)):

- **ANDI 29.2.2**, Copyright Social Security Administration, Apache License 2.0 ([third_party/andi/NOTICE](third_party/andi/NOTICE), [LICENSE.md](third_party/andi/LICENSE.md)). Unmodified copy; use does not imply SSA endorsement.
- **jQuery 3.7.1**, Copyright OpenJS Foundation and other contributors, MIT ([third_party/jquery/LICENSE.txt](third_party/jquery/LICENSE.txt)).
- **SCRT 5.2.0**, Copyright Department of Homeland Security, MIT ([third_party/scrt/LICENSE](third_party/scrt/LICENSE)). Its test rows are read as a template; its pages are used in tests, and [demo/prescrt-viewer/](demo/prescrt-viewer/) reuses its stylesheet. Use does not imply DHS endorsement.
