# Evidence Bundle: [WORK-ID] — [Run ID]

## Identity

```yaml
schema_version: 2
work_id: "[WORK-ID]"
run_id: "[RUN-ID]"
contract_version: "[revision/hash/timestamp]"
mode: direct
risk_tier: 0
accountable_lead: "[session/person]"
model: "[effective model]"
repository: "[path]"
workspace: "[path/worktree]"
revision_before: "[revision or N/A]"
revision_after: "[revision or working-tree identity]"
started_at: "[timestamp]"
finished_at: "[timestamp]"
run_status: succeeded # succeeded | failed | blocked | cancelled
runtime_identity: "[pinned image digest and profile version, VM/toolchain identity, or N/A]"
workspace_disposition: primary # primary | isolated | disposable
host_evidence_uri: "[host-owned path/URI]"
recommended_work_state: evidence_ready
```

## Acceptance evidence

| Claim | Observer/action | Expected | Observed | Artifact | Result |
|---|---|---|---|---|---|
| [Scenario/invariant] | [command/journey/state query] | [expected] | [observed] | [path/URI] | PASS/FAIL |

## Changed artifacts and ownership

| Artifact | Declared owner | Change | Within contract |
|---|---|---|:---:|
| [path] | [lead/worker] | [summary] | yes |

Unexpected artifacts require explanation and verifier escalation.

## Deterministic gates

| Gate | Command | Exit/status | Artifact/output | Result |
|---|---|---|---|---|
| [gate-id] | [exact command] | [0/status] | [path or captured output] | PASS/FAIL |

No passing summary may replace missing raw output or artifact references.

## Protected-oracle isolation

Required when `independent_oracle` is set; otherwise record `N/A`.

```yaml
workspace_identity: "[disposable workspace identity]"
runtime_identity: "[pinned image digest/profile or equivalent]"
execution_profile: "[profile name and version]"
mount_manifest_artifact: "[host-owned path/URI]"
oracle_exclusion_proof: "[host-owned namespace/mount inspection artifact]"
credential_refs: [] # indirection names only; never values
egress_policy: "[policy identity or reviewed exception]"
executor_finished_at: "[timestamp]"
oracle_started_at: "[later timestamp]"
oracle_hash: "[content hash; never source/path/content]"
host_evidence_owner: "[control-plane/verifier identity]"
```

| Executor mount destination | Host source reference | Access | Purpose | Allowlisted |
|---|---|---|---|:---:|
| [destination] | [non-secret source identity or indirection] | ro/rw | [purpose] | yes |

The host records the complete mount manifest and direct proof that verifier storage was absent from the executor namespace. A worktree location, read-only permission, ownership rule, or worker statement is not absence proof.

## Real-system exercise

- Interface exercised:
- Environment identity:
- Initial state:
- Action:
- Resulting state:
- Screenshot/video/log/trace/state artifact:

## Worker results

For Fan-out or Mission mode, list worker run IDs, typed results, worktrees, and integration disposition.

## Verification

- Verifier:
- Context separation:
- Oracle owner:
- Oracle hash:
- Host-side oracle artifact:
- Verdict: NOT_REQUIRED / PASS / FAIL / ESCALATE
- Failure class: null / implementation_failure / oracle_failure / ambiguous_requirement / environment_failure / runner_failure
- Failed public invariant: [stable public ID or null]
- Minimal counterexample: [minimal public input and observed output, or null]
- Oracle source/path/content disclosed to executor: no / N/A
- Gate weakening detected: yes/no

## Approvals and containment

| Approval/guard | Actor | Scope | Timestamp | Evidence |
|---|---|---|---|---|
| [flag] | [actor] | [exact action] | [time] | [reference] |

- Rollback readiness:
- Canary/flag:
- Post-action health result:

## Repair and escalation history

| Attempt | Failure class | Failed invariant | Action | Outcome |
|---:|---|---|---|---|
| 1 | [class] | [constraint] | [repair/escalation] | [result] |

## Limitations and unresolved items

- None. / [Explicit limitation]

## Learning conversion

- Observation and evidence reference:
- Candidate hypotheses considered:
- Weakest sufficient hypothesis:
- Scope:
- Assumptions:
- Evidence count:
- Falsifier or narrowing observation:
- Supported invariant to protect:
- Rule:
- Skill:
- Test/gate:
- Eval candidate:
- Environment improvement:
- No reusable lesson, because:

## Final decision

- Work state: evidence_ready / verified / rework / blocked
- Decided by:
- Reason tied to evidence:
