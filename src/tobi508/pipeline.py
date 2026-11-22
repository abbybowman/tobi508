"""run_tt_tests and answer_questions orchestration. Generic over checks.

1. Check the URL against the allowlist before launching anything; a page that
   is never tested is a RunRefused (tool error), not a finding.
2. Record the page live to evidence/page.har.zip (allowlist enforced on every
   top-level navigation and redirect hop).
3. If any selected check uses it, run the shared keyboard walk once
   (walk.py): P1 Tab and P2 Shift+Tab, each from a fresh load of the replay.
4. Each selected check (checks/REGISTRY) collects any extra evidence it needs,
   then its rules module evaluates. A selected test with no check is
   NEEDS_REVIEW "This test could not be performed" (never NOT_TESTED, p. 6).
5. The result links the full report (`report_uri`, a run:// resource) for the
   user to save; the run folder is kept only for `run_ttl_hours`, to finish
   open questions and serve evidence.

Nothing here decides an outcome: checks do, from their specs.

The result a tool returns is shaped in result_view.py (fit to the client's
size limit) and next_steps.py (what the agent does next, follow-up calls and
the work left in a session).
"""

from __future__ import annotations

import asyncio
import functools
import math
import shutil
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.async_api import Browser, async_playwright

from tobi508 import (
    config,
    flashcap,
    hidden,
    jobs,
    motion,
    pagecache,
    reveal,
    rules,
    scrt,
)
from tobi508 import count as inventory
from tobi508.browser import (
    MOTION_BROWSER,
    NavigationBlocked,
    launch_browser,
    launch_for,
    replay_browser_name,
    replay_in_full_chromium,
)
from tobi508.capture import Capture, document_sha, replay_context, unrecorded_code
from tobi508.checks import REGISTRY, RunContext
from tobi508.checks.base import (
    AFTER,
    PageRef,
    budget_s,
    out_of_budget_reason,
    time_for,
)
from tobi508.config import Settings
from tobi508.egress import EgressProxy
from tobi508.engine import apply_guards
from tobi508.frozen import NotFrozen, obtain
from tobi508.judgment import get_judge, record_answers
from tobi508.models import (
    REVIEW_HEAD,
    Answer,
    AnswerResult,
    Count,
    Finding,
    FindingView,
    OtherPage,
    Outcome,
    Remaining,
    Report,
    RunResult,
    TestId,
    TestTime,
    utcnow,
    waiting_head,
)
from tobi508.motion import MOTION_INIT_JS
from tobi508.next_steps import QUESTION_PAGE, follow_ups, next_step, todo
from tobi508.policy import check_url
from tobi508.progress import Tracker
from tobi508.redact import safe_error, safe_url
from tobi508.resources.runs import run_uri
from tobi508.result_view import (
    _evidence_uris,
    _page_text,
    _question_view,
    _shared_inputs,
    _walk_summary,
    fit,
)
from tobi508.runlog import RunRecorder, expires_at, prune_runs
from tobi508.site import same_place
from tobi508.traverse import (
    Pace,
    ReplayPlan,
    TooManyItems,
    WalkTooLong,
    metered,
    settle,
)
from tobi508.versions import collect_versions, measure_display
from tobi508.walk import KeyboardWalk, walk_page

NO_SPEC_REASON = "No rules exist for this test yet, so it was not run."

# The run limit (4.C spec section 2, Run limits). Checks stop starting new work
# RESERVE_S before the limit; a phase still running HARD_MARGIN_S before it is
# cancelled (its tests are NEEDS REVIEW), leaving time to write the report.
RESERVE_S = 10
HARD_MARGIN_S = 2
TIME_NOTE = (
    "The run reached its time limit ({limit} s) before every test finished; "
    "what was not finished is NEEDS REVIEW. To finish it, run again with "
    "no_time_limit=true (the call can then take several minutes)."
)

Progress = Callable[[float, float | None, str], Awaitable[None]]

# Other pages of the same site a caller may name (9.A-9.C).
# The cap keeps one call within its time limit; a caller who turns the limit
# off may name more, up to a bound on the input itself.
OTHER_PAGES_MAX = 5
OTHER_PAGES_NO_LIMIT_MAX = 50


class RunRefused(Exception):
    """The page was never tested (not allowed, or it could not be loaded), or
    the run does not exist. A tool error, not a finding."""


# The tests whose specs count hidden fields (front matter `count:`
# fields_hidden): the hidden-field check runs only for them.
HIDDEN_FIELD_TESTS = frozenset(
    TestId(t) for t in ("5.A", "5.B", "5.C", "5.D", "5.F", "5.G", "5.H")
)


def evidence_name(test_id: TestId) -> str:
    return test_id.value.lower().replace(".", "") + ".json"  # "4.C" -> "4c.json"


def _opener(
    get_browser,
    settings: Settings,
    har: Path,
    final_url: str,
    run,
    frames: list[str],
    init_scripts: tuple[str, ...] = (),
    autoplay: bool = False,
    ignore: SettleIgnore | None = None,
    viewport: dict[str, int] | None = None,
    paused_clock: bool = False,
):
    """A fresh replay context and page for every load (docs/solutions/
    focus-and-walk.md). A page with cross-site frames replays in full
    Chromium (browser.replay_in_full_chromium). `init_scripts`: extra hooks;
    `autoplay`: pass T's browser (full Chromium, headless, autoplay allowed;
    plan Q1 and Q11). `viewport` and `paused_clock`: 3.A's flash capture
    (flashcap.py), at 1024 x 768 with Playwright's clock installed and paused
    before the page loads, so the capture steps the page's time; 2.C's clock
    check uses the paused clock too, with `init_scripts` added after it."""
    full = autoplay or replay_in_full_chromium(settings, frames)

    async def new_page():
        browser = await get_browser(full, autoplay)
        replay = await replay_context(
            browser,
            settings,
            har,
            run.log,
            init_scripts=() if paused_clock else init_scripts,
            viewport=viewport,
        )
        if paused_clock:
            await flashcap.pause_clock(replay.context)
            # After the clock: Playwright's clock replaces the timer functions,
            # so a hook added before it would see none (2.C's clock check).
            for script in init_scripts:
                await replay.context.add_init_script(script)
        page = await replay.context.new_page()
        await replay.guard.goto(page, final_url)
        if ignore is not None:
            await ignore.join(page)
        return replay.context, page

    return new_page


