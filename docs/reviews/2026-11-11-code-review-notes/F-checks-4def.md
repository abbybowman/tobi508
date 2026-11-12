# F: checks 4.D, 4.E, 4.F review

## Overview

- All three checks follow their spec row for row in order and thresholds: the first-match tables are the spec's, the constants in t4d.py equal the spec table, and no outcome is decided outside a spec row except the places named below.
- The serious problems are in the evidence, not the tables: 4.D passes a stop whose box merely shifted (F-02, ran: false PASS), 4.F says DOES NOT APPLY on a trapped page with four links (F-11, ran), 4.F treats a stop it could not measure as "no signal" (F-12), and 4.E fails a fragment-only URL change (F-06, ran).
- Menus with 7 or more items always make 4.D NEEDS REVIEW (F-01, ran): the widget loop presses once too often.
- 4.F silently shows the agent only the first 60 stops (F-15), the spec row for one image per 60 stops has no code.
- Token and time: 4.F repeats a 60-stop list in every question (F-17, about 6,800 characters each), 4.D lists PASS stops as instances (F-19), 4.D reads a whole computed style per stop (F-21).
- About 100 lines of applicability, label, key text and trap bookkeeping are copied three times and have drifted (F-22).
- Counts: P0 2 (F-02, F-11), P1 4 (F-01, F-06, F-12, F-15), P2 11, P3 6.


## Spec vs code table: 4.D (spec 1.5.0, code t4d.py)

| Spec row | Code | Same condition? | Same order? |
| --- | --- | --- | --- |
| A1 (0 stops, 0 inventory: DNA) | t4d.py:882-887 | yes | yes |
| A2 (0 stops, inventory>0: NR) | t4d.py:888-893 | yes | yes |
| A3 (stops>0) | t4d.py:894 | yes | yes |
| M1 (all steps unresolved/re-read: NR) | t4d.py:904-911; `unreliable = unresolved or rerun` at :609 | yes. Dropped instances (M3) are built with `unreliable=False` (:582) so M1 never applies to them | yes |
| M2 (frame stop, next stop inside: PASS) | t4d.py:912-917; `next_inside_frame` :611-617 | yes (any attempt) | yes |
| M3 (focus dropped: FAIL) | t4d.py:918, instance built at :567-586 from `t4e.classify` | looser: no M1 check and no reproduce replay, see F-03 | yes |
| M4 (no complete evidence: NR) | t4d.py:919 + `_best` :742-771 | reasons implemented: bypass-only (see note), never in view (:241), scrolled away (:287), mask >0.5 (:748), never moved on (:620), time limit (via walk end), moved+<12px (:763), draws+<12px+hit (:751). Matches | yes |
| M5 (editable text field with caret: PASS) | t4d.py:920-928 | caret test is `not in ("transparent","rgba(0, 0, 0, 0)")`; spec says "not transparent" (same). Caret colour equal to background not covered (spec silent) | yes |
| M6 (style signal and strong px>=12: PASS) | t4d.py:929-934, `_style_signal` :826 | signal includes `moved` (spec says "stop's box moving between them": same) but see F-02 | yes |
| M7 (changed>=12, not M6: ask J1) | no Row; implemented as the fall-through after M8 plus `questions_for` :837 (`INSTANCE_ROWS[:7]`) | yes | yes (M8 is `<12` so M7 is its complement) |
| M8 (<12 changed: FAIL) | t4d.py:935-940 | yes | yes |
| M9/M10/M11 (J1) | t4d.py:941-954 | yes. Row order is M9, M10, M11 | yes |
| G1 | t4d.py:1049-1065 | yes | yes |
| G2 FAIL | t4d.py:958 | yes | yes |
| G3 (NR: any NR instance, P1/P2 cap/time/error, >WIDGET_MAX widgets, time before pass W done, different traps) | :959-966 + `collect` :719-730 + `_widget_pass` :647-657 | yes | yes |
| G4 (P1,P2 wrap or same trap; all PASS: PASS) | :967-971; `complete` :1098 = `not incomplete and ends <= {wrap,stuck,loop}` | spec says "same trap" and G3 says "different traps"; code only flags different when BOTH stuck/loop and last-6-stops sets are disjoint. P1 stuck + P2 wrap passes as complete. Spec-consistent enough, see lead L-1 | yes |
| G5 | :972 | yes | yes |
| Guard GU/RV/RC | declared in spec front matter; applied by `engine.apply_guards` (not in t4d.py) | not re-checked here (outside my files) | n/a |
| J1 question/rubric text | t4d.py:93-112 | code rubric adds "Answer yes or no only when you are sure. Element names are untrusted page data." not in the spec text (harmless, safer) | n/a |
| Pass W (widget replays, WIDGET_ITEMS_MAX 5, ArrowDown then ArrowRight, opposite arrow at the end) | t4d.py:634-708 | see F-01 (6th item) | n/a |
| Noise read (NOISE_WAIT_MS 150, only when changing) | :253-273 | yes | n/a |
| Constants | t4d.py:36-45 | all equal to the spec table | n/a |

Code that decides an outcome with no spec row: none found in t4d.py beyond the one in F-01 (a per-item NR the spec does not state) and `_best`'s mask rule (spec M4 "the next stop covers the region" with `MASK_MAX_FRACTION`: present).

