# Kernel v2 — Candidate Operating Model

**Status:** candidate; v1 remains active until the pilot exit gate passes.
**Decision owner:** merulox.
**Execution substrate:** OMP.
**Control plane:** repository contracts during pilots; Aperture after adapter cutover.

Kernel v2 governs how work is shaped, executed, verified, and learned from. It does not implement another agent runtime.

## Core model

```text
human intent and risk policy
        ↓
durable work/control plane
        ↓
accountable lead selects a topology
        ↓
OMP execution in direct, fan-out, or mission mode
        ↓
deterministic gates + real-system evidence
        ↓
risk-triggered verification and approval
        ↓
failures become rules, skills, tests, or evals
```

## Start here

1. Read [CONSTITUTION.md](CONSTITUTION.md).
2. Select an execution topology with [MODES.md](MODES.md).
3. Classify risk and required gates with [RISK-GATES.md](RISK-GATES.md).
4. Create an intent contract from [templates/intent-contract.md](templates/intent-contract.md) when the persistence rule requires one.
5. Execute through the boundary defined in [CONTROL-PLANE.md](CONTROL-PLANE.md).
6. Close only with an evidence bundle based on [templates/evidence-bundle.md](templates/evidence-bundle.md).
7. Convert repeated failures using [LEARNING.md](LEARNING.md).

## Persistence rule

A permanent intent contract is required when work:

- crosses sessions;
- is delegated to a separate top-level agent or unattended runner;
- uses Fan-out or Mission mode;
- is Tier 1 or above and introduces observable behavior;
- requires a Product Owner approval;
- changes production, persistent data, schema, billing, credentials, or security posture;
- needs durable audit evidence.

Otherwise the accountable lead may hold the same fields in the active OMP todo and task contracts.

## Directory map

| File | Authority |
|---|---|
| [CONSTITUTION.md](CONSTITUTION.md) | Invariants, authority, planes, definition of closed |
| [MODES.md](MODES.md) | Direct, Fan-out, Mission, Routine selection and execution |
| [RISK-GATES.md](RISK-GATES.md) | Risk tiers, approvals, verification matrix, repair limits |
| [CONTRACTS.md](CONTRACTS.md) | Intent, worker, verifier, run, and evidence contracts |
| [CONTROL-PLANE.md](CONTROL-PLANE.md) | Aperture/OMP/systemd/Temporal responsibilities and lifecycle |
| [LEARNING.md](LEARNING.md) | Failure conversion, evals, metrics, calibration |
| [PILOTS.md](PILOTS.md) | v2 validation and v1 cutover gate |
| [templates/intent-contract.md](templates/intent-contract.md) | Copyable intent, evidence, and manifest templates in the same directory |

## Candidate boundary

Until [PILOTS.md](PILOTS.md) declares the exit gate passed:

- `agents/`, `workflows/`, and existing project task files remain the active v1 protocol;
- Aperture remains a viewer and Codex launcher;
- v2 may be used only for recorded pilots or explicit Product Owner decisions;
- no v1 file is archived or silently reinterpreted.

Research basis:

- [Frontier Agentic Orchestration](../docs/research/frontier-agentic-orchestration-2026-07-24.md)
- [Agentic QA Gauntlets](../docs/research/agentic-qa-gauntlets-2026-07-24.md)
