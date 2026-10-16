# Intent Contract: K2-P03 — Genesis Public Autonomy Oracle

```yaml
schema_version: 2
work_id: K2-P03
status: review-ready
mode: direct
risk_tier: 2
repository: ~/kernel
consumer_repository: ~/projects/genesis
allowed_paths:
  - ~/kernel/v2/pilots/K2-P03-genesis-public-autonomy/**
evidence_path: ~/kernel/v2/pilots/K2-P03-genesis-public-autonomy/evidence.md
```

## Outcome

Genesis public-autonomy readiness depends on an independently versioned Kernel allowlist for the exact Moltbook red-team runner and corpus, rather than treating a digest embedded in Genesis as sufficient authority.

## Acceptance scenarios

1. A canonical authority names one runner version, corpus digest, ordered case-ID set, count, and fail-closed posture.
2. Missing, malformed, non-canonical, or mismatched authority blocks evidence recording and autonomous readiness.
3. Readiness exposes the authority digest used for its decision.
4. Review mode remains usable; this pilot neither enables nor switches autonomous mode.

## Trust boundary

Kernel is a separately versioned repository and review surface. This is an independent repository allowlist, not hard filesystem isolation: a sufficiently privileged local process can still modify both repositories. The consumer only needs read access to the fixed authority path, including under `ProtectSystem=strict`.

## Forbidden side effects

- No network or model invocation by the red-team runner.
- No mode switch, deployment, service restart, or relaxation of an existing gate.
- No writable Kernel access required by the Genesis service.
