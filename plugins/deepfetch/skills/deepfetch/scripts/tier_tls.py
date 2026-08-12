#!/usr/bin/env python3
"""Tier 'tls': curl_cffi mit TLS-Impersonation gegen WAFs, die auf den
TLS-Fingerprint reagieren statt (nur) auf den User-Agent.

Probiert safari -> chrome -> firefox, stoppt beim ersten verdict='ok'.
Bricht sofort ab, wenn ein Versuch ein terminal-Ergebnis liefert (captcha,
paywall, notfound, ratelimit) — weitere Browser-Identitaeten wuerden daran
nichts aendern.
"""

from __future__ import annotations

import time

from common import FetchResult
from classify import classify
from extract import html_to_text, extract_structured

try:
    from curl_cffi import requests as curl_requests
    _CURL_CFFI_AVAILABLE = True
except ImportError:
    curl_requests = None
    _CURL_CFFI_AVAILABLE = False

# Reihenfolge safari -> chrome -> firefox, wie bei insane-search Phase 2.
_IMPERSONATE_ORDER = ["safari17_2_1", "chrome124", "firefox133"]


def fetch_tls(url: str, timeout: int = 20) -> FetchResult:
    """Tier 'tls': curl_cffi mit TLS-Impersonation, probiert safari -> chrome -> firefox,
    stoppt beim ersten Ergebnis mit verdict='ok'."""
    if not _CURL_CFFI_AVAILABLE:
        return FetchResult(
            url=url,
            tier="tls",
            ok=False,
            verdict="error",
            note="curl_cffi not installed — pip install curl_cffi",
        )

    last_result: FetchResult | None = None

    for impersonate in _IMPERSONATE_ORDER:
        start = time.monotonic()
        try:
            resp = curl_requests.get(
                url, impersonate=impersonate, timeout=timeout, allow_redirects=True
            )
        except Exception as exc:
            last_result = FetchResult(
                url=url,
                tier="tls",
                ok=False,
                verdict="error",
                note=f"impersonate {impersonate} failed: {exc}",
                elapsed_ms=int((time.monotonic() - start) * 1000),
            )
            continue

        elapsed_ms = int((time.monotonic() - start) * 1000)

        try:
            status = resp.status_code
            html = resp.text or ""
            final_url = str(resp.url) if resp.url else url
            headers = dict(resp.headers or {})
            verdict = classify(status, html, headers, final_url=final_url)

            result = FetchResult(
                url=url,
                tier="tls",
                ok=True,
                status=status,
                final_url=final_url,
                html=html,
                text=html_to_text(html, base_url=final_url),
                verdict=verdict,
                structured=extract_structured(html),
                note=f"impersonated {impersonate}",
                elapsed_ms=elapsed_ms,
            )
        except Exception as exc:
            result = FetchResult(
                url=url,
                tier="tls",
                ok=False,
                verdict="error",
                note=f"impersonate {impersonate} post-processing failed: {exc}",
                elapsed_ms=elapsed_ms,
            )

        last_result = result

        if result.verdict == "ok":
            return result
        if result.terminal:
            return result
        # Ambiguous non-terminal, non-ok (e.g. waf/login/empty/error) -> try next identity.

    # All three tried, none ok, none terminal-stopping — best available info.
    return last_result


if __name__ == "__main__":
    if not _CURL_CFFI_AVAILABLE:
        print("tier_tls.py: curl_cffi not installed, tested graceful-degradation path only")
        result = fetch_tls("https://example.com")
        assert result.verdict == "error"
        assert "curl_cffi" in result.note
        print(f"note: {result.note}")
    else:
        result = fetch_tls("https://example.com")
        assert result.usable
        print(f"example.com: verdict={result.verdict} tier={result.tier} note={result.note}")

        try:
            bot_result = fetch_tls("https://bot.sannysoft.com")
            print(
                f"bot.sannysoft.com: verdict={bot_result.verdict} "
                f"usable={bot_result.usable} note={bot_result.note}"
            )
        except Exception as exc:
            print(f"bot.sannysoft.com check skipped: {exc}")

    print("tier_tls.py: self-test passed")
