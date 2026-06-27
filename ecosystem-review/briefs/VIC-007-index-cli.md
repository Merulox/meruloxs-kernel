# VIC-007 — CLI: victorique index (Full Pipeline)

**Status:** briefed · **Depends on:** VIC-004, VIC-005, VIC-006

## EXECUTOR
codex

## PROJECT CONTEXT

- Project root: `~/projects/victorique/`
- Venv: `~/projects/victorique/.venv/bin/python`
- `victorique` CLI already installed (editable install from VIC-002)
- `cli.py` already stubs out the `index` command — just needs the real implementation
- Modules built in previous tasks:
  - `from victorique.core.db import init_db`
  - `from victorique.core.vault import parse_vault, read_body`  
  - `from victorique.core.chunker import chunk_and_store`
  - `from victorique.core.embedder import embed_chunks, check_ollama`

## GOAL

Wire the `victorique index` CLI command to chain all three pipeline stages:
vault parse → chunking → embedding.

## FILES IT OWNS

```
~/projects/victorique/src/victorique/core/vault.py   — EDIT: update index_vault() function
```

The `index` command in `cli.py` already calls `from victorique.core.vault import index_vault`.
So the entry point lives in `vault.py`.

## DO NOT TOUCH

- `src/victorique/cli.py` — do not modify; it already has the correct stub
- `src/victorique/core/db.py`
- `src/victorique/core/chunker.py`
- `src/victorique/core/embedder.py`

## IMPLEMENTATION

Update the `index_vault()` function in `src/victorique/core/vault.py`:

```python
def index_vault(incremental: bool = False, stats_only: bool = False) -> None:
    from rich.console import Console
    from victorique.config import load
    from victorique.core.db import init_db
    from victorique.core.chunker import chunk_and_store, read_body
    from victorique.core.embedder import embed_chunks, check_ollama

    conf = load()
    console = Console()
    conn = init_db(conf.storage.db_path)

    if stats_only:
        note_count = conn.execute("SELECT COUNT(*) FROM notes WHERE status='active'").fetchone()[0]
        chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        embedded = conn.execute("SELECT COUNT(*) FROM chunks WHERE embedded_at IS NOT NULL").fetchone()[0]
        console.print(f"Notes: {note_count}")
        console.print(f"Chunks: {chunk_count}")
        console.print(f"Embedded: {embedded}/{chunk_count}")
        conn.close()
        return

    # Stage 1: parse vault → notes table
    console.print("[bold]Stage 1/3:[/bold] Parsing vault notes...")
    note_count = parse_vault(conf.vault.path, conn, incremental=incremental)
    conn.commit()
    console.print(f"  {note_count} notes indexed")

    # Stage 2: chunk notes
    console.print("[bold]Stage 2/3:[/bold] Chunking notes...")
    chunk_count = chunk_all_notes(conn, conf.vault.path, incremental=incremental)
    conn.commit()
    console.print(f"  {chunk_count} chunks created")

    # Stage 3: embed chunks
    if not check_ollama():
        console.print("[yellow]Ollama not running — skipping embedding. Run: systemctl --user start ollama[/yellow]")
    else:
        console.print("[bold]Stage 3/3:[/bold] Embedding chunks (Ollama)...")
        embedded = embed_chunks(conn, conf.storage.lancedb_path)
        conn.commit()
        console.print(f"  {embedded} chunks embedded")

    conn.close()
    console.print("[green]Index complete.[/green]")
```

Also ensure `chunk_all_notes(conn, vault_root: Path, incremental: bool = False) -> int` is
implemented in `chunker.py` — if it's not, add it there. It should:
- Query all active notes from DB
- For each note: read body from vault file, chunk, upsert chunks
- For incremental: skip notes where all chunks have `embedded_at IS NOT NULL` and `body_hash` unchanged
- Return total chunk count

And `parse_vault()` must accept `incremental` param:
- For incremental: skip notes where `body_hash` matches the current file hash

## DONE LOOKS LIKE

1. `victorique index` runs end-to-end without errors
2. `victorique index --incremental` skips unchanged notes
3. `victorique stats` shows note count, chunk count, embedding coverage

## VERIFY WITH

```bash
cd ~/projects/victorique

# Full index run (first time — may take several minutes)
.venv/bin/victorique index 2>&1

# Confirm stats
.venv/bin/victorique stats

# Incremental should be fast (nothing changed)
time .venv/bin/victorique index --incremental 2>&1 | tail -5
```

Expected:
- Full index: `Index complete.` with note/chunk/embedding counts
- `victorique stats` shows note_count > 100, chunk_count > 200
- Incremental run: fast (seconds), prints `0 notes indexed` or similar

## OUT OF SCOPE

- Semantic search (VIC-008)
- Entity extraction (VIC-010)
- Any vault writes
