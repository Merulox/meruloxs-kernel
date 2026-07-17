# AP-29: Blocked-classifier recalibration — quoting an error ≠ being blocked

**Status:** briefed
**Depends on:** — (AP-16 was the first pass; this closes what it missed)
**Date:** 2026-07-04
**Touches:** `~/projects/aperture/src/pages/api/launch-codex.ts` (HARD_BLOCK/EXPECTED_LIMITATION/blockedReasonFor), `~/kernel/agents/executor.md` (reporting contract)

<!-- gates: depends=; inputs=; confirms= -->

---

## GOAL

A completed job whose report *quotes* an already-worked-around error is classified `done`, not `blocked` — while genuinely blocked jobs still surface. Regression-proven against the three real false-blocked reports from 2026-07-04.

## WHY

Three consecutive false blocks (AP-27 job `31da32e2`, S-28 job `fa17a40b`, plus repeated D-010-class near-misses): each time the executor **finished the work**, but `blocked` status meant (a) `applyCommit` never ran → architect hand-commits every time (D-010 pattern is now partially *caused* by this), (b) the AP-27 Telegram ping says ⚠️ blocked → PO alarm for nothing. Root cause, verified in code: `HARD_BLOCK` (`launch-codex.ts:197`) matches phrases like `command not found` across the **entire** last message — but honest reports quote error output inside "Commands run" and "Deviations" sections precisely when describing successful workarounds. Transparency is being punished; the incentive gradient points toward executors *hiding* errors, which is the worst possible failure mode for a trust pipeline.

## ROOT CAUSE (verified 2026-07-04)

- `blockedReasonFor` (`launch-codex.ts:212`): `HARD_BLOCK.exec(content)` over the whole report. S-28's report contained the literal quote `zsh:1: command not found: openssl` in Deviations (workaround: Node crypto — task fully done, own verification 403/403/200 passed) → blocked.
- AP-27's report: `read-only file system` + failed outbound fetch (both expected sandbox limits) → blocked; `EXPECTED_LIMITATION` (line 198) doesn't cover read-only registry paths, `commander-register`, or sandbox network denial.

## FILES IT OWNS

- `src/pages/api/launch-codex.ts` — `blockedReasonFor`, `HARD_BLOCK`, `EXPECTED_LIMITATION` only
- `~/kernel/agents/executor.md` — add the reporting contract section (below)

## DO NOT TOUCH

- `applyCommit` / `applyRestarts` / notify wiring / job record shape
- The `## Blockers or open questions`-section pathway as the primary signal (keep it primary — sharpen it)

## IMPLEMENTATION SPEC

### 1. Scope HARD_BLOCK to where it means something
Split into two tiers:
```ts
// Deliberate sentinels an executor emits ON PURPOSE — match anywhere:
const SENTINEL_BLOCK = /MISSING_DEP|BRIEF_ERROR|NEEDS_CLARIFICATION/;
// Circumstantial phrases — match ONLY inside the "Blockers or open questions" section:
const HARD_BLOCK = /must .* authorize|authorize the required|outside .* FILES IT OWNS|not in FILES IT OWNS|command not found|no such file or directory|apply_patch rejected|writable roots are limited|outside (?:the )?(?:sandbox|writable)/i;
```
`blockedReasonFor`: sentinel match anywhere → blocked (unchanged intent). Circumstantial regex runs against `sectionBody(content, 'Blockers or open questions')` only. Quoted errors in "Commands run"/"Deviations" no longer classify.

### 2. Extend EXPECTED_LIMITATION (sandbox facts of life)
Add alternations for: `read-only file system` · `commander-register` · outbound network denial (`fetch failed|network .*(?:denied|unreachable|blocked)|outbound .*not (?:allowed|permitted)`) · `\.blocked` marker write failures. These lines get filtered out of the Blockers section before the substantive check, same as today's mechanism.

### 3. Fallback path
`classifyCompletion` falls back to `tailLines(log, 120)` when there's no last message — keep sentinel-only matching there (a raw log tail has no sections; circumstantial phrases in a log are even noisier).

### 4. `executor.md` reporting contract (the durable half)
Add a short section: *"Classification reads your report. If you completed the task: the `## Blockers or open questions` section must be exactly `None.` Quote errors freely in Commands run / Deviations — quoting is encouraged and does not block. If you are genuinely blocked: state it in the Blockers section, or emit `MISSING_DEP` / `BRIEF_ERROR` / `NEEDS_CLARIFICATION` on its own line anywhere. Expected sandbox limits (no network, read-only registries, no systemctl) are NOT blockers — list them as deviations and mark the task complete."*

### 5. Regression fixtures — the three real reports
The false-positive reports are on disk; they are the test:
- `~/.local/share/aperture/jobs/fa17a40b-*.json.last.md` (S-28) → expect `undefined`
- `~/.local/share/aperture/jobs/31da32e2-*.json.last.md` (AP-27) → expect `undefined`
- Synthetic true positive: a report whose Blockers section says "Cannot proceed: schema migration requires PO approval" → expect a defined reason
- Synthetic sentinel: `MISSING_DEP: node-fetch` anywhere → expect defined

## DONE LOOKS LIKE

1. Both real false-positive reports classify as `done` (blockedReasonFor → undefined).
2. Synthetic true-block and sentinel cases still classify blocked.
3. `npm run build` clean; aperture restarted + active.
4. `executor.md` contains the reporting contract.
5. Changes committed (including this file's status flip if applyCommit handles it — otherwise architect commits, noting the irony budget is spent).

## VERIFY WITH (paste raw output)

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
npx esbuild src/pages/api/launch-codex.ts --bundle --format=esm --platform=node --external:astro --outfile=/tmp/ap29-classify.mjs
node --input-type=module -e "
import { blockedReasonFor } from '/tmp/ap29-classify.mjs';
import { readFileSync } from 'node:fs';
const g = (p) => readFileSync(p, 'utf8');
console.log('S-28 report  →', blockedReasonFor(g(process.env.HOME + '/.local/share/aperture/jobs/fa17a40b-e6b8-4047-bcae-c77f6b825a2f.json.last.md')) ?? 'done ✓');
console.log('AP-27 report →', blockedReasonFor(g(process.env.HOME + '/.local/share/aperture/jobs/31da32e2-fd2a-4802-ae93-df486ff4f243.json.last.md')) ?? 'done ✓');
console.log('true block   →', blockedReasonFor('## Blockers or open questions\n\nCannot proceed: schema migration requires PO approval.') ? 'blocked ✓' : 'MISSED');
console.log('sentinel     →', blockedReasonFor('did stuff\nMISSING_DEP: node-fetch\n') ? 'blocked ✓' : 'MISSED');
"
grep -n "reporting contract\|Blockers or open questions" ~/kernel/agents/executor.md | head -3
systemctl --user restart aperture && systemctl --user is-active aperture
```

## OUT OF SCOPE

- The Stage-2 LLM verify agent (reserved as AP-28 per AP-27's brief — a judgment layer is the eventual real fix; this brief just stops the bleeding deterministically)
- applyCommit path-matching improvements (separate D-010 thread, AP-17 territory)
- Retroactively reclassifying old job records

## HANDOFF PROMPT

```
Read ~/kernel/agents/executor.md.
Then read ~/kernel/ecosystem-review/briefs/AP-29-blocked-classifier-recalibration.md and implement it.
Report back using ~/kernel/templates/implementation-report.md. Paste raw command output.
```
