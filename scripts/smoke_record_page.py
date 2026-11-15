"""Record one page into a frozen-pages folder, for the hosted smoke test in CI
(.github/workflows/container.yml, job "hosted").

    DEV_MODE=true DEV_ALLOWED_ADDRESSES='["172.30.0.10/32"]' \
        uv run --no-sync python scripts/smoke_record_page.py URL FOLDER

The smoke test's page is served inside the CI job, at a private address the
egress proxy refuses unless DEV_MODE is on. The server under test keeps
DEV_MODE off, so the page reaches it this way instead: this recorder (a
separate container of the same image, with DEV_MODE on and the one
address let through) records the page as a live run would (capture.record:
the allowlist and every redirect hop checked), and the server replays the
recording (FROZEN_PAGES_DIR, FROZEN_PAGES_MODE=replay: a URL with no
recording is a tool error, never fetched live). The URL is under .gov, so
the server's default allowlist passes it unchanged.
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright

from tobi508.browser import launch_browser
from tobi508.config import Settings
from tobi508.egress import EgressProxy
from tobi508.frozen import load, obtain


async def record(url: str, folder: Path) -> None:
    s = Settings(frozen_pages_dir=folder, frozen_pages_mode="record_missing")
    if not s.dev_mode:
        sys.exit("The recorder needs DEV_MODE=true (the server under test never does).")

    def log(step, status="ok", **detail):
        print(step, status, detail)

    with tempfile.TemporaryDirectory() as tmp:
        async with EgressProxy(s) as proxy, async_playwright() as pw:
            browser = await launch_browser(pw, s, proxy)
            try:
                await obtain(browser, s, url, Path(tmp) / "page.har.zip", log, proxy)
            finally:
                await browser.close()
    if url not in load(folder):
        sys.exit(f"{url} was not recorded")
    print("recorded", url, "into", folder)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    asyncio.run(record(sys.argv[1], Path(sys.argv[2])))
