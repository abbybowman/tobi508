# D: traverse.py, walk.py, observe.py, reveal.py, forms.py, labels.py

## Overview

The core is carefully built and heavily commented, and its main design choices are sound (isolated-world focus reading, a pinned retry on navigation, a quick-replay mechanism with a safety redo, caps reported in `incomplete` for most cases). The weak spot is the boundary between "evidence could not be read" and "nothing there": `evaluate_top` and `reader.call` return `None` for both, and several readers cover only the light DOM of the top frame. Two of those paths reach DOES NOT APPLY or PASS (5.A "no form fields", 4.A pointer scan). Shadow DOM is the most common gap: declarative shadow roots are invisible to the settle log, shadow content is invisible to `COMPONENTS_JS` and `DOMDebugger.getEventListeners`. Time costs are dominated by per-stop CDP round trips (about 8 sequential calls per `FocusReader._read`), duplicated whole-DOM `path()` walks in `reveal._state` and a quadratic `FOCUS_JS` in `labels.py`. Embedded JS is duplicated across at least five files, with already-diverging copies of the field selector.

Counts: P0 0, P1 2, P2 11, P3 5. Findings below were checked by reading and, where marked "confirmed", by a small Playwright script run in the repo's venv (scripts in the scratchpad `d/` folder, nothing in the repo touched).

---

