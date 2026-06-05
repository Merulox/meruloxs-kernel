# Workflow: Executor → Reviewer Handoff

---

## When executor hands off for review

After completing implementation, executor:

1. Fills in `~/agent-infra/templates/implementation-report.md`
2. Reports to architect: "Implementation complete. Report: [paste report]"
3. Architect confirms report looks complete, then opens a Reviewer session

Executor does NOT directly contact reviewer. Architect is the relay.

---

## Tasks that always require a Reviewer

- Any task with `[DATA]` flag (writes to NocoDB or other database)
- Any task with `[SCHEMA]` flag
- Any task with `[DEPLOY]` flag
- Any task where DONE LOOKS LIKE includes "audit passes clean"

## Tasks where Reviewer is optional

- Read-only tasks (probes, research scripts)
- UI-only changes with no data path
- Documentation-only changes

---

## Reviewer handoff message

Give this to a fresh reviewer session:

```
Read ~/agent-infra/agents/reviewer.md.
Read docs/planning/[task-id]-[name].md — focus on DONE LOOKS LIKE and VERIFY WITH.
Read the implementation report below.
Run all verify commands yourself.
Fill in ~/agent-infra/templates/review-report.md and report back.

[paste implementation report here]
```

---

## After review

- If PASS: architect accepts, updates TASKS.md to `done`, updates CONTEXT.md
- If FAIL: architect sends issues back to executor via a fix brief (or directly if trivial)
- If ESCALATE: architect handles the escalation before accepting

Mark review complete in agent-comms.md.
