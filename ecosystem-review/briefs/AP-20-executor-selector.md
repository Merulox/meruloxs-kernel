# AP-20 — Executor selector field in briefs + Aperture routing

## GOAL
Each brief declares which executor should run it; Aperture's launch UI reads that field and shows the correct launch button.

## WHY
With two executors available (Codex via Aperture, OpenCode via terminal), the launch decision is currently implicit. Architects choose at runtime based on memory. The brief should be the authority — routing must be explicit, not ambient.

## FILES IT OWNS
- `~/kernel/templates/brief.md` — add `## EXECUTOR` field
- `~/projects/aperture/src/lib/tasks.ts` — parse `EXECUTOR` field from brief markdown
- `~/projects/aperture/src/pages/tasks.tsx` — show executor badge on each task card
- `~/projects/aperture/src/pages/api/launch-codex.ts` — guard: reject launch if `EXECUTOR: opencode` (task must be run manually)

## DO NOT TOUCH
- Any brief file in `~/kernel/ecosystem-review/briefs/` — architect updates those manually
- `~/kernel/agents/` — role definitions are out of scope
- `crm.db` or any database
- Any `.env` or `~/.secrets/` file

## EXECUTOR FIELD SPEC
Add to brief template after `## OUT OF SCOPE`:

```markdown
## EXECUTOR
codex | opencode | either
```

Defaults to `codex` if the field is absent (backwards-compatible).
- `codex` — launched via Aperture's "Launch Codex" button (current behavior)
- `opencode` — must be run manually from terminal: `cd <workroot> && opencode`; Aperture shows a badge but no launch button
- `either` — both buttons active

## DONE LOOKS LIKE
1. `~/kernel/templates/brief.md` has `## EXECUTOR` field with valid values documented
2. Aperture task cards show an executor badge: `[CODEX]`, `[OPENCODE]`, or `[EITHER]` next to task status
3. Tasks with `EXECUTOR: opencode` show a disabled "Launch Codex" button with tooltip "Run manually: cd <workroot> && opencode"
4. Tasks with `EXECUTOR: codex` (or absent field) behave identically to current behavior
5. `tasks.ts` unit-parseable: `parseExecutor(briefMarkdown)` returns one of `"codex" | "opencode" | "either"` with `"codex"` as default

## VERIFY WITH
```bash
# 1. Template has EXECUTOR field
grep -n "EXECUTOR" ~/kernel/templates/brief.md

# 2. Parser exists and handles missing field
cd ~/projects/aperture && node -e "
const {parseExecutor} = require('./src/lib/tasks.ts');
console.assert(parseExecutor('## GOAL\nfoo') === 'codex', 'missing field default failed');
console.assert(parseExecutor('## EXECUTOR\nopencode') === 'opencode', 'opencode parse failed');
console.log('parser OK');
"

# 3. Aperture builds clean
cd ~/projects/aperture && npm run build 2>&1 | tail -5

# 4. Manual UI check: open http://localhost:4321/tasks — confirm executor badges visible
```

## OUT OF SCOPE
- Auto-launching OpenCode from Aperture (would require PTY/TUI integration — future brief)
- Per-task workroot override (already handled by AP-12)
- Any changes to how Codex launch arguments are built

## EXECUTOR
codex

## RISK
LOW — additive only; no existing behavior changes if EXECUTOR field is absent from old briefs
