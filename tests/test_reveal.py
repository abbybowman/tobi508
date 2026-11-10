"""Opening everything, phase 1 (src/tobi508/reveal.py, guards `reveal` and
`reveal-content` in engine.apply_guards). The parts that need no browser: what
makes a stop a trigger, what the summary tells the guards, and the guards'
rows. The pages are in test_fixtures_5a.py (f22-f24) and the 4.x fixtures."""

from __future__ import annotations

from types import SimpleNamespace as NS

import pytest

from tobi508 import reveal
from tobi508.engine import apply_guards
from tobi508.models import Finding, Outcome, Stop, TestId


def stop(**kw) -> Stop:
    return Stop(kind="element", key="f:1", css_path="#x", **{"tag": "button", **kw})


@pytest.mark.parametrize(
    ("kw", "why"),
    [
        ({"collapsed": True}, ["collapsed"]),
        ({"collapsed": True, "tag": "summary"}, ["summary"]),
        ({"haspopup": "menu"}, ["popup"]),
        ({"controls": "p", "controls_hidden": True}, ["controls"]),
        ({"tab_unselected": True}, ["tab"]),
        (
            {"collapsed": True, "controls": "p", "controls_hidden": True},
            ["collapsed", "controls"],
        ),
        # not triggers: a plain button, aria-controls on a region that is
        # shown (the selected tab's panel), a form field, a native date part
        ({}, []),
        ({"controls": "p", "controls_hidden": False}, []),
        ({"collapsed": True, "control": "combobox"}, []),
        ({"haspopup": "dialog", "control": "date", "group": "input:#d"}, []),
    ],
)
def test_what_makes_a_stop_a_trigger(kw, why):
    assert reveal.reasons(stop(**kw)) == why


def opened(n=1, status=reveal.OPENED, **kw):
    return reveal.Opened(n=n, name=f"t{n}", status=status, **kw)


def test_summary_lists_what_was_not_opened_and_what_could_not_be_read():
    rv = reveal.Reveal(
        triggers=[
            opened(1, new_focusable=2, read=True),
            opened(2, reveal.NOTHING, reason=reveal.WHY[reveal.NOTHING]),
            opened(3, reveal.NAVIGATED),  # a link that goes elsewhere
            opened(4, read=False),
            opened(5, reveal.NOT_FOUND, reason=reveal.WHY[reveal.NOT_FOUND]),
        ],
        over_cap=2,
    )
    s = rv.summary()
    assert s["triggers"] == 7 and s["opened"] == 2
    assert [x["name"] for x in s["not_opened"]] == ["t2", "t5", "2 more"]
    assert s["read_failed"] == ["t4"]
    assert s["opened_with_focusable"] == 1


def finding() -> Finding:
    return Finding(
        test_id=TestId.T5C,
        test_name="1.3.1-programmatic-label",
        outcome=Outcome.PASS,
        rationale="",
        rows=["G4"],
        summary="Everything passes.",
    )


def report(**rv):
    return NS(reveal=rv, unrecorded_code_count=0)


def test_guard_rv_moves_a_pass_when_something_that_opens_was_not_opened():
    rv = {"triggers": 2, "opened": 1, "not_opened": [{"name": "Menu", "why": "x"}]}
    f = apply_guards(finding(), ("reveal",), report(**rv))
    assert f.outcome is Outcome.NEEDS_REVIEW and f.rows[-1] == "RV"
    assert '"Menu"' in f.summary and f.note
    # read failures count too; a run whose opening failed outright counts
    f = apply_guards(
        finding(), ("reveal",), report(triggers=1, opened=1, read_failed=["Tabs"])
    )
    assert f.outcome is Outcome.NEEDS_REVIEW
    f = apply_guards(finding(), ("reveal",), report(failed=True))
    assert f.outcome is Outcome.NEEDS_REVIEW


def test_guard_rv_leaves_a_clean_pass_and_every_other_outcome_alone():
    clean = {"triggers": 1, "opened": 1, "not_opened": [], "read_failed": []}
    assert apply_guards(finding(), ("reveal",), report(**clean)).outcome is Outcome.PASS
    # nothing opened at all and nothing there: no triggers, no reveal record
    assert apply_guards(finding(), ("reveal",), report()).outcome is Outcome.PASS
    # the spec does not declare it
    bad = {"not_opened": [{"name": "Menu", "why": "x"}]}
    assert apply_guards(finding(), (), report(**bad)).outcome is Outcome.PASS
    for o in (Outcome.FAIL, Outcome.DNA, Outcome.NEEDS_REVIEW):
        f = finding()
        f.outcome = o
        assert apply_guards(f, ("reveal",), report(**bad)).outcome is o


def test_guard_rc_moves_a_pass_only_when_opened_content_holds_controls():
    some = {"triggers": 1, "opened": 1, "opened_with_focusable": 1}
    none = {"triggers": 1, "opened": 1, "opened_with_focusable": 0}
    f = apply_guards(finding(), ("reveal", "reveal-content"), report(**some))
    assert f.outcome is Outcome.NEEDS_REVIEW and f.rows[-1] == "RC"
    assert "has not checked inside them yet" in f.summary
    keep = apply_guards(finding(), ("reveal", "reveal-content"), report(**none))
    assert keep.outcome is Outcome.PASS
    # a spec without reveal-content (5.A-5.C read opened content; 4.F's pass R)
    assert apply_guards(finding(), ("reveal",), report(**some)).outcome is Outcome.PASS
