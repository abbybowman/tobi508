"""9.A, 9.B and 9.C on custom multi-page fixtures (tests/fixtures/9x/): no
W3C ACT rule or Baseline Alignment case covers 9.B or 9.C, and these fill
9.A's gaps. Each case is a tested page plus the other pages it is compared
with; all three tests run in one call. Expected outcomes and scripted
answers (what a correct agent would say) live here, never in a page."""

from __future__ import annotations

import pytest

from .drafts import drafts  # noqa: F401 (a fixture)
from .harness import instance_rows, run_tests

DOC = {"choice": "documented", "key": "Alt+S", "quote": "press Alt+S to skip"}

# case -> (tested page, other pages, {test: expected outcome}, answers)
EXPECTED: dict[str, tuple[str, list[str], dict[str, str], dict]] = {
    "consistent-site": (
        "a1-home",
        ["a2-benefits"],
        {"9.A": "PASS", "9.B": "PASS", "9.C": "PASS"},
        {},
    ),
    "nav-reordered": (
        "a1-home",
        ["a3-nav-reordered"],
        {"9.A": "PASS", "9.B": "FAIL", "9.C": "PASS"},
        {},
    ),
    "nav-css-order": ("a1-home", ["a4-nav-css-order"], {"9.B": "FAIL"}, {}),
    # K-04: an unnamed javascript:void(0) icon here and a "Close alert"
    # javascript:void(0) link there are not "the same destination": they do
    # not pair, so no FAIL. (The nav links pair and agree.)
    "javascript-links": (
        "f1-js-icon-header",
        ["f2-js-close-alert"],
        {"9.C": "PASS"},
        {},
    ),
    # M-10: an address that already ends in #main has its target before any
    # press, so a do-nothing button is not a skip control. The control: a
    # real skip link to #main on the same kind of address still passes.
    "noop-button-address-with-fragment": (
        "h1-noop-button-alpha#main",
        ["h2-beta"],
        {"9.A": "FAIL"},
        {},
    ),
    "noop-button-address-without-fragment": (
        "h1-noop-button-alpha",
        ["h2-beta"],
        {"9.A": "FAIL"},
        {},
    ),
    "skip-link-address-with-fragment": (
        "a1-home#main",
        ["a2-benefits"],
        {"9.A": "PASS"},
        {},
    ),
    # K-05 (9.C 1.7.0): a pair with no name on either page has nothing to
    # compare. Alone it is NEEDS REVIEW (not DOES NOT APPLY, never PASS);
    # beside a named pair that agrees the named pair decides ("renamed" above
    # is the nearest case that must still FAIL).
    "unnamed-controls-only": (
        "i1-unnamed-only-a",
        ["i2-unnamed-only-b"],
        {"9.C": "NEEDS_REVIEW"},
        {},
    ),
    "unnamed-controls-beside-named": (
        "i3-unnamed-and-named-a",
        ["i4-unnamed-and-named-b"],
        {"9.C": "PASS"},
        {},
    ),
    "two-pages-one-reordered": (
        "a1-home",
        ["a2-benefits", "a3-nav-reordered"],
        {"9.B": "FAIL", "9.C": "PASS"},
        {},
    ),
    "renamed": (
        "a1-home",
        ["a5-renamed"],
        {"9.A": "PASS", "9.B": "PASS", "9.C": "FAIL"},
        {"9.C": {"J1": {"choice": "inconsistent"}}},
    ),
    # Fix 14 (9.C 1.5.0): links in the pages' own content that go to one
    # address with different words are not a repeated component, so they
    # are not paired by address (round 2: Home and Help, key Pass). The
    # header, menu and search still agree. "renamed" above is the nearest
    # case that must still FAIL: the same change in the menu.
    "body-links-reworded": (
        "g1-body-links",
        ["g2-body-links-reworded"],
        {"9.C": "PASS"},
        {},
    ),
    # Pages of another template: nothing can be said (spec 1.1.0 / 1.2.0,
    # A3o). They were DOES NOT APPLY before.
    "unrelated": (
        "a1-home",
        ["c1-unrelated"],
        {"9.A": "NEEDS_REVIEW", "9.B": "NEEDS_REVIEW", "9.C": "NEEDS_REVIEW"},
        {},
    ),
    "microsite": (
        "a1-home",
        ["e1-microsite"],
        {"9.A": "NEEDS_REVIEW", "9.B": "NEEDS_REVIEW", "9.C": "NEEDS_REVIEW"},
        {},
    ),
    # A microsite that has its own header and footer still shares nothing
    # by label or id with the tested page.
    "microsite-with-header-footer": (
        "a1-home",
        ["e3-microsite-with-header-footer"],
        {"9.A": "NEEDS_REVIEW", "9.B": "NEEDS_REVIEW", "9.C": "NEEDS_REVIEW"},
        {},
    ),
    # The same template: nothing changes.
    "same-template": (
        "a1-home",
        ["e2-same-template"],
        {"9.A": "PASS", "9.B": "PASS", "9.C": "PASS"},
        {},
    ),
    # One related page among others: the unrelated one is not compared (N2o)
    # and does not turn the related page's result into a review.
    "related-and-microsite": (
        "a1-home",
        ["e2-same-template", "e1-microsite"],
        {"9.A": "PASS", "9.B": "PASS", "9.C": "PASS"},
        {},
    ),
    # The tested page is the microsite: it has no navigation of its own, so
    # there is nothing a person should look for (A3).
    "microsite-is-tested": (
        "e1-microsite",
        ["a1-home"],
        {"9.A": "DNA", "9.B": "DNA", "9.C": "DNA"},
        {},
    ),
    "skip-past-heading": ("b1-skip-past-heading", ["a2-benefits"], {"9.A": "FAIL"}, {}),
    "skip-after-nav": ("b2-skip-after-nav", ["a2-benefits"], {"9.A": "FAIL"}, {}),
    "documented-key": (
        "b3-documented-key",
        ["a2-benefits"],
        {"9.A": "PASS"},
        {"9.A": {"J1": DOC}},
    ),
    "breadcrumbs-repeated": (
        "b4-no-main-breadcrumbs",
        ["a2-benefits"],
        {"9.A": "PASS"},
        {"9.A": {"J2": {"choice": "repeated"}}},
    ),
    "breadcrumbs-not-repeated": (
        "b4-no-main-breadcrumbs",
        ["a2-benefits"],
        {"9.A": "FAIL"},
        {"9.A": {"J2": {"choice": "not_repeated"}}},
    ),
    "two-links": ("b5-two-links", ["b6-sibling-with-aside"], {"9.A": "PASS"}, {}),
    # The page tells its own script that focus moved; it did not.
    "fake-focus": ("b7-fake-focus", ["a2-benefits"], {"9.A": "FAIL"}, {}),
    "paging": (
        "d1-page4",
        ["d2-page5"],
        {"9.A": "DNA", "9.B": "PASS", "9.C": "PASS"},
        {"9.C": {"J1": {"choice": "consistent"}}},
    ),
    # The read cap (9.A 1.4.0, 9.C 1.6.0; roadmap step 6c): 700 pieces of
    # content, over the old cap of 600, are read whole and decided. Round 2's
    # home page (772) and galleries page (630) held every 9.x cell.
    "over-the-old-cap": (
        "h1-big-menu",
        ["h2-big-menu-benefits"],
        {"9.A": "FAIL", "9.B": "PASS", "9.C": "PASS"},
        {},
    ),
    # The nearest page that must still be NEEDS REVIEW: 5,001 topics, over
    # the cap, so the main content is never reached. 9.A gave DOES NOT APPLY
    # here (A4: "nothing before the main content") before 1.4.0.
    "over-the-cap": (
        "h3-huge-menu",
        ["h2-big-menu-benefits"],
        {"9.A": "NEEDS_REVIEW", "9.B": "NEEDS_REVIEW", "9.C": "NEEDS_REVIEW"},
        {},
    ),
    # An other page over the cap: what repeats cannot be told (9.A A2).
    "other-page-over-the-cap": (
        "h1-big-menu",
        ["h3-huge-menu"],
        {"9.A": "NEEDS_REVIEW", "9.B": "NEEDS_REVIEW", "9.C": "NEEDS_REVIEW"},
        {},
    ),
}

