"""Opening everything, phase 1 (post-round 2 fix 9b; plan
docs/plans/2026-11-08-rules-principle3-build.md): open the menus, tabs,
accordions and filters a page has and record what each one shows, so the
tests that read the page can read what appears. Facts only; no outcome is
decided here (CLAUDE.md principle 2): the guard rows are in the specs.

A *trigger* is a stop of the Tab walk that announces it opens something: a
collapsed control (`aria-expanded` false, a closed `<summary>`), one with
`aria-haspopup`, one that names a region in `aria-controls` that is hidden, or
a tab that is not the selected one. Form fields (including the parts of a
native date input) are not triggers. A plain button with no such hint is not a trigger.
Each is opened on its own fresh load: focus is put on it directly and Enter is
pressed (a click when Enter did nothing). What was not visible before and is
now is what it opened. When the opened content holds sets of check boxes or
radio buttons, up to two options of each are chosen (Space), each on a fresh
load, because choosing one can add controls (a filter that adds a remove
button for each choice). For 5.A-5.C every opened state is read with ANDI
like the page as loaded (`labels.read_revealed`).

What was not opened, and why, is kept: a guard in the specs of the tests
that read opened content moves a would-be PASS to NEEDS REVIEW for it.
Phase 2 (the keyboard walk through opened content) and phase 3 (5.D fills
opened fields) are on the ROADMAP; until then opened content that holds
something a test checks is itself a reason for review (guard
`reveal-content`).
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from tobi508 import labels
from tobi508.observe import observe
from tobi508.traverse import PATH_JS, Session, open_session, screenshot, settle

MAX_TRIGGERS = 20
MAX_SETS = 3  # check box or radio sets tried inside one opened trigger
MAX_OPTIONS = 2  # options chosen in each set

# Status of a trigger. "navigated" is a link that goes elsewhere, not a
# disclosure; every other status except "opened" is something not opened.
OPENED = "opened"
NOTHING = "nothing"  # Enter and a click changed nothing visible
NAVIGATED = "navigated"
NOT_FOUND = "not_found"  # could not be found or focused again
ERROR = "error"
NOT_TRIED = "not_tried"  # over the cap or out of time

# Plain words for each reason a trigger was not opened (the evidence and the
# guard's sentence use them).
WHY = {
    NOTHING: "pressing it showed nothing new",
    NOT_FOUND: "it could not be found again on a fresh load",
    ERROR: "opening it failed to run",
    NOT_TRIED: "it was not tried (over the limit of 20, or out of time)",
}

_COMMON_JS = (
    PATH_JS
    + """
  const vis = (el) => el.checkVisibility ? el.checkVisibility({ visibilityProperty: true }) : el.getClientRects().length > 0;
  const find = (p) => { try { let root = document, el = null;
      for (const part of p.split(/(?<!>) (?!>)/)) { el = root.querySelector(part); if (!el) return null; root = el.shadowRoot || el; }
      return el; } catch (e) { return null; } };
  const chainOf = () => { const c = [];
    try { for (let w = window; w.frameElement; w = w.parent) c.unshift(path(w.frameElement)); }
    catch (e) { c.unshift('?'); }
    return c; };
  const FOCUSABLE = 'a[href], area[href], button, input:not([type="hidden"]), select, textarea, summary, ' +
    '[tabindex]:not([tabindex^="-"]), [contenteditable]:not([contenteditable="false"])';
  const FIELD = 'input:not([type=hidden]):not([type=button]):not([type=submit]):not([type=reset]):not([type=image]), ' +
    'select, textarea, [role=textbox], [role=checkbox], [role=radio], [role=switch], [role=combobox]';
