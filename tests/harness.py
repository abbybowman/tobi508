"""Run one TT check on a page end to end, answering its open questions with
scripted answers that stand in for the calling agent. Answers are test data
(what a correct judge would say), never outcomes, and live in test files,
never in a page."""

from __future__ import annotations

import atexit
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from tobi508.models import (
    TEST_NOT_PERFORMED_NOTE,
    Answer,
    ChoiceAnswer,
    Outcome,
    TestId,
)
from tobi508.pipeline import answer_questions, run_tt_tests
from tobi508.runlog import new_run_id

from .conftest import FIXTURES, _fixture_file
from .harness_4c import assert_plain

# One recording and one walk per fixture page (review item Q-07). A test that
# only changes its answers to a page's open questions used to record and walk
# the page again; `run_shared` keeps the first run in a folder of its own and
# hands every later test a copy of that run's folder under a new run ID, so
# each test's answers stay its own. Per process: pytest-xdist workers do not
# share it, so the saving is the tests of one worker.
SHARED: dict[tuple, Any] = {}
STATS = {"hits": 0, "misses": 0}
_CACHE_DIR: list[Path] = []


def _write_stats() -> None:
    """One line per process in runs/shared-runs.txt (git-ignored): how often a
    page was recorded and walked, and how often a test reused it."""
    if any(STATS.values()):
        out = Path(__file__).parent.parent / "runs"
        out.mkdir(exist_ok=True)
        with (out / "shared-runs.txt").open("a") as f:
            f.write(f"misses {STATS['misses']} hits {STATS['hits']}\n")


atexit.register(_write_stats)


def _cache_dir() -> Path:
    if not _CACHE_DIR:
        d = Path(tempfile.mkdtemp(prefix="tobi-shared-runs-"))
        atexit.register(shutil.rmtree, d, ignore_errors=True)
        _CACHE_DIR.append(d)
    return _CACHE_DIR[0]


def _fixture_key(url: str) -> tuple[str, str] | None:
    """(the page's path, the SHA-256 of its file) for a page the fixture server
    serves from a file; None for any other address (a route that answers
    differently each time is never shared)."""
    f = _fixture_file(urlsplit(url).path)
    if f is None or not f.is_file() or FIXTURES not in f.parents:
        return None
    path = urlsplit(url)
    return (
        path.path + ("?" + path.query if path.query else ""),
        hashlib.sha256(f.read_bytes()).hexdigest(),
    )


async def run_shared(settings, url: str, tests, other_pages=None):
    """`run_tt_tests`, once per fixture page and set of tests; later calls get
    a copy of the run (own folder, own run ID). Same result type."""
    keys = [_fixture_key(u) for u in [url, *(other_pages or [])]]
    if any(k is None for k in keys):
        return await run_tt_tests(settings, url, tests, other_pages=other_pages)
    config = settings.model_dump_json(exclude={"runs_dir"})
    key = (tuple(keys), tuple(t.value for t in tests), config)
    if key not in SHARED:
        STATS["misses"] += 1
        own = settings.model_copy(update={"runs_dir": _cache_dir()})
        SHARED[key] = await run_tt_tests(own, url, tests, other_pages=other_pages)
    else:
        STATS["hits"] += 1
    first = SHARED[key]
    new_id = new_run_id()
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    dest = settings.runs_dir / new_id
    shutil.copytree(_cache_dir() / first.run_id, dest)
    for name in ("report.json",):  # the run's own ID is written in its report
        f = dest / name
        if f.exists():
            f.write_text(f.read_text("utf-8").replace(first.run_id, new_id), "utf-8")

    # The run's ID is in its question links and report URIs: rewrite it all.
    def renamed(model):
        return model.model_dump_json().replace(first.run_id, new_id)

    report = type(first.report).model_validate_json(renamed(first.report))
    data = json.loads(renamed(first))  # the report is not part of the result's JSON
    return type(first).model_validate({**data, "report": report})


