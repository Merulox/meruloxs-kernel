# Protocol: Parallel Executor Isolation via Git Worktrees

Use this protocol whenever two or more executors work on the same repository concurrently.

---

## Why this exists

Multiple Codex executors on the same repository without isolation create:
- Uncommitted file conflicts (executor A and B both modify `index.js`)
- Silent overwrites (later executor's changes wipe earlier ones)
- Mixed-state test runs (executor runs tests against another's partial changes)
- Review ambiguity (architect can't tell whose change is whose)

This protocol prevents all of these. Cost: ~2 minutes per executor setup.

---

## When to use

Use this protocol when:
- Two or more executor briefs will run in parallel
- Briefs touch overlapping files (same repo, even if different files)
- Any executor will modify files already modified by another uncommitted session

Skip when:
- Only one executor is active at a time (standard serialized workflow)
- The task is read-only (audit, probe, report)

---

## Protocol

### Architect: before handing off parallel briefs

1. Ensure the base branch is clean (no uncommitted changes)
2. Create a worktree for each executor:

```bash
# From the repo root (e.g., ~/syntra)
git worktree add ../syntra-ex-A -b ex-A-<brief-id>
git worktree add ../syntra-ex-B -b ex-B-<brief-id>
```

3. Add to each brief's handoff prompt:
```
Your worktree: ~/syntra-ex-A (branch: ex-A-<brief-id>)
Work exclusively in that directory. Do not touch ~/syntra directly.
```

4. When both complete: review, then merge each branch into main sequentially.

---

### Executor: during the task

1. `cd` into your assigned worktree, not the main repo
2. All changes go in the worktree
3. Run tests from the worktree
4. Report the worktree path and branch in your implementation report

```bash
# Verify you're in the right place
git branch --show-current    # should show ex-A-<brief-id>
git worktree list             # shows all active worktrees
```

5. Do not run `git merge`, `git rebase`, or `git push` — the architect handles merge

---

### Architect: after both executors report

1. Review each branch independently:
```bash
git diff main..ex-A-<brief-id>
git diff main..ex-B-<brief-id>
```

2. Merge the lower-risk branch first:
```bash
git checkout main
git merge ex-A-<brief-id>
```

3. Rebase the second branch on the updated main, resolve conflicts, merge:
```bash
git checkout ex-B-<brief-id>
git rebase main
# resolve any conflicts
git checkout main
git merge ex-B-<brief-id>
```

4. Run full test suite after each merge. If tests fail, stop — do not merge the second branch until the first is green.

5. Clean up worktrees:
```bash
git worktree remove ../syntra-ex-A
git worktree remove ../syntra-ex-B
git branch -d ex-A-<brief-id> ex-B-<brief-id>
```

---

## What this does NOT cover

- Three or more concurrent executors (extend the pattern — same logic, more worktrees)
- Executors on different repositories (no collision risk, no protocol needed)
- Merge conflict resolution strategy (case-by-case; escalate to PO if data model changes)

---

## Failure mode: executor worked in main repo anyway

If an executor modified `~/syntra` directly instead of their worktree:

1. Stash their changes: `git stash`
2. Create their worktree: `git worktree add ../syntra-ex-A -b ex-A-<brief-id>`
3. Pop stash into the worktree: `cd ../syntra-ex-A && git stash pop`
4. Continue from there

Document the protocol violation in DECISIONS.md.
