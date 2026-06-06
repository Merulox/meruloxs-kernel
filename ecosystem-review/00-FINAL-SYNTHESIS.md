# 00 — FINAL SYNTHESIS

**Realm Forensic Architecture Review · 2026-06-05 · Architect**

Read order: this file → ECOSYSTEM → BOUNDARIES → REALM_INVENTORY → REALM_ARCHITECTURE → PROJECT_MAP → ARCHITECTURAL_CRITIQUE → WEBSITE_REPRESENTATION → REPOSITORY_STRATEGY.

---

## 1. The recommended final architecture

Eight clean roles, one mental model:

```
METHODOLOGY:  Agent Infra      — how everything is built (governs all)
PRODUCT:      SYNTRA           — the shippable business (curated EDC retail)
PUBLIC FACE:  merulox.com      — the honest portfolio
─────────────────────────────────────────────────────────────────────
AGENT:        Genesis          — the autonomous actor (code public-able, memory never)
ENVIRONMENT:  Realm + brain-*  — state substrate (mostly archive) + engine (live, unbacked)
INTERFACE:    Aperture         — the window onto Genesis/Realm
KNOWLEDGE:    Obsidian vault    — long-term brain (private)
TELEMETRY:    Realm/monitor    — the crown jewel; produce in Realm, display in Aperture
```

The strategic move is **subtraction + wiring, not building**: archive the frozen 80% of Realm, back up the engine, connect the live monitor to Aperture, fix Genesis's safety gaps, and let SYNTRA ship. The ecosystem's problem was never too few ideas — it was unfinished scaffolding burying excellent ones.

## 2. The exact files that should exist

**Keep / finalize:**
- `agent-infra/ecosystem-review/*` (these 9 docs) — the canonical map
- `realm/commons/doctrine.md`, `invariants.md` — preserve (mark as philosophy/concept)
- `realm/monitor/*` — keep + expand (the live telemetry)
- `~/scripts/BRAIN_INDEX.md` — **create** (classify the ~40 brain-* scripts)
- `realm/README.md` — **create** (truthful 1-page; replaces the draft CLAUDE.md)
- SYNTRA `storefront/brand/positioning.md` — already canonical

**Archive (move, don't delete):**
- `realm/_archive/boreal-engine/` ← the ~65 Boréal `.py` scripts
- `realm/_archive/agents/` ← the 59 empty agent dirs
- `realm/_archive/nursery/`, `realm/_archive/events/`, `realm/_archive/outputs/`
- stale `commons/*` (momentum, vitals-as-of-April, self-narrative, world-state) → `_archive/` after mining world-state for insights

**Delete:**
- `realm/CLAUDE.md` (the unapproved-draft constitution) — replace with realm/README.md
- nothing else; preserve by archiving, per doctrine ("never destroy")

## 3. The exact repos that should exist

| Repo | Visibility | Action |
|------|-----------|--------|
| `Merulox/SYNTRA` | private | exists — push pending commits |
| `Merulox/meruloxs-terminal` (merulox.com) | public | exists |
| `Merulox/agent-infra` | **public** | create remote + push |
| `Merulox/aperture` | **private** | create remote + push |
| `Merulox/genesis` | **private** | create remote + push (memory excluded via .gitignore) |
| `Merulox/scripts` | **private** | **create + push — backs up the unversioned engine (highest priority)** |
| realm | — | no repo; archive in place (optional private `realm-archive` snapshot) |

## 4. What should be public now

- **merulox.com** (is public).
- **agent-infra** (pure methodology, no secrets) — strong portfolio piece.
- **SYNTRA** — public-facing storefront when it launches; repo stays private.
- **Genesis as a *concept*** (architecture diagram + the monitoring idea) — writeup only, not the repo, not the memory.

## 5. What should remain private

- Genesis code (private repo) and Genesis **memory/identity** (no repo at all — encrypted backup only).
- Aperture (auth-gated ops tool).
- Realm internals (obsolete + grandiose framing).
- brain-* engine / `~/scripts` (private repo).
- Obsidian vault, CRM, leads, `.env`/tokens.

## 6. What the Executor should do next (after this review is approved)

In priority order — each is a self-contained brief:

1. **EX-1 (Back up the engine):** `git init ~/scripts`, create private `Merulox/scripts`, push. Verify `genesis-memory-backup` + `backup-r2`/`rclone-backup` actually run; if stopped, restart + confirm. *(Prevents catastrophic loss.)*
2. **EX-2 (Push the new repos):** create remotes + push `agent-infra` (public), `aperture` (private), `genesis` (private). **Gate:** verify each `.gitignore` excludes `.env`, tokens, and all `~/obsidian` / genesis-memory paths *before* first push.
3. **EX-3 (Wire Aperture to live telemetry):** point `aperture/src/lib/data.ts` at `realm/monitor/*.jsonl` (service-health, genesis-audit) instead of stale `commons/vitals.json`; add the bug-ledger as a dashboard section. *(Activates the crown jewel.)*
4. **EX-4 (Archive Realm's dead 80%):** move Boréal `.py`, empty `agents/`, `nursery/`, `events/`, `outputs/`, stale commons → `realm/_archive/`; write truthful `realm/README.md`; delete draft `CLAUDE.md`. *(Doctrine-compliant: archive, never destroy.)*
5. **EX-5 (Genesis safety — do before any revival):** implement the 4 audit fixes — bash_exec service blacklist (suicide guard, A3), hard kill-switch (A4), raise TOOL_CALL_LIMIT (B3), raise bash timeout (B4). Source of truth: `realm/monitor/genesis-audit.jsonl`.
6. **EX-6 (Index the engine):** write `~/scripts/BRAIN_INDEX.md` classifying brain-* as load-bearing / utility / experiment / dead.

**Architect (not executor) retains:** the revive-or-retire decision on Genesis/Realm (a strategic fork, not a build task), and approval of each brief before execution.

---

## The one-sentence verdict

You built a system that *describes* an empire and *contains* four genuinely excellent ideas (the monitor, drift-detection, the doctrine, the architect/executor/reviewer method) plus one shippable business (SYNTRA) — buried under unfinished scaffolding; the path forward is to **subtract the scaffolding, back up and wire the real parts, and ship.**

---

## DECISION LOG (post-review)

- **2026-06-05 — REVIVE, not retire.** PO chose to keep Genesis/Realm alive. Consequence: EX-5 (Genesis safety gates) is a hard prerequisite — genesis-core stays down until the suicide guard + kill-switch land. Executor briefs written: `briefs/EX-1…EX-6`.
