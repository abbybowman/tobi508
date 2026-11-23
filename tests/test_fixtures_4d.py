"""4.D (2.4.7-focus-visible): W3C ACT rule oj04fd cases (with DHS TT 5.1
results) and custom fixtures for gaps. Expected outcomes live in
tests/fixtures/act/manifest.json and here, never in a page."""

from __future__ import annotations

import json
import re

import pytest

from tobi508.models import TestId

from .conftest import ACT_ROOT
from .harness import instance_rows, run_check

MANIFEST = json.loads((ACT_ROOT / "manifest.json").read_text())
ACT = {c["id"]: c for c in MANIFEST["cases"] if c["tt_test"] == "4.D"}
# What a correct judge answers where J1 is asked (test data).
ACT_CHOICE: dict[str, str] = {"dd9628d8": "yes"}


def test_oj04fd_cases_are_the_7_approved():
    assert len(ACT) == 7
    for c in ACT.values():
        assert c["dhs_tt51"] == c["expected"], c["id"]  # DHS agrees on all 7


@pytest.mark.parametrize("case_id", sorted(ACT))
async def test_act_case(case_id, settings, act_server):
    c = ACT[case_id]
    got = await run_check(
        settings, f"{act_server}/{c['path']}", TestId.T4D, ACT_CHOICE.get(case_id)
    )
    f = got["finding"]
    assert f.outcome.value == c["expected"], (f.rationale, f.summary, instance_rows(f))


