# Risk Tiers and Gate Matrix

## Classification rule

Classify the highest plausible impact before execution. Risk is determined by blast radius, reversibility, data sensitivity, external side effects, and detectability—not task size.

## Tiers

### Tier 0 — Reversible internal work

Examples: documentation, read-only research, local tooling, reversible refactors with existing coverage.

Required:

- observable outcome;
- relevant fast deterministic checks;
- direct smoke test;
- evidence bundle when persistent or delegated;
- sampled independent audit, not mandatory review.

### Tier 1 — Normal product behavior

Examples: user-visible feature, API behavior, background job logic, non-sensitive persistent state.

Required:

- reviewed intent contract;
- positive, negative, and boundary scenarios;
- independent acceptance oracle for new behavior;
- full project gate stack applicable to the change;
- real user/caller-path evidence;
- independent verifier verdict before closure.

### Tier 2 — Consequential systems

Examples: authentication, privacy, billing, money, destructive data, production mutation, external communications, credentials, security controls.

Required in addition to Tier 1:

- Product Owner approval of intent and side effects before execution;
- protected verifier-owned acceptance tests or checks;
- property/metamorphic tests where applicable;
- diff-scoped mutation testing where applicable;
- security, secret, and dependency scans;
- rollback or containment proof;
- mandatory human review of the behavioral oracle and final evidence;
- canary or feature flag where feasible.

### Tier 3 — Safety-critical or irreversible

Examples: irrecoverable deletion, high-value financial authority, safety-critical control, destructive schema cutover without rollback.

Required in addition to Tier 2:

- explicit Product Owner approval at plan and execution boundaries;
- no unattended merge, deploy, or destructive action;
- independent verifier plus adversarial review;
- staged migration and restore rehearsal;
- formal model or proof where the state machine is narrowly formalizable;
- named rollback owner and stop condition.

## Approval flags

Flags are orthogonal to lifecycle state and risk tier:

| Flag | Approval required before |
|---|---|
| `po_scope` | Contract becomes ready |
| `data` | Persistent data write/delete |
| `schema` | Migration or schema mutation |
| `deploy` | Production publish/restart/cutover |
| `money` | Purchase, billing, transfer, paid API expansion |
| `security` | Credential, auth, permission, or exposure change |
| `independent_oracle` | Implementation begins when acceptance checks must be protected |

A flag is satisfied by a durable confirmation referencing who approved, what exact action was approved, and when. Approval of intent does not imply approval of deployment.

## Gate order

Run cheapest deterministic feedback first:

1. formatting check;
2. compile/type check;
3. lint and architecture checks;
4. secret and changed-file security scans;
5. targeted unit/contract tests;
6. full relevant deterministic suite;
7. property and mutation checks when required;
8. real-system exercise;
9. adversarial or independent verifier review;
10. containment and post-deploy checks.

A later pass does not override an earlier failure.

## Gate matrix

| Gate | T0 | T1 | T2 | T3 |
|---|:---:|:---:|:---:|:---:|
| Observable outcome | required | required | required | required |
| Reviewed intent contract | if persistent | required | required + PO | required + PO |
| Fast deterministic stack | required | required | required | required |
| Independent acceptance oracle | sampled | required for new behavior | protected | protected + adversarial |
| Real-system evidence | smoke | required | required | required |
| Property/metamorphic testing | when natural | when natural | required when applicable | required when applicable |
| Diff-scoped mutation | diagnostic | baseline/advisory | required when applicable | required when applicable |
| Security/dependency scans | secret check | changed-file | required | required |
| Rollback/containment | note reversibility | rollback note | demonstrated | rehearsed |
| Human final review | sampled | by policy | mandatory | mandatory |
| Unattended consequential action | allowed | allowed if reversible | prohibited without explicit gate | prohibited |

“Applicable” must be resolved in the intent contract; it may not be silently interpreted as “skip.”

## Protected oracles

When `independent_oracle` is required, the task uses a public specification with hidden executable checks:

- the intent contract freezes every public scenario, invariant, forbidden outcome, and evidence expectation needed to implement and judge the work;
- the executor receives that complete public specification and executor-visible gates, but no oracle source, storage path, executable content, verifier-only manifest entry, or private fixture;
- an independent verifier derives and owns the executable checks in verifier-only storage;
- a protected oracle's storage is absent from every executor filesystem namespace and every executor mount allowlist; it is not merely read-only or outside the executor's write ownership;
- prompt instructions, `FILES IT OWNS`, permissions, and isolated Git worktrees are defense in depth only. They do not establish read secrecy;
- the host invokes the oracle only after the executor has exited and records the oracle result outside the executor namespace;
- any oracle or verifier-only gate change after implementation begins requires verifier approval, a new oracle identity/hash, and retained evidence against the superseded oracle;
- ambiguity escalates to the Product Owner rather than treating either the implementation or the hidden check as the specification.

Protected-oracle feedback is a structured verdict containing:

```yaml
verdict: PASS | FAIL | ESCALATE
failure_class: null | implementation_failure | oracle_failure | ambiguous_requirement | environment_failure | runner_failure
failed_public_invariant: null | stable-public-invariant-id
minimal_counterexample: null | minimal-public-input-and-observed-output
```

`failure_class`, `failed_public_invariant`, and `minimal_counterexample` must be stable and sufficient to reproduce the public failure when available. Feedback must not expose oracle source, path, private fixture content, or enough private check structure to reconstruct the oracle. `PASS` uses null failure fields; a failure that cannot be attributed without guessing returns `ESCALATE`.

## Repair limits

- Cheap local repair loops must declare a finite limit in the contract.
- Expensive CI, production-like, or external-service retries default to two.
- After the limit, preserve the trace and failing artifact, mark `rework` or `blocked`, and report the exact failed invariant.
- A retry after changing acceptance criteria is a new decision, not another repair attempt.

## Gate weakening

Disabling a check, lowering a threshold, adding an ignore, or rewriting a fixture is a gate change. It requires:

1. a stated reason tied to the contract;
2. approval at the same level as the gate it weakens;
3. a replacement check or explicit accepted risk;
4. evidence that unrelated coverage was not reduced.
5. a new contract decision if public scenarios, invariants, forbidden outcomes, or evidence expectations would be weakened after execution began.
