# VIC-003 — SQLite Schema + db.py

**Status:** briefed · **Depends on:** VIC-002 (done)

## EXECUTOR
codex

## PROJECT CONTEXT

- Project root: `~/projects/victorique/`
- Package: `~/projects/victorique/src/victorique/`
- Venv: `~/projects/victorique/.venv/` — all Python: `~/projects/victorique/.venv/bin/python`
- Data dir (runtime): `~/.local/share/victorique/`
- Install (editable): already done — `pip install -e .` was run during VIC-002

## GOAL

Implement the SQLite database schema and helper module. This is the foundation — all subsequent
Victorique tasks read and write to this DB.

## FILES IT OWNS

```
~/projects/victorique/src/victorique/core/db.py   — CREATE
```

The `~/projects/victorique/src/victorique/core/__init__.py` already exists. Do not overwrite it.

## DO NOT TOUCH

- Any file outside `~/projects/victorique/`
- `src/victorique/config.py`
- `src/victorique/cli.py`
- `src/telegram/`

## IMPLEMENTATION

Create `src/victorique/core/db.py` with:

### Public API

```python
def init_db(db_path: Path) -> sqlite3.Connection
    """Create schema if not exists, run migrations, return connection."""

def get_connection(db_path: Path) -> sqlite3.Connection
    """Return a connection with row_factory = sqlite3.Row."""

def upsert_note(conn, note: dict) -> None
def upsert_chunk(conn, chunk: dict) -> None
def get_note_by_path(conn, path: str) -> sqlite3.Row | None
def get_chunks_for_note(conn, note_id: str) -> list[sqlite3.Row]
def mark_chunk_embedded(conn, chunk_id: str, embedded_at: str) -> None
```

### Schema — create these tables in init_db()

Use `CREATE TABLE IF NOT EXISTS` for all tables. Use `PRAGMA journal_mode=WAL` and
`PRAGMA foreign_keys=ON` on every connection.

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    id           TEXT PRIMARY KEY,
    path         TEXT UNIQUE NOT NULL,
    title        TEXT NOT NULL,
    frontmatter  TEXT,
    tags         TEXT,
    body_hash    TEXT,
    word_count   INTEGER,
    backlinks_out TEXT,
    backlinks_in  TEXT,
    created_at   TEXT,
    modified_at  TEXT,
    indexed_at   TEXT,
    deleted_at   TEXT,
    status       TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS chunks (
    id            TEXT PRIMARY KEY,
    note_id       TEXT NOT NULL REFERENCES notes(id),
    content       TEXT NOT NULL,
    content_hash  TEXT NOT NULL,
    heading_path  TEXT,
    position      INTEGER NOT NULL,
    word_count    INTEGER,
    start_char    INTEGER,
    end_char      INTEGER,
    embedded_at   TEXT
);

