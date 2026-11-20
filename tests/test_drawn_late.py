"""Step 22: no outcome from a walk that missed the page (plan after round 3,
cause 2). Round 3's community pages are an application that draws its
controls a second or more after load; the walk began on an almost empty page,
reached one link of 76 and 90, and 4.F said DOES NOT APPLY ("only one
element"), 5.D "no form fields", and 4.A failed controls "the keyboard never
reaches". The fixture draws its controls 1.2 s after load (custom: no ACT or
Baseline case covers a page that draws itself late). Each test decides from
the inventory taken after the walk; while the walk covered less, NEEDS
REVIEW. Expected outcomes live here, never in the page."""

from __future__ import annotations

import pytest

from tobi508 import traverse
from tobi508.models import Outcome, TestId
from tobi508.pipeline import run_tt_tests

LATE = "walk/drawn-late.html"
TESTS = ("4.A", "4.C", "4.F", "5.A", "5.D", "5.F", "5.G", "5.H")


@pytest.fixture
async def late(settings, server, monkeypatch):
    # Step 22's rows with step 23's wait switched off: a walk that still
    # began before the page drew (a page drawn past the wait's ceiling).
    monkeypatch.setattr(traverse, "DRAW_MAX_S", 0.0)
    out = await run_tt_tests(
        settings, f"{server.base}/{LATE}", [TestId(t) for t in TESTS]
    )
    return {f.test_id.value: f for f in out.report.findings}


# The page's rows today (2026-11-17, step 22). Before: 4.A and 4.C PASS
# (A3, G4), 4.F DOES NOT APPLY (A3: "only one element"), 5.A, 5.D and 5.F
# to 5.H DOES NOT APPLY (A1: "no form fields").
ROWS = {
    "4.A": ["A3", "WK", "WL", "G3"],
    "4.C": ["A3", "WL", "G3"],
    "4.F": ["WL", "G1"],
    "5.A": ["A3", "G1"],
    "5.D": ["A2", "G1"],
    "5.F": ["A2", "G1"],
    "5.G": ["A2", "G1"],
    "5.H": ["A2", "G1"],
}


async def test_a_page_drawn_late_is_never_decided_on_what_was_there_first(late):
    for t in TESTS:
        f = late[t]
        assert (f.outcome, f.rows) == (Outcome.NEEDS_REVIEW, ROWS[t]), (
            t,
            f.outcome,
            f.rows,
            f.summary,
        )
        assert f.note == "This test could not be performed", (t, f.note)
    assert "a few seconds later" in late["4.F"].summary
    assert "after it loaded" in late["5.A"].summary


# The nearest pages that must keep their outcomes: one link only, drawn with
# the page (4.F A3), and a page with no form field at all (5.D A1).
@pytest.mark.parametrize(
    ("page", "test", "row"),
    [
        ("4f/f07-one-link.html", "4.F", "A3"),
        ("4d/f01-background-change.html", "5.D", "A1"),
    ],
)
async def test_a_page_drawn_with_its_load_keeps_its_outcome(
    page, test, row, settings, server
):
    out = await run_tt_tests(settings, f"{server.base}/{page}", [TestId(test)])
    [f] = out.report.findings
    assert (f.outcome, f.rows) == (Outcome.DNA, [row, "G1"]), (f.rows, f.summary)


def _walk(start: int, end1: int, end2: int):
    from tobi508.models import PassResult
    from tobi508.walk import KeyboardWalk

    def p(name, end):
        return PassResult.model_construct(
            name=name,
            steps=[],
            end="wrap",
            inventory=start,
            inventory_end=end,
            inventory_end_items=None,
            form_fields=0,
            form_fields_end=0,
        )

    return KeyboardWalk.model_construct(p1=p("P1", end1), p2=p("P2", end2))


def test_a_late_link_on_a_page_drawn_by_the_server_is_not_a_page_drawn_late():
    """Round 2's home page (step 22's first rerun): 145 elements when the walk
    began, 146 later. One late link is not an application drawn after load:
    no row WL, and coverage keeps counting against the pass it reads."""
    from tobi508.walk import drawn_late

    w = _walk(145, 146, 145)
    assert not w.grew and drawn_late(w) is None
    assert _walk(1, 1, 76).grew  # round 3's community home page
    assert not _walk(10, 10, 20).grew and _walk(10, 10, 21).grew


