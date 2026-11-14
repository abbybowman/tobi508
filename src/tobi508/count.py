"""The page's inventory: what exists on it, whether or not a test reads it
(plan 2026-11-12 part B; review items D-01, H-08, M-02, K-02, N-01, N-06).

One script per frame counts form fields, hidden fields, editable areas, forms
with a button, media, canvases, draggable items, images, focusable elements,
landmarks and links, inside open shadow roots too, and keeps the page's own
document, the shadow roots and the frames apart (`models.Part`). The play
hook (`PLAY_HOOK_JS`, in every replay context before page scripts) keeps the
media elements that played, attached to a document or not.

Facts only. Guard CN (`engine.apply_guards`) compares this with what each
test says it read, by the keys its spec lists (front matter `count:`).
"""

from __future__ import annotations

import re
from typing import Any

from playwright.async_api import Page

from tobi508.models import Count, Part
from tobi508.jslib import JSLIB, PATH_JS

PATHS_MAX = 200

# Frames whose host is a video player (2.A and 3.A's patterns, without the
# autoplay condition): the page's own scripts cannot read inside them.
PLAYER_RE = re.compile(
    r"^https?://(www\.)?(youtube(-nocookie)?\.com/embed|player\.vimeo\.com|"
    r"players\.brightcove\.net|cdnapisec\.kaltura\.com|content\.jwplatform\.com)/"
)

# Before page scripts, every frame: keep each media element that played or
# was asked to play, and count speech. `play()` catches script calls
# (`new Audio(u).play()` is never in a document); the `play` event catches
# `autoplay`, which calls no method. Media events do not cross a shadow
# boundary, so each new shadow root gets the listener too. Defined
# non-writable so the page cannot replace it.
PLAY_HOOK_JS = """(() => {
  if (window.__tobiPlayed) return;
  const played = [];
  const seen = new WeakSet();
  let speech = 0;
  let audio = 0;
  const note = (el) => { if (el && !seen.has(el)) { seen.add(el); played.push(el); } };
  const onplay = (e) => { if (e.target instanceof HTMLMediaElement) note(e.target); };
  try {
    const op = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function (...a) { note(this); return op.apply(this, a); };
    document.addEventListener('play', onplay, true);
    const oa = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function (...a) {
      const r = oa.apply(this, a);
      try { r.addEventListener('play', onplay, true); } catch (e) {}
      return r;
    };
    if (window.speechSynthesis) {
      const os = window.speechSynthesis.speak.bind(window.speechSynthesis);
      window.speechSynthesis.speak = (u) => { speech += 1; return os(u); };
    }
    if (window.AudioScheduledSourceNode) {
      const st = AudioScheduledSourceNode.prototype.start;
      AudioScheduledSourceNode.prototype.start = function (...a) { audio += 1; return st.apply(this, a); };
    }
  } catch (e) {}
  Object.defineProperty(window, '__tobiPlayed', {
    value: Object.freeze({ list: () => played.slice(), speech: () => speech, audio: () => audio }),
    writable: false, configurable: false });
})();"""