"""
)

# Every rendered element of one frame: [path, focusable, field] (shadow
# roots included), and its frame chain.
STATE_FN = (
    "() => {"
    + _COMMON_JS
    + """
  const items = [];
  const walk = (root) => { for (const el of root.querySelectorAll('*')) {
    if (vis(el)) items.push([path(el), el.matches(FOCUSABLE) && !el.matches(':disabled'), el.matches(FIELD)]);
    if (el.shadowRoot) walk(el.shadowRoot); } };
  walk(document);
  return { chain: chainOf(), items: items.slice(0, 6000) };
}"""
)

# Put focus on the element at a path in this frame (its chain must be the
# one asked for): its aria-expanded and where its box is.
FOCUS_FN = (
    "(chain, css) => {"
    + _COMMON_JS
    + """
  if (chainOf().join(' >> ') !== chain) return null;
  const el = find(css);
  if (!el || !vis(el)) return { found: false };
  el.scrollIntoView({ block: 'center', inline: 'center' });
  el.focus({ preventScroll: true });
  const r = el.getBoundingClientRect();
  return { found: true, focused: document.activeElement === el || el.contains(document.activeElement),
           expanded: el.getAttribute('aria-expanded'), x: r.x + r.width / 2, y: r.y + r.height / 2 };
}"""
)

# Check box and radio sets among the elements at the given paths (the newly
# shown ones): [{label, options: [{css, label}]}], options not yet chosen.
SETS_FN = (
    "(chain, paths) => {"
    + _COMMON_JS
    + """
  if (chainOf().join(' >> ') !== chain) return [];
  const sets = new Map();
  for (const p of paths) {
    const el = find(p);
    if (!el || !el.matches('input[type=checkbox], input[type=radio], [role=checkbox], [role=radio]')) continue;
    if (el.matches(':disabled') || el.checked || el.getAttribute('aria-checked') === 'true') continue;
    const radio = el.matches('input[type=radio], [role=radio]');
    const host = el.closest('fieldset, [role=group], [role=radiogroup]');
    const key = (radio && el.name ? 'radio:' + el.name : 'host:' + (host ? path(host) : path(el.parentElement || el)));
    const legend = host ? ((host.querySelector('legend') || host).innerText || '') : '';
    const text = ((el.labels && el.labels[0] && el.labels[0].innerText) || el.getAttribute('aria-label') ||
      (el.parentElement && el.parentElement.innerText) || el.value || '').replace(/\\s+/g, ' ').trim().slice(0, 80);
    if (!sets.has(key)) sets.set(key, { label: legend.replace(/\\s+/g, ' ').trim().slice(0, 80), options: [] });
    sets.get(key).options.push({ css: p, label: text });
  }
  return Array.from(sets.values());
}"""
)


class Option(BaseModel):
    """One option chosen inside opened content."""

    set_label: str = ""
    label: str = ""
    css_path: str = ""
    chosen: bool = False
    read: bool = False  # the page was read with ANDI after choosing it
    new_elements: int = 0  # shown after choosing it, not before


class Opened(BaseModel):
    n: int
    name: str = ""
    role: str | None = None
    tag: str | None = None
    css_path: str = ""
    frame_chain: list[str] = Field(default_factory=list)
    why: list[str] = Field(default_factory=list)  # why it is a trigger
    status: str = NOT_TRIED
    reason: str = ""
    by: str = ""  # "Enter" or "a click"
    new_elements: int = 0
    new_focusable: int = 0  # what a keyboard user could reach in it
    new_fields: int = 0
    dialog: bool = False
    read: bool | None = None  # ANDI read the opened state (None: not asked)
    picture: str | None = None
    options: list[Option] = Field(default_factory=list)

    @property
    def not_opened(self) -> bool:
        return self.status not in (OPENED, NAVIGATED)


class Reveal(BaseModel):
    triggers: list[Opened] = Field(default_factory=list)
    over_cap: int = 0
    incomplete: list[str] = Field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        """What the guards read (Report.reveal)."""
        bad = [t for t in self.triggers if t.not_opened]
        return {
            "triggers": len(self.triggers) + self.over_cap,
            "opened": sum(t.status == OPENED for t in self.triggers),
            "not_opened": [
                {"name": t.name or t.css_path, "why": t.reason or WHY.get(t.status, "")}
                for t in bad
            ]
            + (
                [{"name": f"{self.over_cap} more", "why": WHY[NOT_TRIED]}]
                if self.over_cap
                else []
            ),
            "read_failed": [
                t.name or t.css_path
                for t in self.triggers
                if t.status == OPENED and t.read is False
            ],
            "opened_with_focusable": sum(
                t.status == OPENED and t.new_focusable > 0 for t in self.triggers
            ),
        }


def reasons(stop) -> list[str]:
    """Why a stop is a trigger; empty when it is not one."""
    out: list[str] = []
    # A form field is not a disclosure (a combobox opens its list as you type,
    # a spinbutton updates a total: 5.D's matter), and the parts of a native
    # date input open the browser's own picker, which is not page content.
    if stop.control or stop.group:
        return out
    if stop.collapsed:
        out.append("summary" if stop.tag == "summary" else "collapsed")
    if stop.haspopup:
        out.append("popup")
    if stop.controls and stop.controls_hidden:
        out.append("controls")
    if stop.tab_unselected:
        out.append("tab")
    return out


def triggers(walk) -> list[tuple[Any, list[str]]]:
    """The walk's trigger stops, once each, in Tab order."""
    seen: set[str] = set()
    out = []
    for step in walk.p1.steps:
        st = step.stop
        if st.kind != "element" or st.unresolved or st.path_key in seen:
            continue
        why = reasons(st)
        if why:
            seen.add(st.path_key)
            out.append((st, why))
    return out


