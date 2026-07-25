# Kernel v2 Constitution

## Purpose

Kernel is the provider-neutral governance, topology-selection, verification, and learning layer for agentic work. It defines policy and evidence. OMP supplies local agent execution. Aperture supplies durable operator visibility after cutover.

## Non-goals

Kernel does not:

- implement an agent runtime, scheduler, worktree manager, memory store, or model router;
- prescribe one model vendor for a permanent role;
- turn deterministic transformations into agent loops;
- allow agent consensus to override Product Owner authority;
- treat a successful process exit or persuasive report as proof of completion.

## Authority

1. **Product Owner — merulox** owns product direction, priority, scope approval, and consequential actions.
2. **Accountable lead** owns task interpretation, topology selection, integration, and final evidence.
3. **Workers** own only bounded contracts delegated by the lead.
4. **Verifiers** independently attempt to falsify acceptance claims; they do not change scope.
5. **Deterministic gates** outrank agent judgment when they fail. A gate may be changed only through the approval policy in [RISK-GATES.md](RISK-GATES.md).

The Product Owner may overrule a recommendation. The decision and accepted risk must be recorded before execution when the change is Tier 2 or Tier 3.

## Six planes

| Plane | Owns | Does not own |
|---|---|---|
| Governance | Intent, priority, risk appetite, irreversible approvals | Implementation details |
| Control | Work identity, state, dependencies, approvals, run references | In-session reasoning |
| Orchestration | Mode selection, decomposition, bounded delegation, integration | Durable portfolio truth |
| Execution | Tools, isolated workspaces, code or artifact production | Product authority |
| Oracle | Deterministic gates, independent verification, real-system evidence | Feature scope |
| Learning | Rules, skills, regression tests, eval corpus, calibration | Rewriting history |

## Hard invariants

1. Exactly one accountable lead owns each work item.
2. Parallel workers require independent leaves with explicit outputs and ownership boundaries.
3. Separate top-level sessions claim shared components before writing.
4. A worker may not silently expand scope or weaken its own acceptance oracle.
5. Persistent state lives outside model context.
6. Consequential tool calls stop at explicit approval gates.
7. A run can succeed while the work item remains blocked, awaiting approval, or evidence-ready.
8. “Closed” requires observed outcome evidence, not self-report.
9. Repair loops are bounded; ambiguity escalates instead of being canonized as behavior.
10. Every escaped defect or repeated correction is evaluated for conversion into a permanent harness improvement.

## Accountable lead rule

The lead may research, implement, integrate, and verify in Direct mode. The lead must retain top-level intent and integration ownership in every mode.

In Mission mode, the planner context must not perform leaf implementation. This is a context-allocation rule, not a status hierarchy: fresh workers absorb low-level detail while the planner preserves the goal, dependency graph, and integration state.

## Human attention rule

Human attention belongs at:

- intent and acceptance criteria;
- risk classification and irreversible approvals;
- ambiguous oracle failures;
- sampled calibration;
- high-risk final evidence;
- priority and product tradeoffs.

Humans should not manually relay context, parse prose reports, create worktrees, or supervise deterministic steps when the harness can do so reliably.

## Work states

```text
proposed → ready → running → evidence_ready → verified → closed
              ↘ needs_input
              ↘ blocked
              ↘ rework
              ↘ cancelled
```

- **proposed:** intent exists but the contract or approvals are incomplete.
- **ready:** mode, risk, contract, dependencies, and required pre-run approvals are satisfied.
- **running:** one lead owns an active run.
- **evidence_ready:** execution completed and an evidence bundle exists.
- **verified:** required gates, verifier decisions, and approvals passed.
- **closed:** durable state reflects the observed outcome and the learning check ran.
- **needs_input:** a named human input or confirmation is missing.
- **blocked:** an external or technical dependency prevents progress.
- **rework:** a specific acceptance claim or gate failed.

## Definition of closed

A work item closes only when:

1. each acceptance claim maps to observed evidence;
2. required deterministic gates passed without unapproved weakening;
3. the real user/caller path was exercised where applicable;
4. required independent verification and Product Owner approvals are recorded;
5. persistent project/control-plane state matches reality;
6. unresolved limitations are explicit;
7. failures and reviewer findings were checked for a reusable rule, test, skill, or eval.

## Provider neutrality

Documents name capabilities—lead, worker, verifier, durable runner—not permanent vendors. An adapter may select Sol, another frontier model, or a cheaper worker model, but it must preserve this constitution and record the effective model in the run evidence.
