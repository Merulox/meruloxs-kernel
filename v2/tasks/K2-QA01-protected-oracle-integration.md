# Intent Contract: K2-QA01 — Integrate Hard-Isolated Protected Oracles

```yaml
schema_version: 2
work_id: "K2-QA01"
status: ready
accountable_lead: "omp-kernel-v2-isolation"
mode: direct
risk_tier: 0
repository: "~/kernel"
workspace: "~/kernel/v2"
depends_on: []
requires: []
allowed_paths:
  - "v2/RISK-GATES.md"
  - "v2/CONTRACTS.md"
  - "v2/CONTROL-PLANE.md"
  - "v2/PILOTS.md"
  - "v2/templates/intent-contract.md"
  - "v2/templates/verification-manifest.yaml"
  - "v2/templates/evidence-bundle.md"
protected_paths:
  - "docs/research/agentic-qa-hard-isolation-spike-2026-07-24.md"
  - "project/DECISIONS.md"
max_local_repairs: 2
max_expensive_repairs: 0
evidence_path: "v2/tasks/K2-QA01-review.md"
```

## Outcome

Kernel v2 defines a protected oracle as a verifier-owned check that is absent from the executor filesystem namespace, and its contracts carry enough isolation and evidence data for a future OMP/Aperture adapter to enforce that boundary.

## Why now

The Product Owner selected an independent verifier, public behavioral specifications with hidden executable checks, tiered opt-in rollout, and hard isolation. A real Codex/Podman spike proved that explicit mounts can keep the oracle absent while preserving a writable workspace. Kernel v2 currently protects oracle files from modification but does not define read isolation; worktrees alone do not provide it.

This task integrates the approved decisions and proven boundary into the existing v2 model. It must not create a parallel protocol or runtime.

## Preconditions

- Read `~/kernel/v2/README.md`, `CONTRACTS.md`, `RISK-GATES.md`, `CONTROL-PLANE.md`, and `PILOTS.md`.
- Read the canonical evidence at `~/kernel/docs/research/agentic-qa-hard-isolation-spike-2026-07-24.md`.
- Preserve the rule in `PILOTS.md`: do not modify Aperture's production Codex launcher during methodology pilots.

## Interfaces and ownership

| Interface/path | Owner | Allowed change |
|---|---|---|
| `v2/RISK-GATES.md` | worker | Define protected-oracle read isolation, visibility, failure disclosure, and gate-change rules. |
| `v2/CONTRACTS.md` | worker | Extend intent, worker, verifier, run, and evidence contracts with the minimum isolation fields. |
| `v2/CONTROL-PLANE.md` | worker | Define future adapter responsibilities for disposable workspaces, explicit mounts, host-run oracle, and host-owned evidence. |
| `v2/PILOTS.md` | worker | Queue the next genuine Tier 1 task as the protected-oracle blocking pilot; do not claim it has run. |
| `v2/templates/intent-contract.md` | worker | Add copyable public-spec/hidden-check and isolation fields. |
| `v2/templates/verification-manifest.yaml` | worker | Separate executor-visible gates from verifier-only protected gates and require structured verdicts. |
| `v2/templates/evidence-bundle.md` | worker | Record image/profile, mounts, oracle hash, absence proof, and structured verdict. |
| Research and decision records | architect/verifier | Read-only source of truth. |

Nothing outside this table may change. Do not modify `agents/`, `workflows/`, Aperture, scripts, services, package configuration, or the Podman spike fixtures.

## Acceptance scenarios

### Scenario 1 — Protected means unreadable, not merely immutable

- **Given:** a v2 task requires `independent_oracle`.
- **When:** an uninvolved operator reads the risk and control-plane contracts.
- **Then:** they can determine that the oracle path must be absent from every executor mount/namespace; prompt rules, file ownership, and worktrees are explicitly insufficient as the secrecy boundary.
- **Evidence:** exact contract sections and template fields.

