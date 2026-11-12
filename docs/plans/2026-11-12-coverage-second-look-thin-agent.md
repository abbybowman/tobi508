# Plan: readings that say what they covered, a second look, and a thinner agent (2026-11-12)

Detail for the roadmap items that came out of the code review
([reviews/2026-11-11-code-review.md](../reviews/2026-11-11-code-review.md)).
Agreed in outline by Abby, 2026-11-12, with two decisions: a guard may
move DOES NOT APPLY to NEEDS REVIEW, and none of this is a formal gate;
each step says plainly what each test can and cannot do at that point.
What is scheduled when is in
[the roadmap](../ROADMAP.md); this file keeps no schedule. Nothing here
changes who decides an outcome: outcomes still come only from
`specs/rules/`. Agent-assisted results, not certified Trusted Tester
results.

A thread that builds a part starts from
[reviews/2026-11-11-code-review-fixing.md](../reviews/2026-11-11-code-review-fixing.md)
(how to fix one item, the reproducing pages, which model suits which
part) and then reads its part below.

## Why

- The review found 30 wrong PASS or DOES NOT APPLY results with small
  pages. In all 22 checks the rows and their order matched the specs.
  The errors were in what the rows were fed.
- Three causes cover most of them:
  1. A reading that is empty because nothing is there and a reading
     that is empty because the tool could not look are the same value.
  2. A cap, a time limit or a trap is recorded as an "incomplete"
     reason in some checks, a note in others, nothing in the rest. Only
     the first holds back an outcome.
  3. The specs define "a form", "an error", "a label", "moving" by what
     the tool can see.
- The model and the person only see NEEDS REVIEW. A PASS or a DOES NOT
  APPLY goes straight to the report, so nothing downstream can catch a
  wrong one. Round 2 said the same: the rules alone gave 3 false PASS
  and 2 missed fails; no judge's answer gave any.
- The calling agent reads about 93,000 tokens for one page (measured on
  `tests/fixtures/budget/agency-home.html`), more than half of it two
  files it is told to save by copying them through its own context.

## The parts

| Part | What | Removes (review IDs) | Size (estimate) |
| --- | --- | --- | --- |
| A | Quick fixes that need no spec decision | E-01, E-07, C-03, F-06, H-11, F-01, N-08, W-05, K-04, E-02, K-01, M-11, F-04, H-15 | 1 to 2 days |
| B | A count of what exists, and a guard that holds DOES NOT APPLY | D-01, H-08, M-07, M-02, K-02, M-12, N-01, N-06, E-03, F-11 | 2 to 3 days |
| C | Every reading reports what it covered | the rest of cause 1 and 2: E-12, F-12, F-15, H-03, M-05, H-05, H-07, M-04, M-09, N-05, W-02, W-07, W-11, C-05 | about 2 weeks, reader by reader |
| D | One library for reading the page, frames included | D-03, D-04, D-19, D-21, M-06, F-08, H-01; post-round 2 fix 7 | 4 to 5 days |
| E | Meaning goes to the judge, not to a word list | M-03, E-09, M-08, N-12, N-15 | 1 day a list, plus the judge eval |
| F | A second look at confident outcomes (trial, then a guard) | what nobody thought to test for | trial: half a day; guard: 2 to 3 days |
| G | The person's review page: the page itself, the gaps, a sample | reviewers inheriting the tool's blind spots | adds to the pivot plan's bundle 6 |
| H | The store first, a thin MCP surface, one writer per run | T-01 to T-04, A-02, A-03, G-01, A-01, S-05, B-03, B-04, G-03, G-06, G-07, G-09 | 1 to 2 weeks |
| I | Tests: a grid of hard pages, shared recordings, CI | Q-01, Q-02, Q-03, Q-06, Q-07 | CI: an hour; grid: 2 to 3 days |
| J | Later: the local runner; one watch on a paused clock | N-02 to N-09, W-09 (the watch) | not sized |

Dependencies: I's grid before or with B and C (it is their test). B
before C (C generalises B and keeps its guard). D can run beside C; the
shadow-root gaps close in B as NEEDS REVIEW and in D as real readings.
F's trial needs the server judge working on round 2's frozen pages
(roadmap, Now 3). H's store before G's review page. A is independent.

---

