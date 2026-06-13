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
- **2026-06-12 (evening) — APERTURE FREEZE LIFTED for AP-09 + AP-10 only** (PO order): lead messaging console + live next-actions feed. Both serve Loop A directly (PO's only SMS access was Telegram). Freeze remains for everything else. Also: PO phone stored at `~/.secrets/po-phone.txt` — NEVER hardcode it in repo files (agent-infra remote may be public; number is one transposition from a real lead's number — both live only in `~/.secrets`, never in repo files).
- **2026-06-12 — RESUME BORÉAL.** PO ordered resume per ecosystem audit (`audit-2026-06-11/EXECUTIVE_REPORT.md`), superseding the 2026-05-27 "permanently shelved / partner pivot" halt recorded in rules.md. Inbound pipeline restored + verified end-to-end; proactive SMS senders HELD pending PO go/no-go (see `audit-2026-06-11/BOREAL_RESUME_RUNBOOK.md`). Standing flywheel rule adopted: every brief names its loop (A/B); "neither" needs written PO exception. Also: AP-08 cancelled, Aperture frozen at AP-07, brain-* revival gated on a value-case brief, dead ~/projects dirs archived.
- **2026-06-12 (late) — BORÉAL STRATEGIC REORIENTATION (PO order).** Boréal operates as a low-bandwidth, self-qualifying acquisition system optimized for revenue per founder-hour; outreach behaves like advertising (hand-raise CTAs), not cold sales. Canonical doc lives in the private vault (business-sensitive — not in this repo). Consequences here: BX-04 re-scoped before launch; BX-08 (campaign engine) queued behind BX-01-live/BX-02-P2/BX-03; AP-11 written (taskboard truth + NOW noise filter). BX-02 Phase 1 approved with gateway-coordination amendments; AP-10 verified done; BX-01 in review (live send pending quiet-hours window).
- **2026-06-13 — EXECUTOR SILENT-FAILURE ROOT CAUSE FOUND + fix briefed.** PO reported ~8 consecutive Aperture codex jobs silently failing. Two confirmed bugs in `aperture/src/pages/api/launch-codex.ts`: (1) **silent success** — `status: exitCode===0 ? 'done':'failed'`, but `codex exec` exits 0 when the agent merely finishes its turn (incl. "relaunch with permissions"), so blocked runs are stamped done; (2) **wrong sandbox roots** — non-syntra briefs run cwd=agent-infra, `-s workspace-write`, no `--add-dir`, so BX-* writes to ~/scripts / ~/projects/boreal-leads / crm.db / systemctl are all denied. Fix: **AP-12** (derive writable roots from each brief's FILES IT OWNS → `--add-dir`) then **AP-13** (honest completion: parse report for blockers → status `blocked`+reason; allowlisted `restart-after` for the systemd step sandbox forbids; supersedes AP-11 badge half). Both target aperture only, so they run through the currently-working launcher. AP-11 re-scoped to NOW-feed filter only. STRATEGY.md (acquisition-machine vision) integrated into ~/projects/boreal-leads/ + CLAUDE.md so agents read it unprompted.
- **2026-06-13 — Impact.com confirmed for Peak Design + manifest bug briefed.** (1) Peak Design affiliate program runs on Impact.com (10%/30-day cookie, free signup app.impact.com/campaign-promo-signup/Peak-Design.brand); affiliate.config.json wired to status `impact_awaiting_credentials` — serve-time + hot-reloaded, so the param swap needs no re-ingest/redeploy. PO action: join Impact, paste the issued tracking deeplink. (2) S-17 ingest is DECOUPLED from the affiliate decision (stores base URLs) — remaining gate is the prod --write + [DATA] reviewer only. (3) SYS-01 briefed: manifest-update reports false all-stopped when run without the systemd user-bus env (same class as the claude-ops snapshot bug); fix re-derives XDG_RUNTIME_DIR/DBUS + fails honest.
