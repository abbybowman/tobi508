"""Freezing a round (evals/agent/freeze.py) and Agent B's browser on it in
Playwright MCP (evals/agent/node/frozen-init.cjs): the tested pages only
from the frozen copies; other pages of the tested site live, logged and
through the egress proxy; other sites refused."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evals.agent.arms import PLAYWRIGHT_MCP as MCP_BIN
from evals.agent.arms import browser_arm
from evals.agent.freeze import freeze
from tobi508.egress import EgressProxy

from .conftest import LocalServer


async def _frozen_round(settings, tmp_path, stop=True) -> tuple[Path, list[str]]:
    srv = LocalServer()
    urls = [
        f"{srv.base}/19a/t-benefits.html",
        f"{srv.base}/19a/home.html",
    ]
    rd = tmp_path / "round"
    rd.mkdir()
    (rd / "pages.txt").write_text("".join(f"{u} {'ab' * 32}\n" for u in urls))
    try:
        log = await freeze(rd, settings)
    finally:
        if stop:
            srv.stop()  # from here on, the site is down
    assert {e["status"] for e in log["pages"].values()} == {"frozen"}
    return rd, (urls if stop else (urls, srv))


async def test_freeze_records_the_tested_pages_and_their_searches(settings, tmp_path):
    """Since step 6c the freeze also records 19.A's site search for each
    page (plain, then quoted), and nothing else: no site map, no link."""
    rd, urls = await _frozen_round(settings, tmp_path)
    index = json.loads((rd / "frozen" / "index.json").read_text())
    searches = sorted(set(index) - set(urls))
    assert set(urls) <= set(index)
    assert searches and all("/19a/search.html?" in u for u in searches), searches
    assert not any("sitemap" in u for u in index)
    log = json.loads((rd / "frozen" / "freeze.json").read_text())
    assert log["recordings"] == len(index)
    got = log["searches"][urls[0]]["searches"]
    assert [i["status"] for i in got] == ["frozen"] * len(got), got


async def test_a_replay_of_the_frozen_set_needs_nothing_live(settings, tmp_path):
    """19.A on the frozen set with the site down, in replay mode: its search
    comes from the folder and finds the page, as the live search did
    (test_fixtures_19a "nav-and-live-search": W1 W2 G2)."""
    from .harness import run_tests

    rd, urls = await _frozen_round(settings, tmp_path)
    s = settings.model_copy(
        update={"frozen_pages_dir": rd / "frozen", "frozen_pages_mode": "replay"}
    )
    got = await run_tests(s, urls[0], ["19.A"], {}, other_pages=[urls[1]])
    f = got["19.A"]
    assert f.outcome.value == "PASS", (f.rows, f.summary)
    assert [r for r in f.rows if r != "A5"] == ["W1", "W2", "G2"]


async def test_the_freeze_scrolls_so_content_shown_on_view_is_recorded(
    settings, tmp_path
):
    """An image a script shows only when it comes into view, 2,500 px down:
    a jump to the bottom never shows it; a window-by-window scroll does."""
    from playwright.async_api import async_playwright

    from tobi508.browser import launch_browser
    from tobi508.capture import record

    srv = LocalServer()
    url = f"{srv.base}/lazy/l07-lazy-images.html"
    seen = {}
    try:
        async with EgressProxy(settings) as proxy, async_playwright() as pw:
            browser = await launch_browser(pw, settings, proxy)
            for steps in (False, True):
                s = settings.model_copy(update={"record_scroll_steps": steps})
                har = tmp_path / f"{steps}.har.zip"
                await record(browser, s, url, har, lambda *a, **k: None, proxy)
                import zipfile

                with zipfile.ZipFile(har) as z:
                    name = next(n for n in z.namelist() if n.endswith(".har"))
                    entries = json.loads(z.read(name))["log"]["entries"]
                seen[steps] = any(
                    e["request"]["url"].endswith("/lazy/l07-middle.svg")
                    for e in entries
                )
            await browser.close()
    finally:
        srv.stop()
    assert seen == {False: False, True: True}, seen


async def test_media_chosen_first_puts_each_players_file_first(settings):
    """With two players, each player's chosen file comes before any
    alternative, so a cap spends itself on what a replay plays."""
    from playwright.async_api import async_playwright

    from tobi508.capture import _MEDIA_JS

    html = (
        "<video><source src='https://example.gov/a.mov' type='video/quicktime'>"
        "<source src='https://example.gov/a.webm' type='video/webm'></video>"
        "<video><source src='https://example.gov/b.mov' type='video/quicktime'>"
        "<source src='https://example.gov/b.webm' type='video/webm'></video>"
    )
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.route("**/*", lambda r: r.abort())
        await page.set_content(html)
        await page.wait_for_function(
            "() => [...document.querySelectorAll('video')].every((v) => v.currentSrc)"
        )
        first = await page.evaluate(_MEDIA_JS, True)
        plain = await page.evaluate(_MEDIA_JS, False)
        await browser.close()
    assert first[:2] == ["https://example.gov/a.webm", "https://example.gov/b.webm"]
    assert plain[:2] == ["https://example.gov/a.webm", "https://example.gov/a.mov"]


def _text(res) -> str:
    return "".join(c.text for c in res.content if hasattr(c, "text"))


@pytest.mark.skipif(not MCP_BIN.exists(), reason="npm install in evals/agent/node")
async def test_agent_b_browser_rules(settings, tmp_path):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from playwright.async_api import async_playwright

    rd, (urls, srv) = await _frozen_round(settings, tmp_path, stop=False)
    try:
        hits_before = srv.hits[("127.0.0.1", "/19a/t-benefits.html")]
        async with async_playwright() as pw:
            chrome = pw.chromium.executable_path  # full Chromium, as Agent A's
        live_log = tmp_path / "live.jsonl"
        async with EgressProxy(settings) as proxy:
            (srv_def,) = browser_arm(
                rd / "frozen", tmp_path / "out", chrome, proxy.url, live_log
            )
            params = StdioServerParameters(
                command=srv_def.command, args=srv_def.args, env=srv_def.env
            )
            async with stdio_client(params) as (r, w), ClientSession(r, w) as mcp:
                await mcp.initialize()
                # A tested page: its frozen copy, never the live site.
                got = await mcp.call_tool("browser_navigate", {"url": urls[0]})
                assert "Page Title: Apply for benefits" in _text(got), _text(got)[:2000]
                # Automatic snapshots go to a file Agent B cannot open (it has no
                # file tools); browser_snapshot returns the page inline.
                snap = _text(await mcp.call_tool("browser_snapshot", {}))
                assert "heading" in snap and "Apply for benefits" in snap
                # Another page of the tested site: live, as for Agent A.
                smap = await mcp.call_tool(
                    "browser_navigate", {"url": f"{srv.base}/19a/sitemap.html"}
                )
                assert "Page Title: Site map" in _text(smap), _text(smap)[:2000]
                # Another site: refused.
                other = await mcp.call_tool(
                    "browser_navigate",
                    {"url": f"http://localhost:{srv.port}/19a/sitemap.html"},
                )
                assert other.is_error or "ERR_BLOCKED" in _text(other)
            connected = list(proxy.connected)
        assert srv.hits[("127.0.0.1", "/19a/t-benefits.html")] == hits_before
        assert srv.hits[("127.0.0.1", "/19a/sitemap.html")] >= 1
        assert srv.hits[("localhost", "/19a/sitemap.html")] == 0
        rows = [json.loads(x) for x in live_log.read_text().splitlines()]
        assert any(r.get("live") and r["url"].endswith("/sitemap.html") for r in rows)
        assert any(r.get("refused") and "localhost" in r["url"] for r in rows)
        assert connected, "live loads go through the egress proxy"
    finally:
        srv.stop()


def _fail_in_har(har: Path, path: str) -> None:
    """Mark `path`'s response failed (status -1) in a recording, as a
    recording made where the file could not load would have it."""
    import zipfile

    with zipfile.ZipFile(har) as z:
        files = {n: z.read(n) for n in z.namelist()}
    name = next(n for n in files if n.endswith(".har"))
    data = json.loads(files[name])
    hit = [e for e in data["log"]["entries"] if e["request"]["url"].endswith(path)]
    assert hit, f"{path} is not in {har}"
    for e in hit:
        e["response"]["status"] = -1
    files[name] = json.dumps(data).encode()
    with zipfile.ZipFile(har, "w") as z:
        for n, b in files.items():
            z.writestr(n, b)


@pytest.mark.skipif(not MCP_BIN.exists(), reason="npm install in evals/agent/node")
async def test_one_failed_copy_does_not_hide_a_good_one(settings, tmp_path):
    """Round 1: a recording whose shared files had failed made Agent B's
    browser fail them on every page, though other recordings held them."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from playwright.async_api import async_playwright

    srv = LocalServer()
    urls = [f"{srv.base}/dyn", f"{srv.base}/landed"]  # both fetch /data.json
    rd = tmp_path / "round"
    rd.mkdir()
    (rd / "pages.txt").write_text("".join(f"{u} {'ab' * 32}\n" for u in urls))
    try:
        await freeze(rd, settings)
    finally:
        srv.stop()
    index = json.loads((rd / "frozen" / "index.json").read_text())
    _fail_in_har(rd / "frozen" / index[urls[1]]["har"], "/data.json")
    async with async_playwright() as pw:
        chrome = pw.chromium.executable_path
    (srv_def,) = browser_arm(rd / "frozen", tmp_path / "out", chrome)
    params = StdioServerParameters(
        command=srv_def.command, args=srv_def.args, env=srv_def.env
    )
    async with stdio_client(params) as (r, w), ClientSession(r, w) as mcp:
        await mcp.initialize()
        await mcp.call_tool("browser_navigate", {"url": urls[0]})
        await mcp.call_tool("browser_wait_for", {"time": 1})
        got = _text(
            await mcp.call_tool(
                "browser_evaluate", {"function": "() => xhr.textContent"}
            )
        )
    assert '"0.' in got, got[:1500]  # the nonce from /dyn's own recording