## Part A: quick fixes

Each has a reproducing page in
[reviews/2026-11-11-code-review-pages/](../reviews/2026-11-11-code-review-pages/README.md)
and a named function in the review. None changes a spec row; where the
spec already says the right thing, the code is brought to it.

| Item | Change | Where |
| --- | --- | --- |
| E-01 | The hover cap goes to `st.incomplete`, not `st.notes` | `checks/t4a.py`, hover scan |
| E-07 | One "out of time" helper that always records; use it before 4.C's error-state pass | `checks/base.py`, `checks/t4c.py` |
| C-03, F-06, H-11 | Compare addresses without their fragment in `observe`; 4.E counts a navigation only when the address without its fragment changed | `observe.py`, `checks/t4e.py`, `reveal.py` |
| F-01 | 4.D's arrow loop: five items, then the opposite arrow once | `checks/t4d.py`, pass W |
| N-08 | 2.B's row A1: a streaming player and media over the cap, shared with 2.A and 3.A | `checks/t2b.py`; one helper for the three |
| W-05 | 2.A compares the last reading an element appears in with its first | `checks/t2a.py`, `find_audio` |
| K-04, E-02 | An address that is empty, `#`, `javascript:` or the page itself is not a destination | `site.py` `norm_href`, `checks/t9c.py`, `checks/t4a.py` `_same_link` |
| K-01, M-11 | After recording, refuse an other page whose final address equals the tested page's (fragment, trailing slash and scheme ignored) | `pipeline.py`, other pages |
| F-04 | Set `incomplete` before the `Attempt` is built | `checks/t4d.py` |
| H-15 | `el.matches(':disabled')` | `labels.py` `comps()` |

E-02 and K-04 change which row a control lands on (the question where
it was PASS, another pairing where it was FAIL): word the spec rows to
match, as a MINOR change, and show Abby.

Done when: each page in the index prints the new outcome, each has a
fixture, and each check's fixture file and ACT or Baseline cases pass.

## Part B: a count of what exists, and a guard on DOES NOT APPLY

The cheapest way to stop "nothing here" when something is there.

**The count.** One script, read once per run on the replay after the
page settles, that enters open shadow roots and same-origin frames and
counts what exists whether or not any reader will read it. The walk
already has the start of it (`traverse._INVENTORY_JS`, `dom_inventory`:
focusable elements and form fields, shadow roots entered), and 5.F
already uses it: no field stop but fields in the inventory is NEEDS
REVIEW, where 5.H without it says DOES NOT APPLY (M-04).

- New module `count.py` (or grow `dom_inventory` into it): a function
  that takes a loaded page and returns a `Count`. Called on the walk's
  first load when a walk runs (no extra load), else on pass T's load,
  else on a load of its own. Kept in `ctx.cache["count"]`, written to
  `evidence/count.json` and `report.count`.
