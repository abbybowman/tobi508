"""Redaction for tool errors and logs (GSA template: "Error Handling").

Tool errors, `RunResult.errors` and the run log (steps.jsonl) must not carry
query strings, fragments, credentials in URLs, request headers, stack traces
or page text. The saved report keeps the full target URL (the user's record).

Rules:
  * URLs keep scheme, host, port and path; userinfo, query and fragment go.
  * Error text is one line: the exception type plus the first line of its
    message with URLs redacted, cut at 200 characters. Playwright's "Call
    log:" (request headers) and anything after the first line is dropped.
  * A message from a page (a script error, evaluate result) is not trusted
    to be short or clean, so the same rules apply to every exception.
"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urlsplit, urlunsplit

MAX_ERROR = 200
_URL = re.compile(r"""\b(?:https?|wss?|file)://[^\s"'<>`)\]}]+""", re.IGNORECASE)


def safe_url(url: str) -> str:
    """scheme://host[:port]/path, without userinfo, query or fragment."""
    try:
        p = urlsplit(url)
        host = p.hostname or ""
        if ":" in host:
            host = f"[{host}]"
        port = f":{p.port}" if p.port else ""
    except ValueError:
        return "<unparseable URL>"
    return urlunsplit((p.scheme, host + port, p.path, "", ""))


def scrub(text: str) -> str:
    """Redact every URL in free text."""
    return _URL.sub(lambda m: safe_url(m.group(0)), text)


class AccessLogWithoutQuery(logging.Filter):
    """Uvicorn's access log, each path without its query string. The
    sign-in callback's query carries a one-time code from the identity
    provider (seen in the log on VAST); the path and status
    stay, since they are what a failed sign-in is diagnosed by."""

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        # uvicorn's access record: (client, method, path, http version, status)
        if isinstance(args, tuple) and len(args) == 5 and isinstance(args[2], str):
            record.args = (*args[:2], args[2].split("?", 1)[0], *args[3:])
        return True


def strip_queries_from_access_log() -> None:
    """Install the filter once on uvicorn's access logger. Uvicorn's own
    logging setup, which runs later at startup, replaces the logger's
    handlers but keeps its filters (tests/test_leakage.py)."""
    log = logging.getLogger("uvicorn.access")
    if not any(isinstance(f, AccessLogWithoutQuery) for f in log.filters):
        log.addFilter(AccessLogWithoutQuery())


def safe_error(exc: BaseException) -> str:
    """One redacted line describing an exception, for errors and logs."""
    msg = str(exc).split("Call log:", 1)[0].strip()
    first = msg.splitlines()[0] if msg else ""
    out = f"{type(exc).__name__}: {scrub(first)}" if first else type(exc).__name__
    return out if len(out) <= MAX_ERROR else out[: MAX_ERROR - 1] + "…"


def safe_detail(value: Any) -> Any:
    """Redact URLs in every string of a log entry's detail, recursively."""
    if isinstance(value, str):
        return scrub(value)
    if isinstance(value, dict):
        return {k: safe_detail(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_detail(v) for v in value]
    if isinstance(value, BaseException):
        return safe_error(value)
    return value
