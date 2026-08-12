#!/usr/bin/env python3
"""Turn a raw HTTP response into one of the verdicts in common.py.

This is the one place that decides "did we actually get the page, or did we
get a wall pretending to be one" — every tier calls this on its response
before deciding it succeeded. Getting this wrong means a tier reports OK on
a CAPTCHA page, which is the exact dishonesty the whole tool exists to avoid.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from common import (
    OK, WAF, RATELIMIT, CAPTCHA, LOGIN, PAYWALL, NOTFOUND, EMPTY, ERROR,
)

# Body-text signatures, lowercased substring match. Order matters: first hit wins.
# Keep signatures specific enough to not false-positive on normal pages that
# merely mention "sign in" in a nav link.
_CAPTCHA_SIGNS = [
    "cf-turnstile", "g-recaptcha", "hcaptcha", "verify you are human",
    "checking your browser before accessing", "cf-chl-", "captcha-delivery.com",
    "please verify you are a human", "attention required! | cloudflare",
]
_WAF_SIGNS = [
    "access denied", "request blocked", "perimeterx", "datadome",
    "akamai", "you have been blocked", "sorry, you have been blocked",
    "reference #", "incapsula",
]
_LOGIN_SIGNS = [
    "sign in to continue", "log in to continue", "please log in",
    "login required", "you must be logged in", "create an account to continue",
    "sign up to see", "join to view", "session expired",
]
_PAYWALL_SIGNS = [
    "subscribe to continue reading", "subscribe to read", "become a member",
    "this content is for subscribers", "paywall", "unlock this article",
    "start your free trial",
]
_EMPTY_SIGNS = [
    "enable javascript to run this app", "you need to enable javascript",
    "please enable javascript",
]

# _LOGIN_SIGNS above is body-text and English-only, so it misses a login page
# in any other language — confirmed 2026-08-12: fetching an Instagram URL
# that requires auth landed on https://www.instagram.com/accounts/login/,
# body entirely German ("Bei Instagram anmelden", "Passwort", "Anmelden"),
# matched none of the phrases above, and the page's ~200 visible chars
# cleared the EMPTY threshold — so it classified as OK. A login page is a
# login page regardless of what language it's rendered in, but the URL path
# convention for "this is the login page" is far more stable across sites
# and locales than any wording. Path segments only (never the query string,
# so a `?next=/real/page` redirect target can't itself trigger this), word
# boundaries so this doesn't fire on an unrelated path that merely contains
# "login" as a substring (e.g. "/blog/how-to-login-to-aws").
_LOGIN_URL_SIGNS = re.compile(
    r"/(login|log-in|signin|sign-in|sign_in|authenticate|session/new|users/sign_in)(/|$|\?|#)",
    re.IGNORECASE,
)


def _is_login_url(url: str | None) -> bool:
    if not url:
        return False
    return bool(_LOGIN_URL_SIGNS.search(urlparse(url).path))


def _body_signature(html_lower: str, needles: list[str]) -> bool:
    return any(n in html_lower for n in needles)


def classify(status: int, html: str, headers: dict | None = None, final_url: str | None = None) -> str:
    """Classify a response. `headers` keys are expected lowercase.

    `final_url` is the URL actually reached after redirects (not the one
    requested) — pass it whenever the caller has it. It is what lets a
    login page in an untranslated body signature list still be caught: see
    _LOGIN_URL_SIGNS above.

    Order of checks: transport-level facts (status code, header hints, then
    the redirect-target URL) before body sniffing, since a 429 with a
    generic body should never be misread as WAF (which implies escalation
    might help — 429 means it won't), and a redirect straight to a login
    path is unambiguous regardless of what the body says.
    """
    headers = {k.lower(): v for k, v in (headers or {}).items()}
    html_lower = (html or "").lower()

    if status and 200 <= status < 400 and _is_login_url(final_url):
        return LOGIN

    if status == 429:
        return RATELIMIT
    if status in (401,):
        return LOGIN
    if status == 402:
        return PAYWALL
    if status in (404, 410):
        return NOTFOUND
    if status in (403, 503):
        # Ambiguous by status alone — Cloudflare and friends reuse 403/503
        # for CAPTCHA, WAF, and rate-limit alike. Body sniffing decides.
        if _body_signature(html_lower, _CAPTCHA_SIGNS):
            return CAPTCHA
        if "retry-after" in headers:
            return RATELIMIT
        if _body_signature(html_lower, _WAF_SIGNS) or status == 403:
            return WAF
        return WAF

    if status and status >= 500:
        return ERROR

    if status and 200 <= status < 300:
        if _body_signature(html_lower, _CAPTCHA_SIGNS):
            return CAPTCHA
        if _body_signature(html_lower, _PAYWALL_SIGNS):
            return PAYWALL
        if _body_signature(html_lower, _LOGIN_SIGNS):
            return LOGIN
        if _body_signature(html_lower, _WAF_SIGNS):
            return WAF
        # Client-rendered shell: script/style bodies must not count as
        # "visible" text, or a JS-heavy SPA with 800KB of embedded JS but
        # zero rendered content (e.g. Instagram's splash-screen HTML) reads
        # as a full page by character count alone. Strip their content, not
        # just the tags, before measuring what a human would actually see.
        # Confirmed against a real Instagram response 2026-08-06.
        no_scripts = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", html or "",
                             flags=re.IGNORECASE | re.DOTALL)
        visible_len = len(re.sub(r"<[^>]+>", " ", no_scripts).strip())
        if visible_len < 200 and _body_signature(html_lower, _EMPTY_SIGNS):
            return EMPTY
        if visible_len < 150:
            return EMPTY
        return OK

    return ERROR


if __name__ == "__main__":
    # Minimal self-test — no network needed.
    assert classify(429, "") == RATELIMIT
    assert classify(401, "") == LOGIN
    assert classify(402, "") == PAYWALL
    assert classify(404, "") == NOTFOUND
    assert classify(403, "<html>Please verify you are a human</html>") == CAPTCHA
    assert classify(403, "<html>Access Denied by WAF</html>") == WAF
    assert classify(200, "<html><body>" + "x" * 500 + "</body></html>") == OK
    assert classify(200, "<html><body>Please sign in to continue reading</body></html>") == LOGIN
    assert classify(200, "<div id='root'></div><noscript>enable javascript to run this app</noscript>") == EMPTY
    # Regression test: a JS-heavy SPA shell with a large inline <script> but
    # no real rendered content must be EMPTY, not OK — script/style body
    # text must never count as "visible" (the Instagram splash-page bug).
    spa_shell = (
        "<html><body><div id='splash'></div>"
        "<script>" + ("var x = " + str(1) + ";\n") * 400 + "</script>"
        "</body></html>"
    )
    assert classify(200, spa_shell) == EMPTY, "script content must not count as visible text"

    # Regression test: a login page in a language none of _LOGIN_SIGNS cover
    # must still classify as LOGIN, via the redirect-target URL rather than
    # body text. Reproduces the real German Instagram login page verbatim
    # (2026-08-12) — this exact body previously classified as OK.
    instagram_login_body = (
        "<html><body>Sei dabei, wenn deine engen Freunde ganz alltägliche "
        "Momente erleben. Bei Instagram anmelden. Handynummer, Benutzername "
        "oder E-Mail-Adresse. Passwort. Anmelden. Passwort vergessen? "
        "Mit Facebook anmelden. Neues Konto erstellen</body></html>"
    )
    assert classify(200, instagram_login_body) == OK, (
        "sanity check: without a final_url this body has no signal to catch it on — "
        "confirms the URL check, not the body, is what fixes this case below"
    )
    assert classify(
        200, instagram_login_body,
        final_url="https://www.instagram.com/accounts/login/?next=%2Faccounts%2Fedit%2F",
    ) == LOGIN, "a foreign-language login page must be caught via the redirect URL, not just body text"
    # Same URL check must not false-positive on an unrelated path that merely
    # contains "login" as a substring rather than a real path segment.
    assert classify(
        200, "<html><body>" + "x" * 500 + "</body></html>",
        final_url="https://example.com/blog/how-to-login-to-aws",
    ) == OK, "a substring match on an unrelated path must not trigger LOGIN"

    print("classify.py: all self-tests passed")
