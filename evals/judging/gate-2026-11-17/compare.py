"""Gate 2026-11-17 (steps 21, 36, 22, then 23): every cell that moved, round by
round, against the last run of the same tests (round 1 and 2: step 9b's
gate-2026-11-16 `sides.real`; round 3: the locked blind run's reports), beside
the tester's key and its comment, with the rows that decided each side.

    uv run python evals/judging/gate-2026-11-17/compare.py [--run r1] [--out NAME]

Verdicts come from the round scorer's own functions (gate-2026-11-16's
`side()`, which is `evals.scoring.score` on `tobi508.compare.compare` with the
round's adjudications). Also checks that every page and other page was served
from the freeze (`live_pages`, `frozen_pages`). Agent-assisted results, not
certified Trusted Tester results.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

from evals import judging  # noqa: E402
from tobi508.compare import compare  # noqa: E402

JUD = REPO / "evals" / "judging"
KEYS = {1: JUD / "round1", 2: JUD / "round2-armc", 3: JUD / "round3"}
# The first rerun's tests (steps 21, 36, 22). A rerun with --new and --old
# compares these with the old gate and the rest (step 23's 4.B, 9.A-9.C and
# 19.A) with the baseline below.
FIRST = [
    "4.A",
    "4.C",
    "4.D",
    "4.E",
    "4.F",
    "5.A",
    "5.B",
    "5.C",
    "5.D",
    "5.F",
    "5.G",
    "5.H",
]
TESTS = FIRST + ["4.B", "9.A", "9.B", "9.C", "19.A"]

_spec = importlib.util.spec_from_file_location(
    "g16", JUD / "gate-2026-11-16" / "compare.py"
)
g16 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g16)


def _dirs(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if (p / "report.json").is_file())


def _comments(keys_dir: Path) -> dict[tuple[str, str], str]:
    listed = judging.parse_pages((keys_dir / "pages.txt").read_text("utf-8"))
    keys = judging.read_keys(keys_dir, listed)
    out = {}
    for n, (url, _) in enumerate(listed, 1):
        k = keys.get(url)
        if k is None:
            continue
        for t in compare(k[1], k[1]).tests:
            out[(f"p{n:02d}", t.test_id)] = t.first.comment or ""
    return out


def _rows(folder: Path) -> dict[tuple[str, str], list[str]]:
    out = {}
    for d in _dirs(folder):
        r = json.loads((d / "report.json").read_text("utf-8"))
        for f in r["findings"]:
            out[(d.name, f["test_id"])] = f.get("rows", [])
    return out


def _live(folder: Path) -> list[str]:
    bad = []
    for d in _dirs(folder):
        r = json.loads((d / "report.json").read_text("utf-8"))
        if r.get("live_pages"):
            bad.append(f"{d.name}: {r['live_pages']}")
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="r1")
    ap.add_argument("--out", default="moved")
    ap.add_argument("--new", default="", help="gate folder to read (default: this)")
    ap.add_argument("--old", default="", help="gate folder for FIRST's old side")
    a = ap.parse_args()
    new_gate = JUD / a.new if a.new else HERE
    out_dir = new_gate
    # The first rerun ran FIRST only; a later gate (--new) ran TESTS.
    tests = TESTS if a.new else FIRST
    out: dict = {
        "note": "Agent-assisted results, not certified Trusted Tester results.",
        "rounds": {},
    }
    md = [f"# Moved cells, {new_gate.name}", "", out["note"], ""]
    for rnd in (1, 2, 3):
        new_dir = new_gate / f"round{rnd}" / a.run / "results"
        if not new_dir.is_dir():
            continue
        new = {(r["page"], r["test"]): r for r in g16.side(_dirs(new_dir), KEYS[rnd])}
        if rnd == 3:
            old_dir = JUD / "round3" / "results"
            old = {(r["page"], r["test"]): r for r in g16.side(_dirs(old_dir), KEYS[3])}
            old_rows = _rows(old_dir)
        else:
            sides = json.loads(
                (JUD / "gate-2026-11-16" / f"compare-round{rnd}.json").read_text()
            )
            old = {(r["page"], r["test"]): r for r in sides["sides"]["real"]}
            old_rows = {k: v.get("rows", []) for k, v in old.items()}
        if a.old:
            prev_dir = JUD / a.old / f"round{rnd}" / a.run / "results"
            prev = g16.side(_dirs(prev_dir), KEYS[rnd])
            prev_rows = _rows(prev_dir)
            for r in prev:
                k = (r["page"], r["test"])
                if k[1] in FIRST:
                    old[k] = r
                    old_rows[k] = prev_rows.get(k, [])
        new_rows = _rows(new_dir)
        notes = _comments(KEYS[rnd])
        moved = []
        for k, n in sorted(new.items()):
            if k[1] not in tests or k not in old:
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
                    "old_rows": old_rows.get(k, []),
                    "new": n["tool"],
                    "new_verdict": n["verdict"],
                    "new_rows": new_rows.get(k, []),
                    "judge_decided": n.get("judge_decided"),
                }
            )
        pages = sorted({k[0] for k in new})
        out["rounds"][rnd] = {"pages": pages, "moved": moved, "live": _live(new_dir)}
        md += [f"## Round {rnd} ({len(pages)} pages run: {', '.join(pages)})", ""]
        live = "; ".join(_live(new_dir)) or "none (every page from the freeze)"
        md += [f"Loaded live: {live}", ""]
        if not moved:
            md += ["No cell moved.", ""]
            continue
        md += [
            "| Page | Test | Key | Key's comment "
            "| Old (verdict, rows) | New (verdict, rows) |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for m in moved:
            c = m["comment"].replace("|", "/").replace("\n", " ")[:160]
            was = f"{m['old']} ({m['old_verdict']}; {' '.join(m['old_rows'][:8])})"
            now = f"{m['new']} ({m['new_verdict']}; {' '.join(m['new_rows'][:8])})"
            md.append(
                f"| {m['page']} | {m['test']} | {m['key']} | {c} | {was} | {now} |"
            )
        md.append("")
    (out_dir / f"{a.out}.json").write_text(json.dumps(out, indent=1))
    (out_dir / f"{a.out}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
