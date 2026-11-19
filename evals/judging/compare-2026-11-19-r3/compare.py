"""Compare 2026-11-19: calling agent (A), server judge (C) and no-TOBI baseline (B)
on round 3's 10 frozen science.data.nasa.gov pages, 3 runs each.

    uv run python evals/judging/compare-2026-11-19-r3/compare.py

Writes `compare.json` and `compare.md` beside this file. Development pages; a
rerun that never replaces round 3's blind score. Agent-assisted results, not
certified Trusted Tester results.

Nothing here decides an outcome. Every verdict comes from the scorers already
in the repo, unchanged: 9c's cell scorer (`gate-2026-11-17-9c/compare.py`, which
calls `evals.scoring.score` on `tobi508.compare.compare`) per TT test, and
`evals.agent.score` per WCAG criterion. Round 3's keys are read in place and
never written to; its lock is not checked (this is a rerun, not the locked
round), so the lock check in `evals.agent.score` is stubbed for this script
only. The 30 arm folders are linked into a scratch round in a temp folder so
that scorer's output files never land in the repo.
"""

# ruff: noqa: E501  (the report's table rows and quotes are long lines)
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))

JUD = REPO / "evals" / "judging"
ROUND3 = JUD / "round3"  # keys, pages.txt: read only
RESULTS = HERE / "results"
RUNS = (1, 2, 3)

_s = importlib.util.spec_from_file_location(
    "m9c", JUD / "gate-2026-11-17-9c" / "compare.py"
)
m9c = importlib.util.module_from_spec(_s)
_s.loader.exec_module(m9c)
g16, g0 = m9c.g16, m9c.g16.g0

from evals.agent import score as ascore  # noqa: E402
from evals.scoring import decided_tests  # noqa: E402
from tobi508 import scrt  # noqa: E402
from tobi508.models import Report  # noqa: E402

NOTE = (
    "Development pages; a rerun that never replaces round 3's blind score. "
    "Agent-assisted results, not certified Trusted Tester results."
)


# ── Linking runs into folders the scorers read ───────────────────────────────


def _pre_for(d: Path, dest: Path) -> None:
    """`pre-scrt.json` beside a report: the file when it is there, else rebuilt
    from `report.json` (the C results do not keep it in git; the outcomes are
    the report's, only the report hash and inlined pictures differ)."""
    pre = d / "pre-scrt.json"
    if pre.is_file():
        (dest / "pre-scrt.json").symlink_to(pre.resolve())
        return
    rep = d / "report.json"
    doc = scrt.from_report(Report.model_validate_json(rep.read_text("utf-8")), d, None)
    (dest / "pre-scrt.json").write_text(scrt.dump(doc), encoding="utf-8")


def link_runs(tmp: Path, arm: str, sources: list[Path]) -> Path:
    """tmp/<arm>/runs/<n>/ with report.json and pre-scrt.json for every run
    folder in `sources`: the shape `evals.agent.score.tool_files` reads."""
    base = tmp / arm / "runs"
    for i, d in enumerate(sources):
        if not (d / "report.json").is_file():
            continue
        dest = base / f"{i:03d}-{d.name}"
        dest.mkdir(parents=True)
        (dest / "report.json").symlink_to((d / "report.json").resolve())
        _pre_for(d, dest)
    return tmp / arm


def a_run_dirs(arm: str, n: int) -> list[Path]:
    out: list[Path] = []
    for g in sorted(RESULTS.glob(f"arm-{arm}-g*-{n}")):
        out += sorted(
            p for p in (g / "runs").glob("*") if (p / "report.json").is_file()
        )
    return out


def c_run_dirs(n: int) -> list[Path]:
    return sorted((RESULTS / "c" / f"r{n}" / "results").glob("p*"))


# ── Cells (one per page and TT test), as 9c scores them ─────────────────────


def cells(run_dirs: list[Path], merged=None, who: str = "server") -> list[dict]:
    """9c's `side` rows. `who`: "server" counts the server judge's answers as
    the cell's decider (C); "any" counts the calling agent's too (A)."""
    old = g0.decided_tests
    g0.decided_tests = lambda rep: decided_tests(rep, who)
    try:
        return [
            r
            for r in g16.side(run_dirs, ROUND3, merged)
            if r["verdict"] != "not_scored"
        ]
    finally:
        g0.decided_tests = old


def tool_side(
    tmp: Path, name: str, dirs: list[Path], who: str
) -> tuple[list[dict], dict]:
    arm_dir = link_runs(tmp, name, dirs)
    merged = ascore.tool_files(arm_dir)
    # the linked folders, not `dirs`: they carry a pre-scrt.json (rebuilt from
    # report.json where git does not keep it), which 9c's cell scorer requires
    linked = sorted(p for p in (arm_dir / "runs").glob("*") if p.is_dir())
    return cells(linked, merged, who), merged


# ── Tables ───────────────────────────────────────────────────────────────────


def buckets(rows: list[dict]) -> Counter:
    return Counter(m9c.bucket(r) for r in rows)


def acc_row(rows: list[dict]) -> dict:
    """9c's five buckets plus the totals; `wrong_pass` etc. in the gate's words."""
    b = buckets(rows)
    return {
        "cells": len(rows),
        "agree": b["agree"],
        "unsafe": b["key_fails"],  # PASS/DNA where the key fails
        "fail_where_key_passes": b["key_passes"],
        "other": b["other"],
        "left_for_a_person": b["left"],
    }


def split_acc(rows: list[dict]) -> dict:
    return {
        "all": acc_row(rows),
        "rule_decided": acc_row([r for r in rows if not r["judge_decided"]]),
        "judge_decided": acc_row([r for r in rows if r["judge_decided"]]),
    }


