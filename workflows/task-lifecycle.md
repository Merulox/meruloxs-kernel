# Workflow: Task Lifecycle

---

## Full lifecycle

```
backlog → briefed → in_progress → [review] → done
                                      ↓
                                    fail → (fix brief) → in_progress → review → done
                                      ↓
                                  escalate → (PO decision) → re-brief → ...
```

---

## Stage definitions

### backlog
- **What it is:** Task identified but no brief written
- **Owner:** Architect
- **Entry:** Any agent or PO adds it to TASKS.md with a one-line description
- **Exit:** Architect writes a brief and marks `briefed`
- **Rule:** Nothing goes to an executor from backlog — brief first

### briefed
- **What it is:** Brief written, ready for executor
- **Owner:** Architect
- **Entry:** Architect writes brief in `docs/planning/`, updates TASKS.md
- **Exit:** Executor starts work → architect marks `in_progress`
- **Rule:** Brief must have all required sections before this status is set

### in_progress
- **What it is:** Executor is working on it
- **Owner:** Executor
- **Entry:** Architect hands brief to executor, marks in_progress in TASKS.md
- **Exit:** Executor completes and reports → architect reviews report
- **Rule:** Only one executor per task; if task is interrupted, note what was done

### review
- **What it is:** Awaiting reviewer confirmation
- **Owner:** Reviewer
- **Entry:** Executor reports done, architect decides review is needed
- **Exit:** Reviewer returns PASS / FAIL / ESCALATE
- **Rule:** For [DATA] tasks, review is mandatory. Architect may not skip it.

### done
- **What it is:** Verified complete — live state confirmed
- **Owner:** Architect
- **Entry:** ALL of the following:
  - VERIFY WITH commands ran and passed
  - Reviewer confirmed (if required)
  - Architect accepted
  - TASKS.md updated
  - CONTEXT.md updated
- **Rule:** "Done" means done in the live system, not done in the executor's report

### cancelled
- **What it is:** Task dropped before completion
- **Entry:** Architect or PO decision
- **Rule:** Always include reason in TASKS.md Notes column

### blocked
- **What it is:** Cannot proceed — waiting on external action
- **Entry:** Architect marks it when a dependency is unresolved
- **Rule:** Note the blocker and expected resolution in Notes

---

## New task intake

When a new task appears (from PO, discovered during work, bug report, etc.):

1. Add to TASKS.md with status `backlog`
2. Flag it if it has `[DATA]`, `[SCHEMA]`, `[DEPLOY]`, `[MONEY]` implications
3. Do not give it to an executor yet — write the brief first
4. Prioritize relative to existing tasks (P1 / P2 / P3)

**Rule:** New tasks discovered mid-task go into backlog. Do not expand the current task's scope.
