"""Cancelling a run: the caller's own with tobi_cancel_run, any run by the
server's admin from inside its container (admin.py); a queued run says what
it waits behind. A cancelled run keeps no folder and frees its browser slot.
Plumbing only: no outcome is decided here."""

from __future__ import annotations

import asyncio
import json
import stat

import pytest
from fastmcp import Client
from starlette.testclient import TestClient

from tobi508 import access, admin, config, jobs, pipeline
from tobi508.app import mcp
from tobi508.models import TestId


@pytest.fixture(autouse=True)
def _clean(settings, monkeypatch):
    monkeypatch.setattr(config, "settings", settings)
    jobs._JOBS.clear()
    yield
    for j in list(jobs._JOBS.values()):
        if j.task is not None and not j.task.done():
            j.task.cancel()
    jobs._JOBS.clear()


def _blocked(started: list[str], name: str, gate: asyncio.Event):
    async def run(progress):
        started.append(name)
        await gate.wait()
        return name

    return run


async def test_cancel_frees_the_slot_and_waiting_says_who(settings):
    s = settings.model_copy(update={"max_concurrent_runs": 1})
    gate, started = asyncio.Event(), []
    a = jobs.start(s, "https://a.gov/x", _blocked(started, "a", gate))
    b = jobs.start(s, "https://a.gov/x", _blocked(started, "b", gate))
    await asyncio.sleep(0.05)
    assert started == ["a"]

    queued = jobs.pending(b, 45)
    assert queued.status == "queued"
    assert queued.your_runs_ahead == [a.id] and queued.runs_ahead == 1
    assert "tobi_cancel_run" in queued.next_step
    assert "time limit has not started" in queued.progress

    assert await jobs.cancel(a, "the caller") == "running"
    assert a.task.cancelled()
    with pytest.raises(jobs.RunCancelled, match="cancelled by the caller"):
        await jobs.wait(a, 0.1)
    await asyncio.sleep(0.05)
    assert started == ["a", "b"]  # b got the slot
    gate.set()
    assert await b.task == "b"
    assert await jobs.cancel(b, "the caller") == "finished"


async def test_a_queued_run_can_be_cancelled(settings):
    s = settings.model_copy(update={"max_concurrent_runs": 1})
    gate, started = asyncio.Event(), []
    a = jobs.start(s, "a", _blocked(started, "a", gate))
    b = jobs.start(s, "b", _blocked(started, "b", gate))
    await asyncio.sleep(0.05)
    assert await jobs.cancel(b, "the caller") == "queued"
    gate.set()
    assert await a.task == "a"
    assert started == ["a"]  # b never started


async def test_queued_counts_other_callers_without_naming_them(settings, monkeypatch):
    who = {"sub": "alice"}
    monkeypatch.setattr(access, "caller", lambda: who["sub"])
    s = settings.model_copy(update={"max_concurrent_runs": 1})
    gate, started = asyncio.Event(), []
    jobs.start(s, "a", _blocked(started, "a", gate))
    who["sub"] = "bob"
    b = jobs.start(s, "b", _blocked(started, "b", gate))
    await asyncio.sleep(0.05)
    out = jobs.pending(b, 45)
    assert out.runs_ahead == 1 and out.your_runs_ahead == []
    assert "tobi_cancel_run" not in out.next_step
    gate.set()


async def test_running_line_says_its_percentage_is_one_part(settings):
    gate, started = asyncio.Event(), []
    a = jobs.start(settings, "a", _blocked(started, "a", gate))
    await asyncio.sleep(0.05)
    out = jobs.pending(a, 45)
    assert out.status == "running"
    assert "part 1 of 3" in out.progress
    assert "never the whole run" in out.next_step
    gate.set()


# ── The tool ─────────────────────────────────────────────────────────────────


async def _tool(args: dict) -> tuple[bool, str]:
    async with Client(mcp) as client:
        r = await client.call_tool("tobi_cancel_run", args, raise_on_error=False)
    return r.is_error, r.content[0].text


async def test_tool_cancels_only_the_callers_own_run(settings, monkeypatch):
    who = {"sub": "alice"}
    monkeypatch.setattr(access, "caller", lambda: who["sub"])
    gate, started = asyncio.Event(), []
    a = jobs.start(settings, "https://a.gov/", _blocked(started, "a", gate))
    await asyncio.sleep(0.05)

    who["sub"] = "bob"  # another person's run reads as unknown
    err, text = await _tool({"job_id": a.id})
    assert err and "None of your runs" in text
    assert not a.task.done()

    who["sub"] = "alice"
    err, text = await _tool({"job_id": a.id})
    out = json.loads(text)
    assert not err and out["status"] == "cancelled" and out["was"] == "running"
    assert a.task.cancelled()

    async with Client(mcp) as client:
        r = await client.call_tool(
            "tobi_run_status", {"job_id": a.id}, raise_on_error=False
        )
    assert r.is_error and "cancelled by the caller" in r.content[0].text


async def test_tool_is_marked_destructive():
    async with Client(mcp) as client:
        [tool] = [t for t in await client.list_tools() if t.name == "tobi_cancel_run"]
    assert tool.annotations.destructive_hint is True
    assert tool.annotations.read_only_hint is False
    assert "only when the user asks" in tool.description


