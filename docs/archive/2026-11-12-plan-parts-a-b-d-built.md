# The plan after the code review: parts A, B and D as built (archive)

Cut from `docs/plans/2026-11-12-coverage-second-look-thin-agent.md` on
2026-11-15, when the three parts were built: their design notes, the
drafts shown to Abby and what she decided. The specs and
`specs/rules/_template.md` hold the rules as they are; nothing here is
kept up to date.

## Part A: quick fixes

Each has a reproducing page in
[reviews/2026-11-11-code-review-pages/](../../reviews/2026-11-11-code-review-pages/README.md)
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

### Decided and built: "destination" (K-04 and E-02)

Drafted by the part A thread; **approved by Abby on 2026-11-12** with her
answers to the open questions below (`mailto:` and `tel:` are destinations;
`#name` with no matching element is none; a link to the page itself is
none) and built in the same session: spec 9.A 1.2.0 (the Term), 4.A
1.6.0, 9.C 1.3.0. The intent of 9.C is unchanged: this only decides which
components count as doing the same thing; what must then agree (name and
description) is as before, and shared header and footer controls are
still paired by id, name and place. K-01 (same page under another
spelling): refused by address; a byte-identical copy under another address
is NEEDS REVIEW in 9.A to 9.C and 19.A (Abby, 2026-11-12).

**Why.** 4.A row M3 and 9.C pairing step 1 both treat two links as
"going to the same place" when their `href` text is equal. An address
that goes nowhere (`#`, `javascript:void(0)`, empty) is equal on every
page that uses it, so:

- 4.A PASSes a mouse-only `<a href="#" onclick=...>` because some reached
  link also has `href="#"` (E-02; the page prints PASS, row k1:M3).
- 9.C pairs an unnamed `javascript:void(0)` icon with an unrelated
  "Close alert" on another page, and FAILs it (C2) (K-04).

**Sources read.** TT 5.1.3 4.A HtT 2.b (p. 19): a control with no keyboard
access passes when "another keyboard method" has "the same function"; the
function is what has to match, not the text of the `href`. TT 9.C
Identify Content (p. 44): "components that have the same functionality";
W3C Understanding 3.2.4: same functionality is the "same result when
used". A placeholder address has no result of its own, so equal
placeholders do not say two controls do the same thing. Not read for this
draft (not fetched in this session): the ACT rules and DHS verdicts for
2.1.1, and the Baseline 4.A and 3.1 cases; I checked only that no fixture
of ours contains `javascript:` and that no round's key under
`evals/judging/` mentions it.

**Wording, one Term shared by 4.A and 9.C** (put in `9a-bypass.md` Terms
with the other site terms; 4.A cites it):

> *Destination.* A link has a destination when its address, made
> absolute, is an `http`, `https` or (dev mode) `file` address, or a
> `mailto:` or `tel:` address, and is not the page's own address.
> Fragments: a link to `#name` on its own page has the destination
> `#name` only when `name` is an `id` or `name` on that page; `#` alone,
> an empty address, `javascript:` and a link to the page itself without a
> fragment have no destination. Two links have the *same destination*
> when both have one and the addresses agree after dropping the fragment
> (except own-page places), the scheme's case and a trailing slash.

**4.A, row M3** (MINOR bump, 1.6.0): "K: a link, or a click that navigates,
whose destination is the destination of a reached link". A candidate with
no destination never matches M3 and goes to M4 (J1). Section 4 text
unchanged otherwise. Effect: a control that was PASS by M3 on a
placeholder now asks J1, so the page is NEEDS REVIEW until answered, and
FAIL if J1 says no alternative (this is the E-02 fix; it moves PASS to
NEEDS REVIEW or FAIL, never the other way).

**9.C, Terms step 1** (MINOR bump, 1.3.0): "*Same destination*: links
with the same destination (Terms, 9.A)." Links with none fall through to
step 2 (same id), 3 (same name) and 4 (same place). Effect: the K-04 page
no longer pairs the icon with "Close alert"; they pair only if id, name
or place says so. This removes a FAIL, but it is a FAIL from a pairing the
spec did not intend. **Check before building:** I found no answer key that
confirms such a FAIL; please confirm, because CLAUDE.md asks you first.

