# AP-01b: Taskboard UX — Copy, Initiation Status, Auto-refresh

Status: ready. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.
Builds on AP-01. Read `/tasks` in a browser before implementing — understand what's already there.

## GOAL

Make the taskboard the single place to launch work: copy an executor handoff prompt in one click,
see at a glance which tasks are waiting to be initiated, and watch the board update without
manual reload.

## FILES IT OWNS

```
~/projects/aperture/src/pages/tasks.astro        — add copy buttons, status badges, auto-refresh
~/projects/aperture/src/lib/tasks.ts             — add "uninitiated" classification logic
~/projects/aperture/src/styles/global.css        — extend only (copy button, badge styles)
```

## DO NOT TOUCH

- `src/pages/api/respond.ts` — permission request endpoint, leave alone
- `src/lib/data.ts` — monitor data readers
- `src/pages/index.astro` — main dashboard (nav link already added)
- `src/middleware.ts`

## CHANGES REQUIRED

### 1. Executor handoff prompt — copy on click

For every task in the EX board and SYNTRA task board that is `briefed` (EX: ⬜ emoji in README,
SYNTRA: status = `briefed` or `backlog`):

Render the executor handoff prompt as a copyable block:

```
Read ~/agent-infra/agents/executor.md.
Read ~/agent-infra/ecosystem-review/briefs/[brief-filename].md and implement it.
Report back using ~/agent-infra/templates/implementation-report.md. Paste raw output.
```

For SYNTRA tasks with a brief file: use the brief path from TASKS.md.
For SYNTRA tasks without a brief: prompt = "Brief not yet written — architect must write it first."

Add a **Copy** button next to each such task. On click: copy the prompt to clipboard.
Button label: "Copy prompt" → "Copied ✓" for 2 seconds → back to "Copy prompt".

Use `navigator.clipboard.writeText()`. No external libraries.

### 2. "Uninitiated" status badge

A task is uninitiated if it is `briefed` (brief exists, executor not yet started) or `backlog`
(identified but no brief yet). These need the most attention.

For each task:
- `briefed` → badge: `READY` (green) — brief exists, waiting for executor
- `backlog` → badge: `NO BRIEF` (yellow) — needs architect attention first
- `in_progress` → badge: `RUNNING` (blue)
- `done` → badge: `DONE` (muted grey)
- anything else → badge: status string (muted)

Uninitiated tasks (`briefed` + `backlog`) should appear at the top of each section.
Done tasks should be collapsed under a `[N done — click to expand]` disclosure element.

### 3. Auto-refresh

Add a polling loop in client JS that refreshes the task data every 30 seconds.

Simplest implementation: a `<script>` block on the tasks page that calls
`location.reload()` every 30 seconds. Add a small "Last updated: {time}" label in the
header that updates on each reload.

If you want a non-reloading approach: fetch `/api/tasks-data` (new GET endpoint that returns
the same task JSON used to render the page) and update the DOM. Only implement this if it's
not significantly more complex — page reload is fine.

### 4. Brief preview on hover/expand

For tasks with a known brief file path: add an expand toggle (`▶ View brief`) that, on click,
shows the first 20 lines of the brief inline. Read the brief file at render time (SSR).
If the brief doesn't exist, show "Brief not found at {path}".

## DONE LOOKS LIKE

1. `npm run build` clean
2. `curl -s -u m:st http://127.0.0.1:8788/tasks` response contains "Copy prompt" and "READY"
3. Loading `/tasks` in a browser shows copy buttons on briefed tasks
4. Clicking "Copy prompt" on an EX task copies the correct handoff text (check clipboard)
5. The page includes a 30-second reload mechanism (meta refresh or JS interval)
6. Done tasks are collapsed by default

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && sleep 2
curl -s -u m:st http://127.0.0.1:8788/tasks | grep -oiE 'copy.prompt|READY|NO.BRIEF|RUNNING|last.updated' | sort -u
```

Expected: `READY`, `copy prompt`, and `last updated` in response.

## OUT OF SCOPE

- Marking a task in_progress from the UI (write to TASKS.md) — future work
- Real-time WebSocket updates
- Brief editing from the UI
- Any interaction beyond copy + collapse
