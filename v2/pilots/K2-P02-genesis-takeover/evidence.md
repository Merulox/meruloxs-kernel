# Evidence Bundle: K2-P02 — K2-P02-20260804-01

## Identity

```yaml
schema_version: 2
work_id: "K2-P02"
run_id: "K2-P02-20260804-01"
mode: fan-out
risk_tier: 2
accountable_lead: "omp-agent-substrate-p02"
model: "openai-codex/gpt-5.6-sol"
repository: "/home/merulox/projects/genesis"
workspace: "/tmp/k2-p02-worker -> /home/merulox/projects/genesis"
revision_before: "1cbe25b92e34555e43b5cf3d4a9580e4ec59877b"
revision_after: "working tree on 1cbe25b92e34555e43b5cf3d4a9580e4ec59877b; no commit requested"
started_at: "2026-08-04T19:26:56-04:00"
finished_at: "2026-08-04T20:18:37-04:00"
workspace_disposition: primary
host_evidence_uri: "/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/evidence.md"
recommended_work_state: verified
```

## Contract and isolation

- Approved and closed intent: `/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/intent.md` — SHA-256 `b9190435db47267c26d55615524e87d135aa253a7fb79dee1a8d3f0a51a43b8d`.
- Frozen public contract: `/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/public-spec.md` — SHA-256 `a5aefa5065879a4718acd9e9b4fd9ebbbe6af83c5e350c11b6d022b2dcc4338c`.
- Candidate implementation ran in the disposable worktree `/tmp/k2-p02-worker`; writes were limited to the three approved Genesis paths.
- The executor received the public specification and candidate files only. It did not receive the protected oracle path or source.
- The protected oracle was created by a separate verifier identity and remained outside the candidate workspace under `/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/oracle/`.
- Candidate files were integrated only after public tests, independent review, protected oracle PASS, and a successful deliberate-mutant check.

## Acceptance evidence

| Claim | Observer/action | Expected | Observed | Result |
|---|---|---|---|---|
| P02-I1 exact authorized cancellation | Public suite + protected oracle | Digest/actor/reason validated; invalid/terminal/duplicate requests fail closed | Unauthorized, wrong-digest, unknown, terminal, duplicate, and reason-boundary cases preserved state and emitted durable refusals where a valid subject existed | PASS |
| P02-I2 durable pre-effect cancellation | Public suite + protected oracle | Proposed/approved/pre-effect executing work becomes terminal cancelled and stale claims are fenced | Queue, approval, and observed-unchanged preflight paths cancelled; attempts terminalized; stale execution refused; after-effect/ambiguous cases refused | PASS |
| P02-I3 ordered race outcomes | Separate-connection barrier tests + protected oracle | Cancellation/takeover serializes with execution; no split-brain state/effect | Tests admit only cancelled/no-effect or succeeded/durable-refusal outcomes and assert worker/transaction completion | PASS |
| P02-I4 bounded takeover | Public suite + protected oracle | One allowlisted takeover; queued and safely reversible pre-effect work cancelled; verified effects preserved | Concurrent takeover produced one winner; outstanding request inspection and filesystem state matched the contract | PASS |
| P02-I5 revocation while taken over | Public suite + protected oracle | Proposal, approval, claim, and execution are blocked for the filename | All four public boundaries rechecked durable takeover state; integrated smoke confirmed a proposal was refused while active | PASS |
| P02-I6 exact release and no revival | Public suite + protected oracle | Exact actor/ID/reason releases; stale/duplicate release refuses; cancelled work stays terminal; fresh work succeeds | Wrong/stale/duplicate/concurrent release cases passed; post-release fresh request executed and rolled back; earlier requests remained cancelled | PASS |
| P02-I7 durable inspection | Public suite + protected oracle | Request inspection exposes cancellation; takeover inspection exposes active state and append-only ordered history | Request/attempt/control evidence and takeover/release/refusal history were deterministic and queryable | PASS |
| P02-I8 baseline survives | Full Genesis suite + protected oracle | Existing capability invariants remain valid; schema v2 mismatch fails closed | Integrated full suite passed 125/125; protected oracle included baseline safety, workspace binding, schema-v2 reset-required, crash/recovery, and rollback scenarios | PASS |
| P02-I9 end-to-end lifecycle | Real integrated smoke | Cancel -> takeover -> blocked automation -> release -> fresh approve/execute/review/rollback | `cancelled`, proposal blocked, `released`, fresh `succeeded`, receipt SHA matched, `rolled_back`, target absent | PASS |
| P02-I10 containment | Contract scan + protected oracle | No production service, network, credential, CLI, or unrelated-state access | Changed paths were only the approved broker, test, and contract files; no sensitive-reference/credential pattern matched | PASS |

## Real interface exercise

Executed against the integrated `/home/merulox/projects/genesis` Python API using a disposable SQLite database and workspace:

```json
{"cancel_status":"cancelled","file_exists_after_rollback":false,"receipt_sha_matches":true,"release_status":"released","resumed_created":true,"resumed_status":"succeeded","rollback_status":"rolled_back","stale_claim_captured":true,"takeover_blocked_proposal":true}
```

