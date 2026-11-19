---
title: "Evaluation Document: Section 508 TOBI"
subtitle: "GSA MCP and AI Agent Hackathon · Service \"Read\" Integration track"
---

> **Draft source.** This Markdown file is the source; the Word file in
> GSA's template is built from it (`docs/hackathon/README.md`). **[FILL: …]**
> marks a figure that a run still in progress will supply. Links point at
> `main` of the public repository, so detail lives there, not here.

*TOBI's results are agent-assisted, not certified DHS Trusted Tester results, and nothing here says a tested page is accessible or Section 508 conformant.*

| | |
| --- | --- |
| Server under test | Section 508 TOBI (Tester-Oriented Browser Inspector): [github.com/abbybowman/tobi508](https://github.com/abbybowman/tobi508) |
| Track | Service "Read" Integration: TOBI reads public federal web pages and writes nothing to them |
| Answer keys | DHS's published Trusted Tester verdicts on W3C test pages; a certified Trusted Tester's blind reports on 29 NASA pages |
| Models | Claude Sonnet 5.5 as the calling agent, the baseline agent and TOBI's server judge (pinned prompt, hashed in every report) |

## 1. Overview and Objectives

Federal agencies test websites for Section 508 with the DHS Trusted Tester process, a step-by-step procedure that says which keys to press and what counts as a failure. There are not enough people to run it:

- **Testing is the weakest part of federal Section 508 programs:** 2.00 out of 5 in GSA's FY 2025 assessment ([GSA](https://www.section508.gov/manage/section-508-assessment/2025/findings/accessibility-implementation-outcomes/testing-and-remediation/)).
- **Certification takes about 70 hours of training plus an exam** ([ONRR](https://blog.onrr.gov/trusted-tester/)); in 2024 DHS lowered the pass mark from 90% to 85% to make it more attainable ([Section508.gov](https://www.section508.gov/blog/trusted-tester-update-april2024/)).
- **Scanners cannot do most of it.** They read code and never press a key: of 60 Trusted Tester test conditions, axe-core and pa11y miss 36 entirely, including every keyboard trap ([our coverage map](https://github.com/abbybowman/tobi508/blob/main/docs/research/2026-10-31-tt-coverage-map.md)).

**TOBI** is an MCP server that runs 22 of the 61 Trusted Tester 5.1.3 tests in real Chrome. It records each page once and replays it for every check; walks it with the keyboard, fills in forms, watches for motion and compares pages; decides outcomes from versioned rules written from the DHS PDF; and asks a pinned model only the narrow judgment questions the procedure leaves, sending "unsure" to a person. Five tools each do a whole task: test a page, wait for a long run, answer open questions, explain a result, and read or compare report files ([how it works](https://github.com/abbybowman/tobi508/blob/main/README.md#how-it-works)).

The evaluation asks four questions. Targets were set before the first scored run.

| Question | Measure | Target |
| --- | --- | --- |
| Does TOBI reach a certified tester's outcome? | Unsafe errors (a PASS or DOES NOT APPLY where the tester found a failure); false FAILs; agreement | 0 unsafe; false FAILs ≤ 15% of decided results |
| Does it beat a general-purpose agent? | The same, on the same pages | — |
| Who should make the judgment calls? | Questions answered; consistency across 3 runs | Reported |
| What does it cost? | Model spend and clock time per page | Reported |

Results left for a person are always reported beside accuracy: leaving everything undecided would fake a perfect score.

## 2. Testing Methodology

### Framework and reproducibility

- **Rules are the only source of outcomes.** Each test has one rules file ([specs/rules](https://github.com/abbybowman/tobi508/tree/main/specs/rules)) whose rows cite the Trusted Tester PDF page they rest on; every report records each file's version.
- **One recording per page.** Every check replays it, so the page cannot vary between checks or runs. Browser, inspector, rules and judge versions are pinned and recorded in every report.
- **1,557 tests on every change,** over 149 published answer-key pages and about 560 test pages of our own ([tests/fixtures](https://github.com/abbybowman/tobi508/tree/main/tests/fixtures)). A CI check also refuses a rules change without a new version number.
- **Blind real-page rounds by commit and reveal:** TOBI's results are locked in git before the tester's answers are added ([how a round runs](https://github.com/abbybowman/tobi508/blob/main/docs/how-to/run-a-judging-round.md)).

### Datasets

1. **Published answer keys:** 114 W3C test cases with DHS's Trusted Tester verdicts, and 35 Section 508 Baseline Alignment pages. A development set: the rules were written with them in view.
2. **Our own test pages** for what those lack (frames, web components, dialogs, late-drawing pages, text that tries to trick the tool). They test behavior and are not counted toward accuracy.
3. **29 NASA pages on three sites,** each tested by hand by a certified Trusted Tester in DHS's own reporting tool, one blind round per site: www.nasa.gov (Nov 4), svs.gsfc.nasa.gov (Nov 8), science.data.nasa.gov (Nov 16). After scoring, each site was used for development.

### Evaluators

- **Exact match, no LLM grader.** Outcomes are categories, compared in code with the key.
- **Weighted for the worst error:** agree +1, left for a person 0, unsafe −3, other error −1. A false PASS hides a barrier from someone who cannot use a mouse; a false FAIL costs a developer time.
- **Three arms, same model, same prompt, same pages:** **A**, an agent using TOBI that answers TOBI's questions itself; **B**, the baseline, the same agent with a general browser tool (Playwright MCP) and the web instead of TOBI; **C**, TOBI's server judge answering its own questions.
- **Rule-decided and model-decided results are scored apart,** so neither is blamed for the other's errors.
- **A judge eval after every question change:** a fresh agent answers from TOBI's output alone ([37 runs logged](https://github.com/abbybowman/tobi508/blob/main/evals/README.md)).

## 3. Performance Metrics

### Headline results

On Nov 18 we reran all 29 NASA pages from their original recordings with the current tool, the server judge answering every open question:

- **0 unsafe errors in 593 results:** no PASS or DOES NOT APPLY where the certified tester found a failure.
- **93% agreement where TOBI decided** (331 of 355), with 23 false FAILs.
- **40% left for a person** (238 of 593): the price of never guessing.

These sites were used to fix the tool, so this is development evidence, not a blind result. Per test and per site: [evals/STATUS.md](https://github.com/abbybowman/tobi508/blob/main/evals/STATUS.md), summarized in the [README's status table](https://github.com/abbybowman/tobi508/blob/main/README.md#tt-tests-in-scope).

**Against a general-purpose agent,** the same model with a browser and the same instructions made 16 to 20 unsafe errors per run on the same pages (rounds 1 and 2; round 3: **[FILL]**), and in round 1 it reported no failure on any page. TOBI's own blind runs made 0 to 6. In rounds 1 and 2 every one came from a rule deciding alone; in round 3, one of the three came from the judge, which had been shown Chrome's own error message as if it were the page's (now never shown to it).

On published answer keys, TOBI agrees with 43 of 49 DHS verdicts on W3C test cases, with no unsafe error and 5 left for a person, and matches all 80 expected results on the Section 508 Baseline Alignment pages. Both are development sets, and there the model's questions get scripted answers, so they test the rules, not the model.

### What the blind rounds uncovered

Each round was a NASA site TOBI had never been developed on, scored once before any fix ([round 1](https://github.com/abbybowman/tobi508/blob/main/evals/judging/round1/agent-score.md), [round 2](https://github.com/abbybowman/tobi508/blob/main/evals/judging/round2-armc/abc-score.md), [round 3](https://github.com/abbybowman/tobi508/blob/main/evals/judging/round3/score.md)). Their value was in what they exposed:

| Round | What it uncovered | What changed |
| --- | --- | --- |
| 1: www.nasa.gov, 9 pages (Nov 4) | The calling agent left TOBI's judgment questions unanswered; long runs hit client timeouts | Runs continue as jobs; results end with the work left; the judge moved into the server |
| 2: svs.gsfc.nasa.gov, 10 pages (Nov 8) | A recording missing code the page loads on use hid a keyboard trap; failures sat behind menus TOBI never opened | Such code is recorded; menus and panels are opened and read |
| 3: science.data.nasa.gov, 10 pages (Nov 16) | Pages that draw themselves after loading; Chrome's own form messages read as the page's | TOBI waits for the page to draw; browser messages go to a person |

Early fixes made TOBI more cautious than a careful tester; most later work gave it the evidence to decide again. On svs.gsfc.nasa.gov, decided results rose from 68 to 141 over four reruns with no unsafe error.

### Calling agent vs. server judge

In round 2 the server judge answered all 194 questions in each of 3 repeats, and the repeats agreed on 194 of 200 results, but it was no more accurate than the calling agent: its errors leaned toward FAIL, mostly from one question with faulty evidence. Rerun on round 3's pages after the fixes, three runs each: the calling agent answered **[FILL]** of the questions and the server judge **[FILL]**; their outcomes matched across runs on **[FILL]** and **[FILL]** of results; unsafe errors per run were **[FILL]** and **[FILL]**.

### Cost and time

Model spend is under $1 a page: the server judge costs about $0.13 a page with prompt caching. Browser time is the real cost: 1 to 8 minutes a page, because every shortcut we measured (fewer images, not waiting for late-drawing pages) produced wrong results. A certified tester takes about 10 to 15 minutes a page for these 22 tests **[FILL: timed]**, so TOBI is not faster per page; it runs unattended and in parallel, needs no certified tester for what it decides, and gives the same evidence every time. The baseline agent took seconds and cents, and passed pages that fail.

### Where TOBI is wrong

- **Wrong evidence, not wrong judgment.** When the judge erred, it had been shown the wrong thing: elements placed mid-scroll, a page number read as an error message, a page pictured before it drew. Fixing the evidence fixed the answers.
- **Rules stricter than the procedure.** A search box labeled only by a magnifier icon fails in TOBI and passes for the tester: 7 false FAILs a run on one site.
- **What a recording cannot show:** forms that only reveal errors when really submitted are left for a person.

Current wrong outcomes are listed in the [README](https://github.com/abbybowman/tobi508/blob/main/README.md#known-wrong-outcomes) and [docs/KNOWN-LIMITS.md](https://github.com/abbybowman/tobi508/blob/main/docs/KNOWN-LIMITS.md). With no misses in n true failures, the 95% upper bound on the miss rate is about 3/n; no test has enough failures to prove 5% or less, so these results are promising, not proven.

## 4. Security Considerations

TOBI reads public `.gov` and `.mil` pages only, with no credentials and nothing behind a login. Page content is untrusted, since it can contain text written to steer an AI. Recordings and screenshots are deleted after 24 hours by default; results belong in the user's own repository.

| Threat | Control | Checked by |
| --- | --- | --- |
| Reaching internal networks | Every browser connection passes a proxy that refuses private and cloud-metadata addresses at connect time, so DNS rebinding cannot get through; the allowlist is checked on every redirect | [56 egress tests](https://github.com/abbybowman/tobi508/blob/main/tests/test_egress.py) |
| Prompt injection in page text | Page text reaches the model only in an escaped block marked untrusted; it never picks a URL, a tool or an outcome | [Trick-text test pages](https://github.com/abbybowman/tobi508/tree/main/tests/fixtures/inject) |
| Changing a live site | Key presses and form entries go only to the recording | Replay design |
| An agent posing as a person | Every answer through MCP is recorded as the agent's and outranks no one | Tool tests |
| Secrets in errors and logs | No query strings, cookies, headers or page text | [Seeded-secret tests](https://github.com/abbybowman/tobi508/blob/main/tests/test_leakage.py) |
| Open access to a hosted server | stdio by default; hosted only behind the agency's OIDC sign-in, with runs visible only to their owner and an audit line per call | Sign-in tests in CI; signed in end to end on NASA's VAST platform |
| Results mistaken for certification | Every result says "not a certified Trusted Tester result"; a report cannot be marked certified | Every test run |
| Third-party code changing | The bundled accessibility inspector (ANDI) and jQuery are pinned by hash | CI |

Page content can shape a request only in a few capped cases, all on the tested page's host (for example, the site's own search for the "multiple ways" test); the [README](https://github.com/abbybowman/tobi508/blob/main/README.md#configuration-and-safety) lists them. Known gap: network-level egress rules on the host, as a second layer.

## 5. Lessons Learned and Recommendations

### What we learned about building an MCP server

**1. Don't make correctness depend on the calling agent's diligence.**

*Observation.* Agents treat "I can write the report now" as done. None answered TOBI's questions unless told to, and asked to say what a picture showed, one wrote it "as if I had looked, but I never opened those images." More wording in tool descriptions moved the shortcut; it never removed it.

*Recommendation.* Put every step correctness depends on inside the server, so a skipped step can only leave a result incomplete, never wrong.

**2. Put the next step in the data, not the prose.**

*Observation.* What worked was structure: a `finish=true` option that made the follow-up calls in one call (used in 5 of 6 runs once it existed, almost never before), a status field that could not be relayed as complete, and the to-do list placed last in the result.

*Recommendation.* Return machine-readable state (work left, who it waits on) and collapse follow-ups into one call.

**3. In practice, only tools count.**

*Observation.* Agents seldom read MCP resources, even with a tool for it, and prompts are started by users, not agents. Pictures attached to a tool result were looked at; links were not.

*Recommendation.* Attach what the agent must see to tool results, size-capped; make what it must do a tool.

**4. Design for the client's limits, not the protocol's.**

*Observation.* Clients time out long calls, truncate large results and may not show progress; agents never put optional choices to users. We return within 45 seconds and keep the run going as a job, ask similar questions once (one page's 96 became 4) and halved the largest result. MCP's elicitation, which lets a server ask the user directly, is what we would try next.

*Recommendation.* Test through real agent clients early, with long runs and large results.

**5. The server owns the verdict; the client agent owns the user's context.**

*Observation.* We moved judgment into the server not because its model was smarter but because it answered everything and could be pinned, recorded and measured; a user may bring any model to an MCP server. MCP's sampling feature would borrow the user's model, which is the problem (and it is deprecated as of the 2026-07-28 specification). The calling agent now explains results in the user's project and helps fix them.

*Recommendation.* Where results must be repeatable, keep the decisions on the server, with model, prompt and parameters recorded in every result.

**6. Encode the expertise as versioned rules, and ask the model narrow questions.**

*Observation.* The DHS procedure became one rules file per test, each step citing the PDF; the model answers rubric questions and may say "unsure." Fixes almost always went to the evidence or the rubric, not the model. Objective checks (the test pages and the version lock) kept many parallel AI coding sessions from breaking each other.

*Recommendation.* Encode the procedure, not a prompt about it: rules a domain expert can review, every outcome traced to a rule, and tests every change must pass.

### Recommendations for evaluating an MCP server

1. Look for an official answer key before writing your own; DHS's verdicts gave us one on day one.
2. Name your worst error and weight your score by it.
3. Compare against a capable agent with general tools, not only against no tool.
4. Count what agents do from their transcripts, not their final reports.
5. Score rule-decided and model-decided results apart, and report work left for a person beside accuracy.

### Limitations

- 22 of 61 Trusted Tester tests; the rest are reported as not performed.
- 29 pages on three NASA sites, labeled by one certified tester who is also the developer. Commit and reveal guards against tuning to the key, not against one person's reading of the procedure.
- All three sites are now development sites; no held-out site remains.
- Chromium only, one window size, from a recording; no screen reader testing (Trusted Tester scope is WCAG 2.0 A and AA).
