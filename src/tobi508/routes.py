"""Custom HTTP routes for the MCP server.

These are only active when the server runs over HTTP (streamable-http). They
sit alongside the `/mcp` endpoint on the same app.

Keep `/health` fast and dependency-free.
"""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from tobi508 import __version__, livelog, livepage

NO_STORE = {"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"}

# The pre-SCRT viewer, served as built (demo/prescrt-viewer/viewer.html; the
# image copies the repository and installs it editable). It opens only a file
# the person picks, in their own browser; it sends nothing anywhere.
VIEWER = Path(__file__).resolve().parents[2] / "demo" / "prescrt-viewer" / "viewer.html"
# The policy the file sets for itself in a meta tag (no request of any kind),
# plus frame-ancestors, which only a header can set.
VIEWER_CSP = (
    "default-src 'none'; img-src data:; style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'; "
    "frame-ancestors 'none'"
)


def register_routes(mcp: FastMCP) -> None:
    """Register custom HTTP routes with the server."""

    @mcp.custom_route("/health", methods=["GET"])
    async def health_check(request: Request) -> JSONResponse:
        return JSONResponse({"status": "healthy", "service": "tobi508"})

    @mcp.custom_route("/version", methods=["GET"])
    async def version(request: Request) -> JSONResponse:
        return JSONResponse({"version": __version__})

    # The live log (livelog.py): 404 unless LIVE_LOG is on with a token. The
    # page and its files hold nothing secret; the events need the token.
    async def live_file(request: Request) -> Response:
        if not (livelog.enabled() and livelog.settings.live_log_token):
            return Response("Not Found", status_code=404)
        body, media = livepage.read(request.url.path)
        headers = {
            **NO_STORE,
            "Content-Security-Policy": livepage.CSP,
            "X-Content-Type-Options": "nosniff",
        }
        return Response(body, media_type=media, headers=headers)

    for path in livepage.FILES:
        mcp.custom_route(path, methods=["GET"])(live_file)

    @mcp.custom_route("/live/events", methods=["GET"])
    async def live_events(request: Request) -> Response:
        if not livelog.token_ok(request.headers.get("x-live-token")):
            return Response("Not Found", status_code=404)
        try:
            after = int(request.query_params.get("after", "0"))
        except ValueError:
            after = 0
        return JSONResponse({"events": livelog.events_after(after)}, headers=NO_STORE)

    # The viewer: a static page, open like /health (it holds no data and
    # makes no request; the person loads their own file in their browser).
    @mcp.custom_route("/viewer", methods=["GET"])
    async def viewer(request: Request) -> Response:
        if not VIEWER.is_file():
            return Response("Not Found", status_code=404)
        headers = {
            **NO_STORE,
            "Content-Security-Policy": VIEWER_CSP,
            "X-Content-Type-Options": "nosniff",
        }
        return Response(
            VIEWER.read_text(encoding="utf-8"), media_type="text/html", headers=headers
        )
