# Evals: real agents answer the open questions

`tests/` answer every open question with scripted answers (what a correct
judge would say). That tests the rules, not the questions. Here, fresh
agents answer them for real, seeing only what a consumer agent would get.

The agent eval (a model driving this server, against the same model with
Playwright MCP) is in `agent/`: see [agent/README.md](agent/README.md).

## Run

```bash
uv run python evals/judge_eval.py prepare /tmp/eval   # packets in /tmp/eval-packets
# ONE fresh agent answers every packet folder (questions.json -> answers.json);
# one agent per folder costs ~55k tokens each (docs/solutions/judge-eval.md).
uv run python evals/judge_eval.py apply /tmp/eval     # follow-ups -> round2; score
```

**Isolation.** Each packet holds only the tool's own output: questions,
rubrics, inputs, page text, shared inputs, the evidence files they point to (copied from
`run://`), and the `tobi_answer_questions` description. Local URLs are mapped to
`https://example.gov/site/pageN.html` and folders are shuffled `qNN` IDs,
because fixture names describe the expected answer ("key-in-comment-only").
The answer key (`/tmp/eval/state.json`) is outside the packet tree. Agents
are told to open nothing else and to list every file they opened.

**Pictures (post-round 1 fix 19).** A fourth argument picks how the
packets give pictures: `all` (the default: copied in, as before), `none`
(left as `run://` links the agent cannot open, as for a real agent that
does not read them) or `retry` (as `none`, then each look-to-settle
question answered "unsure" comes back once with its pictures). The arm is
kept in `OUT/images.txt`. `TESTS` may be `all`:

```bash
uv run python evals/judge_eval.py prepare /tmp/eval-none all none
```

## Judging rounds: real pages against a tester's blind SCRT files

A certified tester running their own round: follow
[docs/how-to/run-a-judging-round.md](../docs/how-to/run-a-judging-round.md).

A round can be scored two ways, both against the same keys by commit and
reveal: the scan below (a script drives the tool; one agent fills in the
question packets), or the agent eval (`agent/README.md`: a model drives the
tool itself, beside a Playwright MCP baseline, on frozen copies of the
pages). Round 1 uses the agent eval.

`evals/judging.py` scores the tool on real .gov pages against a certified
Trusted Tester's SCRT files, by commit and reveal, so neither the tool nor
its developers see the pages or the answers first.

1. **Start a round.** The tester commits `evals/judging/<round>/pages.txt`
   when testing begins (not earlier: a page list in the repository lets
   development prepare for it). One page per line, its URL and the SHA-256
   of their SCRT file for it, in either order; `#` comments allowed. Hash
   the exact file to be uploaded (`shasum -a 256 *.json`, `sha256sum *.json`
   or `Get-FileHash *.json`) and do not re-save it in SCRT afterwards.
2. **Scan.** `uv run python evals/judging.py scan evals/judging/<round>`
   runs every implemented test on each page, with the round's other pages
   on the same host as `other_pages` (9.A-9.C, 19.A). In a container, set
   `BROWSER_CHANNEL=chromium HEADLESS=true`. The real allowlist applies.
3. **Answer.** ONE fresh agent answers every
   `<round>/packets/pNN/roundK/questions.json` into `answers.json` in the
   same folder, opening nothing else; then `apply`. Repeat until no page is
   open.
4. **Lock.** `uv run python evals/judging.py lock evals/judging/<round>`,
   then commit `results/` (reports, pre-SCRT files, HARs, `lock.json`).
5. **Reveal.** The tester adds their SCRT files to `<round>/keys/` (any
   names: they are matched to pages by hash) and commits.
6. **Score.** `uv run python evals/judging.py score evals/judging/<round>`
   writes `score.md` and `score.json` (scoring: `evals/scoring.py`, on the
   neutral comparison in `src/tobi508/compare.py`). It stops if a key
   matches no page, if a key's page (`P_Location`) names a different page
   than its line in `pages.txt`, or if `pages.txt`, a result or the scoring
   code changed after the lock (to score with older code, check out the lock
   commit). The rates open with how many pages were scored and why any were
   not. Add a line for
   the round below. Do not copy figures into `docs/hackathon/evaluation.md`
   until a final round is chosen.

Tests the tool does not perform yet, and tests the tester left blank, are
counted apart, never as agreement or disagreement.

**Freezing pages (later rounds).** Round 1 was tested live on the day of
the scan. Pages change, so later rounds record each page on the day the
tester tests it and scan that recording. Until a `freeze` command exists, in
Chrome: DevTools, Network tab, tick "Preserve log" and "Disable cache",
reload the page, then right-click a request and "Save all as HAR with
content". Whether a DevTools HAR replays like our own recordings is not yet
checked.

**Validated catches (Abby, 2026-11-06).** After the reveal, the tester may
confirm that the tool was right where it differed from their key (round 1:
Artemis III 4.D, a player button with no visible focus). They record it in
`<round>/adjudications.json` (page, TT test, the confirmed result, who,
when, why), never by editing a key, which is locked by its hash. The scorer
counts a tool result that matches as a **validated catch**, weighted +1 like
an agreement and shown apart (`evals/scoring.py`). The file sits outside
the lock, as the keys do.

## Gate 2026-11-13: round 2's 10 pages again, the server judge on every type (roadmap step 6)

