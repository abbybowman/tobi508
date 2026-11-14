"""The page's inventory (count.py) and guard CN (engine.apply_guards; plan
2026-11-12 part B). The per-test pages are in test_fixtures_count.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from tobi508 import count as inventory
from tobi508.engine import NOT_INVENTORIED, apply_guards, count_sentence
from tobi508.models import Count, Finding, Outcome, Part, Report, TestId
from tobi508.rules import RuleSpecError, load_spec

REPO_ROOT = Path(__file__).resolve().parents[1]


def finding(outcome: Outcome) -> Finding:
    return Finding(
        test_id=TestId.T5A,
        test_name=TestId.T5A.tt_name,
        outcome=outcome,
        summary="original",
        rows=["A1", "G1"],
    )


def report(**counts: Count) -> Report:
    return Report.model_construct(counts=counts)


class State:
    def __init__(self, read: dict | None = None) -> None:
        self.read = read or {}


SHADOW_FORM = Count(fields=Part(shadow=2), fields_hidden=Part(light=1))


def test_a_gap_moves_does_not_apply_and_pass_to_needs_review():
    for was in (Outcome.DNA, Outcome.PASS):
        f = apply_guards(
            finding(was), (), report(page=SHADOW_FORM), State(), ("fields.shadow",)
        )
        assert f.outcome is Outcome.NEEDS_REVIEW
        assert f.rows == ["A1", "G1", "CN"]
        assert f.note == "This test could not be performed"
        assert "2 form fields inside web components were not checked." in f.summary
        assert f"would have been {was.value}" in f.rationale


def test_fail_needs_review_and_not_tested_are_unchanged():
    for same in (Outcome.FAIL, Outcome.NEEDS_REVIEW, Outcome.NOT_TESTED):
        f = apply_guards(
            finding(same), (), report(page=SHADOW_FORM), State(), ("fields.shadow",)
        )
        assert f.outcome is same and "CN" not in f.rows


def test_quiet_when_the_test_read_as_many_or_lists_no_key():
    st = State({"page": {"fields.shadow": 2, "fields_hidden": 1}})
    keys = ("fields.shadow", "fields_hidden")
    f = apply_guards(finding(Outcome.DNA), (), report(page=SHADOW_FORM), st, keys)
    assert f.outcome is Outcome.DNA
    f = apply_guards(finding(Outcome.DNA), (), report(page=SHADOW_FORM), State(), ())
    assert f.outcome is Outcome.DNA
    # A key the page has none of.
    f = apply_guards(
        finding(Outcome.PASS), (), report(page=SHADOW_FORM), State(), ("media",)
    )
    assert f.outcome is Outcome.PASS


def test_a_run_made_before_the_inventory_is_left_as_it_was():
    f = apply_guards(finding(Outcome.DNA), (), report(), State(), ("fields",))
    assert f.outcome is Outcome.DNA


def test_an_inventory_that_could_not_be_taken_holds_the_outcome():
    bad = Count(where="own load", error="TimeoutError")
    f = apply_guards(finding(Outcome.PASS), (), report(page=bad), State(), ("fields",))
    assert f.outcome is Outcome.NEEDS_REVIEW
    assert NOT_INVENTORIED in f.summary
    assert "inventoried" in NOT_INVENTORIED and "counted" not in NOT_INVENTORIED


def test_a_dna_key_holds_does_not_apply_only():
    c = Count(focusable=Part(light=4))
    st = State({"page": {"focusable": 1}})
    keys = ("focusable@dna",)
    f = apply_guards(finding(Outcome.PASS), (), report(page=c), st, keys)
    assert f.outcome is Outcome.PASS
    f = apply_guards(finding(Outcome.DNA), (), report(page=c), st, keys)
    assert f.outcome is Outcome.NEEDS_REVIEW
    assert "The page has 4 elements that take focus, and the keyboard reached 1." in (
        f.summary
    )


def test_other_pages_are_compared_when_the_test_read_them():
    c = Count(links=Part(shadow=3))
    st = State({"page": {}, "p1": {}})
    keys = ("links.shadow",)
    f = apply_guards(finding(Outcome.DNA), (), report(page=Count(), p1=c), st, keys)
    assert f.outcome is Outcome.NEEDS_REVIEW
    assert "On other page 1, 3 links inside web components were not checked." in (
        f.summary
    )


def test_sentences_name_the_number_and_the_thing():
    assert count_sentence("fields.shadow", 1, 0) == (
        "1 form field inside a web component was not checked."
    )
    assert count_sentence("fields_hidden", 1, 0) == (
        "1 form field is hidden until something opens it, and was not checked."
    )
    assert count_sentence("images", 31, 30) == (
        "31 images: only the first 30 were checked for animation."
    )
    assert count_sentence("media_played.detached", 1, 0) == (
        "1 sound or video played from a script, and was not checked."
    )
    assert count_sentence("canvases", 2, 0) == (
        "2 drawing areas (canvas) were not checked."
    )


def test_the_spec_loader_reads_count_keys(tmp_path: Path):
    text = (REPO_ROOT / "specs/rules/4e-on-focus.md").read_text("utf-8")
    p = tmp_path / "4e-on-focus.md"
    p.write_text(
        text.replace(
            "\nspec_version:", "\ncount: fields.shadow, focusable@dna\nspec_version:"
        ),
        "utf-8",
    )
    assert load_spec(p).count == ("fields.shadow", "focusable@dna")
    p.write_text(
        text.replace("\nspec_version:", "\ncount: forms\nspec_version:"),
        "utf-8",
    )
    with pytest.raises(RuleSpecError, match="unknown count key 'forms'"):
        load_spec(p)


PAGE = """<!doctype html><html lang="en"><head><title>t</title></head><body>
<h1>Inventory</h1><nav><a href="#a">A</a></nav>
<form><label>Name <input name="n"></label><button>Send</button></form>
<div hidden><input type="email" name="e"></div>
<div contenteditable="true">edit</div>
<canvas width="100" height="100"></canvas><div draggable="true">d</div>
<img alt="x" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=">
<div id="h"></div>
<iframe srcdoc="<input name=f><a href=#b>B</a>"></iframe>
<script>
const r = document.getElementById('h').attachShadow({mode: 'open'});
r.innerHTML = '<input name="s"><audio></audio><a href="#c">C</a>';
new Audio('none.wav').play().catch(() => {});
r.querySelector('audio').play().catch(() => {});
</script></body></html>"""


async def test_the_inventory_counts_the_page_its_shadow_roots_and_frames(browser):
    ctx = await browser.new_context()
    await ctx.add_init_script(inventory.PLAY_HOOK_JS)
    page = await ctx.new_page()
    await page.set_content(PAGE)
    await page.wait_for_function(
        "document.querySelector('iframe').contentDocument"
        " && document.querySelector('iframe')"
        ".contentDocument.readyState === 'complete'"
    )
    c = await inventory.take(page, "test")
    await ctx.close()
    assert not c.error
    assert (c.fields.light, c.fields.shadow, c.fields.frames) == (1, 1, 1)
    assert c.fields_hidden.light == 1
    assert c.hidden_field_paths and "input" in c.hidden_field_paths[0]
    assert c.contenteditable.light == 1
    assert c.forms_with_button.light == 1 and len(c.form_paths) == 1
    assert (c.media.shadow, c.media_played.shadow, c.media_played.detached) == (
        1,
        1,
        1,
    )
    # Images are distinct http(s) addresses, as pass T's image read takes them:
    # the page's one image is a data: address.
    assert (c.canvases.light, c.draggable.light, c.images.light) == (1, 1, 0)
    assert (c.links.light, c.links.shadow, c.links.frames) == (1, 1, 1)
    assert c.landmarks.light == 1  # nav
    assert (c.frames, c.frames_unread, c.shadow_roots) == (1, 0, 1)
    assert c.openers >= 1  # the form's Send button
    assert c.get("fields") == 3 and c.get("fields.shadow") == 1


async def test_the_page_cannot_replace_the_play_hook(browser):
    ctx = await browser.new_context()
    await ctx.add_init_script(inventory.PLAY_HOOK_JS)
    page = await ctx.new_page()
    await page.set_content(
        "<script>try { window.__tobiPlayed = null; } catch (e) {}"
        "new Audio('x.wav').play().catch(() => {});</script>"
    )
    c = await inventory.take(page, "test")
    await ctx.close()
    assert c.media_played.detached == 1


def test_hidden_fields_hold_nothing_when_nothing_could_open_them():
    """DHS's Baseline TC10.A-ic-dna-1 and -2: a field hidden by CSS on a page
    with no control stays DOES NOT APPLY (Abby, 2026-11-12, option A)."""
    keys = ("fields_hidden",)
    closed = Count(fields_hidden=Part(light=1), openers=0)
    f = apply_guards(finding(Outcome.DNA), (), report(page=closed), State(), keys)
    assert f.outcome is Outcome.DNA and "CN" not in f.rows
    openable = Count(fields_hidden=Part(light=1), openers=1)
    f = apply_guards(finding(Outcome.DNA), (), report(page=openable), State(), keys)
    assert f.outcome is Outcome.NEEDS_REVIEW and "CN" in f.rows


async def test_the_focusable_count_has_a_radio_group_once(browser):
    """Tab lands on one radio of a group (the same rule as traverse's
    inventory): 3 radios of one name and a button are 2 elements that take
    focus, and a group in another form is its own."""
    ctx = await browser.new_context()
    page = await ctx.new_page()
    await page.set_content(
        "<input type=radio name=s><input type=radio name=s><input type=radio name=s>"
        "<form><input type=radio name=s><input type=radio name=s></form>"
        "<button>Send</button>"
    )
    c = await inventory.take(page, "test")
    await ctx.close()
    assert c.focusable.light == 3
