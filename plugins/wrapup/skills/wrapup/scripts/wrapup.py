#!/usr/bin/env python3
"""Write a session digest to the local store and update the index.

Reads the digest body from a file or stdin, writes it to
<store>/sessions/<date>-<slug>.md, and prepends a one-line entry to
<store>/INDEX.md so recall can scan cheaply without opening digests.

Optionally pushes the same digest to a NotebookLM notebook via the
unofficial `notebooklm` CLI (only if that CLI is installed and authed).
"""

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_STORE = Path(os.environ.get("WRAPUP_STORE", Path.home() / ".claude" / "wrapup"))


def slugify(text: str, maxlen: int = 48) -> str:
    text = text.lower().strip()
    # keep umlauts readable in filenames
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(a, b)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return (text[:maxlen].rstrip("-")) or "session"


def read_body(args) -> str:
    if args.content_file and args.content_file != "-":
        return Path(args.content_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def push_notebooklm(title: str, digest_path: Path, notebook: str | None) -> str:
    """Best-effort push. Returns a status string; never raises."""
    if not shutil.which("notebooklm"):
        return "skipped (notebooklm CLI not installed)"
    cmd = ["notebooklm"]
    if notebook:
        cmd += ["-n", notebook]
    cmd += ["note", "create", "-", "-t", title]
    try:
        body = digest_path.read_text(encoding="utf-8")
        proc = subprocess.run(
            cmd, input=body, text=True, capture_output=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return "failed (notebooklm timed out after 120s)"
    except Exception as exc:  # noqa: BLE001 - push must never break the local write
        return f"failed ({exc})"
    if proc.returncode == 0:
        return "ok"
    err = (proc.stderr or proc.stdout or "").strip().splitlines()
    return f"failed (exit {proc.returncode}: {err[-1] if err else 'no output'})"


def main() -> int:
    p = argparse.ArgumentParser(description="Write a session digest to the wrapup store.")
    p.add_argument("--title", required=True, help="Short human title for this session")
    p.add_argument("--project", default="", help="Project or repo this session belongs to")
    p.add_argument("--tags", default="", help="Comma-separated tags for recall")
    p.add_argument("--content-file", default="-", help="Digest body file, or - for stdin")
    p.add_argument("--store", default=str(DEFAULT_STORE), help="Store directory")
    p.add_argument("--push-notebooklm", action="store_true", help="Also push to NotebookLM")
    p.add_argument("--notebook", default=os.environ.get("WRAPUP_NOTEBOOK", ""),
                   help="NotebookLM notebook id (default: active notebook)")
    args = p.parse_args()

    body = read_body(args).strip()
    if not body:
        print("error: empty digest body — nothing written", file=sys.stderr)
        return 1

    store = Path(args.store)
    sessions = store / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)

    now = dt.datetime.now()
    stamp = now.strftime("%Y-%m-%d-%H%M")
    path = sessions / f"{stamp}-{slugify(args.title)}.md"

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    front = [
        "---",
        f"date: {now.strftime('%Y-%m-%d %H:%M')}",
        f"title: {args.title}",
    ]
    if args.project:
        front.append(f"project: {args.project}")
    if tags:
        front.append(f"tags: [{', '.join(tags)}]")
    front.append("---")
    path.write_text("\n".join(front) + "\n\n" + body + "\n", encoding="utf-8")

    index = store / "INDEX.md"
    header = "# Wrapup Index\n\nEine Zeile pro Session, neueste zuerst.\n"
    existing = index.read_text(encoding="utf-8") if index.exists() else header
    if not existing.startswith("# Wrapup Index"):
        existing = header + existing
    line = f"- {now.strftime('%Y-%m-%d')} [{args.title}](sessions/{path.name})"
    if args.project:
        line += f" — {args.project}"
    if tags:
        line += f" · {' '.join('#' + t for t in tags)}"
    head, _, tail = existing.partition("neueste zuerst.\n")
    index.write_text(head + "neueste zuerst.\n" + line + "\n" + tail.lstrip("\n"),
                     encoding="utf-8")

    print(f"digest: {path}")
    print(f"index:  {index}")
    if args.push_notebooklm:
        print(f"notebooklm: {push_notebooklm(args.title, path, args.notebook or None)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
