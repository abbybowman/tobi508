"""Other pages of the same site, read once for 9.A, 9.B and 9.C.

Each page (the tested page and every page the caller named in
`other_pages`) gets one fresh load of its own HAR and one DOM read of its
rendered content in reading order: *units* (text, headings, images with alt
text, controls) and *regions* (banner, navigation, search, complementary,
contentinfo, main). The read is cached in `RunContext.cache["site"]` so the
three checks share it. Facts only: what repeats and what matches; the specs
(specs/rules/9a-bypass.md Terms) decide what that means.

Page content never chooses a page to read (CLAUDE.md principle 5): the pages
are the caller's.
"""

from __future__ import annotations

import asyncio
import hashlib
from typing import Any
from urllib.parse import urlsplit

from pydantic import BaseModel, Field

from tobi508 import count as inventory
from tobi508.jslib import JSLIB
from tobi508.models import Count
from tobi508.traverse import DEST_JS, PATH_JS, NewPage

# Units read per page (9.A spec section 2). 600 until roadmap step 6c:
# round 2's home page has 772, which held every 9.x cell. The read is
# quadratic on one flat list (traverse.PATH_JS): 5 s at 5,000 links.
UNIT_CAP = 5000
# A site search's results page is read whole: its first page of results,
# often filled in by script after load (post-round 2 fix 11).
RESULTS_CAP = 2000
RESULTS_SETTLE_MS = 5000

