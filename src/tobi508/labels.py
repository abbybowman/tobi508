"""Pass L: form components, their visible labels and ANDI's output, shared by
5.A and 5.C (specs/rules/5c-programmatic-label.md section 2). One fresh load
after the walk: inventory every form component of the top document, read
its label candidates, table headers and list context, focus each
data-entry field and take a clipped image of it with what is around it,
then inject the vendored ANDI and read its output. Fields that appear only
after interaction are read the same way at the end of 4.F's pass R and
5.D's fill pass replays (`read_revealed`). Facts only; no outcome is
decided here (CLAUDE.md principle 2).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from tobi508.andi import andi_output, inject_andi, install_andi_routes
from tobi508.traverse import PATH_JS, Session, screenshot

COMPONENT_MAX = 60
# The image and the nearby-text region around a field (5.A spec section 2).
LEFT, UP, RIGHT, DOWN = 240, 120, 160, 160
NEARBY_CHARS = 400

_SHARED_JS = """
  const doc = document;
  const SEL = 'input,select,textarea,button,[role=button],[role=checkbox],[role=radio],[role=switch],' +
    '[role=combobox],[role=textbox],[role=searchbox],[role=slider],[role=spinbutton],[role=listbox]';
  const vis = (e) => !!(e && e.checkVisibility && e.checkVisibility({ visibilityProperty: true }));
  const shown = (e) => {
    if (!vis(e)) return false;
    const r = e.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) return false;
    const cs = getComputedStyle(e);
    if (parseFloat(cs.opacity) < 0.1) return false;
    if ((cs.clip || '').startsWith('rect(0') || (cs.clipPath || '').includes('inset(50%')) return false;
    return true;
  };
  const txt = (e) => (e ? (e.innerText || e.textContent || '') : '').replace(/\\s+/g, ' ').trim();
  const isOpt = (o) => {
    const t = (o.type || '').toLowerCase(), ro = o.getAttribute('role') || '';
    return t === 'radio' || t === 'checkbox' || ['radio', 'checkbox', 'switch'].includes(ro);
  };
  const isBtn = (o) => {
    const t = (o.type || '').toLowerCase();
    return o.tagName === 'BUTTON' || (o.tagName === 'INPUT' && ['submit', 'reset', 'button'].includes(t)) ||
      o.getAttribute('role') === 'button';
  };
  // A menu or disclosure button opens content; it does not act on form data.
  const isMenu = (o) => o.hasAttribute('aria-expanded') ||
    !['', 'false'].includes((o.getAttribute('aria-haspopup') || '').toLowerCase());
  const comps =() => Array.from(doc.querySelectorAll(SEL)).filter((el) => {
    if (el.closest('#ANDI508')) return false;
    const t = (el.type || '').toLowerCase();
    if (el.tagName === 'INPUT' && ['hidden', 'image'].includes(t)) return false;
    if (el.matches(':disabled') || el.getAttribute('aria-disabled') === 'true') return false;
    return vis(el);
  });
  const ids = (el, a) => (el.getAttribute(a) || '').split(/\\s+/).filter(Boolean)
    .map((id) => doc.getElementById(id)).filter(Boolean);
  const labelEls = (el) => {
    const out = [...(el.labels ? Array.from(el.labels) : []), ...ids(el, 'aria-labelledby')];
    return out;
  };
  const groupEls = (el) => {
    const fs = el.closest('fieldset');
    const lg = fs && Array.from(fs.children).find((c) => c.tagName === 'LEGEND');
    if (lg) return [lg];
    const g = el.closest('[role=radiogroup],[role=group]');
    return g ? ids(g, 'aria-labelledby') : [];
  };
