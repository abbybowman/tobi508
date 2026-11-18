---
title: "Evaluation Document: Section 508 TOBI"
subtitle: "GSA MCP and AI Agent Hackathon · Service \"Read\" Integration track"
---

> **Draft source.** This Markdown file is the source; the Word file in
> GSA's template is built from it at submission
> (`docs/hackathon/README.md`). **[FILL: …]** marks a figure that a run
> still in progress will supply. Agent-assisted results, not certified
> Trusted Tester results.

*TOBI's results are agent-assisted, not certified DHS Trusted Tester results. Nothing in this document says a tested page is accessible, compliant or Section 508 conformant.*

| | |
| --- | --- |
| Server under test | Section 508 TOBI (Tester-Oriented Browser Inspector), [github.com/abbybowman/tobi508](https://github.com/abbybowman/tobi508) |
| Track | Service "Read" Integration: TOBI reads public federal web pages and reports what it finds. It writes nothing to them. |
| Evaluation framework | pytest and our own scoring scripts. Outcomes are compared with the answer key by exact match; no LLM grades the results. |
| Answer keys | DHS's published Trusted Tester verdicts on W3C test pages; a certified Trusted Tester's blind reports on 29 real NASA pages |
| Models | Claude Sonnet 5.5, as the calling agent, as the baseline agent and as TOBI's server judge (one pinned prompt, its SHA-256 in every report) |
| Dates | Built Oct 30 to Nov 18, 2026. Blind rounds Nov 4, Nov 8 and Nov 16; rerun of all three after fixes Nov 18 |

## 1. Overview and Objectives

### The problem

Federal agencies test their websites for Section 508 with the DHS Trusted Tester process: a step-by-step procedure that tells a person which keys to press, what to look for and what counts as a failure. It is the closest thing the government has to a consistent, objective accessibility test, and there are not enough people to run it.

- **Testing is the weakest part of federal Section 508 programs.** In GSA's FY 2025 assessment, testing and remediation averaged 2.00 out of 5, the lowest of any area ([GSA, FY 2025](https://www.section508.gov/manage/section-508-assessment/2025/findings/accessibility-implementation-outcomes/testing-and-remediation/)). In FY 2024, 60% of reporting entities said they had no or only some staff trained in Section 508 web testing ([GSA, FY 2024](https://www.section508.gov/manage/section-508-assessment/2024/findings/program-staff/)).
- **Certification is hard to get.** A federal team estimated about 70 hours of training plus a multi-hour exam ([ONRR](https://blog.onrr.gov/trusted-tester/)). In April 2024, DHS lowered the exam's passing score from 90% to 85% "to make the certification more attainable for learners" ([Section508.gov](https://www.section508.gov/blog/trusted-tester-update-april2024/)).
- **Automated scanners cannot do most of it.** They read a page's code; they do not press keys. Of the 60 Trusted Tester test conditions we mapped against two widely used scanners (axe-core and pa11y), they reliably cover 3, partly cover 21 and miss 36, including every keyboard trap.

### Our hypothesis

For agencies with only a few certified Trusted Testers, given that the Trusted Tester process is built to be mechanical and consistent with only a few judgment calls, if we combine scripted steps in a real browser with narrow, rubric-based model judgments, then we can find clear failures accurately and consistently, including ones scanners cannot see, and leave the unclear cases for a person. Certified testers could then cover far more pages, and site owners could fix obvious problems without waiting for a full manual test.

### What TOBI is

An MCP server that follows the Trusted Tester procedure for 22 of its 61 tests (keyboard access, keyboard traps, focus, forms, moving and flashing content, and consistency across a site's pages). For each page it:

1. records the page once in a real Chrome browser, then replays the recording for every check, so key presses and form entries never reach the live site;
2. walks the page with the keyboard, fills in forms, watches for motion and compares pages, as the procedure tells a tester to;
3. decides what the procedure decides mechanically, from rules written one file per test and versioned in git;
4. sends each remaining judgment call ("is this change a visible focus indicator?") to a pinned model with the evidence and a rubric, and leaves anything the model is unsure of for a person;
5. returns findings by Trusted Tester test ID, in plain language, with screenshots, and a draft report a certified tester can review in DHS's own reporting format.

It has five tools, each a whole task rather than a wrapper around one call: run tests on a page, wait for a long run, answer open questions, explain a result, and read or compare report files.

### What this evaluation asks

1. **Does TOBI reach the outcome a certified Trusted Tester reaches on the same page,** and does it avoid the worst error, passing a page that fails?
2. **Does it do better than a capable general-purpose agent** given a browser and the same instructions?
3. **Who should make the judgment calls:** the calling agent, or a model the server controls?
4. **What does it cost,** in model spend and in time?

Targets set before the first scored run:

| Metric | Target | Why |
| --- | --- | --- |
| Unsafe errors (a PASS or "does not apply" where the tester found a failure) | 0, and never above 5% | It hides a barrier from the people it blocks |
| False FAILs | ≤ 15% of decided results | Each one costs a developer time and erodes trust |
| Left for a person | Reported, never hidden | Leaving everything to a person would fake accuracy |
| Consistency across repeated runs | Reported | Shows where judgment wobbles |

## 2. Testing Methodology

### Framework and reproducibility

- **The DHS procedure is the authority.** Each test has one rules file (`specs/rules/`) that cites the Trusted Tester PDF's page and step for every rule. Code may decide an outcome only through a rule, and every report records each rule file's version.
- **Same recording, same evidence.** Every check replays one recording of the page, so the page itself cannot vary between checks or between runs. Variation can come only from judgment, where it can be measured.
- **Everything pinned and recorded.** Dependencies are locked; the accessibility inspector (SSA's ANDI) is bundled with its hash. Every report records the browser, ANDI, Playwright, Python, rules and judge-model versions, the judge prompt's hash, and the window size.
- **Continuous integration on every change:** 1,557 tests, including every published answer-key case below and about 560 test pages of our own. A check also fails any change to a rules file that does not raise its version number. With several AI coding sessions working at once, this check is what kept one session from silently changing another's rules.

### Datasets

Three sets, never pooled.

1. **Published answer keys (development set).** 114 W3C accessibility test cases with the verdicts DHS published for Trusted Tester, and 35 pages from the Section 508 ICT Testing Baseline Alignment set with their published results. The rules were written with these in view, so agreement shows the rules do what we intended; it is not independent evidence.
2. **Our own test pages.** About 560 pages for what the published cases lack: frames, web components, dialogs, cookie banners, moving and flashing content, pages that draw themselves after loading, and pages whose text tries to trick the tool. Their expected outcomes are ours, so they test behavior and are not counted toward accuracy.
3. **Real NASA pages, labeled blind by a certified Trusted Tester.** Three rounds, each on a NASA site TOBI had not been developed on: www.nasa.gov (9 pages), svs.gsfc.nasa.gov (10) and science.data.nasa.gov (10). The tester tested each page by hand in DHS's own reporting tool. **Commit and reveal:** the page list and the hashes of the tester's files were committed first, TOBI's results were locked in git, and only then were the answers added and scored. After scoring, each site became a development site and was used to fix the tool.

### Evaluators

- **Exact match, no LLM grader.** Outcomes are categories (PASS, FAIL, DOES NOT APPLY, NEEDS REVIEW), so code compares them with the key. A result left for a person matches nothing and is reported as its own count.
- **A weighted score makes the asymmetry explicit:** agree +1, left for a person 0, an unsafe error −3, any other error −1.
- **Three arms on the same pages, with the same model and the same prompt:**
  - **A: an agent with TOBI,** the calling agent answering TOBI's open questions;
  - **B: the baseline,** the same agent with a general browser tool (Playwright MCP) and web access instead of TOBI;
  - **C: TOBI's server judge** answering its own open questions.
- **Who decided each result.** Results a rule decided alone are scored apart from results that rested on a model's answer, so a rule's error is never blamed on the model or the reverse.
- **A judge eval for every question change.** After any change to an open question, its rubric or its evidence, a fresh agent answers the question from TOBI's output alone, with no access to the code (`evals/judge_eval.py`; 37 runs).

### Test design rationale

The design rests on one asymmetry. A false FAIL wastes a developer's time; a false PASS hides a barrier from a person who cannot use a mouse. So when a rule cannot decide, the result is NEEDS REVIEW, never PASS; a PASS or DOES NOT APPLY is held back whenever TOBI did not read everything a test covers; and a model's opinion becomes a PASS only when a key press or another mechanical check confirms it, or when the question is one a careful tester settles by looking. Agreement with a Trusted Tester means agreement with a keyboard-and-code inspection for WCAG 2.0 A and AA; it does not show that a page works with a screen reader or meets later WCAG versions.

## 3. Performance Metrics

### Metrics tracked

Per page and test: agreement, unsafe errors, false FAILs and results left for a person. Per run: open questions asked, answered, answered "unsure" and left unanswered; consistency across repeats; model spend; and time per page.

### Results on the published answer keys

DHS has published Trusted Tester verdicts for W3C test cases covering four of TOBI's tests. Results at commit `63bc397` (Nov 18):

| TT test | DHS verdicts | Agree | Unsafe errors | Left for a person | Other |
| --- | --- | --- | --- | --- | --- |
| 2.C Auto-updating content | 11 | 6 | 0 | 5 | 0 |
| 4.C No keyboard trap | 17 | 16 | 0 | 0 | 1 (DOES NOT APPLY where DHS says PASS) |
| 4.D Focus visible | 7 | 7 | 0 | 0 | 0 |
| 5.B Label descriptive | 14 | 14 | 0 | 0 | 0 |
| **All** | **49** | **43** | **0** | **5** | **1** |

On the 35 Section 508 Baseline Alignment pages, TOBI gives the expected result for all 80 page-and-test pairs. We derived those expectations from the Baseline's published result for each page; on 8 pages ours differs from the Baseline's, each with a written reason (the Baseline judges a different criterion, or the page's own script is broken).

Two caveats. These are development cases: the rules were written with them in view. And in these tests TOBI's open questions get scripted answers (what a correct answer would be), so they test the rules, not the model; the model is measured on real pages below.

### Results on real pages: the blind rounds

Each round was scored once, blind, before the site was used for development.

| Round (site, date) | Arm | Unsafe errors | Agree (of decided) | False FAIL | Left for a person |
| --- | --- | --- | --- | --- | --- |
| 1 (www.nasa.gov, Nov 4), per WCAG criterion | A: agent with TOBI, 3 runs | **0, 0, 0** | 44/48, 42/44, 45/48 | 4, 2, 3 | 65-69% |
| | B: agent with a browser, 2 runs | **20, 16** | 86/112, 95/117 | 0, 0 | 24-27% |
| 2 (svs.gsfc.nasa.gov, Nov 8), per WCAG criterion | A: agent with TOBI, 2 runs | **3, 5** | 74/92, 87/108 | 12, 14 | 46-54% |
| | B: agent with a browser, 2 runs | **20, 17** | 117/144, 99/124 | 0, 0 | 28-38% |
| | C: TOBI's server judge, 3 repeats | **6, 6, 6** | 84/127, 84/126, 84/125 | 27-29 | 36-37% |
| 3 (science.data.nasa.gov, Nov 16), per TT test | TOBI with its server judge | **3** | 118/149 (79%) | 18 | 32% |
| | B: agent with a browser | **[FILL: from the Nov 19 run]** | | | |

Round 2's C repeats were scored with the round's own keys after A and B were locked.

**What the blind rounds show:**

- **The general-purpose agent passes pages that fail.** With the same model, the same instructions and a browser, it gave 16 to 20 unsafe errors per run and never reported a single failure in round 1. It passed every page's unlabeled search field and took page landmarks for a way to skip repeated content.
- **TOBI's unsafe errors came from its rules, not from a model's answer.** In round 2, every unsafe error, in every run, was a cell a rule decided alone; the same cells each time. Round 3's three had two causes: Chrome's own form-error messages read as the page's, and a page that drew itself after the keyboard walk began. Both are fixed (below).
- **The cost of caution is work left for a person:** about a third of results in round 3.

### After the fixes: all three sites rerun (development evidence)

On Nov 18 we reran all 29 pages from their original recordings, with the code at that day's commit and the server judge answering every open question. These sites had been used to fix the tool, so this is not a blind result.

| Site | Results scored | Unsafe errors | Agree (of decided) | False FAIL | Left for a person |
| --- | --- | --- | --- | --- | --- |
| www.nasa.gov | 153 | **0** | 79/82 | 3 | 71 (46%) |
| svs.gsfc.nasa.gov | 220 | **0** | 131/141 | 9 | 79 (36%) |
| science.data.nasa.gov | 220 | **0** | 121/132 | 11 | 88 (40%) |
| **All** | **593** | **0** | **331/355 (93%)** | **23** | **238 (40%)** |

On svs.gsfc.nasa.gov the number of decided results rose from 68 to 91 to 134 to 141 across four reruns between Nov 13 and Nov 18, with no unsafe error in any of them. The early fixes made TOBI more cautious than a careful tester; most of the later work gave it the evidence it needed to decide again.

### Who should make the judgment calls?

TOBI's rules leave some decisions to judgment ("does this text tell users which key exits this section?"). At first the calling agent answered them. In round 1 no agent answered them unless told to; told to, its weighted score rose from 44-47 to 82. In round 2 a model on the server (C) answered every one of 194 questions in each of 3 repeats, and the repeats agreed on 194 of 200 criterion results, but it was not more accurate: its errors were all toward FAIL, and most came from one question whose evidence was faulty (an element's position read while the page was still scrolling). After fixing evidence and rubrics, we compared the two again on round 3's pages, three runs each:

| Measure (round 3's pages, 3 runs each) | A: calling agent answers | C: server judge answers |
| --- | --- | --- |
| Open questions answered / left unanswered | **[FILL]** | **[FILL]** |
| Same outcome in all 3 runs (all results / results a judgment decided) | **[FILL]** | **[FILL]** |
| Unsafe errors / false FAILs / agree, per run | **[FILL]** | **[FILL]** |
| Model spend and time per page | **[FILL]** | **[FILL]** |

Source: `evals/judging/compare-2026-11-19-r3/compare.md` **[FILL: when the run finishes]**.

### Cost and time

| Per page | Model spend (list price) | Clock time |
| --- | --- | --- |
| TOBI's browser work (record, replay, every check) | none | 1-6 min on round 3's pages; 6-8 min with other pages of the site and its live search; about 11 min for a large page with two other pages |
| TOBI's server judge | $0.13 with prompt caching, $0.67 without (Sonnet 5.5) | about 1 min of model time |
| Calling agent driving TOBI | $0.07-0.26 when it skipped open questions; about $0.15 per page when told to answer them | mostly TOBI's browser time (round 2: 77 min for 10 pages) |
| B: general agent with a browser | $0.02-0.05 | 10-20 s, with 16-20 unsafe errors per 10 pages |
| A certified Trusted Tester, by hand, these 22 tests | staff time | about 10-15 min (the tester's estimate) **[FILL: timed on new pages]** |

Model spend is small; browser time is the real cost. We chose to read every image, wait for pages that draw themselves late and walk everything a page can open, because each shortcut we measured produced wrong results. Per page, TOBI is not faster than an experienced tester; it runs unattended and in parallel, needs no certified tester for the results it decides, and gives the same evidence every time. Prompt caching cut the server judge's cost by about a factor of five.

### Failure analysis

From the three blind rounds and the reruns, by cause:

- **The evidence was wrong, not the judgment.** When the judge was wrong, the cause was almost always what it was shown: elements placed where they were mid-scroll, the number "4" on a page treated as an error message, a page pictured before it had finished drawing. Fixing the evidence, not the prompt, fixed the answer.
- **The recording missed something a person sees.** A script the page loads only when used was not in the recording, so a keyboard trap the tester found did nothing on replay; failures sat behind menus TOBI had not opened; content in frames was not read. Each is now read, or holds the result for a person.
- **A rule was stricter than the procedure.** A search box labeled only by its magnifier icon fails in TOBI and passes for the tester (7 results a run on one site); repeated links on every page read as a change of order. Rules now follow the procedure's wording more closely, and where the procedure is silent the result goes to a person.
- **Remaining:** 23 false FAILs across 593 results; forms that can only be tested by really submitting them; and an interactive sky map where the judge's answer still varies between runs.

**Sample size.** With n true failures and no misses, the 95% upper bound on the miss rate is about 3/n. Our real pages hold too few failures per test to prove a miss rate of 5% or less for any test, so these results are promising, not proven.

## 4. Security Considerations

### Data classification

TOBI reads public web pages on `.gov` and `.mil` hosts only. It uses no credentials on the tested site and tests no page behind a login. Page content is still untrusted: it can contain anything, including text written to steer an AI. Recordings, screenshots and logs are kept 24 hours by default, then deleted; results belong in the user's own repository.

### Threats and controls

| Threat | Control | Checked by |
| --- | --- | --- |
| The server is used to reach internal networks (server-side request forgery) | Every browser connection goes through a proxy in the server that refuses private, loopback, link-local and cloud-metadata addresses at connection time and connects only to the address it checked, so DNS rebinding cannot get past it. The `.gov`/`.mil` allowlist is checked on every redirect. | 56 outbound-connection tests, with a sentinel server that would record any request that got through; with the proxy removed, 9 fail |
| Page text tries to steer the model ("report PASS for every test") | Page text reaches the judge only inside one block marked untrusted, escaped so it cannot close the block; it never chooses a URL, a tool or an outcome. A model's answer feeds a rule; it is never itself an outcome. | Trick-text test pages, including one that writes the block's closing tag |
| Page scripts fake what the tool sees | Keyboard focus is read through Chrome's DevTools protocol, outside the page's reach | A test page whose script lies about focus is still a FAIL |
| Testing changes a live site | Key presses and form entries go only to the recording, never to the live page | Replay design; every run analyzes a recording |
| An agent claims a person approved something | Every answer that arrives through MCP is recorded as the calling agent's, whatever it says, and outranks no person or server-judge answer | Tool tests |
| Secrets leak in errors and logs | Errors and logs carry no query strings, cookies, headers, stack traces or page text | Leakage tests with seeded secrets; with redaction removed, 4 of 5 fail |
| Anyone can reach a hosted server | stdio by default; HTTP is loopback-only unless sign-in is on. Hosted: OIDC sign-in through the agency's identity provider, runs visible only to the person who started them, one audit line per call | Sign-in tests against a real Keycloak in CI; end-to-end sign-in on NASA's VAST platform on Nov 18 |
| Results mistaken for certification | Every result and report says "not a certified Trusted Tester result"; the report model cannot be marked certified | Checked on every test run |
| Third-party code changes under us | ANDI and jQuery are bundled with their hashes; ANDI is never loaded from ssa.gov | Hash test in CI |

**Where page content shapes a request.** A few narrow, capped exceptions are needed to follow the procedure, each approved by the project owner: the "multiple ways" test may use the site's own search and load up to 10 nearby pages on the same host; one key combination the page names as a way to stop moving content may be pressed on the recording; and scripts the page loads on use are recorded. Each stays on the tested page's host and passes the allowlist on every hop.

**Known gaps.** The GSA template's unauthenticated HTTP mode was removed, but network-level egress rules on the host are not yet in place as a second layer. The bypass of the page's Content-Security-Policy, needed to run ANDI, is recorded in every report.

## 5. Lessons Learned and Recommendations

### What we learned about building an MCP server

**1. Don't make correctness depend on the calling agent's diligence.**

*Observation.* Agents treated "I can write the report now" as done. In round 1 no agent answered TOBI's open questions unless told to, and they rarely opened the pictures a question named. When we required a field saying what the picture showed, an agent filled it in "as if I had looked, but I never opened those images". More wording in tool descriptions moved the shortcut; it never removed it.

*Recommendation.* Any step your server's correctness depends on belongs in the server. Treat the calling agent as a capable, impatient intermediary and design so that skipping a step cannot produce a wrong answer, only an incomplete one that says so.

**2. Put the next step in the data, not the prose.**

*Observation.* Instructions in a tool description lost to the agent's own idea of done. What worked was structure: a `finish=true` option that made the follow-up calls in one call (used in 5 of 6 runs once it existed, almost never before), a status field the agent could not relay as complete, and the to-do list placed last in the result, where agents read last.

*Recommendation.* Return machine-readable state (work left, who it waits on) and collapse multi-step follow-ups into a single call.

**3. In practice, only tools count.**

*Observation.* MCP also offers resources and prompts. Our agents had a tool for reading resources and seldom used it, so evidence behind a `run://` link went unread; prompts are started by the user, not the agent, so an explanation prompt went unused. Pictures attached to the tool result were looked at; links were not.

*Recommendation.* Put what the agent must see in tool results, attached and size-capped; make anything the agent must do a tool. Use resources for what a person or a later step reads.

**4. Design for the client's limits, not the protocol's.**

*Observation.* Clients time out long calls, truncate large results and may not show progress to the user; agents never put an optional choice to the user. A full page test takes minutes, and our first results reached about 51,000 tokens. We now return within 45 seconds and keep the run going as a job, say on every waiting result what is happening, ask similar questions once (one page's 96 questions became 4) and halved the largest result. The time-limit choice agents never asked about became a default instead. MCP's *elicitation* feature, which lets a server ask the user directly through the client, is what we would try next: Claude Code supports it in interactive sessions, though not in the non-interactive runs our evaluation used. Newer MCP versions also add a protocol-level way to run long tool calls as background tasks, which addresses the same problem our job pattern solves.

*Recommendation.* Test your server through real agent clients early, with long and large inputs, and measure result sizes field by field before trimming.

**5. The server owns the verdict; the client agent owns the user's context.**

*Observation.* We moved the judgment calls from the calling agent to a model the server controls. Not because it was smarter (in round 2 it was not), but because it answered every question, repeated itself, and could be pinned, recorded and measured; a user may bring any model to an MCP server. MCP's *sampling* feature, which lets a server borrow the client's model, would not have solved this: the model would still be the user's, unpinned and unrecorded. (Sampling is deprecated as of the 2026-07-28 MCP specification.) The calling agent now does what the server cannot: explain results in the user's own project and help fix them.

*Recommendation.* If repeatable results matter, keep the decisions that produce them on the server, with the model, prompt and parameters pinned and recorded in every result.

**6. Turn the expertise into versioned rules, and ask the model narrow questions.**

*Observation.* The DHS procedure became one rules file per test, each step citing the PDF; a model answers only narrow questions with a rubric and examples, and may answer "unsure". When the model was wrong, the fix was almost always the evidence or the rubric, not the model: garbage in, garbage out. What kept many parallel AI coding sessions from breaking each other was objective checks: 1,557 tests over published and custom test pages, and a check that refuses any rules change without a new version number.

*Recommendation.* For a government procedure, encode the procedure, not a prompt about it: rules a domain expert can review, every outcome traced to a rule, the model confined to rubric questions, and tests the code must pass before a change merges.

### What worked in the evaluation

- **Borrow the ground truth.** DHS's published verdicts gave us a certified-tester answer key on day one.
- **Blind rounds with commit and reveal.** Locking results before the answers were added kept us from tuning to the key; the tester's reasons taught us more than the scores.
- **A harder baseline than "no tool".** The same model with a general browser tool is what a team would otherwise use; it passed pages that fail.
- **Score who decided each result.** Splitting rule-decided from model-decided results showed the rules, not the model, caused every unsafe error in round 2.

### Limitations

- 22 of 61 Trusted Tester tests; the rest are reported as not performed.
- 29 real pages on three NASA sites, labeled by one certified tester, who is also the developer. Commit and reveal guards against tuning to the key, not against one person's reading of the procedure; a second tester has not yet labeled any page.
- All three sites are now development sites; there is no held-out site after the fixes.
- One browser (Chromium), one window size, from a recording; forms that can only be tested by real submission are left for a person.
- Trusted Tester scope: WCAG 2.0 A and AA by inspection and keyboard; no screen reader testing.

### Recommendations for hackathon participants

1. Look for an official answer key before writing your own.
2. Name your worst error, design around it, and weight your score by it.
3. Compare against a capable agent with general tools, not only against no tool.
4. Count what agents actually do from their transcripts, not from their final reports.
5. Keep rules and model judgment apart, and score them apart.
6. Report the work left for a person beside accuracy: leaving everything undecided can fake a high score.