# Defines units(cap): the page's rendered content in reading order. Shared by
# the site read and 9.A's landing read, so both number units the same way.
UNITS_FN = (
    JSLIB
    + PATH_JS
    + DEST_JS
    + r"""
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const shown = (el) => {
    if (getComputedStyle(el).display === 'contents') return true;
    return el.checkVisibility ? el.checkVisibility({ visibilityProperty: true })
                              : el.getClientRects().length > 0;
  };
  const CONTROL = 'a[href], button, input:not([type="hidden"]), select, textarea, summary, ' +
    '[role=link], [role=button], [role=menuitem], [role=tab], [role=checkbox], [role=radio], ' +
    '[role=switch], [role=combobox], [role=searchbox], [role=textbox], [role=option], ' +
    '[tabindex]:not([tabindex^="-"])';
  const NOT_LANDMARK_ANCESTOR = 'article, aside, main, nav, section, [role=main]';
  const regionRole = (el) => {
    const r = (el.getAttribute('role') || '').trim().split(/\s+/)[0];
    if (['banner', 'navigation', 'search', 'complementary', 'contentinfo', 'main'].includes(r)) return r;
    if (r) return null;
    const t = el.tagName;
    if (t === 'NAV') return 'navigation';
    if (t === 'ASIDE') return 'complementary';
    if (t === 'MAIN') return 'main';
    if (t === 'SEARCH') return 'search';
    if ((t === 'HEADER' || t === 'FOOTER') && !(el.parentElement && el.parentElement.closest(NOT_LANDMARK_ANCESTOR)))
      return t === 'HEADER' ? 'banner' : 'contentinfo';
    return null;
  };
  // Ids in the element's own tree (a web component's ids stay inside it).
  const textOf = (el, ids) => norm(ids.split(/\s+/).map((i) => J.byId(el, i))
    .filter(Boolean).map((e) => e.textContent).join(' '));
  const label = (el) => norm(el.getAttribute('aria-label')) ||
    (el.getAttribute('aria-labelledby') ? textOf(el, el.getAttribute('aria-labelledby')) : '');
  const controlRole = (el) => {
    const r = (el.getAttribute('role') || '').trim().split(/\s+/)[0];
    if (r) return r;
    const t = el.tagName, type = (el.type || '').toLowerCase();
    if (t === 'A') return 'link';
    if (t === 'BUTTON' || t === 'SUMMARY') return 'button';
    if (t === 'SELECT') return el.multiple || el.size > 1 ? 'listbox' : 'combobox';
    if (t === 'TEXTAREA') return 'textbox';
    if (t === 'INPUT') {
      if (['button', 'submit', 'reset', 'image'].includes(type)) return 'button';
      if (type === 'checkbox' || type === 'radio') return type;
      if (type === 'range') return 'slider';
      if (type === 'search') return 'searchbox';
      return 'textbox';
    }
    return 'generic';
  };
  const nameOf = (el) => {
    const l = label(el);
    if (l) return l;
    const t = el.tagName, type = (el.type || '').toLowerCase();
    if (t === 'INPUT' || t === 'SELECT' || t === 'TEXTAREA') {
      if (['button', 'submit', 'reset'].includes(type)) return norm(el.value);
      if (type === 'image') return norm(el.alt);
      const labs = el.labels ? Array.from(el.labels).map((x) => x.textContent).join(' ') : '';
      return norm(labs) || norm(el.getAttribute('placeholder')) || norm(el.title);
    }
    const parts = [];
    const visit = (n) => {
      if (n.nodeType === 3) { parts.push(n.textContent); return; }
      if (n.nodeType !== 1 || !shown(n)) return;
      if (n.tagName === 'IMG') { parts.push(n.getAttribute('alt') || ''); return; }
      if (n.tagName === 'svg' || n.tagName === 'SVG') {
        const tl = n.querySelector('title'); if (tl) parts.push(tl.textContent); return;
      }
      // As rendered: into a web component, and a slot's assigned nodes.
      const kidNodes = n.shadowRoot ? n.shadowRoot.childNodes
        : n.tagName === 'SLOT' && n.assignedNodes({ flatten: true }).length ? n.assignedNodes({ flatten: true })
        : n.childNodes;
      for (const c of kidNodes) visit(c);
    };
    visit(el);
    return norm(parts.join(' ')) || norm(el.title);
  };
  const tabbable = (el) => {
    const ti = el.getAttribute('tabindex');
    if (ti !== null && ti.trim() !== '' && parseInt(ti, 10) < 0) return false;
    if (el.disabled) return false;
    return el.matches('a[href], button, input:not([type="hidden"]), select, textarea, summary') ||
      (ti !== null && ti.trim() !== '' && parseInt(ti, 10) >= 0);
  };
  // The group a link sits in (19.A 1.14.0): its nearest ancestor, at most 4
  // levels up, that holds 3 or more links; an id per ancestor, '' when none.
  const groupIds = new Map();
  const groupOf = (el) => {
    let a = el.parentElement;
    for (let k = 0; a && k < 4; k++, a = a.parentElement) {
      if (a === document.body) break;
      if (a.querySelectorAll('a[href]').length >= 3) {
        if (!groupIds.has(a)) groupIds.set(a, 'g' + groupIds.size);
        return groupIds.get(a);
      }
    }
    return '';
  };
  const units = (cap) => {
    const out = [], regions = [], counts = {}, els = [];
    let truncated = false;
    const box = (el) => {
      const r = el.getBoundingClientRect();
      return [Math.round(r.x + scrollX), Math.round(r.y + scrollY), Math.round(r.width), Math.round(r.height)];
    };
    const push = (el, u, chain) => {
      if (out.length >= cap) { truncated = true; return false; }
      els.push(el);
      const inner = chain.filter((k) => !k.startsWith('main|'));
      out.push(Object.assign({ i: out.length, css: path(el), regions: chain.slice(),
        region_role: inner.length ? inner[inner.length - 1].split('|')[0] : '',
        in_main: chain.some((k) => k.startsWith('main|')), box: box(el),
        keys: norm(el.getAttribute('accesskey') || el.getAttribute('aria-keyshortcuts')) }, u));
      return true;
    };
    // Web components the walk went into (part D), and those inside content
    // that is hidden: both read (nothing hidden is on the page for anyone).
    const roots = new Set();
    const hiddenRoots = (el) => { for (const r of J.roots(el)) if (r instanceof ShadowRoot) roots.add(r);
      if (el.shadowRoot) for (const r of J.roots(el.shadowRoot)) roots.add(r); };
    const walk = (el, chain) => {
      if (truncated) return;
      if (!shown(el)) { hiddenRoots(el); return; }
      if (el.shadowRoot) roots.add(el.shadowRoot);
      const rr = regionRole(el);
      if (rr) {
        counts[rr] = (counts[rr] || 0) + 1;
        const key = rr + '|' + (label(el) || (el.id ? '#' + el.id : '@' + counts[rr]));
        regions.push({ key, role: rr, css: path(el), box: box(el) });
        chain = chain.concat([key]);
      }
      const t = el.tagName;
      if (t === 'IFRAME' || t === 'FRAME') { push(el, { kind: 'frame', role: 'frame', text: '', name: norm(el.title) }, chain); return; }
      if (el.matches(CONTROL)) {
        const name = nameOf(el);
        const raw = el.getAttribute('href');
        push(el, { kind: 'control', role: controlRole(el), name, text: name.toLowerCase().slice(0, 200),
          href: t === 'A' && raw !== null ? el.href : '', href_attr: raw === null ? null : raw,
          dest: t === 'A' && raw !== null ? destHref(el) : '',
          rel: t === 'A' ? norm(el.getAttribute('rel')) : '',
          group: t === 'A' ? groupOf(el) : '',
          submit: !!el.form && (el.type || '').toLowerCase() === 'submit', stop: tabbable(el),
          id: el.id || '' }, chain);
        return;
      }
      const hm = /^H([1-6])$/.exec(t);
      if (hm || el.getAttribute('role') === 'heading') {
        const text = norm(el.textContent);
        if (text) push(el, { kind: 'heading', role: 'heading', level: hm ? +hm[1] : +(el.getAttribute('aria-level') || 2),
          name: text, text: text.toLowerCase().slice(0, 200) }, chain);
        return;
      }
      if (t === 'IMG') {
        const alt = norm(el.getAttribute('alt'));
        if (alt) push(el, { kind: 'image', role: 'img', name: alt, text: alt.toLowerCase().slice(0, 200) }, chain);
        return;
      }
      if (t === 'SCRIPT' || t === 'STYLE' || t === 'TEMPLATE' || t === 'NOSCRIPT') return;
      const own = norm(J.ownText(el));
      if (own) push(el, { kind: 'text', role: 'text', name: own.slice(0, 300), text: own.toLowerCase().slice(0, 200) }, chain);
      for (const c of J.kids(el)) walk(c, chain);
    };
    if (document.body) walk(document.body, []);
    // What it read inside web components, by the inventory's keys (count.py
    // counts every landmark and link in open shadow roots): each root's own
    // tree, once. A read cut by the cap reads only the roots it reached.
    const shadowRead = { landmarks: 0, links: 0 };
    for (const r of roots) {
      shadowRead.landmarks += r.querySelectorAll(J.LANDMARK).length;
      shadowRead.links += r.querySelectorAll(J.LINK).length;
    }
    // Search forms (19.A): a GET submission the tool can make itself.
    const SEARCH_NAME = /^(q|query|search|s|k|keyword|keywords|searchterm|term)$/i;
    const forms = J.all('form').filter(shown).map((f) => {
      const fields = Array.from(f.elements);
      const named = fields.find((e) => e.name && SEARCH_NAME.test(e.name) && e.tagName === 'INPUT');
      const typed = fields.find((e) => e.tagName === 'INPUT' && (e.type || '').toLowerCase() === 'search');
      const isSearch = f.getAttribute('role') === 'search' || !!f.closest('[role=search], search') || !!typed || !!named;
      if (!isSearch) return null;
      const field = typed || named || fields.find((e) => e.tagName === 'INPUT' && ['text', ''].includes((e.type || '').toLowerCase()));
      const hidden = {};
      fields.filter((e) => e.type === 'hidden' && e.name).forEach((e) => { hidden[e.name] = e.value; });
      return { action: f.action, method: (f.getAttribute('method') || 'get').toLowerCase(),
               explicit: !!(f.getAttribute('action') || '').trim(),
               field: field && field.name ? field.name : '', hidden, css: path(f) };
    }).filter(Boolean);
    // Links in navigation, banner or footer regions not shown on load (closed
    // menus): 19.A 1.12.0 W9 cannot say the site navigation does not lead to
    // a page while these were not read (Abby, 2026-11-15).
    const NAV_REGION = 'nav, header, footer, [role=navigation], [role=banner], [role=contentinfo]';
    const hiddenNav = J.all('a[href]').filter((a) => a.closest(NAV_REGION) && !shown(a))
      .map((a) => a.href).slice(0, 2000);
    return { units: out, regions, truncated, url: location.href, els, title: norm(document.title), forms,
             shadow_read: shadowRead, hidden_nav: hiddenNav };
  };
"""
)

