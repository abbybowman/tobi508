"""Does Agent A finish the workflow? Behaviour counts for one or more arm
runs, from the tool's own run folders and the CLI transcript (never from
the agent's own account of what it did).

    uv run python -m evals.agent.followthrough evals/judging/<folder>/results/arm-a-*

Per arm run:
- questions asked, answered, unsure and left open (the report's own record,
  as evals/judging/compare-2026-11-19-r3/compare.py counts them), and who
  answered (the agent, or the server's judge);
- picture answers: the agent's answers to questions whose input names a
  run:// picture, and how many of those pictures it opened with the MCP
  resource reader before the call that sent the answer (pictures attached
  to a result are counted apart: the transcript cannot show whether the
  agent looked at one);
- tobi_explain calls, tobi_run_status calls with finish=true and with no
  job_id, and reads of a run's report or pre-SCRT link (the closest the
  harness's agent can come to saving them: it has no file-writing tool);
- with the server's judge: questions the judge answered unsure, how many of
  them the agent answered anyway, and whether the final message says some
  findings need a person.

Agent-assisted results, not certified Trusted Tester results.
"""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

PIC = re.compile(r"run://[^\"\s]+?\.(?:png|jpe?g)")
PERSON = re.compile(
    r"\b(a person|a human|manual(ly)?|human review|needs? review)\b", re.I
)


def _short(name: str) -> str:
    return name.rsplit("__", 1)[-1]


def _choice(a: dict) -> str | None:
    c = a.get("choice")
    return c.get("choice") if isinstance(c, dict) else c


def transcript(arm: Path, zip_path: Path | None = None) -> list[dict]:
    f = arm / "transcript.json"
    if f.is_file():
        return json.loads(f.read_text("utf-8"))
    if zip_path is not None:
        with zipfile.ZipFile(zip_path) as z:
            return json.loads(z.read(f"{arm.name}/transcript.json"))
    raise FileNotFoundError(f)


def reports(arm: Path) -> list[dict]:
    return [
        json.loads(p.read_text("utf-8"))
        for p in sorted((arm / "runs").glob("*/report.json"))
    ]


def stats(arm: Path, zip_path: Path | None = None) -> dict:
    reps = reports(arm)
    pics: dict[str, set[str]] = {}  # question_id -> pictures its input names
    asked = answered = unsure = left = 0
    by: dict[str, int] = {}
    judge_unsure: set[str] = set()
    for rep in reps:
        latest = {}
        for a in rep.get("answers", []):
            latest[a["answer"]["question_id"]] = a["answer"]
        for q in rep.get("questions", []):
            qid = q["question_id"]
            found = set(PIC.findall(json.dumps(q.get("input"))))
            if found:
                pics.setdefault(qid, set()).update(found)
            asked += 1
            a = latest.get(qid)
            if a is None:
                left += 1
                continue
            who = a.get("answered_by", "client")
            by[who] = by.get(who, 0) + 1
            if _choice(a) == "unsure":
                unsure += 1
                if who.startswith("server"):
                    judge_unsure.add(qid)
            else:
                answered += 1

    read: set[str] = set()
    pic_answers = pic_opened = 0
    explain = finish = status_all = report_reads = attached = 0
    agent_answered: set[str] = set()
    calls: dict[str, int] = {}
    for ev in transcript(arm, zip_path):
        content = (ev.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_result" and isinstance(b.get("content"), list):
                attached += sum(
                    1
                    for y in b["content"]
                    if isinstance(y, dict) and y.get("type") == "image"
                )
            if b.get("type") != "tool_use":
                continue
            name, inp = _short(b.get("name") or ""), b.get("input") or {}
            calls[name] = calls.get(name, 0) + 1
            if name == "ReadMcpResourceTool":
                uri = str(inp.get("uri") or "")
                read.add(uri)
                report_reads += uri.endswith(("report.json", "pre-scrt.json"))
            elif name == "tobi_explain":
                explain += 1
            elif name == "tobi_run_status":
                finish += inp.get("finish") is True
                status_all += not inp.get("job_id")
            elif name == "tobi_answer_questions":
                for a in inp.get("answers") or []:
                    qid = a.get("question_id") if isinstance(a, dict) else None
                    if not qid:
                        continue
                    agent_answered.add(qid)
                    if qid in pics:
                        pic_answers += 1
                        pic_opened += bool(pics[qid] & read)
    final = (arm / "final.md").read_text("utf-8") if (arm / "final.md").exists() else ""
    return {
        "arm": arm.name,
        "pages": len({r["target"] for r in reps}),
        "tool_runs": len(reps),
        "asked": asked,
        "answered": answered,
        "unsure": unsure,
        "left_open": left,
        "answered_by": by,
        "picture_answers_by_agent": pic_answers,
        "picture_opened_before_answer": pic_opened,
        "pictures_attached_to_results": attached,
        "picture_reads": sum(1 for u in read if PIC.fullmatch(u)),
        "tobi_explain_calls": explain,
        "finish_true_calls": finish,
        "run_status_without_job_id": status_all,
        "report_or_pre_scrt_reads": report_reads,
        "judge_unsure": len(judge_unsure),
        "judge_unsure_answered_by_agent": len(judge_unsure & agent_answered),
        "final_says_a_person_checks": bool(PERSON.search(final)) if final else None,
        "tool_calls": calls,
    }


def main(argv: list[str]) -> None:
    zip_path = None
    if argv and argv[0].startswith("--zip="):
        zip_path = Path(argv.pop(0).split("=", 1)[1])
    print(json.dumps([stats(Path(a), zip_path) for a in argv], indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
