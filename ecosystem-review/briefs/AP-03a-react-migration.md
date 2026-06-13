# AP-03a: Aperture — React migration + all panels (foundation)

**Status:** briefed  
**Part of:** AP-03 decomposition (AP-03a → AP-03b → AP-03c; each depends on previous)  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/` — substantial rewrite of tasks.astro + new files  
**Risk gate:** full page migration; back up tasks.astro before touching it

---

## GOAL

Replace the current Astro SSR + vanilla JS `/tasks` page with a fully React-rendered equivalent. After this brief, the page is functionally identical to today — all sections render, all buttons work, state survives poll cycles — but the substrate is React (`client:only`). No SSE, no AI summaries yet.

---

## WHY

The current page destroys and recreates the DOM every 5 seconds via `panel.innerHTML = ...`. This resets `<details>` open state, scroll positions, and makes SSE impossible. AP-03a replaces the substrate. AP-03b and AP-03c add features on top of stable nodes.

AP-03 as a single brief has failed twice (exit 0, no files created) — too large for one executor run. This is the foundational slice.

---

## CURRENT STATE

- `src/pages/tasks.astro`: ~390 lines of Astro SSR + inline `<script>` with vanilla JS that replaces `panel.innerHTML` every 5s
- `src/lib/tasks.ts`: data layer — already exposes `getTaskboardData()`, `getExTasks()`, `getSyntraTasks()`, `getPermissionRequests()`, `getBrainBusSummary()`
- Existing API endpoints: `/api/codex-jobs`, `/api/launch-codex`, `/api/respond`
- No React integration installed yet

---

## FILES IT OWNS

**New:**
- `src/pages/api/tasks-data.ts` — JSON endpoint wrapping `getTaskboardData()`
- `src/components/Taskboard.tsx` — root React component
- `src/components/codex/CodexPanel.tsx` — Codex instances panel
- `src/components/codex/JobRow.tsx` — single job row (polling, no SSE yet)
- `src/components/tasks/ExPanel.tsx` — EX task list
- `src/components/tasks/SyntraPanel.tsx` — SYNTRA task groups
- `src/components/tasks/PermissionRequests.tsx` — permission request cards + form
- `src/components/tasks/BrainBus.tsx` — brain bus queue counts

**Modified:**
- `src/pages/tasks.astro` — reduce to bare shell (back it up first as `tasks.astro.bak`)
- `package.json` — add `@astrojs/react`, `react`, `react-dom`
- `astro.config.mjs` — add `@astrojs/react` integration

---

## DO NOT TOUCH

- `src/lib/tasks.ts` — no changes to the data layer
- `src/pages/api/codex-jobs.ts` — keep; `CodexPanel` polls this
- `src/pages/api/launch-codex.ts` — keep; buttons POST here
- `src/pages/api/respond.ts` — keep; permission form POSTs here
- `src/pages/index.astro` — no changes
- `src/styles/global.css` — no structural changes (components use existing CSS classes)

---

## IMPLEMENTATION SPEC

### 1. Install React integration

```bash
cd ~/projects/aperture && npm install @astrojs/react react react-dom
```

Add to `astro.config.mjs`:
```js
import react from '@astrojs/react';
// add react() to integrations array alongside the existing node() adapter
```

### 2. tasks.astro shell

Back up first: `cp src/pages/tasks.astro src/pages/tasks.astro.bak`

Replace all content with:
```astro
---
import '../styles/global.css';
import Taskboard from '../components/Taskboard';
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tasks · Aperture</title>
</head>
<body>
  <Taskboard client:only="react" />
</body>
</html>
```

### 3. `/api/tasks-data.ts`

```ts
import type { APIRoute } from 'astro';
import { getTaskboardData } from '../../lib/tasks';

