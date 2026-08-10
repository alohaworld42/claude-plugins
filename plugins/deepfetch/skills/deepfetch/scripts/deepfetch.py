#!/usr/bin/env python3
"""deepfetch — multi-tier fetch escalation for Claude Code.

Runs a URL through tiers of increasing cost/capability, stopping at the
first one that returns real content, and stopping *honestly* the moment a
result is terminal (login/paywall/captcha/notfound/ratelimit) — no tier
below is allowed to pretend a wall is content, and no tier above is tried
once escalating cannot possibly help.

Order: direct -> public-route -> tls -> browser -> (cookies, only if the
caller opted in and the domain is pre-approved) -> browser+cookies.

Modeled on two existing tools so nothing either does is missing here:
- insane-search (github.com/fivetaku/insane-search): the phase 0-3 escalation
  idea (public endpoints -> probes -> TLS impersonation -> real browser),
  and the principle of reporting "authentication required" instead of
  faking success on a login wall.
- playwright-bot-bypass (github.com/greekr4/playwright-bot-bypass): real
  Chrome + stealth patches beat headless-with-JS-fakes; both tools' own
  docs list login walls as something they explicitly do NOT cross.

The one thing neither does: reusing the user's OWN already-authenticated
browser session for a page they can already see by hand. That's tier
'cookies' in tier_cookies.py — off by default, gated per-domain, see
--allow-domain / --allow-cookies below.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from common import FetchResult, registrable_domain
import tier_direct
import tier_tls
import tier_browser
import tier_cookies

TIER_ORDER_NOTE = "direct -> public-route -> tls -> browser -> cookies (opt-in) -> browser+cookies"


def _requests_cookies_to_playwright(cookies: dict[str, str], domain: str) -> list[dict]:
    """Convert a plain {name: value} cookie dict into Playwright's cookie format."""
    return [
        {"name": name, "value": value, "domain": "." + domain, "path": "/"}
        for name, value in cookies.items()
    ]


def run(
    url: str,
    timeout: int = 20,
    allow_cookies: bool = False,
    browser_pref: str | None = None,
) -> tuple[FetchResult, list[FetchResult]]:
    """Run the full escalation. Returns (best_result, trace_of_all_attempts)."""
    trace: list[FetchResult] = []

    def attempt(fn, *a, **kw) -> FetchResult:
        r = fn(*a, **kw)
        trace.append(r)
        return r

    r = attempt(tier_direct.fetch_direct, url, timeout)
    if r.usable or r.terminal:
        return r, trace

    r = attempt(tier_direct.fetch_public_route, url, timeout)
    if r.usable or r.terminal:
        return r, trace

    r = attempt(tier_tls.fetch_tls, url, timeout)
    if r.usable or r.terminal:
        return r, trace

    r = attempt(tier_browser.fetch_browser, url, timeout=timeout)
    if r.usable or r.terminal:
        return r, trace

    if r.verdict != "login":
        # Ran out of non-authenticated options and it isn't a login wall
        # (e.g. persistent WAF/empty-shell) — nothing left to try honestly.
        return r, trace

    # Login wall. Only the user's own session can get past this — and only
    # if they already said yes for this exact domain.
    domain = registrable_domain(url)
    if not allow_cookies:
        note = (
            f"authentication required for '{domain}'. This can only be solved by "
            f"reusing your own browser session, and deepfetch never does that "
            f"without asking first. Ask the user: 'allow deepfetch to reuse your "
            f"{browser_pref or 'browser'} login for {domain}?' If yes, run: "
            f"python deepfetch.py --allow-domain {domain}, then retry this URL "
            f"with --allow-cookies."
        )
        r2 = FetchResult(url=url, tier="cookies", ok=False, verdict="login", note=note)
        trace.append(r2)
        return r2, trace

    if not tier_cookies.is_domain_allowed(url):
        note = (
            f"'{domain}' is not yet approved for cookie reuse. Ask the user for "
            f"confirmation, then run: python deepfetch.py --allow-domain {domain}"
        )
        r2 = FetchResult(url=url, tier="cookies", ok=False, verdict="login", note=note)
        trace.append(r2)
        return r2, trace

    r = attempt(tier_cookies.fetch_with_cookies, url, timeout, browser_pref, True)
    if r.usable or r.terminal:
        return r, trace

    # Cookies got past the login wall (verdict likely 'empty') but the page
    # is client-rendered — combine both: real browser, with the same
    # session injected, so JS can hydrate the authenticated page.
    cookies = tier_cookies.get_cookies_for_domain(url, browser=browser_pref)
    if cookies:
        pw_cookies = _requests_cookies_to_playwright(cookies, domain)
        r = attempt(tier_browser.fetch_browser, url, timeout=max(timeout, 30), cookies=pw_cookies)
        return r, trace

    return r, trace


