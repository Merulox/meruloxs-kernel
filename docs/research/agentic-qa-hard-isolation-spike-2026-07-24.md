---
title: Agentic QA Hard-Isolation Spike
date: 2026-07-24
tags:
  - agentic-qa
  - kernel
  - isolation
  - protected-oracles
source: project-experiment
canonical: ~/kernel/docs/research/agentic-qa-hard-isolation-spike-2026-07-24.md
---

# Agentic QA Hard-Isolation Spike

## Summary

A real Codex worker completed a public-contract task inside a rootless Podman container that mounted only its writable workspace, the read-only Nix runtime, an ephemeral home, and the minimum Codex auth/config files. The verifier-owned oracle and the rest of `~/kernel` were not mounted. A host-side hidden oracle passed the correct implementation and rejected a deliberate boundary mutant with a structured failed invariant.

This establishes a workable hard filesystem boundary for protected checks. It does not yet establish a production runner: image/toolchain lifecycle, credential indirection, egress policy, evidence signing, and Aperture/OMP integration remain unresolved.

## Product Owner decisions

- **Oracle owner:** independent verifier, not the implementation worker.
- **Rollout:** tiered opt-in pilot before kernel-wide enforcement.
- **Visibility:** public behavioral specification; executable checks withheld.
- **Enforcement:** hard isolation now. A same-user convention or “DO NOT TOUCH” path is not enough to call checks hidden.

## Gap found in the current candidate architecture

Kernel v2 correctly requires protected verifier-owned checks for Tier 2 and higher work, but an isolated Git worktree is a write-conflict boundary, not a read-secrecy boundary. The current Aperture Codex launcher also uses Codex `workspace-write`; it limits writes but does not prove that unrelated home paths cannot be read.

Therefore:

> A check is “protected” only when the executor process cannot mount or read its storage path. File ownership rules and prompt instructions are defense in depth, not the boundary.

`v2/PILOTS.md` explicitly prohibits modifying `src/pages/api/launch-codex.ts` during methodology pilots. This spike stayed outside the production launcher.

## Isolation contract proven

### Worker namespace

The successful worker ran with:

- rootless Podman;
- read-only container root filesystem;
- all Linux capabilities dropped;
- `no-new-privileges`;
- ephemeral `tmpfs` for `/tmp` and worker home;
- project workspace mounted read-write at `/workspace`;
- `/nix/store` and `/run/current-system/sw` mounted read-only so the existing Codex and language runtimes remained usable;
- only Codex `auth.json` and `config.toml` exposed read-only through a staging mount and copied into ephemeral home;
- no mount for the private oracle, kernel repository, other projects, or the user's home.

The worker received the complete public contract for a `clamp(value, low, high)` function. It implemented the function and ran cheap local checks. It could write `/workspace`; the same container profile could not resolve the verifier oracle path or `~/kernel`.

### Sandbox authority

Codex's inner `workspace-write` sandbox failed inside rootless Podman because nested Bubblewrap could not create another UID map:

```text
bwrap: setting up uid map: Operation not permitted
```

The successful run used Codex's `--dangerously-bypass-approvals-and-sandbox` **inside** the container. This is acceptable only because Podman was the outer mandatory sandbox. The flag must never be used on the host or in a container with broad host mounts.

### Oracle namespace

After the worker exited, the host control plane invoked a verifier-owned oracle that was never mounted into the worker namespace. The oracle returned machine-readable JSON:

```json
{"checks":["below","above","inside","float-inside","collapsed-range","exact-low-returns-value","exact-high-returns-value","invalid-range"],"count":8,"verdict":"PASS"}
```

A deliberate `value <= low` / `value >= high` boundary mutant returned exit 1 and a structured failed invariant:

```json
{"error_type":"AssertionError","failed_check":"exact low boundary must return value, not low","verdict":"FAIL"}
```

This proves the oracle did more than replay the worker's own examples.

## Target execution sequence

```text
1. Architect + PO freeze public intent contract and risk tier.
2. Independent verifier derives executable oracle in verifier-only storage.
3. Control plane hashes the public contract and oracle manifest.
4. Executor container starts with explicit mounts; oracle storage is absent.
5. Executor writes only the mounted workspace and returns a run record.
6. Container exits; host records revision and changed-artifact identity.
7. Host runs cheap deterministic gates, then the protected oracle.
8. On failure, disclose failed public criterion + minimal counterexample, never oracle source.
9. Allow at most two expensive repair attempts.
10. Independent verifier maps every claim to host-owned evidence and returns PASS / FAIL / ESCALATE.
```

