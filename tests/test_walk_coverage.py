"""walk.walk_coverage (row WK, step 6d): what the passes a test reads reached,
against what Tab should land on when the last of them ended. Facts only; the
checks' rows decide what a gap means. Pages are tests/fixtures/walk/."""

from __future__ import annotations

from tobi508.browser import new_context
from tobi508.models import PassResult
from tobi508.traverse import INIT_JS, run_pass
from tobi508.walk import KeyboardWalk, walk_coverage

from .conftest import FIXTURES


async def _walk(browser, settings, name) -> KeyboardWalk:
    url = (FIXTURES / "walk" / name).as_uri()

    async def new_page():
        ctx = await new_context(browser, settings)
        await ctx.add_init_script(INIT_JS)
        page = await ctx.new_page()
        await page.goto(url)
        return ctx, page

    p1 = await run_pass("P1", new_page, "Tab", 50)
    p2 = await run_pass("P2", new_page, "Shift+Tab", 50)
    return KeyboardWalk(p1=p1, p2=p2)


async def test_an_element_no_pass_reaches_is_named(browser, settings):
    w = await _walk(browser, settings, "skip-one-link.html")
    cov = walk_coverage(w)
    assert (w.p1.end, w.p2.end) == ("wrap", "wrap")
    assert (cov.counted, cov.reached, cov.not_reached) == (6, 5, 1)
    assert cov.not_reached_names == ['"Link two" (a)']
    assert not cov.complete
    assert cov.sentence == (
        "The keyboard reached 5 of the 6 elements on this page that take focus, "
        'so "Link two" (a) was not checked.'
    )


async def test_a_trap_is_complete_when_the_other_pass_reached_the_rest(
    browser, settings
):
    w = await _walk(browser, settings, "trap-then-all-reached.html")
    cov = walk_coverage(w)
    assert w.p1.end == "stuck" and w.p2.end == "stuck"
    # 2 links, the search field, the name field and the button: all 5 reached.
    assert (cov.counted, cov.reached, cov.not_reached) == (5, 5, 0)
    assert cov.complete and cov.sentence is None
    assert cov.causes and cov.causes[0].startswith('Tab got stuck at "Search"')


async def test_one_pass_alone_leaves_what_the_trap_hid(browser, settings):
    w = await _walk(browser, settings, "trap-then-all-reached.html")
    cov = walk_coverage(w, passes=("P1",))
    assert w.p1.end == "stuck"
    assert not cov.complete and cov.not_reached == 2  # the name field and Send
    assert cov.sentence.startswith(
        "The keyboard reached 3 of the 5 elements on this page that take focus"
    )
    assert cov.sentence.endswith('Tab got stuck at "Search" (textbox).')


async def test_a_radio_group_and_a_date_input_are_one_element_each(browser, settings):
    w = await _walk(browser, settings, "radio-and-date.html")
    cov = walk_coverage(w)
    # radio group, date input, Send: Tab lands on the date's parts one by one.
    assert (cov.counted, cov.not_reached) == (3, 0), cov
    assert cov.complete


async def test_a_frame_the_walk_went_into_is_reached(browser, settings):
    w = await _walk(browser, settings, "in-a-frame.html")
    cov = walk_coverage(w)
    assert cov.not_reached == 0, cov
    assert cov.counted == 5  # top link, the iframe, 2 inside it, end link


async def test_past_the_item_cap_the_count_alone_decides(browser, settings):
    w = await _walk(browser, settings, "many-links.html")
    assert w.p2.inventory_end == 205 and w.p2.inventory_end_items is None
    cov = walk_coverage(w)
    assert cov.complete and cov.counted == 205

    w = await _walk(browser, settings, "many-links-one-skipped.html")
    cov = walk_coverage(w)
    assert (cov.counted, cov.not_reached) == (205, 1)
    assert cov.not_reached_names == []
    assert cov.sentence.startswith(
        "The keyboard reached 204 of the 205 elements on this page that take focus, "
        "so 1 of them was not checked."
    )


def test_an_end_inventory_that_was_not_read_is_not_complete():
    p = PassResult(name="P2", end="error", cap=50, inventory=3, error="x")
    cov = walk_coverage(KeyboardWalk(p1=p.model_copy(update={"name": "P1"}), p2=p))
    assert not cov.complete and cov.counted is None
    assert "could not count" in cov.sentence
