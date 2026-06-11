# AP-02: Aperture — Codex launch buttons + instance monitoring

**Status:** briefed  
**Date:** 2026-06-10  
**Touches:** `~/projects/aperture/src/`  
**Risk gate:** spawns child processes, no data writes outside `/tmp/` and `~/.local/share/aperture/jobs/`

---

## GOAL

Add a "Send to Codex" button to each briefed task in Aperture, and add a live monitoring panel showing running Codex instances (status, elapsed time, last log lines).

---

## WHY

Briefed tasks currently require copy-pasting a prompt into a Codex window manually. The architect wants to launch Codex from Aperture directly and watch instance progress without switching windows.

---

## CURRENT STATE

- Aperture is a Astro SSR app at `~/projects/aperture/` — built with `npm run build`, served by systemd as `aperture`
- Tasks page at `/tasks` shows briefed SYNTRA and EX tasks
- Each briefed task already has a `prompt` field (full brief content embedded, as of AP-01b changes)
- One existing API endpoint: `POST /api/respond` (permission request responses) — use as pattern
- Codex CLI is at `/run/current-system/sw/bin/codex`

---

## FILES IT OWNS

- `src/pages/api/launch-codex.ts` — **new** — spawn Codex process endpoint
- `src/pages/api/codex-jobs.ts` — **new** — return all job statuses
- `src/pages/tasks.astro` — add monitoring panel + "Send to Codex" buttons to briefed tasks
- `src/lib/tasks.ts` — **no changes needed** (prompt field already populated)

---

## DO NOT TOUCH

- `src/lib/tasks.ts` (already updated this session)
- `src/lib/data.ts`
- `src/styles/global.css` — minimal additions only, no restructuring
- Permission requests section
- Brain bus section
- Brain-* scripts or genesis-* scripts

---

## IMPLEMENTATION SPEC

### 1. Jobs directory

Use `~/.local/share/aperture/jobs/` for job tracking files. Each job is a JSON file named `{jobId}.json`.

Job schema:
```json
{
  "jobId": "uuid-v4",
  "taskId": "S-10",
  "taskTitle": "Path-based routing + SSG pre-rendering",
  "briefPath": "/home/merulox/syntra/docs/planning/task-s10-path-routing-ssg.md",
  "startedAt": "2026-06-10T22:00:00.000Z",
  "pid": 12345,
  "logPath": "/home/merulox/.local/share/aperture/jobs/uuid.log",
  "status": "running",
  "exitCode": null,
  "finishedAt": null
}
```

### 2. `POST /api/launch-codex`

Request body: `{ taskId, taskTitle, briefPath, prompt }`

Steps:
1. Validate inputs — `taskId` must be alphanumeric/dash, `prompt` must be non-empty
2. Generate a `jobId` (`crypto.randomUUID()`)
3. Create jobs directory: `mkdir -p ~/.local/share/aperture/jobs/`
4. Open log file at `~/.local/share/aperture/jobs/{jobId}.log`
5. Derive `cwd` from `briefPath`: if path is under `~/syntra/`, use `~/syntra/`; if under `~/agent-infra/`, use `~/agent-infra/`; otherwise default to `~/`.
6. Spawn the process in full-auto mode (no permission prompts):
   ```ts
   const child = spawn(
     '/run/current-system/sw/bin/codex',
     ['--approval-mode', 'full-auto', '-q', prompt],
     {
       detached: true,
       stdio: ['ignore', logFd, logFd],
       cwd: resolvedCwd,
       env: { ...process.env },
     }
   );
   child.unref();
   ```
   `--approval-mode full-auto` skips all permission prompts. `-q` suppresses interactive UI. This is appropriate for executor tasks launched from well-scoped briefs.
7. Write job JSON file with `pid: child.pid, status: 'running'`
8. Return `{ ok: true, jobId, pid: child.pid }`

### 3. `GET /api/codex-jobs`

Steps:
1. Read all `*.json` files from `~/.local/share/aperture/jobs/`
2. For each job with `status: 'running'`:
   - Check if PID is alive: try `process.kill(pid, 0)` — if it throws ESRCH, the process is done
   - If done: read log file for exit marker or just mark status based on PID absence
   - Update the job JSON file in place with `status: 'done'` or `'failed'` and `finishedAt`
3. For each job, read the last 20 lines of its log file
4. Return `{ jobs: [...] }` sorted by `startedAt` descending, max 20 jobs

### 4. UI changes in `tasks.astro`

**"Send to Codex" button** — add to each briefed task row (both EX and SYNTRA sections) alongside the existing "Copy prompt" button:

