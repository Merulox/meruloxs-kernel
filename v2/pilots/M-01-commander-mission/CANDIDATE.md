# M-01 — Commander Mission-mode governance pilot (candidate)

**Status:** PROPOSED / NOT AUTHORIZED FOR EXECUTION
**Date:** 2026-10-18
**Owner:** Product Owner (approval required)
**Candidate accountable lead:** GPT via ChatGPT for planning/review; API runner optional after adapter verification
**Repository under test:** Merulox/commander
**Governing protocol:** Kernel v1 remains authoritative; Kernel v2 is pilot-only.
**Motivation:** Determine whether versioned intent, independent acceptance and durable session recovery prevent architecture drift and misleading completion claims in a real multi-milestone task.

## Verified baseline (remote repository evidence, not live-runtime evidence)

- Kernel `v2/PILOTS.md` lists K2-P03 Mission pending and protected oracle pilot pending. Fan-out is marked verified in its pilot table but unchecked in its exit checklist; reconcile before global cutover.
- Kernel `v2/CONSTITUTION.md`, `MODES.md`, `CONTRACTS.md`, and `RISK-GATES.md` already define the governance primitives. Do not implement a second runner, scheduler, or memory store.
- Commander's README advertises OMP Workstreams and operational evidence surfaces. This is **not** proof of their behavior in the live installation.
- Commander's `AGENTS.md` requires GitNexus upstream impact analysis *before any symbol edits*, `detect_changes()` *before commits*, and HIGH/CRITICAL warnings before proceeding.
- No local OMP workspace, GitNexus index, runtime logs, or real acceptance suite was accessed in preparing this candidate.

## Gate 0: select a real defect or unfinished feature

Before writing implementation code:
1. Connect the existing OMP execution environment and verify the precise entry point, authentication, workspace isolation and abort path using a harmless read-only action.
2. Run GitNexus query/context on Commander's Workstreams path; inspect real call graph, related tests, run-state source, and current UI/API output.
3. Record one **reproducible user-visible defect or incomplete behavior**, with baseline command, input, expected state, actual state, and evidence artifact. Do not fabricate a feature solely to exercise the pilot.
4. Show why remediation genuinely needs **at least two sequential runnable milestones with a validation barrier**. If not, downgrade to Direct or Fan-out; do not claim K2-P03 completion.
5. Freeze a versioned intent contract with explicit scope, non-goals, positive/negative/boundary scenarios, forbidden changes, risk tier, approval flags and repair limit; obtain PO approval.
6. If Tier 1 new behavior requires protected independent acceptance, establish verifier-only storage, disposable executor namespace, explicit mount allowlist, pinned runtime, limited egress, and host-owned evidence before coding. If unavailable, mark BLOCKED rather than silently replacing the oracle with executor-authored tests.

## Proposed shape, contingent on Gate 0

Milestone A: reproduce the selected Commander workflow defect; establish an executable contract for the real endpoint or UI and the state transition that must occur. Validation barrier: independent verifier confirms baseline reproduction, non-goals, and a passing unchanged-system safety smoke test.

Milestone B: a fresh bounded worker implements the minimum change in an isolated workspace; the accountable lead integrates only after GitNexus impact analysis and ownership checks. Validation barrier: format/type/lint, relevant regression suite, protected acceptance check when applicable, direct exercise of the real interface, verified rollback, and a structured independent PASS/FAIL/ESCALATE verdict.

Optional milestone C: only if Gate 0 discovers a *genuine* further dependent integration requirement; do not manufacture scope.

## Non-negotiable invariants

- No production deployment, auth change, customer data access, messaging, money movement, or persistent-data mutation without tier-appropriate separate approval.
- One accountable lead per work item; implementation workers cannot revise product scope or acceptance.
- Planner in Mission mode does not implement leaves; fresh worker contexts implement bounded contracts.
- Tests oracles may not be weakened by executors; protected tests must not be mounted into their namespaces.
- A successful agent process is **not** a verified or closed work item.
- Every milestone leaves a runnable coherent system and a host-owned evidence bundle.
- At most two expensive retries without escalation; retain unsuccessful artifacts.
- Record original vs effective models and costs, context reset, human steering, regressions, and escaped defects.
- Code commits must respect Commander `AGENTS.md` GitNexus impact and detect_changes requirements.
- Kernel v1 activation state and Aperture launcher are unchanged.

## Required deliverables

`M-01/intent-v1.yaml`: approved scoped intent, invariant IDs, scenarios, dependency DAG, authority, risk and rollback.

`M-01/baseline.md`: exact reproducible input/output, real interface, revision hashes, timestamps and source-of-truth locations.

`M-01/oracle-manifest.json`: verifier identity, protected-oracle digest and isolation proof (no private oracle source or paths exposed to workers).

`M-01/runs/*.json`: durable run IDs, model, worker boundaries, lease/ownership, attempts, status and evidence references.

`M-01/verification.md`: deterministic commands/results, final real-path demonstration, verifier verdict, remaining defects, rollback proof.

`M-01/scorecard.md`: time, human steering, token/cost when available, scope deviations, retries, defects, context continuity; compare to a similar prior task only when baseline is actually available.

## Decision rules

**PASS:** two *genuine* sequential milestones with real runnable barriers; fresh worker continuity; independent evidence sufficient to falsify claims; no unapproved architectural drift; user-visible outcome observed.

**FAIL:** an accepted criterion is disproved, gate silently weakened, code path cannot be exercised, or scope expands without approval.

**ESCALATE/BLOCKED:** missing OMP integration, live GitNexus analysis, protected verifier isolation, product authority or a suitable multi-milestone task.

A PASS here is only evidence toward K2-P03, not automatic Kernel v2 cutover. The separate protected-oracle pilot and all other cutover conditions still apply.

## Immediate next action

Perform read-only discovery through OMP and GitNexus; propose the smallest real Commander Workstreams defect for PO approval. Until then, do **not** represent this document as proof of executed agent orchestration.