def test_the_freeze_flags_a_404_page_and_a_page_without_its_assets(tmp_path):
    """Post-round 1 fix 7: a typo froze NASA's 404 page, and a page frozen in
    the container had its HTML but no CSS or scripts. Both are suspect."""
    import zipfile

    from evals.agent.freeze import check_recording

    def har(name, doc_status, asset_status):
        def entry(url, status, mime, text=""):
            return {
                "request": {"url": url},
                "response": {
                    "status": status,
                    "content": {"mimeType": mime, "text": text},
                },
            }

        page = "<title>Page Not Found</title><h1>Oops</h1>"
        entries = [entry("https://x.gov/p", doc_status, "text/html", page)] + [
            entry(f"https://x.gov/{n}.css", asset_status, "text/css") for n in range(3)
        ]
        p = tmp_path / f"{name}.har.zip"
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("har.har", json.dumps({"log": {"entries": entries}}))
        return p

    typo = check_recording(har("typo", 404, 200), "https://x.gov/p")
    assert typo["suspect"] == "the page itself answered 404"
    assert typo["title"] == "Page Not Found" and typo["heading"] == "Oops"
    bare = check_recording(har("bare", 200, -1), "https://x.gov/p")
    assert bare["suspect"] == "3 of 3 CSS, font and script requests failed"
    ok = check_recording(har("ok", 200, 200), "https://x.gov/p")
    assert "suspect" not in ok and ok["assets"] == 3
