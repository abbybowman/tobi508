"""Tables from one or more labelled passes of the tool selection eval.

    uv run python -m evals.tool_selection.report OUT before after > report.md

Several labels are shown side by side (before / after a description change).
Every run is scored again here from its saved events with the current
scorer, as committed (cases.toml) and with corrections.toml applied.
"""

from __future__ import annotations

import json
import sys
import tomllib
import zipfile
from collections import defaultdict
from pathlib import Path

from evals.tool_selection import score
from evals.tool_selection.run import HERE, load_cases


def corrections() -> dict[str, dict]:
    f = HERE / "corrections.toml"
    rows = tomllib.loads(f.read_text("utf-8")).get("correction", [])
    return {c["id"]: c for c in rows}


def _events(base: Path, name: str) -> str:
    """A run's events: its folder after a pass, or the committed runs.zip
    (the agent's messages and calls, tool results cut to 500 characters
    and the final result: what scoring reads)."""
    f = base / "runs" / name / "events.jsonl"
    if f.is_file():
        return f.read_text("utf-8")
    with zipfile.ZipFile(base / "runs.zip") as z:
        return z.read(f"{name}/events.jsonl").decode("utf-8")


def load(out: Path, label: str, corrected: bool = True) -> list[dict]:
    """The label's runs, scored again from their events."""
    cases = {c["id"]: c for c in load_cases()}
    if corrected:
        for cid, c in corrections().items():
            cases[cid] = cases[cid] | {"expect": c["expect"]}
    base = out / label
    schemas = {}
    rows = []
    for x in (base / "results.jsonl").read_text().splitlines():
        r = json.loads(x)
        mode = r["mode"]
        if mode not in schemas:
            tools = json.loads((base / f"tools-{mode}.json").read_text())
            schemas[mode] = {t["name"]: t["inputSchema"] for t in tools}
        name = f"{r['case']}__{mode}__{r['model']}__{r['repeat']}"
        events = [json.loads(e) for e in _events(base, name).splitlines() if e]
        c = cases[r["case"]]
        rows.append(r | score.score_run(c, events, schemas[mode])
                    | {"expect": c["expect"]["tool"]})  # fmt: skip
    return rows


def short_model(m: str) -> str:
    return m.replace("claude-", "").replace("-5-5", " 5.5").capitalize()


def frac(rows: list[dict], key: str = "passed") -> str:
    vals = [r[key] for r in rows if r[key] is not None]
    if not vals:
        return "n/a"
    n = sum(bool(v) for v in vals)
    return f"{n}/{len(vals)} ({100 * n / len(vals):.0f}%)"


def combos(rows):
    return sorted({(r["mode"], r["model"]) for r in rows}, key=lambda x: (x[1], x[0]))


