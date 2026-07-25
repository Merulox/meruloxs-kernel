# merulox's kernel

A provider-neutral operating model for building software with AI agents: human authority, adaptive execution topology, isolated work, executable outcome gates, and a learning loop that makes the next run more reliable.

## Kernel v2 candidate

[Kernel v2](v2/README.md) is now the candidate operating model.

It reorients the system around:

```text
Kernel   = governance, topology selection, oracles, learning
OMP      = local agent execution substrate
Aperture = durable control and approval plane after cutover
systemd  = predictable local automation
Temporal = optional durable execution when demonstrated necessary
```

The accountable lead selects the least complex topology that fits the work:

- **Direct** — one lead owns tightly coupled work end to end.
- **Fan-out** — isolated workers execute genuinely independent leaves.
- **Mission** — a planner preserves the milestone DAG while fresh workers implement leaves.
- **Routine** — deterministic code owns repeated state transitions; agents handle ambiguity.

Start with [`v2/README.md`](v2/README.md). Research basis:

- [`docs/research/frontier-agentic-orchestration-2026-07-24.md`](docs/research/frontier-agentic-orchestration-2026-07-24.md)
- [`docs/research/agentic-qa-gauntlets-2026-07-24.md`](docs/research/agentic-qa-gauntlets-2026-07-24.md)

## Cutover status

v2 is a candidate, not yet the active global protocol. v1 remains authoritative until the Direct, Fan-out, and Mission pilots in [`v2/PILOTS.md`](v2/PILOTS.md) pass and merulox explicitly approves activation.

During the pilot:

- `agents/`, `workflows/`, and `templates/` remain the v1 protocol;
- v2 contracts and evidence are used only for recorded pilots or explicit Product Owner decisions;
- Aperture remains a viewer and Codex launcher;
- no provider-specific runtime is removed.

## Kernel v1

The original system uses five fixed roles:

| Role | Who | Does |
|---|---|---|
| Product Owner | merulox | Direction, priorities, escalations |
| Architect | Claude | Briefs, verification, project memory |
| Executor | Codex | Implementation only |
| Reviewer | Claude in a separate session | Independent verification |
| Specialist | Any agent | Research, data, design |

Its lifecycle is `backlog → briefed → in_progress → review → done`. Its durable insight remains active: nothing is done until the stated verification commands pass and live state confirms the outcome.

The v1 implementation lives in:

```text
agents/         provider-specific role definitions
workflows/      session, handoff, and task lifecycle protocols
templates/      brief, report, review, decision, bug, and handoff forms
mvaos/          compact historical role documents
ecosystem-review/  forensic audits and executor brief history
```

v1 will move under `archive/v1/` only after the v2 cutover gate passes. No automatic commit or push is part of that migration.
