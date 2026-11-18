# Handoff: starting a thread on a roadmap step

The roadmap's "Order of work" (`docs/ROADMAP.md`) lists the steps to the
demo. Start each step in a new session with its prompt below. Most send
the thread to the instructions below the line (how to fix one item, the
working rules).

**A prompt is removed from this file when its step is merged,** so what
is listed here is what is left to start or still running.

**Done:** steps 1 to 10, 6b to 6h, 9b, 10a, 10c, 12a, 21, 22, 23, 29's
small part, 31 and 36, and 4.F 1.11.0 (PRs #39 to #121; `docs/archive/`). Round 3 is scored.

**Order to start them** (the roadmap's "Order of work"): 9c now (both
pre-cut threads are merged); 10d after
9c; 12b when the Keycloak client arrives; 41 after the demo, beside the test rows; the after-demo rows one
thread at a time each, in the roadmap's order.

## Starting a thread

**Applications, Opus** (after the demo; steps 24, 25, 26, 35a, 35e)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (the applications row under "Next"),
> `docs/KNOWN-LIMITS.md` ("Found in round 3") and
> `docs/plans/2026-11-16-after-round3.md`: causes 2, 5, 14, 15, 17 and
> 21 and the table. Then follow the instructions below the line in
> this file. Round 3's p07 to p10 are Angular applications: they draw
> themselves after load, serve one HTML shell at every address, change
> their address on their own while starting, have no `<form>`
> element, and load code chunks when used. Order, wrong outcomes
> first: **24**, 4.E's control replay waits until the same time
> after load as the original step (3 false FAILs before step 23; in
> its rerun, `gate-2026-11-17-step23`, p07 and p08 are NEEDS REVIEW
> and p10 PASS, so check what is left first; keep
> `4e/f02-navigate-on-focus` FAIL and `4e/f12-pushstate-on-focus`
> PASS); **25**, the freeze runs the chunk store so the chunks are in
> the frozen recording (guard GU held 4.B on p07, p08); then the steps
> that turn NEEDS REVIEW into outcomes, each spec text shown to me
> for approval first: **26**, K-01's byte test only for the same path
> apart from the query string, in 9.A to 9.C and 19.A's A2, aliases
> and suggested pages (16 cells; only after 23, or 9.A could say DOES
> NOT APPLY on an undrawn shell where my key fails; K-01's
> query-string copy stays NEEDS REVIEW); **35a**, form "none" leaves out
> banner and navigation buttons, and 5.C's M5 also matches with spaces
> removed ("SDESDE" against "SDE"); **35e**, 4.C: a press that navigates
> leaves no error state to walk (SDE home). The site tests row waits for your
> step 26: do not touch 9.C or 19.A beyond A2 and the byte test.
>
> **The rerun, at the end** (ask me for the three rounds' frozen
> archives; I hold them): rerun the tests you changed, and the tests
> that read what you changed, on all three rounds' frozen pages, with
> the server judge as step 9b ran it (`evals/apijudge_gate.py run
> --round 1|2`; add `--round 3` for round 3's pages, frozen copies and
> keys, writing under `evals/judging/gate-<date>/round3/`, never under
> `evals/judging/round3/`, which is locked). Serve every page from the
> freeze, other pages too, and say if any was loaded live. Score each
> round with its own keys and scorer. Show me **every cell that moved,
> beside my key and its comment**, old outcome, new outcome and the
> rows that decided it, round by round; a cell on round 1 or 2 that
> moved gets its own line and a reason. Round 3's pages are
> development pages: this is a rerun, never in place of its score.
> Report verified (test or command) apart from assumed, and update the
> README's "Known wrong outcomes" table and `docs/KNOWN-LIMITS.md` for
> what you fixed, in the same commit (not the README's status table).

**4.D and 5.D on what opens, Opus** (after the demo; step 27, then step 15's 4.D and 5.D part)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (the "4.D and 5.D on what opens" row, and step 15 under
> "Next"), `docs/plans/2026-11-16-after-round3.md` (causes 3 and 7) and
> step 6g's notes on `opened.py`. Then follow the instructions below
> the line in this file. **Step 27 first:** on round 3's blog page each
> post's "Image" link passes 4.D's M6 on about 50 changed pixels
> (`MIN_CHANGED_PX` is 12 CSS px², whatever the element's size); my
> key fails it ("no visual indication of that focus"), and only guard
> RC holds the cell at NEEDS REVIEW. Make M6 also need the change to be
> a share of the element's size (measure the share on the three
> rounds' 4.D PASS instances before choosing it), else J1 (M7).
> Fixtures: a large image link with a small mark;
> `4d/f18-small-icon-clear-ring` keeps PASS and
> `4d/f19-small-icon-faint-ring` NEEDS REVIEW. **Only when 27 is
> merged:** step 15's 4.D and 5.D part, 4.D and 5.D read what menus and
> sections open (the shared walk, `opened.py`), so guard RC holds only
> what was not reached (round 3: 9 of its cells). Show me the blog
> page's 4.D cell after both. The forms row waits for you (it changes 5.D
> too).
>
> **The rerun, at the end** (ask me for the three rounds' frozen
> archives; I hold them): rerun the tests you changed, and the tests
> that read what you changed, on all three rounds' frozen pages, with
> the server judge as step 9b ran it (`evals/apijudge_gate.py run
> --round 1|2`; add `--round 3` for round 3's pages, frozen copies and
> keys, writing under `evals/judging/gate-<date>/round3/`, never under
> `evals/judging/round3/`, which is locked). Serve every page from the
> freeze, other pages too, and say if any was loaded live. Score each
> round with its own keys and scorer. Show me **every cell that moved,
> beside my key and its comment**, old outcome, new outcome and the
> rows that decided it, round by round; a cell on round 1 or 2 that
> moved gets its own line and a reason. Round 3's pages are
> development pages: this is a rerun, never in place of its score.
> Report verified (test or command) apart from assumed, and update the
> README's "Known wrong outcomes" table and `docs/KNOWN-LIMITS.md` for
> what you fixed, in the same commit (not the README's status table).

**4.A and 4.F, Opus** (after the demo; steps 28, 32, 33)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (the 4.A and 4.F row),
> `docs/plans/2026-11-16-after-round3.md` (causes 4, 11 and 12) and
> `docs/solutions/judge-eval.md`. Then follow the instructions below
> the line in this file. Order, the cell one step from unsafe first:
> **28**, on round 3's MySearchStory, 4.A's J1 answered "alternative"
> while its reasons say "not the same ... Not certain" (k1, M5 PASS),
> and M8 passed a custom control whose Enter only advanced a carousel;
> my key fails 4.A, and the cell is NEEDS REVIEW only because of
> another answer. Make an "alternative" whose reasons hedge count as
> unsure (rubric and answer check), and M8 need the key's effect to be
> the click's (same navigation, same region changed), else NEEDS
> REVIEW; a button whose Enter a carousel takes is a fixture, and 4.A's
> working custom controls keep PASS. Then **33**, 4.F: J1's order list
> and picture name every element its signals name (p02, p06 unsure for
> that); the rubric says an order that is odd but keeps meaning and
> operation preserves it (p04 FAIL where my key passes: "a little odd
> ... but preserved"); judge eval. Then, each spec text shown to me
> first: 33's S3 not raised for a jump to the top of the next column of
> one list (every Drupal footer) and S6 not raised when the popup is a
> listbox or menu reached by arrows (SDE's "All" dropdown, p09 FAIL);
> **32**, 4.A's U: a frame with no visible area (AddToAny's helper) and a
> listener on the window, document or body are not U, and calibrate
> `HOVER_MAX` on the three rounds' pages (4.A NEEDS REVIEW on all six
> Drupal pages). Keep 4.F's `f04`, `f05`, `f20`, `f21` and 4.A's
> fixtures at their outcomes.
>
> **The rerun, at the end** (ask me for the three rounds' frozen
> archives; I hold them): rerun the tests you changed, and the tests
> that read what you changed, on all three rounds' frozen pages, with
> the server judge as step 9b ran it (`evals/apijudge_gate.py run
> --round 1|2`; add `--round 3` for round 3's pages, frozen copies and
> keys, writing under `evals/judging/gate-<date>/round3/`, never under
> `evals/judging/round3/`, which is locked). Serve every page from the
> freeze, other pages too, and say if any was loaded live. Score each
> round with its own keys and scorer. Show me **every cell that moved,
> beside my key and its comment**, old outcome, new outcome and the
> rows that decided it, round by round; a cell on round 1 or 2 that
> moved gets its own line and a reason. Round 3's pages are
> development pages: this is a rerun, never in place of its score.
> Report verified (test or command) apart from assumed, and update the
> README's "Known wrong outcomes" table and `docs/KNOWN-LIMITS.md` for
> what you fixed, in the same commit (not the README's status table).

**Forms, Opus** (after the demo, once "4.D and 5.D on what opens" is merged; the rest of 29, 30, 35b to 35d, 37)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (the forms row),
> `docs/plans/2026-11-16-after-round3.md` (causes 6, 9, 18, 19, 20 and
> the questions at its top) and `docs/solutions/judge-eval.md`. Then
> follow the instructions below the line in this file. Order, wrong
> outcomes first: **35b**, 5.D on round 3's blog filters (FAIL where my
> key passes): focus that lands on the field's own label or wrapper,
> or the same field drawn again, is not a move, and an action whose
> request the recording cannot answer (the replay showed the site's
> error banner) is NEEDS REVIEW; `5d/f19-rerender-on-change` keeps FAIL.
> **35c**, 5.C on the community home (FAIL): J1 called "GMT" on an
> event card button a missing cue; the rubric says a control's own
> content is not an instruction or cue; judge eval. **35d**, 5.B on the
> FITS verifier (FAIL): read a visually hidden checkbox's `label[for]`
> as its visible label, and an answer whose `seen` says the item is
> not visible is unsure. Then, each spec text shown to me first:
> **29**'s rest, pass L opens the panel that holds a hidden field (the
> Drupal search box behind the magnifier) before its picture, and my
> decision whether a panel's opener showing a magnifier labels the
> field; **30**, 5.F to 5.H on a form with nothing to get wrong (filter
> checkboxes; a search box with nothing required): a spec decision
> with me first; `5f/f19-site-search-required` keeps its outcome.
>
> **The rerun, at the end** (ask me for the three rounds' frozen
> archives; I hold them): rerun the tests you changed, and the tests
> that read what you changed, on all three rounds' frozen pages, with
> the server judge as step 9b ran it (`evals/apijudge_gate.py run
> --round 1|2`; add `--round 3` for round 3's pages, frozen copies and
> keys, writing under `evals/judging/gate-<date>/round3/`, never under
> `evals/judging/round3/`, which is locked). Serve every page from the
> freeze, other pages too, and say if any was loaded live. Score each
> round with its own keys and scorer. Show me **every cell that moved,
> beside my key and its comment**, old outcome, new outcome and the
> rows that decided it, round by round; a cell on round 1 or 2 that
> moved gets its own line and a reason. Round 3's pages are
> development pages: this is a rerun, never in place of its score.
> Report verified (test or command) apart from assumed, and update the
> README's "Known wrong outcomes" table and `docs/KNOWN-LIMITS.md` for
> what you fixed, in the same commit (not the README's status table).

> **Step 37, added from the comparison of steps 9a and 9b:** pass L
> reads a frame's fields on the frame opened alone, so the judge does
> not see text beside the frame on the page (round 2: 5.A on 4914,
> 5.B on 5340 and 5144 FAIL where my key passes; 5.A on 5340 and 5.B
> on 4914 PASS on the same thin evidence). Picture the frame in place
> on its page. Do not hold only the FAILs: a guard that distrusts a
> picture when it fails and trusts it when it passes is the wrong way
> round. With it, 5.B's rubric on a search page's "Sort by" (round 2's
> search page).

**Site tests, Opus** (after the demo, once step 26 is merged; step 34, CILab, 9.C by function)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (the site tests row and step 19b),
> `docs/plans/2026-11-16-after-round3.md` (cause 13, "19.A on round
> 2's CILab page", the questions at its top),
> `docs/archive/2026-11-15-19a-finds-ways.md` and `docs/KNOWN-LIMITS.md`
> (9.C). Then follow the instructions below the line in this file.
> **CILab first** (a wrong FAIL): 19.A passed in step 6h's rerun (the
> home page's card link to `/cilab/index.html`, a verified alias, and
> the subpages' icon row) and FAILs in step 6g's, with the other pages
> loaded live. Ask me for both runs' folders; run 19.A alone on CILab
> in each mode, compare W1 and W6, and find what the FAIL read
> differently. Then **34**: my answers on whether a breadcrumb on a
> child page is a way of its own (the spec counts it as navigation)
> and whether a search results page is one page whatever its query;
> the spec text to me before you build (round 3's home page, blog and
> search page). Then **19b**, 9.C pairs by function, as the roadmap
> entry says, each candidate rule with a pair that must not FAIL and a
> judge eval. The applications row changed 9.A to 9.C and 19.A's A2 (one document at
> every address): build on it.
>
> **The rerun, at the end** (ask me for the three rounds' frozen
> archives; I hold them): rerun the tests you changed, and the tests
> that read what you changed, on all three rounds' frozen pages, with
> the server judge as step 9b ran it (`evals/apijudge_gate.py run
> --round 1|2`; add `--round 3` for round 3's pages, frozen copies and
> keys, writing under `evals/judging/gate-<date>/round3/`, never under
> `evals/judging/round3/`, which is locked). Serve every page from the
> freeze, other pages too, and say if any was loaded live. Score each
> round with its own keys and scorer. Show me **every cell that moved,
> beside my key and its comment**, old outcome, new outcome and the
> rows that decided it, round by round; a cell on round 1 or 2 that
> moved gets its own line and a reason. Round 3's pages are
> development pages: this is a rerun, never in place of its score.
> Report verified (test or command) apart from assumed, and update the
> README's "Known wrong outcomes" table and `docs/KNOWN-LIMITS.md` for
> what you fixed, in the same commit (not the README's status table).

**Step 9c, Sonnet: the last rerun** (when the two pre-cut threads are merged; by early afternoon on Nov 17)

> Read `CLAUDE.md`, `docs/plans/2026-11-08-apijudge-build.md` ("The
> gate"), the docstring of `evals/apijudge_gate.py`, and step 9b's
> write-up in `evals/README.md` ("Gate 2026-11-16") with its folder
> (`compare.py` is the comparison to reuse). Your work is step 9c of
> `docs/ROADMAP.md` "Order of work": step 9b again, on `main`'s head
> (record the commit), one repeat, the server judge answering every
> question type it can take, on all three sites' frozen pages: rounds
> 1 and 2 as 9b ran them, and round 3's ten pages (the pre-cut
> threads added `--round 3` to the gate script; if not, add it:
> round 3's frozen copies and keys, writing under your own gate
> folder, never under `evals/judging/round3/`, which is locked).
> Round 3's pages are development pages now: this is a rerun and is
> never reported in place of round 3's blind score.
>
> Before anything else, check and tell me if any fails: the three
> frozen archives are restored (ask me; never fetch a tested page
> live); and the sites' own search loads in your container for all
> three hosts. In step 9b, svs.gsfc.nasa.gov's new certificate chain
> stopped its search loading, and 8 of round 2's 19.A cells were left
> undecided for that reason alone: run one search per host through
> the tool's browser and show me the result before the run. Do not
> weaken any check to make it load; if it cannot load, say so and I
> will decide whether to run elsewhere.
>
> Run `--dry` first and tell me the request and token estimate. Keep
> each page's report and pre-SCRT file out of git; commit the scores,
> the comparison and the write-up. Report, per site and per test,
> beside step 9b's figures and round 3's blind score: agree, PASS or
> DOES NOT APPLY where my key fails, FAIL or DOES NOT APPLY where it
> passes, left for a person; every cell that moved since 9b (and, on
> round 3's pages, since the blind score) with whether my key agrees;
> and each test that ran out of its time budget. Put the result in
> `evals/README.md`. Do not edit the README's status table (step 10d
> writes it from your results), `docs/ROADMAP.md` or the prompt file.
> Give me the paths of your score files for step 10d.

**Step 10d, Sonnet: the README's status table, made by a script** (after step 9c)

> Read `README.md` ("TT tests in scope"), `tests/test_readme.py`, and
> step 9c's results for all three sites (I will give you the paths;
> until it is done, build against step 9b's,
> `evals/judging/gate-2026-11-16/`, and round 3's blind score,
> `evals/judging/round3/score.json`). The README's status
> table has grown into a list of results per round. It is to be a
> very high-level view: one colour and at most a few words per test.
>
> Write `evals/status_table.py`. It reads the latest scored result of
> each site (step 9c's rerun of all three; the judge answered every
> question type) and, per test, counts over all three: agree, PASS or DOES NOT
> APPLY where the key fails, FAIL or DOES NOT APPLY where the key
> passes, and left for a person. One rule gives the colour and the
> words, first match:
> - red, "passed a page a tester failed": any PASS or DOES NOT APPLY
>   where the key fails;
> - red, "wrong more often than right": more wrong than agreeing
>   among decided cells;
> - yellow, "often fails pages a tester passes": wrong on more than 1
>   in 5 decided cells;
> - yellow, "mostly left for a person": fewer than half the cells
>   decided;
> - green, "agrees with a tester": otherwise.
> Show me the table this gives and the counts behind it before you
> change the README: I may move a threshold.
>
> Then: the README table has the columns ID, test name, spec (version
> and link, as now) and status (the colour and those words, nothing
> else), with one line above it saying what the colours mean, which
> results it is from and that the counts are in `evals/STATUS.md`.
> The script writes the rows between two marker comments in the
> README, and writes `evals/STATUS.md`: per test and site, the counts,
> and which run each is from (round 3 blind; rounds 1 and 2 reruns on
> development pages). `tests/test_readme.py` fails when the README's
> rows are not what the script writes. Everything the old rows said
> about what a test reads or cannot do is already in
> `docs/KNOWN-LIMITS.md` or the specs: check each sentence you remove
> is there, and add the ones that are not. Never write "certified",
> "compliant" or "conformant" about a page; "agrees with a tester"
> is about our evaluation pages only, and the line above the table
> says so.

**Step 12b, Opus: the first deployment** (when the Keycloak client arrives)

> Read `docs/how-to/deploy-on-vast.md`, sections 6a and 9 first, and
> follow it with me: I run the VAST commands and paste what they
> print. VAST gives developers no app namespace: first run the image
> with sign-in at my dev environment's URL (Podman in the dev
> environment, port 8000, `FORWARDED_ALLOW_IPS` as section 6a found),
> sign in from Claude Code, run `scripts/smoke_hosted.py` against that
> URL, then one real page. Then fill `deploy/vast/tobi508.yaml` for the
> cluster admins (outside the repo: no internal host names in git).
> Record what differed from the how-to and fix the how-to. Only when the smoke test passes on VAST, remove
> the two [PENDING] markers about the end-to-end sign-in
> (`docs/hackathon/evaluation.md`, `docs/hackathon/deck.md`) and
> update `SECURITY.md`'s status.

**Step 41, Opus: the live status page** (after the demo; beside the test rows, since it touches no test or spec)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (step 41 and Abby's decision of
> 2026-11-17 above "Known limits"), `docs/how-to/get-started.md`,
> `docs/how-to/deploy-on-vast.md` (sections 4, 6a and 9),
> `src/tobi508/jobs.py`, `src/tobi508/routes.py`, `src/tobi508/app.py`
> (`http_options`), `src/tobi508/tools/run_tt_tests.py` and
> `run_status.py`, and `demo/prescrt-viewer/README.md`. Then plan with
> me before building; one pull request.
>
> **Why.** Using TOBI from Claude Code, I saw the run's progress only
> while a tool call was open: after `CALL_WAIT_S` the call returns a
> job and the progress line goes, and between `tobi_run_status` calls
> only my agent spoke. I want a page in the browser that keeps showing
> what the server is doing while I chat with my agent. A status line
> in Claude Code is out: too hard for our users to install.
>
> **What.** A read-only page served by the server over HTTP (way 3 of
> get-started, and hosted), refreshing itself: each run the server
> holds, with the page tested, its tests, state, the progress step and
> message, and times; when a run is done, its outcome per test and a
> way to open its pre-SCRT file in the viewer (`viewer.html`) in the
> browser. Each tool result that starts or waits on a run carries the
> page's address (one short field; keep tool output small), and the
> agent is told to give it to the user.
>
> **Decided:** the MCP endpoint keeps sign-in; this page is open
> without it, as `/health` is, on a server with `AUTH=oidc`, and shows
> every person's runs, URLs and results (my decision, recorded in the
> roadmap). Without sign-in the server still listens on loopback only:
> never change that rule (`app.http_options`).
>
> **Scope.** Only what the server holds now: jobs in memory
> (`jobs.py`) and run folders until they expire (`RUN_TTL_HOURS`).
> Nothing that outlives a restart or the 24 hours: that is the store,
> step 17. Over stdio there is no HTTP server, so no page; say so in
> get-started.
>
> **Rules to keep.** Read-only: GET only; it starts, answers and
> changes nothing. Page content is untrusted (`CLAUDE.md`, principle
> 5): every URL, title, message and file value is shown as text, never
> HTML, on the page and in the viewer (test it with a page title and a
> URL holding markup and script). No outside scripts, styles or
> requests; a strict Content-Security-Policy. The disclaimer on every
> view; never "certified" or "compliant". The page copies outcomes and
> decides none. The viewer today opens a file the user picks and makes
> no requests; how it gets a run's file (embedded by the server, or a
> same-origin fetch with its CSP changed to allow only that) is a
> choice to bring me with its trade-offs.
>
> **Tests:** the page answers without a token while `/mcp` answers
> 401; it shows a running job's progress and a finished run's
> outcomes; markup in page values is escaped; a POST is refused; the
> result field is present and small. Run it once by hand over way 3
> and show me a screenshot. Update the how-tos, `SECURITY.md` (an
> unauthenticated route), and, as a security control changed,
> `docs/hackathon/evaluation.md` and its slide in `deck.md`.

