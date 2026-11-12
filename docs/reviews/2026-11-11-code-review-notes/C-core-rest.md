# C: the rest of the core (traverse.py, walk.py, observe.py, reveal.py, forms.py, labels.py)

## Overview

The six files are carefully built and the walk logic itself held up under my tests (wrap, loop confirmation on a second load, cross-origin iframe, no-focusable page all behaved). The weak points are at the edges of "what counts as an effect or as opened": `observe` ignores JavaScript dialogs, treats a fragment-only URL change as navigation, and `reveal` attributes any new visible element to the trigger. Two of these give a false PASS I reproduced (4.A, 5.A). Replays give callers no signal that they landed somewhere else, and each check must verify that itself; some do not. Counts: P0 1, P1 2, P2 4, P3 4 (all new; none refutes a D finding). Everything is in the findings below; patterns and a restructuring sketch are at the end.

| file | lines already covered by D findings | lines I read |
| --- | --- | --- |
| traverse.py (1355) | 110-113, 289-324, 350-379, 390-437, 475, 515-562, 564-752, 775-784, 835-851, 913-916, 1022-1037, 1263 | all |
| walk.py (136) | none | all |
| observe.py (320) | 162-218, 283-320 | all |
| reveal.py (475) | 40-41, 64-108, 253-330, 428-452 | all |
| forms.py (227) | 21-49, 74-100 | all |
| labels.py (535) | 21-53, 160-277, 361-477, 497-535 | all |

---


### C-01 4.A passes a mouse-only control whose only effect is `alert()` or `confirm()`
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/observe.py:266-320 (`observe`, `snapshot`, `Effect.kinds`); only checks/t5f.py:463 registers a `dialog` handler
- What: Playwright dismisses a JavaScript dialog on its own when no listener exists. `observe` never listens, so an action whose only visible result is `alert()`/`confirm()` reads as "no effect". 4.A's pointer scan then concludes the control does nothing and is not mouse-only, so it can PASS. The same blind spot hides a download or any other non-DOM effect.
- Evidence: Ran runpage on `c_mouse_alert.html` (`<div style="cursor:pointer" onclick="alert('Help text')">Help</div>`, plus one link): 4.A PASS (row M2). The same page with `onclick` unhiding a paragraph: 4.A NEEDS_REVIEW ("works with a mouse but can't be reached with the keyboard").
- Fix: In `observe`, register `page.on("dialog")` for the action (record, then dismiss) and add an effect kind such as `js_dialog`; likewise `download`. Add a fixture.
- Confidence: confirmed (ran)

### C-02 Reveal calls a trigger "opened" when the page changes by itself
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/reveal.py:312-331 and 400-403 (`new = set(after) - set(before)`); `observe(..., noise_ms=0)`; `Effect.unreliable` is never read here
- What: What opened is "any element visible after and not before". A live feed, ticker or late banner adds elements between the two reads, so a trigger that does nothing is recorded OPENED. Its hidden content is never read, and the RV guard (which only lists not-opened and read-failed triggers) lets the PASS stand.
- Evidence: Ran `c_feed.html` (a button with aria-expanded=false and aria-controls to a hidden unlabeled field; a list that grows every 300 ms; one labelled field elsewhere): 5.A PASS, reveal summary `opened: 1, not_opened: []`, evidence/reveal.json shows "Filters opened Enter new_elements 1".
- Fix: Count only elements new inside the controlled region or after `aria-expanded` flipped; or take a noise window (as `observe` does for 4.A) and mark the trigger `NOTHING`/unreliable when the "new" elements are what the noise window also produced.
- Confidence: confirmed (ran)

### C-03 Reveal drops a menu whose trigger is `<a href="#">`: the fragment change is "navigation"
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/observe.py:302 (`after["url"] != before["url"]`, fragment included); src/tobi508/reveal.py:316, 328-330 (NAVIGATED); reveal.py:169, 183 (not in `not_opened`)
- What: Enter on `<a href="#" aria-haspopup aria-expanded=false>` with a click handler that opens a menu also changes the URL to `...#`. `observe` records "navigation", reveal records NAVIGATED and returns before reading anything, and NAVIGATED is excluded from what the guards read. The menu is neither read nor reported. (This is the "fragment-only URL as navigation" pattern; `traverse.navigated()` handles the fragment correctly, `observe` does not.)
- Evidence: `c_hash.html` (that link, hidden unlabeled field in the menu): 5.A PASS, reveal summary `opened 0, not_opened []`, trigger status "navigated". The same page with `<button>`: 5.A NEEDS_REVIEW with the field found.
- Fix: Compare URLs without the fragment in `observe` (add a separate `fragment` kind); in reveal, NAVIGATED only for a real navigation or new page, and otherwise fall through to the diff.
- Confidence: confirmed (ran)