READ_JS = "(cap) => {" + UNITS_FN + " const r = units(cap); delete r.els; return r; }"


class Unit(BaseModel):
    i: int
    kind: str  # text | heading | image | control | frame
    role: str
    text: str  # the text key: lower case, spaces collapsed
    name: str = ""
    css: str
    regions: list[str] = Field(default_factory=list)  # region keys, outer first
    region_role: str = ""  # innermost region other than main
    in_main: bool = False
    box: list[int] = Field(default_factory=list)  # page x, y, width, height
    href: str = ""
    # Where the link goes, '' when nowhere (DEST_JS): the pairing key of 9.C.
    dest: str = ""
    href_attr: str | None = None
    rel: str = ""  # a link's rel attribute (19.A 1.13.0: prev, next)
    # The group a link sits in: its nearest ancestor (4 levels at most) with
    # 3 or more links, an id on its page; "" when none.
    group: str = ""
    submit: bool = False
    stop: bool = False  # natively tabbable or tabindex >= 0
    id: str = ""
    level: int | None = None
    keys: str = ""  # accesskey or aria-keyshortcuts


class Region(BaseModel):
    key: str  # role|label, role|#id or role|@n
    role: str
    css: str
    box: list[int] = Field(default_factory=list)


class PageRead(BaseModel):
    n: int  # 0: the tested page; 1..5: the caller's other pages
    url: str
    units: list[Unit] = Field(default_factory=list)
    regions: list[Region] = Field(default_factory=list)
    truncated: bool = False
    title: str = ""
    forms: list[dict[str, Any]] = Field(default_factory=list)  # search forms
    error: str = ""
    # The page's inventory, on this same load (count.py; guard CN).
    count: Count | None = None
    # Landmarks and links inside web components the read covered (part D):
    # the inventory's keys, so guard CN compares them.
    shadow_read: dict[str, int] = Field(default_factory=dict)
    # Addresses of links in navigation, banner or footer regions that were
    # not shown on load (closed menus; 19.A W9).
    hidden_nav: list[str] = Field(default_factory=list)
    # The same document as the tested page, under another address (K-01).
    identical: bool = False
    # Nearly the same page: the same address apart from the query string, and
    # at least NEAR_COPY of its text keys shared (K-01, spec A2).
    near_copy: bool = False
    # The draw wait saw this page draw itself after load (step 23's DRAWN):
    # an other page so drawn is read twice (#134, the double read).
    drew_late: bool = False


