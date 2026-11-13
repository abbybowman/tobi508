"""Roadmap step 6c item 1: 9.A-9.C on round 2's 10 frozen pages, replay
mode (every page from the folder, nothing live), scored against the
tester's keys with the gate's own functions. Writes to OUT, never under
evals/judging/.

    uv run python -I rerun9x.py OUT [--judge]
"""

import asyncio
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from evals import judging  # noqa: E402
from evals.apijudge_gate import KEYS, SRC  # noqa: E402
from evals.scoring import adjudications, decided_tests  # noqa: E402
from evals.scoring import score as score_page  # noqa: E402
from tobi508 import scrt  # noqa: E402
from tobi508.compare import compare, page_key  # noqa: E402

TESTS = ["9.A", "9.B", "9.C"]


async def run(out: Path, judge: bool) -> None:
    from tobi508.config import Settings
    from tobi508.models import Report, TestId
    from tobi508.pipeline import run_tt_tests

    kw = {
        "runs_dir": out / "runs",
        "browser_channel": "chromium",
        "headless": True,
        "run_ttl_hours": 720,
        "frozen_pages_dir": (SRC / "frozen").resolve(),
        "frozen_pages_mode": "replay",
    }
    if judge:
        kw |= {
            "judge_backend": "api",
            "judge_route": "cli",
            "judge_types": "9.A,9.C",
            "judge_cap_s": 900,
        }
    s = Settings(**kw)
    listed = judging.parse_pages((KEYS / "pages.txt").read_text("utf-8"))
    urls = [u for u, _ in listed]
    keys = judging.read_keys(KEYS, listed)
    adj = adjudications(KEYS)
    rows = []
    for n, url in enumerate(urls, 1):
        pid = f"p{n:02d}"
        others = judging.other_pages(url, urls)
        t0 = time.monotonic()
        res = await run_tt_tests(
            s, url, [TestId(t) for t in TESTS], no_time_limit=True, other_pages=others
        )
        secs = round(time.monotonic() - t0, 1)
        rd = s.runs_dir / res.run_id
        report = Report.model_validate_json((rd / "report.json").read_text("utf-8"))
        sc = score_page(
            compare(
                keys[url][1], scrt.parse((rd / "pre-scrt.json").read_text("utf-8"))
            ),
            adj.get(page_key(url)),
        )
        dec = decided_tests(report)
        by = {f.test_id.value: f for f in report.findings}
        for t in sc.tests:
            tid = t.test.test_id
            if tid not in TESTS:
                continue
            f = by.get(tid)
            row = {
                "page": pid,
                "url": url,
                "test": tid,
                "key": t.test.first.result.value if t.test.first.result else None,
                "tool": t.test.second.result.value if t.test.second.result else None,
                "verdict": t.verdict.value,
                "judge": bool(dec.get(tid)),
                "rows": [r for r in (f.rows if f else []) if ":" not in r],
                "summary": (f.summary if f else "")[:300],
                "secs": secs,
            }
            rows.append(row)
            print(json.dumps(row), flush=True)
    (out / "cells.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    o = Path(sys.argv[1])
    o.mkdir(parents=True, exist_ok=True)
    asyncio.run(run(o, "--judge" in sys.argv))