def report(out: Path, labels: list[str]) -> str:
    data = {lb: load(out, lb) for lb in labels}
    raw = {lb: load(out, lb, corrected=False) for lb in labels}
    allrows = [r for rows in data.values() for r in rows]
    cs = combos(allrows)
    models = sorted({m for _, m in cs})
    fixed = ", ".join(corrections()) or "none"
    L: list[str] = []
    L.append(
        "## Overall: runs scored correct\n\n"
        "First call: the first TOBI call is the right tool (or rightly none), "
        "valid against its inputSchema, with the required arguments, and the "
        "final message has the caveat where asked. As committed: cases.toml "
        f"as written before any run. Corrected: corrections.toml applied ({fixed}). "
        "Anywhere: the expected call made at any point (valid, required "
        "arguments), no forbidden call (corrected).\n"
    )
    heads = [
        f"{lb}: {k}"
        for lb in labels
        for k in ("first call, as committed", "first call, corrected", "anywhere")
    ]
    L.append("| Model | Judge mode | " + " | ".join(heads) + " |")
    L.append("| --- | --- |" + " --- |" * len(heads))

    def row_cells(pick) -> list[str]:
        out_ = []
        for lb in labels:
            out_ += [frac(pick(raw[lb])), frac(pick(data[lb])),
                     frac(pick(data[lb]), "anywhere")]  # fmt: skip
        return out_

    for mode, model in cs:
        cells = row_cells(
            lambda rows, mode=mode, model=model: [
                r for r in rows if (r["mode"], r["model"]) == (mode, model)
            ]
        )
        L.append(f"| {short_model(model)} | {mode} | " + " | ".join(cells) + " |")
    for model in models:
        cells = row_cells(
            lambda rows, model=model: [r for r in rows if r["model"] == model]
        )
        L.append(f"| {short_model(model)} | both | " + " | ".join(cells) + " |")

    L.append("\n## By check (all models and modes; corrected)\n")
    L.append("| Check | " + " | ".join(labels) + " |")
    L.append("| --- |" + " --- |" * len(labels))
    checks = (
        ("tool_ok", "right tool (or rightly none)"),
        ("valid", "arguments valid against inputSchema"),
        ("args_ok", "required arguments present (right tool only)"),
        ("text_ok", "caveat in the final message (where asked)"),
    )
    for key, name in checks:
        L.append(
            f"| {name} | " + " | ".join(frac(data[lb], key) for lb in labels) + " |"
        )

    L.append("\n## By expected tool (first call, corrected; all modes)\n")
    hdr = [f"{short_model(m)} {lb}" for m in models for lb in labels]
    L.append("| Expected | " + " | ".join(hdr) + " |")
    L.append("| --- |" + " --- |" * len(hdr))
    for tool in sorted({r["expect"] for r in allrows}):
        cells = [frac([r for r in data[lb] if r["model"] == m and r["expect"] == tool])
                 for m in models for lb in labels]  # fmt: skip
        L.append(f"| {tool} | " + " | ".join(cells) + " |")

    L.append(
        "\n## By case (first call, corrected; correct runs of 3; "
        + " → ".join(labels)
        + ")\n"
    )
    L.append(
        "| Case | Expected | "
        + " | ".join(f"{short_model(m)} {mo}" for mo, m in cs)
        + " |"
    )
    L.append("| --- | --- |" + " --- |" * len(cs))
    by = defaultdict(list)
    for lb in labels:
        for r in data[lb]:
            by[(r["case"], r["mode"], r["model"], lb)].append(r)
    cases = list(dict.fromkeys(r["case"] for r in allrows))
    expect = {r["case"]: r["expect"] for r in allrows}
    for c in cases:
        cells = []
        for mode, model in cs:
            parts = []
            for lb in labels:
                rs = by.get((c, mode, model, lb), [])
                parts.append(f"{sum(r['passed'] for r in rs)}/{len(rs)}" if rs else "–")
            cells.append(" → ".join(parts))
        L.append(f"| {c} | {expect[c]} | " + " | ".join(cells) + " |")

    for lb in labels:
        bad = [r for r in data[lb] if not r["passed"]]
        L.append(f"\n## Failed runs, {lb} ({len(bad)})\n")
        for r in sorted(
            bad, key=lambda r: (r["case"], r["model"], r["mode"], r["repeat"])
        ):
            who = (
                f"{r['case']} / {short_model(r['model'])} / {r['mode']} #{r['repeat']}"
            )
            did = f"called {r['calls'] or 'nothing'}; " + "; ".join(r["notes"][:4])
            L.append(f"- {who}: {did}")

    L.append("\n## Cost (list price, from the CLI's result events)\n")
    L.append("| Pass | Runs | Cost $ | Runs without a result |")
    L.append("| --- | --- | --- | --- |")
    for lb in labels:
        rows = data[lb]
        cost = sum(r["cost_usd_list_price"] or 0 for r in rows)
        L.append(f"| {lb} | {len(rows)} | {cost:.2f} | "
                 f"{sum(1 for r in rows if r['ended'] == 'no result')} |")  # fmt: skip
    return "\n".join(L) + "\n"


def main(argv: list[str]) -> None:
    print(report(Path(argv[0]), argv[1:]), end="")


if __name__ == "__main__":
    main(sys.argv[1:])
