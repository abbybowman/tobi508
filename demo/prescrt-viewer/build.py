"""Build demo/prescrt-viewer/viewer.html: one self-contained file.

Inlines SCRT's stylesheet (third_party/scrt/CSS/acrt_styles.css, read and
never changed) and src/viewer.css and src/viewer.js into src/viewer.src.html.

    uv run python demo/prescrt-viewer/build.py          # write viewer.html
    uv run python demo/prescrt-viewer/build.py --check  # fail if out of date
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRT_CSS = ROOT / "third_party" / "scrt" / "CSS" / "acrt_styles.css"
OUT = HERE / "viewer.html"


def build() -> str:
    page = (HERE / "src" / "viewer.src.html").read_text("utf-8")
    parts = {
        "/*@@SCRT_CSS@@*/": SCRT_CSS.read_text("utf-8"),
        "/*@@VIEWER_CSS@@*/": (HERE / "src" / "viewer.css").read_text("utf-8"),
        "/*@@VIEWER_JS@@*/": (HERE / "src" / "viewer.js").read_text("utf-8"),
    }
    for marker, text in parts.items():
        if page.count(marker) != 1:
            raise SystemExit(f"{marker} must appear once in viewer.src.html")
        if "</style" in text.lower() or "</script" in text.lower():
            raise SystemExit(f"{marker}: text would close its element early")
        page = page.replace(marker, text)
    return page


def main(argv: list[str]) -> int:
    page = build()
    if "--check" in argv:
        if not OUT.exists() or OUT.read_text("utf-8") != page:
            print("viewer.html is out of date: run demo/prescrt-viewer/build.py")
            return 1
        return 0
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page.encode())} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