async def _state(s: Session) -> dict[str, tuple[bool, bool]]:
    """Every rendered element of every frame the tool can read, by frame
    chain and path: (focusable, field)."""
    out: dict[str, tuple[bool, bool]] = {}
    r = s.traversal.reader
    for _, sess, ctx in await r.frames():
        try:
            got = await r.call_in(sess, ctx, STATE_FN)
        except Exception:
            continue
        pre = " >> ".join(got["chain"])
        for p, foc, fld in got["items"]:
            out[f"{pre}|{p}"] = (bool(foc), bool(fld))
    return out


async def _focus(s: Session, frame_chain: list[str], css: str) -> dict | None:
    """Focus the trigger directly; its aria-expanded and centre."""
    r = s.traversal.reader
    chain = " >> ".join(frame_chain)
    for _, sess, ctx in await r.frames():
        try:
            got = await r.call_in(sess, ctx, FOCUS_FN, [chain, css])
        except Exception:
            continue
        if got is not None:
            return got if got.get("found") else None
    return None


async def _sets(s: Session, new: list[str]) -> list[dict]:
    """Check box and radio sets among the newly shown elements."""
    r = s.traversal.reader
    out: list[dict] = []
    by_chain: dict[str, list[str]] = {}
    for key in new:
        chain, _, p = key.partition("|")
        by_chain.setdefault(chain, []).append(p)
    for _, sess, ctx in await r.frames():
        try:
            got = await r.call_in(sess, ctx, STATE_FN)
        except Exception:
            continue
        chain = " >> ".join(got["chain"])
        if chain not in by_chain:
            continue
        try:
            for st in await r.call_in(sess, ctx, SETS_FN, [chain, by_chain[chain]]):
                out.append({**st, "chain": chain})
        except Exception:
            continue
    return out


def _chain(chain: str) -> list[str]:
    return [c for c in chain.split(" >> ") if c]


async def _open_to(
    ctx, stop, choose: list[tuple[str, str]] | None = None
) -> tuple[Session, dict[str, Any]]:
    """A fresh load with the trigger opened and, when `choose` (frame chain,
    path of each) is given, those options chosen in turn with Space. Returns the session (the
    caller closes it) and what was seen: `status` is set when nothing opened
    (not found, navigated, an error)."""
    s = await open_session(ctx.new_page, ctx.quiet_ms)
    info: dict[str, Any] = {}
    try:
        before = await _state(s)
        got = await _focus(s, stop.frame_chain, stop.css_path)
        if got is None:
            info["status"] = NOT_FOUND
            return s, info
        # Enter first, as the keyboard does it; a click when it showed
        # nothing (a control only a mouse operates), as 4.A's pointer check.
        eff = await observe(
            s, ctx.quiet_ms, lambda: s.page.keyboard.press("Enter"), None, noise_ms=0
        )
        by = "Enter"
        gone = {"navigation", "new_page", "frame_navigation"}
        after = await _state(s)
        if not (gone & set(eff.kinds)) and set(after) <= set(before) and not eff.any:
            eff = await observe(
                s,
                ctx.quiet_ms,
                lambda: s.page.mouse.click(got["x"], got["y"]),
                None,
                noise_ms=0,
            )
            by = "a click"
            after = await _state(s)
        if gone & set(eff.kinds):
            info["status"] = NAVIGATED
            return s, info
        new = sorted(set(after) - set(before))
        again = await _focus(s, stop.frame_chain, stop.css_path)
        info |= {
            "by": by,
            "before": before,
            "after": after,
            "new": new,
            "dialog": "dialog" in eff.kinds,
            "flipped": bool(again) and again.get("expanded") != got.get("expanded"),
        }
        if choose:
            done = 0
            for chain, css in choose:
                c = await _focus(s, _chain(chain), css)
                if c is None:
                    continue
                await s.page.keyboard.press(" ")
                await settle(s.page, ctx.quiet_ms)
                done += 1
            info["chosen"] = done
            info["after_choice"] = await _state(s)
        return s, info
    except Exception as exc:
        info["status"] = ERROR
        info["error"] = type(exc).__name__
        return s, info


