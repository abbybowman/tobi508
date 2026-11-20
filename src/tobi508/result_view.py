"""How a run's result is shaped for the calling agent.

A run's full report can be hundreds of kilobytes; an MCP client passes on
about 45,000 characters of a tool result before it hides the rest. This module
builds what tobi_run_tt_tests and tobi_answer_questions return around the
report: up to ten open questions, with a question and rubric that several
share given once; only the page text and shared evidence those questions
need; and, when that is still too long, fewer questions or text cut to the
passages the questions quote (fit). Every cut says so, and the report keeps
everything whole. It shapes output only and decides nothing. The server's
judge (apijudge.py) reuses the evidence helpers to build its own requests.
"""

from __future__ import annotations

import json
from typing import Any

from tobi508.checks import REGISTRY
from tobi508.models import OpenQuestion, Report, TestId
from tobi508.next_steps import QUESTION_PAGE, next_step, todo
from tobi508.resources.runs import run_uri
from tobi508.runlog import RunRecorder
from tobi508.walk import KeyboardWalk


def _walk_summary(walk: KeyboardWalk) -> dict[str, Any]:
    def one(p):
        return {"end": p.end, "presses": len(p.steps), "cap": p.cap}

    return {"P1": one(walk.p1), "P2": one(walk.p2)}


def _evidence_uris(run: RunRecorder) -> list[str]:
    """The report and the evidence files. Pictures are not listed: the
    questions and the report name the ones that matter (post-round 1 fix 6b:
    a large page's list of pictures was 13k characters)."""
    files = [run.report_path] + sorted(run.evidence_dir.glob("*.json"))
    return [run_uri(run.run_id, run.rel(f)) for f in files if f.exists()]


# What one result's text may be, in characters (round 2). Claude
# Code passes an MCP result on only up to two limits: about 25k tokens
# (MAX_MCP_OUTPUT_TOKENS), and about 50 KB of text, over which it saves the
# result to a file and shows the agent a 2 KB preview (CLI 2.1.319: a 51.2 KB
# result was saved, 37 KB passed). An agent that reads the file gets no
# pictures. Round 2's first runs lost 140 open questions to results of
# 85-469k characters (one page's text for 4.B, and shared inputs built for
# every open question, not only those shown), and a 51 KB result lost 62
# more. Pictures get what the text leaves (inline.py).
RESULT_CHARS = 45_000
# A long text the shown questions need is cut to the passages around what
# they quote, this many characters each side.
EXCERPT_SIDE = 600


def _quoted(value: Any) -> list[str]:
    """Strings of 20 characters or more in a question input."""
    if isinstance(value, str):
        return [value] if len(value) >= 20 else []
    if isinstance(value, dict):
        return [s for v in value.values() for s in _quoted(v)]
    if isinstance(value, list):
        return [s for v in value for s in _quoted(v)]
    return []


def _excerpt(text: str, quotes: list[str], budget: int) -> str:
    """The passages of `text` around each quote, in page order, joined by
    " [...] ", within `budget` characters; the text's start when none is
    found. Words are never changed, only left out."""
    spans: list[list[int]] = []
    for qt in quotes:
        i = text.find(qt.strip())
        while i >= 0 and len(spans) < 200:
            spans.append([max(0, i - EXCERPT_SIDE), i + len(qt) + EXCERPT_SIDE])
            i = text.find(qt.strip(), i + 1)
    if not spans:
        return text[:budget]
    spans.sort()
    merged = [spans[0]]
    for a, b in spans[1:]:
        if a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    out, used = [], 0
    for a, b in merged:
        part = text[a:b]
        if used + len(part) > budget:
            part = part[: max(0, budget - used)]
        if part:
            out.append(part)
            used += len(part)
        if used >= budget:
            break
    return " [...] ".join(out)


# Characters kept of a long string in shared inputs when a result is cut:
# first the longer, then, if a result is still too long, the shorter.
SHORT_STRINGS = (160, 60)
# Fewer questions than this are shown uncut only after cutting was tried.
MIN_UNCUT = 5


def _shorten(value: Any, keep: int) -> Any:
    """Strings longer than `keep` cut, ending with " [...]"."""
    if isinstance(value, str) and len(value) > keep:
        return value[:keep] + " [...]"
    if isinstance(value, dict):
        return {k: _shorten(v, keep) for k, v in value.items()}
    if isinstance(value, list):
        return [_shorten(v, keep) for v in value]
    return value


