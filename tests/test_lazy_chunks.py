"""The chunk store (capture.py; docs/solutions/recordings-miss-lazy-scripts.md):
scripts that recorded scripts name by a string literal are saved inside the
HAR and served on replay, so a page's code-split handlers run. A script the
store could not save is reported by `unrecorded_code`. Pages come from the
local test server (no network)."""

from __future__ import annotations

import shutil
import zipfile

from tobi508 import capture
from tobi508.capture import (
    chunk_index,
    record,
    replay_context,
    script_refs,
    unrecorded_code,
)

from .conftest import noop_log

BASE = "http://127.0.0.1:9/app/main.js"


def test_script_refs_reads_string_literals_only_and_resolves_from_the_script():
    text = (
        'x=()=>import("./a-1.js");y=import("../up/b.mjs");z=import("/root/c.js");'
        'import{g as o}from"./d.js";import"./e.js";'
        "w=import(name);v=import(`./t.js`);u=import('https://other.test/f.js');"
        't=import("./g.js?v=2");s=import("./not-a-script.css");'
    )
    assert script_refs(text, BASE) == [
        "http://127.0.0.1:9/app/a-1.js",
        "http://127.0.0.1:9/up/b.mjs",
        "http://127.0.0.1:9/root/c.js",
        "http://127.0.0.1:9/app/d.js",
        "http://127.0.0.1:9/app/e.js",
    ]


async def _click_then_text(page, selector="#out"):
    await page.click("#go")
    await page.wait_for_timeout(300)
    return await page.evaluate(
        "(s) => { const e = document.querySelector(s);"
        " return e.dataset.loaded || e.textContent; }",
        selector,
    )


async def test_a_lazy_chunk_is_stored_and_the_handler_runs_on_replay(
    settings, browser, server, tmp_path
):
    har = tmp_path / "page.har.zip"
    cap = await record(
        browser, settings, f"{server.base}/lazy/l01-lazy-on-click.html", har, noop_log
    )
    [c] = cap.chunks
    assert c["url"].endswith("/l01-chunk.js") and c["file"] and c["size"] > 0
    assert "missing" not in c
    assert chunk_index(har)[0]["file"] == c["file"]
    assert unrecorded_code(har) == []
    r = await replay_context(browser, settings, har, noop_log)
    try:
        page = await r.context.new_page()
        await r.guard.goto(page, cap.final_url)
        assert await _click_then_text(page) == "yes"
    finally:
        await r.context.close()


async def test_without_the_store_the_handler_does_nothing_and_it_is_reported(
    settings, browser, server, tmp_path
):
    """What 5340 showed: the same recording with the stored chunk removed."""
    har = tmp_path / "page.har.zip"
    cap = await record(
        browser, settings, f"{server.base}/lazy/l01-lazy-on-click.html", har, noop_log
    )
    bare = tmp_path / "bare.har.zip"
    with zipfile.ZipFile(har) as src, zipfile.ZipFile(bare, "w") as dst:
        for n in src.namelist():
            if n != capture.CHUNKS_INDEX and not n.startswith("a11y-chunk-"):
                dst.writestr(n, src.read(n))
    assert [u.rsplit("/", 1)[-1] for u in unrecorded_code(bare)] == ["l01-chunk.js"]
    r = await replay_context(browser, settings, bare, noop_log)
    try:
        page = await r.context.new_page()
        await r.guard.goto(page, cap.final_url)
        assert await _click_then_text(page) == ""
    finally:
        await r.context.close()


async def test_a_chunk_that_names_another_chunk_is_stored_too(
    settings, browser, server, tmp_path
):
    har = tmp_path / "page.har.zip"
    cap = await record(
        browser, settings, f"{server.base}/lazy/l02-nested.html", har, noop_log
    )
    names = sorted(c["url"].rsplit("/", 1)[-1] for c in cap.chunks if c["file"])
    assert names == ["l02-a.js", "l02-b.js"]
    assert unrecorded_code(har) == []
    r = await replay_context(browser, settings, har, noop_log)
    try:
        page = await r.context.new_page()
        await r.guard.goto(page, cap.final_url)
        assert await _click_then_text(page) == "yes"
    finally:
        await r.context.close()


async def test_a_chunk_that_cannot_be_stored_is_listed_with_why(
    settings, browser, server, tmp_path
):
    har = tmp_path / "gone.har.zip"
    cap = await record(
        browser, settings, f"{server.base}/lazy/l03-missing-chunk.html", har, noop_log
    )
    [c] = cap.chunks
    assert c["file"] is None and c["missing"] == "answered 404"
    assert [u.rsplit("/", 1)[-1] for u in unrecorded_code(har)] == ["l03-gone.js"]
    other = tmp_path / "other.har.zip"
    cap = await record(
        browser, settings, f"{server.base}/lazy/l04-other-host.html", other, noop_log
    )
    [c] = cap.chunks
    assert c["missing"] == "another host than the script that names it"
    # a script on another host is not "unrecorded code" of this page's host:
    # the page cannot be made whole by the store, and the report says nothing
    # about hosts it never fetches from
    assert unrecorded_code(other) == []


