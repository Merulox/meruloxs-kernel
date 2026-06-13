# AP-03: Aperture — Full SPA migration + live streaming + AI summaries

**Status:** briefed  
**Supersedes:** original AP-03 (SSE-only scope — too narrow for the longterm vision)  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/` (substantial rewrite of tasks.astro)  
**Risk gate:** full page migration; keep old tasks.astro backup until verified

---

## GOAL

Migrate the Aperture `/tasks` page from Astro SSR + vanilla JS DOM manipulation to a fully reactive React SPA (`client:only`). Every section — Codex panel, task lists, permission requests, brain bus — becomes a live-updating React component. Add SSE log streaming for running Codex jobs and AI-generated one-line activity summaries.

---

## WHY

The current architecture destroys and re-creates the DOM on every poll cycle. This:
- Resets `<details>` open state, scroll positions, and any other DOM state
- Makes SSE streaming (stable DOM nodes required) architecturally incompatible
- Requires a full page reload to see task status changes or new permission requests
- Cannot scale to the Aperture's longterm vision: a real-time operational nervous system across agents, tasks, decisions, and events

The root fix is not a patch — it's replacing the substrate. React's reconciler diffs and patches only changed nodes. SSE then becomes straightforward (append to stable nodes). Every future panel gets reactivity for free.

---

## CURRENT STATE

- `tasks.astro`: Astro SSR page that renders everything server-side at request time, with vanilla JS that replaces `panel.innerHTML` every 5s for the Codex section
- API endpoints: `/api/codex-jobs`, `/api/launch-codex`, `/api/respond`
- No API endpoints for tasks, permission requests, or brain bus — these are SSR-rendered only
- `src/lib/tasks.ts`: data layer — already exposes `getTaskboardData()`, `getExTasks()`, `getSyntraTasks()`, `getPermissionRequests()`, `getBrainBusSummary()`

---

## FILES IT OWNS

- `src/pages/tasks.astro` — reduce to a bare shell (`<div id="taskboard-root">`) that mounts the React app
- `src/components/Taskboard.tsx` — **new** — root React component, owns all state
- `src/components/codex/CodexPanel.tsx` — **new** — Codex instances panel with SSE streaming
- `src/components/codex/JobRow.tsx` — **new** — single job row with log viewer
- `src/components/tasks/SyntraPanel.tsx` — **new** — SYNTRA task groups
- `src/components/tasks/ExPanel.tsx` — **new** — EX task list
- `src/components/tasks/PermissionRequests.tsx` — **new** — permission request cards with response form
- `src/components/tasks/BrainBus.tsx` — **new** — brain bus queue counts
- `src/pages/api/tasks-data.ts` — **new** — JSON endpoint wrapping `getTaskboardData()`
- `src/pages/api/log-stream.ts` — **new** — SSE endpoint for streaming a job's log file
- `src/pages/api/summarize-job.ts` — **new** — Claude Haiku call returning one-line activity summary
- `src/styles/global.css` — minimal updates only (no structural changes)
- `package.json` — add `react`, `react-dom` (if not already present from Astro's React integration)
- `astro.config.mjs` — add `@astrojs/react` integration if not already configured

---

## DO NOT TOUCH

- `src/lib/tasks.ts` — no changes to the data layer
- `src/pages/api/codex-jobs.ts` — keep for backward compatibility / history fallback
- `src/pages/api/launch-codex.ts` — no changes
- `src/pages/api/respond.ts` — the React form will POST to this same endpoint
- `src/pages/index.astro` — no changes to the dashboard page

---

## IMPLEMENTATION SPEC

### 1. Astro React integration

Add `@astrojs/react` to `astro.config.mjs`:
```js
import react from '@astrojs/react';
export default defineConfig({
  integrations: [react(), node({ mode: 'standalone' })],
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

Install: `npm install @astrojs/react react react-dom`

### 2. tasks.astro shell

Replace all content with a minimal shell:
```astro
---
import '../styles/global.css';
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Tasks · Aperture</title>
</head>
<body>
  <div id="taskboard-root"></div>
  <Taskboard client:only="react" />
</body>
</html>
```

### 3. `GET /api/tasks-data`

Thin wrapper around `getTaskboardData()` from `src/lib/tasks.ts`. Returns:
```json
{
  "permissionRequests": [...],
  "exTasks": [...],
  "syntraTasks": [...],
  "brainBus": { "pending": 0, "claimed": 1, "failed": 7, "failedTasks": [...] }
}
```

### 4. Taskboard.tsx — root component

```tsx
export function Taskboard() {
  const [data, setData] = useState(null);
  const [jobs, setJobs] = useState([]);

  // Poll tasks-data every 30s
  useEffect(() => {
    const refresh = () => fetch('/api/tasks-data').then(r => r.json()).then(setData);
    refresh();
    const t = setInterval(refresh, 30_000);
    return () => clearInterval(t);
  }, []);

  // Poll codex-jobs every 5s
  useEffect(() => {
    const refresh = () => fetch('/api/codex-jobs').then(r => r.json()).then(d => setJobs(d.jobs || []));
    refresh();
    const t = setInterval(refresh, 5_000);
    return () => clearInterval(t);
  }, []);

  return (
    <main>
      <header className="topbar">...</header>
      <div className="taskboard">
        <PermissionRequests items={data?.permissionRequests ?? []} />
        <ExPanel tasks={data?.exTasks ?? []} jobs={jobs} />
        <SyntraPanel tasks={data?.syntraTasks ?? []} jobs={jobs} />
        <CodexPanel jobs={jobs} onLaunch={() => refresh()} />
        <BrainBus summary={data?.brainBus} />
      </div>
    </main>
  );
}
```

### 5. CodexPanel.tsx — SSE streaming

Each running job opens an `EventSource` for its log:

```tsx
function JobRow({ job }) {
  const logRef = useRef(null);
  const [logLines, setLogLines] = useState(job.logTail?.split('\n') ?? []);
  const [summary, setSummary] = useState('');

  // SSE stream for running jobs
  useEffect(() => {
    if (job.status !== 'running') return;
    const es = new EventSource(`/api/log-stream?jobId=${job.jobId}`);
    es.onmessage = (e) => {
      setLogLines(prev => [...prev, e.data]);
      setTimeout(() => logRef.current?.scrollTo(0, logRef.current.scrollHeight), 0);
    };
    es.addEventListener('done', () => es.close());
    return () => es.close();
  }, [job.jobId, job.status]);

  // AI summary every 15s for running jobs
  useEffect(() => {
    if (job.status !== 'running') return;
    const refresh = () =>
      fetch(`/api/summarize-job?jobId=${job.jobId}`)
        .then(r => r.json())
        .then(d => setSummary(d.summary || ''));
    refresh();
    const t = setInterval(refresh, 15_000);
    return () => clearInterval(t);
  }, [job.jobId, job.status]);

  return (
    <div className={`codex-job status-${job.status}`}>
      <span className="task-id">{job.taskId}</span>
      <span className={`badge badge-${statusColor(job.status)}`}>{job.status.toUpperCase()}</span>
      <span className="task-title">{job.taskTitle}</span>
      <span className="elapsed">{elapsed(job.startedAt, job.finishedAt)}</span>
      {summary && <span className="job-summary">{summary}</span>}
      <pre className="job-log" ref={logRef}>{logLines.join('\n')}</pre>
    </div>
  );
}
```

### 6. `GET /api/log-stream?jobId={id}`

SSE endpoint. Track byte offset, emit new bytes every 500ms:

```ts
export const GET: APIRoute = async ({ url }) => {
  const jobId = url.searchParams.get('jobId');
  // validate jobId, find log path from job JSON
  const stream = new ReadableStream({
    async start(controller) {
      let offset = 0;
      const interval = setInterval(async () => {
        const content = await readFile(logPath, 'utf8').catch(() => '');
        const newContent = content.slice(offset);
        offset = content.length;
        if (newContent) {
          for (const line of newContent.split('\n').filter(Boolean)) {
            controller.enqueue(`data: ${line}\n\n`);
          }
        }
        if (!isPidAlive(job.pid)) {
          controller.enqueue(`event: done\ndata: ${job.exitCode ?? 1}\n\n`);
          clearInterval(interval);
          controller.close();
        }
      }, 500);
    }
  });
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  });
};
```

### 7. `GET /api/summarize-job?jobId={id}`

```ts
// Read last 40 lines of log, filter [gitnexus] noise, call Claude Haiku
const filtered = logLines.filter(l => !l.includes('[gitnexus]')).slice(-40).join('\n');
const response = await anthropic.messages.create({
  model: 'claude-haiku-4-5-20251001',
  max_tokens: 30,
  system: 'Output ONE phrase (max 8 words) describing what the agent is doing. No punctuation.',
  messages: [{ role: 'user', content: filtered }]
});
return { summary: response.content[0].text };
```

Read API key from `process.env.ANTHROPIC_API_KEY` — already set in Aperture's environment (confirm it's in the service env or `.env`).

### 8. PermissionRequests.tsx

Port the existing HTML permission request form to React. POST to `/api/respond` on submit (same endpoint, no changes needed there).

### 9. Launch button state (React)

The "Send to Codex" button state is now managed by React — no more manual DOM sync. Button disabled + relabeled when `jobs.some(j => j.taskId === task.id && j.status === 'running')`.

---

## DONE LOOKS LIKE

1. `npm run build` clean, service active
2. `/tasks` loads — all sections render: permission requests, EX tasks, SYNTRA tasks, Codex panel, brain bus
3. Opening `<details>` sections, expanding task briefings — state survives the 5s/30s poll cycles
4. Start a job via "Send to Codex" — log streams live without panel re-render, scroll position held
5. Summary line appears ~15s after launch, updates during run
6. Permission request form submits and disappears on success
7. `curl http://localhost:8788/api/tasks-data` — returns valid JSON with all four sections
8. `curl http://localhost:8788/api/log-stream?jobId={running-id}` — returns SSE stream
9. All implementation files committed to git (`git status` clean)
10. Status updated to `review` in `~/agent-infra/ecosystem-review/briefs/README.md` for AP-03

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build
systemctl --user restart aperture && systemctl --user is-active aperture

# Tasks API
curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/api/tasks-data | node -e "
  const d = JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'));
  console.log('exTasks:', d.exTasks?.length);
  console.log('syntraTasks:', d.syntraTasks?.length);
  console.log('permissionRequests:', d.permissionRequests?.length);
"

# Confirm page renders
curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/tasks | grep -c "taskboard-root"

# Git clean
cd ~/projects/aperture && git status --short
```

---

## OUT OF SCOPE

- Migrating the `/` (dashboard) page — only `/tasks` in this brief
- Changing the visual design or CSS structure
- WebSocket (SSE is sufficient for log streaming)
- Multiple concurrent SSE connections per job
- Summary storage / history

---

## NOTE ON ARCHITECTURE RESEARCH

A background research agent is producing a tech evaluation at `~/obsidian/knowledge/inbox/aperture-tech-research-2026-06-11.md`. The executor should proceed with React (already available in the Astro project via `@astrojs/react`). If the research surfaces a compelling reason to prefer SolidJS, that's a future migration — not a blocker for this brief.

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-03-live-streaming.md and implement it.
When done: commit all files, then set AP-03 status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
The architect will verify from the job log — do not paste output back.
```
