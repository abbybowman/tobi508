"""Each spec version stands for one rule text (Abby, 2026-11-12, after 4.A
1.6.0 was taken on two branches and merged with no conflict).

- specs/rules/versions.lock holds each spec's version and text hash: a text
  changed without a new version fails here, and two branches that bump one
  spec both edit its line, so git raises a conflict.
- scripts/check_spec_versions.py (CI) fails a pull request whose changed
  spec is not above main's version.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

from tobi508.rules import LOCK_NAME, load_specs, lock_text, read_lock

REPO = Path(__file__).resolve().parents[1]
RULES = REPO / "specs" / "rules"
FIX = "uv run python -m tobi508.rules lock"


def test_every_spec_matches_its_line_in_the_lock():
    lock = read_lock(RULES)
    specs = {s.path.name: s for s in load_specs(RULES).values()}
    assert set(lock) == set(specs), (
        f"{LOCK_NAME} and specs/rules/ list different specs; run `{FIX}`."
    )
    for name, s in specs.items():
        ver, sha = lock[name]
        if s.sha256 != sha:
            assert s.spec_version != ver, (
                f"{name}: its text changed but spec_version is still {ver}. "
                "Bump it (MINOR for a rule change, PATCH for wording), take a "
                f"number main has not used, then run `{FIX}`."
            )
            raise AssertionError(f"{name}: {LOCK_NAME} is out of date; run `{FIX}`.")
        assert s.spec_version == ver, f"{name}: run `{FIX}`."


def test_the_lock_is_what_the_writer_writes():
    assert (RULES / LOCK_NAME).read_text("utf-8") == lock_text(RULES)


def _checker():
    spec = importlib.util.spec_from_file_location(
        "check_spec_versions", REPO / "scripts" / "check_spec_versions.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _spec(version: str, body: str) -> str:
    return f"---\ntt_test: 4.A\nspec_version: {version}\n---\n\n{body}\n"


def test_ci_check_catches_a_reused_or_missing_bump(tmp_path: Path, monkeypatch):
    rules = tmp_path / "specs" / "rules"
    rules.mkdir(parents=True)
    f = rules / "4a-keyboard-access.md"
    _git(tmp_path, "init", "-q")
    f.write_text(_spec("1.5.0", "rows"))
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "base")
    base = _git(tmp_path, "rev-parse", "HEAD")
    check = _checker()
    monkeypatch.chdir(tmp_path)

    f.write_text(_spec("1.5.0", "rows changed"))  # text changed, no bump
    _git(tmp_path, "commit", "-qam", "no bump")
    assert check.problems(base)

    f.write_text(_spec("1.6.0", "rows changed"))  # bumped
    _git(tmp_path, "commit", "-qam", "bump")
    assert check.problems(base) == []

    # main took 1.6.0 for other rows: the merged text at 1.6.0 differs from
    # main's 1.6.0, so the branch must move on.
    _git(tmp_path, "checkout", "-q", base)
    f.write_text(_spec("1.6.0", "other rows"))
    _git(tmp_path, "commit", "-qam", "main's 1.6.0")
    main = _git(tmp_path, "rev-parse", "HEAD")
    _git(tmp_path, "checkout", "-q", "-")
    f.write_text(_spec("1.6.0", "other rows\nrows changed"))  # a merged text
    _git(tmp_path, "commit", "-qam", "merged")
    assert check.problems(main)