async def test_the_chunk_limit_leaves_the_rest_listed_not_stored(
    settings, browser, server, tmp_path, monkeypatch
):
    monkeypatch.setattr(capture, "MAX_CHUNKS", 1)
    har = tmp_path / "page.har.zip"
    cap = await record(
        browser, settings, f"{server.base}/lazy/l02-nested.html", har, noop_log
    )
    got = {c["url"].rsplit("/", 1)[-1]: c for c in cap.chunks}
    assert got["l02-a.js"]["file"] and got["l02-b.js"]["missing"] == (
        "more than the chunk limit"
    )
    assert [u.rsplit("/", 1)[-1] for u in unrecorded_code(har)] == ["l02-b.js"]


def test_a_recording_made_before_the_store_is_still_checked():
    """The frozen pages of round 2 (restored by hand, git-ignored): 5340's
    recording names scripts it lacks."""
    from pathlib import Path

    import pytest

    p = Path("evals/judging/round2/frozen/pages/008.har.zip")
    if not p.exists():
        pytest.skip("round 2's frozen pages are not restored here")
    got = unrecorded_code(p)
    assert any(u.endswith("/index-CxrirnWy.js") for u in got)
    assert unrecorded_code(Path("evals/judging/round2/frozen/pages/001.har.zip")) == []
    shutil.which  # (keeps the import used when the file is skipped)


# ── guard GU: a would-be PASS is NEEDS REVIEW when the recording lacks code ──

GUARDED = ("4.A", "4.B", "4.C", "4.D", "4.E", "4.F", "5.D", "5.F", "5.G", "5.H")


def test_the_specs_that_press_keys_or_type_declare_the_guard():
    from tobi508.config import REPO_ROOT
    from tobi508.models import TestId
    from tobi508.rules import load_specs

    specs = load_specs(REPO_ROOT / "specs" / "rules")
    got = {t.value for t, s in specs.items() if s.guards}
    assert got == set(GUARDED)
    assert all(specs[TestId(t)].guards == ("unrecorded-code",) for t in GUARDED)


def test_an_unknown_guard_in_front_matter_fails_loudly(tmp_path):
    import pytest

    from tobi508.config import REPO_ROOT
    from tobi508.rules import RuleSpecError, load_spec

    text = (REPO_ROOT / "specs/rules/4e-on-focus.md").read_text("utf-8")
    p = tmp_path / "4e-on-focus.md"
    p.write_text(text.replace("guards: unrecorded-code", "guards: made-up"), "utf-8")
    with pytest.raises(RuleSpecError, match="unknown guard 'made-up'"):
        load_spec(p)


def test_the_guard_only_moves_a_pass_to_needs_review():
    from tobi508.engine import apply_guards
    from tobi508.models import Finding, Outcome, Report, TestId

    def finding(outcome):
        return Finding(
            test_id=TestId.T4E,
            test_name=TestId.T4E.tt_name,
            outcome=outcome,
            summary="original",
            rows=["G4"],
        )

    def report(n):
        return Report.model_construct(unrecorded_code_count=n)

    g = ("unrecorded-code",)
    got = apply_guards(finding(Outcome.PASS), g, report(3))
    assert got.outcome is Outcome.NEEDS_REVIEW and got.rows == ["G4", "GU"]
    assert got.note == "This test could not be performed"
    assert "loads more code when it is used" in got.summary
    for same in (Outcome.FAIL, Outcome.DNA, Outcome.NEEDS_REVIEW):
        assert apply_guards(finding(same), g, report(3)).outcome is same
    assert apply_guards(finding(Outcome.PASS), g, report(0)).outcome is Outcome.PASS
    assert apply_guards(finding(Outcome.PASS), (), report(3)).outcome is Outcome.PASS


async def test_a_page_whose_chunk_is_missing_cannot_pass_but_its_twin_can(
    settings, server
):
    from tobi508.models import TestId
    from tobi508.pipeline import run_tt_tests

    tests = [TestId(t) for t in ("4.A", "4.B", "4.D", "4.E", "5.D")]
    gone = await run_tt_tests(
        settings, f"{server.base}/lazy/l05-gone-chunk.html", tests
    )
    plain = await run_tt_tests(
        settings, f"{server.base}/lazy/l06-plain-form.html", tests
    )
    assert plain.report.unrecorded_code_count == 0
    assert {f.outcome.value for f in plain.report.findings} == {"PASS"}
    assert gone.report.unrecorded_code_count == 1
    assert [u.rsplit("/", 1)[-1] for u in gone.report.unrecorded_code] == [
        "l05-gone.js"
    ]
    for f in gone.report.findings:
        assert (f.outcome.value, f.rows[-1], f.note) == (
            "NEEDS_REVIEW",
            "GU",
            "This test could not be performed",
        ), (f.test_id, f.rows)


def test_inline_scripts_are_read_by_the_html_rules():
    """An end tag with a space, attributes or other case still ends the
    script (a regular expression for `</script>` missed these), a script with
    a src has no inline code, and text outside scripts is not read."""
    from tobi508.capture import _code_of

    html = (
        '<p>import("./not-code.js")</p>'
        '<script type="module">import("./a.js")</script >'
        '<SCRIPT>import("./b.js")</SCRIPT foo="1">'
        '<script src="x.js">import("./ignored.js")</script>'
        "<script>import('./c.js')</script>"
    )
    code = _code_of(html, "text/html; charset=utf-8")
    assert [r.rsplit("/", 1)[-1] for r in script_refs(code, BASE)] == [
        "a.js",
        "b.js",
        "c.js",
    ]
    assert _code_of("import('./z.js')", "text/javascript") == "import('./z.js')"
