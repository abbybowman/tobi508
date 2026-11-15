"""19.A (2.4.5) on a small custom site (tests/fixtures/19a/): no ACT rule,
DHS verdict or Baseline Alignment case covers it. Each case is a tested page
plus the other pages given; the fixture server answers the site search
(search.html for any query; search-empty.html finds nothing). Expected
outcomes and scripted answers live here, never in a page."""

from __future__ import annotations

import pytest

from .drafts import drafts  # noqa: F401 (a fixture)
from .harness import run_tests

# case -> (tested page, other pages, expected outcome, rows, answers)
EXPECTED: dict[str, tuple[str, list[str], str, list[str], dict]] = {
    "nav-and-site-map": ("t-benefits", ["home", "sitemap"], "PASS", ["W1", "G2"], {}),
    # Part D (19.A 1.9.0; step 8, reader 2; review K-02): the site header,
    # navigation and search box, built as a web component, is read like a
    # plain one. Its twin with one way only still FAILs.
    "wc-nav-and-site-map": (
        "w-benefits",
        ["w-home", "w-sitemap"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    "wc-one-way-nothing-else": ("w-t3-forms", ["w-home2"], "FAIL", ["W1", "G4"], {}),
    "nav-and-related-link": (
        "t-benefits",
        ["home", "related"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    # 19.A 1.11.0 (Abby, 2026-11-15): the site map the home page links to is
    # checked by the test itself, before the site search, and the test stops
    # at two kinds. Before 1.11.0 these were PASS by the live search (W2) and
    # NEEDS REVIEW naming the site map (G3). The search stays covered by the
    # quoted-search cases below, whose pages link no site map.
    "nav-and-site-map-found-by-the-test": (
        "t-benefits",
        ["home"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    "search-finds-nothing-site-map-found-by-the-test": (
        "t2-status",
        ["home"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    "search-finds-nothing-site-map-given": (
        "t2-status",
        ["home", "sitemap"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    "one-way-nothing-else": ("t3-forms", ["home2"], "FAIL", ["W1", "G4"], {}),
    "contact-form-not-process": (
        "contact",
        ["home", "sitemap"],
        "PASS",
        ["W1", "G2"],
        {"J1": {"choice": "not_process"}},
    ),
    # Post-round 2 fix 10 (19.A 1.4.0; svs.gsfc.nasa.gov/search/, key Pass):
    # the page is the site search form's own target, so the search reaches
    # it; with a content link on the home page, two kinds.
    "search-page-is-the-forms-target": (
        "search",
        ["home3"],
        "PASS",
        ["W1", "W5", "G2"],
        {},
    ),
    # The nearest case that must still FAIL: a page about searching, which
    # the form does not submit to, linked once from the home page; the
    # search for its heading does not find it.
    "search-help-page-not-the-target": (
        "search-help",
        ["home3"],
        "FAIL",
        ["W1", "W3", "G4"],
        {},
    ),
    # Post-round 2 fix 11 (19.A 1.5.0; svs.gsfc.nasa.gov/14592/, key Pass):
    # the site's search answers "No results for:" the plain heading and finds
    # the page with the heading in quotation marks; its results arrive by
    # script after the page loads.
    "quoted-search-finds-it": (
        "t4-flare",
        ["home4"],
        "PASS",
        ["W1", "W2", "G2"],
        {},
    ),
    # The nearest case that must still FAIL: neither search finds the page.
    "quoted-search-finds-nothing": (
        "t5-eclipse",
        ["home4"],
        "FAIL",
        ["W1", "W3", "G4"],
        {},
    ),
    # Step 6c item 3 (19.A 1.7.0; step 6's six false FAILs): the results
    # page's own script did not load, so the search never showed results.
    # That is a search not verified (W4), not one that found nothing (W3).
    # "quoted-search-finds-nothing" above is the nearest case that must
    # still FAIL: a finished search that does not list the page.
    "search-results-script-failed": (
        "t6-aurora",
        ["home5"],
        "NEEDS_REVIEW",
        ["W1", "W4", "G3"],
        {},
    ),
    # Step 6h (19.A 1.10.0; round 2 p05, svs.gsfc.nasa.gov/cilab/, key Pass):
    # every link to the microsite's home goes to its index.html. Loaded, it
    # is the same document, so those links count: the agency's labs page
    # (content) and the lab's own menu (navigation).
    "alias-index-html-is-the-page": (
        "micro/",
        ["lab-home", "micro/people"],
        "PASS",
        ["W1", "W6", "G2"],
        {},
    ),
    # The nearest case that must never PASS: thin/index.html is another page
    # under the same heavy template (same title and heading, one paragraph
    # apart). Its bytes differ, so it is not verified: NEEDS REVIEW, where
    # before this the page FAILed with no way found.
    "alias-index-html-is-another-page": (
        "thin/",
        ["lab-home"],
        "NEEDS_REVIEW",
        ["W1", "W7", "G3"],
        {},
    ),
    # 19.A 1.11.0 (Abby, 2026-11-15): a tester goes down to a child page.
    # The section home is linked only in the agency's content; its first
    # project's breadcrumb links back to it (navigation).
    "second-way-on-a-child-page": (
        "sec/",
        ["hub"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    # ... and up to the parent: the funding page links the grants page in
    # its content; the agency's menu links it too.
    "second-way-on-the-parent": (
        "par/item",
        ["hub"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    # A child page that leaves the site after a redirect is not checked: the
    # test cannot FAIL on a set it did not finish (W8, G3).
    "child-page-not-checked": (
        "gone/",
        ["hub"],
        "NEEDS_REVIEW",
        ["W1", "W8", "G3"],
        {},
    ),
    "process-step": (
        "step2",
        ["home"],
        "DNA",
        ["A3", "G1"],
        {"J1": {"choice": "process"}},
    ),
}


@pytest.mark.parametrize("case", sorted(EXPECTED))
async def test_case(case, settings, server, drafts):  # noqa: F811
    page, others, outcome, rows, answers = EXPECTED[case]
    got = await run_tests(
        settings,
        f"{server.base}/19a/{page}" + ("" if page.endswith("/") else ".html"),
        ["19.A"],
        {"19.A": answers},
        other_pages=[f"{server.base}/19a/{o}.html" for o in others],
    )
    f = got["19.A"]
    assert f.outcome.value == outcome, (f.rows, f.summary, f.rationale)
    assert [r for r in f.rows if r != "A5"] == rows, f.rows
    if case == "alias-index-html-is-another-page":
        assert "thin/index.html is this page under another address" in f.summary
    if f.outcome.value == "FAIL":  # names what was checked (Abby, 2026-11-15)
        assert "We checked the 1 other page you gave" in f.summary, f.summary
        assert "search the web for pages that link to" in f.summary


async def test_without_other_pages_nothing_runs(settings, server, drafts):  # noqa: F811
    got = await run_tests(settings, f"{server.base}/19a/t-benefits.html", ["19.A"], {})
    f = got["19.A"]
    assert f.outcome.value == "NEEDS_REVIEW" and f.rows == ["A1", "G1"]


def test_template_links_are_navigation_only():
    """19.A 1.1.0 (Abby, 2026-11-02): on a results page or a site map page,
    the shared menus, header and footer link to T whatever the search found
    or the site map lists. Built evidence: no fixture page has that template."""
    from tobi508.checks.t19a import _kind, results_link_to
    from tobi508.site import PageRead, Unit

    t = "https://example.gov/apply.html"

    def link(region_role):
        return Unit(
            i=0,
            kind="control",
            role="link",
            text="apply",
            name="Apply",
            css="a",
            href=t,
            region_role=region_role,
        )

    menu_only = PageRead(
        n=101, url="https://example.gov/search", units=[link("navigation")]
    )
    assert not results_link_to(menu_only, t)  # "No results", menu link only
    hit = PageRead(
        n=101, url="https://example.gov/search", units=[link(""), link("navigation")]
    )
    assert results_link_to(hit, t)
    site_map = PageRead(n=2, url="https://example.gov/sitemap.html", units=[])
    assert _kind(link("banner"), site_map, {2}) == "navigation"
    assert _kind(link(""), site_map, {2}) == "site_map"


def test_live_search_url_drops_the_action_query():
    """A GET submission replaces the action's own query (spec Terms)."""
    from tobi508.checks.t19a import search_url

    form = {
        "method": "get",
        "field": "q",
        "action": "https://example.gov/s?x=1",
        "hidden": {"site": "main"},
    }
    assert search_url(form, "Apply") == "https://example.gov/s?site=main&q=Apply"


def test_links_to_the_requested_url_count_after_a_redirect():
    """Spec edge case: menus link to /benefits, which redirects to
    /benefits/apply; those links reach T too (review #6)."""
    from tobi508.checks.t19a import links_to
    from tobi508.site import PageRead, Unit

    menu = Unit(
        i=0,
        kind="control",
        role="link",
        text="benefits",
        name="Benefits",
        css="a",
        href="https://example.gov/benefits",
        region_role="navigation",
    )
    other = PageRead(n=1, url="https://example.gov/", units=[menu])
    final, requested = (
        "https://example.gov/benefits/apply",
        "https://example.gov/benefits",
    )
    assert links_to(final, [other], set()) == []
    assert [x.kind for x in links_to((final, requested), [other], set())] == [
        "navigation"
    ]


async def test_the_test_checks_the_suggested_pages_itself(
    settings,
    server,
    drafts,  # noqa: F811
):
    """19.A 1.11.0 (Abby, 2026-11-15): the site map, parent, child pages and
    home page are loaded by the test itself, one at a time, each recorded as
    a page it loaded (purpose "suggested"), and it stops at two kinds. No
    follow-up call is left for 19.A (before 1.11.0, none was ever made in the
    eval runs, and the call carried no suggested page when 5 were given)."""
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    url = f"{server.base}/19a/t2-status.html"
    out = await run_tt_tests(
        settings, url, [TestId.T19A], other_pages=[f"{server.base}/19a/home.html"]
    )
    assert out.follow_up_calls == []
    loaded = [(p.purpose, p.url) for p in out.report.live_pages]
    assert loaded == [("suggested", f"{server.base}/19a/sitemap.html")], loaded
    f = next(x for x in out.report.findings if x.test_id.value == "19.A")
    assert f.outcome.value == "PASS"


def test_suggested_pages_in_order():
    """19.A 1.11.0 Terms: the site map, the parent (from T's address), up to
    2 child pages under T's directory, the home page; never a page given, T
    or a suspected alias of T; no child pages for a T at the site root."""
    from tobi508.checks.t19a import parent_of, suggested_pages
    from tobi508.site import PageRead, Unit

    def link(href, name="x"):
        return Unit(
            i=0,
            kind="control",
            role="link",
            text=name.lower(),
            name=name,
            css="a",
            href=href,
        )

    t = "https://ex.gov/a/b/"
    main = PageRead(
        n=0,
        url=t,
        units=[
            link("https://ex.gov/a/b/index.html"),  # an alias: never suggested
            link("https://ex.gov/a/b/report.pdf"),  # not a page
            link("https://ex.gov/a/b/one/"),
            link("https://ex.gov/a/b/two.html"),
            link("https://ex.gov/a/b/three.html"),  # past the 2 children
            link("https://ex.gov/elsewhere/"),  # not under T's directory
        ],
    )
    other = PageRead(
        n=1, url="https://ex.gov/x/", units=[link("https://ex.gov/map/", "Site map")]
    )
    got = suggested_pages(t, main, [main, other], {"https://ex.gov/x/"})
    assert [(c.role, c.url) for c in got] == [
        ("site_map", "https://ex.gov/map/"),
        ("parent", "https://ex.gov/a/"),
        ("child", "https://ex.gov/a/b/one/"),
        ("child", "https://ex.gov/a/b/two.html"),
        ("home", "https://ex.gov/"),
    ]
    assert parent_of("https://ex.gov/a/b/c.html") == "https://ex.gov/a/b/"
    assert parent_of("https://ex.gov/a/b/index.html") == "https://ex.gov/a/"
    assert parent_of("https://ex.gov/") is None
    root = PageRead(n=0, url="https://ex.gov/", units=[link("https://ex.gov/a/")])
    assert suggested_pages("https://ex.gov/", root, [root], set()) == []
    query = PageRead(n=0, url="https://ex.gov/?q=1", units=[link("https://ex.gov/a/")])
    assert [
        c.role for c in suggested_pages("https://ex.gov/?q=1", query, [query], set())
    ] == ["home"]


def test_failed_scripts_reads_the_recording(tmp_path):
    """A script the recording saved with no response (-1: refused, as the
    container's untrusted proxy certificate did in step 6) or an error status
    counts; other resources and loaded scripts do not."""
    import json
    import zipfile

    from tobi508.capture import failed_scripts

    def entry(url, kind, status):
        return {
            "request": {"url": url},
            "response": {"status": status},
            "_resourceType": kind,
        }

    har = tmp_path / "r.har.zip"
    with zipfile.ZipFile(har, "w") as z:
        z.writestr(
            "r.har",
            json.dumps(
                {
                    "log": {
                        "entries": [
                            entry("https://cdn.example/app.js", "script", -1),
                            entry("https://example.gov/static/r.js", "script", 404),
                            entry("https://example.gov/ok.js", "script", 200),
                            entry("https://example.gov/x.png", "image", -1),
                        ]
                    }
                }
            ),
        )
    assert failed_scripts(har) == [
        "https://cdn.example/app.js",
        "https://example.gov/static/r.js",
    ]


def test_suspected_alias():
    """19.A 1.10.0 Terms (Abby, 2026-11-14 and 2026-11-15): an index.* or
    default.* last segment either way round, the scheme and a leading www.
    make a suspected alias; a query string, another directory or another
    file name do not; neither does T itself."""
    from tobi508.checks.t19a import suspected_alias

    t = "https://svs.example.gov/cilab/"
    yes = [
        "https://svs.example.gov/cilab/index.html",
        "https://svs.example.gov/cilab/default.aspx",
        "http://svs.example.gov/cilab/index.html#top",
        "https://www.svs.example.gov/cilab/",
    ]
    no = [
        "https://svs.example.gov/cilab/",
        "https://svs.example.gov/cilab",
        "https://svs.example.gov/cilab/?page=2",
        "https://svs.example.gov/cilab/information.html",
        "https://svs.example.gov/index.html",
        "https://other.example.gov/cilab/index.html",
        "mailto:lab@example.gov",
    ]
    assert [u for u in yes if not suspected_alias(u, t)] == []
    assert [u for u in no if suspected_alias(u, t)] == []
    assert suspected_alias(
        "https://svs.example.gov/cilab/", "https://svs.example.gov/cilab/index.html"
    )


def test_alias_reasons_are_plain_words():
    """Principle 8: why an alias was not loaded, without exception names."""
    from tobi508.checks.t19a import _load_reason
    from tobi508.frozen import NotFrozen

    assert _load_reason(NotFrozen("x")) == "no saved copy of it was available to load"
    assert "time" in _load_reason(TimeoutError())
    assert "Error" not in _load_reason(RuntimeError("boom"))
