# Plan: the server judges, a person reviews, the client agent explains (2026-11-07; human review added 2026-11-08; status 2026-11-11)

Decision record for moving judgment questions from the calling agent to
TOBI's own model on VAST, and reshaping TOBI into a hosted NASA service.
Proposed by Abby, 2026-11-07. Nothing here changes an outcome rule: outcomes
still come only from `specs/rules/`, and every answer still goes through
`record_answers` and its guards.

## Why

- **Calling agents skip the work.** Runs 5-11: answers skipped, pictures
  not opened, `seen` filled without looking, follow-up calls dropped
  (`docs/solutions/agent-follow-through.md`). More wording and more proof
  fields moved the shortcut; they did not remove it.
- **The judge is an uncontrolled variable.** A user may bring Opus,
  Sonnet, Copilot or GPT. Our evals measure one of them. Repeatability
  (same page, same result) is the success measure, and it needs a pinned
  judge: model id, prompt hash, parameters, recorded in every report.
- **Each side does what it is good at.**
  - The server owns verdicts: repeatable, auditable, under NASA's control.
  - The client agent owns what the server cannot see: the user's code,
    CMS and questions. It explains results and walks people through fixes.

## Decisions

1. **Target shape:** a hosted TOBI service on VAST. Runner, ApiJudge,
   results store, answer-once-per-site and cross-page tests all live on
   the server. MCP tools: request a scan, check status, explain, walk
   through a fix, record a person's answer.
2. **Judge model:** NASA's in-house Sonnet with vision, if it passes the
   judge-eval bar (below). Opus only for question types where Sonnet
   misses the bar, decided per question type from eval data.
3. **When the server judge is unsure,** the question goes to a person, not
   back to the calling agent (which had a worse view of the same picture).
   A person's answer overrides the model's, and **a person's answer only
   comes from TOBI's own review UI,** signed in as that person. An answer
   that arrives through MCP is the client agent's, whatever it says (see
   "Human answers" below; Abby, 2026-11-08).
4. **If a model call fails** (timeout, refusal, bad schema), the question
   stays open for a person. Never answered by default.
5. **Public pages only** until a NASA security POC agrees otherwise. The
   egress proxy already refuses any host that resolves to a non-public
   address; the allowlist stays `.gov`/`.mil`.
6. **Optional local runner later** (sends a recording to VAST for judging),
   for staging and localhost pages: the "check a fix before it ships"
   path. Not in the Nov 20 cut.

## Human answers: only from a person, in TOBI's own UI (2026-11-08)

**Why.** Agents in rounds 1 and 2 reported untested PASSes, changed
confirmed FAILs to needs review, and claimed work they had not done (round 2
debriefs). An agent could as easily say "my user checked this" when no one
did. Today `tobi_answer_questions` accepts `decided_by: "human"` from the
calling agent, and a "human" answer overrides the model's: the server
cannot tell a person from an agent's claim.

**Rule.** The MCP tools never record a person's answer. Every answer through
MCP is `answered_by: "client"` (done 2026-11-08) and `decided_by` from MCP is
treated as the model's (to do: today it is trusted). A person's answer is
recorded only by the review UI, from a signed-in session, with the person's
identity (`sub`), their role, the time, and what they were shown (the
finding, the picture hashes, the page version).

**Who answers what (Abby, 2026-11-12).** Anyone signed in may answer
any open question, and each answer saves an updated pre-SCRT. Every
outcome and note in a pre-SCRT is traceable to a time and to who gave
the answer behind it: a signed-in person with their role, the server
judge, or the calling agent. Answers rank: a Trusted Tester's over a
reviewer's, a reviewer's over the server judge's, the server judge's
over the calling agent's. A person's answer, trained or not, is assumed
better than a model's, which is why the plain-language explanation of
each test and question matters most for reviewers. A pre-SCRT carries a
"Not certified by a Trusted Tester" banner until a Trusted Tester has
certified every row; only then can they save it as a permanent SCRT
record, which drops the banner. That SCRT is the Trusted Tester's
record, not TOBI's (principle 1).

