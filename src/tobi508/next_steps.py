"""What the calling agent should do next, and the work left in a session.

Agents in the development runs left questions unanswered and follow-up calls
unmade. Every result therefore ends with plain instructions (next_step) and a
short to-do list (todo), and lists the tool calls that would let a test left
for review decide (follow_ups). Some of those calls the server may make
itself (server_may_make); tobi_run_status with finish=true takes them from
finished runs (take_follow_ups), records each one it starts
(record_follow_up), and, with no job_id, lists what is left across the
session's runs (outstanding). Wording and bookkeeping only: no outcome is
decided here.
"""

from __future__ import annotations

from typing import Any

from tobi508 import config
from tobi508.checks import REGISTRY
from tobi508.config import Settings
from tobi508.judgment import has_image
from tobi508.models import (
    Outcome,
    Outstanding,
    OutstandingRun,
    Report,
    TestId,
    unsure_by_server,
)
from tobi508.resources.runs import run_uri
from tobi508.runlog import RunRecorder


def viewer_location() -> str:
    """Where the user opens the pre-SCRT viewer: this server's /viewer when it
    runs over HTTP, else the file beside the server (a local server)."""
    s = config.settings
    if s.public_base_url:
        return s.public_base_url.rstrip("/") + "/viewer"
    if s.mcp_transport == "streamable-http":
        host = "[::1]" if s.mcp_host == "::1" else s.mcp_host
        return f"http://{host}:{s.mcp_port}/viewer"
    from tobi508.routes import VIEWER

    return VIEWER.as_uri()


def viewer_text() -> str:
    """How to show a saved pre-SCRT file to a person (demo run, 2026-11-20:
    agents wrote their own Markdown comparisons instead)."""
    return (
        f"The viewer ({viewer_location()}) shows a saved pre-SCRT file as a "
        "table in the user's own browser and sends nothing anywhere: they "
        "choose the file as the report file and, to compare, a person's SCRT "
        'file under "Compare with". A web page cannot open the user\'s files by '
        "itself, so tell them which saved files to choose."
    )


# Open questions shown per result (agent follow-through plan, change 2b:
# development run 7's agent skipped the pictures of results 25-70k
# characters long). The rest come with each tobi_answer_questions result.
QUESTION_PAGE = 10


def follow_ups(
    report: Report, states: dict[TestId, Any], skipped: dict[TestId, str] | None
) -> list[dict]:
    """Tool calls that would let a NEEDS_REVIEW test decide: a check's own
    `follow_up`, if it has one, and a test left out over a cap
    (5.D, with no_time_limit). For next_step; never made by the server."""
    review = {f.test_id for f in report.findings if f.outcome is Outcome.NEEDS_REVIEW}
    out: list[dict] = []
    for t in [t for t in TestId if t in review]:
        fn = getattr(REGISTRY.get(t), "follow_up", None)
        call = fn(states[t], report) if fn and t in states else None
        if call:
            out.append(call)
    for t in skipped or {}:
        out.append({"url": report.target, "tests": [t.value], "no_time_limit": True})
    return out


def _calls_text(calls: list[dict] | None) -> str:
    if not calls:
        return ""
    n = len(calls)
    user = sum(1 for c in calls if not server_may_make(c))
    ask = (
        f" {user} of them need the user's choice (no_time_limit): ask the "
        "user, then make those yourself as given."
        if user
        else ""
    )
    return (
        f" Then call tobi_run_status with finish=true: the server makes the "
        f"follow-up call{'s' if n != 1 else ''} in follow_up_calls that it may "
        "make itself, which let tests left for review decide, and waits for "
        f"them (the development runs' agents made almost none).{ask} Replace "
        "those tests' results in the saved report with the new ones."
    )


FINISH = (
    ' `work` stays "incomplete" while anything is left (`remaining`); '
    "your work is finished only when tobi_run_status with no job_id lists "
    "nothing left (the fourth development run's agent ended with questions "
    "and follow-up calls open). In a FAIL finding, `confirmed` (true) means "
    "the rules decided it and `unconfirmed` counts instances still waiting for "
    "answers: report them apart. Each finding is one line here: tobi_explain "
    "with the run_id gives the full summaries, reasons and fixes."
)


