"""Fail when the CI test groups together collect fewer tests than the suite.

Reads the matrix of `.github/workflows/ci.yml`, collects each group's tests
with `pytest --collect-only`, and compares the union with the whole suite.
Run from the repository root: `uv run python scripts/ci_groups_check.py`.
(Review item Q-01: a test file no group named was never run.)
"""

from __future__ import annotations

import glob
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def collect(args: list[str]) -> set[str]:
    cmd = [
        "uv",
        "run",
        "pytest",
        "--collect-only",
        "-q",
        "-n0",
        "-p",
        "no:cacheprovider",
        *args,
    ]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if out.returncode not in (0, 5):
        sys.exit(f"collect failed for {args}:\n{out.stdout}\n{out.stderr}")
    return {line for line in out.stdout.splitlines() if "::" in line}


def main() -> int:
    wf = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    groups = wf["jobs"]["test"]["strategy"]["matrix"]["include"]
    whole = collect(["tests/"])
    seen: dict[str, set[str]] = {}
    for g in groups:
        # The runner's shell expands globs; pytest options keep their own.
        args: list[str] = []
        for a in shlex.split(g["args"]):
            hits = (
                sorted(glob.glob(a, root_dir=ROOT))
                if "*" in a and not a.startswith("-")
                else []
            )
            args.extend(hits or [a])
        seen[g["group"]] = collect(args)
    union = set().union(*seen.values())
    for name, ids in seen.items():
        print(f"{name}: {len(ids)} tests")
    print(f"groups together: {len(union)}; whole suite: {len(whole)}")
    missing = sorted(whole - union)
    if missing:
        print(f"{len(missing)} tests are in no CI group:")
        for m in missing[:30]:
            print("  ", m)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
