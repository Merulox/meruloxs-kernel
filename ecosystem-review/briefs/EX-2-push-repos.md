# EX-2: Push the New Repos (secret-safe)

Status: ready. Architect 2026-06-05. After EX-1. Read `~/agent-infra/agents/executor.md`.

## GOAL
Create remotes and push three repos: `agent-infra` (public), `aperture` (private), `genesis` (private). **Gate: verify each .gitignore excludes secrets and all Genesis memory before the first push.**

## WHY
These exist locally with no remote. Backing them up + (for agent-infra) making the methodology public. Genesis is identity-bearing — its memory must never leave the machine.

## FILES IT OWNS
- `.gitignore` in `~/agent-infra`, `~/projects/aperture`, `~/projects/genesis` (create/extend as needed)

## DO NOT TOUCH
- Source code in any repo
- `~/obsidian/` (never commit it anywhere)

## STEPS — per repo, in this order

### A. agent-infra → PUBLIC
1. `grep -rilE 'token|secret|api[_-]?key|password|\.env' ~/agent-infra` → confirm nothing sensitive (it's pure docs; should be clean)
2. `cd ~/agent-infra && gh repo create Merulox/agent-infra --public --source=. --push`

### B. aperture → PRIVATE
1. Confirm `.gitignore` covers `node_modules/`, `dist/`, `.astro/`, `.env*` (already does)
2. Confirm the basic-auth creds (m/st) are acceptable in a private repo, or move to env — **report this**, don't decide
3. `cd ~/projects/aperture && gh repo create Merulox/aperture --private --source=. --push`

### C. genesis → PRIVATE, MEMORY EXCLUDED (critical)
1. Write/verify `.gitignore` excludes: any path under `~/obsidian`, `*.log`, `*-state.json`, `__pycache__/`, `.next-wakeup`, any `.secrets`, tokens. Genesis identity lives in `~/obsidian/knowledge/projects/genesis/` — that's OUTSIDE the repo, good, but double-check nothing symlinks/copies it in.
2. `git -C ~/projects/genesis status` — confirm only code (daemon.py, agent.py, telegram-bridge.py, genesis.nix, CLAUDE.md, ambient-interface-vision.md, .agent/) is staged. **If any soul/autobiography/memory content appears, STOP and report.**
3. `cd ~/projects/genesis && gh repo create Merulox/genesis --private --source=. --push`

## DONE LOOKS LIKE
1. Three repos exist with correct visibility (agent-infra public; aperture, genesis private)
2. `git -C ~/projects/genesis ls-files` contains NO soul/autobiography/memory/vault content
3. No `.env`, token, or key tracked in any of the three

## VERIFY WITH
```bash
gh repo view Merulox/agent-infra --json visibility    # public
gh repo view Merulox/aperture   --json visibility     # private
gh repo view Merulox/genesis    --json visibility     # private
git -C ~/projects/genesis ls-files | grep -iE 'soul|autobio|memory|patterns|obsidian'   # expect empty
```

## OUT OF SCOPE
- realm (no repo — EX-4 archives it in place)
- Any code change
