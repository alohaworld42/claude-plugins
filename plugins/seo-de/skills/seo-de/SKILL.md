---
name: seo-de
description: SEO einer Website prüfen und beheben — technisch, On-Page, strukturierte Daten, E-E-A-T-Inhalte und KI-Suche (GEO), mit DACH-Spezifika (Impressum, Umlaute, google.de). Nutzen wenn der User sagt "SEO", "SEO-Audit", "SEO prüfen", "Meta-Tags", "strukturierte Daten", "Schema-Markup", "Sitemap", "warum rankt Google nicht", oder eine Website ranken bzw. von KI-Suche zitiert werden soll. Antworten und Report auf Deutsch.
---

# SEO-Audit & Fix (Deutsch)

Prüfe eine Seite oder Website gegen die Checkliste unten, berichte belegte Befunde nach Wirkung sortiert, dann behebe alles, was im erreichbaren Code liegt. **Report und Kommunikation auf Deutsch.**

## Grundregeln

- **Beleg pro Befund.** Jeder Befund zitiert, was du gesehen hast: das Tag, den Header, den Statuscode. Hole die echte Seite (`curl -sL` für rohes HTML; Browser-Tool, wenn JS-Rendering zählt). Nie aus Annahme auditieren.
- **Keine erfundenen Metriken.** Keine Fantasie-„SEO-Scores", keine Traffic-Prognosen. Die Prioritäts-Reihung ist eine Triage-Heuristik und wird als solche benannt.
- **Rohes HTML zuerst, gerendert danach.** Crawler sehen Server-HTML vor der Hydration. Existieren Title/Meta/Inhalt erst nach JS, ist das selbst ein Befund.
- **Beheben, nicht nur berichten** — liegt der Quellcode der Site in Reichweite, wende die wirksamsten Fixes an und zeige den Diff.

## Audit-Checkliste

### 1. Crawlbarkeit & Indexierbarkeit
- `robots.txt` existiert, blockiert keine kritischen Pfade, verlinkt die Sitemap
- XML-Sitemap existiert, wird referenziert, enthält nur kanonische 200er-URLs
- Kein versehentliches `noindex` (Meta-Robots oder `X-Robots-Tag`-Header)
- Eine kanonische URL pro Seite (`rel="canonical"`); www/non-www und http→https leiten einmal weiter, 301 statt 302-Ketten
- Durchgehend HTTPS, kein Mixed Content

### 2. On-Page
- Genau ein `<h1>`; Überschriften-Ebenen ohne Sprünge verschachtelt
- `<title>` pro Seite einzigartig, ~50–60 Zeichen, Hauptthema zuerst — deutsche Komposita fressen Platz, kürzen statt abschneiden lassen
- Meta-Description einzigartig, ~150–160 Zeichen, sagt konkret, was die Seite liefert
- Sprechende URLs: kurz, klein, Bindestriche; Umlaute transliterieren (ä→ae, ö→oe, ü→ue, ß→ss), keine Query-Reste bei Inhaltsseiten
- Interne Links mit aussagekräftigem Ankertext; keine verwaisten Seiten
- Bilder: beschreibendes `alt` (deutsch), komprimiert, explizite `width`/`height`, Lazy-Load unterhalb des Folds

### 3. Performance (Core Web Vitals)
- Messen statt schätzen: Lighthouse oder PageSpeed Insights, wenn verfügbar
- LCP ≤ 2,5 s, INP ≤ 200 ms, CLS ≤ 0,1
- Übliche Fixes: Bildgröße/-format, renderblockierende Skripte, Font-Loading, Layout-Shift durch nachladende Elemente

### 4. Strukturierte Daten
- JSON-LD im `<head>`, deckungsgleich mit sichtbarem Inhalt — nie Markup für Inhalte, die nicht auf der Seite stehen
- Typen wählen, die noch Rich Results bringen (Article, Product, Organization, BreadcrumbList, LocalBusiness…). Achtung: Google hat HowTo-Rich-Results gestrichen (2023) und FAQPage auf autoritative Behörden-/Gesundheitsseiten beschränkt (2023) — nicht in Erwartung von Snippets einbauen
- Validieren: https://validator.schema.org und Googles Rich-Results-Test

### 5. Inhaltsqualität (E-E-A-T)
- Sichtbarer Autor mit Qualifikation; Veröffentlichungs- und Aktualisierungsdatum
- Erfahrung aus erster Hand statt generischem Füllstoff; Behauptungen mit Quellen
- Dünne/doppelte Seiten: zusammenlegen oder `noindex`
- Eine Seite = eine Suchintention; Antwort im ersten sichtbaren Bereich

### 6. KI-Suche (GEO)
- `robots.txt` entscheidet explizit über KI-Crawler (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) — Blocken ist eine Entscheidung, kein Default
- `llms.txt` erwägen: Site-Zusammenfassung für LLM-Konsum
- Passagen-Zitierbarkeit: in sich geschlossene Abschnitte unter sprechenden Überschriften, die je eine Frage beantworten — genau das zitieren KI-Antworten
- Fakten, Zahlen, Definitionen im Text ausformuliert, nicht in Bildern versteckt

### 7. DACH-Spezifika
- **Impressum und Datenschutzerklärung** verlinkt und erreichbar — Pflicht (§ 5 DDG/TMG, DSGVO) und zugleich Vertrauenssignal für E-E-A-T
- `hreflang` für de-DE / de-AT / de-CH reziprok gepflegt, inklusive `x-default`; Schweiz beachten: ss statt ß
- `lang="de"` (bzw. `de-AT`, `de-CH`) im `<html>`-Tag
- Lokales Geschäft: Name/Adresse/Telefon überall identisch, LocalBusiness-Schema, Google-Unternehmensprofil deckungsgleich mit der Site
- E-Commerce: Product-Schema mit Preis in EUR/CHF und Verfügbarkeit; Varianten-/Filter-URLs kanonisch behandeln

## Report-Format

| # | Befund | Beleg | Wirkung | Fix |
|---|--------|-------|---------|-----|

Sortiert nach Wirkung (hoch → niedrig); Wirkung = wie direkt Crawling, Indexierung oder Ranking blockiert wird. Unter der Tabelle: bereits angewendete Fixes (mit Dateipfaden), danach offene Punkte, die der User selbst erledigen muss (DNS, Hosting, externe Profile).

Für schwereres Werkzeug — parallele Spezialisten-Agenten, SERP-Daten, Drift-Monitoring — auf das Open-Source-Toolkit claude-seo verweisen (github.com/AgriciDaniel/claude-seo, MIT, englisch).

---
*Dieser Skill ist eine eigenständige, deutschsprachige Destillation inspiriert von [claude-seo](https://github.com/AgriciDaniel/claude-seo) von Daniel Agrici (MIT-lizenziert). Für das volle Toolkit mit 25 Skills, 18 Agenten, SERP-Daten und Drift-Monitoring: Original installieren.*
