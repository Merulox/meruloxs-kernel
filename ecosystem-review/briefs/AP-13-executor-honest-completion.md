# AP-13 — Executor honest completion: never report a blocked job as done

**Loop:** A and B (executor reliability — kills silent failure)
**Priority:** P0 · **Safety:** changes job-status meaning + adds an allowlisted post-job service restart. Touches aperture only.
**Status:** briefed · **Depends on:** AP-12 (writes must land before "did it work?" is meaningful) · **Runs cleanly today**
**Supersedes:** AP-11's badge half (AP-11 keeps only the NOW-feed decline filter)

## GOAL
A codex job is marked `done` only when it actually completed its work; blocked or no-op runs are marked `blocked` with the reason surfaced on the taskboard; and the one thing the sandbox can't do — restarting a live service — happens automatically after a clean run via a declared, allowlisted restart.

## WHY
`launch-codex.ts` sets `status: exitCode === 0 ? 'done' : 'failed'`. But `codex exec` exits 0 whenever the agent finishes its turn, including when it wrote nothing and reported "relaunch with permissions." Result: ~8 consecutive blocked runs all stamped `done`, the board shows them as complete, and you relaunch paid jobs that already "succeeded" (MO-01/HK-01) while real work (BX-02/BX-03) never happened. Exit 0 is necessary but not sufficient. The executor report template already has `## Deviations from the brief` and `## Blockers or open questions` sections — capture the agent's final message and read them. Separately, BX-02/BX-03 need a `systemctl --user restart`, which `workspace-write` forbids; defer it to aperture post-run.

## FILES IT OWNS
- `~/projects/aperture/src/pages/api/launch-codex.ts` (capture last message via `-o`, status computation, restart-after)
- `~/projects/aperture/src/lib/tasks.ts` (badge overlay from honest job status)
- `~/projects/aperture/src/components/Taskboard.tsx` + the codex job row component (render `blocked` state + reason)
- `~/projects/aperture/src/styles/global.css` (blocked/awaiting-verify badge styles)

## DO NOT TOUCH
- `briefWorkContext` / work-roots (AP-12 owns it)
- The NOW feed / actions.ts (AP-11)
- briefs/README.md and all status sources — UI stays a viewer, never writes status

## SPEC

### 0. Fix the invalid syntra sandbox flag (one line, do this first)
`launch-codex.ts` line ~208 uses `--dangerously-skip-sandbox`, which **does not exist in codex-cli 0.133.0** — every syntra launch dies instantly with `error: unexpected argument '--dangerously-skip-sandbox' found` (this is why S-14/S-17 errored). Replace it with the real flag: `--dangerously-bypass-approvals-and-sandbox`. Verify after build: launching a syntra task no longer errors on an unknown argument.

### 1. Capture the agent's final report
Add `-o <jobPath>.last.md` to the codex args (writes the agent's last message). This is the executor's implementation report.

### 2. Honest status on exit
Replace the exit handler's status rule. After exit:
- exit code ≠ 0 → `failed`.
- exit 0, then read `<jobPath>.last.md` (and, as fallback, the tail of the job log). Mark **`blocked`** if any of these match (case-insensitive):
  - `read-only file system`, `outside .* sandbox`, `permission denied`, `could not be written`, `relaunch with`, `is outside .* FILES IT OWNS`, `operation not permitted`
  - a `## Blockers or open questions` section whose body is non-empty and not just `None`/`N/A`
  - a `## Deviations from the brief` section listing that required steps were skipped (body contains `not executed`, `not modified`, `could not`, `was not run`)
- exit 0 with none of the above → `done`. Store a `blockedReason` field (the first matched line + up to 400 chars of surrounding context) on the job record when blocked.
- Optional secondary signal: if the chosen cwd is a git repo, record `git status --porcelain | wc -l` delta isn't required, but if zero files changed AND status would be `done`, downgrade to `blocked` with reason `no file changes produced`.

### 3. Surface it (no more silent)
- Job record gains `blockedReason?: string`.
- Taskboard codex-job row: `blocked` renders a red **BLOCKED** badge with the reason shown inline (expandable), distinct from `failed` (process error) and `done`.
- Task badge overlay in tasks.ts (the AP-11 badge logic, now living here): for a `briefed` task whose latest job is `blocked` → badge **BLOCKED — see reason**, keep the launch button; latest job `done` exit 0 clean → **AWAITING VERIFY** (orange), no launch button, show finish time; `running` → **RUNNING**; `failed` → **FAILED — RELAUNCH**. README `done`/`review` always wins over job state.

### 4. Deferred service restart (the sandbox-impossible step)
- Briefs may declare services to restart in their frontmatter or a `## APPLY` line, format: `restart-after: sms-inbox, calendly-poller`.
- After a job resolves to `done` (not blocked/failed), aperture parses that directive from the brief file and runs `systemctl --user restart <svc>` for each — **only if `<svc>` is in a hardcoded allowlist**: `sms-inbox sms-webhook missed-call-bot calendly-poller callback-reminder pipeline-integrity-check`. Anything not on the allowlist is logged and skipped (never restart aperture itself from within a job — circular; aperture deploys stay manual).
- Append the restart result to the job log: `[aperture] restart sms-inbox: active`.

## DONE LOOKS LIKE
1. A job that exits 0 but reports a blocker is marked `blocked` (not `done`) and the reason shows on the board.
2. Re-running a verified-done task is discouraged: its badge reads AWAITING VERIFY with no launch button until the architect flips README.
3. A `done` BX-03 job (which declares `restart-after: sms-inbox`) leaves sms-inbox freshly restarted, logged in the job log.
4. A genuine clean job still reads `done`.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
systemctl --user restart aperture
# Replay the known-blocked corpse to prove detection:
cp ~/.local/share/aperture/jobs/d39e3549-9820-4fac-be56-6c89bfcbec74.log /tmp/blocked-sample.md
node -e "/* call the blocked-detector on /tmp/blocked-sample.md; expect match */" 2>&1 | head
# Live: launch a no-op/blocked-prone task, confirm board shows BLOCKED + reason:
curl -s -u <auth> localhost:8788/api/tasks-data | python3 -c "import json,sys;[print(t['id'],t['statusBadge']) for t in json.load(sys.stdin)['exTasks']]"
# Restart allowlist: launch a task declaring restart-after: sms-inbox, then:
grep "restart sms-inbox" \$(ls -t ~/.local/share/aperture/jobs/*.log | head -1)
systemctl --user show sms-inbox -p ActiveEnterTimestamp   # recent
```

## OUT OF SCOPE
- The NOW-feed decline filter (stays in AP-11)
- Auto-writing task status back to README from the UI (never)
- Restarting aperture itself automatically (manual deploy)
- Network for sandboxed jobs
- Retry/auto-relaunch of blocked jobs (surface only; human decides)
