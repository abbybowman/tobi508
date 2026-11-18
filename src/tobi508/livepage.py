"""The /live page: the live log (livelog.py) in a browser, for a demo.

A static shell (live/index.html), its script and stylesheet; the events come
from /live/events with the token in the X-Live-Token header (the page reads
it from the address's fragment, #token=..., which browsers never send, so it
stays out of access logs). Every value from an event is shown as text
(textContent), never as HTML: it holds page text. A picture is shown only as
a data: URL of a PNG, JPEG, GIF or WebP whose data is plain base64.
"""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent / "live"

CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src data:; "
    "connect-src 'self'; base-uri 'none'; form-action 'none'; "
    "frame-ancestors 'none'"
)

FILES = {
    "/live": ("index.html", "text/html"),
    "/live/app.js": ("app.js", "text/javascript"),
    "/live/app.css": ("app.css", "text/css"),
}


def read(path: str) -> tuple[str, str]:
    """(body, media type) of one of the page's files."""
    name, media = FILES[path]
    return (HERE / name).read_text(encoding="utf-8"), media
