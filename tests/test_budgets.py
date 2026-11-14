"""A time budget per test inside the run limit (roadmap step 6c, item 2;
checks/base.py TEST_BUDGET_S): a test still collecting when its budget ends
is NEEDS REVIEW, not performed, and the tests after it still run."""

from __future__ import annotations

import asyncio

from tobi508.checks import REGISTRY, base
from tobi508.models import Outcome, Report, TestId
from tobi508.pipeline import run_tt_tests


def _report(settings, res) -> Report:
    return Report.model_validate_json(
        (settings.runs_dir / res.run_id / "report.json").read_text()
    )


async def test_a_test_past_its_budget_is_review_and_the_next_still_runs(
    settings, server, monkeypatch
):
    async def slow(ctx, walk):
        await asyncio.sleep(30)

    monkeypatch.setitem(base.TEST_BUDGET_S, "4.B", 1)
    monkeypatch.setattr(REGISTRY[TestId.T4B], "collect", slow)
    res = await run_tt_tests(
        settings, f"{server.base}/no_trap.html", [TestId.T4B, TestId.T4D]
    )
    report = _report(settings, res)
    by = {f.test_id: f for f in report.findings}
    b = by[TestId.T4B]
    assert b.outcome is Outcome.NEEDS_REVIEW
    assert b.note == "This test could not be performed"
    assert "ran out of its time (1 s)" in b.summary, b.summary
    # The test after it ran: a decided outcome, not "did not complete".
    d = by[TestId.T4D]
    assert "did not complete" not in d.summary, d.summary
    assert report.versions.test_budgets_s["4.B"] == 1
    assert report.versions.test_budgets_s["5.D"] == base.budget_s("5.D")
    # Rerunning with no_time_limit would not lift a budget: no such call.
    assert not any("4.B" in c["tests"] for c in report.follow_up_calls)
    assert any("4.B: ran out of its time" in e for e in report.errors)


async def test_a_2x_test_past_its_budget_leaves_the_shared_pass_to_the_others(
    settings, server, monkeypatch
):
    """2.A waits on pass T, which the 2.x tests and 3.A share; its budget
    ending must not cancel that pass (motion.collect shields it)."""
    monkeypatch.setitem(base.TEST_BUDGET_S, "2.A", 1)
    res = await run_tt_tests(
        settings, f"{server.base}/no_trap.html", [TestId.T2A, TestId.T2B]
    )
    by = {f.test_id: f for f in _report(settings, res).findings}
    assert "ran out of its time (1 s)" in by[TestId.T2A].summary
    assert "did not complete" not in by[TestId.T2B].summary, by[TestId.T2B].summary
    assert "ran out of its time" not in by[TestId.T2B].summary


def test_every_registered_test_has_a_budget():
    assert {t.value for t in REGISTRY} <= set(base.TEST_BUDGET_S)
    assert all(v >= 60 for v in base.TEST_BUDGET_S.values())