def next_step(
    report: Report, calls: list[dict] | None = None, shown: int = QUESTION_PAGE
) -> str:
    """What the calling agent does next, in one place in every result
    (post-round 1 fixes 4, 12 and 19: agents left every question unanswered,
    decided NEEDS_REVIEW findings themselves, and opened few images)."""
    qs = report.open_questions
    review = (
        "a NEEDS_REVIEW finding is reported as needs review (a person checks "
        "it), never as a pass or a fail"
    )
    if not qs:
        waiting = len(unsure_by_server(report))
        person = (
            f" {waiting} question(s) the server's judge was unsure about wait "
            "for a person, not for you: say so, and do not answer them."
            if waiting
            else ""
        )
        return (
            f"No open questions. Relay each finding's summary; {review}.{person}"
            + _calls_text(calls)
            + " Then save both files, pre_scrt_uri and report_uri (save_hint)."
            + FINISH
        )
    asked = {q.test_id for q in qs}
    tests = [t.value for t in TestId if t in asked]
    looks = (
        " Some questions ask what an image shows: open each run:// image they "
        "name with your MCP client's resource reader (read resource; a file "
        "reader cannot open run:// links; the pictures are also attached to "
        "this result) and look before answering. Their answers need `seen`: "
        "something the picture shows; or, if a picture cannot be opened or "
        "shows nothing, `picture_error` saying what happened, with unsure. "
        "An answer with neither is refused."
        if any(has_image(q.input) for q in qs)
        else ""
    )
    return (
        f"Not finished: {', '.join(tests)} stay NEEDS_REVIEW until you answer "
        f"the {len(qs)} open question(s)"
        + (
            f" ({shown} are in open_questions now; each answer result "
            "brings the next ones)"
            if len(qs) > shown
            else " in open_questions"
        )
        + ". Answer them now, "
        "yourself, in one tobi_answer_questions call per batch, each by its rubric; "
        "answer unsure only when the evidence does not settle it (only those go "
        f"to a person).{looks} Until then, {review}." + _calls_text(calls) + FINISH
    )


def todo(
    report: Report, calls: list[dict] | None = None, shown: int = QUESTION_PAGE
) -> list[str]:
    """A short to-do list put last in every result (agent follow-through plan,
    change 2b: development run 7's agent said the instructions were "buried
    in 25-70k-character outputs" and asked for a short list at the end)."""
    out: list[str] = []
    qs = report.open_questions
    if qs:
        shown_qs = qs[:shown]
        pics = sum(1 for q in shown_qs if has_image(q.input))
        pic = (
            f"; {pics} name a picture: look and give `seen`, or "
            "`picture_error` with unsure"
            if pics
            else ""
        )
        more = (
            f" {len(qs) - len(shown_qs)} more come with the answer result: "
            "answer those too, the same way, until none are left."
            if len(qs) > len(shown_qs)
            else ""
        )
        out.append(
            f"[ ] Answer the {len(shown_qs)} open question(s) in open_questions in "
            f"one tobi_answer_questions call (run_id {report.run_id}){pic}.{more}"
        )
    calls = calls or []
    mine = [c for c in calls if server_may_make(c)]
    user = [c for c in calls if not server_may_make(c)]
    if mine:
        out.append(
            f"[ ] Call tobi_run_status with finish=true: the server makes {len(mine)} "
            "follow-up call(s) itself and waits for them."
        )
    if user:
        out.append(
            f"[ ] Ask the user about {len(user)} call(s) that need no_time_limit "
            "(in follow_up_calls; they can take many minutes), then make them."
        )
    waiting = len(unsure_by_server(report))
    if waiting:
        out.append(
            f"[ ] {waiting} question(s) wait for a person (the server's judge "
            "was unsure): do not answer them; say they need a person."
        )
    out.append(
        "[ ] Before reporting: call tobi_run_status with no job_id, and repeat "
        "until it lists nothing left (it covers every run of this session)."
    )
    out.append(
        f"[ ] Before writing your report: call tobi_explain with run_id "
        f"{report.run_id} for the tests you report on (every FAIL at least): "
        "results give one line per finding; it gives the places on the page, "
        "the reasons and how to fix them."
    )
    out.append(
        "[ ] Save both files before expires_at, exactly as read: pre_scrt_uri "
        "(the file the user opens in the viewer) and report_uri (the full "
        'record). "Save the report" means both (save_hint).'
    )
    out.append(
        "[ ] Afterwards: to show the results, point the user to the viewer "
        f"({viewer_location()}) with the saved pre-SCRT file, rather than "
        "writing your own summary or comparison file. If they have a person's "
        "SCRT file for this page and ask how the results compare or where "
        "they differ, call tobi_read_report with content=pre_scrt_uri and "
        "compare_to=their file, sent unchanged. Write files only when asked."
    )
    out.append(
        "[ ] Report NEEDS_REVIEW findings as needs review, and say which "
        "findings still wait on work (waiting_on)."
    )
    return out


