# Intent Contract: K2-P02 — Genesis cancellation and human takeover

```yaml
schema_version: 2
work_id: "K2-P02"
status: verified
accountable_lead: "omp-agent-substrate-p02"
mode: fan-out
risk_tier: 2
repository: "/home/merulox/projects/genesis"
workspace: "disposable isolated worktree"
depends_on:
  - "/home/merulox/projects/realm/operations/governed-agent-substrate.md"
  - "/home/merulox/projects/genesis/docs/capability-v2-contract.md"
  - "/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/public-spec.md"
requires:
  - po_scope
  - data
  - schema
  - security
  - independent_oracle
allowed_paths:
  - "/home/merulox/projects/genesis/runtime_v2/capabilities.py"
  - "/home/merulox/projects/genesis/tests/test_capability_v2.py"
  - "/home/merulox/projects/genesis/docs/capability-v2-contract.md"
  - "/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/intent.md"
  - "/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/public-spec.md"
  - "/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/evidence.md"
protected_paths:
  - "/home/merulox/projects/genesis/runtime_v2/cli.py"
  - "/home/merulox/projects/genesis/runtime_v2/worker.py"
  - "/home/merulox/projects/genesis/runtime_v2/model.py"
  - "/home/merulox/projects/genesis/runtime_v2/memory.py"
  - "/home/merulox/projects/genesis/state"
  - "/home/merulox/projects/genesis/memory"
  - "/home/merulox/.config/systemd/user"
  - "/home/merulox/projects/aperture"
  - "/home/merulox/.secrets"
oracle:
  mode: public_spec_hidden_checks
  visibility: protected
  owner: "independent-verifier"
  executor_disclosure: public_spec_only
isolation:
  workspace_disposition: disposable
  mount_allowlist:
    - "/workspace:rw"
    - "/public-spec.md:ro (exact frozen public specification only)"
    - "/nix/store:ro"
    - "/run/current-system/sw:ro"
  oracle_excluded_from_executor_namespace: true
  kernel_excluded_from_executor_namespace: true  # except exact /public-spec.md mount
  unrelated_home_excluded_from_executor_namespace: true
  credential_refs: []
  egress_policy: none
repair_limit: 2
rollback:
  method: "discard candidate worktree before integration; after integration, revert only declared source changes; capability schema v2 databases are isolated/disposable and are never migrated silently"
  stop_condition: "oracle escalation, protected-path change, production path access, gate weakening, or second failed repair"
real_system_exercise:
  interface: "CapabilityBroker public Python surface"
  environment: "disposable SQLite database and 0700 workspace only"
  expected_result: "all P02-I1..P02-I10 evidence recorded without external or production effects"
evidence_path: "/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/evidence.md"
```

## Outcome

A real stateful adapter demonstrates proposal, exact approval, lease failure/recovery/retry, verified execution, cancellation, human takeover, release, review, and rollback while preserving the broker's existing security properties.

## Why Fan-out

Two leaves are genuinely independent after this public specification is frozen:

1. an implementation worker changes only the three Genesis source/contract/test files;
2. an independent verifier derives protected acceptance checks from the public specification without seeing candidate implementation.

The accountable lead owns isolation, integration, public gates, real-system exercise, evidence, and final Product Owner review. Neither leaf may weaken the public contract or edit the other's artifacts.

## Approval boundary

The Product Owner selected the Genesis capability broker as the preferred next pilot. That selection chooses direction but does not by itself approve the exact Tier 2 side effects below.

Execution requires durable Product Owner approval for:

- adding `cancelled` request and attempt states;
- adding persistent takeover/release records in capability schema version 3;
- making version-2 capability databases fail initialization with an explicit reset-required error instead of silently migrating;
- modifying authority/security behavior for proposal, approval, claim, execution, cancellation, takeover, and release;
- running the implementation and protected oracle only in disposable isolated storage;
- no deployment, service restart, production database mutation, external communication, credential access, model authority, or Kernel v2 cutover.

## Non-goals

- No production or legacy Genesis state.
- No edits to the CLI currently owned by the Genesis memory-v2 session.
- No generic scheduler, workflow engine, agent runtime, MCP server, A2A layer, or Aperture integration.
- No interpretation of reject or rollback as cancellation or takeover.
- No automatic rollback during takeover.
- No deployment or activation of Kernel v2.

## Clarifications and approved changes

Append timestamped approvals or contract changes here. Any scope, risk, side-effect, public invariant, or protected-oracle change requires a new decision and stops active workers.

- 2026-08-04T19:26:56-04:00 — merulox approved the exact isolated Tier 2 P02 scope and its `po_scope`, `data`, `schema`, `security`, and `independent_oracle` flags: capability schema v3, explicit cancellation/takeover/release semantics, disposable database/workspace writes, and protected-oracle execution. This approval explicitly excludes production state, deployment, services, network, credentials, CLI changes, external communication, model authority, and Kernel v2 cutover.
- 2026-08-04T20:18:37-04:00 — Pilot verification closed: public and full suites passed, protected oracle passed the candidate and killed a deliberate authority mutant, independent review closed all findings, real lifecycle smoke passed, and the exact verified files were integrated without deployment or Kernel v2 cutover.
