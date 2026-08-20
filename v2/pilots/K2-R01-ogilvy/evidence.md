# Evidence Bundle: K2-R01 — K2-R01-20260804-01

## Identity

```yaml
schema_version: 2
work_id: "K2-R01"
run_id: "K2-R01-20260804-01"
contract_version: "intent.md @ 2026-08-04"
mode: routine
risk_tier: 0
accountable_lead: "omp-agent-substrate"
model: "openai-codex/gpt-5.6-sol"
repository: "/home/merulox/projects/boreal"
workspace: "/home/merulox/projects/boreal"
revision_before: "N/A — primary workspace already contained unrelated uncommitted changes"
revision_after: "working-tree identity recorded by changed artifact paths below"
started_at: "2026-08-04T16:48:00-04:00"
finished_at: "2026-08-04T17:30:43-04:00"
run_status: succeeded
runtime_identity: "NixOS 25.11 host navi; Python 3"
workspace_disposition: primary
host_evidence_uri: "/home/merulox/kernel/v2/pilots/K2-R01-ogilvy/evidence.md"
recommended_work_state: verified
```

## Pilot scorecard

| Metric | Observed |
|---|---|
| Elapsed wall time | Approximately 42 minutes 43 seconds |
| Product Owner interventions after scope approval | 0 |
| Accountable-lead steering events | 0 external steering events |
| Worker count and model | 1 accountable lead; `openai-codex/gpt-5.6-sol` |
| Repair attempts | 1 bounded repair after the receipt-boundary regression reproduced |
| Expensive retries | 0 |
| Ownership or merge conflicts | 0 encountered within the declared pilot files |
| Deterministic gate failures | 1 intentional red test reproducing false receipt inference; all closure gates passed |
| Verifier verdict / false rejection | `NOT_REQUIRED` for Tier 0 / none |
| Escaped defects known at closure | 0 |
| Token or cost data | Not available from the runtime |
| Reusable conversions | 1 managed-skill update; 1 regression test; 1 cross-resident reconciliation eval candidate |
| Topology result | Routine/sequential execution fit the repeated, deterministic inspection workflow; no topology failure observed |

## Acceptance evidence

| Claim | Observer/action | Expected | Observed | Artifact | Result |
|---|---|---|---|---|---|
| Existing Ogilvy proposals expose the shared governed-action fields without a schema migration | Real `ogilvy-review --action-id 1 --inspect` against an isolated HOME-backed SQLite fixture | Stable JSON envelope including ownership, capability, digest, normalized lifecycle, approval, execution, and evidence references | Exit 0; all required fields returned; pending proposal normalized to `proposed` / `pending` / `not_started` | Raw result below; `scripts/ogilvy.py`; `scripts/ogilvy-review` | PASS |
| Inspection is read-only | SHA-256 of fixture database and content batch before and after the real executable | Both artifacts byte-identical | DB `7177f0192edce0e365d5fa161a3adcf5ea3932e87420448f30d0fcd8457055d1` before and after; content `c62780e7a439c860b4d34350885cdef79686afb68f84a7f5d57b4f93b6848178` before and after | Real-system exercise below | PASS |
| Legal evidence combinations normalize deterministically | `python -m unittest -v test_ogilvy.py` | Pending, approved/materialized, and declined states match the shared contract | All state tests passed | `test_ogilvy.py` | PASS |
| Contradictory evidence fails closed | Test reviewed flag without a decision and materialized receipt without a matching approval | `reconciliation_required`, never inferred success | Both contradictions returned `approval.state=inconsistent` and `execution.state=reconciliation_required` | `test_ogilvy.py` | PASS |
| A stray marker is not accepted as an execution receipt | Test marker text outside a valid `POST <number>` heading | No receipt; reconciliation required | Initial test failed with false `succeeded`; repaired structural matching test passed | `test_ogilvy.py`; `scripts/ogilvy.py` | PASS |
| Existing approve/decline path remains operational | Existing CLI contract test | Approved proposal appends once and records a decision; decline records decision without appending | Existing tests passed unchanged alongside projection tests | `test_ogilvy.py`; `scripts/ogilvy-review` | PASS |

## Raw real-interface result

```json
{
  "exit_code": 0,
  "stdout": {
    "accountable_owner": "merulox",
    "action_id": 1,
    "action_key": "ogilvy:content:smoke",
    "approval": {
      "actor": null,
      "decided_at": null,
      "decision": null,
      "required": true,
      "reviewed_at": null,
      "state": "pending"
    },
    "capability": "boreal.content_batch.append",
    "effect_class": "reversible_local",
    "evidence_refs": ["learning_actions:1"],
    "execution": {"receipt": null, "state": "not_started"},
    "idempotency_key": "ogilvy:1",
    "normalized_state": "proposed",
    "ok": true,
    "payload_digest": "e7f30f22a81ed46f6a3b967ca38a9d4501220c7fda46be6fd22796bf2a30199a",
    "producer": "ogilvy",
    "schema_version": 1
  },
  "stderr": "",
  "hashes_unchanged": true,
  "before": {
    "db": "7177f0192edce0e365d5fa161a3adcf5ea3932e87420448f30d0fcd8457055d1",
    "content": "c62780e7a439c860b4d34350885cdef79686afb68f84a7f5d57b4f93b6848178"
  },
  "after": {
    "db": "7177f0192edce0e365d5fa161a3adcf5ea3932e87420448f30d0fcd8457055d1",
    "content": "c62780e7a439c860b4d34350885cdef79686afb68f84a7f5d57b4f93b6848178"
  }
}
```

