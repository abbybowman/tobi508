"""Gate 2026-11-20-134 (#134: steps 24, 25, 26, 35a, 35e and guard WL):
every cell that moved, round by round, against gate 2026-11-17-9c's real run
(`compare-roundN.json`, `sides.real`), beside the tester's key and its
comment, with the rows that decided each side.

    uv run python evals/judging/gate-2026-11-20-134/compare.py

Verdicts come from the round scorer's own functions (gate-2026-11-16's
`side()`), as gate 9c's were. Also lists any page loaded live. Gate 9c ran
"tested_frozen" (19.A's search and suggested pages live); this rerun ran
"replay" (every page from the freeze), so 19.A cells can move by the mode
alone. Agent-assisted results, not certified Trusted Tester results.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
JUD = HERE.parent
TESTS = "4.A,4.B,4.C,4.E,4.F,5.A,5.B,5.C,5.D,5.F,9.A,9.B,9.C,19.A".split(",")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


g17 = _load("g17", JUD / "gate-2026-11-17" / "compare.py")


def main() -> None:
    out: dict = {
        "note": "Agent-assisted results, not certified Trusted Tester results.",
        "rounds": {},
    }
    md = [
        f"# Moved cells, {HERE.name}, against gate 2026-11-17-9c",
        "",
        out["note"],
        "",
    ]
    for rnd in (3, 2, 1):
        new_dir = HERE / f"round{rnd}" / "r1" / "results"
        if not new_dir.is_dir():
            continue
        new = {
            (r["page"], r["test"]): r
            for r in g17.g16.side(g17._dirs(new_dir), g17.KEYS[rnd])
        }
        sides = json.loads(
            (JUD / "gate-2026-11-17-9c" / f"compare-round{rnd}.json").read_text()
        )
        old = {(r["page"], r["test"]): r for r in sides["sides"]["real"]}
        new_rows = g17._rows(new_dir)
        notes = g17._comments(g17.KEYS[rnd])
        moved = []
        for k, n in sorted(new.items()):
            if k[1] not in TESTS or k not in old:
                continue
            o = old[k]
            if (o["tool"], o["verdict"]) == (n["tool"], n["verdict"]):
                continue
            moved.append(
                {
                    "page": k[0],
                    "test": k[1],
                    "key": n["key"],
                    "comment": notes.get(k, ""),
                    "old": o["tool"],
                    "old_verdict": o["verdict"],
                    "old_rows": o.get("rows", []),
                    "new": n["tool"],
                    "new_verdict": n["verdict"],
                    "new_rows": new_rows.get(k, []),
                    "judge_decided": n.get("judge_decided"),
                }
            )
        pages = sorted({k[0] for k in new})
        live = g17._live(new_dir)
        out["rounds"][rnd] = {"pages": pages, "moved": moved, "live": live}
        md += [
            f"## Round {rnd} ({len(pages)} pages)",
            "",
            f"Loaded live: {'; '.join(live) or 'none (every page from the freeze)'}",
            "",
        ]
        if not moved:
            md += ["No cell moved.", ""]
            continue
        md += [
            "| Page | Test | Key | Key's comment | 9c (verdict, rows) | Now (verdict, rows) |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for m in moved:
            c = m["comment"].replace("|", "/").replace("\n", " ")[:140]
            was = f"{m['old']} ({m['old_verdict']}; {' '.join(m['old_rows'][:8])})"
            now = f"{m['new']} ({m['new_verdict']}; {' '.join(m['new_rows'][:8])})"
            md.append(
                f"| {m['page']} | {m['test']} | {m['key']} | {c} | {was} | {now} |"
            )
        md.append("")
    (HERE / "moved.json").write_text(json.dumps(out, indent=1))
    (HERE / "moved.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
