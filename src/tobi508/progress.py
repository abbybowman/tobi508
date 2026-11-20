"""The progress line a running job reports (jobs.Job.progress, RunPending).

A run reads the page in several steps (recording it, other pages, the
keyboard walk, opening menus, the inventory, hidden fields), some of which a
given run does not need, then checks its tests one by one in an order that
is not the report's (cheapest first, checks.base.AFTER). A bare phase name
told the calling agent and its user little about how far along the run was,
so each line says how many of the run's reading steps are done or not
needed, then how many of its tests are done, with a rough percentage.

The plan of reading steps is fixed when the run starts and a step that turns
out not to be needed counts as done, so the counts never go back. The client
bar's step (of 4) keeps its stages: reading 0-2, tests 2-3, evaluating and
judging 3-4. No outcome is decided here.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable

Progress = Callable[[float, float | None, str], Awaitable[None]]


def _pct(done: int, total: int) -> int:
    return 100 if total <= 0 else int(100 * done / total)


def _now(message: str) -> str:
    return message[:1].lower() + message[1:]


class Tracker:
    def __init__(self, progress: Progress | None, steps: Iterable[str]) -> None:
        self._progress = progress
        self.steps = list(dict.fromkeys(steps))
        self.closed: set[str] = set()
        self.tests_total = 0

    def close(self, *keys: str) -> None:
        """Steps done, or found not needed."""
        self.closed.update(k for k in keys if k in self.steps)

    async def _send(self, step: float, line: str) -> None:
        if self._progress is not None:
            await self._progress(step, 4, line)

    async def reading(self, message: str) -> None:
        n, t = len(self.closed), len(self.steps)
        await self._send(
            2 * n / t if t else 0,
            f"Reading the page, {n} of {t} steps done or not needed "
            f"({_pct(n, t)}%): {_now(message)}",
        )

    async def testing(self, done: int, total: int, message: str) -> None:
        self.close(*self.steps)
        self.tests_total = total
        await self._send(
            2 + (done / total if total else 1),
            f"Page read (100%). Testing, {done} of {total} tests done "
            f"({_pct(done, total)}%): {_now(message)}",
        )

    async def finishing(self, step: float, message: str) -> None:
        self.close(*self.steps)
        t = self.tests_total
        await self._send(
            step,
            f"Page read and all {t} test{'s' if t != 1 else ''} checked (100%). "
            f"Finishing: {_now(message)}",
        )
