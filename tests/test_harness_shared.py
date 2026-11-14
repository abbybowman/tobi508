"""The shared run (Q-07): one recording and one walk per fixture page, each
test's answers its own. Tests of the harness only; no rule is tested here."""

from __future__ import annotations

from tobi508.models import Answer, ChoiceAnswer, Outcome, TestId
from tobi508.pipeline import answer_questions

from . import harness
from .harness import run_shared

PAGE = "4a/f19-placeholder-link-twin.html"


def _answer(q) -> Answer:
    return Answer(
        question_id=q.question_id,
        choice=ChoiceAnswer(choice="no_alternative", reasons="scripted test answer"),
        rationale="scripted test answer",
        seen="scripted: the picture was not opened",
    )


async def test_a_second_run_of_a_page_is_a_copy_and_answers_stay_apart(
    settings, server
):
    url = f"{server.base}/{PAGE}"
    hits = harness.STATS["hits"]
    a = await run_shared(settings, url, [TestId.T4A])
    b = await run_shared(settings, url, [TestId.T4A])
    assert harness.STATS["hits"] == hits + 1  # the second did not record the page
    assert a.run_id != b.run_id and a.report.run_id == a.run_id
    assert b.report.run_id == b.run_id and b.report_uri.startswith(f"run://{b.run_id}")
    assert (settings.runs_dir / b.run_id / "walk.json").exists() or (
        settings.runs_dir / b.run_id / "evidence" / "walk.json"
    ).exists()
    qs = [q for q in a.report.open_questions if q.test_id is TestId.T4A]
    assert qs, "the page asks a question"
    res = await answer_questions(settings, a.run_id, [_answer(q) for q in qs])
    assert res.errors == [] and res.rejected == []
    [fa] = [f for f in res.report.findings if f.test_id is TestId.T4A]
    assert fa.outcome is not Outcome.NEEDS_REVIEW
    # The other copy, and a third, still have the question and no answer.
    c = await run_shared(settings, url, [TestId.T4A])
    for run in (b, c):
        assert [q for q in run.report.open_questions if q.test_id is TestId.T4A]
        [f] = [f for f in run.report.findings if f.test_id is TestId.T4A]
        assert f.outcome is Outcome.NEEDS_REVIEW


async def test_a_page_the_server_builds_each_time_is_not_shared(settings, server):
    before = dict(harness.STATS)
    for _ in range(2):
        await run_shared(settings, f"{server.base}/dyn", [TestId.T4C])
    assert harness.STATS == before
