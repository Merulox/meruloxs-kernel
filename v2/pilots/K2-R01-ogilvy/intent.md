# Intent Contract: K2-R01 — Ogilvy governed-action projection

```yaml
schema_version: 2
work_id: "K2-R01"
status: verified
accountable_lead: "omp-agent-substrate"
mode: routine
risk_tier: 0
repository: "/home/merulox/projects/boreal"
workspace: "/home/merulox/projects/boreal"
depends_on:
  - "/home/merulox/projects/realm/operations/governed-agent-substrate.md"
requires: []
allowed_paths:
  - "/home/merulox/projects/boreal/scripts/ogilvy-review"
  - "/home/merulox/projects/boreal/scripts/ogilvy.py"
  - "/home/merulox/projects/boreal/test_ogilvy.py"
  - "/home/merulox/kernel/v2/pilots/K2-R01-ogilvy/evidence.md"
protected_paths:
  - "/home/merulox/projects/boreal/scripts/crm_lib.py"
  - "/home/merulox/projects/boreal-outreach/04-content-batch.md"
  - "/home/merulox/projects/boreal-leads/crm.db"
  - "/home/merulox/.config/systemd/user"
oracle:
  mode: none
  visibility: not_applicable
  owner: null
  executor_disclosure: public_spec_only
isolation:
  workspace_disposition: primary
  mount_allowlist: []
  oracle_excluded_from_executor_namespace: false
  runtime_identity: "host Python runtime"
  credential_refs: []
  egress_policy: "no network access required"
  host_evidence_path: "/home/merulox/kernel/v2/pilots/K2-R01-ogilvy/evidence.md"
max_local_repairs: 2
max_expensive_repairs: 0
evidence_path: "/home/merulox/kernel/v2/pilots/K2-R01-ogilvy/evidence.md"
```

## Outcome

An operator can inspect any Ogilvy content proposal through a deterministic read-only command and receive one normalized governed-action envelope derived from existing proposal, review, and content-batch evidence.

## Why now

Ogilvy is the lowest-risk real resident path: it proposes persistent content, requires human review, appends only to a local batch after approval, suppresses duplicate appends, and never publishes directly. A read-only projection tests the shared semantics without changing authority or storage.

## Preconditions

- The existing Ogilvy proposal and review behavior remains canonical.
- `ogilvy-review` continues to require explicit `approved` or `declined` decisions for mutation paths.
- The production CRM and content batch remain untouched during verification.
- The current user instruction on 2026-08-04 to carefully plan and start the governed substrate rollout is recorded as Product Owner scope approval for this read-only pilot only.

## Interfaces and ownership

| Interface/path | Owner | Allowed change |
|---|---|---|
| `scripts/ogilvy-review` | accountable lead | Add a mutually exclusive read-only inspection mode while preserving review behavior |
| `scripts/ogilvy.py` | accountable lead | Add pure helpers for canonical proposal digest or batch-receipt inspection only if this avoids duplication |
| `test_ogilvy.py` | accountable lead | Add observable CLI scenarios using temporary CRM and content files |
| `evidence.md` | accountable lead | Record exact gates and real CLI output after implementation |

Nothing outside this table may change without returning the contract to `proposed` or `needs_input`.

## Public specification

- Visibility: public.
- Public caller: `ogilvy-review --action-id <id> --inspect`.
- Inspection is mutually exclusive with `--decision` and never acknowledges, approves, declines, appends, publishes, sends, or writes.
- Successful output is one JSON object with:
  - `ok: true`;
  - `schema_version: 1`;
  - stable `action_id` and `action_key`;
  - `producer: "ogilvy"`;
  - `accountable_owner: "merulox"`;
  - `capability: "boreal.content_batch.append"`;
  - `effect_class: "reversible_local"`;
  - `idempotency_key` equal to the existing Ogilvy batch marker identity;
  - deterministic `payload_digest` over the immutable proposal action key, summary, and canonical detail JSON;
  - `approval.required: true` plus normalized state, decision evidence, and actor when available;
  - `execution.state` plus the existing content-batch marker receipt when available;
  - `normalized_state`;
  - `evidence_refs` identifying only existing project-local records.
- Normalized states:
  - unresolved proposal with no decision and no receipt: `proposed`;
  - declined proposal with matching review evidence and no receipt: `rejected`;
  - approved proposal with matching review evidence and batch marker: `succeeded`;
  - contradictory or incomplete evidence: `reconciliation_required`.
- Missing, malformed, non-Ogilvy, or non-reviewable identities return `ok: false`, a stable error string, and non-zero exit without mutation.

## Acceptance scenarios

### Scenario 1 — Pending proposal

- **Given:** an Ogilvy `content_proposed` action with no `reviewed_at`, decision row, or batch marker.
- **When:** the operator runs `--inspect`.
- **Then:** the command reports `normalized_state=proposed` and performs zero writes.
- **Evidence:** CLI JSON plus before/after database and content hashes.