# One frame's document and its open shadow roots. `light` is the document
# itself, `shadow` everything inside a shadow root at any depth.
COUNT_JS = (
    "(pathsMax) => {"
    + JSLIB
    + PATH_JS
    + """
  const { FIELD, inert, rendered, focusable, off } = J;
  const LANDMARK = 'header, nav, main, footer, aside, [role=banner], [role=navigation], [role=main], ' +
    '[role=contentinfo], [role=complementary], [role=search], [role=region], [role=form]';
  // What could show hidden content: a button, a disclosure, a same-page or
  // script link, an element with an inline click handler (Abby, 2026-11-12:
  // hidden fields with nothing that can open them do not hold an outcome).
  const OPENER = 'button, [role=button], input[type=button], summary, a[href^="#"], ' +
    'a[href^="javascript:" i], [onclick], [aria-expanded], [aria-controls]';
  const BUTTON = 'button, input[type=submit], input[type=button], input[type=image], [role=button]';
  const part = () => ({ light: 0, shadow: 0 });
  const out = { fields: part(), fields_hidden: part(), contenteditable: part(), forms_with_button: part(),
    media: part(), canvases: part(), draggable: part(), images: part(), focusable: part(),
    landmarks: part(), links: part(), shadow_roots: 0, closed_hosts: 0, openers: 0,
    hidden_field_paths: [], form_paths: [], played: { light: 0, shadow: 0, detached: 0 },
    speech: 0, audio: 0 };
  const radios = { light: new Set(), shadow: new Set() };
  const imgs = { light: new Set(), shadow: new Set() };
  const walk = (root, where) => {
    for (const el of root.querySelectorAll('*')) {
      const add = (k) => { out[k][where] += 1; };
      if (el.matches(FIELD) && !off(el)) {
        if (rendered(el)) {
          if (el.matches('input[type=radio]') && el.name) {
            const k = (el.form ? 'f' : '') + el.name;
            if (!radios[where].has(k)) { radios[where].add(k); add('fields'); }
          } else add('fields');
        } else {
          add('fields_hidden');
          if (where === 'light' && out.hidden_field_paths.length < pathsMax) out.hidden_field_paths.push(path(el));
        }
      }
      if (el.isContentEditable && !(el.parentElement && el.parentElement.isContentEditable) && rendered(el)) add('contenteditable');
      if (el.tagName === 'FORM' && el.querySelector(BUTTON)) {
        add('forms_with_button');
        if (where === 'light' && out.form_paths.length < pathsMax) out.form_paths.push(path(el));
      }
      if (el.matches(OPENER) && rendered(el) && !el.matches(':disabled')) out.openers += 1;
      if (el.tagName === 'VIDEO' || el.tagName === 'AUDIO') add('media');
      if (el.tagName === 'CANVAS') {
        const r = el.getBoundingClientRect();
        if (r.width >= 50 && r.height >= 50) add('canvases');
      }
      if (el.getAttribute('draggable') === 'true') add('draggable');
      if (el.tagName === 'IMG') {
        const u = (el.currentSrc || '').split('#')[0];
        if (/^https?:/.test(u) && imgs[where].size < 1000) imgs[where].add(u);
      }
      if (focusable(el)) add('focusable');
      if (el.matches(LANDMARK)) add('landmarks');
      if (el.matches('a[href], area[href]')) add('links');
      if (el.shadowRoot) { out.shadow_roots += 1; walk(el.shadowRoot, 'shadow'); }
      else if (el.tagName.includes('-') && window.customElements && customElements.get(el.tagName.toLowerCase())) out.closed_hosts += 1;
    }
  };
  walk(document, 'light');
  out.image_srcs = { light: Array.from(imgs.light), shadow: Array.from(imgs.shadow) };
  const hook = window.__tobiPlayed;
  if (hook) {
    for (const el of hook.list()) {
      const root = el.isConnected ? el.getRootNode() : null;
      out.played[root === document ? 'light' : root ? 'shadow' : 'detached'] += 1;
    }
    out.speech = hook.speech();
    out.audio = hook.audio();
  }
  return out;
}"""
)

_PARTS = (
    "fields",
    "fields_hidden",
    "contenteditable",
    "forms_with_button",
    "media",
    "canvases",
    "draggable",
    "focusable",
    "landmarks",
    "links",
)


def _merge_images(count: Count, got: dict[str, Any], main: bool, seen: set) -> None:
    """Distinct image addresses (`http(s)` only, as pass T's image read takes
    them), each counted once across the page's documents."""
    for where in ("light", "shadow"):
        fresh = [u for u in got["image_srcs"][where] if u not in seen]
        seen.update(fresh)
        part = where if main else "frames"
        setattr(count.images, part, getattr(count.images, part) + len(fresh))