## Changed artifacts and ownership

| Artifact | Declared owner | Change | Within contract |
|---|---|---|:---:|
| `/home/merulox/projects/boreal/scripts/ogilvy.py` | `omp-agent-substrate` | Added read-only governed-action projection and structural receipt validation | yes |
| `/home/merulox/projects/boreal/scripts/ogilvy-review` | `omp-agent-substrate` | Added mutually exclusive `--inspect` CLI path with normalized error output | yes |
| `/home/merulox/projects/boreal/test_ogilvy.py` | `omp-agent-substrate` | Added state, contradiction, read-only, and receipt-boundary regression tests | yes |
| `/home/merulox/kernel/v2/pilots/K2-R01-ogilvy/intent.md` | `omp-agent-substrate` | Recorded Tier 0 classification, corrected protected content path, and clarified authority | yes |
| `/home/merulox/kernel/v2/pilots/K2-R01-ogilvy/evidence.md` | `omp-agent-substrate` | Recorded this evidence bundle | yes |

The primary Boréal workspace already had unrelated changes across 18 files. GitNexus therefore reported repo-wide critical risk. That report is not treated as clean isolation evidence for K2-R01. This pilot did not edit `crm_lib.py`, the production CRM database, the production content batch, services, timers, credentials, or deployment state.

## Deterministic gates

| Gate | Command | Exit/status | Artifact/output | Result |
|---|---|---|---|---|
| syntax | `python -m py_compile scripts/ogilvy.py scripts/ogilvy-review` | 0 | No stderr/stdout | PASS |
| contract suite | `python -m unittest -v test_ogilvy.py` | 0 | 17 tests passed in 1.289 s | PASS |
| real CLI | `/home/merulox/projects/boreal/scripts/ogilvy-review --action-id 1 --inspect` with isolated `HOME` fixture | 0 | Raw JSON above | PASS |
| read-only proof | Compare SHA-256 of fixture SQLite/content files before and after real CLI | equal | Raw hashes above | PASS |

## Protected-oracle isolation

N/A. Tier 0 did not require an independent oracle.

## Real-system exercise

- Interface exercised: installed executable path `/home/merulox/projects/boreal/scripts/ogilvy-review`.
- Environment identity: isolated temporary `HOME`; production module files; HOME-relative fixture database and content batch.
- Initial state: one real Ogilvy proposal row; no decision; no receipt.
- Action: `--action-id 1 --inspect`.
- Resulting state: normalized `proposed`; approval `pending`; execution `not_started`; fixture hashes unchanged.
- Artifact: raw JSON and hashes in this evidence bundle.

## Verification

- Verifier: accountable lead, deterministic Tier 0 checks.
- Context separation: not required.
- Oracle owner: N/A.
- Oracle hash: N/A.
- Host-side oracle artifact: N/A.
- Verdict: NOT_REQUIRED.
- Failure class: null.
- Failed public invariant: null.
- Minimal counterexample: stray `[ogilvy:1]` marker outside a valid post heading initially produced false `succeeded`; now returns reconciliation required.
- Oracle source/path/content disclosed to executor: N/A.
- Gate weakening detected: no.

## Approvals and containment

| Approval/guard | Actor | Scope | Timestamp | Evidence |
|---|---|---|---|---|
| Tier 0 classification | accountable lead | Read-only projection and isolated verification only | 2026-08-04 | `intent.md` clarification |

- Rollback readiness: revert the three Boréal pilot files; no data migration or persistent pilot state exists.
- Canary/flag: `--inspect` is explicit and inert unless invoked.
- Post-action health result: production files, database, services, timers, credentials, and outbound behavior were not exercised or changed.

## Repair and escalation history

| Attempt | Failure class | Failed invariant | Action | Outcome |
|---:|---|---|---|---|
| 1 | implementation_failure | Execution receipt must be structurally valid, not a raw substring | Reproduced false success with a stray marker; changed receipt detection to require a valid `POST <number>` heading; reran focused and full suites | PASS |

## Limitations and unresolved items

- K2-R01 validates a read-only adapter over Ogilvy's existing proposal/decision/materialization evidence. It does not add a shared persistent schema or runtime.
- Retry, cancellation, human takeover, lease recovery, and full work-item closure are not exercised because this pilot creates no execution authority. The broader rollout audit keeps that gap open for a later stateful action adapter.
- Independent external verification was not required for Tier 0.

## Learning conversion

- Rule: execution success requires a structurally valid receipt from the target interface; substrings are not evidence.
- Skill: updated managed skill `propose-review-gate-resident-agent` with governed-action projection and receipt-validation procedure.
- Test/gate: `test_inspect_ignores_stray_marker_outside_post_header` protects the repaired boundary.
- Eval candidate: contradictory evidence normalization across future resident adapters.
- Environment improvement: none.

## Final decision

- Work state: verified.
- Decided by: accountable lead `omp-agent-substrate`.
- Reason tied to evidence: all public acceptance checks passed, the real CLI preserved fixture hashes, and no production authority or state was changed.
