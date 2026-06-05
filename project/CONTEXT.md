# Project Context — Live State

_Updated at the end of every session. This file is the re-entry point after
any interruption. Read this + TASKS.md to fully restore context in under 2 minutes._

Last updated: [YYYY-MM-DD HH:MM]
Updated by: [architect / product owner]

---

## Current state summary

[2–3 sentences on where the project is right now. What was just finished. What is in flight.]

---

## What was just completed

- [task or milestone]
- [task or milestone]

## What is in flight (do not start anything new until these resolve)

- **[TASK-ID]**: [brief description] — status: in_progress / awaiting review
  - Brief: `docs/planning/[filename].md`
  - Executor: [who]
  - Blocking: [what it's blocking, if anything]

## What is next (already decided, brief not yet written)

- [next task — one line]
- [next task — one line]

---

## Key decisions made this session

- [decision summary] — see DECISIONS.md entry [ID]

---

## Known blockers

- [blocker] — owned by [who] — ETA [date or "unknown"]

---

## Live system state

| System | State |
|--------|-------|
| [database / NocoDB] | [X records, last import date] |
| [API server] | [running / stopped] |
| [web client] | [running / stopped] |
| [last verified clean] | [date + what audit ran] |

---

## Resume instructions

If resuming as architect:
1. Read this file
2. Read TASKS.md — find in_progress items
3. If an in_progress task exists: run its VERIFY WITH commands before assuming it's done
4. Write the next brief or handle the escalation in the open decisions above
