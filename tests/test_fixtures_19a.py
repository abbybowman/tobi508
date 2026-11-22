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
    # Step 26 (19.A, #134): an index.html alias with the same document is no
    # longer verified by the document alone (an application sends one
    # document for every address), so this page and the two lab pages below
    # are NEEDS REVIEW (W7, alias not verified) where they were PASS, PASS
    # and FAIL. Round 2's CILab (key Pass) depends on such an alias.
    # Step 6h (19.A 1.10.0; round 2 p05, svs.gsfc.nasa.gov/cilab/, key Pass):
    # every link to the microsite's home goes to its index.html. Loaded, it
    # is the same document, so those links count: the agency's labs page
    # (content) and the lab's own menu (navigation).
    # 19.A 1.20.0 (#138 draft A, Abby 2026-11-22): verified again by the
    # same document and the same drawn text (90% shared).
    "alias-index-html-is-the-page": (
        "micro/",
        ["lab-home", "micro/people"],
        "PASS",
        ["W1", "W6", "G2"],
        {},
    ),
    # Must stay not verified: an application's one document draws another
    # page at index.html (#134's case).
    "alias-app-shell-draws-another-page": (
        "micro2/",
        ["hub4"],
        "NEEDS_REVIEW",
        ["W1", "W7", "G3"],
        {},
    ),
    # 19.A 1.20.0 (#138 draft B2): round 2's CILab as it is live. The rows
    # differ by the item that swaps (Information on the home, Home on
    # Information) and by Contact Us: "#" on one, mailto: on the other,
    # the same item by name. Without the link home, Information's row is all
    # in the home's: navigation; with the agency's card link, PASS.
    "icon-row-with-swapped-items-is-navigation": (
        "lab4/",
        ["hub4"],
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
    # 19.A 1.18.0 (Abby, 2026-11-21, #138 draft D): a breadcrumb trail is a
    # way of its own, apart from the site's menus (her keys: round 3 p01,
    # p02, p08, p09). The section is in the agency's menu; its first story's
    # trail, a navigation region named "Breadcrumb", links back to it.
    "breadcrumb-is-a-way-of-its-own": (
        "crumb/",
        ["crumb-hub"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    # ... and a trail marked only by its list's class (`ol.breadcrumb`).
    "breadcrumb-list-by-class": (
        "crumb2/",
        ["crumb-hub"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    # Must not PASS: the child page's trail does not include the page (round
    # 2's svs home, key Fail: "Page breadcrumbs don't include it").
    "breadcrumb-without-the-page": (
        "crumb3/",
        ["crumb-hub"],
        "FAIL",
        ["W1", "G4"],
        {},
    ),
    # 19.A 1.21.0 (#138 draft C, Abby 2026-11-22): W4 counts only a script
    # that could draw the results. An `async` tag from another host that
    # fails beside results drawn in the document is left out, so the
    # search's answer stands (round 3: script.crazyegg.com).
    "search-async-tag-beside-drawn-results-is-left-out": (
        "sr/t1",
        ["sr/h1"],
        "FAIL",
        ["W1", "W3", "G4"],
        {},
    ),
    # Must keep (step 6c): results drawn by the site's own script, which
    # failed, beside the same tag: not verified.
    "search-own-results-script-failed": (
        "sr/t2",
        ["sr/h2"],
        "NEEDS_REVIEW",
        ["W1", "W4", "G3"],
        {},
    ),
    # ... the tag beside a results page that shows no results: not verified.
    "search-tag-and-no-results-shown": (
        "sr/t3",
        ["sr/h3"],
        "NEEDS_REVIEW",
        ["W1", "W4", "G3"],
        {},
    ),
    # ... a script from another host the page waits for (no async): not
    # verified.
    "search-off-host-script-the-page-waits-for": (
        "sr/t4",
        ["sr/h4"],
        "NEEDS_REVIEW",
        ["W1", "W4", "G3"],
        {},
    ),
    # 19.A 1.21.0 (#138 draft C2): the page is headed "Website feedback"
    # and the menus call it "Contact Us" (round 3's contact page). The
    # heading finds nothing; the menu's name lists a page whose content
    # links to it: navigation and a content link.
    "search-by-menu-name-lists-a-page-that-links-to-it": (
        "sr/fb",
        ["sr/fbhome"],
        "PASS",
        ["W1", "W3", "G2"],
        {},
    ),
    # ... and a listed page that redirects to it: the search leads there
    # (round 3's home page, listed as /home).
    "search-lists-a-page-that-redirects-to-it": (
        "sr/fb2",
        ["sr/fbhome2"],
        "PASS",
        ["W1", "W2", "G2"],
        {},
    ),
    # Round 3's contact page as it is: the heading's search shows no
    # results beside a failed tag (not verified), then the menu's name
    # lists a page whose content links to it: PASS.
    "search-unverified-then-menu-name-finds-a-content-link": (
        "sr/fb3",
        ["sr/fbhome3"],
        "PASS",
        ["W1", "W4", "G2"],
        {},
    ),
    # ... and when the menu's name lists nothing that leads to it, the
    # heading's search was never verified: NEEDS REVIEW, not FAIL.
    "search-unverified-then-menu-name-finds-nothing": (
        "sr/fb4",
        ["sr/fbhome4"],
        "NEEDS_REVIEW",
        ["W1", "W4", "G3"],
        {},
    ),
    # 19.A 1.21.0 (#138; round 3's community forum, key Pass by breadcrumbs
    # on its posts): an application drawn by script after load opens its
    # posts from cards that are not links, so the pages that lead back
    # cannot be found from the markup: one way found is NEEDS REVIEW (W10),
    # never FAIL. "one-way-nothing-else" (a page drawn at load) keeps FAIL.
    "app-page-with-one-way-is-not-a-fail": (
        "appf/",
        ["appf-hub"],
        "NEEDS_REVIEW",
        ["W1", "W10", "G3"],
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
    # 19.A 1.12.0 W9 (Abby, 2026-11-15: "we can't say we've checked for nav
    # links as a way if we haven't read the nav"). The other page links the
    # grants page in its content and inside a menu that is closed on load:
    # NEEDS REVIEW, not FAIL. Its twin with the menu open PASSes.
    "closed-menu-not-read": (
        "t7-grants",
        ["menu-closed"],
        "NEEDS_REVIEW",
        ["W1", "W9", "G3"],
        {},
    ),
    "open-menu-read": (
        "t7-grants",
        ["menu-open"],
        "PASS",
        ["W1", "G2"],
        {},
    ),
    # 19.A 1.15.0 W9 (step 6g; Abby, 2026-11-15): the one visible button
    # that controls the hidden link to T is opened; when the link is then
    # shown it is a navigation way. Above, a button that opens nothing stays
    # NEEDS REVIEW; here one that opens the menu PASSes, and a link in a
    # mobile copy of the menu (no visible button controls it) is not a way.
    "closed-menu-opened": ("t7-grants", ["menu-script"], "PASS", ["W1", "G2"], {}),
    "mobile-menu-copy": (
        "t7-grants",
        ["menu-mobile"],
        "NEEDS_REVIEW",
        ["W1", "W9", "G3"],
        {},
    ),
    # 19.A 1.13.0 (Abby, 2026-11-15: "previous and next ... almost certain
    # to result in a valid way"; round 2's leaf pages): the next story links
    # back in its content. Its twin's next story does not: FAIL, naming it.
    "next-page-links-back": ("nb/b/", ["hub2"], "PASS", ["W1", "G2"], {}),
    "next-page-does-not-link-back": ("nb/d/", ["hub2"], "FAIL", ["W1", "G4"], {}),
    # ... and a related page T links to in its content (round 1's ISS hub).
    "related-page-links-back": ("rel/x/", ["hub2"], "PASS", ["W1", "G2"], {}),
    # 19.A 1.14.0 (Abby, 2026-11-15, option 1; round 2's CILab): a lab's
    # subpages repeat its home page's row of icon links, outside any
    # navigation region. The row is on T too, so the link back (to
    # index.html, a verified alias) is navigation. Its twin's subpage links
    # back only from a paragraph of links T does not have: one kind, FAIL.
    # 1.20.0: both back to their 1.14.0 outcomes (#138, drafts A and B2).
    "repeated-link-row-is-navigation": (
        "lab2/",
        ["hub3"],
        "PASS",
        ["W1", "W6", "G2"],
        {},
    ),
    "content-links-not-on-t-are-not-navigation": (
        "lab3/",
        ["hub3"],
        "FAIL",
        ["W1", "W6", "G4"],
        {},
    ),
    # ... and a related link that is an API's JSON is not a page: it takes
    # no place, and a link held back is checked instead.
    "json-is-not-a-page": ("rel/y/", ["hub3"], "PASS", ["W1", "G2"], {}),
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
    if case == "next-page-does-not-link-back":
        assert "its previous or next page" in f.summary, f.summary
    if case == "closed-menu-not-read":
        assert "inside a closed menu on" in f.summary, f.summary
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
        ("related", "https://ex.gov/a/b/three.html"),
        ("related", "https://ex.gov/elsewhere/"),
        ("home", "https://ex.gov/"),
    ]
    # 1.13.0: previous and next first after the site map, related pages after
    # the children (3 at most; a query-only variant counts once).
    seq = PageRead(
        n=0,
        url=t,
        units=[
            link("https://ex.gov/topic/"),
            link("https://ex.gov/topic/?page=2"),
            link("https://ex.gov/a/b/one/"),
            link("https://ex.gov/a/c/", "Next page"),
            link("https://ex.gov/t2/"),
            link("https://ex.gov/t3/"),
            link("https://ex.gov/t4/"),
        ],
    )
    got = suggested_pages(t, seq, [seq], set())
    assert [(c.role, c.url) for c in got] == [
        ("prev_next", "https://ex.gov/a/c/"),
        ("parent", "https://ex.gov/a/"),
        ("child", "https://ex.gov/a/b/one/"),
        ("related", "https://ex.gov/topic/"),
        ("related", "https://ex.gov/t2/"),
        ("related", "https://ex.gov/t3/"),
        ("home", "https://ex.gov/"),
    ]
    assert parent_of("https://ex.gov/a/b/c.html") == "https://ex.gov/a/b/"
    assert parent_of("https://ex.gov/a/b/index.html") == "https://ex.gov/a/"
    assert parent_of("https://ex.gov/") is None
    # A T at the root has no child pages; a link in its content is a related
    # page (1.13.0), never a child.
    root = PageRead(n=0, url="https://ex.gov/", units=[link("https://ex.gov/a/")])
    got = suggested_pages("https://ex.gov/", root, [root], set())
    assert [(c.role, c.url) for c in got] == [("related", "https://ex.gov/a/")]
    query = PageRead(n=0, url="https://ex.gov/?q=1", units=[link("https://ex.gov/a/")])
    got = suggested_pages("https://ex.gov/?q=1", query, [query], set())
    assert [c.role for c in got] == ["related", "home"]


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


def test_g5_names_what_was_found_and_checked():
    """19.A 1.13.0 G5 (Abby, 2026-11-15): one way found (the site search) and
    everything checked is NEEDS REVIEW, saying what was found and checked."""
    from tobi508.checks.t19a import Search, State19A, Suggested, evaluate

    st = State19A(
        t_url="https://ex.gov/a/",
        pages=[{"n": 1, "url": "https://ex.gov/b/"}],
        search_forms=1,
        search=Search(status="found", tries=["A"]),
        checked=[Suggested(url="https://ex.gov/", role="home", status="checked")],
    )
    f = evaluate(st, [])
    assert f.outcome.value == "NEEDS_REVIEW" and f.rows[-1] == "G5"
    assert (
        "We found 1 way to reach this page (the site search), and no second way"
        in f.summary
    )
    assert (
        "We checked the 1 other page you gave, the home page and the site "
        "search (1 search)" in f.summary
    )


# 19.A 1.19.0 (Abby, 2026-11-21, #138 draft E): the site search's own results
# page is one page whatever its query; round 3 p04, key Pass by "navigation
# and content links" (the home page's topic tags lead to other queries).
# Cases: tested page (with its query), other page, outcome, rows.
QUERY_CASES = {
    # A search form submits to res.html (W5), and the topics page links it
    # with other queries: links between pages, and the search.
    "results-page-whatever-its-query": (
        "res.html?q=test&sort=rel",
        "res-home",
        "PASS",
        ["W1", "W5", "G2"],
    ),
    # Must not count: the search form submits to the home page's own
    # address (round 1's nasa.gov: "/?search=artemis", key DNA). Links to
    # the home page carry no search, so they are the home page, not the
    # results page: only the search's own way (W5) is found.
    "home-page-links-are-not-the-results-page": (
        "hq.html?search=moon",
        "hq-other",
        "NEEDS_REVIEW",
        ["W1", "W5", "G5"],
    ),
    # Must not count: no search form submits to app.html, so app.html?id=2
    # is another record (a web app whose parameters are other content).
    "other-query-of-a-page-no-form-submits-to": (
        "app.html?id=1",
        "app-home",
        "FAIL",
        ["W1", "G4"],
    ),
}


@pytest.mark.parametrize("case", sorted(QUERY_CASES))
async def test_query_case(case, settings, server, drafts):  # noqa: F811
    page, other, outcome, rows = QUERY_CASES[case]
    got = await run_tests(
        settings,
        f"{server.base}/19a/{page}",
        ["19.A"],
        {"19.A": {}},
        other_pages=[f"{server.base}/19a/{other}.html"],
    )
    f = got["19.A"]
    assert f.outcome.value == outcome, (f.rows, f.summary, f.rationale)
    assert [r for r in f.rows if r != "A5"] == rows, f.rows
