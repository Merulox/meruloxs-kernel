# AP-04: Aperture — Sequential task dependency gates

**Status:** briefed  
**Depends on:** AP-03a verified and accepted  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/lib/tasks.ts`, `~/projects/aperture/src/components/tasks/ExPanel.tsx`

---

## GOAL

When an EX task has an unmet prerequisite, its "Send to Codex" button is visually disabled with a label indicating what must be done first. Once the prerequisite reaches `done`, the button becomes active automatically on the next poll.

---

## WHY

AP-03b and AP-03c will silently fail if launched before their predecessor is done. The current UI shows both as READY with identical buttons — there's no signal that one must precede the other. This brief wires the `Depends On` column (already present in README.md after 2026-06-11 architect edit) into the UI so ordering is enforced visually.

---

## CURRENT STATE (after AP-03a)

- `README.md` table has a `Depends On` column (column index 6; `cells[6]`). AP-03b has `AP-03a`, AP-03c has `AP-03b`, all others have `—`.
- `ExTask` interface has no `dependsOn` or `blocked` fields.
- `getExTasks()` reads `cells[5]` for `riskGate` but ignores `cells[6]`.
- `ExPanel.tsx` (created by AP-03a) renders a "Send to Codex" button for briefed tasks with no gate logic.

---

## FILES IT OWNS

- `src/lib/tasks.ts` — add `dependsOn` + `blocked` to `ExTask` interface; parse `cells[6]`; compute `blocked` via second pass
- `src/components/tasks/ExPanel.tsx` — disable button + show indicator when `task.blocked`
- `src/styles/global.css` — add `.dep-gate`, `.btn-disabled`, `.dep-label` styles

---

## DO NOT TOUCH

- `ecosystem-review/briefs/README.md` — column already added by architect
- `src/pages/api/tasks-data.ts` — no changes (ExTask is serialized as-is)
- Any other component or file

---

## IMPLEMENTATION SPEC

### 1. `src/lib/tasks.ts` — ExTask interface

Add two fields:

```ts
export interface ExTask {
  // ... existing fields ...
  dependsOn: string;   // empty string if no dependency
  blocked: boolean;    // true if dependsOn task is not `done`
}
```

### 2. `src/lib/tasks.ts` — getExTasks()

Parse `cells[6]` and compute `blocked` in a second pass after all tasks are built:

```ts
export async function getExTasks(): Promise<ExTask[]> {
  const [content, briefFiles] = await Promise.all([readText(EX_BOARD), listFiles(EX_BRIEFS_DIR)]);
  const tasks = await Promise.all(content
    .split(/\r?\n/)
    .filter((line) => /^\|\s*[A-Z]+-\d+[a-z]?\s*\|/.test(line))
    .map(async (line) => {
      const cells = tableCells(line);
      const id = cells[0];
      const status = (cells[1] || 'unknown').replaceAll('`', '');
      const title = cells[2] || '';
      const briefFile = briefFiles.find((file) => file.startsWith(`${id}-`) && file.endsWith('.md'));
      const briefPath = briefFile ? join(EX_BRIEFS_DIR, briefFile) : '';
      const preview = await getBriefPreview(briefPath);
      const dependsOn = (cells[6] || '').replace(/^—$/, '').trim();
      return {
        id,
        status,
        ...classifyStatus(status),
        title,
        briefPath,
        ...preview,
        prompt: status === 'briefed' && briefPath ? promptForBrief(briefPath) : '',
        riskGate: cells[5] || '',
        dependsOn,
        blocked: false, // resolved in second pass
      };
    }));

  // Second pass: resolve blocked state
  const statusMap = new Map(tasks.map((t) => [t.id, t.status]));
  const resolved = tasks.map((t) => ({
    ...t,
    blocked: t.dependsOn ? statusMap.get(t.dependsOn) !== 'done' : false,
  }));

  return sortTasks(resolved);
}
```

### 3. `src/components/tasks/ExPanel.tsx` — button gate

When `task.blocked` is true, replace the active "Send to Codex" button with a disabled variant:

```tsx
{task.status === 'briefed' && (
  task.blocked ? (
    <div className="dep-gate">
      <button disabled className="btn btn-disabled">Send to Codex</button>
      <span className="dep-label">requires {task.dependsOn}</span>
    </div>
  ) : (
    <button onClick={() => handleLaunch(task)}>Send to Codex</button>
  )
)}
```

Add to `global.css`:

```css
.dep-gate {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.dep-label {
  font-size: 0.75rem;
  color: var(--muted);
  font-style: italic;
}
```

---

## DONE LOOKS LIKE

1. `npm run build` clean, service active
2. `/tasks` loads — AP-03b and AP-03c show a grayed "Send to Codex" button with `requires AP-03a` / `requires AP-03b` beside it
3. AP-03a shows a normal active button (no dependency)
4. `curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/api/tasks-data | python3 -c "import sys,json; tasks=json.load(sys.stdin)['exTasks']; [print(t['id'], t['dependsOn'], t['blocked']) for t in tasks if t['dependsOn']]"` — prints `AP-03b AP-03a True` and `AP-03c AP-03b True` (or False if predecessor is done)
5. `git status` clean — all changes committed
6. AP-04 status set to `review` in `~/agent-infra/ecosystem-review/briefs/README.md`

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture

curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/api/tasks-data | python3 -c "
import sys, json
tasks = json.load(sys.stdin)['exTasks']
for t in tasks:
    if t.get('dependsOn'):
        print(f\"{t['id']}: dependsOn={t['dependsOn']} blocked={t['blocked']}\")
"

cd ~/projects/aperture && git status --short
```

---

## OUT OF SCOPE

- Dependency gates for SYNTRA tasks
- Chained dependency chains (A→B→C resolved transitively) — each task declares only its direct predecessor
- Any tooltip or popover — the inline label is sufficient
- Changing the visual design beyond the CSS above

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-04-dependency-gates.md and implement it.
Prerequisite: AP-03a must be verified and accepted before starting this brief.
When done: commit all files, set AP-04 status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
```