**Code to follow** (after your word): one `destination()` in
`site.py` (replacing `norm_href`'s use for pairing), used by
`checks/t9c.py`, `checks/t4a.py` `_same_link`, and 9.B and 19.A where
they compare `norm_href`; a fixture each: `4a/f19-placeholder-link-twin`
(E-02) and a `9x` pair (K-04: `v/js-a`, `v/js-b`).

**Open for you:** is `mailto:`/`tel:` a destination (I say yes: the
address is the function), and does a link to `#name` with no such target
count as no destination (I say yes: it goes nowhere)?

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

### Design note (step 8, 2026-11-14; for Abby before code)

**Checked first** (a throwaway test against the fixture server, full
Chromium replay; verified, run):

1. ANDI 29.2.2 does not analyse a field inside an open shadow root. A
   page with one labelled field outside and one inside a web component
   gave ANDI output for the outside one only; `andi.js` has no
   `shadowRoot` code.
2. ANDI runs in place inside a frame from another site: injected into
   the frame's own document (`frame.add_script_tag`) on the replay, it
   reported the frame's button ("Inner"), version 29.2.2, nothing
   aborted. This is TT Appendix D's workaround, done by the tool.
3. A frame's page loaded as its own top-level page on the replay is
   refused by the navigation allowlist (`NavigationGuard`: "host
   'localhost' is not in the allowlist"). Opening it would need a new
   exception to principle 5: page content (the frame's `src`) choosing
   a top-level address.
4. Frames from another site are already in the tested page's recording:
   the HAR is recorded for the whole browser context, frames included
   (`Capture.cross_site_frames`, `tests/test_full_chromium.py`), and
   such pages replay in full Chromium, where the frame runs out of
   process. Playwright and CDP reach it there (the walk already follows
   focus into it; `count.take` already counts inside it).

**What `jslib` exports.** `src/tobi508/jslib.py`, one string `JSLIB` of
`const` declarations put at the start of every reader's script, as
`PATH_JS` is today (`PATH_JS` moves into it; `traverse` re-exports the
name). One definition of each rule, taken from the copy the count uses
(`count.COUNT_JS`), so the count and the readers cannot disagree:

| Name | What it is | Replaces |
| --- | --- | --- |
| `kids(n)` | the children as rendered (composed tree): a host's shadow root's children; a `slot`'s assigned nodes; else the element's children. Light children a slot does not show are left out | `el.children` walks (`site.py`), `[...shadowRoot.children, ...children]` (`motion.py`) |
| `all(sel, root?)` | every element matching `sel` in a document and its open shadow roots, at any depth, in document order | `document.querySelectorAll` in the readers |
| `rendered(el)` | `checkVisibility({visibilityProperty: true})` | five copies (D-19) |
| `seen(el)` | `rendered`, at least 4 by 4 px, opacity 0.1 or more, not clipped away: what a sighted person can see | `labels.shown`, `site.shown` |
| `text(el)` | visible text: the text nodes under `el` (composed tree) whose parent is `seen`, `alt` of shown images, not `select`/`option` (H-01) | `innerText` reads (`labels.txt`, 5.F, 4.B) |
| `FIELD`, `isField(el)` | the 5.D field selector (with `searchbox`, `slider`, `spinbutton`) | `labels.SEL`, `reveal.FIELD`, `traverse`'s copy |
| `tabbable(el)`, `inert(el)` | the count's `focusable` rule | `_INVENTORY_JS`, `site.tabbable`, `_FOCUS_NEXT_JS` |
| `byId(el, id)` | `el.getRootNode().getElementById(id)`: an `aria-labelledby` or `headers` id is looked up in the field's own tree (D-21) | `document.getElementById` |
| `path(el)`, `find(path)` | below | `PATH_JS`, `reveal.find`, `t4a`'s copy |
| `hostOf(el)` | the nearest web component host's tag (`x-form`), or `''` | new: for the location sentence |

Readers keep their own rules (what a label is, what an error is); only
these shared tests move. A reader that cannot use a rule unchanged
says so in its commit.

**Frames are read by Python, one document at a time.** No script reaches
into `frame.contentDocument`. A reader asks `jslib.documents(session)`
for every frame CDP reaches (`FocusReader.frames()`: frame id, session,
isolated world), each with its chain, its address, its title and
whether it is on another host, and runs its script in each one's
isolated world (the page's own scripts cannot change what it sees). The
same code then reads a same-site frame and a frame from another site;
the count does the same (`count.take`). A frame no script could run in
is `frames_unread`, as today.

**How a reader names an element.** As the walk names its stops, so a
reader's element and a walk stop still match by name:

- In one document, `path(el)`: CSS segments joined by ` > `; at a
  shadow boundary, the host's path, one space, then the path inside
  the root (`x-form #email`). `find(path)` reads it back, one shadow
  root at a time (reveal's `find`, with an escaped space in an id no
  longer taken for a boundary).
- Across frames, the chain: the CSS paths of the `iframe` elements, top
  first (`Stop.frame_chain`), computed in Python from each frame's
  element (as `traverse`'s inventory does). The whole name is
  `path_key`: chain and path joined by ` >> `.
- Every reader's item carries `frame_chain` and `css`; in the report a
  person reads "inside the web component `<x-form>`" and "in the frame
  'Contact form' (forms.example.com)" (fix 7: the frame's title, else
  its address), with the chain and path in the evidence.

**A frame from another site: recorded, loaded, located.**

- *Recorded:* in the tested page's own recording, as today (point 4).
  Nothing new is fetched and no second recording is made.
- *Loaded:* in place, on the tested page's replay, in full Chromium.
  Each reader reads it as one more document (above), and pass L injects
  ANDI into the frame's own document and reads its output there (point
  2; TT Appendix D). **This changes the roadmap's wording** ("loaded as
  its own page from its own recording"). Reasons: it needs no exception
  to principle 5 or the allowlist (point 3); the frame keeps the size
  and place it has on the page, so 5.A's picture of a field and its
  nearby text are what a person sees there; the walk's stops in the
  frame and the readers' items match by `path_key`. TT allows both: 12.D
  says "test in new tab", Appendix D says run ANDI in the frame's
  context. If you prefer the new tab, the change is one rule: a replay
  (never live) may open, as a top-level page, an address the tested
  page's recording holds as one of its frames' documents; the readers
  stay the same.
- *Located:* by its chain and its title or address, as above.
- *Not in the recording:* a shown frame whose document did not load from
  the recording (its request failed while recording, or was never made,
  such as a frame a click adds) becomes Chrome's error page or stays
  blank on the replay. The count records it as `frames_missing`
  (decision 3 below).

**The readers, in the plan's order** (8a, one pull request each, with
its fixtures, the grid rerun and a page that must still FAIL beside
every cell that becomes PASS):

| # | Reader | Tests whose `read` it fills | Review items |
| --- | --- | --- | --- |
| 1 | `jslib` itself; `labels.py` `comps()`, `FOCUS_JS`, ANDI per frame | 5.A, 5.B, 5.C (`fields.shadow`, `fields.frames`) | D-01 (read), H-01 |
| 2 | `site.py` `walk` (composed tree) | 9.A, 9.B, 9.C, 19.A (`landmarks.shadow`, `links.shadow`) | K-02, M-12 |
| 3 | `motion.py` `M.media` and element reads | 2.A (`media.shadow`, `media.frames`), 2.B | N-01 (2.B's wrong DNA) |
| 4 | `checks/t5f.py` text walker and form read | 5.F, 5.G, 5.H (`fields.shadow`, `fields.frames`) | M-06 |
| 5 | `observe.py` dialogs and overlays | 4.E, 5.D | F-08 |
| 6 | `forms.py` id lookups and `SIG_FN` | 5.D | D-21 |
| 7 | `reveal.py` field list | the reveal guards | D-19 |
| 8 | 4.A's listeners in shadow roots (`traverse`, CDP `pierce`) and changes in server-rendered shadow roots (`INIT_JS`) | 4.A, 4.B (NEW-1) | D-03, D-04 |

Reader 8 touches `traverse.py`, beside step 6d's `walk.py`: it goes
last, after merging `main`. 8b is then small, because the readers
already read frames from another site: ANDI's per-frame run checked
there, `frames_missing`, the location sentence, and fixtures (the ACT
and Baseline frame cases, 5340's shape: a form in a frame from another
site), all in full Chromium.

**The grid.** Its rule today is "never PASS". After step 8 a cell on
`shadow`, `frame-same` or `frame-other` may PASS only where the reader
read the content (the test's `read` matches the count, so guard CN is
quiet) and the grid has a twin page, the same with one defect, where
that test FAILs. The rule in its docstring changes to say so, in
reader 1's pull request.

**Not in step 8:** closed shadow roots (nothing can enter one; still
`closed_hosts`), a frame inside a web component inside a frame (read,
but not given its own fixture), and 4.x's use of the walk (step 6d).

### Decided (Abby, 2026-11-14)

1. **Frames are tested as their own pages for ANDI,** not in place:
   ANDI run inside an embedded frame is not accurate and does not find
   everything (Abby's experience; TT 12.D's "test in new tab"). Pass L
   (5.A-5.C) reads every frame with a document of its own (same site or
   another) on a page of its own, opened in the same replay context,
   in the configured window: the inventory, the visible labels, the
   pictures and ANDI. Its components keep the frame's chain, so they
   still match the walk's stops by `path_key`. The readers that use no
   ANDI (5.D-5.H, 2.A, 4.E) read frames in place, where the page's own
   behaviour (submitting, errors, playing) is what people get. The rule
   this needs, a new principle 5 exception: *on a replay, never live, a
   page of its own may be opened at the address of a frame the tested
   page's replay showed and its recording holds; at most 10 frames a
   run; no other address*. The navigation guard checks the address
   against that list instead of the allowlist.
2. **Not a decision:** a TT test's PASS or FAIL is valid in the page's
   own document, a web component or a frame alike. The template
   paragraph stays as a statement of how the tool reads, not a choice.
   A FAIL with several instances is already a parent row and one child
   row per instance in the pre-SCRT file (`scrt.from_report`); each
   instance's location says the web component or frame, so failures
   inside a frame show as their own child rows. PASS and DOES NOT APPLY
   stay one row.
3. **(1a) Chrome's accessibility tree** gives the name and description
   of a component inside a web component, for 5.B and 5.C, recorded as
   that source. Making the vendored ANDI read shadow roots would mean
   changing it (its hashes are pinned) or copying the web component's
   content into the page, which changes what the names resolve to
   (ids inside a shadow root do not reach out of it): a false PASS risk.
4. **The spec changes are approved,** one MINOR version per spec, in the
   pull request of the reader that makes each true.
5. **`frames_missing` holds PASS and DOES NOT APPLY** as proposed.
   Government sites carry no advertising frames, so no size floor
   beyond "shown". **Later (not step 8, not part F):** at recording
   time, one more live try of a frame whose document failed, under the
   allowlist and the egress rules, as the fuller freeze does for media;
   it is a request page content chooses, so it needs its own principle
   5 exception. The second look (part F) asks a model to reread
   confident outcomes and fetches nothing.

### Status (2026-11-15)

Built, one reader per commit, each with the grid rerun and a FAIL twin for
every new PASS: reader 1 and frames as pages of their own for pass L (PRs
#58, #60), reader 2 (#61), reader 3 (#62), readers 4-8 (#64), and 8b's pass E
in frames (5.F 1.10.0, 5.G 1.8.0, 5.H 1.8.0; fixtures `5f/f30`, `f31`) (#68);
then the grid's NEW-2 cells closed with twins (`4d/f27`, `f28`, `4f/f24`,
`f25` new) and 5.D 1.9.0's `frames_missing`. Pages that PASSed on `main` and
now ask or FAIL: `4e/f13`, `f14`, `5d/f23`, `4a/f29`, `f31`. After #79:
M-06's red box and fleeting message (5.F 1.11.0, 5.G 1.9.0, row A3c;
`5f/f32`, `f33`) and focus dropped on focus inside a web component (4.D
1.10.0, 4.E 1.7.0; `4d/f29`, `4e/f15`). Not done: the same inside a frame
from another site is not reached by the walk (NEEDS REVIEW); the walk's one
capped end on `frame-other` in CI, not reproduced (`docs/KNOWN-LIMITS.md`).

### Spec wording for step 8's three decisions (draft, for Abby)

**Decision 1: a result read inside a web component or a frame may PASS
on the same rows.** In `specs/rules/_template.md`, a new paragraph
after "Guards":

> **Inside web components and frames** (Abby, 2026-11-xx; plan
> 2026-11-12 part D). Content inside an open shadow root (a web
> component), at any depth, and content inside a frame, from the same
> site or another, is part of the page. A test reads it with the same
> reader as the rest of the page and decides it on the same rows: it
> may PASS, FAIL or DOES NOT APPLY there exactly as outside. It counts
> as read only when the reader really read it: the test's `read`
> includes it, so guard CN compares it with the inventory. What no
> reader can enter (a closed shadow root; a frame no script runs in) is
> never read and never counted as read. A frame is read in its own
> document, in place on the tested page's replay; ANDI, where a test
> uses it, is run in the frame's own document (TT Appendix D). A finding
> inside one says where: "inside the web component `<x-form>`", "in
> the frame 'Contact form' (forms.example.com)".

**Decision 1a, for 5.B and 5.C only (yours; not in the roadmap):**
ANDI cannot read inside a web component (point 1). Proposed: for a
component inside an open shadow root, the "ANDI output" in the Terms is
replaced by Chrome's own accessible name and description for it (the
accessibility tree, the same tree a screen reader reads; CDP
`Accessibility.getPartialAXTree`, which the walk already uses), named as
that source in the finding and the question's input, and decided on the
same rows. Spec wording, 5.C Terms, *ANDI output*:

> ... For a component inside a web component, which ANDI 29.2.2 does
> not analyse (checked 2026-11-14), Chrome's accessible name and
> description from its accessibility tree, recorded as that source
> (Abby, 2026-11-xx).

The alternative keeps ANDI as the only source: such a component stays
row M2, NEEDS REVIEW ("ANDI did not analyse the component"), so 5.C
cannot PASS on a page whose fields are in web components. 5.A (visible
label) reads no ANDI output and is not affected.

**Decision 2: the spec changes that say so,** one MINOR version per
spec, each in the pull request of the reader that makes it true:

- *Terms.* Each test's thing is defined wherever it is. 5.A, 5.B, 5.C,
  5.F, 5.G, 5.H, *form component* / *field*: "... in the page's own
  document, inside an open shadow root at any depth, or inside a frame
  (from the same site or another)". 2.A, *media element*: the same.
  9.A-9.C and 19.A, the units of the site read: "... inside open shadow
  roots too; a frame is one unit, as before (a player's own links are
  not the site's navigation)". New Term in each spec that reads frames,
  *frame*: "an `iframe` or `frame` element whose document is read in
  place, as part of the page; its findings name the frame by title or
  address".
- *Section 2 sentences that become untrue.* For example 5.C step 1
  ("in the top document ... Components inside frames are not read yet")
  becomes "in the page's document, its open shadow roots and its
  frames"; 5.F "Run limits" loses "Fields inside frames are not checked
  yet"; each guard CN paragraph's "Pass L reads the page's own document
  only: nothing inside web components or frames" becomes what the
  reader now reads.
- *`count:` keys.* Unchanged lists: `fields.shadow` and `fields.frames`
  stay and the guard goes quiet because `read` now reports them.
  Added: `frames_missing` (decision 3) to every spec whose list has a
  `.frames` key or the whole `fields` (5.A, 5.B, 5.C, 5.D, 5.F, 5.G,
  5.H, 2.A). 9.A-9.C and 19.A gain no `.frames` key.
- *`_template.md`*: the paragraph above, and guard CN's list of keys
  gains `frames_missing`.

**Decision 3: a recording that lacks a frame's page holds the test at
NEEDS REVIEW (proposed: yes).** A new inventory key in guard CN, with
no reader ever reading it (so it always holds):

> *`frames_missing`*: a frame shown on the page (rendered, at least 20
> by 20 pixels) whose document did not load from the recording: its
> request failed while recording, or was never made (a frame added by
> a click). What is inside it was never seen. Sentence: "1 frame on
> this page was not recorded, so what is inside it was not checked."

It holds PASS and DOES NOT APPLY only, never FAIL, like every guard.
Its cost is measured in step 9b (round 2's frozen pages): a page with
an advertising or tracking frame that failed to record would be held
too; if that is common, the size floor rises before the key is listed.

