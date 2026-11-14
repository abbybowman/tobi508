"""One library for reading the page (plan 2026-11-12 part D; review D-19).

`JSLIB` is put at the start of a reader's script, as `PATH_JS` is: it
declares one constant, `J`, whose members are the shared rules every reader
uses, so the readers and the page's inventory (`count.py`) cannot disagree
about what a field is, what is rendered or how to enter a web component.
Readers keep their own rules (what a label is, what an error is).

Members of `J`:

* `roots(root?)`: the document and every open shadow root inside it, at any
  depth, document order (closed roots cannot be entered).
* `all(sel, root?)`: every element matching `sel` in those roots.
* `where(el)`: "light" (the document itself) or "shadow".
* `rendered(el)`: laid out and not `visibility: hidden`.
* `seen(el)`: rendered, at least 4 by 4 px, opacity 0.1 or more, not clipped
  away: what a sighted person can see.
* `text(el)`: visible text, composed tree, hidden words left out (H-01).
* `texts(root, fn)`: every text node of `root` and the shadow roots inside
  it (slotted text is counted where it is written, once).
* `FIELD`, `off(el)`, `field(el)`: the 5.D field selector; a field that is
  disabled, read-only or inert; a field the inventory counts (rendered, not
  off).
* `inert(el)`, `focusable(el)`: the inventory's rule for a Tab stop.
* `byId(el, id)`: an id looked up in `el`'s own tree (an `aria-labelledby`
  inside a web component names an element inside it; review D-21).
* `scope(el)`: the element a reader searches around `el` when it has no
  form: the document's body, or the shadow root holding it.
* `active()`: the focused element, followed into open shadow roots.
* `hostOf(el)`: the tag of the web component holding `el`, or "".
* `path(el)`, `find(path)`: the walk's CSS path (a shadow boundary is one
  space after the host's path) and its reading back, one root at a time.

Frames are not entered here: Python reads each frame as its own document
(part D's design note).
"""

from __future__ import annotations

PATH_JS = """
  const seg = (n) => {
    const root = n.getRootNode();
    if (n.id && root.querySelectorAll('#' + CSS.escape(n.id)).length === 1) return { s: '#' + CSS.escape(n.id), unique: true };
    const tag = n.tagName.toLowerCase();
    // An element directly in a shadow root has the root as its parent node.
    const p = n.parentElement || (n.parentNode && n.parentNode.host ? n.parentNode : null);
    if (!p) return { s: tag, unique: false };
    const same = Array.from(p.children).filter((c) => c.tagName === n.tagName);
    return { s: same.length > 1 ? `${tag}:nth-of-type(${same.indexOf(n) + 1})` : tag, unique: false };
  };
  const path = (n) => {
    const parts = [];
    for (let cur = n; cur && cur.nodeType === 1; cur = cur.parentElement) {
      const { s, unique } = seg(cur);
      parts.unshift(s);
      if (unique || !cur.parentElement) break;
    }
    const root = n.getRootNode();
    return (root.host ? path(root.host) + ' ' : '') + parts.join(' > ');
  };
"""

FIELD_SELECTOR = (
    "input:not([type=hidden]):not([type=button]):not([type=submit]):not([type=reset])"
    ":not([type=image]):not([type=color]):not([type=file]), select, textarea, "
    "[role=textbox], [role=searchbox], [role=combobox], [role=checkbox], [role=switch], "
    "[role=radio], [role=slider], [role=spinbutton]"
)