**Step 13, Sonnet: the scored run for the pitch** (Nov 18-19, when I say the submission commit is fixed)

> Read `CLAUDE.md` and `docs/hackathon/README.md`. I have fixed the
> submission commit: <commit>. Run the scored suite once at that commit
> as `docs/hackathon/README.md` describes, and fill every [FILL] in
> `docs/hackathon/evaluation.md` and `deck.md` from that one run, with
> its commit, date and environment. Remove a [PENDING] marker only
> where the work exists and is checked. Never describe a tested page as
> certified or compliant. Show me the filled figures before you commit.

---

You are working on one step of `docs/ROADMAP.md` "Order of work"; your
prompt names it. Most steps fix items from a finished code review of
this codebase (`tobi508`); steps 4 and 5 fix items from the
post-round 2 plan, and the same way of working applies.

## Read first, in this order

1. `CLAUDE.md`: the eight principles and the rules for specs, fixtures
   and docs. They bind every fix.
2. `docs/reviews/2026-11-11-code-review.md`: "The short version", the P0
   table, then the full entry of each item in your bundle (what is wrong,
   where, the smallest fix, how it was checked).
3. `docs/reviews/2026-11-11-code-review-pages/README.md`: the page and the
   command that reproduce each item, and what it printed.
4. For a check (2.A to 19.A): its spec in `specs/rules/`, and the reviewer's
   row-by-row table of spec against code in
   `docs/reviews/2026-11-11-code-review-notes/` (files E, F, H, M, N, K).
   The other raw notes hold measurements (T, W) and test coverage (Q).
   Severities in the raw notes were changed in the triage: the review file
   wins.

