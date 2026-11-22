"""Gate 2026-11-22-136b (#136 after its rerun: 4.A 1.18.0, a title that
rewords the name; 4.F 1.15.0, a trap going round): every 4.A and 4.F cell
that moved against gate 2026-11-21-136, round by round, beside the tester's
key and its comment, with the rows that decided each side.

    uv run python evals/judging/gate-2026-11-22-136b/compare.py

Both sides are scored with the round scorer's own functions (gate-2026-11-16's
`side()`, through gate-2026-11-17's helpers), as gate 2026-11-21-136 was. Also
lists any page loaded live. Agent-assisted results, not certified Trusted
Tester results.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
JUD = HERE.parent
BEFORE = JUD / "gate-2026-11-21-136"
TESTS = ["4.A", "4.F"]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


g17 = _load("g17", JUD / "gate-2026-11-17" / "compare.py")


def _side(results: Path, rnd: int) -> dict:
    return {
        (r["page"], r["test"]): r
        for r in g17.g16.side(g17._dirs(results), g17.KEYS[rnd])
        if r["test"] in TESTS
    }


def main() -> None:
    out: dict = {
        "note": "Agent-assisted results, not certified Trusted Tester results.",
        "rounds": {},
    }
    md = [f"# Moved cells, {HERE.name}, against {BEFORE.name}", "", out["note"], ""]
    for rnd in (3, 2, 1):
        new_dir = HERE / f"round{rnd}" / "r1" / "results"
        old_dir = BEFORE / f"round{rnd}" / "r1" / "results"
        if not new_dir.is_dir() or not old_dir.is_dir():
            continue
        new, old = _side(new_dir, rnd), _side(old_dir, rnd)
        new_rows, old_rows = g17._rows(new_dir), g17._rows(old_dir)
        notes = g17._comments(g17.KEYS[rnd])
        tally: dict[str, int] = {}
        for n in new.values():
            tally[n["verdict"]] = tally.get(n["verdict"], 0) + 1
        moved = []
        for k, n in sorted(new.items()):
            o = old.get(k)
            if o is None or (o["tool"], o["verdict"]) == (n["tool"], n["verdict"]):
                continue
            moved.append(
                {
                    "page": k[0],
                    "test": k[1],
                    "key": n["key"],
                    "comment": notes.get(k, ""),
                    "old": o["tool"],
                    "old_verdict": o["verdict"],
                    "old_rows": old_rows.get(k, []),
                    "new": n["tool"],
                    "new_verdict": n["verdict"],
                    "new_rows": new_rows.get(k, []),
                }
            )
        live = g17._live(new_dir)
        out["rounds"][rnd] = {"tally": tally, "moved": moved, "live": live}
        md += [
            f"## Round {rnd}",
            "",
            f"Loaded live: {'; '.join(live) or 'none (every page from the freeze)'}",
            "",
            "4.A and 4.F now: "
            + ", ".join(f"{v} {c}" for v, c in sorted(tally.items())),
            "",
        ]
        if not moved:
            md += ["No cell moved.", ""]
            continue
        md += [
            "| Page | Test | Key | Key's comment | Before (verdict, rows) "
            "| Now (verdict, rows) |",
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
