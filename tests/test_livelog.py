"""The live log (livelog.py, /live): off by default, opens only with its
token, and records requests, responses, pictures and run steps."""

from __future__ import annotations

import base64
import json

import pytest
from fastmcp import Client
from pydantic import SecretStr
from starlette.testclient import TestClient

from tobi508 import livelog
from tobi508.app import mcp
from tobi508.runlog import RunRecorder

TOKEN = "demo-token-123"


@pytest.fixture
def live(monkeypatch):
    monkeypatch.setattr(livelog.settings, "live_log", True)
    monkeypatch.setattr(livelog.settings, "live_log_token", SecretStr(TOKEN))
    livelog.clear()
    yield
    livelog.clear()


@pytest.fixture
def http():
    return TestClient(mcp.http_app(transport="streamable-http"))


async def _explain():
    async with Client(mcp) as c:
        await c.call_tool("tobi_explain", {"about": "4.C"})


async def test_off_by_default_records_nothing_and_hides_the_page(http):
    assert livelog.settings.live_log is False
    livelog.clear()
    await _explain()
    assert livelog.events_after(0) == []
    for path in ("/live", "/live/app.js", "/live/app.css"):
        assert http.get(path).status_code == 404
    assert http.get("/live/events", headers={"X-Live-Token": TOKEN}).status_code == 404


async def test_on_without_a_token_stays_hidden(http, monkeypatch):
    monkeypatch.setattr(livelog.settings, "live_log", True)
    monkeypatch.setattr(livelog.settings, "live_log_token", None)
    assert http.get("/live").status_code == 404
    assert http.get("/live/events", headers={"X-Live-Token": ""}).status_code == 404


async def test_records_the_request_and_the_full_response(live):
    await _explain()
    events = livelog.events_after(0)
    call = next(e for e in events if e["kind"] == "call")
    result = next(e for e in events if e["kind"] == "result")
    assert call["name"] == "tobi_explain" and call["arguments"] == {"about": "4.C"}
    assert result["call"] == call["call"] and result["name"] == "tobi_explain"
    text = result["parts"][0]["text"]
    assert "2.1.2-no-keyboard-trap" in text  # the response itself, not a summary


def test_events_need_the_token(http, live):
    livelog.emit("progress", job="job-x", target="https://example.gov/", message="m")
    assert http.get("/live/events").status_code == 404
    wrong = http.get("/live/events", headers={"X-Live-Token": "wrong"})
    assert wrong.status_code == 404
    r = http.get("/live/events?after=0", headers={"X-Live-Token": TOKEN})
    assert r.status_code == 200 and r.headers["cache-control"] == "no-store"
    assert [e["message"] for e in r.json()["events"]] == ["m"]
    last = r.json()["events"][-1]["seq"]
    again = http.get(f"/live/events?after={last}", headers={"X-Live-Token": TOKEN})
    assert again.json()["events"] == []


def test_page_has_no_inline_script_and_a_strict_policy(http, live):
    r = http.get("/live")
    assert r.status_code == 200
    csp = r.headers["content-security-policy"]
    assert "default-src 'none'" in csp and "script-src 'self'" in csp
    assert "unsafe" not in csp
    assert "<script>" not in r.text and 'src="/live/app.js"' in r.text
    js = http.get("/live/app.js").text
    assert "innerHTML" not in js  # page text is only ever set as text
    assert http.get("/live/app.css").status_code == 200


def test_run_steps_are_mirrored(live, tmp_path):
    run = RunRecorder(tmp_path)
    run.log("walk", presses=12, target="https://www.nasa.gov/x?secret=1")
    [e] = [e for e in livelog.events_after(0) if e["kind"] == "step"]
    assert e["run_id"] == run.run_id and e["step"] == "walk"
    assert e["detail"]["target"] == "https://www.nasa.gov/x"  # redacted as on disk


def test_pictures_are_kept_small_ones_whole_large_ones_named():
    small = base64.b64encode(b"\x89PNG" + b"0" * 100).decode()
    large = base64.b64encode(b"0" * (livelog.MAX_IMAGE + 10)).decode()
    assert livelog._image("image/png", small)["data"] == small
    big = livelog._image("image/png", large)
    assert "data" not in big and big["bytes"] > livelog.MAX_IMAGE


def test_long_text_is_trimmed_and_says_so():
    out = livelog._trim("x" * (livelog.MAX_TEXT + 5))
    assert len(out["text"]) == livelog.MAX_TEXT and out["more_chars"] == 5
    json.dumps(out)  # events stay JSON