- Read it after the walk's `start()` settles, not before (C-09).
- Fields, each a number, with the part inside open shadow roots and the
  part inside frames kept apart:
  - `fields` (the walk's field selector), `fields_hidden` (in the DOM
    and not rendered: `display: none`, `hidden`, a closed `<details>`),
    `contenteditable`
  - `forms_with_button` (a `form` holding any button, submit type or
    not, button-only forms included)
  - `media` (`video`, `audio`), `media_played` (see the hook below)
  - `canvases` (50 px or more), `draggable`
  - `images` (so a reader with a cap of 30 can say it was passed)
  - `players` (frames whose host is a known player), `frames_unread`
  - `landmarks` and `links`, for the site read
  - `shadow_roots`, and custom elements with no open root (a possible
    closed root, which nothing can enter)
  - `focusable` (today's inventory)
- **One hook, before page scripts:** wrap `HTMLMediaElement.prototype
  .play` to count elements that played, attached to the document or
  not (N-01). It goes in the init script every replay context gets.
  `speechSynthesis.speak` the same way.

**What each check reports.** A check says how many of each thing its
own reader read, in its state: `read = {"fields": 3, "fields_in_shadow":
0, ...}`. Today's readers read nothing in shadow roots, so the gap
shows. After part D they read them and the gap closes with no change to
the guard.

**The guard.** A new shared guard beside GU, RV and RC, in
`engine.apply_guards`: for each count key the spec lists, if the count
is larger than what the check read, DOES NOT APPLY and PASS become
NEEDS REVIEW, with a plain sentence that names the number and the thing
("2 form fields inside a web component were not checked", "1 form is
hidden until something opens it", "31 images: only the first 30 were
checked for animation"). Trace row `CN`. FAIL is unchanged.

- This changes a rule Abby set on 2026-11-09 (guards left DOES NOT
  APPLY unchanged). **Approved by Abby, 2026-11-12.** In the same
  commit as the guard: `specs/rules/_template.md` ("Guards": a guard
  moves a would-be PASS or DOES NOT APPLY to NEEDS REVIEW, never the
  other way) and CLAUDE.md principle 3 (never PASS or DOES NOT APPLY
  on a reading that is not complete). The case: H-08 and D-01 are DOES
  NOT APPLY on pages that plainly have a form.
- The keys per test live in the specs (principle 2): front matter
  `count:` beside `guards:`, and one paragraph in section 3. Draft, for
  the spec author to settle:

| Tests | Count keys that hold the outcome |
| --- | --- |
| 5.A, 5.B, 5.C | `fields` in shadow roots and frames, `fields_hidden`, `contenteditable` |
| 5.D | `fields_hidden`, `contenteditable`, `fields` the walk did not reach |
| 5.F, 5.G, 5.H | `forms_with_button` against forms tested, `fields_hidden` |
| 2.A | `media_played` against media read, `media` in shadow roots |
| 2.B, 2.C | `players`, `media` in shadow roots, `images` over the cap, `canvases` |
| 3.A | `images` over the cap, `players` |
| 4.A | `canvases`, `draggable` (also fix A1 itself: E-03) |
| 4.F | `focusable` against distinct stops |
| 9.A, 9.B, 9.C, 19.A | `landmarks` and `links` in shadow roots and frames, per page read |

**Fixtures** (from the pages folder): `v/shadow-form`, `h/b3`, `h/b2`,
`m/mh_delete`, `m/mf_hidden`, `v/sh-a` with `v/sh-b`, `n/a_detached`,
`n/a_shadow`, `n/g_many`, `e/canvasonly`, `f/trap`. Each must end NEEDS
REVIEW with its sentence. Add one page where the count and the reading
agree, to show the guard stays quiet.

**With it:** `specs/rules/_template.md` (the guard and its direction),
a MINOR bump of every spec that lists it, the README status lines,
`docs/hackathon/evaluation.md` and the deck slide, and the roadmap's
"Known limits".

### Design note (thread B, 2026-11-12; for Abby before code)

**The `Count`** (`count.py`, a Pydantic model; facts only). Each thing
is a `Part` with `light` (the page's own document), `shadow` (inside
open shadow roots, at any depth) and `frames` (inside any frame,
including its shadow roots); a spec key names a part with a dot
(`fields.shadow`) or the whole with the bare name (`fields`).

| Key | What is counted | Notes |
| --- | --- | --- |
| `fields` | rendered form fields, the walk's `FIELD` selector, radio groups once | same definition as `dom_inventory`'s `form_fields` |
| `fields_hidden` | fields in the DOM and not rendered (`display: none`, `hidden`, closed `<details>`); paths kept (light DOM, first 200) | not disabled; `type=hidden` excluded |
| `contenteditable` | editable regions not inside a field | |
| `forms_with_button` | `form` elements holding any `button` or `input[type=submit\|button\|image]`, rendered or not; paths kept | |
| `media`, `media_played` | `video`/`audio` elements; elements that played (the hook), split light / shadow / detached | `media_played` has a fourth part, `detached` |
| `canvases`, `draggable`, `images` | canvas 50 px or more; `draggable=true`; `img` | |
| `focusable` | the walk's tabbable candidates (today's inventory) | |
| `landmarks`, `links` | landmark elements and roles; `a[href]` | |
| `frames`, `frames_unread`, `players` | frames; frames a script could not run in; frames whose host is a known player (2.B's list) | plain numbers |
| `shadow_roots`, `closed_hosts` | open roots entered; custom elements with no open root (maybe a closed one) | plain numbers |

Plus `where` ("walk", "own load", "site read"), `error` (the count
could not be taken) and `played_from` ("pass T" or the count's load).

**Where it is read.**

- Tested page: a walk extra of the pipeline's own, P1 only, whose
  `on_start` runs the count after `Traversal.start()` has settled (no
  extra load; C-09). A confirming second P1 does not count again. When
  no walk runs, one load of its own (settle, count, close) before the
  checks collect. Kept in `ctx.cache["count"]`, written to
  `evidence/count.json` and `report.counts["page"]`.
- Other pages: `site.read_page` runs the same script on the load it
  already makes, into `PageRead.count` and `report.counts["p1"]` ...
- One script per Playwright frame (as `dom_inventory` does, so
  cross-site frames are counted too); a frame that refuses it adds to
  `frames_unread`.
- **The play hook** (`PLAY_HOOK_JS`), added by `capture.replay_context`
  to every replay context before page scripts: wraps
  `HTMLMediaElement.prototype.play` and `speechSynthesis.speak`, listens
  for `play` on the document (capture) and on every shadow root as
  `attachShadow` makes it (media events do not cross a shadow
  boundary, and `<audio autoplay>` never calls `play()`). It keeps the
  elements in a list, so `new Audio()` counts though it is never in the
  document. Read at the count; and at the end of pass T's watch, which
  is the load where autoplay is allowed: that reading replaces
  `media_played` when pass T runs (`played_from: "pass T"`).

**How a check reports what it read.** Every check's state gets
`read: dict[str, dict[str, int]]`, keyed by page (`"page"`, `"p1"` ...)
then by count key, filled in `collect` from its reader's own data (a
number, never a decision). Readers that today enter no shadow root or
frame report 0 there, so the gap shows; after part D they report what
they read and the guard goes quiet with no change. Where a count by
number would let one read thing hide another, the check matches by
path: `fields_hidden` read = hidden fields whose path a revealed read
(`labels.read_revealed`, 5.D's pass F) actually read;
`forms_with_button` read = forms 5.F-5.H took. 2.A's `media_played`
read = played elements that are in its own media list (`M.media`).
A check that does not report a key the spec lists reads as 0 there.

**The guard** (`CN`, front matter `count:`, in `engine.apply_guards`
after GU, RV and RC; it gets the check's state as a new argument):

- For each page the check's `read` names and each key the spec lists,
  a gap is `count - read` when positive. Any gap: PASS or DOES NOT
  APPLY becomes NEEDS REVIEW, note "This test could not be performed",
  row `CN`, the gaps' sentences in the summary (first three), all of
  them in the rationale with their numbers. FAIL and NOT TESTED are
  unchanged.
- The count is missing or has `error` while the spec lists keys: the
  same move, "This page's contents could not be inventoried, so this
  test's result could not be confirmed." (Abby, 2026-11-12: "inventoried",
  not "counted". The inventory is taken once, so this means it could not
  be taken, not that two readings disagreed.)
  An old run with no `counts` is left as it was.
- A key may be marked `@dna` (`count: focusable@dna`): it holds DOES
  NOT APPLY only. Proposed for 4.F, where a page often has more
  focusable elements than the walk reaches and the walk's own rows
  already decide PASS (F-11 is the DOES NOT APPLY case).
- Sentences, one per key and part, plain, with the number:
  - "2 form fields inside web components were not checked."
  - "1 form field inside a frame was not checked."
  - "1 form field is hidden until something opens it, and was not checked."
  - "1 editable text area was not checked."
  - "1 form with a button was not tested."
  - "1 sound or video played from a script or a web component, and was not checked."
  - "31 images: only the first 30 were checked for animation."
  - "1 video player in a frame was not checked." ; "1 drawing area
    (canvas) and 1 item moved by dragging were not checked."
  - "The page has 4 elements that take focus, and the keyboard reached 1."
  - "On other page 1, 3 links inside a web component were not read."

**Keys per spec** (the draft table above, made concrete):

| Tests | `count:` |
| --- | --- |
| 5.A, 5.B, 5.C | `fields.shadow, fields.frames, fields_hidden, contenteditable` |
| 5.D | `fields, fields_hidden, contenteditable` |
| 5.F, 5.G, 5.H | `forms_with_button, fields_hidden, fields.shadow, fields.frames` |
| 2.A | `media_played, media.shadow, media.frames` |
| 2.B, 2.C | `players, media.shadow, images, canvases` |
| 3.A | `images, players` |
| 4.A | `canvases, draggable`, and row A1 itself requires none recorded (E-03) |
| 4.F | `focusable@dna` |
| 9.A, 9.B, 9.C, 19.A | `landmarks.shadow, landmarks.frames, links.shadow, links.frames` |

**Order of work,** one commit each, every fixture of the family rerun:
(1) `count.py`, the hook, the report field, and the guard with the
template and principle 3, no spec listing a key yet (nothing moves);
(2) 5.A-5.C (`v/shadow-form`, `h/b3`, `h/b2`); (3) 5.D; (4) 5.F-5.H
(`m/mf_hidden`, `m/mh_delete`); (5) 2.A (`n/a_detached`, `n/a_shadow`);
(6) 2.B, 2.C, 3.A (`n/g_many`); (7) 4.A (`e/canvasonly`); (8) 4.F
(`f/trap`); (9) 9.A-9.C, 19.A (`v/sh-a` with `v/sh-b`). The pages go
to `tests/fixtures/count/` with one test file; the quiet page is a
light-DOM form, a played `<audio>` with controls, and a light header.

**Decided (Abby, 2026-11-12):** 4.F's `focusable` holds DOES NOT APPLY
only (`@dna`); 5.D lists `fields_hidden` (NEEDS REVIEW on a page with a
hidden form until phase 3 of fix 9b); the count runs on every run.

## Part C: every reading reports what it covered

Part B catches what a count can see. This part catches the rest: a cap
reached, time run out, a trap, a read that failed, a window too short.

- **One record.** `models.Coverage`: `not_entered` (kind, how many,
  where), `caps` (name, limit, how many were there), `time_cut`,
  `failed` (what could not be read), `watched` (seconds, which states
  were opened, which part of the page). Every reader returns one with
  its data: the walk, the label pass, the form and error passes, the
  site read, the reveal pass, the watcher, the flash capture.
- **One rule in the engine.** A finding carries `gaps: list[str]`,
  plain sentences built from the records of the readings it used. PASS
  or DOES NOT APPLY with a gap becomes NEEDS REVIEW with the first
  sentences and "This test could not be performed". Row `CV`. This
  replaces each check's own `incomplete` list and the notes that should
  have been one (E-01). Part B's guard becomes one source of gaps.
- **The spec template** gains one sentence: an applicability row that
  gives DOES NOT APPLY, and a page row that gives PASS, need a complete
  reading. Each spec keeps its own list of what "complete" means for
  it, where it has one today (G3 rows).
- **Order of conversion,** each a commit with the hard-page grid
  (part I) green: the walk (ends `stuck`, `loop`, `cap`, `time` and the
  stops it never reached: H-03, M-05, F-11, C-07), the label pass
  (H-05, H-07, H-12), the error pass (M-04, M-09, M-17), the site read,
  the reveal pass (C-02, C-05, D-17), the watcher (N-05, W-07, W-11,
  N-06), the flash capture (W-02, W-12).
- **Failed reads stop being `None`.** `evaluate_top` and `reader.call`
  raise or return a marked failure (D-02); a caller that wants to go on
  records it in `failed`.
- **The checks' shared base goes in with it,** since every check is
  touched anyway: `checks/common.py` with the finding builder, the
  not-performed finding, the page outcome, the label and key-text
  helpers and the one "out of time" helper. This is the roadmap's old
  "Tidy the checks" item. Every outcome stays the same except where a
  gap now holds one back; rerun the judge eval when a question's text
  changes. Share only what means the same thing: each check keeps its
  spec constants and the conditions that feed its rows. Known items
  carried over from that roadmap entry: the "could not be performed"
  note typed by hand (`models.TEST_NOT_PERFORMED_NOTE`); 5.G importing
  5.F's private helpers (the error pass could be its own module, like
  `labels.py`); `forms.py` exporting underscore names;
  `RunContext.cache` keys as bare strings; `checks/base.py`'s steps
  telling the reader to copy a check.

Done when: no check reads an `incomplete` list or a `notes` list to
decide anything, the grid is green, and the review's items listed for
this part are marked fixed.

## Part D: one library for reading the page

- **Today** the rules for "what is a field", "what is visible", "what
  is tabbable", "how to enter a shadow root" and "how to name an
  element" are written out as JavaScript in Python strings in
  `traverse.py`, `observe.py`, `reveal.py`, `labels.py`, `forms.py`,
  `site.py`, `motion.py`, `checks/t4a.py` and `checks/t5f.py`, and the
  copies disagree (D-19). Most use `document.querySelectorAll`.
- **Instead** one `jslib` string put in front of every script, as
  `PATH_JS` already is: a walk that enters open shadow roots and
  same-origin frames; visible text taken from text nodes that are
  really shown, so hidden words do not count (H-01); the field and
  tabbable tests; the path. Listeners are read inside shadow roots too
  (D-03), and changes inside server-rendered shadow roots are observed
  (D-04).
- **Frames:** this absorbs post-round 2 fix 7. Same-origin frames are
  read in place by the shared walk. A cross-origin frame is loaded as
  its own page from its own recording, with ANDI run there, and its
  findings are located by frame chain, as that fix describes (TT
  Appendix D: a tester runs ANDI inside the frame's own context).
- **Replace, in this order,** each with its fixtures rerun: `labels.py`
  `comps()` and `FOCUS_JS`; `site.py` `walk`; `motion.py` `M.media`
  and the element reads; `checks/t5f.py`'s text walker; `observe.py`
  dialogs and overlays; `forms.py` id lookups; `reveal.py`'s field
  list (which lacks slider, searchbox and spinbutton today).
- Done when: the count of part B and each reader agree on shadow-root
  and same-origin frame content for the grid's pages, and the guard no
  longer fires on them.

## Part E: meaning goes to the judge

A word list decides an outcome in these places. Each is English only,
and each can be wrong in English too.

| Where | The list decides | Change |
| --- | --- | --- |
| 5.H `HINT` (`checks/t5h.py`) | no consequence word: DOES NOT APPLY | Ask J1 for every form the error pass took; the list only orders them |
| 5.H `ERROR` ("checked") | new text with "required" or "must": PASS | "Stayed on the form" needs the same fields visible; text not tied to a field goes to J2 (M-08) |
| 4.B `TIMING` (`checks/t4b.py`) | no timing phrase: PASS | When the page has custom key handlers or its language is not English, ask one question about the page's instructions; the list only picks the sentences shown |
| 2.x `MENTION` (`checks/t2c.py`) | no "pause" word: "no mechanism described" | Ask J2 for every text in the windows (at most 9 a content), or NEEDS REVIEW when the language is not English |
| 2.B `LOADING` | the agent's reason has "load": refuse "essential" | Decide from evidence (a change after 5 s on a page with a control), not from the reason's words |

Each is a spec change (MINOR) with research and a judge eval for the
new or changed question. A first step that needs no new question: when
`<html lang>` is not English, the word-list rows give NEEDS REVIEW
(M-03). Also widen 4.B's list ("press Enter twice", "double-click":
E-09) and report when more than 20 sentences were found (E-05).

## Part F: a second look at confident outcomes

The idea: the server's model looks at a picture of the whole page and
at the tool's own PASS and DOES NOT APPLY claims, and may only add
doubt. It is the one layer that can find a gap nobody wrote a test page
for. It has no measurement behind it yet, so it starts with a trial.
The trial measures and shapes the guard; it is not a gate (Abby,
2026-11-12).

**Trial** (`evals/second_look.py`, not part of the server):

- Pages: round 2's 10 frozen pages, where the rules' own errors are
  known from Abby's keys: the false PASS cells (4.A on CILab, 4.C and
  5.D on 5340), 3.A's DOES NOT APPLY for unplayed video on 14592, and
  9.A's missed fails
  ([abc-score.md](../../evals/judging/round2-armc/abc-score.md)). Use
  the rules as they were for round 2 (the lock commit), or the trial
  only measures what is already fixed.
- One request per page through the judge's connection (`apijudge`
  routes, the pinned model): the full-page picture in tiles, a second
  picture taken 3 s later for motion, and the run's results as plain
  sentences ("5.A: this page has no form fields").
