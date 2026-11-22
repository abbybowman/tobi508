# Focus, the keyboard walk and its probes

How the walk reads the page, and what cost time in 4.C and 4.D. Read before touching `traverse.py`, `walk.py` or a check's replays.

## Read focus through CDP, not page script

**Problem.** A page can override `document.activeElement` (or move focus in a
blur handler), so reading focus from page script can be spoofed or stale.

**What we do.** `traverse.FocusReader` reads the focused node through CDP in an
isolated world, follows it into in- and out-of-process iframes and open and
closed shadow roots, and takes role and name from Chrome's accessibility tree.
Tested by `tests/test_traverse.py::test_page_cannot_spoof_focus`.

**Identity across loads.** CDP backend node IDs change on every load. Within a
load a stop is `(frame ID, backend node ID)`; across loads (probes, the two
passes) stops match by frame chain plus CSS path (`Stop.path_key`).

**Browser facts that shaped rules** (Linux Chromium; the same on Windows
Chrome 156, 2026-11-02: `specs/rules/_browser-checks.md`, 4.C):

- Script `focus()` pulls keyboard focus back even from the browser toolbar
  (V15), so a refocus-on-blur pair cycles in both directions.
- Tab skips an iframe with `tabindex=-1` and everything inside it (V9).

**Every focus read that decides an outcome goes through the isolated world.**
9.A first asked `page.evaluate` for `document.activeElement` after a skip
link (code review, 2026-11-02). A page that overrides that getter turned a
broken skip link into a PASS. The fix was one line: run the same script with
`s.traversal.reader.evaluate_top(...)`, where the page's getter does not
apply. That was simpler than resolving the CDP stop's path, which breaks at
shadow roots ([focus-and-walk.md](focus-and-walk.md)).
Fixture `9x/b7-fake-focus.html`. Its first version still came out FAIL on
the old code, because the next-Tab check (M6) caught it. To show a false
PASS, a fixture has to get past every later row too (no stop after the faked
landing). Run a new fixture against the old code once to see it fail.

## Focus events in Chrome: what the log does and doesn't show

**Blur inside a focus handler.** When an element calls `this.blur()` in its
own focus handler (F55), Chrome fires no `focusin` for it. The log shows only
the previous element's `focusout`, whose `relatedTarget` names the element
focus was going to. 4.E takes the target from there (`t4e.classify`).

**What the log records** (`traverse.INIT_JS`, every frame, before page
scripts): type, time, tag, id, `isTrusted`, a short element path, and for
`focusout` the `relatedTarget` path and whether it is inside the element
losing focus (a widget handing focus to its own item). Untrusted (synthetic)
events make a step unreliable.

**Fixture trap: `id="close"`.** An element id becomes a global name, but
built-ins win: `close` is `window.close`, so `close.focus()` silently does
nothing. Use `document.getElementById(...)` in fixture scripts.

## A fresh browser context per load, not just a fresh page

**Problem.** Reusing one context and opening a new page per probe looks like a
cheap speedup. But pages keep state in localStorage, sessionStorage and
cookies. A probe that presses Enter on "Accept" in a cookie banner can store
that, and the next "fresh" load then has no banner: the evidence differs
between probes of the same frozen page.

**What we do.** `traverse.Session.close()` closes the whole context, and the
opener builds a new context with the HAR replay routes for every load.

**Where the time really went** (spec 1.4.0 → 1.5.0, same code otherwise):
probes that continued to the end of the page, P5/P4 sweeps, Enter and Space
on every member, a 300 ms focus window plus a 300 ms DOM window per press, and
a screenshot per press. Cutting those took F04 from 71 s to 9.5 s and F32 from
80 s to 25 s; context creation was not the bottleneck.

## Element paths must be unique; positions must be top-level

**Paths.** A path built from tag names alone (`form > fieldset`) is the same
for two sibling fieldsets or eight `<details>`, so groups merged and the
wrong container was checked (4.F F02, F13). Paths now add
`:nth-of-type(n)` where a tag repeats and stop at an id (escaped with
`CSS.escape`). Stop identity across loads still uses the CDP reader's
`Stop.path_key`.