# Rules tests only, left out of the judge eval: the same page and question
# as another case with the opposite scripted answer.
NOT_EVAL = {"breadcrumbs-not-repeated"}

ROWS = {
    ("skip-past-heading", "9.A"): ["M8"],
    ("documented-key", "9.A"): ["M7"],  # the documented key, pressed
    ("fake-focus", "9.A"): ["M5"],
    ("breadcrumbs-repeated", "9.A"): ["M9"],
    ("nav-reordered", "9.B"): ["N3"],
    ("nav-css-order", "9.B"): ["N4"],
    ("renamed", "9.C"): ["C1"] * 10 + ["C4", "C4"],
    ("paging", "9.C"): ["C1", "C3", "C3"],
    ("unnamed-controls-only", "9.C"): ["C0", "C0"],
    ("unnamed-controls-beside-named", "9.C"): ["C1", "C1", "C0"],
}


@pytest.mark.parametrize("case", sorted(EXPECTED))
async def test_case(case, settings, server, drafts):  # noqa: F811
    page, others, want, answers = EXPECTED[case]
    page, hash_, frag = page.partition("#")  # "name#main": the tested address
    got = await run_tests(
        settings,
        f"{server.base}/9x/{page}.html{hash_}{frag}",
        list(want),
        answers,
        other_pages=[f"{server.base}/9x/{o}.html" for o in others],
    )
    for t, outcome in want.items():
        f = got[t]
        assert f.outcome.value == outcome, (t, f.rows, f.summary)
        if (case, t) in ROWS:
            assert sorted(instance_rows(f)) == sorted(ROWS[(case, t)]), f.rows


