"""Fields hidden from everyone (guard CN's hidden fields; Abby, 2026-11-15,
roadmap step 6e; plan docs/archive/2026-11-15-fields-hidden-from-everyone.md).

A form field hidden when the page loads is *hidden from everyone* only when
nothing a careful tester does shows it, read by behaviour, never by its
markup or a plugin's name:

1. **Open:** every trigger the reveal pass opened, and the options it chose
   (`reveal.Opened.new_field_paths`); then every opener the inventory
   counts (a button, a same-page or script link, a click handler, a
   disclosure), each clicked in turn on one load, with a read after each.
   When the reveal pass did not run, left a trigger unopened, hit its cap,
   or the page has more openers than `OPENERS_MAX`, nothing is hidden from
   everyone.
2. **Wait and scroll:** one fresh load watched for `WATCH_S` with no input
   (a popup that opens by itself), then scrolled down a window at a time.
3. **Choose and type:** per form that holds such a field, one fresh load on
   which each option of each list box, each radio button and each checkbox
   of the form is chosen in turn, then a value is typed into each text box,
   then each of the form's buttons is pressed with those values in place (a
   later step of a form that checks the first), with a read after each.

Only a field inside a form that is shown on load can be hidden from
everyone (Abby, 2026-11-15): a field whose whole form is hidden on load (a
popup, a panel, a mobile copy) stays counted, because a recording may not
reproduce what shows it (round 1's feedback popup never opened on replay).
A field any step shows stays counted (guard CN holds the tests until a
reader reads it). A field outside any form, a load or read that failed, or
a run out of time leaves its fields counted. Facts only; the guard row is
in specs/rules/_template.md (guard CN).
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from pydantic import BaseModel, Field

from tobi508.jslib import JSLIB, PATH_JS

WATCH_S = 15
CHOICES_MAX = 60  # choices tried per form
OPTIONS_MAX = 10  # options tried per list box
OPENERS_MAX = 40  # openers pressed per page; more, and nothing is decided
FORMS_MAX = 10  # forms swept
STEP_WAIT_MS = 250
TYPED = "test"

# Which of `paths` are shown now (top document only, as the inventory's
# hidden-field paths are).
_SHOWN_JS = (
    "(paths) => {"
    + JSLIB
    + PATH_JS
    + """
  return paths.filter((p) => { const el = J.find(p); return !!el && J.rendered(el); });
}"""
)

# The form (by path) of each field, and whether that form is shown now
# (read right after a fresh load); "" for a field outside any form.
_FORMS_JS = (
    "(paths) => {"
    + JSLIB
    + PATH_JS
    + """
  const out = {};
  for (const p of paths) {
    const el = J.find(p);
    const f = el && (el.form || el.closest('form'));
    out[p] = f ? [path(f), J.rendered(f)] : ['', false];
  }
  return out;
}"""
)

# The form's controls a person can use now: list boxes with their options,
# radio buttons and checkboxes, and text boxes.
_CONTROLS_JS = (
    "([formPath, optionsMax]) => {"
    + JSLIB
    + PATH_JS
    + """
  const f = J.find(formPath);
  if (!f) return null;
  const usable = (el) => J.rendered(el) && !J.off(el);
  const TEXT = ['text', 'search', 'email', 'tel', 'url', 'number', ''];
  const own = Array.from(f.querySelectorAll('select, input, textarea'));
  const linked = f.id
    ? Array.from(document.querySelectorAll('[form="' + CSS.escape(f.id) + '"]'))
    : [];
  const all = own.concat(linked);
  const out = [];
  for (const el of all) {
    if (!usable(el)) continue;
    if (el.tagName === 'SELECT') {
      const n = Math.min(el.options.length, optionsMax);
      for (let i = 0; i < n; i++) {
        out.push({ kind: 'option', path: path(el), index: i });
      }
    } else if (el.type === 'radio' || el.type === 'checkbox') {
      out.push({ kind: 'choice', path: path(el) });
    } else if (el.tagName === 'TEXTAREA' || TEXT.includes(el.type)) {
      out.push({ kind: 'type', path: path(el) });
    }
  }
  return out;
}"""
)

# Acts on one control by path, as a person would through the page's own
# events: a list box option chosen, a radio button or checkbox clicked, a
# value typed. Done in the page so a control that moved stays findable.
_ACT_JS = (
    "([c, typed]) => {"
    + JSLIB
    + PATH_JS
    + """
  const el = J.find(c.path);
  if (!el || !J.rendered(el)) return false;
  if (c.kind === 'option') {
    el.selectedIndex = c.index;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  } else if (c.kind === 'choice') {
    el.click();
  } else {
    el.focus();
    el.value = typed;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    el.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 't' }));
  }
  return true;
}"""
)

# Every opener the inventory counts (count.py OPENER), shown and enabled,
# in the top document: what a person could press to show something.
_OPENERS_JS = (
    "(max) => {"
    + JSLIB
    + PATH_JS
    + """
  const OPENER = 'button, [role=button], input[type=button], summary, a[href^="#"], ' +
    'a[href^="javascript:" i], [onclick], [aria-expanded], [aria-controls]';
  const out = [];
  for (const el of document.querySelectorAll(OPENER)) {
    if (!J.rendered(el) || el.matches(':disabled')) continue;
    out.push(path(el));
    if (out.length > max) break;
  }
  return out;
}"""
)

_CLICK_JS = (
    "(p) => {"
    + JSLIB
    + PATH_JS
    + """
  const el = J.find(p);
  if (!el || !J.rendered(el)) return false;
  el.click();
  return true;
}"""
)

# The buttons of a form a person can press now (top document).
_BUTTONS_JS = (
    "(formPath) => {"
    + JSLIB
    + PATH_JS
    + """
  const f = J.find(formPath);
  if (!f) return [];
  const sel = 'button, input[type=submit], input[type=button], [role=button]';
  return Array.from(f.querySelectorAll(sel))
    .filter((b) => J.rendered(b) && !b.matches(':disabled')).map((b) => path(b));
}"""
)

_SCROLL_JS = """async ([steps, wait]) => {
  for (let i = 0; i < steps; i++) {
    const before = window.scrollY;
    const top = before + Math.max(200, innerHeight * 0.9);
    window.scrollTo({ top, behavior: 'instant' });
    await new Promise((r) => setTimeout(r, wait));
    if (window.scrollY === before) break;
  }
}"""


class HiddenCheck(BaseModel):
    """What the check did, and the hidden fields nothing showed."""

    ran: bool = False
    why_not: str = ""  # plain words, when it did not run or decided nothing
    never_shown: list[str] = Field(default_factory=list)  # paths
    shown_by: dict[str, str] = Field(default_factory=dict)  # path -> step
    kept: dict[str, str] = Field(default_factory=dict)  # path -> why counted
    seconds: float = 0.0


def _reveal_complete(rv: Any) -> str:
    """ "" when the reveal pass opened every trigger it found, else why not."""
    if rv is None:
        return "the menus and sections that open were not opened in this run"
    if rv.over_cap:
        return "the page has more things that open than were opened"
    if any(t.not_opened for t in rv.triggers):
        return "something that opens could not be opened"
    return ""


async def check(ctx: Any, hidden_paths: list[str], rv: Any) -> HiddenCheck:
    """Steps 1 to 3 on the inventory's hidden-field paths. Never raises."""
    t0 = time.monotonic()
    out = HiddenCheck()
    try:
        await _check(ctx, list(dict.fromkeys(hidden_paths)), rv, out)
    except Exception as exc:  # anything unexpected: every field stays counted
        out.never_shown = []
        out.why_not = f"the check failed ({type(exc).__name__})"
    out.seconds = round(time.monotonic() - t0, 1)
    return out


