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
    # None: the page has nothing for this test (see `nothing_here`); the run's
    # outcome there is not part of the table.
    outcome: Outcome | None
    # No outcome: why the page is not a case for this test (a plain page, for
    # a test about something the page does not have).
    nothing_here: str | None = None
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


def na(reason: str) -> Cell:
    return Cell(None, nothing_here=reason)


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

NEW3_AND_4 = {
    "NEW-3": (
        "4.E PASSes after a keyboard trap: the walk stopped inside the trap "
        'and 4.C says NEEDS REVIEW, but 4.E reads "each element we could '
        'reach" as all of them. The same cause as H-03, M-05 and F-11 (a '
        "trap counted as a complete walk), in a test they do not name."
    ),
    "NEW-4": (
        "4.A, 4.C, 4.D, 4.E and 4.F PASS on a page whose only form opens "
        "from a plain button: the walk reached the page's own 4 stops and "
        "never opened the panel, and no guard holds the PASS (rows A3, G4 "
        "only; the 5.x tests say NEEDS REVIEW for the same page)."
    ),
}
UNFILED.update(NEW3_AND_4)


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


def _plain(reason: str, tests: tuple[str, ...]) -> dict[str, Cell]:
    return {t: na(reason) for t in tests}


WALK = ("4.A", "4.B", "4.C", "4.D", "4.E", "4.F")
FIELDS = ("5.A", "5.C", "5.D", "5.F")
NOTHING_MOVES = {
    "2.C": dna("no text, counter or feed on the page updates by itself"),
    "2.D": dna("nothing on the page changes by itself"),
}
NO_MEDIA = {
    "2.A": dna("the page has no audio or video and plays no sound"),
    "2.B": dna("nothing on the page moves, blinks or scrolls"),
    "3.A": dna("nothing on the page flashes"),
    **NOTHING_MOVES,
}
CONTACT_FORM = dna(
    "the form is a plain contact form: no payment, legal agreement, change to "
    "saved data or test"
)
NO_CHECKING = dna(
    "the form has no required field and no typed field, so the page never "
    "checks it for errors"
)

