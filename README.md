# Agent Infrastructure — Daily Use Guide

Local multi-agent system for Merulox projects.
Designed for: SYNTRA, Merulox website, product pipelines, and any future project.

---

## The five-role model

| Role | Who | Primary artifact |
|------|-----|-----------------|
| Product Owner | You | Decisions, priorities, escalations |
| Architect | Claude Opus/Sonnet | Briefs, reviews, project memory |
| Executor | Codex | Code, fixes, implementations |
| Reviewer | Claude Sonnet | Pass/fail reports, issue flags |
| Specialist | Any agent | Research, design, data work |

---

## Starting a new session (30 seconds)

**Architect session:**
> Read `~/agent-infra/agents/architect.md`.
> Read `.agent/CONTEXT.md` in the current project.
> Read `.agent/TASKS.md`.
> Resume as architect.

**Executor session (Codex):**
> Read `~/agent-infra/agents/executor.md`.
> Read the task brief at `docs/planning/<task>.md`.
> Implement the task. Report back with the implementation report template.

**Reviewer session:**
> Read `~/agent-infra/agents/reviewer.md`.
> Read the task brief DONE LOOKS LIKE and VERIFY WITH sections.
> Run the verify commands. Fill in `templates/review-report.md`. Report to architect.

---

## Starting a new project

```bash
mkdir -p ~/projects/<name>/.agent/logs
cp ~/agent-infra/project/* ~/projects/<name>/.agent/
cp ~/agent-infra/logs/*    ~/projects/<name>/.agent/logs/
```

Fill in `.agent/PROJECT.md` first. Everything else follows from there.

---

## Daily workflow

```
1. Architect reads CONTEXT.md + TASKS.md                 (2 min)
2. Architect picks next task, writes brief in docs/planning/  (10–30 min)
3. You hand brief to Codex: "Read this brief and implement it"
4. Codex implements, reports back with implementation-report
5. Architect runs verification commands from brief         (2 min)
6. If needed: Reviewer session confirms pass/fail
7. Architect accepts or writes fix brief
8. Architect updates TASKS.md, CONTEXT.md, DECISIONS.md
9. Architect writes next brief or closes session
```

---

## New task intake

When you think of a new task:

1. Add it to `.agent/TASKS.md` with status `backlog`
2. Add any risk flag if it touches data, money, or deployment
3. Architect picks it up at next session and writes the brief

Do NOT hand backlog items directly to executors. Brief first, always.

---

## Resume after interruption

```
Read ~/agent-infra/agents/architect.md
Read .agent/CONTEXT.md
Read .agent/TASKS.md — look for any in_progress tasks
If in_progress task exists: check what the brief says, verify what was actually done
Resume from there
```

The project state lives in files, not in conversation history. An interrupt costs seconds.

---

## "Done" means done

A task is done when ALL of the following are true:

- [ ] Verification commands from the brief ran and passed
- [ ] Reviewer confirmed (if the task touched data, payments, schema, or public output)
- [ ] Architect accepted (not just executor reported)
- [ ] TASKS.md updated to `done`
- [ ] CONTEXT.md updated with new state
- [ ] If a decision was made: DECISIONS.md entry added

"The executor said it's done" is not done.

---

## Escalate to Product Owner when

- Product direction changes
- Scope expansion (new features, new systems)
- Data schema changes with migration risk
- Deleting data or records
- Deployment / publishing to production
- Paid services (API keys, subscriptions)
- Security-sensitive changes
- Unresolved disagreement between agents
- Any action that cannot be undone

---

## File locations

| What | Where |
|------|-------|
| Role definitions | `~/agent-infra/agents/` |
| Workflow protocols | `~/agent-infra/workflows/` |
| Blank templates | `~/agent-infra/templates/` |
| Project memory | `<project>/.agent/` |
| Task briefs | `<project>/docs/planning/` |
| Agent comms log | `<project>/.agent/logs/agent-comms.md` |
| Session log | `<project>/.agent/logs/session-log.md` |

---

## SYNTRA example

- Briefs: `~/syntra/docs/planning/task-b1-bellroy-probe.md`
- Project memory: `~/syntra/.agent/` (to be created)
- Existing SESSION.md continues to serve as CONTEXT.md equivalent
- ROLE.md in project root serves as quick heartbeat

---

## What still needs your decision

- Whether to move SYNTRA's SESSION.md into `.agent/CONTEXT.md` or keep both
- Whether to run a Reviewer pass on Bellroy Task B2 (data write — recommend yes)
- Future: whether to automate any of the relay steps with a file-watcher daemon