**Coordinates.** `getBoundingClientRect()` inside an iframe is relative to the
frame. Positions for comparing order (4.F) must come from the walk's
`Stop.bounding_box`, which the reader already converts to top-level viewport
coordinates, plus the top page's scroll. Using the frame's own coordinates
made a button inside a frame look like it sat above the page.

## Shadow roots: `contains()` stops at the boundary

**Problem.** 4.A asks whether a pointer target is "reached": a stop, inside a
stop, or around one. `a.contains(b)` is false when `b` is in `a`'s shadow
root, and `document.querySelector("#host #btn")` finds nothing for a path
that crosses a shadow boundary (the walk writes it as a lone space). The
first version fell back to the host and called the shadow button on
`no_trap.html` unreachable, sending a working page to a person.

**What we do.** `t4a._COMMON_JS`: `find()` resolves a path part by part
through each `shadowRoot`; `deepContains()` walks up through `parentNode`
or `host`. Covered by `test_fixtures_4a.py::test_shadow_and_frame_stops_are_reached`.
Any new scan that matches the walk's paths should reuse these helpers and
`traverse.PATH_JS`, which builds the walk's own paths.

## CDP lists page listeners only from the page's own world

**What cost time.** 4.A passed a video row that plays on a mouse click
(CILab, round 2). The row's click handler was added by jQuery, and every
listener lookup returned nothing, so the row was never a mouse target.

**Why.** `DOMDebugger.getEventListeners` on an object from TOBI's isolated
world returns only that world's listeners: 0 on CILab. The same call on
`document` evaluated in the main world (no `contextId`, `depth: -1`)
returned 21. This is the CDP's behaviour, not jQuery's: any library, and
`el.onclick = fn`, show up from the main world.

**Do.** Read listeners from the main world, and map them to nodes by
backend node ID. Probe a fresh Playwright page with `route_from_har` on the
recording to see the difference in a minute.