EXPECTED.update(
    {
        # More than a cap: 31 images, then a long gap, then an animated image.
        # N-06; guard CN holds 2.B and 3.A. The rest of the page is plain.
        "cap": {
            "2.A": dna("the page has no audio or video and plays no sound"),
            "2.B": nr(),
            "2.C": NOTHING_MOVES["2.C"],
            "2.D": NOTHING_MOVES["2.D"],
            "3.A": nr(),
            **_plain(
                "the cap is on images; the page has no mouse-only control, "
                "trap, menu or hidden text",
                WALK,
            ),
            **_plain("a plain labelled form; the cap is on images", FIELDS),
            "5.B": nr(),
            "5.G": nr(),
            "5.H": CONTACT_FORM,
            **_site_cells(),
        },
        # A trap in mid-page: the Search field swallows Tab; a form follows.
        "trap": {
            **NO_MEDIA,
            "4.A": nr(),
            "4.B": nr(),
            "4.C": nr(),
            "4.D": nr(),
            "4.E": wrong(Outcome.PASS, "NEW-3", UNFILED["NEW-3"]),
            "4.F": nr(),
            "5.A": na(
                "5.A read all 3 fields, the 2 after the trap too (rows c1 to "
                "c3), and their labels are plain"
            ),
            "5.B": nr(),
            "5.C": nr(),
            "5.D": nr(),
            # The identical form PASSes 5.F on cap.html: only the trap differs.
            "5.F": wrong(
                Outcome.DNA,
                "M-05",
                "the form after the trap was never tested and the run reads "
                'that as "the page did not check the form"; the same form '
                "PASSes 5.F on cap.html. The same cause as M-05 (a trap "
                "counted as a complete test), here as DOES NOT APPLY.",
            ),
            "5.G": wrong(
                Outcome.DNA,
                "M-05",
                'as 5.F: the form after the trap was never tested, so "the '
                'page did not check the form".',
            ),
            "5.H": nr(),
            **_site_cells(),
        },
        # Starts late: a script plays a sound after 4.5 s, a block flashes
        # from 9 s; the watch is 6.5 s.
        "late": {
            "2.A": wrong(
                Outcome.DNA,
                "N-02",
                "a sound a script starts after about 4.5 s is not heard in "
                'the 6.5 s watch ("No audio played by itself").',
            ),
            "2.B": wrong(
                Outcome.DNA,
                "N-04",
                "a block that starts to flash after 9 s is past the 6.5 s "
                'watch ("Nothing on it moved").',
            ),
            "2.C": nr(),
            "2.D": nr(),
            "3.A": wrong(
                Outcome.DNA,
                "N-07",
                "flashing that starts after 9 s is past the capture "
                '("Nothing on this page flashes").',
            ),
            **_plain(
                "what starts late is audio and a flash; the page has no "
                "mouse-only control, trap, menu or hidden text",
                WALK,
            ),
            **_plain("a plain labelled form; what starts late is not a field", FIELDS),
            "5.B": nr(),
            "5.G": nr(),
            "5.H": CONTACT_FORM,
            **_site_cells(),
        },
        # lang="ru": Russian and Japanese labels, a Russian sentence about
        # holding a key, fields with a misleading aria-label.
        "language": {
            **NO_MEDIA,
            "4.A": na("no mouse-only control: nothing here depends on the words"),
            "4.B": wrong(
                Outcome.PASS,
                "M-03",
                "an English word list decides 4.B: the Russian sentence "
                '"Нажмите и удерживайте пробел 3 секунды" (press and hold '
                'the space bar for 3 seconds) is not found, so "nothing on '
                'this page asks you to press keys at a certain speed".',
            ),
            **_plain(
                "decided by the keyboard walk and focus pictures, not by the "
                "page's words",
                ("4.C", "4.D", "4.E", "4.F"),
            ),
            "5.A": na(
                "every field has a visible label with text (rows c1, c2); "
                "5.A asks only that one is there"
            ),
            "5.B": nr(),
            "5.C": wrong(
                Outcome.PASS,
                "H-02",
                "the visible labels are Cyrillic and Japanese, the announced "
                'names are "f1" and "x1": the word splitter keeps only '
                "a-z and 0-9, so no visible word is missing.",
            ),
            "5.D": na("two plain text fields; nothing on the page changes on input"),
            "5.F": NO_CHECKING,
            "5.G": dna(
                "the page did not check the form for errors, so there is no "
                "error to suggest a fix for"
            ),
            "5.H": CONTACT_FORM,
            **_site_cells(),
        },
        # Words hidden from people: a screen-reader-only label and a label
        # pushed off the screen by text-indent.
        "hidden-text": {
            **NO_MEDIA,
            **_plain("no mouse-only control, trap, menu or timing text", WALK),
            "5.A": wrong(
                Outcome.PASS,
                "H-01",
                "both labels' words are hidden from people (a clipped span, "
                "text-indent: -9999px) and still count as a visible label "
                "(rows c1, c2 on M2).",
            ),
            "5.B": nr(),
            "5.C": nr(),
            "5.D": na("two plain text fields; nothing on the page changes on input"),
            "5.F": NO_CHECKING,
            "5.G": dna(
                "the page did not check the form for errors, so there is no "
                "error to suggest a fix for"
            ),
            "5.H": CONTACT_FORM,
            **_site_cells(),
        },
        # A form behind a plain button (the panel is `hidden` until a click).
        "form-behind-button": {
            **NO_MEDIA,
            "4.A": wrong(Outcome.PASS, "NEW-4", UNFILED["NEW-4"]),
            "4.B": na(
                "no text about timing, hidden or shown: the panel holds only a form"
            ),
            "4.C": wrong(Outcome.PASS, "NEW-4", UNFILED["NEW-4"]),
            "4.D": wrong(Outcome.PASS, "NEW-4", UNFILED["NEW-4"]),
            "4.E": wrong(Outcome.PASS, "NEW-4", UNFILED["NEW-4"]),
            "4.F": wrong(Outcome.PASS, "NEW-4", UNFILED["NEW-4"]),
            # H-08: held by guard CN ("hidden until something opens it").
            **{t: nr() for t in ("5.A", "5.B", "5.C", "5.D", "5.F", "5.G", "5.H")},
            **_site_cells(),
        },
    }
)


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
            if c.outcome is None:
                assert c.nothing_here and len(c.nothing_here) > 20, where
                assert c.known_wrong is None and c.nothing_for_it is None, where
                continue
            assert c.nothing_here is None, where
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
        if c.outcome is None:
            continue  # the page has nothing for this test; the table says why
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