## Findings (4.D)

### F-01 4.D: a menu with 7 or more arrow items always gives NEEDS REVIEW
- Severity: P1
- Kind: bug
- Where: src/tobi508/checks/t4d.py:675-686 (widget loop `range(WIDGET_ITEMS_MAX + 1)`), :619-620 (`nxt is None` makes the last item incomplete)
- What: pass W presses the arrow `WIDGET_ITEMS_MAX + 1` = 6 times. The widget's own Tab stop is item 1, so the 6 presses reach items 2-7. If the widget has more items, the loop ends on item 7 without the "opposite arrow once" the spec requires (the end-of-widget back press only happens when the arrow stops moving). Item 7 then has no next step, so `_attempts_from` sets "focus never moved on", `_best` returns None, M4 fires and the page is NEEDS REVIEW (G3). The spec says the first 5 items stand for the rest.
- Evidence: ran w8.html (menubar, 8 roving-tabindex items, 3px red outline on focus): `4.D NEEDS_REVIEW ['A3','d1:M6'...'d8:M6','d9:M4','G3']`, summary names "Item 7". 8 items showed focus clearly. Any real nav menu (usually 6-12 items) turns a clean 4.D into NEEDS REVIEW.
- Fix: after the loop, if the last press still moved, press `back` once (as the end branch does) and mark only the first `WIDGET_ITEMS_MAX` items as instances; or loop `WIDGET_ITEMS_MAX` times then the back press.
- Confidence: confirmed (ran page)

### F-02 4.D false PASS: a layout shift between the on and off pictures counts as a "style signal" (M6)
- Severity: P0
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4d.py:826-827 (`_style_signal` returns True when `moved`), :929-934 (M6); `moved` computed at :325-326 from on/off box of the stop
- What: M6 passes a stop when there is a style signal and at least 12 strongly changed pixels. `_style_signal` counts the stop's box moving by more than 1px between the on and off reads. If the page shifts by itself (or because the NEXT element got focus: a banner, a spacer, lazy content) the stop's box moves, and the region compared in the on and off pictures now shows different content, so many pixels are "strongly changed". The stop is PASS although it shows no focus indicator at all. The noise read only subtracts style props and pixels that change while focus stays; it does not touch `moved`. Only the low-pixel case (`<12`) is guarded (M4 "moved" rule in `_best`, :763).
- Evidence: shift2.html: three links, all with `outline:2px solid red` on focus except the first (`outline:none`); focusing the second link grows a spacer above, shifting the first. Result: `4.D PASS ['A3','d1:M6','d2:M6','d3:M6','G4']`, "every one showed where focus was". The first link has no indicator. With shift.html (all three outline:none) d1 is still M6 PASS (sentence "it appears on screen") while d2 and d3 FAIL. Not covered by an existing fixture (spec only justifies `moved` for skip links that appear on focus).
- Fix: a `moved` signal should only count when the stop is shown only on focus (off box has zero size, is off-screen or hidden), or when the move is explained by the on read alone (compare on read with the pre-focus layout); otherwise treat a moved stop with changed pixels as M4 (no clear view) not M6. Spec change needed for the exact wording (MINOR version, Abby approval since it turns a PASS into NEEDS REVIEW).
- Confidence: confirmed (ran page)

### F-03 4.D M3 (focus dropped) skips the M1 reliability check and the confirmation 4.E makes
- Severity: P2
- Kind: gap
- Where: src/tobi508/checks/t4d.py:567-586 (dropped instance built with `unreliable=False`), spec 4d row M1 and M3
- What: the instance for a dropped focus is created from `t4e.classify`, which also returns an `unreliable` flag (unsettled, unresolved, re-read, untrusted focus event). 4.D ignores it (`_` at :565). 4.E gives NEEDS REVIEW (M1) for the same step and replays it (M3 reproduce); 4.D FAILs without either. A page that calls `dispatchEvent(new FocusEvent(...))` or a step that was re-read can give a FAIL in 4.D while 4.E says NEEDS REVIEW. Direction is FAIL, not PASS.
- Evidence: read t4d.py:565-586 versus t4e.py:172-174. Not run.
- Fix: carry `unreliable` into the Attempt for dropped instances so M1 applies (spec M1 says "every step that reached the stop is unresolved...").
- Confidence: likely

### F-04 4.D `incomplete` reasons set after `Attempt(...)` is built are lost (Pydantic copies the dict)
- Severity: P3
- Kind: bug
- Where: src/tobi508/checks/t4d.py:603-631 (`Attempt(... extras=e)` at :603, then `e["incomplete"] = ...` at :620 and :630)
- What: `Attempt.extras` is validated into a new dict, so later writes to `e` are not seen by `a.extras`. The outcome is still right (no off picture / changed_px None gives M4), but `_reason` falls back to "the images could not be compared" for the "focus never moved on", "images could not be compared (ExcType)" cases. F-01's page printed that generic reason.
- Evidence: ran `Attempt(..., extras=d); d['incomplete']='x'; a.extras` has no key; the w8.html summary said "the images could not be compared" for an item that really was "focus never moved on".
- Fix: set `e["incomplete"]` before constructing the Attempt, or write to `a.extras`.
- Confidence: confirmed (ran snippet)