# Custom fixtures (specs/rules/4d-focus-visible.md). "choice" is the scripted J1
# answer where J1 is asked.
EXPECTED: dict[str, dict] = {
    "f01-background-change": {"outcome": "PASS"},
    "f02-text-field-caret": {"outcome": "PASS"},
    "f03-skip-link": {"outcome": "PASS"},
    "f04-radio-label-highlight": {"outcome": "PASS"},
    "f05-outline-transition": {"outcome": "PASS"},
    "f06-slideshow-behind-links": {"outcome": "FAIL", "choice": "no"},
    "f07-sticky-header-covers": {"outcome": "FAIL"},
    # Post-round 1 fix 11 (1.2.0): the title's focus outline is drawn but
    # clipped, and the card marks focus elsewhere; 0 px where the title is
    # is no clear view (M4), not a FAIL.
    "f15-card-title-outline-clipped": {"outcome": "NEEDS_REVIEW", "rows": ["M4"]},
    # 1.3.0: focus shifts each link's text colour too little to see, and a
    # counter 160 px to the first link's right updates by itself; J1 gets
    # where the changed pixels sit.
    "f16-faint-color-and-counter": {"outcome": "NEEDS_REVIEW", "choice": "unsure"},
    "f08-focusable-iframe": {"outcome": "PASS"},
    # F-02 (1.8.0): the page shifts while link 1 (outline: none) is pictured.
    # The move is not a focus style, since the link is not shown only on
    # focus: NEEDS REVIEW (PASS before). f03 above is the nearest case that
    # must still PASS: a skip link shown only on focus.
    "f22-page-shifts-link-without-outline": {"outcome": "NEEDS_REVIEW"},
    # C-07 (1.7.0): a script moves focus off link 3 at once, so the walk never
    # stops on it: 4.D checked 10 of the page's 11 elements and may not say
    # PASS. f21 is the same page with every element reached: still PASS.
    # 4.D 1.11.0: 4 links reached only by Shift+Tab are past the 5 replays
    # for a before image: J1 looks at their clear rings.
    "f20-script-moves-focus-off-one-link": {"outcome": "NEEDS_REVIEW", "choice": "yes"},
    "f21-eleven-links-all-reached": {"outcome": "PASS"},
    # F-01 (Abby approved, 2026-11-12): a menubar of 8 items with a clear
    # outline on each. The loop stopped on item 7 with no "after" picture, so
    # it was NEEDS REVIEW for any menu of 7 or more; the first five items
    # stand for the rest (spec, widget pass W), and the cap now steps back
    # once so the last item reached has its picture too.
    "f17-menubar-of-eight-items": {"outcome": "PASS", "rows": ["M6"]},
    # A radio group counts once (Tab lands on one radio of it; P1 on the
    # first, P2 on the last). f23 has three: 2 of the page's 4 radios and
    # link are stops, and the group is one candidate, so every element was
    # reached: PASS (guard CN said NEEDS REVIEW). f24 is the nearest page that
    # must stay NEEDS REVIEW: a script moves focus off every radio at once, so
    # the group is never a stop and the walk is not complete (row WK; guard CN
    # holds it too).
    "f23-radio-group-of-three": {"outcome": "PASS"},
    "f24-radio-group-focus-moved-off": {"outcome": "NEEDS_REVIEW", "page_rows": ["WK"]},
    # Row WK (1.9.0, step 6d): a loop is complete when the other pass reached
    # every element. f25: P1 loops between two buttons, Shift+Tab from the end
    # reaches the rest: 6 of 6 reached, PASS. f26 is the nearest page that must
    # stay NEEDS REVIEW: a script skips link 2 in both directions, 3 of 4.
    "f25-loop-both-passes-reach-all": {"outcome": "PASS", "walk": (6, 6)},
    "f26-link-skipped-by-script-both-ways": {
        "outcome": "NEEDS_REVIEW",
        "page_rows": ["WK"],
        "walk": (3, 4),
    },
    "f09-faint-outline": {"outcome": "NEEDS_REVIEW", "choice": "unsure"},
    # Fix 26 (4.D 1.4.0): small round icons. The pictures carry context and
    # are scaled up for the judge, and J1's input says the changed pixels
    # form a ring. F18's ring is clear (PASS); F19's is nearly the page's
    # colour (stays NEEDS REVIEW: a ring is a shape, not how visible it is).
    "f18-small-icon-clear-ring": {"outcome": "PASS", "choice": "yes"},
    "f19-small-icon-faint-ring": {"outcome": "NEEDS_REVIEW", "choice": "unsure"},
    # ~59-62 s alone on the 2026-11-01 container (was ~55 s when the guard was
    # set), and over 65 s now and then under -n 8 with the full suite: 75 s
    # still catches a real slowdown (Abby, 2026-11-01). Pausing the mutation
    # log around 4.D's own screenshots costs ~2 s here (solutions/time-budget.md).
    "f10-100-links": {"outcome": "PASS", "max_s": 75},
    "f11-blur-on-focus": {"outcome": "FAIL", "rows": ["M3"]},
    # Step 8 (the grid's NEW-2): a link whose focus shows nothing, inside a
    # web component and inside a frame from another site, still FAILs (M8):
    # the twins of the grid's PASSes.
    # 4.D 1.11.0: the 16 px region takes in 36 px of a neighbour's change, so
    # the link is no longer M8; those pixels did not change both ways, so J1
    # looks (M7) and a correct judge says no (M10): still FAIL.
    "f27-no-focus-indicator-in-web-component": {
        "outcome": "FAIL",
        "rows": ["M10"],
        "choice": "no",
    },
    "f28-no-focus-indicator-in-frame": {"outcome": "FAIL", "rows": ["M8"]},
    # 4.D 1.10.0: f11's focus dropped on focus, inside a web component: the
    # focus log names it by its host, so M3 sees it (it was WK, NEEDS REVIEW).
    "f29-blur-on-focus-in-web-component": {"outcome": "FAIL", "rows": ["M3"]},
    # Step 27 (#135): round 3's blog. The picture's own link shows nothing
    # with focus; the next link's focus ring, drawn round the whole picture,
    # is in the first link's "off" picture, and M6 passes it on those pixels.
    # 4.D 1.11.0: M6 needs the change confirmed both ways, against a before
    # picture, so J1 looks (M7); a correct judge sees the ring only in image
    # A (the next link's) and nothing on the link in B or D: no (M10). The
    # caption and title links keep M6. test_f30_before_picture checks the
    # counts.
    # #135 (round 2's SVS 14592, key Pass): the player's group gets a new id
    # on every load, so P2's stops have other paths than P1's; Shift+Tab
    # leaves them under the sticky header, where they showed nothing (M8).
    # They are P1's stops (same role, name and place), which P1 pictured.
    "f31-new-id-each-load-under-sticky-header": {"outcome": "PASS"},
    # 4.D 1.12.0 (#135, round 2's SVS 5340, key Pass): the tab's outline is
    # clipped by its own scrolling tab list, which answers at the tab's centre.
    # Clipped by its container, not covered: M4 (NEEDS REVIEW), not M8.
    "f32-tab-clipped-by-its-tab-list": {"outcome": "NEEDS_REVIEW", "rows": ["M4"]},
    # 4.D 1.13.0 (step 15, #135): the stops inside what a menu opened are
    # instances. F33: the menu stays open, so Shift+Tab back through it gives
    # before pictures and its items pass (M6), with no guard RC. F34: it
    # closes when focus leaves, so no before pictures: J1 looks at its clear
    # rings (a correct judge: yes). F35: its items show nothing: M8, FAIL.
    "f33-menu-stays-open-items-ring": {"outcome": "PASS"},
    "f34-menu-closes-when-focus-leaves": {"outcome": "PASS", "choice": "yes"},
    # F35's last item has the next link's ring in its off picture, changed one
    # way only: J1, and a correct judge says no (the blog's pattern).
    "f35-menu-items-show-no-focus": {"outcome": "FAIL", "rows": ["M8"], "choice": "no"},
    "f30-next-outline-over-image-link": {
        "outcome": "FAIL",
        "choice": "no",
        "rows": ["M6", "M10"],
    },
    "f12-listbox-activedescendant": {"outcome": "PASS"},
    "f13-listbox-no-highlight": {"outcome": "FAIL"},
    # 4.D 1.11.0: the first item's pixels were its neighbour's (changed one
    # way only): J1, and a correct judge says no.
    "f14-menubar-roving-no-indicator": {"outcome": "FAIL", "choice": "no"},
}


