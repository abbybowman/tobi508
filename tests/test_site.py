"""site.py: the per-page read 9.A-9.C share, and its matching helpers."""

from __future__ import annotations

from tobi508.site import (
    PageRead,
    SiteRead,
    before,
    norm_href,
    pair_aligned,
    pair_in_order,
    read_page,
    repeated_flags,
)

CASES = "WAI/content-assets/wcag-act-rules/testcases"
CH2 = "WAI/content-assets/wcag-act-rules/test-assets/bypass-blocks-cf77f2/chapter2.html"


def _opener(browser, url):
    async def new_page():
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(url)
        return ctx, page

    return new_page


async def _read(browser, n, url):
    return await read_page(n, url, _opener(browser, url))


async def test_units_regions_and_repetition(browser, act_server):
    main = await _read(
        browser,
        0,
        f"{act_server}/{CASES}/cf77f2/235a899f291a8dbcd536b439728c2af509c8f1d6.html",
    )
    ch2 = await _read(browser, 1, f"{act_server}/{CH2}")
    assert not main.error and not ch2.error
    kinds = [(u.kind, u.role, u.text[:20]) for u in main.units]
    assert kinds[0] == ("control", "link", "skip to main content")
    assert kinds[1][:2] == ("control", "link")
    assert main.units[0].href_attr == "#main" and main.units[0].stop
    aside = next(u for u in main.units if u.text.startswith("the romance"))
    assert aside.regions == ["complementary|#about-book"]
    assert {r.key for r in ch2.regions} >= {
        "navigation|#chapters-navigation",
        "complementary|#about-book",
        "main|@1",
    }
    flags = repeated_flags(SiteRead(pages=[main, ch2]))
    assert [u.text[:12] for u, f in zip(main.units, flags, strict=True) if f] == [
        "the romance "
    ]


def test_helpers():
    page = "https://a.gov/x/page.html"
    assert norm_href("https://a.gov/x/page.html#main", page) == "#main"
    assert norm_href("https://a.gov/about/", page) == "https://a.gov/about"
    assert norm_href("https://a.gov/about#team", page) == "https://a.gov/about"
    assert before([0, 0, 10, 10], [0, 20, 10, 10])  # above
    assert before([0, 0, 10, 10], [20, 0, 10, 10])  # same line, left
    assert not before([20, 0, 10, 10], [0, 0, 10, 10])
    assert not before([0, 0, 0, 0], [0, 20, 10, 10])  # no box: not compared
    assert pair_in_order([("a", 0), ("b", 1), ("a", 2)], [("a", 5), ("a", 7)]) == [
        (0, 5),
        (2, 7),
    ]
    assert SiteRead(pages=[PageRead(n=0, url="", error="X")]).errors == [
        "the tested page could not be read: X"
    ]


def test_other_pages_are_checked_before_anything_runs(settings):
    import pytest

    from tobi508.pipeline import RunRefused, check_other_pages

    url = "http://127.0.0.1:8000/a.html"
    same = "http://127.0.0.1:8000/b.html"
    assert check_other_pages(settings, url, [same, same]) == [same]
    with pytest.raises(RunRefused, match="not allowed"):
        check_other_pages(settings, url, ["https://example.com/b"])
    with pytest.raises(RunRefused, match="same site"):
        settings.allowed_domains = ["127.0.0.1", "localhost"]
        check_other_pages(settings, url, ["http://localhost:8000/b.html"])
    with pytest.raises(RunRefused, match="itself"):
        check_other_pages(settings, url, [url + "#top"])
    six = [f"{same}?{i}" for i in range(6)]
    with pytest.raises(RunRefused, match="At most 5 .*no_time_limit=true"):
        check_other_pages(settings, url, six)
    # The cap keeps a call within its time limit; without the limit, more.
    assert check_other_pages(settings, url, six, no_time_limit=True) == six
    with pytest.raises(RunRefused, match="At most 50"):
        check_other_pages(
            settings, url, [f"{same}?{i}" for i in range(51)], no_time_limit=True
        )


