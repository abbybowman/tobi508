"""Judge backends."""

from __future__ import annotations

import pytest

from tobi508.judgment import ApiJudge, ClientJudge, get_judge
from tobi508.models import OpenQuestion, TestId

Q = OpenQuestion(
    question_id="q1",
    test_id=TestId.T4C,
    kind="J1",
    instance="i1",
    question="?",
    rubric="r",
    input={"text": []},
)


async def test_client_judge_defers_every_question():
    result = await ClientJudge().judge([Q])
    assert result.answers == [] and result.pending == [Q]


async def test_api_judge_defers_to_the_loop_that_runs_after_the_report_is_saved():
    # The server's answers come from apijudge.judge_run (tests/test_apijudge.py),
    # which needs the saved run; the Judge interface only defers.
    result = await ApiJudge().judge([Q])
    assert result.answers == [] and result.pending == [Q]


def test_get_judge():
    assert isinstance(get_judge("client"), ClientJudge)
    assert isinstance(get_judge("api"), ApiJudge)
    with pytest.raises(ValueError):
        get_judge("other")
