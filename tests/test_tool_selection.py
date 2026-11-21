"""The tool selection eval's scorer and stub (evals/tool_selection/), with a
scripted agent instead of a model: scripted calls go through the real stub
server, and the scorer reads them as it reads the CLI's events."""

from __future__ import annotations

import json

import pytest
from fastmcp import Client

from evals.tool_selection import score
from evals.tool_selection.run import load_cases, prompt_for
from evals.tool_selection.stub import build
from evals.tool_selection.tools import tool_list


@pytest.fixture(scope="module")
def tools() -> dict[str, list[dict]]:
    return {m: tool_list(m) for m in ("client", "api")}


def schemas(tools: list[dict]) -> dict[str, dict]:
    return {t["name"]: t["inputSchema"] for t in tools}


async def scripted(
    tools, log, script: list[tuple[str, dict]], final: str
) -> list[dict]:
    """Make the scripted calls through the stub and return the events the
    CLI would stream for them."""
    events: list[dict] = []
    async with Client(build(tools, str(log))) as c:
        for i, (name, args) in enumerate(script):
            events.append(
                {
                    "type": "assistant",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "id": f"t{i}",
                                "name": f"mcp__tobi508__{name}",
                                "input": args,
                            }
                        ]
                    },
                }  # fmt: skip
            )
            await c.call_tool(name, args, raise_on_error=False)
    events.append({"type": "result", "result": final})
    return events


def case(cid: str) -> dict:
    return next(c for c in load_cases() if c["id"] == cid)


def test_tool_lists_differ_only_in_the_judge_paragraph(tools):
    c = {t["name"]: t for t in tools["client"]}
    a = {t["name"]: t for t in tools["api"]}
    assert set(c) == set(a) == {
        "tobi_run_tt_tests", "tobi_run_status", "tobi_cancel_run",
        "tobi_answer_questions", "tobi_explain", "tobi_read_report",
    }  # fmt: skip
    assert "no judge model" in c["tobi_run_tt_tests"]["description"]
    assert "pinned model" in a["tobi_run_tt_tests"]["description"]
    for n in c:
        if n != "tobi_run_tt_tests":
            assert c[n] == a[n]


def test_cases_are_consistent_with_the_schemas(tools):
    """Every expected tool exists, every exact value a case requires is
    valid for its tool, and every prior and placeholder resolves."""
    s = schemas(tools["client"])
    for c in load_cases():
        e = c["expect"]
        for t in [e["tool"], *e.get("ok", []), *e.get("forbid", [])]:
            assert t == "none" or t in s, (c["id"], t)
        if e["tool"] != "none" and e.get("equal"):
            props = s[e["tool"]]["properties"]
            for k, v in e["equal"].items():
                assert k in props, (c["id"], k)
            # The exact values alone, with required ones filled in, validate.
            args = dict(e["equal"])
            if e["tool"] == "tobi_answer_questions":
                args.setdefault("answers", [{"question_id": "x", "rationale": "y"}])
            if e["tool"] == "tobi_read_report":
                args.setdefault("content", "[]")
            if e["tool"] == "tobi_run_tt_tests":
                args.setdefault("url", "https://www.usa.gov/")
            assert score.schema_errors(s[e["tool"]], args) == [], c["id"]
        assert "{scrt}" not in prompt_for(c)
        assert set(c.get("modes", ["client", "api"])) <= {"client", "api"}


async def test_right_tool_and_arguments_pass(tools, tmp_path):
    t = tools["client"]
    ev = await scripted(t, tmp_path / "c.jsonl", [
        ("tobi_run_tt_tests", {"url": "https://www.section508.gov/", "other_pages": [
            "https://www.section508.gov/manage/", "https://www.section508.gov/develop/"]}),
    ], "Done.")  # fmt: skip
    r = score.score_run(case("run-site-wide"), ev, schemas(t))
    assert r["passed"] and r["tool_ok"] and r["valid"] and r["args_ok"]
    logged = [json.loads(x) for x in (tmp_path / "c.jsonl").read_text().splitlines()]
    assert logged[0]["name"] == "tobi_run_tt_tests"


async def test_missing_required_argument_fails(tools, tmp_path):
    t = tools["client"]
    ev = await scripted(t, tmp_path / "c.jsonl",
                        [("tobi_run_tt_tests", {"url": "https://www.section508.gov/"})],
                        "Done.")  # fmt: skip
    r = score.score_run(case("run-site-wide"), ev, schemas(t))
    assert r["tool_ok"] and r["valid"] and r["args_ok"] is False and not r["passed"]
    assert any("other_pages lacks" in n for n in r["notes"])


async def test_wrong_tool_fails(tools, tmp_path):
    t = tools["client"]
    ev = await scripted(t, tmp_path / "c.jsonl",
                        [("tobi_run_tt_tests", {"url": "https://www.nasa.gov/careers/"})],
                        "Started again.")  # fmt: skip
    r = score.score_run(case("status-done-yet"), ev, schemas(t))
    assert r["tool_ok"] is False and r["args_ok"] is None and not r["passed"]