# Step 23: a load waits until the page has drawn itself (the count of elements
# that take focus unchanged for 2 s, at most 10 s). The page drawn 1.2 s after
# load then gives what its twin with the same controls in the document at load
# gives, test by test: every outcome and row. Run with no answers, so 5.B's
# question stays open on both.
ALL = (
    "4.A",
    "4.C",
    "4.D",
    "4.E",
    "4.F",
    "5.A",
    "5.B",
    "5.C",
    "5.D",
    "5.F",
    "5.G",
    "5.H",
)


async def test_a_page_drawn_late_is_read_as_it_is_drawn(settings, server):
    got = {}
    for page in ("walk/drawn-late.html", "walk/drawn-at-load.html"):
        out = await run_tt_tests(
            settings, f"{server.base}/{page}", [TestId(t) for t in ALL]
        )
        got[page] = {f.test_id.value: (f.outcome, f.rows) for f in out.report.findings}
    late, at_load = got["walk/drawn-late.html"], got["walk/drawn-at-load.html"]
    assert late == at_load
    # Decided, not left for a person on the late page's account.
    assert late["4.F"][0] is Outcome.PASS and late["5.D"][0] is Outcome.PASS
    assert not any("WL" in rows for _, rows in late.values())


# Row WL as a guard (#134): a page still drawing itself when the 10 s wait
# ended (a status link comes and goes every 400 ms; the controls appear 11 s
# after load), walked in under 3 s, was read as it stood: before the guard,
# 4.A and 4.C PASS and 5.A to 5.F DOES NOT APPLY ("no form fields"). A reading
# from such a load decides nothing. 5.D does not take the guard yet (#135 and
# #137 hold its spec), so it still says DOES NOT APPLY: a known gap.
AFTER_WAIT = "walk/drawn-after-wait.html"
GUARDED = ("4.A", "4.C", "4.F", "5.A", "5.B", "5.C", "5.F")


@pytest.mark.slow
async def test_a_page_still_drawing_when_the_wait_ended_decides_nothing(
    settings, server
):
    out = await run_tt_tests(
        settings,
        f"{server.base}/{AFTER_WAIT}",
        [TestId(t) for t in (*GUARDED, "5.D")],
    )
    got = {f.test_id.value: f for f in out.report.findings}
    assert out.report.drawn_past_wait, out.report.drawn_past_wait
    for t in GUARDED:
        f = got[t]
        assert f.outcome is Outcome.NEEDS_REVIEW, (t, f.outcome, f.rows, f.summary)
        assert f.outcome is not Outcome.PASS and f.outcome is not Outcome.DNA
        assert f.note == "This test could not be performed", (t, f.rows)
    # 4.A and 4.C walked the page as it stood and passed it: only the guard
    # holds them. The others' own rows may hold them first (a pass that ended
    # after 11 s sees the fields: 5.A's A3), depending on timing.
    for t in ("4.A", "4.C"):
        assert got[t].rows[-1] == "WL", (t, got[t].rows)
        assert "still drawing itself 10 seconds" in got[t].summary, t
    assert got["5.D"].outcome is Outcome.DNA  # not guarded yet (#135, #137)


def test_the_guard_moves_only_pass_and_does_not_apply():
    from tobi508.engine import apply_guards
    from tobi508.models import Finding

    class R:
        drawn_past_wait = ["http://x/"]

    for before, after in [
        (Outcome.PASS, Outcome.NEEDS_REVIEW),
        (Outcome.DNA, Outcome.NEEDS_REVIEW),
        (Outcome.FAIL, Outcome.FAIL),
        (Outcome.NEEDS_REVIEW, Outcome.NEEDS_REVIEW),
    ]:
        f = Finding.model_construct(
            test_id=TestId("4.C"),
            outcome=before,
            rows=["G4"],
            summary="",
            note=None,
            rationale="",
        )
        g = apply_guards(f, ("drawn-past-wait",), R())
        assert g.outcome is after, (before, g.outcome)
        assert ("WL" in g.rows) == (before in (Outcome.PASS, Outcome.DNA))

    class Quiet:
        drawn_past_wait: list[str] = []

    f = Finding.model_construct(
        test_id=TestId("4.C"),
        outcome=Outcome.PASS,
        rows=["G4"],
        summary="",
        note=None,
        rationale="",
    )
    assert apply_guards(f, ("drawn-past-wait",), Quiet()).outcome is Outcome.PASS
