"""tobi_explain's brief view after a run (agent debriefs, 2026-11-23): places
in plain words with how to reach each, no spec codes, at most BRIEF_PLACES
listed, the summary's sentences said once, unnamed elements named for
people. Wording only: no outcome is decided here."""

from __future__ import annotations

from tobi508 import explain
from tobi508.checks import t4a, t4c, t4d, t4e, t5d
from tobi508.checks.base import element_name
from tobi508.models import Finding, Instance, Outcome, Report, TestId


def _report(f: Finding, settings) -> Report:
    from tobi508.models import utcnow
    from tobi508.versions import collect_versions

    return Report(
        run_id="20261123T000000Z-abcdef",
        target="https://x.gov",
        started_at=utcnow(),
        versions=collect_versions(settings, None),
        findings=[f],
        evidence_dir="/tmp",
    )


def _finding(n_loud: int, n_quiet: int) -> Finding:
    loud = [
        Instance(
            outcome=Outcome.FAIL,
            plain=f'"Link {k}" shows no focus. Press Tab {k} times.',
            description=f'd{k} [M8 FAIL] "Link {k}" (link) changed 0 px',
        )
        for k in range(1, n_loud + 1)
    ]
    quiet = [
        Instance(outcome=Outcome.PASS, description=f"d{k} [M6 PASS] ok")
        for k in range(100, 100 + n_quiet)
    ]
    summary = (
        "Some links show no focus. "
        + " ".join(i.plain for i in loud)
        + (f" {n_quiet} other element(s) showed focus clearly." if n_quiet else "")
    )
    return Finding(
        test_id=TestId.T4D,
        test_name=TestId.T4D.tt_name,
        outcome=Outcome.FAIL,
        summary=summary,
        instances=loud + quiet,
    )


def test_places_are_plain_capped_and_said_once(settings):
    f = _finding(10, 120)
    text = explain.build("4.D", _report(f, settings))
    for k in range(1, explain.BRIEF_PLACES + 1):
        assert text.count(f'"Link {k}" shows no focus. Press Tab {k} times.') == 1
    # Past the cap: not a place line, so its sentence stays in the summary.
    assert f"- and {10 - explain.BRIEF_PLACES} more like these" in text
    assert '"Link 10" shows no focus. Press Tab 10 times.' in text
    assert "120 other place(s) passed or did not apply." in text
    assert "showed focus clearly" not in text  # the count, said once
    assert "[M8 FAIL]" not in text and "changed 0 px" not in text
    assert "Some links show no focus." in text
    full = explain.build("4.D", _report(f, settings), "full")
    assert "[M8 FAIL]" in full and f.summary in full and "d100 [M6 PASS]" in full


def test_open_questions_come_before_the_fix_link(settings):
    f = _finding(1, 0)
    text = explain.build("4.D", _report(f, settings))
    assert text.index("How to fix:") > text.index("Summary")
    assert "Places on the page that failed or need a person:" in text


def test_a_place_without_a_sentence_loses_its_codes(settings):
    f = _finding(0, 0)
    f.instances = [
        Instance(
            outcome=Outcome.NEEDS_REVIEW, description='p2 [N4 NEEDS_REVIEW] "a" / "b"'
        )
    ]
    text = explain.build("4.D", _report(f, settings))
    assert '- "a" / "b"' in text


def test_an_unnamed_element_is_named_for_people():
    assert element_name("", "button") == "an unnamed button"
    assert element_name(" ", "generic") == "an unnamed element"
    assert element_name(None, None, unnamed="field") == "an unnamed field"
    assert element_name("Go", "button") == '"Go" (button)'
    assert element_name("x" * 80, "link").startswith('"' + "x" * 57 + '..."')
    # Every check's own naming goes through it: never a CSS path.
    info = {"name": "", "role": "button", "css_path": "div.css-x7f2a > button"}
    for label in (t4a._label, t4c._label, t4d._label, t4e._label):
        assert label(info) == "an unnamed button"
    assert t5d._label({"css_path": "#f > input", "kind": "text field"}) == (
        "an unnamed text field"
    )
