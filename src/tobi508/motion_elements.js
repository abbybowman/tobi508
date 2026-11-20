
  const r = units(cap);
  const drop = new Set();
  r.els.forEach((el, i) => {
    if (r.units[i].kind !== 'control' || !el.labels) return;
    for (const lab of el.labels) {
      const j = r.els.findIndex((e, k) => k !== i && r.units[k].kind === 'text' && (e === lab || lab.contains(e)));
      if (j < 0) continue;
      const a = lab.getBoundingClientRect(), b = el.getBoundingClientRect();
      const shared = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
      if (shared >= Math.min(a.height, b.height) / 2) drop.add(j);
    }
  });
  const keep = [], out = [];
  r.els.forEach((el, i) => {
    if (drop.has(i) || el.closest('[aria-hidden="true"]')) return;
    const u = r.units[i];
    keep.push(el);
    out.push({ kind: u.kind, role: u.role, name: (u.name || '').slice(0, 200), css: u.css, box: u.box, stop: !!u.stop,
      href: u.href_attr === undefined ? null : u.href_attr });
  });
  // A media element's own controls (V1): one control element, at its place
  // in document order; the walk focuses its play button inside it.
  for (const m of J.all('audio[controls], video[controls]')) {
    if (!shown(m) || m.closest('[aria-hidden="true"]')) continue;
    let at = keep.findIndex((e) => m.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING);
    if (at < 0) at = keep.length;
    const b = m.getBoundingClientRect();
    keep.splice(at, 0, m);
    out.splice(at, 0, { kind: 'control', role: m.tagName.toLowerCase(), name: 'media controls', css: path(m),
      box: [Math.round(b.x + scrollX), Math.round(b.y + scrollY), Math.round(b.width), Math.round(b.height)],
      stop: true, href: null });
  }
  if (window.__a11yMotion) window.__a11yMotion.els = keep;
  return { elements: out, truncated: r.truncated };
}
