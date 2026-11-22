# Section 508 TOBI — Tester-Oriented Browser Inspector

TOBI (`tobi508` in code) is an MCP server that runs the [DHS Trusted Tester](https://www.section508.gov/test/trusted-tester/) v5.1.3 process for Section 508 (WCAG 2.0 A and AA) on a web page in a real Chrome browser, and reports what it finds by Trusted Tester test ID. It is named after [ANDI](https://www.ssa.gov/accessibility/andi/help/install.html), SSA's Accessible Name & Description Inspector, which it runs inside the browser. TOBI is independent of DHS and SSA.

> [!WARNING]
> **Not a certified Trusted Tester result.** TOBI produces agent-assisted findings only. They must not be reported, cited or relied on as a DHS Trusted Tester result. A certified Trusted Tester must perform any test that counts for Section 508 conformance.

**Why TOBI exists:** Since automated accessibility scanners like [pa11y](https://github.com/pa11y/pa11y) and [axe-core](https://github.com/dequelabs/axe-core) can only read a page's code, they can't find failures that require actually using the page: keyboard traps, lack of visible focus, labels that disappear when you type, no way to skip the header, etc. By loading the page in a browser, TOBI can do the repetitive tabbing, typing and visual comparisons, then apply the Trusted Tester procedures and pass/fail criteria through deterministic Python scripts as well as focused LLM judgment calls, while leaving any unclear cases for a human to judge.

**What TOBI provides** for each of the 22 Trusted Tester tests it performs: PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW, a plain-language explanation with evidence, and a pre-SCRT file with the same rows as DHS's standard [SCRT report](https://section508coordinators.github.io/SCRT/), marked as not certified and explaining where each result came from. The pre-SCRT reports can be opened in TOBI's HTML [viewer](demo/prescrt-viewer/viewer.html), filtered, and compared with other pre-SCRT or SCRT reports ([how to use it](demo/prescrt-viewer/README.md)).

## How TOBI works

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
| `tobi_cancel_run` | Stops one of your own runs that is still queued or running, and frees its browser slot; nothing from it is kept. For when the user asks, or a run was started twice by mistake. The server's admin can cancel anyone's run from inside the server's container (`tobi508-admin`). | `job_id` |
| `tobi_explain` | Explains tests in plain language: what a test checks, or, with a `run_id`, what that run found and why (full summaries, the reasoning, the places on the page, what can still change a result, and the W3C links for fixing it). Results carry one line per finding; this holds the detail. | `about` (test IDs, a WCAG criterion or words); `run_id` |
| `tobi_read_report` | Reads an SCRT or pre-SCRT file: what failed and what still needs a person. With `compare_to`, it lists every test whose result differs between two files, with both results and comments (TOBI's run beside a Trusted Tester's SCRT file, or before and after a fix). | `content`; `compare_to` |

**Also:**
- **Resources:** `run://{run_id}/...` (a run's files, kept 24 hours) and `tt://5.1.3/...` (the TT text).
- **Prompt:** `explain` (a test or a result in plain language; the same material as `tobi_explain`, as a command for the user).

## Tests in scope

Trusted Tester (TT) v5.1.3 has 61 active tests. Together they check all 38 WCAG 2.0 Level A and AA success criteria, plus 3 Section 508 requirements that WCAG doesn't include. TOBI can currently perform 22 of these 61 tests, listed below with their rules spec and how each did on our evaluation pages. The other 39 come back NEEDS REVIEW, "This test could not be performed".

The WCAG SC column links each test's WCAG 2.0 success criteria. A Trusted Tester test often checks only part of a criterion: 1.3.1 Info and Relationships, for example, is split across seven TT tests, and TOBI performs only the one about form labels (5.C). A PASS here is not a pass of the whole criterion.

Status is based on the latest results from 29 real webpages across three NASA sites, scored against a certified Trusted Tester's blind SCRT files (not a large sample size yet!):
- ✅ **green:** agrees with the tester.
- ⚠️ **yellow:** often fails pages the tester passes, or leaves most cells for a person.
- ❌ **red:** passed a page the tester failed, or was wrong more often than right.

Counts and the run each comes from: [evals/STATUS.md](evals/STATUS.md). A test marked "see known wrong outcomes below" has wrong results open on test pages built to probe it, even where it agrees with the tester on our evaluation pages.

<!-- status-table:start -->
| ID | Test name | WCAG SC | Spec | Status |
| --- | --- | --- | --- | --- |
| 2.A | Audio control | [1.4.2](https://www.w3.org/TR/WCAG20/#visual-audio-contrast-dis-audio) | [1.2.0](specs/rules/2a-audio-control.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 2.B | Blinking moving scrolling | [2.2.2](https://www.w3.org/TR/WCAG20/#time-limits-pause) | [1.5.0](specs/rules/2b-blinking-moving-scrolling.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 2.C | Auto updating | [2.2.2](https://www.w3.org/TR/WCAG20/#time-limits-pause) | [1.2.0](specs/rules/2c-auto-updating.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 2.D | Change notify auto | [4.1.2](https://www.w3.org/TR/WCAG20/#ensure-compat-rsv) | [1.3.0](specs/rules/2d-change-notify-auto.md) | ✅ agrees with a tester |
| 3.A | Flashing | [2.3.1](https://www.w3.org/TR/WCAG20/#seizure-does-not-violate) | [1.4.0](specs/rules/3a-flashing.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.A | Keyboard access | [2.1.1](https://www.w3.org/TR/WCAG20/#keyboard-operation-keyboard-operable) | [1.19.0](specs/rules/4a-keyboard-access.md) | ⚠️ often fails pages a tester passes; see known wrong outcomes below |
| 4.B | No keystroke timing | [2.1.1](https://www.w3.org/TR/WCAG20/#keyboard-operation-keyboard-operable) | [1.4.0](specs/rules/4b-no-keystroke-timing.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.C | No keyboard trap | [2.1.2](https://www.w3.org/TR/WCAG20/#keyboard-operation-trapping) | [1.19.0](specs/rules/4c-no-keyboard-trap.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.D | Focus visible | [2.4.7](https://www.w3.org/TR/WCAG20/#navigation-mechanisms-focus-visible) | [1.10.0](specs/rules/4d-focus-visible.md) | ⚠️ often fails pages a tester passes; see known wrong outcomes below |
| 4.E | On focus | [3.2.1](https://www.w3.org/TR/WCAG20/#consistent-behavior-receive-focus) | [1.9.0](specs/rules/4e-on-focus.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 4.F | Focus order meaning | [2.4.3](https://www.w3.org/TR/WCAG20/#navigation-mechanisms-focus-order) | [1.15.1](specs/rules/4f-focus-order-meaning.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 5.A | Label provided | [3.3.2](https://www.w3.org/TR/WCAG20/#minimize-error-cues) | [1.16.0](specs/rules/5a-label-provided.md) | ✅ agrees with a tester |
| 5.B | Label descriptive | [2.4.6](https://www.w3.org/TR/WCAG20/#navigation-mechanisms-descriptive) | [1.14.0](specs/rules/5b-label-descriptive.md) | ⚠️ often fails pages a tester passes |
| 5.C | Programmatic label | [1.3.1](https://www.w3.org/TR/WCAG20/#content-structure-separation-programmatic), [4.1.2](https://www.w3.org/TR/WCAG20/#ensure-compat-rsv) | [1.16.0](specs/rules/5c-programmatic-label.md) | ✅ agrees with a tester |
| 5.D | On input | [3.2.2](https://www.w3.org/TR/WCAG20/#consistent-behavior-unpredictable-change) | [1.12.0](specs/rules/5d-on-input.md) | ⚠️ often fails pages a tester passes |
| 5.F | Error identification | [3.3.1](https://www.w3.org/TR/WCAG20/#minimize-error-identified) | [1.17.0](specs/rules/5f-error-identification.md) | ⚠️ mostly left for a person |
| 5.G | Error suggestion | [3.3.3](https://www.w3.org/TR/WCAG20/#minimize-error-suggestions) | [1.12.0](specs/rules/5g-error-suggestion.md) | ⚠️ mostly left for a person |
| 5.H | Error prevention | [3.3.4](https://www.w3.org/TR/WCAG20/#minimize-error-reversible) | [1.10.0](specs/rules/5h-error-prevention.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 9.A | Bypass function | [2.4.1](https://www.w3.org/TR/WCAG20/#navigation-mechanisms-skip) | [1.9.0](specs/rules/9a-bypass.md) | ✅ agrees with a tester |
| 9.B | Consistent navigation | [3.2.3](https://www.w3.org/TR/WCAG20/#consistent-behavior-consistent-locations) | [1.9.0](specs/rules/9b-consistent-navigation.md) | ✅ agrees with a tester |
| 9.C | Consistent identification | [3.2.4](https://www.w3.org/TR/WCAG20/#consistent-behavior-consistent-functionality) | [1.12.0](specs/rules/9c-consistent-identification.md) | ✅ agrees with a tester; see known wrong outcomes below |
| 19.A | Multiple ways | [2.4.5](https://www.w3.org/TR/WCAG20/#navigation-mechanisms-mult-loc) | [1.17.0](specs/rules/19a-multiple-ways.md) | ✅ agrees with a tester |

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

The run takes minutes: until it is done, each result says `"status": "running"` and how far along it is, in three parts: reading the page, testing, finishing. A percentage covers only the part it names (`"progress": "Part 1 of 3, reading the page: 2 of 5 reading steps done or not needed (40% of this part; the tests have not started). Now: walking the page with Tab and Shift+Tab (45 s so far)"`, later `"Part 2 of 3, testing (the page has been read): 7 of 21 tests done (33% of the tests). Now: checking 5.C (3 min 10 s so far)"`), and the agent waits with `tobi_run_status`. A run waiting behind another says so, and names the caller's own runs ahead of it; `tobi_cancel_run` stops one.

When it is done, ask the agent to save the results: it saves both files, the pre-SCRT file (open it in the [viewer](demo/prescrt-viewer/viewer.html), or `/viewer` on a hosted server) and the full report. To see how TOBI's results differ from a Trusted Tester's, ask it to compare the run with their SCRT file (`tobi_read_report`), or open both in the viewer ("Compare with").

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
