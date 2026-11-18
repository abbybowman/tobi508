# Deck text

> Generated from `out/TOBI-deck.pptx` (built by `build_pptx.py`, the
> source) so the deck can be read and diffed as text. Do not edit by hand:
> change `build_pptx.py`, rebuild, regenerate this file (README).

<!-- Slide number: 1 -->
# Section 508 TOBI
An MCP server that runs the DHS Trusted Tester process in a real browser
GSA MCP and AI Agent Hackathon · Service "Read" Integration · Abby Bowman
Agent-assisted results, not certified Trusted Tester results

### Notes:
TOBI (Tester-Oriented Browser Inspector) runs 22 of the 61 DHS Trusted Tester
5.1.3 tests on public federal web pages: it opens the page in real Chrome,
presses real keys, decides what the procedure decides mechanically, and
leaves the rest for a person. It reads pages and writes nothing to them.
Code: github.com/abbybowman/tobi508. The evaluation document has every
figure on these slides and its source.

<!-- Slide number: 2 -->
# The challenge: a precise test, too few people to run it
2.00 / 5
~70 hours
36 of 60
Testing and remediation: the weakest area of federal Section 508 programs (GSA, FY 2025)
of training plus an exam to become a certified Trusted Tester; in 2024 DHS lowered the pass mark from 90% to 85% to make it more attainable
Trusted Tester test conditions that automated scanners do not cover at all, including every keyboard trap
The DHS Trusted Tester process is the government's consistent, objective accessibility test: it says which keys to press and what counts as a failure.
Scanners read a page's code; they cannot press Tab. Certified people can, and agencies do not have enough of them.

### Notes:
Sources: GSA FY 2025 governmentwide Section 508 assessment, testing and
remediation (section508.gov/manage/section-508-assessment/2025). FY 2024: 60%
of reporting entities had no or only some staff trained in Section 508 web
testing. ONRR estimated about 70 hours of training plus a multi-hour exam
(blog.onrr.gov/trusted-tester). Section508.gov, April 2024: the passing score
for the Practice and Final exams went from 90% to 85% "to make the
certification more attainable for learners". Scanner coverage: our map of 60
Trusted Tester test conditions against axe-core and pa11y: 3 reliably covered,
21 partly, 36 not at all (docs/research/2026-10-31-tt-coverage-map.md).

<!-- Slide number: 3 -->
# Our hypothesis
FOR
agencies with only a few certified Trusted Testers and no capacity to test pages at scale,
GIVEN
that the Trusted Tester process is built to be mechanical and consistent, with only a few judgment calls,
IF
we combine scripted steps in a real browser with narrow, rubric-based model judgments,
THEN
we can find clear failures accurately and consistently, including ones scanners cannot see, and leave the unclear cases for a person,
THUS
certified testers can cover far more pages, and site owners can fix obvious problems without waiting for a full manual test.

### Notes:
In the spirit of SSA's ANDI, the free accessibility inspector Trusted Testers
already use: TOBI supports certified testers; it does not replace them.

<!-- Slide number: 4 -->
# Why not just give an AI agent a browser?
Same model, same instructions, same pages, scored blind against a certified Trusted Tester. Unsafe error: a PASS where the tester found a failure.
Agent with a general browser tool
Unsafe errors per run:
20, 16 (round 1)   20, 17 (round 2)
In round 1 it reported no failure on any page. It passed every unlabeled search field and took page landmarks for a way to skip repeated content.
Agent with TOBI
Unsafe errors per run:
0, 0, 0 (round 1)   3, 5 (round 2)
Every round 2 unsafe error came from a rule deciding alone, the same cells each run; those rules are fixed. None came from a model's answer.
The procedure has to be encoded, not prompted. A capable agent knows what WCAG says; it does not follow a 90-page test procedure step by step.

### Notes:
Round 1: 9 www.nasa.gov pages (Nov 4). Round 2: 10 svs.gsfc.nasa.gov pages
(Nov 8). Arm B is the same Claude Sonnet 5.5 with Playwright MCP and web
access instead of TOBI. Scored per WCAG criterion. Round 3 baseline:
[FILL from the Nov 19 run]. Full tables: evaluation document, section 3.

