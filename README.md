# Section 508 TOBI — Tester-Oriented Browser Inspector

TOBI (`tobi508` in code) is an MCP server that runs the DHS Trusted Tester 5.1.3 process for Section 508 on a web page, in a real Chrome browser, and reports what it finds by Trusted Tester test ID. It is named after ANDI, SSA's Accessible Name & Description Inspector, which it runs inside the browser. TOBI is independent of DHS and SSA.

> **Not a certified Trusted Tester result.** TOBI produces agent-assisted findings only. They must not be reported, cited or relied on as a DHS Trusted Tester result. A certified Trusted Tester must perform any test that counts for Section 508 conformance.

**Why it exists.** Automated scanners read a page's code; they never press a key. They miss the failures you only find by using the page: a keyboard trap, focus you can't see, a label that vanishes when you type, no way to skip the header. The Trusted Tester process finds them, step by step, and there are too few certified testers to run it on every page. TOBI does the repetitive tabbing, typing and comparing, decides what the procedure decides mechanically, and leaves the cases that need a person to a person.

**What you get** for each of the 22 Trusted Tester tests it performs: PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW, a plain-language explanation with evidence, and a pre-SCRT file with the same rows as DHS's SCRT report, marked as not certified, saying where each result came from. Open it in the [viewer](demo/prescrt-viewer/viewer.html), which reads the file in your own browser and sends nothing anywhere ([how to use it](demo/prescrt-viewer/README.md)).

## How it works