File and line numbers in the review are as of commit `e4d4165`. Lines
move: find the function by name.

## How to fix one item

1. **Reproduce it first.** Run the item's command from the pages README
   and see the outcome it lists. If it no longer reproduces, say so and
   stop on that item.
2. **Decide whether the spec changes.** The spec is the only source of
   outcome logic (principle 2).
   - The code does not do what the spec already says (E-01, E-07, F-15,
     H-03, N-08, K-06): fix the code, no spec change.
   - The spec's own rows or Terms give the wrong outcome (most items
     marked "spec change" or "(needs Abby)"): draft the spec change
     first, as a MINOR version, with the research CLAUDE.md asks for (TT
     text from `catalog.py`, the W3C Understanding page and techniques,
     ACT rules, the Baseline test). Show me the draft before building.
     `specs/rules/` needs my review (CODEOWNERS).
   - Every fix in the review moves a PASS or a DOES NOT APPLY toward
     NEEDS REVIEW or FAIL, or removes a wrong FAIL. If yours would turn a
     NEEDS REVIEW into a PASS, or remove a FAIL an answer key confirms,
     ask me first.
3. **Make the page a fixture.** Copy the reproducing page into
   `tests/fixtures/<test>/` under the folder's naming, with its expected
   outcome and rows in the test file, never in the page. Prefer an ACT or
   Baseline case when one covers the rule. Write the test, see it fail,
   then fix.
