"""4.A (2.1.1-keyboard-access) on W3C ACT cases (akn7bn, 0ssw9k) and custom
fixtures for gaps, plus rules unit tests for rows no page triggers reliably.
Section 508 Baseline cases are in test_baseline_cases.py. Expected outcomes
and scripted answers (what a correct agent would say) live here and in the
manifests, never in a page."""

from __future__ import annotations

import json
import re

import pytest

from tobi508.checks import t4a
from tobi508.models import Outcome, TestId
from tobi508.observe import Effect

from .conftest import ACT_ROOT, FIXTURES
from .harness import instance_rows, run_check
from .scoring import write_score

NO_ALT = {"J1": {"choice": "no_alternative"}}

EXPECTED: dict[str, dict] = {
    "f01-click-only-text": {"outcome": "FAIL", "rows": ["M6"], "choice": NO_ALT},
    "f02-custom-button-ignores-keys": {"outcome": "FAIL", "rows": ["M10"]},
    "f03-custom-button-with-keys": {"outcome": "PASS", "rows": ["M8"]},
    "f04-hover-only-menu": {"outcome": "FAIL", "rows": ["M6", "M6"], "choice": NO_ALT},
    "f05-hover-and-focus-menu": {"outcome": "PASS", "rows": []},
    "f06-print-icon-and-button": {
        "outcome": "PASS",
        "rows": ["M5"],
        "choice": {"J1": {"choice": "alternative", "element": 1}},
    },
    "f07-same-address-link": {"outcome": "PASS", "rows": ["M3"]},
    # Fix 24 (4.A 1.8.0): an arrow that scrolls a container whose items the
    # Tab walk reaches is decided mechanically. The nearest case that must
    # still ask: the same arrow over items with no link or control.
    # Fix 25 (4.A 1.8.1): J1's input says where the click went; the one reached
    # link goes to a different address, so nothing matches mechanically.
    "f22-click-goes-elsewhere": {"outcome": "FAIL", "rows": ["M6"], "choice": NO_ALT},
    "f20-scroll-arrow-items-have-links": {"outcome": "PASS", "rows": ["M3s"]},
    "f21-scroll-arrow-items-have-no-links": {
        "outcome": "FAIL",
        "rows": ["M6"],
        "choice": NO_ALT,
    },
    # Native date input parts are native (1.2.0): only the custom picker is
    # executed. NEEDS REVIEW since 1.5.0: the picker opens a panel with
    # controls, which this test does not walk yet (guard RC, fix 9b phase 2).
    "f13-native-date-and-custom-picker": {"outcome": "NEEDS_REVIEW", "rows": ["M8"]},
    "f08-title-only-format": {
        "outcome": "FAIL",
        "rows": ["M14"],
        "choice": {"J2": {"choice": "essential"}},
    },
    "f09-title-repeats-label": {"outcome": "PASS", "rows": ["M11"]},
    "f10-canvas-map": {"outcome": "NEEDS_REVIEW", "rows": ["M16"]},
    "f11-pointer-cursor-decoration": {"outcome": "PASS", "rows": ["M2", "M2"]},
    "f12-roving-tabs": {"outcome": "PASS", "rows": []},
    # Row WK (1.11.0, step 6d): a script skips link 2 in both directions, so
    # no pass stops on it: 3 of the page's 4 elements reached, NEEDS REVIEW.
    # f30 is the same page without the script: 4 of 4, PASS.
    "f29-link-skipped-by-script-both-ways": {
        "outcome": "NEEDS_REVIEW",
        "choice": "unsure",
        "rows": ["M7"],
        "page_rows": ["WK"],
        "walk": (3, 4),
    },
    "f30-links-all-reached": {"outcome": "PASS", "rows": [], "walk": (4, 4)},
    # Media start (1.4.0): a click that starts a video is an effect. The row's
    # click handler is added by script, which the main-world listener read
    # finds (CILab, round 2).
    "f14-script-added-click-row": {
        "outcome": "FAIL",
        "rows": ["M6"],
        "choice": NO_ALT,
    },
    "f15-video-click-to-play": {"outcome": "FAIL", "rows": ["M6"], "choice": NO_ALT},
    "f16-video-click-and-button": {
        "outcome": "PASS",
        "rows": ["M5"],
        "choice": {"J1": {"choice": "alternative", "element": 1}},
    },
    "f17-click-only-play-button": {"outcome": "FAIL", "rows": ["M10"]},
    # E-01: 45 links, a mouse-only menu on the 45th. The hover scan stops at
    # 40 stops, which is a cap reached: never PASS (spec G3).
    "f18-hover-menu-past-the-cap": {"outcome": "NEEDS_REVIEW", "rows": []},
    # E-02: a mouse-only <a href="#"> beside another <a href="#">. "#" goes
    # nowhere, so the two do not "go to the same place" (M3): J1 is asked.
    "f19-placeholder-link-twin": {
        "outcome": "FAIL",
        "rows": ["M6"],
        "choice": NO_ALT,
    },
    # C-01 (1.9.0): an alert() or a download is an effect of a click, so a
    # mouse-only control whose only effect is one is a candidate (J1 is
    # asked). The control: a click that does nothing is still no instance.
    "f23-click-only-alert": {"outcome": "FAIL", "rows": ["M6"], "choice": NO_ALT},
    "f24-click-only-download": {"outcome": "FAIL", "rows": ["M6"], "choice": NO_ALT},
    "f25-click-only-does-nothing": {"outcome": "PASS", "rows": ["M2"]},
    # E-08 (1.10.0): Tab reaches a native button that answers only mousedown,
    # but Enter and Space do nothing (F54). f27 has a click handler too
    # (Enter works); f28 is a link whose Enter follows its address.
    "f26-native-button-mousedown-only": {"outcome": "FAIL", "rows": ["M10"]},
    "f27-native-button-mousedown-and-click": {"outcome": "PASS", "rows": []},
    "f28-link-with-mousedown-tracking": {"outcome": "PASS", "rows": []},
}