class SiteRead(BaseModel):
    pages: list[PageRead]
    # Step 26 (#134): other pages set aside, one plain sentence each (could
    # not be read in full, or the tested page again), and how many the
    # caller gave. The tests compare the tested page with the rest.
    left_out: list[str] = Field(default_factory=list)
    given: int = 0
    # Each other page's address as the caller gave it, by number (labels).
    given_urls: dict[int, str] = Field(default_factory=dict)

    def label(self, p: PageRead) -> str:
        """An other page by its path, as the caller gave it (step 26)."""
        return short_path(self.given_urls.get(p.n, p.url))

    def leave_out(self, test, why) -> SiteRead:
        """A copy without the other pages `test` picks, each named in
        `left_out` with `why(page)` (9.A: a page over its read cap)."""
        drop = [p for p in self.others if test(p)]
        return self.model_copy(
            update={
                "pages": [p for p in self.pages if p not in drop],
                "left_out": self.left_out + [why(p) for p in drop],
            }
        )

    def compared_sentence(self) -> str:
        """For the finding's summary (the pre-SCRT comment): how many other
        pages were read in full and compared, and which were left out."""
        n = len(self.others)
        if not self.given:
            return ""
        names = ", ".join(self.label(p) for p in self.others)
        s = (
            f"We compared this page with {n} of the {self.given} other "
            f"page{'' if self.given == 1 else 's'} given"
            + (f": {names}." if n else ".")
        )
        if self.left_out:
            s += " Left out: " + "; ".join(self.left_out) + "."
        return s

    @property
    def main(self) -> PageRead:
        return self.pages[0]

    @property
    def others(self) -> list[PageRead]:
        return self.pages[1:]

    @property
    def read(self) -> dict[str, dict[str, int]]:
        """What the site read covered on each page it read, for guard CN
        (count.py): `walk` follows the page as rendered, into open shadow
        roots (part D), so the landmarks and links of every web component it
        reached; a frame is one unit, its content not read."""
        return {
            ("page" if p.n == 0 else f"p{p.n}"): {
                "landmarks.shadow": p.shadow_read.get("landmarks", 0),
                "links.shadow": p.shadow_read.get("links", 0),
                "landmarks.frames": 0,
                "links.frames": 0,
            }
            for p in self.pages
            if not p.error
        }

    @property
    def errors(self) -> list[str]:
        """Rows A2 (step 26): the tested page could not be read, or no other
        page is left to compare with."""
        out = [
            f"{page_label(p)} could not be read: {p.error}"
            for p in self.pages
            if p.error
        ]
        if self.given and not self.others:
            out.append(
                "none of the other pages given could be compared: "
                + "; ".join(self.left_out)
            )
        return out