class SettleIgnore:
    """Content pass T found still changing by itself (a ticker, a carousel):
    the settle rule stops waiting on its DOM changes (traverse.INIT_JS
    setIgnore; Abby, 2026-11-04, T1 (b)). Pages of the tested page join it;
    when pass T ends, the list goes to every page still open (the walk's
    included) and to each page opened after."""

    def __init__(self) -> None:
        self.sels: dict[str, list[str]] = {}
        self.pages: list = []

    async def _apply(self, page) -> None:
        for frame in page.frames:
            key = "" if frame == page.main_frame else frame.url
            sels = self.sels.get(key)
            if not sels:
                continue
            try:
                await frame.evaluate(
                    "(s) => window.__a11yLog && window.__a11yLog.setIgnore(s)", sels
                )
            except Exception:
                continue

    async def join(self, page) -> None:
        self.pages = [p for p in self.pages if not p.is_closed()]
        self.pages.append(page)
        if self.sels:
            await self._apply(page)

    async def set(self, sels: dict[str, list[str]]) -> None:
        self.sels = sels
        for page in [p for p in self.pages if not p.is_closed()]:
            await self._apply(page)


async def _watch_then_ignore(ctx, run, extend=None, keep_shots=True):
    mp = await motion.collect(ctx, keep_shots)
    sels = motion.settle_ignore(mp)
    if sels and ctx.settle_ignore is not None:
        await ctx.settle_ignore.set(sels)
        run.log("settle_ignore", regions=sum(len(v) for v in sels.values()))
    if sels and extend is not None:
        extend()
    return mp


def _context(
    settings: Settings,
    run: RunRecorder,
    get_browser,
    final_url: str,
    deadline: float,
    frames: list[str],
):
    har = run.evidence_dir / "page.har.zip"
    ignore = SettleIgnore()
    return RunContext(
        new_page=_opener(
            get_browser, settings, har, final_url, run, frames, ignore=ignore
        ),
        # Pass T (2.A-2.D) in its own browser: full Chromium, headless, with
        # autoplay allowed (plan Q1, Q11), so the walk's browser is unchanged.
        open_motion=_opener(
            get_browser,
            settings,
            har,
            final_url,
            run,
            frames,
            (MOTION_INIT_JS,),
            autoplay=True,
            ignore=ignore,
        ),
        # 3.A's flash capture: pass T's browser, 1024 x 768, the page's clock
        # paused before it loads (flashcap.py), and no hooks of ours.
        open_flash=_opener(
            get_browser,
            settings,
            har,
            final_url,
            run,
            frames,
            autoplay=True,
            viewport=dict(zip(("width", "height"), flashcap.VIEWPORT)),
            paused_clock=True,
        ),
        # 2.C's clock check (2.C spec 1.2.0): pass T's browser and window, the
        # page's clock paused before it loads, and a timer hook added after it.
        open_clock=_opener(
            get_browser,
            settings,
            har,
            final_url,
            run,
            frames,
            (motion.TIMER_HOOK_JS, motion.MUTATION_COUNT_JS),
            autoplay=True,
            paused_clock=True,
        ),
        settle_ignore=ignore,
        motion_browser=MOTION_BROWSER,
        quiet_ms=settings.settle_quiet_ms,
        deadline=deadline,
        shots=run.evidence_dir / "shots",
        rel=run.dir,
        third_party=settings.third_party_dir,
    )


def _soft_deadline(
    start: float, settings: Settings, no_time_limit: bool, pages: int = 0
) -> float:
    if no_time_limit:
        return start + settings.max_run_s - RESERVE_S
    return start + _limit(settings, pages) - RESERVE_S


def _limit(settings: Settings, pages: int) -> int:
    """The run limit: `run_limit_s`, plus `other_page_s` for each other page
    recorded (2026-11-02: the limit is set per page)."""
    return settings.run_limit_s + pages * settings.other_page_s


BUDGET_GRACE_S = 10  # a test stops starting work this long before its end


def run_order(checks: list, settings: Settings) -> list:
    """Cheapest budget first, each test after the selected tests
    its collect reads (checks.base.AFTER); ties keep the registry's order."""
    left = list(checks)
    ids = {c.test_id.value for c in left}
    done: set[str] = set()
    out: list = []
    while left:
        ready = [
            c
            for c in left
            if all(d in done or d not in ids for d in AFTER.get(c.test_id.value, ()))
        ]
        nxt = min(ready or left, key=lambda c: budget_s(settings, c.test_id.value))
        out.append(nxt)
        left.remove(nxt)
        done.add(nxt.test_id.value)
    return out


def uses_pages(check) -> bool:
    return bool(getattr(check, "uses_pages", False))


def _reveals(check) -> bool:
    return bool(getattr(check, "uses_reveal", False))


def needs_walk(check, ctx: RunContext) -> bool:
    """A check that compares pages needs nothing (not even the walk) when no
    other pages were given: it is not performed."""
    return check.uses_walk and not (uses_pages(check) and not ctx.pages)


def _site(url: str) -> tuple[str, str]:
    parts = urlsplit(url)
    return parts.scheme.lower(), (parts.hostname or "").lower().rstrip(".")


def _same_site(a: str, b: str) -> bool:
    """Same host (and both file:// in dev mode), the rule for other pages."""
    sa, sb = _site(a), _site(b)
    if "file" in (sa[0], sb[0]):
        return sa[0] == sb[0] == "file"
    return sa[1] == sb[1] and sa[1] != ""


def same_address(a: str, b: str) -> bool:
    """The same page address: the fragment, the scheme, the case of the host
    and a trailing slash or empty query do not tell pages apart (K-01). A
    query string can (page.html?id=2), so it does. Used so a page is never
    compared with itself under another spelling."""

    def key(u: str) -> tuple[str, int | None, str, str]:
        p = urlsplit(u)
        try:
            port = p.port
        except ValueError:
            port = None
        if port in (80, 443):
            port = None
        return (
            (p.hostname or "").lower().rstrip("."),
            port,
            p.path.rstrip("/") or "/",
            p.query,
        )

    return key(a) == key(b)


def check_other_pages(
    settings: Settings, url: str, other: list[str], no_time_limit: bool = False
) -> list[str]:
    """The caller's other pages, deduplicated in order; raises RunRefused if
    one is not allowed, not on the tested page's host, or is the page itself.
    Page content never adds to this list (CLAUDE.md principle 5)."""
    out: list[str] = []
    for u in other:
        if not any(same_address(u, o) for o in out):
            out.append(u)
    if len(out) > OTHER_PAGES_NO_LIMIT_MAX:
        raise RunRefused(
            f"At most {OTHER_PAGES_NO_LIMIT_MAX} other pages can be compared in "
            "one call."
        )
    if len(out) > OTHER_PAGES_MAX and not no_time_limit:
        raise RunRefused(
            f"At most {OTHER_PAGES_MAX} other pages can be compared within the "
            "time limit. To compare more, run again with no_time_limit=true "
            f"(each page adds about {settings.other_page_s} s)."
        )
    for i, u in enumerate(out, 1):
        d = check_url(u, settings.allowed_domains, settings.dev_mode)
        if not d.allowed:
            raise RunRefused(f"Other page {i} not allowed: {d.reason}")
        if not _same_site(u, url):
            raise RunRefused(
                f"Other page {i} is not on the tested page's host; other pages "
                "must be pages of the same site."
            )
        if same_address(u, url):
            raise RunRefused(f"Other page {i} is the tested page itself.")
    return out