CREATE TABLE IF NOT EXISTS entities (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    type          TEXT NOT NULL,
    canonical     TEXT,
    aliases       TEXT,
    first_seen    TEXT,
    last_seen     TEXT,
    mention_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS entity_mentions (
    id            TEXT PRIMARY KEY,
    entity_id     TEXT NOT NULL REFERENCES entities(id),
    note_id       TEXT NOT NULL REFERENCES notes(id),
    chunk_id      TEXT REFERENCES chunks(id),
    context       TEXT,
    sentiment     TEXT,
    mentioned_at  TEXT
);

CREATE TABLE IF NOT EXISTS themes (
    id            TEXT PRIMARY KEY,
    label         TEXT NOT NULL,
    description   TEXT,
    note_ids      TEXT NOT NULL,
    centroid_id   TEXT,
    confidence    REAL NOT NULL,
    evidence      TEXT,
    created_at    TEXT,
    last_updated  TEXT,
    status        TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS projects (
    id             TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    status         TEXT NOT NULL,
    note_ids       TEXT NOT NULL,
    first_activity TEXT,
    last_activity  TEXT,
    momentum_score REAL,
    stall_days     INTEGER,
    description    TEXT,
    evidence       TEXT,
    detected_at    TEXT,
    user_confirmed BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS claims (
    id            TEXT PRIMARY KEY,
    note_id       TEXT NOT NULL REFERENCES notes(id),
    chunk_id      TEXT REFERENCES chunks(id),
    text          TEXT NOT NULL,
    topic         TEXT,
    polarity      TEXT,
    certainty     TEXT,
    evidence_type TEXT,
    confidence    REAL NOT NULL,
    created_at    TEXT
);

CREATE TABLE IF NOT EXISTS contradictions (
    id             TEXT PRIMARY KEY,
    claim_a_id     TEXT NOT NULL REFERENCES claims(id),
    claim_b_id     TEXT NOT NULL REFERENCES claims(id),
    description    TEXT NOT NULL,
    conflict_type  TEXT,
    time_gap_days  INTEGER,
    confidence     REAL NOT NULL,
    status         TEXT DEFAULT 'open',
    resolution     TEXT,
    detected_at    TEXT
);

CREATE TABLE IF NOT EXISTS open_loops (
    id             TEXT PRIMARY KEY,
    note_id        TEXT NOT NULL REFERENCES notes(id),
    chunk_id       TEXT REFERENCES chunks(id),
    description    TEXT NOT NULL,
    loop_type      TEXT NOT NULL,
    first_seen     TEXT,
    last_mentioned TEXT,
    mention_count  INTEGER DEFAULT 1,
    note_ids       TEXT,
    status         TEXT DEFAULT 'open',
    confidence     REAL NOT NULL,
    detected_at    TEXT
);

CREATE TABLE IF NOT EXISTS research_questions (
    id              TEXT PRIMARY KEY,
    text            TEXT NOT NULL,
    origin_note_ids TEXT,
    status          TEXT DEFAULT 'open',
    sub_questions   TEXT,
    dossier_path    TEXT,
    created_at      TEXT,
    last_activity   TEXT
);

CREATE TABLE IF NOT EXISTS suggested_backlinks (
    id              TEXT PRIMARY KEY,
    note_a_id       TEXT NOT NULL REFERENCES notes(id),
    note_b_id       TEXT NOT NULL REFERENCES notes(id),
    reason          TEXT NOT NULL,
    connection_type TEXT,
    similarity      REAL,
    confidence      REAL NOT NULL,
    status          TEXT DEFAULT 'pending',
    created_at      TEXT,
    reviewed_at     TEXT
);

CREATE TABLE IF NOT EXISTS generated_insights (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL,
    title           TEXT,
    content         TEXT NOT NULL,
    citations       TEXT NOT NULL,
    confidence      REAL NOT NULL,
    inference_level TEXT,
    agent_mode      TEXT,
    status          TEXT DEFAULT 'new',
    created_at      TEXT,
    reviewed_at     TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
    id              TEXT PRIMARY KEY,
    item_type       TEXT NOT NULL,
    item_id         TEXT,
    action_class    TEXT NOT NULL,
    description     TEXT NOT NULL,
    content_preview TEXT,
    diff_preview    TEXT,
    confidence      REAL,
    citations       TEXT,
    status          TEXT DEFAULT 'pending',
    created_at      TEXT NOT NULL,
    expires_at      TEXT,
    reviewed_at     TEXT,
    decision_note   TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
    id           TEXT PRIMARY KEY,
    timestamp    TEXT NOT NULL,
    agent_mode   TEXT,
    action_class TEXT NOT NULL,
    action_type  TEXT NOT NULL,
    target       TEXT,
    input_hash   TEXT,
    output_id    TEXT,
    approved_by  TEXT,
    result       TEXT NOT NULL,
    error_msg    TEXT,
    duration_ms  INTEGER
);
```

### Migration system

Migrations are additive SQL statements keyed by version integer.
On `init_db()`, check current version in `schema_version`, apply any missing migrations in order.
For MVP the migration dict is empty — all tables are created by the initial schema above.
Version 0 = tables created. Record `INSERT OR IGNORE INTO schema_version VALUES (0, <now>)` after schema creation.

### upsert helpers

- `upsert_note(conn, note: dict)`: INSERT OR REPLACE into notes
- `upsert_chunk(conn, chunk: dict)`: INSERT OR REPLACE into chunks
- `get_note_by_path(conn, path: str)`: SELECT WHERE path = ?
- `get_chunks_for_note(conn, note_id: str)`: SELECT WHERE note_id = ? ORDER BY position
- `mark_chunk_embedded(conn, chunk_id: str, embedded_at: str)`: UPDATE chunks SET embedded_at = ?

## DONE LOOKS LIKE

1. `~/projects/victorique/.venv/bin/python -c "from victorique.core.db import init_db; from pathlib import Path; c = init_db(Path('/tmp/vic-test.db')); print(c.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()); c.close()"` prints all 14 table names
2. No import errors
3. `rm /tmp/vic-test.db` to clean up

## VERIFY WITH

```bash
cd ~/projects/victorique
.venv/bin/python -c "
from victorique.core.db import init_db, upsert_note, get_note_by_path
from pathlib import Path
import datetime
c = init_db(Path('/tmp/vic-test.db'))
tables = [r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\").fetchall()]
print('Tables:', tables)
assert 'notes' in tables and 'chunks' in tables and 'audit_events' in tables and 'schema_version' in tables
upsert_note(c, {'id': 'abc', 'path': 'test.md', 'title': 'Test', 'frontmatter': '{}', 'tags': '[]', 'body_hash': 'x', 'word_count': 10, 'backlinks_out': '[]', 'backlinks_in': '[]', 'created_at': None, 'modified_at': None, 'indexed_at': datetime.datetime.utcnow().isoformat(), 'deleted_at': None, 'status': 'active'})
c.commit()
row = get_note_by_path(c, 'test.md')
assert row is not None and row['title'] == 'Test'
c.close()
import os; os.unlink('/tmp/vic-test.db')
print('ALL CHECKS PASSED')
"
```

Expected: `ALL CHECKS PASSED`

## OUT OF SCOPE

- LanceDB schema — that's in VIC-006
- Any vault file reading
- Entity extraction, theme detection, or any analysis
