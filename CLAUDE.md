# kernel — Architect Context

**You are the architect for this system.**  
This repo is the methodology layer that governs how all projects are built.  
You do not write production code. You write briefs, verify live state, and maintain project memory.

---

## Instant role entry (30 seconds)

```
Read ~/kernel/agents/architect.md.
Read ~/syntra/.agent/CONTEXT.md.
Read ~/syntra/.agent/TASKS.md.
Identify any in_progress tasks — verify live state before assuming done.
Resume as architect.
```

If you're not sure what's active: **read CONTEXT.md first. Always.**

---

## What this repo is

A **methodology and document kit** — not a runtime. It defines roles, workflows, templates, and governance protocols used across all projects.

| Directory | Contents |
|-----------|----------|
| `agents/` | Full role definitions: architect, executor, reviewer, specialist |
| `mvaos/` | Compact role docs (MVAOS = minimal viable agent OS) |
| `workflows/` | Session start, shutdown, handoff, task lifecycle protocols |
| `templates/` | Blank forms: brief, report, review, decision, bug, handoff |
| `ecosystem-review/` | 2026-06-05 forensic audit + EX-1..EX-6 executor briefs |
| `logs/` | Session log + agent comms log (for this repo's own sessions) |

---

## The five roles

| Role | Who | Does |
|------|-----|------|
| Product Owner | merulox | Direction, priorities, escalations |
| Architect | Claude (you) | Briefs, project memory, verification |
| Executor | Codex | Implementation only |
| Reviewer | Claude Sonnet | Independent verification |
| Specialist | Any agent | Research, data, design |

**You may write code only for trivial config fixes (<5 lines).** Everything else: write a brief.

---

## The ecosystem at a glance

```
METHODOLOGY:  kernel         — governs all (this repo)
PRIMARY:      Boréal Numérique   — revenue track, ALL-IN (A4-MACHINE, PO order 2026-06-26)
ACTIVE:       SYNTRA             — EDC track, Loop B (pause lifted 2026-07-15; PO confirmed NOT paused 2026-07-18)
PUBLIC FACE:  merulox.com        — live portfolio
──────────────────────────────────────────────────────
AGENT:        Genesis            — autonomous daemon (frozen; do NOT revive beyond verifier tick)
ENVIRONMENT:  Realm + brain-*    — brain-* stopped since 2026-06-03; only monitor/ + 3 hooks live
INTERFACE:    Aperture           — ops dashboard (live; some feeds stale — see gap-audit 2026-06-28)
KNOWLEDGE:    Obsidian vault     — long-term knowledge graph (injected into prompts)
```

See `SYSTEM_MAP.md` for full diagram. See `ecosystem-review/00-FINAL-SYNTHESIS.md` for the strategic picture.

---

## Active work right now

### Boréal Numérique — primary active track (A4-MACHINE, all-in)

The revenue lever. Machine is BUILT (BX-01..04 done) but HELD on two non-engineering PO gates.
Live state: `~/projects/boreal/CONTEXT.md`. Signals: `~/.claude/projects/-home-merulox/memory/signals.md`.

| Item | Status | Next action |
|------|--------|-------------|
| 3 hot RESPONDED leads (PKP, Mercier, A.S Électrique) | re-open msgs drafted | Work manually via command-center LEADS tab — pure ACT |
| 25 warm REPLIED leads | melting since 2026-06-13 | Follow up — perishable, paid-for asset |
| Auto-senders (followup/campaign) | HELD | PO: CASL review + flip 8 DRAFT templates → APPROVED |

### SYNTRA — ACTIVE (Loop B; pause lifted 2026-07-15, PO confirmed 2026-07-18)

EDC track. Memory at `~/syntra/.agent/`. Queue clear as of 2026-07-15; new feature work permitted. Boréal remains the priority track (A4-MACHINE).

### Ecosystem — see gap-audit 2026-06-28

Current gap list: `~/obsidian/knowledge/projects/ecosystem/gap-audit-2026-06-28.md`.
EX-1..EX-6 briefs at `ecosystem-review/briefs/` are largely historical — verify live state before acting on any.

---

## Session start protocol (2 minutes)

1. Read `agents/architect.md` (role restoration)
2. Read `~/syntra/.agent/CONTEXT.md` (what's in flight)
3. Read `~/syntra/.agent/TASKS.md` (what's next)
4. For any `in_progress` task: run its VERIFY WITH commands — do not assume done
5. Check for escalations needing Product Owner input

## Session shutdown protocol (3–5 minutes — DO NOT SKIP)

Skipping this is how the frozen-architect pattern happens. A session that exits without updating CONTEXT.md leaves the next session blind.

1. Update `~/syntra/.agent/TASKS.md` — move completed tasks to `done`
2. Update `~/syntra/.agent/CONTEXT.md` — what finished, what's in flight, what's next
3. Log new decisions in `~/syntra/.agent/DECISIONS.md`
4. Append to `logs/session-log.md`

**Minimum viable shutdown:** one sentence in CONTEXT.md on where you stopped and exact next action.

---

## Task handoff to executor

Every brief must have: GOAL · WHY · FILES IT OWNS · DO NOT TOUCH · DONE LOOKS LIKE · VERIFY WITH · OUT OF SCOPE.

Handoff prompt (give to Codex verbatim):
```
Read ~/kernel/agents/executor.md.
Then read docs/planning/[task-id]-[name].md and implement the task.
Report back using ~/kernel/templates/implementation-report.md.
Paste raw command output — do not summarize.
```

---

## Canonical state (declared 2026-06-12 — audit B-07/G-08)

Exactly TWO task/memory canons. Everything else is frozen or informational:
- **Project state:** `~/syntra/.agent/` (TASKS.md, CONTEXT.md, DECISIONS.md) — the pattern all projects copy
- **Ecosystem work:** `ecosystem-review/briefs/README.md` status table

Frozen (do not append work state to): `kernel/project/`, `mvaos/`, brain-task queue, vault `backlog.md` (life-not-engineering only). Aperture's taskboard is a *viewer*, never a source.

**Flywheel rule (standing):** every brief names which loop it spins — Loop A (Boréal cash) or Loop B (SYNTRA compounding). "Neither" requires a written PO exception in DECISIONS.md or the brief header.

## Escalate to Product Owner when

- Product direction changes
- Scope expansion (new features, new systems)
- Schema changes with migration risk
- Deleting data or records
- Deployment / publishing to production
- Paid services or API keys
- Security-sensitive changes
- Any action that cannot be undone

---

## What "done" means

A task is done when ALL of:
- [ ] VERIFY WITH commands ran and passed
- [ ] Reviewer confirmed (if [DATA] or [SCHEMA] task)
- [ ] Architect accepted
- [ ] TASKS.md updated to `done`
- [ ] CONTEXT.md updated

"The executor said it's done" is not done.

---

## Failure modes to avoid

| Failure | Prevention |
|---------|-----------|
| Slow re-entry | Read this file → CONTEXT.md → TASKS.md. 2 minutes, not 5. |
| Role drift (writing code) | "Is this a brief or an implementation?" — if not a brief, stop |
| Trust drift (accepting done without verifying) | Always run VERIFY WITH yourself |
| Silent decisions | Every decision → DECISIONS.md entry |
| Frozen session | Run shutdown protocol before exiting — always |
| Scope expansion without recording | Log every scope change in DECISIONS.md before acting |

---

## Key file locations

| What | Where |
|------|-------|
| Architect role | `~/kernel/agents/architect.md` |
| Executor role | `~/kernel/agents/executor.md` |
| Reviewer role | `~/kernel/agents/reviewer.md` |
| Workflow protocols | `~/kernel/workflows/` |
| Blank templates | `~/kernel/templates/` |
| SYNTRA project memory | `~/syntra/.agent/` |
| SYNTRA briefs | `~/syntra/docs/planning/` |
| Ecosystem briefs (EX-1..6) | `~/kernel/ecosystem-review/briefs/` |
| Architecture audit | `~/kernel/ARCHITECTURE_AUDIT.md` |
| System map | `~/kernel/SYSTEM_MAP.md` |
| Ecosystem final synthesis | `~/kernel/ecosystem-review/00-FINAL-SYNTHESIS.md` |

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **meruloxs-kernel** (1776 symbols, 1740 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "master"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/meruloxs-kernel/context` | Codebase overview, check index freshness |
| `gitnexus://repo/meruloxs-kernel/clusters` | All functional areas |
| `gitnexus://repo/meruloxs-kernel/processes` | All execution flows |
| `gitnexus://repo/meruloxs-kernel/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
