# VIC-004 — Vault Parser (vault.py)

**Status:** briefed · **Depends on:** VIC-003

## EXECUTOR
codex

## PROJECT CONTEXT

- Project root: `~/projects/victorique/`
- Package: `~/projects/victorique/src/victorique/`
- Venv: `~/projects/victorique/.venv/bin/python`
- Vault: `~/obsidian/` (READ ONLY — never write to it)
- DB: `~/.local/share/victorique/vault.db`
- Config: `~/projects/victorique/src/victorique/config.py` (already exists — `from victorique.config import load` to get config)
- DB module: `from victorique.core.db import init_db, upsert_note, get_connection` (built in VIC-003)

## GOAL

Walk the Obsidian vault, parse every `.md` file (frontmatter + body), extract metadata,
and upsert note records into the SQLite DB. This is the read path — no vault writes ever.

## FILES IT OWNS

```
~/projects/victorique/src/victorique/core/vault.py   — CREATE
```

`~/projects/victorique/src/victorique/core/__init__.py` already exists. Do not modify it.

## DO NOT TOUCH

- `~/obsidian/` — read-only, never write
- `src/victorique/config.py`
- `src/victorique/cli.py`
- `src/victorique/core/db.py`

## IMPLEMENTATION

Create `src/victorique/core/vault.py`.

### Excluded directories (skip entirely)

```python
EXCLUDED_DIRS = {
    "context-bundle", "attachments", "claude-bus",
    "anime", ".obsidian", "_archive", "templates",
}
```

Skip any directory in this set during walk (prune from os.walk).

### Noise detection

A note is noise if:
- Its parent directory is in EXCLUDED_DIRS
- Word count < 30
- Filename starts with `_` or `.`
- It has tag `#noise` or `#template` in frontmatter

### parse_note(path: Path, vault_root: Path) -> dict | None

Returns None if the note is noise. Otherwise returns a dict matching the `notes` table schema:

```python
{
    "id": sha1(vault_relative_path),     # hashlib.sha1(str(rel_path).encode()).hexdigest()
    "path": str(rel_path),               # e.g. "projects/boreal.md"
    "title": extract_title(content, path), # first H1 or filename without extension
    "frontmatter": json.dumps(fm_dict),
    "tags": json.dumps(tags),            # merge frontmatter tags + inline #tags from body
    "body_hash": sha1(body_text),        # sha1 of body only (after frontmatter stripped)
    "word_count": len(body_text.split()),
    "backlinks_out": json.dumps(wikilinks), # all [[wikilinks]] found in body
    "backlinks_in": "[]",               # filled in second pass
    "created_at": fm_dict.get("created") or iso_from_stat(path.stat().st_ctime),
    "modified_at": fm_dict.get("updated") or fm_dict.get("modified") or iso_from_stat(path.stat().st_mtime),
    "indexed_at": datetime.utcnow().isoformat(),
    "deleted_at": None,
    "status": "active",
}
```

Use `python-frontmatter` (`import frontmatter`) to parse. It splits frontmatter and body.

Extract wikilinks with regex: `\[\[([^\]|]+)(?:\|[^\]]+)?\]\]` — capture group 1 is the target.
Extract inline tags with regex: `(?<!\w)#([a-zA-Z][a-zA-Z0-9_/-]*)` — skip tags inside code blocks.

### parse_vault(vault_path: Path, conn) -> int

Walk `vault_path` (from config), skip EXCLUDED_DIRS, parse every `.md`, upsert to DB.
Return note count. Print progress with `rich.progress.track()`.

After upserting all notes, do a second pass to populate `backlinks_in`:
- Build a map: target_path_stem → [note_ids that link to it]
- For each note, update `backlinks_in` = JSON array of note IDs linking to it

### index_vault(incremental: bool = False, stats_only: bool = False) -> None

This is the entry point called by `cli.py`'s `index` command.

```python
def index_vault(incremental: bool = False, stats_only: bool = False) -> None:
    from victorique.config import load
    from victorique.core.db import init_db, get_connection
    conf = load()
    conn = init_db(conf.storage.db_path)
    if stats_only:
        # print note count, word count total from DB and return
        ...
        return
    count = parse_vault(conf.vault.path, conn)
    conn.commit()
    conn.close()
    print(f"Indexed {count} notes.")
```

For `incremental=True`: only parse notes where `modified_at` (from filesystem) is newer than
`indexed_at` in the DB. Skip notes with unchanged `body_hash`.

## DONE LOOKS LIKE

1. `victorique index` runs without errors on the real vault
2. `victorique stats` shows note count > 0
3. `~/projects/victorique/.venv/bin/python -c "from victorique.core.vault import parse_note"` imports cleanly

## VERIFY WITH

```bash
cd ~/projects/victorique

# Unit test: parse a single real note
.venv/bin/python -c "
from victorique.core.vault import parse_note
from pathlib import Path
vault = Path.home() / 'obsidian'
note = next(vault.rglob('*.md'), None)
if note:
    result = parse_note(note, vault)
    if result:
        print('title:', result['title'])
        print('word_count:', result['word_count'])
        print('tags:', result['tags'])
        print('backlinks_out:', result['backlinks_out'])
        print('PARSE OK')
    else:
        print('note was noise (ok if small)')
else:
    print('no .md files found')
"

# Full index test (safe — read-only)
.venv/bin/victorique index 2>&1 | tail -5
.venv/bin/victorique stats
```

Expected: note count > 100, no errors.

## OUT OF SCOPE

- Chunking (VIC-005)
- Embedding (VIC-006)
- Any write to ~/obsidian/
