"""The demo viewer (demo/prescrt-viewer/viewer.html) opened from disk.

It shows SCRT and pre-SCRT files as text only, never as HTML, and makes no
network request. Offline: the page is a file:// URL and loads nothing else.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from playwright.async_api import async_playwright

from tobi508 import scrt

from .conftest import FIXTURES

ROOT = Path(__file__).resolve().parents[1]
VIEWER_DIR = ROOT / "demo" / "prescrt-viewer"
VIEWER = VIEWER_DIR / "viewer.html"
SAMPLE = FIXTURES / "scrt" / "sample-scrt.json"
HOSTILE = '<img src=x onerror="window.__pwned=1"><script>window.__pwned=2</script>'
PNG = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
    "nGNgYGD4DwABBAEAwS2OUAAAAABJRU5ErkJggg=="
)


def _pre_scrt() -> str:
    tool = scrt.Source(by="tool", run_id="r1", outcome="PASS", spec_version="1.0.0")
    rows = [
        scrt.Row(TestID="4.A", TestResult=scrt.ScrtResult.PASS, source=tool),
        scrt.Row(
            TestID="5.C",
            TestResult=scrt.ScrtResult.FAIL,
            TesterComment=HOSTILE,
            ImageSrc=PNG,
            source=tool,
        ),
        scrt.Row(
            TestID="5.C",
            TestResult=scrt.ScrtResult.FAIL,
            location="javascript:alert(1)",
            ImageSrc="https://example.gov/x.png",
            parent=1,
            source=tool,
        ),
        scrt.Row(
            TestID="9.A",
            needs_review=True,
            source=scrt.Source(by="tool", outcome="NEEDS_REVIEW"),
        ),
        scrt.Row(
            TestID="1.A",
            needs_review=True,
            TesterComment="This test could not be performed: not yet.",
            source=scrt.Source(by="tool", outcome="NEEDS_REVIEW", performed=False),
        ),
    ]
    return scrt.dump(scrt.PreScrt(Criteria=rows))


async def _open(pw):
    browser = await pw.chromium.launch()
    page = await browser.new_page()
    errors: list[str] = []
    requests: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on(
        "console",
        lambda m: errors.append(m.text) if m.type in ("error", "warning") else None,
    )
    page.on("request", lambda r: requests.append(r.url))
    await page.goto(VIEWER.as_uri())
    return browser, page, errors, requests


def test_viewer_html_is_built_from_its_sources():
    out = subprocess.run(
        [sys.executable, str(VIEWER_DIR / "build.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr


async def test_viewer_shows_scrt_and_pre_scrt_files_as_text(tmp_path):
    pre = tmp_path / "page.pre-scrt.json"
    pre.write_text(_pre_scrt())
    bad = tmp_path / "other.json"
    bad.write_text(json.dumps({"hello": "world"}))
    async with async_playwright() as pw:
        browser, page, errors, requests = await _open(pw)

        # An SCRT file: every row, a neutral line, no warning banner.
        await page.set_input_files("#primary-file", str(SAMPLE))
        await page.wait_for_selector("#results")
        rows = len(json.loads(SAMPLE.read_text())[0]["Criteria"])
        assert await page.locator("#results tbody tr").count() == rows
        assert "SCRT file" in await page.inner_text("#status")
        assert "a person's SCRT record" in await page.inner_text("#banner")
        assert await page.locator("#banner.warn").count() == 0

        # A pre-SCRT file: the banner with the file's disclaimer.
        await page.set_input_files("#primary-file", str(pre))
        await page.wait_for_selector("#results tbody tr >> nth=4")
        assert await page.locator("#results tbody tr").count() == 5
        assert "pre-SCRT file" in await page.inner_text("#status")
        banner = await page.inner_text("#banner.warn")
        assert "not a Trusted Tester's record" in banner
        assert scrt.PreScrt().disclaimer in banner

        needs = page.locator("#results tbody tr", has_text="9.A")
        assert "Needs review: a person must decide" in await needs.inner_text()
        not_done = page.locator("#results tbody tr", has_text="1.A")
        assert "This test could not be performed" in await not_done.inner_text()

        # File text is shown as text and runs nothing; only data: images show.
        hostile = page.locator("#results tbody tr").nth(1)
        assert HOSTILE in await hostile.inner_text()
        assert await page.evaluate("window.__pwned") is None
        assert await page.locator("#results img[src='x']").count() == 0
        assert await page.locator("#results script").count() == 0
        assert await page.locator("#results img").count() == 1
        assert await page.locator("#results a").count() == 0
        child = page.locator("#results tbody tr.child")
        assert "https://example.gov/x.png" in await child.inner_text()

        # Filters: only rows needing a person.
        await page.check("#filter-person")
        assert await page.locator("#results tbody tr:visible").count() == 2

        # Compare with the SCRT sample: results side by side, differences marked.
        await page.set_input_files("#compare-file", str(SAMPLE))
        await page.wait_for_selector("#results th.cmp")
        assert await page.locator("#results tr.differs").count() >= 1

        # Not a report: an error, and nothing rendered.
        await page.set_input_files("#primary-file", str(bad))
        await page.wait_for_selector("#error:not(:empty)")
        assert "not a pre-SCRT file" in await page.inner_text("#error")
        assert await page.locator("#report").is_hidden()
        assert await page.locator("#results").count() == 0

        assert errors == []
        assert requests == [VIEWER.as_uri()]
        await browser.close()
