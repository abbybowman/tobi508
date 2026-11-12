"""Run TT tests on one of the review's small pages and print the outcome.

Usage, from the repository root:

    uv run python docs/reviews/2026-11-11-code-review-pages/runpage.py \
        <group>/<page.html> <tests> [other pages ...]

`<tests>` is a comma-separated list such as `4.A,4.C`. Pages are served
from `pages/` beside this file on 127.0.0.1; other pages are named the
same way (`v/site-a.html?x=1`). Set `RL=17` to hold the run to 17 seconds
(`no_time_limit=false`). Nothing here is a test: the README lists what
each page printed on 2026-11-11 and 12.
"""

import asyncio
import http.server
import ipaddress
import os
import sys
import tempfile
import threading
from pathlib import Path

from tobi508 import egress
from tobi508.config import Settings
from tobi508.models import TestId
from tobi508.pipeline import run_tt_tests

PAGES = Path(__file__).parent / "pages"


async def offline_resolver(host: str, port: int) -> list[str]:
    if host == "localhost":
        return ["127.0.0.1"]
    return [str(ipaddress.ip_address(host))]


egress.RESOLVER = offline_resolver


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PAGES), **kwargs)

    def log_message(self, *args) -> None:
        pass


def serve() -> int:
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]


async def main() -> None:
    port = serve()
    runs = Path(tempfile.mkdtemp()) / "runs"
    settings = Settings(
        _env_file=None,
        allowed_domains=["127.0.0.1"],
        dev_mode=True,
        browser_channel="chromium",
        headless=True,
        browser_args=["--disable-features=LocalNetworkAccessChecks"],
        runs_dir=runs,
        dev_allowed_addresses=["127.0.0.1/32"],
        call_wait_s=600,
        run_limit_s=int(os.environ.get("RL", "120")),
        page_cache_s=0,
    )
    base = f"http://127.0.0.1:{port}/"
    url = base + sys.argv[1]
    tests = [TestId(t) for t in sys.argv[2].split(",")]
    others = [base + o for o in sys.argv[3:]]
    try:
        if others:
            out = await run_tt_tests(settings, url, tests, None, True, others)
        else:
            out = await run_tt_tests(settings, url, tests)
    except Exception as exc:
        print("ERROR", type(exc).__name__, exc)
        return
    print("errors:", out.errors)
    for f in out.report.findings:
        print(f.test_id.value, f.outcome.value, f.rows, "|", f.summary[:400])
    print("open questions:", [q.question_id for q in out.report.open_questions][:20])
    print("run folder:", runs / out.run_id)


asyncio.run(main())
