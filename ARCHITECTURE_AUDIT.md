# Architecture Audit — agent-infra

**Date:** 2026-06-05  
**Auditor:** Architect (instance X)  
**Scope:** agent-infra repo + full ecosystem context from ecosystem-review/

---

## Current State

### What actually exists

**Agent Infra (this repo)** — a methodology and document kit, not a runtime.

| Component | Path | State |
|-----------|------|-------|
| Role definitions (full) | `agents/architect.md`, `executor.md`, `reviewer.md` | Complete, in use |
| Role definitions (MVAOS) | `mvaos/ARCHITECT.md`, `EXECUTOR.md`, `REVIEWER.md` | Complete — parallel system |
| Workflow protocols | `workflows/` (6 files) | Complete |
| Templates | `templates/` (6 files) | Complete |
| Ecosystem review | `ecosystem-review/` (9 docs + 6 briefs) | Complete — 2026-06-05 forensic audit |
| Project templates | `project/` (7 files) | Templates only — never instantiated for this repo |
| MVAOS project state | `mvaos/PROJECT.md`, `SESSION_RECOVERY.md`, `TASKS.md` | Templates only — never filled |
| Session log | `logs/session-log.md` | 1 entry (2026-06-05 setup session) |
| CLAUDE.md | — | **Does not exist** ← root cause of slow re-entry |

**SYNTRA** — the primary active project using agent-infra.

| Component | Path | State |
|-----------|------|-------|
| Agent context | `~/syntra/.agent/CONTEXT.md` | Current — last updated 2026-06-05 |
| Task board | `~/syntra/.agent/TASKS.md` | Current — B1 briefed, B2 backlog |
| Briefs | `~/syntra/docs/planning/` | B1 exists, B2 not written |
| B1 probe script | `~/syntra/src/cli/probe-bellroy.js` | **Done but unrecorded** |
| B2 ingest script | `~/syntra/src/cli/ingest-bellroy.js` | Exists (executor produced it) — B2 brief not yet written |

**Ecosystem (from forensic review 2026-06-05):**

| System | Runtime state | Agent-infra adoption |
|--------|--------------|---------------------|
| SYNTRA | Engine live, UI stopped | Full — `.agent/`, briefs, CONTEXT, TASKS |
| Genesis | Frozen (self-killed Apr 28) | None |
| Realm | 80% frozen; monitor + bus live | None |
| Aperture | MVP live; reads stale data | None |
| merulox.com | Live | None |

---

## Intended State

From the README, role docs, and ecosystem-review synthesis:

1. **Every project** has a `.agent/` dir with `PROJECT.md`, `CONTEXT.md`, `TASKS.md`, `DECISIONS.md`, `RISKS.md`, `logs/`.
2. **Every architect session** enters role in <30 seconds by reading a project CLAUDE.md → architect.md → CONTEXT.md → TASKS.md.
3. **Tasks flow:** backlog → briefed (architect) → in_progress (executor) → review (reviewer) → done (architect verifies).
4. **Session continuity:** CONTEXT.md is the recovery artifact. Architect never leaves a session without updating it.
5. **agent-infra itself** is governed by the same protocol it defines — it has a `.agent/` dir, a CLAUDE.md, and sessions log to `logs/session-log.md`.
6. **EX-1..EX-6** executor briefs (written and approved 2026-06-05) are executed in dependency order.

---

## Drift Analysis

