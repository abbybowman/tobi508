"""Guard CN on the code review's pages (plan 2026-11-12 part B): something the
page plainly has, which a test's reader did not read, holds a PASS or DOES
NOT APPLY as NEEDS REVIEW with a sentence that names it. Expected outcomes
live here, never in a page. The pages are copies of
docs/reviews/2026-11-11-code-review-pages/pages/ (asset paths made absolute
for the fixture server); `quiet.html` is the page where the inventory and the
readings agree."""

from __future__ import annotations

import pytest

from tobi508.models import Outcome, TestId
from tobi508.pipeline import run_tt_tests

# page -> test -> (outcome, a sentence the summary holds, or None when CN must
# stay quiet). Review IDs in the comments.
EXPECTED: dict[str, dict[str, tuple[str, str | None]]] = {
    # D-01: a form inside a web component.
    "shadow-form": {
        "5.A": (
            "NEEDS_REVIEW",
            "2 form fields inside web components were not checked.",
        ),
        "5.B": (
            "NEEDS_REVIEW",
            "2 form fields inside web components were not checked.",
        ),
        "5.C": (
            "NEEDS_REVIEW",
            "2 form fields inside web components were not checked.",
        ),
    },
    # H-08: a form a plain button shows.
    "hidden-form-button": {
        "5.A": (
            "NEEDS_REVIEW",
            "1 form field is hidden until something opens it, and was not checked.",
        ),
        "5.C": (
            "NEEDS_REVIEW",
            "1 form field is hidden until something opens it, and was not checked.",
        ),
        "5.D": (
            "NEEDS_REVIEW",
            "1 form field is hidden until something opens it, and was not checked.",
        ),
    },
    # H-08: a form a link shows, and an editable text area.
    "hidden-form-link": {
        "5.A": (
            "NEEDS_REVIEW",
            "2 form fields are hidden until something opens them, and were not "
            "checked.",
        ),
        "5.D": ("NEEDS_REVIEW", "1 editable text area was not checked."),
    },
    # M-07: a payment form a plain button shows.
    "pay-form-hidden": {
        t: (
            "NEEDS_REVIEW",
            "2 form fields are hidden until something opens them, and were not "
            "checked.",
        )
        for t in ("5.F", "5.G", "5.H")
    },
    # M-02: a form that is only a button.
    "delete-button-form": {
        "5.H": ("NEEDS_REVIEW", "1 form with a button was not tested."),
    },
    # N-01: audio a script plays with no element on the page.
    "audio-detached": {
        "2.A": (
            "NEEDS_REVIEW",
            "1 sound or video played from a script, and was not checked.",
        ),
    },
    # N-01: autoplaying audio inside a web component.
    "audio-shadow": {
        "2.A": (
            "NEEDS_REVIEW",
            "1 sound or video played inside a web component, and was not checked.",
        ),
    },
    # N-06: an animated image after the 30th image.
    "many-images": {
        "2.B": ("NEEDS_REVIEW", "32 images: only the first 30 were checked"),
        "3.A": ("NEEDS_REVIEW", "32 images: only the first 30 were checked"),
    },
    # E-03: a page that is only a canvas and a dragged box. Row A1 itself
    # (4.A 1.6.0) now leaves it for review, before the guard is reached.
    "canvas-only": {"4.A": ("NEEDS_REVIEW", None)},
    # F-11: the first element swallows Tab.
    "first-link-traps": {
        "4.F": (
            "NEEDS_REVIEW",
            "The page has 4 elements that take focus, and the keyboard reached 1.",
        ),
    },
}

QUIET = {"2.A", "4.F", "5.A", "5.C", "5.D", "5.F", "5.G", "5.H"}


def _cases():
    for page, tests in EXPECTED.items():
        yield pytest.param(page, tests, id=page)


@pytest.mark.parametrize(("page", "tests"), _cases())
async def test_the_guard_names_what_was_not_read(page, tests, settings, server):
    out = await run_tt_tests(
        settings, f"{server.base}/count/{page}.html", [TestId(t) for t in tests]
    )
    by = {f.test_id.value: f for f in out.report.findings}
    for t, (outcome, sentence) in tests.items():
        f = by[t]
        assert f.outcome is Outcome(outcome), (t, f.outcome, f.summary)
        if sentence is None:
            continue  # the test's own rows decide; the guard is not reached
        assert "CN" in f.rows, (t, f.rows)
        assert sentence in f.summary, (t, f.summary)
        assert f.note == "This test could not be performed"


async def test_the_guard_stays_quiet_when_the_readings_agree(settings, server):
    out = await run_tt_tests(
        settings, f"{server.base}/count/quiet.html", [TestId(t) for t in QUIET]
    )
    count = out.report.counts["page"]
    assert not count.error and count.fields.light == 2
    # The muted audio played on pass T's load, and the media read listed it.
    assert count.played_from == "pass T" and count.media_played.light == 1
    for f in out.report.findings:
        assert "CN" not in f.rows, (f.test_id, f.rows, f.summary)


async def test_navigation_inside_a_web_component_is_not_does_not_apply(
    settings, server
):
    """K-02, M-12: two pages share a header built as a web component."""
    out = await run_tt_tests(
        settings,
        f"{server.base}/count/site-header-a.html",
        [TestId(t) for t in ("9.A", "9.B", "9.C", "19.A")],
        other_pages=[f"{server.base}/count/site-header-b.html"],
    )
    by = {f.test_id.value: f for f in out.report.findings}
    assert set(out.report.counts) == {"page", "p1"}
    for t in ("9.B", "9.C"):
        f = by[t]
        assert f.outcome is Outcome.NEEDS_REVIEW, (t, f.outcome, f.summary)
        assert "CN" in f.rows, (t, f.rows)
        assert "3 links inside web components were not checked." in f.summary
        assert "On other page 1, 3 links inside web components" in f.rationale or (
            "On other page 1" in f.summary
        )
    # 9.A is not DOES NOT APPLY or PASS on it either.
    assert by["9.A"].outcome not in (Outcome.PASS, Outcome.DNA), by["9.A"].summary
    # The guard never moves a FAIL: 19.A's "no way to reach this page" here is
    # a wrong FAIL the guard cannot touch (left for a spec decision).
    assert by["19.A"].outcome is not Outcome.PASS