def per_test_acc(runs_rows: dict[int, list[dict]]) -> dict[str, dict]:
    tests = sorted(
        {r["test"] for rs in runs_rows.values() for r in rs}, key=g16._tests_key
    )
    out = {}
    for t in tests:
        out[t] = {
            f"run{n}": acc_row([r for r in rs if r["test"] == t])
            for n, rs in runs_rows.items()
        } | {
            "all_runs": acc_row(
                [r for rs in runs_rows.values() for r in rs if r["test"] == t]
            )
        }
    return out


def consistency(runs_rows: dict[int, list[dict]]) -> dict:
    """The same tool outcome in all runs, per cell. Source of a flipped cell:
    "judge" when an answer decided it in any run, else "scan" (the rule's own
    evidence changed between loads)."""
    by: dict[tuple[str, str], dict[int, dict]] = defaultdict(dict)
    for n, rs in runs_rows.items():
        for r in rs:
            by[(r["page"], r["test"])][n] = r
    same, same_j, tot_j, flips = 0, 0, 0, []
    for (page, test), per in sorted(
        by.items(), key=lambda kv: (kv[0][0], g16._tests_key(kv[0][1]))
    ):
        if len(per) != len(runs_rows):
            continue
        outs = [per[n]["tool"] for n in sorted(per)]
        jd = any(per[n]["judge_decided"] for n in per)
        tot_j += jd
        if len(set(outs)) == 1:
            same += 1
            same_j += jd
        else:
            flips.append(
                {
                    "page": page,
                    "test": test,
                    "key": next(iter(per.values()))["key"],
                    "outcomes": {
                        f"run{n}": per[n]["tool"] or "NEEDS REVIEW" for n in sorted(per)
                    },
                    "verdicts": {f"run{n}": per[n]["verdict"] for n in sorted(per)},
                    "source": "judge" if jd else "scan",
                }
            )
    n_all = len([1 for per in by.values() if len(per) == len(runs_rows)])
    return {
        "cells": n_all,
        "same_in_all_runs": same,
        "judge_decided_cells": tot_j,
        "judge_decided_same_in_all_runs": same_j,
        "flipped": flips,
    }


# ── Per WCAG criterion: what the agent relayed (A, B) and what the tool found ──


def crit_row(counts: dict) -> dict:
    """abc-score's columns from the scorer's verdict counts."""
    c = Counter(counts)
    scored = sum(c.values()) - c["not_scored"]
    left = c["needs_review"] + c["not_performed"] + c["no_answer"]
    decided = scored - left
    return {
        "scored": scored,
        "false_pass": c["false_pass"],
        "missed_fail_dna": c["missed_fail"],
        "agree": c["agree"] + c["validated_catch"],
        "decided": decided,
        "false_fail": c["false_fail"],
        "fail_vs_dna": c["fail_vs_dna"],
        "other": c["other_mismatch"],
        "needs_review": c["needs_review"] + c["not_performed"],
        "no_answer": c["no_answer"],
        "weighted": ascore.weighted(c),
    }


def _sum(rows: list[dict]) -> dict:
    out: Counter = Counter()
    for r in rows:
        out.update(r)
    return dict(out)


def repair_final(text: str) -> tuple[str, bool]:
    """B's malformed RESULT line (the outer brace missing): the same text with
    up to two closing braces added. Sensitivity only: the scorer's own reading
    (malformed = no answer) is the primary one."""
    out, fixed = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("RESULT:") and not fixed:
            body = s[len("RESULT:") :]
            for extra in ("", "}", "}}"):
                try:
                    json.loads(body + extra)
                except ValueError:
                    continue
                fixed = bool(extra)
                s = "RESULT:" + body + extra
                break
        out.append(s if s.startswith("RESULT:") else line)
    return "\n".join(out) + "\n", fixed


def virtual_round(tmp: Path, name: str, arms: list[Path], repaired: bool = False):
    rd = tmp / name
    (rd / "results").mkdir(parents=True)
    (rd / "keys").symlink_to((ROUND3 / "keys").resolve())
    (rd / "pages.txt").write_text(
        (ROUND3 / "pages.txt").read_text("utf-8"), encoding="utf-8"
    )
    repaired_dirs = []
    for d in arms:
        if repaired:
            dest = rd / "results" / d.name
            dest.mkdir()
            (dest / "summary.json").write_text(
                (d / "summary.json").read_text("utf-8"), encoding="utf-8"
            )
            txt, fixed = repair_final((d / "final.md").read_text("utf-8"))
            (dest / "final.md").write_text(txt, encoding="utf-8")
            if fixed:
                repaired_dirs.append(d.name)
        else:
            (rd / "results" / d.name).symlink_to(d.resolve())
    return rd, repaired_dirs


def tool_criteria(rd: Path, arm_dir: Path) -> dict:
    """`evals.agent.score._server` for one tool arm folder: per TT test and per
    criterion counts, on the pages of the round."""
    pages = ascore._pages(rd)
    keys = ascore.read_keys(rd, pages)
    key_tt = {
        url: {tid: ascore.summary(rows) for tid, rows in ref.results().items()}
        for url, (_, ref) in keys.items()
    }
    return ascore._server(rd, arm_dir, keys, key_tt, ascore.criteria())


