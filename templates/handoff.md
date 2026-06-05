# Handoff: [Project Name] — [YYYY-MM-DD HH:MM]

Use when: switching sessions, handing off to a different Claude instance, or creating
a compaction-safe state dump.

---

## Role being handed off

[ ] Architect
[ ] Executor (task: [ID + brief path])
[ ] Reviewer (task: [ID + brief path])

## Re-entry prompt

Paste this into the new session to restore context:

```
Read ~/agent-infra/agents/[role].md.
Read [project]/.agent/CONTEXT.md.
Read [project]/.agent/TASKS.md.
[Optional: Read docs/planning/[task].md for the current task.]
Resume as [role].
```

---

## What was in progress at handoff

**Task:** [ID + title]
**Status:** in_progress / briefed / review
**Brief:** `docs/planning/[filename].md`

What was done before handoff:
- [step completed]
- [step completed]

What is left:
- [step remaining]
- [step remaining]

## Key facts the new session needs

[Any non-obvious context that is not in the files — e.g., "the API returns null for unauthenticated requests, but the brief assumes it returns a value — we discovered this after writing the brief."]

## Open decisions or blockers

- [decision needed / blocker]

## Files that changed this session (not yet committed)

```bash
git status
```

[paste output or list manually]

---

## Handoff checklist

- [ ] CONTEXT.md updated with current state
- [ ] TASKS.md has correct statuses
- [ ] Any new decisions logged in DECISIONS.md
- [ ] New risks logged in RISKS.md
- [ ] This handoff doc is complete enough that the new session can start in 2 minutes
