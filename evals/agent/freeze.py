"""Freeze a round's tested pages once, for both arms of the agent eval
(docs/plans/2026-10-31-agent-eval.md section 6).

    uv run python -m evals.agent.freeze evals/judging/<round>

(headless: BROWSER_CHANNEL=chromium HEADLESS=true; --accept-suspect calls a
recording frozen even when it looks broken: a 404 page, or most of its CSS,
fonts and scripts missing)

Each page in <round>/pages.txt is recorded once, as a live run records it
(capture.record: the allowlist and every redirect hop checked, scrolled to
load lazy content), into <round>/frozen/ (index.json, the recordings and
freeze.json). Since roadmap step 6c (round 3 on; a locked round's frozen
set is never recorded again) the freeze also:
  * scrolls each page down one window at a time, so images that load when
    they come into view are recorded (`record_scroll_steps`; since step
    10a whatever the page's scroll behaviour, and each page's
    `capture_scroll_steps` line, with `reached_end`, is kept in
    freeze.json);
  * lists every frame the recording does not hold, seen live or asked for
    by one replay of the copy (`frames_not_recorded`, step 10a: a report,
    not a fix);
  * stores the media file each player chose, in full, before any
    alternative source (`media_chosen_first`, caps MEDIA_CAP_MB and
    MEDIA_CAP_S per page);
  * records 19.A's site search for each page: the same form and term 19.A
    would use (the page's first heading, plain and in quotation marks),
    read from the frozen copies, so a replay needs nothing live.
Other routes an agent tries (site maps, any other page) still load live in
"tested_frozen" mode.

In a cloud container, set UPSTREAM_PROXY to the container's HTTPS_PROXY
first (docs/solutions/environment.md): otherwise the browser refuses the
container's certificates and pages are frozen without their CSS and scripts
(the check below calls them suspect).

This step touches the live site, close to the tester's own testing; compare
each page's footer timestamp with the tester's after freezing.
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

from evals.judging import JudgingError, _pages
from tobi508.browser import launch_browser
from tobi508.config import Settings
from tobi508.egress import EgressProxy
from tobi508.frozen import load, obtain
from tobi508.policy import check_url
from tobi508.redact import safe_error

FROZEN = "frozen"
MEDIA_CAP_MB = 500  # per page: round 2's chosen files were 2-92 MB
MEDIA_CAP_S = 300
ASSET_TYPES = ("stylesheet", "script", "font")
MOST = 0.5  # more than half the CSS, font and script requests failed


def _kind(e: dict) -> str | None:
    t = (e.get("_resourceType") or "").lower()
    if t in ASSET_TYPES:
        return t
    mime = (e.get("response", {}).get("content", {}).get("mimeType") or "").lower()
    url = e.get("request", {}).get("url", "").split("?")[0].lower()
    if "css" in mime or url.endswith(".css"):
        return "stylesheet"
    if "javascript" in mime or url.endswith((".js", ".mjs")):
        return "script"
    if "font" in mime or url.endswith((".woff", ".woff2", ".ttf", ".otf")):
        return "font"
    return None


def check_recording(har_zip: Path, final_url: str) -> dict:
    """What a frozen page's recording holds (post-round 1 fix 7: a typo
    froze a 404 page, and a page frozen in the cloud container had its HTML
    but none of its CSS or scripts; both reached the agents). Returns the
    main document's status, the CSS, font and script requests and how many
    failed, the title and first heading, and `suspect` with the reason."""
    import html
    import re
    import zipfile

    with zipfile.ZipFile(har_zip) as z:
        name = next(n for n in z.namelist() if n.endswith(".har"))
        entries = json.loads(z.read(name))["log"]["entries"]

        def body(e: dict) -> str:
            c = e.get("response", {}).get("content", {})
            if c.get("text") is not None:
                return c["text"]
            f = c.get("_file")
            return z.read(f).decode("utf-8", "replace") if f in z.namelist() else ""

        want = final_url.split("#")[0].rstrip("/")
        doc = next(
            (
                e
                for e in entries
                if e["request"]["url"].split("#")[0].rstrip("/") == want
                and e["response"].get("status", 0) not in (301, 302, 303, 307, 308)
            ),
            None,
        )
        text = body(doc) if doc else ""
    assets = [e for e in entries if _kind(e)]
    failed = [e for e in assets if not 200 <= e["response"].get("status", -1) < 400]

    def first(pattern: str) -> str:
        m = re.search(pattern, text, re.I | re.S)
        raw = re.sub(r"<[^>]+>", " ", m.group(1)) if m else ""
        return html.unescape(re.sub(r"\s+", " ", raw)).strip()[:120]

    status = doc["response"].get("status") if doc else None
    out = {
        "document_status": status,
        "assets": len(assets),
        "assets_failed": len(failed),
        "title": first(r"<title[^>]*>(.*?)</title>"),
        "heading": first(r"<h1[^>]*>(.*?)</h1>"),
    }
    if status is None or not 200 <= status < 300:
        out["suspect"] = f"the page itself answered {status}"
    elif assets and len(failed) > MOST * len(assets):
        out["suspect"] = (
            f"{len(failed)} of {len(assets)} CSS, font and script requests failed"
        )
    return out


async def freeze(rd: Path, settings: Settings, accept: bool = False) -> dict:
    if (rd / "results" / "lock.json").exists():
        raise JudgingError("This round is locked")
    folder = rd / FROZEN
    s = settings.model_copy(
        update={
            "frozen_pages_dir": folder,
            "frozen_pages_mode": "record_missing",
            "record_scroll_steps": True,
            "media_chosen_first": True,
            "media_cap_mb": MEDIA_CAP_MB,
            "media_cap_s": MEDIA_CAP_S,
        }
    )
    pages = [u for u, _ in _pages(rd)]
    log: dict = {"started_at": datetime.now(timezone.utc).isoformat(), "pages": {}}
    async with EgressProxy(s) as proxy, async_playwright() as pw:
        browser = await launch_browser(pw, s, proxy)
        try:
            for url in pages:
                t0 = time.monotonic()
                entry: dict = {}
                print(f"freezing {url}", flush=True)
                decision = check_url(url, s.allowed_domains, s.dev_mode)
                scroll: list[dict] = []

                def keep(step: str, status: str = "ok", **detail) -> None:
                    # The scroll's log lines go in freeze.json: a reader checks
                    # that every page's scroll reached its end (step 10a).
                    if step.startswith("capture_scroll"):
                        scroll.append({"step": step, "status": status, **detail})

                try:
                    if not decision.allowed:
                        raise ValueError(f"not allowed: {decision.reason}")
                    with tempfile.TemporaryDirectory() as tmp:
                        cap = await obtain(
                            browser,
                            s,
                            url,
                            Path(tmp) / "page.har.zip",
                            keep,
                            proxy,
                        )
                    entry.update(
                        status="frozen",
                        final_url=cap.final_url,
                        cross_site_frames=len(cap.cross_site_frames),
                        scroll=scroll,
                        scroll_reached_end=any(x.get("reached_end") for x in scroll),
                    )
                    rec = load(folder).get(url)
                    if rec is not None:
                        entry.update(check_recording(folder / rec.har, cap.final_url))
                        entry["frames_not_recorded"] = await frames_not_recorded(
                            browser, s, folder / rec.har, rec.final_url, cap.frame_urls
                        )
                    if entry.get("suspect") and not accept:
                        entry["status"] = "suspect"
                except Exception as exc:  # recorded: the arms are refused it
                    entry.update(status="error", error=safe_error(exc)[:300])
                entry["seconds"] = round(time.monotonic() - t0, 1)
                log["pages"][url] = entry
            log["searches"] = await record_searches(browser, s, proxy, pages)
        finally:
            await browser.close()
    folder.mkdir(parents=True, exist_ok=True)
    log["finished_at"] = datetime.now(timezone.utc).isoformat()
    log["recordings"] = len(load(folder))
    (folder / "freeze.json").write_text(json.dumps(log, indent=1) + "\n")
    return log


def _recorded_urls(har_zip: Path) -> set[str]:
    """Request URLs the recording answers (fragment dropped), with a
    response: a frame the recording asked for and got nothing is not there."""
    import zipfile

    with zipfile.ZipFile(har_zip) as z:
        name = next(n for n in z.namelist() if n.endswith(".har"))
        entries = json.loads(z.read(name))["log"]["entries"]
    return {
        e["request"]["url"].split("#")[0]
        for e in entries
        if e["response"].get("status", 0) > 0
    }


REPLAY_FRAME_WAIT_MS = 5_000


async def frames_not_recorded(
    browser, s: Settings, har_zip: Path, final_url: str, live: list[str]
) -> list[dict]:
    """Every frame the freeze saw whose address the recording does not hold
    (step 10a: a report, not a fix). `live`: the frame addresses at the end
    of the recording; then one replay of the frozen copy is loaded and its
    frame addresses read: one there that the recording lacks is an address
    that differs between two loads (reCAPTCHA, a lazy video embed). Each
    is given without its query; `why` says which."""
    from tobi508.capture import replay_context
    from tobi508.redact import safe_url

    have = _recorded_urls(har_zip)
    out: list[dict] = []

    def add(u: str, why: str) -> None:
        item = {"frame": safe_url(u), "why": why}
        if item not in out:
            out.append(item)

    for u in live:
        if u.split("#")[0] not in have:
            add(u, "not recorded")
    replay = None
    try:
        replay = await replay_context(browser, s, har_zip, lambda *a, **k: None)
        page = await replay.context.new_page()
        asked: list[str] = []

        def note(req) -> None:
            # A frame whose address the recording lacks is aborted, and the
            # frame then shows an error page's address: read the request.
            if (
                req.is_navigation_request()
                and req.frame != page.main_frame
                and req.url.startswith(("http:", "https:"))
            ):
                asked.append(req.url)

        page.on("request", note)
        await replay.guard.goto(page, final_url)
        await page.wait_for_timeout(REPLAY_FRAME_WAIT_MS)
        again = asked + [
            f.url for f in page.frames[1:] if f.url.startswith(("http:", "https:"))
        ]
    except Exception as exc:  # the report says it could not look
        add(final_url, f"replay not read: {type(exc).__name__}")
        again = []
    finally:
        if replay is not None:
            await replay.context.close()
    for u in again:
        if u.split("#")[0] not in have:
            add(u, "differs between two loads")
    return out


async def _read_frozen(browser, s: Settings, url: str):
    """A frozen page read as 19.A reads it (site.read_page on a replay)."""
    from tobi508.capture import replay_context
    from tobi508.site import read_page

    rec = load(s.frozen_pages_dir).get(url)
    if rec is None:
        return None

    async def new_page():
        replay = await replay_context(
            browser, s, s.frozen_pages_dir / rec.har, lambda *a, **k: None
        )
        page = await replay.context.new_page()
        await replay.guard.goto(page, rec.final_url)
        return replay.context, page

    got = await read_page(0, rec.final_url, new_page)
    return None if got.error else got


def search_urls(main, others) -> list[str]:
    """The site searches 19.A would make for `main` (t19a._live_search):
    the first form of the tested page, then of the other pages in the
    caller's order, that the tool can submit; the term, then the term in
    quotation marks."""
    from tobi508.checks.t19a import _term, search_url

    forms = [f for p in [main, *others] for f in p.forms]
    term = _term(main)
    if not term:
        return []
    out = []
    for t in [term] + ([] if '"' in term else [f'"{term}"']):
        u = next((u for u in (search_url(f, t) for f in forms) if u), None)
        if u and u not in out:
            out.append(u)
    return out


async def record_searches(browser, s: Settings, proxy, pages: list[str]) -> dict:
    """Record 19.A's searches for every page into the frozen set, under the
    rules of the live search (allowlist on every hop, the tested page's
    host). Page content chooses only what 19.A's own search would."""
    from evals.judging import other_pages
    from tobi508.pipeline import _same_site

    reads = {u: await _read_frozen(browser, s, u) for u in pages}
    out: dict = {}
    for url in pages:
        main = reads.get(url)
        if main is None:
            out[url] = {"status": "not read"}
            continue
        others = [reads[o] for o in other_pages(url, pages) if reads.get(o)]
        done = []
        for su in search_urls(main, others):
            item: dict = {"url": su}
            done.append(item)
            if not check_url(su, s.allowed_domains, s.dev_mode).allowed or not (
                _same_site(su, main.url)
            ):
                item["status"] = "not allowed"
                continue
            try:
                with tempfile.TemporaryDirectory() as tmp:
                    cap = await obtain(
                        browser,
                        s,
                        su,
                        Path(tmp) / "search.har.zip",
                        lambda *a, **k: None,
                        proxy,
                        tested=False,
                    )
                if not _same_site(cap.final_url, main.url):
                    item["status"] = "left the host"
                    continue
                rec = load(s.frozen_pages_dir).get(su)
                item["status"] = "frozen"
                if rec is not None:
                    item.update(
                        check_recording(s.frozen_pages_dir / rec.har, cap.final_url)
                    )
            except Exception as exc:
                item.update(status="error", error=safe_error(exc)[:300])
        out[url] = {"searches": done}
    return out