async def capture_other(
    browser,
    settings: Settings,
    run,
    url: str,
    rel: str,
    proxy,
    hard: float,
    use_cache: bool = True,
) -> tuple[Capture, Any]:
    """Record one other page of the site as its own HAR at `rel`, cancelled
    at `hard` (monotonic; TimeoutError): the one code path for the caller's
    other pages and the pages 19.A loads itself (its suspected aliases and,
    without the page cache, its site search). `obtain` checks the allowlist
    on every redirect hop; the caller checks the host after redirects.
    Returns the capture and the page cache's hit (None when recorded now)."""
    (run.dir / rel).parent.mkdir(parents=True, exist_ok=True)
    hit = pagecache.reused(settings, url, run.dir / rel) if use_cache else None
    if hit:
        return (
            Capture(
                target_url=url,
                final_url=hit.final_url,
                har_path=run.dir / rel,
                cross_site_frames=list(hit.cross_site_frames),
                frozen=hit.frozen,
            ),
            hit,
        )
    oc = await _bounded(
        obtain(browser, settings, url, run.dir / rel, run.log, proxy, tested=False),
        hard,
    )
    if use_cache:
        pagecache.keep(
            settings, url, run.dir / rel, oc.final_url, oc.cross_site_frames, oc.frozen
        )
    return oc, None


