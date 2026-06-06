# EX-1: Back Up the Engine (highest priority — loss prevention)

Status: ready. Architect 2026-06-05. Read `~/agent-infra/agents/executor.md` first.
**Do this before EX-2…EX-6.** The brain-* engine is currently unversioned and unbacked — one `rm` loses it.

## GOAL
Put `~/scripts/` under git, push to a private GitHub repo `Merulox/scripts`, and verify the existing backup services run.

## WHY
`~/scripts/` holds the live engine (brain-* bus/executor, realm-*, dozens of load-bearing tools). It has no repo and (per manifest) `backup-r2`/`backup-dotfiles` are stopped. This is the single highest-severity risk in the ecosystem.

## FILES IT OWNS
- `~/scripts/.git/` (new), `~/scripts/.gitignore` (new)

## DO NOT TOUCH
- Contents of any script (no edits — this is backup only)
- Other repos

## STEPS
1. `cd ~/scripts && git init`
2. Write `.gitignore`: exclude anything with secrets — `*.db`, `*.log`, `*-state.json`, `.secrets`, `*token*`, `*.key`, `*.pem`, `__pycache__/`, `*.pyc`, any `.env`. **Grep first** (`grep -rilE 'api[_-]?key|token|secret|password' ~/scripts | head`) and confirm flagged files are gitignored before committing.
3. `git add -A && git commit -m "Snapshot ~/scripts engine"`
4. Create private remote: `gh repo create Merulox/scripts --private --source=. --push` (requires `gh auth`; if not authed, STOP and report — user runs `gh auth login`).
5. Verify backups: `systemctl --user status backup-r2 backup-dotfiles genesis-memory-backup --no-pager`. If stopped/disabled, report state — do NOT enable without confirming they target the right destinations.

## DONE LOOKS LIKE
1. `git -C ~/scripts log --oneline` shows the snapshot commit
2. `gh repo view Merulox/scripts` exists, private, pushed
3. No secret/token/db file is tracked: `git -C ~/scripts ls-files | grep -iE 'token|secret|\.db$|\.env' ` returns nothing
4. Backup service states reported (running / stopped / misconfigured)

## VERIFY WITH
```bash
git -C ~/scripts ls-files | grep -iE 'token|secret|\.db$|\.env|\.pem|\.key'   # expect: empty
git -C ~/scripts log --oneline -1
gh repo view Merulox/scripts --json visibility,pushedAt 2>/dev/null
```

## OUT OF SCOPE
- Editing/refactoring scripts (that's EX-6)
- Enabling backup services without confirming destinations