def page_label(p: PageRead) -> str:
    return "the tested page" if p.n == 0 else f"other page {p.n}"


async def read_page(
    n: int, url: str, new_page: NewPage, results: bool = False
) -> PageRead:
    """One fresh load of a page's HAR and one DOM read (no key pressed).
    `results`: a site search's results page, read after its scripts have
    fetched what they fetch, with a larger cap."""
    try:
        context, page = await new_page()
    except Exception as exc:
        return PageRead(n=n, url=url, error=type(exc).__name__)
    try:
        await page.wait_for_load_state("load")
        if results:
            try:
                await page.wait_for_load_state("networkidle", timeout=RESULTS_SETTLE_MS)
            except Exception:
                pass
        from tobi508.traverse import DRAWN, wait_drawn

        await wait_drawn(page)  # step 23: an application draws after load
        seen = DRAWN.get() or {}
        drew_late = (seen.get(page.url.split("#", 1)[0]) or 0.0) > 0.0
        data = await page.evaluate(READ_JS, RESULTS_CAP if results else UNIT_CAP)
        try:
            count = await inventory.take(page, "site read")
        except Exception as exc:
            count = Count(where="site read", error=type(exc).__name__)
        return PageRead(
            count=count,
            n=n,
            url=data["url"],
            units=[Unit(**u) for u in data["units"]],
            regions=[Region(**r) for r in data["regions"]],
            truncated=data["truncated"],
            title=data.get("title") or "",
            forms=data.get("forms") or [],
            shadow_read=data.get("shadow_read") or {},
            hidden_nav=data.get("hidden_nav") or [],
            drew_late=drew_late,
        )
    except Exception as exc:
        return PageRead(n=n, url=url, error=type(exc).__name__)
    finally:
        await context.close()


async def _cached_read(p: Any) -> PageRead:
    """An other page's read, from pagecache when this recording was read in
    an earlier call of this server session."""
    from tobi508 import pagecache

    hit = pagecache.read("site", getattr(p, "har_sha", None))
    if hit is not None:
        return hit.model_copy(update={"n": p.n})
    got = await read_page(p.n, p.final_url, p.new_page)
    if got.drew_late and not got.error:
        got = await _read_again(p, got)
    pagecache.keep_read("site", getattr(p, "har_sha", None), got)
    return got


def _texts(r: PageRead) -> set[str]:
    return {u.text for u in r.units if u.text and u.kind != "frame"}


async def _read_again(p: Any, first: PageRead) -> PageRead:
    """The double read (#134; Abby, 2026-11-20). An other page that draws
    itself after load is read on a second fresh load, and the read is used
    only when both show the same texts. Round 3's gate: one read of the
    community home page lacked part of its header, so 9.A found almost
    nothing repeated on the forum and said DOES NOT APPLY where the key
    fails. When the two differ, the page could not be read in full: it is
    left out (step 26), and never cached."""
    second = await read_page(p.n, p.final_url, p.new_page)
    if second.error:
        return second
    if _texts(first) == _texts(second):
        return first
    return first.model_copy(
        update={
            "error": "two reads of it differed; it draws itself after loading",
            "units": [],
        }
    )


NEAR_COPY = 0.9  # the share of text keys two pages share to be "nearly the same"


def _address_no_query(url: str) -> tuple[str, int | None, str]:
    p = urlsplit(url)
    try:
        port = p.port
    except ValueError:
        port = None
    if port in (80, 443):
        port = None
    return ((p.hostname or "").lower().rstrip("."), port, p.path.rstrip("/") or "/")


def text_share(a: PageRead, b: PageRead) -> float:
    """The share of text keys two pages have in common: |A and B| / |A or B|
    over the keys of their units (frame units apart). 0.0 with no text."""
    ka = {u.text for u in a.units if u.text and u.kind != "frame"}
    kb = {u.text for u in b.units if u.text and u.kind != "frame"}
    both = ka | kb
    return len(ka & kb) / len(both) if both else 0.0


def near_copy(main: PageRead, other: PageRead) -> bool:
    """The other page is the tested page again with another query string and
    nearly the same content (K-01; a server that changes the page on every
    request defeats the byte comparison)."""
    if main.error or other.error or not main.url or not other.url:
        return False
    if _address_no_query(main.url) != _address_no_query(other.url):
        return False
    return text_share(main, other) >= NEAR_COPY


