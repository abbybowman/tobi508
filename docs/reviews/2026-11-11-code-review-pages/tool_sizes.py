"""Print what the tool list costs a session, in characters (A-02).

uv run python docs/reviews/2026-11-11-code-review-pages/tool_sizes.py
"""

import asyncio
import json

from tobi508.app import mcp


async def main() -> None:
    total = 0
    for t in await mcp.list_tools():
        tool = t.to_mcp_tool()
        desc = len(t.description or "")
        inp = len(json.dumps(tool.inputSchema))
        out = len(json.dumps(tool.outputSchema)) if tool.outputSchema else 0
        total += desc + inp + out
        print(f"{t.name:26} description {desc:6} input {inp:6} output {out:6}")
    print("total", total, "server instructions", len(mcp.instructions or ""))


asyncio.run(main())