ACT = {
    c["id"]: c
    for c in json.loads((ACT_ROOT / "manifest.json").read_text())["cases"]
    if c["tt_test"] == "4.A"
}
# 62673162 and aa153f67 need no answer: keyboard focus reaches nothing, so
# no alternative can exist (M4n, mechanical).
ANSWERS: dict[str, dict] = {}


def test_every_fixture_is_listed():
    names = {p.stem for p in (FIXTURES / "4a").glob("*.html")}
    assert names == set(EXPECTED)
    for n in names:
        assert re.fullmatch(r"f\d{2}-[a-z0-9-]+", n), n


@pytest.mark.parametrize("name", sorted(EXPECTED))
async def test_outcome(name, settings, server):
    e = EXPECTED[name]
    got = await run_check(
        settings, f"{server.base}/4a/{name}.html", TestId.T4A, e.get("choice")
    )
    f = got["finding"]
    assert (f.outcome.value, instance_rows(f)) == (e["outcome"], e["rows"]), (
        f.rationale,
        f.summary,
    )
    if "page_rows" in e:
        assert set(e["page_rows"]) <= set(f.rows), f.rows
    if "walk" in e:  # row WK's evidence: elements reached of elements counted
        r, c = e["walk"]
        assert f"Walk: reached {r} of {c}" in f.rationale, f.rationale


@pytest.mark.parametrize("case_id", sorted(ACT))
async def test_act_case(case_id, settings, act_server):
    case = ACT[case_id]
    got = await run_check(
        settings, f"{act_server}/{case['path']}", TestId.T4A, ANSWERS.get(case_id)
    )
    outcome = got["finding"].outcome.value
    write_score(case_id, outcome, got["finding"].rows)
    assert outcome == case["expected"], got["finding"].rationale


async def test_pass_says_what_was_looked_for_and_the_browser(settings, server):
    got = await run_check(
        settings, f"{server.base}/4a/f05-hover-and-focus-menu.html", TestId.T4A
    )
    s = got["finding"].summary
    assert "We looked for" in s and "Results are for the browser used" in s


# ── Rules on recorded evidence (rows no page triggers reliably) ──────────────


def _state(*insts: t4a.Inst4A, incomplete: list[str] | None = None) -> t4a.State4A:
    return t4a.State4A(
        p1={"end": "wrap"},
        p2={"end": "wrap"},
        stops=2,
        inventory=2,
        targets=2,
        stop_list=[
            t4a.StopRef(n=1, path_key="#a", role="link", name="A", index=0),
            t4a.StopRef(n=2, path_key="#b", role="button", name="B", index=1),
        ],
        instances=list(insts),
        incomplete=incomplete or [],
    )


def _k(**kw) -> t4a.Inst4A:
    return t4a.Inst4A(
        id="k1",
        kind="K",
        target={"css_path": "#k", "name": "K", "reason": "native"},
        **kw,
    )


