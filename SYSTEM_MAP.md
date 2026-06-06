# System Map — agent-infra + Ecosystem

**Date:** 2026-06-05  
**Maintainer:** Architect  
**Source of truth:** `ecosystem-review/` docs

---

## The eight-layer mental model

```
METHODOLOGY:  Agent Infra        — how we build (governs all projects)
PRODUCT:      SYNTRA             — what we sell (curated EDC)
PUBLIC FACE:  merulox.com        — what others see
─────────────────────────────────────────────────────────────────────
AGENT:        Genesis            — the autonomous actor (frozen/broken)
ENVIRONMENT:  Realm (state)      — where Genesis runs + doctrine
ENGINE:       brain-* scripts    — the code that drives Realm
INTERFACE:    Aperture           — the window onto Genesis/Realm
KNOWLEDGE:    Obsidian vault     — the long-term knowledge graph
```

---

## Agent Infra — roles and responsibilities

```mermaid
graph TD
    PO[Product Owner<br/>merulox<br/>Decisions · Priorities · Escalations]
    
    ARCH[Architect<br/>Claude Opus/Sonnet<br/>Briefs · Reviews · Memory]
    EXEC[Executor<br/>Codex<br/>Implementation]
    REV[Reviewer<br/>Claude Sonnet<br/>Verification · QA]
    SPEC[Specialist<br/>Any agent<br/>Research · Design · Data]
    
    PO -->|scope + priorities| ARCH
    ARCH -->|brief + handoff| EXEC
    EXEC -->|implementation report| ARCH
    ARCH -->|review request| REV
    REV -->|PASS / FAIL / ESCALATE| ARCH
    REV -->|design flaw| ARCH
    ARCH -->|escalation| PO
    ARCH -->|research brief| SPEC
    SPEC -->|findings| ARCH
```

### Role boundaries (what each role owns)

| Role | Owns | Cannot |
|------|------|--------|
| Product Owner | Direction, priorities, escalation decisions | Write code, write briefs |
| Architect | Briefs, project memory, verification, decisions | Write production code (>5 lines), approve own work |
| Executor | Implementation, implementation reports | Change scope, mark own work done |
| Reviewer | Verify commands, pass/fail verdict | Rewrite implementation, lower acceptance criteria |
| Specialist | Domain-specific research/output | Architecture decisions |

---

## Task lifecycle

```mermaid
stateDiagram-v2
    [*] --> backlog: identified
    backlog --> briefed: architect writes brief
    briefed --> in_progress: executor starts
    in_progress --> review: executor reports done
    in_progress --> blocked: dependency missing
    review --> done: reviewer PASS + architect accepts
    review --> in_progress: reviewer FAIL → fix brief
    review --> backlog: reviewer ESCALATE → re-brief
    blocked --> in_progress: blocker resolved
    done --> [*]
    backlog --> cancelled: PO/architect drops
    in_progress --> cancelled: PO/architect drops
```

**Rule:** Nothing goes from backlog directly to an executor. Brief first.  
**Rule:** Done = verification commands ran + reviewer confirmed (for [DATA] tasks) + architect accepted + files updated.

---

## Persistence layers

| Layer | Location | What it stores | Owner | Consumed by |
|-------|----------|---------------|-------|-------------|
| Project memory | `<project>/.agent/` | CONTEXT, TASKS, DECISIONS, RISKS | Architect | Architect on re-entry |
| Task briefs | `<project>/docs/planning/` | Exact implementation specs | Architect | Executor, Reviewer |
| Agent comms log | `<project>/.agent/logs/agent-comms.md` | Architect↔executor↔reviewer messages | All agents | Architect, PO |
| Session log | `<project>/.agent/logs/session-log.md` | Session summaries | Architect | Architect, PO |
| Obsidian vault | `~/obsidian/` | Long-term knowledge, claims, domains | brain-ingest, human | Claude sessions (injected) |
| Realm commons | `~/projects/realm/commons/` | Operational state (mostly frozen) | brain-* scripts | Aperture (stale) |
| Realm monitor | `~/projects/realm/monitor/` | Live service health + Genesis bug ledger | monitor scripts | **Nothing — gap** |
| Claude memory | `~/.claude/projects/*/memory/` | Session continuity, signals, rules | Director sessions | Claude on re-entry |
| brain-* state | `~/obsidian/claude-bus/` | Inter-instance task queue | brain-bus-router | brain-task-executor |

---

## Communication paths

