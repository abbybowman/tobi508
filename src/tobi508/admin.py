"""The server's operator: list and cancel every caller's runs from inside the
server's container (`podman exec` or `kubectl exec`), never through MCP.

A tool caller can cancel only their own runs (tobi_cancel_run). The person
running the server sometimes needs more: in the 2026-11-20 demo a run nobody
could reach any more held the only browser slot, and a restart, which ends
every run, was the only way to free it.

How it is guarded:
  * Over HTTP, the server writes a fresh random token at start to
    ADMIN_TOKEN_FILE (default: the container's temp directory), mode 600.
    Nothing outside the container can read it, and a restart replaces it.
  * GET /admin/jobs and POST /admin/jobs/{job_id}/cancel answer only a
    request carrying that token (X-Admin-Token) and no proxy header (a
    request through the platform's gateway or ingress always carries one).
    Anything else is 404, as /live is without its token.
  * `tobi508-admin` (main, below) reads the file and calls the server on
    loopback, bypassing any HTTP proxy settings.
  * Each cancel writes an audit line. A listing shows each run's address
    without its query string and the signed-in subject who started it; no
    page content.

No outcome is decided here.
"""

from __future__ import annotations

import argparse
import contextlib
import hmac
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from tobi508 import jobs
from tobi508.access import audit
from tobi508.redact import safe_url

HEADER = "x-admin-token"
PROXY_HEADERS = ("x-forwarded-for", "x-forwarded-host", "forwarded", "x-real-ip")
NO_STORE = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}

_TOKEN: str | None = None


def write_token(path: Path) -> str:
    """A fresh token for this server process, written to `path` (mode 600)."""
    global _TOKEN
    token = secrets.token_urlsafe(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.suppress(FileNotFoundError):
        path.unlink()  # never write through a file someone else made
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(token)
    _TOKEN = token
    return token


def _allowed(request: Request) -> bool:
    if _TOKEN is None:
        return False
    if any(h in request.headers for h in PROXY_HEADERS):
        return False
    given = request.headers.get(HEADER, "")
    return hmac.compare_digest(given.encode(), _TOKEN.encode())


def _status(job: jobs.Job) -> str:
    t = job.task
    if t is None or not t.done():
        return "queued" if job.started is None else "running"
    if t.cancelled():
        return "cancelled"
    return "failed" if t.exception() is not None else "done"


def _line(job: jobs.Job) -> dict[str, Any]:
    now = time.monotonic()
    return {
        "job_id": job.id,
        "status": _status(job),
        "target": safe_url(job.url),
        "started_by": job.owner or "(no sign-in)",
        "minutes": round((now - job.created) / 60, 1),
        "progress": job.message,
        "cancelled_by": job.cancelled_by,
    }


def register_routes(mcp) -> None:
    """The admin routes, beside /health (routes.py)."""

    @mcp.custom_route("/admin/jobs", methods=["GET"])
    async def admin_jobs(request: Request) -> Response:
        if not _allowed(request):
            return Response("Not Found", status_code=404)
        return JSONResponse(
            {"jobs": [_line(j) for j in jobs.every_job()]}, headers=NO_STORE
        )

    @mcp.custom_route("/admin/jobs/{job_id}/cancel", methods=["POST"])
    async def admin_cancel(request: Request) -> Response:
        if not _allowed(request):
            return Response("Not Found", status_code=404)
        job = jobs.get_any(request.path_params.get("job_id", ""))
        if job is None:
            return JSONResponse(
                {"error": "no such job (a restart forgets every job)"},
                status_code=404,
                headers=NO_STORE,
            )
        was = await jobs.cancel(job, "the server's operator")
        audit(
            "admin.cancel",
            job_id=job.id,
            url=safe_url(job.url),
            started_by=job.owner,
            was=was,
        )
        return JSONResponse({"was": was, "job": _line(job)}, headers=NO_STORE)


# ── The command ──────────────────────────────────────────────────────────────


def _base(host: str, port: int) -> str:
    if host in ("::1", "::"):
        return f"http://[::1]:{port}"
    return f"http://127.0.0.1:{port}"


def _call(base: str, token: str, method: str, path: str) -> dict[str, Any]:
    req = urllib.request.Request(
        base + path, method=method, headers={"X-Admin-Token": token}
    )
    # Loopback only: never through an HTTP proxy from the environment.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            try:
                return json.loads(exc.read().decode("utf-8"))
            except ValueError:
                raise SystemExit(
                    "The server refused the token: is this the server's own "
                    "container, and did the server restart after this token "
                    "was written?"
                ) from None
        raise SystemExit(f"The server answered {exc.code}.") from None
    except urllib.error.URLError as exc:
        raise SystemExit(f"Cannot reach the server at {base}: {exc.reason}") from None


def _print_jobs(lines: list[dict[str, Any]]) -> None:
    if not lines:
        print("No runs since the server started.")
        return
    for j in lines:
        print(
            f"{j['job_id']}  {j['status']:<9}  {j['minutes']:>5} min  "
            f"{j['started_by']}  {j['target']}"
        )
        if j["status"] in ("queued", "running"):
            print(f"    {j['progress']}")


def main(argv: list[str] | None = None) -> None:
    """tobi508-admin: list or cancel the server's runs. Run it inside the
    server's container, for example `podman exec tobi uv run --no-sync
    tobi508-admin jobs`."""
    from tobi508.config import settings

    parser = argparse.ArgumentParser(
        prog="tobi508-admin",
        description="List or cancel this server's runs (every user's). Run "
        "inside the server's container.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("jobs", help="list runs: queued, running and recent")
    c = sub.add_parser("cancel", help="cancel a queued or running run")
    c.add_argument("job_id", help="a job id from `jobs`, such as job-580260490609")
    args = parser.parse_args(argv)

    try:
        token = settings.admin_token_file.read_text("utf-8").strip()
    except OSError:
        raise SystemExit(
            f"No admin token at {settings.admin_token_file}: run this "
            "inside the server's container while the server runs over HTTP."
        ) from None
    base = _base(settings.mcp_host, settings.mcp_port)
    if args.command == "jobs":
        _print_jobs(_call(base, token, "GET", "/admin/jobs").get("jobs", []))
        return
    out = _call(base, token, "POST", f"/admin/jobs/{args.job_id}/cancel")
    if "error" in out:
        raise SystemExit(f"{args.job_id}: {out['error']}")
    was = out["was"]
    if was == "finished":
        print(f"{args.job_id} had already ended; nothing was cancelled.")
    else:
        print(f"Cancelled {args.job_id} (it was {was}); nothing from it is kept.")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
