"""The progress lines a run sends: how many of its reading steps are done or
not needed, then how many of its tests are done, each with a rough
percentage that never goes back; the bar's step moves through its stages
(reading 0-2, tests 2-3, finishing 3-4 of 4), so a client's bar does not sit
still (progress.py)."""

from __future__ import annotations

import re

from tobi508.models import TestId
from tobi508.pipeline import run_tt_tests
from tobi508.progress import Tracker

TESTING = re.compile(
    r"Page read \(100%\)\. Testing, (\d+) of (\d+) tests done \((\d+)%\): "
    r"checking (\S+)"
)
READING = re.compile(
    r"Reading the page, (\d+) of (\d+) steps done or not needed \((\d+)%\): .+"
)


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
    reading = [READING.fullmatch(m) for _, _, m in lines if m.startswith("Reading")]
    assert reading and all(reading), [m for _, _, m in lines]
    done = [int(m[1]) for m in reading]
    assert done == sorted(done) and done[0] == 0
    testing = [(s, TESTING.fullmatch(m)) for s, _, m in lines if "Testing" in m]
    assert all(m for _, m in testing), [m for _, _, m in lines]
    assert [(m[1], m[2], m[3]) for _, m in testing] == [
        ("0", "2", "0"),
        ("1", "2", "50"),
    ]
    assert {m[4] for _, m in testing} == {"4.C", "4.D"}
    steps = [s for s, _ in testing]
    assert steps == sorted(steps) and steps[0] == 2 and steps[-1] < 3
    assert lines[-1][2].startswith(
        "Page read and all 2 tests checked (100%). Finishing:"
    )
    bar = [s for s, _, _ in lines]
    assert bar == sorted(bar)
    assert all(total == 4 for _, total, _ in lines)


async def test_steps_not_needed_count_as_done_and_never_go_back():
    lines: list[tuple[float, str]] = []

    async def progress(step, total, message):
        lines.append((step, message))

    t = Tracker(progress, ["record", "other1", "other2", "walk", "inventory"])
    await t.reading("Recording the page")
    t.close("record")
    await t.reading("Recording other page 1 of 2")
    t.close("other1", "other2")  # page 2 cut short: not needed any more
    t.close("nonsense")  # a step not in the plan changes nothing
    await t.reading("Walking the page with Tab and Shift+Tab")
    t.close("walk")  # the inventory came with the walk: never announced
    t.tests_total = 3
    await t.testing(0, 3, "Checking 1.A")
    await t.testing(2, 3, "Checking 4.C")
    await t.finishing(3, "Evaluating")
    assert [m for _, m in lines] == [
        "Reading the page, 0 of 5 steps done or not needed (0%): recording the page",
        "Reading the page, 1 of 5 steps done or not needed (20%): "
        "recording other page 1 of 2",
        "Reading the page, 3 of 5 steps done or not needed (60%): "
        "walking the page with Tab and Shift+Tab",
        "Page read (100%). Testing, 0 of 3 tests done (0%): checking 1.A",
        "Page read (100%). Testing, 2 of 3 tests done (66%): checking 4.C",
        "Page read and all 3 tests checked (100%). Finishing: evaluating",
    ]
    steps = [s for s, _ in lines]
    assert steps == sorted(steps) and steps[0] == 0 and steps[-1] == 3


async def test_without_a_listener_nothing_is_sent():
    t = Tracker(None, ["record"])
    await t.reading("Recording the page")
    await t.testing(0, 1, "Checking 1.A")
    await t.finishing(3.5, "Judging: 1 of 2 questions")
