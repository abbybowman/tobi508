"""Agent C for round 2: TOBI's open questions answered the way the planned
server judge (ApiJudge) would answer them, on round 2's frozen pages (Abby,
2026-11-08; docs/research/2026-11-07-visual-judgment-and-apijudge.md section
5, and the server judge pivot plan of 2026-11-07). A stand-in: claude.ai's
Sonnet 5.5 through the Claude Code CLI, not NASA's in-house endpoint.

    uv run python -m evals.agent.judge_c prepare <round2> <armc>
    uv run python -m evals.agent.judge_c fresh <round2> <armc>
    uv run python -m evals.agent.judge_c dry <armc>               # no model
    uv run python -m evals.agent.judge_c run <armc> --label 1     # arm-c-1

First round (`<armc>/first-round/runs/`): for each page, an Agent A tool run
that no agent answered, copied whole with its evidence; for the pages whose
every Agent A run was answered (14592, 5144, 4914), a fresh TOBI run on the
same frozen copy, with the other page Agent A's paired run used (Abby,
2026-11-08). Each repeat copies the first round into `results/arm-c-N/` and
answers it there, so every repeat starts from the same state.

One model call per question: a fixed system prompt (judge_c_prompt.md, its
SHA-256 recorded), the question, rubric, choices, input and shared inputs
in one block labelled untrusted page data, and every picture the input
names attached at native resolution (tall ones in slices). No tools, no
URLs, no files. Structured output: the question's choices as an enum, plus
reasons, quote and seen. A call that fails (timeout, error, no structured
output) is tried once more; a second failure leaves the question open. An
"unsure" answer is never retried. A page's J0 (gate) questions are answered
and applied before its others. Answers go through
pipeline.answer_questions (record_answers and every guard), with
answered_by "server:<model>", so outcomes come only from the specs; new
questions are answered the same way until none is open. Then the follow-up
calls the server may make (19.A's suggested pages, live, as finish=true makes
them) are made and their questions answered too.

C's result per WCAG criterion is rolled up from its tool files by the
scorer's own functions (tool_files, rollup), so it relays the tool exactly.

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
# recorded (steps.jsonl has no answers_recorded).
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
# Pages with no unanswered Agent A run: a fresh TOBI run each, with the
# other page of Agent A's paired run.
FRESH = {
    "https://svs.gsfc.nasa.gov/14592/": ["https://svs.gsfc.nasa.gov/cilab/"],
    "https://svs.gsfc.nasa.gov/5144/": ["https://svs.gsfc.nasa.gov/4914/"],
    "https://svs.gsfc.nasa.gov/4914/": ["https://svs.gsfc.nasa.gov/5144/"],
}
# Pictures taller than this go in native-resolution slices: the API scales
# an image whose long edge passes about 1568 px down (assumed for Sonnet 5.5
# from the documented limit; not measured here).
SLICE = 1400
CONCURRENCY = 3
CALL_TIMEOUT_S = 300
TRIES = 2  # a failed call is tried once more; an answer is never retried
FIELDS = ("element", "elements", "key", "duration_ms", "presses", "quote", "value")
WORD = {"Pass": "PASS", "Fail": "FAIL", "Does Not Apply": "DNA"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prompt_sha() -> str:
    return hashlib.sha256(PROMPT_FILE.read_bytes()).hexdigest()


def _no_keys(*rds: Path) -> None:
    for rd in rds:
        k = rd / "keys"
        if k.exists() and any(k.iterdir()):
            sys.exit(f"{k} holds answer keys: arm C must finish before the reveal")


def _settings(runs: Path, frozen: Path | None = None, model: str = MODEL):
    from tobi508.config import Settings

    kw: dict[str, Any] = {
        "runs_dir": runs,
        "browser_channel": "chromium",
        "headless": True,
        "run_ttl_hours": 720,
        "judging_model": f"server:{model} prompt:{prompt_sha()[:12]}",
    }
    if frozen is not None:
        # As Agent A's server: the tested page only from the frozen copy;
        # other pages of its site, and 19.A's search, live (Abby, 2026-11-04).
        kw |= {"frozen_pages_dir": frozen, "frozen_pages_mode": "tested_frozen"}
    if os.environ.get("UPSTREAM_PROXY"):
        kw["upstream_proxy"] = os.environ["UPSTREAM_PROXY"]
    return Settings(**kw)


# ── first round ──────────────────────────────────────────────────────────────
def prepare(src: Path, out: Path) -> None:
    """Round 2's page list and frozen index, and each source run (whole,
    with its evidence), into `out`. Refuses if keys exist."""
    _no_keys(src, out)
    runs = out / "first-round" / "runs"
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
        rows.append({"page": url, "run_id": run_id, "from": f"round2/{where}"})
    _sources(out, rows)


def _sources(out: Path, rows: list[dict]) -> None:
    f = out / "first-round" / "sources.json"
    old = json.loads(f.read_text()) if f.exists() else []
    f.write_text(json.dumps(old + rows, indent=1) + "\n")


async def fresh(src: Path, out: Path) -> None:
    """A fresh TOBI run of each FRESH page on round 2's frozen copy."""
    from tobi508 import pipeline as P
    from tobi508.checks import REGISTRY

    _no_keys(src, out)
    runs = (out / "first-round" / "runs").resolve()
    settings = _settings(runs, (src / "frozen").resolve())
    rows = []
    for url, others in FRESH.items():
        t0 = time.monotonic()
        res = await P.run_tt_tests(settings, url, list(REGISTRY), other_pages=others)
        rows.append(
            {
                "page": url,
                "run_id": res.run_id,
                "from": "fresh TOBI run on round2/frozen (tested_frozen)",
                "other_pages": others,
                "seconds": round(time.monotonic() - t0, 1),
                "open_questions": len(res.report.open_questions),
            }
        )
        print(rows[-1], flush=True)
    _sources(out, rows)


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
            more = (
                f" (part {i} of {len(parts)}, top to bottom)" if len(parts) > 1 else ""
            )
            images.append((link + more, b))
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


