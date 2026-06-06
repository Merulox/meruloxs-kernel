# BOUNDARIES.md — What Each Thing Is and Is Not

**Date:** 2026-06-05 · **Reviewer:** Architect

Purpose: resolve the overlaps. Where two things do the same job, this file rules.

---

## Direct boundary answers (the questions posed)

**What is Genesis?**
A persistent autonomous *agent* — an actor with identity, memory, goals, a daemon, and a voice. The "who."

**What is Realm?**
The *environment* that agent operates in — shared state, governance doctrine, monitoring. The "where/rules." Realm is a place; Genesis is an inhabitant.

**What is Aperture?**
An *interface* — a read-only web window onto Genesis/Realm state. Not infrastructure, not an agent. The "view."

**What is Agent Infra?**
A *methodology* — the architect/executor/reviewer operating system and its document templates. Not a runtime. The "how we build." Reusable across everything.

**What is SYNTRA?**
A *product* — a curated-EDC retail business with a custom ingestion engine. The "what we sell." Unrelated to the agent infrastructure except that it's *built using* Agent Infra.

**What is merulox.com?**
The *public surface* — the portfolio/shop window. The "what others see."

**Is Realm separate from Genesis, or part of Genesis?**
**Separate.** Genesis runs without Realm; Realm's monitor watches Genesis. They were co-developed and the docs blur them, but mechanically they are distinct: Genesis = `~/projects/genesis` daemon; Realm = `~/projects/realm` state + `~/scripts/brain-*` engine. *Rule: Genesis is an agent that uses Realm; Realm is not Genesis.*

**Is Aperture a project, interface, dashboard, or website section?**
A **dashboard/interface**, deployed as its own small web app (aperture.merulox.com). It is its own project repo but its *role* is "interface to Genesis/Realm," not a standalone product. Not a section of merulox.com (different audience: private ops vs public portfolio).

**Is Agent Infra part of Realm, or reusable across everything?**
**Reusable across everything, and separate from Realm.** Realm is runtime state for autonomous agents; Agent Infra is a build methodology for *any* project (it governs SYNTRA, which has nothing to do with Realm). *Rule: Agent Infra is the meta-layer above all projects; Realm is one specific (mostly-dormant) runtime.*

**Should monitoring belong to Realm, Aperture, or Agent Infra?**
**Realm owns the monitoring *producers* (the polling scripts → JSONL feeds). Aperture is the *consumer* (renders them).** Agent Infra defines the *methodology* (verify live state) but does not run monitors. *Rule: Realm produces telemetry, Aperture displays it, Agent Infra prescribes the discipline.*

**Which systems are private infrastructure?**
Genesis, Realm, Aperture, the brain-* engine, the Obsidian vault. All private.

**Which should be public portfolio projects?**
SYNTRA (once storefront live), Agent Infra (as methodology), merulox.com (is public). Genesis as a *concept writeup* only.

**Which should not be shown publicly yet?**
Aperture (auth-gated ops tool), Realm internals (mostly obsolete + would read as grandiose), Genesis identity/memory (personal), the brain-* sprawl (undocumented).

---

## Overlap resolutions (where things collide)

### Overlap 1 — Three "memory/brain" layers
**Collision:** Realm commons, Obsidian vault, and Claude per-project memory all store "memory."
**Resolution:**
- **Obsidian vault** = durable *knowledge* (claims, doctrine, domains). The long-term brain.
- **Realm commons** = ephemeral *operational state* (vitals, queues, world-state). The working memory.
- **Claude `.claude/.../memory`** = per-session *continuity* (signals, rules, director state). The scratch memory.
- *Rule: knowledge → vault; live ops state → realm commons; session continuity → claude memory.* Stop cross-writing.

### Overlap 2 — Realm (data) vs brain-* (code)
**Collision:** "Realm" colloquially means both the `realm/` folder and the `brain-*` scripts.
**Resolution:** Rename mentally and in docs: **Realm = the state substrate** (`~/projects/realm/`); **the engine = `brain-*`** (`~/scripts/`). They are two halves of one system but must be referred to distinctly. The engine should get an index (`~/scripts/BRAIN_INDEX.md`).

### Overlap 3 — Monitoring ownership
**Collision:** monitor/ lives in realm/ but serves Genesis and the whole stack.
**Resolution:** Monitoring *producers* stay in Realm (they're system-wide telemetry). Aperture consumes. Do not duplicate monitors in Aperture.

### Overlap 4 — Agent Infra vs Realm agent definitions
**Collision:** Both define "agents" (Agent Infra has architect/executor/reviewer; Realm has 59 track agents).
**Resolution:** Different meanings of "agent." Agent Infra = *roles a Claude/Codex session plays* (methodology). Realm tracks = *autonomous cron-driven workers* (runtime). Keep them separate; Realm's empty agent scaffolds should be archived so the word "agent" isn't overloaded by dead dirs.

### Overlap 5 — Aperture vs merulox.com
**Collision:** both are web properties on the merulox.com domain.
**Resolution:** merulox.com (apex) = public portfolio (Cloudflare Pages). aperture.merulox.com (subdomain) = private ops dashboard (tunnel). Same domain, opposite audiences, never merge.

### Overlap 6 — Two "Syntra"s (already resolved)
**Status:** Resolved 2026-06-05 (D-003). The Genesis storefront merged into `~/syntra/storefront/`. No remaining collision. Noted here so it doesn't recur.

---

## The clean mental model (carry this)

```
METHODOLOGY:  Agent Infra        — how we build (governs all)
PRODUCT:      SYNTRA             — what we sell
PUBLIC FACE:  merulox.com        — what others see
─────────────────────────────────────────────────────────────
AGENT:        Genesis            — the autonomous actor
ENVIRONMENT:  Realm (state) + brain-* (engine) — where it runs
INTERFACE:    Aperture           — the window onto it
KNOWLEDGE:    Obsidian vault     — the long-term brain
```

If a new file/idea doesn't clearly belong to one of these eight, that's a signal to stop and place it before building.
