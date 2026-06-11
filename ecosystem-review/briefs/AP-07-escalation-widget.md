# AP-07: Aperture — executor escalation widget

**Status:** briefed  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/` — one new API endpoint, one new component, one CSS block

---

## GOAL

When a Codex job exits 0 but the executor was blocked (brief errors, missing dependency, clarification needed), surface the blocker in the Aperture taskboard. Currently those jobs are silent — the task stays READY with no indication anything happened.

---

## WHY

The FAIL badge catches hard exits (non-zero). It does NOT catch "executor read the brief, decided it was blocked, and exited 0 with a report explaining why". Those are indistinguishable from a successful run right now. AP-03c and S-17 both hit this and went unnoticed.

---

## MECHANISM

The executor writes a structured blocked file alongside the job log when it decides to stop without implementing. The Aperture reads these files and shows them as pending escalations.

**Convention**: when an executor is blocked, it writes (in addition to its implementation report output):

```
~/.local/share/aperture/jobs/{jobId}.blocked
```

Contents: one-paragraph plain text. The first line is the blocker category (`MISSING_DEP`, `BRIEF_ERROR`, `NEEDS_CLARIFICATION`, `NETWORK`, `PERMISSION`). Subsequent lines are the explanation.

The executor.md must be updated to include this convention.

---

## FILES IT OWNS

- `src/pages/api/escalations.ts` — **new** — scans jobs dir for `.blocked` files, returns list with jobId + taskId + text
- `src/components/tasks/EscalationPanel.tsx` — **new** — renders pending escalations above the task list
- `src/styles/global.css` — **update** — add `.escalation-panel`, `.escalation-item`, `.escalation-category` classes

---

## DO NOT TOUCH

- `src/pages/api/launch-codex.ts`
- `src/lib/tasks.ts`
- `src/components/tasks/ExPanel.tsx`

---

## IMPLEMENTATION SPEC

### 1. `/api/escalations.ts`

```ts
import type { APIRoute } from 'astro';
import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

const JOBS_DIR = join(homedir(), '.local/share/aperture/jobs');

export const GET: APIRoute = async () => {
  let files: string[] = [];
  try { files = await readdir(JOBS_DIR); } catch { return Response.json([]); }

  const blockedFiles = files.filter(f => f.endsWith('.blocked'));
  const escalations = await Promise.all(blockedFiles.map(async (file) => {
    const jobId = file.replace('.blocked', '');
    const text = await readFile(join(JOBS_DIR, file), 'utf8').catch(() => '');
    // Read taskId from the matching .json job record
    let taskId = '';
    try {
      const job = JSON.parse(await readFile(join(JOBS_DIR, `${jobId}.json`), 'utf8'));
      taskId = job.taskId;
    } catch {}
    const lines = text.trim().split('\n');
    const category = lines[0]?.trim() || 'BLOCKED';
    const message = lines.slice(1).join('\n').trim();
    return { jobId, taskId, category, message };
  }));

  return Response.json(escalations.filter(e => e.message));
};
```

### 2. `EscalationPanel.tsx`

Poll `/api/escalations` every 30s. If any exist, render above the EX tasks panel with a red left border. Each entry shows:
- `taskId` badge (red)
- `category` chip (orange)
- `message` text
- Dismiss button that DELETEs the `.blocked` file via a `DELETE /api/escalations?jobId=X` request

Add the `DELETE` handler to `escalations.ts`.

Dismiss removes the file — the next poll won't show it. No persistence needed beyond the file existence.

### 3. `global.css` additions

```css
.escalation-panel {
  border-left: 3px solid var(--red);
  padding: 10px 12px;
  background: #150a0a;
  margin-bottom: 12px;
}

.escalation-item {
  display: grid;
  grid-template-columns: auto auto 1fr auto;
  align-items: start;
  gap: 8px;
  padding: 6px 0;
  border-top: 1px solid #2a1010;
  font-size: 0.78rem;
}

.escalation-category {
  font-size: 0.68rem;
  font-weight: 700;
  color: #f97316;
  text-transform: uppercase;
}

.escalation-message {
  color: var(--text);
  line-height: 1.5;
  white-space: pre-wrap;
}

.dismiss-btn {
  border: 1px solid var(--muted);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  font: inherit;
  font-size: 0.65rem;
  padding: 3px 6px;
}
```

### 4. Update `executor.md`

Add this rule to the "When blocked" section of `~/agent-infra/agents/executor.md`:

```
When you are blocked before implementation:
1. Write your implementation report as usual.
2. ALSO write ~/.local/share/aperture/jobs/{jobId}.blocked (if APERTURE_JOB_ID is set in env).
   Line 1: one of MISSING_DEP | BRIEF_ERROR | NEEDS_CLARIFICATION | NETWORK | PERMISSION
   Lines 2+: one paragraph explaining the specific blocker and what the architect must resolve.
3. Exit cleanly (exit 0).
```

Note: `APERTURE_JOB_ID` needs to be passed as an env var when Codex is launched from Aperture. Add it to launch-codex.ts spawn env.

---

## DONE LOOKS LIKE

1. `npm run build` clean
2. A `.blocked` file dropped in `~/.local/share/aperture/jobs/` causes the escalation panel to appear above EX TASKS
3. Dismiss button removes the file; panel disappears on next poll
4. No escalations = panel not rendered (no empty state clutter)
5. `git status` clean — committed
6. AP-07 marked `review` in README.md

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture

# Simulate a blocked job
echo -e "BRIEF_ERROR\nCategory mapping in brief used Phone Cases instead of Tech Carry. Fix the normalization table and re-run." \
  > ~/.local/share/aperture/jobs/test-escalation.blocked
echo '{"jobId":"test-escalation","taskId":"S-99","status":"done","exitCode":0}' \
  > ~/.local/share/aperture/jobs/test-escalation.json

curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/api/escalations
# Expected: [{taskId: "S-99", category: "BRIEF_ERROR", message: "..."}]

# Clean up
rm ~/.local/share/aperture/jobs/test-escalation.*

cd ~/projects/aperture && git status --short
```

---

## OUT OF SCOPE

- Email/Telegram notifications for escalations
- Escalation history or archiving
- Multiple blockers per job (one `.blocked` file per job)

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-07-escalation-widget.md and implement it.
Working directory: ~/projects/aperture
When done: commit all files, mark AP-07 as `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
Also update ~/agent-infra/agents/executor.md with the blocked-file writing convention.
Also update ~/projects/aperture/src/pages/api/launch-codex.ts to pass APERTURE_JOB_ID as an env var to the Codex spawn.
```
