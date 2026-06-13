# COMPONENTS — Full Inventory (2026-06-11)

Classification legend:
- **ACTIVE** — exists, used, earning its keep
- **DARK** — exists, built, deliberately or accidentally off
- **DUPLICATE** — exists but another component does the same job
- **VISION** — idea only, no meaningful artifact
- **DEAD** — abandoned; consuming nothing but namespace and attention

Verification method noted where it matters. "Verified" = checked live this session.

---

## Revenue layer

| Component | Class | Evidence | Verdict |
|---|---|---|---|
| Boréal pipeline (sms-webhook, missed-call-bot, outreach-batch, close-agent, db-reactivation, follow-up-auto/brief/sequence, calendly-poller, callback-reminder) | **DARK** | All `inactive/dead`, verified via systemctl. claude-ops paused 2026-05-17 19:33, never resumed. | The only near-term revenue path. Decision required: resume or formally kill. Limbo is the worst state. |
| boreal-tunnel | ACTIVE (pointlessly) | Running, but the webhook it fronts is dead | Stop it or restart what it fronts |
| crm.db / boreal.db / crm_lib.py | ACTIVE asset, decaying | 98 responders as of late April; no touches since pause | The single most perishable asset in the ecosystem |
| boreal-site, boreal-leads, boreal-outreach | DARK | Static artifacts, fine at rest | Keep |
| SYNTRA | **ACTIVE** | Live at syntraworks.ca; 593 products audit CLEAN 06-11; verified | Strongest build. Pre-revenue: 0 confirmed affiliate programs (Secrid: none exists; Peak Design: unconfirmed; Bellroy/Orbitkey: unverified), no traffic engine until S-14 ships |
| SYNTRA ingestion engine (probe→normalize→ingest→audit CLIs) | **ACTIVE, compounding** | 4 brands ingested with same pattern | The best engineering asset in the ecosystem — repeatable per brand |
| NocoDB (cloud) + src/nocodb.js + nocodb-audit/verify CLIs | **DUPLICATE/DEAD** | Superseded by Supabase (D-009, 2026-06-06) | Decommission account, archive the CLIs |
| L'Arbitrageur (~/projects/arbitrageur) | VISION | 2 md files, untouched since 04-10 | Correctly deferred per Track D gate (2 clients). Zero attention cost — leave |
| track-c (~/projects/track-c) | DARK | builds + distribution-queue, last touch 05-06 | Dormant Gumroad track. Kill or archive — see DELETE_LIST |

## Public face

| Component | Class | Evidence | Verdict |
|---|---|---|---|
| merulox.com (~/website) | ACTIVE | Live; WEB-01/WEB-02 done; log-digest timer firing nightly | Healthy. 1 unpushed commit |
| log pipeline (log-digest, log-ingest-receiver, chatgpt-log-bridge, twitter-watch) | ACTIVE | Timers verified firing | Healthy, low maintenance |

## Methodology layer

| Component | Class | Evidence | Verdict |
|---|---|---|---|
| agent-infra (roles, workflows, templates, briefs) | ACTIVE | 30 briefs executed through it in 6 days; verification protocol demonstrably catches executor violations (S-15, B-02) | Genuinely working. Stop adding to it — it's done |
| mvaos/ | DUPLICATE | Compact copies of agents/ | Harmless; freeze |
| project/ (CONTEXT/TASKS/DECISIONS for agent-infra itself) | DUPLICATE-ish | Mostly template; real state lives in syntra/.agent and briefs/README | Freeze |
| ecosystem-review/ (06-05 audit + 30 briefs) | ACTIVE | Brief queue is the de-facto task system | Keep; this audit extends it |

## Meta / agent layer