| # | Drift | Severity | Fix |
|---|-------|----------|-----|
| D-1 | **No CLAUDE.md** — architect cold-start costs 5+ minutes instead of 30 seconds | **Critical** | Create CLAUDE.md (this session) |
| D-2 | **Two parallel role systems** — `agents/` (full) and `mvaos/` (compact) with overlapping content | Medium | Consolidate: mvaos/ is the canonical compact version; agents/ is the extended reference |
| D-3 | **SYNTRA B1 done, not recorded** — `probe-bellroy.js` runs, TASKS.md still says `briefed` | High | Update SYNTRA TASKS.md + CONTEXT.md |
| D-4 | **SYNTRA B2 ingest script exists** — executor wrote `ingest-bellroy.js` without a brief | Medium | Architect reviews script, validates, writes acceptance criteria retroactively |
| D-5 | **EX-1..EX-6 briefs written, none executed** — engine unversioned, Aperture unconnected | High | Assign to executor in dependency order; EX-1 is loss-prevention |
| D-6 | **mvaos/ and project/ templates unfilled** for agent-infra itself | Low | Fill in mvaos/PROJECT.md and SESSION_RECOVERY.md this session |
| D-7 | **Session shutdown missed** — the frozen 35h session exited without updating CONTEXT.md | Medium | CLAUDE.md must make shutdown protocol impossible to miss |
| D-8 | **`~/scripts/` unversioned** — the brain-* engine has no git backup; backup services stopped | **Critical** | EX-1 (highest priority executor task) |

---

## Risks

### R-1: Context loss loop (observed this session)
**What:** No CLAUDE.md → architect spends 5+ minutes rediscovering role and system state instead of working.  
**Observed:** Instance X took 3+ exchanges to establish architect context.  
**Mitigation:** Create CLAUDE.md with immediate role entry + recovery prompt.

### R-2: Frozen-architect pattern
**What:** Long-running Claude session (PID 602273, 35+ hours) holding a role without producing output. Invisible to outside observer.  
**Observed:** Today. The session had finished its work but never exited cleanly.  
**Mitigation:** Session shutdown protocol (already in `workflows/session-shutdown.md`) must be surfaced in CLAUDE.md so it's harder to skip.

### R-3: Engine loss (highest severity)
**What:** `~/scripts/` (the brain-*, backup, command-center, and 100+ other scripts) is unversioned. Backup services stopped. A drive failure loses the entire running engine.  
**Mitigation:** EX-1 — `git init ~/scripts` + private push. Do first.

### R-4: Genesis safety gap
**What:** genesis-core has no bash_exec guard and no kill-switch. It already self-destructed Apr 28. Revival before EX-5 (safety gates) creates the same risk.  
**Mitigation:** EX-5 must complete before genesis-core is started.

### R-5: Silent scope expansion
**What:** Executor wrote `ingest-bellroy.js` (B2 scope) without a brief being written. Work happened outside the task lifecycle.  
**Mitigation:** Architect must validate and retroactively accept or reject. Going forward, executor briefing is enforced by CLAUDE.md instructions.

### R-6: Aperture reads stale data
**What:** aperture.merulox.com is live but reads `commons/vitals.json` (last updated April). The live monitor feed (`realm/monitor/*.jsonl`) is not consumed anywhere.  
**Mitigation:** EX-3.

---

## Recommendations (ordered by ROI)

| Priority | Action | Rationale |
|----------|--------|-----------|
| 1 | **Create CLAUDE.md for agent-infra** | Eliminates D-1; every future session enters role in <30s |
| 2 | **Update SYNTRA state (B1 done, B2 assessment)** | D-3/D-4; clears the task board to ground truth |
| 3 | **EX-1: back up ~/scripts/** | R-3; catastrophic loss prevention; architect approves then hands to executor |
| 4 | **EX-2: push repos** | After EX-1; agent-infra public push is safe (no secrets) |
| 5 | **EX-5: Genesis safety gates** | R-4; prerequisite for any Genesis revival |
| 6 | **EX-3: wire Aperture → live monitor** | Converts the crown jewel into a useful daily dashboard |
| 7 | **EX-4: archive Realm frozen 80%** | Makes live ≠ dead obvious; reduces confusion |
| 8 | **EX-6: index brain-* engine** | Low urgency; useful once engine is backed up |
| 9 | **Consolidate mvaos/ + agents/** | D-2; minor cleanup; mvaos/ wins as the canonical compact form |