async def site_read(ctx: Any) -> SiteRead:
    """The tested page and every other page, read once per run (cached)."""
    if "site" not in ctx.cache:
        reads = await asyncio.gather(
            read_page(0, "", ctx.new_page),
            *(_cached_read(p) for p in ctx.pages),
        )
        pages = list(reads)
        # A copy: the read may be the one pagecache keeps for other runs.
        for i, ref in enumerate(ctx.pages, 1):
            if getattr(ref, "same_content_as_tested", False):
                pages[i] = pages[i].model_copy(update={"identical": True})
            elif near_copy(pages[0], pages[i]):
                pages[i] = pages[i].model_copy(update={"near_copy": True})
        # Step 26 (#134): an other page that could not be read, or that is
        # the tested page again, is set aside; the rest are compared.
        given_urls = {r.n: r.url for r in ctx.pages}
        kept = [pages[0]]
        left: list[str] = []
        for p in pages[1:]:
            why = left_out_reason(p)
            if why:
                left.append(f"{short_path(given_urls.get(p.n, p.url))} {why}")
            else:
                kept.append(p)
        ctx.cache["site"] = SiteRead(
            pages=kept, left_out=left, given=len(ctx.pages), given_urls=given_urls
        )
    return ctx.cache["site"]


def left_out_reason(p: PageRead) -> str:
    """Why an other page is not compared (step 26), or "" to compare it."""
    if p.error:
        return f"could not be read ({p.error[:80]})"
    if p.identical:
        return (
            "is the tested page again (the same address apart from the query "
            "string, and the same document)"
        )
    if p.near_copy:
        return (
            "is nearly the same page as the tested page (the same address "
            "apart from the query string, and nearly the same text)"
        )
    return ""


def short_path(url: str) -> str:
    """An other page's address without its scheme and host, which the
    tested page's give (step 26's sentence: Abby, 2026-11-20). Redacted as
    every address in output is: no query string (it can carry a token)."""
    from tobi508.redact import safe_url

    return urlsplit(safe_url(url)).path or "/"


def same_place(a: str, b: str) -> bool:
    """The same host and path apart from the query string (step 26): only
    then can an identical document make an other page the tested page again.
    An application can send one document for every address and draw each
    page in the browser (round 3's p07 to p10)."""
    return _address_no_query(a) == _address_no_query(b)


# ── Facts about repetition and matching (no outcomes) ───────────────────────


def repeated_flags(site: SiteRead) -> list[bool]:
    """Per unit of the tested page: its text key appears on another page, or
    it sits in a region (not main) that another page also has (9.A Terms)."""
    texts: set[str] = set()
    regions: set[str] = set()
    for p in site.others:
        texts |= {u.text for u in p.units if u.text}
        regions |= {r.key for r in p.regions if r.role != "main"}
    return [
        bool(u.text and u.text in texts)
        or any(k in regions for k in u.regions if not k.startswith("main|"))
        for u in site.main.units
    ]


def norm_href(href: str, page_url: str = "") -> str:
    """A link destination for matching: absolute, fragment dropped unless the
    link is to a place on its own page, trailing slash ignored."""
    if not href:
        return ""
    base, _, frag = href.partition("#")
    own = page_url.split("#")[0]
    if frag and own and base == own:
        return "#" + frag
    return base.rstrip("/")


def before(a: list[int], b: list[int]) -> bool:
    """Visual order (9.B Terms): a's box ends above b's, or they share a line
    and a is to the left. Boxes are page x, y, width, height."""
    if not a or not b or a[2] * a[3] == 0 or b[2] * b[3] == 0:
        return False
    if a[1] + a[3] <= b[1] + 1:
        return True
    overlap = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    if overlap >= 0.5 * min(a[3], b[3]):
        return a[0] + a[2] <= b[0] + 1
    return False


ALIGN_MAX_CELLS = 6_000_000  # table size past which equal items pair in order


def pair_in_order(left: list[tuple[str, int]], right: list[tuple[str, int]]):
    """Pair items with equal keys, the k-th with the k-th. Each item is (key,
    position); returns (left position, right position) pairs. The fallback of
    `pair_aligned` for lists too long to align."""
    from collections import defaultdict

    slots: dict[str, list[int]] = defaultdict(list)
    for k, pos in right:
        slots[k].append(pos)
    taken: dict[str, int] = defaultdict(int)
    out = []
    for k, pos in left:
        j = taken[k]
        if j < len(slots[k]):
            out.append((pos, slots[k][j]))
            taken[k] = j + 1
    return out