- A fixed question list, the same for every page, each answered yes,
  no or unsure with at most 200 characters of what was seen: is there
  a form or a field; a button that submits or deletes; a menu or
  section that opens; a video or a player; anything that looks
  clickable; anything that moved between the two pictures; a header or
  menu a site would repeat; text in a language other than English.
- Score: of the known wrong PASS and DOES NOT APPLY cells, how many it
  raised doubt on; of the cells the key agrees with, how many it
  raised doubt on (false alarms); tokens and seconds per page; three
  repeats for sameness.
- Write the result here and in `evals/README.md`: what it caught, what
  it missed, what it flagged that the key says is right, and which
  questions earned their place. Drop or reword the questions that only
  add noise.

**Then the guard** (`SL`, beside `CN`): a "yes" that
contradicts a DOES NOT APPLY or a PASS moves it to NEEDS REVIEW with
the model's sentence, marked as the model's. Never the other way; never
used to skip a test. The prompt is fixed and hashed into the report as
the judge's is. The picture is untrusted: page text in it that says
"there is no form" can at worst remove a doubt, which leaves today's
result. Switched on per test like `JUDGE_TYPES`. The README says for
each test whether the second look runs and what the trial showed it
can and cannot catch.

Not in this part: a model reading the page's source. It is large, it is
untrusted text, and part B's count answers the same questions exactly.

