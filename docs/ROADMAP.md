# Roadmap

What is left to build, and the one place that says what is scheduled when.
A living list, not a log: delete an item once it is built, and put any
decision it needed into the spec, CLAUDE.md or `docs/solutions/` where it
belongs. Plans in `docs/plans/` hold the detail of an item; they do not
keep their own schedule.

## Where things stand (2026-11-17)

- **22 TT tests are built:** 2.A-2.D, 3.A, 4.A-4.F, 5.A-5.D, 5.F-5.H,
  9.A-9.C and 19.A. The [README](../README.md) has a status per test
  and the wrong outcomes known today; what each cannot do is in
  [KNOWN-LIMITS.md](KNOWN-LIMITS.md).
- **Direction** ([plan](plans/2026-11-07-server-judge-pivot.md)): the
  server judges, a person reviews, the client agent explains, as a
  hosted service on VAST. The server's judge answers every open
  question type in our runs: a type left off goes to the calling
  agent, which is less consistent, not to nobody.
- **On real pages** ([evals/README.md](../evals/README.md)), three
  sites, each scored against Abby's blind SCRT files:

  | Run | Decided of scored | Agree | PASS or DNA where the key fails | FAIL or DNA where it passes |
  | --- | --- | --- | --- | --- |
  | Round 3, blind (science.data.nasa.gov, 2026-11-16) | 149 of 220 | 118 | 3 | 28 |
  | Round 2's pages, rerun (svs.gsfc.nasa.gov, step 9b) | 134 of 220 | 122 | 0 | 12 |
  | Round 1's pages, rerun (www.nasa.gov, step 9b) | 76 of 153 | 74 | 0 | 2 |

  Rounds 1 and 2 were blind rounds earlier; a later run on a round's
  frozen pages is a development rerun and never replaces its blind
  score. On round 2's pages, decided cells went 68 (Nov 13) to 91 to
  134, with no unsafe error since Nov 13.
- **What round 3 showed** ([plan](plans/2026-11-16-after-round3.md)):
  its four application pages hold 41 of its 102 wrong or undecided
  cells (the tool read them before they had drawn themselves), and
  its three unsafe cells have two causes, both small to make safe
  (steps 21 and 22).
- **Hosting:** sign-in, run ownership and audit lines are built, and
  the built image passes a smoke test in CI behind a real Keycloak
  ([guide](how-to/deploy-on-vast.md)). On VAST (2026-11-17) the image
  runs in a dev environment and ran a live page there through Claude
  Code over an ssh tunnel; the dev URL's gateway is measured; sign-in
  there waits for a Keycloak client from the admins. Without a gateway for the judge,
  a hosted server leaves open questions to the calling agent.
- Earlier steps and their notes: [archive](archive/).

## Now: the last day of development (Nov 17)

**The cut** is the end of Nov 17: from Nov 18 only the deck and the
presentation. What is not merged by then waits.

**One numbering.** A step number in this file is the only name a
piece of work has; plans keep their own cause numbers inside
themselves. Each row below is one thread, started with its prompt in
[reviews/2026-11-11-code-review-fixing.md](reviews/2026-11-11-code-review-fixing.md);
a prompt is removed when its step is merged. This thread keeps this
file and the prompt file; other threads write to their plan.

### Order of work

| Order | Steps | What | Model | When |
| --- | --- | --- | --- | --- |
| - | 12b | Hosted on VAST: sign-in at the dev URL done 2026-11-18 (smoke test passed); next a group and the audience, then YAML for the cluster admins (after the demo) | Opus | now |
| - | 13 | The pitch: the scored run at the submission commit, rehearsal, fallback video | Abby; Sonnet for the run | Nov 18-19 |

### Why these, and what they should do to the status table

Step 9c (done, 2026-11-18) ran all three sites' frozen pages after the
rows below, and the README's status table (step 10d, done) is written
from it: 16 tests green, 6 yellow (4.A, 4.D, 5.B, 5.D, 5.F, 5.G), none
red. The rows below are what moved the tests:

