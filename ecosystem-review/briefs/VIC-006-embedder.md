# VIC-006 — Ollama Embedding Pipeline (embedder.py)

**Status:** briefed · **Depends on:** VIC-005

## EXECUTOR
codex

## PROJECT CONTEXT

- Project root: `~/projects/victorique/`
- Venv: `~/projects/victorique/.venv/bin/python`
- Ollama: running as systemd service on `http://localhost:11434` — `ollama list` to verify
- Embedding model: `nomic-embed-text` (768 dimensions) — `ollama pull nomic-embed-text` if missing
- LanceDB data dir: `~/.local/share/victorique/lancedb/`
- SQLite DB: `~/.local/share/victorique/vault.db`
- httpx is available in the venv (for Ollama API calls)

## GOAL

Embed all unembedded chunks via Ollama and store vectors in LanceDB.
Update `chunks.embedded_at` in SQLite when done.

## FILES IT OWNS

```
~/projects/victorique/src/victorique/core/embedder.py   — CREATE
```

## DO NOT TOUCH

- `src/victorique/core/db.py`
- `src/victorique/core/vault.py`
- `src/victorique/core/chunker.py`
- Any vault files

## IMPLEMENTATION

Create `src/victorique/core/embedder.py`.

### Dependencies already in venv

```python
import httpx          # for Ollama API
import lancedb        # vector store
import pyarrow as pa  # schema
```

### LanceDB schema

```python
LANCE_SCHEMA = pa.schema([
    pa.field("id", pa.utf8()),
    pa.field("note_id", pa.utf8()),
    pa.field("note_title", pa.utf8()),
    pa.field("heading_path", pa.utf8()),
    pa.field("content", pa.utf8()),
    pa.field("vector", pa.list_(pa.float32(), 768)),
    pa.field("word_count", pa.int32()),
    pa.field("modified_at", pa.utf8()),
    pa.field("tags", pa.utf8()),
])
```

### embed_text(text: str) -> list[float]

POST to `http://localhost:11434/api/embeddings` with:
```json
{"model": "nomic-embed-text", "prompt": "<text>"}
```
Return `response["embedding"]` (list of 768 floats).
Raise `RuntimeError` if Ollama is not reachable or model not found.

### embed_chunks(conn, lancedb_path: Path, batch_size: int = 20) -> int

1. Open LanceDB at `lancedb_path`. Create table `chunks` with `LANCE_SCHEMA` if it doesn't exist.
2. Query SQLite: `SELECT c.*, n.title, n.tags, n.modified_at FROM chunks c JOIN notes n ON n.id = c.note_id WHERE c.embedded_at IS NULL`
3. Process in batches of `batch_size`:
   - Embed each chunk's content
   - Build LanceDB records (join with note metadata)
   - Upsert to LanceDB table (mode="overwrite" on the batch's IDs, or use `tbl.merge_insert`)
   - Mark each chunk embedded: `UPDATE chunks SET embedded_at = ? WHERE id = ?`
   - Commit SQLite after each batch
4. Show progress with `rich.progress.track()`.
5. Return total embedded count.

**LanceDB upsert pattern** — add records using:
```python
db = lancedb.connect(str(lancedb_path))
if "chunks" not in db.table_names():
    tbl = db.create_table("chunks", schema=LANCE_SCHEMA)
else:
    tbl = db.open_table("chunks")
tbl.add(records)  # list of dicts matching LANCE_SCHEMA
```

For incremental runs, chunks already in LanceDB (embedded_at is NOT NULL in SQLite) are skipped.

### check_ollama() -> bool

GET `http://localhost:11434/api/tags` — return True if 200 and `nomic-embed-text` in model list.
Print a clear error and return False if not reachable.

## DONE LOOKS LIKE

1. `from victorique.core.embedder import embed_chunks, check_ollama` imports cleanly
2. `check_ollama()` returns True (Ollama is running with nomic-embed-text)
3. After running embed_chunks on a test DB, LanceDB table `chunks` contains vectors
4. SQLite `chunks.embedded_at` is updated for embedded chunks

## VERIFY WITH

```bash
# 1. Confirm Ollama is running and model present
ollama list | grep nomic-embed-text

# 2. Sanity test: embed a string
cd ~/projects/victorique
.venv/bin/python -c "
from victorique.core.embedder import embed_text, check_ollama
ok = check_ollama()
print('Ollama OK:', ok)
if ok:
    vec = embed_text('test sentence about consciousness and perception')
    print('Vector dims:', len(vec))
    assert len(vec) == 768, f'Expected 768 dims, got {len(vec)}'
    print('EMBED OK')
"
```

Expected: `Ollama OK: True`, `Vector dims: 768`, `EMBED OK`

If Ollama is not running: `systemctl --user start ollama` (or `sudo systemctl start ollama`).
If model missing: `ollama pull nomic-embed-text`

## OUT OF SCOPE

- Semantic search (VIC-008)
- Re-embedding already-embedded chunks (incremental is skip-based, not force-re-embed)
- Similarity search — LanceDB query is in VIC-008
