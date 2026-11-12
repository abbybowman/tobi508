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


def apply_guards(
    f: Finding,
    guards: tuple[str, ...],
    report: Any,
    state: Any = None,
    count: tuple[str, ...] = (),
) -> Finding:
    """The shared page guards a spec declares in its front matter (their rows
    are in the spec and `_template.md`; this runs them). A guard moves a
    would-be PASS, or (CN only) a DOES NOT APPLY, to NEEDS REVIEW, never the
    other way (Abby, 2026-11-12). `state`: the check's evidence, whose `read`
    CN compares with the inventory; `count`: the spec's `count:` keys.

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
    return _count_guard(f, report, state, count)


# Guard CN's sentences, one per inventory key: (singular, plural) nouns, and
# where a part is. Wording only; the comparison is in _count_guard.
_NOUN = {
    "fields": ("form field", "form fields"),
    "contenteditable": ("editable text area", "editable text areas"),
    "forms_with_button": ("form with a button", "forms with a button"),
    "media": ("audio or video element", "audio or video elements"),
    "canvases": ("drawing area (canvas)", "drawing areas (canvas)"),
    "draggable": ("item moved by dragging", "items moved by dragging"),
    "landmarks": ("page region (landmark)", "page regions (landmarks)"),
    "links": ("link", "links"),
    "players": ("video player in a frame", "video players in frames"),
    "frames": ("frame", "frames"),
    "frames_unread": ("frame that could not be read", "frames that could not be read"),
    "shadow_roots": ("web component", "web components"),
    "closed_hosts": ("closed web component", "closed web components"),
}
_PLACE = {
    "shadow": (" inside a web component", " inside web components"),
    "frames": (" inside a frame", " inside frames"),
    "detached": (" outside the page", " outside the page"),
}
_PLAYED = {
    "": "",
    "light": " on the page",
    "shadow": " inside a web component",
    "frames": " inside a frame",
    "detached": " from a script",
}


def count_sentence(key: str, there: int, read: int) -> str:
    """One plain sentence for one gap of guard CN (`there` > `read`)."""
    name, _, part = key.partition(".")
    gap = there - read
    one = gap == 1
    was = "was" if one else "were"
    if name == "fields_hidden":
        place = _PLACE.get(part, ("", ""))[not one]
        return (
            f"{gap} form field{'' if one else 's'}{place} "
            f"{'is' if one else 'are'} hidden until something opens "
            f"{'it' if one else 'them'}, and {was} not checked."
        )
    if name == "media_played":
        return (
            f"{gap} {'sound or video' if one else 'sounds or videos'} played"
            f"{_PLAYED.get(part, '')}, and {was} not checked."
        )
    if name == "images":
        if read:
            return f"{there} images: only the first {read} were checked for animation."
        return f"{gap} image{'' if one else 's'} {was} not checked for animation."
    if name == "focusable":
        return (
            f"The page has {there} elements that take focus, and the keyboard "
            f"reached {read}."
        )
    noun = _NOUN.get(name, (name, name))[not one]
    place = _PLACE.get(part, ("", ""))[not one]
    verb = "tested" if name == "forms_with_button" else "checked"
    return f"{gap} {noun}{place} {was} not {verb}."


NOT_INVENTORIED = (
    "This page's contents could not be inventoried, so this test's result "
    "could not be confirmed."
)


def _page_label(page: str) -> str:
    return "This page" if page == "page" else f"Other page {page.lstrip('p')}"


def _count_guard(f: Finding, report: Any, state: Any, keys: tuple[str, ...]) -> Finding:
    """CN (`count:`): the page's inventory (`report.counts`, count.py) shows
    more of a thing than the test read (`state.read`): a would-be PASS or DOES
    NOT APPLY becomes NEEDS REVIEW (Abby, 2026-11-12). A key marked `@dna`
    holds DOES NOT APPLY only. FAIL and NOT TESTED are unchanged. A run made
    before the inventory existed (no `counts`) is left as it was."""
    if not keys or f.outcome not in (Outcome.PASS, Outcome.DNA):
        return f
    counts = getattr(report, "counts", None) or {}
    if not counts:
        return f
    read = getattr(state, "read", None) or {}
    sentences: list[str] = []
    trace: list[str] = []
    for page in ["page", *sorted(p for p in read if p != "page")]:
        c = counts.get(page)
        if c is None or c.error:
            head = (
                NOT_INVENTORIED
                if page == "page"
                else f"{_page_label(page)}'s contents could not be inventoried, "
                "so this test's result could not be confirmed."
            )
            sentences.append(head)
            trace.append(f"{page}: no inventory ({c.error if c else 'missing'})")
            continue
        got = read.get(page, {})
        for spec_key in keys:
            key, dna_only = spec_key.removesuffix("@dna"), spec_key.endswith("@dna")
            if dna_only and f.outcome is not Outcome.DNA:
                continue
            there, done = c.get(key), int(got.get(key, 0))
            if key.startswith("fields_hidden") and c.openers == 0:
                # Nothing on the page could show them: hidden for everyone,
                # as DHS's Baseline TC10.A-ic-dna-1 and -2 (Abby, 2026-11-12).
                there = 0
            if there > done:
                s = count_sentence(key, there, done)
                if page != "page":
                    s = f"On {_page_label(page).lower()}, {s[0].lower()}{s[1:]}"
                sentences.append(s)
                trace.append(f"{page} {key} {there} > read {done}")
    if not sentences:
        return f
    was = f.outcome.value
    f.outcome = Outcome.NEEDS_REVIEW
    f.rows = [*f.rows, "CN"]
    more = len(sentences) - 3
    f.summary = (
        f"{REVIEW_HEAD} "
        + " ".join(sentences[:3])
        + (f" ({more} more in the report.)" if more > 0 else "")
    )
    f.note = TEST_NOT_PERFORMED_NOTE
    f.rationale += f" Guard CN (would have been {was}): " + "; ".join(trace) + "."
    return f