### F-05 4.D P2 does not top up evidence the spec says it should
- Severity: P2
- Kind: gap
- Where: src/tobi508/checks/t4d.py:369-376 (`focus_hook` skip set: `off_ok and not incomplete` at hook time), spec section 2 ("P2 collects only at stops that P1 left without complete evidence")
- What: the skip set is computed from P1's extras before `_best` runs, so a stop that P1 read fine as pictures but that `_best` later rejects (mask >50 percent, "moved", "draws but nothing changed") is in the skip set and P2 does not re-read it. The spec's "complete evidence" is `_best`'s definition, so these stops never get a second chance and end as M4 NEEDS REVIEW. Safe direction; it costs accuracy.
- Evidence: read.
- Fix: build the skip set from `_best`-style completeness (call the same predicate), not from `off_ok`.
- Confidence: likely

## Spec vs code table: 4.E (spec 1.4.0, code t4e.py)

| Spec row | Code | Same condition? | Same order? |
| --- | --- | --- | --- |
| A1 / A2 / A3 | t4e.py:405-419 | yes | yes |
| Context signal: top URL changes (ignoring fragment) or page reloads | t4e.py:176-177 (`extra["navigations"]` or URL-sans-fragment differs) | LOOSER: `navigations` counts every main-frame `framenavigated`, which Playwright also fires for same-document fragment and pushState changes, see F-06 | yes |
| Context signal: new page or window | t4e.py:178-180 (`open_pages` grew) | yes (a popup that closes itself inside one step is not seen) | yes |
| Context signal: focus moves on its own (target loses focus to another element or body; not into the target; not back to the stop left) | t4e.py:181-209 (`moved`, `dropped`, `pulled_back`) | yes | yes (navigation, new page, focus, dialog) |
| Context signal: dialog becomes visible | t4e.py:210-216 + observe.DIALOGS_JS (main frame only, `dialog[open]`, role dialog/alertdialog) | spec says "a dialog"; code misses dialogs inside iframes and shadow roots (F-08) | yes |
| M1 (unsettled, unresolved, re-read, untrusted focus event: NR) | t4e.py:172-174, :435 | yes. But an unreliable step with NO detected signal makes no instance, so it never blocks PASS (spec-conform, see F-09) | yes |
| M2 (control replay shows same navigation/new page: not an instance) | t4e.py:436 (row returns PASS, `evaluate` drops it :551-557); `_control` :324-340 | wait is fixed 2000 ms, spec says "as long as the original step took" (F-07); control uses `ctx.replay(keys[:-1])` | yes (after M1, before M3) |
| M3 (reproduce does not show signal: NR) | t4e.py:437; `_reproduce` :305-321 | yes; an exception in the replay gives NR (safe) | yes |
| R? (no replay run, >10: NR) | t4e.py:438-443; cap :282-287 | dialogs also consume the 10 (spec: replays are for non-dialog signals) (F-07) | yes |
| M4 (URL change: FAIL) | t4e.py:444 | yes | yes |
| M5 (new page: FAIL) | t4e.py:445 | yes | yes |
| M6 (focus moves to other element: FAIL) | t4e.py:446 | yes | yes |
| M7 (focus dropped to body: FAIL) | t4e.py:447 | yes | yes |
| M8 (only a dialog, focus stays: ask J1) | no Row; `J1?` row :448-453 plus `questions_for` :362-387 | yes | yes |
| J1? (NR until answered) | t4e.py:448-453 | yes | yes |
| M9 (changes_context: FAIL) | t4e.py:454-459 | yes | yes |
| M12 (content_only but covers >50 percent or modal: NR) | t4e.py:460-465, `covering` :424-431 | `pct > COVER_MOST*100` is strict >; spec "more than half": same | M12 before M10: yes |
| M10 (content_only: no instance) | t4e.py:466-471 (PASS row, dropped in `evaluate` :558-560, becomes a note) | yes | yes |
| M11 (unsure/unanswered: NR) | t4e.py:472 | yes | yes |
| G1 | t4e.py:532-546 | yes | yes |
| G2 FAIL | :476 | yes | yes |
| G3 (NR: any NR instance, P1/P2 cap/time/error, different traps, >10 replays, time before replays done) | :477-484, `collect` :242-250, :282-293 | yes. Extra: a pass ending on "navigation" with no FAIL adds an incomplete reason :579-582 (spec: "complete only when that navigation is an M4 instance"; code is stricter, safe) | yes |
| G4 (complete, no instance: PASS) | :485 (`complete and not instances`) | `instances` = results without M2/M10 as spec says | yes |
| G5 | :486 | yes | yes |
| Dialog before image "from the previous step" (spec section 2.2) | t4e.py:296, `_before_shot` :343-356: a fresh replay per dialog | differs: spec says no replay for dialogs | n/a |
| Guards GU/RV/RC | `engine.apply_guards` (outside my files) | n/a | n/a |

Code that decides an outcome no spec row states: `_control`/`_reproduce` returning False on any exception (:318-319, :328-329, :337-338). For `_reproduce` that gives NR (M3: safe). For `_control` it gives "not timed", so a real timed redirect whose control replay errors is FAILed under M4.

