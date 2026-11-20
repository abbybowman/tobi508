"""Runs that outlive one tool call (post-round 1 fixes 2 and 5, option C).

A tool call starts a run as a job and waits for it up to `call_wait_s`
(default 45 s, under the common 60 s MCP client timeout). A run that
finishes in time is returned as before; otherwise the call returns the job
id and the progress so far, and tobi_run_status waits again. The run goes
on in the server meanwhile, within its own time limit (`run_limit_s` and
the rest, unchanged), so a client's timeout or background move no longer
loses it.

At most `max_concurrent_runs` runs use a browser at once. A job waiting for
a slot has not started its run yet, so the wait does not use its time limit
(the pipeline starts the clock when it is called). A run gives its slot back
when its browsers close (`release_browser_slot`), so the server's judge,
which needs no browser, never holds one (code review B-04).

A job carries the signed-in caller who started it, and only that caller
sees it (`get`, `all_jobs`, `running`), as run folders do (code review
A-01). Without sign-in every job is open: a local server has one user.

A job can be cancelled (`cancel`): by the caller who started it, with
tobi_cancel_run, or by the server's operator from inside its container
(`admin.py`, which sees every caller's jobs). A cancelled run keeps no
folder (pipeline.py removes it), and waiting on it raises RunCancelled
(demo run, 2026-11-20: a duplicate run held the only browser slot, and a
restart was the only way to stop it).

Jobs live in this process's memory: a server restart loses running jobs
and the record of finished ones (a finished run's folder and report stay
until `run_ttl_hours`; an unfinished one's folder is pruned with them). No
outcome is decided here.
"""

from __future__ import annotations

import asyncio
import secrets
import time
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from tobi508 import access, livelog
from tobi508.config import Settings
from tobi508.models import RunPending, RunResult

ProgressFn = Callable[[float, float | None, str], Awaitable[None]]


@dataclass
class Job:
    id: str
    url: str
    tests: list[str] = field(default_factory=list)
    created: float = field(default_factory=time.monotonic)
    started: float | None = None  # when it got a browser slot
    finished: float | None = None
    step: float = 0.0
    message: str = "Waiting for a free browser slot"
    task: asyncio.Task | None = None
    waiters: list[ProgressFn] = field(default_factory=list)
    owner: str | None = None  # the signed-in caller who started it (A-01)
    cancelled_by: str | None = None  # "the caller" or "the server's operator"

    async def progress(self, step: float, total: float | None, message: str) -> None:
        self.step, self.message = step, message
        livelog.emit("progress", job=self.id, target=self.url, message=message)
        for w in list(self.waiters):
            try:
                await w(step, total, message)
            except Exception:
                # A waiter whose call has ended: its client is gone.
                if w in self.waiters:
                    self.waiters.remove(w)


class RunCancelled(Exception):
    """Waiting on a job that was cancelled: a tool error, with who did it."""


# How long a cancel waits for the run to close its browsers.
CANCEL_WAIT_S = 15.0

_JOBS: dict[str, Job] = {}
_SLOTS: dict[tuple[int, int], asyncio.Semaphore] = {}
# The running job's way to give its browser slot back early (B-04).
_RELEASE: ContextVar[Callable[[], None] | None] = ContextVar(
    "tobi508_slot_release", default=None
)


def release_browser_slot() -> None:
    """Called by the pipeline once its browsers are closed: the work after
    that (evaluating, the server's judge) does not hold a browser slot, so a
    queued run can start. Outside a job, nothing to do."""
    fn = _RELEASE.get()
    if fn is not None:
        fn()


def _slots(n: int) -> asyncio.Semaphore:
    key = (id(asyncio.get_running_loop()), n)
    if key not in _SLOTS:
        _SLOTS[key] = asyncio.Semaphore(n)
    return _SLOTS[key]


def _prune(settings: Settings) -> None:
    now = time.monotonic()
    for jid, j in list(_JOBS.items()):
        if j.finished is not None and now - j.finished > settings.job_keep_s:
            del _JOBS[jid]


def start(
    settings: Settings,
    url: str,
    run: Callable[[ProgressFn], Awaitable[RunResult]],
) -> Job:
    """Start `run` (the pipeline call, given a progress function) as a job."""
    _prune(settings)
    job = Job(id="job-" + secrets.token_hex(6), url=url, owner=access.caller())
    slots = _slots(settings.max_concurrent_runs)

    async def go() -> RunResult:
        held = False

        def release() -> None:
            nonlocal held
            if held:
                held = False
                slots.release()

        _RELEASE.set(release)  # this task's own context
        try:
            await slots.acquire()
            held = True
            job.started = time.monotonic()
            await job.progress(
                0, 4, "Starting the browser; part 1 of 3, reading the page, is next"
            )
            return await run(job.progress)
        finally:
            release()
            job.finished = time.monotonic()
            job.waiters.clear()

    job.task = asyncio.get_running_loop().create_task(go())
    _JOBS[job.id] = job
    return job


