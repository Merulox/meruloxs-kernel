# Intent Contract: [WORK-ID] — [Title]

```yaml
schema_version: 2
work_id: "[WORK-ID]"
status: proposed
accountable_lead: "[session or person]"
mode: direct # direct | fan-out | mission | routine
risk_tier: 0 # 0 | 1 | 2 | 3
repository: "[absolute or canonical repo path]"
workspace: "[primary workspace or control-plane reference]"
depends_on: []
requires: [] # po_scope | data | schema | deploy | money | security | independent_oracle
allowed_paths: []
protected_paths: [] # executor-visible write protection only; never list protected-oracle storage
oracle:
  mode: none # none | independent
  visibility: not_applicable # not_applicable | public_spec_hidden_checks
  owner: null # independent verifier identity when mode is independent
  executor_disclosure: public_spec_only
isolation:
  workspace_disposition: primary # primary | isolated | disposable
  mount_allowlist: [] # complete executor-visible mounts; verifier storage must never appear
  oracle_excluded_from_executor_namespace: false
  runtime_identity: null # pinned image digest/profile or equivalent
  credential_refs: [] # names/indirections only; never values
  egress_policy: null # policy identity or explicit reviewed exception
  host_evidence_path: "[host-owned evidence path]"
max_local_repairs: 3
max_expensive_repairs: 2
evidence_path: "[path written on completion]"
```

When `requires` includes `independent_oracle`, set `oracle.mode` to `independent`, `oracle.visibility` to `public_spec_hidden_checks`, name the independent verifier owner, and require a disposable workspace, explicit mount allowlist, true oracle exclusion, pinned runtime identity, credential indirection, explicit egress policy, and host-owned evidence. Do not put oracle source, path, content, private fixtures, or verifier-only gate entries anywhere in the executor-visible contract.

## Outcome

One sentence describing the observable world-state change.

## Why now

What this enables, what depends on it, and why it has priority.

## Preconditions

- [Required state, dependency, input, or approval]

## Interfaces and ownership

| Interface/path | Owner | Allowed change |
|---|---|---|
| [path/symbol/API] | [lead/worker/verifier] | [bounded change] |

Nothing outside this table may change without returning the contract to `proposed` or `needs_input`.

## Public specification

- Visibility: [public / public_spec_hidden_checks]
- Public interface and inputs:
- Public outputs and state transitions:
- Boundary and error semantics:

The acceptance scenarios, invariants, forbidden outcomes, and evidence expectations below are the complete behavioral specification. Hidden executable checks may test only this public contract; they must not introduce private requirements.

## Acceptance scenarios

### Scenario 1 — [Happy path]

- **Given:** [initial observable state]
- **When:** [real user/caller action]
- **Then:** [observable result]
- **Evidence:** [command, state query, screenshot, trace, or metric]

### Scenario 2 — [Negative/boundary case]

- **Given:**
- **When:**
- **Then:**
- **Evidence:**

## Invariants

- [Property that must remain true]

## Forbidden outcomes and side effects

- [Publicly forbidden result, state, system, file, API, or behavior]

## Evidence expectations

| Public claim/invariant | Required observer or action | Required artifact |
|---|---|---|
| [stable public ID] | [command, journey, state query, trace, or metric] | [host-owned path/URI] |

## Verification plan

| Gate | Command/observer | Expected result | Blocking |
|---|---|---|:---:|
| [gate-id] | [exact action] | [observable result] | yes |

Manifest: [project verification manifest path or “not available” with reason]

## Real-system exercise

Describe the actual interface that must be exercised. Unit tests alone are not sufficient when a real interface exists.

## Rollback and containment

- Rollback method:
- Stop condition:
- Post-action health check:

## Non-goals

- [Explicitly deferred behavior]

## Clarifications and approved changes

Append timestamped clarifications here. Scope, risk, acceptance, side-effect, or gate changes require a new contract version and affected workers must stop.