<!-- Slide number: 5 -->
# The solution: an MCP server that follows the procedure
Record the page once in real Chrome; replay it for every check
1
Five tools, each a whole task
tobi_run_tt_tests: test a page
tobi_run_status: wait for a long run
tobi_answer_questions: record answers
tobi_explain: a result in plain words
tobi_read_report: read or compare report files
Resources: the TT text (tt://) and a run's evidence (run://)
22 of 61 tests: keyboard, focus, forms, moving and flashing content, consistency across a site's pages
Walk it with the keyboard, fill in forms, watch for motion, compare pages
2
Decide what the procedure decides mechanically, from versioned rules
3
Ask a pinned model narrow questions with evidence and a rubric; "unsure" goes to a person
4
Report by Trusted Tester test ID, in plain language, with screenshots, and a draft in DHS's own report format
5

### Notes:
Inputs are Pydantic models with precise descriptions; the list of implemented
tests in the tool description comes from the code's registry. Python,
FastMCP, Pydantic and Playwright, from GSA's template. stdio by default;
hosted over HTTP only behind the agency's sign-in. Any MCP client is the
front end: a developer asks in plain words in the tool they already use.

<!-- Slide number: 6 -->
# Server design: how a page gets tested
![Flow diagram. 1: the developer's AI agent, any MCP client, asks TOBI to test a page. Inside the TOBI MCP server: 2, record the page once in real Chrome, every test runs on the same replayed copy; 3, rules decide, one written rules spec per Trusted Tester test; when a rule needs a judgment it asks an open question; 4, the server judge, TOBI's own pinned model, answers by rubric from evidence and pictures. If it is sure, the rule uses the answer and gives an outcome (PASS, FAIL or DOES NOT APPLY) with evidence; if unsure or the call failed, 5, a person reviews (planned). Results go back to the agent with a link to the full report, and into 6, a pre-SCRT file with a not-certified banner, and later 7, the Trusted Tester's own SCRT record (planned). The rules decide every outcome; unsure never becomes PASS; agent-assisted, not certified.](Flow diagram)

### Notes:
Solid lines are built; dashed are planned (the person's review page and the
SCRT record). The server judge now answers every question type whenever the
server has a model. One module per Trusted Tester test, one rules file per
module, one tool per file: adding a test changes no tool.

<!-- Slide number: 7 -->
# Key decision: the DHS procedure is the code
One rules file per test
Every step cites the Trusted Tester PDF's page.
No outcome is decided anywhere else: not in evidence collection, the judge or the tools.
Versioned and locked
Every report records each rule's version.
CI refuses a rule change without a new version number: what kept parallel AI coding sessions from overwriting each other.
Proportionate to the PDF
A step must match something the PDF asks a person to do.
Anything past that goes to a person. The aim: a careful tester, not more.
1,557
149
~560
tests run on every change
published answer-key pages (W3C, DHS, Section 508 Baseline)
test pages of our own: frames, dialogs, trick text, late-drawing pages

### Notes:
Built Oct 30 to Nov 18, 2026 by one person with Claude Code: about 990
commits and 137 merged pull requests. The developer reviewed the rules and
the results, not each line of AI-written code; the tests are what made that
safe. When the PDF disagrees with itself, the spec records it rather than
resolving it silently.

<!-- Slide number: 8 -->
# Key decision: record once, replay every check
Every key press, form entry and screenshot happens on one recording of the page.
Testing never touches the live site: no form is really submitted.
Same recording, same evidence: run-to-run variation can only come from judgment, where it can be measured.
Browser, ANDI, Playwright, rules, judge model and prompt hash are recorded in every report.
Pages can lie; the browser cannot
Focus is read through Chrome's DevTools protocol, outside the page's reach. A test page whose script fakes focus still fails.
What a recording missed
A NASA page loaded a script only when used, so a keyboard trap did nothing on replay. Such scripts are now saved, and a test cannot PASS without them.

### Notes:
The second card is a real-page lesson from round 2: the tester found a
keyboard trap and a focus jump that the replay could not show. The fix
records the code the page loads on use (capped and allowlisted) and holds the
result for a person when any is missing.

<!-- Slide number: 9 -->
# Key decision: a false PASS is the worst error
A rule decides
PASS, FAIL or DOES NOT APPLY, with the PDF step it rests on
Example: keyboard trap
TOBI presses Shift+Tab, arrows, Escape and Enter to get out.
The model only reads the page for a documented escape key.
TOBI then presses that key. Only if focus leaves is it a PASS.
A rule cannot decide
NEEDS REVIEW, never PASS
The test did not read everything
PASS and DOES NOT APPLY are held back
A model gives an opinion
PASS only when a key press or measurement confirms it
A false PASS hides a barrier from someone who cannot use a mouse; a false FAIL costs a developer time. Our score weights an unsafe error -3, any other error -1, agreement +1, and a result left for a person 0.

### Notes:
"Unsafe" in this deck means a PASS or DOES NOT APPLY where the certified
tester found a failure. A wrong DOES NOT APPLY hides a barrier as surely as a
wrong PASS, so both are held back when a test's reading of the page is
incomplete. A few questions are ones a careful tester settles by looking
(for example, whether a focus outline is visible); there the model must
answer "unsure" whenever the evidence does not settle it.

<!-- Slide number: 10 -->
# Key decision: the judge moved into the server
Round 1: the calling agent judges
No agent answered TOBI's questions unless told to.
Told to, the score rose from 44-47 to 82.
Asked to say what each picture showed, one wrote it "as if I had looked, but I never opened those images".
Round 2: a server judge, on trial
Answered all 194 questions in each of 3 repeats; repeats agreed on 194 of 200 results.
But not more accurate: more false FAILs, most from one question whose evidence was faulty.
Now: the server judges
One pinned model and prompt, recorded in every report.
Unsure goes to a person.
The calling agent explains results in the user's project and helps fix them.
Why: repeatable, auditable and measurable, not smarter. Fixing the evidence fixed most wrong answers.
Re-measured Nov 19 on round 3's pages, 3 runs each: [FILL]

### Notes:
Round 2's server judge (arm C) answered every question, but its errors were
all toward FAIL, mostly from the focus-order question: elements were placed
where they were while the page was still scrolling. Fixing that evidence,
not the prompt, fixed the answers. A user may bring any model to an MCP
server; only a model the server controls can be pinned and recorded.
[FILL: the Nov 19 comparison of the calling agent and the server judge:
questions answered, consistency across 3 runs, accuracy, cost.]

<!-- Slide number: 11 -->
# Demo: NASA's Artemis III page, in plain words
0:00
What TOBI is, and why scanners cannot do this
The 5-minute video
Uploaded with this deck.
Link: [FILL]
0:25
Sign-in: only NASA people reach the hosted server
0:55
Ask in plain words: test a page and two others from its site
1:20
The keyboard walk, sped up (about 11 minutes)
1:50
Results, and the questions only judgment can answer
2:40
Explain the results and the tool's limits
3:25
The draft report beside the certified tester's own
4:25
Every call audited; not certified

### Notes:
Script: docs/hackathon/demo.md.

<!-- Slide number: 12 -->
# Evaluation: three comparisons, scored by exact match
vs. published answer keys
114 W3C test cases with DHS's Trusted Tester verdicts; 35 Section 508 Baseline Alignment pages.
A development set: the rules were written with them in view.
vs. a certified Trusted Tester
29 NASA pages on 3 sites, each tested by hand in DHS's own report tool.
Commit and reveal: TOBI's results are locked before the answers go in.
vs. a general-purpose agent
The same model and instructions with Playwright MCP and the web instead of TOBI.
Harder than a no-tool baseline.
No LLM grades the results: outcomes are categories, compared in code.
Results a rule decided are scored apart from results a model's answer decided.
After any change to a question, a fresh agent answers it from TOBI's output alone (37 runs).

### Notes:
Each real site was tested blind once, then used for development. The tester
also built the tool: commit and reveal guards against tuning to the key, not
against one person's reading of the procedure. A second certified tester has
not yet labeled any page.

<!-- Slide number: 13 -->
# Results: no unsafe errors after the fixes
0 of 593
93%
40%
unsafe errors on all 29 pages, rerun Nov 18 after the fixes
agreement with the certified tester where TOBI decided (331 of 355)
left for a person (238 of 593): the price of caution

| Evidence | Agree | Unsafe errors | Left for a person |
| --- | --- | --- | --- |
| Round 3, blind: a site never used before (10 pages) | 118 of 149 (79%) | 3 (both causes fixed) | 32% |
| Same pages, general agent with a browser | [FILL] | [FILL] | [FILL] |
| DHS's published verdicts (49 W3C cases) | 43 of 49 | 0 | 5 of 49 |

The rerun used sites the tool was then fixed on: development evidence, not a blind result. Too few true failures per test to prove a miss rate: promising, not proven.

### Notes:
Rerun by site: www.nasa.gov 79 of 82 agree, 0 unsafe; svs.gsfc.nasa.gov 131
of 141, 0 unsafe; science.data.nasa.gov 121 of 132, 0 unsafe. On
svs.gsfc.nasa.gov the decided results rose from 68 to 91 to 134 to 141
across four reruns with no unsafe error: early fixes made TOBI too cautious,
and later work gave it the evidence to decide again. Round 3's three unsafe
errors: Chrome's own form-error messages read as the page's, and a page that
drew itself after the keyboard walk began.

<!-- Slide number: 14 -->
# What it costs: cents per page, minutes per page

| Per page | Model spend (list price) | Clock time |
| --- | --- | --- |
| TOBI's browser work | none | 1-6 min; 6-8 min with other pages of the site |
| TOBI's server judge | $0.13 cached, $0.67 uncached | about 1 min |
| Calling agent driving TOBI | $0.07-0.26 | mostly TOBI's browser time |
| General agent with a browser | $0.02-0.05 | 10-20 s, and wrong |
| Certified tester, by hand | staff time | about 10-15 min [FILL] |

Model spend is small; browser time is the cost. Every shortcut we measured (fewer images, not waiting for late pages) gave wrong results.
Per page, TOBI is not faster than an experienced tester. It runs unattended and in parallel, needs no certified tester for what it decides, and gives the same evidence every time.

### Notes:
Model figures: Claude Sonnet 5.5 list prices as Claude Code reports them;
an agency's own route will differ. Prompt caching cut the server judge's
cost about five times. The tester's time is an estimate pending timed pages.

<!-- Slide number: 15 -->
# Security: public pages, untrusted content, signed-in hosting
Internal networks
Every browser connection is checked when it connects; private and cloud-metadata addresses refused (56 tests).
Prompt injection
Page text reaches the model only inside an escaped, untrusted block; it never picks a URL, tool or outcome.
The live site
Key presses and form entries go only to the recording.
An agent posing as a person
Every answer through MCP is recorded as the agent's; it outranks no one.
Secrets in logs
No query strings, cookies, headers or page text in errors and logs (seeded-secret tests).
Hosted access
Agency sign-in (OIDC); runs visible only to their owner; one audit line per call.
Every result says "not a certified Trusted Tester result"; a report cannot be marked certified.

### Notes:
.gov and .mil pages only, checked on every redirect. A few narrow exceptions
let page content shape a request, each capped, on the same host and
approved: the site's own search and up to 10 nearby pages for the
"multiple ways" test, one key the page names to stop moving content, and the
scripts a page loads on use. Known gap: network-level egress rules on the
host as a second layer. End-to-end sign-in tested on NASA's VAST platform on
Nov 18.

<!-- Slide number: 16 -->
# Six lessons for building MCP servers
1. Don't depend on the agent's diligence
Agents skipped questions and pictures, and filled proof fields without looking. Put correctness-critical steps in the server.
2. Put the next step in the data
Wording lost to the agent's idea of done. One finish=true call and a to-do list at the end worked.
3. In practice, only tools count
Agents seldom read resources and cannot start prompts. Attach what they must see to tool results.
4. Design for the client's limits
Timeouts, result size, unseen progress: return in 45 s and keep the run going; one page's 96 questions became 4.
5. The server owns the verdict
Pin the model that decides; let the client agent explain and fix. Sampling would borrow the user's model.
6. Encode the expertise as rules
Versioned rules a domain expert can review; narrow rubric questions; tests every change must pass.

### Notes:
Each lesson, with its evidence, is in section 5 of the evaluation document.
Elicitation (a server asking the user directly through the client) is what
we would try next for choices agents never put to users; Claude Code
supports it in interactive sessions. Sampling is deprecated as of the
2026-07-28 MCP specification, and would not have helped: the model would
still be the user's, unpinned and unrecorded.

<!-- Slide number: 17 -->
# Limits, and what comes next
Limits
22 of 61 Trusted Tester tests
29 pages, 3 NASA sites, one certified tester, who is also the developer
Every site is now a development site
One browser, one window size, from a recording
About a third of results go to a person
Next
A blind round on a new site, with a second certified tester
A signed-in page where a person answers what the model was unsure of
More tests where scanners and people disagree most: images, contrast, headings
Another agency can fork it and host it with its own sign-in
Elicitation, so the server can ask the user directly

### Notes:
Status per test: the repository README.
