#!/usr/bin/env python3
"""Tier 'cookies' — the tier neither insane-search nor playwright-bot-bypass has.

Both reference tools explicitly refuse to touch login walls (insane-search
reports "authentication required" and stops; playwright-bot-bypass's own
README lists Instagram/Facebook/LinkedIn under "doesn't touch"). This tier
exists specifically for that gap: reuse the user's own already-authenticated
browser session to read a page they can already see in their own browser.

This is not a bypass of anyone's access control — it is the same access the
user already has, read programmatically instead of by hand. That is also
exactly why it needs its own permission gate: it must never fire silently.

Design rules (do not relax these without re-reading the reasoning):
- OFF by default. The scheduler only calls this tier when the caller passes
  allow_cookies=True *and* the domain is present in the on-disk allowlist,
  or the caller explicitly passes a one-off confirmation for this run.
- Cookies are scoped to registrable_domain(url) and never sent to a
  different domain, even if the browser jar contains them for the same
  parent domain under a different subdomain policy than expected.
- Cookie values are never written to a log, a FetchResult.note, stdout, or
  any file other than a short-lived temp cookie jar that is deleted before
  the function returns (finally-block, not best-effort).
- No password, token, or credential is ever read, entered, or generated
  here — only the cookie jar the browser already has from the user's own
  prior, manual login.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from http.cookiejar import MozillaCookieJar
from pathlib import Path

import requests

from common import FetchResult, DEFAULT_HEADERS, registrable_domain, truncate
from classify import classify
from extract import html_to_text, extract_structured

CONFIG_DIR = Path(os.environ.get("DEEPFETCH_HOME", Path.home() / ".config" / "deepfetch"))
ALLOWLIST_FILE = CONFIG_DIR / "cookie_domains.txt"

# Tried in this order — Firefox first because yt-dlp's extraction path for it
# doesn't need the browser closed, which makes for a smoother first run.
BROWSER_ORDER = ["firefox", "chrome", "edge", "brave", "chromium"]


def load_allowlist() -> set[str]:
    """Domains the user has explicitly approved for cookie reuse. One per line."""
    if not ALLOWLIST_FILE.exists():
        return set()
    lines = ALLOWLIST_FILE.read_text(encoding="utf-8").splitlines()
    return {ln.strip().lower() for ln in lines if ln.strip() and not ln.startswith("#")}


def add_to_allowlist(domain: str) -> None:
    """Persist consent for a domain so future runs don't need to ask again."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    domain = registrable_domain(domain) if "//" in domain else domain.lower()
    existing = load_allowlist()
    if domain in existing:
        return
    with ALLOWLIST_FILE.open("a", encoding="utf-8") as f:
        f.write(domain + "\n")
    try:
        os.chmod(ALLOWLIST_FILE, 0o600)
    except OSError:
        pass  # best-effort on platforms without POSIX perms (Windows)


def is_domain_allowed(url: str) -> bool:
    return registrable_domain(url) in load_allowlist()


