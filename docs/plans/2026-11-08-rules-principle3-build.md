# Build plan: bundle 2, `rules-principle3` (2026-11-08, proposed)

Bundle 2 of the server judge pivot's "Sequencing to Nov 20"
([2026-11-07-server-judge-pivot.md](2026-11-07-server-judge-pivot.md)):
post-round 2 fixes 1-6 and 9b
([2026-11-08-post-round2-fixes.md](2026-11-08-post-round2-fixes.md)).
Each fixes a cell where a failure passed or was set aside as Does Not
Apply (principle 3). Status: **proposed, nothing built.** Research: four
read-only notes (2026-11-08), summarised here with their file and line
references; questions for Abby are at the end, each with a default so
the build can start, and the three that block a part are marked.

Agent-assisted results, not certified Trusted Tester results.

**Rules for every part** (CLAUDE.md): spec first (MINOR bump, decided
only in the spec's rows), then the fixture (vendored ACT or Baseline
first; none covers any of these, so custom pages, expected outcomes in
the test files, never in a page), the full suite, and the judge eval when
a question, rubric or question input changes. The hackathon
`evaluation.md` and deck slide change in the same commit as a spec
version. Before a change removes a FAIL, read the key's comment for that
cell and check its elements are still found. Never edit
`evals/judging/round2*/`.

## What the research changed

- **5340's embedded app is a same-host frame**, not a cross-origin one
  (round 2's frozen index lists no cross-site frames; the frame is
  `svs.gsfc.nasa.gov/webapps/climate-legacies/`). 4.C and 5.D already
  follow focus into it (5.D filled all 15 frame fields). So fixes 2 and
  5 do not wait for the frames bundle; only fix 3's 5.F part needs its
  simpler half (same-host frames read in place).
- **Fix 5 is already in the spec and code** (5.D 1.2.0 section 3,
  `t5d.py:333-359, 421-432`) but no fixture exercises it. The likely miss:
  5.D reads focus once after a 150 ms settle; 4.C's 1 s re-read is not
  used there (assumed; a diagnostic run decides).
- **CILab's click-to-play video was never a 4.A candidate** (4.A took one
  load, 2.7 s): a detection miss, not a row error; and a click that only
  calls `video.play()` changes no DOM, so `observe.Effect` sees no effect
  (verified in a probe: `paused` true→false is readable even when the
  file is not served).
- **3.A on 14592 will most likely become NEEDS REVIEW, not Not Tested:**
  its videos are 4K files over the media store's 50 MB cap, and any video
  over 10 s is NEEDS REVIEW by rule O4 unless a flash is found. That is
  the principle-3 fix (never DNA); matching the key would need full
  decoding, which is not proportionate now.
- **9b's Home evidence needs a 5.C rule too:** `t5c.shown()`
  (`t5c.py:122-127`) compares an icon-only button with its own (empty)
  text, so the revealed X buttons named "Remove filter from selection"
  would PASS. Revealing them is not enough (question B1).
- **9.B has a false PASS today:** two unrelated pages that each have an
  unlabelled `<header>` and `<footer>` match two regions by position
  (`site.py:128, 298`).

## Step 0: recordings and two diagnostics (no model tokens)

Shared with bundle 1's real-page gate (its plan, D): record round 2's 10
pages fresh into `runs/gate-frozen/` (`FROZEN_PAGES_DIR`,
`record_missing`; outside git; the container reaches the site), and run
TOBI on them with the client backend. Then:
- **CILab 4.A:** log the pointer scan's `reasonOf`, `hit()` and
  visibility for `#demo-reel-row` (hypotheses: the centre point is
  covered by the bottom navbar, or a script did not load in the replay).
- **5340 5.D:** read `focus_after_leave` and `leave_expected` for the name
  and year fields (is it timing, the value typed, or a re-render?).
- **5340 4.C:** record what Enter on "View timeline" does (new stops,
  focus frame).
Write what was found in each part's spec change. If a page drifted
from round 2 so that its cell no longer shows the problem, say so and use
the fixture alone.

## Parts (one PR each)

