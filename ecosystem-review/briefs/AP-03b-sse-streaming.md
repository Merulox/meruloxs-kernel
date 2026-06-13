# AP-03b: Aperture — SSE log streaming for running Codex jobs

**Status:** briefed  
**Depends on:** AP-03a verified and accepted  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/` — one new API endpoint, one component update

---

## GOAL

Replace poll-based log display for running Codex jobs with a live SSE stream. Log lines appear in real-time; scroll position is held; the rest of the page is not re-rendered.

---

## WHY

After AP-03a, `JobRow` still uses `logTail` from the 5s `/api/codex-jobs` poll — same 100-line tail, refreshed every 5 seconds. This is the pre-migration behavior. SSE streams each new byte as it's written, without polling. Required: stable DOM nodes (provided by AP-03a's React substrate).

---

## CURRENT STATE (after AP-03a)

- `src/components/codex/JobRow.tsx` renders `job.logTail` in a `<pre>`; refreshes every 5s via parent poll
- No `/api/log-stream` endpoint exists
- `~/.local/share/aperture/jobs/*.json` has `logPath` for each job

---

## FILES IT OWNS

- `src/pages/api/log-stream.ts` — **new** — SSE endpoint
- `src/components/codex/JobRow.tsx` — **update** — open EventSource for running jobs

---

## DO NOT TOUCH

- `src/pages/api/codex-jobs.ts` — keep; still used for non-running job history
- `src/components/Taskboard.tsx` — no changes
- Any other component

---

## IMPLEMENTATION SPEC

### 1. `/api/log-stream.ts`

SSE endpoint. Reads `jobId` from query string, finds the job JSON in `~/.local/share/aperture/jobs/`, tails the `logPath` every 500ms, emits new bytes as `data:` lines. Closes when PID is no longer alive.

```ts
import type { APIRoute } from 'astro';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

const JOBS_DIR = join(homedir(), '.local/share/aperture/jobs');

function isPidAlive(pid: number): boolean {
  try { process.kill(pid, 0); return true; } catch (e: any) { return e.code !== 'ESRCH'; }
}

export const GET: APIRoute = async ({ url }) => {
  const jobId = url.searchParams.get('jobId');
  if (!jobId || !/^[\w-]+$/.test(jobId)) {
    return new Response('invalid jobId', { status: 400 });
  }

  let job: any;
  try {
    job = JSON.parse(await readFile(join(JOBS_DIR, `${jobId}.json`), 'utf8'));
  } catch {
    return new Response('job not found', { status: 404 });
  }

  const stream = new ReadableStream({
    async start(controller) {
      let offset = 0;
      const enc = new TextEncoder();
      const tick = setInterval(async () => {
        const content = await readFile(job.logPath, 'utf8').catch(() => '');
        const chunk = content.slice(offset);
        offset = content.length;
        for (const line of chunk.split('\n')) {
          if (line) controller.enqueue(enc.encode(`data: ${line}\n\n`));
        }
        if (!isPidAlive(job.pid)) {
          controller.enqueue(enc.encode(`event: done\ndata: ${job.exitCode ?? 1}\n\n`));
          clearInterval(tick);
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
    },
  });
};
```

### 2. JobRow.tsx update

For running jobs: open an `EventSource` on mount, append lines to local state, auto-scroll. Close on unmount or when `done` event fires. Non-running jobs still render `job.logTail` statically (no EventSource needed).

```tsx
import { useState, useEffect, useRef } from 'react';

export function JobRow({ job }: { job: any }) {
  const logRef = useRef<HTMLPreElement>(null);
  const [lines, setLines] = useState<string[]>(
    job.logTail ? job.logTail.split('\n') : []
  );

  useEffect(() => {
    if (job.status !== 'running') return;
    const es = new EventSource(`/api/log-stream?jobId=${job.jobId}`);
    es.onmessage = (e) => {
      setLines(prev => [...prev, e.data]);
      setTimeout(() => logRef.current?.scrollTo(0, logRef.current.scrollHeight), 0);
    };
    es.addEventListener('done', () => es.close());
    return () => es.close();
  }, [job.jobId, job.status]);

  // ... rest of the row JSX using existing CSS classes
}
```

---

## DONE LOOKS LIKE

1. `npm run build` clean, service active
2. Start a job via "Send to Codex" — log lines appear in the running job row within 1s, without the panel re-rendering
3. Scroll position in the log `<pre>` is not reset between new line arrivals
4. `curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/log-stream?jobId=FAKE"` → 404
5. `curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/log-stream?jobId=VALID_RUNNING_ID"` → `text/event-stream` content-type, `data:` lines streaming
6. `git status` clean — all changes committed
7. AP-03b status set to `review` in `~/agent-infra/ecosystem-review/briefs/README.md`

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture

# Confirm endpoint exists and rejects bad input
curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/log-stream?jobId=FAKE" -o /dev/null -w "%{http_code}"
# Expected: 404

# Confirm SSE headers on valid job (if one exists)
curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/log-stream?jobId=$(ls ~/.local/share/aperture/jobs/ | head -1 | sed 's/\.json//')" -I | grep content-type

cd ~/projects/aperture && git status --short
```

---

## OUT OF SCOPE

- AI summaries — AP-03c
- Multiple concurrent SSE connections per job
- SSE for non-log events (permission requests, task updates)

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-03b-sse-streaming.md and implement it.
Prerequisite: AP-03a must be verified and accepted before starting this brief.
When done: commit all files, set AP-03b status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
```