def _export_cookies_via_ytdlp(domain: str, browser: str, jar_path: Path) -> bool:
    """Ask yt-dlp to dump this browser's cookie jar to a Netscape-format file.

    yt-dlp needs a URL to attach the export to; it doesn't need that URL to
    succeed or even be fetched — --skip-download plus --simulate means it
    only touches the network long enough to resolve, and often not even
    that. We point it at the target domain itself so cookie scoping lines up
    with what a real navigation would send.
    """
    if not shutil.which("yt-dlp"):
        return False
    try:
        proc = subprocess.run(
            [
                "yt-dlp",
                "--cookies-from-browser", browser,
                "--cookies", str(jar_path),
                "--skip-download",
                "--simulate",
                "--quiet",
                "--no-warnings",
                f"https://{domain}/",
            ],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    # yt-dlp often "fails" to extract a video from a non-video URL — that's
    # fine and expected. What matters is whether it wrote a non-empty jar.
    return jar_path.exists() and jar_path.stat().st_size > 0


def _load_jar_for_domain(jar_path: Path, domain: str) -> dict[str, str]:
    """Read only the cookies scoped to `domain` out of a Netscape cookie jar."""
    jar = MozillaCookieJar(str(jar_path))
    try:
        jar.load(ignore_discard=True, ignore_expires=True)
    except OSError:
        return {}
    out: dict[str, str] = {}
    for c in jar:
        cookie_domain = c.domain.lstrip(".").lower()
        if cookie_domain == domain or domain.endswith("." + cookie_domain):
            out[c.name] = c.value
    return out


def get_cookies_for_domain(url: str, browser: str | None = None) -> dict[str, str]:
    """Best-effort cookie extraction for one domain. Never raises.

    Returns {} if nothing could be extracted — callers must treat that as
    "no session available", not as an error worth surfacing loudly; the user
    may simply not be logged into that site in that browser.
    """
    domain = registrable_domain(url)
    browsers = [browser] if browser else BROWSER_ORDER

    with tempfile.TemporaryDirectory(prefix="deepfetch-cookies-") as tmpdir:
        jar_path = Path(tmpdir) / "cookies.txt"
        try:
            for b in browsers:
                try:
                    jar_path.unlink(missing_ok=True)
                    if _export_cookies_via_ytdlp(domain, b, jar_path):
                        cookies = _load_jar_for_domain(jar_path, domain)
                        if cookies:
                            return cookies
                except Exception:
                    continue  # try the next browser; never let one failure abort all
            return {}
        finally:
            jar_path.unlink(missing_ok=True)  # belt-and-suspenders; TemporaryDirectory also wipes it


def fetch_with_cookies(
    url: str,
    timeout: int = 15,
    browser: str | None = None,
    allow_cookies: bool = False,
) -> FetchResult:
    """Tier 'cookies': fetch `url` using the user's own browser session.

    Refuses to run unless `allow_cookies=True` AND the domain is on the
    on-disk allowlist — this function is the enforcement point, not just the
    scheduler, so a misconfigured caller can't accidentally leak a session
    to a domain the user never approved.
    """
    domain = registrable_domain(url)

    if not allow_cookies:
        return FetchResult(
            url=url, tier="cookies", ok=False, verdict="login",
            note="cookie tier disabled for this call (allow_cookies=False) — "
                 "ask the user before enabling it for a login-walled page",
        )
    if not is_domain_allowed(url):
        return FetchResult(
            url=url, tier="cookies", ok=False, verdict="login",
            note=f"'{domain}' is not in the cookie allowlist — ask the user to "
                 f"confirm, then call add_to_allowlist('{domain}') before retrying",
        )

    t0 = time.monotonic()
    cookies = get_cookies_for_domain(url, browser=browser)
    if not cookies:
        return FetchResult(
            url=url, tier="cookies", ok=False, verdict="login",
            note=f"no browser session found for '{domain}' — user may not be "
                 f"logged in, or logged in on a browser not in {BROWSER_ORDER}",
            elapsed_ms=int((time.monotonic() - t0) * 1000),
        )

    headers = dict(DEFAULT_HEADERS)
    try:
        resp = requests.get(
            url, headers=headers, cookies=cookies, timeout=timeout, allow_redirects=True,
        )
    except requests.RequestException as exc:
        return FetchResult(
            url=url, tier="cookies", ok=False, verdict="error",
            note=f"request failed even with cookies: {exc}",
            used_cookies=True,
            elapsed_ms=int((time.monotonic() - t0) * 1000),
        )

    elapsed = int((time.monotonic() - t0) * 1000)
    verdict = classify(resp.status_code, resp.text, dict(resp.headers), final_url=resp.url)
    text = html_to_text(resp.text, base_url=url) if resp.text else ""
    structured = extract_structured(resp.text) if resp.text else {}

    return FetchResult(
        url=url, tier="cookies", ok=resp.ok, status=resp.status_code,
        final_url=resp.url, text=truncate(text), verdict=verdict,
        structured=structured, used_cookies=True, elapsed_ms=elapsed,
        note="authenticated via reused browser session"
             if verdict == "ok" else "had cookies, still did not get through",
    )


if __name__ == "__main__":
    # No-network self-tests: allowlist plumbing and the permission gate.
    # Module-level (not inside a function), so plain assignment already
    # rebinds the globals used by load_allowlist()/add_to_allowlist() below
    # — no `global` keyword, no reload tricks needed at this scope.
    import shutil as _sh

    test_home = Path(tempfile.mkdtemp(prefix="deepfetch-test-"))
    CONFIG_DIR = test_home
    ALLOWLIST_FILE = CONFIG_DIR / "cookie_domains.txt"

    try:
        assert load_allowlist() == set(), "fresh allowlist must be empty"
        assert not is_domain_allowed("https://example.com/page"), \
            "unapproved domain must not be allowed"

        add_to_allowlist("https://example.com/some/path")
        assert is_domain_allowed("https://example.com/x"), \
            "domain added via URL must be recognized for another URL on same domain"
        assert not is_domain_allowed("https://other.com"), \
            "adding one domain must not allow a different one"

        r = fetch_with_cookies("https://example.com", allow_cookies=False)
        assert r.verdict == "login" and not r.ok, "must refuse when allow_cookies=False"

        add_to_allowlist("nottallowed-check.example")  # unrelated add, sanity check name shape
        r2 = fetch_with_cookies("https://not-on-allowlist.example", allow_cookies=True)
        assert r2.verdict == "login" and not r2.ok, \
            "must refuse when domain is not on the allowlist even if allow_cookies=True"

        print("tier_cookies.py: all self-tests passed (no-network permission-gate checks)")
    finally:
        _sh.rmtree(test_home, ignore_errors=True)
