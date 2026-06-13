# SYSTEM MAP — 2026-06-11 Forensic Audit

**Supersedes** `~/agent-infra/SYSTEM_MAP.md` (2026-06-05). All statuses verified live this session (systemctl, git, journalctl) — not inferred from docs.

---

## The ecosystem, by what it does for you

```
MONEY (the point)
├── Boréal Numérique      ⛔ DARK — all 12+ pipeline services stopped since claude-ops
│   ├── sms-webhook, missed-call-bot, outreach-batch,      pause 2026-05-17 (25 days).
│   │   close-agent, db-reactivation, follow-up-*,         boreal-tunnel still running
│   │   calendly-poller, callback-reminder                 (pointing at nothing).
│   ├── crm.db (98 warm responders, decaying daily)
│   └── boreal-site, boreal-leads, boreal-outreach
├── SYNTRA                 🟢 LIVE at syntraworks.ca — 593 products, 0 confirmed
│   ├── Supabase catalog (593 rows, audit CLEAN 06-11)     affiliate programs, no
│   ├── ingestion engine (probe→normalize→ingest→audit)    traffic strategy yet.
│   └── S-10 routing: committed, NOT deployed (PO push)    Pre-revenue.
└── L'Arbitrageur          💭 VISION — 2 markdown files, correctly deferred

PUBLIC FACE
└── merulox.com            🟢 LIVE — log-digest + twitter-watch pipelines working

METHODOLOGY
└── agent-infra            🟢 ACTIVE — architect/executor/reviewer OS; used daily;
                              11 unpushed commits, dirty tree

META / AGENT LAYER (the attention sink)
├── Aperture               🟢 RUNNING — heaviest June investment (AP-01..08:
│                             React SPA, SSE, dep gates, escalation widget);
│                             14 unpushed commits
├── Genesis                🟡 FROZEN-ISH — GX-01..07 done; ran architect ticks
│                             7502–7546 (verified SYNTRA tasks 06-06→06-11);
│                             genesis-core service stopped now
├── brain-* engine         ⛔ ALL STOPPED since 2026-06-03 audit disable —
│                             53 scripts; hooks (session/bus-stop/realm-context)
│                             still firing on every prompt
├── Realm                  🗄️ 80% ARCHIVED (EX-4 done); monitor/ + MANIFEST
│                             autogen live
├── commander              🟢 telegram-commander + command-center running
└── instance bus           🟡 Hooks active; registry stale (5 of 6 instances
                              dead 60+ days, flagged "safe to close")

KNOWLEDGE / MEMORY (6+ overlapping layers)
├── Obsidian vault         🟢 4,400 notes, 113MB — injected into EVERY prompt (~76KB)
├── Claude memory dirs     🟢 director_state, signals, rules, per-project memory
├── syntra/.agent          🟢 canonical project memory — works well
├── agent-infra/project    🟡 mostly template scaffolding
├── realm/commons          🗄️ archived/stale
└── NocoDB                 ⚰️ superseded by Supabase (D-009) — not yet decommissioned

SUBSTRATE
├── NixOS (navi)           🟢 single machine — SPOF for everything
├── backup-r2 (restic→R2)  🟢 HEALTHY — nightly, snapshot a8dd8214 today, 18.3GiB
├── backup-dotfiles        🟢 nightly timer firing
├── GitHub repos           🟡 all 6 have remotes; 30 commits unpushed across 4 repos
└── claude-ops             ⛔ PAUSED since 2026-05-17 19:33 — 29 units tracked;
                              this is THE switch that turned the economy off

DEAD WEIGHT (~/projects/)
└── perpetual-optimizer, fb-poster-workflow, GhostTrack, torzu,
    track-dialogue, gumroad-thumbnails, _template, backup/ — all
    untouched since March–April. See DELETE_LIST.md
```

---

## The one structural fact that matters

Engineering output June 5–11 (from git logs + brief queue): **~30 briefs executed**, of which **~24 were meta-layer** (Aperture, Genesis prompts, repo hygiene, log pipeline) and **~6 were product** (SYNTRA ingestion/routing). **Zero touched the revenue pipeline**, which has been off the entire time.

The system is excellent at building the machine that watches the machine. The machine that makes money is unplugged.

## Read order for this audit

COMPONENTS → DEPENDENCY_GRAPH → BOTTLENECKS → COMPOUNDING → GAPS → BUILD_QUEUE → DELETE_LIST → FLYWHEEL → **EXECUTIVE_REPORT** (the verdict).