## Part G: the person's review page

Adds to bundle 6 of the
[pivot plan](2026-11-07-server-judge-pivot.md) ("Human answers"); the
roles, WebAuthn and the option table there stand.

- **The page beside every crop.** A person who sees only TOBI's crops
  inherits TOBI's blind spots. From the first version (option A), each
  question shows the full-page picture with the crop's place marked.
- **What was not looked at.** The gaps of parts B and C, in plain
  words, at the top of the review of a page.
- **A sample of PASS and DOES NOT APPLY.** A Trusted Tester is shown a
  few confident results per page to confirm or dispute (start with
  two per page, chosen by a seeded draw so a rerun shows the same
  ones). A dispute makes the result NEEDS REVIEW with the person's
  comment; it never makes a PASS.
- **Every dispute becomes a fixture.** The review page records the run,
  the test, and what the person saw; a thread turns each into a page
  under `tests/fixtures/` and, if a rule was wrong, a spec change. This
  is how gaps keep being found after the code review.

## Part H: the store first, a thin MCP surface, one writer per run

The pivot plan's bundle 7 (the store) moves ahead of the review page,
because the review page needs it and because it is what takes the
report out of the agent's context.

**The store and run state.**

- A `runs` module owns a run's files: one lock per run id, writes to a
  temporary file and renames (B-03). `report.json` is written compact,
  and an answer holds its question's id, not a copy of the question
  (T-03); check the readers in `scrt.py` and `compare.py` first.
