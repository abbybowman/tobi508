"""A time budget per test inside the run limit (roadmap step 6c, item 2;
settings test_budgets_s, checks.base): a test still collecting when its
time ends is NEEDS REVIEW, not performed, and the tests after it still run.
A test gets its budget or half of what is left of the run, whichever is
smaller; tests run cheapest budget first, after the tests they read."""

from __future__ import annotations

import asyncio

import numpy as np

from tobi508 import flash
from tobi508.checks import REGISTRY
from tobi508.checks.base import AFTER, time_for
from tobi508.config import TEST_BUDGETS_DEFAULT
from tobi508.models import Outcome, Report, TestId
from tobi508.pipeline import run_order, run_tt_tests


def _report(settings, res) -> Report:
    return Report.model_validate_json(
        (settings.runs_dir / res.run_id / "report.json").read_text()
    )


def _with(settings, **budgets):
    return settings.model_copy(
        update={"test_budgets_s": {**settings.test_budgets_s, **budgets}}
    )


async def test_a_test_past_its_budget_is_review_and_the_next_still_runs(
    settings, server, monkeypatch
):
    async def slow(ctx, walk):
        await asyncio.sleep(30)

    s = _with(settings, **{"4.B": 1})
    monkeypatch.setattr(REGISTRY[TestId.T4B], "collect", slow)
    res = await run_tt_tests(s, f"{server.base}/no_trap.html", [TestId.T4B, TestId.T4D])
    report = _report(s, res)
    by = {f.test_id: f for f in report.findings}
    b = by[TestId.T4B]
    assert b.outcome is Outcome.NEEDS_REVIEW
    assert b.note == "This test could not be performed"
    assert "ran out of its time (1 s)" in b.summary, b.summary
    # The test after it ran: a decided outcome, not "did not complete".
    assert "did not complete" not in by[TestId.T4D].summary, by[TestId.T4D].summary
    t = report.test_times
    assert (t["4.B"].budget_s, t["4.B"].ran_out) == (1, True)
    assert t["4.B"].seconds < 5 and not t["4.D"].ran_out
    assert t["4.D"].budget_s == TEST_BUDGETS_DEFAULT["4.D"]
    assert report.versions.test_budgets_s["4.B"] == 1
    # Rerunning with no_time_limit would not lift a budget: no such call.
    assert not any("4.B" in c["tests"] for c in report.follow_up_calls)
    assert any("4.B: ran out of its time" in e for e in report.errors)
    # A budget is not the run's limit: no note that the run ran out of time.
    assert not any("run reached its time limit" in e for e in report.errors)


async def test_a_2x_test_past_its_budget_leaves_the_shared_pass_to_the_others(
    settings, server
):
    """2.A waits on pass T, which the 2.x tests and 3.A share; its budget
    ending must not cancel that pass (motion.collect shields it). A budget
    of 1 s ends while 2.A waits (0 would never start it)."""
    s = _with(settings, **{"2.A": 1})
    res = await run_tt_tests(s, f"{server.base}/no_trap.html", [TestId.T2A, TestId.T2B])
    by = {f.test_id: f for f in _report(s, res).findings}
    assert "ran out of its time (1 s)" in by[TestId.T2A].summary
    assert "did not complete" not in by[TestId.T2B].summary, by[TestId.T2B].summary
    assert "ran out of its time" not in by[TestId.T2B].summary


def test_a_test_gets_its_budget_or_half_of_what_is_left(settings):
    assert time_for(settings, "5.D", 3000) == 600
    assert time_for(settings, "5.D", 600) == 300  # RUN_LIMIT_S 600: half
    assert time_for(settings, "4.B", 1000) == 60
    assert time_for(settings, "4.B", 50) == 25
    assert time_for(settings, "4.B", -5) == 0