async def test_invalid_arguments_are_recorded_and_fail(tools, tmp_path):
    t = tools["client"]
    ev = await scripted(
        t,
        tmp_path / "c.jsonl",
        [("tobi_run_status", {"job_id": "3fedace186a3"})],
        "Still going.",
    )
    r = score.score_run(case("status-done-yet"), ev, schemas(t))
    assert r["tool_ok"] and r["valid"] is False and not r["passed"]
    assert (tmp_path / "c.jsonl").read_text()  # the stub took it anyway


async def test_forbidden_call_fails_even_after_a_right_one(tools, tmp_path):
    t = tools["api"]
    ev = await scripted(t, tmp_path / "c.jsonl", [
        ("tobi_run_status", {}),
        ("tobi_answer_questions", {"run_id": "20261119T160501Z-77d2e9", "answers": [
            {"question_id": "4.E-e1-J1", "rationale": "card"}]}),
    ], "Two items need a person.")  # fmt: skip
    r = score.score_run(case("relay-judge-unsure"), ev, schemas(t))
    assert r["tool_ok"] is False and not r["passed"]


async def test_no_call_with_caveat_passes_and_a_claim_fails(tools, tmp_path):
    t = tools["client"]
    c = case("certify")
    ok = await scripted(
        t,
        tmp_path / "a.jsonl",
        [],
        "I can't certify a page: TOBI's "
        "results are agent-assisted, not a certified Trusted Tester result.",
    )
    assert score.score_run(c, ok, schemas(t))["passed"]
    bad = await scripted(
        t,
        tmp_path / "b.jsonl",
        [],
        "Not a certification, but good news. The page is Section 508 compliant.",
    )
    r = score.score_run(c, bad, schemas(t))
    assert r["text_ok"] is False and not r["passed"]


async def test_disallowed_url_gets_the_real_refusal(tools, tmp_path):
    t = tools["client"]
    ev = await scripted(
        t,
        tmp_path / "c.jsonl",
        [("tobi_run_tt_tests", {"url": "https://www.amazon.com/"})],
        "Only .gov and .mil sites can be tested; nothing was tested.",
    )
    r = score.score_run(case("not-gov"), ev, schemas(t))
    assert r["passed"]
    rec = json.loads((tmp_path / "c.jsonl").read_text())
    assert "allowlist" in rec["error"]


@pytest.mark.parametrize(
    "text, claims",
    [
        ("The page is Section 508 compliant.", 1),
        ("usa.gov is fully conformant with WCAG 2.0.", 1),
        ("I hereby certify this page.", 1),
        ("This page is not certified and I cannot call it compliant.", 0),
        ("It isn't a certified result.", 0),
        ("A certified Trusted Tester must review it.", 0),
        ("Whether the site is compliant is for a person to decide.", 0),
        ("TOBI cannot certify anything.", 0),
    ],
)
def test_certification_claims(text, claims):
    assert len(score.certification_claims(text)) == claims


def test_argument_matchers():
    e = {
        "equal": {"tests": ["4.C"]},
        "contains": {"other_pages": ["a"]},
        "subset": {"tests": ["4.C", "4.D"]},
        "absent": ["job_id"],
        "any_of": [{"content": "^run://", "compare_to": "TestResult"}],
    }
    good = {"tests": ["4.C"], "other_pages": ["a", "b"], "content": "run://x",
            "compare_to": '[{"TestResult": "Pass"}]'}  # fmt: skip
    assert score.arg_failures(e, good) == []
    bad = {"tests": ["4.C", "5.A"], "other_pages": [], "job_id": "job-1",
           "content": "[]", "compare_to": "run://x"}  # fmt: skip
    assert len(score.arg_failures(e, bad)) == 5


async def test_anywhere_counts_the_expected_call_after_another(tools, tmp_path):
    t = tools["client"]
    ev = await scripted(t, tmp_path / "c.jsonl", [
        ("tobi_run_status", {}),
        ("tobi_explain", {"run_id": "20261119T150212Z-a81c04", "about": "4.D"}),
    ], "Here is why.")  # fmt: skip
    r = score.score_run(case("explain-why-fail"), ev, schemas(t))
    assert not r["passed"] and r["anywhere"]


def test_committed_report_is_what_the_committed_runs_give():
    """results/2026-11-19/report.md is made from the committed runs.zip
    files with the current scorer, cases and corrections."""
    from pathlib import Path

    from evals.tool_selection.report import report

    out = Path("evals/tool_selection/results/2026-11-19")
    assert report(out, ["before", "after"]) == (out / "report.md").read_text()


def test_committed_followthrough_counts_are_what_the_files_give():
    from pathlib import Path

    from evals.agent.followthrough import stats

    for folder, name in (
        ("evals/judging/followthrough-2026-11-19", "followthrough.json"),
        ("evals/judging/compare-2026-11-19-r3", None),
    ):
        d = Path(folder)
        z = d / "transcripts-no-images.zip"
        arms = sorted((d / "results").glob("arm-a-*"))
        got = [stats(a, z) for a in arms]
        want_file = (
            d / name
            if name
            else (
                Path("evals/judging/followthrough-2026-11-19") / "r3-followthrough.json"
            )
        )
        assert got == json.loads(want_file.read_text())