### D-01 Form fields in shadow roots read as "no form fields" and give DOES NOT APPLY
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/labels.py:53 (`comps()` uses `doc.querySelectorAll(SEL)`), labels.py:361-380 (only iframes add to `incomplete`), checks/t5a.py:238-243
- What: Pass L inventories form components with a plain `document.querySelectorAll`, so fields inside open (or declarative) shadow roots are never seen. The only "not checked" note is for iframes. 5.A then sees `not lp.components and not lp.incomplete` and returns DOES NOT APPLY ("This page has no form fields"). Design-system pages (web components for inputs) hit this. The walk's own `inventory.form_fields` does pierce open shadow roots and would disagree, but 5.A/5.B/5.C never compare against it (only 5.D/5.F read `walk.p1.form_fields`).
- Evidence: Ran `COMPONENTS_JS` on a page with `<label>Name <input></label>` inside an open shadow root: returned `[]`. `grep form_fields` shows no use in t5a/t5b/t5c. t5a.py:238 gives DNA when components and incomplete are both empty.
- Fix: In `read_session`, when `components` is empty (or fewer than the walk's form-field count), add an `incomplete` note using `walk.p1.form_fields` or a shadow-piercing count, like the `framed` note. Better: make `comps()` walk open shadow roots.
- Confidence: confirmed

### D-02 `evaluate_top` turns a thrown exception into `None`, which callers read as "nothing found"
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/traverse.py:539-546 (compare `call_in`, traverse.py:475, which does check `exceptionDetails`); callers labels.py:362/403, observe.py:42, checks using `evaluate_top` (11 call sites)
- What: `evaluate_top` returns `res["result"].get("value")` without looking at `exceptionDetails`. A JS error inside `COMPONENTS_JS` (or any other snippet) comes back as `None` (or `{}`), not an exception. `read_session` then does `got or []`, so zero components with no `incomplete` note, which is the DNA branch of 5.A (and the same in 5.B/5.C). `reader.call` (traverse.py:436) likewise returns `None` for "cannot be reached" and for "the function returned null", and checks such as t5d.py:290 do `await reader.call(...) or {}`, so unreadable fields look like fields with an empty label.
- Evidence: `evaluate_top("throw new Error('x')")` and `evaluate_top("(function(){null.x})()")` both returned `None` with no exception (confirmed by script). `call_in` raises `RuntimeError` on the same input, so the two helpers disagree.
- Fix: Make `evaluate_top` raise on `exceptionDetails` like `call_in`; make `FocusReader.call` distinguish failure from a null result (raise or return a sentinel), and let the t5d/t5f callers treat failure as unreadable instead of `{}`.
- Confidence: confirmed (the helper); likely (a real page triggering it, since the isolated world is hard to break, but any snippet bug lands here)

### D-03 Click handlers inside shadow roots are not found, so 4.A's mouse-only scan can miss them
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/traverse.py:515-518 (`DOMDebugger.getEventListeners` with `pierce: False`); consumer checks/t4a.py:391-401 (`_mark_listeners`)
- What: Listeners are read from the document node with `depth: -1, pierce: False`, which does not enter shadow roots. A web-component button with a `click` handler inside its shadow root gets no click/odd mark, so the pointer scan never sees it as "mouse-only", while 4.A's other scan code does walk shadow roots (t4a.py:107). The docstring only warns about delegation, not shadow roots.
- Evidence: Page with `#a` (light DOM) and a `<span>` inside an open shadow root, both with click listeners: `listeners()` returned 1 listener (the light one) only (script t2.py). Other 4.A heuristics (cursor, role) may still catch some cases, which I did not trace.
- Fix: Also collect listeners from each shadow root (the nodes are reachable via `DOM.getDocument pierce` and `describeNode`), or use `pierce: True` and filter backend nodes by frame; and say in the 4.A coverage note when shadow content was not covered.
- Confidence: confirmed (the gap); likely (outcome effect)

### D-04 Mutations inside declarative shadow roots are invisible to the settle log and to effects
- Severity: P2
- Kind: bug
- Where: src/tobi508/traverse.py:110-113 (observer only on `document` plus `attachShadow` monkey patch)
- What: Shadow roots created by `<template shadowrootmode>` (SSR web components) never call `attachShadow`, and a document-level `MutationObserver` does not see inside them. The settle rule thinks the page is quiet, `Effect.mutations` is 0 (so 4.A can report "no effect" for a control whose only result is a change inside such a root), and the step is not flagged unsettled.
- Evidence: Mutated text inside a declarative root after the init script ran: 0 mutations counted; the same change in an imperatively attached root counted 1 (script t3.py).
- Fix: At init-script time and in `settle`/`snapshot`, walk existing shadow roots (`el.shadowRoot`) and observe them, e.g. a one-time sweep after load and at each `_read_logs`.
- Confidence: confirmed

### D-05 Stale isolated-world cache after an in-page frame navigation; failures hidden by `call()`
- Severity: P2
- Kind: bug
- Where: src/tobi508/traverse.py:390-411 (`_worlds` cache), 413-437 (`call` swallows everything), 554-562 (`read` is the only place the cache is cleared)
- What: `_worlds` maps frame id to (session, execution context id). When a frame navigates, the context is destroyed but the cache entry stays. `read()` clears the cache after an exception, but `call()`, `frames()`, `call_in()` and `evaluate_top()` use the stale context directly. `call()` returns `None` (looks like "unresolved"), `call_in` raises, and callers (`_state`, `playing_media`, `_scan`) catch and `continue`, so that frame silently contributes nothing for the rest of the session unless a `read()` happens first.
- Evidence: Read of `_session_for` and every caller's `except Exception: continue`; no invalidation on `Page.frameNavigated`/context destroyed.
- Fix: Listen for `Runtime.executionContextDestroyed` (or `Page.frameNavigated`) on each session and drop the entry; or retry once with a fresh world in `call`/`call_in`.
- Confidence: likely

### D-06 `FocusReader._session_for` creates a CDP session for every frame on each cache miss and never detaches them
- Severity: P2
- Kind: time
- Where: src/tobi508/traverse.py:390-411
- What: On a miss it builds `candidates` eagerly: `_top` plus a new `context.new_cdp_session(f)` for every other frame, before trying any. For in-process frames the first candidate would succeed, so the extra sessions are wasted. With N iframes (ads, embeds) that is O(N^2) `Target.attachToTarget` round trips per page load, and the sessions live until the context closes (`read()` also drops `_top` without detaching it).
- Evidence: Read of the loop; no `detach` anywhere in the class.
- Fix: Try `_top` first and create per-frame sessions lazily (generator), only for frames where the top session fails; detach on cache clear.
- Confidence: likely

### D-07 `_read` takes about 8 sequential CDP round trips per stop; `getFrameTree` is repeated
- Severity: P2
- Kind: time
- Where: src/tobi508/traverse.py:564-684 (`_read`), 548-552 (`_top_frame_id` calls `Page.getFrameTree` on every read and again in `frames()`), 696-752 (`_element` adds `Accessibility.getPartialAXTree` and a `location.href` evaluate)
- What: Each press reads: getFrameTree, `hasFocus`, `activeElement`, `describeNode`, `callFunctionOn(_DESCRIBE_FN)`, a shadow root resolve and call, then for the element the AX tree and a `location.href` evaluate; then `press()` adds 3-4 more `frame.evaluate` calls per frame (`_read_logs` twice, `settle` polls, `_focus_events`). `observe.snapshot` calls `read()` twice per action. The walk's presses dominate a run, so this is the largest per-run cost in the core.
- Evidence: Read; the `time-budget` notes in the spec say about 70% of presses are replay prefixes.
- Fix: Cache the top frame id (invalidate on navigation); put `hasFocus`, `location.href` and the active-element description in one `callFunctionOn` (return `isFrame/shadow` hints), and fetch the AX node only when the stop is new. `_read_logs`+`_focus_events` could be one evaluate per frame.
- Confidence: likely

### D-08 `settle` counts nominal 50 ms per poll instead of elapsed time
- Severity: P2
- Kind: time
- Where: src/tobi508/traverse.py:835-851 (`waited += POLL_MS`), also 913-916 (rerun window)
- What: Each loop iteration does one `evaluate` per frame (`_read_logs`) plus a 50 ms sleep, but only 50 ms is counted. With several frames each iteration takes much longer, so a continuously mutating page waits well beyond `SETTLE_MAX_MS` (1.5 s) and the 1.0 s re-read window per press; the "unsettled" flag arrives late. The initial `requestAnimationFrame` evaluate and the `_read_logs` calls also have no timeout (unlike `observe._Opened`, which guards the same headed-Chrome hang), so a stalled frame holds a press until the run's outer limit.
- Evidence: Read; no use of `time.monotonic` in `settle`.
- Fix: Use a monotonic clock for `waited`; wrap the per-poll reads in `asyncio.wait_for`.
- Confidence: likely (counting); speculative (hang on a backgrounded headed page)

### D-09 `_focus_events` keys its offsets by frame URL, so same-URL frames lose events
- Severity: P2
- Kind: bug
- Where: src/tobi508/traverse.py:775-784
- What: `before` is keyed by `frame.url`. Two frames with the same URL (two `about:blank` or `about:srcdoc` iframes, two copies of one embed) share one counter that is advanced by both, so the second frame's `slice(before)` skips its own new events. 4.E reads `step.focus_events` for `trusted is False` (script-moved focus) in checks/t4e.py:174, so the "unreliable" flag can be missed.
- Evidence: Read; `page.frames` for two srcdoc iframes yields `['about:blank', 'about:srcdoc', 'about:srcdoc']` (script t1.py). The `_read_logs` totals used by the re-read rule are unaffected.
- Fix: Key by frame object (`id(frame)` or a CDP frame id), not URL.
- Confidence: likely

### D-10 `reveal._open_to` clicks at frame-local coordinates for triggers inside iframes
- Severity: P2
- Kind: false-pass-risk
- Where: src/tobi508/reveal.py:96-108 (`FOCUS_FN` returns `r.x + r.width / 2` from `getBoundingClientRect` in the frame's own viewport), 319-327 (`page.mouse.click(got["x"], got["y"])` in top-page coordinates)
- What: When Enter showed nothing, the fallback clicks the point returned by `FOCUS_FN`. For a trigger inside an iframe that point is relative to the iframe, not the top page, so the click lands on whatever top-page element sits there. If that click opens something, the trigger is recorded as "opened" (and ANDI reads that state), while the trigger's own content is never read; if it does nothing the trigger is "nothing" (reviewed, so safe). The coordinates are also taken before Enter, so a scroll caused by Enter shifts them.
- Evidence: Read of both sites; no frame offset added anywhere (compare `_DESCRIBE_FN` offsets in `FocusReader._read`).
- Fix: Add the iframe element offsets (frame chain) to the point, or use `ElementHandle.click()`/`page.frame(...).locator(...)` instead of raw coordinates; re-measure after Enter.
- Confidence: likely (logic); not exercised on a page

### D-11 `FIELD_FN` calls `checkValidity()`, which fires `invalid` events and runs the page's handlers
- Severity: P2
- Kind: bug
- Where: src/tobi508/forms.py:92-93
- What: Reading a field's state calls `this.checkValidity()`. That dispatches a cancelable `invalid` event on every invalid field, which the page's own handlers see (custom error UI may appear) and INIT_JS's capture listener records in `log.v` (traverse.py:145). 5.F counts `invalid_events` as a delta around the submit press (checks/t5f.py:378-385), so tool reads between do not pollute that count, but the page's handler side effects (an error message appearing on a read before submission) can change what 5.D/5.F/5.H later see.
- Evidence: Read; `validity.valid` gives the same boolean without events.
- Fix: Use `this.validity && !this.validity.valid` (no event, no page code).
- Confidence: likely

### D-12 `labels.FOCUS_JS` does roughly fields x elements x others work; 40 ms per field on a modest page
- Severity: P2
- Kind: time
- Where: src/tobi508/labels.py:160-277 (loop at 234-252 and `inOther` at 186), 394-432 (one `evaluate_top` plus one screenshot per field), 454 (see D-13)
- What: For each of up to 60 data-entry fields the script walks every text node, up to 3,000 elements calling `inOther(p)` (a linear scan over all other fields' label elements and fieldsets) and `shown(p)` (rect + computed style) before the cheap region check, and computes `getComputedStyle(p, '::before')` and `::after`. It also repeats `labelEls` over all fields for `nbr`. Cost per field grows with page size; on 60 fields + 3,000 elements it measured 2.4 s (40 ms each), and on a heavy page it is much more. The text-node walk and the pseudo-element scan both could test `inReg(rect)` first (the cheapest filter) and share one pass.
- Evidence: Timed `FOCUS_JS` on 60 fields with 1,500 filler paragraphs (script t1.py): 2.37 s total.
- Fix: Reorder checks (rect/region first, `inOther` last), precompute the `others` set once per call into a `Set`/WeakSet, compute `labelEls` per component once.
- Confidence: confirmed (timing); likely (worse on real pages)

### D-13 Fixed 500 ms sleep after ANDI injection, repeated for every opened state
- Severity: P2
- Kind: time
- Where: src/tobi508/labels.py:445 (`await page.wait_for_timeout(500)`); called per `read_session` (pass L plus every `read_revealed`: up to 20 triggers + 3 sets x 20)
- What: `inject_andi` already waits for `#ANDI508` to attach; the extra 500 ms is paid on every read. In the worst reveal case that is tens of seconds of pure sleep.
- Evidence: Read; callers at reveal.py:414 and 452.
- Fix: Poll `andi_output` until rows are non-empty or a short timeout (e.g. 100 ms steps up to 1 s).
- Confidence: likely

### D-14 `reveal._sets` re-runs the full `STATE_FN` just to read the frame chain; `_state` builds a path for every element three or more times per trigger
- Severity: P2
- Kind: time
- Where: src/tobi508/reveal.py:267-288 (`_sets` calls `STATE_FN` and discards `items`), 81-91 (`STATE_FN`), 305/317/327 (`_state` before, after Enter, after click)
- What: `STATE_FN` computes `path(el)` for every rendered element in the frame (each path walks ancestors and runs `querySelectorAll('#id')` for each ancestor with an id), up to 6,000 items. `_sets` calls it again only to obtain `chain`. Each trigger reloads the page and runs `_state` 2-3 times, so 20 triggers on a large page cost hundreds of whole-DOM path computations. The 6,000-item cap (`items.slice(0, 6000)`) is also silent: opened content beyond the 6,000th element reads as "pressing it showed nothing new" and is classed `NOTHING` (review-safe but misleading).
- Evidence: Read. The cap appears nowhere in `Reveal.incomplete` or the summary.
- Fix: Get the chain from a tiny `chainOf()` function (or store it from the `before` read); compute state as a set of cheap keys (tag + index chain) and only build paths for elements that are new; report the 6,000 cap in `incomplete`.
- Confidence: likely

### D-15 `open_session` always runs `dom_inventory`, including on every replay and reveal load, and the result is discarded
- Severity: P2
- Kind: time
- Where: src/tobi508/traverse.py:1022-1037 (`dom_inventory` inside `open_session`), 350-379 (per frame: whole-DOM scan, plus `frame_element()` and an `evaluate` per ancestor frame); callers include reveal.py:302, `replay()` (traverse.py:1174) and about ten check modules
- What: Only the walk's passes use `Session.inventory` (cap, `form_fields`, `inventory`); replays and probes ignore it. Each replay pays a full DOM scan (`querySelectorAll('*')` with `checkVisibility` and two `matches` per element) in every frame. `run_pass` then calls `dom_inventory` again at the end (traverse.py:1263).
- Evidence: `grep open_session(` shows 11 call sites; `Session.inventory` is read in `drive`/`run_pass` only (and in `Pace.check`).
- Fix: Add `inventory: bool = False` to `open_session`; the walk passes `True`.
- Confidence: likely

### D-16 `observe`/`snapshot` blind spots: failed reads compare equal, dialogs ignore shadow roots and frames, same-count swaps are invisible
- Severity: P2
- Kind: gap
- Where: src/tobi508/observe.py:195-218 (`snapshot`), 301-320 (`observe`), 162-177 (`playing_media`)
- What: If the focus read or the dialog count fails in both snapshots, they are `None == None`, so no "focus"/"dialog" effect is recorded and the action reads as "no effect" (for 4.A a control that did something is then "no effect"). The dialog count is a main-frame light-DOM `querySelectorAll` count, so a dialog in an iframe or shadow root is never counted, and one closing while another opens is no change. `playing_media` silently drops frames it cannot read and indexes media by position, so an element added before the player shifts indexes. `own` is matched with `f.startswith(own)`, so `#nav` matches `#nav-link` and focus moving to a sibling whose id starts with the same text is not an effect.
- Evidence: Read; `snapshot` swallows all exceptions into `None`; `observe` compares with `!=`.
- Fix: Carry an `unreadable` flag in the snapshot and set `Effect.unreliable`/a kind when either snapshot is missing a field; compare dialog paths (DIALOGS_JS) instead of counts and pierce shadow/frames; match `own` on exact path key or a ` > `/` >> ` boundary.
- Confidence: likely

### D-17 Silent caps in reveal options and labels components
- Severity: P2
- Kind: gap
- Where: src/tobi508/reveal.py:40-41 and 428-435 (`MAX_SETS = 3`, `MAX_OPTIONS = 2`), 449-450; src/tobi508/labels.py:21 and 389-393 (`COMPONENT_MAX = 60`)
- What: Sets beyond three, and options beyond two per set, are never tried and never mentioned (only the trigger cap goes into `Reveal.incomplete`). `o.chosen = True` is set for every option in the batch even when `_focus` could not find one of them (`done` is counted but not compared). `COMPONENT_MAX` is reported, but the 60 counts buttons and options together and truncates in DOM order, so a page with many buttons before the form hides fields; revealed components appended in `labels_pass` bypass the cap.
- Evidence: Read; `info["chosen"]` is set but only `not info.get("chosen")` is tested.
- Fix: Add the number of untried sets/options to `Reveal.incomplete`; mark `chosen` only if `info["chosen"] == len(opts)` (or per option); cap fields before buttons.
- Confidence: confirmed

### D-18 `labels_pass` caches before later revealed reads can arrive
- Severity: P2
- Kind: false-pass-risk
- Where: src/tobi508/labels.py:497-535 (cache at 499 and 534), `read_revealed` appends to `ctx.cache["labels-revealed"]` (472-477); producers: reveal.py:414/452, checks/t4f.py:424, checks/t5d.py:642
- What: `labels_pass` merges the revealed reads that exist when it first runs, caches the result, and returns the cached copy forever. Reveal runs before checks in pipeline.py, but 4.F's pass R and 5.D's fill pass also call `read_revealed` in their own `collect`. If 5.A/5.B/5.C ran before 4.F or 5.D in `checks`, those reads would be dropped from 5.A-5.C evidence with no note, so a field revealed there would never be checked for a label. I did not verify check ordering, so the ordering rule needs a test.
- Evidence: Read of the cache; check order is set by `checks.REGISTRY`/selection, not by this module.
- Fix: Record in the cache how many revealed reads were merged and re-merge new ones on each call (or merge at the end of the collect phase), or assert the order.
- Confidence: speculative (depends on check order)

### D-19 Embedded JS duplicated across files, with copies already diverging
- Severity: P3
- Kind: design
- Where: shadow-walk helper: traverse.py:314-324 (`_INVENTORY_JS`), observe.py:27-33 (`SHOWN_JS`), observe.py:151-156 (`MEDIA_JS`), reveal.py:86-89 (`STATE_FN`), checks/t4a.py:107-108. Path resolver `find`: reveal.py:65-67 (walks shadow roots one segment at a time), traverse.py:1302 and 1324 (`_BYPASS_JS`/`_FOCUS_NEXT_JS`, simpler fallback), checks/t4a.py:104. Visibility test (`checkVisibility` with `getClientRects` fallback): traverse.py:288, observe.py:28 and 55, reveal.py:64, labels.py:30, traverse.py:266. Form-field selector: traverse.py:304-306 (`FIELD`, includes `searchbox`, `slider`, `spinbutton`), reveal.py:74-75 (`FIELD`, lacks those three), labels.py:28-29 (`SEL`), forms.py (via `Stop.control`). Tabbable test: traverse.py:294-301 (`candidate`) vs `_FOCUS_NEXT_JS` (traverse.py:1328-1329, a different rule). Text-node walker with visibility filter: forms.py (`FIELD_FN`, `SIG_FN`) and labels.py (`FOCUS_JS`). INIT_JS has a third `path` (traverse.py:116-125, six levels, no shadow handling) beside `PATH_JS`.
- What: Each copy encodes a small rule (what is a field, what is visible, what is tabbable). They have already drifted: `reveal.new_fields` ignores slider/searchbox/spinbutton that `form_fields` counts, so the two numbers disagree for the same page. The next check needs to copy again.
- Fix: One `jslib.py` with a `HELPERS_JS` string (shadow walker, `vis`, `find`, `FIELD_SEL`, `TABBABLE`) prepended where PATH_JS is today (the PATH_JS pattern already works).
- Confidence: confirmed

### D-20 Fragile `str.replace` templating of JS constants
- Severity: P3
- Kind: design
- Where: src/tobi508/labels.py:273-276 (`.replace("LEFT"...).replace("UP"...)` over the whole script), src/tobi508/forms.py:100 (`.replace("BEFORE", ...)` also rewrites the comment "BEFORE_CHARS"), forms.py:42-49 (`_on_host` with `.replace("BODY", fn)`)
- What: Replacing the substrings `UP`, `LEFT`, `RIGHT`, `DOWN` anywhere in a long script works today (I checked the rendered string has no accidental matches) but breaks silently the day someone adds a selector or word containing one of them.
- Fix: Pass the numbers as function arguments (`(i, LEFT, UP, RIGHT, DOWN) =>`) or use `string.Template`/f-string placeholders with a unique delimiter.
- Confidence: confirmed (fragility); no current bug

### D-21 `FIELD_FN` and `SIG_FN` read the light DOM through `ownerDocument`/`doc.body`
- Severity: P3
- Kind: gap
- Where: src/tobi508/forms.py:21-39 (`doc.getElementById`), 74-90 (tree walker on `doc.body`, `compareDocumentPosition` against a field in a shadow root)
- What: For a field inside a shadow root, `aria-labelledby`/`aria-describedby` ids are looked up in the document (not the root), `before` text is computed with `compareDocumentPosition` across trees (implementation-defined ordering), and `SIG_FN` never sees text inside shadow roots, so a change there reads as "no change in the page". Evidence is missing rather than wrong, but 5.D's "nothing changed" is based on it.
- Fix: Use `this.getRootNode()` for id lookups; walk shadow roots in `SIG_FN`; note unreadable scope in the field record.
- Confidence: likely

### D-22 Reveal treats `new_page`/`navigation` as "navigated" (not a disclosure) with no guard
- Severity: P3
- Kind: gap
- Where: src/tobi508/reveal.py:316-330, 169-170 (`not_opened` is False for NAVIGATED), 183-191 (summary leaves NAVIGATED out of `not_opened`)
- What: A control with `aria-haspopup`/`aria-expanded` whose Enter opens a new window or loads another page is recorded as "navigated" and excluded from what the guards see, so a trigger that is both a disclosure and a link has its menu content marked as neither read nor unread. Probably intended for plain links, but `new_page` from a popup trigger is not the same as a link.
- Fix: Report navigated triggers in the summary count (not as `not_opened`) so the specs can decide, or limit NAVIGATED to `navigation` of the top URL.
- Confidence: speculative

### D-23 `observe` repeats the 300 ms noise window and a CDP session per action
- Severity: P3
- Kind: time
- Where: src/tobi508/observe.py:283-295 (`noise_ms` default 300; `_Opened` creates and detaches a CDP session each call), callers checks/t4a.py:817-830 (Enter then Space in the same session each pay it), t4b.py
- What: On one session the noise window measured for Enter is valid for the Space that follows, as 5.D's leave step already does with `noise_ms=0`. `_Opened` attaches to the target for every action.
- Fix: Cache noise per session (`Session.noise`), pass `noise_ms=0` for the second observe; keep one `_Opened` per session.
- Confidence: likely

### D-24 `FocusReader.mark` and `reveal._focus` are per-node round trips
- Severity: P3
- Kind: time
- Where: src/tobi508/traverse.py:521-537 (two CDP calls per node for each click/odd listener), reveal.py:253-264 (`_focus` calls `r.frames()`, hence `getFrameTree` + a world per frame, every time it focuses)
- What: `_mark_listeners` marks each listener node with resolve+call; a page with hundreds of listeners makes hundreds of round trips. `_focus` rebuilds the frame list for each focus call.
- Fix: Resolve with `DOM.pushNodesByBackendIdsToFrontend`-style batch or one `callFunctionOn` on a node array; cache `frames()` per session until navigation.
- Confidence: likely

### D-25 `FocusReader._read` loop limit returns BODY with focus claimed
- Severity: P3
- Kind: gap
- Where: src/tobi508/traverse.py:583, 682-684
- What: After 20 nested frame/shadow hops the loop ends and returns `Stop(kind="BODY")` when the top document has focus. A real element deeper than that (nested widgets) reads as body focus, not as unresolved. Unlikely, but the fallback should be `unresolved`.
- Fix: Return an `unresolved` stop when the loop ran out without reaching an element.
- Confidence: speculative

---

## Unverified leads

- `dom_inventory` and `_INVENTORY_JS` count `fieldKey` radios as `radio:f<name>` for any form, so same-named radios in two different forms are merged into one field (undercount of `form_fields`, traverse.py:307-310); compare the per-form group key in `_DESCRIBE_FN` (traverse.py:250).
- `Traversal.press` re-read path (traverse.py:910-926): the re-read runs only when focus events changed since the last step; a delayed handler that changes the DOM but not focus (after the 2 animation frames) is missed. The spec accepts this for focus; I did not check what 4.D/4.E do for delayed non-focus changes.
- `_element` computes `in_viewport` without scroll offsets and `x/y` offset for nested frames ignores iframe border/padding (traverse.py:710-719); used for 4.D images and `in_viewport`, so a small error is possible for framed stops.
- `bypass()` (traverse.py:1337) clicks a text spot found by `_BYPASS_JS`; the spot is any non-interactive text after the trap, but an ancestor with a click handler (not covered by `INTERACTIVE`) would run page code; page content picks the click position within the page, not a URL.
- `ReplayPlan.of` keeps only the first pass per first-step key, so a second pass with the same key (a re-confirmed pass) is ignored for quick flags; harmless but untested.
- `walk._confirmed` runs the whole second pass when the first ends in a trap, including `again_pace`; for a long page that doubles the walk time; not measured.
