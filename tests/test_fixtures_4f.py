"""4.F (2.4.3-focus-order-meaning) on custom fixtures (no ACT rule covers
2.4.3). Expected outcomes and scripted J1 answers live here, never in a page."""

from __future__ import annotations

import pytest

from tobi508.checks import t4f
from tobi508.models import TestId

from .conftest import FIXTURES
from .harness import instance_rows, run_check

# "choice" is what a correct judge answers where J1 is asked (test data).
EXPECTED: dict[str, dict] = {
    "f01-logical-order": {"outcome": "PASS", "rows": ["M4"]},
    "f02-address-form-interleaved": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S1", "S5"},
    },
    # 1.3.0: the form at the end of a long page; image A is the crop around
    # the stops the signals name (test_order_image_is_cropped_to_the_signals).
    "f19-long-report-form-interleaved": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S1"},
    },
    "f03-footer-first-tabindex": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S1"},
    },
    "f04-independent-columns-reordered": {
        "outcome": "PASS",
        "choice": "preserves",
        "signals": {"S3"},
    },
    "f05-nav-after-main": {"outcome": "PASS", "choice": "preserves", "signals": {"S3"}},
    "f06-social-icons-reordered": {
        "outcome": "DNA",
        "choice": "does_not_matter",
        "signals": {"S3"},
    },
    "f07-one-link": {"outcome": "DNA", "rows": []},
    # 1.14.0 (#136 step 33c): Tab going down one footer column and up to the
    # top of the next is no signal (round 3's Drupal footers). The near
    # miss: a jump up into a column that starts higher than the one left.
    "f30-footer-link-columns": {"outcome": "PASS", "rows": ["M4"]},
    "f31-footer-column-starts-higher": {
        "outcome": "PASS",
        "choice": "preserves",
        "signals": {"S3"},
    },
    # A menu button whose menu the arrow keys enter and Tab leaves is no
    # signal (SDE's "All"); a disclosure with no popup, whose links Tab skips,
    # still is.
    "f32-menu-button-arrow-keys": {"outcome": "PASS", "rows": ["M4", "M4"]},
    # 1.15.0 (#136): Tab enters a trap partway (round 2's 5340 timeline) and
    # wraps from its last control to its first. That wrap is the trap going
    # round, not the order: no signal; the walk never wrapped, so NEEDS REVIEW.
    # The scripted answer would FAIL the page if the wrap were a signal.
    "f34-trap-entered-midway": {
        "outcome": "NEEDS_REVIEW",
        "choice": "does_not_preserve",
        "rows": ["M4"],
    },
    "f33-disclosure-tab-skips-content": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S6"},
    },
    # Fix 12 (4.F 1.7.0): a different order from the one drawn is not
    # "does not preserve" by itself. Cards reached right to left, a card's
    # buttons reached in the other order than drawn: meaning and operation
    # hold. The same layout with numbered steps out of sequence must FAIL.
    "f20-cards-reached-right-to-left": {
        "outcome": "PASS",
        "choice": "preserves",
        "signals": {"S3"},
    },
    "f21-card-buttons-in-other-order": {
        "outcome": "PASS",
        "choice": "preserves",
        "signals": {"S3"},
    },
    # Fix 13 (4.F 1.8.0): a skip link shown only on focus, a one-pixel
    # screen-reader link and two independent columns. The first two have no
    # visible box on a fresh load, so image A draws no badge for them.
    "f23-stops-with-no-visible-box": {
        "outcome": "PASS",
        "choice": "preserves",
        "signals": {"S3"},
    },
    # Step 8 (the grid's NEW-2): f03 inside a web component and inside a
    # frame from another site still FAILs, the twins of the grid's PASSes.
    "f24-positive-tabindex-in-web-component": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S1"},
    },
    "f25-positive-tabindex-in-frame": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S1"},
    },
    "f22-steps-out-of-sequence": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S3"},
    },
    "f08-menu-not-adjacent": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S6"},
    },
    "f09-disclosure-adjacent": {"outcome": "PASS"},
    "f10-modal-keeps-focus": {"outcome": "PASS", "rows_include": ["M3"]},
    "f11-modal-lets-focus-escape": {"outcome": "FAIL", "rows_include": ["M2"]},
    "f12-native-dialog": {"outcome": "PASS", "rows_include": ["M3"]},
    # 1.16.0 (#135 step 15): every accordion is opened and walked (pass R
    # opened 6 of 8, NEEDS REVIEW); each one's next Tab goes into it.
    "f13-eight-accordions": {"outcome": "PASS"},
    # 1.16.0 (#135 step 15, Abby 2026-11-23, option a): Tab reaches a menu's
    # options only after other stops (F85): S6, and J1 decides.
    "f36-menu-options-reached-late": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S6"},
    },
    # Neither Tab nor the arrows reach the options: 4.A's finding, not an
    # order; no signal.
    # 1.16.0 (Abby, 2026-11-23; round 1's Careers page): a tab whose panel
    # Tab reaches right after the rest of its tab list: no signal.
    "f38-tab-panel-after-tab-list": {
        "outcome": "PASS",
        "says": "Tab goes through the rest of its tab list and then into its panel",
    },
    # The near miss: other links come between the tab list and the panels.
    "f39-tab-panel-after-other-links": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S6"},
    },
    "f37-menu-nothing-reaches": {
        "outcome": "PASS",
        "rows": ["M4", "M4"],
        "says": "keyboard access (TT 4.A) reports it",
    },
    "f14-backward-order-differs": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S4"},
    },
    # Focus reads "Step 3, Step 4, Step 1, Step 2": numbered steps out of
    # sequence (was "unsure"; the judge eval's agent was right, Abby 2026-10-31).
    # Post-round 1 fix 16: a site overlay (role=dialog, aria-modal) that
    # shows itself is not the dialog the menu button opened (it names its
    # list with aria-controls), so Tab leaving it is not M2. The overlay sits
    # between the button and its menu, so Tab after opening the menu lands
    # in the overlay: J1 decides (judge eval run 18: does_not_preserve, which
    # a careful tester would say too).
    "f16-site-overlay-not-the-menu": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S6"},
    },
    # Post-round 1 fix 16 (4.F 1.2.0's rubric): a card grid read row by row,
    # each card's image link then its title link, preserves meaning.
    "f17-card-grid-row-by-row": {"outcome": "PASS", "choice": "preserves"},
    # Post-round 1 fix 16 (1.2.0): filter boxes drawn apart from their
    # labels are placed by their labels, so a one-column list raises no
    # order signal.
    "f18-filter-boxes-drawn-apart": {"outcome": "PASS", "rows": ["M4"]},
    # 1.11.0: a page that scrolls smoothly is placed by boxes read with the
    # scroll in one call; read apart, round 2's date fields and sidebar links
    # were placed lower than they are and raised S3.
    "f26-smooth-scroll-in-order": {"outcome": "PASS", "rows": ["M4"]},
    # 1.11.0: an id made on each load is not a different element; round 2's
    # video player raised S4 though Shift+Tab was the exact reverse of Tab.
    "f27-new-id-each-load": {"outcome": "PASS", "rows": ["M4"]},
    # 1.11.0: a list in a box that scrolls by itself is placed where it lies
    # in the box's content; placed where focus scrolled it, round 2's
    # sidebar links sat above the link before them and raised S3.
    "f28-scroll-box-in-order": {"outcome": "PASS", "rows": ["M4"]},
    # The nearest page that must still raise S3 and FAIL: numbered steps in
    # a scroll box, drawn 1 to 5 (CSS order) and reached 3, 1, 5, 2, 4 (as
    # f22, inside the box). A first version drew the box bottom to top with
    # Tab following its numbers; the judge eval's agent said "preserves",
    # which a careful tester could say too.
    # f28's list inside a frame 400 px down the page. A stop in a frame was
    # placed on the page, but its scroll box where it sits in the frame, so
    # the first topic read as above the link before it and raised S3 (round
    # 2's timeline tool, #136).
    "f35-scroll-box-in-frame-in-order": {"outcome": "PASS", "rows": ["M4"]},
    "f29-scroll-box-steps-out-of-sequence": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S3"},
    },
    "f15-columns-arbitrary": {
        "outcome": "FAIL",
        "choice": "does_not_preserve",
        "signals": {"S3"},
    },
}