# ── one call (the Claude Code CLI route, as arms A and B) ────────────────────
async def call(system: str, text: str, images, sch: dict, model: str) -> dict:
    from evals.agent.cli import DROP

    content: list[dict] = [{"type": "text", "text": text}]
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
            return {"ok": False, "error": "timeout", "seconds": CALL_TIMEOUT_S}
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


def to_answer(q, s: dict, model: str):
    """The model's structured output as an Answer, or None when it does not
    fit the question (the question is left open)."""
    from tobi508.models import Answer, ChoiceAnswer

    if s.get("choice") not in q.choices:
        return None
    extra = {k: s[k] for k in FIELDS if s.get(k) not in (None, "", [])}
    reasons = (s.get("reasons") or "").strip()
    try:
        return Answer(
            question_id=q.question_id,
            choice=ChoiceAnswer(choice=s["choice"], reasons=reasons[:500], **extra),
            rationale=reasons[:1000] or s["choice"],
            seen=(s.get("seen") or "")[:300],
            picture_error=(s.get("picture_error") or "")[:300],
            answered_by=f"server:{model}",
        )
    except Exception:
        return None


# ── a repeat ─────────────────────────────────────────────────────────────────
def _gate_first(qs: list) -> list:
    """A page's J0 questions alone when it has any (their answers can make
    the rest moot, e.g. 5.F's 'any errors?' for 5.F-5.H), else all."""
    gates = [q for q in qs if q.question_id.endswith("-J0")]
    return gates or qs