Round 2's 10 frozen svs.gsfc.nasa.gov pages (Abby's `round2-frozen`
archive, every file checked against its manifest), tested once with
`main` at `c0236572` (steps 1 to 5 merged: PRs 39, 41, 42, 43, 44), the
server judge switched on for all 21 types it can take (4.C stays with the
client), CLI route, `claude-sonnet-5-5`, prompt SHA-256 `e8320f2c…`.
Folder `evals/judging/gate-2026-11-13/`: `dry-r1.json` (the count),
`r1/results/pNN/` (report and pre-SCRT per page), `gate.json`
(`apijudge_gate.py score`), `compare.md` and `compare.json`
(`compare.py`: beside round 2's three arm C repeats, per TT test, cells a
judge answer decided apart from the rest, guard CN's NEEDS REVIEW apart).
Scored with round 2's scorer (`evals.scoring.score` on `compare`,
unchanged since round 2's lock `e14580a`, with its adjudication); on
round 2's side it reproduces the locked rows exactly. Agent-assisted
results, not certified Trusted Tester results; a development site, one
repeat.

- **Cost.** Dry count: 46 requests, 187 questions, ~200k text tokens,
  173 pictures. Run: 48 calls, 0 failed, 224 questions answered, 34
  "unsure", none left open; ~0.62M input tokens (Agent C: 1.71M), 34k
  output, 328 s in calls. Browser time 78 min (dry) and about the same
  run; 14194 hit the run cap (below).
- **All 220 scored cells (per TT test):**

  | Run | False PASS | Missed fail (DNA) | False FAIL | Other | Needs review (guard CN) | Agree (of decided) |
  | --- | --- | --- | --- | --- | --- | --- |
  | Gate 2026-11-13 | **0** | **0** | **11** | 1 | 152 (14) | 56/68 |
  | Round 2 C repeats 1-3 | 3 | 2 | 24-26 | 9 | 86-88 | 94/132-134 |

  Judge-decided cells: 54 (round 2: 42): 0 false PASS, 0 missed fail, 4
  false FAILs (round 2: 11-13), 36 NEEDS REVIEW (5 CN), 14/18 agree
  (round 2: 16/27-29). Rule-decided cells: 166 (round 2: 178): 0 false
  PASS, 0 missed fail (round 2: 3 and 2), 7 false FAILs (round 2: 13), 116
  NEEDS REVIEW (9 CN), 42/50 agree (round 2: 78/105).
- **Round 2's 5 wrong PASS and DOES NOT APPLY cells are gone:** 4.A on
  CILab now fails with the key (a judge answer); 4.C and 5.D on 5340,
  and 9.A on CILab and 14592, are NEEDS REVIEW (the reveal guard, guard
  GU, the 600-item read cap). No new one.
- **The 11 false FAILs:** 6 are 19.A (CILab, 14592, 14194, 5340, 5144,
  4914; rule rows W3 G4) and come from **this container, not the rules**:
  the live site search's results page loads its results with scripts
  from cdn.jsdelivr.net and the site's `/static/`, and the browser here
  refused every one (`net::ERR_CERT_AUTHORITY_INVALID`: it does not trust
  the egress proxy's certificate), so no search ever showed results and
  W3 ("the search does not lead to the page") applied. Round 2's
  follow-up runs found 14194, 5340, 5144 and 4914 through the same search.
  It also shows a weakness: a results page whose own scripts failed is
  read as a finished search; W4 ("search not verified", NEEDS REVIEW) is
  the row for it. The other 5: 4.A home page (judge: 17 "no alternative"
  answers), 4.F home page and 5340 (judge: "does not preserve"), 4.D 14592
  (judge) and 5340 (rule; both as in round 2).
- **The run cap.** 14194 reached `MAX_RUN_S` (1800 s): 3.A's stepped
  capture took about 17 min (55 s in the dry run), so 5.A-5.H were not
  performed there (NEEDS REVIEW, "the run reached its time limit"; 7
  cells, keys Pass or Does Not Apply).
- **NEEDS REVIEW (152; round 2: 86-88), in three groups** (lists per
  cell: `compare.md`):
  - **Inside a frame or a web component: 19** (step 8's target), all
    frames, none web components: 5.A-5.H on 5340, 5144 and 4914 (forms
    in embedded frames) and 4.A on 5144 (a frame it could not read). The
    key fails 4 of them (5.C on 5340, 5144, 4914; 4.A on 5144): failures
    the frames hide today. 2 (5.H on 5144 and 4914) are also guard CN.
  - **Guard CN, the rest: 12,** all where the key says Pass (2) or Does
    Not Apply (10): 2.B and 3.A on more than 30 images (home, search,
    galleries, 4914: 6), 5.A, 5.B, 5.F, 5.G on the home page's forms
    hidden until opened (4), 5.H on a form that is only a button (home,
    search). Over all 14 CN cells the keys show no failure the guard held
    back: on these pages it cost agreements and found nothing.
  - **Every other reason: 121.** 2.C and 2.D on all 10 pages (20: moving
    content not settled in 6.5 s; as round 2); the reveal guard on 4.C,
    4.E and 5.D (20: "menus or sections that open"); 9.A and 9.C (20: the
    600-item read cap); 9.B (10: an other page not read whole); 4.D and
    4.F (14: the judge's "unsure"); the run cap on 14194 (7); 4.A (6:
    embedded players, a 40-element cap, controls asked about); audio,
    video or flashing not playable or checkable from the recording (9:
    2.A, 2.B, 3.A); 2.B moving regions the judge left unsure (3); fields
    the walk could not reach (2: 5.F, 5.G on 14592); and 10 others (98
    fields on search, a form sent to its server, 5.D focus events, guard
    GU 2, one open 4.C question, 4.B on 5340).
- **Per question type, read against "The gate" (one repeat; not a gate
  result, and the test-page half was not run here):**

  | Type | Judge cells | Decided | Agree | Wrong PASS | Wrong DNA | Wrong FAIL | Unsure | Against the thresholds |
  | --- | --- | --- | --- | --- | --- | --- | --- | --- |
  | 4.B | 5 | 5 | 5 | 0 | 0 | 0 | 0 | meets all but the cell count (5 of 6) |
  | 5.B | 8 | 2 | 2 | 0 | 0 | 0 | 6 | no wrong; too few decided (2) |
  | 5.C | 2 | 2 | 2 | 0 | 0 | 0 | 0 | no wrong; too few (2) |
  | 5.H | 6 | 2 | 2 | 0 | 0 | 0 | 4 | no wrong; too few (2) |
  | 5.D | 1 | 1 | 1 | 0 | 0 | 0 | 0 | no wrong; too few (1) |
  | 4.A | 7 | 3 | 2 | 0 | 0 | 1 | 4 | wrong FAILs 33% of decided (over 20%); too few (3) |
  | 4.D | 6 | 1 | 0 | 0 | 0 | 1 | 5 | wrong FAIL 100%; too few (1) |
  | 4.F | 9 | 2 | 0 | 0 | 0 | 2 | 7 | 2 wrong FAILs in a repeat (over 1); 100% |
  | 2.B | 3 | 0 | 0 | 0 | 0 | 0 | 3 | nothing decided |
  | 9.C | 7 | 0 | 0 | 0 | 0 | 0 | 7 | nothing decided (the read cap holds the cell) |

  2.A, 2.C, 2.D, 3.A, 4.E, 5.A, 5.F, 5.G, 9.A, 9.B and 19.A asked nothing
  the judge answered on these pages: no cells. No type has a wrong PASS or
  a wrong DOES NOT APPLY. `JUDGE_TYPES` is unchanged (empty).
- **Not verified here:** the test-page half of the gate
  (`judge_eval.py answer --backend api --repeat 3`); repeats; 19.A's live
  search in a browser that trusts the proxy; 14194 within the run cap.

## Run 34, 2026-11-13: 5.A 1.8.0 and 5.B 1.6.0 (a button with words labels its field), their packets

Abby, 2026-11-13: a button that is part of a field labels it whatever its words (TT p. 25 Note 3, "regardless of accuracy"), so 5.A 1.8.0 drops 1.1.0's rule that "Go", "Find" or "Subscribe" do not label a field (the rubric and question now say accuracy is another test's), and a text button in the field's input group or search form is row M2i like an icon. 5.B 1.6.0 judges the button's words as the field's near text. Rubric examples are on no fixture page (checked). 44 cases (5.A and 5.B), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **43/44 match**, no false PASS.
- **The new cases:** "Subscribe" under a lone email box (F40) was answered labeled for 5.A and not descriptive for 5.B; the last of three fields with only the form's Continue button below (F41) not_labeled.
- **The mismatch is safe:** the arrow (F37) unsure again (NEEDS REVIEW against FAIL), as in run 33.
- **Unclear to it:** whether a page heading ("Find an office") over a lone box labels it (it answered not_labeled; F02 expects FAIL); a cropped picture over two rows of "Name:"/"Street:".

## Run 33, 2026-11-13: 5.B 1.5.0 (a field labelled only by an icon), its packets

Fix 8b (Abby, 2026-11-13; TT p. 25 Note 3, "regardless of accuracy"): 5.A 1.7.0 counts an icon button that is part of a field as its label (row M2i, no question), so run 32's tree and arrow pages now pass 5.A; 5.B 1.5.0 judges the picture. The rubric's picture examples (a flower or a company logo on a search box, a telephone on an email field) are on no fixture page; the first preparation named the fixtures' own pairs and was redone. 29 cases (5.B J1), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **28/29 match**, no false PASS.
- **The icon cases:** the magnifier (F27) all_descriptive; the tree (F36) and the envelope on a search box (F39) some_not_descriptive.
- **The mismatch is safe:** the arrow (F37) was answered unsure ("whether a right-arrow counts as a commonly understood search symbol"), NEEDS REVIEW against FAIL, as Abby wants for a picture that does not settle it.
- **Injection pages:** it named the text in two pages that told it how to answer, and ignored it.
- **Unclear to it:** which numbers to name when the same labels repeat (it listed all four, which matches).

## Run 32, 2026-11-13: 5.A 1.6.0, fix 8's icon cases, its packets

Fix 8 sends a placeholder-only field with an icon button in its group to J1 (the graphic case). Run 31 had only the magnifier page; this run adds two pages where the icon must not count: a tree icon (F36) and an arrow, which says only what the button does (F37). 18 cases, 21 questions (all 5.A J1), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **18/18 match**, no false PASS, no "unsure". Leak grep clean (also for "tree" and "arrow").
- **The icon cases:** the magnifier (F27) was answered graphic; the tree and the arrow not_labeled, each reasoned from the rubric (a tree does not plainly label a search box; an arrow is a "Go"-type control).
- **Unclear to it:** whether the tree is not_labeled or unsure (either is safe: FAIL or NEEDS REVIEW); quotes are asked only for labeled.

## Run 31, 2026-11-13: 5.A 1.6.0 and 5.C 1.7.0 (an option's own row; a heading directly over a set), their packets

Post-round 2 fix 9c narrows an option's visible text to its own row (result cards beside a filter no longer reach it) and fails a heading directly over a set without a question (M3h). 27 cases, 35 questions (5.A and 5.C), one fresh Sonnet agent, Read/Write/Glob only, inside the packets: **27/27 match**, no false PASS, no "unsure" answer. Leak grep clean.
- **The new cases:** the two filter sets beside result cards (F33) were asked once per set, each box's visible text its own label only, and answered complete; the plain-text question over wrapped-label radios (F30) was answered missing; the heading with "Choose any." between it and the set (F31) was answered missing, quoting "Choose any." (it read the heading as a section title), which reaches M7 (FAIL) as expected.
- **Unclear to it:** whether a section heading ("Newsletter", "Find an office") labels a field beside a "Subscribe" or "Find" button (it answered not_labeled, which matches); whether a page title above a set is its question when no `heading_over_them` is given (it answered complete, which matches); a tight crop around a field with nothing near it (5.A, answered not_labeled).

## Run 35, 2026-11-12: post-round 2 fixes 12, 13, 14, 24, 25, 26, 27 (the CLI route)

The server judge's own route (`answer --backend api`, `claude -p`, Sonnet), two repeats each, on the cases `prepare` found to ask questions, before and after each change. Judge eval only: it hands pictures over as the judge's own requests do, not as links a client agent must open. The baseline before any fix (4.F, 9.C, 4.A, 4.D, 2.B: 32 cases): **31/32 in both repeats**, no wrong PASS; the miss is 4.F f05 (main content before a left-hand list of links), a false FAIL in repeat 1 and an unsure in repeat 2. Unsure answers in the baseline: 4.D f09 and f16 (faint changes; both expect NEEDS REVIEW), 2.B t-below-fold in repeat 2.

**Fix 12, 4.F 1.7.0 (rubric: meaning and operation, not the drawn order).** Cases: the 11 existing plus F20 (tiles reached right to left), F21 (a tile's buttons in another order than drawn) and F22 (numbered steps out of sequence: must still FAIL), 14 cases.
- **Before (rubric 1.6.0):** 12/14 and 11/14. F20 answered does_not_preserve (FAIL, key PASS) in both repeats; F21 and F05 unsure in some.
- **After (1.7.0):** **14/14 and 14/14.** F22 is still does_not_preserve; no wrong PASS; the rubric's examples are on no fixture page's words except main content before side navigation, which is also F05's shape (Understanding 2.4.3 states it that way).
**Fix 13, 4.F 1.8.0 (the order picture draws only stops with a visible box).** New case F23 (a skip link shown only on focus, a one-pixel screen-reader link, two independent columns); 15 cases.
- **Before (1.7.0 code):** F23, F04 and F05: 3/3 in both repeats, but the picture drew badges 1 and 2 on empty boxes (the two hidden links). The answers did not change: these hidden links were not what the judge hesitated over, so this run shows the picture, not an answer, was wrong.
- **First after run:** 14/15 and 15/15; F16 (a site overlay that is not the menu) went unsure in 3 of 6 runs, though its input was identical. The "drawn: false" sentences were in every question. Added to the question and rubric only when a stop is undrawn, F16 was **15/15 in each of three repeats**. Lesson: a sentence about a case that is not on the page makes the agent less sure (same as "A rubric's only example becomes the rule").
- **After:** **15/15, 15/15 and 15/15**, no wrong PASS, nothing left open.
- **Limit:** the judge eval cannot show how an agent that never opens the order picture answers (see "The judge eval hands images over as files" in docs/solutions/judge-eval.md).

**Fix 14, 9.C 1.5.0 (pair repeated components, not every link with one destination).** New case g1/g2: body links to the same addresses with different words, in the same header and menu; expected PASS.
- **Before (1.4.0):** 2/3 in each of three repeats. The new case asked 2 questions and the judge answered **inconsistent** on both, every time ("same destination, different words"): a false FAIL (key Pass in round 2). Renamed and paging matched.
- **After (1.5.0):** **2/2 in each of three repeats**; the body-link pair asks no question (the rule decides: PASS, nothing to compare), so it leaves the eval. Renamed (header and search worded differently: FAIL, the nearest case that must still FAIL) and paging match.
- **Is 9.C's eval clean?** Yes, on the 2 cases that now ask (6 answers, all as expected, none unsure). It is thin: only the two cases ask a question, and the case that showed the false FAIL no longer asks one, so the change is shown by the rule's own test (`test_9c_pairs_by_destination_only_inside_a_repeated_block`) and by "before" above, not by a judge answering it.

**Fix 24, 4.A 1.8.0 (a scroll arrow whose items Tab reaches).** New cases F20 (an arrow over six cards that each hold a link: expected PASS) and F21 (the same arrow over six text-only cards: must still FAIL); 12 cases.
- **Before (1.7.0 code):** 10/12, 12/12, 12/12. F20 and F21 were answered correctly every time (alternative, no_alternative), so on this tidy page the judge needed no help; the two misses in repeat 1 are the baseline's 4.A f01 and f04 (unsure, expected FAIL). Round 2's real carousels (21 unsure answers) are not in the eval.
- **After (1.8.0):** F20 asks no question (row M3s), so 11 cases ask; **10/11, 9/11, 11/11**. The misses are unsure on f01-click-only-text and inject-f01, which expect FAIL: the same pages that were unsure before, no wrong PASS. They are the case fix 25 is about ("See rates" goes to `#rates`, which does not say it is the same job).
- **What this does not show:** that a real carousel is decided; its arrows are often moved by a transform, which the check does not see. Re-score on round 2's pages in step 6.

**Fix 25, 4.A 1.8.1 (J1 gets where the candidate goes).** The mechanical half (a reached link with the candidate's address matches without a question) was already built as M3 in 4.A 1.6.0; what was left is the destination in J1's input: `candidate.goes_to` (a link's address, or where a click that navigated went) and a rubric sentence that a reached link to the same address is already matched and one to a different address counts only if it plainly does the same job. New case F22 (a card whose click goes to `#form-b`; the one reached link goes to `#form-a`; expected FAIL).
- **Before (1.8.0 code):** 12/12 in each of three repeats (F22 answered no_alternative every time).
- **After (1.8.1):** 12/12 in each of three repeats.
- **Reading:** no change the eval can see. The earlier unsure answers (4.A f01, f04, inject-f01: "does not clearly do the same job") did not recur in either run, so they were run-to-run noise on a small sample, not something the field fixes. The field is evidence the judge can read, not a measured improvement.

**Fix 26, 4.D 1.6.0 (pictures big enough to judge; the ring as a fact).** Small elements are pictured with at least 160 x 100 CSS px of page around them, pictures under 480 px on the long side are enlarged for the judge, and `changed_pixels` gains `sides_changed` and `ring`. New cases F18 (a clear ring drawn by a sibling: the rule decides it, M6, so it asks nothing) and F19 (a 1 px near-white ring round three 44 px circles: must stay NEEDS REVIEW); 4.D cases that ask: f09, f16, f19.
- **Before (1.5.0):** 3/3 in each of three repeats; all answers unsure: "a thin 1px ring ... too faint to tell" (F19, 64 x 64 px pictures).
- **After (1.6.0):** **3/3 in each of three repeats**; all unsure, on purpose: the answers now describe the ring ("a ring appears ... near-white on white") and still say it is too faint. Pictures 480 x 300. A ring is a shape, not a verdict.
- **Ring definition changed after CI (same spec version, before merge):** CI's fonts made a colour change inside a link's text reach all four edges of its box, so f16 was called a ring. The ring now counts only changed pixels in the band just outside the box (at least 6 CSS px per side), never inside it. Re-run: **3/3 in each of three repeats**, all unsure as before.
- **What this does not show:** whether round 2's 7 unsure cells (48 x 47 px pictures; the key passes) now get an answer. No fixture here is a visible-but-not-strong ring the key would pass, and picking one would mean choosing the answer; the effect on real pages is for step 6 (the round 2 rerun). The eval shows only that no faint change turned into a yes.

**Fix 27, 2.B 1.3.0 (a region with no visible motion is not moving).** Pass T finds a pixel change at a difference of one; a region of pixels on the top page now counts as moving only when its box differs by 8 of 255 or more somewhere between frames. New cases t-color-hair (a 41 px box whose colour moves by 3 of 255: expected DOES NOT APPLY) and t-color-subtle (the same box moving by 23 of 255, the nearest case that must still be blinking: expected FAIL); 9 cases.
- **Before (1.2.0 code):** 6/9, 7/9, 8/9. t-color-hair asked J1 and was **unsure in 3 of 3** repeats ("box is blank or faint in both pictures"), NEEDS REVIEW against the key's DOES NOT APPLY. t-color-subtle and t-below-fold were unsure in some repeats.
- **After (1.3.0):** 6/8, 7/8, 6/8. t-color-hair asks nothing and gives DOES NOT APPLY by rule (A2) every time, so it leaves the eval (8 cases ask). The misses are unsure on t-below-fold (the baseline's miss) and on **t-color-subtle**, 3 of 3 (before: 2 of 3). That page's question is the old J1 about a small status box, and the judge says it is "not clearly a loader or a game, so the pictures do not settle it": a safe unsure, not changed by this fix, and not tuned here because making J1 answer it would mean pushing it toward not_essential.
- **No wrong PASS in any run.** The rule's risk is a false DOES NOT APPLY: a change under 8 of 255 in every frame is dropped (it is also noted in the finding). A slow fade is kept, because the box is compared with its first frame as well as the frame before.

## Run 30, 2026-11-07: 4.D 1.3.0 (where the changed pixels sit), its packets

4.D was missing from `judge_eval.py`'s cases (its custom fixtures and its ACT cases); both are in now. 2 cases ask (F09's faint outline, F16's faint colour change with a counter beside the link), 4 questions, one fresh Sonnet agent: **2/2 match**, all four answers unsure, no false PASS.
- **`changed_pixels`:** it matched the numbers to the pictures (touching only for the thin outline, on the element for the colour shift) and saw the counter's pixels as elsewhere.
- **What the numbers do not say:** how visible a change is; hundreds of pixels can still be a shift no one sees, which is why it answered unsure.
- **Rules:** it opened the two evidence JSON files the questions' `evidence_paths` name, inside the packets.

## Run 29, 2026-11-07: pictures and guards (2.B 1.1.0, 4.E 1.2.0, 4.F 1.3.0, 5.C 1.4.0, 5.D 1.2.0), their packets

2.B content below the first screen in crops; 4.F's order picture cropped to the stops in question; 4.E J1 and 5.D J2 given `covers_window` and `modal`, with content_only over half the window or modal refused by rule; 5.C text drawn by CSS in `visible`. 45 cases, 51 questions (7 2.B, 4 4.E, 11 4.F, 7 5.C, 16 5.D), two with a follow-up round, one fresh Sonnet agent: **44/45 match**, no false PASS, no false DNA. Leak grep clean.
- **The new cases all match:** the badge below the first screen, answered from its crops (was unsure in run 16); the tips panel and the terms panel over most of the window, answered changes_context; the long report's interleaved form, from the crop; the "*" drawn by CSS, answered missing.
- **The mismatch is safe:** 4.F f05 (main content before a left-hand list of links) was unsure, NEEDS REVIEW against PASS. Run 25 raised the same gap: the rubric does not say how to treat main content reached before a left sidebar.
- **Pictures:** it opened the crops for every 4.F case that had one, both 2.B crops, the 4.E and 5.D after pictures, and the 5.C pictures.
- **Unclear to it:** a menu whose items the next Tab skips (4.F, as run 25); whether "Mission status" over three options is their question (5.C; it answered missing, which matches); grouped 5.D questions, answered once for every field listed.

## Run 28, 2026-11-07: reading questions without pictures (2.D 1.1.0, 5.F 1.3.0), their packets

2.D J1 and J2 and 5.F J1 are settled by reading, so their pictures moved from the question input to evidence only (Abby, 2026-11-07); the agent is no longer asked to say what a picture shows for them. 5.F J2 (the field's look) keeps its pictures. 19 cases (2 2.D, 17 5.F, one with a follow-up round), one fresh Sonnet agent: **19/19 match**, no false PASS, no answer refused. It opened pictures only for the 5.F J2 questions, which name them.
- **Limit:** both 2.D cases expect PASS, so no fixture checks a 2.D not_sufficient answer without the picture.
- **Rules:** it used one read-only Bash call and Grep inside the packets, against its instructions (Read, Write and Glob only); the follow-up round used only the allowed tools.
- **Unclear to it:** whether "Go" in 5.F f11 is a search or filter button (it picked "Send my question", which matches); "Enter your full name" as a reference to the Full name field (it answered described, which matches).

## Runs 26 and 27, 2026-11-07: 9.C 1.1.1 (when names show different things), its packets

The rubric now says names that name different things count as
different_function, and different words for the same action are
inconsistent. 2 cases, 4 questions, one fresh Sonnet agent each run.
- **Run 26:** 2/2, but the rubric's examples ("Contact" / "Get in touch",
  "Search" / "Find") were the fixture pairs themselves. The agent said "the
  rubric names this exact pair", so the run tested matching, not
  judgment.
- **Run 27:** the examples were changed to names on no fixture page.
  **2/2 match**, no false PASS, each answer reasoned from the evidence:
  same destination with different words is inconsistent; different
  destinations are different_function.

Still unclear to the agent: links named "Go to page N" whose number does
not match where they go. It followed the different-destination rule,
which matches.

## Run 25, 2026-11-07: compact question inputs (4.F, 5.B packets)

After the result refactor (agent follow-through change 2b), question
inputs as sent round coordinates to one decimal and leave out empty fields.
33 cases (11 4.F, 22 5.B), one fresh Sonnet agent: **33/33 match**, no
false PASS. It opened every picture and found each one readable.

What it found unclear:
- **Where 5.B puts numbers:** the question says "in elements", but the
  `element` field's description says "from input.stops".
- **4.F main content before a left sidebar:** the rubric does not say how
  to treat main content reached before a left-hand sidebar.
- **4.F menu skipped by the next Tab:** the rubric does not say whether a
  menu whose content the next Tab skips counts as reached far from its
  trigger. It answered does_not_preserve, which matches.

## Run 24, 2026-11-06: `seen` and `picture_error` (4.D, 4.F, 5.A, 5.C packets)

Answers to a question whose input names a picture now need `seen`
(something the picture shows), or `picture_error` with unsure; a bare
answer is refused (agent follow-through plan, change 3). 29 cases, one
fresh Sonnet agent: **29/29 match**, no false PASS, no answer refused. It
opened every picture, filled `seen` with what the numbered or outlined
elements showed, and never needed `picture_error`. It used Bash once
(read-only, a packet file) against its instructions. Points it raised:
- **Shared texts are easy to miss.** About half the cases point to
  `question_texts`.
- **The `answer_format` line is long.** Read shows it on every packet file.
- **`choice.quote`:** whether it is needed for "labeled" or "missing" is
  not said.
- **Close calls it flagged:** 5.A's "Find an office" heading over a field
  with only a Find button (it answered not_labeled), and a sidebar order
  in 4.F (preserves). Both match.

## Run 23, 2026-11-06: 5.C 1.3.0 (the heading over an option), its packets only

J1's input now gives an option's heading (`heading_over_it`,
`heading_over_them`) and its rubric names a heading that is the question
of a set (an example not on any fixture page, "Delivery speed"). 6 cases,
one fresh Sonnet agent: **6/6 match**, no false PASS. On F19 it answered the
set's one question `missing`, quoting the heading "Mission status", which
now reaches M7 (FAIL), as Abby judged NASA's Missions page. It read every
shared question through `question_texts` without trouble. It also used
Grep once on a packet file, within the packet.

## Run 22, 2026-11-06: 5.C 1.2.0 (options of one set asked once), its packets only

6 cases, one fresh Sonnet agent, Read/Write/Glob only. **6/6 match** after
one expectation was corrected: on the new F19 (three filter boxes under the
heading "Mission status") it answered the set's one question `missing`,
quoting the heading, where the test data had said `complete`. Its reading
is the careful one (the rubric counts a heading whose absence could
confuse), so F19 now expects that answer. Because pass L does not count a
heading as text beside a field, M7's quote check cannot pass and each box
is M9 (NEEDS REVIEW, safe). That is a spec gap for Abby: NASA's Missions
page, which the key fails on 5.C, would stay NEEDS REVIEW this way. It
found the grouped question clear.

## Run 21, 2026-11-05: the pointer wording (5.D), its packets only

After run 20, a shared question's `question` and `rubric` say where the
text is. 15 cases; one fresh Sonnet agent, Read/Write/Glob only: **14/14
scored match** (F10's follow-up left open), none unsure. It found the
shared text through the pointer ("clear once I did"). It also noticed that
5.D J1's rubric example "Choosing a state takes you to its page" is the
very sentence on fixture F02 (and F07's page): the eval gives that answer
away. Fixed after the run: F02 and F06 are reworded, so no fixture page repeats
a rubric example.

## Run 20, 2026-11-05: shared question texts (5.C, 5.D), their packets only

Packets now carry `question_texts`, as a client gets them (post-round 1
fix 6b): a question that shares its question and rubric with others in its
run names a key there instead. 20 cases; one fresh Sonnet agent: **19/19
scored match** (5.D F10's follow-up round left open), none unsure. It
answered the shared questions correctly but said their `question` and
`rubric` were empty and that it took the text from sibling packets: it
had not seen `question_texts` in the same file. So a shared question's
fields now say where its text is (`Shared with other questions: read
question_texts["5.D-J1"].question.`). It also wrote its answers with one
Bash call, against its instructions (it opened nothing outside the
packets).

## Run 19, 2026-11-05: fix 19's picture arms (4.A, 4.D, 4.F, 5.A-5.D)

The same 71 cases prepared three ways (`all`, `none`, `retry`), each
answered by one fresh Sonnet agent with the same prompt; `retry`'s first
round reused `none`'s answers (identical packets), then a fresh agent
answered its picture round (5 packets). 70 cases scored in each arm (5.D
F10's follow-up round left open in all three).

| Arm | Match | False PASS | False FAIL | Unsure | Agent tokens |
| --- | --- | --- | --- | --- | --- |
| `all` (pictures from the start) | 67 | 0 | 0 | 3 | about 296k |
| `none` (`run://` links only) | 64 | 0 | 1 | 6 | about 300k |
| `retry` (pictures for unsure answers) | 69 | 0 | 1 | 0 | about 300k + 96k |

- Without pictures the agent answered 5.A F09 (a magnifier icon is the
  search box's label) `not_labeled`, sure of itself: a false FAIL. The
  retry arm cannot catch it, since only unsure answers come back.
- The retry round settled all 5 of its unsure answers correctly (two 4.F
  orders, 4.A, two 5.B forms).
- Pictures cost little here: `all` used about as many tokens as `none`
  (each agent's fixed start-up and the questions dominate). The retry
  round's 96k is mostly a new agent's start-up; in real use the same
  agent would answer it.
- The `all` arm's three mismatches are unsure answers (NEEDS REVIEW), so
  the arms differ by agent as much as by pictures: one run per arm.

## Run 18, 2026-11-05: post-round 1 fixes (4.F, 5.A, 5.B, 5.D), their packets only

`prepare OUT 4.F,5.A,5.B,5.D` (images `all`): 61 cases ask questions,
including the new F15 (5.D: one J1 for four filter boxes) and F16 and F17
(4.F: a site overlay; a card grid). One fresh Sonnet agent, file tools
only, answered all 61 (about 223k tokens), then a second answered 5.D
F10's follow-up round. **60/61 match, no false PASS.**
- 5.D F15: `not_told` for the four boxes at once (FAIL, as expected).
- 4.F F17: `preserves` for a card grid read row by row (the rubric's new
  line), PASS.
- 4.F F16: `does_not_preserve` where the test data said `preserves`:
  after the menu opens, the next Tab lands in the overlay, which sits
  between the button and its menu. The agent is right, and F16 now
  expects FAIL through J1. The fix (no mechanical M2 for a dialog the
  menu did not open) is unchanged.
- It opened only packet files, and each 4.F order image and 5.A image a
  question named.

## Run 17, 2026-11-04: 2.A (draft spec 0.2.0), its packets only

`prepare OUT 2.A`: one case asks a question (2.A asks none of its own):
the page's first text, "Press Ctrl+Shift+M to mute the sound." (J2).
Preparing it showed that 2.A had borrowed 2.C's J2 wording ("pause, stop,
hide or slow"), which leaves out muting and the volume that 2.A's ER 1
counts: a careful agent could have answered no, a false FAIL. 2.A now has
its own J2 ("pause or stop that audio, or turn its volume down or mute
it"). Leak grep clean. One fresh Sonnet agent, told to use file tools
only: **1/1 match**: describes, key Ctrl+Shift+M; the tool pressed it once
and the audio was muted (K4, then E3, gated). It opened only packet
files.

## Run 16, 2026-11-04: 2.B (draft spec 0.2.0), its packets only

`prepare OUT 2.B`: 7 cases ask questions (`test_fixtures_2b.EVAL`): an
infinite spinning badge, a marquee, a two-colour blink, a four-colour
cycle, a sliding carousel, a badge with a "Pause animation" button (J2 in
round 2, after the probe found it works) and a badge below the first
screen. Leak grep clean. One fresh Sonnet agent, told to start no
sub-agents and write no scripts (about 100,000 tokens, 34 s, plus round
2): **7/7 match, no false PASS, no false DNA.** Every J1 was not essential
except the badge below the first screen, which it answered unsure: no
frame shows it (A5, NEEDS REVIEW, as intended; a crop of the content
itself would let J1 settle it, a follow-up). Its least sure calls: the two
spinning squares, which could be loading indicators; the usable page
around them decided it. It read one file through a shell one-liner and
wrote the answers with printf, against its instructions (no file saved
outside the packets).

## Run 15, 2026-11-04: 2.C and 2.D (draft specs 0.3.0 and 0.2.0), their packets only

`prepare OUT 2.C,2.D`: 10 cases ask questions: 5 ACT efbfc7 cases (four
J1 on a working Stop, Pause or Hide button; passed 5's J2 on "activate the
"Control changes" button"), and 6 custom pages in `tests/fixtures/2x/`
(`test_fixtures_2x.EVAL`): pause, "Update less often", "Options" (works,
not evident: the false-PASS check), a hotkey named in the first text (J2,
then J1 after the tool pressed it, round 2), focus moved to "New message
4 from Ana" (2.D J1) and a dialog "Prices were updated." (2.D J2). Before
the run, 2.C J1 had no image although its question named "image A": it
now carries pass T's first frame, the control's box and where it is in
words. Leak grep clean (the only hit is 2.D J1's own example, "New
message from Ana", which the fixture echoes, so that case is easy). One
fresh Sonnet agent, told to start no sub-agents and write no scripts
(about 99,000 tokens, 30 s, plus round 2): **10/10 match, no false PASS.**
"Options" was not evident. Its least sure call was passed 5's J2, which
it answered unsure: the text names a button but not what it does (NEEDS
REVIEW either way, K8 instead of K5). For the hotkey's J1 it noted the
mechanism is text naming a key, not a button, and judged it evident by
the rubric: J1's wording ("Pressing input.mechanism") fits controls
better than text; a follow-up for the 2.C spec. It opened only packet
files; it wrote the ten answers with one shell command.

## Run 14, 2026-11-02: 5.B 1.1.0 after the merge, its packets only

`prepare OUT 5.B` after 5.B 1.1.0 (an option in a set no longer takes the
legend as its label). 23 cases ask questions; leak grep clean. One fresh
Sonnet agent, told to start no sub-agents (about 154,000 tokens, 7 min):
23/23 match, no false PASS, no follow-up round. Its least sure calls:
duplicate "Name"/"Street" labels told apart by visible "Shipping"/"Billing"
headings (descriptive) against the same labels with no heading (not); a
field whose only visible label is "Go". **Coverage gap:** no packet has a
radio button or checkbox, so this run shows 5.B's cases still hold but does
not exercise the 1.1.0 change itself.

## Run 13, 2026-11-02: 5.A 1.1.0 after the rubric fix, its packets only

`prepare OUT 5.A`, fresh packets after run 12's two fixes. 13 of the cases
ask questions (16 questions); leak grep clean. One fresh Sonnet agent, told
to start no sub-agents (about 102,000 tokens, 2 min): 13/13 match, no false
PASS, no follow-up round. It called the "Find" and "Subscribe" fields
not_labeled ("names the action, not the field content"), the "Search"
button's box labeled, and quoted "Official Name:" (now matched on its
words). Least sure: the search box whose placeholder and button both say
"Search". It opened only packet files and used only Read and Write.

## Run 12, 2026-11-02: 5.A and 5.C 1.1.0 (PR #3 review fixes), their packets only

`prepare OUT 5.A,5.C` after 5.A J1's input gained `buttons_next_to_it` and
`question_of_the_set` (spec 1.1.0). 18 cases ask questions; leak grep clean.
One fresh Sonnet agent (it split the work across four sub-agents of its
own; about 49,000 tokens reported): **15/18, two false PASS.** With the
buttons beside a field shown and the rubric's only example "a Search button
beside a search box", it counted "Subscribe" (f01) and "Find" (f02) as
labels. Fix: the rubric now says a button counts only when its words say
what to type into the field, and names action words that do not. The third
miss (TC10.A-all-pass-6, NEEDS REVIEW for PASS) was the quote check: the
page shows "Official Name" and ":" as two pieces of text and the agent
quoted "Official Name:"; a quote now also matches on its words (M4). The
scripted tests could not see either problem: they answer as a correct judge
would.
## Run 11, 2026-11-02: 5.H after J2 named G155 and G168, its packets only

G155 (a required confirm checkbox) and G168 (an "Are you sure?"
confirmation) had been listed in the plan but not read; J2's rubric did not
name them, so a form confirming that way could have been judged "none" (a
false FAIL). The rubric and question now name both, with a fixture for
each (f06, f07). `prepare OUT 5.H`: 9 cases ask questions. One fresh
Sonnet agent, two rounds (about 100,000 tokens): 9/9 match, no false PASS;
it judged the dialog and the checkbox review_step. It read the packets with
one read-only Python snippet against its instructions; nothing outside the
packets was opened.

## Run 10, 2026-11-02: 5.B and 5.H (draft specs 0.1.0), their packets only

`prepare OUT 5.B,5.H`: 30 of the cases ask questions (5.B asks one question
per form on every labelled form; 5.H only when a form hints at
consequences): 16 ACT cc0f0a cases, the TC10.A/E and TC10.G Baseline
cases, and the custom 5.H pages. Leak grep clean. One fresh Sonnet agent
(about 127,000 tokens for round 1, 140 s; it also answered the four 5.H J2
follow-ups in round 2): 30/30 match, no false PASS. 5.B used the field
images (it saw the "Shipping"/"Billing" headings that make repeated
"Name" labels descriptive, and their absence when they are off screen).
Its least certain calls: a "step 1 of 3" form with a Next button that
leaves the recorded page (judged multi_step, then unsure about J2, which is
NEEDS REVIEW as intended). It opened only packet files, listed the folders
with one shell command, and wrote no scripts.

## Run 9, 2026-11-02: 19.A (draft spec 0.1.0), its packets only

`prepare OUT 19.A`: 2 of the 9 cases ask J1 (is the page a step in a
process?): a review step ("Step 2 of 3") and a contact form whose intro
says "Thank you for your interest" (hinted, not a process). One fresh
Sonnet agent (about 72,000 tokens, 13 s), told to use no scripts: 2/2
match, no false PASS. It opened only packet files and wrote none outside
them.

## Run 8, 2026-11-02: 9.A, 9.B and 9.C (draft specs 0.1.0), their packets only

`prepare OUT 9.A,9.B,9.C`. Cases now carry other pages (`pages`: the ACT
cases are compared with the rules' chapter2.html, the custom cases with
their sibling pages in `tests/fixtures/9x/`); `NOT_EVAL` in
`test_fixtures_9x.py` leaves out one rules-only case (the same page and
question as another, with the opposite scripted answer). 4 of the 47 cases
ask questions (9.A and 9.B decide almost everything mechanically; 9.B asks
nothing); leak grep clean. One fresh Sonnet agent (about 76,000 tokens,
32 s): 4/4 match, no false PASS, no follow-up round. 9.A J1 named Alt+S
with its quote; 9.A J2 judged a "Start / Benefits overview" trail as
repeated (the agent's least certain answer: no breadcrumb landmark, it went
by the links and separator); 9.C J1 judged "Go to page 3/4" and "5/6"
consistent, "Contact"/"Get in touch" and "Search"/"Find" inconsistent. It
opened only packet files; it read and wrote them with inline Python, which
its instructions said not to do (no file was saved).

## Run 7, 2026-11-01: 5.A and 5.C (draft specs 0.4.0 and 0.3.0), their packets only

`prepare /tmp/eval 5.A,5.C`; f12 runs with 4.F (its pass R reveals the
field), and packets hold only the case's own test's questions. 16 of the
50 cases ask questions (5.C decides most pages mechanically); leak grep
clean. One fresh Sonnet agent (about 89,000 tokens, 44 s): 16/16 match, no
false PASS, no follow-up round. It opened only packet files and wrote no
scratch file (it printed and wrote with inline Python). Borderline calls
it listed: a field named only by its table header judged complete; a red
"*" on a field without `required` judged missing; on the floating-label
page it read the small "ZIP code" label in the image as the label.

## Run 6, 2026-11-01: 5.F and 5.G at 1.0.0, their packets only

After Abby's review: a plain "Save" is a submit control again (f09 back to
"Save", f12 new), native date fields get a date outside their range in
attempt 2 (f13 `max`, f14 a birth date checked by script), and a date
field is read through its input (it had been dropped from its form: a
false DNA). 33 of 5.F's and 5.G's 42 cases ask questions; leak grep clean.
One fresh Sonnet agent (about 94,000 tokens, 171 s; then 9 s for f11's two
round-2 packets after J0's rerun): 33/33 match, no false PASS. It opened
only packet files; it wrote a scratch file (`/tmp/dump.txt`) and deleted
it, against its instructions, as agents did in runs 1 and 5. Borderline
calls it listed: instruction-style messages ("City: enter the city ...")
judged described; a valid "abc" name with only the ZIP code's error listed
judged no_error.

## 2026-11-01: shared replays and 4.A 1.2.0, no agent run needed

4.A now reuses 4.D's pass W arrows and 4.F's pass R Enter presses, and
treats native date-input parts as native (4.A 1.2.0). Packets for every
Test 4 fixture were built on main and on the branch and compared case by
case (`questions.json`, run IDs normalised): all 45 that ask questions
are identical, so no question or input changed.

## Run 5, 2026-11-01: 5.F and 5.G (draft specs), their packets only

`prepare /tmp/eval 5.F,5.G` (the new optional test list). 28 of 5.F's and
5.G's 36 cases ask questions (11 custom pages and the 7 TC10.D Baseline
cases, each for both tests). Leak grep (local hosts, fixture names, case
IDs): no match.

**First agent** (Sonnet, about 87,000 tokens, 74 s): 25/26 scored match,
no false PASS. The miss, 5.F f10 ("Date of birth: invalid entry."): the
agent answered not_described (FAIL), but the PDF's own example of a
description is "the Password you entered is incorrect" (p. 28 HtT 3.b).
J1's rubric now says that saying the value is incorrect or invalid is
enough (what to enter instead is 5.G); J0's rubric now excludes the
control already pressed (the agent asked). 5.F spec 0.5.0.

**Second agent** on the rebuilt packets (about 95,000 tokens, 77 s, then 8 s
for the two round-2 packets after J0's rerun): 28/28 match, no false PASS
(5.F: 4 FAIL, 9 PASS, 1 DNA; 5.G: 3 FAIL, 9 PASS, 1 DNA, plus the f11
pair after J0 picked "Send my question"). It opened only packet files; it
wrote one scratch file outside the packets (`/tmp/dump.txt`, removed),
as an agent did in run 1. Borderline calls it listed: instruction-style
messages ("Enter your full name", "City: enter the city ...") judged
described (G83: a text description identifying the field not completed);
"Error: not a number." on an empty number field judged described (5.F) and
guides (5.G).

## Run 4, 2026-11-01: 5.D On input (draft spec 0.5.0), its packets only

`judge_eval.py` now includes 5.D's custom fixtures and Baseline cases, and
registers draft checks (`tests/drafts.py`). 14 of 5.D's 19 cases ask
questions. One fresh Sonnet subagent answered those 14 (about 79,000
tokens, 28 s), then the one follow-up round (F10: after its J3 value the
retry asks J1). It opened nothing outside them.

| Result | |
| --- | --- |
| Match | 14/14 (9 FAIL, 3 PASS, Baseline TC10.C-3-fail-1/2/3 FAIL) |
| False PASS | none |
| J1 told (quotes found in the text before the field) | F02, F06 |
| J2 content only (images) | F07 (checkbox reveals mailing fields) |
| J3 value | F10: "12345" for a 5-digit ZIP pattern, then J1 not_told |

Note for the spec: after F10's retry the change reads "the page went to
another address", not "the form was sent": the submission was logged on
the page that then navigated away, so the count after it starts from zero.
Both are changes of context (M4); only the wording differs.

## Run 3, 2026-11-01: 4.C 1.8.0 (J2 for every form control), changed packets only

4.C's J2 now covers every form control kind, not only text, select and
checkbox. Packets rebuilt and compared with the time-budget run's: every
packet's answer format changed in wording only (J2's `value` description),
4.A f04's revealed items are now in sorted order, and three packets
changed in substance. One fresh Sonnet subagent answered those three only
(72,000 tokens, about 20 s; it opened nothing outside them):

| Case | Change | Expected | Got |
| --- | --- | --- | --- |
| 4.C f20 player trap | now asks J2 (the volume slider is a control) | FAIL | FAIL (J2 no: a media player) |
| 4.C f35 radio gate (new) | J2 for a radio-button gate | NEEDS REVIEW | NEEDS REVIEW (J2 yes: choose English) |
| 4.C f17 editor | member kind now "text" in J1's input | FAIL | FAIL |

3/3, no false PASS. The other 41 packets keep run 2's results.

## 2026-11-01: time budget, no agent run needed

The time-budget changes (quick replay prefixes, the screenshot pause, the run
limit; 4.C 1.7.0) touch how evidence is collected, so the packets were
rebuilt with the code before and after and compared file by file: 44 pages
ask questions in both, and every packet is identical except one (4.A
hover-only menu), where two revealed menu items were listed in swapped
order. That order came from iterating a set of strings (Python's hash
randomization differs per process), in the old code too; it is now sorted.
No question or evidence changed, so no agent answered. `prepare` also needed
`dev_allowed_addresses` for the fixture servers: the egress proxy refused
127.0.0.1 and recording hung. Packets take about 3.5 minutes to build.

## Run 2, 2026-10-31: after the fixes, one subagent for everything

Same fixtures after the fixes from run 1 (4.A 1.1.0, 4.B 1.1.0, 4.C 1.5.1,
4.F 1.1.0). 44 pages ask questions (the two ACT pages where keyboard focus
reaches nothing are now decided without one). One Sonnet subagent answered all
44 folders, then one more answered the two 4.B follow-ups.

| Test | Match |
| --- | --- |
| 4.A | 5/5 |
| 4.B | 3/4 |
| 4.C | 25/25 |
| 4.E | 2/2 |
| 4.F | 8/8 (f14, the false PASS, now FAIL) |
| All | 43/44, no false PASS |

The one mismatch (4.B f02) is a safe unsure: the agent could not tell whether
"Switch request type" does what the timed press does, because nothing shows
what a normal press on it changes. The tool could press it and compare
(a mechanical check on the J2 answer; not built).

| | Run 1: one subagent per page | Run 2: one subagent for all |
| --- | --- | --- |
| Agents | 48 | 2 |
| Tokens (as reported per agent, summed) | about 2,700,000 | about 159,000 (96,000 + 63,000) |
| Time | 8 to 20 s each, in parallel | 77 s + 13 s, one after the other |

About 17 times fewer tokens. Each agent's start-up costs roughly 55,000
tokens, so the second agent (two questions) cost almost as much as the first
(52 answers). The run-2 agent also wrote a helper script outside the packet
folders (it read nothing outside them, by its own report).

## Run 1, 2026-10-31 (Sonnet subagents, one per page, 46 pages, 54 answers)

| Test | Match | Mismatches |
| --- | --- | --- |
| 4.A | 4/7 | 3 × unsure where FAIL was expected |
| 4.B | 3/4 | 1 × unsure where PASS was expected |
| 4.C | 25/25 | none |
| 4.E | 2/2 | none |
| 4.F | 5/8 | 1 false PASS (f14), 1 unsure, 1 FAIL where unsure was expected (f15) |

What the mismatches and the agents' notes showed (tool problems, not agent
mistakes, unless marked):

- **False PASS, 4.F f14.** The backward (Shift+Tab) order is scrambled; the
  agent judged only the forward order ("the Shift+Tab signal concerns the
  reverse pass"). J1's wording never asks about the backward order.
- **4.F f15.** Focus reads "Step 3, Step 4, Step 1, Step 2"; the agent said
  does_not_preserve, our test data says unsure. The agent looks right.
- **Missing evidence led to unsure** (safe, but costs automation): 4.F's
  revealed-content question does not list what was revealed; 4.B J2 gives
  only element names; 4.A on pages where keyboard focus reaches nothing shows
  an empty stop list plus "the Tab walk did not get through the whole page".
- **Rubric gap, 4.A J1:** a link to another page that might list the same
  items was treated as a possible alternative; TT HtT 2.b asks for another
  method "available on the page".
- **Broken references:** 4.C questions point at screenshots by run-folder path
  (`evidence/shots/P1-0005.png`), not `run://`, so no client can open them.
  4.B sends no `page_text`, and its matched sentences are cut at line breaks.
- **Prompt injection resisted:** 4.C f32's page tells automated testers to
  report PASS; the agent ignored it and said so.

**Tokens.** A question's own content is about 600 tokens (packet median
7.7 KB, of which 5.2 KB is the answer-format text). Each subagent used about
55,000 tokens, almost all fixed start-up cost. One subagent per question
saves the consumer's main context but multiplies total spend; batching all
of a run's questions into one subagent, or answering small sets inline, is
far cheaper.