- A job carries the caller who started it, and `get`, `all_jobs` and
  `running` return only the caller's (A-01). A token with no `sub` is
  refused under `AUTH=oidc` (S-05). A limit on queued runs per caller
  (G-09).
- Applying answers runs as a job like a run (G-03). The judge runs
  after the browser slot is released (B-04). A follow-up run that
  fails is listed, and one the user declines can be dismissed (G-06,
  G-07).
- The rest of bundle 7 as planned: the run index, answers kept by
  content hash and spec version, retention, the disk check.

**The surface an agent sees.**

- Tools register with no output schema and return text only (A-02).
- A result is: the counts by outcome; each FAIL in TOBI's own words;
  each NEEDS REVIEW with its one-line reason (the opening sentence and
  the first reason: G-08); who is being waited on; one link to the
  stored report. No raw page text beyond short quoted names (80
  characters), no `evidence` list, no empty fields (A-11, T-08).
- One instruction block, at the end, and nothing an agent cannot act
  on (A-03).
- Pictures and question inputs go to the calling agent only when it is
  the judge (`JUDGE_BACKEND=client`, the local default). With the
  server judge on, an unsure question waits for a person.
- The report is fetched by the user's browser or saved by the server,
  not copied through the model: a download route behind sign-in when
  hosted; `report_uri` stays for stdio. The pre-SCRT file is built on
  request (T-01, T-02).
