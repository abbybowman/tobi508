"""Opening everything, phase 2: a Tab walk through what each menu,
tab or section opened, made once per page on reveal.py's opening and shared
by the tests that read it (4.C for traps, 4.E for changes on focus, 4.D for
focus pictures, with its own walk extra on these loads; 4.D 1.13.0; 5.D for
the fields to fill, pass FO, 5.D 1.13.0). Facts
only; no outcome is decided here (CLAUDE.md principle 2): the rows are in
the specs.

The *opened content* of a trigger is the elements that take keyboard focus
after it was opened and did not before (reveal.py's `new`, focusable ones).
From the opened state, with focus where the opening left it (the trigger, or
inside a dialog it opened), Tab is pressed with P1's
stuck and loop rules (4.C spec section 2) until focus reaches a stop that is
neither in the opened content nor the trigger (the walk *left* it), OUT, a
navigation or new page, a trap event, the cap (2 x opened elements + 3, at
most 60) or the run's deadline. The walk runs on the load reveal.py opened
the trigger in when nothing reads that load after it (no ANDI read for
5.A-5.C), and on a fresh load opened the same way otherwise: ANDI changes
the page, and Tab moves focus and often closes a menu, so neither can follow
the other on one load. Either way it is walked however it was opened (Enter,
or a click when Enter showed nothing), and the record says which.
"""

from __future__ import annotations

import asyncio
import json
import time

from pydantic import BaseModel, Field

from tobi508.jslib import JSLIB
from tobi508.models import Step
from tobi508.traverse import Session, detect_p1_end, drive, settle

WALK_CAP_MAX = 60


def stop_key(reveal_key: str) -> str:
    """reveal.py's element key ("chain|path") as a stop's `path_key`."""
    chain, _, path = reveal_key.partition("|")
    return f"{chain} >> {path}" if chain else path


class Walked(BaseModel):
    """One trigger's walk through what it opened."""

    by: str = ""  # how it was opened: "Enter" or "a click"
    same_load: bool = False  # walked on reveal.py's own load
    opened: list[str] = Field(default_factory=list)  # stop keys to reach
    # Shown by the opening but behind the modal dialog it opened: Tab is not
    # expected to reach them while the dialog is open (step 6g, Abby
    # 2026-11-15; as step 6d's walk coverage leaves out what a modal covers).
    behind_modal: list[str] = Field(default_factory=list)
    reached: list[str] = Field(default_factory=list)
    end: str = ""  # left | stuck | loop | navigation | cap | time | error
    trap: list[str] = Field(default_factory=list)  # stop keys of a trap event
    steps: list[Step] = Field(default_factory=list)
    error: str | None = None
    seconds: float = 0.0
    # reveal.py's keys for what opened ("chain|path"), so the walk can be
    # made again on a fresh load (4.C's confirmation and probes).
    source_all: list[str] = Field(default_factory=list)
    source_focusable: list[str] = Field(default_factory=list)

    @property
    def complete(self) -> bool:
        """Every opened element Tab is expected to reach was reached (facts;
        guard RC reads it). One behind an open modal dialog is not expected."""
        return self.end != "error" and set(self.opened) <= set(self.reached)


# Which of the given top-document paths are inside the open modal dialog, in
# 4.C's terms (Terms, modal dialog): a <dialog> opened with showModal, or role
# dialog or alertdialog with aria-modal="true". null when none is open.
MODAL_FN = (
    "(() => {"
    + JSLIB
    + """
  const m = document.querySelector('dialog:modal') ||
    Array.from(document.querySelectorAll('[role=dialog][aria-modal=true],[role=alertdialog][aria-modal=true]'))
      .find((e) => J.rendered(e));
  if (!m) return null;
  return PATHS.map((p) => { const e = J.find(p); if (!e) return false;
    for (let n = e; n; n = n.parentNode || n.host || null) if (n === m) return true;
    return false; });
})()"""
)


FOCUS_STILL_MS = 300  # focus unchanged this long before the first Tab
FOCUS_WAIT_MS = 1500  # at most this long


async def focus_still(s: Session, quiet_ms: int) -> None:
    """Settle, then wait until focus stops moving: a dialog can move focus
    to itself after its opening animation (round 2's Search page: the first
    Tab, pressed at once, landed on the dialog's own box)."""
    await settle(s.page, quiet_ms)
    last, waited = None, 0
    while waited < FOCUS_WAIT_MS:
        here, _ = await s.traversal.reader.read()
        if here.path_key == last:
            break
        last = here.path_key
        await asyncio.sleep(FOCUS_STILL_MS / 1000)
        waited += FOCUS_STILL_MS
    await s.traversal.resync()
    await s.traversal.forget_focus_events()
    # Walk extras that keep state (4.E's open dialogs) start from the opened
    # state: what the opening showed is not the first Tab's doing.
    for h in s.traversal.hooks:
        if hasattr(h, "rebase"):
            await h.rebase(s.traversal)


async def walk(
    s: Session,
    new_all: list[str],
    new_focusable: list[str],
    trigger_key: str,
    by: str,
    same_load: bool,
    deadline: float | None,
    quiet_ms: int,
) -> Walked:
    """Tab through the opened content from where the opening left focus
    (module docstring)."""
    t0 = time.monotonic()
    targets = sorted({stop_key(k) for k in new_focusable})
    w = Walked(
        by=by,
        same_load=same_load,
        opened=targets,
        source_all=list(new_all),
        source_focusable=list(new_focusable),
    )
    # Inside: anything that opened, a dialog's own box too; to reach: the
    # new elements that take focus.
    inside = set(targets) | {stop_key(k) for k in new_all}

    def left(own: list[Step], first: str | None):
        st = own[-1].stop
        if st.kind == "OUT":
            return "left", []
        if (
            st.kind == "element"
            and st.path_key not in inside
            and (st.path_key != trigger_key)
        ):
            return "left", []
        return detect_p1_end(own, None)

    try:
        await focus_still(s, quiet_ms)
        top = [k for k in targets if " >> " not in k]
        if top:
            inside_modal = await s.traversal.reader.evaluate_top(
                MODAL_FN.replace("PATHS", json.dumps(top))
            )
            if inside_modal is not None:
                w.behind_modal = [k for k, i in zip(top, inside_modal) if not i]
                w.opened = [k for k in targets if k not in set(w.behind_modal)]
        # Where the opening left focus (a menu's first item, say) is reached:
        # the walk starts there.
        here, _ = await s.traversal.reader.read()
        start = here.path_key if here.kind == "element" else None
        end, trap, own = await drive(
            s, "Tab", min(2 * len(targets) + 3, WALK_CAP_MAX), left, deadline
        )
        w.end, w.trap, w.steps = end, list(trap), list(own)
        w.reached = sorted(
            {x.stop.path_key for x in own if x.stop.path_key in inside}
            | ({start} & set(targets))
        )
    except Exception as exc:
        w.end, w.error = "error", f"{type(exc).__name__}: {exc}"[:300]
    w.seconds = round(time.monotonic() - t0, 2)
    return w