def _report_markdown(url: str, result: FetchResult, trace: list[FetchResult], elapsed_ms: int) -> str:
    lines = [f"# deepfetch report", ""]
    if result.usable:
        lines.append(f"✓ Got content via tier `{result.tier}` (verdict: {result.verdict})")
    else:
        lines.append(f"✗ Could not get usable content (final verdict: {result.verdict})")
    lines += [
        f"- **URL:** {url}",
        f"- **Final URL:** {result.final_url or url}",
        f"- **Tiers tried:** {' -> '.join(t.tier for t in trace)}",
        f"- **Total time:** {elapsed_ms}ms",
    ]
    if result.note:
        lines.append(f"- **Note:** {result.note}")
    lines.append("")
    if result.structured and (result.structured.get("og") or result.structured.get("jsonld")):
        lines.append("## Structured data")
        if result.structured.get("og"):
            lines.append(f"OGP: {json.dumps(result.structured['og'], ensure_ascii=False)}")
        if result.structured.get("jsonld"):
            lines.append(f"JSON-LD blocks: {len(result.structured['jsonld'])}")
        lines.append("")
    if result.usable:
        lines.append("## Content")
        lines.append("")
        lines.append(result.text)
    else:
        lines.append("## Trace (why each tier stopped)")
        for t in trace:
            lines.append(f"- `{t.tier}`: verdict={t.verdict}, note={t.note or '(none)'}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Multi-tier fetch escalation. " + TIER_ORDER_NOTE,
    )
    p.add_argument("url", nargs="?", help="URL to fetch")
    p.add_argument("--timeout", type=int, default=20)
    p.add_argument("--allow-cookies", action="store_true",
                    help="Permit the cookies tier for domains already on the allowlist")
    p.add_argument("--browser", default=None, choices=["firefox", "chrome", "edge", "brave", "chromium"],
                    help="Which browser's cookies to reuse (default: try all, firefox first)")
    p.add_argument("--allow-domain", metavar="DOMAIN",
                    help="Add DOMAIN to the cookie allowlist and exit — run this only "
                         "after the user has explicitly confirmed it in chat")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of Markdown")
    args = p.parse_args()

    if args.allow_domain:
        tier_cookies.add_to_allowlist(args.allow_domain)
        msg = f"'{args.allow_domain}' added to the cookie allowlist ({tier_cookies.ALLOWLIST_FILE})"
        if args.json:
            print(json.dumps({"ok": True, "message": msg}))
        else:
            print(msg)
        return 0

    if not args.url:
        p.error("url is required unless --allow-domain is used")

    t0 = time.monotonic()
    result, trace = run(args.url, timeout=args.timeout, allow_cookies=args.allow_cookies,
                         browser_pref=args.browser)
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    if args.json:
        out = {
            "url": args.url,
            "result": result.to_dict(),
            "trace": [t.to_dict() for t in trace],
            "elapsed_ms": elapsed_ms,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(_report_markdown(args.url, result, trace, elapsed_ms))

    return 0 if result.usable else 1


if __name__ == "__main__":
    sys.exit(main())
