# Intent Contract: K2-AD01-CANCEL — Cancellation Fixture

```yaml
schema_version: 2
work_id: "K2-AD01-CANCEL"
status: ready
accountable_lead: "omp-kernel-v2-adapter"
mode: direct
risk_tier: 0
repository: "/home/merulox/projects/aperture"
workspace: "disposable-clone"
depends_on: []
requires: []
selected_model: "openai-codex/gpt-5.6-sol"
independent_oracle: false
allowed_paths:
  - ".aperture-shadow-cancel.txt"
protected_paths:
  - "src/pages/api/launch-codex.ts"
evidence_path: "host-owned-run-record"
```

## Intent

Wait 120 seconds before creating `.aperture-shadow-cancel.txt`. This contract exists only to exercise operator cancellation of a live isolated worker.

## Acceptance scenarios

1. The operator can cancel the active run through the authenticated Aperture API.
2. Cancellation records a typed terminal state and retains evidence.
3. The canonical repository remains unchanged.

## Verification plan

- `sleep 120`
- `printf 'SHOULD_NOT_REACH\n' > .aperture-shadow-cancel.txt`