def relayed_by_run(tmp: Path) -> tuple[dict, dict, list[str]]:
    """({arm: {run: crit_row}}, per-group rows, B folders whose RESULT line
    was malformed under the scorer)."""
    ascore._verify = lambda rd: {"code_commit": "none (a rerun, not a locked round)"}
    arms = sorted(RESULTS.glob("arm-[ab]-g*-*"))
    rd, _ = virtual_round(tmp, "vr", arms)
    out = ascore.score(rd)
    per_group, by = {}, defaultdict(list)
    malformed = []
    for name, a in out["arms"].items():
        m = re.fullmatch(r"arm-([ab])-g(\d)-(\d)", name)
        arm, n = m.group(1), int(m.group(3))
        row = crit_row(a["per_criterion"]["counts"])
        per_group[name] = row
        by[(arm, n)].append(row)
        if a["result_line"] != "found":
            malformed.append(name)
    res = {arm: {n: _sum(by[(arm, n)]) for n in RUNS} for arm in "ab"}
    # sensitivity: B with the missing brace added
    barms = sorted(RESULTS.glob("arm-b-g*-*"))
    rd2, repaired = virtual_round(tmp, "vr-fixed", barms, repaired=True)
    out2 = ascore.score(rd2)
    byb = defaultdict(list)
    for name, a in out2["arms"].items():
        n = int(name.rsplit("-", 1)[1])
        byb[n].append(crit_row(a["per_criterion"]["counts"]))
    res["b_repaired"] = {n: _sum(byb[n]) for n in RUNS}
    return res, per_group, malformed, repaired


# ── Completeness: what was asked, answered, left, and what A looked at ───────


def _latest_answers(rep: dict) -> dict[str, dict]:
    out = {}
    for a in rep.get("answers", []):  # recorded in order: the last one is in force
        out[a["answer"]["question_id"]] = a["answer"]
    return out


def completeness(dirs: list[Path]) -> dict:
    """Over every run folder (one per page-load by the tool): questions asked,
    answered, unsure, left open; who answered; what A recorded about pictures."""
    asked = answered = unsure = open_q = 0
    by, seen_n, pic_err, not_viewed = Counter(), 0, 0, 0
    page_runs = Counter()
    for d in dirs:
        rep = json.loads((d / "report.json").read_text("utf-8"))
        page_runs[rep["target"]] += 1
        qids = {q["question_id"] for q in rep.get("questions", [])}
        ans = _latest_answers(rep)
        asked += len(qids)
        for qid in qids:
            a = ans.get(qid)
            if a is None:
                open_q += 1
                continue
            ch = (
                a["choice"]["choice"]
                if isinstance(a.get("choice"), dict)
                else a.get("choice")
            )
            if ch == "unsure":
                unsure += 1
            else:
                answered += 1
            by[a["answered_by"]] += 1
            seen_n += bool(a.get("seen"))
            pic_err += bool(a.get("picture_error"))
            not_viewed += bool(a.get("not_viewed"))
    return {
        "run_folders": len(dirs),
        "pages_loaded_more_than_once": sum(1 for v in page_runs.values() if v > 1),
        "asked": asked,
        "answered": answered,
        "unsure": unsure,
        "unanswered": open_q,
        "answered_by": dict(by),
        "seen_recorded": seen_n,
        "picture_error": pic_err,
        "not_viewed": not_viewed,
    }


def read_transcript(folder: Path) -> list:
    """A group's transcript: the full file when it is on disk (git ignores it),
    else the copy without picture bytes that is in git (`transcripts-no-images.zip`;
    the stats below need only the tool calls and the image blocks' count)."""
    f = folder / "transcript.json"
    if f.is_file():
        return json.loads(f.read_text("utf-8"))
    import zipfile

    with zipfile.ZipFile(HERE / "transcripts-no-images.zip") as z:
        return json.loads(z.read(f"{folder.name}/transcript.json"))


def transcript_stats(n: int) -> dict:
    """A's tool calls over the run's groups, from transcript.json."""
    calls, finish, explain, pic_reads, run_reads = Counter(), 0, 0, 0, 0
    status_all = 0
    res_pics = 0
    for g in sorted(RESULTS.glob(f"arm-a-g*-{n}")):
        for e in read_transcript(g):
            c = (e.get("message") or {}).get("content")
            if not isinstance(c, list):
                continue
            for b in c:
                if b.get("type") == "tool_use":
                    name, inp = b["name"], b.get("input") or {}
                    calls[name] += 1
                    if inp.get("finish") is True:
                        finish += 1
                    if name.endswith("tobi_explain"):
                        explain += 1
                    if name.endswith("tobi_run_status") and not inp.get("job_id"):
                        status_all += 1
                    uri = inp.get("uri") or inp.get("file_path") or ""
                    if "run://" in str(uri):
                        run_reads += 1
                        pic_reads += bool(re.search(r"\.(png|jpe?g)$", str(uri)))
                elif b.get("type") == "tool_result" and isinstance(
                    b.get("content"), list
                ):
                    res_pics += sum(1 for y in b["content"] if y.get("type") == "image")
    return {
        "tool_calls": dict(calls),
        "finish_true_calls": finish,
        "tobi_explain_calls": explain,
        "run_status_without_job_id_calls": status_all,
        "run_uri_reads": run_reads,
        "picture_reads_by_uri": pic_reads,
        "pictures_attached_to_results": res_pics,
    }


# ── Cost and time ────────────────────────────────────────────────────────────

TOK = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)


def summaries(arm: str, n: int) -> list[dict]:
    return [
        json.loads((g / "summary.json").read_text("utf-8"))
        for g in sorted(RESULTS.glob(f"arm-{arm}-g*-{n}"))
    ]


