# AP-12 — Executor work-roots: grant writes where the brief actually works

**Loop:** A and B (executor reliability — unblocks every BX-* and cross-repo brief)
**Priority:** P0 · **Safety:** changes what dirs the codex sandbox can write; stays in `workspace-write` (no full-access). Touches aperture only.
**Status:** briefed · **Depends on:** none · **Runs cleanly today** (cwd=aperture is already writable)

## GOAL
The codex executor runs with every directory its brief declares it owns made writable, so file writes land instead of being silently denied by the sandbox.

## WHY
`launch-codex.ts` runs non-syntra briefs with `cwd=agent-infra`, `-s workspace-write`, and **no `--add-dir`**. BX-* briefs live in `agent-infra/` but write to `~/scripts`, `~/projects/boreal-leads`, and `crm.db` — all outside the sandbox. The agent does its analysis, every write is denied, it reports "relaunch with write access," and exits 0. This is the root of the silent-failure epidemic (the last ~8 BX/S runs). `codex exec` supports `--add-dir <DIR>` ("additional directories that should be writable alongside the primary workspace") — verified in codex-cli 0.133.0. We already have the brief's `## FILES IT OWNS` section declaring exactly what it touches; use it as the permission manifest.

## FILES IT OWNS
- `~/projects/aperture/src/pages/api/launch-codex.ts` (the `briefWorkContext` function + `codexArgs` assembly)

## DO NOT TOUCH
- Job-status logic (`child.once('exit', …)`) — that's AP-13
- tasks.ts, Taskboard.tsx, any other file
- The syntra `skipSandbox` path (leave as-is; syntra ingests need network — separate concern)

## SPEC

### 1. Derive writable roots from the brief
Add a function that, given a resolved brief path, reads the brief file and extracts the `## FILES IT OWNS` section (everything from that heading to the next `##`). For each path token in that section:
- Expand `~/` to `$HOME`; strip backticks, list markers (`-`), parenthetical notes (`(new)`, `(read-only)`), and trailing prose.
- Resolve to an existing ancestor: if the path or its parent doesn't exist yet (new files like `boreal_send.py`), walk up to the first existing directory.
- Map to its **top-level project root** from a known set: `~/scripts`, `~/projects/boreal-leads`, `~/projects/aperture`, `~/syntra`, `~/agent-infra`, `~/website`, `~/.local/share/boreal-outreach`. If a resolved path falls under one of these, use that root; otherwise use the path's own directory.
Dedupe the resulting roots.

### 2. Choose cwd + add-dirs
- `cwd` = the root that contains the most owned paths (ties → the brief's own repo, i.e. the dir of the brief file). codex needs a git repo as cwd → if the chosen cwd isn't a git repo, add `--skip-git-repo-check`.
- All other derived roots → `--add-dir <root>` (repeatable).
- Always also `--add-dir` the brief's own repo (so the agent can read the brief + write a report there if asked) and `~/.local/share/aperture/jobs` is NOT needed (job record is written by aperture, not codex).

### 3. Keep the existing special cases
- AP-* → cwd=aperture, plus derived roots (agent-infra will be among them). 
- syntra → unchanged skipSandbox path.
- Fallback when no `## FILES IT OWNS` parses cleanly: current behavior (cwd=agent-infra, no add-dirs) BUT log a warning line to the job log: `[aperture] WARN: could not derive work-roots from brief; running with repo-only write access`.

### 4. Read-only safety
Do NOT switch any task to `danger-full-access`. Service restarts (systemctl) remain impossible in workspace-write — that is handled separately in AP-13 (deferred restart-after). This brief is writes-only.

## DONE LOOKS LIKE
1. Launching BX-03 (owns `sms-inbox` in `~/scripts` + retry queue) runs with `--add-dir ~/scripts` and the agent can write `~/scripts/sms-inbox`.
2. Launching BX-02 runs with `~/scripts` and `~/projects/boreal-leads` writable; the executor can edit `crm.db`, `crm_lib.py`, and `bx02-crm-migrate`.
3. AP-* briefs still run (regression check: nothing about aperture-targeting briefs changed in effect).
4. A brief with a malformed FILES section logs the WARN line and falls back, doesn't crash the launch.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
# Dry inspection: add a temporary console.error(JSON.stringify({cwd, addDirs})) OR unit-test the deriver against three real briefs:
node --input-type=module -e "
import {briefWorkContext} from './src/pages/api/launch-codex.ts'  // if not exported, test via a tiny harness
" 2>&1 | head
# Real launch test (after build + restart): launch BX-03 from the board, then:
tail -40 \$(ls -t ~/.local/share/aperture/jobs/*.log | head -1)   # expect actual edits to ~/scripts/sms-inbox, NOT 'read-only file system'
grep -c "read-only file system\|outside .* sandbox" \$(ls -t ~/.local/share/aperture/jobs/*.log | head -1)  # expect 0
systemctl --user restart aperture
```

## OUT OF SCOPE
- Job-status honesty / blocked detection (AP-13)
- systemctl restarts from within a job (AP-13 deferred-apply)
- Network access for sandboxed jobs (syntra ingests) — keep the existing skip path
- Granting full-access sandbox to anything