def assert_note(f) -> None:
    # Principle 2 and _template.md G3: every NEEDS REVIEW says the test could
    # not be performed, and nothing else does. Every fixture checks it.
    assert (f.note == TEST_NOT_PERFORMED_NOTE) == (f.outcome is Outcome.NEEDS_REVIEW), (
        f.test_id.value,
        f.outcome.value,
        f.note,
        f.rows,
    )


async def run_check(
    settings,
    url: str,
    test: TestId,
    choice: str | dict[str, dict[str, Any]] | None = None,
    reasons: str = "scripted test answer",
) -> dict[str, Any]:
    """`choice` answers every "choice" question the run asks: one choice for
    all, or a dict from the question ID's last part ("J1", "J2") to
    ChoiceAnswer fields (choice, element, key, duration_ms, presses)."""
    out = await run_shared(settings, url, [test])
    assert out.errors == [], out.errors
    report = out.report
    for _ in range(3):
        open_qs = [q for q in report.open_questions if q.test_id is test]
        if not open_qs:
            break
        assert choice is not None, f"{url}: a question was asked: {open_qs[0].question}"

        def fields(q) -> dict[str, Any]:
            if isinstance(choice, dict):
                f = choice.get(q.question_id.rsplit("-", 1)[-1])
                assert f is not None, f"{url}: no scripted answer for {q.question_id}"
                return {"reasons": reasons, **f}
            return {"choice": choice, "reasons": reasons}

        answers = [
            Answer(
                question_id=q.question_id,
                choice=ChoiceAnswer(**fields(q)),
                rationale="scripted test answer",
                seen="scripted: the picture was not opened",
            )
            for q in open_qs
        ]
        res = await answer_questions(settings, out.run_id, answers)
        assert res.errors == [] and res.rejected == [], (res.errors, res.rejected)
        report = res.report
    [finding] = [f for f in report.findings if f.test_id is test]
    assert_plain(finding.summary)
    assert_note(finding)
    # "asked": the first report's questions, so a test can check a question's
    # input on the run it already made instead of running the page again.
    return {
        "finding": finding,
        "report": report,
        "run_id": out.run_id,
        "asked": out.report.open_questions,
    }


def instance_rows(finding) -> list[str]:
    return sorted(r.split(":")[1] for r in finding.rows if ":" in r)


async def run_tests(
    settings,
    url: str,
    tests,
    answers: dict[str, dict[str, dict[str, Any]]],
    other_pages: list[str] | None = None,
    asked: list | None = None,
) -> dict[str, Any]:
    """Several tests in one call (tests that share a collection pass, such as
    5.A and 5.C). `answers` maps a test ID to its scripted answers, keyed by
    the question ID's last part. Returns each test's finding."""
    out = await run_shared(
        settings, url, [TestId(t) for t in tests], other_pages=other_pages
    )
    assert out.errors == [], out.errors
    report = out.report
    if asked is not None:  # the first report's questions (see run_check)
        asked.extend(report.open_questions)
    for _ in range(3):
        qs = [q for q in report.open_questions if q.test_id.value in tests]
        if not qs:
            break
        sent = []
        for q in qs:
            f = (answers.get(q.test_id.value) or {}).get(
                q.question_id.rsplit("-", 1)[-1]
            )
            assert f is not None, f"{url}: no scripted answer for {q.question_id}"
            sent.append(
                Answer(
                    question_id=q.question_id,
                    choice=ChoiceAnswer(**{"reasons": "scripted test answer", **f}),
                    rationale="scripted test answer",
                    seen="scripted: the picture was not opened",
                )
            )
        res = await answer_questions(settings, out.run_id, sent)
        assert res.errors == [] and res.rejected == [], (res.errors, res.rejected)
        report = res.report
    got = {f.test_id.value: f for f in report.findings if f.test_id.value in tests}
    for f in got.values():
        assert_plain(f.summary)
        assert_note(f)
    return got
