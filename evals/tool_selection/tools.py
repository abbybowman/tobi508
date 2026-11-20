"""The tool list an MCP client sees from the real server, in one judge mode.

    uv run python -m evals.tool_selection.tools client   # JSON on stdout

The server builds some descriptions from its settings when it starts (the
judge paragraph of tobi_run_tt_tests differs with JUDGE_BACKEND), so each
mode is listed in its own process, with the setting in its environment.
The list is read in process through FastMCP's client, exactly as the
server sends it over MCP: names, descriptions, input schemas, output
schemas and annotations.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODES = ("client", "api")

# What each mode needs to start. "api" with the CLI route needs no gateway
# address or key; the judge is never called, only described.
MODE_ENV = {
    "client": {"JUDGE_BACKEND": "client"},
    "api": {"JUDGE_BACKEND": "api", "JUDGE_ROUTE": "cli"},
}
# Settings that would change a description if a developer's shell had them.
CLEAR = (
    "JUDGE_BACKEND",
    "JUDGE_ROUTE",
    "JUDGE_BASE_URL",
    "JUDGE_API_KEY",
    "NO_TIME_LIMIT_DEFAULT",
    "RUN_LIMIT_S",
    "OTHER_PAGE_S",
    "MAX_RUN_S",
    "CALL_WAIT_S",
    "DEV_MODE",
)


async def _list() -> list[dict]:
    from fastmcp import Client

    from tobi508.app import mcp

    async with Client(mcp) as c:
        tools = await c.list_tools()
    return [t.model_dump(mode="json", by_alias=True, exclude_none=True) for t in tools]


def tool_list(mode: str) -> list[dict]:
    """The real server's tools in `mode`, from a fresh process."""
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    env = {k: v for k, v in os.environ.items() if k not in CLEAR} | MODE_ENV[mode]
    out = subprocess.run(
        [sys.executable, "-m", "evals.tool_selection.tools", mode],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)


def main(argv: list[str]) -> None:
    mode = argv[0] if argv else "client"
    from tobi508 import config

    if config.settings.judge_backend != mode:
        sys.exit(
            f"Started for {mode!r} but the server resolved "
            f"{config.settings.judge_backend!r}: use tool_list()"
        )
    print(json.dumps(asyncio.run(_list()), indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
