"use strict";
const token = new URLSearchParams(location.hash.slice(1)).get("token") || "";
const log = document.getElementById("log");
const status = document.getElementById("status");
const IMG = /^image\/(png|jpeg|gif|webp)$/;
const B64 = /^[A-Za-z0-9+/]+={0,2}$/;
let after = 0;
const names = {};  // call id -> tool or resource name

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = String(text);
  return e;
}
function pretty(text) {
  try { return JSON.stringify(JSON.parse(text), null, 2); } catch (_) { return text; }
}
function block(title, text, open) {
  const d = el("details");
  d.open = !!open;
  d.append(el("summary", "", title), el("pre", "", text));
  return d;
}
// A line of the outcomes a response carries, copied as they are.
function outcomes(text) {
  const box = el("div", "outcomes");
  let data;
  try { data = JSON.parse(text); } catch (_) { return box; }
  const list = (data && Array.isArray(data.findings)) ? data.findings : [];
  for (const f of list) {
    if (f && f.test_id && f.outcome) box.append(el("span", "chip", f.test_id + " " + f.outcome));
  }
  if (data && data.status && !list.length) {
    box.append(el("span", "chip", "status: " + data.status +
      (data.progress ? " · " + data.progress : "")));
  }
  return box;
}
function shown(kind) {
  const box = document.getElementById("f-" + (kind === "error" ? "result" : kind));
  return !box || box.checked;
}
function render(e) {
  const row = el("div", "ev " + e.kind);
  row.dataset.kind = e.kind;
  const head = el("div", "head");
  head.append(el("time", "", new Date(e.ts * 1000).toLocaleTimeString()));
  if (e.kind === "call") {
    names[e.call] = e.name;
    head.append(el("span", "kind", "→ request"), el("span", "name", e.name),
                el("span", "mut", e.action + (e.who ? " · " + e.who : "")));
    row.append(head);
    if (e.arguments && Object.keys(e.arguments).length)
      row.append(block("arguments", JSON.stringify(e.arguments, null, 2), true));
  } else if (e.kind === "result" || e.kind === "error") {
    head.append(el("span", "kind", e.kind === "error" ? "✕ error" : "← response"),
                el("span", "name", e.name || names[e.call] || ""),
                el("span", "mut", e.seconds + " s" + (e.is_error ? " · tool error" : "")));
    row.append(head);
    if (e.error) row.append(el("pre", "", e.error));
    const first = (e.parts || [])[0];
    if (first && first.type === "text") row.append(outcomes(first.text || ""));
    (e.parts || []).forEach((p, i) => {
      if (p.type === "text") {
        const t = pretty(p.text || "");
        const more = p.more_chars ? " (+" + p.more_chars + " more characters not shown)" : "";
        row.append(block("text, " + (p.text || "").length + " characters" + more, t, i === 0 || t.length < 4000));
      } else if (p.type === "image") {
        const cap = el("div", "mut", "picture " + (i + 1) + ": " + p.mime + ", " + p.bytes + " bytes");
        row.append(cap);
        if (p.data && IMG.test(p.mime) && B64.test(p.data)) {
          const img = el("img", "ev-img");
          img.alt = "Picture sent in this response";
          img.src = "data:" + p.mime + ";base64," + p.data;
          row.append(img);
        }
      } else {
        row.append(el("div", "mut", p.type + (p.bytes ? ", " + p.bytes + " bytes" : "")));
      }
    });
  } else if (e.kind === "progress") {
    head.append(el("span", "kind", "… progress"), el("span", "", e.message),
                el("span", "mut", e.job));
    row.append(head);
  } else if (e.kind === "step") {
    head.append(el("span", "kind", "· step"), el("span", "name", e.step),
                el("span", "mut", e.status + " · run " + e.run_id));
    row.append(head);
    if (e.detail && Object.keys(e.detail).length)
      row.append(el("pre", "", JSON.stringify(e.detail)));
  }
  row.hidden = !shown(e.kind);
  return row;
}
async function poll() {
  try {
    const r = await fetch("/live/events?after=" + after, {
      headers: { "X-Live-Token": token }, cache: "no-store" });
    if (r.status === 404) { status.textContent = "Live log is off, or the token is wrong."; }
    else if (!r.ok) { status.textContent = "Error " + r.status; }
    else {
      const data = await r.json();
      for (const e of data.events) { log.append(render(e)); after = e.seq; }
      status.textContent = "Live · " + new Date().toLocaleTimeString();
      if (data.events.length && document.getElementById("follow").checked)
        window.scrollTo(0, document.body.scrollHeight);
    }
  } catch (_) { status.textContent = "Not connected; retrying…"; }
  setTimeout(poll, 1000);
}
for (const k of ["call", "result", "progress", "step"]) {
  document.getElementById("f-" + k).addEventListener("change", () => {
    for (const row of log.children) row.hidden = !shown(row.dataset.kind);
  });
}
document.getElementById("clear").addEventListener("click", () => log.replaceChildren());
if (!token) status.textContent = "Add #token=… to this page's address.";
else poll();
