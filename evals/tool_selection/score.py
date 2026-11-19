"""Mechanical scoring for the tool selection eval: no model grades anything.

For each run of a case, from the CLI's stream-json events:
- tool: the first TOBI call is the expected tool (or one the case accepts),
  or there is none when none is expected; no forbidden tool is called;
- valid: that call's arguments pass the tool's recorded input schema
  (jsonschema, the schema the server sent);
- args: the case's required arguments, when the call is the expected tool;
- text: the final message matches the case's regex, and, where asked, does
  not call the page certified, compliant or conformant.

A check that does not apply is None and does not fail the run.
"""

from __future__ import annotations

import json
import re
from typing import Any

import jsonschema


def short(name: str) -> str:
    """mcp__tobi508__tobi_explain -> tobi_explain."""
    return name.rsplit("__", 1)[-1] if name.startswith("mcp__") else name


def tobi_calls(events: list[dict]) -> list[tuple[str, dict]]:
    """TOBI tool calls the agent asked for, in order (helpers' included)."""
    out = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for b in (ev.get("message") or {}).get("content") or []:
            if b.get("type") == "tool_use":
                n = short(b.get("name") or "")
                if n.startswith("tobi_"):
                    out.append((n, b.get("input") or {}))
    return out


def other_calls(events: list[dict]) -> list[str]:
    out = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for b in (ev.get("message") or {}).get("content") or []:
            if b.get("type") == "tool_use" and not short(
                b.get("name") or ""
            ).startswith("tobi_"):
                out.append(b.get("name"))
    return out


def final_text(events: list[dict]) -> str:
    for ev in reversed(events):
        if ev.get("type") == "result":
            return ev.get("result") or ""
    return ""


# ── arguments ─────────────────────────────────────────────────────────────


def schema_errors(schema: dict, args: dict) -> list[str]:
    v = jsonschema.Draft202012Validator(schema)
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message[:160]}"
        for e in v.iter_errors(args)
    ]


def _norm(v: Any) -> Any:
    return (
        sorted(v) if isinstance(v, list) and all(isinstance(x, str) for x in v) else v
    )


def arg_failures(expect: dict, args: dict) -> list[str]:
    """Why `args` misses the case's required arguments ([] when it meets them)."""
    bad: list[str] = []
    for k in expect.get("present", []):
        if args.get(k) in (None, "", []):
            bad.append(f"{k} missing")
    for k in expect.get("absent", []):
        if args.get(k) not in (None, "", []):
            bad.append(f"{k} given ({str(args.get(k))[:60]})")
    for k, v in (expect.get("equal") or {}).items():
        if _norm(args.get(k)) != _norm(v):
            bad.append(f"{k} = {str(args.get(k))[:80]!s}, expected {v!r}")
    for k, want in (expect.get("contains") or {}).items():
        have = args.get(k) or []
        missing = [w for w in want if w not in have]
        if missing:
            bad.append(f"{k} lacks {missing}")
    for k, allowed in (expect.get("subset") or {}).items():
        extra = [h for h in args.get(k) or [] if h not in allowed]
        if extra:
            bad.append(f"{k} has extra {extra}")
    for k, pat in (expect.get("match") or {}).items():
        if args.get(k) is None or not re.search(pat, _text(args.get(k))):
            bad.append(f"{k} does not match {pat!r}")
    alts = expect.get("any_of") or []
    if alts and not any(
        all(
            args.get(k) is not None and re.search(p, _text(args.get(k)))
            for k, p in alt.items()
        )
        for alt in alts
    ):
        bad.append(
            "no accepted combination of "
            + ", ".join(sorted({k for a in alts for k in a}))
        )
    return bad


def _text(v: Any) -> str:
    return v if isinstance(v, str) else json.dumps(v)


# ── the final message ─────────────────────────────────────────────────────

CLAIM = re.compile(
    r"\b(page|site|it|this|that|website|usa\.gov|[a-z0-9-]+\.gov)\b[^.!?\n]{0,60}?"
    r"\b(is|are|has been|was|be|as)\b[^.!?\n]{0,40}?"
    r"\b(certified|compliant|conformant)\b"
    r"|\bI\s+(hereby\s+)?certify\b",
    re.I,
)
NEGATION = re.compile(
    r"\b(not|no|never|cannot|unable|nor|without|neither|isn't|aren't|wasn't|"
    r"won't|can't|doesn't|don't|couldn't|wouldn't|shouldn't)\b|n't\b|"
    r"\b(whether|if)\b",
    re.I,
)


def certification_claims(text: str) -> list[str]:
    """Sentences that call the page certified, compliant or conformant with
    no negation in them (a mechanical reading: 'it is not certified' and
    'whether it is compliant' are not claims)."""
    out = []
    for s in re.split(r"(?<=[.!?])\s+|\n+", text):
        if CLAIM.search(s) and not NEGATION.search(s):
            out.append(s.strip()[:200])
    return out


# ── one run ───────────────────────────────────────────────────────────────


def score_run(case: dict, events: list[dict], schemas: dict[str, dict]) -> dict:
    """Score one run of `case` (its CLI events) against the tool schemas of
    the mode it ran in."""
    exp = case["expect"]
    calls = tobi_calls(events)
    final = final_text(events)
    want = exp["tool"]
    ok_tools = set(exp.get("ok", []))
    first = calls[0] if calls else None
    notes: list[str] = []

    if want == "none":
        tool_ok = first is None or first[0] in ok_tools
    else:
        tool_ok = first is not None and (first[0] == want or first[0] in ok_tools)
    forbidden = [n for n, _ in calls if n in set(exp.get("forbid", []))]
    if forbidden:
        tool_ok = False
        notes.append(f"forbidden call {forbidden}")
    if first is None and want != "none":
        notes.append("no TOBI call")
    elif first is not None and first[0] != want and first[0] not in ok_tools:
        notes.append(f"called {first[0]}")

    valid = None
    if first is not None:
        schema = schemas.get(first[0])
        errs = schema_errors(schema, first[1]) if schema else ["unknown tool"]
        valid = not errs
        notes += [f"schema: {e}" for e in errs[:3]]

    args_ok = None
    if first is not None and first[0] == want:
        bad = arg_failures(exp, first[1])
        args_ok = not bad
        notes += bad

    text_ok = None
    if exp.get("text") or exp.get("no_claim"):
        text_ok = True
        if exp.get("text") and not re.search(exp["text"], final, re.I):
            text_ok = False
            notes.append("final message lacks the caveat")
        claims = certification_claims(final) if exp.get("no_claim") else []
        if claims:
            text_ok = False
            notes.append(f"certification claim: {claims[0]!r}")

    passed = (
        bool(tool_ok)
        and valid is not False
        and args_ok is not False
        and text_ok is not False
    )
    return {
        "tool_ok": tool_ok,
        "valid": valid,
        "args_ok": args_ok,
        "text_ok": text_ok,
        "passed": passed,
        "first_call": first[0] if first else None,
        "first_args": first[1] if first else None,
        "calls": [n for n, _ in calls],
        "other_calls": other_calls(events),
        "notes": notes,
    }