# ── A real run ───────────────────────────────────────────────────────────────


async def _until(job: jobs.Job, prefix: str, seconds: float = 60) -> None:
    for _ in range(int(seconds * 20)):
        if job.message.startswith(prefix) or job.task.done():
            return
        await asyncio.sleep(0.05)
    raise AssertionError(f"never reached {prefix!r}: {job.message!r}")


async def test_a_run_cancelled_while_reading_keeps_no_folder(settings, server):
    url = f"{server.base}/no_trap.html"
    job = jobs.start(
        settings, url, lambda p: pipeline.run_tt_tests(settings, url, [TestId.T4C], p)
    )
    await _until(job, "Part 1 of 3")
    assert await jobs.cancel(job, "the caller") == "running"
    assert job.task.cancelled()
    assert not settings.runs_dir.exists() or list(settings.runs_dir.iterdir()) == []


async def test_a_run_cancelled_while_judging_keeps_no_folder(
    settings, server, monkeypatch
):
    class Stuck:
        async def judge(self, questions):
            await asyncio.Event().wait()

    monkeypatch.setattr(pipeline, "get_judge", lambda backend: Stuck())
    url = f"{server.base}/no_trap.html"
    job = jobs.start(
        settings, url, lambda p: pipeline.run_tt_tests(settings, url, [TestId.T4C], p)
    )
    await _until(job, "Part 3 of 3")
    assert await jobs.cancel(job, "the caller") == "running"
    assert job.task.cancelled()
    assert list(settings.runs_dir.iterdir()) == []


# ── The admin routes and command ─────────────────────────────────────────────


@pytest.fixture
def http(tmp_path, monkeypatch):
    path = tmp_path / "admin.token"
    token = admin.write_token(path)
    yield TestClient(mcp.http_app(transport="streamable-http")), token, path
    monkeypatch.setattr(admin, "_TOKEN", None)


def test_token_file_is_private_and_fresh(http, tmp_path):
    _, token, path = http
    assert path.read_text() == token
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert admin.write_token(path) != token  # each start, a new one


def test_admin_routes_need_the_token_and_no_proxy(http):
    client, token, _ = http
    assert client.get("/admin/jobs").status_code == 404
    assert client.get("/admin/jobs", headers={"X-Admin-Token": "x"}).status_code == 404
    through_gateway = {"X-Admin-Token": token, "X-Forwarded-For": "127.0.0.1"}
    assert client.get("/admin/jobs", headers=through_gateway).status_code == 404
    assert client.post("/admin/jobs/job-000000000000/cancel").status_code == 404
    r = client.get("/admin/jobs", headers={"X-Admin-Token": token})
    assert r.status_code == 200 and r.json() == {"jobs": []}
    assert r.headers["cache-control"] == "no-store"


def test_admin_lists_and_cancels_every_callers_run(http, settings, monkeypatch):
    client, token, _ = http
    monkeypatch.setattr(access, "caller", lambda: "alice")
    lines: list[str] = []
    monkeypatch.setattr(access.AUDIT, "info", lines.append)

    async def scenario():
        gate, started = asyncio.Event(), []
        return jobs.start(
            settings, "https://a.gov/p?secret=1", _blocked(started, "a", gate)
        )

    # The TestClient runs the app in its own event loop: start the job there.
    with client:
        job = client.portal.call(scenario)
        r = client.get("/admin/jobs", headers={"X-Admin-Token": token})
        [line] = r.json()["jobs"]
        assert line["job_id"] == job.id and line["started_by"] == "alice"
        assert line["target"] == "https://a.gov/p"  # no query string
        r = client.post(
            f"/admin/jobs/{job.id}/cancel", headers={"X-Admin-Token": token}
        )
        assert r.json()["was"] in ("queued", "running")
        assert job.cancelled_by == "the server's operator"
        r = client.get("/admin/jobs", headers={"X-Admin-Token": token})
        assert r.json()["jobs"][0]["status"] == "cancelled"
    [entry] = [json.loads(x) for x in lines if "admin.cancel" in x]
    assert entry["job_id"] == job.id and entry["url"] == "https://a.gov/p"


def test_admin_command_without_a_token_says_where_to_run_it(
    settings, monkeypatch, tmp_path, capsys
):
    monkeypatch.setattr(
        config,
        "settings",
        settings.model_copy(update={"admin_token_file": tmp_path / "none"}),
    )
    with pytest.raises(SystemExit, match="inside the server's container"):
        admin.main(["jobs"])


# ── Where the viewer is (next_steps.viewer_location) ─────────────────────────


def test_viewer_location_follows_how_the_server_runs(settings, monkeypatch):
    from tobi508.next_steps import viewer_location

    def at(**kw):
        monkeypatch.setattr(config, "settings", settings.model_copy(update=kw))
        return viewer_location()

    assert at(public_base_url="https://tobi.example.gov/") == (
        "https://tobi.example.gov/viewer"
    )
    assert at(mcp_transport="streamable-http", mcp_port=8000) == (
        "http://127.0.0.1:8000/viewer"
    )
    local = at(mcp_transport="stdio")
    assert local.startswith("file://") and local.endswith("viewer.html")