**Accounts.** NASA users only. Trusted Testers at other agencies get no
accounts here: an agency forks the repository and hosts it in its own
infrastructure with its own sign-in. So nothing NASA-specific may be
hard-coded (sign-in is already generic OIDC), and the deployment notes
must be enough for another agency to stand it up.

**Who.** Two roles from Keycloak groups:
- **Trusted Tester:** a person an admin has added after seeing their DHS
  certificate (no public registry to check against). Sees TT test IDs, WCAG
  criteria, rule rows and SCRT fields; can answer any open question,
  override any outcome (with a comment), and add an issue the tool missed.
  Their result can be exported as an SCRT file.
- **Reviewer (anyone else signed in):** sees plain-language questions and
  failure explanations, no spec codes. Answers any open question ("is
  there a visible outline on the highlighted link?"), and the answer
  settles it until a Trusted Tester answers; cannot override a rule's
  outcome or certify.
- **Adding a Trusted Tester:** Abby or another approved admin confirms
  the person's DHS certificate (with DHS where needed) and adds them to
  the group; the store records who added them and when. Certification
  does not expire, so it is not rechecked.

**Proving it is a person.** Signing in proves an account, not a person: an
agent driving the user's own browser (computer use, Playwright MCP) could
click through a signed-in UI. Defences:
- submitting answers needs a fresh user-presence check (WebAuthn: a touch
  of a PIV card or security key) per batch, which no agent can perform.
  Whether NASA's Keycloak can ask for it on one action rather than at
  sign-in is unknown: to try on VAST; if it cannot, the review UI asks
  for it itself;
- answers are signed server-side with the session's identity; the report
  records "person, verified by WebAuthn", never only "human";
- the MCP tools have no way to submit to the review UI's endpoint.

**Where the person looks: options.** A Trusted Tester wants the problem in
the page's real context, as ANDI shows it: a layer turned on and off over
the page. Measured for round 2's 10 recordings: 288 MB, of which HTML, CSS,
JS and fonts are 7 MB, full-size images 199 MB and video 95 MB.

| Option | What the person sees | Person's UX | VAST cost and risk |
| --- | --- | --- | --- |
| **A. Evidence page** (web app on VAST: screenshots, crops, element and question) | Pictures TOBI took, not the page | Fine for a reviewer's one-off questions; a TT cannot check context, scroll, or try the keyboard | Cheapest: the pictures already kept for FAIL and NEEDS REVIEW (storage table); no page code served |
| **B. Overlay on the live page** (a browser extension, "ANDI with TOBI's layer") | The real page, with markers on each finding's element, a panel per TT test, focus moved to the element on request | Closest to how TTs work today; can sit beside ANDI; keyboard and screen reader testable in place. Install needed: published open source for anyone to download, as ANDI is (Abby, 2026-11-12; a managed policy on NASA machines is not likely) | No page storage, little compute (findings API only). Risks: the live page may have changed since the scan (element moved, text edited); states the scan reached (menu open, form errors) must be re-created on the live site, and submitting forms there has side effects |
| **C. Overlay on the recorded page** (VAST serves the scanned version with the layer) | Exactly what was tested, states replayable (TOBI already replays focus and key presses) | No install; matches the evidence; same view for TT and reviewer | Storage: about 1 MB per page if images are stored at their displayed size and video as a poster frame (estimate from the numbers above, not measured), much more if not. Security: serving third-party page scripts from a NASA host needs a separate cookieless origin with a sandbox CSP, and a security review. Some pages do not replay (cross-site frames) |
| **E. MCP App** (TOBI's view rendered inside the person's chat: Claude, ChatGPT, VS Code and Microsoft 365 Copilot, others; MCP Apps spec 2026-01-26) | Evidence and comments pinned to elements, in the chat the person already uses; the agent can read what the person did (`ui/update-model-context`) and explain it | No storage beyond A. **Cannot prove a person did it:** a click in the app reaches the server as an ordinary `tools/call` forwarded by the host, with no field saying it came from the app; app-only tools are enforced by the host (the user's client), not by TOBI; no WebAuthn inside the app. So answers given there are drafts, made a person's only by "Sign on VAST" (`ui/open-link`) in the review UI |
| **D. Remote browser** (VAST runs Chromium; the person drives it in a stream) | Live or recorded page in a real browser, overlay drawn server side | No install; laggy; assistive technology on the person's own machine cannot read a video stream | Heaviest: one browser per reviewer (hundreds of MB of RAM each); not accessible to a screen reader user, so it fails 508 itself |

**Recommendation (revised 2026-11-08 with Abby).**
1. **Now (Nov 20 cut, small):** close the MCP path for human answers, and
   build option A for reviewers' plain-language questions, with WebAuthn
   on submit.
2. **The Trusted Tester's workspace: option C for the latest scan,** as
   below. VAST keeps one cheap review copy per page (its latest scan:
   HTML, CSS, scripts and fonts, images at their displayed size, video as a
   poster frame); older scans keep only their pre-SCRT and report. Only
   after the security review of serving recorded pages from a separate
   origin.
3. **Option B (an extension on the live page) only if** Trusted Testers
   need TOBI's layer on the live page often enough to install it; the
   workspace's live link covers most of that.
4. **Not D:** a streamed browser is not accessible to screen reader users.
5. **Option E (an MCP App) later, as a front end only:** people and their
   agent look and comment in the chat (each comment labelled by role);
   an answer counts as a person's only once signed on VAST.

### The Trusted Tester's workspace

This extends the planned SCRT-like review (the TT reviews the pre-SCRT
findings and screenshots, edits and fixes them, checks off each row, and
saves a final SCRT file once every row is validated).

**Views, in panes or in separate windows.** By default the pre-SCRT grid
(tests, results, comments, screenshots, each row's check-off) is on one
side and the page on the other, with a switch for what it shows. Any view
can also open in its own window, kept in step with the others (same
review app origin; a `BroadcastChannel`), because two panes do not suit
everyone (Abby, 2026-11-08):
- a screen magnifier user needs one large view at a time, not two halves;
- a screen reader user is better served by one document per window, with
  "Show in page" moving focus to the page window and saying where it went,
  than by focus jumping between panes of one page;
- two monitors.

The layout also reflows to one column at 400% zoom (WCAG 1.4.10), and
every switch has a keyboard shortcut. The views:

| View | What it is | Why |
| --- | --- | --- |
| **Report** | The pre-SCRT grid, partly filled, for the TT to validate and edit | Where the TT's decisions are made and recorded |
| **Page** | The recorded page, no overlay | What was tested, as a user saw it |
| **Page + ANDI** | ANDI, from TOBI's vendored copy, run on the recorded page | The tool TTs already know and trust; no relearning |
| **Page + TOBI** | TOBI's layer: each finding on its element, with its evidence | What ANDI does not show (below) |
| **Live page** (opens a new tab) | The site as it is now | Video and audio (the review copy keeps a poster frame only), anything the copy cannot replay, and checking that the page has not changed |

**Every pre-SCRT row links to its element.** "Show in page" scrolls the
page pane to the element, outlines it, and opens TOBI's layer at that
finding. The live link adds a text fragment (`#:~:text=`) where the
element has unique text, so the live tab scrolls to it too. Links live in
TOBI's pre-SCRT and review UI only; the exported SCRT file stays clean.

**How much of TOBI's layer duplicates ANDI.** Little, if the layer shows
TT-test results and states, not element properties:
- **ANDI already shows** what each element is: accessible name and
  description, role, focusable order (fANDI), links and buttons (lANDI),
  images (gANDI), tables, structure, contrast (cANDI), hidden content,
  frames. TOBI's layer should not redraw these: a finding about a name
  (5.A-5.C) gets an "Open in ANDI" button that switches to Page + ANDI and
  focuses the element, so ANDI's panel inspects it (assumed: ANDI inspects
  the focused element in its focusable-elements module; to check).
- **Only TOBI shows** what TOBI did to the page:
  - the Tab walk's order drawn as a path, and where it looped or stuck
    (4.C, 4.F);
  - focus off and on, with the changed pixels, for 4.D;
  - what focus or input changed (4.E, 5.D), and the error states it
    submitted (5.F-5.H);
  - regions that moved, updated or flashed on their own (2.A-2.D, 3.A);
  - blocks repeated across the site's pages, and their order (9.A-9.C);
  - each finding's outcome, its open question and who answered it.
- **TOBI can replay a state** on the recorded copy, which neither ANDI nor
  a screenshot can: "focus this element" (the walk's key presses),
  "show the error message" (the submission it recorded). On the live site
  that would mean submitting real forms.

**ANDI and TOBI's layer one at a time.** ANDI changes the page it runs on
(`docs/solutions/andi-output.md`), so the two are not stacked.
TOBI's layer changes nothing in the page: a small script in the review
copy reports element positions to the review app, which draws the layer
in its own frame above the page.

**Recorded copy or live page, by test** (Abby, 2026-11-08: it depends on
the test). The review copy has no audio or video and replays only what the
scan recorded, so a row's "Show in page" goes to the live page where the
copy cannot show what the test is about:

| Tests (built) | Validate on | Why |
| --- | --- | --- |
| 4.A-4.F, 5.A-5.C | Recorded copy | Keyboard and focus behaviour and labels are in the page's code, which the copy replays |
| 5.D | Recorded copy | What a field's input changes is in the page's code; a submission is never made |
| 5.F-5.H | Recorded copy for the submissions TOBI made; live (with a warning: submitting a real form has effects) for any other | The copy holds only the server's replies TOBI recorded |
| 9.A-9.C | Recorded copies of the tested page and the other pages | Each other page was recorded in the same run |
| 2.A (audio), 3.A (flashing) | Live page | No audio or video in the copy; 3.A's frames and TOBI's evidence stay beside it |
| 2.B, 2.C, 2.D | Live page when the content is video or comes from the server after load (feeds, polls); otherwise the copy | The copy replays scripts but not new data or media |
| 19.A | Live site | Other ways to the page (site map, search) are on the live site |

Media tests TOBI does not perform yet (16.A-17.G: transcripts, captions,
audio description and their controls) also go to the live page. **For a
final SCRT** (Abby, 2026-11-12): the agency, not DHS, accepts it. A
Trusted Tester confirms on the live page where possible, since a
recording can be out of date. A pre-SCRT and an SCRT are each valid for
their moment only: both carry the time of the scan and of each answer,
and the workspace records per row which view (live or recorded) it was
checked in. Sites change between scans; that is an accepted risk.

**Either UI must itself conform to Section 508** (keyboard, screen reader,
contrast), and be tested with TOBI and by a Trusted Tester, since its users
include people with disabilities.

## Storage budget (20 GB)

Measured from round 1: `report.json` is 0.6-0.8 MB and `pre-scrt.json`
1.8-3.1 MB per page, uncompressed. JSON compresses roughly 5-10x.

| Kept | How long |
| --- | --- |
| Report and pre-SCRT, gzipped | Indefinitely (about 0.3-0.6 MB per page: 30,000+ page results) |
| Screenshots and crops for FAIL and NEEDS REVIEW rows only, as WebP | 90 days, or until a newer scan of the page |
| Answers (choice, reasons, `seen`, who, model id), keyed by content hash | Indefinitely (small) |
| Site reads for cross-page tests | Until a newer read, or 30 days |
| Review copy of each page's latest scan (HTML, CSS, scripts, fonts; images at displayed size; video as a poster frame; about 1 MB a page, estimated) | Until a newer scan of the page; older scans keep their pre-SCRT and report only |
| HARs, full-page screenshots, motion frames | Current behaviour: 24 hours (`run_ttl_hours`) |

Add a disk-use check that stops new scans at 85% and says so.

## How the evals change

- **Judge eval is the gate.** Before ApiJudge is switched on for a
  question type: zero false PASS and zero false DNA in every one of three
  repeats, at least run 19's agent-with-pictures score (67/70), and every
  injection case answered as if the injected text were absent. Run it for
  Sonnet first, then Opus only for the types Sonnet misses.
  **Added after round 2:** the gate also runs on real pages, round 2's
  first-round questions (`evals/judging/round2-armc/first-round/`, 182
  questions with Abby's keys), scored only on the cells a judge's answer
  decides; and it caps false FAILs per type, not only false PASSes (Agent
  C's 4.F J1 was wrong on 5-6 of 10 pages, all toward FAIL).
- **Judging rounds against TT SCRT files:** unchanged, and stronger,
  since the judge no longer varies. If time allows, score round 2's
  remaining tests both ways (client agent as judge, server judge) on the
  same frozen pages. That comparison is the deck's main slide.
- **Agent eval:** smaller. It checks that the client agent relays results
  faithfully, never calls a result certified or compliant, and gives fix
  guidance that matches the spec and W3C technique.

## What round 2 changed (2026-11-08)

Round 2 ran Agent C, a stand-in for ApiJudge (`evals/agent/judge_c.py`:
Sonnet 5.5 on the CLI route, one call per question, the untrusted block,
pictures at native resolution, choices as an enum), beside Agents A and B
([abc-score.md](../../evals/judging/round2-armc/abc-score.md)). What it
means for this plan:

- **The pivot holds.** A server judge finished every question (194 of
  194, in each of 3 repeats, 0 failed calls) where the calling agent left
  whole pages unanswered, and it gave the same result on 194 of 200
  criterion cells across repeats. Agent B made 15-19 false PASSes per run;
  no false PASS came from any judge's answer.
- **Its errors are all toward FAIL, and they come from our questions,
  not the model:** 4.F J1's rubric lets "differs from the visual order"
  read as "does not preserve meaning", and its order picture draws boxes
  for stops nobody can see; 9.C pairs unrelated content links. So ApiJudge
  is switched on per question type, and 4.F and 9.C stay with a person
  until post-round 2 fixes 12-14 pass the gate.
- **Picture questions only, or all:** round 2 gives no reason to limit it
  to pictures. Its errors were one picture type (4.F) and one text type
  (9.C), both question problems; unsure was 35% on picture questions and
  25-30% on text ones. Plan on all question types (Abby), each behind
  the gate.
- **The rules' own errors are bigger than any judge's** (3 false PASS and
  2 missed fail cells, 13-15 false FAILs per run, all rules deciding
  alone). ApiJudge work must not crowd out the principle-3 rule fixes
  (post-round 2 fixes 1-7).
- **People's load:** about 62 unsure answers per 10 pages go to a person.
  About 50 trace to our rules or questions (post-round 2 plan, "Unsure
  answers"); fixes 9c and 14 alone remove about half. Answer-once-per-site
  and the review UI's reviewer view matter for the rest.
- **Cost and speed:** 1.71M input tokens per 10 pages (about 8.8k per
  question; Home alone 794k for 63 questions, from the shared Tab-stop
  list and full-page pictures), 7-8 minutes at 3 calls at a time. A
  repeat with the cache warm cost a fifth as much: ApiJudge should put a
  page's shared inputs first in the prompt and send a page's questions
  together, so the cache serves them. Sonnet looks sufficient on this
  evidence; Opus only per type, after the gate says so.
- **Built already:** `Answer.answered_by` (set by the server), the request
  and prompt draft (`judge_c.py`, `judge_c_prompt.md`), a failed call
  retried once and then left open, unsure never retried, gate questions
  (J0) answered before the rest of a page.

## What the code review changed (2026-11-12)

The review ([reviews/2026-11-11-code-review.md](../reviews/2026-11-11-code-review.md))
supports this plan's division of work and adds to it
([the plan after the code review](2026-11-12-coverage-second-look-thin-agent.md)):

- **The judge and the person only see NEEDS REVIEW.** All 30 wrong PASS
  and DOES NOT APPLY results the review found went straight to the
  report. So readings must say what they covered (parts B and C), and
  a second look at confident results is worth a trial (part F).
- **The gate** needs a minimum number of decided cells and must count a
  wrong DOES NOT APPLY (L-02, L-03), and it reuses pages the prompt was
  tuned on (L-13). "How the evals change" above stands with those
  added.
- **The calling agent** should carry nothing: no raw page text, no
  report files (part H). It is the party that holds the user's
  repository, and the tested page is untrusted.
- **The review page** (option A) must show the whole page beside each
  crop, or a reviewer inherits the tool's blind spots (part G).
- **Decision 6, the local runner,** is where the agent's own value is
  (the user's unreleased pages); it stays later (part J).

## Bundles and status (2026-11-11)

Fix numbers are those of the
[post-round 2 fixes](2026-11-08-post-round2-fixes.md). What is scheduled
for the Nov 20 demo and what comes after is in
[the roadmap](../ROADMAP.md), the one status of record.

| # | Bundle | Contents | Status |
| --- | --- | --- | --- |
| 1 | `apijudge` | ApiJudge in the server; the judge-eval backend; the gate | Built, off by default; the gate has run as a 2-page trial only ([plan](2026-11-08-apijudge-build.md)) |
| 2 | `rules-principle3` | Fixes 1-6, 9b phase 1, the chunk store and guard GU | Built, except fix 3 (error values) |
| 3 | `frames` | Fix 7: 5.x reads fields in frames; the per-test frame leftovers | Not started; built as part D of [the plan after the code review](2026-11-12-coverage-second-look-thin-agent.md) |
| 4 | `questions-for-judges` | Fixes 12-14 and 24-27; then the gate for 4.F and 9.C | Not started |
| 5 | `rules-false-fail` | Fixes 8-11 and 9c | Built (PR #44), with fix 8b (5.B, icon labels) |
| 6 | `human-answers` | Close MCP's `decided_by: "human"`; roles; WebAuthn on submit; the evidence page (option A) | Not started; part G of that plan adds the whole page beside each crop, the list of what was not looked at, and a sample of PASS and DOES NOT APPLY |
| 7 | `vast-deploy` | Store (run index, answers by content hash), retention and disk check, Keycloak, one page end to end | Not started (sign-in built against a stand-in: [plan](2026-11-06-hosted-auth.md)); the store now comes before bundle 6 and carries the thin MCP surface (part H of that plan) |
| 8 | `scorer-round3` | Fixes 15-17 and 29 | 29 built; 17 partly |

Later: cross-page tests from the store, the fix path, the local runner,
internal pages after the security review. A separate results service and
dashboard on Databricks (proposed 2026-11-04) was dropped on 2026-11-11:
the store on VAST replaces it.

## Open questions

- Can NASA's Keycloak require WebAuthn (PIV or security key) for one
  action rather than the whole sign-in? Unknown: try it on VAST.
- The judge's endpoint: Luna (an alternative provider with tokens for
  the demo, since Ask Sage has none this month) or the in-house Sonnet.
  Vision input size, structured output, rate limits, token quota per
  day. Until then, development runs use the CLI route.

Answered on 2026-11-12 (Abby) and written into the sections above: who
may answer which question; accounts outside NASA; the extension's
distribution; who confirms a Trusted Tester and how often; live page or
recorded copy for a final SCRT. Also: sending screenshots of public
pages to the in-house model needs no data-handling note, and the
hackathon's reviewers see a recorded demo, not a guest account.
