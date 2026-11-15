"""The shared keyboard walk: one forward (Tab) and one backward (Shift+Tab)
pass per page, each from a fresh load of the recorded page.

TT 5.1.3 chains its keyboard tests: 4.D "Continue from Test 4.C", 4.E
"Continue from Test 4.D" (p. 22) and 4.F "Use the tab key to move focus through
the page" (p. 23). So the walk runs once per page and every check reads it.
Collect once, evaluate many. The walk records facts only; what a stop means
for an outcome is decided by each check's rules module.

Pass end conditions, the press cap and the settle rule are defined in the 4.C
spec (section 2), which the other keyboard specs use by reference.

A trap event ends a pass only when a second pass of the same key, from a
fresh load, ends in the same trap (4.C 1.9.0). Some pages differ from load to
load: Artemis III's survey dialog opens on about 1 load in 10, takes focus and
keeps it, and ended P1 after 9-13 presses on those loads while every other
walk and replay saw a page without it (docs/solutions/trap-seen-once.md).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from tobi508.models import PassResult, Stop
from tobi508.traverse import NewPage, Pace, StepHook, run_pass

TRAP_ENDS = ("stuck", "loop")


class KeyboardWalk(BaseModel):
    p1: PassResult  # forward, Tab
    p2: PassResult  # backward, Shift+Tab

    @property
    def stops(self) -> int:
        return sum(
            s.stop.kind == "element" for p in (self.p1, self.p2) for s in p.steps
        )

    @property
    def inventory(self) -> int:
        return max(self.p1.inventory, self.p2.inventory)


# A check's walk extras: called once per pass with the pass name ("P1" or
# "P2") and P1's result when making P2's hooks (so P2 can top up only what P1
# missed). Returns a fresh hook for that pass.
ExtraFactory = Callable[[str, "PassResult | None"], StepHook]


async def walk_page(
    new_page: NewPage,
    quiet_ms: int,
    deadline: float | None,
    shots: Path | None = None,
    rel: Path | None = None,
    extras: list[ExtraFactory] | None = None,
    pace: Pace | None = None,
) -> KeyboardWalk:
    """P1 then P2. `extras` are the union of the selected checks' walk extras;
    running 4.C alone passes none. With `pace`, P1 raises WalkTooLong as soon
    as its pace shows the walk cannot finish before the deadline."""
    extras = extras or []
    p1 = await _confirmed(
        "P1",
        new_page,
        "Tab",
        quiet_ms,
        deadline,
        shots,
        rel,
        lambda: [f("P1", None) for f in extras],
        pace,
    )
    p2 = await _confirmed(
        "P2",
        new_page,
        "Shift+Tab",
        quiet_ms,
        deadline,
        shots,
        rel,
        lambda: [f("P2", p1) for f in extras],
        None,
    )
    return KeyboardWalk(p1=p1, p2=p2)


def trap_paths(p: PassResult) -> set[str]:
    """The trap's stops by frame chain plus CSS path: stop keys hold node IDs,
    which change on every load (4.C spec section 2, Stop identity)."""
    return {s.stop.path_key for s in p.steps if s.stop.key in set(p.trap)}


async def _confirmed(
    name: str,
    new_page: NewPage,
    key: str,
    quiet_ms: int,
    deadline: float | None,
    shots: Path | None,
    rel: Path | None,
    hooks: Callable[[], list[StepHook]],
    pace: Pace | None,
) -> PassResult:
    """One pass; when it ends in a trap event, a second pass from a fresh load
    (4.C spec section 2, 1.9.0). The same trap again: the first pass stands,
    confirmed. Anything else: the second pass stands, carrying the first as
    `unrepeated` (4.C row M1 leaves that trap for a person). Each pass gets
    fresh hooks: walk extras keep state per pass."""
    first = await run_pass(
        name, new_page, key, quiet_ms, deadline, shots, rel, hooks=hooks(), pace=pace
    )
    if first.end not in TRAP_ENDS:
        return first
    # The time-limit pace starts again with this pass: the first pass may
    # have stopped after a few presses.
    again_pace = Pace(pace.deadline) if pace is not None else None
    again = await run_pass(
        name,
        new_page,
        key,
        quiet_ms,
        deadline,
        shots,
        rel,
        hooks=hooks(),
        pace=again_pace,
        shot_label=f"{name}-again",
    )
    if again.end == first.end and trap_paths(again) == trap_paths(first):
        return first.model_copy(update={"confirmed": True})
    return again.model_copy(update={"unrepeated": first})


# --- Coverage: was the walk complete for a test? (row WK; 6d) ---------------


class WalkCoverage(BaseModel):
    """What the passes a test reads reached, against what Tab should land on
    when the last of them ended (`PassResult.inventory_end`, `inventory_end_items`).
    Facts only: each check's rows decide what an incomplete walk means."""

    counted: int | None = None  # None: the end inventory was not read
    reached: int = 0
    not_reached: int = 0
    not_reached_names: list[str] = []  # up to 3, as `"Two" (a)`; [] past the item cap
    causes: list[str] = []  # how a pass ended, when not at the wrap
    sentence: str | None = None  # the plain sentence; None when complete

    @property
    def complete(self) -> bool:
        return self.counted is not None and self.not_reached == 0


def _chain(stop: Stop) -> str:
    return " >> ".join(stop.frame_chain)