### C-04 Reveal never checks that `focus()` worked before pressing Enter
- Severity: P2
- Kind: bug
- Where: src/tobi508/reveal.py:106 (`focused` returned), 306-312 (`got["focused"]` never read)
- What: If the trigger cannot take focus (inert, covered, hidden by a handler), Enter goes to whatever has focus, and anything that then appears is credited to the trigger (compounds C-02). The click fallback also uses the pre-Enter coordinates (D-10).
- Evidence: read of both sites; grep shows no use of `["focused"]`.
- Fix: Treat `focused: false` as NOT_FOUND/ERROR.
- Confidence: likely

### C-05 Reveal's summary says nothing about options not chosen or not read
- Severity: P2
- Kind: gap
- Where: src/tobi508/reveal.py:177-200 (`summary`), 442-462; src/tobi508/engine.py:118-134
- What: `Option.chosen/read` stay False when a set could not be chosen or ANDI failed, but `summary()` has only `not_opened`, `read_failed` (triggers) and `opened_with_focusable`. Guard RV cannot see unchosen/unread options, so a PASS stands although the state behind a filter choice was never read. (Adds to D-17, which covers the silent caps.) `rv.get("failed")` in engine.py is set only by pipeline.py:1158 and is fine.
- Evidence: read.
- Fix: Add `options_unread` (names) to the summary and to the RV `bad` list.
- Confidence: likely

