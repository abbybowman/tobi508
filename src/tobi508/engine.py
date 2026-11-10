"""Shared rules machinery: first-match tables and the template's page outcome.

Every rules spec (specs/rules/_template.md) has the same shape: applicability
rows, instance rows (first match wins) and page rows G1-G5. This module runs
those tables; the rows themselves, with their conditions, live in each test's
module (e.g. t4c.py) and come from its spec. Nothing here decides an outcome
on its own.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tobi508.models import REVIEW_HEAD, TEST_NOT_PERFORMED_NOTE, Finding, Outcome


@dataclass(frozen=True)
class Row:
    id: str
    when: Callable[[Any], bool]
    outcome: Outcome | None  # None: not decisive, continue down the table
    source: str = ""


def first_match(rows: list[Row], evidence: Any) -> Row | None:
    """The first row whose condition holds and that gives an outcome. Rows with
    outcome None that match are skipped (e.g. M5 "not an exit; continue")."""
    for row in rows:
        if row.outcome is not None and row.when(evidence):
            return row
    return None


@dataclass
class PageEvidence:
    """Inputs to the template's table 3b."""

    applicability: Row  # the matched section 1 row
    instances: list[tuple[str, Outcome]]  # (instance id, outcome)
    incomplete: list[str]  # reasons evidence is incomplete
    complete_for_pass: bool  # the test's G4 completeness condition


PAGE_ROWS = [
    Row(
        "G1",
        lambda e: e.applicability.outcome in (Outcome.DNA, Outcome.NEEDS_REVIEW),
        None,
    ),
    Row("G2", lambda e: any(o is Outcome.FAIL for _, o in e.instances), Outcome.FAIL),
    Row(
        "G3",
        lambda e: (
            bool(e.incomplete) or any(o is Outcome.NEEDS_REVIEW for _, o in e.instances)
        ),
        Outcome.NEEDS_REVIEW,
    ),
    Row(
        "G4",
        lambda e: (
            e.complete_for_pass and all(o is Outcome.PASS for _, o in e.instances)
        ),
        Outcome.PASS,
    ),
    Row("G5", lambda e: True, Outcome.NEEDS_REVIEW),
]


def page_outcome(e: PageEvidence) -> tuple[str, Outcome]:
    """Table 3b, first match wins. G1 returns section 1's outcome."""
    if PAGE_ROWS[0].when(e):
        return "G1", e.applicability.outcome  # type: ignore[return-value]
    row = first_match(PAGE_ROWS[1:], e)
    assert row is not None  # G5 always matches
    return row.id, row.outcome  # type: ignore[return-value]


def _names(items: list[str], more: str = "") -> str:
    shown = [f'"{i}"' for i in items[:3]]
    left = len(items) - len(shown)
    return ", ".join(shown) + (f" and {left} more" if left > 0 else "") + more


UNRECORDED_CODE_SENTENCE = (
    "The page loads more code when it is used, for example when you type in a "
    "field, and the recording of the page does not have that code, so what "
    "happens when you press keys or type could not be checked."
)


def apply_guards(f: Finding, guards: tuple[str, ...], report: Any) -> Finding:
    """The shared page guards a spec declares in its front matter (their rows
    are in the spec and `_template.md`; this runs them). A guard only moves a
    would-be PASS to NEEDS REVIEW, never the other way.

    GU (`unrecorded-code`): the recording lacks code that the page's own
    scripts name and load when used, so a replay cannot run the page's
    handlers; a test that presses keys or types cannot PASS on it (Abby,
    2026-11-09)."""
    if (
        "unrecorded-code" in guards
        and f.outcome is Outcome.PASS
        and getattr(report, "unrecorded_code_count", 0) > 0
    ):
        f.outcome = Outcome.NEEDS_REVIEW
        f.rows = [*f.rows, "GU"]
        f.summary = f"{REVIEW_HEAD} {UNRECORDED_CODE_SENTENCE}"
        f.note = TEST_NOT_PERFORMED_NOTE
        f.rationale += (
            f" Guard GU: {report.unrecorded_code_count} script(s) the page "
            "loads when used are not in the recording."
        )
    rv = getattr(report, "reveal", None) or {}
    # RV (`reveal`): something that opens was not opened or not read, so what
    # is inside it was not checked (Abby, 2026-11-09, fix 9b).
    if "reveal" in guards and f.outcome is Outcome.PASS and rv:
        bad = [x["name"] for x in rv.get("not_opened", [])] + list(
            rv.get("read_failed", [])
        )
        if bad or rv.get("failed"):
            f.outcome = Outcome.NEEDS_REVIEW
            f.rows = [*f.rows, "RV"]
            f.summary = (
                f"{REVIEW_HEAD} The page has menus or sections that open, and "
                f"some could not be opened or read ({_names(bad)}), so what is "
                "inside them was not checked."
                if bad
                else f"{REVIEW_HEAD} The page's menus and sections could not be "
                "opened, so what is inside them was not checked."
            )
            f.note = TEST_NOT_PERFORMED_NOTE
            f.rationale += " Guard RV: something that opens was not opened or read."
    # RC (`reveal-content`): opened content holds things this test checks,
    # and the keyboard walk and the fields' fill do not go through opened
    # content until phase 2 and 3 of fix 9b are built.
    if (
        "reveal-content" in guards
        and f.outcome is Outcome.PASS
        and rv.get("opened_with_focusable", 0) > 0
    ):
        f.outcome = Outcome.NEEDS_REVIEW
        f.rows = [*f.rows, "RC"]
        f.summary = (
            f"{REVIEW_HEAD} The page has menus or sections that open to show "
            "more controls, and this test has not checked inside them yet, so a "
            "person needs to check what they hold."
        )
        f.note = TEST_NOT_PERFORMED_NOTE
        f.rationale += (
            f" Guard RC: {rv['opened_with_focusable']} opened section(s) hold "
            "controls that were not checked."
        )
    return f
