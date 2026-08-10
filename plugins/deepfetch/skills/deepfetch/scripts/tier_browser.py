#!/usr/bin/env python3
"""Tier 'browser' — real headless or headed Chrome via Playwright.

The heaviest tier: used only after cheaper tiers (direct, tls, cookies) have
failed. Playwright may not even be installed in this environment, and even
if it is, the Chromium binary it needs may be missing — both are expected,
recoverable states, not bugs, so this module must never crash on them.
"""

from __future__ import annotations

import time

from common import FetchResult, truncate
from classify import classify
from extract import html_to_text, extract_structured

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)


def _run_once(url: str, timeout: int, cookies: list[dict] | None, headed: bool) -> FetchResult:
    """One browser launch + navigation attempt. Never raises — always returns a FetchResult."""
    t0 = time.monotonic()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return FetchResult(
            url=url, tier="browser", ok=False, verdict="error",
            note="playwright not installed — pip install playwright && playwright install chromium",
            elapsed_ms=int((time.monotonic() - t0) * 1000),
        )

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(
                    headless=not headed,
                    args=["--disable-blink-features=AutomationControlled"],
                )
            except Exception as exc:
                msg = str(exc)
                if "Executable doesn't exist" in msg or "playwright install" in msg:
                    return FetchResult(
                        url=url, tier="browser", ok=False, verdict="error",
                        note="playwright installed but browser binary missing — "
                             "run: playwright install chromium",
                        elapsed_ms=int((time.monotonic() - t0) * 1000),
                    )
                return FetchResult(
                    url=url, tier="browser", ok=False, verdict="error",
                    note=f"failed to launch browser: {exc}",
                    elapsed_ms=int((time.monotonic() - t0) * 1000),
                )

            context = None
            try:
                context = browser.new_context(
                    user_agent=DEFAULT_UA,
                    viewport={"width": 1920, "height": 1080},
                    locale="de-DE",
                    timezone_id="Europe/Vienna",
                )
                context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

                used_cookies = False
                if cookies:
                    context.add_cookies(cookies)
                    used_cookies = True

                page = context.new_page()
                try:
                    resp = page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
                except Exception:
                    try:
                        resp = page.goto(url, timeout=timeout * 1000, wait_until="load")
                    except Exception as exc:
                        return FetchResult(
                            url=url, tier="browser", ok=False, verdict="error",
                            note=f"navigation failed ({'headed' if headed else 'headless'}"
                                 f"{', cookies injected' if used_cookies else ''}): {exc}",
                            used_cookies=used_cookies,
                            elapsed_ms=int((time.monotonic() - t0) * 1000),
                        )

                status = resp.status if resp is not None else None
                final_url = page.url
                html = page.content()

                elapsed = int((time.monotonic() - t0) * 1000)
                verdict = classify(status or 200, html, {})
                text = html_to_text(html, base_url=url) if html else ""
                structured = extract_structured(html) if html else {}

                mode = "headed" if headed else "headless"
                note = f"rendered via real Chrome ({mode})"
                if used_cookies:
                    note += ", cookies injected"
                if verdict != "ok":
                    note += " — still did not get through"

                return FetchResult(
                    url=url, tier="browser", ok=(status is None or status < 400),
                    status=status, final_url=final_url, html=html,
                    text=truncate(text), verdict=verdict, structured=structured,
                    used_cookies=used_cookies, note=note, elapsed_ms=elapsed,
                )
            finally:
                try:
                    if context is not None:
                        context.close()
                finally:
                    browser.close()
    except Exception as exc:
        return FetchResult(
            url=url, tier="browser", ok=False, verdict="error",
            note=f"unexpected browser-tier failure: {exc}",
            elapsed_ms=int((time.monotonic() - t0) * 1000),
        )


def fetch_browser(
    url: str,
    timeout: int = 30,
    cookies: list[dict] | None = None,
    headed: bool = False,
) -> FetchResult:
    """Tier 'browser': echter Headless- oder Headed-Chrome via Playwright.

    `cookies`: optionale Liste von Playwright-Cookie-Dicts (Format:
    [{"name": ..., "value": ..., "domain": ..., "path": "/"}, ...]) —
    wird VOR der Navigation in den Browser-Context injiziert, damit eine
    zuvor mit Cookies authentifizierte Seite (Tier 'cookies') jetzt mit
    echtem JS-Rendering nachgeladen werden kann.

    `headed=False` -> headless zuerst (Standard). `headed=True` -> erzwingt
    sichtbares Fenster (manche Anti-Bot-Systeme flaggen speziell Headless).
    """
    result = _run_once(url, timeout, cookies, headed)

    # Escalate exactly once: only when caller started headless (default),
    # and the result is worth retrying with a visible window.
    if not headed and not result.terminal and result.verdict != "ok":
        headed_result = _run_once(url, timeout, cookies, True)
        return headed_result

    return result


if __name__ == "__main__":
    try:
        import playwright  # noqa: F401
        _HAS_PLAYWRIGHT = True
    except ImportError:
        _HAS_PLAYWRIGHT = False

    if not _HAS_PLAYWRIGHT:
        print("tier_browser.py: playwright not installed, tested graceful-degradation path only")
        result = fetch_browser("https://example.com")
        assert result.verdict == "error", result.verdict
        assert "playwright" in result.note.lower(), result.note
        print(f"tier_browser.py: self-test passed ({result.note})")
    else:
        # Might still be missing the Chromium binary, or fully working.
        result = fetch_browser("https://example.com")
        if result.verdict == "error" and (
            "binary" in result.note.lower() or "install" in result.note.lower()
        ):
            print("tier_browser.py: playwright installed but browser binary missing, "
                  "tested graceful-degradation path only")
            print(f"tier_browser.py: self-test passed ({result.note})")
        else:
            assert result.usable, result.note
            assert "Example Domain" in result.text, result.text
            print("tier_browser.py: all self-tests passed (full browser fetch succeeded)")