async def run(rd: Path, label: str, model: str, dry: bool) -> dict:
    from tobi508 import pipeline as P
    from tobi508.models import Report, TestId
    from tobi508.runlog import RunRecorder

    _no_keys(rd, rd.parent / "round2")
    if (rd / "results" / "lock.json").exists():
        sys.exit("This round is locked")
    first = (rd / "first-round" / "runs").resolve()
    sources = json.loads((rd / "first-round" / "sources.json").read_text())
    arm = (rd / "results" / f"arm-c-{label}").resolve()
    if dry:
        runs = first
    else:
        if arm.exists() and any(arm.iterdir()):
            sys.exit(f"{arm} is not empty: this repeat already ran")
        runs = arm / "runs"
        shutil.copytree(first, runs)
    frozen = (rd.parent / "round2" / "frozen").resolve()
    settings = _settings(runs, frozen, model)
    system = PROMPT_FILE.read_text("utf-8")
    log_path = (rd / "first-round" / "dry-steps.jsonl") if dry else arm / "steps.jsonl"
    log = log_path.open("w")
    sem = asyncio.Semaphore(CONCURRENCY)
    totals: dict[str, Any] = dict.fromkeys(
        (
            "questions",
            "calls",
            "retried_calls",
            "failed_calls",
            "answered",
            "unsure",
            "rejected",
            "left_open",
            "picture_questions",
            "text_questions",
            "follow_up_runs",
            "input_tokens",
            "output_tokens",
            "cache_read_input_tokens",
            "cache_creation_input_tokens",
        ),
        0,
    ) | {"seconds_in_calls": 0.0, "cost_usd": 0.0}
    per_page: dict[str, dict] = {}
    t0 = time.monotonic()

    def write(row):
        log.write(json.dumps({"ts": _now(), **row}, default=str) + "\n")
        log.flush()

    async def one(report, states, q, run_dir, url):
        text, images = build(report, states, q, run_dir)
        row: dict[str, Any] = {
            "type": "question",
            "page": url,
            "run_id": report.run_id,
            "question_id": q.question_id,
            "test": q.test_id.value,
            "picture_question": bool(images),
            "images": len(images),
            "image_bytes": sum(len(b) for _, b in images),
            "text_chars": len(text),
        }
        totals["questions"] += 1
        totals["picture_questions" if images else "text_questions"] += 1
        if dry:
            write(row)
            return None
        attempts = []
        for _ in range(TRIES):
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
            attempts.append(
                {
                    k: out.get(k)
                    for k in (
                        "ok",
                        "error",
                        "seconds",
                        "usage",
                        "model_usage",
                        "model_reported",
                        "tools",
                        "structured",
                    )
                }
            )
            if out["ok"]:
                break
        if len(attempts) > 1:
            totals["retried_calls"] += 1
        last = attempts[-1]
        ans = to_answer(q, last["structured"], model) if last["ok"] else None
        if ans is None:
            totals["failed_calls"] += 1
        row.update(
            answered_by=f"server:{model}",
            prompt_sha256=prompt_sha(),
            parameters={
                "route": "cli",
                "temperature": "CLI default (not settable)",
                "schema": "choices enum; reasons, seen, picture_error, quote, fields",
                "slice_px": SLICE,
            },
            attempts=attempts,
            answer=ans.model_dump() if ans else None,
        )
        write(row)
        return ans

    async def answer_run(run_id: str, url: str) -> None:
        page = per_page.setdefault(url, {"runs": [], "questions": 0, "rounds": 0})
        page["runs"].append(run_id)
        tried: set[str] = set()
        while True:
            run = RunRecorder.open(runs, run_id)
            report = Report.model_validate_json(run.report_path.read_text("utf-8"))
            states = P._load_states(run)
            todo = _gate_first(
                [q for q in report.open_questions if q.question_id not in tried]
            )
            if not todo:
                break
            page["rounds"] += 1
            page["questions"] += len(todo)
            tried |= {q.question_id for q in todo}
            got = await asyncio.gather(
                *[one(report, states, q, runs / run_id, url) for q in todo]
            )
            got = [a for a in got if a is not None]
            if dry:
                continue
            if not got:
                continue
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
                    "accepted": res.accepted,
                    "rejected": [r.model_dump() for r in res.rejected],
                    "errors": res.errors,
                }
            )

    for src in sources:
        await answer_run(src["run_id"], src["page"])
        if dry:
            continue
        # The follow-up calls the server may make (19.A's suggested pages,
        # live), as tobi_run_status with finish=true makes them.
        run = RunRecorder.open(runs, src["run_id"])
        report = Report.model_validate_json(run.report_path.read_text("utf-8"))
        mine = [c for c in report.follow_up_calls if P.server_may_make(c)]
        report.follow_up_calls = [
            c for c in report.follow_up_calls if not P.server_may_make(c)
        ]
        run.write_json(run.report_path, report)
        for c in mine:
            tests = [TestId(t) for t in c["tests"]]
            try:
                res = await P.run_tt_tests(
                    settings,
                    c["url"],
                    tests,
                    no_time_limit=settings.no_time_limit_default,
                    other_pages=list(c.get("other_pages") or []),
                )
            except Exception as exc:
                write(
                    {
                        "type": "follow_up_error",
                        "page": src["page"],
                        "error": str(exc)[:300],
                    }
                )
                continue
            P.record_follow_up(settings, src["run_id"], c, f"armc-{res.run_id}")
            totals["follow_up_runs"] += 1
            write(
                {
                    "type": "follow_up",
                    "page": src["page"],
                    "run_id": res.run_id,
                    "tests": c["tests"],
                    "other_pages": c.get("other_pages"),
                }
            )
            await answer_run(res.run_id, src["page"])
    log.close()
    if not dry:
        for url, page in per_page.items():
            left = 0
            for rid in page["runs"]:
                r = json.loads((runs / rid / "report.json").read_text())
                left += len(r["open_questions"])
            page["left_open"] = left
            totals["left_open"] += left
    summary = {
        "arm": "c",
        "label": label,
        "route": "cli",
        "model_requested": model,
        "answered_by": f"server:{model}",
        "prompt_file": "evals/agent/judge_c_prompt.md",
        "prompt_sha256": prompt_sha(),
        "temperature": "CLI default (not settable on this route)",
        "dry": dry,
        "pages": [s["page"] for s in sources],
        "first_round": sources,
        "per_page": per_page,
        "concurrency": CONCURRENCY,
        "slice_px": SLICE,
        "tries_per_call": TRIES,
        "wall_s": round(time.monotonic() - t0, 1),
        "ended": "completed",
        "finished_at": _now(),
        **totals,
        "tokens": {
            k: totals[k]
            for k in (
                "input_tokens",
                "output_tokens",
                "cache_read_input_tokens",
                "cache_creation_input_tokens",
            )
        },
        "cost_usd_list_price": round(totals["cost_usd"], 4),
    }
    if not dry:
        (arm / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
        (arm / "final.md").write_text(final_md(arm), "utf-8")
    return summary


def final_md(arm: Path) -> str:
    """C's result per WCAG criterion: its tool files rolled up by the
    scorer's own functions (score.tool_files, scoring.rollup), so it relays
    the tool exactly. A FAIL lists the failing rows' comments."""
    from evals.agent.prompt import criteria
    from evals.agent.score import tool_files
    from evals.scoring import rollup
    from tobi508.compare import summary as tt_summary
    from tobi508.scrt import ScrtResult

    out: dict[str, dict] = {}
    for page, pre in tool_files(arm).items():
        rows = pre.results()
        per: dict[str, dict] = {}
        for c in criteria():
            got = rollup(
                [tt_summary(rows[t]) if t in rows else None for t in c["tests"]]
            )
            word = WORD.get(got.value, "NEEDS_REVIEW") if got else "NEEDS_REVIEW"
            els: list[str] = []
            if word == "FAIL":
                for t in c["tests"]:
                    for r in rows.get(t, []):
                        if r.TestResult is ScrtResult.FAIL:
                            els.append(f"{t}: {(r.TesterComment or '')[:160]}")
            per[c["id"]] = {"result": word, "elements": els[:10]}
        out["https://" + page] = per  # the scorer matches pages by page_key
    return (
        "Agent C (stand-in for the server judge): TOBI's results with its open "
        "questions answered by the server-side model, rolled up per criterion "
        "by code. Agent-assisted results, not a certified Trusted Tester "
        "result.\n\nRESULT: " + json.dumps(out) + "\n"
    )


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["prepare", "fresh", "dry", "run"])
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--label", default="1")
    a = ap.parse_args(argv)
    if a.action == "prepare":
        prepare(a.paths[0], a.paths[1])
        return
    if a.action == "fresh":
        asyncio.run(fresh(a.paths[0], a.paths[1]))
        return
    s = asyncio.run(run(a.paths[0], a.label, a.model, a.action == "dry"))
    print(
        json.dumps(
            {k: v for k, v in s.items() if k not in ("per_page", "first_round")},
            indent=1,
        )
    )
    print(json.dumps(s["per_page"], indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
