"""A replay of a page that draws nothing until a hidden frame's silent
sign-in check answers (keycloak-js check-sso; round 3's Data Governance
pages). The check's state changes on every load, so the replay asks an
address the recording never saw. The replay answers it as the recording
did ("not signed in"), with only the new request's state, and logs it."""

from __future__ import annotations

import json
import zipfile

import pytest
from playwright.async_api import async_playwright

from tobi508.browser import launch_browser
from tobi508.capture import (
    record,
    replay_context,
    signin_answers,
    signin_location,
)
from tobi508.egress import EgressProxy

from .conftest import LocalServer

REC = (
    "https://site.gov/app/silent.html#error=login_required&state=OLD"
    "&iss=https%3A%2F%2Fauth.site.gov%2Frealms%2Fx"
)


def test_only_the_state_is_replaced():
    req = "https://auth.site.gov/auth?client_id=a&prompt=none&state=NEW&nonce=n"
    got = signin_location(REC, req)
    assert got == (
        "https://site.gov/app/silent.html#error=login_required&state=NEW"
        "&iss=https%3A%2F%2Fauth.site.gov%2Frealms%2Fx"
    )


@pytest.mark.parametrize(
    "req",
    [
        "https://auth.site.gov/auth?client_id=a&state=NEW",  # not silent
        "https://auth.site.gov/auth?prompt=login&state=NEW",
        "https://auth.site.gov/auth?prompt=none",  # no state
        "https://auth.site.gov/auth?prompt=none&state=a&state=b",
    ],
)
def test_anything_but_a_silent_check_with_one_state_is_not_answered(req):
    assert signin_location(REC, req) is None


def _hits(page_text: str) -> bool:
    return "Knowledge hub" in page_text


async def test_a_replay_answers_the_silent_check_and_the_page_draws(settings, tmp_path):
    srv = LocalServer()
    url = f"{srv.base}/signin/app.html"
    har = tmp_path / "app.har.zip"
    lines: list[tuple[str, dict]] = []
    try:
        async with EgressProxy(settings) as proxy, async_playwright() as pw:
            browser = await launch_browser(pw, settings, proxy)
            await record(browser, settings, url, har, lambda *a, **k: None, proxy)
            srv.stop()  # from here on the site is down: nothing live

            # The recording drew the page and holds the check, answered
            # "not signed in" with the recording's own state.
            [(check, loc)] = signin_answers(har).items()
            assert check == f"{srv.base}/signin/auth"
            assert loc.startswith(f"{srv.base}/signin/silent.html#")

            rp = await replay_context(
                browser, settings, har, lambda st, *a, **k: lines.append((st, k))
            )
            page = await rp.context.new_page()
            await rp.guard.goto(page, url)
            await page.wait_for_function(
                "document.body.innerText.includes('Knowledge hub')", timeout=10_000
            )
            await rp.context.close()
            await browser.close()
    finally:
        srv.stop()
    [made] = [k for st, k in lines if st == "replay_signin_answer"]
    assert made["url"] == f"{srv.base}/signin/auth"
    assert made["to"] == f"{srv.base}/signin/silent.html"


async def test_without_a_recorded_answer_nothing_is_made_up(settings, tmp_path):
    """A recording whose check was not answered "not signed in" (here: the
    redirect removed) gets no answer: the frame is aborted as before and the
    page stays blank."""
    srv = LocalServer()
    url = f"{srv.base}/signin/app.html"
    har = tmp_path / "app.har.zip"
    lines: list[str] = []
    try:
        async with EgressProxy(settings) as proxy, async_playwright() as pw:
            browser = await launch_browser(pw, settings, proxy)
            await record(browser, settings, url, har, lambda *a, **k: None, proxy)
            srv.stop()
            bare = tmp_path / "bare.har.zip"
            with zipfile.ZipFile(har) as z, zipfile.ZipFile(bare, "w") as out:
                for n in z.namelist():
                    data = z.read(n)
                    if n.endswith(".har"):
                        h = json.loads(data)
                        h["log"]["entries"] = [
                            e
                            for e in h["log"]["entries"]
                            if "/signin/auth" not in e["request"]["url"]
                        ]
                        data = json.dumps(h).encode()
                    out.writestr(n, data)
            assert signin_answers(bare) == {}
            rp = await replay_context(
                browser, settings, bare, lambda st, *a, **k: lines.append(st)
            )
            page = await rp.context.new_page()
            await rp.guard.goto(page, url)
            await page.wait_for_timeout(2_000)
            text = await page.evaluate("document.body.innerText")
            await rp.context.close()
            await browser.close()
    finally:
        srv.stop()
    assert not _hits(text)
    assert "replay_signin_answer" not in lines
