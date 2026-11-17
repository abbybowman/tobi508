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

from tobi508.models import Outcome, TestId
from tobi508.pipeline import run_tt_tests

LATE = "walk/drawn-late.html"
TESTS = ("4.A", "4.C", "4.F", "5.A", "5.D", "5.F", "5.G", "5.H")


@pytest.fixture
async def late(settings, server):
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