- `tobi_explain` for a run lists places and one link per test, caps
  the places, and leaves rule codes in the report (A-10, T-05, T-10).
- **Budget, checked by a test:** the tool list under 5,000 tokens
  (12,700 today), a run result for `agency-home.html` under 8,000
  without pictures (8,500 today, plus 2,100 for pictures), an answer
  result under 1,500 (3,600 and 1,000 today). Measure with
  `reviews/2026-11-11-code-review-pages/tool_sizes.py` and the method
  in the notes' `T-tokens.md`.

**For Abby:** whether `tobi_answer_questions` is registered at all on a
hosted server with the judge on, or only locally.

## Part I: tests

- **CI, first** (an hour): add `tests/test_fixtures_inject.py` to a
  group and make "the rest" ignore only `test_fixtures_[0-9]*`; a step
  that fails when the groups collect fewer tests than the whole suite
  (Q-01). The docs-only filter skips `docs/*` and nothing else (Q-02).
  Timeouts and `uv sync --locked` (Q-08).
- **A grid of hard pages.** Nine shared pages, each run against all 22
  checks: a shadow root, a frame, more items than a cap, a trap in
  mid-page, something that starts late, text not in English and not in
  Latin letters, hidden text, a form behind a button, a reading that
  fails. One table in the test file, check by page, where each cell is
  the expected outcome or a written reason that the page has nothing
  for that test. The rule the table must obey: never PASS, and DOES
  NOT APPLY only with a reason. Start from the pages folder.
