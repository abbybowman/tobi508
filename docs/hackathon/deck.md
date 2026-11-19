# Deck text

> Generated from `out/TOBI-deck.pptx` (built by `build_pptx.py`, the
> source) so the deck can be read and diffed as text. Do not edit by hand:
> change `build_pptx.py`, rebuild, regenerate this file (README).

<!-- Slide number: 1 -->
# Section 508 TOBI
An MCP server that runs the DHS Trusted Tester process in a real browser
GSA MCP and AI Agent Hackathon · Service "Read" Integration · Abby Bowman
Agent-assisted results, not certified Trusted Tester results
Code: github.com/abbybowman/tobi508. The evaluation document gives every figure in this deck with its source.

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
Sources: GSA FY 2024 and FY 2025 governmentwide Section 508 assessments; ONRR, "Trusted Tester"; Section508.gov, April 2024. Scanner coverage: our map of 60 Trusted Tester test conditions against axe-core 4.14 and pa11y 10.

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
In the spirit of SSA's ANDI, the free inspector Trusted Testers already use: TOBI supports certified testers; it does not replace them.

<!-- Slide number: 4 -->
# Server design: how a page gets tested
![Flow diagram, How TOBI tests a page. Solid lines are built and running today; dashed lines are planned. 1: the developer's AI agent, any MCP client, asks TOBI to test a page with tobi_run_tt_tests. Inside the TOBI MCP server: 2, record the page once in real Chrome, and every check runs on the replay, not the live site; 3, walk and collect: Tab through the page, fill in forms, watch for motion, compare other pages; 4, rules decide, one rules spec per Trusted Tester test with each step citing the DHS PDF, giving an outcome of PASS, FAIL, DOES NOT APPLY or NEEDS REVIEW with evidence. Held back when unsure: a rule that cannot decide says NEEDS REVIEW, and a PASS or DOES NOT APPLY becomes NEEDS REVIEW when a test did not read everything. When a rule needs a judgment it asks an open question; 5, the server judge, TOBI's own pinned model given evidence, pictures and a rubric, answers yes, no or unsure. A sure answer goes back to the rule. Unsure, or a failed call, goes to 7, a person on a signed-in review page whose answer overrides the model's (planned). Outcomes go to 6, a draft report (pre-SCRT) marked not certified, recording who answered what, and later to 8, the Trusted Tester's own SCRT record once they certify every row (planned). Results and a link to the full report go back to the agent.](Flow diagram)
Five tools, each a whole task: test a page, wait for a long run, answer open questions, explain a result, read or compare reports. Python, FastMCP, Pydantic and Playwright, from GSA's template.

<!-- Slide number: 5 -->
# Key decision: the DHS procedure is the code
Rules, not prompts
One rules file per Trusted Tester test; every row cites the PDF page it rests on
Only rules decide outcomes; every report records each rule's version
CI refuses a rule change without a new version number, which kept parallel AI coding sessions from overwriting each other
A step must match something the PDF asks a person to do; anything past it goes to a person
Record once, replay every check
Key presses and form entries never reach the live site
Same recording, same evidence: variation can only come from judgment, where it can be measured
Focus is read from Chrome itself, so page scripts cannot fake it
Browser, rules, judge model and prompt are pinned and recorded in every report
1,557 tests run on every change, over 149 published answer-key pages and about 560 of our own. Built Oct 30 to Nov 18, 2026 by one person with Claude Code: about 990 commits, 137 merged pull requests.

<!-- Slide number: 6 -->
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

<!-- Slide number: 7 -->
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
Round 2's server judge erred only toward FAIL, mostly because elements were placed while the page was still scrolling. Fixing that evidence, not the prompt, fixed the answers.

<!-- Slide number: 8 -->
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

<!-- Slide number: 9 -->
# Evaluation: blind rounds against a certified tester
How we scored
29 NASA pages on 3 sites, each tested by hand in DHS's own report tool
Commit and reveal: TOBI's results are locked before the answers go in
Exact match, no LLM grader; an unsafe error (a PASS where the tester found a failure) weighs -3
Baseline: the same model with a general browser tool and the same instructions
What each round uncovered
Round 1, www.nasa.gov: agents left judgment questions unanswered. The judge moved into the server.
Round 2, svs.gsfc.nasa.gov: a recording missing code hid a keyboard trap; failures sat behind closed menus. Both are now read.
Round 3, science.data.nasa.gov: pages that draw themselves late; Chrome's own form messages. TOBI waits; those go to a person.
Each site was new to TOBI and scored once before any fix; then it became a development site. Scores: evals/judging/ in the repository.

<!-- Slide number: 10 -->
# Results: no unsafe errors with the current tool
0 of 593
93%
40%
unsafe errors on all 29 pages, rerun Nov 18
agreement with the certified tester where TOBI decided (331 of 355)
left for a person (238 of 593): the price of never guessing
A general agent with a browser: 16-20 unsafe errors per run on the same pages, and in round 1 no failure reported anywhere (round 3: [FILL])
DHS's published verdicts on W3C test pages: 43 of 49 agree, no unsafe error
Cost: under $1 of model spend and 1-8 minutes of browser time a page; a certified tester takes 10-15 minutes [FILL]
Calling agent vs. server judge, 3 runs each: [FILL]
The rerun used sites the tool was then fixed on: development evidence, not a blind result. Per test and site: evals/STATUS.md. Too few true failures per test to prove a miss rate: promising, not proven.

<!-- Slide number: 11 -->
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
Known gap: no network-level egress rules on the host yet, as a second layer. Page content may shape a request only in a few capped, approved cases, all on the tested page's own host.

<!-- Slide number: 12 -->
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

<!-- Slide number: 13 -->
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
