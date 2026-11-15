"""jslib (plan 2026-11-12 part D): the readers' shared rules, read straight
from a page with web components, nested ones and slots."""

from __future__ import annotations

from playwright.async_api import async_playwright

from tobi508.count import COUNT_JS
from tobi508.jslib import FIELD_SELECTOR, JSLIB
from tobi508.reveal import _COMMON_JS

PAGE = """<!doctype html><html lang="en"><body>
<style>.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}</style>
<p id="lbl">Outside</p>
<label id="hid"><span class="sr">Email address</span><span>*</span></label>
<label id="off" style="display:inline-block;width:120px;overflow:hidden;text-indent:-9999px">Phone</label>
<x-outer></x-outer>
<script>
customElements.define('x-inner', class extends HTMLElement {
  constructor() { super(); this.attachShadow({ mode: 'open' }).innerHTML =
    '<label for="i"><slot name="l"></slot></label><input id="i" aria-labelledby="lbl"><input type="range" id="r">'; }
});
customElements.define('x-outer', class extends HTMLElement {
  constructor() { super(); this.attachShadow({ mode: 'open' }).innerHTML =
    '<x-inner><span slot="l">City name</span></x-inner><x-inner id="has space"></x-inner>'; }
});
</script></body></html>"""


async def _eval(body: str):
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        p = await b.new_page()
        await p.set_content(PAGE)
        try:
            return await p.evaluate("() => {" + JSLIB + body + "}")
        finally:
            await b.close()


async def test_all_enters_nested_web_components_and_find_reads_paths_back():
    got = await _eval("""
      const ins = J.all('input');
      return { n: ins.length, paths: ins.map((e) => J.path(e)),
               back: ins.every((e) => J.find(J.path(e)) === e),
               where: ins.map(J.where), fields: J.all(J.FIELD).length };""")
    assert got["n"] == 4 and got["back"], got
    assert set(got["where"]) == {"shadow"}
    # Two same-tag components directly in one root get their own paths.
    assert len(set(got["paths"])) == 4, got["paths"]
    assert got["fields"] == 4  # text inputs and sliders are fields


async def test_visible_text_follows_slots_and_leaves_hidden_words_out():
    got = await _eval("""
      const lab = J.all('label').find((l) => l.getRootNode() !== document);
      return { slotted: J.text(lab), hidden: J.text(document.getElementById('hid')),
               off: J.text(document.getElementById('off')) };""")
    assert got == {"slotted": "City name", "hidden": "*", "off": ""}, got


async def test_ids_are_looked_up_in_the_elements_own_tree():
    got = await _eval("""
      const i = J.all('input')[0];
      return { inside: !!J.byId(i, 'i'), outside: !!J.byId(i, 'lbl') };""")
    assert got == {"inside": True, "outside": False}


def test_one_field_rule_for_the_inventory_and_the_readers():
    assert "const FIELD = J.FIELD;" in _COMMON_JS  # reveal.py (D-19)
    assert "const { FIELD, inert, rendered, focusable, off } = J;" in COUNT_JS
    assert "[role=slider]" in FIELD_SELECTOR and "[role=spinbutton]" in FIELD_SELECTOR
