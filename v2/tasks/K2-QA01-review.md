# Review Report: K2-QA01 — Hard-Isolated Protected Oracles

Reviewer: independent OMP reviewer `ReviewK2QA01`
Date: 2026-07-24
Intent contract: `v2/tasks/K2-QA01-protected-oracle-integration.md`
Worker: `KernelV2IsolationIntegrator`

## Acceptance scenarios

| # | Scenario | Result | Evidence |
|---:|---|---|---|
| 1 | Protected means unreadable, not merely immutable | PASS | `RISK-GATES.md` requires oracle storage to be absent from every executor namespace and mount allowlist; `CONTROL-PLANE.md` requires explicit mounts and direct absence proof. Worktrees, prompts, permissions, and ownership are explicitly insufficient. |
| 2 | Executor receives a complete public contract | PASS | `CONTRACTS.md` requires the worker contract to include all public scenarios, invariants, forbidden outcomes, and evidence expectations while excluding oracle source/path/content and verifier-only gates. The intent and verification templates encode the same split. |
| 3 | Failure remains debuggable | PASS after repair 1 | Risk policy, verifier contract, manifest, and evidence template consistently emit PASS/FAIL/ESCALATE, stable failure class, public invariant, and minimal counterexample using null failure fields for PASS without exposing oracle internals. |
| 4 | Future adapter can enforce the boundary | PASS | `CONTROL-PLANE.md` requires disposable workspace, explicit mount allowlist, verifier-storage exclusion, pinned runtime, credential indirection, egress policy, host-run oracle after executor exit, host-owned evidence, and gated integration. |
| 5 | Pilot remains honest | PASS | `PILOTS.md` records the next genuine Tier 1 task as pending, identifies the Podman spike as feasibility evidence only, preserves K2-P01 verified and K2-P02/P03 pending, and retains the Aperture launcher prohibition. |

## Invariants

| Invariant | Result |
|---|---|
| Kernel v2 remains methodology, not another runtime | PASS |
| Existing topology pilot results remain unchanged | PASS |
| Run success remains distinct from work verification | PASS |
| Public requirements cannot be silently weakened | PASS |
| Worktree isolation is not treated as oracle secrecy | PASS |
| No production launcher or service changes | PASS |

## Initial review failure

The first independent review returned FAIL with confidence `0.97`:

1. `v2/templates/evidence-bundle.md` used `none` where the manifest's protected verdict schema required `null`.
2. `v2/templates/verification-manifest.yaml` limited the protected gate to Tier 1–3 despite `independent_oracle` being an orthogonal approval flag that may be set on Tier 0.

## Bounded repair 1/2

The original worker changed only the two failing templates:

- evidence verdict failure fields now use `null`;
- protected-acceptance `risk_tiers` is `[0, 1, 2, 3]` and remains dispatched by `requires_flag: independent_oracle`.

The worker reported successful parsing of the manifest and all three embedded YAML blocks. The independent reviewer re-read the repaired templates and returned:

```text
PASS. Evidence null sentinels match the risk policy and manifest. The protected-acceptance gate now dispatches at Tier 0 when independent_oracle is required. No new inconsistency or out-of-scope edit found.
```

The parent session could not independently invoke PyYAML because that module is absent from its runtime; no contrary parse evidence was observed.

## File scope

Worker changes were limited to the seven allowed paths:

- `v2/RISK-GATES.md`
- `v2/CONTRACTS.md`
- `v2/CONTROL-PLANE.md`
- `v2/PILOTS.md`
- `v2/templates/intent-contract.md`
- `v2/templates/verification-manifest.yaml`
- `v2/templates/evidence-bundle.md`

Repair 1 changed only the final two template files. The intent contract, research spike, D-003/D-004, v1 files, Aperture launcher, scripts, and services were not modified by the worker.

Parent-session scope verification inspected `history://KernelV2IsolationIntegrator`: the implementation edit operations at trace lines 104 and 132 targeted only the seven allowed files; repair edit line 186 targeted only the two permitted template files. No worker edit operation targeted the task contract or protected source records.

The intent contract remains frozen with its launch-time `status: ready`; this review/evidence file is the authoritative closure record.

## Final verdict

**PASS** — K2-QA01 is verified after one bounded repair. The production adapter and first genuine Tier 1 protected-oracle pilot remain intentionally pending.
