# Build plan: bundle 2, fixing the rules that let failures through

Bundle 2 of the server judge pivot's "Sequencing to Nov 20"
([2026-11-07-server-judge-pivot.md](2026-11-07-server-judge-pivot.md));
post-round 2 fixes 1-6 and 9b
([2026-11-08-post-round2-fixes.md](2026-11-08-post-round2-fixes.md)).
Status: **step 1 done, no rule changed yet.** Agent-assisted results, not
certified Trusted Tester results.

## Status

- Step 1 (2026-11-09, branch `frozen-page-checks`): frozen pages restored
  (12 files, all match the manifest). Verified by running TOBI in `replay`
  mode on the frozen copy and by Playwright probes on the recordings
  (scripts not kept). Findings are in "Step 1 findings" below; three differ
  from what this plan assumed, so fixes 2 and 5 wait for Abby (questions
  there). Not built: fixes 1-6, 9b, 3. No model calls were made.
- Fix 6 (9.A-9.C other templates): built, branch `template-mismatch-9abc`
  (PR number below). Specs 9.A 1.1.0, 9.B 1.1.0, 9.C 1.2.0; `site.kinship()`
  (counts and a template fingerprint, recorded as `kinship` in each 9.x
  evidence file). Verified (commands): `test_fixtures_9x.py` (20 + 6 new:
  unrelated, microsite, microsite-with-header-footer, same-template,
  related-and-microsite, microsite-is-tested; A3o rows; kinship counts; 9.B
  capped read), see the full-suite line when added. Assumed: "navigation of
  its own" (a banner, navigation, search or contentinfo region, or 4+ links
  outside main) and "almost nothing" (no region with the same label or id,
  and one unit or under 4 words shared) are my reading of the plan's words,
  for Abby to confirm; 9.C's A3o applies only when no pair was made (a pair
  by address or id still goes through the instance rules). Full suite:
  1088 passed, 3 skipped, 1 xfailed (the skips are the agent-eval browser
  tests). Frozen pages (replay mode, 9.A / 9.B / 9.C): 14592 with CILab ->
  all three NEEDS REVIEW by A3o (were Does Not Apply; key: 9.A Fail, 9.B and
  9.C Pass); 5144 with 4914 and 4914 with 5144 -> 9.A FAIL, 9.B PASS, 9.C
  PASS, as the key; CILab with home, help, search and galleries -> all three
  NEEDS REVIEW because pages are over the 600-piece read cap (key: 9.A Fail,
  9.B and 9.C Pass, "totally different header from rest of site"). The
  14592 and CILab 9.A cells move toward the key's Fail only as far as a
  review: the rule cannot say Fail without comparing against its own
  template. Nothing here turns a Fail or review into a Pass.

## Step 1 findings (2026-11-09)

1. **CILab 4.A (fix 4).** TOBI says PASS ("no instances"), reproduced on
   the frozen page. The guess (`hit()` fails on a covered centre) is
   **wrong**: `#demo-reel-row` is visible and its centre hits itself. The
   row has no pointer cursor and no `onclick` attribute; its click handler
   is attached by script (jQuery 3.5.1 `.click()`, i.e. `addEventListener`).
   Cause: `traverse.listeners()` and `t4a._own_listener_types()` ask CDP
   (`DOMDebugger.getEventListeners`) from TOBI's **isolated world**, which
   returns **0** listeners there; from the page's main world the same call
   returns 21 on this page, including the row's click. So 4.A has never
   seen listeners that page scripts add, on any page, with any library.
   Fix 4 gains a first step: read listeners from the main world (any
   library, no script parsing). A handler on an ancestor (delegation) is
   still not tied to the child it serves; decide that when building.
2. **5340 4.C and 5.D reproduce as false PASS** on the frozen copy: 4.C
   PASS (M4, "View timeline"), 5.D PASS ("no changes").
