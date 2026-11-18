"""Gate 2026-11-17-9c (roadmap step 9c): one round's real run, per cell and per
test, beside the earlier figures.

    uv run python evals/judging/gate-2026-11-17-9c/compare.py --round 1|2|3

Writes `compare-roundN.json` (same shape as gate-2026-11-16's: `sides.real` has
page, url, test, verdict, key, tool, judge_decided, cn, inside, rows for every
cell, scored by the round's own scorer and keys) and `compare-roundN.md`.

Baselines: round 1 and 2 against step 9b (gate-2026-11-16 `sides.real`); round 3
against the blind run (`round3/results`, locked, only read). The comparison
decides nothing: verdicts are the round scorer's own. Agent-assisted results,
not certified Trusted Tester results.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

JUD = REPO / "evals" / "judging"
KEYS = {1: JUD / "round1", 2: JUD / "round2-armc", 3: JUD / "round3"}
_spec = importlib.util.spec_from_file_location(
    "g16", JUD / "gate-2026-11-16" / "compare.py"
)
g16 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g16)

PASSING = {"Pass", "Does Not Apply"}
FAILING = {"Fail", "Does Not Apply"}
LEFT = {"needs_review", "not_performed"}


def bucket(c: dict) -> str:
    """The same five buckets as evals/status_table.py."""
    if c["verdict"] == "agree":
        return "agree"
    if c["verdict"] in LEFT:
        return "left"
    if c["key"] == "Fail" and c["tool"] in PASSING:
        return "key_fails"
    if c["key"] == "Pass" and c["tool"] in FAILING:
        return "key_passes"
    return "other"


def per_test(rows: list[dict]) -> dict[str, Counter]:
    out: dict[str, Counter] = {}
    for r in rows:
        if r["verdict"] == "not_scored":
            continue
        out.setdefault(r["test"], Counter())[bucket(r)] += 1
    return out


def fmt(n: Counter | None) -> str:
    if not n:
        return "-"
    return (
        f"{n['agree']} agree; {n['key_fails']} PASS/DNA vs key Fail; "
        f"{n['key_passes']} FAIL/DNA vs key Pass; {n['other']} other; "
        f"{n['left']} left"
    )


def main_round(rnd: int) -> None:
    gd = HERE / f"round{rnd}" / "r1" / "results"
    dirs = sorted(p for p in gd.iterdir() if (p / "report.json").is_file())
    keys = KEYS[rnd]
    real = g16.side(dirs, keys)
    if rnd == 3:
        base_name = "blind"
        base = g16.side(
            sorted(
                p
                for p in (JUD / "round3" / "results").iterdir()
                if (p / "report.json").is_file()
            ),
            keys,
        )
    else:
        base_name = "9b"
        base = json.loads(
            (JUD / "gate-2026-11-16" / f"compare-round{rnd}.json").read_text("utf-8")
        )["sides"]["real"]
    old = {(r["page"], r["test"]): r for r in base if r["verdict"] != "not_scored"}
    moved = []
    for r in real:
        if r["verdict"] == "not_scored":
            continue
        o = old.get((r["page"], r["test"]))
        if o and (o["tool"], o["verdict"]) != (r["tool"], r["verdict"]):
            moved.append(
                {
                    "page": r["page"],
                    "test": r["test"],
                    "key": r["key"],
                    f"{base_name}_tool": o["tool"],
                    f"{base_name}_verdict": o["verdict"],
                    "tool": r["tool"],
                    "verdict": r["verdict"],
                    "key_agrees": "yes"
                    if r["verdict"] == "agree"
                    else "left for a person"
                    if r["verdict"] in LEFT
                    else "no",
                    "judge_decided": r["judge_decided"],
                    "rows": r["rows"],
                }
            )
    reps = g16._reports(dirs)
    times = g16.times(reps)
    now, then = per_test(real), per_test(base)
    out = {
        "round": rnd,
        "note": "Agent-assisted results, not certified Trusted Tester results.",
        "baseline": base_name,
        "per_test": {
            t: {"now": dict(now[t]), base_name: dict(then.get(t, {}))}
            for t in sorted(now, key=g16._tests_key)
        },
        "moved": moved,
        "times": times,
        "sides": {"real": real, base_name: base},
    }
    (HERE / f"compare-round{rnd}.json").write_text(json.dumps(out, indent=1) + "\n")
    lines = [
        f"# Round {rnd}: gate 2026-11-17-9c beside {base_name}",
        "",
        "Agent-assisted results, not certified Trusted Tester results.",
        "",
        f"| Test | This run | {base_name} |",
        "| --- | --- | --- |",
    ]
    for t in out["per_test"]:
        lines.append(f"| {t} | {fmt(now[t])} | {fmt(then.get(t))} |")
    lines += [
        "",
        f"## Cells that moved since {base_name} ({len(moved)})",
        "",
        f"| Page | Test | Key | {base_name} | Now | Key agrees |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for m in moved:
        lines.append(
            f"| {m['page']} | {m['test']} | {m['key']} | "
            f"{m[base_name + '_tool'] or 'NEEDS REVIEW'} ({m[base_name + '_verdict']}) | "  # noqa: E501
            f"{m['tool'] or 'NEEDS REVIEW'} ({m['verdict']}) | {m['key_agrees']} |"
        )
    ran = {t: v["ran_out"] for t, v in times.items() if v["ran_out"]}
    lines += ["", f"## Ran out of its time budget: {ran or 'none'}", ""]
    (HERE / f"compare-round{rnd}.md").write_text("\n".join(lines))
    print(f"round {rnd}: {len(moved)} moved; ran out: {ran or 'none'}")


if __name__ == "__main__":
    if "--round" not in sys.argv:
        sys.exit(__doc__)
    main_round(int(sys.argv[sys.argv.index("--round") + 1]))
