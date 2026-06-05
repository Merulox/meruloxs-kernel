# Workflow: Session Shutdown

Run this before ending any architect session — takes 3–5 minutes.
The project state lives in files. If you skip this, the next session starts blind.

---

## Step 1: Update TASKS.md

For every task touched this session:
- Move completed tasks to `done`
- Move started tasks to `in_progress`
- Add any new tasks discovered to `backlog`

## Step 2: Update CONTEXT.md

Fill in:
- "What was just completed" — what finished this session
- "What is in flight" — any in_progress tasks with their current state
- "What is next" — already-decided next tasks
- "Key decisions made this session" — link to DECISIONS.md entries
- "Known blockers" — anything waiting on external action
- "Live system state" — record counts, last verified date

## Step 3: Log new decisions

For every architectural or product decision made this session:
- Add a D-NNN entry to DECISIONS.md
- Include context, decision, alternatives, consequences

## Step 4: Log new risks

If anything risky was discovered or resolved:
- Add or update an entry in RISKS.md

## Step 5: Commit project memory

```bash
git add .agent/ docs/ SESSION.md ROLE.md
git commit -m "chore: update project memory — [session summary]"
```

Do not auto-commit code changes. Only commit project memory files.

## Step 6: Note what the next session should start with

Add to the bottom of CONTEXT.md:
> Resume: [one sentence on what to do first next session]

---

## Minimum viable shutdown (if time-pressed)

At absolute minimum, update CONTEXT.md with:
- One sentence on where you stopped
- The exact next action to take

Even 30 seconds of CONTEXT.md update is worth it.
