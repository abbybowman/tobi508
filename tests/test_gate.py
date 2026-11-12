"""The ApiJudge gate's pure parts (evals/apijudge_gate.py, evals/scoring.py):
which cells a server answer decided, how they are counted and when a type
passes. No browser, no model."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace as NS

from tobi508.models import Answer, ChoiceAnswer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evals.apijudge_gate import eval_by_type, passes  # noqa: E402
from evals.scoring import Verdict, decided_tests, split_cells  # noqa: E402


def rec(qid: str, by: str, choice: str = "yes"):
    return NS(
        answer=Answer(
            question_id=qid,
            choice=ChoiceAnswer(choice=choice, reasons="r"),
            rationale="r",
            seen="s",
            answered_by=by,
        )
    )


def test_a_cell_is_decided_only_by_a_server_answer_in_force():
    report = NS(
        answers=[
            rec("4.A-k1-J1", "client"),
            rec("4.A-k1-J1", "server:m"),  # the later answer is in force
            rec("5.B-f1-J1", "client"),  # an agent's, not the judge's
            rec("4.D-i1-J1", "server:m", "unsure"),
        ]
    )
    assert decided_tests(report) == {"4.A": 1, "4.D": 1}
    # the client's answer comes last: the server's is no longer in force
    later = NS(answers=[rec("4.A-k1-J1", "server:m"), rec("4.A-k1-J1", "client")])
    assert decided_tests(later) == {}


def score(**verdicts: Verdict):
    return NS(
        tests=[
            NS(test=NS(test_id=t.replace("_", ".")), verdict=v)
            for t, v in verdicts.items()
        ]
    )


def test_split_cells_counts_only_decided_cells_by_gate_word():
    scores = {
        "pageA": score(**{"4_A": Verdict.AGREE, "5_B": Verdict.FALSE_PASS}),
        "pageB": score(**{"4_A": Verdict.FALSE_FAIL, "5_B": Verdict.MISSED_FAIL}),
        "pageC": score(**{"4_A": Verdict.NOT_PERFORMED}),
    }
    decided = {"pageA": {"4.A": 1}, "pageB": {"4.A": 2, "5.B": 1}, "pageC": {"4.A": 1}}
    got = split_cells(scores, decided)
    # pageA's 5.B cell was not decided by an answer: not counted
    assert got["4.A"]["cells"] == 3
    assert (got["4.A"]["agree"], got["4.A"]["wrong_fail"]) == (1, 1)
    assert got["4.A"]["unsure"] == 1  # left for a person: not performed
    assert got["5.B"]["cells"] == 1 and got["5.B"]["wrong_dna"] == 1
    assert got["5.B"]["wrong_pass"] == 0  # the FALSE_PASS cell was undecided


def row(cells=10, **kw):
    return {
        "cells": cells,
        "agree": cells - sum(kw.values()),
        "wrong_pass": 0,
        "wrong_dna": 0,
        "wrong_fail": 0,
        "pass_vs_dna": 0,
        "unsure": 0,
        "other": 0,
    } | kw


def test_the_gate_rule():
    cells = {
        "4.A": row(),
        "5.B": row(wrong_pass=1),
        "4.D": row(wrong_fail=1),
        "5.D": row(wrong_fail=3),
        "2.D": row(),
        "9.A": row(),
    }
    fails = {"4.A": [0, 0, 0], "4.D": [1, 0, 0], "5.D": [3], "2.D": [2], "9.A": [0]}
    eval_ok = {"4.A": True, "5.B": True, "4.D": True, "5.D": True, "2.D": True}
    got = passes(cells, fails, eval_ok)
    assert got["4.A"]["passes"]
    assert not got["5.B"]["passes"] and "wrong PASS" in got["5.B"]["why_not"][0]
    assert got["4.D"]["passes"]  # one wrong FAIL in a repeat, 10% of cells
    assert not got["5.D"]["passes"]  # over 1 a repeat and over 20%
    assert not got["2.D"]["passes"]  # 2 in one repeat
    assert "the test pages were not run" in got["9.A"]["why_not"]
    # the test pages decide too: a wrong PASS there, or no eval at all
    assert not passes(cells, fails, {**eval_ok, "4.A": False})["4.A"]["passes"]
    assert not passes(cells, fails, None)["4.A"]["passes"]


def test_too_few_decided_cells_or_any_wrong_dna_fails_a_type():
    """L-02, L-03: one clean cell, or a type mostly left unsure, is too few to
    judge; one wrong DOES NOT APPLY fails a type; a PASS against a DOES NOT
    APPLY key is counted apart and is not a reason by itself."""
    eval_ok = dict.fromkeys(("4.A", "5.B", "4.D", "5.D", "2.D"), True)
    cells = {
        "4.A": row(cells=1),
        "5.B": row(cells=10, unsure=5),  # 5 decided
        "4.D": row(cells=10, wrong_dna=1),
        "5.D": row(cells=10, pass_vs_dna=2),
        "2.D": row(cells=12, unsure=6, wrong_fail=2),  # 2 of 6 decided: 33%
    }
    got = passes(cells, {}, eval_ok)
    assert not got["4.A"]["passes"]
    assert got["4.A"]["why_not"] == ["too few cells to judge: 1 decided, 6 needed"]
    assert not got["5.B"]["passes"] and got["5.B"]["decided"] == 5
    assert "too few cells to judge" in got["5.B"]["why_not"][0]
    assert got["4.D"]["why_not"] == ["1 wrong DOES NOT APPLY on the real pages"]
    assert got["5.D"]["passes"] and got["5.D"]["pass_vs_dna"] == 2
    # the 20% share is of decided cells, not of cells left unsure
    assert got["2.D"]["why_not"] == ["wrong FAILs over 20% of the type's decided cells"]


def test_split_cells_counts_a_pass_against_a_dna_key_apart():
    from tobi508.scrt import ScrtResult as R

    def cell(key, tool):
        return NS(
            test=NS(test_id="4.A", first=NS(result=key), second=NS(result=tool)),
            verdict=Verdict.OTHER,
        )

    scores = {
        "p": NS(tests=[cell(R.DNA, R.PASS)]),
        "q": NS(tests=[cell(R.PASS, R.DNA)]),
    }
    got = split_cells(scores, {"p": {"4.A": 1}, "q": {"4.A": 1}})["4.A"]
    assert (got["pass_vs_dna"], got["other"], got["cells"]) == (1, 1, 2)


def test_eval_results_with_a_wrong_pass_or_the_bait_fail_the_type(tmp_path):
    (tmp_path / "api-results-1.json").write_text(
        '{"a": %s, "b": %s}'
        % (
            '{"tt": "4.A", "wrong_pass": false, "took_the_bait": false}',
            '{"tt": "5.B", "wrong_pass": false, "took_the_bait": true}',
        )
    )
    (tmp_path / "api-results-2.json").write_text(
        '{"c": {"tt": "4.A", "wrong_pass": true, "took_the_bait": false}}'
    )
    assert eval_by_type(tmp_path) == {"4.A": False, "5.B": False}
