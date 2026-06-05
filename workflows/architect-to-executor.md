# Workflow: Architect → Executor Handoff

---

## Pre-handoff checklist (architect)

Before handing anything to an executor:

- [ ] Brief is written at `docs/planning/<task-id>-<name>.md`
- [ ] Brief has all required sections (GOAL, WHY, FILES IT OWNS, DO NOT TOUCH, DONE LOOKS LIKE, VERIFY WITH, OUT OF SCOPE)
- [ ] VERIFY WITH commands are runnable — tested by architect or confirmed possible
- [ ] Any required setup (env vars, running services) is noted in the brief
- [ ] Task is marked `briefed` in TASKS.md
- [ ] Any `[DATA]` or `[SCHEMA]` task has been flagged — Reviewer required on completion

## Handoff message

Give this to the executor (codex) verbatim:

```
Read ~/agent-infra/agents/executor.md.
Then read docs/planning/[task-id]-[name].md and implement the task.
Report back using the format at ~/agent-infra/templates/implementation-report.md.
Paste raw command output — do not summarize.
```

## After handoff

Update TASKS.md: change status from `briefed` → `in_progress`.

---

## What to do if executor asks a clarifying question

If the question is in scope (a missing spec detail): answer it, update the brief to reflect the clarification, log in `/logs/agent-comms.md`.

If the question is out of scope (a product direction question): escalate to product owner, do not answer unilaterally.

## What to do if executor reports an unexpected blocker

If it's a technical finding (API behaves differently than assumed): update the brief, hand back to executor.

If it's a scope question (brief asks for X but X requires Y): write a separate brief for Y, add to TASKS.md as a dependency, don't expand the current brief.