def _f16_pixels(asked) -> None:
    """1.3.0: J1's input counts the changed pixels on the element, touching
    it (within 8 px) and elsewhere. In F16 focus shifts the links' text colour
    faintly, and a counter beside the first link changes by itself."""
    px = {q.instance: q.input["changed_pixels"] for q in asked}
    assert px and all(p["on_element"] > 0 for p in px.values()), px
    assert any(p["elsewhere"] > 0 for p in px.values()), px  # the counter


def _f19_ring(asked) -> None:
    """1.6.0 (fix 26): a faint 1 px ring round a 44 px circle. J1's input says
    the changed pixels run along all four sides (ring), and the pictures are
    the enlarged copies; a ring is a shape, not a verdict (still unsure)."""
    assert asked
    for q in asked:
        px = q.input["changed_pixels"]
        assert px.get("ring") is True and len(px["sides_changed"]) == 4, px
        for k in ("image_a_off", "image_b_on", "image_c_changed"):
            assert "-x" in q.input[k] and q.input[k].endswith(".png"), q.input


def _f16_no_ring(asked) -> None:
    """A colour shift on link text is no ring."""
    assert asked and all("ring" not in q.input["changed_pixels"] for q in asked)


# Checks on the questions a fixture's run asks (on test_fixture's own run).
ASKED = {
    "f16-faint-color-and-counter": lambda a: (_f16_pixels(a), _f16_no_ring(a)),
    "f19-small-icon-faint-ring": _f19_ring,
}


def test_every_fixture_is_listed():
    from .conftest import FIXTURES

    assert {p.stem for p in (FIXTURES / "4d").glob("*.html")} == set(EXPECTED)


@pytest.mark.parametrize("name", sorted(EXPECTED))
async def test_fixture(name, settings, server):
    import time

    e = EXPECTED[name]
    t0 = time.monotonic()
    got = await run_check(
        settings, f"{server.base}/4d/{name}.html", TestId.T4D, e.get("choice")
    )
    took = time.monotonic() - t0
    f = got["finding"]
    assert f.outcome.value == e["outcome"], (f.rows, f.summary)
    if "rows" in e:
        assert set(e["rows"]) <= set(instance_rows(f)), f.rows
    if "page_rows" in e:  # the finding's own rows (a guard), not an instance's
        assert set(e["page_rows"]) <= set(f.rows), f.rows
    if "walk" in e:  # row WK's evidence: elements reached of elements counted
        r, c = e["walk"]
        assert f"Walk: reached {r} of {c}" in f.rationale, f.rationale
    if "max_s" in e:
        assert took < e["max_s"], took
    if name in ASKED:
        ASKED[name](got["asked"])


def test_a_link_moved_by_the_page_while_pictured_is_not_failed():
    """Post-round 1 fix 11 (4.D 1.2.0): on NASA's Artemis III page a layout
    shift moved links between their measure and the pictures, so the region
    compared was empty and they failed at 0 px. Moved with almost no change
    is no clear view (M4); moved with a clear change still counts (a skip
    link that slides in)."""
    from tobi508.checks.t4d import Attempt, Inst4D, _best

    def inst(px: float, only: bool = False) -> Inst4D:
        e = {
            "moved": True,
            "shown_only_on_focus": only,
            "changed": [],
            "on": "on.png",
            "off": "off.png",
        }
        a = Attempt(
            pass_name="P1",
            step=1,
            keys=["Tab"],
            unreliable=False,
            extras=e,
            changed_px=px,
            strong_px=px,
            mask_fraction=0.0,
        )
        return Inst4D(id="d1", subject="#a", label={}, attempts=[a])

    stuck = inst(0.0)
    assert _best(stuck) is None
    assert "moved on the page" in stuck.attempts[0].extras["incomplete"]
    slid_in = inst(3600.0, only=True)
    assert _best(slid_in) is slid_in.attempts[0]
    # F-02 (1.8.0): not shown only on focus and no style change: the move
    # proves nothing and the pixels may be the page's shift: no clear view.
    shifted = inst(3600.0, only=False)
    assert _best(shifted) is None
    assert "moved on the page" in shifted.attempts[0].extras["incomplete"]


