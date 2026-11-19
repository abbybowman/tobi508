"""The live log: what the server is doing, as it happens, for a demo.

Off by default (settings.live_log). When on, it keeps the last MAX_EVENTS
events in memory, never on disk, and GET /live shows them to anyone who
holds LIVE_LOG_TOKEN (routes.py):

  * "call": an MCP request (a tool call, resource read or prompt) with its
    full arguments and the caller;
  * "result": its response, text trimmed to MAX_TEXT characters, pictures
    kept (base64) up to MAX_IMAGE bytes each; or "error";
  * "step": a run's step log line (RunRecorder.log, already redacted);
  * "progress": a running job's progress line (jobs.Job.progress).

Unlike the audit lines, it holds page text, evidence and answers, for every
caller (2026-11-18: demo only, off by default). It decides nothing and
changes no result: a failure here is swallowed, never raised into a call.
"""

from __future__ import annotations

import base64
import hmac
import itertools
import json
import time
from collections import deque
from typing import Any

from fastmcp.server.middleware import Middleware

from tobi508 import access
from tobi508.config import settings
from tobi508.redact import safe_error

MAX_EVENTS = 2000
MAX_TEXT = 20_000
MAX_IMAGE = 400_000  # bytes of a picture kept; larger ones are named only

_EVENTS: deque[dict[str, Any]] = deque(maxlen=MAX_EVENTS)
_SEQ = itertools.count(1)


def enabled() -> bool:
    return bool(settings.live_log)


def token_ok(given: str | None) -> bool:
    """The page and its events open only with the configured token."""
    want = settings.live_log_token
    if not (enabled() and want and given):
        return False
    return hmac.compare_digest(given.encode(), want.get_secret_value().encode())


def emit(kind: str, **fields: Any) -> None:
    """Add one event (no-op when the live log is off)."""
    if not enabled():
        return
    try:
        _EVENTS.append({"seq": next(_SEQ), "ts": time.time(), "kind": kind, **fields})
    except Exception:  # never let the demo log break a call
        pass


def events_after(seq: int, limit: int = 200) -> list[dict[str, Any]]:
    return [e for e in list(_EVENTS) if e["seq"] > seq][:limit]


def clear() -> None:
    _EVENTS.clear()


def _trim(text: str) -> dict[str, Any]:
    if len(text) <= MAX_TEXT:
        return {"text": text}
    return {"text": text[:MAX_TEXT], "more_chars": len(text) - MAX_TEXT}


def _image(mime: str, data_b64: str) -> dict[str, Any]:
    size = len(data_b64) * 3 // 4
    if size > MAX_IMAGE or not mime.startswith("image/"):
        return {"mime": mime, "bytes": size}
    return {"mime": mime, "bytes": size, "data": data_b64}


def _blocks(content: list[Any]) -> list[dict[str, Any]]:
    """MCP content blocks as text parts and pictures."""
    out: list[dict[str, Any]] = []
    for b in content or []:
        kind = getattr(b, "type", "")
        if kind == "text":
            out.append({"type": "text", **_trim(b.text)})
        elif kind == "image":
            out.append({"type": "image", **_image(b.mimeType, b.data)})
        else:
            out.append({"type": kind or type(b).__name__})
    return out


def _resource_blocks(result: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c in getattr(result, "contents", None) or []:
        body, mime = c.content, c.mime_type or ""
        if isinstance(body, bytes):
            b64 = base64.b64encode(body).decode()
            out.append(
                {
                    "type": "image" if mime.startswith("image/") else "bytes",
                    **_image(mime, b64),
                }
            )
        else:
            text = body if isinstance(body, str) else json.dumps(body, default=str)
            out.append({"type": "text", "mime": mime, **_trim(text)})
    return out


class LiveLogMiddleware(Middleware):
    """Records each MCP request and its response while the live log is on."""

    async def _watch(self, call: dict[str, Any], run, render):
        if not enabled():
            return await run()
        call_id = next(_SEQ)
        emit("call", call=call_id, who=access.caller(), **call)
        t0 = time.monotonic()
        try:
            result = await run()
        except Exception as exc:
            emit(
                "error",
                call=call_id,
                seconds=round(time.monotonic() - t0, 2),
                error=safe_error(exc),
                **{k: call[k] for k in call if k != "arguments"},
            )
            raise
        try:
            parts = render(result)
        except Exception as exc:  # a shape we did not expect: say so
            parts = [{"type": "text", "text": f"(not shown: {type(exc).__name__})"}]
        emit(
            "result",
            call=call_id,
            seconds=round(time.monotonic() - t0, 2),
            is_error=bool(getattr(result, "is_error", False)),
            parts=parts,
            **{k: call[k] for k in call if k != "arguments"},
        )
        return result

    async def on_call_tool(self, context, call_next):
        m = context.message
        return await self._watch(
            {"action": "tool", "name": m.name, "arguments": m.arguments or {}},
            lambda: call_next(context),
            lambda r: _blocks(r.content),
        )

    async def on_read_resource(self, context, call_next):
        return await self._watch(
            {"action": "resource", "name": str(context.message.uri)},
            lambda: call_next(context),
            _resource_blocks,
        )

    async def on_get_prompt(self, context, call_next):
        m = context.message
        return await self._watch(
            {"action": "prompt", "name": m.name, "arguments": m.arguments or {}},
            lambda: call_next(context),
            lambda r: [{"type": "text", **_trim(str(r))}],
        )
