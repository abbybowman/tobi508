"""This gate run beside round 2's locked arm C rows, per TT test, judge-decided
cells apart from rule-decided ones (roadmap step 6).

    uv run python evals/judging/gate-2026-11-13/compare.py

Neutral on outcomes: every verdict comes from the round 2 scorer's own
functions (`evals.scoring.score` on `tobi508.compare.compare`, with the
round's adjudications), unchanged since round 2's lock commit e14580a. A cell
is judge-decided when an answer of the server's judge is in force for one of
its test's questions in the run that gave the cell (`scoring.decided_tests`);
round 2's arm C answers are recorded the same way (`server:claude-sonnet-5-5`).
A cell is "guard CN" when its finding's rows include `CN`.

Writes compare.json and compare.md beside this file. Reads the keys, never
copies them. Agent-assisted results, not certified Trusted Tester results.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from evals import judging  # noqa: E402
from evals.scoring import Verdict, adjudications, decided_tests  # noqa: E402
from evals.scoring import score as score_page  # noqa: E402
from tobi508 import scrt  # noqa: E402
from tobi508.compare import compare, page_key  # noqa: E402

KEYS = REPO / "evals" / "judging" / "round2-armc"
# A NEEDS REVIEW finding whose summary gives a frame or a web component as
# what was not read (roadmap step 8 aims at these). Tight on purpose: 4.A's
# fixed sentence "including inside frames" and 3.A's "frame-by-frame" do not
# count.
INSIDE = re.compile(
    r"inside (?:a )?frames?\b|(?:fields?|form fields?|buttons?\(s\)) inside "
    r"(?:a )?frames?|embedded frame we could not read|web component|shadow root",
    re.I,
)
COLS = (
    "cells",
    "agree",
    "false_pass",
    "missed_fail",
    "false_fail",
    "fail_vs_dna",
    "other",
    "needs_review",
    "needs_review_cn",
    "not_scored",
)
WORD = {
    Verdict.AGREE: "agree",
    Verdict.VALIDATED_CATCH: "agree",
    Verdict.FALSE_PASS: "false_pass",
    Verdict.MISSED_FAIL: "missed_fail",
    Verdict.FALSE_FAIL: "false_fail",
    Verdict.FAIL_NOT_APPLICABLE: "fail_vs_dna",
    Verdict.OTHER: "other",
    Verdict.NEEDS_REVIEW: "needs_review",
    Verdict.NOT_PERFORMED: "needs_review",
    Verdict.NOT_SCORED: "not_scored",
}


def _runs(run_dirs: list[Path]):
    """Per page key: [(finished_at, tests, report, pre-scrt path)], oldest first."""
    out: dict[str, list] = {}
    for d in run_dirs:
        rep, pre = d / "report.json", d / "pre-scrt.json"
        if not (rep.is_file() and pre.is_file()):
            continue
        r = json.loads(rep.read_text("utf-8"))
        k = page_key(r.get("target"))
        out.setdefault(k, []).append((r.get("finished_at") or "", r["tests"], r, pre))
    for v in out.values():
        v.sort(key=lambda x: x[0])
    return out


def _cell_source(runs, test):
    """The latest run of the page whose tests included `test` (as
    evals.agent.score.tool_files merges a page's runs)."""
    got = None
    for item in runs:
        if test in item[1]:
            got = item
    return got


def side(run_dirs: list[Path], merged_pre: dict | None = None) -> list[dict]:
    """One row per (page, TT test) the keys score."""

    listed = judging.parse_pages((KEYS / "pages.txt").read_text("utf-8"))
    keys = judging.read_keys(KEYS, listed)
    adj = adjudications(KEYS)
    runs = _runs(run_dirs)
    rows = []
    for n, (url, _) in enumerate(listed, 1):
        k = page_key(url)
        key = keys.get(url)
        if key is None or k not in runs:
            continue
        pre = (merged_pre or {}).get(k) or scrt.parse(runs[k][-1][3].read_text("utf-8"))
        sc = score_page(compare(key[1], pre), adj.get(k))
        for t in sc.tests:
            tid = t.test.test_id
            src = _cell_source(runs[k], tid)
            decided = bool(src and decided_tests(_Rep(src[2])).get(tid))
            finding = next(
                (f for f in (src[2]["findings"] if src else []) if f["test_id"] == tid),
                None,
            )
            rows.append(
                {
                    "page": f"p{n:02d}",
                    "url": url,
                    "test": tid,
                    "verdict": WORD.get(t.verdict, "other"),
                    "key": t.test.first.result.value if t.test.first.result else None,
                    "tool": t.test.second.result.value
                    if t.test.second.result
                    else None,
                    "judge_decided": decided,
                    "cn": bool(finding and "CN" in finding.get("rows", [])),
                    "inside": bool(
                        finding
                        and INSIDE.search(
                            finding["summary"].replace("including inside frames", "")
                        )
                    ),
                    # the rule's own rows; per-instance rows (`k1:M6`) counted
                    "rows": [
                        x for x in (finding or {}).get("rows", []) if ":" not in x
                    ],
                    "instance_rows": sum(
                        1 for x in (finding or {}).get("rows", []) if ":" in x
                    ),
                }
            )
    return rows


class _Rep:
    """decided_tests reads report.answers[].answer.{question_id,answered_by}."""

    def __init__(self, r: dict):
        class A:
            def __init__(self, a):
                self.question_id = a["question_id"]
                self.answered_by = a["answered_by"]

        class R:
            def __init__(self, a):
                self.answer = A(a["answer"])

        self.answers = [R(a) for a in r.get("answers", [])]


def tally(rows: list[dict], who: str | None = None) -> dict[str, dict[str, int]]:
    """Per test and "all": counts by verdict. who: None (every cell),
    "judge" or "rule"."""
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        if who == "judge" and not r["judge_decided"]:
            continue
        if who == "rule" and r["judge_decided"]:
            continue
        for t in (r["test"], "all"):
            row = out.setdefault(t, dict.fromkeys(COLS, 0))
            row["cells"] += 1
            row[r["verdict"]] += 1
            if r["verdict"] == "needs_review" and r["cn"]:
                row["needs_review_cn"] += 1
    return out


def _line(name: str, row: dict | None) -> str:
    if not row:
        return f"| {name} | 0 | | | | | | | | |"
    scored = row["cells"] - row["not_scored"]
    decided = scored - row["needs_review"]
    return (
        f"| {name} | {scored} | {row['false_pass']} | {row['missed_fail']} | "
        f"{row['false_fail']} | {row['fail_vs_dna']} | {row['other']} | "
        f"{row['needs_review']} ({row['needs_review_cn']} CN) | "
        f"{row['agree']}/{decided} |"
    )


HEAD = (
    "| Run | Scored | False PASS | Missed fail (DNA) | False FAIL | Fail vs DNA "
    "| Other | Needs review (guard CN) | Agree (of decided) |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
)


def _short(r: dict) -> str:
    n = r["instance_rows"]
    return " ".join(r["rows"]) + (f" (+{n} instance rows)" if n else "")


def markdown(out: dict) -> str:
    t = out["tally"]
    names = list(t)
    lines = [
        "# Gate 2026-11-13 beside round 2 (arm C), per TT test",
        "",
        out["note"],
        "",
        f"Scorer: {out['scorer']}. Agree counts validated catches. "
        "Judge-decided: an answer of the server's judge is in force for one of "
        "the test's questions in the run that gave the cell.",
        "",
    ]
    for who, title in (
        ("all", "All cells"),
        ("judge", "Judge-decided cells"),
        ("rule", "Rule-decided cells"),
    ):
        lines += [f"## {title}", "", HEAD]
        for n in names:
            lines.append(_line(n, t[n][who].get("all")))
        lines.append("")
    tests = sorted(
        {k for n in names for k in t[n]["all"] if k != "all"},
        key=lambda x: [
            int(p) if p.isdigit() else p for p in x.replace(".", " ").split()
        ],
    )
    lines += [
        "## Per TT test (all cells; judge-decided / rule-decided in brackets)",
        "",
    ]
    lines += [
        "| Test | Run | Scored | False PASS | Missed fail | False FAIL "
        "| Needs review (CN) | Agree | Judge-decided cells |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for test in tests:
        for n in names:
            a = t[n]["all"].get(test)
            j = t[n]["judge"].get(test) or dict.fromkeys(COLS, 0)
            r = t[n]["rule"].get(test) or dict.fromkeys(COLS, 0)
            if not a:
                continue
            scored = a["cells"] - a["not_scored"]
            pair = lambda c: f"{a[c]} ({j[c]}/{r[c]})"  # noqa: E731
            lines.append(
                f"| {test} | {n} | {scored} | {pair('false_pass')} | "
                f"{pair('missed_fail')} | {pair('false_fail')} | "
                f"{a['needs_review']} ({a['needs_review_cn']}) | {pair('agree')} | "
                f"{j['cells'] - j['not_scored']} |"
            )
    gate = out["sides"][names[0]]
    wrong = [
        r
        for r in gate
        if r["verdict"]
        in ("false_pass", "missed_fail", "false_fail", "fail_vs_dna", "other")
    ]
    lines += [
        "",
        f"## {names[0]}: every wrong cell",
        "",
        "| Page | Test | Key | Tool | Verdict | Judge-decided | Rows |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in wrong:
        lines.append(
            f"| {r['page']} | {r['test']} | {r['key']} | {r['tool']} | "
            f"{r['verdict']} | "
            f"{'yes' if r['judge_decided'] else 'no'} | {_short(r)} |"
        )
    nr = [r for r in gate if r["verdict"] == "needs_review"]
    sel = [r for r in nr if r["inside"]]
    lines += [
        "",
        f"## {names[0]}: NEEDS REVIEW cells inside a frame or a web component: "
        f"{len(sel)}",
        "",
        "| Page | Test | Key | Guard CN | Judge-decided |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in sel:
        lines.append(
            f"| {r['page']} | {r['test']} | {r['key']} | "
            f"{'yes' if r['cn'] else 'no'} | {'yes' if r['judge_decided'] else 'no'} |"
        )
    for cn, title in (
        (True, "made by guard CN (row CN)"),
        (False, "for any other reason"),
    ):
        sel = [r for r in nr if r["cn"] is cn]
        lines += [
            "",
            f"## {names[0]}: NEEDS REVIEW cells {title}: {len(sel)}",
            "",
            "| Page | Test | Key | Judge-decided | Rows |",
            "| --- | --- | --- | --- | --- |",
        ]
        for r in sel:
            lines.append(
                f"| {r['page']} | {r['test']} | {r['key']} | "
                f"{'yes' if r['judge_decided'] else 'no'} | {_short(r)} |"
            )
    return "\n".join(lines) + "\n"


def _dump(out: dict) -> str:
    """JSON with one cell per line, so the file diffs and reads by row."""
    head = {k: v for k, v in out.items() if k != "sides"}
    body = json.dumps(head, indent=1)[:-2]
    sides = []
    for name, rows in out["sides"].items():
        cells = ",\n".join("   " + json.dumps(r) for r in rows)
        sides.append(f"  {json.dumps(name)}: [\n{cells}\n  ]")
    return body + ',\n "sides": {\n' + ",\n".join(sides) + "\n }\n}\n"


def main() -> None:
    from evals.agent.score import tool_files

    gate = side(sorted((HERE / "r1" / "results").glob("p*")))
    r2 = {}
    for a in (1, 2, 3):
        arm = KEYS / "results" / f"arm-c-{a}"
        r2[f"round2-c{a}"] = side(sorted((arm / "runs").glob("*")), tool_files(arm))
    out = {
        "note": "Agent-assisted results, not certified Trusted Tester results.",
        "scorer": "evals.scoring.score on tobi508.compare.compare, "
        "round 2 adjudications",
        "sides": {"gate-2026-11-13": gate, **r2},
        "tally": {
            name: {w or "all": tally(rows, w) for w in (None, "judge", "rule")}
            for name, rows in {"gate-2026-11-13": gate, **r2}.items()
        },
    }
    (HERE / "compare.json").write_text(_dump(out))
    (HERE / "compare.md").write_text(markdown(out))
    print(
        json.dumps({n: t["all"].get("all") for n, t in out["tally"].items()}, indent=1)
    )


if __name__ == "__main__":
    main()
