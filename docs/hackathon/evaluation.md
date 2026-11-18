# Evaluation Document

GSA MCP and AI Agent Hackathon

> **Draft.** **[FILL: …]** marks a final figure, copied from one scored
> run at the submission commit. **[PENDING]** marks work not done yet.
> Structure follows GSA's sample evaluation document (sections 1-5).
> Agent-assisted results, not certified Trusted Tester results.

| | |
| --- | --- |
| Server under test | Section 508 TOBI (Tester-Oriented Browser Inspector), package `tobi508`, [github.com/abbybowman/tobi508](https://github.com/abbybowman/tobi508) |
| What it does | Runs parts of the DHS Trusted Tester (TT) 5.1.3 Section 508 web test process in a real Chrome browser and reports agent-assisted findings by TT test ID. It reads public government web pages and writes nothing to them. **Not a certified Trusted Tester result.** |
| Tests implemented | 22 of the 61 active TT 5.1.3 tests: 2.A-2.D (audio, moving and updating content), 3.A (flashing), 4.A-4.F (keyboard), 5.A-5.D and 5.F-5.H (forms), 9.A-9.C and 19.A (across pages of a site). Spec versions: **[FILL: at the submission commit]**. Every other test is reported as "needs review: this test could not be performed". |
| Evaluation framework | Three layers, reported apart: (1) pytest with a scoring module that compares outcomes with DHS's published Trusted Tester verdicts, exact match; (2) a judge eval, where a fresh agent answers the tool's open questions from its output alone; (3) rounds on real .gov pages scored against a certified Trusted Tester's blind answer files |
| Agent model | Rounds 1 and 2: Claude Sonnet 5.5 through the Claude Code CLI, as the calling agent, the baseline agent and the server-judge stand-in. **[FILL: who answered open questions in the scored run]** |
| Browser | **[FILL: Playwright and browser versions, OS, headed or headless for the scored run]** |
| Run | **[FILL: commit, date, command, tests passed, duration]** |

## 1. Overview and objectives

### Why this matters

The goal is to put some of the Trusted Tester process into more hands, so certified testers spend their time on edge cases and low-confidence calls instead of the clear-cut ones.

- **Agencies lack trained testers.** In GSA's FY 2024 governmentwide assessment, 60% of reporting entities (146) said they had no or only some development and testing staff trained in Section 508 web testing ([GSA, FY 2024](https://www.section508.gov/manage/section-508-assessment/2024/findings/program-staff/)).
- **Testing is the weakest link.** In FY 2025, testing and remediation was the weakest implementation area, averaging 2.00 on a 5-point scale ([GSA, FY 2025](https://www.section508.gov/manage/section-508-assessment/2025/findings/accessibility-implementation-outcomes/testing-and-remediation/)).
- **Certification is a real investment.** A federal team estimated about 70 hours of training plus a multi-hour exam ([ONRR](https://blog.onrr.gov/trusted-tester/)). DHS does not publish how many certified testers there are.
- **Scanners miss most barriers, and all of these.** In the UK Government Digital Service's audit of a page with 143 deliberate barriers, the best tool found about 40%, and 29% were missed by all 10 tools ([GDS](https://accessibility.blog.gov.uk/2017/02/24/what-we-found-when-we-tested-tools-on-the-worlds-least-accessible-webpage/)). In our own map of TT test conditions against axe-core 4.14 and pa11y 10, scanners reliably cover 3, partly cover 21 and give no coverage for 36 (`docs/research/2026-10-31-tt-coverage-map.md`). axe-core has no rule for keyboard traps, focus visibility, focus changes or focus order.

### What we're testing

**Does the tool reach the same outcome a certified Trusted Tester reaches on the same page?** A passing server:

- misses no real failures: a false PASS hides a barrier from disabled users, so it is the worst error;
- rarely flags passing pages: a false FAIL wastes a developer's time;
- says "needs review" instead of guessing, without escalating everything;
- gives the same outcome on repeated runs of the same recorded page.

A second question: **can an agent with no accessibility training use the tool correctly,** relay its outcomes faithfully, and never describe them as certified? Rounds 1 and 2 answered this in part, and the answer changed the design (section 3.3).

| Metric | Target | Why |
| --- | --- | --- |
| False-PASS rate | ≤ 5% per TT test | The worst error |
| False-FAIL rate | ≤ 15% | Wastes time, erodes trust |
| Needs-review rate | Reported | Escalating everything would fake accuracy |
| Consistency across repeats | Reported | Shows where judgment wobbles |

Targets were set before the first scored run.

## 2. Testing methodology

### 2.1 Framework and reproducibility

- **The TT PDF is the authority.** Each TT test has a rules spec in `specs/rules/`, citing the PDF's page and step for every rule. Code may decide an outcome only through a spec row, and each report records the spec version.
- **Recorded pages.** A live page is recorded once and every pass replays the recording, so key presses and form entries never reach the live site and a run can be repeated. Test pages are stored with SHA-256 hashes and served locally; tests never fetch from the network.
- **Pinned versions.** Dependencies are locked; ANDI 29.2.2 and jQuery are bundled with hashes. Every report records ANDI, Playwright, browser, OS, Python, spec and judging-model versions, and the window the page was tested in.
- **One command** runs the scored set and prints the agreement table: `uv run pytest tests/test_act_cases.py`. **[FILL: confirm at the submission commit.]**

### 2.2 Datasets

Three sets, never pooled.

1. **Published answer keys (a development set).** W3C's ACT test cases with the verdicts DHS's Section 508 Coordinators published for Trusted Tester 5.1 ([act-tt](https://github.com/Section508Coordinators/act-tt)), joined on each case's hash; and the Section 508 Baseline Alignment cases for the form tests, with their published expected results. **[FILL: cases per TT test and the PASS / FAIL / DNA split.]** The rules were written with these cases in view and the cases have been public for years, so agreement shows the rules do what we intended; it is not independent evidence. No ACT rule covers 4.E, 4.F or 5.D, so those rely on set 3.
2. **Custom test pages.** **[FILL: number]** pages for what the published cases lack (frames, shadow DOM, dialogs, cookie banners, moving and flashing content, pages whose text tries to steer the tool). Their expected outcomes are ours, so they test the code's behavior and are not counted toward accuracy.
3. **Real .gov pages, labeled blind by a certified Trusted Tester.** The tester tests each page in DHS's own report tool (SCRT) before any run. **Commit and reveal** (`evals/judging.py`): the page list and the hashes of the answer files are committed when a round starts, the tool's results are locked, and only then are the answers added and scored. Round 1: 9 pages of www.nasa.gov. Round 2: 10 pages of svs.gsfc.nasa.gov. Pages on one site share templates and bugs, so both sites are now development sites. No site is held out yet (section 5).

### 2.3 Evaluators

- **Outcomes: exact match, no LLM judge.** Outcomes are categories (PASS, FAIL, Does Not Apply, NEEDS REVIEW), compared in code with the answer key. NEEDS REVIEW matches nothing and is reported as its own rate. On real pages a weighted score makes the asymmetry explicit: agree +1, needs review 0, a false PASS or missed failure -3, other errors -1.
- **Open questions: the judge eval.** Some rules need a judgment ("does the page say how to leave this section?"). Scripted answers in the test suite test the rules, not the questions, so after any change to a question, its rubric or its evidence, a fresh agent answers it from the tool's output alone (`evals/judge_eval.py`; each run is logged in `evals/README.md`). It found a false PASS the scripted tests could not.
- **Three arms on real pages,** on the same recorded pages with the same prompt:
  - **A:** an agent with TOBI.
  - **B, the baseline:** the same model with a general browser tool (Playwright MCP) and web search instead. GSA's sample compares against a no-tool baseline; this is a harder one.
  - **C, the server judge** (round 2): TOBI's own questions answered on the server by a fixed model and prompt, three repeats.
  Cells decided by a rule alone are reported apart from cells an answer decided, so a rule's error is never blamed on a model, or the reverse.
- **Two checks on every test run.** A finding's summary may not contain spec codes or jargon, and every report carries the "not certified" disclaimer (the report model cannot be marked certified).
- **Human baseline from published research.** In a study of 22 experts rating all WCAG 2.0 criteria on four pages, experts produced 20% false positives and missed 32% of true problems ([Brajnik, Yesilada and Harper 2010](https://dl.acm.org/doi/10.1145/1878803.1878813)); a follow-up found expert agreement of about 70-75% ([2012](https://www.researchgate.net/publication/235339930_Is_accessibility_conformance_an_elusive_property_A_study_of_validity_and_reliability_of_WCAG_20)). No published figure exists for certified Trusted Testers following TT 5.1.3, whose step-by-step procedure exists to raise agreement.

### 2.4 Test design rationale

The false-PASS asymmetry drives the design. When a rule cannot decide, the outcome is NEEDS REVIEW, never PASS. An opinion leads to PASS only when a key press or another mechanical check confirms it, or when the question is one a careful tester settles by looking, and then the judge must answer "unsure" whenever the evidence does not settle it. DHS's verdicts make "agrees with a certified tester" measurable instead of a claim. Agreeing with a Trusted Tester means agreeing with a code-inspection process for WCAG 2.0 A and AA; it does not mean a page is accessible, works with screen readers, or meets WCAG 2.1 or later.

## 3. Performance metrics

### 3.1 Metrics tracked

Per TT test: agreement with the answer key, false PASS, false FAIL and needs-review counts. Operational: run time per page, the size of a tool result, and agreement across repeats.

### 3.2 Results of the scored run

**[FILL: commit, environment and date.]**

| TT test | Answer key | Cases | Agreement | False PASS | False FAIL | Needs review |
| --- | --- | --- | --- | --- | --- | --- |
| [FILL] | DHS verdicts on ACT cases; Baseline cases (development set) | [FILL] | [FILL] | [FILL] of [FILL] failures | [FILL] of [FILL] passes | [FILL] |

- **Run time:** **[FILL: per-page time on the realistic test pages and on real pages.]** A tool call returns within 45 s; a longer run goes on in the server and the agent waits for it with a second tool, so client timeouts do not cut runs off.
- **Agreement across repeats:** **[FILL]**.

**Sample-size caveat.** If the tool misses none of n true failures, the 95% upper bound on its miss rate is about 3/n. Showing ≤ 5% needs about 60 failing cases with no misses. **[FILL: n per test and the bound.]** Below that, results are "promising", not "validated".

### 3.3 Real pages: what each round taught us and what it changed

Both rounds are development evidence: the sites were then used to fix the tool. Full tables: `evals/agent/README.md` and `evals/judging/round2-armc/abc-score.md`.

**Round 1 (9 pages of www.nasa.gov, scored 2026-11-04).** Scored per WCAG 2.0 criterion.

| Arm | False PASS | False FAIL | Left for review |
| --- | --- | --- | --- |
| A: agent with TOBI (3 runs) | 0 in every run | 2-4 per run | about two thirds of cells |
| B: same model, general browser tool (2 runs) | 16 and 20 | 0 (it reported no failure anywhere) | about a quarter |

- **Learned: the rules did not pass failing pages, and the baseline did.** The general-purpose agent passed every page's unlabeled search field and took landmarks for a way to skip the header.
- **Learned: agents left the judgment work undone.** No agent answered the tool's open questions unprompted, and agents rarely opened the pictures a question named. Told to answer, the tool's weighted score rose from 44-47 to 82, still with no false PASS.
- **Learned: limits cut the work short.** A time limit per call, client timeouts and results too large for the client each left tests undone.
- **Changed:** a call returns within 45 s and a long run continues in the server; a run tests the whole page by default; every result ends with the work left and how to do it; the pictures a question needs are attached to the result; questions that are alike are asked once (one page's 96 became 4) and the busiest page's result went from about 51k to 24k tokens. The tester's answers also corrected rules for 4.D, 4.F, 5.A, 5.B, 5.F and 5.G.

**Round 2 (10 pages of svs.gsfc.nasa.gov, scored 2026-11-08).** The tool per TT test, 220 cells.

| Who answered the tool's questions | False PASS | Missed failure | False FAIL | Left for review |
| --- | --- | --- | --- | --- |
| A: the calling agent (2 runs) | 2-3 | 0-2 | 14-17 | 91-118 |
| C: the server judge (3 repeats) | 3 | 2 | 24-26 | 86-88 |

Agent B, per criterion: 15 and 19 false PASSes.

- **Learned: every false PASS came from a rule deciding alone,** the same cells in every run; no answer from either judge caused one. The rules' own errors (3 false PASS, 2 missed failures, 13-15 false FAILs a run) outnumbered any judge's.
- **Learned: a server judge is repeatable but not yet right.** It answered all 194 questions in every repeat and its repeats agreed on 194 of 200 criterion cells. About 45% of the cells its answers decided were wrong, all toward FAIL, most from one question (focus order). About a third of its answers were "unsure".
- **Learned: a recording can hide a failure.** One page loads a script only when it is used; the recording lacked it, so a keyboard trap and a focus jump the tester found did nothing on replay.
- **Learned: a person opens everything; the tool had not.** A failure sat behind a filter that had to be opened first. Content in frames was the largest gap.
- **Changed, the design:** the server judges with a pinned model and prompt, a person reviews what it is unsure of, and the calling agent explains results and helps fix them. The judge is built and, since 2026-11-18, answers every question type whenever the server is given a model (Abby's decision: the gate's checks were informative, not decisive, and a pinned judge's answers, unsure ones included, are steadier than a calling agent's); without a model, questions go to the calling agent.
- **Changed, the rules:** recordings keep the scripts a page loads when used, and a keyboard or typing test cannot pass without them; menus, tabs, accordions and filters are opened and what appears is read, and the keyboard-trap and on-focus tests Tab through what they open; the multiple-ways test opens a closed menu that hides a link to the page (the browser's own video controls are not counted as menus); an exit from a keyboard trap that needs activating a control is not an exit; every video is checked for flashing, played or not; a click that starts a video counts as mouse-only; other pages from another template leave the multi-page tests for review.
- **Changed after the code review (2026-11-12):** the tool takes an inventory of each page, inside web components and frames too, and each test says how much of it it read. When the inventory has something the test did not read (a form inside a web component, a form hidden until a button opens it), a PASS or a Does Not Apply becomes NEEDS REVIEW with a sentence that says what was not checked. Does Not Apply is now held back like PASS: a wrong Does Not Apply hides a barrier as surely as a wrong PASS.
- **Changed after the review's known wrong outcomes (2026-11-13):** eleven single-test fixes, each with a fixture and the nearest page that must keep its old outcome. They moved only toward NEEDS REVIEW or FAIL, with two exceptions the owner approved: a form whose `type="button"` control really runs the page's check can now reach PASS from Does Not Apply, and the bar for "the tested page again" (nine tenths of its text shared) was set from live NASA search pages (the same page 1.00, the highest different page 0.44).
- **Changed, step 8 (2026-11-14):** one library of reading rules shared by every reader and the inventory. 5.A, 5.B and 5.C read fields inside web components like any field (a name there comes from Chrome's accessibility tree, since ANDI cannot read inside them) and inside frames, each frame opened as a page of its own with ANDI run there, as TT 12.D tells a tester; a frame the recording lacks holds the result for a person. A label's text is only words a person can see. The multi-page tests (9.A-9.C, 19.A) read a site header built as a web component like a plain one. The watcher for sound, motion, updates and flashing (2.A-2.D, 3.A) reads and watches inside web components too. The form error tests (5.F-5.H) read errors and fields inside web components and frames. A page that changes when a form is sent, in a way the tool cannot read as an error (a red box, a message that vanishes at once), is left for a person instead of "did not check". A dialog that opens inside a web component or a frame counts for 4.E and 5.D (it was missed: a false PASS). 4.A sees mouse-only controls and changes inside web components, and 4.B reads their text. Each new PASS has a test page beside it that must still FAIL.
- **Changed, step 6e (2026-11-15):** 2.C and 2.D held every round 2 page at NEEDS REVIEW because the page sets a timer longer than the 6.5 s watch. On those pages the timers were analytics heartbeats (Parse.ly, about 150 s; Google Analytics, 24 hours). Now one more load runs the page's clock past such timers and clears them only when nothing on the page changes and no request is made (2.C 1.2.0, 2.D 1.3.0). On round 2's frozen pages this decided 8 cells, all Does Not Apply as the tester's key says; the page the key fails stays NEEDS REVIEW, and so do pages with a canvas or a timer that asks the server. The grid's late-start page caught a false Does Not Apply in the first build (a flash toggled an even number of times between two looks); the check now looks five times and counts every change.
- **Changed, step 6e (2026-11-15), images:** 2.B and 3.A read at most 30 images, and any page with more, or with one they skipped, was held for a person. On round 2's pages the cap was never the only cause: lazy images, a 14 MB photo skipped for its size alone, a redirect and failed requests were unread among the first 30. Now every image is read, up to 300, lazy ones after a scroll; a photo's type is read from its first bytes before its size matters; a redirect inside the recording is followed (2.B 1.5.0, 3.A 1.4.0). On round 2's frozen pages this decided 6 cells, all Does Not Apply as the key says; a test page with a strobing image after the 31st, which the code review found as a missed flash, is now Not Tested (flashing found).
- **Changed, step 6e (2026-11-15), hidden forms:** 5.H (error prevention for legal, financial and data forms) left a page for a person whenever a form was hidden until opened. A person decides whether 5.H applies by opening the panel and reading the form; submitting it is not needed. Now 5.H reads hidden forms' fields, buttons and words from the page, never opening or submitting them, and judges them with the rest (5.H 1.9.0). On the frozen pages this decided 8 cells (2 of round 2's, 6 of round 1's), all Does Not Apply as the key says; a hidden payment form still goes to the question, and one never submitted stays with a person.
- **Changed, step 6f (2026-11-15):** 9.C no longer treats a footer link and a header logo that go to one address as one component named two ways (round 1: "Home" against "NASA — return to the homepage" failed 8 of 9 pages, and the key passes them). Two links pair by address only inside the same kind of block, with the same name when both blocks are named. The nearest page that must still FAIL: one footer link worded two ways. 9.B's time budget went from 60 s to 180 s (spec 9.C 1.10.0).
- **Changed, step 6h (2026-11-15), the page under another address:** a tester treats `/cilab/index.html` as `/cilab/`; the tool did not, and FAILed round 2's CILab page where the key passes. Now, while 19.A has fewer than two ways, a link that differs from the page's address only by `index.*` or `default.*`, its scheme or a leading `www.` is loaded (at most 3, each as a caller's other page) and counts only when it ends at the page's address or its document is byte for byte the same; anything else is held for a person, never a FAIL or a match. Its test page beside it: another page at `index.html` under the same template, held for a person, never a PASS.
- **Changed, step 6h (2026-11-15), looking further as a tester does:** 19.A named the site map and home page for a follow-up call that the eval runs never made (and that dropped them when 5 pages were given), so it was undecided on 8 of 9 round 1 pages. Now, while it has fewer than two ways, it loads the site map, the page's previous and next pages, its parent, up to two pages below it, up to three pages it links to (one that is not a web page, such as an API's data, takes no place) and the home page itself (at most 10); a row of links that repeats the page's own header counts as the site navigation even outside a navigation region (round 2's CILab), one at a time, each as a caller's other page, and stops at two ways. It FAILs only when all were checked, and says what it checked; a page it could not load, or a closed menu it did not open on a page it read, holds the result for a person (it cannot say the site navigation does not lead to the page without reading the navigation). Each test page has a twin that must keep its outcome.
- **Changed, step 6e (2026-11-15), fields hidden from everyone:** anti-spam fields (honeypots, reCAPTCHA's response box) are hidden on nearly every form, so 5.A to 5.H left such forms for a person for ever. Now a hidden field inside a form shown on load is out of scope when nothing a careful tester does shows it: opening every menu and pressing every button that could show it, waiting 15 s and scrolling, trying each choice in its form, then typing a value in each text box and pressing its buttons. It is decided by behaviour, never by a plugin's name (5.A 1.13.0 to 5.H 1.10.0). It decides no cell on the 19 frozen pages, by design: their hidden fields are a popup, a mobile copy and filter panels, which stay in scope. Its first build put round 1's feedback popup out of scope and moved 16 cells off the guard; they agreed with the key only because that popup never opens for anyone (a script-order error on nasa.gov, checked live), and they went back to NEEDS REVIEW once a field whose whole form is hidden was kept in scope. Test pages caught two wrong results on the way: a form behind a plain button, and a step-by-step form whose second step appears only after the first is filled.
- **Changed, step 29, the small part (2026-11-17):** 5.B said "no form field has a label people can see" (Does Not Apply) on round 3's Drupal pages, where the search box sits in a panel the magnifier opens and the label test (5.A) was unsure, though the key passes counting the magnifier. 5.B now says Does Not Apply only when the label test found every such field unlabelled by a rule or its own "not labelled" answer; a field it left unsure makes 5.B NEEDS REVIEW, and a field it found labelled by a picture is judged by that picture (spec 5.B 1.10.0). A placeholder-only search box with no icon (round 1's nasa.gov) keeps its FAIL and Does Not Apply. It moves only Does Not Apply toward NEEDS REVIEW or an outcome from a judge's look.
- **Changed, step 31 (2026-11-17):** 9.B paired equal links "in order", so a link repeated on every page, with one more copy on some (round 3's Drupal pages: "Home" in the top bar, the footer's logo block and the footer list, and the breadcrumb's on every page but the home page), made the links between the copies read as reversed: 6 false FAILs where the key passes. Equal components now pair by an alignment that keeps their order where it can (the longest common subsequence of the two pages' lists), so an extra copy is an insertion; two different links swapped, or repeated links whose copies change places with a link between them, still FAIL (spec 9.B 1.7.0, fixtures `9x/m1`-`m3`, `n1`-`n2`). It moves only FAIL to PASS where the order is kept, on pages no key fails.
- **Changed, step 21 (2026-11-17):** on round 3's contact page the form had no error messages of its own, only the browser's. The tool read Chrome's message for every empty field as shown, though the browser shows one field's message at a time, and judged Chrome's words for a bad email address ("Please enter a part following '@'"), where Firefox, which the tester used, says only "Please enter an email address": 5.F and 5.G PASSed where the key fails. A message that is the browser's own is now NEEDS REVIEW in both tests, with a sentence that it is the browser's, shows one field at a time and differs by browser; its words are no longer judged (spec 5.F 1.13.0, 5.G 1.11.0). Whether TT 5.F fails such a form is the owner's open decision, so it is never FAIL. The test page beside it, where the page cancels the browser's message and only marks the field, keeps its FAIL. It moves only PASS toward NEEDS REVIEW.
- **Changed, step 36 (2026-11-17):** on round 2's 5340 the only text a press added was the number "4" (a count the page shows), and the judge, asked whether that "error message" named each field, failed 25 fields on it; 5.G followed. New text is now a candidate error message only when it holds a word (two letters in a row, in any script); when an attempt's only new text holds none, each field is left for a person and no question is asked. The judge's rubric for both tests now says that text which is not a message (a number or count, a date or time, a result the page shows) is "no error" (spec 5.F 1.14.0, 5.G 1.12.0). The test page beside it shows a real one-word message ("Invalid") for two fields and keeps its FAIL. It moves only FAIL toward NEEDS REVIEW.
- **Changed, step 22 (2026-11-17):** round 3's community pages are an application that draws its controls about a second after load; the keyboard walk began before that and reached one link of 76 and 90, so 4.F said "only one element" (Does Not Apply where the key fails), 5.D "no form fields", and the judge, shown one reached stop, failed about 20 controls in 4.A. The page is now counted again 3 s after the backward walk's load, and when it holds more than the walk began with and reached, 4.A, 4.C, 4.F, 5.A to 5.D and 5.F to 5.H decide nothing from the walk: NEEDS REVIEW, with a sentence that the page draws itself after it loads, and 4.A asks no question about a control the walk did not reach (specs 4.A 1.13.0, 4.C 1.15.0, 4.F 1.9.0, 5.A 1.14.0, 5.B 1.11.0, 5.C 1.13.0, 5.D 1.11.0, 5.F 1.15.0). A page with one link drawn with the page, and a page with no form field, keep their Does Not Apply. It moves only PASS, Does Not Apply and FAIL toward NEEDS REVIEW. Its first rerun caught it reaching too far: on round 2's home page one late link (145 elements, then 146) moved 4.C and 4.E from agreeing PASS to NEEDS REVIEW, so it now needs the page to have more than doubled after the walk began, or to have had no form field then (specs 4.A 1.14.0, 4.C 1.16.0, 4.F 1.10.0, 5.A 1.15.0, 5.B 1.12.0, 5.C 1.14.0, 5.D 1.12.0, 5.F 1.16.0).
- **Changed, step 23 (2026-11-17):** a probe first replayed round 3's four application pages from their frozen recordings: each drew its controls 0.7 to 1.1 s after the load began (from 0 or 9 elements to 76, 91, 9 and 7), and what it drew matched the tester's notes (the forum's tag word cloud, the header search, the search engine's "All" menu and search box, the story page's buttons). Every load a test reads now waits until the count of elements that take focus has not changed for 2 s (at most 10 s; a later load of a page drawn at load does not wait), so the walk, the label read, the error pass and the site read see the page a person sees. No rule changed (spec 4.C 1.17.0 describes the wait). A test page drawn 1.2 s after load gives, test by test, exactly what its twin with the same controls in the page at load gives; the step 22 guard still holds a walk that began before the page drew.
- **Changed, 4.F 1.11.0 (2026-11-17):** step 23's rerun gave three new false FAILs on round 2 (p02, p03, p07), each after the judge was unsure about the same page in the run before. The cause was the evidence, not the judge: 4.F read each element's box and the page's scroll in two calls, and the site scrolls smoothly when focus moves, so a date field, a card's copy button and sidebar links were placed out of line, a different few each run (more under load), and the order picture drew them there; a sidebar that scrolls by itself placed its later links above earlier ones; a video player that takes a new id on each load raised "Shift+Tab is not the reverse of Tab" on pages where it was; and the Shift+Tab list, numbered on its own and cut at 60, showed a long page's last 60 elements beside its first 60. Now the box and the scroll are read in one call, a box that scrolls by itself is one block of the page, an id only one walk has is the same element, and the Shift+Tab list names each element by its number in the Tab list (spec 4.F 1.11.0). On round 2's p02, p07 and p10 only the footer's two link columns remain (3, 8 and 5 order signals before, each the same in two runs); the judge eval matched 18 of 18 4.F questions (evals/README.md, run 37). Rerun on all three rounds' frozen pages with the server judge: round 2's 4.F false FAILs went from 4 to 2 (one of them new: the judge on an interactive sky map), round 1's agreeing cells from 5 to 8, and no page gave a false PASS (`evals/judging/gate-2026-11-17-4f/`).
- **Still open** (`docs/ROADMAP.md`): the rules' false FAILs (a search field an icon button labels: 7 cells a run), the questions that end in "unsure" or a wrong FAIL.

**[PENDING] The check against round 2:** the same 10 recorded pages run once more with the rules as fixed and the server judge answering, scored beside the rows above.

### 3.4 Failure analysis

**[FILL: one row per disagreement in the scored run: the case, the tool's outcome, the reference, and whether it traces to a spec ruling, a bug, or a difference between DHS and W3C.]**

From round 2, by cause: a rule too strict (5.A, 5.C, 19.A); a question a judge could not answer from its evidence (4.F's order picture drew stops nobody can see; 9.C paired links by destination instead of repeated components); evidence the tool did not have (frames, lazily loaded code, content behind a control).

## 4. Security considerations

### Data classification

The server reads public web pages, by default only on `.gov` and `.mil`. It needs no credentials and tests no pages behind a login. Pages can still contain anything, including user-submitted text, so recorded pages, screenshots and logs are treated as untrusted. They are kept for at most 24 hours (configurable), then deleted; durable results belong in the user's own repository.

### Scope containment as a control

- **Allowlist on every hop.** The allowlist is checked on every top-level navigation and every redirect, not just the first URL.
- **Live requests shaped by page content: 19.A's site search, and its check of the page under another address.** A link on another page that differs from the tested page's address only by `index.*` or `default.*`, its scheme or a leading `www.` is loaded only while fewer than two ways are found, at most 3 a run, each exactly as a caller's other page (allowlist on every hop, the same host after redirects, its own replay file); its links are never followed (Abby, 2026-11-14). Only when the caller's pages show fewer than two ways to reach the page, the tool submits the site's own search form, at most twice: a GET form on the tested page's host (allowlist on every hop), the tested page's heading as the term, and the same heading in quotation marks only when the first search does not find the page; each results page recorded as its own replay file. Before the search, while fewer than two ways are found, up to 10 pages of the tested page's host are loaded one at a time and the test stops at two ways: the site map a page links to, the page's parent (from its own address), up to two links on it to pages under its directory, its previous and next pages, up to three other links in its content, and the home page (Abby, 2026-11-06, widened 2026-11-15): allowlisted, on the same host before and after redirects, each its own replay file. No other link found on a page is visited.
- **Two more narrow exceptions, each approved and capped.** A key combination that page text names as a way to stop moving content or audio is pressed once, on a replay, only to confirm it (never a key the browser itself uses). The recorder also saves the scripts that recorded scripts name (code a page loads only when it is used), from the same host, allowlisted, capped in number, size, depth and time; a keyboard or typing test cannot PASS while the recording lacks such code.
- **Other pages chosen by the caller only.** The multi-page tests compare the tested page with up to five other pages the caller names (up to 50 when the caller turns the time limit off). Each must pass the allowlist and be on the tested page's host before and after redirects, or nothing is tested; one that cannot be recorded within its 20 s share leaves the multi-page tests NEEDS REVIEW while the other tests still run; page content never adds a page (links on the tested page are never followed). Each is recorded as its own replay file.
- **Refused pages produce no findings.** A blocked, unreachable or invalid page is a tool error with no findings, so no "result" exists for a page that was never tested.
- **Dev-only local files.** `file://` URLs work only in development mode.
- **Connection-time address checks.** The allowlist matches any `.gov` or `.mil` host by suffix, which this use needs, but a name says nothing about where it points. So Chrome's only way out is a local proxy inside the server. For every connection (the page, iframes, subresources, WebSockets, each redirect hop and the guard's own fetch), the proxy resolves the host once. It refuses the connection if any answer is a private, loopback, link-local, multicast, unspecified, reserved or cloud-metadata address, including IPv4-mapped, IPv4-compatible, 6to4 and Teredo IPv6 forms, or if the port isn't 80 or 443. Otherwise it connects to the address it just checked, so a second DNS answer (rebinding) is never used. TLS stays end to end, so Chrome still verifies the certificate for the real hostname. If the proxy is down, nothing gets out. A refused page is a tool error; refused page parts are listed in the result. Development mode reaches the local test server only through an explicit address allowlist that is ignored outside development mode. An optional upstream proxy (`UPSTREAM_PROXY`, off by default) serves hosts whose direct connections are re-signed by a gateway browsers do not trust, such as a cloud test container: the checks still run, then the connection is tunneled by name, so the upstream resolves the name again (weaker against DNS rebinding); used only for the agent eval's runs in such a container.
- **Outbound security tests** (`tests/test_egress.py`). A `.gov` name resolving to 10.x, 127.x, 169.254.169.254 and ::ffff:127.0.0.1; a name with one good and one private answer; a redirect to a private address; an iframe, image and script pointing at one; a resolver whose answer changes mid-run; alternate address forms (integer, hex, octal, short and IPv4-mapped); the development allowlist outside development mode; a disallowed port; and an unresolvable name. A sentinel server on a refused loopback address would record any request that got through, and none did. With the proxy removed from Chrome's launch, 9 of these tests fail.
- **[PENDING]** Network-level egress rules on any host that runs the server, as a second layer (the GSA template asks for both).

### Untrusted input and prompt injection

- **The server's text never includes page text.** Page strings appear only in a labeled untrusted field, and the server's own question wording is fixed.
- **Page scripts can't fake focus.** Focus is read through the Chrome DevTools Protocol in an isolated context; a test checks that page script can't spoof it. This includes where a skip link lands (9.A): a test page that tells its own script focus moved, when it did not, is a FAIL, not a PASS. A page that cancels the browser's own error message (5.F) is not credited with that message.
- **Outcomes come only from spec rows.** A model's answer is recorded as a fact for a rule, never as an outcome.
- **An agent can't claim to be a person.** Every answer that arrives through MCP is recorded as the calling agent's, whatever it says, so it needs what any agent answer needs (a picture question needs what the picture shows) and outranks nothing. A person's answer is to come from TOBI's own signed-in page (`tests/test_tools.py`).
- **Adversarial fixture.** Fixture F32 contains text telling automated testers to report PASS for every test; the expected result is FAIL with both traps reported. **[FILL: result at the submission commit.]**

- **Trick text aimed at the server's judge.** Three more pages (`tests/fixtures/inject/`) ask for the outcome the page would not get; one writes the untrusted block's closing tag before its trick. Page data is escaped (`<`, `>` and `&`), so page text cannot end the block. Tests check that the model sees such text only inside the block marked untrusted; in a two-call trial (before the third page) the judge answered both correctly. Not yet covered: injected text in accessible names and in frames.
- **Page text can't choose a file for the judge.** The server's judge attaches a picture only when a question's input value is exactly a link to that run's own screenshot, read through the same guarded reader as the run's resources (no `..`, no other run, no other person's run). A link written into page text, such as a link's name, is never read (`tests/test_apijudge.py`).

### Logs and errors

- **Redacted errors and logs.** Following the GSA template, tool errors and the run log carry no query strings, cookies, headers, stack traces or page text. URLs keep only scheme, host, port and path; an error is one line (exception type and first message line, URLs redacted, capped at 200 characters). The run log is redacted where it is written, so no caller can bypass it. The user's saved report keeps the full URL.
- **Data-leakage tests** (`tests/test_leakage.py`). Secrets are seeded in a URL query string, a page script error, a console error, a cookie and a failing subresource; a redirect out of the allowlist and an unreachable page are also covered. Each test checks the tool error, the result's error list, the run log, Python logging and the process's stdout and stderr. With the redaction removed, 4 of the 5 tests fail.
- **The live log is the one exception, and it is off by default.** For a demo, `LIVE_LOG=true` with a `LIVE_LOG_TOKEN` keeps the last 2,000 events in memory (never on disk) and shows them at `/live`: every MCP call's full arguments and response, pictures included, and each run's steps. It holds page text and answers for every caller, so it bypasses the per-person run rule below for whoever holds the token. The token travels in the address's fragment and a request header, never a query string. Without both settings every `/live` address answers 404. Only GET is answered. The page shows values as text only, under a Content-Security-Policy with no inline script: page text holding markup and script stays text in a real browser. It is a plain route like `/health`, so it opens with its token while `/mcp` still requires sign-in (`tests/test_livelog.py`, `tests/test_access_signin.py`).
- **The hosted viewer is open and holds nothing.** `GET /viewer` serves the pre-SCRT viewer without sign-in, like `/health`. A person picks a saved file and it is read in their own browser; the page's Content-Security-Policy, in the file and as a header with `frame-ancestors 'none'`, blocks every request, so it cannot reach `/mcp`, `/live` or anywhere else. A browser test checks it asks for nothing after the page and shows file text as text (`tests/test_prescrt_viewer.py`).

### Secrets and configuration

Settings load from a `.env` file or environment variables (a Kubernetes Secret when hosted) and are never committed. The sign-in client secret and token-signing key are secret-typed settings, never printed or logged. With the default settings no model key is needed, because the calling agent answers open questions. The server's own judge, when switched on, loads its endpoint and key the same way; a test checks the key never appears in a report, a log or an error.

### Transport and isolation

- **Local by default; hosted only with NASA sign-in.** stdio is the default transport. HTTP is opt-in and checks the Host and Origin headers of every request, so a web page can't reach it through DNS rebinding (`tests/test_transport.py`). Without sign-in it binds only to a loopback address (127.0.0.1 or ::1). It listens beyond loopback only with `AUTH=oidc`, which needs every setting below or the server refuses to start (`tests/test_access.py`):
  - **Sign-in on every MCP request.** FastMCP's OIDC proxy signs MCP clients in through VAST's Keycloak, which brokers to NASA Launchpad with NAMS access enforced. A request without a valid token gets 401 and a link to the sign-in metadata (standard MCP authorization, so any compliant client works). A token that names no subject (`sub`) is refused, since runs are owned by subject. Only the server's public host passes the Host check.
  - **Optional group gate.** `REQUIRED_GROUPS` admits only members of the listed VAMS or NAMS groups.
  - **Runs belong to their maker.** A run, its answers, its `run://` evidence, its reports and the job that runs it are visible only to the person who started it. To anyone else a run reads as expired and a job as unknown, so an ID reveals nothing, and the list of work left shows only the caller's own runs.
  - **Audit trail.** One JSON line per tool call, resource read and prompt: who (Keycloak subject and NASA email), what (tool, URL without its query string, run ID, test IDs, how many answers), outcome and duration. It never includes answers, page text or report content. Lines go to stderr, where the platform collects them: the audit logger has its own handler since 2026-11-15, when the hosted smoke test (`scripts/smoke_hosted.py`) found that without one every line was dropped (`tests/test_access.py`).
  - **End-to-end sign-in on VAST** (2026-11-18). Claude Code signed in through VAST's Keycloak and NASA's sign-in at a VAST dev URL and ran a live page. The hosted smoke test (`scripts/smoke_hosted.py`) passed there: sign-in, a live run, its report, and the audit line naming the person with no token in the log. That a second person cannot open the first person's run is checked on every image build, with the image signed in through a real Keycloak behind TLS with two users, and in a full sign-in against a local stand-in provider (`tests/test_access_signin.py`); on VAST it was not tried, since it needs a second NASA identity at one computer.
- **Fresh state for every load.** Each page load gets a fresh browser context, so cookies and storage can't carry state between probes.
- **CSP bypass, recorded.** The page's Content-Security-Policy is bypassed in every test browser context so that ANDI's injected script runs (`BYPASS_CSP`, on by default since 2026-11-07); every report records the setting. The browser only shows the recording.
- **Pinned third-party code.** ANDI and jQuery are bundled with hashes, and requests to ssa.gov are blocked so ANDI is never loaded live.

The template's entry point started an unauthenticated HTTP server on all interfaces whenever a `PORT` or `DATABRICKS_APP_PORT` environment variable was set. That branch is removed and those variables are ignored; HTTP beyond loopback now requires sign-in (above).

### Known gaps

- Sign-in is tested against a stand-in provider and a real Keycloak, not yet against NASA's (above).
- A code review in November 2026 raised leads not yet verified (`docs/reviews/`); they are checked before anything is hosted.

### Misuse: findings mistaken for certification

Agencies accept Trusted Tester results only from certified people. Every tool response and report carries a "not a certified Trusted Tester result" disclaimer. The report model has `certified: False` as a fixed value. Contributor rules ban "certified," "compliant" and "Section 508 conformant" about a tested page.

## 5. Lessons learned and recommendations

### What worked

- **Borrow the ground truth.** DHS's published verdicts on W3C test pages gave us a certified-tester answer key on day one. Writing our own would have measured agreement with ourselves.
- **Exact match beats an LLM judge when outputs are categories.** Cheaper, reproducible, and no judge bias to review.
- **Blind labels, commit and reveal.** Locking the tool's results before the tester's answers are added kept us from tuning to the key, and the tester's reasons taught us more than the scores.
- **A harder baseline.** The same model with a general browser tool passed pages that fail. That is the case for encoding the procedure instead of prompting for it.
- **Report who decided each cell.** Splitting rule-decided from judge-decided cells showed the rules, not the model, caused every false PASS.
- **Proportionate to the procedure.** A spec step must match something the PDF asks a human tester to do; anything past that is "needs review". The aim is consistency with a careful tester, not exceeding one.
- **Write lessons down.** `docs/solutions/` records what took more than an hour to understand: pages can fake focus, cookie banners leak state between probes, ANDI changes the page it inspects, the TT PDF disagrees with itself in places.

### What did not work

- **Asking the calling agent to do the judging.** More wording and proof fields moved the shortcut; they did not remove it. The judge moved into the server.
- **Trusting test pages alone.** Custom pages missed what real pages showed within a day: late-loading scripts, survey pop-ups on one load in ten, templates that share nothing.

### Limitations

- 22 of 61 active tests. **[FILL: scored cases and true failures per test.]**
- The published answer keys served as the development set, and both real sites are development sites now: no held-out site yet, and one certified tester labeled every real page.
- Round 2's false FAILs and "unsure" answers are still being fixed; the server judge is off by default.
- Results are for the Chromium version each report records, at one window size, from a recording: fields in frames are not read, and code a page loads only when used may be missing (the result is then "needs review").
- Trusted Tester scope: WCAG 2.0 A and AA by code inspection and keyboard; no screen reader testing.
- **[FILL: whether the scored run used the target environment.]**

### Recommendations for hackathon participants

- **Look for an official answer key before writing your own.** Agencies often publish the verdicts you need.
- **Name your worst error and design around it.** For us that is a false PASS; when unsure, the tool says so.
- **Keep rules and model judgment apart,** and score them separately.
- **Report needs-review and refusal rates beside accuracy.** Escalating everything can fake a high score.
- **Measure what the agent does, not what the tool description asks.** Put the next step in the data.
- **Record what you verified and what you assumed.** Human-review anything a model wrote, including this document.