def pair_aligned(left: list[tuple[str, int]], right: list[tuple[str, int]]):
    """Pair items with equal keys by an alignment that keeps their order where
    it can (Terms). Each item is (key, position); returns (left
    position, right position) pairs in left order.

    The longest common subsequence of the two key lists is the alignment (a
    key found once on each page weighs more than any number of repeated ones,
    so a repeated link gives way to the unique ones around it). Items it keeps
    are paired as aligned; an extra copy of a repeated key on one page is then
    an insertion, not a swap. Copies it cannot keep on both pages (an equal
    number of unaligned copies of one key) pair in order, so a real reorder
    still crosses. Pure and deterministic; lists whose table would pass
    `ALIGN_MAX_CELLS` pair in order, as before 1.7.0."""
    from collections import Counter, defaultdict

    lc, rc = Counter(k for k, _ in left), Counter(k for k, _ in right)
    li = [(k, p) for k, p in left if k in rc]
    ri = [(k, p) for k, p in right if k in lc]
    if all(lc[k] == 1 and rc[k] == 1 for k, _ in li):
        return pair_in_order(li, ri)  # no repeated key: nothing to align
    a, b = [k for k, _ in li], [k for k, _ in ri]
    top = max(len(a), len(b)) + 1

    def weight(k: str) -> int:
        return top if lc[k] == 1 and rc[k] == 1 else 1

    # Equal ends always pair; the table covers what is between them.
    pre = 0
    while pre < min(len(a), len(b)) and a[pre] == b[pre]:
        pre += 1
    suf = 0
    while (
        suf < min(len(a), len(b)) - pre and a[len(a) - 1 - suf] == b[len(b) - 1 - suf]
    ):
        suf += 1
    ma, mb = a[pre : len(a) - suf], b[pre : len(b) - suf]
    if len(ma) * len(mb) > ALIGN_MAX_CELLS:
        return pair_in_order(li, ri)
    n, m = len(ma), len(mb)
    step = bytearray((n + 1) * (m + 1))  # 1 pair, 2 skip left, 3 skip right
    below = [0] * (m + 1)
    for i in range(n - 1, -1, -1):
        row = [0] * (m + 1)
        for j in range(m - 1, -1, -1):
            best, how = below[j], 2
            if row[j + 1] > best:
                best, how = row[j + 1], 3
            if ma[i] == mb[j] and below[j + 1] + weight(ma[i]) >= best:
                best, how = below[j + 1] + weight(ma[i]), 1
            row[j], step[i * (m + 1) + j] = best, how
        below = row
    kept: list[tuple[int, int]] = [(x, x) for x in range(pre)]
    i = j = 0
    while i < n and j < m:
        how = step[i * (m + 1) + j]
        if how == 1:
            kept.append((pre + i, pre + j))
            i += 1
            j += 1
        elif how == 2:
            i += 1
        else:
            j += 1
    kept += [(len(a) - suf + x, len(b) - suf + x) for x in range(suf)]
    # Copies the alignment dropped on both pages pair in order (a reorder).
    used_a, used_b = {x for x, _ in kept}, {y for _, y in kept}
    spare_a: dict[str, list[int]] = defaultdict(list)
    spare_b: dict[str, list[int]] = defaultdict(list)
    for x, k in enumerate(a):
        if x not in used_a:
            spare_a[k].append(x)
    for y, k in enumerate(b):
        if y not in used_b:
            spare_b[k].append(y)
    for k, xs in spare_a.items():
        kept += list(zip(xs, spare_b.get(k, []), strict=False))
    return [(li[x][1], ri[y][1]) for x, y in sorted(kept)]


# ── Kinship: do the other pages share a template with the tested page? ──────
# Counts only; 9.A, 9.B and 9.C decide what they mean (their specs, A3o and
# N2o). Round 2: pages of different templates shared 0, pages of one template
# 10 or more.

SMALL_WORDS = 4  # 9.A A4: "one control, or fewer than 4 words in all"
NAV_ROLES = {"banner", "navigation", "search", "contentinfo"}
NAV_LINKS = 4  # links outside main that count as a navigation of their own


