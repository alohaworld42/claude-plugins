#!/usr/bin/env python3
"""HTML -> readable text and structured metadata (OGP + JSON-LD).

This is the tier-agnostic post-processing step: every tier hands its raw
HTML here to fill `FetchResult.text` and `FetchResult.structured`.
"""

from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup

_JUNK_TAGS = ["script", "style", "nav", "header", "footer", "aside", "noscript"]
_JUNK_NEEDLES = ["cookie", "banner", "advert", "sidebar"]


def _is_junk(tag) -> bool:
    classes = tag.get("class") or []
    if isinstance(classes, str):
        classes = [classes]
    ident = " ".join(classes) + " " + (tag.get("id") or "")
    ident = ident.lower()
    return any(n in ident for n in _JUNK_NEEDLES)


def html_to_text(html: str, base_url: str = "") -> str:
    """Wandelt rohes HTML in lesbaren Artikeltext um."""
    if not html or not html.strip():
        return ""

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return ""

    for tag_name in _JUNK_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Substring-match on class/id for cookie/banner/advert/sidebar-ish blocks.
    for tag in soup.find_all(True):
        if tag.parent is None:
            continue
        if _is_junk(tag):
            tag.decompose()

    root = soup.find("article") or soup.find("main") or soup.find("body") or soup

    block_tags = [
        "p", "h1", "h2", "h3", "h4", "h5", "h6",
        "li", "blockquote", "pre", "td", "figcaption",
    ]
    paragraphs: list[str] = []
    for tag in root.find_all(block_tags):
        text = tag.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            paragraphs.append(text)

    if not paragraphs:
        text = root.get_text(separator="\n", strip=True)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()

    # Drop consecutive duplicate lines (common with nested block tags).
    deduped: list[str] = []
    for p in paragraphs:
        if not deduped or deduped[-1] != p:
            deduped.append(p)

    return "\n\n".join(deduped).strip()


def extract_structured(html: str) -> dict:
    """Extrahiert Open Graph Meta-Tags + JSON-LD.

    Rueckgabe: {"og": {...}, "jsonld": [...]}
    """
    result: dict = {"og": {}, "jsonld": []}
    if not html or not html.strip():
        return result

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        try:
            soup = BeautifulSoup(html, "html.parser")
        except Exception:
            return result

    og: dict = {}
    for meta in soup.find_all("meta"):
        prop = meta.get("property")
        if prop and prop.lower().startswith("og:"):
            content = meta.get("content", "")
            og[prop] = content
    result["og"] = og

    jsonld: list = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string
        if raw is None:
            raw = script.get_text()
        if not raw or not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        jsonld.append(data)
    result["jsonld"] = jsonld

    return result


if __name__ == "__main__":
    # 1. Normaler Artikel mit Nav+Footer-Muell.
    article_html = """
    <html><body>
      <nav><a href="/">Home</a><a href="/about">About</a></nav>
      <header>Site Header Junk</header>
      <div class="cookie-banner">We use cookies, accept now!</div>
      <article>
        <h1>Der Titel des Artikels</h1>
        <p>Dies ist der erste Absatz mit dem eigentlichen Inhalt.</p>
        <p>Und ein zweiter Absatz mit mehr Text ueber das Thema.</p>
      </article>
      <aside class="sidebar">Related links junk</aside>
      <footer>Copyright 2024 Footer Junk</footer>
    </body></html>
    """
    text = html_to_text(article_html)
    assert "Der Titel des Artikels" in text
    assert "erste Absatz" in text
    assert "zweiter Absatz" in text
    assert "Home" not in text
    assert "Site Header Junk" not in text
    assert "cookies, accept now" not in text
    assert "Related links junk" not in text
    assert "Copyright 2024 Footer Junk" not in text

    # 2. OGP-Tags vorhanden.
    ogp_html = """
    <html><head>
      <meta property="og:title" content="Ein toller Titel" />
      <meta property="og:description" content="Eine Beschreibung" />
      <meta property="og:url" content="https://example.com/page" />
      <meta name="description" content="ignoriert, kein og:" />
    </head><body><p>Inhalt</p></body></html>
    """
    structured = extract_structured(ogp_html)
    assert structured["og"]["og:title"] == "Ein toller Titel"
    assert structured["og"]["og:description"] == "Eine Beschreibung"
    assert structured["og"]["og:url"] == "https://example.com/page"
    assert len(structured["og"]) == 3

    # 3. JSON-LD vorhanden: ein gueltiger Block + ein absichtlich kaputter.
    jsonld_html = """
    <html><head>
      <script type="application/ld+json">
      {"@context": "https://schema.org", "@type": "Article", "headline": "Hallo"}
      </script>
      <script type="application/ld+json">
      { this is not valid json, oops }
      </script>
    </head><body><p>Inhalt</p></body></html>
    """
    structured2 = extract_structured(jsonld_html)
    assert len(structured2["jsonld"]) == 1
    assert structured2["jsonld"][0]["headline"] == "Hallo"

    # 4. Leeres/kaputtes HTML -> leerer String, keine Exception.
    assert html_to_text("") == ""
    assert html_to_text("   ") == ""
    assert html_to_text("<html><body><<<>>>broken") == "" or isinstance(
        html_to_text("<html><body><<<>>>broken"), str
    )
    empty_structured = extract_structured("")
    assert empty_structured == {"og": {}, "jsonld": []}
    broken_structured = extract_structured("not even html <<<>>>")
    assert broken_structured["og"] == {}
    assert broken_structured["jsonld"] == []

    print("extract.py: all self-tests passed")