## Required production hardening

1. **Runner ownership:** implement as the future provider-neutral OMP/Aperture adapter, not as a second agent runtime.
2. **Credential indirection:** replace direct `auth.json` exposure with a host-side credential proxy or a narrowly scoped ephemeral credential if the provider supports it.
3. **Egress policy:** the spike allowed normal container networking because Codex requires model access. Restrict egress to required provider endpoints or a host proxy before consequential use.
4. **Image/toolchain policy:** pin an image digest and project toolchain contract; do not depend on an unversioned general-purpose image.
5. **Workspace lifecycle:** use a disposable copy/worktree and integrate only after host-side gates pass. A worker must not directly mutate the canonical checkout.
6. **Host-owned evidence:** capture container spec, image digest, input contract hash, workspace revision, changed files, exit status, gate output, oracle hash, and verdict outside the worker namespace.
7. **Oracle storage:** use a verifier-owned path outside every worker mount. Encrypt-at-rest or filesystem permissions are useful but do not replace mount exclusion.
8. **Failure classes:** distinguish implementation failure, oracle failure, ambiguous requirement, environment failure, and runner failure.
9. **Supply-chain gates:** scan the pinned image and dependencies before treating the runner as a security boundary.
10. **Cutover discipline:** do not alter Aperture's production Codex launch path until Kernel v2 pilot exit criteria and the dedicated adapter brief pass.

## Threat model and limitations

Proven:

- the worker can modify the intended workspace;
- the worker cannot read unmounted host paths through normal filesystem access;
- the private oracle can execute after the worker exits;
- the oracle detects at least one plausible boundary fault;
- a real Codex model call and file edit work inside the outer container.

Not yet proven:

- defense against a container-engine or kernel escape;
- least-privilege model credentials;
- restricted network egress;
- reproducible project-specific toolchain images;
- safe cancellation and timeout behavior;
- tamper-evident evidence storage;
- full OMP or Aperture adapter integration;
- calibration on a real production-shaped task.

## Reproduction evidence

The successful worker invocation used the following container profile. The public task contract was supplied on stdin; credential values were never printed or copied into this note.

```bash
podman run -i --rm \
  --read-only \
  --cap-drop=all \
  --security-opt=no-new-privileges \
  --tmpfs /tmp:rw,nosuid,nodev,size=256m \
  --tmpfs /worker-home:rw,nosuid,nodev,size=512m \
  -v /nix/store:/nix/store:ro \
  -v /run/current-system/sw:/run/current-system/sw:ro \
  -v /home/merulox/tmp/gauntlet-worker:/workspace:rw \
  -v /home/merulox/.codex/auth.json:/worker-config/auth.json:ro \
  -v /home/merulox/.codex/config.toml:/worker-config/config.toml:ro \
  -e HOME=/worker-home \
  -e PATH=/run/current-system/sw/bin:/usr/bin:/bin \
  docker.io/library/archlinux:latest \
  /bin/sh -lc 'mkdir -p /worker-home/.codex &&
    cp /worker-config/auth.json /worker-home/.codex/auth.json &&
    cp /worker-config/config.toml /worker-home/.codex/config.toml &&
    exec /run/current-system/sw/bin/codex exec \
      -C /workspace \
      --skip-git-repo-check \
      --dangerously-bypass-approvals-and-sandbox \
      -o /worker-home/last.md -'
```

The same mount profile returned:

```text
workspace-writable
oracle-unmounted
kernel-unmounted
```

The host-side oracle commands were:

```bash
/home/merulox/tmp/gauntlet-hidden/oracle.py \
  /home/merulox/tmp/gauntlet-worker/calculator.py

/home/merulox/tmp/gauntlet-hidden/oracle.py \
  /home/merulox/tmp/gauntlet-worker/calculator-mutant.py
```

Observed return codes: `0` for the worker and correct candidate, `1` for the deliberate boundary mutant.

## Claims

- A Git worktree isolates writes and merge state, but it does not hide verifier checks from a same-user agent that can read sibling paths.
- Rootless Podman with explicit mounts can make verifier-owned oracle paths genuinely absent from an implementation worker's filesystem namespace.
- Nested Codex Bubblewrap fails in the tested rootless Podman configuration; the outer container can replace it only when mounts, capabilities, privileges, and evidence are controlled by the host.
- Public-spec/hidden-check operation can remain debuggable by revealing the failed public invariant and a minimal counterexample rather than oracle source.
- The current experiment supports a dedicated adapter pilot; it does not justify modifying the production Aperture launcher or claiming the gauntlet is complete.