def _www(host: str) -> str:
    host = (host or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def _live_recorder(
    browser, settings, run, report, proxy, final_url, get_browser, tested_har=None
):
    """Pages 19.A loads itself, each by the code a caller's other page uses
    (`capture_other`): its live site search (CLAUDE.md),
    its suspected aliases of the tested page
    and its suggested pages.
    Allowlisted on every hop and on the tested page's host after redirects;
    an alias may be asked for under the host with or without a leading
    "www." (its definition), and must still end on the tested page's host."""

    async def record_live(url: str, purpose: str = "search") -> PageRef:
        d = check_url(url, settings.allowed_domains, settings.dev_mode)
        if purpose == "alias":
            host_ok = _same_site(url, final_url) or (
                urlsplit(url).scheme in ("http", "https")
                and _www(urlsplit(url).hostname or "")
                == _www(urlsplit(final_url).hostname or "")
            )
        else:
            host_ok = _same_site(url, final_url)
        if not d.allowed or not host_ok:
            raise ValueError("not on the tested page's host or not allowed")
        n = len(report.live_pages) + 1
        rel = f"evidence/pages/live{n}.har.zip"
        t1 = time.monotonic()
        # The same share a caller-named page gets, so a slow load cannot take
        # the later checks' time (19.A W4 or W7 on a timeout). The search is
        # never taken from the page cache: its results are read as they are.
        lc, hit = await capture_other(
            browser,
            settings,
            run,
            url,
            rel,
            proxy,
            time.monotonic() + settings.other_page_s,
            use_cache=purpose != "search",
        )
        if not _same_site(lc.final_url, final_url):
            raise ValueError("it ended on another host after redirects")
        same = False
        # Step 26 (#134): the same document counts only at the tested page's
        # host and path apart from the query string; an application sends one
        # document for every address. An alias (index.*, www.) is then the
        # tested page only when it ends at the tested page's address.
        if (
            purpose in ("alias", "suggested")
            and tested_har is not None
            and same_place(final_url, lc.final_url)
        ):
            mine = document_sha(tested_har, final_url)
            same = mine is not None and mine == document_sha(
                run.dir / rel, lc.final_url
            )
        # 19.A 1.20.0 (#138 draft A): an alias with T's document anywhere;
        # 19.A then compares the page as drawn (site.text_share).
        same_document = False
        if purpose == "alias" and tested_har is not None and not same:
            mine = document_sha(tested_har, final_url)
            same_document = mine is not None and mine == document_sha(
                run.dir / rel, lc.final_url
            )
        report.live_pages.append(
            OtherPage(
                n=n,
                url=url,
                final_url=lc.final_url,
                har=rel,
                purpose=purpose,
                same_content_as_tested=same,
                cross_site_frames=lc.cross_site_frames,
                frozen=lc.frozen if settings.frozen_pages_dir else None,
                reused_from=(
                    datetime.fromtimestamp(hit.recorded_at, timezone.utc).isoformat(
                        timespec="seconds"
                    )
                    if hit
                    else None
                ),
                replay_browser=replay_browser_name(settings, lc.cross_site_frames),
            )
        )
        run.log(
            "captured_live",
            n=n,
            purpose=purpose,
            seconds=round(time.monotonic() - t1, 2),
        )
        return PageRef(
            n=100 + n,
            url=url,
            final_url=lc.final_url,
            har=run.dir / rel,
            same_content_as_tested=same,
            same_document=same_document,
            new_page=_opener(
                get_browser,
                settings,
                run.dir / rel,
                lc.final_url,
                run,
                lc.cross_site_frames,
            ),
        )

    return record_live


def _page_refs(get_browser, settings: Settings, run, report: Report) -> list[PageRef]:
    return [
        PageRef(
            n=p.n,
            url=p.url,
            final_url=p.final_url or p.url,
            same_content_as_tested=p.same_content_as_tested,
            har_sha=pagecache.sha256(run.dir / p.har)
            if (run.dir / p.har).is_file()
            else None,
            new_page=_opener(
                get_browser,
                settings,
                run.dir / p.har,
                p.final_url or p.url,
                run,
                p.cross_site_frames,
            ),
        )
        for p in report.other_pages
    ]


def _awaiting(coro, depth: int = 40) -> str:
    """Where a suspended coroutine waits: each frame down its await chain."""
    out = []
    while coro is not None and depth:
        frame = getattr(coro, "cr_frame", None) or getattr(coro, "gi_frame", None)
        if frame is not None:
            code = frame.f_code
            out.append(
                f"{code.co_filename.rsplit('/', 1)[-1]}:{frame.f_lineno} {code.co_name}"
            )
        coro = getattr(coro, "cr_await", None) or getattr(coro, "gi_yieldfrom", None)
        depth -= 1
    return " > ".join(out)


async def _abandoned_at(aw, hard: float, log=None, name: str = ""):
    """Await `aw` until `hard`; then cancel it and return at once (TimeoutError),
    without waiting for its cleanup. `asyncio.wait_for` waits for a cancelled
    task to finish, and a test's cleanup can wait on a busy page (closing a
    context whose page is still running script): 14194's 3.A ran 1,178 s
    against a 240 s budget that way. The task finishes cancelling
    on its own; the run's end closes the browsers. Where it was is logged."""
    left = hard - time.monotonic()
    if left <= 0:
        aw.close()
        raise TimeoutError
    task = asyncio.ensure_future(aw)
    done, _ = await asyncio.wait({task}, timeout=left)
    if task in done:
        return task.result()
    where = _awaiting(task.get_coro())
    task.cancel()
    task.add_done_callback(lambda t: t.cancelled() or t.exception())
    if log is not None:
        log("check_abandoned", "error", test=name, where=where[:2000])
    raise TimeoutError


async def _bounded(aw, hard: float):
    """Await `aw`, cancelling it at `hard` (TimeoutError)."""
    if hard == math.inf:
        return await aw
    left = hard - time.monotonic()
    if left <= 0:
        aw.close()
        raise TimeoutError
    return await asyncio.wait_for(aw, left)


def _cap_skipped(exc: TooManyItems) -> str:
    c = exc.cap
    minutes = max(1, round(exc.estimate_s / 60))
    return (
        f"this page has {exc.count} {c.noun}, and one call checks at "
        f"most {c.limit}. The other tests ran. To run this one too, call again "
        f'with tests ["{c.test}"] and no_time_limit=true (about {minutes} min '
        "or more; follow it with tobi_run_status), and replace its result in "
        "the saved report."
    )


def _too_long(exc: WalkTooLong, limit: int) -> str:
    minutes = max(1, round(exc.estimate_s / 60))
    if isinstance(exc, TooManyItems):
        c = exc.cap
        return (
            f"This page has {exc.count} {c.noun}; one call checks at most "
            f"{c.limit} for test {c.test}, so most of them would be left for a "
            f"person. Nothing was tested. To test them all, call again with "
            f"no_time_limit=true (about {minutes} min or more), or leave {c.test} "
            "out of the tests, or test a smaller page."
        )
    return (
        f"This page has about {exc.candidates} places the keyboard can reach. At "
        f"the pace of the first {exc.presses} key presses, walking it with Tab "
        f"and Shift+Tab alone would take about {minutes} min, more than one call "
        f"allows ({limit} s). Nothing was tested. To test it anyway, call again "
        "with no_time_limit=true (the call will take that long or more), or "
        "test a smaller page."
    )


class _LazyBrowser:
    """Starts Chrome only if a check needs it (resume often does not); full
    Chromium only if a page with cross-site frames is replayed."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._pw = self._proxy = None
        self._browsers: dict[tuple[bool, bool], Browser] = {}

    async def get(self, full: bool = False, autoplay: bool = False) -> Browser:
        if self._proxy is None:
            self._proxy = await EgressProxy(self.settings).__aenter__()
            self._pw = await async_playwright().start()
        if (full, autoplay) not in self._browsers:
            self._browsers[(full, autoplay)] = await launch_for(
                self._pw, self.settings, self._proxy, full, autoplay
            )
        return self._browsers[(full, autoplay)]

    async def close(self) -> None:
        for b in self._browsers.values():
            await b.close()
        if self._pw is not None:
            await self._pw.stop()
        if self._proxy is not None:
            await self._proxy.__aexit__(None, None, None)


def _blocked_hosts(proxy: EgressProxy) -> str:
    """Hosts the egress proxy refused for their address (host, port and
    reason only)."""
    seen: dict[str, str] = {}
    for r in proxy.refused:
        if not r["reason"].startswith("resolves to"):
            continue
        seen.setdefault(f"{r['host']}:{r['port']}", r["reason"])
    return "; ".join(f"{h} ({why})" for h, why in seen.items())


def _load_states(run: RunRecorder) -> dict[TestId, Any]:
    states = {}
    for t, check in REGISTRY.items():
        path = run.evidence_dir / evidence_name(t)
        if path.exists():
            states[t] = check.state_type.model_validate_json(path.read_text("utf-8"))
    return states


@functools.lru_cache(maxsize=4)
def _specs(rules_dir: str):
    return rules.load_specs(Path(rules_dir))


def _guards(test_id: TestId) -> tuple[str, ...]:
    """The shared page guards a test's spec declares (specs/rules front matter)."""
    spec = _specs(str(config.settings.rules_dir)).get(test_id)
    return spec.guards if spec else ()


def _count_keys(test_id: TestId) -> tuple[str, ...]:
    """The inventory keys guard CN compares for a test (front matter `count:`)."""
    spec = _specs(str(config.settings.rules_dir)).get(test_id)
    return spec.count if spec else ()


async def _own_count(ctx: RunContext) -> Count:
    """The inventory on a load of its own, when no walk took it (count.py)."""
    try:
        context, page = await ctx.new_page()
    except Exception as exc:
        return Count(where="own load", error=safe_error(exc))
    try:
        await settle(page, ctx.quiet_ms)
        return await inventory.take(page, "own load")
    except Exception as exc:
        return Count(where="own load", error=safe_error(exc))
    finally:
        await context.close()


def _evaluate(
    run: RunRecorder,
    report: Report,
    states: dict[TestId, Any],
    skipped: dict[TestId, str] | None = None,
) -> None:
    """Findings and questions for every selected test, from the checks' rules.
    `skipped`: tests the run left out on purpose, with the reason."""
    from tobi508.traverse import DRAW_CUT

    for u in DRAW_CUT.get() or []:
        if safe_url(u) not in report.drawn_past_wait:
            report.drawn_past_wait.append(safe_url(u))
    tests = report_tests(report)
    asked = {q.question_id for q in report.questions}
    findings: list[Finding] = []
    for t in tests:
        check = REGISTRY.get(t)
        if check is None:
            findings.append(Finding.not_performed(t, NO_SPEC_REASON))
            continue
        if t not in states and skipped and t in skipped:
            findings.append(Finding.not_performed(t, skipped[t]))
            continue
        if t not in states:
            why = "; ".join(report.errors) or "unknown error"
            findings.append(
                Finding.not_performed(t, f"The run did not complete: {why}")
            )
            continue
        rel = f"evidence/{evidence_name(t)}"
        uri = run_uri(run.run_id, rel)
        report.questions += [
            q for q in check.questions(states[t], [uri]) if q.question_id not in asked
        ]
        findings.append(
            apply_guards(
                check.evaluate(states[t], [rel]),
                _guards(t),
                report,
                states[t],
                _count_keys(t),
            )
        )
    report.findings = findings
    answered = {r.answer.question_id for r in report.answers}
    report.open_questions = [
        q for q in report.questions if q.question_id not in answered
    ]
    # Wording only: while questions are open, say so instead of "a person
    # needs to check it" (the agent usually answers them next).
    for f in report.findings:
        n = sum(q.test_id is f.test_id for q in report.open_questions)
        if (
            n
            and f.outcome is Outcome.NEEDS_REVIEW
            and f.summary.startswith(REVIEW_HEAD)
        ):
            f.summary = waiting_head(n) + f.summary[len(REVIEW_HEAD) :]


def _walk_extras(checks) -> list:
    """The union of the selected checks' walk extras, one per hook name."""
    seen: dict[str, Any] = {}
    for c in checks:
        for factory in c.walk_extras():
            name = factory("P1", None).name
            seen.setdefault(name, factory)
    return list(seen.values())


def report_tests(report: Report) -> list[TestId]:
    return [TestId(t) for t in report.tests]


async def run_tt_tests(
    settings: Settings,
    url: str,
    tests: list[TestId],
    progress: Progress | None = None,
    no_time_limit: bool = False,
    other_pages: list[str] | None = None,
    lift_media_cap: bool | None = None,
) -> RunResult:
    t_start = time.monotonic()
    from tobi508.traverse import DRAW_CUT, DRAWN

    DRAWN.set({})  # step 23: which addresses of this run draw after load
    DRAW_CUT.set([])  # row WL: loads still drawing when the wait ended
    if no_time_limit if lift_media_cap is None else lift_media_cap:
        # The user's choice also lifts the media store's cap (plan Q9); the
        # server's default of no time limit does not.
        settings = settings.model_copy(
            update={"media_cap_mb": None, "media_cap_s": None}
        )
    decision = check_url(url, settings.allowed_domains, settings.dev_mode)
    if not decision.allowed:
        raise RunRefused(f"URL not allowed: {decision.reason}")
    others = check_other_pages(settings, url, other_pages or [], no_time_limit)
    prune_runs(settings.runs_dir, settings.run_ttl_hours)
    run = RunRecorder(settings.runs_dir)
    selected = [t for t in TestId if t in set(tests)]
    run.log("run_start", target=url, tests=[t.value for t in selected])
    report = Report(
        run_id=run.run_id,
        target=url,
        tests=[t.value for t in selected],
        started_at=utcnow(),
        versions=collect_versions(settings, None, no_time_limit),
        judge_backend=settings.judge_backend,
        evidence_dir="evidence",
        frozen_pages=settings.frozen_pages_mode if settings.frozen_pages_dir else None,
    )
    checks = [REGISTRY[t] for t in selected if t in REGISTRY]
    # Other pages are recorded only for a check that compares pages.
    if others and not any(uses_pages(c) for c in checks):
        report.errors.append(
            "The other pages were not used: none of the selected tests compares pages."
        )
        others = []
    soft = _soft_deadline(t_start, settings, no_time_limit, len(others))
    hard = (
        t_start + settings.max_run_s - HARD_MARGIN_S
        if no_time_limit
        else t_start + _limit(settings, len(others)) - HARD_MARGIN_S
    )
    # Cheapest budget first, each after the tests whose replays it reads
    # (checks.base.AFTER). Findings keep the report's order.
    checks = run_order(checks, settings)
    # The reading steps this run may take, fixed now so the counts in the
    # progress line never go back: one not needed counts as done (progress.py).
    walks = any(c.uses_walk or getattr(c, "uses_motion", False) for c in checks)
    track = Tracker(
        progress,
        [
            "record",
            *(f"other{i}" for i in range(1, len(others) + 1)),
            *(["walk"] if walks else []),
            *(["reveal"] if walks and any(_reveals(c) for c in checks) else []),
            "inventory",
            *(
                ["hidden"]
                if any(c.test_id in HIDDEN_FIELD_TESTS for c in checks)
                else []
            ),
        ],
    )
    states: dict[TestId, Any] = {}
    skipped: dict[TestId, str] = {}  # tests left out, and why (fix 12)
    ran_out: dict[TestId, str] = {}  # tests past their own budget
    walk: KeyboardWalk | None = None
    motion_task: asyncio.Task | None = None
    allowance = [0]  # T1 (a): seconds added once pass T finds moving content

    def extend() -> None:
        if no_time_limit or allowance[0]:
            return
        allowance[0] = settings.moving_allowance_s
        if ctx_ref:
            ctx_ref[0].deadline += allowance[0]
        run.log("time_allowance", seconds=allowance[0])

    ctx_ref: list = []

    async with EgressProxy(settings, log=run.log) as proxy, async_playwright() as pw:
        browser = await launch_browser(pw, settings, proxy)
        extra_browsers: dict[tuple[bool, bool], Browser] = {}  # on first need

        async def get_browser(full: bool = False, autoplay: bool = False) -> Browser:
            if not full and not autoplay:
                return browser
            if (full, autoplay) not in extra_browsers:
                extra_browsers[(full, autoplay)] = await launch_for(
                    pw, settings, proxy, full, autoplay
                )
                kind = MOTION_BROWSER if autoplay else "full Chromium"
                run.log("browser_launched", kind=kind)
            return extra_browsers[(full, autoplay)]

        try:
            report.versions = collect_versions(settings, browser, no_time_limit)
            report.versions.display = await measure_display(settings, browser)
            run.log("browser_launched", version=browser.version)
            await track.reading("Recording the page")
            har = run.evidence_dir / "page.har.zip"
            t0 = time.monotonic()
            try:
                cap = await _bounded(
                    obtain(browser, settings, url, har, run.log, proxy), hard
                )
            except Exception as exc:
                # The page never loaded: a tool error, and nothing is kept.
                shutil.rmtree(run.dir, ignore_errors=True)
                if isinstance(exc, TimeoutError):
                    raise RunRefused(
                        "The page could not be recorded within the time limit."
                    ) from None
                if isinstance(exc, (NavigationBlocked, NotFrozen)):
                    raise RunRefused(str(exc)) from exc
                raise RunRefused(
                    f"The page could not be loaded: {safe_error(exc)}"
                ) from None
            report.final_url = cap.final_url
            report.cross_site_frames = cap.cross_site_frames
            report.replay_browser = replay_browser_name(settings, cap.cross_site_frames)
            missing = unrecorded_code(har)
            report.unrecorded_code = [safe_url(u) for u in missing[:20]]
            report.unrecorded_code_count = len(missing)
            track.close("record")
            pages_cut = ""
            for i, other in enumerate(others, 1):
                await track.reading(f"Recording other page {i} of {len(others)}")
                rel = f"evidence/pages/p{i}.har.zip"
                t1 = time.monotonic()
                try:
                    # Each other page records within its own share of the
                    # limit, so a slow one cannot eat the other tests' time.
                    share = hard if no_time_limit else t1 + settings.other_page_s
                    oc, hit = await capture_other(
                        browser, settings, run, other, rel, proxy, min(hard, share)
                    )
                except TimeoutError:
                    # The single-page tests still run; the tests that compare
                    # pages are not performed rather than run on fewer pages.
                    pages_cut = (
                        f"Other page {i} could not be recorded within its "
                        f"{settings.other_page_s} s, so the tests that compare "
                        "pages were not performed. To run them, give fewer other "
                        "pages, or run again with no_time_limit=true."
                    )
                    run.log("captured_other", "error", n=i, error="time limit")
                    report.errors.append(pages_cut)
                    report.other_pages = []
                    track.close(*(f"other{j}" for j in range(i, len(others) + 1)))
                    break
                except Exception as exc:
                    shutil.rmtree(run.dir, ignore_errors=True)
                    if isinstance(exc, (NavigationBlocked, NotFrozen)):
                        raise RunRefused(f"Other page {i}: {exc}") from exc
                    raise RunRefused(
                        f"Other page {i} could not be loaded: {safe_error(exc)}"
                    ) from None
                if not _same_site(oc.final_url, cap.final_url):
                    shutil.rmtree(run.dir, ignore_errors=True)
                    raise RunRefused(
                        f"Other page {i} ended on another host after redirects; "
                        "other pages must be pages of the same site."
                    )
                # After redirects, an other page that ended on the tested
                # page, or on an earlier other page, is the same page: the
                # comparisons would PASS on no evidence (K-01).
                same_as = None
                if same_address(oc.final_url, cap.final_url):
                    same_as = "the tested page"
                else:
                    for o in report.other_pages:
                        if same_address(oc.final_url, o.final_url):
                            same_as = f"other page {o.n}"
                            break
                if same_as:
                    shutil.rmtree(run.dir, ignore_errors=True)
                    raise RunRefused(
                        f"Other page {i} ends on the same page as {same_as} after "
                        "redirects. Give pages that differ."
                    )
                # A query string can make another page, so the address was not
                # refused; the same document bytes under another address is the
                # tested page again (K-01).
                # Step 26: only at the same host and path apart from the query
                # string (an application sends one document at every address).
                tested_sha = document_sha(har, cap.final_url)
                same_content = (
                    tested_sha is not None
                    and same_place(cap.final_url, oc.final_url)
                    and tested_sha == document_sha(run.dir / rel, oc.final_url)
                )
                report.other_pages.append(
                    OtherPage(
                        n=i,
                        url=other,
                        final_url=oc.final_url,
                        same_content_as_tested=same_content,
                        har=rel,
                        cross_site_frames=oc.cross_site_frames,
                        frozen=oc.frozen if settings.frozen_pages_dir else None,
                        reused_from=(
                            datetime.fromtimestamp(
                                hit.recorded_at, timezone.utc
                            ).isoformat(timespec="seconds")
                            if hit
                            else None
                        ),
                        replay_browser=replay_browser_name(
                            settings, oc.cross_site_frames
                        ),
                    )
                )
                track.close(f"other{i}")
                run.log(
                    "captured_other",
                    n=i,
                    reused=bool(hit),
                    final_url=oc.final_url,
                    seconds=round(time.monotonic() - t1, 2),
                )
            blocked = _blocked_hosts(proxy)
            if blocked:
                # The page loaded without these parts; the findings cover only
                # what loaded. A note, not an outcome.
                report.errors.append(
                    "Some page content was not loaded because its host resolves "
                    f"to a non-public address: {blocked}"
                )
            run.log(
                "captured",
                final_url=cap.final_url,
                redirects=cap.redirects,
                seconds=round(time.monotonic() - t0, 2),
            )
            ctx = _context(
                settings, run, get_browser, cap.final_url, soft, cap.cross_site_frames
            )
            ctx.no_time_limit = no_time_limit
            ctx_ref.append(ctx)
            ctx.selected = frozenset(c.test_id.value for c in checks)
            ctx.requested_url = url
            ctx.pages = _page_refs(get_browser, settings, run, report)
            ctx.record_live = _live_recorder(
                browser,
                settings,
                run,
                report,
                proxy,
                cap.final_url,
                get_browser,
                tested_har=har,
            )
            if any(getattr(c, "uses_motion", False) for c in checks) or any(
                needs_walk(c, ctx) for c in checks
            ):
                # Pass T beside the walk, in its own browser (plan Q2; no
                # measurable cost to the walk, item 18). The 2.x checks await
                # this task through motion.collect. It also runs for the walk
                # alone: what it finds still changing, the settle rule stops
                # waiting on (T1 (b)).
                motion_task = asyncio.create_task(
                    _watch_then_ignore(
                        ctx,
                        run,
                        extend,
                        # Frames are evidence for 2.x questions only.
                        any(getattr(c, "uses_motion", False) for c in checks),
                    )
                )
                ctx.cache["motion_task"] = motion_task
            while any(needs_walk(c, ctx) for c in checks):
                await track.reading("Walking the page with Tab and Shift+Tab")
                caps = [c.cap for c in checks if getattr(c, "cap", None)]
                pace = None if no_time_limit else Pace(soft, caps=caps)
                try:
                    with metered() as cost:
                        walk = await _bounded(
                            walk_page(
                                ctx.new_page,
                                ctx.quiet_ms,
                                ctx.deadline,
                                ctx.shots,
                                ctx.rel,
                                [
                                    *_walk_extras(checks),
                                    inventory.walk_extra(ctx.cache),
                                ],
                                pace,
                            ),
                            hard,
                        )
                except TooManyItems as exc:
                    # Over one check's cap (5.D's form fields), found at the
                    # first load: leave that test out, say how to run it, and
                    # test the rest (post-round 1 fix 12).
                    t = TestId(exc.cap.test)
                    checks = [c for c in checks if c.test_id is not t]
                    skipped[t] = _cap_skipped(exc)
                    report.errors.append(f"{t.value} was not run: {skipped[t]}")
                    run.log("cap_skipped", test=t.value, count=exc.count)
                    continue
                except WalkTooLong as exc:
                    # Stop and say so instead of running out of time: the
                    # caller chooses no_time_limit or another page.
                    shutil.rmtree(run.dir, ignore_errors=True)
                    raise RunRefused(_too_long(exc, settings.run_limit_s)) from None
                except TimeoutError:
                    report.errors.append(
                        "The keyboard walk did not finish within the time limit."
                    )
                    run.log("walk", "error", error="time limit", cost=asdict(cost))
                except Exception as exc:
                    # E.g. an embed that detached mid-read (post-round 1 fix 1):
                    # the checks that need the walk are left for review, the
                    # rest still run.
                    err = safe_error(exc)
                    report.errors.append(f"The keyboard walk failed: {err}")
                    run.log("walk", "error", error=err, cost=asdict(cost))
                if walk is not None:
                    ctx.plan = ReplayPlan.of(walk.p1, walk.p2)
                    # 2.C A2's walk cross-check: steps that never settled.
                    ctx.cache["walk_unsettled"] = sum(
                        st.unsettled for p in (walk.p1, walk.p2) for st in p.steps
                    )
                    run.write_json(run.evidence_dir / "walk.json", walk)
                    run.log("walk", **_walk_summary(walk), cost=asdict(cost))
                break
            track.close("walk")
            if walk is not None and any(_reveals(c) for c in checks):
                # Open every menu, tab and section the walk found, once, for
                # the tests that read opened content (fix 9b, reveal.py).
                await track.reading("Opening menus and expandable sections")
                try:
                    with metered() as cost:
                        rv = await _bounded(
                            reveal.collect(ctx, walk, _walk_extras(checks)),
                            hard + allowance[0],
                        )
                    ctx.cache["reveal"] = rv
                    report.reveal = rv.summary()
                    run.write_json(run.evidence_dir / "reveal.json", rv)
                    run.log(
                        "reveal",
                        triggers=report.reveal["triggers"],
                        opened=report.reveal["opened"],
                        cost=asdict(cost),
                    )
                except Exception as exc:
                    # Nothing known about what opens: a guard then keeps a
                    # PASS from standing (principle 3).
                    err = (
                        "time limit"
                        if isinstance(exc, TimeoutError)
                        else safe_error(exc)
                    )
                    report.reveal = {"failed": True, "triggers": 0, "opened": 0}
                    report.errors.append(f"Opening menus and sections failed: {err}")
                    run.log("reveal", "error", error=err)
            # The page's inventory (count.py): taken at the walk's first load,
            # else on a load of its own, before the checks read it.
            track.close("reveal")
            if "count" not in ctx.cache:
                await track.reading("Taking an inventory of the page")
                try:
                    ctx.cache["count"] = await _bounded(_own_count(ctx), hard)
                except TimeoutError:
                    ctx.cache["count"] = Count(where="own load", error="time limit")
            count = ctx.cache["count"]
            track.close("inventory")
            if (
                not count.error
                and count.openers > 0
                and count.hidden_field_paths
                and any(c.test_id in HIDDEN_FIELD_TESTS for c in checks)
            ):
                # Hidden fields nothing a careful tester does shows (hidden.py;
                # guard CN; Abby, 2026-11-15).
                await track.reading("Checking which hidden fields can ever be shown")
                hc = await hidden.bounded(
                    ctx, count.hidden_field_paths, ctx.cache.get("reveal"), hard
                )
                count.hidden_never_shown = hc.never_shown
                count.hidden_check = hc.why_not or (
                    f"{len(hc.never_shown)} of {len(count.hidden_field_paths)} "
                    f"never shown ({hc.seconds:g} s)"
                )
                run.write_json(run.evidence_dir / "hidden.json", hc)
                run.log("hidden", never_shown=len(hc.never_shown), why_not=hc.why_not)
            report.counts["page"] = ctx.cache["count"]
            run.write_json(run.evidence_dir / "count.json", ctx.cache["count"])
            # The count is over this run's tests, skipped ones included, so it
            # never jumps back; the bar moves from stage 2 to 3 through them.
            track.tests_total = len(checks)
            for n, c in enumerate(checks, 1):
                if pages_cut and uses_pages(c):
                    continue  # NEEDS REVIEW, not performed: pages_cut says why
                if needs_walk(c, ctx) and walk is None:
                    continue  # NEEDS REVIEW: the run did not complete (errors say why)
                await track.testing(n - 1, len(checks), f"Checking {c.test_id.value}")
                # The test's own time, inside the run limit: its
                # budget or a share of what is left, whichever is smaller. It
                # stops starting work a little before (ctx.out_of_time) and is
                # cancelled at the end.
                tid = c.test_id.value
                t0 = time.monotonic()
                limit = hard + allowance[0]
                own_s = time_for(settings, tid, limit - t0)
                own = t0 + own_s
                ctx.test_deadline = own - min(BUDGET_GRACE_S, own_s / 6)
                times = report.test_times[tid] = TestTime(
                    budget_s=budget_s(settings, tid), limit_s=round(own_s, 1)
                )
                try:
                    with metered() as cost:
                        state = await _abandoned_at(
                            c.collect(ctx, walk), min(limit, own), run.log, tid
                        )
                except TimeoutError:
                    if own < limit:
                        ran_out[c.test_id] = out_of_budget_reason(own_s)
                        times.ran_out = True
                        msg = f"ran out of its time ({own_s:.0f} s)"
                    else:
                        msg = "the run reached its time limit before this test finished"
                    run.log("check_error", "error", test=tid, error=msg)
                    report.errors.append(f"{tid}: {msg}")
                    continue
                except Exception as exc:
                    err = safe_error(exc)
                    run.log("check_error", "error", test=tid, error=err)
                    report.errors.append(f"{tid}: {err}")
                    continue
                finally:
                    if time.monotonic() > ctx.test_deadline:
                        times.ran_out = True  # stopped early, or cancelled
                    ctx.test_deadline = math.inf
                    times.seconds = round(time.monotonic() - t0, 1)
                states[c.test_id] = state
                run.write_json(run.evidence_dir / evidence_name(c.test_id), state)
                run.log("collected", test=c.test_id.value, cost=asdict(cost))
            # Other pages' inventories, taken on the site read's loads.
            site = ctx.cache.get("site")
            for pr in site.others if site is not None else []:
                if pr.count is not None:
                    report.counts[f"p{pr.n}"] = pr.count
            # Media that played, from pass T's load (autoplay allowed there),
            # in place of the count's load where it is not (count.py).
            mp = ctx.cache.get("motion")
            if mp is not None and getattr(mp, "played", None) is not None:
                c = report.counts["page"]
                c.media_played, c.played_from = mp.played, "pass T"
                run.write_json(run.evidence_dir / "count.json", c)
            # Only when something was cut short: work that finished inside the
            # reserve needs no note.
            walk_cut = walk is not None and "time" in (walk.p1.end, walk.p2.end)
            hard_cut = any("time limit" in e for e in report.errors)
            if ctx.timed_out or walk_cut or hard_cut:
                report.errors.append(
                    TIME_NOTE.format(limit=_limit(settings, len(others)) + allowance[0])
                )
        except RunRefused:
            raise  # its folder is already removed
        except BaseException:
            # A tool error leaves no run folder (CLAUDE.md).
            shutil.rmtree(run.dir, ignore_errors=True)
            raise
        finally:
            if motion_task is not None and not motion_task.done():
                motion_task.cancel()
            for b in (browser, *extra_browsers.values()):
                await b.close()
    # No browser from here on: a queued run may start while this one is
    # evaluated and judged (code review B-04).
    jobs.release_browser_slot()

    try:
        await track.finishing(3, "Evaluating")
        report.findings = []
        _evaluate(run, report, states, {**skipped, **ran_out})
        result = await get_judge(settings.judge_backend).judge(report.open_questions)
        report.open_questions = result.pending
        report.finished_at = utcnow()
        report.follow_up_calls = follow_ups(report, states, skipped)
        run.write_json(run.report_path, report)
        pre_scrt = scrt.write_for_run(run.dir, run.report_path, report)
        if settings.judge_backend == "api":
            report, states = await _judge_phase(
                settings, run, report, states, track.finishing
            )
        run.log("run_end", status="error" if report.errors else "ok")
    except asyncio.CancelledError:
        # Cancelled while evaluating or judging (jobs.cancel): no folder is
        # kept, as for a run cancelled while it had a browser.
        shutil.rmtree(run.dir, ignore_errors=True)
        raise
    qview = _question_view(report.open_questions[:QUESTION_PAGE])
    calls = report.follow_up_calls
    result = RunResult(
        run_id=run.run_id,
        target=url,
        final_url=report.final_url,
        tests=report.tests,
        findings=[FindingView.of(f, report) for f in report.findings],
        open_questions=qview[0],
        question_texts=qview[1],
        page_text=_page_text(report, states),
        shared_inputs=_shared_inputs(report, states),
        walk=_walk_summary(walk) if walk else {},
        evidence=_evidence_uris(run),
        expires_at=expires_at(run.dir, settings.run_ttl_hours),
        report=report,
        report_uri=run_uri(run.run_id, run.rel(run.report_path)),
        pre_scrt_uri=run_uri(run.run_id, run.rel(pre_scrt)),
        errors=report.errors,
        next_step=next_step(report, calls),
        follow_up_calls=calls,
        work=Remaining.of(report).work,
        remaining=Remaining.of(report),
        todo=todo(report, calls),
        more_questions=max(0, len(report.open_questions) - QUESTION_PAGE),
    )
    return fit(result, report, states)


async def _judge_phase(
    settings: Settings, run: RunRecorder, report: Report, states, say
):
    """The server's own judge (apijudge.py) answers the switched-on question
    types of a finished run through answer_questions, then the result is
    built from the saved report. Nothing switched on: only the record."""
    from tobi508 import apijudge

    stats = None
    if settings.judge_types_set:
        try:
            stats = await apijudge.judge_run(settings, run.run_id, say=say)
        except Exception as exc:
            # A judge that fails leaves its questions to the calling agent.
            run.log("judge_error", "error", error=safe_error(exc))
    report = Report.model_validate_json(run.report_path.read_text("utf-8"))
    report.judge = apijudge.judge_record(settings, stats)
    run.write_json(run.report_path, report)
    return report, _load_states(run)


async def answer_questions(
    settings: Settings, run_id: str, answers: list[Answer]
) -> AnswerResult:
    """Record answers, apply them (pressing documented keys in the recorded
    page where a check needs it), and re-evaluate."""
    try:
        run = RunRecorder.open(settings.runs_dir, run_id)
    except FileNotFoundError as exc:
        raise RunRefused(str(exc)) from exc
    report = Report.model_validate_json(run.report_path.read_text("utf-8"))
    before = {f.test_id: (f.outcome, f.summary, f.note) for f in report.findings}
    from tobi508.inline import attached

    accepted, rejected = record_answers(report, answers, attached(run.dir))
    states = _load_states(run)
    errors: list[str] = []
    browser = _LazyBrowser(settings)
    try:
        no_limit = bool(report.versions.run_settings.get("no_time_limit"))
        ctx = _context(
            settings,
            run,
            browser.get,
            report.final_url or report.target,
            _soft_deadline(time.monotonic(), settings, no_limit),
            report.cross_site_frames,
        )
        ctx.no_time_limit = no_limit
        ctx.pages = _page_refs(browser.get, settings, run, report)
        walk_path = run.evidence_dir / "walk.json"
        if walk_path.exists():
            w = KeyboardWalk.model_validate_json(walk_path.read_text("utf-8"))
            ctx.plan = ReplayPlan.of(w.p1, w.p2)
        for t, state in states.items():
            try:
                errors += await REGISTRY[t].resume(ctx, state, report)
            except Exception as exc:
                errors.append(f"{t.value}: {safe_error(exc)}")
            run.write_json(run.evidence_dir / evidence_name(t), state)
    finally:
        await browser.close()
    _evaluate(run, report, states)
    # A test left out over a cap (no_time_limit) stays to do after answers.
    kept = [c for c in report.follow_up_calls if c.get("no_time_limit")]
    made = [
        {k: v for k, v in c.items() if k != "job_id"} for c in report.follow_ups_made
    ]
    report.follow_up_calls = [
        c for c in follow_ups(report, states, None) if c not in made
    ] + kept
    run.write_json(run.report_path, report)
    pre_scrt = scrt.write_for_run(run.dir, run.report_path, report)
    run.log(
        "answers_recorded",
        "error" if errors else "ok",
        accepted=accepted,
        rejected=rejected,
        errors=errors,
    )
    qview = _question_view(report.open_questions[:QUESTION_PAGE])
    calls = report.follow_up_calls
    # Only the findings this answer changed (agent follow-through plan,
    # change 2b): the rest were in earlier results and are in the report.
    changed = [
        f
        for f in report.findings
        if before.get(f.test_id) != (f.outcome, f.summary, f.note)
        or any(q.test_id == f.test_id for q in report.open_questions)
    ]
    result = AnswerResult(
        run_id=run_id,
        accepted=accepted,
        rejected=rejected,
        findings=[FindingView.of(f, report) for f in changed],
        unchanged=[f.test_id.value for f in report.findings if f not in changed],
        open_questions=qview[0],
        question_texts=qview[1],
        page_text=_page_text(report, states),
        shared_inputs=_shared_inputs(report, states),
        report=report,
        report_uri=run_uri(run.run_id, run.rel(run.report_path)),
        pre_scrt_uri=run_uri(run.run_id, run.rel(pre_scrt)),
        errors=errors,
        next_step=next_step(report, calls),
        follow_up_calls=calls,
        work=Remaining.of(report).work,
        remaining=Remaining.of(report),
        todo=todo(report, calls),
        more_questions=max(0, len(report.open_questions) - QUESTION_PAGE),
    )
    return fit(result, report, states)
