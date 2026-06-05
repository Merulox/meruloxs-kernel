# Workflow: Reviewer → Architect

---

## How reviewer sends results back

Reviewer fills in `~/agent-infra/templates/review-report.md` and reports to architect.

Architect reads the report and takes one of three actions:

---

## If PASS

1. Architect confirms acceptance
2. Update TASKS.md: status → `done`
3. Update CONTEXT.md: move task to "what was just completed"
4. If a decision was made during the task: add DECISIONS.md entry
5. Write the next brief

---

## If FAIL

Architect decides: is this a fix-brief (small, isolated) or a re-brief (significant)?

**Fix-brief (preferred for small issues):**
- Write a brief addendum or a new small brief describing only what needs to change
- Hand back to executor with the failure reason
- Update TASKS.md: add new fix task, keep original as `in_progress` with a note

**Re-brief (significant scope error or wrong approach):**
- Write a new brief that supersedes the old one
- Log in DECISIONS.md what changed and why
- Update TASKS.md: cancel old task with a note, add new task as `briefed`

---

## If ESCALATE

Reviewer flagged a design flaw or risk the brief didn't account for.

1. Architect reads the escalation
2. If it's a product decision: surface to product owner before accepting
3. If it's an architectural fix: update the brief, write a fix brief for executor
4. Log the escalation in DECISIONS.md with resolution

---

## Reviewer independence

Architect must not prime the reviewer with their own view before review.
Give reviewer only: the brief + the implementation report. Let them form an independent view.
