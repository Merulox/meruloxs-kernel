# AP-15 — Orchestrator commits each task's work on a clean run (no push)

**Loop:** A and B (executor hygiene — kills the entangled-working-tree problem)
**Priority:** P1 · **Safety:** local git commits only, NEVER push; aperture-only code change
**Status:** briefed · **Depends on:** AP-12, AP-13 (done) · **Runs through the executor**

## GOAL
When a codex job completes cleanly (`status === 'done'`), Aperture commits *that task's owned files*, in whatever repo each lives, with a task-tagged message — and never pushes. One task = one isolated, revertable commit.

## WHY
Executors can't commit (sandbox makes `.git` read-only for `--add-dir` repos — this false-blocked BX-02), and committing from inside an unverified sandbox run is the wrong gate anyway. So today every task's changes pile up uncommitted and **entangle**: right now `~/scripts` holds BX-02 + BX-03 + SYS-01 edits mixed together, and aperture holds AP-09/10/13/14 — you can't tell which file belongs to which task, and reverting one means surgery on the heap. The fix mirrors `restart-after`: the trusted orchestrator (aperture, un-sandboxed) commits per task after a clean run. Result: atomic attribution, `git revert <sha>` rollback, and the architect verifies an isolated diff. **Reconciliation with "don't auto-commit":** that rule protects *shared/pushed* history — AP-15 commits locally and NEVER pushes; the PO still owns every push. (This policy is scoped to the executor pipeline; interactive Claude sessions still don't auto-commit.)

## FILES IT OWNS
- `~/projects/aperture/src/pages/api/launch-codex.ts` (add `applyCommit`, call it in the done branch)
- `~/agent-infra/agents/executor.md` (flip the git line — see SPEC 5)

## DO NOT TOUCH
- `restart-after`/`applyRestarts` logic beyond ordering · the classifier · work-root derivation
- The user's global `~/.claude/CLAUDE.md` (out of scope; "don't auto-commit" there governs interactive Claude, not this pipeline)
- crm.db or any data file (see exclusions)

## SPEC

### 1. When
In the exit handler, only when the computed `status === 'done'` (not blocked/failed). Order: **commit first, then `applyRestarts`** (restart runs the now-committed code).

### 2. What to commit — the brief's owned files, grouped by repo
- Parse `## FILES IT OWNS` from the brief (reuse AP-12's parser). Resolve each entry: expand `~`, strip backticks/parenthetical notes, expand directory/glob entries (e.g. `src/components/now/*`) to their matching paths.
- Group resolved paths by their containing git repo root (`git rev-parse --show-toplevel`).
- **Exclusions (never stage):** anything matching `*.db`, `*.sqlite*`, `*.bak-*`, or paths under a `boreal-leads` data dir that aren't `*.md`/`*.py`/`*.yaml`/`*.json` text. (We commit code + reports, never the live DB binary.)
- For each repo: `git -C <root> add -- <its owned paths that exist>`; if `git diff --cached --quiet` (nothing staged) → skip that repo, log `[aperture] commit <task>: no changes in <root>`.

### 3. The commit
Per repo with staged changes:
`git -C <root> commit -m "<TASK-ID>: <taskTitle> [executor]" -m "job <jobId> · brief <briefBasename>"`
Log `[aperture] commit <task> @ <root>: <short-sha>`. On failure, log the error (don't crash the handler).

### 4. NEVER push
No `git push` anywhere, ever. No remote operations. Add a comment asserting this.

### 5. executor.md
Replace the current line that forbids `git commit/add` with:
> - Run any `git` write (`add`/`commit`/`push`). The sandbox makes `.git` read-only, and Aperture commits your owned files for you on a clean run (task-tagged, **never pushed** — the PO pushes). Leave changes as working-tree edits; just report what you changed.

### 6. Safety notes in code
- Committing aperture itself is fine (commit writes `.git`, doesn't restart the process — unlike the circular restart case).
- Committing unverified "done" work is acceptable *because* every commit is one `git revert <sha>` and nothing is pushed; the architect's verification gates the push.

## DONE LOOKS LIKE
1. A clean task run produces exactly one commit per touched repo, message `^<TASK-ID>: .* \[executor\]$`, containing only that task's owned files.
2. A task touching two repos (owned files in each) produces one commit in each.
3. No `*.db` ever staged; no `git push` ever issued (grep the code).
4. A blocked/failed job produces NO commit.
5. `executor.md` reflects the new policy.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
grep -n "push" src/pages/api/launch-codex.ts   # no git push anywhere
systemctl --user restart aperture
# Dogfood: launch a tiny no-op-ish briefed task, then:
git -C ~/projects/aperture log --oneline -1     # shows "<TASK>: ... [executor]"
git -C ~/projects/aperture log -1 --stat        # only that task's owned files
git -C ~/projects/aperture status --porcelain   # clean for the committed files
git -C ~/projects/aperture log @{u}..HEAD --oneline  # commits exist locally, NOT pushed
```

## OUT OF SCOPE
- Pushing / PRs / branches (PO pushes; revisit branch-per-task later if desired)
- Committing the existing entangled pile (PO commits that manually one last time)
- Auto-commit for interactive Claude sessions (unchanged)
- crm.db / data versioning
