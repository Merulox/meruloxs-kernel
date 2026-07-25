# Execution Modes

## Selection algorithm

Choose the least complex mode that satisfies the work:

1. Is the work repeated and mostly deterministic? Use **Routine**.
2. Must it survive unattended across process or machine failures, or span several milestones? Use **Mission**; add a durable runner only when required.
3. Does it contain two or more independent leaves with explicit interfaces and low merge risk? Use **Fan-out**.
4. Otherwise use **Direct**.

Complexity alone does not justify Fan-out. More agents are useful only when work is independently parallelizable or context partitioning outweighs coordination cost.

## Decision matrix

| Property | Direct | Fan-out | Mission | Routine |
|---|---:|---:|---:|---:|
| Sequential/tightly coupled | Best | Avoid | Milestone sequence | If repeated |
| Independent parallel leaves | Optional | Best | Within milestones | Static branches |
| Cross-session | Contract required | Required | Required | Workflow definition |
| Unattended hours/days | Avoid | Limited | Best | Best if deterministic |
| Dynamic decomposition | Lead-local | One wave/DAG | Recursive planner | Avoid |
| Human scope approval | By risk | By risk | Required before start | By side-effect tier |
| Fresh worker contexts | Optional | Required | Required | Per ambiguous node |
| Integration barrier | Final | Final | Every milestone | At state transitions |

## Direct mode

**Use when:** one context can safely own the work and the path is sequential or tightly coupled.

```text
intent → lead researches → lead implements → gates → real-system exercise → evidence
```

Rules:

- The lead owns the task end to end and may edit directly.
- No executor brief or implementation report is required unless the persistence rule applies.
- Read-only scouts or reviewers may assist without changing the mode.
- Independent verification remains risk-triggered.
- If decomposition reveals independent leaves, the lead may promote the task to Fan-out and record why.

## Fan-out mode

**Use when:** at least two leaves can run independently and produce separately verifiable outputs.

```text
lead defines contracts → isolated workers run concurrently
→ typed results or isolated changes → lead integrates → gates → evidence
```

Before spawning, the lead must define for every worker:

- target files, symbols, or research domain;
- exact change or question;
- non-goals and protected areas;
- observable acceptance result;
- output schema;
- merge/apply policy;
- any interface contract shared with siblings.

Rules:

- Use one worker per real leaf; never invent work to increase concurrency.
- Workers start blank and receive all slice-specific requirements.
- Concurrent writers use isolated worktrees.
- The lead owns cross-slice contracts and final integration.
- Peer messages resolve interfaces only; they do not transfer product authority.
- If leaves become coupled, stop parallel execution and downgrade to Direct or sequence them.

## Mission mode

**Use when:** work spans milestones, many context windows, or unattended hours/days.

```text
PO-approved intent → planner creates milestone DAG
→ fresh workers execute leaves
→ validation barrier
→ bounded repair or escalation
→ next milestone → final evidence
```

Rules:

- The planner context owns decomposition, dependencies, resource allocation, and milestone acceptance; it does not implement leaves.
- Each milestone must produce a coherent, runnable state.
- A validation barrier runs before downstream milestones begin.
- Parallelism is permitted only between leaves without hidden shared state.
- The durable control plane records milestone state, run identities, artifacts, and retry counts.
- Expensive repair attempts default to two; further retries require a recorded decision.
- User steering updates the durable contract before descendants act on it.

## Routine mode

**Use when:** a workflow repeats and its state transitions can be expressed deterministically.

```text
trigger → deterministic workflow → agent judgment node when needed
→ guarded side effect → recorded outcome
```

Rules:

- Code owns scheduling, state, retries, idempotency, and known transformations.
- Agents handle ambiguity, synthesis, or open-ended tool use—not plumbing.
- Every side effect has an idempotency or duplicate-suppression strategy.
- Sensitive actions use blocking pre-execution guards.
- systemd is the default local substrate; use a durable workflow engine only when replay, cross-machine survival, or long human interrupts are demonstrated requirements.

## Mode changes

A mode change is allowed when new facts alter task shape. Record:

- old mode and new mode;
- evidence that triggered the change;
- new ownership/dependency boundaries;
- cost or approval consequences;
- whether active workers must stop.

Never change topology merely to rescue an underspecified contract. Fix intent first.