| Component | Class | Evidence | Verdict |
|---|---|---|---|
| Aperture | ACTIVE | Running; AP-01..AP-07 done; 14 unpushed commits | MVP exceeded. **Feature-complete — freeze.** It's a dashboard for watching agents; it watches agents fine |
| AP-08 (Ollama summaries) | VISION | Briefed, not built | Cancel — cosmetic summaries of executor logs |
| Genesis | DARK (semi-active) | genesis-core stopped; but ticks 7502–7546 verified SYNTRA tasks 06-06→06-11, so it runs in some manual/burst mode | Useful as cheap architect-verifier. Resist full revival (voice, ambient, identity work) |
| brain-* engine (53 scripts) | DARK | All units stopped since 06-03; BRAIN_INDEX classifies 18 "load-bearing" — for a runtime that is off | "Load-bearing" is aspirational. Reclassify: load-bearing-if-revived. No revival case exists while revenue is off |
| brain hooks (session-hook, bus-stop-hook, realm-context-hook) | ACTIVE | Fire on every prompt; inject instance_context + ops_state | Working but injecting noise (stale instances, "system halted" rule) — trim |
| Realm | ARCHIVED | EX-4 done; monitor/ + MANIFEST autogen live | Correct end state. Touch nothing |
| commander (telegram-commander, command-center) | ACTIVE | Both running | Keep — this is the right home for a revenue panel (see GAPS) |
| instance bus / claude-sessions | ACTIVE, stale | 5 of 6 registered instances dead 60+ days | One-time cleanup |
| navi (shell daemon) | DARK | Stopped | Personal tool, fine |
| credit-monitor, claude-credits-reminder | **DARK — ironic** | credit-monitor stopped; credits-reminder timer fires daily | Credit exhaustion froze claude-ops, AP-03c, and log-digest — and the monitor for it is off. Restart |

## Knowledge / memory layer

| Component | Class | Evidence | Verdict |
|---|---|---|---|
| Obsidian vault | ACTIVE, compounding | 4,400 notes; injected per-prompt; ingest-queue routes inbox | Crown-jewel knowledge asset. Problem: injection size (~76KB/prompt), not the vault |
| vault-query-hook + obsidian_vault hook | ACTIVE | Verified in this prompt: ~94KB combined injection | Highest-leverage trim available — see BOTTLENECKS B-03 |
| Claude memory (director_state, signals, rules, per-project) | ACTIVE | signals/rules referenced by ops_state hook | Keep; rules.md says "NONE — halted" — that's the pending decision, in file form |
| syntra/.agent | ACTIVE | Canonical, current, verified accurate against live state | The model all projects should copy |
| realm/commons | ARCHIVED | — | Done |

## Substrate

| Component | Class | Evidence | Verdict |
|---|---|---|---|
| NixOS on `navi` | ACTIVE | Single machine | SPOF, mitigated below |
| backup-r2 (restic→Cloudflare R2) | **ACTIVE, healthy** | Snapshot a8dd8214 last night, 96k files / 18.3GiB, exit 0 | The best infra decision made. EX-1 paid off |
| backup-dotfiles | ACTIVE | Timer fired 13h ago | Healthy |
| GitHub repos (scripts, agent-infra, SYNTRA, aperture, genesis, website) | ACTIVE | All 6 have remotes; **30 unpushed commits** (agent-infra 11, aperture 14, syntra 4, website 1) | Push discipline gap — S-10 deploy is hostage to it |
| gitnexus-reindex | ACTIVE | Timer fired 10h ago | Fine |

## Dead weight (~/projects/)

| Component | Last touch | Verdict |
|---|---|---|
| perpetual-optimizer | 04-04 | DEAD — essay drafts + n8n workflow. Archive |
| fb-poster-workflow | 04-09 | DEAD — one orphan workflow.json. Archive |
| track-dialogue | 04-09 | DEAD — log dir only. Delete |
| torzu | 04-17 | DEAD — nix packaging experiment. Delete |
| GhostTrack | 04-27 | DEAD — cloned OSINT tool, never integrated. Delete clone |
| gumroad-thumbnails | 04-28 | DEAD — single PNG. Fold into track-c archive |
| backup/ | 03-23 | DEAD — one research md, superseded by working restic. Archive note to vault, delete dir |
| _template | 03-29 | DEAD — one md. Delete |
| research/ | 04-05 | ARCHIVE — April strategy docs; move to vault inbox if worth keeping |
| compounder | 06-06 | Borderline — script + memory, recently touched. Keep, don't invest |