```mermaid
graph LR
    ARCH[Architect] -->|writes brief to| BRIEF[docs/planning/*.md]
    BRIEF -->|read by| EXEC[Executor]
    EXEC -->|writes impl report| REPORT[direct message / comms log]
    REPORT -->|read by| ARCH
    ARCH -->|writes review request| REV[Reviewer]
    REV -->|writes review report| ARCH
    
    ARCH -->|updates| CTX[.agent/CONTEXT.md]
    ARCH -->|updates| TASKS[.agent/TASKS.md]
    ARCH -->|appends| DECISIONS[.agent/DECISIONS.md]
    
    CTX -->|re-entry context| ARCH
    TASKS -->|re-entry context| ARCH
```

**Inter-instance coordination (brain-bus):**
```
brain-bus-router (live) ──> routes tasks via ~/obsidian/claude-bus/tasks/
brain-task-executor (live) ──> claims + executes queued shell tasks
Instance X ──> brain-task claim --role any
```

---

## Recovery mechanisms

| Mechanism | How | When to use |
|-----------|-----|-------------|
| Project re-entry | Read `.agent/CONTEXT.md` + `TASKS.md` | Start of any architect session |
| Role restoration | Read `~/agent-infra/agents/architect.md` | Lost role clarity |
| MVAOS compact recovery | Read `~/agent-infra/mvaos/ARCHITECT.md` + `SESSION_RECOVERY.md` | Quick context restore |
| Global CLAUDE.md | `~/.claude/CLAUDE.md` | System-wide preferences + environment facts |
| Agent-infra CLAUDE.md | `~/agent-infra/CLAUDE.md` | Repo-specific role + active work state |
| brain-status | `brain-status` | See all active Claude instances |
| session-log | `<project>/.agent/logs/session-log.md` | Audit trail of past sessions |

**Minimum recovery prompt (paste to any new Claude session):**
```
Read ~/agent-infra/agents/architect.md.
Read ~/syntra/.agent/CONTEXT.md.
Read ~/syntra/.agent/TASKS.md.
Identify any in_progress tasks. Verify live state before assuming done.
Resume as architect.
```

---

## Ecosystem: data flow (actual, 2026-06-05)

```mermaid
graph TD
    subgraph Live
        BBR[brain-bus-router] --> BUS[claude-bus/tasks/]
        BTE[brain-task-executor] --> BUS
        MON[realm/monitor scripts] --> JSONL[monitor/*.jsonl]
        MANIFEST[MANIFEST.md auto-gen] --> CLAUDE_CTX[injected into every Claude prompt]
    end
    
    subgraph Gap
        JSONL -.->|should read| APT[Aperture dashboard]
        APT -->|reads instead| STALE[commons/vitals.json STALE]
    end
    
    subgraph Frozen
        GEN[Genesis daemon] -.->|self-killed Apr 28| DEAD[stopped]
        REALM[Realm 80%] --> ARCHIVE[frozen since Apr]
    end
    
    subgraph Active
        SYNTRA[SYNTRA engine] --> NOCODB[NocoDB 107+ products]
        SYNTRA --> UI[discovery UI]
    end
```

---

## Project adoption status

| Project | .agent/ | CONTEXT.md | TASKS.md | DECISIONS.md | Briefs | CLAUDE.md |
|---------|:-------:|:----------:|:--------:|:------------:|:------:|:---------:|
| SYNTRA | ✅ | ✅ current | ✅ current | ✅ | ✅ B1 | ❌ |
| agent-infra | ❌ | ❌ | ❌ | ❌ | — | ❌ → creating |
| Genesis | ❌ | ❌ | ❌ | ❌ | — | ❌ |
| Aperture | ❌ | ❌ | ❌ | ❌ | — | ❌ |

**Next adoption target:** agent-infra itself (this session).

---

## Open executor briefs (EX-1..EX-6)

All approved 2026-06-05. None executed yet.

| Brief | Action | Gate | Risk |
|-------|--------|------|------|
| EX-1 | Back up `~/scripts/` to git | Do first | Secret-scan before push |
| EX-2 | Push agent-infra (public), aperture, genesis repos | After EX-1 | Genesis memory must NOT be committed |
| EX-3 | Wire Aperture → live monitor feed | Any time | Read-only |
| EX-4 | Archive Realm frozen 80% | Any time | Move never delete |
| EX-5 | Genesis safety gates | **Before any genesis-core start** | Safety-critical |
| EX-6 | Index brain-* engine | Last | Classify only |

Full briefs at: `~/agent-infra/ecosystem-review/briefs/`