def fit(result: Any, report: Report, states: dict[TestId, Any]) -> Any:
    """`result` (a RunResult or AnswerResult) cut to RESULT_CHARS, by steps:
    up to 10 open questions, and evidence (page text, shared inputs) only for
    those shown; then fewer questions, down to MIN_UNCUT; then the page text
    cut to the passages around what the shown questions quote and long
    strings in shared inputs cut (SHORT_STRINGS), with 10 questions down to
    one. Each cut says so in the result; the rest of the questions come with
    the next answer result (more_questions). The report and the questions'
    own inputs are never cut. Decides nothing."""
    qs = report.open_questions
    calls = report.follow_up_calls

    def size(r: Any) -> int:
        return len(r.model_dump_json(exclude={"report"}))

    def build(n: int, keep: int | None = None) -> Any:
        shown = qs[:n]
        qview = _question_view(shown)
        page = _page_text(report, states, shown)
        shared = _shared_inputs(report, states, shown)
        if keep is not None:
            shared = (
                {
                    **_shorten(shared, keep),
                    "cut": f"Text over {keep} characters in these inputs is cut, "
                    "ending with [...]: the whole result was too long. The "
                    "report has it whole.",
                }
                if shared
                else shared
            )
            rest = (
                size(build(n))
                - len(json.dumps(page))
                - len(json.dumps(_shared_inputs(report, states, shown)))
                + len(json.dumps(shared))
            )
            # 80%: JSON escapes (newlines, non-ASCII) lengthen the text.
            room = max(1_500, (RESULT_CHARS - rest) * 4 // 5) // max(1, len(page))
            quotes = [t for q in shown for t in _quoted(q.input)]
            page = [
                p
                if len(p.get("text", "")) <= room
                else {
                    **p,
                    "text": _excerpt(p["text"], quotes, room),
                    "excerpt": f"The whole text is {len(p['text']):,} characters, "
                    "too long for one result: these are the passages around "
                    "what the open questions quote, joined by [...].",
                }
                for p in page
            ]
        return result.model_copy(
            update={
                "open_questions": qview[0],
                "question_texts": qview[1],
                "page_text": page,
                "shared_inputs": shared,
                "next_step": next_step(report, calls, shown=n),
                "todo": todo(report, calls, shown=n),
                "more_questions": max(0, len(qs) - n),
            }
        )

    top = min(QUESTION_PAGE, len(qs))
    out = build(top)
    if not qs or size(out) <= RESULT_CHARS:
        return out
    for n in range(top - 1, MIN_UNCUT - 1, -1):
        out = build(n)
        if size(out) <= RESULT_CHARS:
            return out
    for keep in SHORT_STRINGS:
        for n in range(top, 0, -1):
            out = build(n, keep)
            if size(out) <= RESULT_CHARS:
                return out
    return out


def _compact(v: Any) -> Any:
    """A question input as sent: floats to one decimal, None and empty
    values left out of objects. Text is never changed."""
    if isinstance(v, float):
        r = round(v, 1)
        return int(r) if r == int(r) else r
    if isinstance(v, dict):
        return {
            k: _compact(x)
            for k, x in v.items()
            if x is not None and x != [] and x != {}
        }
    if isinstance(v, list):
        return [_compact(x) for x in v]
    return v


def _question_view(
    qs: list[OpenQuestion],
) -> tuple[list[OpenQuestion], dict[str, dict[str, str]]]:
    """Open questions for a result, with each question and rubric that
    several share given once in question_texts (post-round 1 fix 6b: 56 of
    a page's questions repeated one text). The report keeps them whole."""
    counts: dict[tuple[str, str], int] = {}
    for q in qs:
        counts[(q.question, q.rubric)] = counts.get((q.question, q.rubric), 0) + 1
    keys: dict[tuple[str, str], str] = {}
    texts: dict[str, dict[str, str]] = {}
    out = []
    for q in qs:
        # A picture already in the input is not listed again, coordinates
        # are rounded and empty fields dropped (change 2b; the report keeps
        # the input as recorded).
        named = json.dumps(q.input)
        paths = [p for p in q.evidence_paths if f'"{p}"' not in named]
        q = q.model_copy(update={"evidence_paths": paths, "input": _compact(q.input)})
        pair = (q.question, q.rubric)
        if counts[pair] < 2:
            out.append(q)
            continue
        if pair not in keys:
            base = f"{q.test_id.value}-{q.question_id.rsplit('-', 1)[-1]}"
            key, n = base, 2
            while key in texts:
                key, n = f"{base}-{n}", n + 1
            keys[pair] = key
            texts[key] = {"question": pair[0], "rubric": pair[1]}
        k = keys[pair]
        # A pointer, not an empty field: judge eval run 20's agent missed
        # question_texts when the fields were blank.
        see = f'Shared with other questions: read question_texts["{k}"]'
        view = {"question": f"{see}.question.", "rubric": f"{see}.rubric.", "texts": k}
        out.append(q.model_copy(update=view))
    return out, texts


def _shared_inputs(
    report: Report, states: dict[TestId, Any], qs: list[OpenQuestion] | None = None
) -> dict[str, Any]:
    """Evidence the open questions share, once per result (a check's optional
    `shared_inputs(state)`), limited to the keys the questions shown (`qs`,
    default all open questions) name."""
    qs = report.open_questions if qs is None else qs
    wanted = {k for q in qs for k in q.shared}
    out: dict[str, Any] = {}
    for t in {q.test_id for q in qs}:
        check = REGISTRY.get(t)
        if check is not None and t in states and hasattr(check, "shared_inputs"):
            out.update(
                {k: v for k, v in check.shared_inputs(states[t]).items() if k in wanted}
            )
    return out


def _page_text(
    report: Report, states: dict[TestId, Any], qs: list[OpenQuestion] | None = None
) -> list[dict[str, str]]:
    asking = {q.test_id for q in (report.open_questions if qs is None else qs)}
    out: list[dict[str, str]] = []
    for t in asking:
        check = REGISTRY.get(t)
        if check is not None and t in states and hasattr(check, "page_text"):
            out += check.page_text(states[t])
    return out
