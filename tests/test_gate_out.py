"""The gate's `--out` / `--from-repeat` options and the calling-agent arm's
explicit client judge (comparison runs, 2026-11-19). No browser, no model."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals import apijudge_gate as gate  # noqa: E402
from evals.agent.arms import tool_arm  # noqa: E402


def test_out_overrides_the_gate_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "OUT_DIR", tmp_path / "c")
    assert gate.gate_dir("x", 3) == tmp_path / "c"
    monkeypatch.setattr(gate, "OUT_DIR", None)
    assert gate.gate_dir("x", 3).name == "round3"


def test_timing_file_has_both_ends(tmp_path):
    from datetime import datetime, timezone

    gate._timing(tmp_path, datetime.now(timezone.utc))
    t = (tmp_path / "timing.json").read_text()
    assert "call_started" in t and "call_finished" in t


def test_the_calling_agent_arm_never_gets_the_server_judge(tmp_path, monkeypatch):
    # The default judge backend turns the server judge on whenever a gateway
    # is set; arm A must keep the questions for the agent.
    monkeypatch.setenv("JUDGE_BASE_URL", "http://x")
    (srv,) = tool_arm(tmp_path, "m", tmp_path / "runs")
    assert srv.env["JUDGE_BACKEND"] == "client"
    assert "JUDGE_BASE_URL" not in srv.env
