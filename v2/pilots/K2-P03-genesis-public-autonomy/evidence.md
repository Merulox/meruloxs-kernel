# Evidence Bundle: K2-P03 — Genesis Public Autonomy Oracle

## Identity

```yaml
schema_version: 2
work_id: K2-P03
status: review-ready
risk_tier: 2
consumer: ~/projects/genesis/runtime_v2/moltbook.py
authority: ~/kernel/v2/pilots/K2-P03-genesis-public-autonomy/oracle-authority.json
```

## Reviewed artifact

The canonical authority independently allowlists `moltbook-redteam-v1`, corpus SHA-256 `be8af218c41bea50976aa0c323397da0954c9b40281fa80e2be0d1ad119bf774`, and the ordered 22-case corpus. Its semantic authority version is `2026-10-16.1`. The exact canonical authority SHA-256 is `d17bd50a5cd67ddefd3732dade90b53cab50988509a122d3c1f4bdda2d4c0827`; Genesis readiness exposes this digest.

## Acceptance evidence scaffold

| Claim | Deterministic observation | Expected |
|---|---|---|
| Authority is strict and canonical | Parse and canonical reserialize the JSON | Exact bytes and exact field set match |
| Valid authority permits evidence | Run the offline corpus using the injected authority path | Passing row recorded; authority digest exposed |
| Missing authority fails closed | Use a nonexistent injected authority path | Recording refused; readiness false |
| Corpus mismatch fails closed | Change only authority corpus digest in a test fixture | Recording refused; readiness false |
| Embedded drift lacks authority | Change consumer corpus without Kernel update | Digest or ordered IDs mismatch; readiness false |
| Service remains read-only | Inspect consumer access | Authority path is only read; no Kernel write |

## Review notes

This bundle does not claim hard filesystem isolation. Independence comes from a distinct repository, fixed path, explicit version, and separate review/commit. Verification and commit receipts are completed by the accountable lead after the parent test run.
