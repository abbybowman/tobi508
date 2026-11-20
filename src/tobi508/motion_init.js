
  if (window.__a11yMotion) return;
  const now = () => performance.timeOrigin + performance.now();
  const M = { recs: [], attrs: 0, dropped: 0, timers: [], audio: 0, snaps: [], live0: new WeakSet(), held: new Map(), focus: [], ctxs: new Set(), io: [], t0: null };
  Object.defineProperty(window, '__a11yMotion', { value: M });
  const REC_MAX = 1500, ATTR_MAX = 300, TIMER_MAX = 200;
  const LIVE = LIVE_SELECTOR;
  const CAROUSEL = CAROUSEL_SELECTOR;
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const isLive = (e) => {
    if (!e.matches(LIVE)) return false;
    if (!e.hasAttribute('aria-live')) return true;
    const v = norm(e.getAttribute('aria-live')).toLowerCase();
    return v === 'polite' || v === 'assertive';
  };
  const liveOf = (el) => { for (let e = el; e; e = e.parentElement) if (isLive(e)) return e; return null; };
  // 3.A's triggers (3.A spec section 2): callbacks of timers under 334 ms
  // and of requestAnimationFrame that change the page or draw on a canvas,
  // by time. A second observer's takeRecords() sees a callback's own DOM
  // changes synchronously, without taking them from the observer below.
  M.fast = []; M.draws = 0;
  const FAST_MS = 334, FAST_MAX = 600;
  const fx = new MutationObserver(() => {});
  fx.observe(document, { subtree: true, childList: true, attributes: true, characterData: true });
  const drawHook = (C, names) => {
    if (!C) return;
    for (const k of names) {
      const o = C.prototype[k];
      if (typeof o === 'function') C.prototype[k] = function (...a) { M.draws++; return o.apply(this, a); };
    }
  };
  const D2 = ['fillRect', 'clearRect', 'strokeRect', 'fill', 'stroke', 'drawImage', 'putImageData', 'fillText', 'strokeText'];
  drawHook(window.CanvasRenderingContext2D, D2);
  drawHook(window.OffscreenCanvasRenderingContext2D, D2);
  drawHook(window.WebGLRenderingContext, ['drawArrays', 'drawElements', 'clear']);
  drawHook(window.WebGL2RenderingContext, ['drawArrays', 'drawElements', 'clear']);
  const fast = (f, kind) => function (...a) {
    const d0 = M.draws;
    try { return f.apply(this, a); } finally {
      try { if ((fx.takeRecords().length || M.draws !== d0) && M.fast.length < FAST_MAX) M.fast.push({ at: now(), kind }); } catch (e) {}
    }
  };
  const raf = window.requestAnimationFrame;
  if (raf) window.requestAnimationFrame = function (f, ...a) { return raf.call(this, typeof f === 'function' ? fast(f, 'raf') : f, ...a); };
  // Timers (2.C A2: a period longer than the watch, item 7).
  const si = window.setInterval, st = window.setTimeout;
  window.setInterval = function (f, ms, ...a) {
    const v = Number(ms) || 0;
    if (v >= 1000 && M.timers.length < TIMER_MAX) M.timers.push({ kind: 'interval', ms: Math.round(v), at: now() });
    if (typeof f === 'function' && v < FAST_MS) f = fast(f, 'interval');
    return si.call(this, f, ms, ...a);
  };
  window.setTimeout = function (f, ms, ...a) {
    const v = Number(ms) || 0;
    if (v >= 1000 && M.timers.length < TIMER_MAX) M.timers.push({ kind: 'timeout', ms: Math.round(v), at: now() });
    if (typeof f === 'function' && v < FAST_MS) f = fast(f, 'timeout');
    return st.call(this, f, ms, ...a);
  };
  // What the page waits to see scrolled into view (Understanding 2.2.2:
  // starting when scrolled into view counts as starting by itself).
  if (window.IntersectionObserver) {
    const io = IntersectionObserver.prototype.observe;
    IntersectionObserver.prototype.observe = function (t) {
      try { if (t && t.nodeType === 1 && M.io.length < 50) M.io.push(t); } catch (e) {}
      return io.apply(this, arguments);
    };
  }
  // Web Audio connected to the speakers (2.A, item 5).
  if (window.AudioNode) {
    const cn = AudioNode.prototype.connect;
    AudioNode.prototype.connect = function (d, ...a) {
      try { if (window.AudioDestinationNode && d instanceof AudioDestinationNode) { M.audio++; M.ctxs.add(d.context); } } catch (e) {}
      return cn.call(this, d, ...a);
    };
  }
  // DOM changes with their targets (2.D: the change, and the live region
  // around it at the time). The <head> is skipped: the tool's screenshots
  // add and remove a style element there.
  const textOf = (el) => norm(el && (el.innerText !== undefined ? el.innerText : el.textContent)).slice(0, 200);
  const meaningful = (nodes) => Array.from(nodes).some((n) => n.nodeType === 1 || (n.nodeType === 3 && norm(n.textContent)));
  const obs = new MutationObserver((rs) => {
    const at = now();
    for (const r of rs) {
      const el = r.target.nodeType === 1 ? r.target : r.target.parentElement;
      if (!el || (el.closest && el.closest('head'))) continue;
      let kind;
      if (r.type === 'characterData') kind = 'text';
      else if (r.type === 'childList') { if (!meaningful(r.addedNodes) && !meaningful(r.removedNodes)) continue; kind = 'children'; }
      else kind = ['src', 'srcset', 'poster'].includes(r.attributeName) ? 'src' : 'attr';
      if (kind === 'attr') { if (M.attrs >= ATTR_MAX) { M.dropped++; continue; } M.attrs++; }
      if (M.recs.length >= REC_MAX) { M.dropped++; continue; }
      M.recs.push({ at, kind, attr: r.attributeName || null, el, live: liveOf(el),
        before: r.type === 'characterData' ? norm(r.oldValue).slice(0, 200) : '',
        after: kind === 'text' || kind === 'children' ? textOf(el) : '' });
    }
  });
  const OBS = { subtree: true, childList: true, attributes: true, characterData: true, characterDataOldValue: true };
  obs.observe(document, OBS);
  // Changes inside web components too (part D; the cause of review D-04):
  // each open shadow root as it is attached, and those already in the page
  // when the watch starts (a server-rendered root attaches none).
  const watched = new WeakSet();
  const watchRoot = (r) => {
    if (!r || watched.has(r)) return;
    watched.add(r);
    try { obs.observe(r, OBS); fx.observe(r, { subtree: true, childList: true, attributes: true, characterData: true }); } catch (e) {}
  };
  const oas = Element.prototype.attachShadow;
  Element.prototype.attachShadow = function (...a) {
    const r = oas.apply(this, a);
    if (a[0] && a[0].mode === 'open') watchRoot(r);
    return r;
  };
  M.watchRoots = () => { for (const r of J.roots()) if (r !== document) watchRoot(r); };
  // Focus moves with no key pressed (2.D N4), as element references.
  addEventListener('focusin', (e) => { if (M.focus.length < 100) M.focus.push({ at: now(), el: e.composedPath()[0] }); }, true);
  // Pass T's start: live regions present and rendered now (2.D: a region
  // added with the change does not count).
  M.mark0 = () => {
    M.t0 = now();
    M.watchRoots();
    const vis = (e) => e.checkVisibility ? e.checkVisibility({ visibilityProperty: true }) : e.getClientRects().length > 0;
    const out = [];
    for (const e of J.all(LIVE)) {
      if (!isLive(e) || !vis(e)) continue;
      M.live0.add(e);
      out.push({ css: path(e), role: e.getAttribute('role') || '', live: norm(e.getAttribute('aria-live')) });
    }
    const car = J.all(CAROUSEL).slice(0, 10).map((e) => path(e));
    return { t0: M.t0, live: out, carousels: car };
  };
  // What each element shows (2.C Terms, kind): a hash of its visible text,
  // image sources and rendered children, and its box. Text clipped away by
  // an overflow ancestor (a sliding carousel's other slides) is not shown.
  const H = (h, s) => { for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619) >>> 0; return h; };
  M.snap = () => {
    const map = new WeakMap();
    const visit = (el, clip, faded) => {
      let cs;
      try { cs = getComputedStyle(el); } catch (e) { return 0; }
      if (cs.display === 'none') return 0;
      const r = el.getBoundingClientRect();
      const fade = faded || parseFloat(cs.opacity) === 0;
      let c = clip;
      if (cs.display !== 'contents' && (cs.overflowX !== 'visible' || cs.overflowY !== 'visible'))
        c = [Math.max(clip[0], r.left), Math.max(clip[1], r.top), Math.min(clip[2], r.right), Math.min(clip[3], r.bottom)];
      const inClip = r.width > 0 && r.height > 0 && r.right > clip[0] && r.left < clip[2] && r.bottom > clip[1] && r.top < clip[3];
      const self = !fade && cs.visibility !== 'hidden' && (inClip || cs.display === 'contents');
      let h = 2166136261, n = 0;
      // What it looks like apart from its content (2.B: a colour-only
      // change is blinking) and how it is placed (a spinner rotates).
      let ch = 2166136261, th = 2166136261;
      if (self) {
        ch = H(ch, [cs.color, cs.backgroundColor, cs.borderTopColor, cs.fill, cs.stroke, cs.opacity, cs.visibility].join('|'));
      }
      th = H(th, cs.transform + '|' + cs.translate + '|' + cs.rotate + '|' + cs.scale);
      if (self) {
        for (const t of el.childNodes) if (t.nodeType === 3) { const s = norm(t.textContent); if (s) { h = H(h, s); n++; } }
        if (el.tagName === 'IMG') { h = H(h, 'img:' + (el.currentSrc || el.src || '')); n++; }
        if (cs.backgroundImage && cs.backgroundImage !== 'none') { h = H(h, 'bg:' + cs.backgroundImage); n++; }
        if ((el.tagName === 'INPUT' && el.type !== 'hidden') || el.tagName === 'TEXTAREA') { h = H(h, 'v:' + el.value); n++; }
      }
      const kids = el.shadowRoot ? [...el.shadowRoot.children, ...el.children] : el.children;
      for (const k of kids) {
        const hk = visit(k, c, fade);
        if (hk) { h = H(h, String(hk)); n++; }
        const v = map.get(k);
        if (v) { ch = H(ch, String(v[5])); th = H(th, String(v[6])); }
      }
      const out = n ? h >>> 0 : 0;
      map.set(el, [out, Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height), ch >>> 0, th >>> 0]);
      return out;
    };
    const t = now();
    if (document.body) visit(document.body, [-1e9, -1e9, 1e9, 1e9], false);
    M.snaps.push({ at: t, map });
    return t;
  };
  // Regions for a group of changed tiles (2.C Terms, region). `boxes` are
  // the changed pixels' bounding boxes, one per tile, in viewport pixels.
  // The group goes to the smallest element whose box covers it, by overlap
  // (not by tile centres, which missed edge tiles; item 6). When its
  // changed pixels fall in two or more of that element's children, one in
  // each, each child's part is its own region (two widgets side by side).
  // Inside a carousel, the region is the whole carousel. An iframe hands its
  // part to its own frame.
  const ov = (r, b) => Math.max(0, Math.min(r.right, b[2]) - Math.max(r.left, b[0])) * Math.max(0, Math.min(r.bottom, b[3]) - Math.max(r.top, b[1]));
  // 4 px of slack: a focus ring is drawn just outside its element.
  const covers = (r, b) => r.left <= b[0] + 4 && r.top <= b[1] + 4 && r.right >= b[2] - 4 && r.bottom >= b[3] - 4;
  // Covering now and at the first read: content that moved there (the slide
  // in view at the end of a sliding carousel) does not cover it.
  const steady = (e, b) => {
    if (!covers(e.getBoundingClientRect(), b)) return false;
    const v = M.snaps.length ? M.snaps[0].map.get(e) : null;
    return !v || covers({ left: v[1], top: v[2], right: v[1] + v[3], bottom: v[2] + v[4] }, b);
  };
  const bboxOf = (bs) => [Math.min(...bs.map((b) => b[0])), Math.min(...bs.map((b) => b[1])), Math.max(...bs.map((b) => b[2])), Math.max(...bs.map((b) => b[3]))];
  const rendered = (e) => { try { return getComputedStyle(e).display !== 'none'; } catch (x) { return false; } };
  const cover = (bs) => {
    const bx = bboxOf(bs), seen = new Set();
    const step = Math.max(1, Math.floor(bs.length / 24));
    for (let i = 0; i < bs.length; i += step) {
      const b = bs[i];
      for (const e of document.elementsFromPoint((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)) seen.add(e);
    }
    let best = null, area = Infinity, over = null, most = 0, overArea = Infinity;
    for (const e of seen) {
      const r = e.getBoundingClientRect(), a = r.width * r.height;
      if (steady(e, bx)) { if (a < area) { area = a; best = e; } }
      else { const o = ov(r, bx); if (o > most || (o === most && a < overArea)) { most = o; over = e; overArea = a; } }
    }
    return { el: best || over || document.body, covered: !!best };
  };
  const split = (el, idx, bs, depth) => {
    if (depth > 12 || idx.length < 2 || el.tagName === 'IFRAME' || el.tagName === 'FRAME') return [[el, idx]];
    const kids = (el.shadowRoot ? [...el.shadowRoot.children, ...el.children] : Array.from(el.children))
      .filter(rendered).map((c) => [c, c.getBoundingClientRect()]);
    const parts = new Map();
    for (const i of idx) {
      const hit = kids.filter(([, r]) => ov(r, bs[i]) > 0);
      if (hit.length !== 1) return [[el, idx]];
      const c = hit[0][0];
      if (!parts.has(c)) parts.set(c, []);
      parts.get(c).push(i);
    }
    if (parts.size < 2) return [[el, idx]];
    const out = [];
    for (const [c, sub] of parts) {
      // The smallest descendant of c covering its part.
      let e = c;
      const bx = bboxOf(sub.map((i) => bs[i]));
      for (let k = 0; k < 30; k++) {
        const next = Array.from(e.children).filter(rendered).find((d) => steady(d, bx));
        if (!next) break;
        e = next;
      }
      out.push(...split(e, sub, bs, depth + 1));
    }
    return out;
  };
  M.regionsAt = (bs) => {
    if (!bs.length) return [];
    const all = bs.map((_, i) => i);
    let { el: top, covered } = cover(bs);
    // A running animation's target whose box, grown by half its size (a
    // rotated square reaches about 0.21 of its side past its box), covers the
    // changed pixels is the region: a spinning badge, not the <main> around
    // it, whose other content never changed.
    const bx = bboxOf(bs);
    let best = null, area = Infinity;
    for (const a of document.getAnimations()) {
      const t = a.effect && a.effect.target;
      if (!t || t.nodeType !== 1 || a.playState !== 'running' || !(top === t || top.contains(t))) continue;
      const r = t.getBoundingClientRect(), g = Math.max(r.width, r.height) / 2;
      const grown = { left: r.left - g, top: r.top - g, right: r.right + g, bottom: r.bottom + g };
      if (covers(grown, bx) && r.width * r.height < area) { best = t; area = r.width * r.height; }
    }
    if (best) { top = best; covered = true; }
    const frames = Array.from(document.querySelectorAll('iframe, frame'));
    return split(top, all, bs, 0).map(([el0, idx]) => {
      if (el0.tagName === 'IFRAME' || el0.tagName === 'FRAME') {
        const r = el0.getBoundingClientRect();
        return { frame: frames.indexOf(el0), dx: r.left + el0.clientLeft, dy: r.top + el0.clientTop, idx };
      }
      const car = el0.closest(CAROUSEL);
      let el = car || el0;
      // An element that was not on the page at the first read (replaced
      // with innerHTML every second): its region is the ancestor that was.
      const first = M.snaps.length ? M.snaps[0].map : null;
      while (first && !first.has(el) && el.parentElement && el !== document.body) el = el.parentElement;
      const css = path(el);
      M.held.set(css, el);
      const r = el.getBoundingClientRect();
      return { css, tag: el.tagName.toLowerCase(), part: el !== el0 ? path(el0) : null, carousel: !!car, covered, idx,
        box: [Math.round(r.left + scrollX), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height)] };
    });
  };
  // A region at the end of the watch: what it showed at each read, whether
  // its children moved, its DOM changes and their live regions.
  M.describe = (css) => {
    const el = M.held.get(css);
    if (!el) return null;
    const sigs = M.snaps.map((s) => { const v = s.map.get(el); return v ? v[0] : null; });
    const colors = M.snaps.map((s) => { const v = s.map.get(el); return v ? v[5] : null; });
    const transforms = M.snaps.map((s) => { const v = s.map.get(el); return v ? v[6] : null; });
    let moved = false;
    // Any descendant (capped), not only children: a sliding carousel's track
    // sits inside a clipping box. More than 20 px against the region: a
    // ticker gaining a digit nudges the inline text after it, which is not
    // motion.
    const kids = Array.from(el.querySelectorAll('*')).slice(0, 400);
    for (let i = 1; i < M.snaps.length && !moved; i++) {
      const a = M.snaps[i - 1].map, b = M.snaps[i].map, pa = a.get(el), pb = b.get(el);
      if (!pa || !pb) continue;
      for (const k of kids) {
        const ka = a.get(k), kb = b.get(k);
        if (ka && kb && ka[0] && (Math.abs((ka[1] - pa[1]) - (kb[1] - pb[1])) > 20 || Math.abs((ka[2] - pa[2]) - (kb[2] - pb[2])) > 20)) { moved = true; break; }
      }
    }
    const rec = (r) => ({ at: r.at, kind: r.kind, attr: r.attr, css: r.el.isConnected ? path(r.el) : '', before: r.before, after: r.after,
        live: r.live ? (r.live.isConnected ? path(r.live) : '') : null, live_at_start: !!(r.live && M.live0.has(r.live)) });
    const mine = M.recs.filter((r) => r.at >= M.t0 && (el === r.el || el.contains(r.el)));
    const changes = mine.filter((r) => r.kind !== 'attr').slice(0, 100).map(rec);
    // 2.D's note: inside or holding aria-live="off" (W3C's carousel pattern
    // turns announcements off while it rotates).
    const liveOff = !!(el.closest('[aria-live="off" i]') || el.querySelector('[aria-live="off" i]'));
    // Class and style changes (slides shown by a class or slid by transform): 2.D's changes when
    // a region shows new content with no text change.
    // Style changes too: a carousel that slides with transform has nothing else.
    const attrList = mine.filter((r) => r.kind === 'attr').slice(0, 30).map(rec);
    const attrs = mine.filter((r) => r.kind === 'attr').length;
    const focusIn = M.focus.filter((f) => f.at >= M.t0 && (el === f.el || el.contains(f.el))).map((f) => f.at);
    let anims = [];
    try {
      anims = el.getAnimations({ subtree: true }).slice(0, 20).map((a) => {
        const t = a.effect ? a.effect.getComputedTiming() : {};
        const target = a.effect && a.effect.target;
        return { css: target && target.nodeType === 1 ? path(target) : '', name: a.animationName || a.transitionProperty || a.id || '',
          infinite: t.iterations === Infinity, iterations: t.iterations === Infinity ? 0 : (t.iterations || 0),
          duration_ms: typeof t.duration === 'number' ? Math.round(t.duration) : 0, state: a.playState };
      });
    } catch (e) {}
    return { live_off: liveOff, sigs, colors, transforms, moved, changes, attr_list: attrList, attrs, focus_in: focusIn, anims, text: textOf(el), connected: el.isConnected };
  };
  // Inside web components too (part D; review N-01): J.all.
  M.media = () => J.all('video, audio').slice(0, 20).map((m) => ({
    css: path(m), tag: m.tagName.toLowerCase(), shadow: J.where(m) === 'shadow', paused: m.paused, muted: m.muted, volume: m.volume,
    time: m.currentTime, duration: isFinite(m.duration) ? m.duration : null, loop: m.loop, autoplay: m.autoplay,
    controls: m.controls, error: m.error ? m.error.code : null,
    decoded: typeof m.webkitAudioDecodedByteCount === 'number' ? m.webkitAudioDecodedByteCount : null,
    src: (m.currentSrc || '').slice(0, 500),
    // Every address the element could play (its src and its <source> children),
    // for 3.A, which reads a video that never played from its file.
    urls: [m.getAttribute('src') ? m.src : '', ...Array.from(m.querySelectorAll('source')).map((x) => x.src)]
      .filter((u) => /^https?:/.test(u || '')).map((u) => u.slice(0, 500)).slice(0, 6),
    total: J.all('video, audio').length }));
  // <blink> and text-decoration: blink do not blink in Chrome (plan item 9):
  // a note for 2.B only.
  const blinkMarkup = () => {
    if (document.querySelector('blink')) return true;
    const all = document.querySelectorAll('body *');
    for (let i = 0; i < all.length && i < 3000; i++) {
      if ((getComputedStyle(all[i]).textDecorationLine || '').includes('blink')) return true;
    }
    return false;
  };
  // 3.A's trigger: running animations whose colour, background (a pattern
  // shifted by its position), opacity, visibility or filter changes more
  // than 3 times a second (keyframe changes, each
  // steps(n) easing counting n, per iteration).
  const FLASHY = /^(color|background(Color|Image|Position|PositionX|PositionY|Size)?|opacity|visibility|filter|fill|stroke|border(Top|Right|Bottom|Left)?Color|outlineColor|boxShadow|textShadow)$/;
  M.fastAnims = () => {
    const out = [];
    for (const a of document.getAnimations()) {
      if (out.length >= 20) break;
      try {
        if (a.playState !== 'running' || !a.effect || !a.effect.getKeyframes) continue;
        const t = a.effect.getComputedTiming();
        const dur = typeof t.duration === 'number' ? t.duration : 0;
        if (!(dur > 0)) continue;
        const kf = a.effect.getKeyframes();
        const look = (k) => Object.keys(k).filter((p) => FLASHY.test(p)).map((p) => p + ':' + k[p]).sort().join('|');
        let changes = 0;
        for (let i = 1; i < kf.length; i++) {
          if (look(kf[i]) === look(kf[i - 1])) continue;
          const m = /steps\((\d+)/.exec(kf[i - 1].easing || '');
          changes += m ? Number(m[1]) : 1;
        }
        if (kf.length > 1 && look(kf[kf.length - 1]) !== look(kf[0]) && !String(t.direction || '').includes('alternate')) changes++;
        const perS = changes * 1000 / dur * Math.abs(a.playbackRate || 1);
        if (perS <= 3) continue;
        const tg = a.effect.target;
        out.push({ css: tg && tg.nodeType === 1 ? path(tg) : '', name: a.animationName || a.transitionProperty || a.id || '',
          per_s: Math.round(perS * 100) / 100, duration_ms: Math.round(dur) });
      } catch (e) {}
    }
    return out;
  };
  M.facts = () => ({ timers: M.timers, audio: M.audio, dropped: M.dropped, blink: blinkMarkup(),
    fast: M.fast.map((f) => ({ at: f.at, kind: f.kind })), fast_anims: M.fastAnims(),
    // Web Audio contexts playing to the speakers (2.A), and the iframes'
    // sources (2.A: a YouTube or Vimeo player cannot be measured).
    audio_states: Array.from(M.ctxs).map((c) => c.state),
    iframes: Array.from(document.querySelectorAll('iframe')).map((f) => (f.src || '').slice(0, 500)).slice(0, 30) });
  // Motion the frames may not show (below the first screen): animations
  // running with more than 5 s of active time, marquees, playing videos,
  // that are not inside a region already found (2.B Terms).
  // Hints below the first screen (2.C spec section 2, scrolled watch; plan
  // Q3): what the page observes for scrolling into view, and carousels,
  // that lie below the first viewport and are not inside a region found.
  M.below = (known) => {
    const inside = (e) => known.some((css) => { const r = M.held.get(css); return r && (r === e || r.contains(e)); });
    const out = [];
    const cand = [...M.io, ...J.all(CAROUSEL)];
    for (const e of cand) {
      if (!e.isConnected || inside(e)) continue;
      const r = e.getBoundingClientRect();
      if (r.top + scrollY < innerHeight || r.width === 0 || r.height === 0) continue;
      const css = path(e);
      if (!out.includes(css)) out.push(css);
    }
    return out.slice(0, 10);
  };
  M.images = () => Array.from(new Set(Array.from(document.images)
    .map((i) => (i.currentSrc || '').split('#')[0]).filter((u) => /^https?:/.test(u)))).slice(0, 1000);
  M.extras = (known, longImages) => {
    const inside = (e) => known.some((css) => { const r = M.held.get(css); return r && (r === e || r.contains(e)); });
    const out = [];
    const add = (e, source, detail) => {
      if (!e || e.nodeType !== 1 || inside(e) || out.length >= 10) return;
      const css = path(e);
      if (out.some((o) => o.css === css)) return;
      M.held.set(css, e);
      known.push(css);
      const r = e.getBoundingClientRect();
      out.push({ css, tag: e.tagName.toLowerCase(), source, detail,
        box: [Math.round(r.left + scrollX), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height)] });
    };
    for (const a of document.getAnimations()) {
      if (a.playState !== 'running' || !a.effect) continue;
      const t = a.effect.getComputedTiming();
      const active = t.iterations === Infinity ? Infinity : (t.iterations || 0) * (typeof t.duration === 'number' ? t.duration : 0);
      if (active > 5000) add(a.effect.target, 'animation', (a.animationName || a.transitionProperty || '') + (active === Infinity ? ' (infinite)' : ' ' + Math.round(active) + ' ms'));
    }
    for (const m of J.all('marquee')) add(m, 'marquee', 'marquee');
    // Animated images over 5 s in all, by G152 (frames x delays x loops,
    // decoded from the recording in the tool page), wherever they are.
    for (const i of document.images) {
      const d = (longImages || {})[(i.currentSrc || '').split('#')[0]];
      if (d) add(i, 'image', d);
    }
    // Content the DOM log saw keep changing where no frame showed it (below
    // the first screen): three or more text or child changes, the last at
    // 5 s or later.
    // Only changes that change its text: a poll that writes the same value
    // again (a replay answers every poll alike) is not an update.
    const byEl = new Map();
    for (const r of M.recs) {
      if (r.kind === 'attr' || r.at < M.t0 || !r.el || !r.el.isConnected) continue;
      const v = byEl.get(r.el) || { n: 0, last: 0, text: null };
      if (r.after !== v.text) {
        if (v.text !== null) { v.n++; v.last = Math.max(v.last, r.at); }
        v.text = r.after;
      }
      byEl.set(r.el, v);
    }
    for (const [e, v] of byEl) {
      if (v.n >= 3 && v.last - M.t0 >= 5000) add(e, 'dom', v.n + ' changes');
    }
    for (const v of J.all('video')) {
      if (!v.paused && (v.loop || (isFinite(v.duration) && v.duration - v.currentTime > 5))) add(v, 'video', v.loop ? 'playing, looping' : 'playing');
    }
    return out;
  };
  // The elements (read at 0 s, ELEMENTS_JS) inside a region's element.
  M.inside = (css) => {
    const el = M.held.get(css);
    if (!el || !M.els) return { inside: [], next: null };
    const out = [];
    M.els.forEach((e, i) => { if (el === e || el.contains(e)) out.push(i); });
    // Content with no element inside it (an empty spinning box) is placed
    // by document order: the first element that follows it.
    let next = null;
    if (!out.length) {
      next = M.els.findIndex((e) => el.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING);
      if (next < 0) next = M.els.length;
    }
    return { inside: out, next };
  };
})()
