# deepfetch

Explains: what it is, what was actually verified before shipping, and what it does not claim to do.

## What it is

Five-tier fetch escalation for Claude Code: `direct → public-route → tls → browser → cookies (opt-in) → browser+cookies`. Built to cover everything [insane-search](https://github.com/fivetaku/insane-search) and [playwright-bot-bypass](https://github.com/greekr4/playwright-bot-bypass) do, plus the one thing neither does — reusing the user's own already-authenticated browser session for login-walled pages, gated behind explicit per-domain consent. Full behavior and the consent flow: [SKILL.md](skills/deepfetch/SKILL.md).

## What was actually verified (2026-08-06)

Not asserted — run, in this order, against this environment (Windows, Python 3.14, no `curl_cffi`/`playwright` installed):

- **6 module self-tests, all green:** `classify.py`, `extract.py`, `tier_direct.py`, `tier_tls.py`, `tier_cookies.py`, `tier_browser.py`.
- **Live network calls**, not mocks: `example.com` (tier `direct`), a real Reddit `.json` endpoint (correctly classified `ratelimit` and stopped — Reddit now rate-limits unauthenticated JSON requests), `r.jina.ai` (correctly classified `waf`/escalatable), and a real login-walled Instagram post — twice: once with cookies denied (stopped honestly, told the agent exactly what to ask the user), once approved (9 real cookies extracted from Firefox via `yt-dlp`, GET returned status 200 past the login wall).
- **Graceful degradation confirmed, not assumed:** with `curl_cffi` and `playwright` both absent, `tier_tls`/`tier_browser` return a clean `verdict=error` with the exact install command — never a crash, never a false success.

### Two real bugs found and fixed during that verification

1. **Brotli mismatch.** `DEFAULT_HEADERS` advertised `Accept-Encoding: br` unconditionally; without a `brotli`/`brotlicffi` decoder installed, a compressed response (Instagram) came back as undecodable garbage bytes, not an error. Fixed: `common.py` now checks for a working decoder at import time and only advertises `br` when one exists.
2. **Script content counted as visible text.** `classify.py`'s empty-page detector stripped HTML tags but not `<script>`/`<style>` *contents*, so a JS-only SPA shell with a large inline bundle (Instagram again — 839 KB of HTML, zero rendered text) was misclassified `ok` instead of `empty`. Fixed: script/style bodies are stripped before measuring visible length, with a regression test.
3. **Follow-on design gap, fixed same session:** even after fix #2 correctly flagged the Instagram page `empty`, its result was still being discarded — `FetchResult.usable` required `verdict == "ok"`, so a page with no rendered text but a fully-populated `og:description` (Instagram's real caption, confirmed present) was treated as useless. Fixed: `usable` now accepts `verdict == "empty"` when real structured data (OGP/JSON-LD) was found, while still correctly rejecting a truly blank shell.

## What it does not claim

Same honesty principle as its two references: does not solve CAPTCHAs, does not defeat real rate limits or IP-reputation blocks, does not circumvent a paywall, does not touch an account the user hasn't already logged into themselves. See [SKILL.md](skills/deepfetch/SKILL.md#what-this-does-not-do) for the full list and the reasoning.

## Layout

```
.claude-plugin/plugin.json
skills/deepfetch/
  SKILL.md
  scripts/
    deepfetch.py     # CLI entry point / scheduler
    common.py         # FetchResult, shared headers, usable/terminal logic
    classify.py       # HTTP response -> verdict
    extract.py        # HTML -> text / OGP / JSON-LD
    tier_direct.py     # tiers: direct, public-route
    tier_tls.py        # tier: tls (curl_cffi impersonation)
    tier_browser.py    # tier: browser (Playwright + stealth)
    tier_cookies.py    # tier: cookies (consent-gated session reuse)
    setup.py           # preflight / dependency check
```

## License

MIT
