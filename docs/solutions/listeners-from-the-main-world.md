# CDP lists page listeners only from the page's own world

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
