# Code review, 2026-11-11: what to fix, in order

A triaged list from a line-by-line review of `tobi508`, for Abby to review
and hand to other threads. Nothing here has been fixed; this thread changes
no code.

**Progress.** Phase 0 is done (the first attempt's leads, checked). Phases
1 to 4 add the files nobody has reviewed yet; phase 5 adds the "if we
started over" section. Each phase is committed when it is checked.

| Phase | Covers | State |
| --- | --- | --- |
| 0 | Leads from the first attempt (tools, pipeline, traverse, 9.B/9.C/19.A, evals) | done |
| 1 | Security files; what an agent receives, measured; the rest of tools and pipeline | not started |
| 2 | 4.A-4.F and 5.A-5.D against their specs | not started |
| 3 | 5.F-5.H, 9.A, 2.A-2.D, 3.A and the watchers | not started |
| 4 | The rest of the core; tests, CI, Dockerfile, packaging | not started |
| 5 | "If we started over"; final ordering | not started |

**How each item was checked**

- **Verified (run):** I reproduced it with a test run or a script; the
  item says which.
- **Verified (read):** I read the code and the callers and agree; not run.
- **Reviewer's claim:** a reviewer reported it and I have not checked it.
  All P0 and P1 items are verified one way or the other, or say why not.
- **Refuted:** checked and wrong; listed at the end so nobody chases it
  again.

**Priorities.** P0: a false PASS or a wrong DOES NOT APPLY on real pages,
or a security hole. P1: a wrong result, crash or hang in plausible
conditions, or large waste. P2: moderate waste, or a gap that stays
NEEDS REVIEW. P3: cleanup. Inside a priority, what touches the Nov 20
demo or what a calling agent sees (tokens, time) comes first.

IDs (A-01, D-03 and so on) are handles for other threads to cite. The
letter is the review group: A tools and models, B pipeline and judge,
D the keyboard core, K 9.B/9.C/19.A, L evals.

---

## P0

Six items. Four give a wrong outcome on any page built with web
components; two are security holes that open only in a mode that is off
by default (hosted sign-in, the server judge) but that the demo plan
turns on.

### D-03 4.A passes a page whose mouse-only control is in a shadow root

- **What is wrong:** 4.A finds mouse-only controls by asking Chrome for
  the click handlers in the document. The request does not look inside
  shadow roots, so a control with a click handler inside a web component
  is never seen.
- **Why it matters:** a false PASS. The same control in the ordinary DOM
  raises a question; inside a shadow root the test says "we found nothing
  a keyboard user would miss". Design systems built on web components
  put every control in a shadow root.
- **Where:** `src/tobi508/traverse.py:515-518` (`getEventListeners` with
  `pierce: False`); used by `src/tobi508/checks/t4a.py:391-401`.
- **Smallest fix:** also read listeners from each open shadow root (or
  `pierce: True`, keeping only this frame's nodes). Until then, when the
  page has any shadow root, add a coverage note so 4.A cannot PASS.
  Fixture: one clickable `<span>` in a shadow root.
- **Checked:** verified (run). Two one-control pages, same handler: in
  the ordinary DOM, 4.A is NEEDS REVIEW with question `4.A-k1-J1`; in a
  shadow root, 4.A is PASS (rows A3, G4).

### D-01 5.A, 5.B and 5.C say "no form fields" when the form is in a shadow root

- **What is wrong:** the label pass lists form fields with a plain
  `document.querySelectorAll`, which does not enter shadow roots. Fields
  in frames get a "not checked" note; fields in shadow roots get nothing.
  With no fields and no note, the three tests return DOES NOT APPLY.
- **Why it matters:** a wrong DOES NOT APPLY on any page whose inputs are
  web components. `docs/ROADMAP.md` ("Known limits") says this case is a
  NEEDS REVIEW note; for shadow roots it is not.
- **Where:** `src/tobi508/labels.py:53` (`comps()`), `labels.py:361-380`
  (only frames add a note); `src/tobi508/checks/t5a.py:238-243` and the
  same branch in `t5b.py` and `t5c.py`.
- **Smallest fix:** in `read_session`, count fields inside open shadow
  roots (the walk's inventory already does) and add an "N form fields
  inside web components were not checked" note, as for frames. Reading
  them properly is the second step.
- **Checked:** verified (run). A page with a text field, an email field
  and a button in an open shadow root: 5.A, 5.B and 5.C all DOES NOT APPLY
  ("This page has no form fields"). On the same page 5.D sees the two
  fields, and 5.F, 5.G and 5.H are NEEDS REVIEW ("2 form field(s) could
  not be read"), which is the safe answer.

### K-01 An "other page" that is the tested page under another spelling gives 9.B and 9.C a PASS

- **What is wrong:** the tool refuses an other page only when its text
  equals the tested page's text. A query string, a trailing slash, http
  for https, or a URL that redirects to the tested page all get through.
  After loading, only the host is compared.
- **Why it matters:** the page is compared with itself. Everything
  matches in the same order with the same names, so 9.B and 9.C PASS on
  no evidence. An agent that passes `https://x.gov` and `https://x.gov/`
  gets there without meaning to.
- **Where:** `src/tobi508/pipeline.py:319` (text comparison) and about
  line 1000 (after recording, host only).
- **Smallest fix:** after recording, refuse an other page whose final URL
  (fragment dropped, trailing slash and scheme ignored) equals the tested
  page's final URL, and drop duplicates among the other pages the same
  way. One fixture.
- **Checked:** verified (run). Tested page `site-a.html`, other page
  `site-a.html?x=1`: 9.B PASS (row N6), 9.C PASS (eight pairs, all C1).

### K-02 Navigation inside a shadow root or a frame is invisible to 9.B, 9.C and 19.A

- **What is wrong:** the site read walks `el.children` only. A header or
  menu built as a web component, or placed in a frame, yields nothing.
- **Why it matters:** 9.B and 9.C answer DOES NOT APPLY ("no navigation
  on this page appears on the other pages") and 19.A answers FAIL ("no
  way to reach this page") for a site whose shared header is plainly
  there. Nothing in the result says content was skipped. 9.A has a frame
  guard; these three have none.
- **Where:** `src/tobi508/site.py:124-162` (`walk`); the DNA and FAIL
  branches at `checks/t9b.py:200-214`, `checks/t9c.py:471-477`,
  `checks/t19a.py:422-438`.
- **Smallest fix:** count shadow roots and frames while reading each page
  and, when there are any, make these DNA and FAIL branches NEEDS REVIEW
  with the count (the way the cap rule N1 works). Walking open shadow
  roots is the second step.
- **Checked:** verified (run) for shadow roots: two pages sharing a
  `<site-header>` web component with a three-link menu gave 9.B DNA,
  9.C DNA and 19.A FAIL. Frames: verified (read) only.

### A-01 Hosted mode: one signed-in user can list and collect another user's run

- **What is wrong:** jobs are kept in one list for the whole server, with
  no owner. `tobi_run_status` with no `job_id` lists every job still
  running, for every user, with its job id and URL. Anyone can then wait
  on that job id and receive the finished result. Run folders are
  protected by an owner check; the job's result is not.
- **Why it matters:** with `AUTH=oidc` this leaks which pages another
  person is testing and their findings and page text. It is the first
  thing to close before the VAST step of the demo plan.
- **Where:** `src/tobi508/jobs.py:57-58, 98-99`;
  `src/tobi508/tools/run_status.py:75-96`;
  `src/tobi508/pipeline.py:1572-1585` (`outstanding`).
- **Smallest fix:** store `access.caller()` on the job when it starts;
  `get`, `all_jobs` and `running` return only the caller's jobs. A test
  beside `tests/test_access.py`.
- **Checked:** verified (read). `Job` has no owner field; `outstanding`
  adds running jobs to its list before any owner check. Not exercised
  with two real tokens.

### B-01 Server judge: a page can make the server read picture files outside the run

- **What is wrong:** the server judge collects every `run://...png` it
  finds anywhere in a question's input and opens it as a path under the
  run folder. Question inputs hold page text (names, labels, links). A
  page that puts `run://x/../../other.png` in a link's name makes the
  server open that file and send it to the judging model. The run id in
  the link is ignored.
- **Why it matters:** page content chooses a file the server reads
  (principle 5), and in hosted mode it reaches another user's
  screenshots, past the owner check. Only `.png` files, and only when
  `JUDGE_BACKEND=api` with a type switched on, which is what the round 2
  check in the demo plan does. The pictures attached to agent results go
  through the guarded reader and are not affected.
- **Where:** `src/tobi508/apijudge.py:380-416` (`_links`, `pictures_of`).
- **Smallest fix:** resolve each link with `resources.runs.run_file` (it
  already refuses `..`, other runs and other owners) and require the
  link's run id to be this run. Better: take links only from input
  values that are exactly a link, as `inline._links` does, never from a
  search of the text.
- **Checked:** verified (run). `pictures_of` with input
  `run://r1/../r2/evidence/other.png` returned run r2's picture;
  `run://r1/../../secret.png` returned a file two folders up.

---

## P1

### What a calling agent pays

#### A-02 Every session pays about 12,000 tokens for the tool list, most of it output schemas

- **What is wrong:** the five tools cost 48,400 characters before any
  call. Output schemas are 31,600 of that (`tobi_run_status` 11,200,
  `tobi_run_tt_tests` 9,300, `tobi_answer_questions` 7,800). They repeat
  every field description, and an agent cannot use them. Each result is
  also sent twice: as JSON text and again as `structured_content`.
- **Why it matters:** about 8,000 tokens per session bought nothing, and
  a client that forwards both copies doubles every result.
- **Where:** return annotations in `src/tobi508/tools/run_status.py:36`,
  `run_tt_tests.py:196`, `answer_questions.py`, `read_report.py`;
  `src/tobi508/inline.py:222-251`.
- **Smallest fix:** register the tools with no output schema and return
  text content only. Check how `tests/test_tools.py` reads results first.
- **Checked:** verified (run): sizes measured from `mcp.list_tools()`.
  Whether a given client shows the model both copies of a result is not
  checked (phase 1 measures it).

#### A-03 Every result gives the same instructions three or four times

- **What is wrong:** "answer the open questions", "call `tobi_run_status`
  with finish=true", "save `report_uri`" and "report NEEDS REVIEW as
  needs review" each appear in `next_step`, in `todo`, in `todo` again as
  the closing "TO DO" block, and in the tool description. `work`,
  `remaining` and `waiting_on` describe the same state again. Some text
  is project history an agent cannot act on ("the fourth development
  run's agent...").
- **Why it matters:** about 2,200 characters of fixed text on every run,
  answer and status result, on top of the result itself.
- **Where:** `src/tobi508/pipeline.py:1316-1440` (`next_step`, `FINISH`,
  `_calls_text`, `todo`); `src/tobi508/inline.py:211-237`;
  `src/tobi508/models.py:631-697`.
- **Smallest fix:** keep one channel (the closing checklist), leave
  `todo` out of the JSON, and remove the history from the wording.
- **Checked:** verified (read) that `todo` is in the JSON and in the
  closing block; the sizes are the reviewers' measurement (phase 1
  repeats it on a real page).

### Wrong outcomes

#### K-05 9.C passes pairs where neither side has a name (needs Abby)

- **What is wrong:** row C1 is "names agree". Two controls with no name
  at all agree, so a pair of unnamed icon buttons is a PASS, and the
  summary says they "have the same names for screen reader users".
- **Why it matters:** a PASS resting on no names. Whether an unnamed pair
  is a 9.C matter or only a 4.1.2 one is a spec decision; today the code
  decides it silently.
- **Where:** `src/tobi508/checks/t9c.py:285-298`; spec 9.C section 3a,
  rows C1 and C2.
- **Smallest fix:** a row before C1: both names empty is NEEDS REVIEW (or
  the pair is left out with a note). A MINOR spec change.
- **Checked:** verified (run). Two pages, each with the same nameless
  icon button and nameless icon link in the header: 9.C PASS, four pairs,
  all C1.

#### K-04 9.C pairs every `javascript:` link with every other, and FAILs unrelated controls

- **What is wrong:** links are paired "by destination" on their href
  text. `javascript:void(0)` on two pages is the same text, so two
  unrelated controls pair, and a name on one side only is a FAIL.
- **Why it matters:** a wrong FAIL on a common pattern, in a test where
  the roadmap is already cutting false FAILs.
- **Where:** `src/tobi508/checks/t9c.py:131, 203`;
  `src/tobi508/site.py:314-323` (`norm_href`).
- **Smallest fix:** give a link a destination only when it is http, https
  or file; the rest fall through to id, name and place.
- **Checked:** verified (run). An unnamed `javascript:void(0)` icon link
  on the tested page and a "Close alert" link on the other: 9.C FAIL
  ("has a name screen readers announce on one page and none on other
  page 1").

#### K-03 9.C reads "ANDI named nothing" as "nothing to compare"

- **What is wrong:** after injecting ANDI the code waits a fixed half
  second and reads its output. An empty list counts as "ANDI ran". Every
  control then has no ANDI name, all are dropped, and the result is DOES
  NOT APPLY. Controls ANDI skips one by one (not focusable) vanish
  without a count.
- **Why it matters:** a wrong DOES NOT APPLY if ANDI is slow on a heavy
  page, and silent loss of controls otherwise.
- **Where:** `src/tobi508/checks/t9c.py:141-153, 173-174, 471-477`;
  `src/tobi508/andi.py:126-136`.
- **Smallest fix:** if a page has marked controls and ANDI named none of
  them, return the existing "ANDI did not run" NEEDS REVIEW; say in the
  summary how many controls ANDI left out.
- **Checked:** verified (read). Not reproduced: I did not find a page
  where ANDI is still working after 500 ms, so how often this happens is
  unknown.

#### D-02 A script error while reading the page looks like "nothing found"

- **What is wrong:** `evaluate_top` returns the value of a script and
  never looks at whether it threw. An error comes back as `None`, and
  callers treat `None` as an empty result. For the label pass that is
  "no form fields", the DOES NOT APPLY branch of D-01. `reader.call`
  does the same for "could not reach the element".
- **Why it matters:** any bug in one of these scripts, or a page that
  breaks one, turns into DOES NOT APPLY or an empty label with no error
  anywhere. The sister helper `call_in` does raise.
- **Where:** `src/tobi508/traverse.py:539-546`; callers
  `src/tobi508/labels.py:362, 403`, `src/tobi508/observe.py:42` and nine
  more.
- **Smallest fix:** raise on `exceptionDetails`, as `call_in` does. The
  label pass already turns an exception into a "could not be read" note.
- **Checked:** verified (read). The reviewer ran `evaluate_top("throw
  new Error('x')")` and got `None`; I did not repeat it. No real page is
  known to trigger it.

### Security and the server judge

#### B-02 Server judge: page text can close the "untrusted data" block

- **What is wrong:** page data goes to the judging model as JSON between
  `<untrusted_page_data>` tags. JSON leaves `<`, `>` and `/` as they are,
  so page text containing `</untrusted_page_data>` ends the block, and
  whatever follows reads as instructions.
- **Why it matters:** the judge can only pick one of a question's
  choices, but principle 8 lets some answers lead to PASS on the judge's
  word. No test page tries this.
- **Where:** `src/tobi508/apijudge.py:478-484` (`_tag`).
- **Smallest fix:** escape `<`, `>` and `&` in the JSON (`<` and so
  on), and add a page to `tests/fixtures/inject/` that contains the
  closing tag.
- **Checked:** verified (run) for the mechanism: `_tag` leaves the
  closing tag intact inside the data. Whether the model then obeys is
  not tested.

#### A-05 "A person decided this" is the calling agent's own claim (roadmap Now, item 4)

- **What is wrong:** an agent may send `decided_by: "human"`. Nothing
  checks it. Such an answer skips the rule that a picture question needs
  `seen`, and outranks every other agent answer.
- **Why it matters:** the picture rule exists because agents answered
  without looking; this is the way round it. No check turns "human" into
  a PASS by itself.
- **Where:** `src/tobi508/tools/answer_questions.py:48-52`;
  `src/tobi508/judgment.py:103-105, 175-180, 191-195`.
- **Smallest fix:** as the roadmap says: record every answer arriving
  through MCP as the agent's (`decided_by` model), and apply the picture
  rule to all of them.
- **Checked:** verified (read).

#### S-05 Hosted mode: a sign-in token with no `sub` claim opens every run

- **What is wrong:** the owner check asks "who is calling" and treats
  "nobody" as a local server with one user, where every run is open. A
  signed-in caller whose token has no `sub` claim also comes back as
  "nobody".
- **Why it matters:** under `AUTH=oidc` such a caller can read and change
  every user's runs, and the runs it starts get no owner. It needs a
  token without `sub`; whether VAST's Keycloak always sends one is a
  thing to confirm with the admin, since nothing at startup requires it.
- **Where:** `src/tobi508/access.py:44-55` (`caller`), `76-86`
  (`may_open`).
- **Smallest fix:** under `AUTH=oidc`, a token with no `sub` is refused;
  "nobody" stays open only when sign-in is off. One test in
  `tests/test_access.py`.
- **Checked:** verified (read). Not exercised with a real token.

#### B-04 Server judge: judging holds a browser slot and sits outside every time limit

- **What is wrong:** the judge phase runs inside the same slot as the
  browser work, after the browsers have closed, for up to `JUDGE_CAP_S`
  (900 s).
- **Why it matters:** with the default of two slots, two runs being
  judged block every other run for up to 15 minutes while no browser is
  in use, and a job can run past `MAX_RUN_S`.
- **Where:** `src/tobi508/pipeline.py:1214-1215`;
  `src/tobi508/jobs.py:78-83`.
- **Smallest fix:** release the slot before judging (run the judge from
  the job wrapper, after the browser part returns).
- **Checked:** verified (read).

### The gate that decides `JUDGE_TYPES`

#### L-02 and L-03 A question type passes the gate on one clean cell, and wrong DOES NOT APPLY never counts

- **What is wrong:** the gate passes a type that has no wrong PASS and
  few wrong FAILs. It asks for no minimum number of cells, counts
  "unsure" as a cell, never reads the wrong DOES NOT APPLY count, and
  puts "tool PASS where the key says DOES NOT APPLY" in a bucket it
  never reads.
- **Why it matters:** the gate's output is the list of types Abby would
  switch on. A type judged on one page, or one that turns failures into
  DOES NOT APPLY, shows as passing.
- **Where:** `evals/apijudge_gate.py:62-85` (`passes`);
  `evals/scoring.py:104, 206-217`.
- **Smallest fix:** a minimum of decided cells (agree plus wrong, not
  unsure) with "too few cells to judge" as a reason; fail a type on any
  wrong DOES NOT APPLY; count PASS against a DOES NOT APPLY key
  separately. Decide the numbers in the plan.
- **Checked:** verified (run). `passes()` returned "passes" for a type
  with one cell, and for a type with 6 wrong DOES NOT APPLY in 10 cells.

---

## P2

Shorter entries. Unless marked, these are a reviewer's claim that I have
not checked.

### What a calling agent pays (tokens, time)

- **A-06** `tobi_run_tt_tests`' description is 4,300 characters: it
  repeats what `next_step` says, names "the explain prompt" (agents
  cannot call prompts), gives five timeout numbers and a plan to "ask the
  user" about `no_time_limit` that CLAUDE.md says never happens. The test
  list is paid three times (description, instructions, the `tests`
  default). `tools/run_tt_tests.py:34-101`. Fix: cut to about 1,200
  characters. Sizes verified (run).
- **A-07** The answer tool's input schema is 5,200 characters; its
  description re-lists what the schema says, and the schema shows fields
  the server sets (`answered_by`, `not_viewed`). The agent writes two
  justifications per answer (`rationale` and `choice.reasons`).
  `tools/answer_questions.py:40-69`, `models.py:322-424`. Fix: keep
  server fields off the wire model; drop one of the two texts. Size
  verified (run).
- **A-11** Results serialize empty and default fields (`note: null`,
  `unconfirmed: 0`, `errors: []`, `shared_inputs: {}` ...) and fields
  that restate others (`confirmed`, `tests`, `evidence`, the seconds in
  `RunPending`). `Finding.confidence` is never set. `models.py:559-715`.
  Fix: dump with `exclude_none` and `exclude_defaults`, keeping the
  disclaimer.
- **A-10** `tobi_explain` with a run id has no size cap: every instance
  of every finding. A FAIL on a large page can pass the size where
  Claude Code moves a result to a file. `explain.py:106-132, 177-237`.
  Fix: cap instances ("N more in the report").
- **A-08** Pictures already sent are sent again whenever their question
  comes back (a rejected answer, the next page of questions), up to
  about 20,000 tokens. Encoding them blocks the event loop while other
  runs share it. `inline.py:99-196`. Fix: skip pictures already
  attached; encode in a thread.
- **B-08** Other pages are recorded one after another before the walk
  starts: 5 pages can add 100 s, 50 pages 1,000 s. `pipeline.py:939-1032`.
  Fix: record them beside the walk, two or three at a time.
- **K-08** 19.A repeats its live site search on every follow-up run (up
  to 20 s each). `checks/t19a.py:217-218, 483-493`. Fix: carry the
  earlier result into the follow-up.
- **K-09** 9.C loads every page twice (once for ANDI, once for the site
  read) plus a fixed half second per page. `checks/t9c.py:262-269`.
  Fix: build the site read from the ANDI load.
- **K-11** 9.B stores every out-of-order pair (about n²/2 for a reversed
  menu) and 9.C writes one sentence per failing pair, with no cap; the
  agent sees 5. `checks/t9b.py:115-126`, `checks/t9c.py:490-505`. Fix:
  a count plus the first 20.
- **B-18** Each judge round rebuilds the whole agent-facing result (every
  check resumed, every evidence file rewritten, the workbook
  regenerated, `fit()` run) and throws it away. `apijudge.py:808`.
  Fix: split "apply answers" from "build the result".
- **D-07** Each Tab press costs about 8 Chrome round trips to read focus,
  then 3 or 4 more per frame. The walk's presses are most of a run.
  `traverse.py:564-752`. Fix: cache the top frame id; one call for
  focus, URL and description.
- **D-12** The label pass does fields × elements × other fields work:
  2.4 s for 60 fields on a modest page (the reviewer timed it).
  `labels.py:160-277`. Fix: test the cheap region check first.
- **D-13** A fixed half-second sleep after every ANDI injection,
  repeated for every opened state (tens of seconds in the worst case).
  `labels.py:445`. Fix: poll for ANDI's rows.
- **D-14** The reveal pass computes a path for every element three or
  more times per trigger, and once more only to read the frame chain.
  Its cap of 6,000 elements is silent. `reveal.py:81-91, 267-330`.
- **D-15** Every replay and reveal load runs a whole-page inventory that
  only the walk reads. `traverse.py:1022-1037`. Fix: make it optional.
- **D-06, D-08** Reading focus opens a Chrome session for every frame
  on each miss and never closes them; the settle rule counts 50 ms per
  poll whatever the poll took, so a busy page waits well past its 1.5 s
  limit. `traverse.py:390-411, 835-851`.

### Outcomes and gaps (each stays NEEDS REVIEW or needs a narrow case)

- **B-03 and A-04** Two calls that change one run at the same time lose
  work: each reads `report.json`, waits on the browser, and writes the
  whole file back. Two overlapping answer calls drop the first one's
  answers after telling the agent they were accepted; an answer call
  overlapping `tobi_run_status(finish=true)` can start the same
  follow-up run twice. `pipeline.py:1443-1483, 1536-1569`. Fix: one lock
  per run id around read-change-write; write to a temporary file and
  rename. Verified (read). See "Refuted" for the half-written-file part.
- **B-06** An exception in one check's rules ends the whole call with a
  tool error, no findings for any test, and a run folder left behind.
  In the answer path the answers just given are lost. `pipeline.py:759-806`
  has no handler. Fix: catch per test and return "could not be
  evaluated" for that test. Verified (read).
- **K-12** 9.B counts a plain `<header>` and `<footer>` as matched
  navigation, which can be enough to reach PASS. The spec says such
  regions "do not match". `checks/t9b.py:92-99, 149`. I tried one
  different-template pair and got NEEDS REVIEW (the kinship rule caught
  it); a pair sharing two or three texts is not tried. Fix: leave
  position-only regions out.
- **K-06** 9.C differs from its spec in two places: same-address pairs
  ignore the region, and "dropped" (C5) is decided before the table, so
  it can win over C2. `checks/t9c.py:203-222, 316-321`.
- **K-10** The site read reads the page straight after load, with no
  settle step; a menu drawn just after load is missing, which gives DNA
  or FAIL (see K-02 for the same effect). `site.py:248-256`.
- **D-18** The label pass caches its result when first asked. If 5.A-5.C
  ever ran before 4.F or 5.D, fields those reveal later would never be
  checked for a label. Depends on check order; nobody verified the
  order. `labels.py:497-535`. Fix: a test that pins the order, or merge
  again on each call.
- **D-10** When Enter opens nothing, the reveal pass clicks at
  coordinates measured inside the trigger's frame but applied to the top
  page, so it clicks the wrong thing for triggers in frames.
  `reveal.py:96-108, 319-327`.
- **D-04** Changes inside server-rendered shadow roots (`<template
  shadowrootmode>`) are invisible to the settle rule and to "what did
  this action change". `traverse.py:110-113`. The reviewer confirmed it
  with a script.
- **D-16** Two failed reads compare as equal, so an action that could
  not be observed reads as "no effect"; dialogs in frames or shadow
  roots are not counted; `#nav` matches `#nav-link`.
  `observe.py:162-218, 301-320`.
- **D-05, D-09** After a frame navigates, its cached Chrome context is
  stale and the frame silently contributes nothing; focus events are
  keyed by frame URL, so two frames with one URL lose events (4.E reads
  them). `traverse.py:390-437, 775-784`.
- **D-11** Reading a field calls `checkValidity()`, which fires the
  page's own `invalid` handlers and can make error text appear before
  anything is submitted. `forms.py:92-93`. Fix: read `validity.valid`.
- **D-17** Reveal tries 3 sets and 2 options per set and says nothing
  about the rest; the label cap of 60 counts buttons with fields, so
  many buttons before a form hide its fields. `reveal.py:40-41, 428-450`,
  `labels.py:21, 389-393`.
- **B-13** After an answer call, a test left out over a cap loses its
  "run again with no time limit" reason and shows an unrelated error
  list. `pipeline.py:1475`. Still NEEDS REVIEW.
- **B-07** On refusal the run folder is deleted while the motion watcher
  is still writing into it, which can recreate it; a browser that fails
  to start leaves the folder. `pipeline.py:894-895, 1104-1108, 1193-1203`.
- **A-09** `tobi_run_status` is marked read-only and idempotent, but
  with `finish=true` it starts runs and rewrites reports. A client may
  auto-approve or retry it. `tools/run_status.py:30-34`. Verified (read).

### Security hardening

- **B-10** The judge's (or the agent's) answer can name any key, and 4.B
  presses it in the replayed page with no list of allowed keys
  ("Control+W", "F5"). CLAUDE.md allows page-named keys only for
  2.A-2.C under limits. `checks/t4b.py:121-129`, `apijudge.py:622-639`.
  Verified (read) that `_key` passes any string through.
- **K-07** 19.A's live search compares host only, not scheme or port, and
  "one search per run" holds only because one caller calls it once.
  `pipeline.py:281-287, 328-368`. Fix: compare scheme and port; refuse a
  second call.
- **K-15** 19.A puts page-chosen URLs, query string and all, into text
  the agent reads, with "you need not ask the user first".
  `checks/t19a.py:171-193, 403-413`. Fix: suggest scheme, host and path
  only.
- **S-02, S-03** The store for scripts a page loads later (principle 5's
  fourth exception) does not hold every limit CLAUDE.md states. The host
  and allowlist checks apply to the named address only, and the fetch
  then follows up to 20 redirects to any public host (the reviewer saw
  this with a counting proxy). The 40 s limit is checked before a round
  of fetches, not during it (150 files at 10 s each, 8 at a time, is
  about 190 s). The 3 MB limit is checked after the whole file is read.
  "A script" cannot fail, because the address always ends in `.js`.
  "Same host" ignores the port. The 150-file, 12 MB and 3-level limits
  hold. `src/tobi508/capture.py:326-328, 342-409`. Fix: no redirects for
  these fetches; check the deadline inside each fetch; require a
  JavaScript content type. Verified (read).
- **S-04** The media store downloads up to 20 addresses taken from the
  page's `<video>` and `<audio>` elements, with no allowlist check and
  redirects followed. This is not one of the four approved exceptions,
  though the browser has already loaded the same files as part of the
  page. With `no_time_limit=true` the size and time caps are lifted
  and each file is read whole into memory. `capture.py:118-208`. Fix:
  keep a hard ceiling even when the caps are lifted; decide whether the
  allowlist applies and write the rule into CLAUDE.md. Verified (read).
- **S-01** A script that names very many other scripts stalls the whole
  server: the scan keeps a list and searches it for each name. 40,000
  names (750 KB of script) took 6.2 s here, and the time grows with the
  square, so a 3 MB script is over a minute with every other run and
  the proxy stopped. `capture.py:331-339, 386-409, 515-518`. Fix: a set
  beside the list; stop listing after the 150-file limit. Verified
  (run): timed `script_refs` at 5,000, 20,000 and 40,000 names. Honest
  pages do not look like this; it takes a crafted script on an allowed
  site.
- **S-08** A redirect chosen by the tested site (`Location: data:text/
  plain,<any text>`) is quoted in the tool error the agent reads, up to
  200 characters and unmarked. Redaction also leaves `ftp://user:pass@`
  whole and stops at `)`. `src/tobi508/redact.py:23-36`,
  `src/tobi508/browser.py:244-269`. Fix: errors name the scheme and host
  of a blocked target only. The reviewer ran `safe_url` and `scrub`.
- **S-06, S-07** `tobi_read_report` returns the page and product names
  of an untrusted file at any length (comments are clipped, these are
  not), has no cap on rows (a 40 MB file is about 2 million rows), and a
  malformed file raises a generic error where "not an SCRT file" is
  meant. `src/tobi508/tools/read_report.py:122-195`,
  `src/tobi508/scrt.py:222-290`. Fix: clip the four fields; refuse more
  than a few thousand rows; turn parse errors into `NotAReport`.
- **B-05** The judge's time cap is checked once per round only; one bad
  round can run far past it and fire dozens of extra calls. Requests are
  not split by text size. Retries repeat errors that cannot succeed.
  `apijudge.py:547-564, 675-727`.

### Evals

- **L-01** Scoring an agent round builds its criteria from today's test
  list. Round 1 was scored on 17 criteria; today's code gives 20, and
  the three new ones would count as wrong answers. CLAUDE.md's rule
  (score a locked round with the code at its lock commit) avoids it, and
  the lock check already refuses today's code (L-11).
  `evals/agent/score.py:158`. Fix: record the criteria in each arm's
  summary. Verified (read).
- **L-11** The lock hashes live source files, so any edit to
  `scoring.py` or `catalog.py` makes every locked round unscoreable with
  current code; rounds 1 and 2 already are. `evals/judging.py:59-70,
  372-383`. Fix: have `score` read the files from the lock commit.
- **L-04** A tool PASS against a key FAIL becomes a "validated catch"
  (+1) if the tester later agrees, and leaves the false-PASS line.
  `evals/scoring.py:125-144`. Fix: never convert a false PASS; list it
  on its own line.
- **L-05** The judge eval and the gate rerun the whole browser pipeline
  for every repeat; only the model call needs repeating.
  `evals/judge_eval.py:611-664`, `evals/apijudge_gate.py:132-169`.
- **L-13** The gate runs on round 2's pages and keys, which the prompt
  and rubrics were tuned on. It measures repeat noise more than new
  pages. Say so in its output.
- **L-08** `judge_eval.py apply` leaves cases with bad answers out of
  its tally ("scored 40: 40 match" with 3 unanswerable) and loses state
  on an exception. `evals/judge_eval.py:505-559`.
- **L-09** The per-criterion score reports "not performed" as "needs
  review", and sorts review reasons by searching comment wording.
  `evals/agent/score.py:142-151, 270-276`.
- **L-10** `freeze.py` skips its own check for a URL with a fragment,
  and "freeze again" cannot replace a bad recording.
  `evals/agent/freeze.py:152, 186-188`.
- **L-12** A CLI arm has no overall time or spend cap, and its child
  processes inherit the whole environment minus 12 names.
  `evals/agent/cli.py:109-133, 189-251`.
- **L-06, L-07** `judge_c.py` is a finished one-off that copies most of
  `apijudge.py`; `per_test.py` copies the scorer's merge and hides
  missed fails under "Other".

---

## P3

Cleanup. All reviewers' claims unless marked.

- **Wording and stale text:** `other_pages` says "up to 5" when the
  default allows 50, and tells the agent to ask the user (A-16); the
  explain prompt is advertised to agents that cannot call it (A-19);
  `time_budget.py` says the limit is 120 s, `prompt_dev.py` and
  `arms.py` still say "a11y" (L-17).
- **Fixed text in every result:** the untrusted-data notice and the save
  hint repeat in each result; `ReadResult` has two flags no agent uses
  (A-12).
- **Dead code:** the `Judge`, `ClientJudge` and `ApiJudge` classes do
  nothing (`report.open_questions = result.pending` assigns a list to
  itself, `pipeline.py:1208-1209`; verified (read)); four functions find
  picture links three different ways, one of them the cause of B-01
  (B-14); `evals/snapshot.py`, the unused API route in `evals/agent/`
  (L-17).
- **Loose data:** follow-up calls are plain dicts read by key in five
  places; `RunResult` and `AnswerResult` copy about 14 fields (A-17).
- **Memory and disk:** a finished job holds its whole report for 24
  hours and `tobi_run_status` re-reads every report from disk on each
  call (A-13); the page cache never evicts and can hand out a
  half-copied recording (B-15); `evals/judging/` tracks about 250 MB,
  half of it repeated copies of one run (L-16).
- **`run://` resource:** serves any file in the run folder whole, with
  no size cap: a HAR of tens of MB, the `owner` file (A-18). The owner
  check does apply.
- **Small gaps:** a follow-up call with no tests vanishes (A-14);
  progress callbacks are awaited with no timeout (A-15); guards read
  cached global settings, and a check with no spec file gets no guards
  silently (B-16); the judge's HTTP client follows redirects with the
  API key header, the CLI process is killed without being waited for
  (B-17, L-14); `formmethod` on a submit button is ignored and the first
  search form is taken even when a later one is on the host (K-14);
  eval packets copy evidence files without scrubbing fixture names
  (L-15); smaller scoring table gaps (L-18).
- **Security edges:** the early allowlist check accepts four address
  forms Chrome reads differently (`https://evil.com\.gov/` and three
  more); the second check on Chrome's own form of the address blocks
  them, so the browser is safe, but any use of `check_url` that does not
  go through a navigation inherits the gap (S-09; the reviewer ran 23
  trick addresses). Nothing caps the size of a recording or the number
  of "refused" log lines a page can cause (S-10). The ANDI rule covers
  `https://www.ssa.gov/` exactly, not `http://` or `ssa.gov`, and a
  tested page on www.ssa.gov loses its own requests (S-11). The egress
  proxy accepts any process on the machine (S-12).
- **Core:** the same small rules (what is a field, what is visible, what
  is tabbable, how to walk shadow roots) are written out in five files
  and have drifted: reveal's field list lacks slider, searchbox and
  spinbutton (D-19). Scripts are templated with `str.replace("UP", ...)`
  over the whole text (D-20). Field reads use the document, not the
  shadow root, for id lookups (D-21). A menu trigger that opens a new
  page is counted as a link (D-22). The 300 ms noise window and a Chrome
  session are repeated per action (D-23, D-24). Past 20 nested frames
  focus reads as "body" instead of "unknown" (D-25).
- **9.x duplication:** `_finding`, the "not performed" block and the
  cache-or-read pattern are copied in 9.B, 9.C and 19.A (K-13).

---

## Checked, and it holds

So nobody reviews these again without a reason. From the security
reviewer (phase 1); I read the summary, not every line behind it.

- **The allowlist** is enforced on every top-level navigation and every
  redirect hop, with a second check on Chrome's own form of the address.
  Userinfo, trailing dots, upper case, `.gov.evil.com`, IP literals,
  `data:`, `javascript:`, `blob:` and `file://` outside dev mode are all
  refused; popups and meta refresh take the same route; service workers
  are blocked. Frames and subresources are checked by the egress proxy
  only, not the allowlist. That matches the code's own notes, but
  CLAUDE.md does not say it.
- **The egress proxy** resolves a name once, checks every address and
  connects to the address it checked, which defeats DNS rebinding.
  Metadata, link-local, IPv4-mapped, NAT64, 6to4 and Teredo addresses
  are refused. Every error path closes the connection. WebRTC is held to
  the proxy.
- **Replay never goes live:** a request not in the recording is aborted.
  File names inside a recording are never chosen by the page.
- **Run ownership** is checked by the tools and by `run://` resources
  alike (but see A-01 for jobs and S-05 for a token with no `sub`).
- **Report files:** JSON only, so no zip or XML tricks; a hosted server
  never reads its own disk for `tobi_read_report`.
- **ANDI** is never loaded from ssa.gov.

## Refuted

- **B-03, the half-written file.** The claim: `tobi_run_status` can read
  `report.json` while another call is writing it, fail to parse it, and
  say "nothing is left". Inside one server process this cannot happen:
  both the write (`Path.write_text`) and the read run to completion on
  the one event-loop thread, and jobs live in one process. The bare
  `except Exception: continue` at `pipeline.py:1589-1593` is still worth
  narrowing, and the lost-update half of B-03 is real (see P2).

## Leads nobody has checked

One line each, from the reviewers' "unverified" lists; none is counted
above.

- A cancelled job (server shutdown) raises `CancelledError` through
  `tobi_run_status`, which only catches `Exception`.
- `/version` is outside the sign-in gate.
- `ALLOWED_DOMAINS=.gov,.mil` (not JSON) may fail at startup;
  `JUDGE_TYPES` with a typo ("4.a") silently switches nothing on.
- `tobi_read_report` is a synchronous tool parsing up to 40 M
  characters; whether it blocks the event loop is not checked.
- The walk runs while the motion watcher is still setting the list of
  changes to ignore, so two runs of one page can settle differently.
- Same-named radio groups in two forms are counted as one field.
- `bypass()` clicks a text spot after a trap; an ancestor with a click
  handler would run page code.
- A second walk pass after a trap doubles the walk time on a long page.
- 9.C's place pairing uses `regions[-1]`, which may be `main`.
- No test covers a live search that goes off host or off port.
- With the default settings, sign-in checks no audience and requires no
  group, so any user of the realm can sign in: confirm the deployment
  sets `OIDC_AUDIENCE` and `REQUIRED_GROUPS`.
- A stored media file whose address has a query string may not be found
  on replay (exact match on the address).
- The audit log records the caller's email on every call: intended, but
  confirm it fits the retention policy.

## If we started over

Written in phase 5, from the design notes of every phase.
