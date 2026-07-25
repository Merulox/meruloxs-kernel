# Control and Execution Boundaries

## Target architecture

```text
Aperture: durable work, approvals, run/evidence visibility
        ↓ provider-neutral run adapter
OMP: lead session, tools, todo, subagents, worktrees, verification
        ↓ only when durability requires it
systemd or Temporal: scheduling, replay, retries, long interrupts
```

Kernel defines the contracts between these systems. It does not duplicate their implementations.

## Pilot authority

During v2 pilots:

- repository intent contracts and evidence bundles are canonical;
- current project task files remain authoritative for v1 work;
- Aperture remains a viewer and Codex launcher;
- an OMP run is started manually from the relevant repository;
- results are recorded in the pilot evidence bundle.

Aperture becomes the v2 canonical control plane only after the exit gate in [PILOTS.md](PILOTS.md) passes and the Product Owner approves cutover.

## Aperture target responsibilities

Aperture should own:

- stable work ID and lifecycle state;
- priority, dependencies, mode, and risk tier;
- missing inputs and approval confirmations;
- active and historical run records;
- evidence and artifact links;
- retry and escalation state;
- service, deploy, and post-deploy visibility.

Aperture should not own:

- model reasoning;
- in-session task decomposition;
- peer messaging;
- worktree mechanics;
- code intelligence;
- verification implementation;
- model-specific report parsing.

## OMP adapter contract

The eventual provider-neutral adapter must:

1. validate that the work item is `ready`;
2. resolve repository, workspace, intent contract, mode, risk, and approval policy;
3. launch a provider-neutral OMP session with the contract as input;
4. preserve OMP's normal tool approvals—never blanket `--auto-approve` consequential work;
5. capture session/run identity and structured output;
6. stream lifecycle events without parsing free-form completion prose;
7. attach artifacts and evidence paths to the run record;
8. distinguish run success from work verification;
9. support cancellation and steering without losing durable state;
10. redact secrets from prompts, logs, and evidence.

For a protected oracle, the same adapter—not a second methodology or runtime—must additionally:

1. create a disposable copy, worktree, container workspace, or VM workspace and prevent the executor from mutating the canonical checkout directly;
2. construct the executor namespace from an explicit mount allowlist and reject undeclared mounts;
3. exclude verifier storage, oracle source/path/content, unrelated repositories, and broad user-home mounts from every executor namespace;
4. launch a pinned runtime identity, such as an image digest plus execution-profile version or an equivalently pinned VM/toolchain profile;
5. resolve credentials through host-side indirection or narrowly scoped ephemeral references, never by copying credential values into contracts or evidence;
6. apply and record an explicit egress policy limited to required endpoints, or record a reviewed exception before execution;
7. keep the oracle reference and verifier-only manifest on the host, wait for executor exit, then invoke the protected oracle host-side against the resulting workspace;
8. capture the contract hash, runtime/profile identity, complete mount manifest, workspace revision, changed files, executor exit, oracle identity/hash, gate output, and structured verdict in host-owned evidence unavailable for worker modification;
9. integrate or expose the disposable result only after blocking host-side gates and the protected oracle pass;
10. prove oracle exclusion from the recorded namespace/mount manifest rather than inferring secrecy from prompts, permissions, file ownership, or worktree location.

Candidate CLI shape, subject to a dedicated adapter brief:

```text
omp -p --mode json --cwd <repo> @<intent-contract>
```

Mode-specific behavior belongs in the contract and OMP agent policy, not in hardcoded provider branches. The protected-oracle requirements specify a future adapter boundary only; they do not authorize implementation or modification of Aperture's production Codex launcher.

## Workspace policy

- Direct mode uses the claimed primary workspace unless an isolated experiment is safer.
- Fan-out and Mission workers use OMP-managed isolated worktrees or dedicated VMs.
- Any run requiring `independent_oracle` overrides those defaults with a disposable workspace and an explicit mount allowlist.
- A worktree isolates writes and integration state, not reads; it cannot by itself protect an oracle.
- Verifier storage must be absent from every executor mount and filesystem namespace. Read-only mounts, file permissions, prompt prohibitions, and write ownership do not satisfy this boundary.
- A worker may write only within its declared ownership boundary.
- The lead integrates worker changes; siblings never merge each other.
- The host owns namespace construction, credentials, egress policy, executor-exit ordering, oracle invocation, and evidence capture.
- Separate top-level sessions continue to use `session-workspace` claims because OMP can isolate only agents it owns.

## Durable-runner threshold

Use systemd when:

- one machine is the intended host;
- the action is repeatable and idempotent;
- restart-from-beginning is acceptable or state is simple;
- normal service supervision is sufficient.

Use Temporal or an equivalent durable engine only when at least one is true:

- a run must resume precisely after process/machine failure;
- work spans days or weeks with expensive completed steps;
- human interrupts must survive deploys/restarts;
- retries, compensation, or cross-machine scheduling are complex;
- observed reliability failures justify the operational dependency.

## Lifecycle reconciliation

The control plane, not an agent transcript, resolves truth after interruption:

1. read durable work state;
2. inspect active run/session state;
3. reconcile workspace and artifact existence;
4. stop runs whose work became ineligible;
5. preserve successful evidence even if verification is pending;
6. requeue only under the bounded repair policy;
7. surface inconsistencies as operator-visible errors.

## Security boundary

- Secrets are referenced by name or host-side indirection, never copied into contracts.
- Workers receive least-privilege credentials and network access.
- Blocking guards run before consequential tools.
- Logs and artifacts redact credentials and personal data.
- Control-plane approval records describe the action, not the secret value.
