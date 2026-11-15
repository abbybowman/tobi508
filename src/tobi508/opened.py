"""Opening everything, phase 2 (step 6g): a Tab walk through what each menu,
tab or section opened, made once per page on reveal.py's opening and shared
by the tests that read it (4.C for traps, 4.E for changes on focus). Facts
only; no outcome is decided here (CLAUDE.md principle 2): the rows are in
the specs.

The *opened content* of a trigger is the elements that take keyboard focus
after it was opened and did not before (reveal.py's `new`, focusable ones).
From the opened state, with focus on the trigger, Tab is pressed with P1's
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

import time

from pydantic import BaseModel, Field

from tobi508.models import Step
from tobi508.traverse import Session, detect_p1_end, drive

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
    reached: list[str] = Field(default_factory=list)
    end: str = ""  # left | stuck | loop | navigation | cap | time | error
    trap: list[str] = Field(default_factory=list)  # stop keys of a trap event
    steps: list[Step] = Field(default_factory=list)
    error: str | None = None
    seconds: float = 0.0

    @property
    def complete(self) -> bool:
        """Every opened element was reached (facts; the guard reads it)."""
        return bool(self.opened) and set(self.opened) <= set(self.reached)


async def walk(
    s: Session,
    new_focusable: list[str],
    trigger_key: str,
    by: str,
    same_load: bool,
    deadline: float | None,
) -> Walked:
    """Tab through the opened content from the trigger (module docstring)."""
    t0 = time.monotonic()
    targets = sorted({stop_key(k) for k in new_focusable})
    w = Walked(by=by, same_load=same_load, opened=targets)
    inside = set(targets)

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
        end, trap, own = await drive(
            s, "Tab", min(2 * len(targets) + 3, WALK_CAP_MAX), left, deadline
        )
        w.end, w.trap, w.steps = end, list(trap), list(own)
        w.reached = sorted({x.stop.path_key for x in own if x.stop.path_key in inside})
    except Exception as exc:
        w.end, w.error = "error", f"{type(exc).__name__}: {exc}"[:300]
    w.seconds = round(time.monotonic() - t0, 2)
    return w