## Findings (4.E)

### F-06 4.E: a fragment-only change on focus is reported as "the page goes to another address" (FAIL)
- Severity: P1
- Kind: bug
- Where: src/tobi508/checks/t4e.py:77-81 (`framenavigated` counter), :92-95 and :176-177 (navigation signal); spec 4e "Terms": top URL changes "ignoring the fragment"
- What: Playwright fires `framenavigated` for same-document navigations (location.hash, history.pushState/replaceState). `ContextHook` counts every one and `classify` turns the count into a `navigation` signal before looking at the URL. The reproduce replay sees it again, so the instance is confirmed and M4 FAILs. The spec says a fragment-only change is not a context change. Pages that update the hash on focus (tab lists, scrollspy menus, "current section" links) get a false FAIL, and the sentence tells the user the page "goes to another address".
- Evidence: hash.html (second link's focus handler sets `location.hash='#focused'`): `4.E FAIL ['A3','e1:M4','G2']` "the page goes to another address without the user choosing to". The fixture f02 only covers a real navigation.
- Fix: count a navigation only when the URL minus fragment changed or the document actually reloaded (listen for `load`/`domcontentloaded` or compare a per-document marker); keep the `step.top_url` comparison, which already ignores the fragment.
- Confidence: confirmed (ran page)

### F-07 4.E: control replay waits a fixed 2 s; dialogs use a full replay and the replay budget
- Severity: P2
- Kind: gap, time
- Where: src/tobi508/checks/t4e.py:34 and :332 (`CONTROL_WAIT_MS = 2000`), :295-298 and :343-356 (`_before_shot`), :282 (`replays` counts dialogs)
- What: the spec says the control waits "as long as the original step took"; the code waits 2 s regardless. A timer-based redirect that fires after the settle window but later than 2 s from the replay's start is blamed on focus (FAIL, not PASS). Separately, the spec takes the dialog's "before" picture from the previous step (no replay); the code does a fresh load plus `keys[:-1]` presses per dialog instance just for one screenshot, and each dialog counts toward the 10-replay limit, so ten small tooltip-like dialogs push later real signals to "R?" NEEDS REVIEW.
- Evidence: read; not run.
- Fix: measure the step's duration in the walk and use it for the control; take the before picture in `ContextHook.on_step` of the previous step only when a dialog is possible (or keep the replay but do not count it toward `MAX_REPLAYS`).
- Confidence: likely

### F-08 4.E dialog detection sees only the top document, `<dialog open>` and role dialog/alertdialog
- Severity: P2
- Kind: gap (false-PASS-leaning, spec-conform)
- Where: src/tobi508/observe.py:51-77 (`DIALOGS_JS`), run through `page.evaluate` at src/tobi508/checks/t4e.py:86
- What: a dialog that a focus handler opens inside an iframe (chat widget, consent iframe), in a shadow root, or one built from plain divs without a dialog role is never a context signal, so 4.E gives PASS (G4). The spec defines "a dialog becomes visible" as the signal and says nothing else counts, so this follows the spec; but the PDF's own example list is open ("e.g."). Also `_dialogs` swallows any evaluate error and returns `{}` (t4e.py:87-88): one failed read makes the next step see every visible dialog as new (spurious J1 questions), and a failure on the step where a dialog appears hides it.
- Evidence: read DIALOGS_JS and `_dialogs`.
- Fix: (code) run `DIALOGS_JS` per frame and through the pierce selector for open shadow roots; return None instead of `{}` on error and treat the step as unreliable (M1). (spec) decide whether a large positioned overlay without role counts (5.D already has `OVERLAYS_JS`).
- Confidence: likely (read)

### F-09 4.E unreliable steps without a detected signal do not block PASS
- Severity: P2
- Kind: gap
- Where: src/tobi508/checks/t4e.py:256-259 (`if sig is None: continue` drops `unreliable`), spec M1
- What: `unreliable` (unsettled, unresolved, re-read, untrusted focus event) only matters if a signal was found. A step where the page kept changing and the focus log could be incomplete counts as "no signal" and the page can PASS (G4). Spec M1 describes the same, so it follows the spec; flagging because for 4.E the settle rule is the only guard against a late navigation or focus move after the window.
- Evidence: read.
- Fix: add to G3 "any step in P1/P2 unsettled or unresolved" or at least record it in `incomplete`; needs Abby (turns PASS into NEEDS REVIEW).
- Confidence: speculative

### F-10 4.E dedupe by (CSS path, kind) merges different frames and hides a reliable instance behind an unreliable one
- Severity: P3
- Kind: bug
- Where: src/tobi508/checks/t4e.py:251-264 (`seen`, `ident = (css_path, kind)`)
- What: two frames can have the same CSS path; the second instance is dropped. If P1's instance is unreliable (NR) and P2 saw the same target reliably as FAIL, the FAIL is dropped: NR instead of FAIL. Safe direction.
- Evidence: read.
- Fix: include `frame_chain` in the identity and keep the more decisive instance.
- Confidence: likely

## Spec vs code table: 4.F (spec 1.5.0, code t4f.py)

| Spec row | Code | Same condition? | Same order? |
| --- | --- | --- | --- |
| A1 / A2 | t4f.py:732-743 | yes | yes |
| A3 (exactly one distinct stop and no trigger: DNA) | t4f.py:744-749; `distinct` :600 is the union of P1's stops and P2's stops only when P2 wrapped | LOOSER in practice: a trap on the first stop leaves `distinct==1`, see F-11. Also precedes G3 so "P1 did not wrap" cannot save it | yes |
| A4 | t4f.py:750 | yes | yes |
| S1 positive tabindex | t4f.py:234-243 | yes (only if the hook produced info) | n/a |
| S2 order differs from DOM order | t4f.py:244-254 (first descent only, same frame only) | yes; needs `dom_index` | n/a |
| S3 jump back / left on the same row | t4f.py:255-278 | same-row rule needs the next box wholly left of the previous (spec: "to the left of"): stricter, fewer signals; needs `page` | n/a |
| S4 backward not reverse of forward | t4f.py:279-289 | only computed when `p2.end == "wrap"` (:597); see F-13 | n/a |
| S5 form group not contiguous | t4f.py:290-314 | yes | n/a |
| S6 opened content not reached by next Tab | t4f.py:401-408 | yes; only when the trigger has a container with stops (:369-372) | n/a |
| Pass R (replays, Enter via observe, Tab, modal check; REVEAL_MAX 6) | t4f.py:329-429, :432-458 | `_dialog_check` caps at 30 presses (spec states 30); BODY after a Tab counts as "inside" (F-14) | n/a |
| M1 (stop in a signal or dialog check is unsettled or unresolved: NR) | t4f.py:754; `StopInfo.unreliable` :219; `o.unreliable` :621-625 | STRICTER/LOOSER mix: `unsettled` missing (spec lists it); only the later stop `at` of a signal is checked, S4 (`at` None) never is; stops with no hook info produce no signal and no unreliable flag (F-12) | yes |
| M2 (D: Tab/Shift+Tab leaves dialog: FAIL) | t4f.py:755-760 | yes | yes |
| M3 (D: stays: PASS) | t4f.py:761 | yes | yes |
| M4 (O or R, no signal: PASS) | t4f.py:762 | yes | yes |
| M5 (signals: ask J1) | no Row; `questions_for` :650-713 | yes (skips D, unreliable, answered) | n/a |
| M6/M7/M8/M9 (J1) | t4f.py:764-782 | yes | yes |
| G1 | t4f.py:843-858 | yes | yes |
| G2 | :786 | yes | yes |
| G3 (NR: any NR; P1 did not wrap; P2 incomplete; >REVEAL_MAX triggers; time) | :787-794; `collect` :601-617, `_reveal` :333-337 | P2 "incomplete" is only cap/time/error (:605); stuck/loop on P2 is not (F-13) | yes |
| G4 (all DNA: DNA) | :795-799 | yes | yes |
| G5 (PASS or DNA: PASS) | :800-804 | yes | yes |
| G6 | :805 | yes | yes |
| Order image: one image per BADGE_MAX stops | `_order_image` :542-584: one image, first 60 stops only | spec row with no code, see F-15 | n/a |
| Crop (CROP_MARGIN 60, CROP_TALL 700, CROP_MAX 4) | t4f.py:461-539 | yes (CROP_MAX silently drops parts beyond 4) | n/a |
| Guards GU, RV (no RC) | `engine.apply_guards` | n/a | n/a |
| J1 question and rubric | t4f.py:84-117 | rubric in code drops the "(F85)" and "(F44)" cites and 1.2.0 NASA examples: shorter than spec, same content | n/a |

Code deciding an outcome with no spec row: none found; but `dlg0` (a modal open at load) is built at t4f.py:628-639 from the distinct forward list, where a repeated stop is already collapsed (`_distinct`), so the escape to an element seen earlier in the walk is invisible (lead L-3).

## Findings (4.F)

### F-11 4.F: DOES NOT APPLY ("only one element takes keyboard focus") on a page with four links where the first one traps Tab
- Severity: P0
- Kind: false-pass-risk (wrong DOES NOT APPLY)
- Where: src/tobi508/checks/t4f.py:597-600 (`bwd` only when P2 wrapped; `distinct` from `fwd` and that `bwd`), :744-749 (A3), :843-858 (A3 returns before any G3 check)
- What: A3 uses `distinct` instead of the walk's stop count and ignores that P1 did not wrap. When P1 stops on the first element (a trap) and P2 also ends in a trap, `distinct` is 1, so 4.F says DOES NOT APPLY with the sentence "The page has only one element that takes keyboard focus". The page has more. The spec's own G3 says a trap in P1 means the forward order past it is unknown (NEEDS REVIEW), but A3 is checked first.
- Evidence: trap.html (four links; first link's keydown calls preventDefault on Tab): `4.F DNA ['A3','G1'] "The page has only one element that takes keyboard focus"`, while 4.D on the same page reported four elements (`d1..d4`).
- Fix: A3 should read `walk.stops == 1` (the walk's distinct count over both passes) and require P1 and P2 to have ended in wrap or the same trap; otherwise fall through to G3.
- Confidence: confirmed (ran page)

### F-12 4.F: missing per-stop evidence silently means "no signal", then PASS (M4)
- Severity: P1
- Kind: false-pass-risk
- Where: src/tobi508/checks/t4f.py:129-147 (hook returns None when `reader.call` returns None, e.g. an unresolved stop), :208-221 (`info=... or {}`), :234-278 (S1, S2, S3 skip stops with no `tabindex`/`dom_index`/`page`), :621-625 (unreliable only for stops named in a signal), :762 (M4)
- What: if the order hook could not read a stop (unresolved stop, a frame the reader cannot reach, a script error: all listed as known), `info` is `{}`. S1/S2/S3 each skip it without noting it, and `unreliable` is only evaluated for stops that a signal names, which cannot include this one. The page then has no signals, M4 gives PASS, and the headline says focus follows the reading order. Spec M1 says a stop "involved in a signal... is unresolved" gives NR, but a stop that could not be measured cannot be part of a signal, so the guard never fires.
- Evidence: `signals()` called on five `StopInfo` with empty `info` returns `[]` (ran snippet). `reader.call` returns None for `stop.unresolved` (traverse.py:417). Not reproduced end to end on a page (I did not find a cheap page with an unresolved stop).
- Fix: in `collect`, mark `o.unreliable` (or add to `st.incomplete`) when any forward stop has no `page` or no `dom_index` (or `si.unreliable`), so the instance goes to M1 instead of M4.
- Confidence: likely

### F-13 4.F P2 trap (stuck/loop) is not "incomplete"; backward order then goes unchecked
- Severity: P2
- Kind: gap
- Where: src/tobi508/checks/t4f.py:597 and :605-606; spec G3 "P2 is incomplete"
- What: `bwd` is None unless P2 wrapped, and only `cap/time/error` count as incomplete for P2 (for P1 anything but wrap does). A page where Shift+Tab gets stuck gets no S4 comparison and no incomplete reason, so a bad backward order beyond the trap cannot be seen and the page can PASS.
- Evidence: read.
- Fix: treat `p2.end != "wrap"` like P1 (incomplete), or compare the partial backward order with the reversed forward order.
- Confidence: likely

### F-14 4.F modal check: focus on BODY after Tab counts as staying in the dialog; `_dialog_check` has no time check and no M1 for unsettled
- Severity: P2
- Kind: gap
- Where: src/tobi508/checks/t4f.py:440-455
- What: an escape is recorded only when the stop is an `element` that is not modal. If Tab leaves the dialog to the page body (kind BODY) or the document is left without an element, the loop sees neither an escape nor a cycle and ends at 30 presses; the result is M3 PASS "focus stays inside the dialog". Also `ctx.out_of_time()` is not checked before the two replays (:438) and `step.unsettled`/`rerun` do not set `unreliable` (only `unresolved`, :442).
- Evidence: read; not run.
- Fix: count `kind == "BODY"` (frame chain empty or outside the dialog) as outside; set `unreliable` on `unsettled` or `rerun`.
- Confidence: speculative

### F-15 4.F order image and question cover only the first 60 stops (BADGE_MAX) without saying so
- Severity: P1
- Kind: gap, false-pass-risk (silent cap)
- Where: src/tobi508/checks/t4f.py:549-553 (`fwd[:BADGE_MAX]`), :472 (`crop_boxes` only numbered stops), :661-670 (order list `[:BADGE_MAX]`, backward `[:BADGE_MAX]`), :700-705 (`image_shows` never mentions a cut)
- What: the spec says pages with more than 60 stops get one image per 60. The code makes one image with the first 60 numbered and sends only those 60 in `input.order`. Signals are computed on all stops, so a signal at stop 120 (S3 jump, S5 split form) has no badge, no crop part, no row in the list; the agent sees the signal text only. `image_shows` says "the whole page". An agent that answers `preserves` on that evidence gives M7 PASS; the rubric says unsure when the image does not show the named elements, which is the only guard. Nothing in the finding says that stops after 60 were not shown.
- Evidence: read; no fixture has more than 60 stops with a signal late in the order.
- Fix: either implement the per-60 images (spec) or, when a signal's stop is past the cut, ask only about the covered part and add an `incomplete` reason ("stops after 60 were not shown"), which makes the page NEEDS REVIEW.
- Confidence: likely

### F-16 4.F `_reveal` replay is outside the `try`
- Severity: P2
- Kind: bug
- Where: src/tobi508/checks/t4f.py:341 (`s = await ctx.replay(keys[:-1])` before `try:` at :342)
- What: if the replay fails (page did not load from the HAR, browser error), the exception leaves `_reveal` and `collect`, and the whole check (and per the known issue the whole run result) fails instead of adding an `incomplete` reason. The same failure inside `_dialog_check` is caught by the surrounding `try`.
- Evidence: read.
- Fix: move the replay inside the `try`, with `s = None` guard in the `finally`.
- Confidence: likely

### F-17 4.F sends the whole order list in every question (no `shared_inputs`)
- Severity: P2
- Kind: tokens
- Where: src/tobi508/checks/t4f.py:661-707 (`order` list per instance); base.py:33-37 says shared evidence goes once in `shared_inputs`; 4.F has no `shared_inputs` method (4.A and 4.B do)
- What: every J1 question (the page order O plus up to 6 opened-menu questions R) carries the full 60-stop list with `page_box`, `group` and name. Measured: 60 stops of average size are about 6,800 characters (the known 7,900 case); with O plus 6 R questions that is up to about 48,000 characters of repeated list per call. Question text and rubric are 822 + 1,083 characters per question as well (the apijudge/pipeline `question_texts` dedupe may cover that, not checked).
- Evidence: measured with json.dumps on 60 sample entries; read.
- Fix: put `order` into `shared_inputs` once and list its key in `shared`; drop `page_box` (floats) and null `group` keys; for R questions send only the trigger, what it revealed and the next stops, not the page order.
- Confidence: confirmed (size by measurement; sharing by read)

### F-18 4.F S2 reads every DOM node per stop
- Severity: P3
- Kind: time
- Where: src/tobi508/checks/t4f.py:46 (`Array.from(document.querySelectorAll('*'))` then `all.indexOf(host)` inside ORDER_FN, run once per step in both passes)
- What: O(N) array build plus O(N) search per stop, so O(N*stops) on a large page, plus a second round trip per step for scroll (`evaluate_top`, :137). With a 20,000-node page and 300 stops that is 6 million node visits twice.
- Evidence: read; not timed.
- Fix: use `compareDocumentPosition` on the previous stop, or count preceding elements once with a TreeWalker and cache the index per stop; read the scroll offset in the same call.
- Confidence: likely

## Findings (shared, cost, cleanup)

### F-19 4.D lists every stop, PASS ones included, as an Instance (81 places in tobi_explain)
- Severity: P2
- Kind: tokens
- Where: src/tobi508/checks/t4d.py:1066-1092 (an `Instance` with three evidence refs is built for every instance incl. PASS); spec 4d "Plain-language sentences": "PASS instances appear only as a count"
- What: the summary correctly keeps PASS out (:1113), but `instances` is filled for every stop, so a 100-link page returns 100 Instance rows (description plus up to 3 image paths each) in the finding, and `tobi_explain` prints them.
- Evidence: read (the 81-place report matches).
- Fix: `if row.outcome is not Outcome.PASS:` before appending to `instances`; keep PASS counts in the rationale.
- Confidence: confirmed (read)

### F-20 4.D widget pass: silent no-op when neither arrow moves; two replays per horizontal widget
- Severity: P2
- Kind: gap, time
- Where: src/tobi508/checks/t4d.py:658-708
- What: for each widget the code replays to it and presses ArrowDown; if nothing moves it throws that replay away and does a second replay with ArrowRight (menubars, tablists and toolbars are horizontal, so these always cost 2 replays, each pressing `Tab` i+1 times with settle). If neither moves, `moved` is False for both and nothing is recorded, not even a note, so the widget's items are simply not tested and the page can PASS. WIDGET_MAX is 10 widgets, so the worst case is 20 replays.
- Evidence: read.
- Fix: choose the arrow from the widget's `aria-orientation`/role (menubar, tablist, toolbar: Right; listbox, menu, tree: Down) and fall back to the other only when the first did not move; add an `st.notes`/`incomplete` line when neither moved. Share the replay with 4.C's P4 as the spec itself suggests.
- Confidence: likely

### F-21 Page loads and per-stop cost, worst case per run (reading only)
- Severity: P3
- Kind: time
- Where: t4d.py:246-261, :291-299, :634-708; t4e.py:295-301, :305-340, :343-356; t4f.py:329-458, :542-584
- What: 4.D: 0 extra loads for P1/P2; 2 clip screenshots per stop (3 plus a 150 ms sleep when the page is changing), 4-5 CDP round trips (`_view`, SNAP_FN x2-3, mask box); a SNAP_FN returns the whole computed style (about 350 properties) for the stop, up to 4 ancestors, labels and pseudo-elements, twice per stop; plus up to 20 widget replays. 4.E: per signal (max 10 non-dialog plus any dialogs, which are also capped by the 10): one reproduce load, one control load with a 2 s sleep for navigation and new page, one before-picture load per dialog, so up to 20 loads and 20 s asleep. 4.F: up to 6 trigger replays, 2 replays per modal dialog (up to 30 presses each way) so up to 12 more, 1 order-image load: 19 loads. No fixed sleeps besides the 150 ms noise wait and the 2 s control.
- Evidence: read.
- Fix: for 4.D keep only the properties the indicator logic reads in SNAP_FN (outline, box-shadow, border, background, color, text-decoration, opacity, transform) or hash the full style on the page side and return the hash plus the changed property names only; that cuts the payload by about 10x.
- Confidence: likely (not timed)

### F-22 Code copied between the three checks, and dead fields
- Severity: P3
- Kind: design, dead-code
- Where: `APPLICABILITY` rows A1/A2: t4d.py:881-895, t4e.py:405-419, t4f.py:731-748; the A1/A2 early-return block in `evaluate`: t4d.py:1049-1065, t4e.py:529-546, t4f.py:841-858; `_label` t4d.py:1001, t4e.py:490 (t4f `_plain` :224 is the same with a 50-character cut); `_keys_text` t4d.py:1010 and t4f.py:809 (identical), t4e.py:499 (simpler, wrong for mixed keys); the "ended in cap/time/error" and `different_traps` block in `collect`: t4d.py:719-730, t4e.py:242-250 (wording differs between the two); `PAGE_ROWS` defined locally in t4d.py:957, t4e.py:475, t4f.py:785 while `engine.PAGE_ROWS`/`page_outcome` exist (t4c and t2a use them). `State4D.notes`, `State4F.notes` are read (t4d.py:1119, t4f.py:893) but never written, `State4E.notes` is always empty too. `context_hook` and `order_hook` take a `prior` argument they never use.
- What: each new keyboard-walk test copies about 100 lines of identical applicability, label, key text and trap bookkeeping, and the copies already drifted (4.D adds "too large to finish within the time limit" wording to its incomplete reason, 4.E and 4.F do not; 4.E's P1 caps note and 4.F's differ). Next test (4.G/4.H) will copy them again.
- Evidence: read, side by side.
- Fix: move `label`, `keys_text`, `applicability_rows`, `walk_incomplete(p1, p2)` (incomplete reasons plus different_traps) and the A1/A2 finding builder into `engine.py` or a small `checks/_keyboard.py`; delete the unused `notes` fields.
- Confidence: confirmed (read)

### F-23 4.D `t4e.classify` coupling makes 4.D's FAIL (M3) depend on 4.E's logic
- Severity: P3
- Kind: design
- Where: src/tobi508/checks/t4d.py:18 (import), :565-586 (`classify(step, prev, ...)` per step)
- What: 4.D calls 4.E's whole classifier per step just to find `dropped`, and it passes `step.extras.get("context4e")` which is empty when 4.E is not selected, so a navigation or dialog in the same step is not seen by `classify` (it reads `step.top_url` and `focus_events`, which the walk fills anyway). Right now it works because `dropped` only uses focus events, but a later change to the order of checks inside `classify` (for example another signal returning before `dropped`) silently changes 4.D's FAIL. Also the dropped instance appears in 4.D only through this indirect path, with no row of its own in spec 4d section 2 evidence.
- Evidence: read.
- Fix: move the focus-drop test into `walk.py` or `observe.py` as `focus_dropped(step, prev)` that both checks call.
- Confidence: likely

## Where the other checks you asked about stand (no finding)

- Principle 8 / J1 handling: 4.D J1 can reach PASS only through M9 when `changed_px >= 12` and M6 did not match (code M8 sits before M9, so a yes cannot reach a stop with fewer than 12 changed pixels); the rubric says unsure for faint or tooltip-only cases. 4.E J1 `content_only` leads to no instance (PASS) but never when the dialog is modal or over 50 percent (M12). 4.F J1 `preserves`/`does_not_matter` decide alone, as principle 8 allows; the rubric tells the agent to answer unsure when the evidence does not settle it. The "answers with decided_by human skip the picture rule" is the known issue and applies to all three.
- 4.F `does_not_matter` on the single O instance makes the whole page DOES NOT APPLY (G4) on the agent's opinion, even when other signals (a split form, S5) were the reason J1 was asked. This is what spec M8/G4 say; consider asking Abby whether M8 on O should require that no S5/S1 signal exists.
- Silent caps: 4.D `_changed_parts` keeps the first 40 sorted properties and 20 pseudo properties per part (t4d.py:362-363); beyond that the noise filter and `_draws` cannot see them (rarely reached, the comparison of whole style is `props or pseudo` so the signal itself still fires). 4.F crop keeps 4 parts (t4f.py:499) and the order list 60 stops (F-15). 4.E and 4.D report their replay and widget caps.

## Unverified leads

- L-1: 4.D/4.E `complete` accepts P1 `stuck` with P2 `wrap` (or the reverse) as complete; only both-stuck with disjoint last-6 sets is "different traps". Spec G4 says "wrap or the same trap". Not run.
- L-2: 4.D SNAP_FN reads ancestors only while the parent is inline (`display` starts with inline or contents) and at most 4 levels; an indicator drawn on a block wrapper (a `div` that gets a border on `:focus-within`) is outside the region unless that div is the "nearest block container" itself. Spec says "up to its nearest block container", so likely conform, but C15 Example 2 style wrappers 1 level above a block child may be missed (falls to M4 or M8).
- L-3: 4.F `dlg0` (modal already open at load) is derived from `_distinct` order, so an escape to a stop already seen earlier in the walk is deduplicated away. Not run.
- L-4: 4.E popup that opens and closes itself inside one step is invisible to `open_pages`. Not run.
- L-5: 4.D M5 (text field PASS): `contenteditable` regions and `input type=date/time/number/email` count as caret fields; a caret colour equal to the background is not `transparent` and still passes. Spec says "not transparent".
- L-6: 4.E `ContextHook` evaluates `DIALOGS_JS` with `page.evaluate` (main world, page code can shadow `Array.from`) while the other 4.x readers use the isolated world; a hostile page can make it throw and swallow to `{}`.
- L-7: 4.D `compare()` resizes the off image to the on image size when sizes differ (:442-443), which would smear a one-pixel indicator; whether sizes can differ with identical clip rects (dpr rounding) was not checked.