4. **Fix at the shared place when the item says so.** Several items are
   one cause seen in many checks (fragment-only address changes: C-03,
   F-06, H-11; "trap counts as complete": H-03, M-05, F-11; light-DOM
   reads: D-01, D-03, K-02, N-01, M-06). Fix the shared function and add
   a fixture per check it changes.
5. **Run what could have moved:** the check's own fixture file, its ACT
   and Baseline cases, and any other check that uses the function you
   changed. Not only the new test. For a long run, keep one line per test
   in a log (CLAUDE.md, "Commands").
6. **If a question, its rubric or its input changed,** run the judge eval
   for it (`docs/solutions/judge-eval.md`). Scripted answers in `tests/`
   test the rules, not the questions.
7. **Update with the fix, in the same commit:** the spec's `spec_version`;
   the README's status line for the test and its row in the README's
   "Known wrong outcomes" table (remove the case you fixed; add any new
   one you find), so the README says what the test can and cannot do
   today (Abby, 2026-11-12); `docs/hackathon/evaluation.md`
   and the matching slide when a spec version, evaluation method or
   security control changes; `docs/ROADMAP.md` "Known limits" when a limit
   is removed or newly stated.
8. **Mark the item in the review file:** add a line `- **Fixed:** <commit>,
   spec <id> <version>` (or `- **Not fixed:** <why>`) under the item's
   "Checked" line, and change its row in the P0 table to say fixed.