def _stop_ids(passes: list[PassResult]) -> tuple[set[str], set[str], set[str]]:
    """Every identity a stop gives: its path key, its group (a radio group or a
    date input's parts, with the frame chain), the composite widget holding
    it, and each frame the walk went
    into (the walk reads the deepest focused element, so a focusable frame is
    never a stop of its own)."""
    keys: set[str] = set()
    groups: set[str] = set()
    frames: set[str] = set()
    for p in passes:
        for st in p.steps:
            s = st.stop
            if s.kind != "element":
                continue
            keys.add(s.path_key)
            if s.widget:
                # Focus handed to an item of a composite widget (a listbox's
                # option): the widget itself was reached.
                keys.add(s.widget)
            if s.group:
                groups.add(f"{_chain(s)}|{s.group}")
            for i in range(len(s.frame_chain)):
                frames.add(" >> ".join(s.frame_chain[: i + 1]))
    return keys, groups, frames


def _describe(stop: Stop) -> str:
    what = stop.role or stop.control or stop.tag or "element"
    return f'"{stop.name}" ({what})' if stop.name else f"a {what}"


_WHO = {"P1": "Tab", "P2": "Shift+Tab"}


def _cause(p: PassResult) -> str | None:
    who = _WHO.get(p.name, p.name)
    if p.end in ("stuck", "loop"):
        els = [s.stop for s in p.steps if s.stop.kind == "element"]
        at = f" at {_describe(els[-1])}" if els else ""
        return (
            f"{who} {'got stuck' if p.end == 'stuck' else 'went round in a loop'}{at}"
        )
    if p.end == "cap":
        return f"{who} stopped at its limit of {p.cap} presses"
    if p.end == "time":
        return f"{who} ran out of time"
    if p.end == "error":
        return f"{who} could not finish"
    if p.end == "navigation":
        return f"{who} left the page"
    return None


def walk_coverage(
    walk: KeyboardWalk, passes: tuple[str, ...] = ("P1", "P2")
) -> WalkCoverage:
    """Row WK for the elements that take focus (spec Terms). An element is
    reached when a pass in `passes` stopped on it. The elements to reach are
    the candidates of the last pass named, counted when that pass ended: a
    page that grew is complete if everything present then was reached, and a
    pass that ended in a trap, a loop, a cap or out of time matters only
    through what is left over. A radio group is one element, a date input
    one, a frame the walk went into one."""
    read = [p for name, p in (("P1", walk.p1), ("P2", walk.p2)) if name in passes]
    last = read[-1]
    causes = [c for p in read if (c := _cause(p))]
    cov = WalkCoverage(causes=causes)
    if last.inventory_end is None:
        cov.sentence = (
            "The keyboard walk could not count the elements on this page that take "
            "focus when it ended, so we cannot say it reached all of them."
        )
        return cov
    keys, groups, frames = _stop_ids(read)
    cov.counted = last.inventory_end
    items = last.inventory_end_items
    if items is not None:
        left = [
            c
            for c in items
            if not (c.key in keys or c.key in frames or (c.group and c.group in groups))
        ]
        cov.not_reached = len(left)
        cov.reached = len(items) - len(left)
        cov.not_reached_names = [
            f'"{c.label}" ({c.kind})' if c.label else f"a {c.kind}" for c in left[:3]
        ]
    else:
        # Past the list's cap: stops against the count (radio groups, date
        # inputs and entered frames once).
        n = len(
            {
                f"{_chain(s.stop)}|{s.stop.group}" if s.stop.group else s.stop.path_key
                for p in read
                for s in p.steps
                if s.stop.kind == "element"
            }
        ) + len({f for f in frames if f not in keys})
        cov.reached = min(n, cov.counted)
        cov.not_reached = max(0, cov.counted - n)
    if cov.not_reached:
        which = (
            " and ".join(cov.not_reached_names)
            if cov.not_reached_names and cov.not_reached <= 3
            else (
                f"{', '.join(cov.not_reached_names)} and {cov.not_reached - 3} more"
                if cov.not_reached_names
                else f"{cov.not_reached} of them"
            )
        )
        cov.sentence = (
            f"The keyboard reached {cov.reached} of the {cov.counted} elements on "
            f"this page that take focus, so {which} "
            f"{'was' if cov.not_reached == 1 else 'were'} not checked."
        )
        if causes:
            cov.sentence += " " + "; ".join(causes) + "."
    return cov


def field_coverage(
    walk: KeyboardWalk, passes: tuple[str, ...] = ("P1",)
) -> WalkCoverage:
    """Row WK for the 5.x tests: the form fields the page has when the last
    pass named ended (`PassResult.form_fields_end`, radio groups once), against
    the fields a pass stopped on (a radio group once, not read-only, not
    disabled: the same stops `forms._fields` lists). 5.D and 5.F read P1."""
    read = [p for name, p in (("P1", walk.p1), ("P2", walk.p2)) if name in passes]
    last = read[-1]
    cov = WalkCoverage(causes=[c for p in read if (c := _cause(p))])
    if last.form_fields_end is None:
        return cov  # not counted: no sentence (the check's own lines stand)
    seen = {
        s.stop.group or s.stop.path_key
        for p in read
        for s in p.steps
        if s.stop.kind == "element"
        and s.stop.control
        and not s.stop.readonly
        and not s.stop.disabled
    }
    cov.counted = last.form_fields_end
    cov.not_reached = max(0, cov.counted - len(seen))
    cov.reached = cov.counted - cov.not_reached
    if cov.not_reached:
        cov.sentence = (
            f"The keyboard reached {cov.reached} of the {cov.counted} form fields "
            f"on this page, so {cov.not_reached} "
            f"{'was' if cov.not_reached == 1 else 'were'} not checked."
        )
        if cov.causes:
            cov.sentence += " " + "; ".join(cov.causes) + "."
    return cov