def _counts(info: dict[str, Any]) -> tuple[int, int, int]:
    """New elements, new focusable ones, new fields among what opened."""
    after = info["after"]
    return (
        len(info["new"]),
        sum(1 for k in info["new"] if after[k][0]),
        sum(1 for k in info["new"] if after[k][1]),
    )


async def collect(ctx, walk) -> Reveal:
    """Open every trigger the walk found (up to MAX_TRIGGERS), each on a fresh
    load, and record what it showed. For 5.A-5.C each opened state is read
    with ANDI, and up to two options of each opened set are chosen."""
    trigs = triggers(walk)
    out = Reveal(over_cap=max(0, len(trigs) - MAX_TRIGGERS))
    read = labels.wanted(ctx)
    for n, (stop, why) in enumerate(trigs[:MAX_TRIGGERS], 1):
        rec = Opened(
            n=n,
            name=(stop.name or "")[:80],
            role=stop.role,
            tag=stop.tag,
            css_path=stop.css_path or "",
            frame_chain=list(stop.frame_chain),
            why=why,
        )
        out.triggers.append(rec)
        if ctx.out_of_time():
            rec.status, rec.reason = NOT_TRIED, WHY[NOT_TRIED]
            continue
        s = None
        try:
            s, info = await _open_to(ctx, stop)
            if "status" in info:
                rec.status = info["status"]
                rec.reason = WHY.get(rec.status, "")
                continue
            rec.by = info["by"]
            rec.new_elements, rec.new_focusable, rec.new_fields = _counts(info)
            rec.dialog = bool(info["dialog"])
            if not (info["new"] or info["dialog"] or info["flipped"]):
                rec.status, rec.reason = NOTHING, WHY[NOTHING]
                continue
            rec.status = OPENED
            sets = await _sets(s, info["new"]) if read else []
            try:
                shot = ctx.shots / f"reveal-{n}.png"
                ctx.shots.mkdir(parents=True, exist_ok=True)
                await screenshot(s.page, path=str(shot), animations="disabled")
                rec.picture = shot.resolve().relative_to(ctx.rel.resolve()).as_posix()
            except Exception:
                pass
            if read:
                # Last on this session: ANDI changes the page.
                rec.read = await labels.read_revealed(
                    ctx, s, f'press Enter on "{rec.name or "the control"}"'
                )
        except Exception as exc:
            rec.status, rec.reason = ERROR, f"{WHY[ERROR]} ({type(exc).__name__})"
            continue
        finally:
            if s is not None:
                await s.close()
        if not read or rec.status != OPENED:
            continue
        # Options: choosing one can add controls (Home's filter adds a remove
        # button for each choice), so each set is chosen from on its own fresh
        # load, two options together, and the page read once after.
        for st in sets[:MAX_SETS]:
            opts = [
                Option(
                    set_label=st.get("label", ""),
                    label=o["label"],
                    css_path=o["css"],
                )
                for o in st["options"][:MAX_OPTIONS]
            ]
            rec.options += opts
            if ctx.out_of_time():
                break
            s2 = None
            try:
                s2, info2 = await _open_to(
                    ctx, stop, [(st["chain"], o.css_path) for o in opts]
                )
                if "status" in info2 or not info2.get("chosen"):
                    continue
                gained = len(set(info2["after_choice"]) - set(info2["after"]))
                for o in opts:
                    o.chosen = True
                    o.new_elements = gained  # of the set's choices together
                read_ok = bool(
                    await labels.read_revealed(
                        ctx,
                        s2,
                        f'press Enter on "{rec.name or "the control"}", then '
                        "Space on " + " and ".join(f'"{o.label}"' for o in opts),
                    )
                )
                for o in opts:
                    o.read = read_ok
            except Exception:
                continue
            finally:
                if s2 is not None:
                    await s2.close()
    if out.over_cap:
        out.incomplete.append(
            f"The page has {len(trigs)} things that open; only the first "
            f"{MAX_TRIGGERS} were opened."
        )
    return out


def write(ctx, rv: Reveal, path) -> None:
    path.write_text(json.dumps(rv.model_dump(mode="json"), indent=1))
