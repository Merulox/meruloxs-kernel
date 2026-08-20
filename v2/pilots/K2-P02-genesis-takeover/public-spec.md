# K2-P02 public specification — Genesis capability cancellation and human takeover

## Scope

Extend the isolated Genesis `workspace.write_text` capability broker with explicit, durable cancellation and per-filename human takeover/release. Preserve the existing authority boundary, lease fencing, receipt verification, recovery, and rollback behavior.

This is a parallel-runtime pilot only. No production capability database, Genesis service, model tool access, deployment, external communication, credential, CRM, or Aperture path is in scope.

## Public interface

The broker must add:

```python
cancel(request_id, expected_digest, requested_by, reason, now=None) -> dict
takeover(filename, requested_by, reason, now=None) -> dict
release_takeover(filename, takeover_id, requested_by, reason, now=None) -> dict
inspect_takeover(filename) -> dict
```

`requested_by` must be an allowlisted operator. Every reason must be non-empty and bounded consistently with approval reasons. Cancellation must bind the exact immutable request digest. Release must bind the exact active takeover ID so a stale operator action cannot release a newer takeover.

## States and durable evidence

- Add terminal request state `cancelled`.
- Add terminal attempt state `cancelled`.
- Record every cancellation, takeover, release, race outcome, and refusal durably.
- A takeover subject is one validated capability filename inside the configured workspace.
- Takeover history must remain inspectable after release; only one active takeover may exist per filename.
- Existing cancelled requests remain terminal after release.

The schema becomes capability schema version 3. Because capability-v2 is isolated and explicitly disposable before cutover, version-2 databases must fail initialization with a clear reset-required error; no silent relabeling or risky in-place CHECK-constraint migration is allowed.

## Public invariants

### P02-I1 — Cancellation authority and digest binding

Only an allowlisted operator presenting the exact request digest and a non-empty reason can cancel. Wrong digest, unauthorized operator, empty reason, unknown request, terminal request, or unsupported state fails without mutation.

### P02-I2 — Cancellation before effect

`proposed`, `approved`, or `executing` requests may become `cancelled` only if the broker acquires the workspace serialization boundary before their filesystem effect begins. Cancellation clears leases, terminalizes an active attempt as `cancelled`, and prevents any later worker use of that claim.

### P02-I3 — Cancellation race

Cancellation and execution are serialized by the same workspace lock and database critical section. If cancellation wins, no file effect occurs and the worker is fenced. If execution already owns the boundary and succeeds first, cancellation fails without changing `succeeded`; rollback remains the only reversal path. No race may report both cancelled and succeeded.

### P02-I4 — Human takeover

An allowlisted operator may take over one validated filename with a non-empty reason. Before takeover returns, the broker must serialize against execution, cancel every `proposed`, `approved`, or not-yet-applied `executing` request for that filename, and persist one active takeover record. Existing verified effects remain unchanged and may be reversed only through the existing rollback interface.

### P02-I5 — Revocation while taken over

While takeover is active, proposal, approval, claim, and execution for the filename must fail closed or remain ineligible without filesystem mutation. Defense must exist at more than one boundary so a claim obtained before takeover cannot later execute.

### P02-I6 — Explicit release

Only an allowlisted operator with the exact active takeover ID and a non-empty reason may release. Wrong/stale ID, unauthorized operator, empty reason, duplicate release, or unknown filename fails without mutation. Release permits new proposals; it never revives cancelled requests or approvals.

### P02-I7 — Durable inspection

`inspect(request_id)` exposes cancellation evidence and cancelled attempts. `inspect_takeover(filename)` exposes active state and append-only takeover/release history. Audit ordering is deterministic.

### P02-I8 — Existing broker invariants survive

All existing capability-v2 acceptance scenarios remain valid: immutable requests, idempotency, approval binding, execution gating, path/type safety, stale-worker fencing, crash reconciliation, exact receipts, bounded rollback, and no production access.

### P02-I9 — End-to-end lifecycle exercise

Against an isolated database and workspace, exercise and preserve evidence for:

1. proposal and exact approval;
2. execution failure or expired-lease recovery followed by a newer retry;
3. successful execution and receipt review;
4. cancellation before effect;
5. takeover fencing an outstanding request;
6. refusal of new automatic work while taken over;
7. explicit human release;
8. a fresh post-release proposal, approval, execution, and review;
9. existing rollback containment.

### P02-I10 — Forbidden effects

The implementation and verifier must not touch production state, services, timers, network, credentials, model tools, CRM, legacy Genesis state, Aperture, or paths outside disposable workspaces and declared source files.

## Required tests

- Positive, negative, boundary, and concurrency tests for every invariant above.
- Existing `test_capability_v2.py` must still pass.
- A real Python public-surface exercise in a disposable workspace must emit inspectable JSON/state evidence.
- A protected verifier-owned oracle must pass the candidate and reject at least one plausible deliberate mutant.
- Applicable changed-file security and secret checks must pass.

## Repair limit

At most two implementation repair rounds after the protected oracle first runs. A changed public invariant requires a new contract decision, not a repair.

## Result contracts

Implementation result:

```yaml
status: succeeded | failed | blocked
changed_paths: []
public_gates: []
known_limitations: []
```

Verifier result:

```yaml
verdict: PASS | FAIL | ESCALATE
failure_class: null | implementation_failure | oracle_failure | ambiguous_requirement | environment_failure | runner_failure
failed_public_invariant: null | P02-I1..P02-I10
minimal_counterexample: null | string
```
