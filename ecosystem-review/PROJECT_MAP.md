# PROJECT_MAP.md

**Date:** 2026-06-05 · **Reviewer:** Architect

One record per project. `should_appear_on_merulox_com` and the public/private split feed WEBSITE_REPRESENTATION.md.

---

```yaml
name: SYNTRA
purpose: Curated multi-brand retailer of calm, considered everyday-carry (EDC). A product-intelligence engine ingests premium carry brands into NocoDB + a discovery UI, used as the merchandising tool; the storefront sells the curated shelf via an affiliate bridge (v1).
status: active — strongest project. Engine + 280-product catalog (Bellroy+Orbitkey) + discovery UI working; thesis defined; storefront GTM merged; domain (syntraworks.ca) + fulfillment (affiliate v1) decided.
public_or_private: code private; storefront will be public (syntraworks.ca)
repository: github.com/Merulox/SYNTRA (private)
source_paths: ~/syntra (engine src/, web/, docs/, storefront/, .agent/)
dependencies: NocoDB Cloud, Node, Bellroy/Orbitkey public APIs, (future) Shopify, affiliate programs
contains: ingestion CLIs, normalizer, audit, discovery API+client, full GTM content stack
used_by: (future) syntraworks.ca storefront
should_appear_on_merulox_com: YES — as a flagship build (engine + UI), once storefront is live
public_description: "A curated everyday-carry storefront with a custom product-intelligence engine that ingests and normalizes catalogs from multiple brands."
private_description: Affiliate-bridge economics, NocoDB schema, curation scoring, sourcing strategy
```

```yaml
name: merulox.com
purpose: Public personal site / portfolio. Dark minimal Astro terminal aesthetic. Also hosts the ChatGPT-log digest pipeline.
status: active, live
public_or_private: public
repository: github.com/Merulox/meruloxs-terminal
source_paths: ~/website
dependencies: Astro, Cloudflare Pages, log-ingest-receiver service
contains: site src, Cloudflare Functions, browser extension, data feeds (reading/music/tweets)
used_by: the public; employers; collaborators
should_appear_on_merulox_com: it IS merulox.com
public_description: "Personal site — work, projects, and what I'm building."
private_description: log-digest pipeline internals
```

```yaml
name: Aperture
purpose: Web dashboard surfacing Genesis/Realm operational state (mode, health, pending decisions, vitals). Long-term: the ambient interface layer for Genesis (voice).
status: MVP live (built 2026-06-05) at aperture.merulox.com behind Basic Auth (m/st). Reads state files; not yet wired to the live monitor feed.
public_or_private: private (auth-gated; internal ops view)
repository: ~/projects/aperture (local git, no remote yet)
source_paths: ~/projects/aperture
dependencies: Astro SSR, Node, boreal-webhook cloudflared tunnel, Realm/Genesis state files
contains: SSR dashboard, basic-auth middleware, data readers
used_by: operator (you)
should_appear_on_merulox_com: NO (private ops tool) — but a screenshot could illustrate the Genesis project
public_description: n/a (keep private for now)
private_description: Internal dashboard for the autonomous-agent stack
```

```yaml
name: Genesis
purpose: A persistent autonomous agent with its own identity, memory, and goals; runs as a daemon on a heartbeat, acts via Claude CLI, communicates via Telegram. Aspires to an always-on ambient voice co-regulator.
status: built but frozen/broken — genesis-core killed itself 2026-04-28 (no suicide guard); runs only when manually started. claude-bridge (Telegram) intermittently live. ~25 known bugs logged, unresolved.
public_or_private: PRIVATE — personal, identity-bearing, not for public display
repository: ~/projects/genesis (local git, no remote)
source_paths: ~/projects/genesis; identity in ~/obsidian/knowledge/projects/genesis
dependencies: Claude CLI, systemd, Telegram bot, Kokoro TTS, Obsidian vault
contains: daemon.py, agent.py, telegram-bridge.py, genesis.nix, soul/autobiography/live-state
used_by: operator; Realm monitor watches it
should_appear_on_merulox_com: PARTIAL — concept worth showing as a research project; identity/memory contents must stay private
public_description: "An experiment in a persistent, memory-accumulating personal AI agent."
private_description: soul.md, autobiography, partner-patterns, all conversation memory — never public
```

```yaml
name: Realm
purpose: State substrate + governance doctrine + monitoring for autonomous agent work. Born to run the Boréal revenue engine.
status: ~80% frozen (April Boréal era). Live parts: monitor/, MANIFEST auto-gen, 2 brain services. Most agents are empty scaffolds.
public_or_private: PRIVATE — internal infra, much of it obsolete
repository: none of its own (sits under ~/projects/.git, untracked); should get its own
source_paths: ~/projects/realm; engine in ~/scripts/brain-*
dependencies: brain-* scripts, systemd, Obsidian vault, CRM
contains: doctrine, invariants, commons state, agents scaffold, nursery, events, monitor
used_by: Genesis (as environment), the inter-instance Claude bus
should_appear_on_merulox_com: NO directly — but the MONITOR and the doctrine could anchor a "building autonomous systems" writeup once cleaned
public_description: n/a (mostly archive)
private_description: Internal agent-coordination substrate; mostly historical
```

```yaml
name: Agent Infra
purpose: Reusable architect/executor/reviewer operating system — roles, workflows, templates, the MVAOS minimal kit, and this ecosystem review. A methodology, not a runtime.
status: active, built 2026-06-05; adopted by SYNTRA; clean and current
public_or_private: could be public (it's generic, no secrets) — strong portfolio candidate
repository: ~/agent-infra (local git; no remote yet)
source_paths: ~/agent-infra
dependencies: none (pure docs/markdown)
contains: agents/, workflows/, templates/, project/, mvaos/, ecosystem-review/
used_by: SYNTRA (and intended for all projects)
should_appear_on_merulox_com: YES — as a methodology/writeup ("how I run multi-agent builds")
public_description: "A lightweight operating system for running AI coding agents as a coordinated architect/executor/reviewer team with durable memory."
private_description: which client projects use it
```

---

## Cross-cutting assets (not projects, but mapped for completeness)

```yaml
name: brain-* engine
belongs_to: Realm / Agent Infra (boundary unresolved — see BOUNDARIES.md)
path: ~/scripts/brain-*
status: partial; brain-bus-router + brain-task-executor live
note: The real executable engine. Needs its own inventory + classification.
```

```yaml
name: Obsidian vault (knowledge graph)
path: ~/obsidian
status: active (vault-query-hook injects claims into prompts)
note: The knowledge-memory layer. Feeds Realm/Genesis. Private. Personal.
```