**Check on any new listener-based signal.** Run it on a page whose handler
is added by a script, not an attribute (CILab's frozen copy).

## An exit check must accept reaching the end of the page

**Problem.** Spec 1.5.0 calls a probe an exit when it reaches a stop outside
the trap and the next 3 presses do not return to it. On a 3-element page,
3 more Tabs go past the end (OUT), wrap to the top and land on the trap again,
so a real exit (F16: Escape, then Tab, leaves a textarea) read as a FAIL.

**What we do.** Reaching OUT during the check confirms the exit: traversal got
past the rest of the page. OUT before any outside stop still does not count.
`t4c.Collector.probe`; covered by the F16 outcome test.

**Second lesson (ACT b92b5214).** "Returns to a trap member" is also wrong as
the test: after Ctrl+M switches the trap off, Shift+Tab walks back through the
former trap's buttons, which are now free. The check now asks whether the trap
*happens again* (stuck, or looping only on its own stops) within
2 x trap size + 3 presses.

## Pages that keep changing: animation is not a focus indicator

**Problem.** 4.D compares an image taken while an element has focus with one
taken after focus moves on. On a page with a slideshow or animation, pixels
and styles change between the two for reasons unrelated to focus, which could
read as an indicator (a false PASS). Such pages also never "settle", so
treating unsettled steps as unreliable sent every element to a person.

**What we do.** While the element has focus, if the page is changing (the step
did not settle, the DOM changed, or `document.getAnimations()` is not empty),
a second image and style read are taken 150 ms later. Whatever differs
between the two focused reads is noise and is left out of the comparison.
Unsettled steps are no longer unreliable by themselves. Static pages skip the
second read, which keeps 4.D near 0.2 s per element. Covered by 4.D F06.

## Widget items: roving tabindex and aria-activedescendant

**Why they need arrow keys.** Items inside menubars, tab lists, listboxes and
grids get focus from arrow keys, not Tab, so the shared walk reaches only one
item per widget. With aria-activedescendant, DOM focus stays on the container
and the "focused" item is the one the attribute names (WAI-ARIA 1.2: it "is
treated as having keyboard focus"; the author styles it). 4.D's widget pass W
arrows through up to 5 items.

**Lessons.**
- Mask the *next subject's* box (the next active item), not the element with
  DOM focus: for an active-descendant listbox that is the whole list, which
  masked almost everything.
- At the end of a widget the arrow stops moving, so the last item never gets
  its "after" read; press the opposite arrow once.
- Try ArrowDown, then ArrowRight if nothing moved, instead of guessing the
  orientation from the role.

**Native radio groups (4.A 1.19.0, 1.20.0, #136).** Radio buttons with the
same `name` in one form are one group with no role on any element: Tab
enters it once (at its checked radio, else its first; Shift+Tab at its
last) and the arrow keys move *and check*. So the walk reaches one or two
of a group and 4.A sent the rest to the judge as "works with a mouse but
can't be reached" (round 1's "Last Month" filter was judged FAIL). Group
them by `name` and form owner and probe them like a widget, from the
radio Tab reached. Lessons:
- **Shift+Tab lands on the last radio** of a group with none checked, so
  P2 reaches it: a fixture with three radios has one candidate, not two
  (F41).
- **A change can make the page leave.** Round 2's search filters submit
  their form on `change`, so ArrowDown checks the next radio and the page
  reloads before focus can be read, and a replay cannot follow it (the
  new address is not recorded). Record the radio a press selects through
  a CDP binding (`Runtime.addBinding`; its calls arrive over CDP even as
  the page leaves), one press per fresh replay (`t4a._radio_probe`, F43).
  The key's verdict there: 4.A passes (the arrows choose each filter),
  5.D fails (the reload). A tester reads the reload as an On Input
  problem, not a keyboard one.
- **Read the page's own markup before guessing why a probe failed:** the
  frozen page's HAR (`frozen/pages/NNN.har.zip`, unzip it into a scratch
  folder) had `class="... submitonchange"` and the script that submits.

## Where a stop is on the page (4.F 1.11.0)

**Problem.** Step 23's rerun gave three false FAILs on round 2's pages,
each a page where the judge had been unsure the run before. The signals
it was shown were measurement errors, a different few each run:
- **A box and a scroll read in two calls.** The walk's box comes with the
  step; the hook read `scrollX, scrollY` in a later call. Bootstrap sets
  `scroll-behavior: smooth`, so focus starts a scroll that runs on between
  the two reads: a date field was placed below the next row, a card's
  copy button below its Download button. Worse under load.
- **A box that scrolls by itself** (`max-height`, `overflow: auto`): focus
  scrolls it, so its later links sit above earlier ones on the screen.
- **A script-made id** (`#html5_media_<random>`): P1 and P2 load the page
  apart, so path keys with that id never match and S4 said Shift+Tab was
  not the reverse of Tab when it was exactly that.

**What we do.** Read the box and the scroll in one `evaluate` (ORDER_FN's
own `page`); place a stop in a scroll box by where it lies in the box's
content against its neighbours in the box, and by the box's own place
against everything else; for S4, treat an id found in only one walk as
the same. Fixtures 4f/f26 to f29 (f29: steps out of sequence inside a
scroll box still FAIL).

**A scroll box inside a frame (4.F 1.15.1, #136).** A stop in a frame gets
its `page` box from the walk, already top-level; the hook then moved that
box onto the page but left its scroll box (`scroller_page`) where it sits
in the frame. On round 2's 5340 timeline (a frame 396 px down) the panel's
button read as above the panel: S3, and a FAIL with the judge. Move every
box a frame's stop carries by the same offset as the stop (F35). **How it
was found:** the S3's two stops were parent and child, the child "above";
`page` y 646 against `scroller_page` y 250, and 646 - 250 was the frame's
offset. When a signal names a jump that cannot be, print every box of
both stops and look for two coordinate origins.

**How to find it next time.** Run the page alone twice with no judge
(signals only) and diff the signal lists; a signal that comes and goes on
a replay is a measurement, not the page. Compare the two walks by path
key before believing S4.
