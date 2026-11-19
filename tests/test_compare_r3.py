"""The 2026-11-19 comparison (evals/judging/compare-2026-11-19-r3/compare.py):
its pieces, and that the committed compare.json is what the script computes
from the committed results (no network, no browser)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

DIR = (
    Path(__file__).resolve().parents[1] / "evals" / "judging" / "compare-2026-11-19-r3"
)


@pytest.fixture(scope="module")
def cmp():
    if not (DIR / "compare.py").is_file():
        pytest.skip("compare folder not in this checkout")
    spec = importlib.util.spec_from_file_location("compare_r3", DIR / "compare.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RESULT = '{"https://a.example/": {"1.3.1": {"result": "PASS", "elements": []}}'


def test_repair_adds_the_missing_outer_brace_only(cmp):
    text, fixed = cmp.repair_final("done\nRESULT: " + RESULT + "\n")
    assert fixed and text.splitlines()[-1] == "RESULT: " + RESULT + "}"
    good = "RESULT: " + RESULT + "}\n"
    text, fixed = cmp.repair_final(good)
    assert not fixed and text == good


def test_every_answer_in_arm_a_is_the_calling_agents(cmp):
    """The brief's check: arm A never got the server judge."""
    seen = set()
    for n in cmp.RUNS:
        for d in cmp.a_run_dirs("a", n):
            rep = json.loads((d / "report.json").read_text("utf-8"))
            seen |= {a["answer"]["answered_by"] for a in rep["answers"]}
            assert rep["judge_backend"] == "client"
    assert seen == {"client"}


def test_debrief_quotes_are_verbatim(cmp):
    assert sum(len(v) for v in cmp.quotes().values()) == 9


def test_compare_json_is_what_the_script_computes(cmp):
    got = json.loads(json.dumps(cmp.build(), default=str))
    assert got == json.loads((DIR / "compare.json").read_text("utf-8"))
