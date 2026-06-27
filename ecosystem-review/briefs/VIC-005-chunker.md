# VIC-005 — Chunker (chunker.py)

**Status:** briefed · **Depends on:** VIC-004

## EXECUTOR
codex

## PROJECT CONTEXT

- Project root: `~/projects/victorique/`
- Package: `~/projects/victorique/src/victorique/`
- Venv: `~/projects/victorique/.venv/bin/python`
- DB module: `from victorique.core.db import get_connection, upsert_chunk`
- Vault parser: `from victorique.core.vault import parse_note`

## GOAL

Split parsed note bodies into overlapping chunks suitable for embedding.
Chunks are the unit of vector storage — everything semantic search operates on.

## FILES IT OWNS

```
~/projects/victorique/src/victorique/core/chunker.py   — CREATE
```

## DO NOT TOUCH

- `src/victorique/core/db.py`
- `src/victorique/core/vault.py`
- `src/victorique/config.py`
- `src/victorique/cli.py`

## IMPLEMENTATION

Create `src/victorique/core/chunker.py`.

### Constants

```python
MIN_WORDS = 50
MAX_WORDS = 400
HEADING_RE = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
CODE_BLOCK_RE = re.compile(r'```[\s\S]*?```', re.MULTILINE)
```

### chunk_note(note_id: str, body: str) -> list[dict]

Returns list of chunk dicts matching the `chunks` table schema.

**Algorithm:**

1. Strip code blocks from body before processing (replace with placeholder to preserve positions, but exclude from chunk content).
2. Split body at H2 and H3 headings. Each section = heading line + content until next heading.
3. If a section is < MIN_WORDS: merge with next section.
4. If a section is > MAX_WORDS: split at paragraph boundaries (blank lines), each paragraph segment up to MAX_WORDS.
5. Track `heading_path` for each chunk: the heading chain, e.g. `"## Projects > ### Boréal"`.
6. Skip chunks that are pure link lists (> 70% of non-blank lines start with `[[` or `-`).

For each chunk, compute:
```python
{
    "id": hashlib.sha1(f"{note_id}:{position}:{content[:100]}".encode()).hexdigest(),
    "note_id": note_id,
    "content": chunk_text,
    "content_hash": hashlib.sha1(chunk_text.encode()).hexdigest(),
    "heading_path": heading_path,
    "position": position,    # 0-indexed
    "word_count": len(chunk_text.split()),
    "start_char": start,
    "end_char": end,
    "embedded_at": None,
}
```

### chunk_and_store(note_id: str, body: str, conn) -> int

Call `chunk_note()`, then `upsert_chunk(conn, chunk)` for each result.
Return number of chunks stored.

If the note already has chunks with matching `content_hash` values, skip them (incremental).

### chunk_all_notes(conn) -> int

Query all `active` notes from DB that have `word_count > 30`.
For each: fetch body by re-reading the file (vault path from config), chunk and store.
Return total chunk count.

**Why re-read the file:** vault.py doesn't store the body in the DB (only the hash).
Use `conf.vault.path / note['path']` to re-read each file's body.

```python
import frontmatter as fm
def read_body(vault_root: Path, note_path: str) -> str:
    post = fm.load(str(vault_root / note_path))
    return post.content
```

## DONE LOOKS LIKE

1. `from victorique.core.chunker import chunk_note` imports cleanly
2. A 2000-word note with 4 H2 sections produces 4–6 chunks
3. Each chunk is 50–400 words
4. `chunk_all_notes(conn)` runs without errors after `victorique index`

## VERIFY WITH

```bash
cd ~/projects/victorique

.venv/bin/python -c "
from victorique.core.chunker import chunk_note

# Synthetic test
body = '''
## Introduction
This is the first section. ''' + ' word' * 60 + '''

## Background  
This is the second section. ''' + ' word' * 80 + '''

## Methods
This is the third section. ''' + ' word' * 70 + '''
'''

chunks = chunk_note('test-note-id', body)
print(f'Chunks: {len(chunks)}')
for c in chunks:
    print(f'  pos={c[\"position\"]} words={c[\"word_count\"]} heading={c[\"heading_path\"]}')
assert len(chunks) >= 2, f'Expected >= 2 chunks, got {len(chunks)}'
print('CHUNKER OK')
"
```

Expected: 3 chunks (one per H2 section), each 50-400 words.

## OUT OF SCOPE

- Embedding (VIC-006)
- Any vault writes
- Entity extraction
