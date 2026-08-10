#!/usr/bin/env python3
"""Turn a raw HTTP response into one of the verdicts in common.py.

This is the one place that decides "did we actually get the page, or did we
get a wall pretending to be one" — every tier calls this on its response
before deciding it succeeded. Getting this wrong means a tier reports OK on
a CAPTCHA page, which is the exact dishonesty the whole tool exists to avoid.
"""

from __future__ import annotations

import re

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


def _body_signature(html_lower: str, needles: list[str]) -> bool:
    return any(n in html_lower for n in needles)


def classify(status: int, html: str, headers: dict | None = None) -> str:
    """Classify a response. `headers` keys are expected lowercase.

    Order of checks: transport-level facts (status code, header hints) before
    body sniffing, since a 429 with a generic body should never be misread
    as WAF (which implies escalation might help — 429 means it won't).
    """
    headers = {k.lower(): v for k, v in (headers or {}).items()}
    html_lower = (html or "").lower()

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
    print("classify.py: all self-tests passed")