class Kin(BaseModel):
    """The tested page compared with one other page."""

    n: int
    shared_units: int = 0  # tested-page units whose text key is on that page
    shared_controls: int = 0
    shared_words: int = 0
    shared_regions: list[str] = Field(default_factory=list)  # by label or id
    almost_nothing: bool = False


class Kinship(BaseModel):
    """Recorded in each 9.x evidence file (for the later site-wide store)."""

    own_navigation: bool = False  # the tested page has navigation of its own
    fingerprints: dict[int, str] = Field(default_factory=dict)  # page n -> hash
    pages: list[Kin] = Field(default_factory=list)
    all_unrelated: bool = False  # every other page shares almost nothing
    # A3o (9.A, 9.C) and N2o/A3o (9.B): nothing can be said about repetition
    unrelated_review: bool = False  # all_unrelated and own_navigation

    def almost_nothing(self, n: int) -> bool:
        return any(k.n == n and k.almost_nothing for k in self.pages)


UNRELATED_REASON = (
    "The other pages you gave share almost nothing with this page, so they "
    "look like they come from a different template, and we could not tell "
    "which content repeats. Give pages that use the same header, menu and "
    "footer as this one."
)

# A3o when nothing matches but the tested page has navigation of its own
# (9.A 1.6.0, 9.B 1.5.0, 9.C 1.8.0; Abby 2026-11-14, round 2 item 13: CILab,
# whose top links match nothing on the main site's pages).
NO_MATCH = {
    "9.A": "Nothing on this page appears on the other pages you gave, so we "
    "could not tell which content repeats.",
    "9.B": "None of this page's navigation appears on the other pages you "
    "gave, so we could not tell whether it is consistent with theirs.",
    "9.C": "None of this page's links or controls appear on the other pages "
    "you gave, so we could not tell whether they are named consistently.",
}
SAME_PART = (
    "Give other pages from the same part of the site (for a microsite, its own pages)."
)


def a3o_reason(kin: Kinship, test: str) -> str:
    """Row A3o's sentence: another template when every other page shares
    almost nothing, else nothing matching."""
    return UNRELATED_REASON if kin.all_unrelated else f"{NO_MATCH[test]} {SAME_PART}"


def _named_regions(p: PageRead) -> set[str]:
    """Region keys that name a label or id (`role|label`, `role|#id`), not a
    place among their role (`role|@n`); main is left out."""
    return {r.key for r in p.regions if r.role != "main" and "|@" not in r.key}


def template_fingerprint(p: PageRead) -> str:
    named = sorted(_named_regions(p))
    roles = sorted(r.role for r in p.regions if r.role != "main")
    blob = "\n".join(named) + "\n--\n" + ",".join(roles)
    return hashlib.sha256(blob.encode()).hexdigest()[:12]


def has_own_navigation(p: PageRead) -> bool:
    if any(r.role in NAV_ROLES for r in p.regions):
        return True
    links = [u for u in p.units if u.kind == "control" and u.role == "link"]
    return sum(1 for u in links if not u.in_main) >= NAV_LINKS


def kin(main: PageRead, other: PageRead) -> Kin:
    there = {u.text for u in other.units if u.text and u.kind != "frame"}
    shared = [u for u in main.units if u.text and u.kind != "frame" and u.text in there]
    regions = sorted(_named_regions(main) & _named_regions(other))
    words = sum(len(u.text.split()) for u in shared)
    controls = sum(1 for u in shared if u.kind == "control")
    return Kin(
        n=other.n,
        shared_units=len(shared),
        shared_controls=controls,
        shared_words=words,
        shared_regions=regions,
        almost_nothing=not regions and (len(shared) <= 1 or words < SMALL_WORDS),
    )


def kinship(site: SiteRead) -> Kinship:
    pages = [kin(site.main, p) for p in site.others]
    own = has_own_navigation(site.main)
    every = bool(pages) and all(k.almost_nothing for k in pages)
    return Kinship(
        own_navigation=own,
        fingerprints={p.n: template_fingerprint(p) for p in site.pages},
        pages=pages,
        all_unrelated=every,
        unrelated_review=every and own,
    )


def with_compared(f: Any, sentence: str) -> Any:
    """Step 26 (#134): every finding of 9.A to 9.C and 19.A says, in its
    summary (the pre-SCRT comment), how many other pages it compared and
    which were left out. Not on A1 (no pages) or A2 (it says why)."""
    if sentence and f.rows[:1] not in (["A1"], ["A2"]):
        f.summary = f"{f.summary} {sentence}".strip()
    return f