def _merge(count: Count, got: dict[str, Any], main: bool) -> None:
    for k in _PARTS:
        p: Part = getattr(count, k)
        if main:
            p.light += got[k]["light"]
            p.shadow += got[k]["shadow"]
        else:
            p.frames += got[k]["light"] + got[k]["shadow"]
    pl = got["played"]
    mp = count.media_played
    if main:
        mp.light += pl["light"]
        mp.shadow += pl["shadow"]
        mp.detached += pl["detached"] + got["audio"] + got["speech"]
        count.hidden_field_paths = got["hidden_field_paths"]
        count.form_paths = got["form_paths"]
    else:
        mp.frames += (
            pl["light"] + pl["shadow"] + pl["detached"] + got["audio"] + got["speech"]
        )
    count.speech += got["speech"]
    count.shadow_roots += got["shadow_roots"]
    count.openers += got["openers"]
    count.closed_hosts += got["closed_hosts"]


async def take(page: Page, where: str) -> Count:
    """The inventory of a loaded, settled page, every frame read. A frame
    whose script cannot run is counted in `frames_unread`; when the page's
    own document cannot be read, `error` says so (guard CN then holds a PASS
    or DOES NOT APPLY)."""
    count = Count(where=where, played_from=where)
    images: set[str] = set()
    for frame in [page.main_frame, *(f for f in page.frames if f != page.main_frame)]:
        main = frame == page.main_frame
        if not main:
            count.frames += 1
            if PLAYER_RE.match(frame.url or ""):
                count.players += 1
        try:
            got = await frame.evaluate(COUNT_JS, PATHS_MAX)
        except Exception as exc:
            if main:
                count.error = type(exc).__name__
                return count
            count.frames_unread += 1
            continue
        _merge(count, got, main)
        _merge_images(count, got, main, images)
    return count


# What played on this load, in one frame; `listed`: those pass T's media read
# (`motion.M.media`: the document's first 20 `video`/`audio`) also lists.
# Speech and Web Audio sources count as played from a script.
PLAYED_JS = """() => {
  const hook = window.__tobiPlayed;
  if (!hook) return null;
  const out = { light: 0, shadow: 0, detached: 0, listed: 0 };
  const listed = new Set(Array.from(document.querySelectorAll('video, audio')).slice(0, 20));
  for (const el of hook.list()) {
    const root = el.isConnected ? el.getRootNode() : null;
    out[root === document ? 'light' : root ? 'shadow' : 'detached'] += 1;
    if (listed.has(el)) out.listed += 1;
  }
  out.detached += hook.audio() + hook.speech();
  return out;
}"""


async def played(page: Page) -> tuple[Part, Part] | None:
    """Media that played on this load, every frame (pass T's load, where
    autoplay is allowed), and those of them pass T's media read lists, by
    the same parts. None when the page's own document cannot be read."""
    part, listed = Part(), Part()
    for frame in page.frames:
        main = frame == page.main_frame
        try:
            got = await frame.evaluate(PLAYED_JS)
        except Exception:
            if main:
                return None
            continue
        if got is None:
            continue
        if main:
            part.light += got["light"]
            part.shadow += got["shadow"]
            part.detached += got["detached"]
            listed.light += got["listed"]
        else:
            part.frames += got["light"] + got["shadow"] + got["detached"]
            listed.frames += got["listed"]
    return part, listed


class CountHook:
    """A walk extra the pipeline adds for P1: takes the inventory once the
    first load has settled (`Traversal.start` runs `on_start` after the
    settle rule; C-09), so no extra load is made. A confirming second P1
    does not count again."""

    name = "count"

    def __init__(self, sink: dict[str, Any], active: bool) -> None:
        self.sink, self.active = sink, active

    async def on_start(self, t: Any) -> None:
        if self.active and "count" not in self.sink:
            self.sink["count"] = await take(t.page, "walk")

    async def on_step(self, t: Any, step: Any) -> None:
        return None


def walk_extra(sink: dict[str, Any]):
    """The factory `walk.walk_page` takes (`ExtraFactory`)."""
    return lambda name, _p1: CountHook(sink, name == "P1")
