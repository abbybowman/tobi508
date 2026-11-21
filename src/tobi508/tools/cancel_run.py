"""Tool: cancel a run the caller started (tobi_run_tt_tests or a follow-up)."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field

from tobi508 import jobs
from tobi508.models import NOT_CERTIFIED_DISCLAIMER


class CancelResult(BaseModel):
    disclaimer: str = NOT_CERTIFIED_DISCLAIMER
    job_id: str
    target: str
    status: Literal["cancelled", "already_finished"] = Field(
        description='"cancelled": stopped, nothing kept; "already_finished": '
        "it had ended, nothing changed (tobi_run_status with its job_id gives "
        "its result)."
    )
    was: str = Field(description='What it was doing: "queued" or "running".')
    next_step: str


def register(mcp: FastMCP) -> None:
    """Register the tobi_cancel_run tool with the MCP server."""

    @mcp.tool(
        name="tobi_cancel_run",
        annotations={
            "title": "Cancel a run",
            "readOnlyHint": False,
            "destructiveHint": True,  # the run's work so far is discarded
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def cancel_run(
        job_id: Annotated[
            str,
            Field(
                pattern=r"^job-[0-9a-f]{12}$",
                description='job_id of one of your runs that is "queued" or '
                '"running" (tobi_run_status with no job_id lists them).',
            ),
        ],
    ) -> CancelResult:
        """Stop one of your own runs that is still queued or running, and free
        its browser slot. Nothing from it is kept: no report, no pre-SCRT
        file.

        Use it only when the user asks to stop a run, or for a run you started
        twice by mistake (the same page and tests as another of your runs
        still going); say which run you cancelled and why. Never cancel a run
        to start it again with other settings unless the user asks. You can
        cancel only runs started in your own session; the server's operator
        can cancel any run from the server itself.
        """
        job = jobs.get(job_id)
        if job is None:
            raise ToolError(
                "None of your runs has this job_id: it may be another person's, "
                "long finished, or from before a server restart (a restart ends "
                "every run)."
            )
        was = await jobs.cancel(job, "the caller")
        if was == "finished":
            return CancelResult(
                job_id=job.id,
                target=job.url,
                status="already_finished",
                was="finished",
                next_step="Nothing was cancelled: the run had already ended. "
                f"tobi_run_status with job_id {job.id!r} gives its result.",
            )
        return CancelResult(
            job_id=job.id,
            target=job.url,
            status="cancelled",
            was=was,
            next_step="Tell the user the run was cancelled and nothing from it "
            "was kept. A run queued behind it can now start. Start this page "
            "again only if the user asks.",
        )
