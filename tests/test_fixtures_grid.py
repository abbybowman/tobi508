"""The grid of hard pages (plan 2026-11-12 part I, Q-03; roadmap step 7).

One table: page by TT test. Every page of `tests/fixtures/grid/` is run
against all 22 checks in one call, with no answers to open questions, and
each cell says what the run gives today. The rule the table obeys:

* never PASS, and
* DOES NOT APPLY only with a written reason.

A cell that breaks the rule today is not hidden and not fixed here: it is
a *known wrong outcome* that names its review item
(docs/reviews/2026-11-11-code-review.md). The test still asserts the
outcome the run gives today, so the day a fix lands the cell fails and must
be updated, as an expected failure that is no longer one. A cell the grid
found that the review has no item for is `NEW-n`, described in `UNFILED`.

Expected outcomes live here, never in a page (CLAUDE.md, "Fixtures"). Pages
are served from `tests/fixtures/` by the shared fixture server (conftest).
This file adds tests only: no spec and no outcome changed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

from tobi508.checks import REGISTRY
from tobi508.models import Outcome, TestId
from tobi508.pipeline import run_tt_tests

GRID = Path(__file__).parent / "fixtures" / "grid"
REVIEW = Path(__file__).parent.parent / "docs" / "reviews" / "2026-11-11-code-review.md"
# Pages another page loads: part of a grid page, not a grid page of their own.
HELPERS = {"frame-inner"}


@dataclass(frozen=True)
class Cell:
    outcome: Outcome
    # DOES NOT APPLY only: why the page has nothing for this test.
    nothing_for_it: str | None = None
    # A cell that breaks the rule today: (review item, what is wrong).
    known_wrong: tuple[str, str] | None = None


def nr() -> Cell:
    return Cell(Outcome.NEEDS_REVIEW)


def fail() -> Cell:
    return Cell(Outcome.FAIL)


def dna(reason: str) -> Cell:
    return Cell(Outcome.DNA, nothing_for_it=reason)


def wrong(outcome: Outcome, item: str, what: str) -> Cell:
    return Cell(outcome, known_wrong=(item, what))


# Findings of the grid that the code review has no item for. Each needs a
# line in the review's list (or a fix) from whoever takes it up; none is
# fixed here.
UNFILED = {
    "NEW-1": (
        "4.B reads the visible text of every frame but not of open shadow "
        'roots: the same instruction ("press and hold the Space bar for 3 '
        'seconds") is a question inside a frame and is not read inside a '
        "shadow root, so 4.B PASSes."
    ),
    "NEW-2": (
        "The PASS of 4.C, 4.D, 4.E, 4.F and 5.D on a page whose stops are in "
        "a shadow root or a frame. The keyboard walk reached all 6 stops the "
        "page has (3 links, 2 fields, 1 button), so the PASS may well be "
        "right; it is listed because the grid's rule is never PASS, and "
        "nothing in the run says what a frame or a shadow root hid from the "
        "readings that sit beside the walk (focus pictures, the fields' "
        "answers)."
    ),
}

NO_OTHER_PAGES = "no other pages of the site were given"


def _site_cells() -> dict[str, Cell]:
    """9.A to 9.C and 19.A compare with other pages; the grid gives none, so
    they cannot be performed (rows A1, 'needs other pages')."""
    return {t: nr() for t in ("9.A", "9.B", "9.C", "19.A")}


def _frame_cells() -> dict[str, Cell]:
    """What a page whose content is in a frame (same site or another) gives:
    the two frame pages read the same today."""
    walk = wrong(Outcome.PASS, "NEW-2", UNFILED["NEW-2"])
    return {
        # Audio that starts by itself and has no control before it: a real FAIL.
        "2.A": fail(),
        # The looping video moves by itself; essential or not is a question.
        "2.B": nr(),
        "2.C": dna(
            "no text, counter or feed on the page updates by itself; the "
            "looping video is 2.B's"
        ),
        "2.D": dna("nothing on the page changes by itself except the video (2.B)"),
        "3.A": dna(
            "the only moving thing is a grey video that never changes "
            "brightness, so nothing flashes"
        ),
        "4.A": nr(),
        "4.B": nr(),
        "4.C": walk,
        "4.D": walk,
        "4.E": walk,
        "4.F": walk,
        "5.A": nr(),
        "5.B": nr(),
        "5.C": nr(),
        "5.D": walk,
        "5.F": nr(),
        "5.G": nr(),
        "5.H": nr(),
        **_site_cells(),
    }


# page -> test -> the cell. Review IDs in the `wrong` cells.
EXPECTED: dict[str, dict[str, Cell]] = {
    # An open shadow root with a form, a navigation block, a mouse-only
    # control, a sentence about holding a key, audio and a video.
    "shadow": {
        # N-01 (fixed for 2.A: guard CN, "2 sounds or videos played inside a
        # web component, and were not checked").
        "2.A": nr(),
        "2.B": wrong(
            Outcome.DNA,
            "N-01",
            "2.B's watcher reads media with the same document-only query as "
            "2.A did (`M.media`), so the looping video inside the shadow "
            'root is never seen: "Nothing on it moved". On the same page '
            "outside the root, or in a frame, 2.B is NEEDS REVIEW.",
        ),
        "2.C": dna(
            "no text, counter or feed on the page updates by itself; the "
            "looping video is 2.B's"
        ),
        "2.D": dna("nothing on the page changes by itself except the video (2.B)"),
        "3.A": dna(
            "the only moving thing is a grey video that never changes "
            "brightness, so nothing flashes"
        ),
        "4.A": wrong(
            Outcome.PASS,
            "D-03",
            'the mouse-only "Show details" is inside the shadow root; its '
            "click listener is read from the light DOM only.",
        ),
        "4.B": wrong(Outcome.PASS, "NEW-1", UNFILED["NEW-1"]),
        "4.C": wrong(Outcome.PASS, "NEW-2", UNFILED["NEW-2"]),
        "4.D": wrong(Outcome.PASS, "NEW-2", UNFILED["NEW-2"]),
        "4.E": wrong(Outcome.PASS, "NEW-2", UNFILED["NEW-2"]),
        "4.F": wrong(Outcome.PASS, "NEW-2", UNFILED["NEW-2"]),
        # D-01: no longer "no form fields"; guard CN holds them.
        "5.A": nr(),
        "5.B": nr(),
        "5.C": nr(),
        "5.D": wrong(Outcome.PASS, "NEW-2", UNFILED["NEW-2"]),
        "5.F": nr(),
        "5.G": nr(),
        "5.H": nr(),
        **_site_cells(),
    },
    # The same four things in a frame from the same site (frame-inner.html).
    "frame-same": {
        **_frame_cells(),
    },
    # The same frame from another site (localhost against 127.0.0.1): it is
    # recorded and replayed in full Chromium, so the frame is out of process.
    "frame-other": {
        **_frame_cells(),
    },
}


def _items() -> set[str]:
    """Review item IDs: a heading or a bold ID in the review file."""
    text = REVIEW.read_text()
    ids: set[str] = set()
    for m in re.finditer(r"^#### (.+)$", text, re.M):
        ids.update(re.findall(r"\b[A-Z]-\d{2}\b", m.group(1).split(" ", 1)[0]))
        ids.update(re.findall(r"\b[A-Z]-\d{2}\b", m.group(1)))
    ids.update(re.findall(r"^- \*\*([A-Z]-\d{2})\*\*", text, re.M))
    return ids


def _pages_in_folder() -> set[str]:
    return {p.stem for p in GRID.glob("*.html")} - HELPERS


# --- The table's own rules: fast, no browser --------------------------------


def test_every_grid_page_has_a_row_and_every_row_a_cell_for_every_test():
    assert set(EXPECTED) == _pages_in_folder()
    tests = {t.value for t in REGISTRY}
    for page, cells in EXPECTED.items():
        assert set(cells) == tests, (page, tests ^ set(cells))


def test_the_table_never_passes_and_does_not_apply_only_with_a_reason():
    for page, cells in EXPECTED.items():
        for test, c in cells.items():
            where = (page, test)
            if c.known_wrong is not None:
                assert c.outcome in (Outcome.PASS, Outcome.DNA), where
                assert c.nothing_for_it is None, where
                assert len(c.known_wrong[1]) > 20, where
                continue
            assert c.outcome is not Outcome.PASS, ("PASS is not a cell", where)
            if c.outcome is Outcome.DNA:
                assert c.nothing_for_it and len(c.nothing_for_it) > 20, where
            else:
                assert c.nothing_for_it is None, where


def test_a_known_wrong_cell_names_an_item_the_review_or_this_file_has():
    known = _items()
    for page, cells in EXPECTED.items():
        for test, c in cells.items():
            if c.known_wrong is None:
                continue
            item = c.known_wrong[0]
            assert item in known or item in UNFILED, (page, test, item)
    for item in UNFILED:  # an unfiled item is used at least once
        assert any(
            c.known_wrong and c.known_wrong[0] == item
            for cells in EXPECTED.values()
            for c in cells.values()
        ), item


# --- The run ----------------------------------------------------------------


@pytest.mark.parametrize("page", sorted(EXPECTED))
async def test_each_page_gives_each_cell_its_outcome(page, settings, server):
    out = await run_tt_tests(
        settings, f"{server.base}/grid/{page}.html", [TestId(t) for t in REGISTRY]
    )
    assert out.errors == [], out.errors
    by = {f.test_id.value: f for f in out.report.findings}
    assert set(by) == {t.value for t in REGISTRY}
    off = []
    for test, c in EXPECTED[page].items():
        f = by[test]
        if f.outcome is not c.outcome:
            fixed = " (a known wrong outcome: fixed? update the cell)" * bool(
                c.known_wrong
            )
            got = f"{test}: {f.outcome.value}, table says {c.outcome.value}"
            off.append(got + fixed)
        # The only outcomes that need no reason; never PASS on this page unless
        # the table says it is a known wrong outcome.
        if f.outcome is Outcome.PASS:
            assert c.known_wrong, (test, "a PASS the table does not own up to")
        if f.outcome is Outcome.DNA:
            assert c.nothing_for_it or c.known_wrong, (test, f.summary)
    assert not off, off