```html
<button type="button" class="launch-codex"
  data-task-id={task.id}
  data-task-title={task.title}
  data-brief-path={task.briefPath}
  data-prompt={task.prompt}>
  Send to Codex
</button>
```

Button click handler (in `<script>`):
```ts
document.querySelectorAll('.launch-codex').forEach((btn) => {
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    btn.textContent = 'Launching...';
    const response = await fetch('/api/launch-codex', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        taskId: btn.dataset.taskId,
        taskTitle: btn.dataset.taskTitle,
        briefPath: btn.dataset.briefPath,
        prompt: btn.dataset.prompt,
      }),
    });
    const result = await response.json();
    if (response.ok) {
      btn.textContent = `Launched (PID ${result.pid})`;
      window.setTimeout(() => loadJobs(), 1000);
    } else {
      btn.textContent = 'Failed';
      btn.disabled = false;
    }
  });
});
```

**Monitoring panel** — new section in tasks.astro at the top, before permission requests:

```html
<section class="panel" id="codex-instances-panel" aria-labelledby="codex-heading">
  <div class="section-head">
    <div class="label" id="codex-heading">codex instances</div>
    <span class="badge badge-muted" id="codex-count">0 running</span>
  </div>
  <div id="codex-jobs-list">
    <p class="state-entry">— no active instances —</p>
  </div>
</section>
```

Dynamic rendering via JS `loadJobs()` function (called on page load + every 10s):
```ts
async function loadJobs() {
  const { jobs } = await fetch('/api/codex-jobs').then(r => r.json());
  const panel = document.getElementById('codex-jobs-list');
  const count = document.getElementById('codex-count');
  const running = jobs.filter(j => j.status === 'running').length;
  count.textContent = `${running} running`;
  if (!jobs.length) {
    panel.innerHTML = '<p class="state-entry">— no active instances —</p>';
    return;
  }
  panel.innerHTML = jobs.map(job => `
    <div class="codex-job status-${job.status}">
      <span class="task-id">${job.taskId}</span>
      <span class="badge badge-${job.status === 'running' ? 'blue' : job.status === 'done' ? 'muted' : 'red'}">
        ${job.status.toUpperCase()}
      </span>
      <span class="task-title">${job.taskTitle}</span>
      <span class="elapsed">${elapsed(job.startedAt, job.finishedAt)}</span>
      <pre class="job-log">${job.logTail || '(no output yet)'}</pre>
    </div>
  `).join('');
}

function elapsed(startedAt, finishedAt) {
  const end = finishedAt ? new Date(finishedAt) : new Date();
  const ms = end - new Date(startedAt);
  const s = Math.floor(ms / 1000);
  return s < 60 ? `${s}s` : `${Math.floor(s / 60)}m ${s % 60}s`;
}

loadJobs();
window.setInterval(loadJobs, 10_000);
```

(Remove or keep the existing 30s full-page reload — confirm with architect before removing.)

---

## DONE LOOKS LIKE

1. `npm run build` in `~/projects/aperture/` completes with no errors
2. `systemctl --user restart aperture && systemctl --user is-active aperture` → active
3. At `/tasks`, every briefed task shows a "Send to Codex" button next to "Copy prompt"
4. Clicking "Send to Codex" on any briefed task:
   - Button changes to "Launching..." then "Launched (PID XXXXXX)"
   - A job entry appears in the monitoring panel within ~2s
5. `GET http://localhost:8788/api/codex-jobs` returns valid JSON with `{ jobs: [] }` when idle
6. `cat ~/.local/share/aperture/jobs/*.json` shows correct job structure after a launch
7. Monitoring panel shows: task ID, status badge, elapsed time, last log lines
8. Completed jobs show DONE badge; failed jobs show red FAILED badge

---

## VERIFY WITH

```bash
# Build + restart
cd ~/projects/aperture && npm run build
systemctl --user restart aperture
systemctl --user is-active aperture

# Check API endpoints exist
curl -s http://localhost:8788/api/codex-jobs | node -e "const d=JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')); console.log('jobs:', d.jobs?.length)"

# Check jobs directory created on first launch (after clicking a button)
ls ~/.local/share/aperture/jobs/ 2>/dev/null || echo "dir will be created on first launch"

# Verify page renders monitoring panel
curl -s http://localhost:8788/tasks | grep -c "codex-instances-panel"
```

---

## OUT OF SCOPE

- Killing / cancelling a running Codex instance from the UI (follow-on)
- Log streaming via WebSocket (full page refresh every 10s is sufficient)
- Job history persistence beyond the jobs directory
- Any changes to how briefs are read or tasks are parsed

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-02-codex-launch-monitor.md and implement the task.
Report back using ~/agent-infra/templates/implementation-report.md.
Paste raw command output — do not summarize.
```
