"""Gate 2026-11-14 (roadmap step 9a): one round's real run beside its dry run,
step 6 (round 2) and the round's locked rows, per TT test; the dry-vs-real
difference on cells no judge answer decided; guard CN; test times.

    uv run python evals/judging/gate-2026-11-14/compare.py --round 1|2
    uv run python evals/judging/gate-2026-11-14/compare.py --combined

`--round N` writes `compare-roundN.json` and `.md` beside this file.
`--combined` reads both rounds' `gate.json` and writes `combined.md`: each
question type over both rounds' judge-decided cells against "The gate"'s
thresholds, and every test that ran out of its budget with the longest time
each test took.

Verdicts come from the round scorer's own functions (`evals.scoring.score` on
`tobi508.compare.compare`, with the round's adjudications), as in
`gate-2026-11-13/compare.py`, whose `side()` this reuses with the keys folder
as a parameter. Agent-assisted results, not certified Trusted Tester results.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

JUD = REPO / "evals" / "judging"
KEYS = {1: JUD / "round1", 2: JUD / "round2-armc"}

_spec = importlib.util.spec_from_file_location(
    "gate0", JUD / "gate-2026-11-13" / "compare.py"
)
g0 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g0)  # step 6's helpers, unchanged

from evals.scoring import decided_tests  # noqa: E402


def side(run_dirs: list[Path], keys_dir: Path, merged_pre=None) -> list[dict]:
    """`g0.side` with the keys folder given (round 1 or 2)."""
    g0.KEYS = keys_dir
    return g0.side(run_dirs, merged_pre)


def _reports(dirs: list[Path]) -> dict[str, dict]:
    """page id (pNN) -> report, for a results/ or dry/ folder."""
    return {
        d.name: json.loads((d / "report.json").read_text("utf-8"))
        for d in sorted(dirs)
        if (d / "report.json").is_file()
    }


def _finding(rep: dict, test: str) -> dict | None:
    return next((f for f in rep["findings"] if f["test_id"] == test), None)


def _decided(rep: dict) -> dict[str, bool]:
    return decided_tests(g0._Rep(rep))


def dry_vs_real(real: dict[str, dict], dry: dict[str, dict]) -> dict:
    """Every cell no judge answer decided in the real run, set against the dry
    run's: outcome, rows, ran out of time, and time (a difference over 50% and
    over 10 s). The dry run had no judge, so a cell a judge answer decided is
    not compared."""
    diffs, same, skipped = [], 0, 0
    for pid, rr in sorted(real.items()):
        dr = dry.get(pid)
        if dr is None:
            continue
        dec = _decided(rr)
        for f in rr["findings"]:
            t = f["test_id"]
            if dec.get(t):
                skipped += 1
                continue
            g = _finding(dr, t)
            tt_r, tt_d = rr["test_times"].get(t, {}), dr["test_times"].get(t, {})
            what = []
            if g is None:
                what.append("not in the dry run")
            else:
                if g["outcome"] != f["outcome"]:
                    what.append(f"outcome {g['outcome']} -> {f['outcome']}")
                if g.get("rows") != f.get("rows"):
                    what.append(f"rows {g.get('rows')} -> {f.get('rows')}")
                if g["summary"] != f["summary"] and not what:
                    what.append("summary only")
            if tt_r.get("ran_out") != tt_d.get("ran_out"):
                what.append(f"ran out {tt_d.get('ran_out')} -> {tt_r.get('ran_out')}")
            sr, sd = tt_r.get("seconds"), tt_d.get("seconds")
            if (
                sr is not None
                and sd is not None
                and abs(sr - sd) > max(10.0, 0.5 * max(sr, sd))
            ):
                what.append(f"seconds {sd} -> {sr}")
            if what:
                diffs.append({"page": pid, "test": t, "what": what})
            else:
                same += 1
    return {
        "same": same,
        "differ": len(diffs),
        "judge_decided_skipped": skipped,
        "cells": diffs,
    }


def times(real: dict[str, dict]) -> dict:
    """Per test over the round's pages: the longest time taken and every page
    where it ran out of its budget."""
    out: dict[str, dict] = {}
    for pid, rep in real.items():
        for t, tt in rep["test_times"].items():
            row = out.setdefault(
                t,
                {
                    "budget_s": tt["budget_s"],
                    "max_s": 0.0,
                    "max_page": "",
                    "ran_out": [],
                },
            )
            if tt["seconds"] > row["max_s"]:
                row["max_s"], row["max_page"] = tt["seconds"], pid
            if tt["ran_out"]:
                row["ran_out"].append(pid)
    return out


def _tests_key(x: str):
    return [int(p) if p.isdigit() else p for p in x.replace(".", " ").split()]


def main_round(rnd: int) -> None:
    from evals.agent.score import tool_files

    gd = HERE / f"round{rnd}"
    keys = KEYS[rnd]
    real_dirs = sorted((gd / "r1" / "results").glob("p*"))
    dry_dirs = sorted((gd / "dry").glob("p*"))
    sides = {"real": side(real_dirs, keys), "dry": side(dry_dirs, keys)}
    if rnd == 2:
        s6 = JUD / "gate-2026-11-13" / "r1" / "results"
        sides["step6"] = side(sorted(s6.glob("p*")), keys)
        for a in (1, 2, 3):
            arm = keys / "results" / f"arm-c-{a}"
            sides[f"round2-c{a}"] = side(
                sorted((arm / "runs").glob("*")), keys, tool_files(arm)
            )
    else:
        for a in (1, 2, 3):
            arm = keys / "results" / f"arm-a-{a}"
            if (arm / "runs").is_dir():
                sides[f"round1-a{a}"] = side(
                    sorted((arm / "runs").glob("*")), keys, tool_files(arm)
                )
    tally = {
        n: {w or "all": g0.tally(rows, w) for w in (None, "judge", "rule")}
        for n, rows in sides.items()
    }
    real = _reports(real_dirs)
    dry = _reports(dry_dirs)
    out = {
        "round": rnd,
        "note": "Agent-assisted results, not certified Trusted Tester results.",
        "tally": tally,
        "dry_vs_real": dry_vs_real(real, dry),
        "times": times(real),
    }
    moved = []
    if rnd == 2:
        old = {(r["page"], r["test"]): r for r in sides["step6"]}
        for r in sides["real"]:
            o = old.get((r["page"], r["test"]))
            if o and o["verdict"] == "needs_review" and r["verdict"] != "needs_review":
                moved.append(
                    {
                        "page": r["page"],
                        "test": r["test"],
                        "key": r["key"],
                        "tool": r["tool"],
                        "verdict": r["verdict"],
                        "judge_decided": r["judge_decided"],
                        "rows": r["rows"],
                    }
                )
    out["moved_from_needs_review"] = moved
    cn = [r for r in sides["real"] if r["cn"]]
    out["cn"] = {
        "cells": len(cn),
        "key_fail": [
            {"page": r["page"], "test": r["test"], "key": r["key"], "tool": r["tool"]}
            for r in cn
            if str(r["key"]).lower().startswith("fail")
        ],
        "all": [
            {
                "page": r["page"],
                "test": r["test"],
                "key": r["key"],
                "verdict": r["verdict"],
            }
            for r in cn
        ],
    }
    out["sides"] = sides
    (HERE / f"compare-round{rnd}.json").write_text(g0._dump(out))
    (HERE / f"compare-round{rnd}.md").write_text(markdown(out))
    print(json.dumps({n: t["all"].get("all") for n, t in tally.items()}, indent=1))
    print("dry vs real:", {k: v for k, v in out["dry_vs_real"].items() if k != "cells"})


def markdown(out: dict) -> str:
    t = out["tally"]
    names = list(t)
    lines = [f"# Gate 2026-11-14, round {out['round']}", "", out["note"], ""]
    for who, title in (
        ("all", "All cells"),
        ("judge", "Judge-decided cells"),
        ("rule", "Rule-decided cells"),
    ):
        lines += [f"## {title}", "", g0.HEAD]
        lines += [g0._line(n, t[n][who].get("all")) for n in names]
        lines.append("")
    tests = sorted(
        {k for n in names for k in t[n]["all"] if k != "all"}, key=_tests_key
    )
    lines += [
        "## Per TT test (all cells; judge/rule in brackets)",
        "",
        "| Test | Run | Scored | False PASS | Missed fail | False FAIL "
        "| Needs review (CN) | Agree | Judge cells |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for test in tests:
        for n in names:
            a = t[n]["all"].get(test)
            if not a:
                continue
            j = t[n]["judge"].get(test) or dict.fromkeys(g0.COLS, 0)
            r = t[n]["rule"].get(test) or dict.fromkeys(g0.COLS, 0)
            pair = lambda c: f"{a[c]} ({j[c]}/{r[c]})"  # noqa: E731
            lines.append(
                f"| {test} | {n} | {a['cells'] - a['not_scored']} | "
                f"{pair('false_pass')} | {pair('missed_fail')} | "
                f"{pair('false_fail')} | {a['needs_review']} "
                f"({a['needs_review_cn']}) | {pair('agree')} | "
                f"{j['cells'] - j['not_scored']} |"
            )
    real = out["sides"]["real"]
    wrong = [
        r
        for r in real
        if r["verdict"]
        in ("false_pass", "missed_fail", "false_fail", "fail_vs_dna", "other")
    ]
    lines += [
        "",
        "## Real run: every wrong cell",
        "",
        "| Page | Test | Key | Tool | Verdict | Judge | Rows |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines += [
        f"| {r['page']} | {r['test']} | {r['key']} | {r['tool']} | {r['verdict']} | "
        f"{'yes' if r['judge_decided'] else 'no'} | {g0._short(r)} |"
        for r in wrong
    ]
    if out["round"] == 2:
        m = out["moved_from_needs_review"]
        lines += [
            "",
            f"## Moved from NEEDS REVIEW (step 6) to an outcome: {len(m)}",
            "",
            "| Page | Test | Key | Tool | Verdict | Judge | Rows |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        lines += [
            f"| {r['page']} | {r['test']} | {r['key']} | {r['tool']} | "
            f"{r['verdict']} | {'yes' if r['judge_decided'] else 'no'} | "
            f"{' '.join(r['rows'])} |"
            for r in m
        ]
    cn = out["cn"]
    lines += [
        "",
        f"## Guard CN cells: {cn['cells']}; key Fail among them: {len(cn['key_fail'])}",
        "",
        "| Page | Test | Key | Verdict |",
        "| --- | --- | --- | --- |",
    ]
    lines += [
        f"| {r['page']} | {r['test']} | {r['key']} | {r['verdict']} |"
        for r in cn["all"]
    ]
    d = out["dry_vs_real"]
    lines += [
        "",
        "## Dry run against real run, cells no judge answer decided",
        "",
        f"Same: {d['same']}. Differ: {d['differ']}. Skipped (a judge answer "
        f"decided them): {d['judge_decided_skipped']}.",
        "",
        "| Page | Test | What differed |",
        "| --- | --- | --- |",
    ]
    lines += [
        f"| {c['page']} | {c['test']} | {'; '.join(c['what'])} |" for c in d["cells"]
    ]
    lines += [
        "",
        "## Test times (real run): longest, and where a test ran out",
        "",
        "| Test | Budget s | Longest s | Page | Ran out on |",
        "| --- | --- | --- | --- | --- |",
    ]
    for k in sorted(out["times"], key=_tests_key):
        v = out["times"][k]
        lines.append(
            f"| {k} | {v['budget_s']} | {v['max_s']} | {v['max_page']} | "
            f"{', '.join(v['ran_out']) or '-'} |"
        )
    return "\n".join(lines) + "\n"


def combined() -> None:
    from evals.apijudge_gate import MIN_DECIDED_CELLS, passes
    from evals.scoring import decided_cells

    rounds = {
        n: json.loads((HERE / f"round{n}" / "gate.json").read_text()) for n in (1, 2)
    }
    keep = (
        "cells",
        "agree",
        "wrong_pass",
        "wrong_dna",
        "wrong_fail",
        "pass_vs_dna",
        "unsure",
        "other",
    )
    cells: dict[str, dict[str, int]] = {}
    fails: dict[str, list[int]] = {}
    for n in (1, 2):
        for test, v in rounds[n]["types"].items():
            tot = cells.setdefault(test, dict.fromkeys(keep, 0))
            for k in keep:
                tot[k] += v[k]
            fails.setdefault(test, []).append(v["wrong_fail"])
    res = passes(cells, fails, None)  # the test-page half is run apart
    lines = [
        "# Gate 2026-11-14, both rounds together (one repeat each)",
        "",
        "Each question type over both rounds' judge-decided cells, read against "
        "The gate's thresholds: zero wrong PASS, zero wrong DOES NOT APPLY, at "
        "most 1 wrong FAIL per round and 20% of decided cells, at least "
        f"{MIN_DECIDED_CELLS} decided cells. The test-page half is not here.",
        "",
        "| Type | Cells | Decided | Agree | Wrong PASS | Wrong DNA | Wrong FAIL "
        "| PASS vs key DNA | Unsure | Real-page half |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for test in sorted(res, key=_tests_key):
        v = res[test]
        why = [w for w in v["why_not"] if "test pages" not in w]
        lines.append(
            f"| {test} | {v['cells']} | {decided_cells(v)} | {v['agree']} | "
            f"{v['wrong_pass']} | {v['wrong_dna']} | {v['wrong_fail']} | "
            f"{v['pass_vs_dna']} | {v['unsure']} | "
            f"{'meets' if not why else '; '.join(why)} |"
        )
    tm: dict[str, dict] = {}
    for n in (1, 2):
        cmp = json.loads((HERE / f"compare-round{n}.json").read_text())
        for t, v in cmp["times"].items():
            row = tm.setdefault(
                t, {"budget_s": v["budget_s"], "max_s": 0.0, "where": "", "ran_out": []}
            )
            if v["max_s"] > row["max_s"]:
                row["max_s"], row["where"] = v["max_s"], f"round {n} {v['max_page']}"
            row["ran_out"] += [f"r{n} {p}" for p in v["ran_out"]]
    lines += [
        "",
        "## Test times over both rounds",
        "",
        "| Test | Budget s | Longest s | Where | Ran out on |",
        "| --- | --- | --- | --- | --- |",
    ]
    for k in sorted(tm, key=_tests_key):
        v = tm[k]
        lines.append(
            f"| {k} | {v['budget_s']} | {v['max_s']} | {v['where']} | "
            f"{', '.join(v['ran_out']) or '-'} |"
        )
    (HERE / "combined.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--combined"]:
        combined()
    elif a[:1] == ["--round"]:
        main_round(int(a[1]))
    else:
        sys.exit(__doc__)
