"""The progress lines a run sends while it checks its tests: each names the
test and its place among the run's tests, and the step moves through the
test stage (between 2 and 3 of 4), so a client's bar does not sit still."""

from __future__ import annotations

import re

from tobi508.models import TestId
from tobi508.pipeline import run_tt_tests


async def test_each_test_says_its_place_and_the_bar_moves(settings, server):
    lines: list[tuple[float, float | None, str]] = []

    async def progress(step, total, message):
        lines.append((step, total, message))

    out = await run_tt_tests(
        settings,
        f"{server.base}/4d/f01-background-change.html",
        [TestId.T4C, TestId.T4D],
        progress=progress,
    )
    assert out.errors == [], out.errors
    checking = [
        (step, m)
        for step, _, m in lines
        if re.fullmatch(r"Checking \S+ \(test \d+ of \d+\)", m)
    ]
    assert [m.split(" (")[1] for _, m in checking] == ["test 1 of 2)", "test 2 of 2)"]
    assert {m.split()[1] for _, m in checking} == {"4.C", "4.D"}
    steps = [step for step, _ in checking]
    assert steps == sorted(steps) and steps[0] == 2 and steps[-1] < 3
    assert all(total == 4 for _, total, _ in lines)