async def _check(ctx: Any, paths: list[str], rv: Any, out: HiddenCheck) -> None:
    why = _reveal_complete(rv)
    if why:
        out.why_not = why
        return
    out.ran = True
    left = set(paths)
    for t in rv.triggers:
        for p in t.new_field_paths:
            if p in left:
                left.discard(p)
                out.shown_by[p] = f'opening "{t.name or "a control"}"'
    if not left:
        return
    # 1b. Press every opener, not only the reveal pass's triggers: a plain
    # button or a "#" link with a click handler can show a form (review H-08;
    # the grid's form-behind-button).
    if not await _press_openers(ctx, left, out):
        out.ran = False
        out.why_not = out.why_not or "not everything that could show a field was tried"
        return
    if not left:
        return
    # 2. Wait and scroll.
    context, page = await ctx.new_page()
    try:
        forms = await page.evaluate(_FORMS_JS, sorted(left))
        for _ in range(WATCH_S):
            await page.wait_for_timeout(1000)
            for p in await page.evaluate(_SHOWN_JS, sorted(left)):
                left.discard(p)
                out.shown_by[p] = "waiting"
        await page.evaluate(_SCROLL_JS, [60, 150])
        await page.wait_for_timeout(1000)
        for p in await page.evaluate(_SHOWN_JS, sorted(left)):
            left.discard(p)
            out.shown_by[p] = "scrolling"
    finally:
        await context.close()
    for p in sorted(left):
        form, shown = forms.get(p) or ["", False]
        if not form:
            left.discard(p)
            out.kept[p] = "it is not in a form"
        elif not shown:
            # Only a hidden part of a form shown on load can be hidden from
            # everyone (Abby, 2026-11-15): a whole form that is hidden (a
            # popup, a panel, a mobile copy) stays counted, since a recording
            # may not reproduce what shows it (round 1's feedback popup).
            left.discard(p)
            out.kept[p] = "its whole form is hidden on load"
    # 3. Choose and type, one fresh load per form.
    by_form: dict[str, list[str]] = {}
    for p in sorted(left):
        by_form.setdefault(forms[p][0], []).append(p)
    for n, (form, fields) in enumerate(by_form.items()):
        if n >= FORMS_MAX or ctx.out_of_time():
            for p in fields:
                left.discard(p)
                out.kept[p] = "its form was not tried (time or cap)"
            continue
        ok = await _sweep(ctx, form, fields, left, out)
        if not ok:
            for p in fields:
                if p in left:
                    left.discard(p)
                    out.kept[p] = "its form could not be tried"
    out.never_shown = sorted(left)