def test_the_reason_a_last_step_has_no_after_picture_is_kept(monkeypatch, tmp_path):
    """F-04: `Attempt` copies its `extras`, so a reason written to the dict
    afterwards was lost and the sentence said "the images could not be
    compared". The walk's last step has no step after it: no "after" read."""
    from types import SimpleNamespace as NS

    from tobi508.checks import t4d

    monkeypatch.setattr(t4d.t4e, "classify", lambda *a, **k: (None, False))
    e = {"subject": "#x", "role": "link", "name": "X", "on": "a.png"}
    step = NS(
        extras={t4d.HOOK: e},
        stop=NS(unresolved=False, css_path="#x", frame_chain=[], kind="element"),
        rerun=False,
    )
    p = NS(steps=[step], name="P1", start_url="", start_pages=1)
    by_subject: dict = {}
    st = t4d.State4D(p1={}, p2={}, stops=1, inventory=1)
    t4d._attempts_from(p, st, by_subject, tmp_path)
    [inst] = by_subject.values()
    assert t4d._reason(inst).startswith("focus never moved on"), t4d._reason(inst)


async def test_f30_before_picture(settings, server):
    """Step 27 (#135), evidence only: each stop also gets a before picture
    (the page before the key press that focused it), and the pixels that
    changed both ways (on vs off and on vs before) are counted. On F30 the
    picture's own link changed only one way: what differs is the next
    link's ring in its off picture. The caption link's ring changed both
    ways; the title links keep (nearly) all their pixels."""
    from tobi508.checks.t4d import MIN_CHANGED_PX

    got = await run_check(
        settings,
        f"{server.base}/4d/f30-next-outline-over-image-link.html",
        TestId.T4D,
        "no",
    )
    [q] = got["asked"]  # the picture link only (M7), with its before picture
    assert (
        '"Image"' in str(q.input["element"])
        or q.input["element"].get("name") == "Image"
    )
    assert q.input["image_d_before"] and q.input["image_d_before"].endswith(".png")
    by = {}
    for i in got["finding"].instances:
        name = i.description.split('"')[1]
        nums = [float(x) for x in re.findall(r"(\d+) px", i.description)]
        by[name] = nums  # changed, strongly, both ways, both ways strongly
        assert len(i.evidence_refs) >= 2
    image, caption = by["Image"], by["A pale circle on a blue field"]
    assert image[1] >= MIN_CHANGED_PX and image[3] < MIN_CHANGED_PX, image
    assert caption[3] >= MIN_CHANGED_PX, caption
    assert by["First post"][3] >= MIN_CHANGED_PX


async def test_f30_before_by_replay(settings, server, monkeypatch):
    """Step 27 (#135), evidence only: with P2's before pictures switched off,
    every stop that would pass M6 gets its before picture from a replay (a
    fresh load, one Tab fewer), and F30's picture link still shows no pixel
    that changed both ways. Its own run: run_shared would hand back F30's
    run with P2's pictures."""
    from tobi508.checks import t4d
    from tobi508.pipeline import run_tt_tests

    monkeypatch.setattr(t4d, "BEFORE_PICTURE", False)
    monkeypatch.setattr(t4d, "BEFORE_REPLAY_MAX", 10)
    out = await run_tt_tests(
        settings,
        f"{server.base}/4d/f30-next-outline-over-image-link.html",
        [TestId.T4D],
    )
    [f] = [x for x in out.report.findings if x.test_id is TestId.T4D]
    image = next(i for i in f.instances if '"Image"' in i.description)
    nums = [float(x) for x in re.findall(r"(\d+) px", image.description)]
    assert nums[1] >= t4d.MIN_CHANGED_PX and nums[3] < t4d.MIN_CHANGED_PX, nums
    caption = next(i for i in f.instances if "pale circle" in i.description)
    assert float(re.findall(r"(\d+) px", caption.description)[3]) >= t4d.MIN_CHANGED_PX
