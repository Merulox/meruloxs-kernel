# Intent Contract: K2-AD01 — Build the OMP Shadow Adapter

```yaml
schema_version: 2
work_id: "K2-AD01"
status: ready
accountable_lead: "omp-kernel-v2-adapter"
mode: direct
risk_tier: 2
repository: "/home/merulox/projects/aperture"
workspace: "/home/merulox/projects/aperture"
depends_on: ["K2-QA01"]
requires: ["po_scope:shadow_adapter"]
selected_model: "openai-codex/gpt-5.6-sol"
independent_oracle: false
allowed_paths:
  - "package.json"
  - "package-lock.json"
  - "deploy/systemd/omp-auth-broker.service"
  - "deploy/systemd/omp-auth-gateway.service"
  - "deploy/systemd/omp-gateway-resolv.conf"
  - "src/lib/nav.ts"
  - "src/lib/omp.ts"
  - "src/components/omp/OmpPanel.tsx"
  - "src/pages/omp.astro"
  - "src/pages/api/omp-intents.ts"
  - "src/pages/api/launch-omp.ts"
  - "src/pages/api/omp-runs.ts"
  - "src/styles/global.css"
  - "docs/planning/AP-33-omp-shadow-adapter.md"
lead_setup_paths:
  - "/home/merulox/.config/systemd/user/omp-auth-broker.service"
  - "/home/merulox/.config/systemd/user/omp-auth-gateway.service"
protected_paths:
  - "src/pages/api/launch-codex.ts"
  - "/home/merulox/.omp/agent/agent.db"
evidence_path: "docs/reviews/AP-33-omp-shadow-adapter-review.md"
```

## Intent

Add an explicitly opt-in OMP execution path to Aperture. It must run agent work in a disposable filesystem namespace, keep credentials behind an auth gateway, persist typed host-owned run evidence, and leave the existing Codex launcher as the production default.

## Why now

Kernel v2 has a verified protected-oracle contract but no runtime adapter. A shadow path is the smallest operational slice that can generate genuine pilot evidence without overriding the unfinished K2-P02/P03 cutover gate.

## Preconditions

- Product Owner selected **Shadow adapter now** on 2026-07-24.
- `K2-QA01` independent review is PASS.
- Rootless Podman can execute OMP and create internal networks.
- Existing Aperture/Codex launch behavior remains production-critical and protected.

## Interfaces and ownership

| Interface/path | Owner | Allowed change |
|---|---|---|
| `/omp` and `/api/omp-*` | lead | Add opt-in shadow UI and API |
| `~/.local/share/aperture/omp-*` | host adapter | Durable runs, disposable clones, broker/gateway state |
| `omp-auth-broker.service` | host adapter | Broker process with isolated credential store |
| `omp-auth-gateway.service` | host adapter | Credential-indirection proxy and network bridge |
| `src/pages/api/launch-codex.ts` | existing Codex path | None |
| Canonical target repository | Product Owner/current workflow | Read-only to shadow runner; no automatic merge |

## Acceptance scenarios

1. **Existing default remains unchanged**
   - Given Aperture before the adapter,
   - when the shadow path is installed,
   - then `/api/launch-codex` remains byte-for-byte unchanged and current task launching still uses it.

2. **Explicit opt-in only**
   - Given the `/omp` page,
   - when no operator presses a launch action,
   - then no OMP worker starts and no canonical repository changes.

3. **Contract allowlist**
   - Given a launch request,
   - when its contract path is outside configured Kernel v2 task roots or the contract is not `status: ready`,
   - then the API returns a deterministic 4xx response and starts no process.

4. **Disposable workspace**
   - Given a valid ready contract,
   - when launched,
   - then the host creates a run-specific full clone and the worker can write only that clone and ephemeral container files.

5. **Protected host filesystem**
   - Given a running worker,
   - then the canonical checkout, Kernel tree, Obsidian vault, home directory, Podman socket, and verifier/oracle storage are absent from its mount namespace.

6. **Credential indirection**
   - Given a running worker,
   - then `agent.db`, OAuth files, refresh tokens, and provider access tokens are not mounted or injected; model calls traverse the dedicated OMP auth gateway.

7. **Limited network**
   - Given a running worker,
   - then it is attached only to an internal Podman network with the gateway as its sole model egress path; direct public-network and arbitrary host-port probes fail.

8. **Typed evidence**
   - Given run lifecycle transitions,
   - then a host-owned JSON record persists run ID, contract identity, runtime identity, clone path, PID, timestamps, status, exit code, session ID, model, allowed-path result, log path, diff path, and failure details without parsing free-form completion prose for success.

9. **Ownership enforcement**
   - Given worker changes after exit,
   - when any changed path falls outside `allowed_paths`,
   - then the run cannot succeed and its record lists the violating paths.

10. **Cancellation**
    - Given a running shadow worker,
    - when the operator cancels it through the API,
    - then only the recorded worker process is terminated and the run becomes `cancelled` with evidence retained.

11. **No automatic promotion**
    - Given a successful shadow run,
    - then its diff is retained for review but never applied, committed, merged, restarted, or deployed automatically.

12. **Real UI and service health**
    - Given the built and restarted Aperture service,
    - when an authenticated browser opens `/omp`,
    - then contracts and run state render at desktop and 390px without overflow, and the original `/tasks` route still loads.

## Negative and abuse cases

- Reject malformed JSON, missing paths, symlink escapes, non-git repositories, duplicate concurrent launches for one contract, and cancellation of unknown/non-running run IDs.
- Fail closed when broker, gateway, Podman network, model configuration, or clone creation is unavailable.
- Never accept a client-supplied repository, model, command, mount, network, or allowed-path override; derive all execution inputs from the host-read contract.

## Evidence required

- Exact build output and active service state.
- Broker/gateway health checks.
- Container mount and network inspection proving absence of protected paths and direct egress.
- One disposable no-write fixture run that reaches the model gateway and produces a typed terminal record.
- Negative launch-path and cancellation responses.
- Browser DOM assertions and screenshots for desktop and 390px.
- Existing `/tasks` and `/api/launch-codex` unchanged/healthy evidence.

## Rollback and containment

- Stop and disable the two OMP auth services.
- Remove the `/omp` nav/page/API additions and adapter module.
- Preserve run/evidence files; remove only disposable clones after review.
- Existing Codex launcher requires no rollback because it must not change.

## Non-goals

- Default execution cutover.
- Automatic merge, commit, restart, deploy, or production side effects.
- K2-P02/K2-P03 completion.
- Protected hidden-oracle execution in the worker container; host-side verifier integration remains a later pilot.
- Broad support for arbitrary contract roots, non-git repositories, Mission/Fan-out orchestration, or remote hosts.

## Clarifications and approved changes

- 2026-07-24 — Product Owner selected an opt-in shadow adapter. Existing Codex remains default until pilot evidence and explicit cutover approval.