def cost_time(arm: str, n: int) -> dict:
    ss = summaries(arm, n)
    tok = Counter()
    for s in ss:
        tok.update({k: (s.get("tokens") or {}).get(k, 0) for k in TOK})
    return {
        "groups": len(ss),
        "cost_usd_list_price": round(
            sum(s.get("cost_usd_list_price") or 0 for s in ss), 4
        ),
        "tokens": dict(tok),
        "wall_s": round(sum(s.get("wall_s") or 0 for s in ss), 1),
        "model_calls": sum(s.get("model_calls") or 0 for s in ss),
        "tool_calls": sum(sum((s.get("tool_calls") or {}).values()) for s in ss),
        "ended": dict(Counter(s.get("ended") for s in ss)),
        "per_page_cost_usd": round(
            sum(s.get("cost_usd_list_price") or 0 for s in ss) / 10, 4
        ),
        "per_page_wall_s": round(sum(s.get("wall_s") or 0 for s in ss) / 10, 1),
    }


def price_fit() -> dict:
    """List-price rates per million tokens implied by A's and B's own summaries
    (cost = tokens x rates; least squares over every group). The server judge's
    CLI calls record tokens but no cost, so C's cost is an estimate at these
    rates (cache creation taken as one rate)."""
    import numpy as np

    X, y = [], []
    for arm in "ab":
        for g in sorted(RESULTS.glob(f"arm-{arm}-g*-*")):
            s = json.loads((g / "summary.json").read_text("utf-8"))
            t = s.get("tokens") or {}
            X.append([t.get(k, 0) for k in TOK])
            y.append(s.get("cost_usd_list_price") or 0)
    X, y = np.array(X, float), np.array(y, float)
    rates, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = float(np.max(np.abs(X @ rates - y)))
    return {
        "usd_per_mtok": dict(zip(TOK, (round(float(r) * 1e6, 3) for r in rates))),
        "max_abs_residual_usd": round(resid, 6),
        "groups_fitted": len(y),
        "_rates": rates,
    }


def c_cost_time(n: int, fit: dict) -> dict:
    dirs = c_run_dirs(n)
    calls = fails = retried = q = ans = unsure = left = 0
    tok, judge_s, wall, test_s = Counter(), 0.0, 0.0, 0.0
    models, prompts = set(), set()
    for d in dirs:
        rep = json.loads((d / "report.json").read_text("utf-8"))
        j = rep["judge"]
        calls += j["calls"]
        fails += j["failed_calls"]
        retried += j["retried_calls"]
        q += j["questions"]
        ans += j["answered"]
        unsure += j["unsure"]
        left += j["left_open"]
        tok.update({k: j["tokens"].get(k, 0) for k in TOK})
        judge_s += j["seconds_in_calls"]
        models.update(j["models_reported"])
        prompts.add(j["prompt_sha256"])
        tm = json.loads((d / "timing.json").read_text("utf-8"))
        from datetime import datetime

        wall += (
            datetime.fromisoformat(tm["call_finished"])
            - datetime.fromisoformat(tm["call_started"])
        ).total_seconds()
        test_s += sum(t["seconds"] for t in rep["test_times"].values())
    est = float(sum(tok[k] * float(r) for k, r in zip(TOK, fit["_rates"])))
    return {
        "pages": len(dirs),
        "judge_calls": calls,
        "failed_calls": fails,
        "retried_calls": retried,
        "questions": q,
        "answered": ans,
        "unsure": unsure,
        "left_open": left,
        "tokens": dict(tok),
        "judge_seconds_in_calls_summed": round(judge_s, 1),
        "call_wall_s": round(wall, 1),
        "tests_seconds_summed": round(test_s, 1),
        "estimated_judge_cost_usd": round(est, 4),
        "per_page_call_wall_s": round(wall / max(len(dirs), 1), 1),
        "per_page_judge_tokens": round(sum(tok.values()) / max(len(dirs), 1)),
        "per_page_estimated_cost_usd": round(est / max(len(dirs), 1), 4),
        "models_reported": sorted(models),
        "judge_prompt_sha256": sorted(prompts),
    }


# ── Same answers, same relayed results across the runs ───────────────────────


def answer_consistency(runs_dirs: dict[int, list[Path]]) -> dict:
    """Per (page, question): the choice word in each run, for questions asked in
    every run."""
    by: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)
    for n, dirs in runs_dirs.items():
        for d in dirs:
            rep = json.loads((d / "report.json").read_text("utf-8"))
            for qid, a in _latest_answers(rep).items():
                ch = (
                    a["choice"]["choice"]
                    if isinstance(a.get("choice"), dict)
                    else a.get("choice")
                )
                by[(rep["target"], qid)][n] = ch
    asked_all = {k: v for k, v in by.items() if len(v) == len(runs_dirs)}
    same = {k: v for k, v in asked_all.items() if len(set(v.values())) == 1}
    differ = [
        {
            "page": k[0],
            "question": k[1],
            "answers": {f"run{n}": v[n] for n in sorted(v)},
        }
        for k, v in sorted(asked_all.items())
        if len(set(v.values())) > 1
    ]
    some = len(by) - len(asked_all)
    return {
        "questions_seen": len(by),
        "asked_in_every_run": len(asked_all),
        "asked_in_some_runs_only": some,
        "same_answer_in_every_run": len(same),
        "answers_differ": differ,
    }


def relayed_cells(
    arm: str, n: int, repaired: bool = False
) -> dict[tuple[str, str], str]:
    """(page, WCAG criterion) -> what the agent reported, from each group's RESULT line."""
    cs = ascore.criteria()
    out: dict[tuple[str, str], str] = {}
    for g in sorted(RESULTS.glob(f"arm-{arm}-g*-{n}")):
        s = json.loads((g / "summary.json").read_text("utf-8"))
        txt = (g / "final.md").read_text("utf-8")
        if repaired:
            txt, _ = repair_final(txt)
        res = ascore.parse_result(txt)
        for url in s["pages"]:
            for c in cs:
                got, _ = ascore.relayed(res, url, c["id"])
                out[(url, c["id"])] = (
                    "missing"
                    if got == ascore.MISSING
                    else (got.value if got is not None else "NEEDS_REVIEW")
                )
    return out


