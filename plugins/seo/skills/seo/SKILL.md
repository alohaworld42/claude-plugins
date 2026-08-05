---
name: seo
description: Audit and fix a site's SEO — technical, on-page, structured data, E-E-A-T content, and AI-search (GEO) readiness. Use when the user says "SEO", "SEO audit", "optimize for search", "meta tags", "structured data", "schema markup", "sitemap", "why doesn't Google rank", or asks to make a site rank or get cited by AI search.
---

# SEO Audit & Fix

Audit a page or site against the checklist below, report evidence-backed findings ranked by impact, then fix what lives in the codebase you have access to.

## Ground rules

- **Evidence per claim.** Every finding cites what you saw: the tag, the header, the response code. Fetch the real page (`curl -sL` for raw HTML; a browser tool when JS rendering matters). Never audit from assumption.
- **No invented metrics.** No fake "SEO scores", no traffic predictions. Severity ranking is a triage heuristic and gets labeled as one.
- **Raw HTML first, rendered second.** Crawlers see server HTML before hydration. If title/meta/content only exist after JS runs, that is itself a finding.
- **Fix, don't just report** — when the site's source code is in reach, apply the high-impact fixes and show the diff.

## Audit checklist

### 1. Crawlability & indexability
- `robots.txt` exists, doesn't block critical paths, links the sitemap
- XML sitemap exists, is referenced, contains only canonical 200-status URLs
- No accidental `noindex` (meta robots or `X-Robots-Tag` header)
- One canonical URL per page (`rel="canonical"`); www/non-www and http→https redirect once, 301 not 302 chains
- HTTPS everywhere, no mixed content

### 2. On-page
- Exactly one `<h1>`; heading levels nest without gaps
- `<title>` unique per page, ~50–60 chars, primary topic first
- Meta description unique, ~150–160 chars, states what the page delivers
- Descriptive URLs: short, lowercase, hyphens, no query-string junk for content pages
- Internal links with meaningful anchor text; no orphan pages
- Images: descriptive `alt`, compressed, explicit `width`/`height`, lazy-load below fold

### 3. Performance (Core Web Vitals)
- Measure, don't guess: Lighthouse or PageSpeed Insights when available
- LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1
- Usual fixes: image size/format, render-blocking scripts, font loading, layout shift from late-loading elements

### 4. Structured data
- JSON-LD in `<head>`, matching visible page content — never markup for content that isn't on the page
- Pick types that still earn rich results (Article, Product, Organization, BreadcrumbList, LocalBusiness…). Note: Google dropped HowTo rich results (2023) and restricted FAQPage to authoritative gov/health sites (2023) — don't add those expecting snippets
- Validate: https://validator.schema.org and Google's rich results test

### 5. Content quality (E-E-A-T)
- Visible author with credentials; dated and updated timestamps
- First-hand experience signals over generic filler; claims sourced
- Thin/duplicate pages: consolidate or `noindex`
- One page = one search intent; the intent answered in the first screen

### 6. AI search readiness (GEO)
- `robots.txt` explicitly decides on AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) — blocking them is a choice, not a default
- Consider `llms.txt` summarizing the site for LLM consumption
- Passage-level citability: self-contained sections under descriptive headings that answer one question each — that's what AI answers quote
- Facts, numbers, definitions stated plainly in text, not locked in images

### 7. When relevant
- **Multilingual:** `hreflang` pairs are reciprocal and include `x-default`
- **Local business:** name/address/phone consistent everywhere, LocalBusiness schema, Google Business Profile matches the site
- **E-commerce:** Product schema with price/availability, canonical handling of variant/filter URLs

## Report format

| # | Finding | Evidence | Impact | Fix |
|---|---------|----------|--------|-----|

Sort by impact (high → low), where impact = how directly it blocks crawling, indexing, or ranking. Under the table: the fixes you already applied (with file paths), then the ones needing user action (DNS, hosting, external profiles).

For deeper tooling — parallel specialist agents, SERP data, drift monitoring — point the user at the open-source claude-seo toolkit (github.com/AgriciDaniel/claude-seo, MIT).