### Scenario 2 — Approved and materialized

- **Given:** a proposal with `reviewed_at`, a matching `content_approved` decision row, and its exact `[ogilvy:<id>]` batch marker.
- **When:** the operator runs `--inspect`.
- **Then:** the command reports `normalized_state=succeeded`, the approval actor, and a batch receipt.
- **Evidence:** CLI JSON plus unchanged database and content hashes.

### Scenario 3 — Declined

- **Given:** a proposal with `reviewed_at`, a matching `content_declined` decision row, and no batch marker.
- **When:** the operator runs `--inspect`.
- **Then:** the command reports `normalized_state=rejected` and no execution receipt.
- **Evidence:** CLI JSON plus unchanged database and content hashes.

### Scenario 4 — Contradictory evidence

- **Given:** approval, review, and batch evidence that cannot describe one legal lifecycle.
- **When:** the operator runs `--inspect`.
- **Then:** the command reports `normalized_state=reconciliation_required`; it does not guess, repair, or mutate.
- **Evidence:** CLI JSON and unchanged fixture hashes.

### Scenario 5 — Existing approval path

- **Given:** the existing approval and decline fixtures.
- **When:** the existing review CLI tests run without `--inspect`.
- **Then:** approval still appends exactly once, decline never appends, and already-resolved/non-Ogilvy actions still fail.
- **Evidence:** the existing Ogilvy test suite.

## Invariants

- Inspection is read-only for SQLite, content files, services, network, and configuration.
- The projection derives state from authoritative existing evidence; it creates no second source of truth.
- Payload digest generation is deterministic and insensitive to JSON key order.
- An approved decision without its materialized receipt is not reported as succeeded.
- A batch marker without matching approval evidence is not treated as approval.
- Existing review output and exit semantics remain unchanged.

## Forbidden outcomes and side effects

- No schema migration or production data mutation.
- No write to `crm_lib.py`, `04-content-batch.md`, or the live CRM.
- No service/timer enablement, restart, or configuration change.
- No Facebook, Telegram, Twilio, browser, MCP, payment, or other network action.
- No automatic approval, repair, reconciliation, publication, or state promotion.
- No Kernel v2 or Aperture cutover claim.

## Evidence expectations

| Public claim/invariant | Required observer or action | Required artifact |
|---|---|---|
| K2-R01-I1 read-only | Hash temporary DB and content before and after every inspect scenario | evidence bundle |
| K2-R01-I2 legal normalization | Exercise pending, approved, declined, and contradiction fixtures | targeted test output |
| K2-R01-I3 existing behavior preserved | Run existing Ogilvy approval/decline tests | targeted test output |
| K2-R01-I4 real caller path | Invoke `ogilvy-review --inspect` against an isolated fixture | captured CLI JSON |
| K2-R01-I5 containment | Confirm protected paths and user services are unchanged | evidence bundle |

## Verification plan

| Gate | Command/observer | Expected result | Blocking |
|---|---|---|:---:|
| Syntax | Python compile for changed scripts | exit 0 | yes |
| Targeted contract | Existing project Ogilvy test command | all tests pass | yes |
| Read-only invariant | Fixture hash checks around inspect calls | hashes identical | yes |
| Real CLI | Invoke inspection against temporary fixture | valid normalized JSON | yes |
| Containment | Inspect allowed paths and service state | no protected mutation or service change | yes |

Manifest: not available; this pilot uses the owning project's existing unittest convention.

## Real-system exercise

Run the actual `ogilvy-review --inspect` executable with environment-overridden temporary CRM and content paths following the existing test harness convention. The executable—not a helper-only test—must emit the normalized JSON while hashes remain unchanged.

## Rollback and containment

- Rollback method: revert only the allowed script/test changes; the pilot creates no persistent migration.
- Stop condition: implementation requires editing `crm_lib.py`, the live CRM/content batch, service configuration, or an outward-facing action.
- Post-action health check: existing review tests pass and `hormozi-cycle`, `boreal-followup`, `boreal-campaign`, and publisher service state remain unchanged.

## Non-goals

- Persisting a new lifecycle table or event schema.
- Changing Ogilvy review, append, or publishing authority.
- Adapting Hormozi, Compounder, Orbit, Genesis, or Boréal follow-up.
- Adding an Aperture/Commander UI.
- Activating Kernel v2 globally.
- Implementing MCP, A2A, WebMCP, NLWeb, commerce, payment, or identity protocols.

## Clarifications and approved changes

- 2026-08-04 — the accountable lead classified the inspection-only pilot as Tier 0 with no approval flags: it reads existing local evidence, changes no schema or persistent data, and performs no deployment or consequential side effect. The broader Product Owner instruction initiated the rollout but is not treated as approval for any later data, schema, deploy, communication, publishing, money, security, or Kernel v2 cutover action.
