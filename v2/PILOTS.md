# Kernel v2 Pilot and Cutover Protocol

## Status

Kernel v2 is a candidate. v1 remains active until all exit criteria pass and the Product Owner explicitly approves cutover.

## Required pilots

| Pilot | Real task shape | Required proof | Status |
|---|---|---|---|
| K2-P01 | Direct: tightly coupled work completed by one accountable lead | Intent, gates, real outcome, evidence bundle | [verified](pilots/K2-P01-direct/evidence.md) — bootstrap |
| K2-P02 | Fan-out: at least two genuinely independent leaves | Worker contracts, isolation, typed results, integration evidence | pending real task |
| K2-P03 | Mission: at least two milestones with a validation barrier | PO-approved intent, milestone DAG, fresh workers, repair/escalation record | pending real task |

Routine mode is validated separately on the first repeated workflow proposed for migration. It is not a prerequisite for replacing the coding-task protocol.

## Protected-oracle blocking pilot

**Status: pending.** Queue the first blocking `public_spec_hidden_checks` run on the next genuine Tier 1 task that introduces new behavior and requires an independent acceptance oracle. Do not manufacture a task or alter its topology to exercise the boundary.

The completed Codex/Podman spike is feasibility evidence only; it is not this pilot and does not prove production adapter integration. The queued task may close only after an independent verifier confirms a disposable executor workspace, explicit mount allowlist, verifier-storage absence, pinned runtime identity, credential indirection, explicit egress policy, host-side oracle execution after worker exit, host-owned evidence, and a structured verdict. Until then this pilot and every related exit criterion remain unchecked.

This pilot does not change K2-P01's verified status, does not satisfy K2-P02 or K2-P03, and does not authorize any Aperture launcher or service change.

## Pilot procedure

1. Select a real task; do not manufacture parallelism or milestones to exercise a mode.
2. Create an intent contract with mode, risk, approvals, ownership, evidence, and repair limit.
3. Record baseline expectations: why this mode should reduce risk or human attention.
4. Execute without changing v1 global instructions.
5. Produce an evidence bundle.
6. Record metrics and topology failures.
7. Decide: keep mode rules, amend them, or reject the topology.
8. Convert reusable failures into a rule, contract field, gate, skill, or eval candidate.

## Scorecard

Each pilot records:

- elapsed wall time;
- Product Owner interventions after scope approval;
- lead interventions and steering events;
- worker count and model assignment;
- repair attempts and expensive retries;
- ownership or merge conflicts;
- deterministic gate failures;
- verifier verdict and any false rejection;
- escaped defects discovered before and after closure;
- available token/cost data;
- rules, tests, skills, or eval cases created from findings.

## Exit gate

All are required before v2 becomes active:

- [x] K2-P01 Direct completed with evidence.
- [ ] K2-P02 Fan-out completed with evidence.
- [ ] K2-P03 Mission completed with evidence.
- [ ] No pilot required silent scope expansion or unbounded repair.
- [ ] Risk tiers produced the expected approval behavior.
- [ ] Evidence bundles allowed an uninvolved verifier to judge outcomes.
- [ ] v2 reduced or justified human attention relative to v1.
- [ ] Root agent instructions have a reviewed v2 cutover patch.
- [x] Aperture OMP shadow adapter has its own impact analysis, [brief](../../projects/aperture/docs/planning/AP-33-omp-shadow-adapter.md), and [evidence](pilots/K2-AD01-shadow/evidence.md).
- [ ] Product Owner explicitly approves v2 activation and Aperture cutover.

## Aperture cutover gate

Do not modify `~/projects/aperture/src/pages/api/launch-codex.ts` during methodology pilots.

After the exit gate passes:

1. run GitNexus API/symbol impact analysis on the launch path;
2. define normalized work and run records;
3. write a separate adapter brief with rollback;
4. add an OMP run path beside Codex temporarily;
5. smoke-test Direct and Fan-out runs through the UI;
6. compare evidence and cancellation behavior;
7. switch the default only with Product Owner approval;
8. remove Codex-specific code after clean cutover—no permanent compatibility shim.

## Failure condition

Kernel v2 is rejected or revised if pilots show that it:

- increases human supervision without compensating quality;
- creates more coordination failures than v1;
- cannot express real approval and evidence requirements;
- duplicates OMP or Aperture capabilities;
- makes durable truth harder to locate;
- encourages unnecessary multi-agent execution.

## Pilot artifacts

Store accepted pilot contracts and evidence under `v2/pilots/<pilot-id>/`. Pilot artifacts are evidence, not permanent templates.