3. **5340 4.C: the plan's picture of "View timeline" is wrong.** In the
   first view, Tab never leaves the frame in 120 presses (about 25 stops
   repeat), so the trap is real. Enter on "View timeline" swaps the view
   (43 focusable items down to 5) and Tab then leaves the frame after 5
   stops. So the new view does **not** loop. Fix 2 as written ("an exit
   counts only when focus leaves the section, with no new trap forming")
   would still count this as an exit and PASS, against Abby's Fail. See
   question A.
4. **5340 5.D: the Tab-away jump did not reproduce.** Typing a name or a
   year (1800, 1985, 12345; blank or already filled; arrived by Tab or
   by focus) and pressing Tab moved focus to the next field, and it stayed
   there for 5 s. What did jump to the app's start: Enter on a "submit"
   button after filling the form (focus went to the app's root `div`, and
   the next Tab reached OVERVIEW). No error popup text appeared. See
   question B.
5. **Year popup (decision 2):** not confirmed. With 1800 and a keyboard
   submit there was no popup in the recording. Item 8 waits on question B.

Questions for Abby:

- **A.** Is an exit that needs Enter on a control *inside* the loop an
  exit? It starts a different view and no standard key (Tab, arrows, Esc)
  leaves the first one. Recommendation: no. Count only exits reached by
  Tab, Shift+Tab, Escape or arrows without activating anything; an
  activation-only way out is NEEDS REVIEW with the page's advice as the
  question (the TT 4.C note on non-standard methods), and FAIL when the
  loop has no way out by those keys and the page does not say how.
- **B.** The exact steps for the 5.D jump and the year popup on 5340
  (which button, which key, what you saw), or a screen capture.

Probe scripts and runs stayed in the session scratchpad (not committed).

## The problem in one line

In round 2, TOBI's own rules (not any judge) passed six things Abby
failed, or called them Does Not Apply. Each fix makes the rule look where a
person looks, and where TOBI still cannot look, say NEEDS REVIEW instead
of PASS.

## The seven fixes

| # | Page | What went wrong | The fix |
| --- | --- | --- | --- |
| 1 | 14592 | 3.A said Does Not Apply: its videos never played, so TOBI never looked for flashing | A video TOBI did not check makes 3.A NEEDS REVIEW. Short videos are checked from their file |
| 4 | CILab | 4.A passed a video that plays only on a mouse click | TOBI notices a click that starts a video, and asks whether the keyboard can do the same |
| 2 | 5340 | 4.C passed a trap: pressing Enter changed the app's view, but focus never left the app | "Getting out" means reaching the rest of the page, not just a new spot inside the app |
| 5 | 5340 | 5.D passed: after editing a field, Tab jumps focus back to the app's start | Wait a moment after tabbing away before reading where focus went |
| 6 | CILab, 14592 | 9.A-9.C said Does Not Apply because the two pages compared were from different templates | When the other pages share nothing with the tested page, NEEDS REVIEW, not Does Not Apply |
| 9b | Home | 5.C missed the filter's X buttons, which only appear after choosing a filter | TOBI opens menus, tabs, accordions and filters and tests what appears. Anything it could not open turns a PASS into NEEDS REVIEW |
| 3 | 5340 | 5.F never made the form show its errors, so the error popup's trap was never tested | Type realistic wrong values (bad email, year out of range), then check the error popup for a keyboard trap |

Every fix only moves results toward FAIL or NEEDS REVIEW. None can turn
an existing FAIL into a PASS.

## What we learned from the research

- 5340's app is on the same site as the page, so fixes 2 and 5 do not
  wait for the frames work.
- 3.A on 14592 will become NEEDS REVIEW, not Not Tested like the key: its
  videos are too large for TOBI to check. That still fixes the real
  problem (never Does Not Apply).
- Revealing Home's X buttons is not enough: 5.C also needs a rule for
  buttons that share one name (decision 1).
- 9.B has another false PASS today: two unrelated pages that both have a
  plain header and footer look "consistent". Fix 6 closes it.

## Order of work

1. **Use round 2's frozen pages** (Abby's archive copy, the exact pages
   her keys describe; no model tokens; the ApiJudge gate uses them too)
   and look at four things on them:
   why 4.A missed CILab's video, why 5.D passed on 5340, and what "View
   timeline" does on 5340, and whether a keyboard user can get back to
   the year field from its error popup.
2. **Three small pieces in parallel** (different files):
   - videos: fixes 1 and 4 (about 2 days);
   - 4.C and 5.D on 5340: fixes 2 and 5 (about 1.5 days);
   - templates: fix 6 (about 1 day).
3. **Opening everything**: fix 9b (about 3 days).
4. **Error values**: fix 3 (about 3 days; its frame part goes with the
   frames bundle).

Steps 1-3 are the Nov 20 cut; 4 if time allows. Each piece is its own pull
request: spec first, a test page, the full test suite, and the judge
eval where a question changes (fixes 4, 9b and 3).

## Abby's decisions (2026-11-09)

1. **Home's X buttons:** ask an open question settled by looking, showing
   each button's row.
2. **5340's year popup:** Abby believes focus was trapped in the popup and
   the year could not be fixed without a mouse click; to check on the
   recording (step 1). If a keyboard user can get back and fix the value,
   it is not a failure (TT 4.C note 2); if not, it is a trap (FAIL).
3. **9.A with no matching pages:** NEEDS REVIEW.

Everything else uses the defaults in the builder notes below.

---

## Builder notes

For the session that builds this. File and line references are from the
2026-11-08 research (read-only; verified by reading the files, round 2's
reports, keys and step logs, and three small Playwright probes).