| PR | Fixes | Files | Size | Judge eval |
| --- | --- | --- | --- | --- |
| 2a `video` | 1 (3.A), 4 (4.A) | `t3a.py`, `t4a.py`, `observe.py`, `motion.py` (sources) | 15 h | yes (4.A J1 input) |
| 2b `trap-tab` | 2 (4.C), 5 (5.D) | `t4c.py`, `t5d.py` | 10-13 h | no (4.C J2 only if its input changes) |
| 2c `templates` | 6 (9.A-9.C) | `site.py`, `t9a-c.py` | 8-10 h | no |
| 2d `reveal` | 9b phase 1 | new `reveal.py`; `traverse.py`, `models.py` (stop attributes), `base.py`, `pipeline.py`, `labels.py`, `t4f.py`, `t5a-c.py`, guard rows in 9 specs | 2.5-3 days | yes (5.A-5.C inputs) |
| 2e `error-states` | 3 (5.F values, 4.C error-state pass) | `forms.py`, `t5f.py`, `t4c.py`; same-host frame reads with bundle 3 | 16-24 h, +6-8 h frames | yes (5.F J1, 4.C) |

**Order.** 2a, 2b and 2c touch different files: three sessions can build
them at once. 2d after 2a and 2b merge (it adds guard rows to 4.A, 4.C
and 5.D). 2e after 2d (4.C again). Spec versions, in that order:
4.C 1.9.0 → 1.10.0 (2b) → 1.11.0 (2d) → 1.12.0 (2e); 4.A 1.2.1 → 1.3.0
(2a) → 1.4.0 (2d); 5.D 1.2.0 → 1.3.0 (2b) → 1.4.0 (2d). Bundle 5's 5.C
fixes (9, 9c) come after 2d's 5.C 1.5.0.

**Nov 20 cut:** 2a, 2b, 2c, 2d. 2e if time; its 5.F frame part goes
with bundle 3 in any case. Total about 9-11 working days for all five;
in parallel sessions, about 6.

### 2a. Video: 3.A unplayed video (fix 1), 4.A click-to-play (fix 4)

**3.A 1.0.0 → 1.1.0.** TT p. 18: DNA only when no flashing content is
found; a video that never played was never looked at.
- Section 2: every `<video>` pass T reads is a trigger, played or not
  (today `triggers()`, `t3a.py:84-123`, takes only videos `played()`
  saw advance; with none, `collect()` returns early and A4 gives DNA).
- A3 gains: a video that did not play and was not decoded (no file, not
  recorded or over the cap, a format Chromium cannot decode); more videos
  than the decode cap (question A2); more than the 20 media elements pass
  T reads. A4 can no longer be reached while a video is unmeasured.
- Code: add unplayed videos to `triggers()` with `played=False`;
  `_video()` already decodes from the media store, which fetches every
  `<video>`/`<source>` URL, played or not. Check the stored bytes before
  opening the flash page (a page whose videos are all over the cap costs
  nothing extra). A correct reason for an empty `currentSrc` (today "it
  streams its video", `t3a.py:387`). Optional: try the element's other
  `<source>` on a failed decode (question A3).
- Fixtures (`tests/fixtures/3a/`): f16 click-to-play strobe (reuses
  `media/video-strobe.webm`) → NOT TESTED by A2; f17 unplayed video with
  a missing file → NEEDS REVIEW by A3; f18 unplayed 3 s grey clip → DNA
  by A4 (add it to `make_media.py`).
- Effect on round 2: 14592, CILab and 14194 move from DNA to NEEDS
  REVIEW (over-cap media). Lower agreement where the key says DNA; never
  a false PASS.

**4.A 1.2.1 → 1.3.0.** TT pp. 19-20 (HtT 1.a, 2, 2.b); WCAG F54, F42.
- Step 0's diagnosis first; if the centre-point hit test is the cause,
  test a few inset points too.
- New term *media start*: an `<audio>` or `<video>` whose `paused` goes
  from true to false after the action. 4.A counts it as an effect in M2,
  M8, M9 and M10. It stays out of the shared *effect* term (4.B and 5.D
  cite 4.A's Terms; changing it would change their outcomes outside their
  specs: question A4).
- Code: `observe.snapshot` reads each media element's `paused` (about
  1 ms); a separate `Effect.media_started`, outside `kinds`, so `.any` in
  4.B, 4.E and 5.D is unchanged.
- J1 still decides whether another keyboard way exists (HtT 2.b); its
  input says "clicking it started a video". Judge eval after.
- Fixtures (`tests/fixtures/4a/`): f14 CILab-like (a row div whose click
  sets `controls` and plays; no focusable control) → FAIL M6 with a
  scripted "no alternative"; f15 a video whose click only plays → FAIL
  M6 (today no instance); f16 the same plus a reachable Play button →
  PASS M5; f17 a role=button Play that answers clicks only → FAIL M10.