async def _press_openers(ctx: Any, left: set[str], out: HiddenCheck) -> bool:
    """Click each opener in turn on one load, reading after each; a fresh
    load when a click left the page. False when not all could be tried."""
    context, page = await ctx.new_page()
    try:
        openers = await page.evaluate(_OPENERS_JS, OPENERS_MAX)
        if len(openers) > OPENERS_MAX:
            out.why_not = "the page has more things to press than were tried"
            return False
        url = page.url
        for p in openers:
            if not left:
                break
            if page.url != url:
                await context.close()
                context, page = await ctx.new_page()
            try:
                await page.evaluate(_CLICK_JS, p)
                await page.wait_for_timeout(STEP_WAIT_MS)
                shown = await page.evaluate(_SHOWN_JS, sorted(left))
            except Exception:
                # The click left the page: try the next one on a fresh load.
                await context.close()
                context, page = await ctx.new_page()
                continue
            for q in shown:
                left.discard(q)
                out.shown_by[q] = "pressing a button or link"
        return True
    finally:
        await context.close()


async def _sweep(
    ctx: Any, form: str, fields: list[str], left: set[str], out: HiddenCheck
) -> bool:
    try:
        context, page = await ctx.new_page()
    except Exception:
        return False
    try:
        controls = await page.evaluate(_CONTROLS_JS, [form, OPTIONS_MAX])
        if controls is None:
            return False
        for c in controls[:CHOICES_MAX]:
            if not any(p in left for p in fields):
                break
            try:
                await page.evaluate(_ACT_JS, [c, TYPED])
            except Exception:
                continue  # the page left or changed: the reads below decide
            await page.wait_for_timeout(STEP_WAIT_MS)
            try:
                shown = await page.evaluate(_SHOWN_JS, [p for p in fields if p in left])
            except Exception:
                return False
            for p in shown:
                left.discard(p)
                out.shown_by[p] = (
                    "typing in its form"
                    if c["kind"] == "type"
                    else "a choice in its form"
                )
        # Then press each of the form's buttons with those values in place: a
        # later step of a form that checks the first step appears only after
        # its fields are filled (fixture later-step-checked).
        if any(p in left for p in fields):
            for b in await page.evaluate(_BUTTONS_JS, form) or []:
                if not any(p in left for p in fields):
                    break
                try:
                    await page.evaluate(_CLICK_JS, b)
                    await page.wait_for_timeout(STEP_WAIT_MS)
                    shown = await page.evaluate(
                        _SHOWN_JS, [p for p in fields if p in left]
                    )
                except Exception:
                    break  # the page left: what was shown so far stands
                for p in shown:
                    left.discard(p)
                    out.shown_by[p] = "pressing a button of its form after typing"
        if len(controls) > CHOICES_MAX:
            for p in fields:
                if p in left:
                    left.discard(p)
                    out.kept[p] = "its form has more choices than were tried"
        return True
    finally:
        await context.close()


async def bounded(
    ctx: Any, hidden_paths: list[str], rv: Any, hard: float
) -> HiddenCheck:
    """`check` within `hard` seconds (monotonic deadline)."""
    left = hard - time.monotonic()
    if left <= 0:
        return HiddenCheck(why_not="there was no time left in this run")
    try:
        return await asyncio.wait_for(check(ctx, hidden_paths, rv), left)
    except TimeoutError:
        return HiddenCheck(why_not="there was no time left in this run")
