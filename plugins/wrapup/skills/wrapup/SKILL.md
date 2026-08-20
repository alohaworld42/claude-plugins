---
name: wrapup
description: Memory across sessions — save a compact digest at the end of a session (decisions, gotchas, status, open items), pull it back selectively at the start of the next instead of rebuilding context. Local plus an optional Notion mirror. Use when the user says "wrapup", "wrap up", "save this session", "remember this for next time", "what did we do last time", "where did we leave off", "do you remember", closes out a session, or asks about earlier decisions/fixes.
---

# Wrapup — Memory Across Sessions

Every new session starts at zero. Rebuilding context costs tokens and time — and whatever was decided last session is lost. This skill solves that with two moves: **save at the end** (`wrapup.py`), **pull back selectively at the start** (`recall.py`).

The saving doesn't come from compression but from **selective loading**: `INDEX.md` is tiny (1 line per session), `recall.py` shows only matching hits, and only then is a single digest read. Never the whole history.

Store: `~/.claude/wrapup/` (`sessions/*.md` + `INDEX.md`). Override via `WRAPUP_STORE`.
Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/wrapup/scripts/`.

## Saving (end of session)

Write only what a **future session** needs to know. This is not a transcript — it's about the next you not walking into the same dead end again.

Goes in:
- **Decisions + rationale.** "X instead of Y, because Z." Without the why, the decision gets re-litigated next time.
- **Gotchas.** What surprised you, broke, or only worked with a trick. The most valuable part — it's in no documentation.
- **Status.** Where the thing stands now, in one sentence.
- **Open items.** What was deliberately left undone.
- **Pointers.** File paths, repos, URLs, commit SHAs. Paths, not contents.

Stays out: conversation history, code dumps (the code is in the repo), the obvious, anything derivable from `git log`.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/wrapup/scripts/wrapup.py" \
  --title "Marketplace Setup" --project claude-plugins --tags "marketplace,plugins" <<'EOF'
## Decisions
- Marketplace public instead of private, so outsiders can install without auth

## Gotchas
- Version pin blocks updates: without a bump, `plugin update` pulls nothing

## Status
- 4 plugins live
EOF
```

The body comes via stdin (or `--content-file PATH`). Empty body → exit 1, nothing written. The script creates the digest and inserts the index line at the top.

`--title` becomes the filename (non-ASCII is transliterated), `--project` and `--tags` make `recall` filterable. Both optional, both worth it.

## Recalling (session start or on demand)

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/wrapup/scripts/recall.py" version pin update
```

Output: ranked digests with path and matching lines. **Only then** open the relevant digest with `Read` — not all of them. Search terms are all lowercased; more terms matched ranks higher.

Options: `--project <name>` narrows to one project, `--limit N` (default 5) caps hits, `--context N` (default 2) the lines per hit.

No hit → say so and work without. Don't invent from memory what isn't in the store.

For "what did we do last time" without a specific search term: read `~/.claude/wrapup/INDEX.md` — the file is small enough to load whole.

## Optional: Notion mirror (recommended secondary store)

If you use Notion, this gives you full-text/semantic search across all sessions, phone access, and structured filters — via the **official** Notion API and the official MCP server. No browser hack, no undocumented endpoints.

Flow after the local write (the local digest is always the base):

1. **Find the database.** Read the cache: `~/.claude/wrapup/notion.json` (`{"data_source_id": "..."}`). File missing → search with `notion-search` for a "Claude Session Log" database, write `data_source_id` into the cache.
2. **If it doesn't exist at all**, offer to create it (don't do it unasked) — `notion-create-database`:
   ```
   CREATE TABLE ("Title" TITLE, "Date" DATE,
                 "Project" SELECT('other':gray),
                 "Tags" MULTI_SELECT('memory':purple, 'gotcha':red, 'decision':blue, 'setup':gray),
                 "Status" RICH_TEXT COMMENT 'One sentence: where the thing stands')
   ```
3. **Push** with `notion-create-pages`, `parent = {type: "data_source_id", data_source_id: <id>}`. Set the `Title`/`Date`/`Project`/`Tags`/`Status` properties, digest body as `content` (Markdown, without a title heading — the title lives in the properties).

The push runs agent-side via MCP, not in the script: a digest is a synthesis of the session — only the model can produce that, no script and no hook.

### Recall from Notion

Two ways, both verified:

- **`notion-search`** with a normal query — finds digests workspace-wide including the matching line. The fast default.
- **`notion-query-data-sources`** (SQL) for structured questions — "all sessions for project X, newest first":
  ```sql
  SELECT "Title", "date:Date:start" AS Date, "Status", url
  FROM "collection://<data_source_id>"
  WHERE "Project" = ? ORDER BY "date:Date:start" DESC LIMIT 5
  ```

Gotcha: `notion-search` with `data_source_url` (semantic search inside the DB) returned **empty** right after a page was created — the index needs time. Workspace search and SQL query work immediately. So don't rely on `data_source_url` for fresh digests.

## Alternative: NotebookLM

`--push-notebooklm` sends the digest to NotebookLM (Gemini Notebook) as a note instead — interesting only for its media features (audio/video overviews, infographics).

```bash
... | python ".../wrapup.py" --title "..." --push-notebooklm --notebook <id>
```

Requires the `notebooklm` CLI installed and logged in (`uv tool install notebooklm-py`, then `notebooklm login`). Without `--notebook` the active notebook applies, or set `WRAPUP_NOTEBOOK`. If the CLI is missing, the script reports `skipped` and the local digest still exists.

**Expectations:** `notebooklm-py` runs on undocumented Google endpoints; there is no public NotebookLM API (as of 08/2026, Enterprise only). Can break at any time. If you have Notion, use Notion.

**Ground rule for both:** the local store is the base, the mirror is a bonus. An external service must never be the only memory — otherwise it's gone when the provider changes something.

## Automatic instead of manual

The skill triggers on request. If you want the digest **always** at session end, you need a `Stop` hook in `settings.json` — hooks are executed by the harness, not the model. Ask about it if the user wants that; never install hooks unasked.