### C-06 `replay()` does not tell the caller when it landed on a different element
- Severity: P2
- Kind: design
- Where: src/tobi508/traverse.py:1166-1206 (`want` compared only when `quick`; the slow redo and plan-less replays compare nothing); callers that do not verify: checks/t4e.py:327 and 345 (`_control`, `_before_shot`), checks/t4d.py:663 (relies on the hook's subject set)
- What: Pages that differ per load (docs/solutions/trap-seen-once.md: a survey dialog on 1 load in 10, A/B content, a banner) can make a replay end on another element. The quick path guards against its own shortcut only. Each check must re-verify; 4.A, 4.B, 5.D, 9.A do, 4.E's control and "before" picture do not (evidence only, so low risk today).
- Evidence: read of all `replay(` callers.
- Fix: Set `Session.landed: bool | None` in `replay()` by comparing the last step's `path_key` with the plan (for every press, not only quick ones) and have `ctx.replay` raise or flag when False.
- Confidence: likely (read; not run)

### C-07 A stop that script moves focus off is never read, and 4.D still PASSes the rest
- Severity: P2
- Kind: gap
- Where: src/tobi508/traverse.py:906-962 (`press` reads where focus is after settling); checks/t4d.py:714-725 (no comparison of distinct stops with `walk.inventory`)
- What: When link 3's focus handler moves focus to link 1, Tab never yields link 3 as a stop, so its focus indicator is never evaluated. P1 ended `loop` after 4 steps, P2 covered the others.
- Evidence: Ran `c_jump.html` (10 links, link 3 focus handler calls `l1.focus()`): P1 `loop` l1,l2,l1,l2 (confirmed on the second load); 4.C PASS (M3), 4.D PASS "each of the 10 elements we could reach" (inventory was 11), 4.E FAIL, 4.A NEEDS_REVIEW. So 4.E and 4.A catch it; 4.D alone would pass.
- Fix: In 4.D/4.E/4.F, a tabbable inventory element no pass stopped on becomes a note and NEEDS_REVIEW (or a spec decision from Abby).
- Confidence: confirmed (ran) for the facts; the outcome is a spec question

### C-08 A page with nothing focusable is walked 100 presses
- Severity: P3
- Kind: time
- Where: src/tobi508/traverse.py:854-867 (`detect_p1_end` needs `first_key`), 1222; walk.py:67-88
- What: With no element stop, every press reads OUT, no end condition fires, and each pass runs to the cap (50). Both passes end `cap`; DNA is still right.
- Evidence: Ran `c_none.html`: p1 and p2 `end=cap, steps=50, inventory 0`, 4.C and 4.D DNA. About 3 s here.
- Fix: End a pass after 3 consecutive OUT reads with no element seen (`wrap` with 0 stops).
- Confidence: confirmed (ran)

### C-09 Inventory is read before the page settles, so the cap can be too small
- Severity: P3
- Kind: gap
- Where: src/tobi508/traverse.py:1040-1042 (`dom_inventory` before `t.start()`/`settle`), 1258 (`cap`)
- What: A page that renders its controls just after `load` gets `inventory` small and `cap = 3 x inventory + 50`. 4.C guards with `inventory_end` (t4c.py:722); 4.D/4.E/4.F do not, but they only see `end=cap`, which is NEEDS_REVIEW-safe. Closed shadow roots are not counted either (`el.shadowRoot` is null).
- Evidence: read; not run.
- Fix: Read the inventory after `t.start()`.
- Confidence: likely

### C-10 Smaller silent reads in labels and reveal
- Severity: P3
- Kind: gap
- Where: src/tobi508/labels.py:370-380 (a frame whose evaluate fails adds nothing to `framed` or `incomplete`); reveal.py:415, 455 (the trigger's accessible name, page text, goes into the description of the read, cut at 80 characters); reveal.py:318 (the click fallback is skipped when Enter produced any "dom" effect, so a ticker page never tries the click and the trigger becomes NOTHING, review-safe)
- Evidence: read.
- Fix: Count unreadable frames; quote the name as data; run the click when Enter showed nothing new regardless of "dom".
- Confidence: likely

---

## Pattern instances (file:line)

1. Light DOM only: labels.py:53 (`comps`), 205/234 (`querySelectorAll` in FOCUS_JS), observe.py:73 (dialogs), 88 (overlays), forms.py:77/112/120, traverse.py:1337 (`_FOCUS_NEXT_JS`), labels.py:372 (frames). Already in D-01/D-16/D-21.
2. Failed read as nothing: traverse.py:413-437, 539-546; observe.py:195-218; labels.py:362, 403-407; reveal.py:244-246 and 278-279 (frames skipped silently).
3. Silent cap: reveal.py:90 (6000), 428/435; labels.py:389; traverse.py:103 (40 ignore selectors); the 20-hop loop at traverse.py:583.
4. Fragment as navigation: observe.py:302 (C-03); correct in traverse.py:980 and t4e.py:339.
5. `innerText` of unseen text: labels.py:40, 90, 126-128.
6. Fixed sleeps: labels.py:445 (500 ms), observe.py:289 (300 ms), traverse.py:849 (50 ms polls).

## If we started over: the core

1. **One effect model.** `observe.Effect` should record JS dialogs, downloads, fragment changes, DOM changes inside a named region, and "noise" per kind, and be the only thing 4.A, 4.B, 5.D and reveal read. Touches observe.py, reveal.py, 4 checks; about 300 lines; fixes C-01, C-02, C-03.
2. **A `Replay` result that knows whether it landed** (C-06): `replay()` returns the session plus `landed` against the walk's plan, for every press; callers stop re-implementing the check. About 100 lines across traverse.py and `ctx.replay`.
3. **One shared JS library** (`jslib.py`: shadow-piercing query, visibility, path, field selector, tabbable test), and `evaluate_*` helpers that raise on failure (D-02, D-19). Touches all six files and t4a; about 400 lines moved, little new.
4. **Split traverse.py** (1355 lines: init script, focus reader, settle, passes, replay, bypass) into `focus.py`, `settle.py`, `passes.py`, `replay.py`. Mechanical, about 1 day, makes the next reviewer's job smaller.
5. **Reveal as a diff of the controlled region**, not of the whole page, using the trigger's aria-controls or its next siblings. About 150 lines in reveal.py.

## Unverified leads

- A page that shows a cookie dialog on every second load: only read, not run (see C-06).
- Download, clipboard and `window.print()` as effects: the same gap as C-01, not run.
- Shadow-root-only page and closed-root inventory (C-09): not run.
- `Stop.key` changes when a framework re-renders a node mid-walk; it could defeat `wrap` (OUT in the cycle blocks `loop`), giving `cap`; not run.
