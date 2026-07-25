# Evidence Bundle: K2-AD01 OMP Shadow Adapter

```yaml
schema_version: 2
work_id: K2-AD01
mode: direct
risk_tier: 2
accountable_lead: omp-kernel-v2-adapter
status: verified
started_at: 2026-07-24
finished_at: 2026-07-25
repository: /home/merulox/projects/aperture
model: openai-codex/gpt-5.6-sol
runtime: rootless-podman-pinned-archlinux-omp-17.0.5
independent_oracle: false
canonical_review: /home/merulox/projects/aperture/docs/reviews/AP-33-omp-shadow-adapter-review.md
```

## Acceptance evidence

| Claim | Observer/action | Result | Artifact |
|---|---|---|---|
| Real model-backed isolated execution | Authenticated `/api/launch-omp` proof run | PASS, `succeeded`, exit 0, one allowed change | `~/.local/share/aperture/omp-runs/d323fb22-f49f-4f85-a3bc-cbe16d6191b3.json` |
| Canonical checkout remains unchanged | Canonical proof-path lookup | PASS, absent | Proof run diff retained separately |
| Filesystem isolation | Live Podman mount inspection | PASS, only clone writable; no protected host paths | AP-33 review § Acceptance 5 |
| Gateway-only worker network | Live worker TCP probes | PASS, gateway reachable; `1.1.1.1:443` blocked | AP-33 review § Acceptance 7 |
| Credential indirection | Gateway strict check and worker mounts | PASS for selected OpenAI credential/model; no worker credentials | AP-33 review § Credential health |
| Ownership rejection | Deliberate host boundary mutant | PASS, run failed with typed violation | `~/.local/share/aperture/omp-runs/de7e72e0-dfd3-4d49-8f1a-8ea21e27d2af.json` |
| Immediate cancellation | Launch → duplicate → cancel | PASS, HTTP 202 → 409 → 200, terminal `cancelled` | `~/.local/share/aperture/omp-runs/f19b8b76-9b34-4e0f-ac2a-722731edb7b0.json` |
| Contract and evidence containment | Out-of-root, symlink, traversal, extension, status, duplicate, prior-success checks | PASS, deterministic 4xx/503 | AP-33 review § Negative and boundary responses |
| Build and deployed health | Astro build + three user services | PASS | `artifact://250`, `artifact://267` |
| Desktop and mobile UI | Authenticated Chromium at 1440px and 390px | PASS, no overflow | `~/.local/share/aperture/omp-runs/verification/` |
| Existing production default | `/tasks`, protected launcher diff | PASS | AP-33 review § Acceptance 1 |

## Changed artifacts and ownership

Implementation stayed within the K2-AD01 contract plus lead-owned systemd setup and verifier-owned evidence. `src/pages/api/launch-codex.ts` has no diff. Successful worker changes remain in disposable clones and evidence patches only.

## Repair history

| Attempt | Failure class | Failed invariant | Action | Outcome |
|---|---|---|---|---|
| 1 | environment | Machine freeze interrupted Astro output and left a missing dist manifest | Stop restart loop; run standalone clean build; restart service | PASS |
| 2 | implementation | Listing blocked completed evidence but authoritative POST did not | Share parser evidence check with launch route and include successful run records | PASS |
| 3 | implementation | Immediate cancellation could race container creation/finalization and become worker failure | Add persistent `cancelling` transition and cancellation-aware finalization | PASS |

## Post-action health

- `aperture.service`: active/running/success
- `omp-auth-broker.service`: active/running/success
- `omp-auth-gateway.service`: active/running/success
- Running `aperture-omp-run-*` containers: none
- OpenAI Codex gateway completion probe: healthy
- Anthropic credential refresh: unhealthy and explicitly outside this adapter's model allowlist

## Decision

Verified as an opt-in shadow adapter. No default Kernel v2 or OMP cutover is approved. K2-P02/K2-P03 and explicit Product Owner cutover approval remain mandatory.