def main(argv: list[str]) -> None:
    accept = "--accept-suspect" in argv
    argv = [a for a in argv if a != "--accept-suspect"]
    if len(argv) != 1:
        sys.exit(__doc__)
    log = asyncio.run(freeze(Path(argv[0]), Settings(), accept))
    for u, e in log["pages"].items():
        print(
            f"{u}: {e['status']}; {e.get('document_status')}; "
            f"{e.get('assets_failed')} of {e.get('assets')} CSS/font/script failed; "
            f"title {e.get('title')!r}; heading {e.get('heading')!r}"
            + (f"; SUSPECT: {e['suspect']}" if e.get("suspect") else "")
        )
        if e.get("status") == "frozen":
            last = next(
                (
                    x
                    for x in e.get("scroll") or []
                    if x["step"] == "capture_scroll_steps"
                ),
                {},
            )
            print(
                f"  scroll: reached the end {e.get('scroll_reached_end')}; "
                f"{last.get('steps')} steps, at {last.get('top')} + window "
                f"{last.get('window')} of height {last.get('height')}"
            )
            for f in e.get("frames_not_recorded") or []:
                print(f"  frame not recorded: {f['frame']} ({f['why']})")
    for u, e in log.get("searches", {}).items():
        for item in e.get("searches", []):
            print(
                f"  19.A search for {u}: {item['url']}: {item.get('status')}"
                + (f"; SUSPECT: {item['suspect']}" if item.get("suspect") else "")
            )
    bad = [u for u, e in log["pages"].items() if e["status"] != "frozen"]
    print(f"{log['recordings']} recordings; pages not frozen: {bad or 'none'}")
    if any(e["status"] == "suspect" for e in log["pages"].values()):
        sys.exit(
            "Some recordings look broken (above). Check them, freeze again, or "
            "rerun with --accept-suspect to call them frozen anyway."
        )


if __name__ == "__main__":
    main(sys.argv[1:])