def server_may_make(call: dict) -> bool:
    """A follow-up call the server makes by itself (agent follow-through plan,
    change 1): any call but one that needs no_time_limit, which stays the
    user's choice (CLAUDE.md). (19.A's suggested pages were made this way
    until 1.11.0; 19.A now checks them itself.)"""
    return not call.get("no_time_limit")


def take_follow_ups(settings: Settings, jobs: list) -> list[tuple[str, dict]]:
    """The follow-up calls the server may make, removed from each finished
    run's report (so they are made once) and recorded there as made.
    Returns (run_id, call) pairs; the caller starts them and records each
    job id with `record_follow_up`."""
    out: list[tuple[str, dict]] = []
    for j in jobs:
        if j.task is None or not j.task.done() or j.task.cancelled():
            continue
        if j.task.exception() is not None:
            continue
        res = j.task.result()
        try:
            run = RunRecorder.open(settings.runs_dir, res.run_id)
            report = Report.model_validate_json(run.report_path.read_text("utf-8"))
        except Exception:
            continue
        mine = [c for c in report.follow_up_calls if server_may_make(c)]
        if not mine:
            continue
        report.follow_up_calls = [
            c for c in report.follow_up_calls if not server_may_make(c)
        ]
        run.write_json(run.report_path, report)
        out.extend((report.run_id, c) for c in mine)
    return out


def record_follow_up(settings: Settings, run_id: str, call: dict, job_id: str) -> None:
    run = RunRecorder.open(settings.runs_dir, run_id)
    report = Report.model_validate_json(run.report_path.read_text("utf-8"))
    report.follow_ups_made.append({**call, "job_id": job_id})
    run.write_json(run.report_path, report)
    run.log("follow_up_started", job_id=job_id, tests=call.get("tests"))


def outstanding(settings: Settings, jobs: list) -> Outstanding:
    """Open questions and follow-up calls left in this session's runs, read
    from each run's report as it is now (answers since the run included)."""
    runs, running, done = [], [], 0
    for j in jobs:
        if j.task is None or not j.task.done():
            running.append(
                {
                    "job_id": j.id,
                    "target": j.url,
                    "status": "queued" if j.started is None else "running",
                    "progress": j.message,
                }
            )
            continue
        if j.task.cancelled() or j.task.exception() is not None:
            continue
        res = j.task.result()
        try:
            run = RunRecorder.open(settings.runs_dir, res.run_id)
            report = Report.model_validate_json(run.report_path.read_text("utf-8"))
        except Exception:
            continue  # expired or removed
        if not report.open_questions and not report.follow_up_calls:
            done += 1
            continue
        waiting = {q.test_id for q in report.open_questions}
        runs.append(
            OutstandingRun(
                run_id=report.run_id,
                target=report.target,
                open_questions=len(report.open_questions),
                tests_waiting=[t.value for t in TestId if t in waiting],
                follow_up_calls=report.follow_up_calls,
                report_uri=run_uri(run.run_id, run.rel(run.report_path)),
            )
        )
    q = sum(r.open_questions for r in runs)
    c = sum(len(r.follow_up_calls) for r in runs)
    user = [
        {"run_id": r.run_id, **call}
        for r in runs
        for call in r.follow_up_calls
        if not server_may_make(call)
    ]
    if runs or running:
        step = (
            f"Left: {q} open question(s) in {len(runs)} run(s) and {c} follow-up "
            f"call(s); {len(running)} run(s) still going. For each run, answer "
            "its open questions with tobi_answer_questions (its report_uri has "
            "them, or call tobi_run_status with the job_id of a run still "
            "going). Then call tobi_run_status with finish=true: the server "
            "makes the follow-up calls it may make itself and waits for them. "
            "Ask the user about those in for_the_user. Call this again until "
            "nothing is left, before you report to the user."
        )
    else:
        step = (
            "Nothing is left: every run of this session is finished, with no "
            "open question or follow-up call."
        )
    items: list[str] = []
    if q:
        items.append(
            f"[ ] Answer {q} open question(s) left in {len(runs)} run(s) "
            "(tobi_answer_questions, one call per run)."
        )
    if c - len(user):
        items.append(
            f"[ ] Call tobi_run_status with finish=true: {c - len(user)} "
            "follow-up call(s) the server makes itself."
        )
    if user:
        items.append(f"[ ] Ask the user about {len(user)} call(s) in for_the_user.")
    if running:
        items.append(
            f"[ ] Wait for {len(running)} run(s) still going (tobi_run_status "
            "with each job_id)."
        )
    items.append(
        "[ ] Call this again until it lists nothing left, then report."
        if items
        else "[x] Nothing left: report to the user, and save each run's report."
    )
    return Outstanding(
        runs=runs,
        running=running,
        done=done,
        for_the_user=user,
        next_step=step,
        todo=items,
    )