- Keep apart: 14592's `<video controls>` flagged unreachable (J1 unsure,
  key Pass); the browser's own video controls may not be recorded as
  stops. Not turned into a FAIL here; a ROADMAP note.

### 2b. 4.C exit within the trap (fix 2), 5.D after tabbing away (fix 5)

**4.C 1.9.0 → 1.10.0.** TT p. 21 (HtT 2.b: "no way to navigate out of
the 'loop' to the rest of the page"; ER 2).
- New term *the trap's section*: for a loop whose stops are all in one
  frame, that frame; otherwise the loop's own stops. A stuck element keeps
  element scope (ER 1), so the OVERVIEW tab's PASS by Tab stays
  (question C1).
- An exit is focus reaching a stop outside the section, after which no
  stuck element or loop forms inside the section during the check
  presses. Today `probe` (`t4c.py:289-385`) counts any non-member stop as
  outside (`:304`), and the re-trap test (`:373`) catches only a new loop
  made of the old members: Enter on "View timeline" swapped in new stops
  inside the frame and counted as an exit (M4 PASS).
- M2, M3 and M4 read "focus reaches the rest of the page". A check that
  hits its cap undecided goes to the incomplete list (G3, NEEDS REVIEW),
  never FAIL.
- Code: `Stop.frame_chain` (the members' common chain); for frame
  sections, `within` and check presses = the frame's stop count + 3
  (from the DOM inventory per frame), capped at about 60; a per-trap probe
  budget (4.C already took 70 s on 5340).
- Fixtures (`tests/fixtures/4c/`): f37 a same-host frame (f18's shape)
  whose setup view's "View timeline" swaps in a timeline view that also
  loops → FAIL M12 with J2 "no"; variant with J2 "yes" → NEEDS REVIEW
  M8 (question C2); f38 Enter on "Done" moves focus to the top page's
  next link → PASS M4. Regression: f11, f13, f36 stay PASS M4; all ACT
  cases unchanged.
- Only makes exits harder to count: no FAIL can be lost.

**5.D 1.2.0 → 1.3.0.** TT p. 27 (HtT 3, 4, 4.a.i).
- After step 0's diagnosis: apply 4.C's focus-check window to the
  tab-away (read again up to 1 s after a focus or blur event or a DOM
  change in the field's document; question C7), and record which read
  counted. If the value was the cause, a valid-value retry (J3 exists).
- Fixtures (`tests/fixtures/5d/`): blur handler that focuses the
  container's first control at once; the same after 500 ms; a list
  re-rendered on change; the delayed case in a same-host frame. Expected:
  FAIL by M9 with J1 "not told"; PASS by M8 with a notice before the
  field.

### 2c. 9.A-9.C: other pages from another template (fix 6)

TT 9.A p. 42 ("repeated on other pages within the site"; EXCLUDE
"repeated individual words, phrases, or single links"), 9.B p. 43, 9.C
p. 44. No ACT or Baseline case for 9.B, 9.C; DHS scored no 9.A rule.
CILab's key: 9.B and 9.C "passes within subpages of the cilab
microsite"; 9.A Fail "No skip link for top nav".

- **Measure (counts in `site.py`, no outcome):** per other page, the
  tested page's units whose text appears there, and its links whose
  destination appears there; regions shared only when matched by label or
  id, not by position (`banner|@1`). An other page **shares almost
  nothing** when no region matches by label or id and the shared units
  are one control or fewer than 4 words in all (TT's EXCLUDE, the
  existing `_small`; not a tuned threshold, question D3). Round 2:
  different templates shared 0 components, same-template pairs 10 or
  more. Plus a fact about the tested page, *own navigation*: a banner,
  navigation or search region before the main content, or 2 or more
  controls there.
- **9.A 1.0.0 → 1.1.0:** row A3o before A3: A3 or A4 would apply, every
  other page shares almost nothing, and the page has own navigation →
  NEEDS REVIEW, not performed: "The other pages you gave share almost
  nothing with this page (no menus, headers or footers in common), so
  they may be another part of the site. Run it again with pages that look
  like this one." On the A5 path, a note only. No FAIL changes
  (question D1 is whether 9.A could go further).
- **9.B 1.0.0 → 1.1.0:** instance row N2o (such a page is not compared,
  with a note) and A3o (nothing compared, a page dropped by N2o, own
  navigation → NEEDS REVIEW). Closes the position-only false PASS. Also
  mirror 9.C 1.1.0's cap rule (A3 over the read cap is not DNA).
- **9.C 1.1.1 → 1.2.0:** with such a page, pair by destination and id
  only (not name or place, the pairs behind Agent C's false FAILs); A3o
  as 9.A. 9.C reads the site from the cache when 9.A or 9.B ran, else one
  load per page (about 1 s), only when there are no pairs.
- Record now, for the later site-wide template store: per page (by
  recording hash and URL) region keys with position-only keys flagged,
  the text keys and destinations outside main, title pattern and path
  prefix; per tested page its own-navigation summary; per pair the counts
  (`kinship` in each 9.x evidence file).
- Fixtures (`tests/fixtures/9x/`): e1 a microsite page (div header and
  nav, no landmarks, no skip link, nothing shared with a1 or a2); e2 same
  template as e1; e3 e1 with `<header>`/`<footer>`. e1 with [a2] and a1
  with [e1]: NEEDS REVIEW by A3o for all three (today DNA). e1 with [e2]:
  9.A FAIL, 9.B PASS, 9.C PASS (the key's "within the microsite"). e3:
  9.A FAIL, 9.B NEEDS REVIEW by N2o (today PASS). Existing: `unrelated`
  (a1 with c1) DNA → NEEDS REVIEW (intended); `paging`, ACT c039d5c0
  and ecc29b73 unchanged. Unit tests in `tests/test_site.py`.

### 2d. The reveal pass, phase 1 (fix 9b)

TT: 4.A ER Note 1 (pp. 19-20); Focus Identify Content p. 21 (4.A-4.H,
"drop-down menus, form fields, revealing/hiding content"); 4.F HtT 2.b
(p. 23: "activate trigger controls that reveal hidden content … to
check the focus order to, from, and within"); 5.B Note 3 (p. 26), 5.C
Note 2 (p. 27). 2.x is not in scope (2.D's note, p. 17, sends interaction
changes to 5.B). No ACT or Baseline case reveals content after
interaction.

**Today.** Only 4.F guards its PASS (pass R, `REVEAL_MAX = 6`,
`t4f.py:37`; over the bound an `incomplete` note gives NEEDS REVIEW).
Pass R reads revealed content only through `aria-controls` or a
`<details>`, and calls `labels.read_revealed` only when that content
holds form fields (`t4f.py:414-428`): Home's X buttons, in a container
with buttons only, are never read. 4.A, 4.C, 4.D, 4.E, 5.A-5.C and 5.D
can PASS with content never opened (4.C and 5.A-5.C only add a note).

**Design: `src/tobi508/reveal.py` (facts only, no outcomes).**
- Triggers from the walk's stops, no new pass: collapsed controls,
  `aria-haspopup`, `aria-controls`, `role=tab` not selected, `<summary>`,
  and buttons whose Enter already showed a dialog (4.A or pass R). Move
  haspopup, controls and selected into the stop description
  (`traverse._DESCRIBE_FN`, `models.Stop`) so they do not depend on 4.F's
  hook. Plain buttons with no hint are not triggers (question B3).
- Each trigger on a fresh load: reach it (direct focus and Enter for the
  5.x reads; Tab replays where 4.F and 4.C need the keyboard path;
  question B5), press through `observe` with a click as fallback, and
  take visible components before and after: the new paths are what it
  revealed (no `aria-controls` needed). Navigation, a new page or an
  error is "could not be opened".
- Depth 2: in each opened container, check up to 2 options per set of
  checkboxes or radios (what makes Home's X buttons appear; question
  B2).
- Records `RevealedState` per trigger (trigger, opened, why not, effect,
  new paths, components read with ANDI last, a picture) and `RevealPass`
  (states, found, opened, unopened with reasons, cut by time), cached in
  `ctx.cache["reveal"]` and written to `evidence/reveal.json` so a
  resumed run does not repeat it.
- Bounds: 20 triggers (14592 has 16), 2 options per set, stops on
  `ctx.out_of_time()`. With no time limit (the default) the 20 cap still
  holds. Cost on Home: about 10 states × 6 s ≈ 60 s, against pass R's
  89 s today once pass R reuses them (assumed for direct focus).
- `base.py` gains `uses_reveal`; the pipeline attaches the walk extras of
  checks that use it only after a trigger is opened. Pass R becomes a
  consumer (its Tab path and dialog checks stay). `labels.read_revealed`
  is replaced by reading the states' components; 5.D's own reveals feed
  the same list. Keyed to a page unit so the frames bundle can run it on
  a frame loaded as its own page.

**Specs.**
- 5.C 1.4.0 → 1.5.0: revealed components read as load components; the
  rule for buttons in one set that share a name (question B1, blocking
  for the Home evidence); the guard.
- 5.A, 5.B 1.2.0 → 1.3.0: revealed components; the guard.
- Guard only, until phases 2 and 3: 4.A (→ 1.4.0 after 2a), 4.C (→
  1.11.0 after 2b; its collapsed-control note becomes the guard), 4.D
  1.3.0 → 1.4.0, 4.E 1.2.0 → 1.3.0, 5.D (→ 1.4.0 after 2b; also when
  revealed fields were not filled).
- 4.F 1.3.0 → 1.4.0: pass R reads `RevealPass`; wider triggers; 20.
- **The guard** (principle 3; FAIL is never lowered): a test that would
  PASS is NEEDS REVIEW, not performed, when (a) a trigger was found and
  not opened (bound, time, error), (b) neither Enter nor a click opened
  it (no new paths, still collapsed; question B4), (c) an opened state
  could not be read, or (d) until the test reads revealed states (phases
  2, 3), any revealed state holds what it tests (stops for 4.x, fields
  for 5.D). Reason: "This test could not be performed: N menus or
  sections could not be opened: …" or "… content that opens was not
  tested yet".
- Effect on round 2 (from its reports): rule (d) turns about 7 PASS cells
  the key passes into NEEDS REVIEW (4.E on 5 pages, 4.A Help, 5.D Home)
  until phase 2; rule (a) none at 20 (question B6).

**Fixtures:** `5c/fNN-filter-remove-buttons.html` (a Filters disclosure
whose checked options add X buttons all named "Remove filter from
selection") → 5.C FAIL; `5a/fNN-accordion-unlabeled-field.html` → 5.A
FAIL, 5.C FAIL (today PASS or DNA); a trigger that opens nothing → the
guard's NEEDS REVIEW; reuse `4f/f13-eight-accordions` with the bound set
to 7 in the test, `5a/f12-revealed-other-field`,
`5d/f07-checkbox-reveals-fields`. Then on the step 0 recording of Home:
the X buttons are found (bundle 5's fix 9 must not lose that FAIL).

**Later (ROADMAP):** phase 2, the Tab walk through revealed content for
4.A, 4.C, 4.D, 4.E, 4.F (3-4 days); phase 3, 5.D fills revealed fields
(1.5 days).

### 2e. Error states (fix 3)

TT pp. 28-29 (5.F Identify Content 2-3: "Intentionally enter values …
that violate format and/or other form instructions"; HtT 1-2; ER 1);
4.C p. 21 (HtT 2.b note 1: "check for keyboard traps in the dialog";
note 2: requiring input before moving on "is not a failure");
Understanding 3.3.1; Baseline TC10.D-* (vendored; no frames or traps).
5340's key: 5.F Pass (an error popup under the field for special
characters in the name, or a year outside 1900-2100); 4.C Fail ("If you
enter a year before 1900, the error popup is a keyboard trap too").

- **5.F 1.3.1 → 1.4.0:** a table of likely-to-error values by type and
  purpose (from `type`, `inputmode`, `autocomplete`, `min`/`max`, and
  name, id and label words; question E3): names with odd characters
  (e.g. `J@n3#`); email `test@`; phone `123`; numbers and years min − 1
  and max + 1, or far past and far future when no range is declared
  (question E2); dates far past as well as `wrong_date`'s far future;
  other text "abc". Attempt 2 becomes 2a (low or odd) and 2b (high).
  The spec says markup shows where errors are likely, never that there
  are none, and records Abby's decision (2026-11-08) replacing the
  current "no values from instructions" line. 5.G and 5.H re-checked (a
  PATCH at most). Likely cause on 5340 (assumed): the year field is a
  number input, where "abc" types nothing, so no error showed.
- **4.C 1.11.0 → 1.12.0:** pass P7, the error state: from each pass E
  state where an error appeared (new text, a popup, a dialog), Tab and
  Shift+Tab with P1's trap detection; a trap is an instance through P3
  and table 3a. A JS `alert()` is browser UI, out of scope. 4.C's replay
  prefix gains a typed-text action so probes can rebuild the state. Pass E
  is shared as 5.F and 5.G share it; with 4.C alone, 4.C runs it
  (question E4). Whether a popup that holds focus until the value is
  fixed is a trap or note 2 is question E1 (blocking for the expected
  outcome).
- Code: a value-choosing helper in `forms.py`; `attempt`
  (`t5f.py:410`) generalised. Fields in same-host frames (today skipped:
  `_css` returns None, `t5f.py:206-214`; `FORMS_JS` top frame only;
  `invalid_events` and the dialog count main frame only) are read in
  place through `reader.frames()` with the frames bundle.
- Fixtures: a top-level form (name, year with no `min`; a script popup
  for years before 1900 that pulls focus back) → 4.C FAIL or NEEDS
  REVIEW per E1; a variant that releases focus on Escape → PASS; a name
  field refusing "#" → 5.F instances; the same form in a same-host frame
  (with the frames bundle). TC10.D cases unchanged. Judge eval (5.F J1
  and 4.C inputs change).
- Risks: more values find more errors, which only adds instances; a
  possible false FAIL on 5340's 5.F (key Pass) by M7 if the popup is not
  announced: check against the step 0 recording.

## Verified and assumed

Verified by the research (reading files, round 2's reports, keys and
step logs, three small Playwright probes): the code paths and lines
cited; 5340's frame host; CILab's and 14592's markup (from Agent B's
transcripts); the `paused` signal; the media store fetching unplayed
sources; no fixture with an unplayed video or a blur focus jump; round
2's shared-component counts. Assumed until step 0 or the fixtures: why
the CILab scan missed, why 5.D passed on 5340, what "View timeline"
does, the year field's type, SVS's video codecs, direct-focus timings
and the run-time estimates.

## Questions for Abby (defaults recommended; **blocking** marked)

Video (2a)
- A1. Do hidden videos (in a closed lightbox) count as 3.A triggers?
  Default: yes, as NEEDS REVIEW if not decoded.
- A2. How many unplayed videos to decode per page? Default 3.
- A3. On a failed decode, try the element's other `<source>`? Default
  yes.
- A4. A click that starts media with no media control among the stops:
  FAIL without J1 (like M4n), or keep J1? And should media start count
  for 4.B and 5.D? Default: keep J1; 4.A only.

Trap and tab (2b)
- C1. The whole frame as a loop's section, a stuck element at element
  scope (the OVERVIEW tab's PASS by Tab stays)? Default yes.
- C2. If an Enter probe already did the section's action (values filled,
  "View timeline") and focus still cannot leave, may J2 "yes, it needs
  input" still give NEEDS REVIEW? Default: no, M8 needs that no probe
  already tried it, so it FAILs.
- C7. 5.D's 1 s re-read after a tab-away, only when something changed?
  Default yes.

Templates (2c)
- D1. 9.A with no other page of the same template: NEEDS REVIEW
  (default, per your 2026-11-02 decision that 9.A needs other pages), or
  take the page's own header and nav as the block through a look-settled
  question (would match the key's Fail)?
- D2. A landmark matched only by position: not shared when deciding
  whether pages are related; unchanged otherwise. Default yes.
- D3. TT's EXCLUDE (one link, or fewer than 4 words) as "shares almost
  nothing"? Default yes.
- D4. A microsite as its own set of pages (CILab's key)? Default yes.

Reveal (2d)
- **B1 (blocking for Home's 5.C):** buttons in one set that share an
  accessible name while their rows show different text (the X chips): a
  rule FAIL, or J1 with each row's text? At load too? Default: J1 with
  the row text (a look-settled question), at load and revealed.
- B2. 20 triggers, 2 options checked per set? Default yes.
- B3. Plain buttons with no markup hint are not triggers (a gap a person
  would find)? Default yes, listed in the summary.
- B4. A trigger that opens nothing by Enter or click: NEEDS REVIEW for
  every named test, or only 4.A? Default: every named test.
- B5. Direct focus plus Enter for 5.x reveals, Tab replays for 4.F and
  4.C? Default yes.
- B6. Accept about 7 PASS cells becoming NEEDS REVIEW until phase 2?
  Default yes.

Error states (2e)
- **E1 (blocking for the fixture's expected outcome):** on 5340's year
  popup, which keys did you press, and could a keyboard user get back to
  the field and fix the value? If yes, note 2 may apply.
- E2. Odd characters and "far" years: `#@$%` and 1000/3000? Default yes.
- E3. May label words (page text) choose the value to type? Not a URL,
  tool or outcome choice. Default yes.
- E4. Pass P7 when 4.C runs without 5.F (4.C runs its own pass E)?
  Default yes.