def relayed_consistency(arm: str, repaired: bool = False) -> dict:
    per = {n: relayed_cells(arm, n, repaired) for n in RUNS}
    keys = sorted(set.intersection(*(set(v) for v in per.values())))
    flips = [
        {
            "page": k[0],
            "criterion": k[1],
            "outcomes": {f"run{n}": per[n][k] for n in RUNS},
        }
        for k in keys
        if len({per[n][k] for n in RUNS}) > 1
    ]
    return {
        "cells": len(keys),
        "same_in_all_runs": len(keys) - len(flips),
        "flipped": flips,
    }


# ── Debrief quotes (copied verbatim; the script checks each is in its file) ──

QUOTES = {
    1: [
        (
            "arm-a-g1-1",
            'I answered "preserves" and explained those jumps as mega-menu sections, but I never checked that. That PASS is weaker than it looks.',
        ),
        ("arm-a-g3-1", "My `seen` text overstated what I had checked."),
        ("arm-a-g5-1", "I did not actually open the run:// images."),
    ],
    2: [
        (
            "arm-a-g1-2",
            "Some `seen` entries described what I assumed rather than what I had checked.",
        ),
        ("arm-a-g3-2", "I never called it, because I did not think I needed it."),
        (
            "arm-a-g5-2",
            "It conflicts with my own NEEDS_REVIEW for 1.3.1 on the same page, and it is the kind of wrong PASS I should have avoided.",
        ),
    ],
    3: [
        ("arm-a-g1-3", "I opened only two of the 5.D images"),
        (
            "arm-a-g3-3",
            "I did not think it would change the results, and I wanted to finish.",
        ),
        (
            "arm-a-g5-3",
            'the tool said each page\'s "other page" had the same content as the tested page, so it compared nothing.',
        ),
    ],
}


def quotes() -> dict:
    out = {}
    for n, items in QUOTES.items():
        out[f"run{n}"] = []
        for folder, q in items:
            text = " ".join(
                (RESULTS / folder / "debrief.md").read_text("utf-8").split()
            )
            assert " ".join(q.split()) in text, f"quote not in {folder}/debrief.md: {q}"
            out[f"run{n}"].append({"from": f"results/{folder}/debrief.md", "quote": q})
    return out


# ── Assemble ─────────────────────────────────────────────────────────────────


def _md_table(head: list[str], rows: list[list]) -> list[str]:
    out = [
        "| " + " | ".join(head) + " |",
        "| " + " | ".join("---" for _ in head) + " |",
    ]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return out + [""]


def build() -> dict:
    tmp = Path(tempfile.mkdtemp())
    out: dict = {"note": NOTE}
    # what ran
    commits = sorted(
        {s["code_commit"] for arm in "ab" for n in RUNS for s in summaries(arm, n)}
    )
    run_json = (
        json.loads((RESULTS / "c" / "run.json").read_text("utf-8"))
        if (RESULTS / "c" / "run.json").is_file()
        else {}
    )
    out["what_ran"] = {
        "arm_commits_in_summaries": commits,
        "c_run_json": run_json,
        "models_requested": sorted(
            {
                s["model_requested"]
                for arm in "ab"
                for n in RUNS
                for s in summaries(arm, n)
            }
        ),
        "prompt_versions": sorted(
            {
                s["prompt_version"]
                for arm in "ab"
                for n in RUNS
                for s in summaries(arm, n)
            }
        ),
        "b_tool_servers": sorted(
            {
                json.dumps([sv["name"] for sv in s["servers"]])
                for n in RUNS
                for s in summaries("b", n)
            }
        ),
        "a_tool_servers": sorted(
            {
                json.dumps([sv["name"] for sv in s["servers"]])
                for n in RUNS
                for s in summaries("a", n)
            }
        ),
    }
    # cells
    ad = {n: a_run_dirs("a", n) for n in RUNS}
    cd = {n: c_run_dirs(n) for n in RUNS}
    a_rows, c_rows = {}, {}
    for n in RUNS:
        a_rows[n], _ = tool_side(tmp, f"a{n}", ad[n], "any")
        c_rows[n], _ = tool_side(tmp, f"c{n}", cd[n], "server")
    blind_dirs = sorted(
        p for p in (ROUND3 / "results").iterdir() if (p / "report.json").is_file()
    )
    blind = cells(blind_dirs, None, "server") if blind_dirs else []
    out["accuracy_per_tt"] = {
        "reference_round3_blind": split_acc(blind),
        "a": {f"run{n}": split_acc(a_rows[n]) for n in RUNS},
        "c": {f"run{n}": split_acc(c_rows[n]) for n in RUNS},
        "a_3_runs": split_acc([r for n in RUNS for r in a_rows[n]]),
        "c_3_runs": split_acc([r for n in RUNS for r in c_rows[n]]),
        "per_test_a": per_test_acc(a_rows),
        "per_test_c": per_test_acc(c_rows),
    }
    # per criterion
    rel, per_group, malformed, repaired = relayed_by_run(tmp)
    rd_t, _ = virtual_round(tmp, "vt", [])
    tool_crit = {"a": {}, "c": {}}
    for n in RUNS:
        for key, dirs in (("a", ad[n]), ("c", cd[n])):
            arm_dir = link_runs(tmp, f"t{key}{n}", dirs)
            t = tool_criteria(rd_t, arm_dir)
            tool_crit[key][n] = {
                "per_criterion": crit_row(t["per_criterion"]["counts"]),
                "per_tt_counts": t["per_tt"]["counts"],
                "needs_review_reasons": t["needs_review_reasons"],
            }
    out["accuracy_per_criterion"] = {
        "a_reported": {f"run{n}": rel["a"][n] for n in RUNS},
        "b_reported": {f"run{n}": rel["b"][n] for n in RUNS},
        "b_reported_if_brace_added": {f"run{n}": rel["b_repaired"][n] for n in RUNS},
        "a_tool": {f"run{n}": tool_crit["a"][n]["per_criterion"] for n in RUNS},
        "c_tool": {f"run{n}": tool_crit["c"][n]["per_criterion"] for n in RUNS},
        "a_tool_per_tt_counts": {
            f"run{n}": tool_crit["a"][n]["per_tt_counts"] for n in RUNS
        },
        "c_tool_per_tt_counts": {
            f"run{n}": tool_crit["c"][n]["per_tt_counts"] for n in RUNS
        },
        "b_malformed_result_lines": malformed,
        "per_group": per_group,
    }
    # completeness
    out["completeness"] = {
        "a": {f"run{n}": completeness(ad[n]) | transcript_stats(n) for n in RUNS},
        "c": {
            f"run{n}": completeness(cd[n])
            | {"judge": c_cost_time(n, {"_rates": [0, 0, 0, 0]})["judge_calls"]}
            for n in RUNS
        },
        "a_debrief_quotes": quotes(),
    }
    # consistency
    out["consistency"] = {
        "a_tool_cells": consistency(a_rows),
        "c_cells": consistency(c_rows),
        "a_answers": answer_consistency(ad),
        "c_answers": answer_consistency(cd),
        "a_reported_criteria": relayed_consistency("a"),
        "b_reported_criteria": relayed_consistency("b"),
        "b_reported_criteria_if_brace_added": relayed_consistency("b", True),
    }
    # cost and time
    fit = price_fit()
    out["cost_time"] = {
        "a": {f"run{n}": cost_time("a", n) for n in RUNS},
        "b": {f"run{n}": cost_time("b", n) for n in RUNS},
        "c": {f"run{n}": c_cost_time(n, fit) for n in RUNS},
        "price_fit": {k: v for k, v in fit.items() if k != "_rates"},
    }
    out["cells"] = {
        "a": {
            f"run{n}": [
                {
                    k: r[k]
                    for k in ("page", "test", "key", "tool", "verdict", "judge_decided")
                }
                for r in a_rows[n]
            ]
            for n in RUNS
        },
        "c": {
            f"run{n}": [
                {
                    k: r[k]
                    for k in ("page", "test", "key", "tool", "verdict", "judge_decided")
                }
                for r in c_rows[n]
            ]
            for n in RUNS
        },
    }
    return out


