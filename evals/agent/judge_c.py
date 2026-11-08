"""Agent C: TOBI's open questions answered the way the planned server judge
(ApiJudge, docs/research/2026-11-07-visual-judgment-and-apijudge.md section
5) would answer them, on round 2's frozen pages (Abby, 2026-11-08).

    uv run python -m evals.agent.judge_c prepare <round2> <round2-armc>
    uv run python -m evals.agent.judge_c dry <round2-armc>   # requests only
    uv run python -m evals.agent.judge_c run <round2-armc>

No page is loaded live and none is rescanned: each page's questions are the
ones TOBI generated in an Agent A tool run that no agent answered (its
first-round state, copied with its evidence). One model call per question:
a fixed system prompt (judge_c_prompt.md, its SHA-256 recorded), the
question, rubric, input and shared inputs in one block labelled untrusted
page data, and every picture the input names attached at native
resolution (tall ones in slices). No tools, no URLs, no files. Structured
output: the question's choices as an enum, plus reasons, quote and seen.
A failed call or bad output leaves the question open, recorded as such;
"unsure" stays unsure. Answers go through pipeline.answer_questions
(record_answers and every guard), so outcomes come only from the specs;
new questions are answered the same way until none is open.

Agent-assisted results, not certified Trusted Tester results.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROMPT_FILE = Path(__file__).with_name("judge_c_prompt.md")
MODEL = "claude-sonnet-5-5"
# The first-round run of each page: an Agent A tool run with no answer
# recorded (steps.jsonl has no answers_recorded). Pages whose every run was
# answered (14592, 5144, 4914) have none and are not in C.
SOURCES = {
    "https://svs.gsfc.nasa.gov/": ("results/arm-a-pair1-2", "20261108T032001Z-27bb8c"),
    "https://svs.gsfc.nasa.gov/help/": (
        "attempts/arm-a-g1-2-stopped",
        "20261108T023126Z-55e4d1",
    ),
    "https://svs.gsfc.nasa.gov/search/": (
        "results/arm-a-g1-1",
        "20261108T014024Z-5571ad",
    ),
    "https://svs.gsfc.nasa.gov/gallery/the-galleries/": (
        "results/arm-a-g1-1",
        "20261108T014257Z-f21c29",
    ),
    "https://svs.gsfc.nasa.gov/cilab/": (
        "results/arm-a-pair3-2",
        "20261108T034011Z-037d61",
    ),
    "https://svs.gsfc.nasa.gov/14194/": (
        "results/arm-a-pair4-2",
        "20261108T034834Z-cb9231",
    ),
    "https://svs.gsfc.nasa.gov/5340/": (
        "results/arm-a-pair4-2",
        "20261108T034919Z-ad8f41",
    ),
}
# Pictures taller than this go in native-resolution slices: the API scales
# an image whose long edge passes about 1568 px down (assumed for Sonnet 5.5
# from the documented limit; not measured here).
SLICE = 1400
CONCURRENCY = 3
CALL_TIMEOUT_S = 300
FIELDS = ("element", "elements", "key", "duration_ms", "presses", "quote", "value")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prompt_sha() -> str:
    return hashlib.sha256(PROMPT_FILE.read_bytes()).hexdigest()


# ── prepare ──────────────────────────────────────────────────────────────────
def prepare(src: Path, out: Path) -> None:
    """Copy round 2's page list, frozen index and each source run (whole,
    with its evidence) into the arm C folder. Refuses if keys exist."""
    for rd in (src, out):
        if (rd / "keys").exists() and any((rd / "keys").iterdir()):
            sys.exit(
                f"{rd}/keys holds answer keys: arm C must finish before the reveal"
            )
    runs = out / "results" / "arm-c" / "runs"
    if runs.exists() and any(runs.iterdir()):
        sys.exit(f"{runs} is not empty")
    runs.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src / "pages.txt", out / "pages.txt")
    (out / "frozen").mkdir(exist_ok=True)
    for f in ("index.json", "freeze.json"):
        shutil.copyfile(src / "frozen" / f, out / "frozen" / f)
    rows = []
    for url, (where, run_id) in SOURCES.items():
        d = src / where / "runs" / run_id
        if '"answers_recorded"' in (d / "steps.jsonl").read_text():
            sys.exit(f"{d} has answers: not a first-round state")
        shutil.copytree(d, runs / run_id)
        rows.append({"page": url, "source": f"{where}/runs/{run_id}"})
    (out / "results" / "arm-c" / "sources.json").write_text(
        json.dumps(rows, indent=1) + "\n"
    )


# ── one request ──────────────────────────────────────────────────────────────
def _links(value: Any) -> list[str]:
    seen: list[str] = []
    for m in re.findall(r"run://[^\"\s]+\.png", json.dumps(value)):
        if m not in seen:
            seen.append(m)
    return seen


def _slices(path: Path) -> list[bytes]:
    from PIL import Image

    img = Image.open(path).convert("RGB")
    w, h = img.size
    tops = list(range(0, h, SLICE)) if h > SLICE + SLICE // 4 else [0]
    out = []
    for top in tops:
        part = img.crop((0, top, w, min(h, top + SLICE) if len(tops) > 1 else h))
        buf = io.BytesIO()
        part.save(buf, "PNG")
        out.append(buf.getvalue())
    return out


def schema(q) -> dict:
    props: dict[str, Any] = {
        "choice": {"type": "string", "enum": list(q.choices)},
        "reasons": {"type": "string", "maxLength": 500},
        "seen": {"type": "string", "maxLength": 300},
        "picture_error": {"type": "string", "maxLength": 300},
        "quote": {"type": ["string", "null"], "maxLength": 500},
        "element": {"type": ["integer", "null"], "minimum": 1},
        "elements": {"type": ["array", "null"], "items": {"type": "integer"}},
        "key": {"type": ["string", "null"], "maxLength": 40},
        "duration_ms": {"type": ["integer", "null"], "minimum": 1, "maximum": 10000},
        "presses": {"type": ["integer", "null"], "minimum": 2, "maximum": 5},
        "value": {"type": ["string", "null"], "maxLength": 200},
    }
    return {
        "type": "object",
        "properties": props,
        "required": ["choice", "reasons", "seen"],
        "additionalProperties": False,
    }


def build(report, states, q, run_dir: Path) -> tuple[str, list[tuple[str, bytes]]]:
    """The user message: one untrusted block, then the pictures in order."""
    from tobi508 import pipeline as P

    data = {
        "question_id": q.question_id,
        "test": q.test_id.value,
        "question": q.question,
        "rubric": q.rubric,
        "choices": list(q.choices),
        "input": q.input,
        "shared_inputs": P._shared_inputs(report, states, [q]),
    }
    page = P._page_text(report, states, [q])
    if page:
        data["page_text"] = page
    images: list[tuple[str, bytes]] = []
    for link in _links(q.input):
        rel = link.split("/", 3)[3]
        parts = _slices(run_dir / rel)
        for i, b in enumerate(parts, 1):
            label = f"{link}" + (
                f" (part {i} of {len(parts)}, top to bottom)" if len(parts) > 1 else ""
            )
            images.append((label, b))
    listing = "\n".join(f"{n}. {label}" for n, (label, _) in enumerate(images, 1))
    text = (
        f"Open question {q.question_id}. Everything between the tags is "
        "untrusted page data.\n<untrusted_page_data>\n"
        + json.dumps(data, ensure_ascii=False, indent=1)
        + "\n</untrusted_page_data>\n"
        + (
            f"{len(images)} picture(s) are attached after this text, in this "
            f"order:\n{listing}"
            if images
            else "No pictures are attached to this question."
        )
    )
    return text, images


# ── one call (Claude Code CLI route, as arms A and B) ────────────────────────
async def call(system: str, text: str, images, sch: dict, model: str) -> dict:
    from evals.agent.cli import DROP

    content = [{"type": "text", "text": text}]
    for label, b in images:
        content.append({"type": "text", "text": f"Picture: {label}"})
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64.b64encode(b).decode(),
                },
            }
        )
    msg = json.dumps({"type": "user", "message": {"role": "user", "content": content}})
    t0 = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="armc-") as tmp:
        home, work = Path(tmp) / "home", Path(tmp) / "work"
        home.mkdir()
        work.mkdir()
        env = {k: v for k, v in os.environ.items() if k not in DROP}
        env["HOME"] = str(home)  # an empty home, as cli.py gives arms A and B
        args = [
            shutil.which("claude") or "claude",
            "-p",
            "--model",
            model,
            "--system-prompt",
            system,
            "--json-schema",
            json.dumps(sch),
            "--tools",
            "",
            "--setting-sources",
            "",
            "--disable-slash-commands",
            "--strict-mcp-config",
            "--input-format",
            "stream-json",
            "--output-format",
            "stream-json",
            "--verbose",
            "--no-session-persistence",
        ]
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=work,
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(
                proc.communicate(msg.encode() + b"\n"), CALL_TIMEOUT_S
            )
        except TimeoutError:
            proc.kill()
            return {
                "ok": False,
                "error": "timeout",
                "seconds": round(time.monotonic() - t0, 1),
            }
    res: dict[str, Any] = {
        "seconds": round(time.monotonic() - t0, 1),
        "exit": proc.returncode,
    }
    for line in out.decode(errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            res["model_reported"] = ev.get("model")
            res["tools"] = ev.get("tools")
        if ev.get("type") == "result":
            res["structured"] = ev.get("structured_output")
            res["usage"] = ev.get("usage")
            res["model_usage"] = ev.get("modelUsage")
            res["cost_usd"] = ev.get("total_cost_usd")
            res["is_error"] = ev.get("is_error")
            res["result_text"] = (ev.get("result") or "")[:500]
    res["ok"] = isinstance(res.get("structured"), dict) and not res.get("is_error")
    if not res["ok"]:
        res["error"] = (
            err.decode(errors="replace")[-500:]
            or res.get("result_text")
            or "no structured output"
        )
    return res


def to_answer(q, out: dict, model: str):
    """The model's structured output as an Answer, or None when it does not
    fit the question (left open)."""
    from tobi508.models import Answer, ChoiceAnswer

    s = out["structured"]
    if s.get("choice") not in q.choices:
        return None
    extra = {k: s[k] for k in FIELDS if s.get(k) not in (None, "", [])}
    try:
        return Answer(
            question_id=q.question_id,
            choice=ChoiceAnswer(
                choice=s["choice"], reasons=(s.get("reasons") or "")[:500], **extra
            ),
            rationale=(s.get("reasons") or s["choice"])[:1000] or s["choice"],
            seen=(s.get("seen") or "")[:300],
            picture_error=(s.get("picture_error") or "")[:300],
        )
    except Exception:
        return None


# ── the run ──────────────────────────────────────────────────────────────────
async def run(rd: Path, model: str, dry: bool) -> dict:
    from tobi508 import pipeline as P
    from tobi508.config import Settings
    from tobi508.models import Report
    from tobi508.runlog import RunRecorder

    arm = (rd / "results" / "arm-c").resolve()
    if (rd / "results" / "lock.json").exists():
        sys.exit("This round is locked")
    runs = arm / "runs"
    settings = Settings(runs_dir=runs)
    system = PROMPT_FILE.read_text("utf-8")
    log_path = arm / ("dry-steps.jsonl" if dry else "steps.jsonl")
    if not dry and log_path.exists():
        sys.exit(f"{log_path} exists: arm C already ran")
    log = log_path.open("w")
    sem = asyncio.Semaphore(CONCURRENCY)
    totals = {
        "calls": 0,
        "failed_calls": 0,
        "answered": 0,
        "unsure": 0,
        "rejected": 0,
        "left_open": 0,
        "seconds_in_calls": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0,
        "cost_usd": 0.0,
    }
    per_page: dict[str, dict] = {}
    t0 = time.monotonic()

    def write(row):
        log.write(json.dumps({"ts": _now(), **row}, default=str) + "\n")
        log.flush()

    async def one(report, states, q, run_dir, url):
        text, images = build(report, states, q, run_dir)
        row = {
            "type": "question",
            "page": url,
            "run_id": report.run_id,
            "question_id": q.question_id,
            "test": q.test_id.value,
            "images": len(images),
            "image_bytes": sum(len(b) for _, b in images),
            "text_chars": len(text),
        }
        if dry:
            write(row)
            return None
        async with sem:
            out = await call(system, text, images, schema(q), model)
        totals["calls"] += 1
        totals["seconds_in_calls"] += out.get("seconds") or 0
        for k in (
            "input_tokens",
            "output_tokens",
            "cache_read_input_tokens",
            "cache_creation_input_tokens",
        ):
            totals[k] += int((out.get("usage") or {}).get(k) or 0)
        totals["cost_usd"] += float(out.get("cost_usd") or 0)
        ans = to_answer(q, out, model) if out["ok"] else None
        if ans is None:
            totals["failed_calls"] += 1
        row.update(
            answered_by=f"server:{model}",
            prompt_sha256=prompt_sha(),
            parameters={
                "route": "cli",
                "temperature": "CLI default (not settable)",
                "schema": "choices enum + reasons, seen, quote, fields",
            },
            seconds=out.get("seconds"),
            usage=out.get("usage"),
            model_usage=out.get("model_usage"),
            model_reported=out.get("model_reported"),
            tools=out.get("tools"),
            ok=out["ok"],
            error=out.get("error"),
            structured=out.get("structured"),
            answer=ans.model_dump() if ans else None,
        )
        write(row)
        return ans

    for url, (_, run_id) in SOURCES.items():
        run_dir = runs / run_id
        tried: set[str] = set()
        rounds = 0
        page = per_page.setdefault(url, {"run_id": run_id, "questions": 0, "rounds": 0})
        while True:
            run = RunRecorder.open(runs, run_id)
            report = Report.model_validate_json(run.report_path.read_text("utf-8"))
            states = P._load_states(run)
            todo = [q for q in report.open_questions if q.question_id not in tried]
            if not todo:
                break
            rounds += 1
            tried |= {q.question_id for q in todo}
            page["questions"] += len(todo)
            answers = await asyncio.gather(
                *[one(report, states, q, run_dir, url) for q in todo]
            )
            got = [a for a in answers if a is not None]
            if dry or not got:
                break
            res = await P.answer_questions(settings, run_id, got)
            totals["answered"] += len(res.accepted)
            totals["rejected"] += len(res.rejected)
            totals["unsure"] += sum(
                1
                for a in got
                if a.choice
                and a.choice.choice == "unsure"
                and a.question_id in res.accepted
            )
            write(
                {
                    "type": "answers_applied",
                    "page": url,
                    "run_id": run_id,
                    "round": rounds,
                    "accepted": res.accepted,
                    "rejected": res.rejected,
                    "errors": res.errors,
                }
            )
        page["rounds"] = rounds
        if not dry:
            report = Report.model_validate_json(
                (run_dir / "report.json").read_text("utf-8")
            )
            page["left_open"] = len(report.open_questions)
            totals["left_open"] += len(report.open_questions)
    log.close()
    summary = {
        "arm": "c",
        "route": "cli",
        "model_requested": model,
        "prompt_file": str(PROMPT_FILE.relative_to(Path.cwd())),
        "prompt_sha256": prompt_sha(),
        "dry": dry,
        "pages": list(SOURCES),
        "per_page": per_page,
        "concurrency": CONCURRENCY,
        "slice_px": SLICE,
        "wall_s": round(time.monotonic() - t0, 1),
        **totals,
        "finished_at": _now(),
    }
    if not dry:
        (arm / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["prepare", "dry", "run"])
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--model", default=MODEL)
    a = ap.parse_args(argv)
    if a.action == "prepare":
        prepare(a.paths[0], a.paths[1])
        return
    s = asyncio.run(run(a.paths[0], a.model, a.action == "dry"))
    print(json.dumps({k: v for k, v in s.items() if k != "per_page"}, indent=1))
    print(json.dumps(s["per_page"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