def test_the_tested_page_under_another_spelling_is_refused_before_anything_runs(
    settings,
):
    """K-01: the same address with a trailing slash, another scheme, a
    different case in the host or a fragment is the tested page itself.
    (A query string can make a different page, so it is not equated.)"""
    import pytest

    from tobi508.pipeline import RunRefused, check_other_pages, same_address

    url = "http://127.0.0.1:8000/a/"
    for spelling in (
        "http://127.0.0.1:8000/a",
        "http://127.0.0.1:8000/a/#top",
        "https://127.0.0.1:8000/a/",
        "http://127.0.0.1:8000/a/?",
    ):
        assert same_address(url, spelling), spelling
        with pytest.raises(RunRefused, match="itself"):
            check_other_pages(settings, url, [spelling])
    assert not same_address(url, "http://127.0.0.1:8000/a/?x=1")
    assert not same_address(url, "http://127.0.0.1:8000/b/")
    # Two spellings of one other page are one page.
    other = "http://127.0.0.1:8000/b"
    assert check_other_pages(settings, url, [other, other + "/", other + "#x"]) == [
        other
    ]


async def test_an_other_page_that_redirects_to_the_tested_page_is_refused(
    settings, server
):
    """K-01: after recording, the final addresses are compared: the tested
    page is not compared with itself (9.B and 9.C would PASS on no evidence)."""
    import pytest

    from tobi508.models import TestId
    from tobi508.pipeline import RunRefused, run_tt_tests

    with pytest.raises(RunRefused, match="same page as the tested page"):
        await run_tt_tests(
            settings,
            f"{server.base}/dyn",
            [TestId.T9B],
            other_pages=[f"{server.base}/redir-ok"],
        )


async def test_an_other_page_with_the_tested_pages_own_content_is_not_compared(
    settings, server
):
    """K-01 (Abby, 2026-11-12): `?x=1` can be another page, so the address is
    not refused; but when the recorded document is byte-for-byte the tested
    page's, 9.A to 9.C would compare a page with itself and PASS on no
    evidence. They are NEEDS REVIEW, not performed, and say why."""
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    url = f"{server.base}/9x/a1-home.html"
    out = await run_tt_tests(
        settings,
        url,
        [TestId.T9A, TestId.T9B, TestId.T9C],
        other_pages=[url + "?x=1"],
    )
    assert out.errors == [], out.errors
    assert out.report.other_pages[0].same_content_as_tested is True
    for f in out.report.findings:
        assert f.outcome.value == "NEEDS_REVIEW", (f.test_id, f.rows, f.summary)
        assert f.note == "This test could not be performed", f.test_id
        assert "is the tested page again" in f.summary, (f.test_id, f.summary)


async def test_a_copy_is_left_out_and_the_rest_are_compared(settings, server):
    """Step 26 (#134; Abby, 2026-11-20): one usable other page is enough, so
    a copy of the tested page among the pages given is left out, named, and
    the test decides on the rest; it says how many it compared."""
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    url = f"{server.base}/9x/a1-home.html"
    out = await run_tt_tests(
        settings,
        url,
        [TestId.T9A, TestId.T9B],
        other_pages=[url + "?x=1", f"{server.base}/9x/a2-benefits.html"],
    )
    for f in out.report.findings:
        assert f.rows[0] != "A2", (f.test_id, f.rows, f.summary)
        want = "compared this page with 1 of the 2 other pages given: /9x/a2-benefits"
        assert want in f.summary, f.summary
        # Addresses in output have no query string (redact.safe_url).
        assert "/9x/a1-home.html is the tested page again" in f.summary, f.summary


async def test_one_document_at_two_paths_is_two_pages(settings, server):
    """Step 26 (#134; plan after round 3, cause 5): an application sends one
    document for every address and draws each page in the browser (round 3's
    p07 to p10). The same bytes at another path are not the tested page
    again: the pages are compared once drawn."""
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    out = await run_tt_tests(
        settings,
        f"{server.base}/9x/app/home.html",
        [TestId.T9A, TestId.T9B, TestId.T9C],
        other_pages=[f"{server.base}/9x/app/forum.html"],
    )
    assert out.report.other_pages[0].same_content_as_tested is False
    for f in out.report.findings:
        assert f.rows[0] != "A2", (f.test_id, f.rows, f.summary)
        want = "compared this page with 1 of the 1 other page given: /9x/app/forum"
        assert want in f.summary, f.summary
    # The repeated header and menu, drawn on both, come before the main
    # content, and nothing bypasses them.
    nine_a = next(f for f in out.report.findings if f.test_id is TestId.T9A)
    assert nine_a.outcome.value == "FAIL", (nine_a.rows, nine_a.summary)


def _pairs(a: str, b: str):
    """Keys are the letters; positions are the indexes."""
    return pair_aligned(list(zip(a, range(len(a)))), list(zip(b, range(len(b)))))