export const GET: APIRoute = async () => {
  const data = await getTaskboardData();
  return new Response(JSON.stringify(data), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
```

### 4. Taskboard.tsx

Root component. Polls `/api/tasks-data` every 30s, `/api/codex-jobs` every 5s. Renders all panels.

```tsx
import { useState, useEffect } from 'react';
import { CodexPanel } from './codex/CodexPanel';
import { ExPanel } from './tasks/ExPanel';
import { SyntraPanel } from './tasks/SyntraPanel';
import { PermissionRequests } from './tasks/PermissionRequests';
import { BrainBus } from './tasks/BrainBus';

export default function Taskboard() {
  const [data, setData] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [lastUpdated, setLastUpdated] = useState('');

  useEffect(() => {
    const refresh = () =>
      fetch('/api/tasks-data')
        .then(r => r.json())
        .then(d => { setData(d); setLastUpdated(new Date().toLocaleTimeString('en-CA', { hour: '2-digit', minute: '2-digit', second: '2-digit' })); });
    refresh();
    const t = setInterval(refresh, 30_000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const refresh = () => fetch('/api/codex-jobs').then(r => r.json()).then(d => setJobs(d.jobs || []));
    refresh();
    const t = setInterval(refresh, 5_000);
    return () => clearInterval(t);
  }, []);

  return (
    <main>
      <header className="topbar">
        <div className="brand">aperture / tasks</div>
        <div className="taskboard-meta">
          <span>Last updated: {lastUpdated}</span>
          <a href="/" className="nav-link">dashboard</a>
        </div>
      </header>
      <div className="taskboard">
        <PermissionRequests items={data?.permissionRequests ?? []} />
        <ExPanel tasks={data?.exTasks ?? []} jobs={jobs} />
        <SyntraPanel tasks={data?.syntraTasks ?? []} jobs={jobs} />
        <CodexPanel jobs={jobs} />
        <BrainBus summary={data?.brainBus} />
      </div>
    </main>
  );
}
```

### 5. CodexPanel.tsx + JobRow.tsx

Port the existing vanilla JS job rendering to React. Running jobs expanded, completed in a `<details>` collapsed. No SSE yet — job logs come from `logTail` in the jobs payload (same as today). Auto-scroll running job logs on render.

Key: button state is managed by React — no manual DOM sync. Button disabled + relabeled when `jobs.some(j => j.taskId === task.id && j.status === 'running')`.

Launch button POSTs to `/api/launch-codex` same as today.

### 6. ExPanel.tsx + SyntraPanel.tsx

Port the existing Astro template markup to React. Same visual structure — ex-grid, syntra-groups, attention/other/done sections, briefed tasks show prompt + "Send to Codex" button, brief preview in `<details>`. State (open/closed `<details>`) now survives poll cycles because React only reconciles changed nodes.

### 7. PermissionRequests.tsx

Port the permission request cards. Form submits via `fetch` POST to `/api/respond`, same as today. On success: re-fetch tasks-data to clear the request.

### 8. BrainBus.tsx

Port the brain bus queue counts and failed task list.

---

## DONE LOOKS LIKE

1. `npm run build` clean
2. `systemctl --user restart aperture && systemctl --user is-active aperture` → active
3. `/tasks` loads — all sections render: header, permission requests, EX tasks, SYNTRA tasks, Codex panel, brain bus
4. Opening a `<details>` section (brief preview, done tasks) — state survives the next 5s/30s poll
5. "Send to Codex" on a briefed task — button disables, shows running PID, job appears in Codex panel
6. `curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/api/tasks-data | python3 -c "import sys,json; d=json.load(sys.stdin); print('ex:', len(d['exTasks']), 'syntra:', len(d['syntraTasks']))"` — returns counts
7. `git status` clean — all new files committed
8. AP-03a status set to `review` in `~/agent-infra/ecosystem-review/briefs/README.md`

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture

curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/api/tasks-data | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('exTasks:', len(d.get('exTasks', [])))
print('syntraTasks:', len(d.get('syntraTasks', [])))
print('permissionRequests:', len(d.get('permissionRequests', [])))
print('brainBus pending:', d.get('brainBus', {}).get('pending'))
"

curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/tasks | grep -c "taskboard"

cd ~/projects/aperture && git status --short
ls src/components/
```

---

## OUT OF SCOPE

- SSE log streaming — AP-03b
- AI activity summaries — AP-03c
- Migrating the `/` dashboard page
- Visual design changes

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-03a-react-migration.md and implement it.
When done: commit all files, set AP-03a status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
The architect verifies from the job log.
```
