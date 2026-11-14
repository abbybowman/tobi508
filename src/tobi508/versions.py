"""Collect the versions recorded in every report."""

from __future__ import annotations

import asyncio
import platform
from importlib.metadata import version
from typing import Any

from playwright.async_api import Browser

from tobi508 import __version__
from tobi508.andi import provenance
from tobi508.browser import new_context
from tobi508.config import Settings
from tobi508.models import Versions
from tobi508.rules import spec_versions


def _judging_model(settings: Settings) -> str:
    """The model that answers open questions: with the api backend, the model
    asked for and the prompt's hash, so a report says which answered."""
    if settings.judge_backend != "api" or settings.judging_model != "none":
        return settings.judging_model
    from tobi508.apijudge import prompt_sha

    return f"server:{settings.judge_model} prompt:{prompt_sha()[:12]}"


def collect_versions(
    settings: Settings, browser: Browser | None, no_time_limit: bool = False
) -> Versions:
    prov = provenance(settings.third_party_dir)
    return Versions(
        tobi508=__version__,
        andi=f"{prov['andi']['version']} ({prov['andi']['commit'][:12]})",
        jquery=prov["jquery"]["version"],
        scrt=f"{prov['scrt']['version'].split(' ')[0]} ({prov['scrt']['commit'][:12]})",
        playwright=version("playwright"),
        browser_channel=settings.browser_channel,
        browser=browser.version if browser else None,
        os=platform.platform(),
        python=platform.python_version(),
        rules_spec=spec_versions(settings.rules_dir),
        judging_model=_judging_model(settings),
        display=configured_display(settings),
        test_budgets_s=_budgets(),
        run_settings={
            "settle_quiet_ms": settings.settle_quiet_ms,
            "record_scroll_passes": settings.record_scroll_passes,
            # Scrolled one window at a time while recording (lazy content).
            "record_scroll_steps": settings.record_scroll_steps,
            # The media store kept each player's chosen file first.
            "media_chosen_first": settings.media_chosen_first,
            "run_limit_s": settings.run_limit_s,
            "other_page_s": settings.other_page_s,
            # The caller turned the run limit off for this run (tobi_run_tt_tests).
            "no_time_limit": no_time_limit,
            # Pages' Content-Security-Policy ignored, so ANDI can run (config).
            "bypass_csp": settings.bypass_csp,
            # How long a load from the recording may take (config).
            "replay_navigation_timeout_ms": settings.replay_navigation_timeout_ms,
        },
    )


def _budgets() -> dict[str, int]:
    from tobi508.checks import REGISTRY
    from tobi508.checks.base import budget_s

    return {t.value: budget_s(t.value) for t in REGISTRY}


def configured_display(settings: Settings) -> dict[str, int | float | None]:
    return {
        "viewport_width": settings.viewport_width,
        "viewport_height": settings.viewport_height,
        "inner_width": None,
        "inner_height": None,
        "device_pixel_ratio": None,
    }


_DISPLAY_JS = "() => [innerWidth, innerHeight, devicePixelRatio]"


async def measure_display(
    settings: Settings, browser: Browser, timeout_s: float = 5.0
) -> dict[str, int | float | None]:
    """The configured viewport plus what a blank page in a fresh context of
    `browser` reports. No page is loaded (about:blank); on any failure the
    measured values stay None."""
    out = configured_display(settings)
    ctx: Any = None
    try:
        async with asyncio.timeout(timeout_s):
            ctx = await new_context(browser, settings)
            page = await ctx.new_page()
            w, h, dpr = await page.evaluate(_DISPLAY_JS)
            out.update(inner_width=int(w), inner_height=int(h))
            out["device_pixel_ratio"] = float(dpr)
    except Exception:
        pass
    finally:
        if ctx is not None:
            try:
                await asyncio.wait_for(ctx.close(), timeout_s)
            except Exception:
                pass
    return out
