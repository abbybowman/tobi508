"""A stub MCP server for the tool selection eval: it serves a recorded tool
list (tools.py) word for word, records every call, and answers each with a
short canned result. Nothing is tested and no page is loaded.

    python -m evals.tool_selection.stub TOOLS.json CALLS.jsonl

Served as recorded: name, title, description, input schema, annotations.
Not served: the output schema (a client checks a result against it, and a
canned result does not match TOBI's; Claude Code does not show it to the
model) and the server's instructions (the eval measures the tool
descriptions alone). The stub does not check arguments: the scorer checks
them against the recorded input schema, so an invalid call is recorded,
not refused.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from fastmcp.tools.base import Tool, ToolResult
from mcp.types import TextContent, ToolAnnotations

DISCLAIMER = (
    "Agent-assisted findings only. This is NOT a certified DHS Trusted Tester "
    "result and must not be reported as one."
)
ALLOWED = (".gov", ".mil")
COMPARE = ("9.A", "9.B", "9.C")


def _allowed(url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return any(host.endswith(s) for s in ALLOWED)


def canned(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """A short result in the shape of the real one. Raises ToolError where
    the real server would refuse before testing anything (a URL outside
    the allowlist, or 9.A-9.C with neither other_pages nor no_other_pages)."""
    base = {"disclaimer": DISCLAIMER, "stub": "evaluation stub: no page was loaded"}
    if name == "tobi_run_tt_tests":
        url = str(args.get("url") or "")
        if not _allowed(url):
            raise ToolError(
                f"Not allowed: {urlsplit(url).hostname or url!r} is not on the "
                "server's allowlist (*.gov, *.mil). Nothing was tested."
            )
        # As tools/run_tt_tests.py's _check_other_pages (no tests means all).
        compare = {"9.A", "9.B", "9.C"} & set(args.get("tests") or COMPARE)
        if compare and not args.get("other_pages") and not args.get("no_other_pages"):
            raise ToolError(
                "Nothing was tested yet. 9.A-9.C compare the page with other "
                "pages of the same site. Ask the user for 2-4 of them and call "
                "again with other_pages; if the user has none, call again with "
                "no_other_pages=true."
            )
        return base | {
            "status": "done",
            "work": "complete",
            "run_id": "20261119T999999Z-stub01",
            "target": url,
            "tests": args.get("tests") or ["(every implemented test)"],
            "findings": [],
            "next_step": "No open questions. Relay each finding's summary.",
            "report_uri": "run://20261119T999999Z-stub01/report.json",
            "pre_scrt_uri": "run://20261119T999999Z-stub01/pre-scrt.json",
        }
    if name == "tobi_run_status":
        if args.get("job_id"):
            return base | {
                "status": "running",
                "job_id": args["job_id"],
                "progress": "Still running (stub).",
            }
        return base | {
            "status": "outstanding",
            "runs": [],
            "running": [],
            "done": 1,
            "started": [],
            "for_the_user": [],
            "next_step": "Nothing is left.",
        }
    if name == "tobi_answer_questions":
        ids = [
            a.get("question_id")
            for a in args.get("answers") or []
            if isinstance(a, dict)
        ]
        return base | {
            "work": "complete",
            "run_id": args.get("run_id"),
            "accepted": ids,
            "rejected": [],
            "findings": [],
            "open_questions": [],
        }
    if name == "tobi_cancel_run":
        return base | {
            "job_id": args.get("job_id"),
            "status": "cancelled",
            "was": "running",
            "next_step": "Tell the user the run was cancelled.",
        }
    if name == "tobi_explain":
        return base | {"text": "(stub) The explanation would be here."}
    if name == "tobi_read_report":
        return base | {
            "format": "scrt",
            "counts": {},
            "failures": [],
            "needs_person": [],
            "comparison": None,
        }
    return base


class StubTool(Tool):
    log_path: str

    async def run(self, arguments: dict[str, Any]) -> ToolResult:
        rec: dict[str, Any] = {
            "t": time.time(),
            "name": self.name,
            "arguments": arguments,
        }
        try:
            out = canned(self.name, arguments)
        except ToolError as exc:
            rec["error"] = str(exc)
            raise
        finally:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")
        return ToolResult(content=[TextContent(type="text", text=json.dumps(out))])


def build(tools: list[dict], log_path: str) -> FastMCP:
    mcp = FastMCP(name="tobi508")
    for t in tools:
        ann = t.get("annotations")
        mcp.add_tool(
            StubTool(
                name=t["name"],
                title=t.get("title"),
                description=t.get("description"),
                parameters=t["inputSchema"],
                annotations=ToolAnnotations(**ann) if ann else None,
                output_schema=None,
                log_path=log_path,
            )
        )
    return mcp


def main(argv: list[str]) -> None:
    tools = json.loads(Path(argv[0]).read_text("utf-8"))
    build(tools, argv[1]).run(show_banner=False)


if __name__ == "__main__":
    main(sys.argv[1:])
