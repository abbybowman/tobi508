"""Every rules spec whose text changed against a base commit has a higher
spec_version than it had there (CI, on every pull request and push to main).

Two branches can each bump a spec to the same next version; git merges the
two texts without a conflict and one version then stands for two rule sets
(4.A 1.6.0, 2026-11-12). GitHub runs a pull request's checks on the pull
request merged into main, so comparing with main's commit here catches a
branch that took a number main has since used, and a text changed with no
bump at all. specs/rules/versions.lock (tests/test_spec_versions.py) is the
local half of the same guard.

    uv run python scripts/check_spec_versions.py <base commit>
"""

from __future__ import annotations

import re
import subprocess
import sys

VERSION = re.compile(r"^spec_version:\s*(\d+)\.(\d+)\.(\d+)\s*$", re.M)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def is_spec(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return (
        path.startswith("specs/rules/")
        and name.endswith(".md")
        and not name.startswith("_")
        and not name.endswith("-build-tasks.md")
    )


def version(text: str) -> tuple[int, ...] | None:
    m = VERSION.search(text)
    return tuple(int(x) for x in m.groups()) if m else None


def problems(base: str) -> list[str]:
    out: list[str] = []
    changed = git("diff", "--name-only", "--diff-filter=M", base, "HEAD", "--")
    for path in filter(is_spec, changed.split()):
        old = git("show", f"{base}:{path}").replace("\r\n", "\n")
        new = open(path, encoding="utf-8").read().replace("\r\n", "\n")
        if old == new:
            continue
        was, now = version(old), version(new)
        if was is None or now is None:
            out.append(f"{path}: no spec_version to compare")
        elif now <= was:
            show = ".".join(map(str, was))
            out.append(
                f"{path}: its text differs from the base commit but its "
                f"spec_version is {'.'.join(map(str, now))}, not above "
                f"{show}. Take the next free version (MINOR for a rule "
                "change, PATCH for wording) and run "
                "`uv run python -m tobi508.rules lock`."
            )
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    found = problems(sys.argv[1])
    for p in found:
        print(p)
    if not found:
        print("Every changed spec has a higher version.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
