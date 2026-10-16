# Public Spec: K2-P03 Genesis Public Autonomy Oracle

## Authority artifact

`oracle-authority.json` is UTF-8 canonical JSON: keys are sorted, separators are `,` and `:`, and no surrounding whitespace is permitted. Its exact field set is:

- `schema_version`: integer `1`
- `authority`: non-empty authority identifier
- `authority_version`: non-empty independently reviewed version
- `allowed_runner_version`: exact runner version allowed
- `corpus_digest`: lowercase SHA-256 of the consumer's canonical embedded corpus
- `expected_case_ids`: non-empty, unique, ordered string IDs
- `expected_case_count`: integer equal to the ID count
- `fail_closed`: literal `true`

Unknown, missing, mistyped, non-canonical, or inconsistent fields invalidate the artifact.

## Consumer behavior

Genesis reads the fixed absolute Kernel path on every computed-run recording and every readiness evaluation. Tests may inject a different path explicitly into the ledger. A computed proof must match the authority's runner, corpus digest, count, and ordered IDs. Readiness records the SHA-256 of canonical authority JSON and blocks on load, schema, canonicalization, or evidence mismatch.

The authority does not authorize public content, bypass policy, auto-switch mode, or replace containment and memory/reflection gates. It only allowlists the exact offline adversarial test definition eligible to contribute readiness evidence.

## Operational boundary

The service requires read-only traversal/read access to the authority path. It performs no write beneath `/home/merulox/kernel`, so a `ProtectSystem=strict` unit remains compatible when normal filesystem permissions permit reading. Separate Git history and review provide administrative independence, not kernel-enforced isolation from a privileged local actor.
