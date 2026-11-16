"""Round 3: one replay of each frozen page against the live page, first 30 s.
Reads only: failed requests, visible text, fixed/sticky overlays, dialogs,
frames and media, and screenshots at 5 s and 30 s. Not part of the repo."""
import asyncio, json, sys
from pathlib import Path

from playwright.async_api import async_playwright

from tobi508.browser import NavigationGuard, launch_browser, new_context
from tobi508.capture import replay_context
from tobi508.config import Settings
from tobi508.egress import EgressProxy
from tobi508.frozen import load

RD = Path("evals/judging/round3")
OUT = Path(sys.argv[1])

STATE_JS = """() => {
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const over = [...document.querySelectorAll('body *')].filter(el => {
    const p = getComputedStyle(el).position; return (p === 'fixed' || p === 'sticky') && vis(el); })
    .map(el => ({tag: el.tagName, id: el.id, cls: String(el.className).slice(0,60),
                 role: el.getAttribute('role'), text: (el.innerText||'').trim().replace(/\\s+/g,' ').slice(0,100)}));
  const dialogs = [...document.querySelectorAll('dialog[open],[role=dialog],[role=alertdialog],[aria-modal=true]')]
    .filter(vis).map(el => (el.innerText||'').trim().replace(/\\s+/g,' ').slice(0,120));
  return {text: (document.body.innerText||''), over, dialogs,
          frames: [...document.querySelectorAll('iframe')].map(f => f.src.split('?')[0]),
          media: [...document.querySelectorAll('video,audio')].map(m => (m.currentSrc||m.src||'').split('?')[0]),
          imgs_broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && vis(i)).map(i => (i.currentSrc||i.src).split('?')[0]).slice(0,20),
          height: document.documentElement.scrollHeight};
}"""


async def watch(ctx, guard, url, tag, name):
    page = await ctx.new_page()
    failed, bad, popups = [], [], []
    page.on("requestfailed", lambda r: failed.append((r.resource_type, r.url.split('?')[0][:140], r.failure)))
    page.on("response", lambda r: r.status >= 400 and bad.append((r.status, r.request.resource_type, r.url.split('?')[0][:140])))
    page.on("popup", lambda p: popups.append(p.url))
    page.on("dialog", lambda d: (popups.append(f"js {d.type}: {d.message[:80]}"), asyncio.ensure_future(d.dismiss())))
    try:
        await guard.goto(page, url)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    states = {}
    for t in (5, 30):
        await page.wait_for_timeout((t - (5 if t == 30 else 0)) * 1000)
        states[t] = await page.evaluate(STATE_JS)
        await page.screenshot(path=str(OUT / f"{name}-{tag}-{t}s.png"))
    await page.close()
    return {"failed": failed, "bad": bad, "popups": popups, "states": states}


async def main():
    s = Settings(browser_channel="chromium", headless=True, run_ttl_hours=1)
    index = load(RD / "frozen")
    pages = [l.split()[0] for l in (RD / "pages.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
    out = {}
    async with EgressProxy(s) as proxy, async_playwright() as pw:
        browser = await launch_browser(pw, s, proxy)
        for n, url in enumerate(pages, 1):
            name = f"p{n:02d}"
            print(name, url, flush=True)
            ctx = await new_context(browser, s)
            g = NavigationGuard(s, live=True, log=lambda *a, **k: None, egress=proxy)
            await g.install(ctx)
            live = await watch(ctx, g, url, "live", name)
            await ctx.close()
            rec = index.get(url)
            rp = await replay_context(browser, s, RD / "frozen" / rec.har, lambda *a, **k: None)
            replay = await watch(rp.context, rp.guard, rec.final_url, "replay", name)
            await rp.context.close()
            out[url] = {"live": live, "replay": replay}
        await browser.close()
    (OUT / "compare.json").write_text(json.dumps(out, indent=1, default=str))

asyncio.run(main())