### Scenario 2 — Executor receives a complete public contract

- **Given:** executable verifier checks are withheld.
- **When:** the worker contract is generated.
- **Then:** it contains all public scenarios, invariants, forbidden outcomes, and evidence expectations but no oracle source/path/content.
- **Evidence:** intent/worker/verifier contract language and template fields.

### Scenario 3 — Failure remains debuggable

- **Given:** a protected check fails.
- **When:** the host runner reports the result.
- **Then:** it emits `PASS`, `FAIL`, or `ESCALATE`, a stable failure class, the failed public invariant, and a minimal counterexample when available—without exposing oracle source.
- **Evidence:** risk policy, manifest schema, and evidence template.

### Scenario 4 — Future adapter can enforce the boundary

- **Given:** the v2 cutover gate later authorizes an OMP/Aperture adapter.
- **When:** its implementer follows `CONTROL-PLANE.md`.
- **Then:** the design requires a disposable workspace, explicit mount allowlist, verifier storage exclusion, host-side oracle execution after worker exit, host-owned evidence, pinned runtime identity, credential indirection, and explicit egress policy.
- **Evidence:** adapter and workspace policy sections.

### Scenario 5 — Pilot remains honest

- **Given:** no genuine Tier 1 task has yet run through the blocking protected-oracle gauntlet.
- **When:** `PILOTS.md` is updated.
- **Then:** it records the protected-oracle pilot as pending on the next genuine Tier 1 task and does not mark any exit criterion complete.
- **Evidence:** pilot status text.

## Invariants

- Kernel v2 remains a methodology and contract layer, not another agent runtime.
- Existing Direct/Fan-out/Mission pilot results remain unchanged.
- Run success remains distinct from work verification.
- Public requirements cannot be weakened after execution begins without a new contract decision.
- Oracle secrecy is never claimed from worktree isolation alone.
- No production launcher or service changes.

## Forbidden side effects

- No edits outside `allowed_paths`.
- No new scripts, services, containers, or dependencies.
- No modification of `~/projects/aperture/src/pages/api/launch-codex.ts`.
- No claim that the next real Tier 1 pilot has already passed.
- No copying secrets, auth files, or private oracle content into contracts or evidence.
- No duplicate v3/vNext protocol beside v2.

## Verification plan

| Gate | Observer | Expected result | Blocking |
|---|---|---|:---:|
| contract coverage | independent reviewer | Every acceptance scenario maps to exact changed sections. | yes |
| scope | independent reviewer | Only `allowed_paths` changed. | yes |
| consistency | independent reviewer | No contradiction across risk, contract, control-plane, pilot, and templates. | yes |
| honesty | independent reviewer | Spike is identified as evidence, not production integration; real pilot stays pending. | yes |
| source integrity | independent reviewer | Research and D-003/D-004 remain unchanged. | yes |

Manifest: `v2/templates/verification-manifest.yaml` after integration.

## Real-system exercise

No production system changes are allowed. The executable feasibility evidence is the already-completed Codex/Podman spike. This task's real outcome is that an uninvolved operator can use the edited v2 contracts and templates to identify the exact enforcement boundary and generate a complete future adapter brief without consulting conversation history.

## Rollback and containment

- Rollback method: revert only K2-QA01-owned documentation changes.
- Stop condition: any requirement to modify Aperture, create a runner, weaken v2 pilot gates, or edit outside allowed paths.
- Post-action health check: existing K2-P01 status and Aperture cutover prohibition remain intact.

## Non-goals

- Implementing the production OMP/Aperture adapter.
- Changing the current Codex launcher.
- Running the first blocking Tier 1 pilot.
- Building image management, credential proxying, or egress controls.
- Activating Kernel v2 or archiving v1.

## Clarifications and approved changes

- 2026-07-24 — Product Owner selected: independent verifier; tiered opt-in; public specification with hidden executable checks; hard isolation; next genuine Tier 1 request as the first blocking real-task pilot.