**Rules for every piece** (CLAUDE.md): spec first with a MINOR bump;
outcomes only in the spec's rows; custom test pages (no ACT or Baseline
case covers any of these), expected outcomes in the test files; full
suite; judge eval when a question or its input changes; hackathon
`evaluation.md` and deck slide in the same commit as a spec version.
Before removing any FAIL, read the key's comment and check its elements
are still found. Never edit `evals/judging/round2*/`.

**Spec versions, in build order:** 3.A 1.0.0→1.1.0; 4.A 1.2.1→1.3.0
(fix 4)→1.4.0 (9b); 4.C 1.9.0→1.10.0 (fix 2)→1.11.0 (9b)→1.12.0
(fix 3); 5.D 1.2.0→1.3.0 (fix 5)→1.4.0 (9b); 9.A, 9.B 1.0.0→1.1.0; 9.C
1.1.1→1.2.0; 5.A, 5.B 1.2.0→1.3.0; 5.C 1.4.0→1.5.0; 4.D 1.3.0→1.4.0;
4.E 1.2.0→1.3.0; 4.F 1.3.0→1.4.0; 5.F 1.3.1→1.4.0.

**Step 1 (frozen pages):** restore `round2-frozen` at the repository
root (`evals/judging/round2/results/ARCHIVE.md`; check each file against
its manifest; HARs are git-ignored; never change them); run TOBI with
`FROZEN_PAGES_DIR=evals/judging/round2/frozen` in `tested_frozen` mode (as Agent C ran), client
backend, runs in `runs/`. CILab: log
`reasonOf`, `hit()` and visibility for `#demo-reel-row` (guess: its
centre point is covered, and `hit()` tests the centre only, `t4a.py`
~125). 5340: read 5.D's `focus_after_leave`, `leave_expected`; what
Enter on "View timeline" adds.

**Fix 1, 3.A** (TT p. 18). `triggers()` (`t3a.py:84-123`) takes only
videos that played; with none, `collect()` returns early and row A4 gives
DNA. Make every `<video>` a trigger; `_video()` already decodes from the
media store, which fetches unplayed sources too. Add to A3: a video not
decoded (no file, over the 50 MB cap, a format Chromium cannot decode),
more videos than 3 per page, more than 20 media elements. Fix the wrong
"it streams its video" reason for an empty `currentSrc` (`:387`). Try
the element's other `<source>` on a failed decode. Test pages in
`3a/`: click-to-play strobe (reuse `media/video-strobe.webm`) → NOT
TESTED; unplayed video with a missing file → NEEDS REVIEW; unplayed 3 s
grey clip (add to `make_media.py`) → DNA. Hidden videos count.

**Fix 4, 4.A** (TT pp. 19-20; WCAG F54). New term *media start*: an
`<audio>`/`<video>` whose `paused` goes true→false after an action; an
effect for 4.A only (M2, M8-M10), kept out of the shared *effect* term
that 4.B and 5.D cite. `observe.snapshot` reads `paused`; a separate
`Effect.media_started`. J1 still decides; its input says "clicking it
started a video". Test pages in `4a/`: CILab-like row div → FAIL M6; a
video whose click only plays → FAIL M6; the same plus a Play button →
PASS M5; a click-only role=button Play → FAIL M10. Leave 14592's
`<video controls>` question (key Pass) alone: a ROADMAP note.