def test_run_order_is_cheapest_first_after_what_a_test_reads(settings):
    order = [c.test_id.value for c in run_order(list(REGISTRY.values()), settings)]
    pos = {t: i for i, t in enumerate(order)}
    for t, before in AFTER.items():
        for b in before:
            assert pos[b] < pos[t], (b, t, order)
    # Cheapest first wherever no AFTER entry holds a test back.
    free = [t for t in order if t not in AFTER]
    budgets = [settings.test_budgets_s[t] for t in free]
    assert budgets == sorted(budgets), list(zip(free, budgets))
    # Every registered test has a budget of at least 60 s by default.
    assert {t.value for t in REGISTRY} <= set(TEST_BUDGETS_DEFAULT)
    assert all(v >= 60 for v in TEST_BUDGETS_DEFAULT.values())


def test_the_linear_table_is_the_formula():
    """W-01: the lookup gives the same values as the power per pixel."""
    rgb = np.arange(256, dtype=np.uint8).reshape(16, 16, 1).repeat(3, axis=2)
    assert np.array_equal(flash.linear(rgb), flash._linear(rgb))


async def test_3a_stepped_capture_stops_at_its_budget(settings, server, monkeypatch):
    """The capture checks the time at every step (3.A 1.2.1): a budget that
    ends mid-capture leaves a cut capture (A3, NEEDS REVIEW), not a test that
    runs on. Each step is slowed to at least 0.15 s (181 steps: 27 s or
    more) through the capture's own time check, so a 20 s budget cuts it."""
    import json
    import time as clock

    from tobi508 import flashcap
    from tobi508.checks import t3a

    orig = t3a.triggers

    def forced(mp):
        tr, un = orig(mp)
        tr.append(t3a.Trigger(kind="timer", detail="forced for the test"))
        return tr, un

    real = flashcap.stepped

    async def slowed(page, images, lead, out_of_time):
        def check():
            clock.sleep(0.15)
            return out_of_time()

        return await real(page, images, lead, check)

    monkeypatch.setattr(t3a, "triggers", forced)
    monkeypatch.setattr(flashcap, "stepped", slowed)
    s = _with(settings, **{"3.A": 20})
    res = await run_tt_tests(s, f"{server.base}/no_trap.html", [TestId.T3A])
    report = _report(s, res)
    f = report.findings[0]
    ev = json.loads((s.runs_dir / res.run_id / "evidence" / "3a.json").read_text())
    assert ev["stepped"]["cut"] is True, ev["stepped"]
    assert ev["stepped"]["frames"] < 181
    assert f.outcome is Outcome.NEEDS_REVIEW, (f.rows, f.summary)
    assert report.test_times["3.A"].ran_out
    assert report.test_times["3.A"].seconds < 25, report.test_times


async def test_a_budget_does_not_wait_for_a_slow_cleanup(settings, server, monkeypatch):
    """The 3.A case (14194: 1,178 s against 240 s): a test whose cleanup
    waits after it is cancelled (closing a page still running script) must
    not hold the run. wait_for would wait the 30 s; the run moves on at the
    budget, and the log says where the test was waiting."""
    import json
    import time as clock

    async def stuck_page(ctx, walk):
        try:
            await asyncio.sleep(60)
        finally:
            await asyncio.sleep(30)  # like context.close() on a busy page

    s = _with(settings, **{"4.B": 1})
    monkeypatch.setattr(REGISTRY[TestId.T4B], "collect", stuck_page)
    t0 = clock.monotonic()
    res = await run_tt_tests(s, f"{server.base}/no_trap.html", [TestId.T4B, TestId.T4D])
    assert clock.monotonic() - t0 < 25
    report = _report(s, res)
    assert report.test_times["4.B"].ran_out
    assert report.test_times["4.B"].seconds < 5, report.test_times["4.B"]
    steps = [
        json.loads(x)
        for x in (s.runs_dir / res.run_id / "steps.jsonl").read_text().splitlines()
    ]
    gone = [e for e in steps if e["step"] == "check_abandoned"]
    assert gone and "stuck_page" in gone[0]["detail"]["where"], gone
