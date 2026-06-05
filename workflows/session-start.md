# Workflow: Session Start

Run this at the beginning of every architect session — takes 2–3 minutes.

---

## Step 1: Restore role

Read `~/agent-infra/agents/architect.md`

Or paste this prompt:
> Read `~/agent-infra/agents/architect.md`. Read `.agent/CONTEXT.md`. Read `.agent/TASKS.md`. Resume as architect.

## Step 2: Check live state

If any task shows `in_progress` in TASKS.md:

- Run the VERIFY WITH commands from its brief — do this BEFORE assuming it's done
- If it's actually done: update TASKS.md to `done`, update CONTEXT.md
- If it's not done: keep it `in_progress`, assess what's left

## Step 3: Read CONTEXT.md

Confirm your understanding of:
- What was just completed
- What is blocked
- What is next

## Step 4: Check for escalations

Scan DECISIONS.md and CONTEXT.md for "Open decisions needing Product Owner input."
If any: surface them to the product owner before starting new work.

## Step 5: Pick the next task

Look at TASKS.md:
- First: unblock any `blocked` tasks if the blocker is resolved
- Then: pick the next `briefed` task (brief already exists — hand to executor)
- Or: write a brief for the next `backlog` task

---

## For executor sessions (Codex)

Give codex this prompt:
> Read `~/agent-infra/agents/executor.md`.
> Read the task brief at `docs/planning/[filename].md`.
> Implement the task. Report back with the format in `~/agent-infra/templates/implementation-report.md`.

---

## For reviewer sessions

Give reviewer this prompt:
> Read `~/agent-infra/agents/reviewer.md`.
> Read the task brief at `docs/planning/[filename].md` — focus on DONE LOOKS LIKE and VERIFY WITH.
> Read the implementation report.
> Run all verify commands. Fill in `~/agent-infra/templates/review-report.md`.