**Fix 2, 4.C** (TT p. 21, HtT 2.b, ER 2). `probe` (`t4c.py:289-385`)
treats any stop outside the loop's members as outside (`:304`); the
re-trap test (`:373`) only catches a loop of the old members. New term
*the trap's section*: a loop inside one frame → the frame; a single
stuck element keeps element scope (so the OVERVIEW tab's PASS stays). An
exit = reaching a stop outside the section, with no new trap forming in
it. Presses for frame sections: the frame's stop count + 3, cap about 60,
with a per-trap budget. If an Enter probe already did the section's action
and focus still cannot leave, M8 does not apply (FAIL, not NEEDS
REVIEW). Test pages in `4c/`: same-site frame whose "View timeline"
swaps in a view that also loops → FAIL; Enter on "Done" leaves to the
top page → PASS; f11, f13, f36 and all ACT cases unchanged.

**Fix 5, 5.D** (TT p. 27, HtT 3-4). The check exists (`t5d.py:333-359,
421-432`) but no test page moves focus on blur. Use 4.C's 1 s re-read
after a focus or blur event or a DOM change; record which read counted.
If step 1 shows the value was the cause, retry with a valid value. Test
pages in `5d/`: immediate blur jump; 500 ms jump; re-render on change;
the delayed jump in a same-site frame.

**Fix 6, 9.A-9.C** (TT pp. 42-44; EXCLUDE: single links, fewer than 4
words). In `site.py` (counts only): an other page *shares almost
nothing* when no region matches by label or id (not position: keys like
`banner|@1`, `site.py:128, 298`) and the shared items are one control or
under 4 words. Round 2: different templates shared 0, same template 10 or
more. New rows: 9.A A3o and 9.C A3o → NEEDS REVIEW when every other page
shares almost nothing and the tested page has its own navigation; 9.B N2o
(skip such a page) and A3o; 9.C pairs by destination and id only with
such pages; 9.B also stops calling a capped read DNA (as 9.C 1.1.0).
Record per page a template fingerprint (`kinship` in each 9.x evidence
file) for the later site-wide store. Test pages in `9x/`: e1 (microsite,
no landmarks, no skip link), e2 (same template), e3 (e1 with header and
footer). The existing `unrelated` case moves DNA → NEEDS REVIEW
(intended); `paging`, ACT c039d5c0 and ecc29b73 unchanged. A microsite
is its own set of pages.

**Fix 9b, opening everything, phase 1** (TT p. 21 Identify Content;
4.A ER Note 1; 4.F HtT 2.b; 5.B Note 3; 5.C Note 2; 2.x not in scope).
Today only 4.F's pass R opens anything (`REVEAL_MAX = 6`, `t4f.py:37`),
and it reads opened content only when it holds form fields
(`:414-428`). New `src/tobi508/reveal.py` (facts only):
- triggers from the walk's stops: collapsed, `aria-haspopup`,
  `aria-controls`, unselected `role=tab`, `<summary>`, a button already
  seen to open a dialog (move these attributes into the stop
  description, `traverse._DESCRIBE_FN`, `models.Stop`); plain buttons
  with no hint are not triggers;
- each on a fresh load: focus it directly and press Enter (click as
  fallback; Tab replays only where 4.F and 4.C need them); compare
  visible components before and after; then check up to 2 options per
  checkbox or radio set inside (that is what shows Home's X buttons);
- up to 20 triggers; record each opened state (new elements, ANDI's
  reading, a picture) and each one not opened with why, in
  `evidence/reveal.json`; `base.py` gains `uses_reveal`; pass R and
  `labels.read_revealed` become readers of it.
Specs: 5.A, 5.B, 5.C read opened content like load content; 5.C asks one
open question per set of same-named buttons, with each row's text
(decision 1). **Guard** in 4.A, 4.C, 4.D, 4.E, 4.F, 5.A-5.D: a would-be
PASS is NEEDS REVIEW when a trigger was not opened, opened nothing, could
not be read, or (until phase 2) opened content holds what the test checks.
In round 2 that turns about 7 PASS cells the key passes into NEEDS REVIEW
until phase 2 (4.E on 5 pages, 4.A Help, 5.D Home); accepted as the
price of not passing what was not tested. Test pages: `5c/` filter whose
checked options add X buttons with one name → 5.C FAIL (or question);
`5a/` accordion with an unlabeled field → 5.A, 5.C FAIL; a trigger that
opens nothing → NEEDS REVIEW; reuse `4f/f13`, `5a/f12`, `5d/f07`. Then
check Home's recording finds the X buttons. Phase 2 (4.x walk through
opened content) and phase 3 (5.D fills opened fields) go to the ROADMAP.

**Fix 3, error values** (TT pp. 28-29; 4.C p. 21 notes 1-2; Baseline
TC10.D). 5.F types "abc" only (`t5f.py:44`; year fields: 2999 with no
range). New table by field type and purpose (`type`, `inputmode`,
`autocomplete`, `min`/`max`, name, id, label words): names `J@n3#`,
email `test@`, phone `123`, numbers and years min−1 and max+1 (or 1000
and 3000 with no range), dates far past and far future, other "abc".
The spec records Abby's 2026-11-08 decision in place of "no values from
instructions". 4.C gains a pass that Tabs through each error state 5.F
found (a JS `alert()` is out of scope); 4.C runs the error pass itself
when 5.F is not selected; its replay learns to type text. Fields in
same-site frames (skipped today, `t5f.py:206-214`) are read with the
frames bundle. Test pages: top-level name and year form with a
focus-grabbing popup for years before 1900 that a keyboard user
cannot leave to fix the value → FAIL (decision 2); a variant that lets Escape out → PASS; a name field that
refuses "#". Baseline TC10.D cases unchanged.

**Assumed until step 1 or the test pages:** why CILab's scan missed, why
5.D passed on 5340, what "View timeline" does, that 5340's year field is
a number field (where "abc" types nothing), SVS's video formats, and all
time estimates.