def _mine(job: Job) -> bool:
    """Whether the caller may see this job: its owner, or anyone without
    sign-in. As with runs, another caller's job reads as unknown."""
    sub = access.caller()
    return sub is None or job.owner == sub


def get(job_id: str) -> Job | None:
    job = _JOBS.get(job_id)
    return job if job is not None and _mine(job) else None


async def wait(
    job: Job, seconds: float, progress: ProgressFn | None = None
) -> RunResult | RunPending:
    """The job's result if it ends within `seconds` (its error is raised),
    else where it is. Waiting never cancels the job."""
    assert job.task is not None
    if progress is not None and not job.task.done():
        job.waiters.append(progress)
    try:
        await asyncio.wait({job.task}, timeout=seconds)
    finally:
        if progress in job.waiters:
            job.waiters.remove(progress)
    if job.task.cancelled():
        raise RunCancelled(cancelled_text(job))
    if job.task.done():
        return job.task.result()
    return pending(job, seconds)


def cancelled_text(job: Job) -> str:
    who = job.cancelled_by or "the server"
    return (
        f"Run {job.id} ({job.url}) was cancelled by {who}; nothing from it was "
        "kept. Tell the user. Start it again only if the user asks."
    )


async def cancel(job: Job, by: str) -> str:
    """Cancel a queued or running job and wait (up to CANCEL_WAIT_S) for it to
    close its browsers. Returns what the job was doing: "queued", "running"
    or, for one already over, "finished" (nothing is changed then)."""
    assert job.task is not None
    if job.task.done():
        return "finished"
    was = "queued" if job.started is None else "running"
    job.cancelled_by = by
    job.task.cancel()
    await asyncio.wait({job.task}, timeout=CANCEL_WAIT_S)
    livelog.emit("progress", job=job.id, target=job.url, message=f"Cancelled by {by}")
    return was


def _mmss(seconds: float) -> str:
    m, sec = divmod(int(seconds), 60)
    return f"{m} min {sec} s" if m else f"{sec} s"


def _ahead(job: Job) -> tuple[list[str], int]:
    """The runs a queued job waits behind: the caller's own (by job id) and
    how many in all, other callers' included (counted, never named)."""
    busy = [
        j
        for j in _JOBS.values()
        if j is not job
        and j.task is not None
        and not j.task.done()
        and j.created <= job.created
    ]
    return [j.id for j in busy if _mine(j)], len(busy)


def pending(job: Job, wait_s: float) -> RunPending:
    now = time.monotonic()
    queued = job.started is None
    again = (
        f"Call tobi_run_status with job_id {job.id!r} to wait for it again (each "
        f"call waits up to {int(wait_s)} s). Do not start the same run "
        "again, and do not end your turn while it runs: you would lose "
        "its result."
    )
    if queued:
        mine, total = _ahead(job)
        dup = (
            f" It waits behind your own run(s) {', '.join(mine)}: if one of them "
            "is the same page started twice, or the user wants to stop one, "
            "tobi_cancel_run cancels it (tell the user which, and why)."
            if mine
            else ""
        )
        return RunPending(
            job_id=job.id,
            target=job.url,
            status="queued",
            seconds_waiting=round(now - job.created, 1),
            seconds_running=0.0,
            progress=(
                f"Waiting for a free browser slot ({_mmss(now - job.created)} so "
                f"far): {total} run(s) ahead of it use the server's browser; it "
                "starts when one ends, and its time limit has not started"
            ),
            runs_ahead=total,
            your_runs_ahead=mine,
            next_step=(
                "Tell the user the run is waiting for another run to finish, "
                "not testing yet." + dup + " " + again
            ),
        )
    return RunPending(
        job_id=job.id,
        target=job.url,
        status="running",
        seconds_waiting=round(job.started - job.created, 1),
        seconds_running=round(now - job.started, 1),
        progress=f"{job.message} ({_mmss(now - job.started)} so far)",
        next_step=(
            "Tell the user the progress line in a few words, keeping its part "
            '(for example "part 1 of 3, reading the page: 5 of 6 steps"). Its '
            "percentage covers only the part it names, never the whole run, "
            "and the parts take different times: give no overall percentage "
            "or time left. The run is still going on in the server; nothing is "
            "lost. To stop it, only if the user asks: tobi_cancel_run. " + again
        ),
    )


def all_jobs(settings: Settings) -> list[Job]:
    """The caller's jobs still kept, oldest first."""
    _prune(settings)
    return sorted((j for j in _JOBS.values() if _mine(j)), key=lambda j: j.created)


def every_job() -> list[Job]:
    """Every caller's jobs, oldest first: for the server's operator only
    (admin.py), never for a tool."""
    return sorted(_JOBS.values(), key=lambda j: j.created)


def get_any(job_id: str) -> Job | None:
    """A job by id whoever started it: for the server's operator only."""
    return _JOBS.get(job_id)


def running() -> list[dict[str, Any]]:
    """Jobs not finished yet (for tests and diagnostics)."""
    return [
        {"id": j.id, "url": j.url}
        for j in _JOBS.values()
        if j.finished is None and _mine(j)
    ]
