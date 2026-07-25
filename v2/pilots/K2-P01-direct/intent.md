# Intent Contract: K2-P01 — Bootstrap Kernel v2

```yaml
schema_version: 2
work_id: K2-P01
status: verified
accountable_lead: omp-kernel-v2
mode: direct
risk_tier: 0
repository: ~/kernel
workspace: ~/kernel
depends_on: []
requires: []
allowed_paths:
  - ~/kernel/v2/**
  - ~/kernel/README.md
  - ~/kernel/CLAUDE.md
  - ~/kernel/AGENTS.md
protected_paths:
  - ~/kernel/agents/**
  - ~/kernel/workflows/**
  - ~/kernel/templates/**
  - ~/projects/aperture/**
max_local_repairs: 2
max_expensive_repairs: 0
evidence_path: ~/kernel/v2/pilots/K2-P01-direct/evidence.md
```

## Outcome

Kernel contains a provider-neutral v2 candidate that defines adaptive execution modes, risk-tiered verification, stable contracts, system boundaries, and a gated pilot/cutover path without changing the active v1 protocol or Aperture runtime.

## Why now

OMP and current frontier models natively provide isolation, typed subagents, peer messaging, worktrees, code intelligence, and verification tools that Kernel v1 manually assigns to provider-specific roles. The methodology must preserve governance and evidence while delegating execution mechanics to OMP.

## Preconditions

- Frontier orchestration and QA research exists under `docs/research/`.
- No other session owns `~/kernel/v2`.
- merulox approved starting the rewrite.

## Interfaces and ownership

| Interface/path | Owner | Allowed change |
|---|---|---|
| `v2/**` | accountable lead | Create candidate methodology and pilot artifacts |
| `README.md` | accountable lead | Route readers to v2 while preserving v1 status |
| `CLAUDE.md` | accountable lead | Surface candidate boundary; keep v1 authoritative |
| `AGENTS.md` | accountable lead | Surface candidate boundary; keep v1 authoritative |

## Acceptance scenarios

### Scenario 1 — New work can select a topology

- **Given:** a task's coupling, parallelism, duration, and repeatability are known
- **When:** the lead follows `v2/MODES.md`
- **Then:** it can select Direct, Fan-out, Mission, or Routine using explicit criteria and mode-change rules
- **Evidence:** required mode headings and selection algorithm exist

### Scenario 2 — Consequential work cannot bypass gates

- **Given:** a task changes product behavior, data, schema, deployment, money, privacy, credentials, or security
- **When:** risk is classified through `v2/RISK-GATES.md`
- **Then:** the required contract, independent oracle, approval, containment, and review posture is explicit
- **Evidence:** Tier 0–3 definitions and gate matrix exist

### Scenario 3 — Completion is evidence-based

- **Given:** execution finishes
- **When:** the lead evaluates closure
- **Then:** it must produce an evidence bundle mapping acceptance claims to observed outcomes; run success alone cannot close work
- **Evidence:** contract and evidence templates plus definition of closed exist

### Scenario 4 — v1 and Aperture are not silently cut over

- **Given:** v2 has not completed all three coding-mode pilots
- **When:** an agent enters the repository
- **Then:** root instructions identify v2 as a candidate and keep v1 authoritative; Aperture remains unchanged
- **Evidence:** `README.md`, `CLAUDE.md`, `AGENTS.md`, and `v2/PILOTS.md`

## Invariants

- Kernel remains methodology-only.
- Product Owner authority is preserved.
- Exactly one accountable lead owns a work item.
- Parallel workers require genuine independent leaves.
- v1 is not archived or reinterpreted during the candidate phase.
- Aperture is not modified by this pilot.

## Forbidden side effects

- No production code, service, taskboard runtime, systemd, or NixOS changes.
- No modification of existing v1 role, workflow, or template bodies.
- No commit or push.

## Verification plan

| Gate | Observer | Expected | Blocking |
|---|---|---|:---:|
| structure | Enumerate `v2/` expected files | Every candidate document and template exists | yes |
| links | Resolve local Markdown links | Zero missing local targets | yes |
| modes | Inspect required headings | Direct, Fan-out, Mission, Routine all present | yes |
| risk | Inspect required headings and matrix | Tier 0–3 and gate matrix present | yes |
| yaml | Parse fenced template YAML and manifest | Valid YAML mappings | yes |
| routing | Inspect root entrypoints | Candidate visible; v1 authority and cutover gate explicit | yes |
| boundary | Inspect pilot contract | Aperture path protected and cutover deferred | yes |

Manifest: not available for methodology-only Markdown; bootstrap verification is encoded above and executed with a read-only validation cell.

## Real-system exercise

Run the repository and vault retrieval hooks with a Kernel v2 orchestration prompt. The expected result is that canonical research and the `v2` project path are discoverable without activating v2 globally.

## Rollback and containment

- Rollback: remove `v2/` and revert the three root routing additions.
- Stop condition: any validation failure, v1 instruction ambiguity, or unintended Aperture modification.
- Post-action health check: active v1 instructions remain explicit in all root entrypoints.

## Non-goals

- Implement the Aperture OMP adapter.
- Archive v1.
- Pretend Fan-out or Mission mode has been validated.
- Add Temporal or another runtime.

## Clarifications and approved changes

- 2026-07-24: This is a bootstrap pilot. User-approved intent existed in the preceding orchestration design and research; the on-disk contract was materialized before final verification, after candidate documents were created.
