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
    "nav-and-live-search": ("t-benefits", ["home"], "PASS", ["W1", "W2", "G2"], {}),
    "search-finds-nothing": (
        "t2-status",
        ["home"],
        "NEEDS_REVIEW",
        ["W1", "W3", "G3"],
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
        f"{server.base}/19a/{page}.html",
        ["19.A"],
        {"19.A": answers},
        other_pages=[f"{server.base}/19a/{o}.html" for o in others],
    )
    f = got["19.A"]
    assert f.outcome.value == outcome, (f.rows, f.summary, f.rationale)
    assert [r for r in f.rows if r != "A5"] == rows, f.rows
    if case == "search-finds-nothing":
        assert "sitemap.html" in f.summary  # suggested, never visited


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


async def test_the_result_names_the_call_that_adds_the_suggested_pages(
    settings,
    server,
    drafts,  # noqa: F811
):
    """Post-round 1 fix 18: an agent named the suggestion but never made the
    call. next_step now spells it out: 19.A alone, the pages given before
    plus the suggested ones, made without asking the user."""
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    page, others = EXPECTED["search-finds-nothing"][:2]
    given = [f"{server.base}/19a/{o}.html" for o in others]
    out = await run_tt_tests(
        settings, f"{server.base}/19a/{page}.html", [TestId.T19A], other_pages=given
    )
    assert "follow_up_calls" in out.next_step
    assert "finish=true" in out.next_step
    [call] = out.follow_up_calls
    assert call["tests"] == ["19.A"] and call["url"].endswith(f"/{page}.html")
    assert any(p.endswith("sitemap.html") for p in call["other_pages"])
    assert all(g in call["other_pages"] for g in given)  # kept


async def test_finish_makes_the_suggested_pages_call_once(
    settings,
    server,
    drafts,  # noqa: F811
):
    """Agent follow-through plan, change 1: tobi_run_status finish=true makes
    19.A's follow-up call itself (Abby, 2026-11-06: the server may visit
    the suggested pages), records it in the report, and never makes it
    twice."""
    from tobi508 import jobs
    from tobi508.models import Report, TestId
    from tobi508.pipeline import run_tt_tests
    from tobi508.runlog import RunRecorder
    from tobi508.tools.run_status import _start_follow_ups

    page, others = EXPECTED["search-finds-nothing"][:2]
    url = f"{server.base}/19a/{page}.html"
    given = [f"{server.base}/19a/{o}.html" for o in others]
    job = jobs.start(
        settings,
        url,
        lambda p: run_tt_tests(settings, url, [TestId.T19A], p, False, given),
    )
    first = await jobs.wait(job, 300)
    assert first.work == "incomplete" and first.remaining.follow_up_calls == 1

    started = [j for j in _start_follow_ups(settings) if j.url == url]
    assert len(started) == 1 and started[0].tests == ["19.A"]
    second = await jobs.wait(started[0], 300)
    assert second.run_id != first.run_id
    assert any(p.url.endswith("sitemap.html") for p in second.report.other_pages)

    run = RunRecorder.open(settings.runs_dir, first.run_id)
    report = Report.model_validate_json(run.report_path.read_text("utf-8"))
    assert report.follow_up_calls == []
    assert report.follow_ups_made[0]["job_id"] == started[0].id
    _start_follow_ups(settings)  # a second finish: nothing more from the first run
    report = Report.model_validate_json(run.report_path.read_text("utf-8"))
    assert len(report.follow_ups_made) == 1


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
