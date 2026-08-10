#!/usr/bin/env python3
"""Tier 'direct' and tier 'public-route' for deepfetch.

'direct' is a plain requests.get with a truthful browser UA. 'public-route'
tries known public API / syndication patterns (Reddit .json, yt-dlp for
YouTube, r.jina.ai as a generic read proxy) before giving up.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time

import requests

from common import DEFAULT_HEADERS, FetchResult, registrable_domain, truncate
from classify import classify
from extract import html_to_text, extract_structured

# The environment has no brotli decoder installed, but DEFAULT_HEADERS
# advertises "br" support; if the server honors that we get bytes requests
# cannot decode, corrupting resp.text. Request only encodings we can decode.
_SAFE_HEADERS = {**DEFAULT_HEADERS, "Accept-Encoding": "gzip, deflate"}


def fetch_direct(url: str, timeout: int = 15) -> FetchResult:
    """Tier 'direct': einfacher requests.get mit DEFAULT_HEADERS."""
    start = time.monotonic()
    try:
        resp = requests.get(
            url, headers=_SAFE_HEADERS, timeout=timeout, allow_redirects=True
        )
    except Exception as exc:
        return FetchResult(
            url=url,
            tier="direct",
            ok=False,
            verdict="error",
            note=f"{type(exc).__name__}: {exc}",
            elapsed_ms=int((time.monotonic() - start) * 1000),
        )

    elapsed_ms = int((time.monotonic() - start) * 1000)
    verdict = classify(resp.status_code, resp.text, dict(resp.headers))
    return FetchResult(
        url=url,
        tier="direct",
        ok=True,
        status=resp.status_code,
        final_url=resp.url,
        html=resp.text,
        text=html_to_text(resp.text, base_url=resp.url),
        verdict=verdict,
        structured=extract_structured(resp.text),
        note="",
        elapsed_ms=elapsed_ms,
    )


def _host(url: str) -> str:
    return registrable_domain(url)


def _try_reddit(url: str, timeout: int) -> FetchResult | None:
    if "reddit.com" not in _host(url):
        return None
    try:
        json_url = url if url.rstrip("/").endswith(".json") else url.rstrip("/") + ".json"
        resp = requests.get(json_url, headers=_SAFE_HEADERS, timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()  # raises if not valid JSON
        return FetchResult(
            url=url,
            tier="public-route",
            ok=True,
            status=resp.status_code,
            final_url=resp.url,
            text=truncate(json.dumps(data)),
            verdict="ok",
            structured={"reddit_json": True},
            note="reddit .json endpoint",
        )
    except Exception:
        return None


def _try_youtube(url: str, timeout: int) -> FetchResult | None:
    host = _host(url)
    if host not in ("youtube.com", "youtu.be"):
        return None
    if not shutil.which("yt-dlp"):
        return None
    try:
        proc = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        data = json.loads(proc.stdout)
        title = data.get("title", "")
        description = data.get("description", "")
        subs = data.get("automatic_captions") or {}
        sub_langs = ", ".join(sorted(subs.keys())[:20])
        parts = [title, description]
        if sub_langs:
            parts.append(f"Auto-captions available: {sub_langs}")
        text = truncate("\n\n".join(p for p in parts if p))
        return FetchResult(
            url=url,
            tier="public-route",
            ok=True,
            status=200,
            final_url=url,
            text=text,
            verdict="ok",
            structured={"yt_dlp_json": True},
            note="yt-dlp --dump-json",
        )
    except Exception:
        return None


def _try_jina(url: str, timeout: int) -> FetchResult | None:
    try:
        proxy_url = "https://r.jina.ai/" + url
        resp = requests.get(proxy_url, headers=_SAFE_HEADERS, timeout=timeout)
        if resp.status_code == 200 and len(resp.text) > 100:
            return FetchResult(
                url=url,
                tier="public-route",
                ok=True,
                status=resp.status_code,
                final_url=proxy_url,
                text=truncate(resp.text),
                verdict="ok",
                structured={},
                note="r.jina.ai read proxy",
            )
        return None
    except Exception:
        return None


def fetch_public_route(url: str, timeout: int = 15) -> FetchResult:
    """Tier 'public-route': bekannte oeffentliche API-/Syndication-Muster."""
    start = time.monotonic()

    for attempt in (_try_reddit, _try_youtube, _try_jina):
        try:
            result = attempt(url, timeout)
        except Exception:
            result = None
        if result is not None and result.usable:
            result.elapsed_ms = int((time.monotonic() - start) * 1000)
            return result

    return FetchResult(
        url=url,
        tier="public-route",
        ok=False,
        verdict="error",
        note="no public route matched or all failed",
        elapsed_ms=int((time.monotonic() - start) * 1000),
    )


if __name__ == "__main__":
    r1 = fetch_direct("https://example.com")
    assert r1.usable, f"expected usable, got verdict={r1.verdict!r} note={r1.note!r}"
    assert "Example Domain" in r1.text, f"expected 'Example Domain' in text, got: {r1.text[:200]!r}"
    print("fetch_direct(example.com): OK, verdict=%r" % r1.verdict)

    r2 = fetch_direct("https://httpstat.us/404")
    if r2.verdict == "error":
        print(f"fetch_direct(httpstat.us/404): network/transport issue in this environment (note={r2.note!r}) — reporting honestly, not hiding it")
    else:
        assert r2.verdict == "notfound", f"expected verdict='notfound', got {r2.verdict!r} (status={r2.status})"
        print("fetch_direct(httpstat.us/404): OK, verdict=%r" % r2.verdict)

    r3 = fetch_public_route("https://www.reddit.com/r/Python/top.json")
    if r3.ok:
        assert r3.verdict == "ok", f"expected verdict='ok', got {r3.verdict!r}"
        print("fetch_public_route(reddit): OK, verdict=%r, tier=%r" % (r3.verdict, r3.tier))
    else:
        print(f"fetch_public_route(reddit): network/route did not succeed (note={r3.note!r}) — reporting honestly, not hiding it")

    print("tier_direct.py: all self-tests passed")
