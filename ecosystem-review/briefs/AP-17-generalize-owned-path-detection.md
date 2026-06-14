# AP-17 — Generalize owned-path detection (stop dropping `web/`, `docs/`, etc.)

**Loop:** A and B (executor-pipeline correctness — prevents silent loss of owned files)
**Priority:** P0 · **Safety:** changes path parsing used by work-roots + applyCommit; aperture-only
**Status:** briefed · **Depends on:** AP-12, AP-15 · **Runs through the executor**

## GOAL
`ownedPathTokens` recognizes any owned file a brief lists, regardless of its top-level directory — not just `src/`/`api/`. This fixes both the writable-roots derivation and `applyCommit`'s staging so files under `web/`, `docs/`, `scripts/`, `lib/`, etc. are committed instead of silently dropped.

## WHY
Measured on S-19 (SYNTRA): the brief owned `src/supabase.js`, `src/server/index.js`, **`web/src/main.jsx`**, and `docs/planning/task-s19-paginate-catalog.md`. The executor implemented all four; the orchestrator committed only the two `src/` files. The client infinite-scroll (`web/src/main.jsx`) was **silently left uncommitted** — and the second run logged `commit S-19: no changes`, masking the loss. Root cause is the `pathLike` allowlist in `ownedPathTokens` (launch-codex.ts ~line 88):

```js
const pathLike = /^(?:~\/|\/|\.{1,2}\/|src\/|api\/|package\.json$|astro\.config\.mjs$|\.gitignore$)/;
```

It only accepts tokens that start with `~/ · / · ./ · ../ · src/ · api/` or a few hardcoded filenames. `web/src/main.jsx` starts with `web/` → rejected; `docs/...` → rejected. So `resolvedOwnedPaths` never returns them, `git add` never stages them, and they vanish from the commit. This is the same silent-loss class AP-13/AP-16 fought, one layer down: any repo whose layout isn't aperture's `src/` convention loses owned files. The architect caught S-19's main.jsx by inspection and committed it manually (0fa7866) — the pipeline must not depend on that.

## FILES IT OWNS
- `~/projects/aperture/src/pages/api/launch-codex.ts` (`ownedPathTokens` — the `pathLike` test; nothing else)

## DO NOT TOUCH
- `resolvedOwnedPaths`, `applyCommit`, `isExcludedCommitPath`, work-root grouping (they're correct — they just never receive the dropped tokens)
- The `ownedPrefix` split on ` — `/`(`/`--` (line ~94) — it already isolates the path from the description; keep it
- The classifier / restart logic

## SPEC
Generalize `pathLike` so a token extracted from the **ownedPrefix** (already description-stripped) is treated as a path when it is plausibly one, while still rejecting prose. Accept a token if ANY:
- starts with `~/`, `/`, `./`, `../` (existing absolute/explicit cases), OR
- is a **relative path containing a slash** — matches `^[\w.@-]+\/\S+` (covers `web/src/main.jsx`, `docs/planning/x.md`, `scripts/prerender.js`, `lib/foo.ts`), OR
- is a **bare filename with a known extension**: `\.(?:js|jsx|ts|tsx|mjs|cjs|json|md|mdx|css|scss|astro|py|yaml|yml|toml|sh|sql|txt|html|env)$` (covers `package.json`, `astro.config.mjs`, top-level configs without needing to enumerate them).

Notes:
- This widening is safe because non-existent resolved paths return `[]` via `filesUnder`, and `isExcludedCommitPath` still blocks `*.db`/`*.sqlite*`/`*.bak-*`/non-text boreal-leads files. A description fragment that sneaks through (e.g. `filters/facets`) simply resolves to nothing.
- Keep extracting from `ownedPrefix` only (don't scan the post-`—` description), so prose after the dash can't inject paths.
- Drop the hardcoded `src/`/`api/`/`package.json`/`astro.config.mjs`/`.gitignore` special-cases — they're subsumed by the rules above.

## DONE LOOKS LIKE
1. For the S-19 brief, `resolvedOwnedPaths` returns all four owned paths (the two `src/` files, `web/src/main.jsx`, `docs/planning/task-s19-paginate-catalog.md`).
2. A brief owning a `web/` or `scripts/` file, run to a clean `done`, produces a commit that **includes** that file.
3. Existing aperture/agent-infra briefs (owning `src/...`, `~/scripts/...`) still resolve exactly as before.
4. No path after the ` — ` description separator is treated as owned.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
node --experimental-strip-types --input-type=module -e "
import { ownedPathTokens } from './src/pages/api/launch-codex.ts';
import { readFileSync } from 'node:fs';
const s19 = readFileSync('/home/merulox/syntra/docs/planning/task-s19-paginate-catalog.md','utf8');
console.log('S-19 tokens:', ownedPathTokens(s19));
// expect: includes src/supabase.js, src/server/index.js, web/src/main.jsx, docs/planning/task-s19-paginate-catalog.md
const ap = readFileSync('/home/merulox/agent-infra/ecosystem-review/briefs/AP-17-generalize-owned-path-detection.md','utf8');
console.log('AP-17 tokens:', ownedPathTokens(ap));  // expect the launch-codex.ts path only
"
# Dogfood: relaunch any web/-touching task; confirm the web file lands in the [executor] commit.
```
(If `ownedPathTokens` isn't exported, export it — test-only export is acceptable.)

## OUT OF SCOPE
- Re-committing S-19's main.jsx (architect already did: 0fa7866)
- Any change to commit message format, push policy, or restart logic
- Detecting owned files the brief didn't list