def _acc_cols(a: dict) -> list:
    return [
        a["cells"],
        a["agree"],
        a["unsafe"],
        a["fail_where_key_passes"],
        a["other"],
        a["left_for_a_person"],
    ]


ACC_HEAD = [
    "Cells",
    "Agree",
    "Unsafe (PASS/DNA, key Fail)",
    "FAIL/DNA, key Pass",
    "Other",
    "Left for a person",
]


def markdown(o: dict) -> str:
    L = [
        "# Compare 2026-11-19: calling agent vs server judge, round 3's pages, 3 runs each",
        "",
        o["note"],
        "",
    ]
    w = o["what_ran"]
    L += [
        "A is the calling agent with TOBI (the client judge answers open questions), B the same model with Playwright MCP only,",
        "C the server judge (`evals/apijudge_gate.py`, 21 test types). All Sonnet 5.5 (`claude-sonnet-5-5`), the CLI route,",
        f"prompt `{', '.join(w['prompt_versions'])}`, round 3's 10 frozen pages. A and B ran as 5 groups of 2 pages per run.",
        "",
    ]
    ap = o["accuracy_per_tt"]
    L += [
        "## Accuracy per TT test (A and C), against round 3's keys",
        "",
        *_md_table(
            ["Run", *ACC_HEAD],
            [
                [
                    "round 3 blind (reference)",
                    *_acc_cols(ap["reference_round3_blind"]["all"]),
                ],
                *[[f"A run {n}", *_acc_cols(ap["a"][f"run{n}"]["all"])] for n in RUNS],
                *[[f"C run {n}", *_acc_cols(ap["c"][f"run{n}"]["all"])] for n in RUNS],
                ["A, 3 runs", *_acc_cols(ap["a_3_runs"]["all"])],
                ["C, 3 runs", *_acc_cols(ap["c_3_runs"]["all"])],
            ],
        ),
    ]
    L += [
        "### Rule-decided and answer-decided cells apart (3 runs together)",
        "",
        *_md_table(
            ["Who", "Decided by", *ACC_HEAD],
            [
                ["A", "rules", *_acc_cols(ap["a_3_runs"]["rule_decided"])],
                [
                    "A",
                    "the agent's answers",
                    *_acc_cols(ap["a_3_runs"]["judge_decided"]),
                ],
                ["C", "rules", *_acc_cols(ap["c_3_runs"]["rule_decided"])],
                [
                    "C",
                    "the server judge's answers",
                    *_acc_cols(ap["c_3_runs"]["judge_decided"]),
                ],
            ],
        ),
    ]
    L += [
        "### Per TT test (3 runs together)",
        "",
        *_md_table(
            [
                "Test",
                "A agree/unsafe/FAIL-vs-Pass/other/left",
                "C agree/unsafe/FAIL-vs-Pass/other/left",
            ],
            [
                [
                    t,
                    "{agree}/{unsafe}/{fail_where_key_passes}/{other}/{left_for_a_person}".format(
                        **ap["per_test_a"][t]["all_runs"]
                    ),
                    "{agree}/{unsafe}/{fail_where_key_passes}/{other}/{left_for_a_person}".format(
                        **ap["per_test_c"][t]["all_runs"]
                    ),
                ]
                for t in ap["per_test_a"]
            ],
        ),
    ]
    pc = o["accuracy_per_criterion"]
    head = [
        "Run",
        "Scored",
        "False PASS",
        "Missed fail (DNA)",
        "Agree (of decided)",
        "False FAIL",
        "Other",
        "Needs review",
        "No answer",
        "Weighted",
    ]

    def crow(name, r):
        return [
            name,
            r["scored"],
            r["false_pass"],
            r["missed_fail_dna"],
            f"{r['agree']}/{r['decided']}",
            r["false_fail"],
            r["other"],
            r["needs_review"],
            r["no_answer"],
            r["weighted"],
        ]

    L += [
        "## Accuracy per WCAG 2.0 criterion (the locked agent scorer's weights)",
        "",
        *_md_table(
            head,
            [
                *[
                    crow(f"A reported, run {n}", pc["a_reported"][f"run{n}"])
                    for n in RUNS
                ],
                *[
                    crow(f"B reported, run {n}", pc["b_reported"][f"run{n}"])
                    for n in RUNS
                ],
                *[
                    crow(
                        f"B if the brace were added, run {n}",
                        pc["b_reported_if_brace_added"][f"run{n}"],
                    )
                    for n in RUNS
                ],
                *[crow(f"A tool, run {n}", pc["a_tool"][f"run{n}"]) for n in RUNS],
                *[crow(f"C tool, run {n}", pc["c_tool"][f"run{n}"]) for n in RUNS],
            ],
        ),
    ]
    L += [
        f"B's final messages with an unparseable RESULT line (the outer brace missing), which the scorer reads as no answer: {', '.join(pc['b_malformed_result_lines']) or 'none'}. The rows 'if the brace were added' are a sensitivity view, not the scorer's reading.",
        "",
    ]
    cm = o["completeness"]
    L += [
        "## Completeness",
        "",
        *_md_table(
            [
                "Run",
                "Run folders",
                "Asked",
                "Answered",
                "Unsure",
                "Unanswered",
                "Answered by",
                "seen recorded",
                "picture_error",
                "not_viewed",
            ],
            [
                *[
                    [
                        f"A run {n}",
                        cm["a"][f"run{n}"]["run_folders"],
                        cm["a"][f"run{n}"]["asked"],
                        cm["a"][f"run{n}"]["answered"],
                        cm["a"][f"run{n}"]["unsure"],
                        cm["a"][f"run{n}"]["unanswered"],
                        cm["a"][f"run{n}"]["answered_by"],
                        cm["a"][f"run{n}"]["seen_recorded"],
                        cm["a"][f"run{n}"]["picture_error"],
                        cm["a"][f"run{n}"]["not_viewed"],
                    ]
                    for n in RUNS
                ],
                *[
                    [
                        f"C run {n}",
                        cm["c"][f"run{n}"]["run_folders"],
                        cm["c"][f"run{n}"]["asked"],
                        cm["c"][f"run{n}"]["answered"],
                        cm["c"][f"run{n}"]["unsure"],
                        cm["c"][f"run{n}"]["unanswered"],
                        cm["c"][f"run{n}"]["answered_by"],
                        cm["c"][f"run{n}"]["seen_recorded"],
                        cm["c"][f"run{n}"]["picture_error"],
                        cm["c"][f"run{n}"]["not_viewed"],
                    ]
                    for n in RUNS
                ],
            ],
        ),
    ]
    L += [
        "### What A did with the tools (from transcript.json)",
        "",
        *_md_table(
            [
                "Run",
                "tobi_run_tt_tests",
                "tobi_answer_questions",
                "tobi_run_status",
                "…with no job_id",
                "finish=true",
                "tobi_explain",
                "run:// reads",
                "pictures attached to results",
            ],
            [
                [
                    f"A run {n}",
                    cm["a"][f"run{n}"]["tool_calls"].get(
                        "mcp__a11y__tobi_run_tt_tests", 0
                    ),
                    cm["a"][f"run{n}"]["tool_calls"].get(
                        "mcp__a11y__tobi_answer_questions", 0
                    ),
                    cm["a"][f"run{n}"]["tool_calls"].get(
                        "mcp__a11y__tobi_run_status", 0
                    ),
                    cm["a"][f"run{n}"]["run_status_without_job_id_calls"],
                    cm["a"][f"run{n}"]["finish_true_calls"],
                    cm["a"][f"run{n}"]["tobi_explain_calls"],
                    cm["a"][f"run{n}"]["run_uri_reads"],
                    cm["a"][f"run{n}"]["pictures_attached_to_results"],
                ]
                for n in RUNS
            ],
        ),
    ]
    L += ["### Debrief quotes (verbatim; checked against the files)", ""]
    for rn, items in cm["a_debrief_quotes"].items():
        for it in items:
            L.append(f'- {rn}, `{it["from"]}`: "{it["quote"]}"')
    L.append("")
    cs = o["consistency"]

    def crow2(name, c):
        return [name, c["cells"], c["same_in_all_runs"], len(c["flipped"])]

    L += [
        "## Consistency across the 3 runs",
        "",
        *_md_table(
            ["What", "Cells", "Same in all 3 runs", "Flipped"],
            [
                crow2("A tool outcome per TT test (all cells)", cs["a_tool_cells"]),
                [
                    "A tool outcome, answer-decided cells only",
                    cs["a_tool_cells"]["judge_decided_cells"],
                    cs["a_tool_cells"]["judge_decided_same_in_all_runs"],
                    cs["a_tool_cells"]["judge_decided_cells"]
                    - cs["a_tool_cells"]["judge_decided_same_in_all_runs"],
                ],
                crow2("C tool outcome per TT test (all cells)", cs["c_cells"]),
                [
                    "C tool outcome, judge-decided cells only",
                    cs["c_cells"]["judge_decided_cells"],
                    cs["c_cells"]["judge_decided_same_in_all_runs"],
                    cs["c_cells"]["judge_decided_cells"]
                    - cs["c_cells"]["judge_decided_same_in_all_runs"],
                ],
                crow2("A reported, per criterion", cs["a_reported_criteria"]),
                crow2(
                    "B reported, per criterion (scorer's reading)",
                    cs["b_reported_criteria"],
                ),
                crow2(
                    "B reported, per criterion (brace added)",
                    cs["b_reported_criteria_if_brace_added"],
                ),
                [
                    "A answers to the same question",
                    cs["a_answers"]["asked_in_every_run"],
                    cs["a_answers"]["same_answer_in_every_run"],
                    len(cs["a_answers"]["answers_differ"]),
                ],
                [
                    "C answers to the same question",
                    cs["c_answers"]["asked_in_every_run"],
                    cs["c_answers"]["same_answer_in_every_run"],
                    len(cs["c_answers"]["answers_differ"]),
                ],
            ],
        ),
    ]
    for name, key in (("A", "a_tool_cells"), ("C", "c_cells")):
        L += [
            f"### {name}: every flipped TT cell and its source",
            "",
            *_md_table(
                ["Page", "Test", "Key", "Run 1", "Run 2", "Run 3", "Source"],
                [
                    [
                        f["page"],
                        f["test"],
                        f["key"],
                        *[f["outcomes"][f"run{n}"] for n in RUNS],
                        f["source"],
                    ]
                    for f in cs[key]["flipped"]
                ],
            ),
        ]
    L += [
        "`source`: `judge` = an answer (the agent's for A, the server judge's for C) decided the cell in at least one run; `scan` = only the rules' own evidence changed between loads.",
        "",
    ]
    ct = o["cost_time"]
    L += [
        "## Cost and time",
        "",
        *_md_table(
            [
                "Run",
                "List price $",
                "Tokens in / out / cache read / cache write",
                "Wall s",
                "Model calls",
                "Per page $",
                "Per page s",
            ],
            [
                *[
                    [
                        f"A run {n}",
                        ct["a"][f"run{n}"]["cost_usd_list_price"],
                        " / ".join(str(ct["a"][f"run{n}"]["tokens"][k]) for k in TOK),
                        ct["a"][f"run{n}"]["wall_s"],
                        ct["a"][f"run{n}"]["model_calls"],
                        ct["a"][f"run{n}"]["per_page_cost_usd"],
                        ct["a"][f"run{n}"]["per_page_wall_s"],
                    ]
                    for n in RUNS
                ],
                *[
                    [
                        f"B run {n}",
                        ct["b"][f"run{n}"]["cost_usd_list_price"],
                        " / ".join(str(ct["b"][f"run{n}"]["tokens"][k]) for k in TOK),
                        ct["b"][f"run{n}"]["wall_s"],
                        ct["b"][f"run{n}"]["model_calls"],
                        ct["b"][f"run{n}"]["per_page_cost_usd"],
                        ct["b"][f"run{n}"]["per_page_wall_s"],
                    ]
                    for n in RUNS
                ],
            ],
        ),
    ]
    L += [
        "C's judge, per run (the CLI route records tokens, not a price; the dollar figure is an estimate at the rates A's and B's own list prices imply, residual "
        f"{ct['price_fit']['max_abs_residual_usd']} over {ct['price_fit']['groups_fitted']} groups: {ct['price_fit']['usd_per_mtok']} $/Mtok):",
        "",
        *_md_table(
            [
                "Run",
                "Judge calls",
                "Failed/retried",
                "Questions",
                "Answered",
                "Unsure",
                "Left open",
                "Tokens in / out / cache read / cache write",
                "Judge s (summed)",
                "Call wall s (browser + judge)",
                "Est. judge $",
                "Per page est. $",
                "Per page wall s",
            ],
            [
                [
                    f"C run {n}",
                    ct["c"][f"run{n}"]["judge_calls"],
                    f"{ct['c'][f'run{n}']['failed_calls']}/{ct['c'][f'run{n}']['retried_calls']}",
                    ct["c"][f"run{n}"]["questions"],
                    ct["c"][f"run{n}"]["answered"],
                    ct["c"][f"run{n}"]["unsure"],
                    ct["c"][f"run{n}"]["left_open"],
                    " / ".join(str(ct["c"][f"run{n}"]["tokens"][k]) for k in TOK),
                    ct["c"][f"run{n}"]["judge_seconds_in_calls_summed"],
                    ct["c"][f"run{n}"]["call_wall_s"],
                    ct["c"][f"run{n}"]["estimated_judge_cost_usd"],
                    ct["c"][f"run{n}"]["per_page_estimated_cost_usd"],
                    ct["c"][f"run{n}"]["per_page_call_wall_s"],
                ]
                for n in RUNS
            ],
        ),
    ]
    return "\n".join(L)


def main() -> None:
    o = build()
    (HERE / "compare.json").write_text(
        json.dumps(o, indent=1, default=str) + "\n", encoding="utf-8"
    )
    (HERE / "compare.md").write_text(markdown(o), encoding="utf-8")
    print("wrote compare.json and compare.md")


if __name__ == "__main__":
    main()