def _x(**kw) -> t4a.Inst4A:
    return t4a.Inst4A(
        id="x1", kind="X", target={"css_path": "#x", "name": "X"}, keys=["Tab"], **kw
    )


EFF = Effect(kinds=["dom"], mutations=1)
NONE = Effect()
NOISY = Effect(kinds=["dom"], mutations=2, noise=3)


@pytest.mark.parametrize(
    ("inst", "outcome", "row"),
    [
        (_k(checked=False), "NEEDS_REVIEW", "C?"),
        (_k(unreliable=True), "NEEDS_REVIEW", "M1"),
        (_x(enter=NOISY), "NEEDS_REVIEW", "M1"),
        (_k(j={"choice": "unsure"}), "NEEDS_REVIEW", "M7"),
        # The named alternative must be a stop; otherwise it is unsure.
        (_k(j={"choice": "alternative", "element": 9}), "NEEDS_REVIEW", "M7"),
        (_k(j={"choice": "alternative", "element": 2}), "PASS", "M5"),
        (_x(enter=NONE, space=EFF), "PASS", "M8"),
        (_x(enter=NONE, space=NONE, click=NONE), "PASS", "M9"),
        (
            t4a.Inst4A(
                id="t1",
                kind="T",
                target={"name": "T"},
                title="x",
                elsewhere=False,
                j={"choice": "not_essential"},
            ),
            "PASS",
            "M13",
        ),
        (
            t4a.Inst4A(
                id="t1",
                kind="T",
                target={"name": "T"},
                title="x",
                elsewhere=False,
                j={"choice": "unsure"},
            ),
            "NEEDS_REVIEW",
            "M15",
        ),
    ],
)
def test_rows_on_recorded_evidence(inst, outcome, row):
    f = t4a.evaluate(_state(inst), [])
    page = {"M9": "PASS", "M5": "PASS", "M8": "PASS", "M13": "PASS"}.get(row, outcome)
    assert (f.outcome.value, instance_rows(f)) == (page, [row]), f.rationale


def test_incomplete_scan_is_never_pass():
    f = t4a.evaluate(_state(incomplete=["The run time limit was reached."]), [])
    assert f.outcome is Outcome.NEEDS_REVIEW and f.note


def test_p1_without_wrap_is_never_pass():
    st = _state()
    st.p1 = {"end": "stuck"}
    assert t4a.evaluate(st, []).outcome is Outcome.NEEDS_REVIEW


async def test_shadow_and_frame_stops_are_reached(settings, server):
    # no_trap.html: a button in a shadow root, one in a frame, and an inert
    # role=button div that neither keys nor a click change (not an instance).
    got = await run_check(settings, f"{server.base}/no_trap.html", TestId.T4A)
    f = got["finding"]
    assert (f.outcome.value, instance_rows(f)) == ("PASS", ["M9"]), f.rationale


async def test_no_stops_fails_without_a_question(settings, act_server):
    # ACT akn7bn Failed Example 1: a link only in a tabindex=-1 frame, nothing
    # else on the page. No keyboard alternative can exist, so no question.
    case = ACT["62673162"]
    got = await run_check(settings, f"{act_server}/{case['path']}", TestId.T4A)
    f = got["finding"]
    assert (f.outcome.value, instance_rows(f)) == ("FAIL", ["M4n"]), f.rationale
    assert "did not get through the whole page" not in f.summary


def test_scroll_arrow_is_covered_only_when_every_revealed_item_is_reached():
    """4.A 1.8.0 (fix 24): row M3s needs at least one revealed item and every
    one of them reached; a partly reached scroller still asks J1."""
    from tobi508.checks.t4a import Inst4A, _scroll_covered

    def inst(scroll):
        return Inst4A(id="k1", kind="K", target={}, scroll=scroll)

    assert _scroll_covered(inst({"container": "ul", "items": 3, "reached": 3}))
    assert not _scroll_covered(inst({"container": "ul", "items": 3, "reached": 2}))
    assert not _scroll_covered(inst({"container": "ul", "items": 0, "reached": 0}))
    assert not _scroll_covered(inst(None))


async def test_j1_says_where_the_click_goes(settings, server):
    """4.A 1.8.1 (fix 25): a candidate whose click navigates carries the
    address it went to, so the judge can compare it with the stops' links."""
    got = await run_check(
        settings,
        f"{server.base}/4a/f22-click-goes-elsewhere.html",
        TestId.T4A,
        NO_ALT,
    )
    [q] = got["asked"]
    assert q.input["candidate"]["goes_to"].endswith("#form-b"), q.input
    assert "goes_to" in q.question
