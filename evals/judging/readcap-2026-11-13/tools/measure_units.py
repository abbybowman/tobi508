"""Measure the site read uncapped on round 2's frozen pages: units, controls,
time of the DOM read, JSON size. Replays only (no live fetch)."""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "src"))

from playwright.async_api import async_playwright  # noqa: E402

from tobi508.browser import launch_browser  # noqa: E402
from tobi508.capture import replay_context  # noqa: E402
from tobi508.config import Settings  # noqa: E402
from tobi508.egress import EgressProxy  # noqa: E402
from tobi508.site import READ_JS  # noqa: E402

FROZEN = REPO / "evals/judging/round2/frozen"


async def main() -> None:
    s = Settings(browser_channel="chromium", headless=True)
    index = json.loads((FROZEN / "index.json").read_text())
    out = []
    async with EgressProxy(s) as proxy, async_playwright() as pw:
        browser = await launch_browser(pw, s, proxy, full_chromium=True)
        for url, e in index.items():
            with tempfile.TemporaryDirectory() as td:
                har = Path(td) / "p.har.zip"
                har.write_bytes((FROZEN / e["har"]).read_bytes())
                rp = await replay_context(browser, s, har, lambda *a, **k: None)
                page = await rp.context.new_page()
                t0 = time.monotonic()
                await rp.guard.goto(page, e["final_url"])
                await page.wait_for_load_state("load")
                t_load = time.monotonic() - t0
                row = {"url": url, "load_s": round(t_load, 2)}
                for cap in (600, 100000):
                    t1 = time.monotonic()
                    d = await page.evaluate(READ_JS, cap)
                    row[f"read_{cap}_s"] = round(time.monotonic() - t1, 3)
                    row[f"units_{cap}"] = len(d["units"])
                    row[f"json_kb_{cap}"] = round(len(json.dumps(d)) / 1024)
                    if cap == 100000:
                        u = d["units"]
                        row["controls"] = sum(1 for x in u if x["kind"] == "control")
                        row["truncated_at_600"] = len(u) > 600
                        # where M (first main unit) falls
                        mains = [x["i"] for x in u if x["in_main"]]
                        row["first_main_unit"] = mains[0] if mains else None
                out.append(row)
                print(json.dumps(row), flush=True)
                await rp.context.close()
        await browser.close()


asyncio.run(main())
