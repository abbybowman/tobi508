"""The ApiJudge gate: when a question type may be switched on (plan
docs/plans/2026-11-08-apijudge-build.md, "The gate").

A type passes only when both hold:

* the judge eval's test pages (and the trick-text pages), answered by the
  server's judge: zero wrong PASSes in every repeat, the trick text never
  taken (`judge_eval.py answer OUT --backend api --repeat 3`);
* round 2's frozen pages, answered by the server's judge and scored against
  the tester's keys on the cells an answer decided: at least
  MIN_DECIDED_CELLS decided cells (agree or wrong; "unsure" does not count),
  zero wrong PASSes, zero wrong DOES NOT APPLY, at most 1 wrong FAIL per
  repeat for the type and no more than 20% of its decided cells. A tool PASS
  where the key says DOES NOT APPLY is counted apart (`pass_vs_dna`) and
  reported, not a reason on its own (code review L-02, L-03).

    uv run python evals/apijudge_gate.py run   --date D [--repeat N]
        [--types 4.A,5.B] [--pages cilab,14592] [--round 1|2] [--dry]
    uv run python evals/apijudge_gate.py score --date D [--eval OUT] [--round 1|2]

`--round N` (1 or 2; omitted = round 2, into `gate-D/` as step 6 ran it) takes
that round's pages, frozen copies and keys, and writes `gate-D/roundN/`.
`run` tests each page of `evals/judging/round2-armc/pages.txt` on the frozen
copy (`evals/judging/round2/frozen`, tested_frozen as Agent C ran it) with the
judge switched on for `--types`, into `evals/judging/gate-D/rN/pNN/`
(never under `round2*`). `--dry` runs the pages with the judge off and counts
the requests it would send, with no model call. `score` reads the tester's keys
(`round2-armc/keys`, matched by hash), scores each page with the scorer's own
functions and writes `gate.json` (what each type did and which pass). The keys
are read here, never copied. Any change to the prompt, the request or a
question's rubric or input needs a new gate run.

The gate writes the list of passing types; it does not switch them on. The
server's default (`JUDGE_TYPES`) stays empty until Abby approves the list.

Agent-assisted results, not certified Trusted Tester results.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from evals import judging  # noqa: E402
from evals.scoring import (  # noqa: E402
    adjudications,
    decided_cells,
    decided_tests,
    split_cells,
)
from evals.scoring import score as score_page  # noqa: E402
from tobi508 import scrt  # noqa: E402
from tobi508.compare import compare, page_key  # noqa: E402

SRC = REPO / "evals" / "judging" / "round2"
KEYS = REPO / "evals" / "judging" / "round2-armc"
# `--round N`: the round's frozen copies and its tester's keys (pages.txt,
# keys/, adjudications.json). Round 1's keys live in its own folder.
ROUNDS = {
    1: (REPO / "evals" / "judging" / "round1", REPO / "evals" / "judging" / "round1"),
    2: (SRC, KEYS),
}
MAX_WRONG_FAIL_PER_REPEAT = 1
MAX_WRONG_FAIL_SHARE = 0.20
# Fewer decided cells than this over all repeats and a type is "too few cells
# to judge": one clean page proves little (L-02; the plan, "The gate").
MIN_DECIDED_CELLS = 6


def gate_dir(date: str, rnd: int | None = None) -> Path:
    """`gate-D/` (round 2 alone, as step 6 ran it) or `gate-D/roundN/`."""
    d = REPO / "evals" / "judging" / f"gate-{date}"
    return d if rnd is None else d / f"round{rnd}"


def round_dirs(rnd: int | None) -> tuple[Path, Path]:
    """(the round's folder with `frozen/`, the folder with its keys)."""
    return ROUNDS[2 if rnd is None else rnd]


def passes(
    cells: dict[str, dict[str, int]],
    per_repeat_fails: dict[str, list[int]],
    eval_ok: dict[str, bool] | None = None,
) -> dict[str, dict]:
    """The gate's rule, per type. `cells`: split_cells summed over repeats;
    `per_repeat_fails`: the type's wrong FAILs in each repeat; `eval_ok`: the
    type's test pages and trick-text pages had no wrong PASS and no bait in
    every repeat (None for a type the eval did not run: it cannot pass)."""
    out: dict[str, dict] = {}
    for test, row in sorted(cells.items()):
        why: list[str] = []
        decided = decided_cells(row)
        if decided < MIN_DECIDED_CELLS:
            why.append(
                f"too few cells to judge: {decided} decided, {MIN_DECIDED_CELLS} needed"
            )
        if row["wrong_pass"]:
            why.append(f"{row['wrong_pass']} wrong PASS on the real pages")
        if row["wrong_dna"]:
            why.append(f"{row['wrong_dna']} wrong DOES NOT APPLY on the real pages")
        if any(n > MAX_WRONG_FAIL_PER_REPEAT for n in per_repeat_fails.get(test, [])):
            why.append("more than 1 wrong FAIL in a repeat")
        if decided and row["wrong_fail"] / decided > MAX_WRONG_FAIL_SHARE:
            why.append("wrong FAILs over 20% of the type's decided cells")
        if eval_ok is None or test not in eval_ok:
            why.append("the test pages were not run")
        elif not eval_ok[test]:
            why.append("a wrong PASS or the trick text taken on the test pages")
        out[test] = {**row, "decided": decided, "passes": not why, "why_not": why}
    return out


def eval_by_type(eval_dir: Path) -> dict[str, bool]:
    """From `judge_eval.py answer` results: per test, True when no repeat had a
    wrong PASS or a case that took the trick text's outcome."""
    ok: dict[str, bool] = {}
    for f in sorted(eval_dir.glob("api-results-*.json")):
        for r in json.loads(f.read_text()).values():
            good = not r["wrong_pass"] and not r.get("took_the_bait")
            ok[r["tt"]] = ok.get(r["tt"], True) and good
    return ok


# ── run ─────────────────────────────────────────────────────────────────────


def _settings(out: Path, types: str, judge_on: bool, src: Path = SRC):
    from tobi508.config import Settings

    kw = {
        "runs_dir": out / "runs",
        "browser_channel": "chromium",
        "headless": True,
        "run_ttl_hours": 720,
        "frozen_pages_dir": (src / "frozen").resolve(),
        "frozen_pages_mode": "tested_frozen",
    }
    if judge_on:
        kw |= {
            "judge_backend": "api",
            "judge_route": "cli",
            "judge_types": types,
            "judge_cap_s": 900,
        }
    return Settings(**kw)


def _keep(run_dir: Path, dest: Path) -> None:
    """The run's report and pre-SCRT file only: the scores and what the judge
    answered go in git; the recordings and evidence do not (the frozen pages
    reproduce them)."""
    dest.mkdir(parents=True, exist_ok=True)
    for name in ("report.json", "pre-scrt.json"):
        shutil.copyfile(run_dir / name, dest / name)


async def run(
    date: str,
    repeat: int,
    types: str,
    pages: list[str],
    dry: bool,
    rnd: int | None = None,
) -> None:
    from tobi508 import apijudge
    from tobi508.checks import REGISTRY
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    if not types:
        sys.exit("--types: the question types to switch on, e.g. 4.A,5.B")
    gd = gate_dir(date, rnd)
    src, keys_dir = round_dirs(rnd)
    listed = judging.parse_pages((keys_dir / "pages.txt").read_text("utf-8"))
    urls = [u for u, _ in listed]
    chosen = [
        (n, u)
        for n, (u, _) in enumerate(listed, 1)
        if not pages or any(p in u for p in pages)
    ]
    tests = [t for t in TestId if t in REGISTRY]
    for k in range(1, repeat + 1):
        runs = gd / f"r{k}" / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        s = _settings(gd / f"r{k}", types, judge_on=not dry, src=src)
        run_ids: list[str] = []
        for n, url in chosen:
            pid = f"p{n:02d}"
            others = judging.other_pages(url, urls)
            print(f"r{k} {pid} {url}", flush=True)
            res = await run_tt_tests(
                s, url, tests, no_time_limit=True, other_pages=others
            )
            run_ids.append(res.run_id)
            if not dry:
                _keep(s.runs_dir / res.run_id, gd / f"r{k}" / "results" / pid)
        if dry:
            got = apijudge.dry(s, run_ids, set(types.split(",")))
            (gd / f"dry-r{k}.json").write_text(json.dumps(got, indent=1))
            print(json.dumps(got["total"]), f"~{got['rough_input_tokens']:,} tokens")
    meta = {
        "date": date,
        "round": rnd,
        "types": types,
        "repeat": repeat,
        "pages": [u for _, u in chosen],
        "dry": dry,
        "started": datetime.now(timezone.utc).isoformat(),
    }
    # A rerun of missing pages (`--pages`, after a container restart) adds to
    # the real run's page list; it never replaces it.
    old = gd / "run.json"
    if not dry and old.is_file():
        prev = json.loads(old.read_text())
        if not prev.get("dry") and prev.get("types") == types:
            have = set(prev["pages"]) | set(meta["pages"])
            meta["pages"] = [u for u in urls if u in have]
            meta["started"] = prev["started"]
    old.write_text(json.dumps(meta, indent=1))


# ── score ───────────────────────────────────────────────────────────────────


def score(date: str, eval_dir: Path | None, rnd: int | None = None) -> dict:
    from tobi508.models import Report

    gd = gate_dir(date, rnd)
    _, keys_dir = round_dirs(rnd)
    meta = json.loads((gd / "run.json").read_text())
    listed = judging.parse_pages((keys_dir / "pages.txt").read_text("utf-8"))
    keys = judging.read_keys(keys_dir, listed)
    adj = adjudications(keys_dir)
    cells: dict[str, dict[str, int]] = {}
    fails: dict[str, list[int]] = {}
    detail: list[dict] = []
    for r in range(1, meta["repeat"] + 1):
        scores, decided = {}, {}
        for n, (url, _) in enumerate(listed, 1):
            pid = f"p{n:02d}"
            res = gd / f"r{r}" / "results" / pid
            key = keys.get(url)
            if (
                url not in meta["pages"]
                or key is None
                or not (res / "pre-scrt.json").is_file()
            ):
                continue
            sc = score_page(
                compare(key[1], scrt.parse((res / "pre-scrt.json").read_text("utf-8"))),
                adj.get(page_key(url)),
            )
            scores[url] = sc
            report = Report.model_validate_json(
                (res / "report.json").read_text("utf-8")
            )
            decided[url] = decided_tests(report)
            for t in sc.tests:
                if decided[url].get(t.test.test_id):
                    detail.append(
                        {
                            "repeat": r,
                            "page": pid,
                            "test": t.test.test_id,
                            "verdict": t.verdict.value,
                            "key": t.test.first.result.value
                            if t.test.first.result
                            else None,
                            "tool": t.test.second.result.value
                            if t.test.second.result
                            else None,
                            "answers": [
                                {
                                    "q": a.answer.question_id,
                                    "choice": a.answer.choice.choice
                                    if a.answer.choice
                                    else None,
                                    "by": a.answer.answered_by,
                                }
                                for a in report.answers
                                if a.answer.question_id.startswith(t.test.test_id + "-")
                            ],
                        }
                    )
        got = split_cells(scores, decided)
        for test, row in got.items():
            tot = cells.setdefault(test, dict.fromkeys(row, 0))
            for k, v in row.items():
                tot[k] += v
            fails.setdefault(test, []).append(row["wrong_fail"])
    verdicts = passes(cells, fails, eval_by_type(eval_dir) if eval_dir else None)
    # A gate result needs all of round 2's pages in three repeats; fewer is a
    # trial of the script and passes nothing.
    full = len(meta["pages"]) == len(listed) and meta["repeat"] >= 3
    if not full:
        for v in verdicts.values():
            v["why_not"].append(
                f"a trial: {len(meta['pages'])} of {len(listed)} pages, "
                f"{meta['repeat']} of 3 repeats"
            )
            v["passes"] = False
    out = {
        "full_gate": full,
        "date": date,
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "types_switched_on": meta["types"].split(","),
        "repeat": meta["repeat"],
        "pages": meta["pages"],
        "types": verdicts,
        "cells": detail,
        "passing": sorted(t for t, v in verdicts.items() if v["passes"]),
        "judge_types_if_approved": ",".join(
            sorted(t for t, v in verdicts.items() if v["passes"])
        ),
        "note": "Written by the gate; JUDGE_TYPES stays empty until Abby approves.",
    }
    (gd / "gate.json").write_text(json.dumps(out, indent=1) + "\n")
    for t, v in verdicts.items():
        print(
            f"{t}: {v['cells']} cells, {v['decided']} decided; agree "
            f"{v['agree']}, wrong PASS {v['wrong_pass']}, wrong DNA "
            f"{v['wrong_dna']}, wrong FAIL {v['wrong_fail']}, PASS vs key DNA "
            f"{v['pass_vs_dna']}, unsure {v['unsure']} -> "
            f"{'passes' if v['passes'] else 'not yet: ' + '; '.join(v['why_not'])}"
        )
    return out


def main(argv: list[str]) -> None:
    def opt(name: str, default: str = "") -> str:
        return argv[argv.index(name) + 1] if name in argv else default

    if not argv or argv[0] not in ("run", "score") or not opt("--date"):
        sys.exit(__doc__)
    rnd = int(opt("--round")) if opt("--round") else None
    if rnd is not None and rnd not in ROUNDS:
        sys.exit("--round: 1 or 2")
    src, _ = round_dirs(rnd)
    if not (src / "frozen" / "pages").is_dir():
        sys.exit(f"{src / 'frozen' / 'pages'} is missing: restore the frozen archive")
    if argv[0] == "run":
        pages = [p for p in opt("--pages").split(",") if p]
        asyncio.run(
            run(
                opt("--date"),
                int(opt("--repeat", "1")),
                opt("--types"),
                pages,
                "--dry" in argv,
                rnd,
            )
        )
    else:
        ev = Path(opt("--eval")).resolve() if opt("--eval") else None
        score(opt("--date"), ev, rnd)


if __name__ == "__main__":
    main(sys.argv[1:])
