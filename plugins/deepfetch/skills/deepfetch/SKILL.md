---
name: deepfetch
description: Fetch a URL that a normal fetch/WebFetch can't reach — 403/WAF-blocked pages, JS-only SPAs, anti-bot walls, and (uniquely) pages behind a login the user already has in their own browser. Escalates through five tiers automatically and stops honestly at real login/paywall/captcha walls instead of pretending to get through. Use when a fetch returns 403, a bot-check page, empty JS-shell content, or when the user says a page "won't load", "is blocked", "needs login", or asks to read something from a site that requires being signed in.
---

# deepfetch

Five-tier fetch escalation. Tries the cheapest thing first, climbs only as far as needed, and — unlike a plain fetch — tells you honestly *why* it stopped instead of returning a CAPTCHA page as if it were content.

```
direct -> public-route -> tls -> browser -> cookies (opt-in) -> browser+cookies
```

Built after two existing tools, deliberately covering everything both do plus the one gap neither closes:

- **[insane-search](https://github.com/fivetaku/insane-search)** — the phase-ladder idea (public endpoints → probes → TLS impersonation → real browser) and the principle of reporting "authentication required" instead of faking success.
- **[playwright-bot-bypass](https://github.com/greekr4/playwright-bot-bypass)** — real Chrome + stealth patches beat a naive headless browser against fingerprint-based anti-bot checks.
- **What neither does — and this plugin's actual reason to exist:** both explicitly refuse login walls (insane-search stops and says so; playwright-bot-bypass's own README lists Instagram/Facebook/LinkedIn under "doesn't touch"). deepfetch adds a **cookies tier** that reuses the user's own already-authenticated browser session — the same access they already have by hand, read programmatically. It is off by default and gated per-domain; see **Cookies tier & consent** below before ever touching it.

## Setup

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/deepfetch/scripts/setup.py"
```

Prints which of the 5 tiers are ready and the exact `pip install` command for any that aren't. `direct` and `public-route` need nothing beyond `requests`/`beautifulsoup4`/`lxml` (installed by default in most Python envs) and work out of the box. `tls`/`browser` are optional upgrades — deepfetch degrades cleanly without them, it just has fewer rungs on the ladder. On Windows use `python`, not `python3`.

Structured check for the agent: `python setup.py --json` → `{"tiers": {...}, "missing_packages": [...], "install_hints": {...}}`. Silent gate: `python setup.py --check` (exit 0 if the core tier works).

## Run

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/deepfetch/scripts/deepfetch.py" "<url>" --json
```

Returns JSON with `result` (the best answer found) and `trace` (every tier tried, in order, with its verdict — read this when `result.usable` is `false` to explain to the user *why*, instead of just saying "it didn't work"). Drop `--json` for a human-readable Markdown report instead.

`result.usable` is the field to check before using `result.text`. A result can be `verdict="empty"` (no rendered body text — a JS-shell SPA) yet still `usable=true` if the page's OGP meta tags carried the real title/description (very common — even Instagram serves this to logged-out requests). Don't discard a result just because `verdict != "ok"`; check `usable`.

`result.structured` holds `{"og": {...}, "jsonld": [...]}` — check this even when `result.text` is empty. Confirmed live: an Instagram post's full caption came back via `og:description` from the `direct` tier alone, no login needed.

Useful flags: `--timeout N` (default 20s), `--browser firefox|chrome|edge|brave|chromium` (which browser's cookies to prefer, once cookies are allowed).

## Cookies tier & consent — read this before using `--allow-cookies`

This is the one capability that makes deepfetch more than a rebuild of the two reference tools, and the one place a careless agent can do real harm to the user's trust. The rules are enforced in code (`tier_cookies.py`), not just documented here, but you still have to drive them correctly:

1. **Never pass `--allow-cookies` on the first try.** Run deepfetch normally first. If the result comes back `verdict="login"`, its `note` field already contains the exact next step and the exact domain.
2. **Ask the user, in chat, before enabling it for a new domain.** Something like: *"This page needs your `instagram.com` login. I can reuse the session from your own browser — no password touches me, I only reuse the cookie your browser already has. OK to proceed?"* Never phrase this as already-decided.
3. **Only after they say yes**, run:
   ```bash
   python deepfetch.py --allow-domain <domain>
   ```
   This persists consent to `~/.config/deepfetch/cookie_domains.txt` (0600 perms) so you don't have to ask again for that domain in future sessions.
4. **Then retry the original fetch with `--allow-cookies`.**

What this tier will never do, by design: read a password, token, or credential; send one domain's cookies to a different domain; write a cookie value to a log, a report, or any file other than a short-lived jar that's deleted before the call returns; or fire without both `--allow-cookies` *and* a prior `--allow-domain` for that exact registrable domain. If you ever see cookie *values* in output somewhere, that's a bug — stop and report it, don't paper over it.

This is reuse of the user's own access, not a bypass of anyone else's — the same distinction that keeps this legitimate. It doesn't touch a site's authentication system; it presents the credential the user's browser already holds, the same way the browser itself would.

## Tier reference

| Tier | What it does | Needs |
|---|---|---|
| `direct` | Plain `requests.get` with a truthful modern browser UA | nothing extra |
| `public-route` | Known public API/syndication shortcuts: Reddit `.json`, `yt-dlp --dump-json` for YouTube, `r.jina.ai` read-proxy fallback | `yt-dlp` for the YouTube path only |
| `tls` | `curl_cffi` TLS impersonation, tries safari → chrome → firefox identities | `pip install curl_cffi` |
| `browser` | Real Chrome via Playwright, headless first then headed once if that alone didn't get through; `navigator.webdriver` stripped | `pip install playwright && playwright install chromium` |
| `cookies` | Reuses the user's browser session (via `yt-dlp`'s cookie export) for the *same* registrable domain only | `yt-dlp`, explicit per-domain consent |

Escalation stops immediately whenever a tier reports a **terminal** verdict — `captcha`, `paywall`, `notfound`, or `ratelimit` — because no heavier tier can honestly change that outcome. It also stops immediately on `ok` (or `empty`-with-real-structured-data). It only keeps climbing on ambiguous outcomes (`waf`, plain `empty`, `error`) where the next tier might plausibly do better.

## What this does NOT do

Mirrors both reference tools' own honesty about their limits, because pretending otherwise is worse than not trying:

- Does not solve CAPTCHAs (Turnstile, DataDome, Kasada, etc.) — reports `captcha` and stops.
- Does not defeat IP-reputation blocks or real rate limits — reports `ratelimit` and stops (escalating tiers wouldn't help; confirmed live against Reddit's `.json` endpoint, which now rate-limits unauthenticated requests).
- Does not pay for or circumvent a paywall — reports `paywall` and stops.
- Does not access an account the user hasn't already logged into in one of their own browsers.

## Failure modes

- **`setup.py` shows a tier missing** → tell the user the exact install command from `install_hints`; don't attempt to install anything yourself without asking, per this plugin's own consent principle.
- **`playwright` installed but browser tier still errors with "binary missing"** → the browsers weren't downloaded; `playwright install chromium` is a separate step from `pip install playwright`.
- **`verdict="login"` and cookies are already allowed for the domain, but the result is still not usable** → the user isn't logged into that site in the browser deepfetch checked; try `--browser <other>` for a different browser, or the user simply isn't logged in anywhere on this machine.
- **A response's text looks like binary garbage** → almost always a compression mismatch (a `brotli` decoder missing while the server sent `br`-encoded content). `common.py` already detects this at import time and only advertises `br` support when a decoder is actually importable — if you still see this, `pip install brotli` fixes it permanently.

## Security & Permissions

**What this skill does:**
- Runs local HTTP requests (`requests`, `curl_cffi`) and, for the heaviest tier, a real local Chromium instance (`playwright`) to fetch a URL the user asked about
- Runs `yt-dlp` locally, only for two narrow purposes: reading YouTube metadata in `public-route`, and exporting browser cookies in `cookies`
- Reads `~/.config/deepfetch/cookie_domains.txt` (consent allowlist) and writes to it only via the explicit `--allow-domain` step
- Extracts cookies from the user's own local browser profile (Firefox/Chrome/Edge/Brave), scoped strictly to the one domain being fetched, held only in memory plus a temp file deleted before the call returns

**What this skill does NOT do:**
- Does not solve CAPTCHAs, defeat paywalls, or bypass real authentication systems — see "What this does NOT do" above
- Does not read, enter, or generate any password, token, or credential
- Does not send one domain's cookies to a different domain
- Does not log, print, or persist actual cookie values anywhere
- Does not fire the cookies tier without both `--allow-cookies` and a prior, explicit `--allow-domain` consent step for that exact domain

**Bundled scripts:** `scripts/deepfetch.py` (CLI entry point / scheduler), `scripts/common.py` (shared types), `scripts/classify.py` (response → verdict), `scripts/extract.py` (HTML → text/OGP/JSON-LD), `scripts/tier_direct.py`, `scripts/tier_tls.py`, `scripts/tier_browser.py`, `scripts/tier_cookies.py`, `scripts/setup.py`.

Review scripts before first use to verify behavior.