The exercise used `RuntimeStore.initialize()`, `CapabilityBroker.initialize()`, `propose`, exact `approve`, `claim`, `cancel`, `takeover`, blocked `propose`, exact `release_takeover`, fresh `propose`/`approve`/`claim`/`execute_claim`, `inspect`, and `rollback`.

## Verification

### Public and regression suites

- Isolated candidate focused capability suite: `python -m unittest -v tests.test_capability_v2` — **52/52 passed**.
- Isolated candidate full suite: `python -m unittest discover -s tests -v` — **125/125 passed** in 14.657 s.
- Integrated primary full suite: `python -m unittest discover -s tests -v` — **125/125 passed** in 13.428 s.
- Runtime: Python 3.13.14 on NixOS host `navi`.

### Protected oracle

Verifier command:

```text
/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/oracle/run_oracle.py --repo <candidate>
```

Final candidate and integrated-primary result:

```json
{"failed_public_invariant":null,"failure_class":null,"minimal_counterexample":null,"verdict":"PASS"}
```

Oracle SHA-256: `3229119ba447faa40e46865d0d6957e6e2017df0b3df624f23449823dc855396`.

The first oracle executions exposed verifier defects rather than candidate counterexamples: missing `RuntimeStore.initialize()`, an attempt-field parser accepting only `state` instead of the public `status`, and shared SQLite connections in threaded cases. The independent verifier repaired only verifier-owned code, reran syntax validation, and classified these as `oracle_failure`. The candidate then passed without oracle-driven candidate changes.

### Protected mutation check

A disposable clone was deliberately weakened by replacing `CapabilityBroker._require_operator` with a no-op. The same protected oracle returned exit 1:

```json
{"failed_public_invariant":"P02-I1","failure_class":"implementation_failure","minimal_counterexample":"unauthorized cancellation changed the request","verdict":"FAIL"}
```

The mutant directory was removed after the oracle killed it.

### Independent review

The first independent candidate review found three test-evidence gaps: real separate-connection cancel/takeover/release races, a complete post-release fresh lifecycle, and takeover/release reason/filename boundaries. These were repaired. A second independent review returned `pass`, closed all three findings, and reported no remaining contract findings.

Residual optional hardening from the reviewer: repeated scheduling could force both legal race serialization orders, and the original concurrent-takeover test could explicitly assert `conn.in_transaction is False` before closing each private connection. These do not weaken a public invariant: the implementation paths commit/refuse cleanly, added race cases assert transaction closure, and the protected oracle independently exercises both behavior classes.

### Security and containment

- `gitleaks`, `detect-secrets`, and `trufflehog` were not installed on the host.
- A direct credential/private-key pattern scan over all three changed files returned no matches.
- Independent review reported no security finding.
- GitNexus classified the broker change as high blast-radius because it touches the core state machine; its affected approve/claim/execute/recover/rollback paths are covered by the 125-test integrated suite and protected oracle.
- LSP diagnostics were unavailable because no Python language server is configured; imports/compilation were exercised by both suites and the real smoke run.

## Changed artifacts and ownership

| Artifact | Declared owner | Change |
|---|---|---|
| `/home/merulox/projects/genesis/runtime_v2/capabilities.py` | `omp-agent-substrate-p02` | Schema v3, durable control audit, cancellation, takeover/release, fencing, inspection, and recovery changes |
| `/home/merulox/projects/genesis/tests/test_capability_v2.py` | `omp-agent-substrate-p02` | Public contract, negative/boundary, concurrency, lifecycle, and regression coverage |
| `/home/merulox/projects/genesis/docs/capability-v2-contract.md` | `omp-agent-substrate-p02` | Durable cancellation/takeover/release contract and acceptance scenarios |
| `/home/merulox/kernel/v2/pilots/K2-P02-genesis-takeover/oracle/run_oracle.py` | `P02ProtectedOracle` | Independent verifier-owned public-invariant oracle |

Integrated file identities matched the verified worktree exactly:

```text
56eae0024c8800ab087ad46dca859b3f7a67f350356d17fce8912bc104c1e91d  runtime_v2/capabilities.py
617adfe079703db58a92ed4669acf6ebded2593934be94c5e58a9c62fa850b22  tests/test_capability_v2.py
9b70e2718566d3c73b638c66268c2d59f5e348dd366b32cdc733de4540201dd5  docs/capability-v2-contract.md
```

## Rollback and containment

- Before integration: discard `/tmp/k2-p02-worker`.
- After integration: restore only the three declared Genesis paths from revision `1cbe25b92e34555e43b5cf3d4a9580e4ec59877b`; do not reset or overwrite unrelated working-tree changes.
- Schema v3 deliberately requires reset of a disposable capability database whose durable metadata records another version. No production capability database or service was touched.

## Limitations and unresolved items

- No production or legacy Genesis service, CLI, credential, network, payment, CRM, or deployment path was exercised; those were explicitly excluded by the approved Tier 2 pilot.
- Concurrency tests are deterministic at the barrier/terminal-invariant level but allow either of the two contract-valid serialization orders.
- The pilot changes remain uncommitted, per the no-auto-commit rule.

## Final decision

- Work state: `verified`
- Oracle verdict: `PASS`
- Independent review: `pass`, no remaining findings
- Integration: completed for the three approved artifacts only
- Kernel v2 status: still pilot-only; no global cutover or production authority was activated
