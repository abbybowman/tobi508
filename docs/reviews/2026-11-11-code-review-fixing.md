# Handoff: starting a thread on a roadmap step

The roadmap's "Order of work" (`docs/ROADMAP.md`) lists the steps to the
demo. Start each step in a new session with its prompt below. Most send
the thread to the instructions below the line (how to fix one item, the
working rules).

**A prompt is removed from this file when its step is merged,** so what
is listed here is what is left to start or still running.

**Done:** steps 1 to 10, 6b to 6h, 10a's freeze fix and 12a (PRs #39
to #101; `docs/archive/2026-11-14-roadmap-to-the-demo.md`). Round 3
is scored. Step 9b's thread is running.

**Order to start them:** threads A and B now, side by side (A's step
23 stops at midday Nov 17 if not merged); 10d when 9b is done; 12b
when the VAST environment exists; round 4 (step 10b) if I key one.
After the demo, bundles R1 to R5, one thread each: R2 before R4, R1's
step 26 before R5. Step 10c is done (`docs/plans/2026-11-16-after-round3.md`).

## Starting a thread

**Thread A, Opus: round 3's steps 21, 22, then a time-boxed 23** (now; before the Nov 17 cut)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (threads A and B, and the step
> entries 21 to 23 under "Next"), `docs/KNOWN-LIMITS.md`, and
> `docs/plans/2026-11-16-after-round3.md`: its questions at the top,
> causes 1 and 2, and the table at the end. Then follow the
> instructions below the line in
> `docs/reviews/2026-11-11-code-review-fixing.md` (how to fix one item,
> the working rules). Three steps, in this order, one pull request
> each; 21 and 22 never wait on 23.
>
> **Step 21: the browser's own error messages (5.F, 5.G).** On round
> 3's contact page the form has no error messages of its own: the
> browser's bubble is the only one. The tool read Chromium's
> `validationMessage` for every empty field as shown (5.F row M2),
> though the browser shows one field's bubble at a time, and J1 judged
> Chromium's words for `test@` (5.G N4), where Firefox, which I tested
> in, says only "Please enter an email address". Both PASS where my key
> fails. Make a native message NEEDS REVIEW in both specs, with a plain
> sentence that the message is the browser's, shows one field at a
> time and differs by browser. Fixture `5f/f01-native-validation` moves
> from PASS to NEEDS REVIEW; `5f/f15` (the page cancels the browser's
> message: FAIL) and the custom-message fixtures keep their outcomes.
> Whether TT 5.F fails native validation is my decision, still open
> (the plan's question 1): do not make it FAIL. MINOR versions, the
> lock, the hackathon evaluation line and slide.
>
> **Step 22: no outcome from a walk that missed the page.** On round
> 3's community pages (p07, p08), an Angular app, the forward walk
> found one link of 76 and 90: the inventory was empty when the walk
> began (the backward pass's cap was 50 = 3 x 0 + 50). 4.F said DOES
> NOT APPLY (A3, "only one element"; my key fails p08), 5.D said no
> fields (A1), 4.A's J1 was shown one reached stop and FAILed ~20
> controls (M6). A page whose controls a script draws 1.2 s after
> load reproduces it, and also gives 5.A DOES NOT APPLY and 4.A and
> 4.C PASS. Make these tests decide from the inventory taken after the
> walk (the "reached N of M" count 4.E and 4.A already print): 4.F A3
> needs one element there, not one stop; 5.A, 5.D and 5.F to 5.H's "no
> form fields" read it; 4.A's unreached candidates are C? while the
> walk is incomplete; 4.C does not PASS on it. Everything moves only
> to NEEDS REVIEW. Fixture: the late-drawn page (custom, no ACT case
> covers it); `4f/f07-one-link` and 5.D on `4d/f01-background-change`
> must stay DOES NOT APPLY.
>
> **Step 23, time-boxed: wait for the page to draw.** It stops at
> midday on Nov 17 if it is not merged, and returns to bundle R1.
> First a probe, no code: ask me for round 3's frozen archive, and on
> its four application pages (p07 to p10) in replay, measure how long
> each takes to draw, the focusable count at the start and when it
> stops changing, and whether the drawn page matches what my key
> describes (the forum's tag word cloud, the community's header
> search, SDE's "All" dropdown and search box, MySearchStory's
> carousel buttons). Also say where the address went on the first key
> press (4.E e1 on p07 and p08; the plan's cause 14), from the run's
> `steps.jsonl` if the archive has it. Show me the probe. Build only if
> the replay draws: before the walk, pass L and the site read, wait
> until the focusable count is unchanged for a short window, with a
> ceiling; take P2's press cap from the inventory when P2 starts.
> Rounds 1 and 2's pages should not move; if one does, say so cell by
> cell. Step 26 (one document at every address) stays after the demo.
>
> Run the rerun below twice: once when 22 is merged, before 23
> starts, so 21 and 22's moved cells reach me on their own; and again
> if 23 is merged.
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

**Thread B, Sonnet: round 3's step 31 (9.B), then 29's small part (5.B)** (now; before the Nov 17 cut, beside thread A)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (threads A and B, and steps 29
> and 31 under "Next"), and `docs/plans/2026-11-16-after-round3.md`:
> causes 6 and 10 and the table at the end. Then follow the
> instructions below the line in
> `docs/reviews/2026-11-11-code-review-fixing.md`. Two pull requests,
> in this order. Thread A changes 5.A, 5.D, 5.F to 5.H, 4.A, 4.C and
> 4.F at the same time: touch none of their specs.
>
> **Step 31: 9.B pairs equal links by alignment.** On round 3's
> Drupal pages there are three links named "Home" to one address (top
> bar, the footer's logo block, the footer list) and a fourth, the
> breadcrumb's, on every page but the home page. The spec pairs equal
> components "in order" (9.B Terms), so the home page's second "Home"
> pairs with the others' breadcrumb and the social links between them
> read as reversed (N3): FAIL on all six pages where my key passes.
> Reproduced on two scratch pages whose repeated links sit in no
> landmark; in distinct landmarks it PASSes. Pair equal components by
> an alignment that keeps their order where it can (the longest
> common subsequence of the two pages' lists), so an extra copy is an
> insertion, not a swap. Fixtures: the two pages (one with the extra
> breadcrumb "Home" in the same region), and a page where a real
> reorder among repeated links must still FAIL (two different links
> swapped, as `9x/a3-nav-reordered`, plus one where the same two equal
> links change places with a different link between them).
> `9x/a3-nav-reordered` and `9x/a4-nav-css-order` keep FAIL.
>
> **Step 29, the small part only: 5.B when 5.A could not decide.** On
> round 3's Drupal pages the search box sits in a panel the magnifier
> opens; 5.A's J1 was unsure (its picture showed the magnifier, not the
> field), and 5.B still said no field has a visible label (A2, DOES NOT
> APPLY; my key passes, counting the magnifier). Make A2 hold only
> when 5.A found every field unlabelled by a rule or by J1 =
> not_labeled; a field 5.A left unsure makes 5.B NEEDS REVIEW, and
> J1 = graphic makes the field an item. Fixture: a search box 5.A is
> unsure about (scripted answer unsure); a placeholder-only search box
> with no icon (round 1's nasa.gov) keeps 5.A FAIL and 5.B DOES NOT
> APPLY. The rest of step 29 (opening the panel; a magnifier as a
> label) is bundle R4, after the demo.
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

**Bundle R1, Opus: applications** (after the demo; steps 23 if thread A left it, 24, 25, 26, 35a, 35e)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (bundle R1 under "Next"),
> `docs/KNOWN-LIMITS.md` ("Found in round 3") and
> `docs/plans/2026-11-16-after-round3.md`: causes 2, 5, 14, 15, 17 and
> 21 and the table. Then follow the instructions below the line in
> this file. Round 3's p07 to p10 are Angular applications: they draw
> themselves after load, serve one HTML shell at every address, change
> their address on their own while starting, have no `<form>`
> element, and load code chunks when used. Order, wrong outcomes
> first: step 23 (if thread A did not merge it: its prompt above,
> probe first); **24**, 4.E's control replay waits until the same time
> after load as the original step (3 false FAILs; keep
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
> leaves no error state to walk (SDE home). Bundle R5 waits for your
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

**Bundle R2, Opus: 4.D and 5.D on what opens** (after the demo; step 27, then step 15's 4.D and 5.D part)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (bundle R2, and step 15 under
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
> page's 4.D cell after both. Bundle R4 waits for you (it changes 5.D
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

**Bundle R3, Opus: 4.A and 4.F** (after the demo; steps 28, 32, 33)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (bundle R3),
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

**Bundle R4, Opus: forms** (after the demo, once R2 is merged; the rest of 29, 30, 35b to 35d)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (bundle R4),
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

**Bundle R5, Opus: site tests** (after the demo, once R1's step 26 is merged; step 34, CILab, 9.C by function)

> Read `CLAUDE.md`, `docs/ROADMAP.md` (bundle R5 and step 19b),
> `docs/plans/2026-11-16-after-round3.md` (cause 13, "19.A on round
> 2's CILab page", the questions at its top),
> `docs/plans/2026-11-15-19a-finds-ways.md` and `docs/KNOWN-LIMITS.md`
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
> judge eval. R1 changed 9.A to 9.C and 19.A's A2 (one document at
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

**Step 10d, Sonnet: the README's status table, made by a script** (when step 9b is done)

> Read `README.md` ("TT tests in scope"), `tests/test_readme.py`,
> `evals/judging/round3/score.json`, and step 9b's results for rounds
> 1 and 2 (`evals/judging/gate-2026-11-16/`). The README's status
> table has grown into a list of results per round. It is to be a
> very high-level view: one colour and at most a few words per test.
>
> Write `evals/status_table.py`. It reads the latest scored result of
> each site (round 3's blind score; step 9b's reruns of rounds 1 and
> 2) and, per test, counts over all three: agree, PASS or DOES NOT
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

**Step 10b, Sonnet: round 4, a second blind round, if I key one** (the freeze the day I key the pages, then the run)

> The freeze. Read `docs/how-to/run-a-judging-round.md`. Freeze the
> pages I give you in this thread with the fuller freeze, check each
> recording against its manifest, and tell me anything that did not
> record. Do not run the tool on the pages, do not open my keys, and
> keep your branch unmerged with no pull request: no other thread may
> see the page list.

> The run, on Nov 17. Read the how-to and `evals/agent/README.md`.
> Run round 4 once on `main`'s head (record the commit; it should be
> 9b's), with the server judge answering: run, lock, then score
> against my keys. Never open my keys before the lock. Report per
> test and in all, and list apart the cells inside a web component or
> a frame. Keep each page's report and pre-SCRT file out of git.
> Change no code from what you find: list it for after the demo.

**Step 12b, Opus: the first deployment** (when the VAST environment exists)

> Read `docs/how-to/deploy-on-vast.md` and follow it with me: I run
> the VAST commands and paste what they print. Deploy, sign in from
> Claude Code, run `scripts/smoke_hosted.py` against the app's
> address, then one real page. Record what differed from the how-to
> and fix the how-to. Only when the smoke test passes on VAST, remove
> the two [PENDING] markers about the end-to-end sign-in
> (`docs/hackathon/evaluation.md`, `docs/hackathon/deck.md`) and
> update `SECURITY.md`'s status.

**Step 11, Sonnet: the second look's trial** (if the days allow)

> Read `CLAUDE.md`, then part F of
> `docs/plans/2026-11-12-coverage-second-look-thin-agent.md`, "Trial".
> Build `evals/second_look.py` and run it on round 2's 10 frozen pages
> with the rules as they were at round 2's lock commit, three repeats,
> through the judge's CLI route. It is a measurement, not a gate: write
> what it caught of the known wrong cells, what it missed, and what it
> flagged that my keys say is right, with tokens and time per page,
> into the plan's part F and `evals/README.md`. Stop there; the guard is
> a later step.

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
