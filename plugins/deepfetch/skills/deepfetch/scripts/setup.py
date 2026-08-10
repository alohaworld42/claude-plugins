#!/usr/bin/env python3
"""Preflight check for deepfetch's 5 fetch tiers.

Usage:
    python setup.py           # human-readable report + install hints
    python setup.py --check   # silent exit-code check (0 = core tier "direct" works)
    python setup.py --json    # structured JSON output for the agent
"""

import argparse
import io
import json
import platform
import shutil
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles (cp1252 can't encode check/cross marks).
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def check_direct():
    try:
        import requests  # noqa: F401
        import bs4  # noqa: F401
        import lxml  # noqa: F401
        return True
    except Exception:
        return False


def check_tls():
    try:
        import curl_cffi  # noqa: F401
        return True
    except Exception:
        return False


def check_browser():
    """Returns (playwright_importable, chromium_binary_found)."""
    try:
        import playwright  # noqa: F401
        playwright_ok = True
    except Exception:
        playwright_ok = False

    chromium_found = False
    try:
        if platform.system() == "Windows":
            cache_dir = Path.home() / "AppData" / "Local" / "ms-playwright"
        elif platform.system() == "Darwin":
            cache_dir = Path.home() / "Library" / "Caches" / "ms-playwright"
        else:
            cache_dir = Path.home() / ".cache" / "ms-playwright"

        if cache_dir.exists():
            for entry in cache_dir.iterdir():
                if entry.is_dir() and entry.name.startswith("chromium-"):
                    chromium_found = True
                    break
    except Exception:
        chromium_found = False

    return playwright_ok, chromium_found


def check_yt_dlp():
    try:
        return bool(shutil.which("yt-dlp"))
    except Exception:
        return False


def gather():
    direct_ok = check_direct()
    tls_ok = check_tls()
    playwright_ok, chromium_found = check_browser()
    browser_ok = playwright_ok and chromium_found
    yt_dlp_ok = check_yt_dlp()

    tiers = {
        "direct": direct_ok,
        "public-route": direct_ok,
        "tls": tls_ok,
        "browser": browser_ok,
        "cookies": yt_dlp_ok,
    }

    missing_packages = []
    install_hints = {}

    if not direct_ok:
        missing_packages.extend(["requests", "beautifulsoup4", "lxml"])
        install_hints["direct"] = "pip install requests beautifulsoup4 lxml"

    if not tls_ok:
        missing_packages.append("curl_cffi")
        install_hints["tls"] = "pip install curl_cffi"

    if not browser_ok:
        if not playwright_ok:
            missing_packages.append("playwright")
            install_hints["browser"] = "pip install playwright && playwright install chromium"
        else:
            install_hints["browser"] = "playwright install chromium"

    if not yt_dlp_ok:
        install_hints["cookies"] = "install yt-dlp: pip install yt-dlp (or: winget install yt-dlp)"

    result = {
        "tiers": tiers,
        "missing_packages": missing_packages,
        "install_hints": install_hints,
        "yt_dlp_available": yt_dlp_ok,
        "platform": platform.system(),
    }

    if not browser_ok and playwright_ok and not chromium_found:
        result["browser_binary_missing"] = True

    return result


def print_human(result):
    tiers = result["tiers"]
    labels = {
        "direct": "direct",
        "public-route": "public-route",
        "tls": "tls",
        "browser": "browser",
        "cookies": "cookies",
    }

    print("deepfetch tier availability:\n")
    for key, label in labels.items():
        mark = "✓" if tiers[key] else "✗"
        print(f"  [{mark}] {label}")

    if result["install_hints"]:
        print("\nMissing dependencies - install with:\n")
        for tier, hint in result["install_hints"].items():
            print(f"  # {tier}")
            print(f"  {hint}\n")
    else:
        print("\nAll tiers ready.")

    print(
        "Hinweis: Der cookies-Tier braucht zusaetzlich, dass der User in mindestens\n"
        "einem Browser (Firefox/Chrome/Edge) bei der Zielseite eingeloggt ist -\n"
        "das prueft dieses Skript nicht, das ist Laufzeit-Sache."
    )


def main():
    parser = argparse.ArgumentParser(description="deepfetch preflight dependency check")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="silent exit-code check")
    group.add_argument("--json", action="store_true", help="structured JSON output")
    args = parser.parse_args()

    result = gather()

    if args.check:
        if result["tiers"]["direct"]:
            sys.exit(0)
        else:
            print("deepfetch: core tier 'direct' is not runnable (missing requests/bs4/lxml)", file=sys.stderr)
            sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print_human(result)


if __name__ == "__main__":
    main()

# --- Manual test invocations (run from scripts/ directory) ---
# python setup.py --json
# python setup.py --check ; echo "exit=$?"
# python setup.py
