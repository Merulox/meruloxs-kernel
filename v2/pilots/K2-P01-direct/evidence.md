# Evidence Bundle: K2-P01 — Bootstrap Kernel v2

## Identity

```yaml
schema_version: 2
work_id: K2-P01
run_id: omp-kernel-v2-bootstrap
contract_version: C0E4
mode: direct
risk_tier: 0
accountable_lead: omp-kernel-v2
model: openai-codex/gpt-5.6-sol
repository: ~/kernel
workspace: ~/kernel
revision_before: not-captured-bootstrap
revision_after: sha256:876215e66bff60d479efce19480bb61521fb50044ce8c2e31218b05ce4c4a2da
started_at: not-captured-bootstrap
finished_at: 2026-07-24T11:18:17-04:00
run_status: succeeded
recommended_work_state: verified
```

The revision digest covers the final candidate tree after pilot-status closure: all v2 files except this self-referential evidence bundle, plus root `README.md`, `CLAUDE.md`, and `AGENTS.md`. Paths are included in the hash stream.

## Acceptance evidence

| Claim | Observer/action | Expected | Observed | Result |
|---|---|---|---|---|
| Candidate structure exists | Enumerated `v2/**/*` | 8 policy docs, 3 templates, pilot intent | All required paths present | PASS |
| Topology is selectable | Checked `MODES.md` headings | Direct, Fan-out, Mission, Routine | All four headings and selection algorithm present | PASS |
| Risk gates are explicit | Checked `RISK-GATES.md` | Tier 0–3 plus gate matrix | All tiers and matrix present | PASS |
| Contracts are machine-readable | `Bun.YAML.parse` on template manifest and fenced intent YAML | Valid mappings and expected schema IDs | manifest schema 1; intent schema 2; pilot ID K2-P01 | PASS |
| Document graph resolves | Resolved every local Markdown target under `v2/` | Zero missing targets | Zero missing targets | PASS |
| Root routing preserves v1 | Checked root README/CLAUDE/AGENTS strings | v2 candidate visible; v1 authoritative | All routing checks true | PASS |
| Aperture cutover is gated | Checked `PILOTS.md` protected route and exit gate | Explicit deferral and PO approval | Both present | PASS |
| Canonical research is discoverable | Exercised `project-context-hook` | Kernel project plus orchestration and QA research | Exit 0; both canonical research paths returned | PASS |
| Strategic retrieval reaches v2 claims | Exercised `vault-query-hook` with targeted orchestration question | `agentic-orchestration` domain and v2 claim | Exit 0; strategic mode; source and claim found | PASS |

## Changed artifacts and ownership

| Artifact | Declared owner | Change | Within contract |
|---|---|---|:---:|
| `v2/README.md` | accountable lead | Candidate entrypoint and persistence rule | yes |
| `v2/CONSTITUTION.md` | accountable lead | Authority, planes, invariants, lifecycle, definition of closed | yes |
| `v2/MODES.md` | accountable lead | Direct, Fan-out, Mission, Routine selection and rules | yes |
| `v2/RISK-GATES.md` | accountable lead | Tier 0–3, approvals, protected oracles, repair policy | yes |
| `v2/CONTRACTS.md` | accountable lead | Intent, worker, verifier, run, and evidence interfaces | yes |
| `v2/CONTROL-PLANE.md` | accountable lead | Aperture/OMP/durable-runner boundaries | yes |
| `v2/LEARNING.md` | accountable lead | Failure conversion, metrics, evals, calibration | yes |
| `v2/PILOTS.md` | accountable lead | Pilot scorecard and cutover gate | yes |
| `v2/templates/*` | accountable lead | Copyable intent, evidence, and verification templates | yes |
| `v2/pilots/K2-P01-direct/*` | accountable lead | Bootstrap Direct pilot contract and evidence | yes |
| `README.md` | accountable lead | Candidate/v1 routing | yes |
| `CLAUDE.md` | accountable lead | Candidate boundary; v1 remains active | yes |
| `AGENTS.md` | accountable lead | Candidate boundary; v1 remains active | yes |

No write or edit operation targeted `agents/**`, `workflows/**`, `templates/**`, or `~/projects/aperture/**`. This is operation-trace evidence, not a claim that those workspaces contain no unrelated user changes.

## Deterministic gates

Final validation output:

```json
{
  "requiredFiles": "PASS",
  "localLinks": "PASS",
  "modes": "PASS",
  "risks": "PASS",
  "yaml": "PASS",
  "routing": "PASS",
  "overall": "PASS"
}
```

Retrieval output:

```json
{
  "project-context-hook": {
    "exitCode": 0,
    "foundKernelProject": true,
    "foundOrchestrationResearch": true
  },
  "vault-query-hook": {
    "exitCode": 0,
    "mode": "strategic",
    "domain": "agentic-orchestration",
    "foundOrchestrationResearch": true,
    "foundKernelV2Claim": true
  }
}
```

## Real-system exercise

- Interface exercised: installed `project-context-hook` and `vault-query-hook` scripts via JSON stdin.
- Environment: local navi workstation, `~/kernel` working directory.
- Action: queried Kernel project detection and a strategic v2 orchestration decision.
- Resulting state: project hook returned `project="kernel"` plus both canonical research files; vault hook returned strategic `agentic-orchestration` content with the Kernel v2 claim.
- Side effects: project hook updated its normal statusline hint; no runtime or production system was changed.

## Verification

- Verifier: accountable lead deterministic validation; separate verifier not required for Tier 0.
- Context separation: not required; this pilot remains eligible for later sampled audit.
- Verdict: PASS
- Failed or disputed invariant: none after repair.
- Gate weakening detected: no.

## Pilot scorecard

| Metric | Observed |
|---|---|
| Elapsed wall time | unavailable; bootstrap began before run-timer capture |
| PO interventions after approval | 0 |
| Lead steering events | 0 external steering events |
| Workers | 0; Direct mode correctly avoided delegation |
| Model | openai-codex/gpt-5.6-sol |
| Local repair attempts | 1 |
| Expensive retries | 0 |
| Ownership/merge conflicts | 0 |
| Initial deterministic failures | 2 validation findings: directory link check and ambiguous root status phrase |
| Final deterministic failures | 0 |
| Escaped defects observed | 0 as of verification |
| Token/cost data | unavailable in session evidence |

## Repair and escalation history

| Attempt | Failure class | Failed invariant | Action | Outcome |
|---:|---|---|---|---|
| 1 | document graph / routing clarity | Local link validator could not verify a directory target; root status lacked literal `v1 remains authoritative` | Linked the concrete intent template and made v1 authority explicit | Full validation passed |

## Limitations and unresolved items

- This is a bootstrap pilot: the on-disk contract was materialized after the candidate documents began, but before verification. The user-approved intent and research predated implementation.
- Start time and token/cost were not captured. Future control-plane adapters must create the run record before execution.
- Fan-out and Mission remain unvalidated; v2 is not active globally.

## Learning conversion

- Rule: persistent run success and work verification are separate states.
- Contract: run records require `started_at`, model, workspace, attempt, and artifacts.
- Gate: local Markdown targets and YAML templates must parse before methodology closure.
- Eval candidate: topology selection on tightly coupled versus independently parallelizable work.
- Environment improvement: eventual Aperture adapter must allocate run identity and timestamps before launching OMP.

## Final decision

- Work state: verified
- Decided by: accountable lead under Tier 0 policy
- Reason: every bootstrap acceptance claim has deterministic or real-hook evidence; no cutover or production side effect occurred.