- **21, 36 (5.F, 5.G; done, #109):** red to yellow. The browser's own error
  messages, and text that is not a message, become NEEDS REVIEW. Both
  tests then have no wrong cell and are mostly left for a person.
- **22 (4.F, and 4.A, 5.D; done, #110, #111):** 4.F red to yellow; two false FAILs of
  4.A and two wrong cells of 5.D go.
- **23 (done, #112):** the replay draws; on round 3's p07, p08 and
  p10, 4.E's three false FAILs, 5.F, 5.G and 5.H moved to NEEDS REVIEW,
  PASS or an agreeing DOES NOT APPLY (`evals/judging/gate-2026-11-17-step23/`).
- **31 (9.B; done):** yellow to green.
- **29, small part (5.B; done):** five wrong cells become NEEDS REVIEW.
- **4.F 1.11.0 (done, #121, not planned):** step 23's rerun showed three
  new 4.F false FAILs on round 2; the cause was measurement (a box read
  while the page scrolled, a scroll box, a script-made id), not the
  judge. Round 2's 4.F false FAILs 4 to 2 (`evals/judging/gate-2026-11-17-4f/`).
- **9c where the search loads (19.A; done):** the sites' own search
  loaded in this run's container for all three sites (svs's failed on
  its first two pages and those two were run again), and 19.A went from
  yellow to green with no code change: 9 of 10 cells agree on round 2
  (one false FAIL, CILab) beside 2 in step 9b
  (`evals/judging/gate-2026-11-17-9c/`).

Left yellow after the cut, each needing more than a day: 4.A, 4.D
and 5.B (the judge unsure or too strict; frames pictured alone),
5.D (opened content), 5.F and 5.G (forms a recording cannot send).

### What each step covers

- **9c. The last rerun (done, 2026-11-18).** As step 9b, one repeat,
  the judge on every type, plus round 3's pages (a rerun, never in
  place of its blind score), on all three rounds' original freezes at
  `main` `30e948c` with #121 (write-up in `evals/README.md`, "Gate
  2026-11-17-9c"; folder `evals/judging/gate-2026-11-17-9c/`, per-page
  reports out of git). No cell PASSes or DOES NOT APPLYs where the key
  fails in any round. The README's status table (step 10d) reads its
  `compare-roundN.json` files. A reference run of round 1 on a refreeze
  is its own experiment (`evals/judging/gate-2026-11-17-9c-refrozen/`),
  not in the table.
- **10d. The README's status table.** One colour and a few words per
  test by one stated rule, written by a script from 9c; a test fails
  when the README's rows are not the script's. Counts per site go to
  a generated `evals/STATUS.md`.
- **12b.** No app namespace for developers on VAST (admin,
  2026-11-17): make it work with sign-in at the dev environment's URL,
  then hand the cluster admins YAML for its resources
  ([guide, section 6a](how-to/deploy-on-vast.md)). Sign in from Claude
  Code, run the smoke test, then one page; then the [PENDING] markers
  about sign-in go.
- **13.** The [FILL] figures from one scored run at the submission
  commit ([docs/hackathon/](hackathon/README.md)).

## Next: after the demo

In this order. One thread at a time per row, so no two threads share a
test. Inside a row, a wrong outcome or a cell one step from unsafe
comes before turning NEEDS REVIEW into answers. A step marked
"approval" turns NEEDS REVIEW into an outcome and waits for Abby's yes
on the spec text; every row reruns its tests on all three sites'
frozen pages and shows Abby each moved cell. The detail of steps 23 to
35 is in [the plan after round 3](plans/2026-11-16-after-round3.md);
of 14 to 20, in
[the plan after the code review](plans/2026-11-12-coverage-second-look-thin-agent.md)
and [the pivot plan](plans/2026-11-07-server-judge-pivot.md).

| Row | Steps | What |
| --- | --- | --- |
| Applications | 24, 25, 26, 35a, 35e | The app's own address changes read as caused by focus (24); the freeze saves code loaded on use (25); every address serving one document (26, approval, 16 cells); controls with no form element (35a, approval); a press that navigates (35e, approval) |
| 4.D and 5.D on what opens | 27, then 15 | A faint mark on a large element is not a focus indicator (27; it must land first: one cell is a PASS the key fails, held only by a guard), then 4.D and 5.D read what menus and sections open (15) |
| 4.A and 4.F | 28, 32, 33 | A hedged judge answer is "unsure" (28); 4.A's undecided signals (32, approval); 4.F's rubric, footer columns and dropdowns (33) |
| Forms | 29 (rest), 30, 35b-d, 37 | The search box in a panel (29, approval); forms with nothing to get wrong (30, approval); the one-cell 5.B, 5.C and 5.D items (35b-d) with 5.B's rubric on a search page; a frame's fields pictured in place on the page, not opened alone (37) |
| Site tests | 34, 19b | 19.A after round 3 and on CILab (34, approval), reruns serving other pages from the freeze, 9.C's sentence when other pages could not be read; 9.C pairs by function (19b) |
| The judge | 40 | For a question type that fails the gate, the judge's FAIL is shown as "likely fails, a person should confirm", never handed to the calling agent (a rule change; Abby's decision first) |
| Coverage | 14, 14b, 14c | Every reading reports what it covered (14); a click past a trap's stops reach 4.D and 4.E (14b); 4.A, 4.B and 4.F past a forward trap (14c) |
| Meaning to the judge | 16 | 5.H's, 4.B's and 2.x's word lists become questions |
| Live status page | 41 | A read-only page on the server, open without sign-in, showing each run it holds as it goes (page, tests, progress) and, when done, its outcomes, with its pre-SCRT file opened in the viewer; a link to it in the tool's results. Runs the server still holds only; the lasting store is 17. Touches no test or spec, so it can run beside the rows above. Not the demo's live log (`/live`, #123: a token-gated log of every call's payload, off by default); build on its parts, under its own path (e.g. `/status`): the `Job.progress` hook, the text-only page under a strict CSP (`livepage.py`, `live/`), the outcome line, and its tests (POST refused, markup stays text, open while `/mcp` answers 401) |
| The service | 17, 18 | The store, a thin MCP surface, one writer per run (17); a person's answer only from TOBI's own page (18) |
| Measures | 10b, 11, 19 | Round 4, a blind round, when Abby keys one (10b); the second look's trial (11), then as a guard (19) |
| SCRT files | 20 | Review, merge, export ([plan](plans/2026-11-02-scrt-io.md)) |

Also for a later watch on a paused clock (the plan's part J): 2.C and
2.D's remaining timers, and what starts after the 6.5 s watch.

## Decisions waiting for Abby

**Before the demo:**

- **VAST** (step 12b): sign-in at the dev URL works (2026-11-18; the
  smoke test passed there with one person). Next: the token's groups and
  audience, so a group can limit who signs in; the programs' own memory
  peak during a full run (with cache it reached 4.21 GB; the how-to,
  section 6b).
- **Publishing the repository.** GSA asks for a GitHub repository;
  SECURITY.md says NASA's release review comes first. Which comes
  first for the submission.
- **Windows headed Chrome** was last run on 2026-11-02: run it again
  before the scored run, or state the limit.
- **The status table's thresholds** (step 10d shows the counts first).

**After the demo:**

- **Round 3's questions** (top of
  [the plan](plans/2026-11-16-after-round3.md)): does native browser
  validation fail TT 5.F; three key cells (MySearchStory; the search
  page's 19.A; breadcrumbs as their own way in 19.A).
- **The judge on types that fail the gate** (step 40). 4.B and 5.H
  meet both halves of the gate today; since 2026-11-18 the judge
  answers every type, so this decides how its FAILs on the others are
  shown.
- **Spec decisions left from the code review** (H-08, E-03, E-13,
  H-04, M-02, 4.F's "order does not matter"), the settle rule, 2.B's
  random content, a second browser, CLAUDE.md's lists, and
  SECURITY.md's two [TO CONFIRM] items: worded in
  [the archive](archive/2026-11-17-roadmap-before-the-last-day.md).

**Decided (Abby, 2026-11-17): VAST runs `:latest`** while TOBI is a
prototype, pulled at each restart, so it follows `main` (the guide,
section 9, "Updating"). A pinned, automatic update (a mirror of the
GitHub repository on VAST's Forgejo, recommended by the VAST admins,
whose workflow moves the deployment to each new build's commit tag;
the image is still built on GitHub, since VAST cannot build it) and
recording the image build in every report wait until after the demo.

**Decided (Abby, 2026-11-18): the server judge answers everything.**
With a gateway's URL and key set, the server's pinned model and prompt
answer every test's open questions (`JUDGE_BACKEND=auto`,
`JUDGE_TYPES=all`); without them, the calling agent does. The gate
(`evals/apijudge_gate.py`) was informative, not decisive, and a pinned
judge's answers, unsure ones included, are steadier than a calling
agent's, which were often not thorough. The gate keeps measuring it.
Step 40 (how a judge FAIL on a type that fails the gate is shown) is
still open: until it is decided, such a FAIL is an outcome like any
other.

**VAST hosting (2026-11-18):** the dev environment's URL is the
self-service host (20 GB, 4 GB of memory; a VAST admin), so TOBI is
hosted there, from Podman (the guide, section 6b); the YAML is for a
deployment beyond it. VAST's names are internal DNS only: Claude Code on
a NASA machine is the client, not claude.ai or Claude Desktop's cloud
connectors. VAST has no objection to the open status page (Abby).
The Keycloak client for the dev URL is minted; the admins recommend
VAST's `py_auth_boilerplate` as the reference for its sign-in, and later
a namespace and pod of TOBI's own from a Kubernetes file, and a mirror
on VAST's Forgejo whose workflows release each new image (the guide,
section 6a).

**Decided (Abby, 2026-11-17): the live status page is open.** The MCP
server keeps sign-in. A read-only page of what the server is running
and has just run (the URLs tested, progress, outcomes and the pre-SCRT
file in the viewer) may be read without it: the pages tested are
public, and VAST's domain is reachable only from NASA's network. It
starts, changes and answers nothing (step 41).

## Known limits, per test

Moved to [KNOWN-LIMITS.md](KNOWN-LIMITS.md) (2026-11-14).

## Later

- **The next tests: the visual-versus-code cluster** (10.x, 14.x, 15.A,
  18.A, 13.C; ANDI is the core evidence for most). Research, with two
  decisions to make in the specs (13.C: ANDI compares contrast after
  rounding, so 4.495 passes; 18.A: which windows, real browser zoom
  through our own extension, a second walk's time):
  [per test](research/2026-11-07-visual-cluster-per-test.md),
  [visual judgment](research/2026-11-07-visual-judgment-and-apijudge.md),
  [coverage map](research/2026-10-31-tt-coverage-map.md). Before 7.C and
  16.B, fix their `tt.json` steps from the printed pages (each repeats
  the previous test's "How to Test").
- **ANDI output beyond forms, and scanners.** Only ANDI's
  focusable-elements module runs today; contrast and image output are
  next (7.x, 13.C). axe-core or HTML_CodeSniffer, if used, are vendored
  with hashes and run on their own fresh load; a clean scan never means
  PASS ([solutions/andi-output.md](solutions/andi-output.md)).
- **Section 508 Baseline Alignment cases** for each new test: vendor with
  `tests/fixtures/baseline/sync_baseline.py` and load each in Chrome
  first.
- **Testing a batch of pages:** each page tested in full in its own call,
  the multi-page tests run once at the end, pages added to an existing
  run. Plan it with the store (Next, 4). Detail (Abby, 2026-11-15, for
  later, not built): with several pages of one site (a round's 8 to 10),
  9.A-9.C and 19.A run as a second pass across the batch, not per page.
  Each page of the site that any of them needs (the batch's pages, and
  19.A's site map, parents, children, home page and suspected aliases)
  is loaded and read once, and every link on it is matched against every
  page of the batch in one go: one site map read answers 19.A for all
  ten. Today the page cache (`pagecache.py`) already records and reads a
  page once per server session, so the loads are shared, but each page's
  run still decides alone and loads in its own order. With the batch pass, 19.A can search more widely and deeply (a site map's sub-pages, more related pages, every page's previous and next) because what one page's check finds is reused for the others instead of loaded again (Abby, 2026-11-15).
- **A "test a page" prompt** for operators who are not Trusted Testers.
- **The local runner** (part J; the pivot plan's decision 6): the
  browser on the user's machine for pages that are not public, the
  judge and the store on the host.
- **One watch on a paused clock** for 2.A-2.D and 3.A (part J), in
  place of 6.5 real seconds and two more loads.
- **Deployment:** network-level egress rules behind the egress proxy;
  browser calls with no time limit of their own (headed runs stalled
  when the screen locked); two egress tests that installed Chrome on
  Windows never exercises
  ([solutions/windows-chrome-results.md](solutions/windows-chrome-results.md)).
- **Only if time matters again:** more shared replays (4.C's widget check
  with 4.D's pass W; 4.C reading 4.F's pass R; 5.D and 5.F both filling
  fields); merging fixture pages (a merged page keeps every FAIL tied to
  its own instance and row).

## Dropped

- A separate results service and dashboard on Databricks (2026-11-11:
  the store on VAST replaces it).
- OpenACR export (2026-11-11: ACRs are product level, not page level).
- The agent eval's wording judge, seeded faults, GPT, Gemini and Ask Sage
  routes and DHS training pages (2026-11-11: the server is the judge).
