#!/usr/bin/env python3
"""Shared contract for every deepfetch tier.

Every tier is a function `(url, cookies, timeout, **kw) -> FetchResult`. The
scheduler in deepfetch.py runs them in order and stops at the first result whose
`.usable` is True, so a tier must be honest about failure rather than returning
a block page as if it were content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any

# Verdicts a tier (or the classifier) can attach to a response.
# Only "ok" counts as content; the rest tell the scheduler whether escalating
# could plausibly help, or whether we must stop and tell the user the truth.
OK = "ok"
WAF = "waf"                # 403/503 from a bot wall — escalation may help
RATELIMIT = "ratelimit"    # 429 / too many requests — escalation will NOT help
CAPTCHA = "captcha"        # interactive challenge — we stop, we never solve these
LOGIN = "login"            # login wall — only the user's own cookies can pass
PAYWALL = "paywall"        # paid content — we stop, we never circumvent payment
NOTFOUND = "notfound"      # 404/410 — escalation is pointless
EMPTY = "empty"            # 200 but no meaningful content (JS-only shell)
ERROR = "error"            # transport failure

# Verdicts where climbing another tier cannot honestly change the outcome.
TERMINAL = {CAPTCHA, PAYWALL, NOTFOUND, RATELIMIT}

# A realistic, current desktop Chrome identity. Sending a truthful modern UA is
# what a normal browser does; it is not a disguise, and it stops servers from
# handing us a degraded page meant for unknown clients.
DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)

def _has_brotli() -> bool:
    """True only if something can actually decode a brotli response body.

    requests/urllib3 advertise whatever Accept-Encoding we send but don't
    verify a decoder exists for it — request 'br' without one installed and
    a compressed site (e.g. Instagram) hands back raw compressed bytes that
    get mis-decoded as garbage text instead of erroring, which is worse than
    not asking for brotli at all. Confirmed against a real fetch 2026-08-06.
    """
    try:
        import brotli  # noqa: F401
        return True
    except ImportError:
        pass
    try:
        import brotlicffi  # noqa: F401
        return True
    except ImportError:
        return False


_ACCEPT_ENCODING = "gzip, deflate, br" if _has_brotli() else "gzip, deflate"

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Accept-Encoding": _ACCEPT_ENCODING,
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Upgrade-Insecure-Requests": "1",
}


@dataclass
class FetchResult:
    """What every tier returns. `tier` and `verdict` drive the scheduler."""

    url: str
    tier: str                      # "direct" | "public-route" | "cookies" | "tls" | "browser"
    ok: bool = False               # transport succeeded (says nothing about content)
    status: int | None = None
    final_url: str | None = None
    html: str = ""
    text: str = ""                 # readable text, filled by extract.html_to_text
    verdict: str = ERROR
    structured: dict[str, Any] = field(default_factory=dict)  # OGP / JSON-LD
    note: str = ""                 # one line, human-readable, why this happened
    elapsed_ms: int = 0
    used_cookies: bool = False

    @property
    def has_structured_content(self) -> bool:
        """True only if og/jsonld actually hold data — extract_structured()
        always returns {"og": {}, "jsonld": []}, a non-empty dict shape even
        when nothing was found, so a plain `bool(self.structured)` check is
        always True and never actually gates anything. Check the payloads."""
        return bool(self.structured.get("og")) or bool(self.structured.get("jsonld"))

    @property
    def usable(self) -> bool:
        """True when this result is real content we can hand to the user.

        A page can be classified EMPTY (no rendered <body> text — a JS-shell
        SPA) while its server-rendered OGP tags still carry the real title/
        description/image, same as any social-share preview would read them.
        Confirmed against a real Instagram post 2026-08-06: verdict=empty,
        but og:description held the full caption. Treat EMPTY-with-real-
        structured-data as usable; EMPTY-with-nothing stays unusable. Every
        other non-OK verdict (login/paywall/captcha/waf/ratelimit/notfound/
        error) stays unusable even if some structured data leaked through —
        that data may belong to an interstitial page, not the real one.
        """
        if self.verdict == OK:
            return bool(self.text.strip()) or self.has_structured_content
        if self.verdict == EMPTY:
            return self.has_structured_content
        return False

    @property
    def terminal(self) -> bool:
        """True when escalating to a heavier tier cannot honestly help."""
        return self.verdict in TERMINAL

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["usable"] = self.usable
        d["terminal"] = self.terminal
        # Never emit raw html in JSON output — it defeats the point of the tool.
        d.pop("html", None)
        return d


def registrable_domain(url: str) -> str:
    """Host without leading www., lowercased. Good enough for cookie scoping."""
    m = re.match(r"^[a-z]+://([^/:?#]+)", url.strip(), re.I)
    host = (m.group(1) if m else url).lower()
    return host[4:] if host.startswith("www.") else host


def truncate(text: str, limit: int = 20000) -> str:
    """Cap text so a single page cannot flood an agent's context."""
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n[... truncated, {len(text) - limit} more chars]"
