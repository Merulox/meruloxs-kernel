# Intent Contract: K2-AD01-PROOF — Isolated Shadow Proof

```yaml
schema_version: 2
work_id: "K2-AD01-PROOF"
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
  - ".aperture-shadow-proof.txt"
protected_paths:
  - "src/pages/api/launch-codex.ts"
evidence_path: "host-owned-run-record"
```

## Intent

Create `.aperture-shadow-proof.txt` in the disposable workspace with exactly this single line:

```text
OMP_SHADOW_PROOF_OK
```

## Acceptance scenarios

1. The file exists in the disposable clone.
2. Its complete content is `OMP_SHADOW_PROOF_OK` followed by one newline.
3. No other repository path changes.
4. Do not commit, push, merge, restart, deploy, or access any host path outside the mounted workspace.

## Verification plan

- `test "$(cat .aperture-shadow-proof.txt)" = "OMP_SHADOW_PROOF_OK"`
- `git status --short`

## Non-goals

- Any production behavior change.
- Any canonical checkout change.