JSLIB = (
    "const J = (() => {"
    + PATH_JS
    + """
  const roots = (root) => {
    const out = [];
    const visit = (r) => {
      out.push(r);
      for (const el of r.querySelectorAll('*')) if (el.shadowRoot) visit(el.shadowRoot);
    };
    visit(root || document);
    return out;
  };
  const all = (sel, root) => {
    const out = [];
    const visit = (r) => {
      for (const el of r.querySelectorAll('*')) {
        if (el.matches(sel)) out.push(el);
        if (el.shadowRoot) visit(el.shadowRoot);
      }
    };
    visit(root || document);
    return out;
  };
  const where = (el) => (el.getRootNode() === el.ownerDocument ? 'light' : 'shadow');
  const rendered = (el) => !!el && (el.checkVisibility
    ? el.checkVisibility({ visibilityProperty: true }) : el.getClientRects().length > 0);
  const seen = (e) => {
    if (!rendered(e)) return false;
    const r = e.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) return false;
    const cs = getComputedStyle(e);
    if (parseFloat(cs.opacity) < 0.1) return false;
    if ((cs.clip || '').startsWith('rect(0') || (cs.clipPath || '').includes('inset(50%')) return false;
    return true;
  };
  const texts = (root, fn) => {
    const visit = (r) => {
      const tw = document.createTreeWalker(r, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
      for (let n = tw.nextNode(); n; n = tw.nextNode()) {
        if (n.nodeType === 3) fn(n);
        else if (n.shadowRoot) visit(n.shadowRoot);
      }
    };
    visit(root);
  };
  // Visible text (review H-01): the text nodes under `el` in the composed
  // tree (a host's shadow root, a slot's assigned nodes) whose parent a
  // person can see and whose box is on the page; not a select's options.
  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'SELECT', 'OPTION', 'TEXTAREA', 'DATALIST']);
  const text = (el) => {
    if (!el) return '';
    const parts = [];
    const visit = (n) => {
      if (n.nodeType === 3) {
        const p = n.parentElement;
        if (!p || !n.textContent.trim() || !seen(p)) return;
        const range = document.createRange();
        range.selectNodeContents(n);
        const b = range.getBoundingClientRect();
        if (!b.width || b.right + scrollX <= 0 || b.bottom + scrollY <= 0) return;
        parts.push(n.textContent);
        return;
      }
      if (n.nodeType !== 1 && n.nodeType !== 11) return;
      if (n.nodeType === 1 && SKIP.has(n.tagName)) return;
      if (n.nodeType === 1 && n.tagName === 'SLOT') {
        const got = n.assignedNodes({ flatten: true });
        for (const c of (got.length ? got : n.childNodes)) visit(c);
        return;
      }
      for (const c of (n.shadowRoot ? n.shadowRoot.childNodes : n.childNodes)) visit(c);
    };
    visit(el);
    return parts.join(' ').replace(/\\s+/g, ' ').trim();
  };
  const FIELD = '"""
    + FIELD_SELECTOR
    + """';
  const inert = (el) => {
    for (let n = el; n; n = n.parentNode || n.host || null) if (n.nodeType === 1 && n.hasAttribute('inert')) return true;
    return false;
  };
  const off = (el) => el.matches(':disabled') || el.readOnly === true || el.getAttribute('aria-disabled') === 'true'
    || el.getAttribute('aria-readonly') === 'true' || inert(el);
  const field = (el) => el.matches(FIELD) && !off(el) && rendered(el);
  const NATIVE = 'a[href], area[href], button, input:not([type="hidden"]), select, textarea, ' +
    'iframe, frame, summary, audio[controls], video[controls], [contenteditable]:not([contenteditable="false"])';
  const tabindex = (el) => {
    const v = el.getAttribute('tabindex');
    return v !== null && v.trim() !== '' && !isNaN(v) ? parseInt(v, 10) : null;
  };
  const focusable = (el) => {
    const ti = tabindex(el);
    if (ti !== null && ti < 0) return false;
    if (!(el.matches(NATIVE) || ti !== null)) return false;
    if (el.tagName === 'SUMMARY' && !(el.parentElement && el.parentElement.tagName === 'DETAILS' &&
        el.parentElement.querySelector(':scope > summary') === el)) return false;
    return !el.matches(':disabled') && !inert(el) && rendered(el);
  };
  const byId = (el, id) => {
    const r = el.getRootNode();
    return r.getElementById ? r.getElementById(id) : null;
  };
  const scope = (el) => {
    const r = el.getRootNode();
    return r === el.ownerDocument ? (r.body || r.documentElement) : r;
  };
  const active = () => {
    let a = document.activeElement;
    while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
    return a;
  };
  const hostOf = (el) => {
    const r = el.getRootNode();
    return r && r.host ? r.host.tagName.toLowerCase() : '';
  };
  const find = (p) => {
    try {
      let root = document, el = null;
      for (const part of p.split(/(?<![>\\\\]) (?!>)/)) {
        el = root.querySelector(part);
        if (!el) return null;
        root = el.shadowRoot || el;
      }
      return el;
    } catch (e) { return null; }
  };
  return { roots, all, where, rendered, seen, texts, text, FIELD, inert, off, field, NATIVE, tabindex,
    focusable, byId, scope, active, hostOf, path, find };
})();
"""
)