![How TOBI tests a page. Solid lines are built; dashed are planned. A developer's AI agent asks the TOBI MCP server to test a page. The server records the page once in real Chrome and runs every check on the recording; walks it with the keyboard, fills in forms, watches for motion and compares pages; and its rules, one spec per Trusted Tester test citing the DHS PDF, decide PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW. A PASS or DOES NOT APPLY is held back to NEEDS REVIEW when a test did not read everything. When a rule needs a judgment it asks an open question, which the server judge, a pinned model given evidence, pictures and a rubric, answers yes, no or unsure; unsure goes to a person (planned: a signed-in review page). Results go into a draft pre-SCRT report and back to the agent, which explains them.](docs/diagrams/tobi-flow.png)

- **Rules decide every outcome.** Each test has one rules spec in [specs/rules/](specs/rules/), every row citing the Trusted Tester PDF page it rests on. Every report records each spec's version.
- **One recording per page.** Key presses and form entries go to the recording, never the live site, and every check sees the same page.
- **A model answers only narrow questions,** by rubric, and may answer "unsure". With a model gateway configured (`JUDGE_BASE_URL`, `JUDGE_API_KEY`), TOBI's own pinned model answers them and records its reason; without one, your calling agent answers by the same rubric. Either way, "unsure" stays NEEDS REVIEW for a person, and TOBI never guesses PASS.
- **Planned, not built:** the signed-in page where a person answers what the model left, and export to a Trusted Tester's own SCRT record.

Why the judging moved into the server: [the decision record](docs/plans/2026-11-07-server-judge-pivot.md) and [what the evaluations showed](docs/solutions/server-judge.md).

## How well it works

Agent-assisted results on our evaluation pages, scored against a certified Trusted Tester's blind reports. They say nothing about any other page.

- **On 29 NASA pages from three sites** (rerun 2026-11-18 with the current tool): no PASS or DOES NOT APPLY where the tester found a failure in 593 results; 93% agreement where TOBI decided (331 of 355); 40% left for a person. Per test and site: [evals/STATUS.md](evals/STATUS.md).
- **Each site was first tested blind,** with TOBI's results locked in git before the tester's answers were added ([how a round runs](docs/how-to/run-a-judging-round.md)); the rounds and every rerun are logged in [evals/README.md](evals/README.md).
- **Against the same model with a general browser tool**, and between TOBI's own judge and the calling agent, three runs each: [the comparison](evals/judging/compare-2026-11-19-r3/compare.md).
- **On published answer keys:** 43 of 49 of DHS's Trusted Tester verdicts on W3C test cases, with no unsafe result, and all 80 expected results on the Section 508 Baseline Alignment pages (development sets; `uv run pytest tests/test_act_cases.py tests/test_baseline_cases.py`).

## Tools

| Tool | What it does | Main inputs |
| --- | --- | --- |
| `tobi_run_tt_tests` | Tests one page. It records the page once, runs the chosen TT tests on the recording, and returns findings, any open questions (answered by the server's judge when it has a model and can reach it, otherwise left for your agent), and links to the full report and pre-SCRT file. | `url` (`.gov` and `.mil` by default); `tests` (default: all implemented); `other_pages` (1-5 pages of the same site, for 9.A-9.C and 19.A); `no_time_limit` |
| `tobi_answer_questions` | Records answers to the open questions and decides again by the spec. Every answer sent here is recorded as the calling agent's; a person's answer, which overrides it, is to come from TOBI's own page. | `run_id`; `answers` (one per question) |
| `tobi_run_status` | Waits for a run that was still going when its call returned, and gives its result. Without `job_id`: what is left across the session's runs (open questions, follow-up calls, runs still going); with `finish=true` it also makes the follow-up calls the server may make itself. | `job_id` (optional); `finish` |
| `tobi_explain` | Explains tests in plain language: what a test checks, or, with a `run_id`, what that run found and why (full summaries, the reasoning, the places on the page, what can still change a result, and the W3C links for fixing it). Results carry one line per finding; this holds the detail. | `about` (test IDs, a WCAG criterion or words); `run_id` |
| `tobi_read_report` | Reads an SCRT or pre-SCRT file: what failed and what still needs a person. With `compare_to`, it lists every test whose result differs between two files (for example, before and after a fix). | `content`; `compare_to` |

**Also:**
- **Resources:** `run://{run_id}/...` (a run's files, kept 24 hours) and `tt://5.1.3/...` (the TT text).
- **Prompt:** `explain` (a test or a result in plain language; the same material as `tobi_explain`, as a command for the user).

## TT tests in scope

TT 5.1.3 has 61 active tests. TOBI performs 22 of them, listed below with their rules spec and how each did on our evaluation pages. The other 39 come back NEEDS REVIEW, "This test could not be performed".

Status describes 29 evaluation pages on three NASA sites, scored against a Trusted Tester's blind SCRT files. It says nothing about any other page.
- ✅ **green:** agrees with the tester.
- ⚠️ **yellow:** often fails pages the tester passes, or leaves most cells for a person.
- ❌ **red:** passed a page the tester failed, or was wrong more often than right.

Counts and the run each comes from: [evals/STATUS.md](evals/STATUS.md). A test marked "see known wrong outcomes below" has wrong results open on test pages built to probe it, even where it agrees with the tester on our evaluation pages.

<!-- status-table:start -->
| ID | TT test name | Spec | Status |
| --- | --- | --- | --- |
| 2.A | 1.4.2-audio-control | [1.2.0](specs/rules/2a-audio-control.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 2.B | 2.2.2-blinking-moving-scrolling | [1.5.0](specs/rules/2b-blinking-moving-scrolling.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 2.C | 2.2.2-auto-updating | [1.2.0](specs/rules/2c-auto-updating.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 2.D | 4.1.2-change-notify-auto | [1.3.0](specs/rules/2d-change-notify-auto.md) | ✅ agrees with a tester |
| 3.A | 2.3.1-flashing | [1.4.0](specs/rules/3a-flashing.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.A | 2.1.1-keyboard-access | [1.15.0](specs/rules/4a-keyboard-access.md) | ⚠️ often fails pages a tester passes; see known wrong outcomes below |
| 4.B | 2.1.1-no-keystroke-timing | [1.4.0](specs/rules/4b-no-keystroke-timing.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.C | 2.1.2-no-keyboard-trap | [1.19.0](specs/rules/4c-no-keyboard-trap.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.D | 2.4.7-focus-visible | [1.10.0](specs/rules/4d-focus-visible.md) | ⚠️ often fails pages a tester passes; see known wrong outcomes below |
| 4.E | 3.2.1-on-focus | [1.9.0](specs/rules/4e-on-focus.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.F | 2.4.3-focus-order-meaning | [1.12.0](specs/rules/4f-focus-order-meaning.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 5.A | 3.3.2-label-provided | [1.16.0](specs/rules/5a-label-provided.md) | ✅ agrees with a tester |
| 5.B | 2.4.6-label-descriptive | [1.14.0](specs/rules/5b-label-descriptive.md) | ⚠️ often fails pages a tester passes |
| 5.C | 1.3.1-programmatic-label | [1.16.0](specs/rules/5c-programmatic-label.md) | ✅ agrees with a tester |
| 5.D | 3.2.2-on-input | [1.12.0](specs/rules/5d-on-input.md) | ⚠️ often fails pages a tester passes |
| 5.F | 3.3.1-error-identification | [1.17.0](specs/rules/5f-error-identification.md) | ⚠️ mostly left for a person |
| 5.G | 3.3.3-error-suggestion | [1.12.0](specs/rules/5g-error-suggestion.md) | ⚠️ mostly left for a person |
| 5.H | 3.3.4-error-prevention | [1.10.0](specs/rules/5h-error-prevention.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 9.A | 2.4.1-bypass-function | [1.8.0](specs/rules/9a-bypass.md) | ✅ agrees with a tester |
| 9.B | 3.2.3-consistent-navigation | [1.8.0](specs/rules/9b-consistent-navigation.md) | ✅ agrees with a tester |
| 9.C | 3.2.4-consistent-identification | [1.11.0](specs/rules/9c-consistent-identification.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 19.A | 2.4.5-multiple-ways | [1.16.0](specs/rules/19a-multiple-ways.md) | ✅ agrees with a tester |

<!-- status-table:end -->

## Known wrong outcomes

Wrong PASS or DOES NOT APPLY results found on test pages built to probe each test's blind spots, and not yet fixed. For these tests, read a PASS or DOES NOT APPLY as "in what the tool looked at". Each links to where its fix is tracked.

<!-- known-gaps:start -->
- **2.A, 2.B, 2.C, 3.A:** content the 6.5-second watch misses: audio or motion that starts late, a blink by `visibility` or about 2.5 times a second, motion that fills the screen, a counter started by scrolling, flashing below the first screen ([roadmap](docs/ROADMAP.md#later)).
- **4.A, 4.C, 4.D, 4.E, 4.F:** controls inside a form that opens from a plain button are not reached; 4.D also passes a faint focus mark on a large linked image ([#135](https://github.com/abbybowman/tobi508/issues/135)).
- **4.B, 5.H:** timing instructions or a payment form not in English, or worded "press Enter twice" ([roadmap](docs/ROADMAP.md#next-after-the-demo)).
- **9.C:** controls in a page's content that do the same thing under different names ([#138](https://github.com/abbybowman/tobi508/issues/138)).
<!-- known-gaps:end -->

The pages that found them are in [the code review](docs/reviews/2026-11-11-code-review.md); what each test cannot do by design is in [KNOWN-LIMITS.md](docs/KNOWN-LIMITS.md).

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

The run takes minutes: until it is done, each result says `"status": "running"` and how far along it is: first the page reading steps done (or not needed), then the tests done, each with a rough percentage (`"progress": "Reading the page, 2 of 5 steps done or not needed (40%): walking the page with Tab and Shift+Tab (45 s so far)"`, later `"Page read (100%). Testing, 7 of 21 tests done (33%): checking 5.C (3 min 10 s so far)"`), and the agent waits with `tobi_run_status`.

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
- `JUDGE_BASE_URL` and `JUDGE_API_KEY`: a Messages API endpoint (Anthropic's API, `https://api.anthropic.com`, or an agency gateway). With both set, the server's own pinned model answers every test's open questions (`JUDGE_TYPES`, default `all`); `JUDGE_BACKEND=client` sends them to your agent instead.

**Safety:**
- Every navigation and redirect is checked against the allowlist.
- Chrome connects through a local proxy that refuses private and cloud-metadata addresses.
- ANDI is served from a vendored copy.
- Page content is treated as data: it never chooses a URL, a tool or an outcome.
- Every report records all versions.

Details: [SECURITY.md](SECURITY.md). What TOBI can't do yet, test by test (and in general, such as replays not freezing randomness or time): [KNOWN-LIMITS.md](docs/KNOWN-LIMITS.md).

## Contribute

- **Testers:** certified Trusted Testers can run their own judging round and contribute it: [docs/how-to/run-a-judging-round.md](docs/how-to/run-a-judging-round.md).
- **Developers:** set up with [Get started](docs/how-to/get-started.md), then read [how TOBI is built](docs/ARCHITECTURE.md), [CLAUDE.md](CLAUDE.md) and [docs/ROADMAP.md](docs/ROADMAP.md). Run the tests with `uv sync --group dev`, then `uv run pytest`. On Windows, `TEST_BROWSER_CHANNEL=chrome TEST_HEADED=1` checks it in real Chrome; run natively, not in WSL2, keep the screen unlocked and don't click in the test windows ([what the first Windows runs found](docs/solutions/windows-chrome-results.md)).

## License

MIT (see [LICENSE](LICENSE)), from the GSA-TTS [mcp-hackathon-template](https://github.com/GSA-TTS/mcp-hackathon-template). Third-party software (see [NOTICE](NOTICE)):

- **ANDI 29.2.2**, Copyright Social Security Administration, Apache License 2.0 ([third_party/andi/NOTICE](third_party/andi/NOTICE), [LICENSE.md](third_party/andi/LICENSE.md)). Unmodified copy; use does not imply SSA endorsement.
- **jQuery 3.7.1**, Copyright OpenJS Foundation and other contributors, MIT ([third_party/jquery/LICENSE.txt](third_party/jquery/LICENSE.txt)).
- **SCRT 5.2.0**, Copyright Department of Homeland Security, MIT ([third_party/scrt/LICENSE](third_party/scrt/LICENSE)). Its test rows are read as a template; its pages are used in tests, and [demo/prescrt-viewer/](demo/prescrt-viewer/) reuses its stylesheet. Use does not imply DHS endorsement.
