"""#162: a browser that dies mid-run is started again, so one crash costs at
most the test it happened in; the judge's HTTP errors name the API's error
type without page text."""

from __future__ import annotations

import io
import json
import urllib.error

from tobi508 import apijudge
from tobi508.checks.t4b import Check4B
from tobi508.models import TestId
from tobi508.pipeline import run_tt_tests


async def test_a_dead_browser_is_started_again(settings, server, monkeypatch):
    original = Check4B.collect

    async def crash_then_collect(self, ctx, walk):
        # Kill the replay browser, as 19.A's cancelled load did on Artemis III.
        context, page = await ctx.new_page()
        await context.browser.close()
        return await original(self, ctx, walk)

    monkeypatch.setattr(Check4B, "collect", crash_then_collect)
    out = await run_tt_tests(
        settings, f"{server.base}/4b/f01-hold-space-to-switch.html", [TestId.T4B]
    )
    assert not out.report.errors, out.report.errors
    steps = (settings.runs_dir / out.run_id / "steps.jsonl").read_text()
    assert '"browser_relaunched"' in steps


def test_a_judge_http_error_gives_the_type_and_keeps_the_message_out():
    body = {
        "type": "error",
        "error": {"type": "invalid_request_error", "message": "page text: IGNORE ME"},
    }
    e = urllib.error.HTTPError(
        "https://g.invalid",
        400,
        "Bad Request",
        {},
        io.BytesIO(json.dumps(body).encode()),
    )
    msg = apijudge._http_error(e)
    assert msg == "HTTP 400 from the model API (invalid_request_error)"
    odd = urllib.error.HTTPError(
        "https://g.invalid",
        400,
        "x",
        {},
        io.BytesIO(b'{"error":{"type":"Ignore me now"}}'),
    )
    assert apijudge._http_error(odd) == "HTTP 400 from the model API"