@pytest.mark.parametrize("case", ["over-the-cap", "other-page-over-the-cap"])
async def test_page_over_the_cap_is_not_performed(case, settings, server, drafts):  # noqa: F811
    """9.A 1.4.0: a page over the read cap is A2 (not performed) before A3,
    A4 or G2 can decide; 9.B N1 and 9.C G3 as before. The summary names the
    cap and the page."""
    from tobi508.site import UNIT_CAP

    page, others, want, answers = EXPECTED[case]
    got = await run_tests(
        settings,
        f"{server.base}/9x/{page}.html",
        list(want),
        answers,
        other_pages=[f"{server.base}/9x/{o}.html" for o in others],
    )
    where = "the tested page" if case == "over-the-cap" else "other page 1"
    assert got["9.A"].rows == ["A2", "G1"], got["9.A"].rows
    assert got["9.A"].note == "This test could not be performed"
    for t in ("9.A", "9.C"):
        assert f"first {UNIT_CAP:,} pieces of content of {where}" in got[t].summary, (
            t,
            got[t].summary,
        )
    assert got["9.B"].rows[-1] == "G3", got["9.B"].rows
    assert got["9.C"].rows[-1] == "G3", got["9.C"].rows


def test_9c_page_over_the_cap_is_never_pass_or_dna():
    """A page over the read cap has controls that were never paired, so
    agreeing pairs (G5) or no pairs (A3) cannot decide (spec 1.1.0). Built
    evidence: no fixture page this large is worth vendoring."""
    from tobi508.checks.t9c import AndiPage, Comp, Pair, State9C, evaluate

    def page(n, truncated):
        c = Comp(k=0, css="a", role="link", href="/home", andi_name="Home")
        return AndiPage(n=n, ran=True, truncated=truncated, comps=[c])

    pair = Pair(id="p1-0", page=1, here=0, there=0, by="destination")
    full = State9C(pages=[page(0, False), page(1, False)], pairs=[pair])
    assert evaluate(full, []).outcome.value == "PASS"
    over = State9C(pages=[page(0, False), page(1, True)], pairs=[pair])
    f = evaluate(over, [])
    assert (f.outcome.value, f.rows[-1]) == ("NEEDS_REVIEW", "G3"), f.rows
    assert "other page 1" in f.summary
    none = State9C(pages=[page(0, True), page(1, False)], pairs=[])
    assert evaluate(none, []).outcome.value == "NEEDS_REVIEW"