def test_every_fixture_is_listed():
    assert {p.stem for p in (FIXTURES / "4f").glob("*.html")} == set(EXPECTED)


def _cropped(settings, got) -> None:
    """1.3.0: on a long page, J1's image A is the parts of the order image
    around the stops the signals name; the full page stays evidence. A full
    page shrunk to 768 px was unreadable (development run 9)."""
    from PIL import Image

    [q] = got["asked"]
    crop, full = q.input["image_a_order"], q.evidence_paths[-1]
    assert crop.endswith("4f-order-crop.png") and full.endswith("4f-order.png"), q
    assert "around the elements" in q.input["image_shows"]
    run, rid = settings.runs_dir / got["run_id"], got["run_id"]
    c = Image.open(run / crop.split(rid + "/", 1)[1])
    f = Image.open(run / full.split(rid + "/", 1)[1])
    assert c.height * 3 < f.height, (c.size, f.size)


def _undrawn(settings, got) -> None:
    """1.8.0: a stop with no visible box gets no badge; the order list says
    so in text (round 2: C saw "empty boxes 28, 30 and 32")."""
    from PIL import Image

    [q] = got["asked"]
    off = {o["name"]: o for o in q.input["order"] if o.get("drawn") is False}
    assert set(off) == {"Skip to bulletins", "Accessibility statement"}, q.input
    assert all(o["page_box"] is None for o in off.values())
    assert all(o["drawn"] if "drawn" in o else True for o in q.input["order"][2:])
    assert "drawn: false" in q.question and "drawn: false" in q.rubric
    # No red box or badge where the hidden skip link would have been (the
    # off-screen box, then the page's top-left corner when focused).
    rid = got["run_id"]
    full = q.evidence_paths[-1]
    img = Image.open(settings.runs_dir / rid / full.split(rid + "/", 1)[1]).convert(
        "RGB"
    )
    red = [
        (x, y)
        for x in range(0, 80)
        for y in range(0, 36)
        if (lambda p: p[0] > 180 and p[1] < 40 and p[2] < 40)(img.getpixel((x, y)))
    ]
    assert not red, "a badge was drawn at the hidden skip link's focused place"


