"""Run the tool selection cases with Claude Code's own client against the
stub server (README.md).

    uv run python -m evals.tool_selection.run OUT --label before \\
        --models claude-sonnet-5-5,claude-haiku-5-5 --repeats 3

Each run is one isolated `claude -p` (the agent eval's CLI isolation:
an empty HOME and working folder, no settings, the session's identifying
variables unset), with Claude Code's default system prompt, only the stub
server and the CLI's MCP resource tools, and at most MAX_TURNS model turns.
OUT/<label>/ gets the tool list served in each mode, one folder per run
(events.jsonl, calls.jsonl) and results.jsonl (one scored line per run).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
import tempfile
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from evals.agent.arms import _base_env
from evals.agent.cli import ClaudeCodeCLI
from evals.tool_selection import score
from evals.tool_selection.tools import MODES, tool_list

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SERVER = "tobi508"
BUILTIN = ["ListMcpResourcesTool", "ReadMcpResourceTool"]
MAX_TURNS = 4
RUN_TIMEOUT_S = 240
# One empty working folder for every run: Claude Code's system prompt names
# it, so a fresh temporary name would defeat the prompt cache between runs
# (pilot: 10k tokens written to the cache on every run). Nothing writes to
# it: the agent has no file tools.
WORK = Path(tempfile.gettempdir()) / "toolsel-work"


def load_cases(path: Path = HERE / "cases.toml") -> list[dict]:
    return tomllib.loads(path.read_text("utf-8"))["case"]


def render_prior(name: str) -> str:
    """Earlier turns as text in the prompt (the CLI cannot be handed a
    fabricated conversation): the user's words, each call with its result,
    and what the assistant said."""
    turns = json.loads((HERE / "priors" / f"{name}.json").read_text("utf-8"))["turns"]
    out = []
    for t in turns:
        if "user" in t:
            out.append(f"User: {t['user']}")
        elif "call" in t:
            c = t["call"]
            out.append(
                f"Assistant called {c['name']} with arguments "
                f"{json.dumps(c['arguments'])}. The tool returned:\n```json\n"
                f"{json.dumps(t['result'], indent=1)}\n```"
            )
        elif "assistant" in t:
            out.append(f"Assistant: {t['assistant']}")
    return "\n\n".join(out)


def prompt_for(case: dict) -> str:
    text = case["prompt"].replace(
        "{scrt}", (HERE / "priors" / "tester-scrt.json").read_text("utf-8").strip()
    )
    if not case.get("prior"):
        return text
    return (
        "Earlier in this conversation (you are the assistant; the tool calls "
        "and results below really happened):\n\n"
        + render_prior(case["prior"])
        + "\n\n---\n\nThe user's new message:\n\n"
        + text
    )


def cli_args(binary: str, model: str, prompt: str, mcp: Path) -> list[str]:
    return [
        binary, "-p", prompt,
        "--model", model,
        "--output-format", "stream-json", "--verbose",
        "--setting-sources", "",
        "--disable-slash-commands",
        "--strict-mcp-config", "--mcp-config", str(mcp),
        "--tools", ",".join(BUILTIN),
        "--allowedTools", ",".join([f"mcp__{SERVER}", *BUILTIN]),
        "--no-session-persistence",
        "--max-turns", str(MAX_TURNS),
    ]  # fmt: skip


async def one_run(
    cli: ClaudeCodeCLI,
    case: dict,
    mode: str,
    model: str,
    tools_file: Path,
    run_dir: Path,
) -> dict:
    run_dir.mkdir(parents=True, exist_ok=True)
    calls = run_dir / "calls.jsonl"
    calls.touch()
    events: list[dict] = []
    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="toolsel-") as tmp:
        tmp = Path(tmp)
        (tmp / "home").mkdir()
        WORK.mkdir(exist_ok=True)
        mcp = tmp / "mcp.json"
        env = _base_env() | {"PYTHONPATH": str(REPO)}
        mcp.write_text(json.dumps({"mcpServers": {SERVER: {
            "command": sys.executable,
            "args": ["-m", "evals.tool_selection.stub", str(tools_file), str(calls)],
            "env": env,
        }}}))  # fmt: skip
        proc = await asyncio.create_subprocess_exec(
            *cli_args(cli.binary, model, prompt_for(case), mcp),
            cwd=WORK,
            env=cli._env(tmp / "home"),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=16 * 1024 * 1024,
        )
        try:
            async with asyncio.timeout(RUN_TIMEOUT_S):
                async for raw in proc.stdout:
                    try:
                        events.append(json.loads(raw))
                    except ValueError:
                        continue
                await proc.wait()
        except TimeoutError:
            proc.kill()
            await proc.wait()
        err = (await proc.stderr.read()).decode("utf-8", "replace")
    with (run_dir / "events.jsonl").open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    res = next((e for e in reversed(events) if e.get("type") == "result"), {})
    init = next((e for e in events if e.get("subtype") == "init"), {})
    servers = init.get("mcp_servers") or []
    return {
        "exit_code": proc.returncode,
        "stderr": err[-500:] if proc.returncode else "",
        "server_connected": any(s.get("status") == "connected" for s in servers),
        "tools_seen": init.get("tools"),
        "model_reported": sorted((res.get("modelUsage") or {}).keys()),
        "cost_usd_list_price": res.get("total_cost_usd"),
        "usage": res.get("usage"),
        "num_turns": res.get("num_turns"),
        "ended": res.get("subtype") or "no result",
        "wall_s": round(time.monotonic() - t0, 1),
        "stub_calls": [json.loads(x) for x in calls.read_text().splitlines() if x],
        "events": events,
    }


async def run_all(
    out: Path,
    label: str,
    models: list[str],
    modes: list[str],
    repeats: int,
    only: set[str] | None,
    concurrency: int,
) -> Path:
    base = out / label
    base.mkdir(parents=True, exist_ok=True)
    cases = [c for c in load_cases() if not only or c["id"] in only]
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip()  # fmt: skip
    schemas: dict[str, dict[str, dict]] = {}
    for mode in modes:
        tools = tool_list(mode)
        f = base / f"tools-{mode}.json"
        f.write_text(json.dumps(tools, indent=1) + "\n")
        schemas[mode] = {t["name"]: t["inputSchema"] for t in tools}
    meta = {
        "label": label, "commit": commit, "models": models, "modes": modes,
        "repeats": repeats, "cases": [c["id"] for c in cases],
        "max_turns": MAX_TURNS, "started_at": datetime.now(timezone.utc).isoformat(),
        "tools_sha256": {
            m: hashlib.sha256((base / f"tools-{m}.json").read_bytes()).hexdigest()
            for m in modes
        },
        "claude_version": subprocess.run(["claude", "--version"], capture_output=True,
                                         text=True).stdout.strip(),
    }  # fmt: skip
    (base / "meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    results = base / "results.jsonl"
    done = set()
    if results.exists():
        for line in results.read_text().splitlines():
            r = json.loads(line)
            done.add((r["case"], r["mode"], r["model"], r["repeat"]))
    cli = ClaudeCodeCLI()
    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    jobs = [
        (c, mode, model, rep)
        for model in models
        for mode in modes
        for rep in range(1, repeats + 1)
        for c in cases
        if mode in c.get("modes", MODES) and (c["id"], mode, model, rep) not in done
    ]

    async def go(c, mode, model, rep):
        async with sem:
            rd = base / "runs" / f"{c['id']}__{mode}__{model}__{rep}"
            r = await one_run(cli, c, mode, model, base / f"tools-{mode}.json", rd)
            s = score.score_run(c, r.pop("events"), schemas[mode])
            line = {"case": c["id"], "expect": c["expect"]["tool"], "mode": mode,
                    "model": model, "repeat": rep, **s, **r}  # fmt: skip
            async with lock:
                with results.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(line, default=str) + "\n")
            mark = "ok " if s["passed"] else "BAD"
            print(f"{mark} {c['id']:24} {mode:6} {model:18} #{rep} "
                  f"{s['first_call']} ${r['cost_usd_list_price']} {s['notes'][:2]}",
                  flush=True)  # fmt: skip

    await asyncio.gather(*(go(*j) for j in jobs))
    return results


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out", type=Path)
    ap.add_argument("--label", required=True, help="e.g. before, after")
    ap.add_argument("--models", default="claude-sonnet-5-5,claude-haiku-5-5")
    ap.add_argument("--modes", default=",".join(MODES))
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--cases", help="comma-separated case ids (default: all)")
    ap.add_argument("--concurrency", type=int, default=4)
    a = ap.parse_args(argv)
    asyncio.run(run_all(
        a.out, a.label, a.models.split(","), a.modes.split(","), a.repeats,
        set(a.cases.split(",")) if a.cases else None, a.concurrency,
    ))  # fmt: skip


if __name__ == "__main__":
    main(sys.argv[1:])