@pytest.mark.parametrize(
    "case", ["unrelated", "microsite", "microsite-with-header-footer"]
)
async def test_other_template_is_a_review_by_row_a3o(case, settings, server, drafts):  # noqa: F811
    page, others, want, answers = EXPECTED[case]
    got = await run_tests(
        settings,
        f"{server.base}/9x/{page}.html",
        list(want),
        answers,
        other_pages=[f"{server.base}/9x/{o}.html" for o in others],
    )
    for t in want:
        assert got[t].rows == ["A3o", "G1"], (t, got[t].rows)
        assert got[t].note == "This test could not be performed"
        assert "different template" in got[t].summary


def test_kinship_counts_and_fingerprints():
    """Facts only (site.py): what two pages share by label or id and by text."""
    from tobi508.site import PageRead, Region, Unit, kin, template_fingerprint

    def unit(i, text, kind="control", in_main=False):
        return Unit(
            i=i,
            kind=kind,
            role="link",
            text=text,
            name=text,
            css=f"a{i}",
            in_main=in_main,
        )

    def region(key, role):
        return Region(key=key, role=role, css=key)

    nav = region("navigation|Main", "navigation")
    here = PageRead(
        n=0,
        url="u0",
        units=[unit(0, "home"), unit(1, "about us today please")],
        regions=[nav, region("banner|@1", "banner")],
    )
    same = PageRead(n=1, url="u1", units=here.units, regions=[nav])
    other = PageRead(
        n=2, url="u2", units=[unit(0, "home")], regions=[region("banner|@1", "banner")]
    )
    assert kin(here, same).shared_regions == ["navigation|Main"]
    assert not kin(here, same).almost_nothing
    # a place among its role (`@1`) is not a match; one shared control is small
    k = kin(here, other)
    assert (k.shared_regions, k.shared_units, k.almost_nothing) == ([], 1, True)
    assert template_fingerprint(here) != template_fingerprint(other)
    assert template_fingerprint(here) == template_fingerprint(
        here.model_copy(update={"n": 5})
    )


def test_9b_page_over_the_cap_is_never_dna():
    """A capped read with no matches cannot be called DNA (N1 before N2, as
    9.C 1.1.0), and a page of another template is skipped (N2o) unless it was
    capped. Built evidence: no fixture page this large is worth vendoring."""
    from tobi508.checks.t9b import Cmp, State9B, evaluate
    from tobi508.site import Kin, Kinship

    unrelated = Kinship(
        own_navigation=True,
        pages=[Kin(n=1, almost_nothing=True)],
        all_unrelated=True,
        unrelated_review=True,
    )
    capped = State9B(cmps=[Cmp(n=1, url="u1", incomplete=True)], kinship=unrelated)
    f = evaluate(capped, [])
    assert (f.outcome.value, f.rows[-1]) == ("NEEDS_REVIEW", "G3"), f.rows
    whole = State9B(cmps=[Cmp(n=1, url="u1")], kinship=unrelated)
    assert evaluate(whole, []).rows == ["A3o", "G1"]
    no_nav = unrelated.model_copy(
        update={"own_navigation": False, "unrelated_review": False}
    )
    assert (
        evaluate(State9B(cmps=[Cmp(n=1, url="u1")], kinship=no_nav), []).outcome.value
        == "DNA"
    )


