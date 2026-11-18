"""Experiment (not part of step 9c's tally): round 1's pages tested again on a
refreeze made 2026-11-18 into `gate-2026-11-17-9c/round1-refrozen/`, beside the
formal 9c run on the original freeze (2026-11-04).

    uv run python evals/judging/gate-2026-11-17-9c-refrozen/compare.py

Pages are in two groups: SAME (p01 p04 p07 p08 p09: the text inside `<main>` is
identical in both freezes; the site's header and footer and its asset names
changed) and CHANGED (p02 p03 p05 p06: the page's own content differs too).
Writes `compare.json` and `compare.md`. Verdicts are the round scorer's own;
nothing here decides an outcome. Agent-assisted results, not certified Trusted
Tester results.
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
_spec = importlib.util.spec_from_file_location(
    "c9", JUD / "gate-2026-11-17-9c" / "compare.py"
)
c9 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c9)

GROUPS = {
    "same main content": ["p01", "p04", "p07", "p08", "p09"],
    "changed content": ["p02", "p03", "p05", "p06"],
}


def main() -> None:
    res = HERE / "round1" / "r1" / "results"
    dirs = sorted(p for p in res.iterdir() if (p / "report.json").is_file())
    new = c9.g16.side(dirs, c9.KEYS[1])
    old = json.loads((JUD / "gate-2026-11-17-9c" / "compare-round1.json").read_text())[
        "sides"
    ]["real"]
    oldmap = {(r["page"], r["test"]): r for r in old if r["verdict"] != "not_scored"}
    out = {
        "note": "Agent-assisted results, not certified Trusted Tester results.",
        "groups": {},
        "sides": {"refrozen": new, "formal": old},
    }
    lines = [
        "# Round 1 on the refreeze, beside the formal 9c run",
        "",
        "Experiment; not part of step 9c's tally. Agent-assisted results, not certified Trusted Tester results.",  # noqa: E501
        "",
    ]
    for name, pages in GROUPS.items():
        rows = [r for r in new if r["page"] in pages and r["verdict"] != "not_scored"]
        now = c9.per_test(rows)
        then = c9.per_test([oldmap[(r["page"], r["test"])] for r in rows])
        diffs = []
        for r in rows:
            o = oldmap[(r["page"], r["test"])]
            if (o["tool"], o["verdict"]) != (r["tool"], r["verdict"]):
                diffs.append(
                    {
                        "page": r["page"],
                        "test": r["test"],
                        "key": r["key"],
                        "formal": o["tool"],
                        "formal_verdict": o["verdict"],
                        "refrozen": r["tool"],
                        "refrozen_verdict": r["verdict"],
                        "key_agrees": "yes"
                        if r["verdict"] == "agree"
                        else "left for a person"
                        if r["verdict"] in c9.LEFT
                        else "no",
                        "rows_formal": o["rows"],
                        "rows_refrozen": r["rows"],
                    }
                )
        tot = lambda m: sum((c for c in m.values()), Counter())  # noqa: E731
        out["groups"][name] = {
            "pages": pages,
            "cells": len(rows),
            "same_cells": len(rows) - len(diffs),
            "differ": diffs,
        }
        lines += [
            f"## {name}: {', '.join(pages)} ({len(rows)} keyed cells, {len(rows) - len(diffs)} the same, {len(diffs)} differ)",  # noqa: E501
            "",
            "Totals (agree / PASS or DNA where the key fails / FAIL or DNA where the key passes / other / left): "  # noqa: E501
            f"refrozen {c9.fmt(tot(now))}; formal {c9.fmt(tot(then))}",
            "",
            "| Page | Test | Key | Formal (original freeze) | Refrozen | Key |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for d in diffs:
            lines.append(
                f"| {d['page']} | {d['test']} | {d['key']} | {d['formal'] or 'NEEDS REVIEW'} ({d['formal_verdict']}) | {d['refrozen'] or 'NEEDS REVIEW'} ({d['refrozen_verdict']}) | {d['key_agrees']} |"  # noqa: E501
            )
        lines.append("")
    (HERE / "compare.json").write_text(json.dumps(out, indent=1) + "\n")
    (HERE / "compare.md").write_text("\n".join(lines))
    for n, g in out["groups"].items():
        print(
            n,
            g["cells"],
            "cells,",
            g["same_cells"],
            "same,",
            len(g["differ"]),
            "differ",
        )


if __name__ == "__main__":
    main()