@pytest.mark.parametrize("name", sorted(EXPECTED))
async def test_fixture(name, settings, server):
    e = EXPECTED[name]
    got = await run_check(
        settings, f"{server.base}/4f/{name}.html", TestId.T4F, e.get("choice")
    )
    f = got["finding"]
    assert f.outcome.value == e["outcome"], (f.rows, f.summary)
    if name == "f19-long-report-form-interleaved":
        _cropped(settings, got)
    if name == "f23-stops-with-no-visible-box":
        _undrawn(settings, got)
    if "rows" in e:
        assert [r.split("[")[0] for r in instance_rows(f)] == e["rows"], f.rows
    if "rows_include" in e:
        assert set(e["rows_include"]) <= {r.split("[")[0] for r in instance_rows(f)}, (
            f.rows
        )
    if "signals" in e:
        found = {
            c
            for r in f.rows
            if "[" in r
            for c in r.split("[")[1].rstrip("]").split(",")
        }
        assert e["signals"] <= found, (f.rows, f.summary)
    if "says" in e:
        assert e["says"] in f.summary, f.summary


async def test_unsure_goes_to_a_person(settings, server):
    # M9: an unsure answer is NEEDS REVIEW (f15 is the page; its right answer
    # is does_not_preserve, but any page asking J1 would do).
    got = await run_check(
        settings, f"{server.base}/4f/f15-columns-arbitrary.html", TestId.T4F, "unsure"
    )
    assert got["finding"].outcome.value == "NEEDS_REVIEW"


async def test_backward_order_is_in_the_question(settings, server):
    # Judge eval 2026-10-31: without the Shift+Tab order the agent judged only
    # the forward order on f14 and answered "preserves" (a false PASS).
    from tobi508.pipeline import run_tt_tests

    out = await run_tt_tests(
        settings, f"{server.base}/4f/f14-backward-order-differs.html", [TestId.T4F]
    )
    [q] = out.open_questions
    assert [s["name"] for s in q.input["backward"]] == ["Four", "Two", "Three", "One"]
    # 1.11.0: each by its number in input.order, so the two lists line up.
    assert [s["n"] for s in q.input["backward"]] == [4, 2, 3, 1]
    assert "Shift+Tab" in q.question


def _si(n: int) -> t4f.StopInfo:
    return t4f.StopInfo(
        path_key=f"#s{n}",
        css_path=f"#s{n}",
        frame=[],
        role="link",
        name=f"Link {n}",
        modal=False,
        collapsed=False,
        unreliable=False,
        info={"page": [0, n * 20, 50, 10]},
    )


def test_j1_is_shown_every_element_a_signal_names_past_60():
    """1.13.0 (#136 step 33a): round 3's Drupal footers were stops 61 on, so
    the S3 signals named links J1's order list and picture did not hold, and
    J1 was unsure for that. The list keeps the first 60 and adds each named
    stop with the one before it, numbered by place; the question says so."""
    fwd = [_si(n) for n in range(1, 81)]
    sig = {
        "code": "S3",
        "at": "#s75",
        "words": 'focus jumps back up the page from "Link 74" to "Link 75"',
    }
    assert t4f.numbered(fwd, [sig]) == [*range(1, 61), 74, 75]
    st = t4f.State4F(p1={}, p2={}, forward=fwd, stops=80, inventory=80)
    st.instances.append(t4f.Inst4F(id="o1", kind="O", label="the page", signals=[sig]))
    st.numbered = t4f.numbered(fwd, [sig])
    (q,) = t4f.questions_for(st, [])
    assert [o["n"] for o in q.input["order"]][-3:] == [60, 74, 75]
    assert "a jump in n is elements left out" in q.question
    # A page within 60 stops: no gap, no extra sentence.
    short = t4f.State4F(p1={}, p2={}, forward=fwd[:30], stops=30, inventory=30)
    short.instances.append(
        t4f.Inst4F(id="o1", kind="O", label="the page", signals=[{**sig, "at": "#s20"}])
    )
    (q2,) = t4f.questions_for(short, [])
    assert len(q2.input["order"]) == 30 and "jump in n" not in q2.question