def test_9c_pairs_by_destination_only_inside_a_repeated_block():
    """1.5.0 (fix 14): the same address from the pages' own content is not a
    repeated component; from the header, menu, search or footer it is. Built
    evidence: the page pair is g1/g2 against a5-renamed."""
    from tobi508.checks.t9c import AndiPage, Comp, make_pairs

    def comp(k, region, name, href="/apply"):
        return Comp(
            k=k, css=f"a{k}", role="link", href=href, region_role=region, andi_name=name
        )

    here = AndiPage(
        n=0,
        ran=True,
        comps=[
            comp(0, "", "benefits application guide"),
            comp(1, "navigation", "Apply"),
        ],
    )
    there = AndiPage(
        n=1,
        ran=True,
        comps=[comp(0, "", "See how to apply"), comp(1, "navigation", "Apply now")],
    )
    got = [(p.here, p.there, p.by) for p in make_pairs(here, there)]
    assert got == [(1, 1, "destination")], got
    # A sidebar (complementary) is not a repeated block either.
    side = AndiPage(n=0, ran=True, comps=[comp(0, "complementary", "Related guide")])
    side2 = AndiPage(n=1, ran=True, comps=[comp(0, "complementary", "Learn more")])
    assert make_pairs(side, side2) == []


async def test_the_tested_page_again_with_other_bytes_is_not_compared(
    settings,
    server,
    drafts,  # noqa: F811
):
    """K-01 (A2 1.4.0 / 1.6.0): the same address apart from the query, nearly
    the same text, bytes that change on every request. 9.A, 9.B, 9.C and
    19.A are NEEDS REVIEW and say why."""
    got = await run_tests(
        settings,
        f"{server.base}/stamp",
        ["9.A", "9.B", "9.C", "19.A"],
        {},
        other_pages=[f"{server.base}/stamp?x=1"],
    )
    for t, f in got.items():
        assert f.outcome.value == "NEEDS_REVIEW", (t, f.rows, f.summary)
        assert "A2" in f.rows, (t, f.rows)
        assert "nearly the same page" in f.summary, (t, f.summary)


async def test_the_same_address_with_other_content_is_still_compared(
    settings,
    server,
    drafts,  # noqa: F811
):
    """The nearest case that must still be compared: one path, a query that
    changes the content (a listing's page 2). Its share of text is far below
    the bar, so 9.B and 9.C compare it and do not stop at A2."""
    got = await run_tests(
        settings,
        f"{server.base}/listing?page=1",
        ["9.B", "9.C"],
        {},
        other_pages=[f"{server.base}/listing?page=2"],
    )
    for t, f in got.items():
        assert "A2" not in f.rows, (t, f.rows, f.summary)
        assert f.outcome.value == "PASS", (t, f.rows, f.summary)


def test_text_share_and_near_copy():
    from tobi508.site import NEAR_COPY, PageRead, Unit, near_copy, text_share

    def page(url, texts):
        return PageRead(
            n=0,
            url=url,
            units=[
                Unit(i=i, kind="control", role="link", text=t, css=f"a{i}")
                for i, t in enumerate(texts)
            ],
        )

    base = [f"link {i}" for i in range(20)]
    a = page("https://x.gov/p", base)
    assert NEAR_COPY == 0.9
    assert text_share(a, page("https://x.gov/p?x=1", base + ["stamp 1"])) > 0.9
    # a different path is never a near copy, whatever its text
    assert not near_copy(a, page("https://x.gov/q?x=1", base))
    # the same path, half the text different: compared
    assert not near_copy(a, page("https://x.gov/p?x=1", base[:10] + ["z"] * 10))
    # a trailing slash, the scheme's default port and host case are not paths
    assert near_copy(a, page("https://X.gov:443/p/?x=1", base))
    # no text at all is not a copy
    assert text_share(page("u", []), page("u", [])) == 0.0
