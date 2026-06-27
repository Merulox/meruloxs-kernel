# VIC-008 — CLI: victorique search (Semantic Search)

**Status:** briefed · **Depends on:** VIC-006

## EXECUTOR
codex

## PROJECT CONTEXT

- Project root: `~/projects/victorique/`
- Venv: `~/projects/victorique/.venv/bin/python`
- LanceDB: `~/.local/share/victorique/lancedb/` — table `chunks` (populated by VIC-006)
- SQLite: `~/.local/share/victorique/vault.db`
- `cli.py` already has the `search` command stub calling `from victorique.core.search import semantic_search`
- `cli.py` also has the `ask` command calling `from victorique.core.search import ask_vault`
- Anthropic key: `~/.secrets/anthropic-api-key.txt`

## GOAL

Implement semantic search: embed a query → ANN search in LanceDB → return cited results.
Also implement `ask_vault()` for the `victorique ask` command (basic cited Q&A via Claude).

## FILES IT OWNS

```
~/projects/victorique/src/victorique/core/search.py   — CREATE
```

## DO NOT TOUCH

- `src/victorique/cli.py`
- `src/victorique/core/embedder.py`
- `src/victorique/core/db.py`

## IMPLEMENTATION

Create `src/victorique/core/search.py`.

### SearchResult dataclass

```python
from dataclasses import dataclass

@dataclass
class SearchResult:
    note_id: str
    note_title: str
    note_path: str
    chunk_id: str
    score: float           # cosine similarity (0.0–1.0)
    excerpt: str           # first 300 chars of chunk content
    heading_path: str
```

### semantic_search(query: str, limit: int = 5, threshold: float = 0.6) -> list[SearchResult]

1. Embed query: `from victorique.core.embedder import embed_text; vec = embed_text(query)`
2. Open LanceDB, open table `chunks`
3. ANN search: `results = tbl.search(vec).limit(limit * 2).to_list()`
   - LanceDB returns `_distance` (lower = more similar for L2) or `_relevance_score` depending on metric
   - Convert distance to similarity: `score = max(0.0, 1.0 - result["_distance"] / 2.0)` for L2
4. Filter by `score >= threshold`, take top `limit`
5. Build `SearchResult` objects from LanceDB fields (chunk already has note_title, note_id etc.)
6. Return sorted by score descending

If LanceDB table doesn't exist or is empty: return empty list (don't crash).

### ask_vault(query: str) -> str

1. Get top 10 search results (no threshold filter for context retrieval)
2. Build context string with citations:
   ```
   [1] "{note_title}" ({note_path})
   {chunk content}
   
   [2] "{note_title}" ({note_path})
   {chunk content}
   ...
   ```
3. Call Claude API with system prompt enforcing citations:
   ```
   System: You are Victorique, a vault intelligence layer. Answer only from the provided vault
   excerpts. Every non-trivial claim must cite the source note using [N] notation.
   If the answer is not in the excerpts, say so explicitly.
   ```
4. Read key from `~/.secrets/anthropic-api-key.txt`
5. Use model `claude-sonnet-4-6`, max_tokens 1024
6. Return the response text

If no search results: return `"No relevant notes found for this query."`

### Claude API call (stdlib only — no anthropic SDK needed)

```python
import urllib.request
import json

def _call_claude(system: str, user: str, api_key: str) -> str:
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["content"][0]["text"]
```

## DONE LOOKS LIKE

1. `victorique search "consciousness perception"` returns results with note titles and excerpts
2. `victorique ask "what do my notes say about focus and ADHD?"` returns a cited answer
3. Empty results handled gracefully (no crash)

## VERIFY WITH

```bash
cd ~/projects/victorique

# Semantic search
.venv/bin/victorique search "focus concentration environment"

# Should print: note title, path, similarity score, excerpt
# Expected: at least 1 result if index is built

# Ask command (requires Anthropic key)
.venv/bin/victorique ask "what themes come up most in my notes about consciousness?"
```

If no results: run `victorique index` first to build the index.

## OUT OF SCOPE

- Entity-aware search (VIC-010+)
- Dashboard search UI (VIC-019)
- Belief drift or contradiction detection
