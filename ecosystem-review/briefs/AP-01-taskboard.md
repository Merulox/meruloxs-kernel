# AP-01: Aperture Taskboard

Status: ready. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Add a `/tasks` page to Aperture where the product owner can see all pending tasks across projects, read and respond to permission requests from executors, and approve/reject work — all without leaving the browser.

## WHY

The multi-agent system currently has no web interface for human-in-the-loop decisions. Executors that hit a scope question must wait for the PO to be in a Claude session. This brief closes that gap: executors write permission requests to a shared directory; Aperture shows them; the PO responds via form; executor polls for the response file.

## FILES IT OWNS

```
~/projects/aperture/src/pages/tasks.astro            — new page
~/projects/aperture/src/pages/api/respond.ts         — POST endpoint (writes response file)
~/projects/aperture/src/lib/tasks.ts                 — data readers for all task sources
~/projects/aperture/src/styles/global.css            — extend only (add task-specific classes)
```

## DO NOT TOUCH

- `src/pages/index.astro` (main dashboard — add-only if nav link is needed)
- `src/lib/data.ts` (monitor readers — do not modify)
- `src/middleware.ts` (auth layer)
- Any file outside `src/`

## DATA SOURCES

### 1. Permission requests (highest priority — show first)

Directory: `~/obsidian/claude-bus/permission-requests/`

**Request file format** (`<id>.request.md`):
```
---
id: <uuid>
requestor: <instance/role>
task: <task-id>
question: <the question>
urgency: HIGH|MED|LOW
created: <ISO timestamp>
---
<context paragraph>
```

**Response file** (`<id>.response.md`) — written by Aperture on form submit:
```
---
id: <uuid>
answered_at: <ISO timestamp>
---
<PO's answer text>
```

A request is "pending" if `<id>.request.md` exists and `<id>.response.md` does not.

If the directory doesn't exist, show an empty section (no error).

### 2. EX task board

File: `~/agent-infra/ecosystem-review/briefs/README.md`

Parse the markdown table rows (lines matching `| EX-N |`). Extract: id, status emoji (✅🔄⬜), title, brief path, risk gate. Show as a simple status grid. No interaction needed — read-only.

### 3. SYNTRA project tasks

File: `~/syntra/.agent/TASKS.md`

Parse the markdown table rows. Extract: id, status (backtick-wrapped), priority, title, notes. Group by status. Show `backlog` and `briefed` prominently (needs attention); show `done` collapsed.

### 4. Brain-bus queue

Directory: `~/obsidian/claude-bus/tasks/`

Subdirs: `pending/`, `claimed/`, `failed/`. Count files in each. Parse frontmatter from any `failed/` files (show `action` + `priority` fields). Show as a summary count row — not a full list.

## PERMISSION REQUEST FORM

For each pending request, render:

```html
<div class="request-card urgency-{HIGH|MED|LOW}">
  <div class="request-meta">{requestor} · {task} · {created}</div>
  <div class="request-question">{question}</div>
  <div class="request-context">{body}</div>
  <form method="POST" action="/api/respond">
    <input type="hidden" name="id" value="{id}" />
    <textarea name="answer" placeholder="Your answer..." required></textarea>
    <button type="submit">Respond</button>
  </form>
</div>
```

The POST `/api/respond` endpoint:
1. Reads `id` and `answer` from form body
2. Writes `~/obsidian/claude-bus/permission-requests/<id>.response.md` with the format above
3. Redirects back to `/tasks` (303)

If the permission-requests directory doesn't exist, create it on first write.

## NAVIGATION

Add a link to `/tasks` in the `<header class="topbar">` of `index.astro`:
```html
<a href="/tasks" class="nav-link">tasks</a>
```

Use existing CSS variables — do not add a new nav component.

## DONE LOOKS LIKE

1. `npm run build` clean
2. `curl -s -u m:st http://127.0.0.1:8788/tasks` returns HTTP 200 with "permission requests" and "ex tasks" text in the body
3. Writing a test request file and loading `/tasks` shows it in the pending section
4. Submitting the response form creates `<id>.response.md` and the request disappears from pending
5. No crash if permission-requests dir is missing, TASKS.md is missing, or README.md table changes format

## VERIFY WITH

```bash
# Build
cd ~/projects/aperture && npm run build 2>&1 | tail -3

# Restart service
systemctl --user restart aperture && sleep 2

# Page loads
curl -s -u m:st http://127.0.0.1:8788/tasks | grep -oiE 'permission.request|ex.task|syntra|brain.bus' | sort -u

# Test permission request round-trip
mkdir -p ~/obsidian/claude-bus/permission-requests
cat > ~/obsidian/claude-bus/permission-requests/test-001.request.md << 'EOF'
---
id: test-001
requestor: codex-test
task: EX-5
question: Is it safe to proceed with the bash_exec blacklist change?
urgency: HIGH
created: 2026-06-06T09:00:00
---
Context: About to modify FORBIDDEN_PATTERNS in genesis-core. Confirming architect approval before write.
EOF

curl -s -u m:st http://127.0.0.1:8788/tasks | grep -c "Is it safe to proceed"
# expect: 1

curl -s -u m:st -X POST http://127.0.0.1:8788/api/respond \
  -d "id=test-001&answer=Yes, approved. Proceed with the blacklist extension."
# expect: 303 redirect

test -f ~/obsidian/claude-bus/permission-requests/test-001.response.md && echo "response written"
```

## OUT OF SCOPE

- Real-time updates / polling / websockets (reload manually)
- Task creation via the web UI (tasks are created by agents/architect, not through this form)
- Editing or deleting tasks from the web UI
- Auth per-action (existing Basic Auth covers the page)
- Multi-project task scanning (SYNTRA only for now; other projects added later)
