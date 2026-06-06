# ECOSYSTEM.md — The Full Map

**Date:** 2026-06-05 · **Reviewer:** Architect

Six systems, three layers: **autonomous infrastructure** (Genesis, Realm), **reusable meta-infra** (Agent Infra), and **products** (SYNTRA, Aperture, merulox.com).

---

## The six (one line each, honest)

| System | One-line truth |
|--------|----------------|
| **Genesis** | A persistent autonomous agent (daemon + identity + memory) that runs on a heartbeat and talks via Telegram. Currently frozen/dead (core killed itself Apr 28; runs only when manually started). |
| **Realm** | The state substrate + governance doctrine + monitor that Genesis was built to operate within. ~80% frozen; the monitor is the live, valuable part. |
| **Agent Infra** | The reusable architect/executor/reviewer operating system built *today* (roles, workflows, templates). Clean, new, product-agnostic. |
| **SYNTRA** | A real product: curated-EDC retailer. Engine ingests carry brands → NocoDB + discovery UI; storefront sells the curated shelf. Furthest-along, genuinely working. |
| **Aperture** | A web dashboard (built today) surfacing Genesis/Realm state. Live at aperture.merulox.com. Currently reads stale state files; should read the live monitor. |
| **merulox.com** | The public personal site (Astro/Cloudflare). Live. The honest shop window for everything above. |

---

## Ecosystem diagram

```
                          ┌───────────────────────────────────────────┐
                          │              merulox.com                   │
                          │   (public portfolio — the shop window)     │
                          └───────────────▲───────────────────────────┘
                                          │ represents (honestly)
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 │                                 │
   PRODUCTS                          INTERFACES                        INFRASTRUCTURE
        │                                 │                                 │
┌───────▼────────┐              ┌─────────▼─────────┐            ┌──────────▼───────────┐
│    SYNTRA      │              │     APERTURE      │            │      GENESIS         │
│ curated-EDC    │              │  web dashboard    │  reads ──> │ autonomous agent     │
│ retailer       │              │ aperture.         │            │ (daemon+soul+memory) │
│                │              │ merulox.com       │            │ STATE: frozen/dead   │
│ engine→NocoDB  │              └─────────▲─────────┘            └──────────┬───────────┘
│ →discovery UI  │                        │ should read                    │ operates within
│ →storefront    │                        │ (currently stale)              ▼
└────────────────┘                        │                     ┌──────────────────────┐
                                          └──────────────────── │       REALM          │
                                            live monitor feed    │ state substrate +    │
                                                                 │ doctrine + MONITOR   │
                                                                 │ (monitor = live;     │
                                                                 │  rest = frozen)      │
                                                                 └──────────┬───────────┘
                                                                            │ engine =
                                                                            ▼
                                                          ┌──────────────────────────────┐
                                                          │   ~/scripts/brain-*  (engine) │
                                                          │   brain-bus-router (live)     │
                                                          │   brain-task-executor (live)  │
                                                          └───────────────┬───────────────┘
                                                                          │ uses
                                                                          ▼
                                                          ┌──────────────────────────────┐
                                                          │  Obsidian vault (knowledge)   │
                                                          │  claims / domains / doctrine  │
                                                          └──────────────────────────────┘

   ┌──────────────────────────────────────────────────────────────────────────────────┐
   │  AGENT INFRA  (~/agent-infra)  —  reusable across ALL of the above                 │
   │  roles · workflows · templates · MVAOS · THIS review                              │
   │  Not a runtime; a methodology + document kit. Governs how the others are built.   │
   └──────────────────────────────────────────────────────────────────────────────────┘
```

## How they relate (the load-bearing edges)

- **Genesis runs *within* Realm** — Realm is the environment/state; Genesis is the actor. They are separate (Genesis daemon works without Realm; Realm's monitor watches Genesis). *Not* the same thing.
- **Aperture *observes* Genesis+Realm** — it's a read-only window. Should consume Realm's live monitor; currently reads stale vitals/health files.
- **Realm's engine is `brain-*`** — the scripts in `~/scripts/`, not files in `realm/`. The Obsidian vault is the knowledge memory those scripts feed.
- **Agent Infra governs all of them** — it's the methodology layer (how to build), not a running system. SYNTRA already uses it (`.agent/`, ROLE.md, briefs).
- **merulox.com represents the subset that's presentable** — see WEBSITE_REPRESENTATION.md.

## Maturity at a glance

| System | Exists | In progress | Vision | Net maturity |
|--------|:-----:|:-----------:|:------:|--------------|
| SYNTRA | engine, 280-product catalog, discovery UI, thesis | storefront, affiliate bridge | scale to N brands | **Strongest / shippable** |
| merulox.com | live site, log pipeline | content refresh | — | **Live** |
| Agent Infra | full doc kit (built today) | adoption across projects | — | **New but solid** |
| Aperture | live dashboard (built today) | wire to live data, auto-refresh | ambient voice layer | **MVP live** |
| Genesis | daemon, soul, memory, bridge | revive core, fix self-destruct | ambient co-regulator | **Built but frozen/broken** |
| Realm | monitor (live), doctrine, state | revive or retire | the "empire" | **Mostly archive + 1 gem** |

## The single most important relationship insight

**The chain `Realm.monitor → Aperture → you` is 90% built and 10% wired.** The monitor produces genuinely valuable live intelligence (service health, the Genesis bug ledger); Aperture is a working dashboard; they just aren't connected to each other (Aperture reads stale snapshots). Closing that one gap converts the most valuable frozen asset (the monitor) into a daily-useful product. That is the highest-leverage edge in the whole ecosystem.
