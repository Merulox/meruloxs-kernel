# AP-03: Aperture — Live log streaming + AI activity summaries

**Status:** briefed  
**Date:** 2026-06-10  
**Touches:** `~/projects/aperture/src/`  
**Risk gate:** new SSE endpoint, one Claude API call per running job per poll

---

## GOAL

Replace the 5s polling approach in the Codex panel with Server-Sent Events (SSE) for live log streaming, and add a one-line AI-generated "what it's doing" summary beneath each running job's header.

---

## WHY

The current panel polls `/api/codex-jobs` every 5 seconds and replaces the full panel HTML. This causes visual flicker, resets scroll position, and feels mechanical. SSE pushes log deltas in real time without re-rendering the whole panel. The AI summary gives a human-readable status line ("normalizing product data", "writing to Supabase", "running tests") instead of raw log noise.

---

## CURRENT STATE

- `GET /api/codex-jobs` — returns all jobs with full log tail (100 lines). Called every 5s.
- `POST /api/launch-codex` — spawns `codex exec` process, writes job JSON + log file.
- Jobs directory: `~/.local/share/aperture/jobs/`
- Log files: `~/.local/share/aperture/jobs/{jobId}.log`
- Panel: `#codex-jobs-list` in `tasks.astro`, fully re-rendered on each poll

---

## FILES IT OWNS

- `src/pages/api/log-stream.ts` — **new** — SSE endpoint streaming log lines for one job
- `src/pages/api/summarize-job.ts` — **new** — Claude API call returning one-line activity summary
- `src/pages/tasks.astro` — replace polling with SSE subscription + summary fetch
- `src/styles/global.css` — minor additions for summary line and stream indicator

---

## DO NOT TOUCH

- `src/pages/api/launch-codex.ts`
- `src/pages/api/codex-jobs.ts` — keep for initial page load (still needed for history)
- `src/lib/tasks.ts`
- Job file format — do not change schema

---

## IMPLEMENTATION SPEC

### 1. `GET /api/log-stream?jobId={id}`

SSE endpoint. For a running job:
1. Open the log file as a readable stream (tail mode)
2. Track byte offset — only send NEW content since last SSE message
3. Every 500ms: read new bytes from log file, emit as SSE `data:` events (one line per SSE event)
4. When the job's PID is no longer alive: emit a final `event: done` message, close the connection

SSE format:
```
data: {log line text}\n\n
event: done\ndata: {exitCode}\n\n
```

Headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`.

Astro SSR supports streaming responses via `new Response(readableStream, ...)`.

### 2. `GET /api/summarize-job?jobId={id}`

Called once per running job per 15-second interval (not on every SSE event).

1. Read the last 40 lines of the job log
2. Filter out `[gitnexus]` lines (noise from the GitNexus background hook)
3. Call Claude API (`claude-haiku-4-5-20251001` — cheap, fast):
   ```
   System: You are a one-line status reporter. Given the last lines of a Codex CLI log, output exactly ONE short sentence (max 10 words) describing what the agent is currently doing. No punctuation at the end. Examples: "writing ingest script", "running dry-run verification", "waiting for Supabase response"
   User: {filtered log lines}
   ```
4. Return `{ summary: "one line string" }`

Claude API key: read from `~/.secrets/anthropic-api-key` or `process.env.ANTHROPIC_API_KEY`.

### 3. Client-side changes in `tasks.astro`

**On page load / `loadJobs()` result:**
- For each running job: open an `EventSource('/api/log-stream?jobId={id}')` if not already open
- Store open EventSources in a `Map<jobId, EventSource>`
- On each SSE `data:` event: append the new line to the job's `pre.job-log`, scroll to bottom
- On `event: done`: close the EventSource, call `loadJobs()` once to update badge status

**Summary polling (separate 15s interval):**
```js
async function refreshSummaries() {
  for (const jobId of openStreams.keys()) {
    const { summary } = await fetch(`/api/summarize-job?jobId=${jobId}`).then(r => r.json());
    const el = document.getElementById(`summary-${jobId}`);
    if (el && summary) el.textContent = summary;
  }
}
window.setInterval(refreshSummaries, 15_000);
```

**Job row HTML** (update `jobRow()` function):
```html
<div class="codex-job status-running">
  <span class="task-id">S-12</span>
  <span class="badge badge-blue">RUNNING</span>
  <span class="task-title">Secrid normalize + ingest</span>
  <span class="elapsed">2m 36s</span>
  <span class="job-summary" id="summary-{jobId}">—</span>
  <pre class="job-log" id="log-{jobId}">{initial log from loadJobs}</pre>
</div>
```

**Keep `/api/codex-jobs` polling at 30s** (was 5s) — only needed for history/completed jobs now that running jobs stream via SSE.

---

## DONE LOOKS LIKE

1. `npm run build` clean, service active
2. Open `/tasks` — running jobs stream live without full panel re-render
3. Scroll position preserved during streaming updates
4. Summary line updates every ~15s with a human-readable phrase
5. When job finishes, `event: done` fires, badge updates from RUNNING → DONE/FAILED within 2s
6. Completed jobs section still shows history via 30s `/api/codex-jobs` poll

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build
systemctl --user restart aperture && systemctl --user is-active aperture

# Start a test Codex job from /tasks, then:
curl -H "Authorization: Basic bTpzdA==" \
  "http://localhost:8788/api/log-stream?jobId=$(ls ~/.local/share/aperture/jobs/*.json | tail -1 | xargs basename | sed 's/.json//')" \
  --no-buffer | head -5

# Summary endpoint:
curl -H "Authorization: Basic bTpzdA==" \
  "http://localhost:8788/api/summarize-job?jobId=$(ls ~/.local/share/aperture/jobs/*.json | tail -1 | xargs basename | sed 's/.json//')"
```

---

## OUT OF SCOPE

- WebSocket (SSE is sufficient for one-directional log streaming)
- Sending input TO a running Codex process
- Summary history / archiving summaries
- Streaming for completed jobs (log is already final)

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-03-live-streaming.md and implement it.
Report back using ~/agent-infra/templates/implementation-report.md.
Paste raw command output — do not summarize.
```