- **Shared recordings.** One recording and one walk per fixture page,
  keyed by the file's hash, reused by tests that only change answers
  (Q-07). Rows that need no page run `evaluate()` on stored evidence,
  as some 4.A, 5.D and 5.H tests already do.
- **Rows, not only outcomes,** in the ACT and Baseline manifests and
  for every PASS in the 9.x table (Q-06).
- **The question hash:** the judge eval writes a hash of each question
  and rubric it ran; a fast test fails when the live hash differs
  (Q-04).

## Part J: later

- **The local runner** (the pivot plan's decision 6): the browser runs
  on the user's machine against a page that is not public, and sends a
  recording to the hosted judge and store. It is where the calling
  agent's own value is (the user's unreleased code), and it keeps
  browsing of arbitrary pages off the host. Open: how far the server
  trusts evidence a runner sends.
- **One watch on a paused clock** for 2.A-2.D and 3.A: run the page
  forward 30 to 60 s of its own time on 3.A's paused clock, in place
  of 6.5 real seconds, a 2 s recording and a stepped capture. It would
  see what starts late and remove the sampling problem (W-09). Until
  then: vary the frame gaps, share 2.C's timer hint with 2.A, 2.B and
  3.A once the hint ignores timers of a minute or more (W-10), and
  scroll to every element that waits to be scrolled into view.

## What this asks of the specs and CLAUDE.md

For Abby to approve before the part that needs it is built.

- **Decided (Abby, 2026-11-12):** guards may move DOES NOT APPLY to
  NEEDS REVIEW (parts B, C, F); CLAUDE.md principle 3 then reads: never
  PASS or DOES NOT APPLY on a reading that is not complete. Thread B
  writes both, with the template, in the commit that builds the guard.
- **Decided (Abby, 2026-11-12):** no formal bar for any part. Each
  change states what the test can and cannot do now (the README's
  status line and its "Known wrong outcomes" table).
- **Principle 5's exceptions:** 9.A presses a key an answer names and
  is not on the list (M-15); the media store fetches addresses the
  page names (S-04). List them with their limits, or remove them.
- **Principle 8's list:** 4.A J1 and J2 and 4.B J1 settle a PASS by
  looking and are not on it (E-06).
- **The spec decisions the review marks "(needs Abby)":** H-08, E-03,
  E-08, E-13, H-04, K-05, M-01, M-02, F-02, C-07, and the 4.F
  "order does not matter" row.
- **The roadmap's "Known limits"** change as each part lands.

## How each part is checked

- The page in the pages folder prints the new outcome (the fixing
  handoff says how).
- The grid of part I stays green after every commit of B, C and D.
- A changed question goes through the judge eval.
- After B and after C: rerun round 2's frozen pages and score beside
  the locked rows. The false PASS and missed-fail cells should fall,
  and NEEDS REVIEW will rise. Report both numbers; a rise in NEEDS
  REVIEW that comes from true gaps is the price of the fix.
- Say what was verified and what was assumed (principle 6).