def test_equal_items_pair_by_an_alignment_that_keeps_their_order():
    """9.B 1.7.0 (step 31): an extra copy of a repeated key is an insertion."""
    # "H" three times against four, the social links "xy" between the last two
    assert _pairs("HHxyH", "HHHxyH") == [(0, 0), (1, 1), (2, 3), (3, 4), (4, 5)]
    # the extra copy is the first, the middle or the last: the same pairs
    # for the unique items around it
    assert _pairs("HabH", "HHabH")[1:3] == [(1, 2), (2, 3)]
    assert _pairs("aHbH", "aHbHH") == [(0, 0), (1, 1), (2, 2), (3, 3)]
    # no repeated key: as before
    assert _pairs("abc", "abc") == [(0, 0), (1, 1), (2, 2)]
    assert _pairs("abc", "xbz") == [(1, 1)]


def test_a_real_reorder_still_crosses_in_the_alignment():
    # two different links swapped: one stays, the other pairs across it
    assert _pairs("abc", "bac") == [(0, 1), (1, 0), (2, 2)]
    # repeated links whose first copies change places around a link between
    # them: the unaligned copies of each key pair in order, so they cross
    assert _pairs("HSCHC", "CSHHC") == [(0, 2), (1, 1), (2, 0), (3, 3), (4, 4)]
    # an equal number of unaligned copies is a move, not an insertion
    assert _pairs("HSH", "SHH") == [(0, 1), (1, 0), (2, 2)]


def test_a_long_list_pairs_in_order(monkeypatch):
    from tobi508 import site

    monkeypatch.setattr(site, "ALIGN_MAX_CELLS", 0)
    assert _pairs("HabH", "aHHbH") == pair_in_order(
        list(zip("HabH", range(4))), list(zip("aHHbH", range(5)))
    )


async def test_an_other_page_drawn_late_is_read_twice(settings, server):
    """The double read (#134; Abby, 2026-11-20): an other page that draws
    itself after load is read twice. Drawn the same way each time, it is
    compared; drawn differently, it could not be read in full and is left
    out, so the test never decides on a read that may be incomplete (round
    3's gate: 9.A DOES NOT APPLY on the forum where the key fails). Two
    reads that differ: test_two_reads_that_differ_leave_the_page_out."""
    from tobi508 import pagecache
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    pagecache.clear()
    base = f"{server.base}/9x/app"
    out = await run_tt_tests(
        settings,
        f"{base}/forum.html",
        [TestId.T9A],
        other_pages=[f"{base}/late-home.html"],
    )
    [f] = out.report.findings
    assert f.rows[0] != "A2", (f.rows, f.summary)
    assert "compared this page with 1 of the 1 other page given" in f.summary


async def test_two_reads_that_differ_leave_the_page_out(monkeypatch):
    """The double read's other side, without a browser: the second read of a
    page drawn late shows another header, so the page could not be read in
    full; one that shows the same texts is used."""
    from types import SimpleNamespace

    from tobi508 import site
    from tobi508.site import PageRead, Unit

    def read(*texts):
        units = [
            Unit(i=i, kind="control", role="link", text=t, css=f"a:nth-of-type({i})")
            for i, t in enumerate(texts)
        ]
        return PageRead(n=7, url="https://a.gov/app/home", units=units, drew_late=True)

    header = ["hub", "home", "forum", "search", "user menu", "privacy"]
    tags = [f"tag {i}" for i in range(14)]
    first = read(*header, *tags)  # 20 texts
    for second, left_out in (
        # Part of the header missing (round 3's gate): 15 of 20 shared.
        (read("hub", "home", "forum", *tags[:12]), True),
        # The same texts, or two tags more (round 3's forum): 20 of 22.
        (read(*header, *tags), False),
        (read(*header, *tags, "tag 14", "tag 15"), False),
    ):

        async def again(*_a, second=second, **_k):
            return second

        monkeypatch.setattr(site, "read_page", again)
        ref = SimpleNamespace(n=7, final_url="https://a.gov/app/home", new_page=None)
        got = await site._read_again(ref, first)
        assert bool(got.error) is left_out, got.error
        if left_out:
            assert "two reads of it differed" in got.error
            assert site.left_out_reason(got).startswith("could not be read")
        else:  # the fuller read
            assert len(got.units) == max(len(first.units), len(second.units))