"""

COMPONENTS_JS = (
    "(function () {"
    + PATH_JS
    + _SHARED_JS
    + """
  const els = comps();
  window.__a11yLabelEls = els;
  const ownText = (li) => Array.from(li.childNodes).filter((n) => n.nodeType === 3)
    .map((n) => n.textContent).join(' ').replace(/\\s+/g, ' ').trim();
  // The text of the row a button sits in, without the button's own text: what
  // tells same-named buttons apart (5.C, fix 9b).
  const rowText = (el) => {
    const row = el.closest('li, tr, [role=row], [role=listitem], article');
    if (!row) return '';
    const own = txt(el);
    let t = (row.innerText || '').replace(/\\s+/g, ' ').trim();
    if (own && t.includes(own)) t = t.split(own).join(' ');
    return t.replace(/\\s+/g, ' ').trim().slice(0, 120);
  };
  const headers = (el) => {
    const cell = el.closest('td,th');
    if (!cell || !cell.closest('table')) return [];
    const out = [];
    const hdr = (cell.getAttribute('headers') || '').split(/\\s+/).filter(Boolean)
      .map((id) => doc.getElementById(id)).filter(Boolean);
    if (hdr.length) return hdr.map(txt).filter(Boolean);
    const tr = cell.parentElement, table = cell.closest('table');
    const rowTh = Array.from(tr.children).find((c) => c.tagName === 'TH' && c !== cell);
    if (rowTh) out.push(txt(rowTh));
    const idx = Array.from(tr.children).indexOf(cell);
    for (const row of Array.from(table.rows)) {
      if (row === tr) break;
      const c = row.children[idx];
      if (c && c.tagName === 'TH') { out.push(txt(c)); break; }
    }
    return out.filter(Boolean);
  };
  // The visible heading over an option (5.C 1.3.0): the nearest heading
  // before it in the page, inside its form (or its section or landmark).
  const HEAD = 'h1,h2,h3,h4,h5,h6,[role=heading]';
  const headingOf = (el) => {
    const scope = el.form || el.closest('form') ||
      el.closest('section,aside,nav,main,[role=region],[role=search],[role=complementary]') || doc.body;
    let best = null;
    for (const h of scope.querySelectorAll(HEAD)) {
      if (h.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING && !h.contains(el) && vis(h)) best = h;
    }
    return best ? txt(best) : '';
  };
  // The heading sits directly over the option's set (5.C 1.7.0, M3h): no
  // visible text between the heading and the set's first option, so the
  // heading is the question the set answers, not a section title further up.
  const headingEl = (el) => {
    const scope = el.form || el.closest('form') ||
      el.closest('section,aside,nav,main,[role=region],[role=search],[role=complementary]') || doc.body;
    let best = null;
    for (const h of scope.querySelectorAll(HEAD)) {
      if (h.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING && !h.contains(el) && vis(h)) best = h;
    }
    return best;
  };
  const headingDirect = (el, first) => {
    const h = headingEl(el);
    if (!h || headingEl(first) !== h) return false;
    const range = doc.createRange();
    range.setStartAfter(h); range.setEndBefore(first);
    const tw = doc.createTreeWalker(range.commonAncestorContainer, NodeFilter.SHOW_TEXT);
    for (let n = tw.nextNode(); n; n = tw.nextNode()) {
      if (!range.intersectsNode(n) || h.contains(n)) continue;
      const p = n.parentElement;
      if (!p || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(p.tagName) || p.closest('#ANDI508')) continue;
      if (n.textContent.trim() && vis(p)) return false;
    }
    return true;
  };
  return els.map((el, i) => {
    const tag = el.tagName.toLowerCase(), type = (el.type || '').toLowerCase(), role = el.getAttribute('role') || '';
    const button = tag === 'button' || (tag === 'input' && ['submit', 'reset', 'button'].includes(type)) || role === 'button';
    const option = isOpt(el);
    // Options under one legend or group label, whatever their names: the
    // legend labels an option only when it is the set's only one (5.A 1.1.0).
    const cont = option ? el.closest('fieldset,[role=radiogroup],[role=group]') : null;
    const set_size = cont ? els.filter((o) => cont.contains(o) && isOpt(o)).length : 1;
    let group = null;
    if (type === 'radio' || type === 'checkbox') group = (el.form ? path(el.form) : '') + ':' + type + ':' + (el.name || path(el));
    else if (role === 'radio') { const g = el.closest('[role=radiogroup]'); group = g ? 'rg:' + path(g) : null; }
    const r = el.getBoundingClientRect();
    return {
      i, css: path(el), tag, type, role, button, option, group, set_size,
      form: (el.form || el.closest('form')) ? path(el.form || el.closest('form')) : '',
      readonly: el.readOnly === true || el.getAttribute('aria-readonly') === 'true',
      required: el.required === true || el.getAttribute('aria-required') === 'true',
      labels: labelEls(el).map(txt).filter(Boolean),
      group_labels: groupEls(el).map(txt).filter(Boolean),
      placeholder: el.getAttribute('placeholder') || '',
      aria_label: el.getAttribute('aria-label') || '',
      title: el.getAttribute('title') || '',
      own_text: button ? (txt(el) || el.value || '') : '',
      row_text: button ? rowText(el) : '',
      menu: button && isMenu(el),
      heading: isOpt(el) ? headingOf(el) : '',
      // Hidden from screen readers and out of the Tab order (5.C 1.8.0).
      aria_hidden: !!el.closest('[aria-hidden="true"]'),
      tabbable: el.tabIndex >= 0,
      heading_direct: (() => {
        if (!isOpt(el) || !el.name) return false;
        const first = els.find((o) => isOpt(o) && o.name === el.name && (o.form || null) === (el.form || null));
        return !!first && headingDirect(el, first);
      })(),
      table_headers: headers(el),
      list_text: Array.from((function* () { for (let li = el.closest('li'); li; li = li.parentElement && li.parentElement.closest('li')) yield li; })())
        .map(ownText).filter(Boolean),
      box: [Math.round(r.left + scrollX), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height)],
    };
  });
})()"""
)

# Focus component i of the last COMPONENTS_JS read; what is visible around it.
FOCUS_JS = (
    "(function (i) {"
    + PATH_JS
    + _SHARED_JS
    + """
  const els = window.__a11yLabelEls || [];
  const el = els[i];
  if (!el) return null;
  el.scrollIntoView({ block: 'center', inline: 'nearest' });
  try { el.focus({ preventScroll: true }); } catch (e) {}
  const r = el.getBoundingClientRect();
  const vw = innerWidth, vh = innerHeight;
  const reg = { l: Math.max(0, r.left - LEFT), t: Math.max(0, r.top - UP),
                r: Math.min(vw, r.right + RIGHT), b: Math.min(vh, r.bottom + DOWN) };
  const inReg = (b) => b.right > reg.l && b.left < reg.r && b.bottom > reg.t && b.top < reg.b;
  const mine = new Set([...labelEls(el), ...groupEls(el)]);
  const others = [];
  for (const o of els) {
    if (o === el) continue;
    others.push(o);
    for (const x of labelEls(o)) if (!mine.has(x)) others.push(x);
  }
  // Fieldsets that do not hold this field belong to other fields (their
  // legend and content); outside the field's form is not its cue.
  for (const fs of doc.querySelectorAll('fieldset')) if (!fs.contains(el)) others.push(fs);
  const form = el.form || el.closest('form');
  const inOther = (n) => others.some((o) => o === n || o.contains(n)) || (form && !form.contains(n));
  const grp = groupEls(el);
  const labels = [...labelEls(el).map((l) => [l, false]), ...grp.map((l) => [l, true])].map(([l, g]) => ({
    text: txt(l), shown: shown(l) && inReg(l.getBoundingClientRect()), group: g }));
  // A button's text beside the field can label it (G167: a "Search" button
  // by a search box); kept apart, it is not the field's own text (5.C).
  // Only a button that acts on this field's form can label it: not one in
  // another form or outside the field's form, and not a menu or disclosure
  // button (a site header's "Explore" beside its search box; 5.A 1.2.0).
  const btns = [];
  for (const o of els) {
    if (o === el || !isBtn(o) || !shown(o) || !inReg(o.getBoundingClientRect())) continue;
    if ((form && !form.contains(o)) || (o.form && o.form !== form) || isMenu(o)) continue;
    const t = txt(o) || o.value || '';
    if (t && !btns.includes(t)) btns.push(t);
  }
  // Buttons with no text (an icon: a magnifier, a clear button) in the
  // field's input group (the same parent) or in its search form: a picture
  // may label the field, so M3 asks J1 instead of failing (5.A 1.5.0; fix 8).
  // The same filter as above: a menu button never counts.
  const srch = !!((form || el).closest('[role=search],search'));
  let icons = 0;
  for (const o of els) {
    if (o === el || !isBtn(o) || !shown(o) || !inReg(o.getBoundingClientRect())) continue;
    if ((form && !form.contains(o)) || (o.form && o.form !== form) || isMenu(o)) continue;
    if (txt(o) || o.value) continue;
    if (srch || o.parentElement === el.parentElement) icons++;
  }
  // Pictures near the field, not another field's: one may be its label
  // (J1's "graphic"), so a field with one is never failed for having no text.
  let imgs = 0;
  for (const m of doc.querySelectorAll('img,svg,[role=img],input[type=image]')) {
    if (el.contains(m) || inOther(m) || !shown(m) || !inReg(m.getBoundingClientRect())) continue;
    imgs++;
  }
  // An option's nearby text is its own row's (5.C 1.7.0, post-round 2 fix
  // 9c): text in a block that holds a link or another option, and not this
  // option, belongs to that block (a result card added inside a filter form:
  // "ID: 15116"). A question in a block of its own stays.
  const opt = isOpt(el);
  const otherRow = (p) => {
    let b = p;
    while (b.parentElement && !b.parentElement.contains(el)) b = b.parentElement;
    if (b.contains(el)) return false;
    if (b.matches('a[href]') || b.querySelector('a[href]')) return true;
    return els.some((o) => o !== el && isOpt(o) && b.contains(o));
  };
  const near = [];
  const tw = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
  const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    const p = n.parentElement;
    if (!p || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'OPTION', 'TEXTAREA'].includes(p.tagName)) continue;
    if (p.closest('#ANDI508') || el.contains(p) || inOther(p) || !shown(p)) continue;
    // Section headings need no association (5.C p. 27 Note 5): not field text.
    if (p.closest('h1,h2,h3,h4,h5,h6,[role=heading]')) continue;
    const t = n.textContent.replace(/\\s+/g, ' ').trim();
    if (!t) continue;
    const range = doc.createRange(); range.selectNodeContents(n);
    const b = range.getBoundingClientRect();
    if (!b.width || !inReg(b)) continue;
    if (opt && otherRow(p)) continue;
    near.push({ t, g: grp.some((x) => x.contains(p)),
                d: Math.hypot((b.left + b.right) / 2 - cx, (b.top + b.bottom) / 2 - cy) });
  }
  near.sort((a, b) => a.d - b.d);
  // Text the page's style draws (::before / ::after content: a red "*", a
  // "(required)"), which no text node holds (5.C 1.4.0). Quoted strings
  // only; counters, attr() and images are left out. Kept apart: 5.C counts
  // it as visible, 5.A and 5.B do not read it.
  const css = [];
  const root = form || doc.body;
  let seen = 0;
  for (const p of root.querySelectorAll('*')) {
    if (++seen > 3000) break;
    if (p === el || p.closest('#ANDI508') || inOther(p) || !shown(p)) continue;
    const b = p.getBoundingClientRect();
    if (!b.width || !inReg(b)) continue;
    for (const pseudo of ['::before', '::after']) {
      const cs = getComputedStyle(p, pseudo);
      if (!cs || cs.display === 'none' || cs.visibility === 'hidden') continue;
      const lit = (cs.content || '').match(/"(?:[^"\\\\]|\\\\.)*"/g);
      if (!lit) continue;
      const unq = (x) => x.slice(1, -1)
        .replace(/\\\\([0-9a-fA-F]{1,6}) ?/g, (_, h) => String.fromCodePoint(parseInt(h, 16)))
        .replace(/\\\\(.)/g, '$1');
      const t = lit.map(unq).join('').replace(/\\s+/g, ' ').trim();
      if (t && !css.some((x) => x.t === t)) {
        css.push({ t, d: Math.hypot((b.left + b.right) / 2 - cx, (b.top + b.bottom) / 2 - cy) });
      }
    }
  }
  css.sort((a, b) => a.d - b.d);
  // Visible labels of other fields in the region: a set of fields (a phone
  // number in three boxes) may share one label (F82); 5.A's J1 may quote them.
  const nbr = [];
  for (const o of els) {
    if (o === el) continue;
    for (const l of labelEls(o)) {
      const t = txt(l);
      if (t && shown(l) && inReg(l.getBoundingClientRect()) && !nbr.includes(t)) nbr.push(t);
    }
  }
  return {
    focused: doc.activeElement === el,
    labels, nearby: near.map((x) => x.t), nearby_other: nbr.slice(0, 6),
    nearby_own: near.filter((x) => !x.g).map((x) => x.t), nearby_buttons: btns.slice(0, 6), nearby_images: imgs, icon_buttons: icons,
    nearby_css: css.slice(0, 6).map((x) => x.t),
    placeholder_shown: !!el.getAttribute('placeholder') && !el.value,
    // Viewport coordinates: a viewport screenshot's clip is relative to it.
    clip: { x: reg.l, y: reg.t, width: Math.max(1, reg.r - reg.l), height: Math.max(1, reg.b - reg.t) },
  };
})""".replace("LEFT", str(LEFT))
    .replace("UP", str(UP))
    .replace("RIGHT", str(RIGHT))
    .replace("DOWN", str(DOWN))
)


class Comp(BaseModel):
    n: int
    css: str
    tag: str = ""
    type: str = ""
    role: str = ""
    button: bool = False
    option: bool = False
    group: str | None = None
    form: str = ""  # form owner's path; "" outside any form (5.B)
    set_size: int = 1  # options under the same legend or group label
    readonly: bool = False
    required: bool = False
    labels: list[str] = Field(default_factory=list)
    group_labels: list[str] = Field(default_factory=list)
    placeholder: str = ""
    aria_label: str = ""
    title: str = ""
    own_text: str = ""
    row_text: str = ""  # a button: the text of the row it sits in, without its own
    menu: bool = False  # a menu or disclosure button (aria-expanded, aria-haspopup)
    heading: str = (
        ""  # an option's nearest visible heading in its form or section (5.C)
    )
    # The heading sits directly over the option's set: no visible text
    # between it and the set's first option (5.C M3h)
    heading_direct: bool = False
    aria_hidden: bool = False  # itself or an ancestor has aria-hidden="true"
    tabbable: bool = True  # tabIndex >= 0 (in the sequential focus order)
    table_headers: list[str] = Field(default_factory=list)
    list_text: list[str] = Field(default_factory=list)
    # With focus (data-entry fields only)
    focused: bool | None = None
    label_shown: list[dict[str, Any]] = Field(default_factory=list)
    nearby: list[str] = Field(default_factory=list)
    nearby_other: list[str] = Field(default_factory=list)  # other fields' labels
    nearby_own: list[str] = Field(default_factory=list)  # nearby, minus the legend
    nearby_buttons: list[str] = Field(default_factory=list)  # buttons' text nearby
    nearby_images: int = 0  # pictures nearby that are not another field's
    # Buttons with no text in the field's input group or search form (5.A M3)
    icon_buttons: int = 0
    # Text drawn by CSS (::before / ::after) nearby: 5.C counts it as shown
    nearby_css: list[str] = Field(default_factory=list)
    placeholder_shown: bool = False
    image: str | None = None
    andi: dict[str, Any] | None = None  # name, desc, group, dangers, warnings
    origin: str = "load"  # or how a replay revealed it
    tab_index: int | None = None  # P1 step index, when it is a walk stop

    @property
    def entry(self) -> bool:
        """A data-entry field (5.A): takes input; not a button, not read-only."""
        return not self.button and not self.readonly

    @property
    def kind(self) -> str:
        if self.button:
            return "button"
        if self.option:
            return self.type or self.role or "option"
        if self.tag == "select":
            return "drop-down"
        return self.role or (
            "text field" if self.tag in ("input", "textarea") else self.tag
        )


class LabelsPass(BaseModel):
    components: list[Comp] = Field(default_factory=list)
    andi_ran: bool = False
    andi_version: str | None = None
    andi_aborted: list[str] = Field(default_factory=list)
    incomplete: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    revealed_from: list[str] = Field(default_factory=list)
    # What this pass read, by the page inventory's keys (count.py; guard CN):
    # documents only, so nothing inside web components or frames, and no
    # editable areas; hidden fields only those an opened section showed.
    read: dict[str, dict[str, int]] = Field(default_factory=dict)


def _norm(t: str) -> str:
    return " ".join((t or "").split())


async def read_session(
    ctx, s: Session, origin: str, images: bool, tag: str
) -> LabelsPass:
    """Inventory, focus reads and images, then ANDI, on one session (its
    page is changed by ANDI: call this last on a session)."""
    out = LabelsPass()
    page = s.page
    try:
        got = await s.traversal.reader.evaluate_top(COMPONENTS_JS)
    except Exception as exc:
        out.incomplete.append(
            f"The form fields could not be read ({type(exc).__name__})."
        )
        return out
    # Forms inside frames are not read yet: say so, never treat them as absent.
    framed = 0
    for fr in page.frames[1:]:
        try:
            framed += await fr.evaluate(
                "document.querySelectorAll('input:not([type=hidden]),select,textarea,button').length"
            )
        except Exception:
            continue
    if framed:
        out.incomplete.append(
            f"{framed} form field(s) or button(s) inside frames were not checked."
        )
    for c in got or []:
        out.components.append(
            Comp(
                n=len(out.components) + 1,
                origin=origin,
                **{k: v for k, v in c.items() if k not in ("i", "box")},
            )
        )
    if len(out.components) > COMPONENT_MAX:
        out.incomplete.append(
            f"The page has {len(out.components)} form fields and buttons; only the first {COMPONENT_MAX} were checked."
        )
        out.components = out.components[:COMPONENT_MAX]
    for i, c in enumerate(out.components):
        if not c.entry:
            continue
        if ctx.out_of_time():
            out.incomplete.append(
                "The run time limit was reached before every form field was looked at."
            )
            break
        try:
            r = await s.traversal.reader.evaluate_top(f"{FOCUS_JS}({i})")
        except Exception:
            r = None
        if not r:
            continue
        c.focused = r.get("focused")
        c.label_shown = r.get("labels") or []
        c.placeholder_shown = bool(r.get("placeholder_shown"))
        near, total = [], 0
        for t in r.get("nearby") or []:
            if total >= NEARBY_CHARS:
                break
            near.append(t)
            total += len(t)
        c.nearby = near
        c.nearby_other = r.get("nearby_other") or []
        c.nearby_own = r.get("nearby_own") or []
        c.nearby_buttons = r.get("nearby_buttons") or []
        c.nearby_images = r.get("nearby_images") or 0
        c.icon_buttons = r.get("icon_buttons") or 0
        c.nearby_css = r.get("nearby_css") or []
        if images:
            try:
                ctx.shots.mkdir(parents=True, exist_ok=True)
                p = ctx.shots / f"5a-{tag}-{c.n}.png"
                await screenshot(
                    page, path=str(p), clip=r["clip"], animations="disabled"
                )
                c.image = p.resolve().relative_to(ctx.rel.resolve()).as_posix()
            except Exception:
                c.image = None
    # ANDI last: it changes the page.
    if ctx.third_party is not None:
        try:
            # Mark each component before ANDI wraps the page (its wrapper
            # changes CSS paths that do not start at an id): match by mark.
            await s.traversal.reader.evaluate_top(
                "(window.__a11yLabelEls || []).forEach((e, i) => e.setAttribute('data-a11y-c', String(i)))"
            )
            out.andi_aborted = await install_andi_routes(
                s.traversal.context, ctx.third_party
            )
            out.andi_version = await inject_andi(page, ctx.third_party)
            await page.wait_for_timeout(500)
            rows = await andi_output(page)
            if rows is not None:
                out.andi_ran = True
                by_mark = {r.get("mark"): r for r in rows if r.get("mark") is not None}
                for i, c in enumerate(out.components):
                    c.andi = by_mark.get(str(i))
        except Exception as exc:
            out.notes.append(f"ANDI could not run on this page ({type(exc).__name__}).")
    return out


def wanted(ctx) -> bool:
    return bool({"5.A", "5.B", "5.C"} & set(ctx.selected))


async def read_revealed(ctx, s: Session, origin: str) -> bool | None:
    """At the end of a replay that revealed content (4.F pass R, 5.D pass F,
    reveal.py): read its form components with ANDI, for 5.A-5.C (spec 5.C
    section 2, fields revealed by interaction). Only when one of them runs in
    this call (None: not asked); call it last on the session (ANDI changes
    the page). True when read, False when it could not be."""
    if not wanted(ctx):
        return None
    if ctx.out_of_time():
        return False
    try:
        got = await read_session(
            ctx, s, origin, True, f"r{len(ctx.cache.get('labels-revealed', [])) + 1}"
        )
    except Exception:
        return False
    ctx.cache.setdefault("labels-revealed", []).append(got)
    return True


def _signature(c: Comp) -> tuple:
    """What makes a control the same control across opened states."""
    return (
        c.tag,
        c.type,
        c.role,
        c.own_text,
        c.row_text,
        tuple(c.labels),
        tuple(c.group_labels),
        c.heading,
        c.aria_label,
        (c.andi or {}).get("name") if isinstance(c.andi, dict) else None,
    )


async def labels_pass(ctx, walk) -> LabelsPass:
    """Pass L, once per call (5.A and 5.C both read it)."""
    if "labels-pass" in ctx.cache:
        return ctx.cache["labels-pass"].model_copy(deep=True)
    from tobi508.traverse import open_session

    s = await open_session(ctx.new_page, ctx.quiet_ms)
    try:
        lp = await read_session(ctx, s, "load", True, "l")
    finally:
        await s.close()
    seen = {c.css for c in lp.components}
    # The same control read in another opened state has another path (a list
    # that grew above it moved its position): it is the same control when its
    # kind, text, group, heading and row are the same. Compared with what was
    # read before that state, so identical controls inside one state stay.
    sigs = {_signature(c) for c in lp.components}
    for extra in ctx.cache.get("labels-revealed", []):
        fresh: set[tuple] = set()
        for c in extra.components:
            sig = _signature(c)
            if c.css in seen or sig in sigs:
                continue
            seen.add(c.css)
            fresh.add(sig)
            lp.components.append(c.model_copy(update={"n": len(lp.components) + 1}))
            if c.origin not in lp.revealed_from:
                lp.revealed_from.append(c.origin)
        sigs |= fresh
    if walk is not None:
        idx = {
            st.stop.css_path: i
            for i, st in enumerate(walk.p1.steps)
            if st.stop.kind == "element" and not st.stop.frame_chain
        }
        for c in lp.components:
            c.tab_index = idx.get(c.css)
    lp.read = {"page": what_was_read(lp, ctx.cache.get("count"))}
    ctx.cache["labels-pass"] = lp
    return lp.model_copy(deep=True)


def what_was_read(lp: LabelsPass, count) -> dict[str, int]:
    """Pass L's reading by the inventory's keys. Hidden fields are matched by
    path: one is read when an opened section showed it and it was read."""
    opened = {c.css for c in lp.components if c.origin != "load"}
    hidden = set(count.hidden_field_paths) if count is not None else set()
    return {
        "fields.shadow": 0,
        "fields.frames": 0,
        "contenteditable": 0,
        "fields_hidden": len(hidden & opened),
    }