9. **Report what you verified and what you assumed,** separately
   (principle 6).

## Working rules

- One bundle or part per thread, on its own branch from `main`. Open a
  pull request every few items rather than one at the end, so other
  threads see the changes; do not start a second bundle.
- Several threads run at once and some change the same checks and
  specs. Before you bump a spec version, rebase on `main` and take the
  next free version. Keep each commit to one item so a conflict is
  small.
- Commit after each item, so a session that is cut off loses nothing.
- At most 3 subagents at a time, and only for separable work (writing
  fixtures from the pages, running fixture files). The first review hit
  the 5-hour usage limit with 18 at once, and this one hit it twice with 3.
- Do not rewrite `evals/judging/`.
- Do not delete `docs/reviews/2026-11-11-code-review-pages/` or the notes
  folder until every item that cites them is fixed.

## Which model for which bundle

From what this review showed: the Sonnet reviewers found and reproduced
problems reliably (every page of theirs that was run again gave the same
outcome), and were less reliable on how serious a problem was and on
claims they had not run (three leads were refuted, one test page proved
less than it claimed). So Sonnet where the item names the line and has a
reproducing page; Opus where the fix needs a decision across spec, code
and tests, or touches security.

| Bundle | Model | Why |
| --- | --- | --- |
| 1. One-line and one-function fixes | Sonnet | Each has a page, a named function and no spec decision |
| 2. Shadow roots | Opus | One shared reader replaces reads in five modules; every fixture must be rerun |
| 3. Spec decisions | Opus, with Abby | Research and a spec draft per item; the code follows the decision |
| 4. Traps and limits (the coverage record) | Opus for the design and the first two readers; Sonnet to carry it through the remaining checks | The pattern is the hard part; applying it is mechanical |
| 5. The watchers | Opus | Timing, sampling and what "observed" means; easy to fix one page and break another |
| 6. What the agent receives | Sonnet | The cuts are listed and measured; `tool_sizes.py` and the reviewer's method check the result |
| 7. The server judge and its gate | Opus | Security (B-01, B-02) and the evaluation method (L-02, L-03) |
| 8. Before VAST | Opus | Sign-in, ownership and the stores that fetch what a page names |
| 9. CI and tests | Sonnet for Q-01, Q-02, Q-08; Opus to design the grid of hard pages (Q-03), Sonnet to fill it | |
