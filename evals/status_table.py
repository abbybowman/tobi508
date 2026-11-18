"""The README's status table and evals/STATUS.md, from the latest scored
result of each site.

    uv run python evals/status_table.py            # print the table and counts
    uv run python evals/status_table.py --write    # README rows + evals/STATUS.md

Per test, over every site's keyed cells (a cell is one page and one test where
a Trusted Tester's blind key gives an answer), it counts: agree; PASS or DOES
NOT APPLY where the key fails; FAIL or DOES NOT APPLY where the key passes;
other mismatches (key DOES NOT APPLY or NOT TESTED against another outcome);
left for a person (NEEDS REVIEW, including "could not be performed"). One
rule, first match, gives the colour and the words (`status()`). The verdicts
are the round scorer's own (`evals.scoring`); nothing here decides an outcome.

"Agrees with a tester" is about our evaluation pages only. Agent-assisted
results, not certified Trusted Tester results.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

JUD = REPO / "evals" / "judging"
README = REPO / "README.md"
STATUS_MD = HERE / "STATUS.md"
START = "<!-- status-table:start -->"
END = "<!-- status-table:end -->"

# Each site's latest scored result. `base` gives every cell; `overlay` is a
# later rerun's `moved.json` (only the cells that differ from the base, for the
# tests that rerun covered). Point these at step 9c's results when it is merged.
# Later reruns' `moved.json`, oldest first: each lists the cells that differ from
# the run before it (step 23's file is against the first rerun for the tests
# that ran twice, against step 9b or the blind run for the rest).
OVERLAYS = [
    JUD / "gate-2026-11-17" / "moved.json",
    JUD / "gate-2026-11-17-step23" / "moved.json",
]

SITES = {
    1: {
        "site": "www.nasa.gov",
        "run": "rerun on development pages, gate 2026-11-17-9c (step 9c), "
        "the server judge on every type it can take, on the original freeze",
        "base": JUD / "gate-2026-11-17-9c" / "compare-round1.json",
        "overlay": [],
    },
    2: {
        "site": "svs.gsfc.nasa.gov",
        "run": "rerun on development pages, gates 2026-11-17 and "
        "2026-11-17-step23 over "
        "gate 2026-11-16 (step 9b)",
        "base": JUD / "gate-2026-11-16" / "compare-round2.json",
        "overlay": OVERLAYS,
    },
    3: {
        "site": "science.data.nasa.gov",
        "run": "rerun on development pages, gate 2026-11-17-9c (step 9c), "
        "the server judge on every type it can take (the blind round 3, "
        "locked 2026-11-16, stays the record in evals/judging/round3/score.md)",
        "base": JUD / "gate-2026-11-17-9c" / "compare-round3.json",
        "overlay": [],
    },
}

PASSING = {"Pass", "Does Not Apply"}
FAILING = {"Fail", "Does Not Apply"}
LEFT = {"needs_review", "not_performed"}
COLS = ("agree", "key_fails", "key_passes", "other", "left")


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _round3_cells() -> list[dict]:
    """The blind run's reports, scored by the round's own scorer."""
    g16 = _load(JUD / "gate-2026-11-16" / "compare.py", "g16")
    dirs = sorted(
        p
        for p in (JUD / "round3" / "results").iterdir()
        if (p / "report.json").is_file()
    )
    return g16.side(dirs, JUD / "round3")


def cells(rnd: int) -> dict[tuple[str, str], dict]:
    """(page, test) -> {key, tool, verdict} for keyed cells of one site."""
    src = SITES[rnd]
    if src["base"] is None:
        rows = _round3_cells()
    else:
        rows = json.loads(src["base"].read_text("utf-8"))["sides"]["real"]
    out = {
        (r["page"], r["test"]): {
            "key": r["key"],
            "tool": r["tool"],
            "verdict": r["verdict"],
        }
        for r in rows
        if r["verdict"] != "not_scored"
    }
    for overlay in src["overlay"]:
        moved = json.loads(overlay.read_text("utf-8"))["rounds"]
        for m in moved.get(str(rnd), {}).get("moved", []):
            out[(m["page"], m["test"])] = {
                "key": m["key"],
                "tool": m["new"],
                "verdict": m["new_verdict"],
            }
    return out


def bucket(c: dict) -> str:
    if c["verdict"] == "agree":
        return "agree"
    if c["verdict"] in LEFT:
        return "left"
    if c["key"] == "Fail" and c["tool"] in PASSING:
        return "key_fails"
    if c["key"] == "Pass" and c["tool"] in FAILING:
        return "key_passes"
    return "other"


def count(cs) -> Counter:
    return Counter(bucket(c) for c in cs)


def status(n: Counter) -> tuple[str, str]:
    """(colour, words): the one rule, first match."""
    total = sum(n[k] for k in COLS)
    wrong = n["key_fails"] + n["key_passes"] + n["other"]
    decided = n["agree"] + wrong
    if total == 0:
        return "grey", "no key on our pages"
    if n["key_fails"]:
        return "red", "passed a page a tester failed"
    if wrong > n["agree"]:
        return "red", "wrong more often than right"
    if wrong * 5 > decided:
        return "yellow", "often fails pages a tester passes"
    if decided * 2 < total:
        return "yellow", "mostly left for a person"
    return "green", "agrees with a tester"


# Colour plus a shape that differs from the others, so colour is never the
# only signal: red X, yellow caution triangle, green check box.
EMOJI = {"red": "❌", "yellow": "⚠️", "green": "✅", "grey": "➖"}


def compute() -> dict[str, dict[int, Counter]]:
    from tobi508 import rules
    from tobi508.models import TestId

    # Built tests: an approved spec (1.0.0 or later; 0.y.z is a draft).
    # tests/test_readme.py checks the list against checks.REGISTRY.
    specs = rules.load_specs(REPO / "specs" / "rules")
    tests = [
        t.value for t in TestId if t in specs and int(specs[t].spec_version[0]) >= 1
    ]
    per_site = {rnd: cells(rnd) for rnd in SITES}
    return {
        t: {
            rnd: count(c for (_, tt), c in per_site[rnd].items() if tt == t)
            for rnd in SITES
        }
        for t in tests
    }


def total(by_site: dict[int, Counter]) -> Counter:
    out: Counter = Counter()
    for n in by_site.values():
        out.update(n)
    return out


def readme_rows() -> list[str]:
    from tobi508 import catalog, rules
    from tobi508.models import TestId

    specs = rules.load_specs(REPO / "specs" / "rules")
    counts = compute()
    rows = ["| ID | TT test name | Spec | Status |", "| --- | --- | --- | --- |"]
    for tid, by_site in counts.items():
        spec = specs[TestId(tid)]
        colour, words = status(total(by_site))
        rows.append(
            f"| {tid} | {catalog.tests()[tid]['name']} | "
            f"[{spec.spec_version}](specs/rules/{spec.path.name}) | "
            f"{EMOJI[colour]} {words} |"
        )
    return rows


def _fmt(n: Counter) -> str:
    cs = sum(n[k] for k in COLS)
    return (
        f"{cs} | {n['agree']} | {n['key_fails']} | {n['key_passes']} | "
        f"{n['other']} | {n['left']}"
    )


def status_md() -> str:
    counts = compute()
    head = (
        "| Test | Site | Cells | Agree | PASS or DNA, key fails "
        "| FAIL or DNA, key passes | Other mismatch | Left for a person |"
    )
    sep = "| --- | --- | --- | --- | --- | --- | --- | --- |"
    lines = [
        "# Status counts behind the README table",
        "",
        "Written by `evals/status_table.py`; do not edit. Agent-assisted "
        'results, not certified Trusted Tester results. "Agrees" is about '
        "our evaluation pages only.",
        "",
        "A cell is one page and one test where a Trusted Tester's blind key "
        "gives an answer. Columns: agree; PASS or DOES NOT APPLY where the key "
        "fails; FAIL or DOES NOT APPLY where the key passes; other mismatch "
        "(the key says DOES NOT APPLY or NOT TESTED and the tool gives "
        "another outcome); left for a person (NEEDS REVIEW). The status "
        'rule, first match: red "passed a page a tester failed" (any '
        'PASS or DNA where the key fails); red "wrong more often than '
        'right" (wrong cells outnumber agreeing ones, over decided cells); '
        'yellow "often fails pages a tester passes" (wrong on more than 1 '
        'in 5 decided cells); yellow "mostly left for a person" (fewer than '
        'half the cells decided); green "agrees with a tester".',
        "",
        "## Runs",
        "",
    ]
    for rnd, s in SITES.items():
        lines.append(f"- Round {rnd}, {s['site']}: {s['run']}.")
    lines += ["", "## Counts", "", head, sep]
    for tid, by_site in counts.items():
        tot = total(by_site)
        colour, words = status(tot)
        for rnd, n in by_site.items():
            lines.append(f"| {tid} | R{rnd} {SITES[rnd]['site']} | {_fmt(n)} |")
        lines.append(f"| **{tid}** | **all: {EMOJI[colour]} {words}** | {_fmt(tot)} |")
    return "\n".join(lines) + "\n"


def write() -> None:
    text = README.read_text("utf-8")
    a, b = text.index(START) + len(START), text.index(END)
    README.write_text(
        text[:a] + "\n" + "\n".join(readme_rows()) + "\n\n" + text[b:], "utf-8"
    )
    STATUS_MD.write_text(status_md(), "utf-8")


def main() -> None:
    if "--write" in sys.argv:
        write()
        return
    print("\n".join(readme_rows()))
    print()
    print(status_md())


if __name__ == "__main__":
    main()
