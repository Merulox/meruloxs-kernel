# Decision Log

_One entry per architectural or product decision. Append-only — never edit past decisions.
Mark superseded decisions with `[SUPERSEDED by D-NNN]` at the top._

---

## Template

### D-NNN: [Short title]

- **Date:** YYYY-MM-DD
- **Decided by:** [architect / product owner]
- **Status:** active | superseded | reversed

**Context:** What situation forced this decision?

**Decision:** What was decided, in one sentence.

**Alternatives considered:** What else was evaluated and why it was rejected.

**Consequences:** What this enables, what it forecloses.

---

## Example entries (SYNTRA)

### D-001: Dedupe by source + source_product_id

- **Date:** 2026-06-05
- **Decided by:** architect
- **Status:** active

**Context:** Multiple importers will write to the same NocoDB table. We need a stable dedupe key that works across runs and sources.

**Decision:** Use composite key `source + source_product_id`. Source = the import system (e.g. "orbitkey", "bellroy"). Source Product ID = the stable ID from that system.

**Alternatives considered:** URL-based dedupe — rejected because URLs are not guaranteed stable across regions or variants. Name-based — rejected as too ambiguous.

**Consequences:** Every importer must set both fields. Backfill required for records imported before the fields existed.

---

### D-002: Supplier field for brand identity (no Brand field in v1)

- **Date:** 2026-06-05
- **Decided by:** product owner
- **Status:** active

**Context:** Readiness doc recommended a dedicated Brand field. But NocoDB schema changes require manual intervention, and Supplier already carries brand name for Orbitkey.

**Decision:** Use Supplier = brand name for v1. No new Brand field.

**Alternatives considered:** Add Brand field — deferred; adds migration risk without clear discovery UI benefit for 2-brand v1.

**Consequences:** Supplier serves double duty as brand. Revisit if cross-brand filtering becomes a UX requirement.


---

## Kernel decisions

### D-003: Independent verifier owns executable acceptance oracle

- **Date:** 2026-07-24
- **Decided by:** product owner
- **Status:** active

**Context:** Agent-written implementation and tests can share the same blind spot. The gauntlet needs an oracle that is independent without turning implementation into a black-box guessing game.

**Decision:** Roll out by tiered opt-in pilot. The executor receives the complete public behavioral specification, while an independent verifier owns executable acceptance checks and discloses only the failed public invariant plus a minimal counterexample.

**Alternatives considered:** Architect writes every test — rejected as the throughput ceiling. Executor proposes tests for verifier approval — rejected because implementation framing leaks into the oracle. Fully visible checks — rejected because they invite example overfitting. Fully hidden requirements — rejected because they make legitimate failures opaque.

**Consequences:** Public intent must be complete enough to implement without private checks. Verifier artifacts must be immutable to the executor. Repair feedback needs a structured failed invariant. Kernel-wide enforcement waits for calibrated pilot evidence.

---

### D-004: Hidden oracles require a hard mount boundary

- **Date:** 2026-07-24
- **Decided by:** product owner
- **Status:** active

**Context:** Aperture's current Codex sandbox restricts writes but does not prove that same-user home paths are unreadable. OMP worktrees isolate changes, not reads.

**Decision:** Do not call an oracle hidden unless its storage path is absent from the executor's filesystem namespace. Use explicit-mount container or VM isolation for the pilot; prompt rules and FILES IT OWNS remain defense in depth only.

**Alternatives considered:** Process-hidden same-user files — rejected because the agent can deliberately search for them. Visible checks until later — rejected because the Product Owner chose hard isolation now.

**Consequences:** A rootless Podman spike proved the boundary and a real Codex edit, but production integration requires a dedicated provider-neutral adapter brief, disposable workspaces, credential indirection, pinned toolchains, host-owned evidence, and Kernel v2 pilot approval. The current Aperture launcher remains unchanged.