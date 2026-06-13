# AP-16 — Recalibrate blocked-detection so expected sandbox limits don't false-block

**Loop:** A and B (executor correctness — makes AP-13/AP-15/restart-after actually function)
**Priority:** P0 · **Safety:** changes job-status classification only; aperture-only
**Status:** briefed · **Depends on:** AP-13, AP-15 · **Runs through the executor**

## GOAL
A codex job is classified `blocked` only when a REAL blocker stopped the work — not when the executor merely couldn't perform an in-sandbox *verification* step (curl localhost, git, systemctl) that the orchestrator/architect handles anyway.

## WHY
Measured this session: **every executor job came back `blocked`, and every one actually succeeded.** The blocked reasons were sandbox-expected limitations the executor honestly reported — "couldn't verify the live API, service not running," "git/systemctl prohibited," "live endpoint verification pending." AP-13's detector treats these as work-failures. Consequence: nothing reaches `status==='done'`, so **AP-15's auto-commit and `restart-after` never fire** (both gate on `done`) — e.g. AP-11's work landed but produced no commit; HEAD never moved. The detector must distinguish a real blocker (the work couldn't be done) from a deferred verification (the work is done; the architect/orchestrator verifies). The architect is the true acceptance gate (sets README `done` after VERIFY WITH), so biasing job-status toward `done` is safe — a wrongly-`done` job is caught at verification, whereas a wrongly-`blocked` job silently kills commit+restart.

## FILES IT OWNS
- `~/projects/aperture/src/pages/api/launch-codex.ts` (`blockedReasonFor` + helpers it uses)
- `~/agent-infra/agents/executor.md` (report-guidance: what is / isn't a blocker)

## DO NOT TOUCH
- The exit-code path (`exit !== 0` → `failed` stays)
- applyCommit / applyRestarts / work-roots
- The `-o` last-message capture

## SPEC

### 1. Recalibrate `blockedReasonFor(content)`
Classify `blocked` ONLY if EITHER:
- **(a) An explicit hard-block phrase** appears (case-insensitive): `must .* authorize` / `authorize the required` / `outside .* FILES IT OWNS` / `not in FILES IT OWNS` / `MISSING_DEP` / `BRIEF_ERROR` / `NEEDS_CLARIFICATION` / `command not found` / `no such file or directory`. → return that match's context.
- **(b) The `## Blockers or open questions` section** has real content after filtering — i.e. non-empty, not `None`/`N/A`, AND not solely composed of EXPECTED-LIMITATION lines (below).

**EXPECTED-LIMITATION denylist (these alone NEVER block):** lines matching any of —
`live .*(verification|endpoint|api)` · `service (was|is)?\s*not running` · `could not (curl|reach|connect)` · `localhost` · `\bgit\b.*(prohibit|forbid|read-only|not allowed|unavailable)` · `\.git/` · `systemctl` · `user scope bus` · `verification .* pending` · `unverified because` · `restart .* (not run|pending)`.
Strip these lines from the blockers section before deciding (b).

**Remove the Deviations-section scan entirely** — Deviations are informational (executors legitimately note "live verification not run"), not blockers. (The old `not executed|not modified|could not|was not run` heuristic is the main false-positive source — delete it.)

Keep returning a short `blockedReason` context string when (a) or (b) fires.

### 2. executor.md — define blocker vs expected-limitation
In the "When blocked" section, add: these are EXPECTED and must NOT be reported as blockers (the orchestrator commits/restarts and the architect verifies live): inability to `curl`/reach localhost or verify a live endpoint; inability to run `git`; inability to run `systemctl`; a service not being reachable from the sandbox. Report a blocker ONLY when the actual implementation could not be completed: missing dependency, a file/API that doesn't match the brief, a required step outside FILES IT OWNS needing architect authorization, or genuinely ambiguous requirements. Put real blockers in `## Blockers or open questions`; put expected-limitation notes in `## Deviations from the brief` instead.

## DONE LOOKS LIKE
1. A job whose only "blocker" is "couldn't verify live endpoint / git / systemctl" → classified **`done`** (so commit + restart fire).
2. A job that genuinely needs authorization (e.g. BX-02's "must authorize crm_lib.py") → still **`blocked`**.
3. Replaying this session's corpses through the detector: AP-11/AP-14/AP-15 → done; BX-02-first-run → blocked.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
node --experimental-strip-types --input-type=module -e "
import { blockedReasonFor } from './src/pages/api/launch-codex.ts';
const F='/home/merulox/.local/share/aperture/jobs/';
import {readFileSync} from 'node:fs';
for (const id of ['9d500175-a684-4a40-b49f-873296fda866','f3d287e7-2f89-4944-a486-8322f86b7026']) {
  console.log(id.slice(0,8), 'blocked?', !!blockedReasonFor(readFileSync(F+id+'.last.md','utf8').catch?'':readFileSync(F+id+'.last.md','utf8')));
}
"  # both should print blocked? false
# Then dogfood: relaunch any aperture task; on clean completion expect a commit:
git -C ~/projects/aperture log --oneline -1   # "<TASK>: ... [executor]"
```

## OUT OF SCOPE
- Branch/push strategy · the architect's README `done` gate (unchanged — still human) · retry automation
