# REALM_INVENTORY.md — Forensic Component Inventory

**Reviewer:** Architect (Claude)
**Date:** 2026-06-05
**Method:** Direct filesystem inspection of `~/projects/realm/` (4,224 files), `~/scripts/brain-*`, `~/scripts/realm-*`, and cross-referenced live service state.
**Scope note:** This is observation, not endorsement. State labels reflect what is *actually true on disk and in systemd*, not what docs claim.

---

## Headline reality check

| Claim (from docs/vitals) | Observed reality |
|--------------------------|------------------|
| "58 agents active / 309 total" (vitals.json) | 59 agent dirs exist; **11 files total across all of them** — they are empty `inbox/` shells. registry.json lists ~40 with metadata. self-narrative peaked at `agents=41`. ambitions.md says "15 agents live". **No two sources agree, and none map to running processes.** |
| "Self-expanding empire where agent output funds more agents" (ambitions A3) | Aspirational. No agent has produced revenue. No agent spawns agents autonomously. |
| "Nursery online, 251 minds" | 290 JSON files in `nursery/`, all dated April. Static records, not running minds. |
| "Event feed active" | Real append-only feed (212 `.event` files) — **last event 2026-05-27** (the freeze date). Dormant. |
| Realm `CLAUDE.md` = "architectural source of truth" | The file is an **unapproved draft** — it literally begins "Waiting for your approval to write..." The approval prompt was saved *as* the constitution. |

**One-line summary:** Realm is ~80% frozen April-era Boréal revenue-engine + governance substrate, ~15% genuinely-running monitor/manifest hooks, ~5% live elsewhere (the `brain-*` scripts). The "empire" framing overstates a system that is mostly dormant state files.

---

## Inventory by component

### Governance / doctrine layer

```yaml
name: doctrine.md
path: ~/projects/realm/commons/doctrine.md
current_state: partial (real content, frozen — last updated 2026-04-10)
type: document
belongs_to: Realm
public_or_private: private
purpose: The realm's "constitution" — Freeze-not-sabotage principle, behavioral-layer philosophy, mode awareness
actual_behavior: Static reference doc; genuinely well-written governance philosophy
claimed_behavior: "Track Φ enforces it, Track Ψ optimizes it" — no such enforcement runs
dependencies: mode.json
value: HIGH — the clearest articulation of the operating philosophy; reusable
risks: Claims enforcement that doesn't exist
recommendation: keep + clarify (mark as philosophy, not active enforcement)
```

```yaml
name: invariants.md (drift log)
path: ~/projects/realm/commons/invariants.md
current_state: partial (frozen after 2026-04-12)
type: system (append-only drift detector output)
belongs_to: Realm
purpose: Logs when system assumptions drift from reality (e.g. stale response baselines)
actual_behavior: Real drift entries Apr 10–12, then stops
claimed_behavior: Continuous drift detection
value: HIGH concept (drift detection is a genuine compounding mechanism), LOW current
recommendation: keep concept, expand (this is one of the best ideas; revive as a generic check)
```

```yaml
name: CLAUDE.md (realm)
path: ~/projects/realm/CLAUDE.md
current_state: unclear — it is an unapproved draft saved verbatim
type: document
belongs_to: Realm
value: MEDIUM (the intended content is a decent index)
risks: It is NOT a finalized constitution; reads as one but never was
recommendation: rewrite (finalize it honestly, or delete and replace with REALM_ARCHITECTURE.md)
```

```yaml
name: ambitions.md
path: ~/projects/realm/ambitions.md
current_state: partial (frozen ~April; A1/A2 are obsolete Boréal goals)
type: document
purpose: Register of high-signal ambitions (A1 first client, A2 $3-10k Boréal, A3 the empire)
value: MEDIUM (historical intent record)
risks: A1/A2 reference dead Boréal pivot; reads as current
recommendation: archive Boréal entries, keep as historical
```

### State / commons layer (`~/projects/realm/commons/`)

```yaml
name: commons/ (shared state)
path: ~/projects/realm/commons/
current_state: partial — ~30 state files; most frozen April, a few hook-written recently
type: system (shared blackboard)
belongs_to: Realm
contains: vitals.json, agent-momentum.json (all 0.0, stale), world-state.md, self-narrative.md,
  build-queue.jsonl, forge-queue.jsonl, doctrine.md, invariants.md, failpoints.md, hypotheses.md,
  evidence-trail.jsonl, gap-log.md, prompt-log.md (recent), hook-health.jsonl (recent)
actual_behavior: A blackboard several scripts read/write; mostly idle
value: MEDIUM — the pattern (shared state dir) is sound; the contents are mostly stale
recommendation: keep structure, archive stale, keep the 2 live files (prompt-log, hook-health)
```

```yaml
name: self-narrative.md
path: ~/projects/realm/commons/self-narrative.md
current_state: abandoned (frozen April 10–12)
type: system (continuity time-series — agents/tracks/nursery/doctrine-hash every 10 min)
value: MEDIUM concept (system self-awareness snapshots), LOW current
recommendation: keep concept, archive data
```

```yaml
name: world-state.md
path: ~/projects/realm/commons/world-state.md
current_state: abandoned (April)
type: system (accumulated world-model hypotheses, e.g. "Quebec contractors decide 5–7am")
value: MEDIUM — genuine insight accumulation; some insights still useful for any outreach
recommendation: mine for insights, then archive
```

### Agent registry layer

```yaml
name: agents/ (59 track dirs + 4 meta-agents)
path: ~/projects/realm/agents/
current_state: abandoned scaffold — 59 dirs, 11 files total, mostly empty inboxes
type: system (intended agent registry)
belongs_to: Realm
actual_behavior: am.md/pf.md/sl.md/te.md are real definitions (Signal-Forge era);
  the track-* dirs are empty placeholders
claimed_behavior: "58 agents active across tiers"
value: LOW (the 4 meta-agent defs are MEDIUM as design artifacts)
risks: The single largest grandiosity gap — implies a workforce that does not exist
recommendation: archive the empty dirs; keep am/pf/sl/te + registry.json as design history
```

```yaml
name: registry.json
path: ~/projects/realm/registry.json
current_state: abandoned (updated 2026-04-13)
type: document (agent registry with tier/drive/birth)
value: MEDIUM (clean record of the intended agent taxonomy)
recommendation: archive
```

### Nursery / events layer

```yaml
name: nursery/
path: ~/projects/realm/nursery/
current_state: abandoned (290 JSON "mind" records, April)
type: archive
purpose: Staging area for proposed/incubating agents ("minds")
value: LOW — static records of an idea-generation burst
recommendation: archive
```

```yaml
name: events/
path: ~/projects/realm/events/
current_state: abandoned (212 .event files; last 2026-05-27)
type: system (append-only event feed: sms_reply, telegram_msg)
value: MEDIUM concept (event sourcing for continuity), LOW current
recommendation: keep concept, archive data
```

### Monitoring layer — THE LIVE PART

```yaml
name: monitor/ (genesis-audit + service-health)
path: ~/projects/realm/monitor/
current_state: ACTIVE — service-health.jsonl + data-integrity-report.jsonl written 2026-06-05
type: system
belongs_to: Realm (but really serves Genesis + the whole stack)
actual_behavior: Periodically snapshots systemd service states, CRM summary, kill-switch
  states, credit burn, and a standing bug register
claimed_behavior: matches — this one actually does what it says
value: HIGH — genuinely useful, still running, and it caught real failures
  (genesis-core dead since Apr 28, no suicide guard, TOOL_CALL_LIMIT=3, no kill switch)
risks: Its findings are ignored — ~25 flagged bugs sit unresolved
recommendation: keep + expand + ACT ON ITS OUTPUT. This is the crown jewel of Realm.
```

```yaml
name: genesis-audit.jsonl
path: ~/projects/realm/monitor/genesis-audit.jsonl
current_state: ACTIVE (last 2026-06-03)
type: system (automated engineering audit of the Genesis stack)
value: HIGH — a real, specific, actionable bug ledger (B1–B8, M1–M5, V1–V10, A1–A5, R1–R2)
recommendation: promote to a tracked issue list; it is doing real work no one reads
```

### Engine layer (NOT in realm/ — in ~/scripts/)

```yaml
name: brain-* script suite
path: ~/scripts/brain-* (~40 scripts)
current_state: partial — 2 services live (brain-bus-router, brain-task-executor), rest on-demand
type: system (the executable engine behind realm state)
belongs_to: Realm / Agent Infra (boundary unclear — see BOUNDARIES.md)
actual_behavior: bus routing, task execution, ingest, synthesis, audit, queue management
value: HIGH — this is the actual working code; realm/ is just its data
risks: Undocumented sprawl; ~40 scripts with overlapping names (brain-queue vs brain-queue-feed
  vs brain-queue-janitor); no single index of what's load-bearing vs experimental
recommendation: inventory + classify (which 5 are load-bearing? archive the rest)
```

```yaml
name: realm-* scripts
path: ~/scripts/realm-session, realm-vitals, realm-dialogue, realm-context-hook, realm_context.py
current_state: partial
type: script
value: MEDIUM (realm-session = tmux launcher; realm-vitals = the metric refresher)
recommendation: keep realm-session + realm-vitals; review the rest
```

### Boréal revenue-engine corpus (the bulk of realm/ root)

```yaml
name: analyze_*/audit_*/p_*/build_*/lead_* python scripts (~65 .py)
path: ~/projects/realm/*.py
current_state: abandoned (Boréal SMS reply analysis, all April)
type: archive
belongs_to: Realm (Boréal era) — superseded by the SYNTRA pivot
purpose: One-off analyses of SMS reply patterns, desperation signals, CRM state for Boréal lead-gen
value: LOW going forward (Boréal is halted); MEDIUM as technique reference
risks: Clutters realm root; obscures what's current
recommendation: archive wholesale into realm/_archive/boreal-engine/
```

### Outputs

```yaml
name: outputs/
path: ~/projects/realm/outputs/ (15MB, largest dir)
current_state: abandoned (April build artifacts)
type: archive
value: LOW
recommendation: archive or delete after a spot-check for anything unique
```

---

## Summary counts

| State | Components | Note |
|-------|-----------|------|
| **Active** | monitor/, manifest auto-gen, 2 brain services, prompt-log/hook-health | The genuinely-running ~5% |
| **Partial** | doctrine, invariants, commons, brain-* suite, realm scripts | Real but mostly idle |
| **Abandoned** | agents/, nursery/, events/, Boréal .py corpus, outputs/, registry | The frozen April bulk |
| **Unclear/draft** | realm CLAUDE.md (unapproved draft) | Needs finalizing |

**Hidden gems (preserve at all costs):** the monitor/genesis-audit system, the drift-detection (invariants) concept, the doctrine philosophy, and the world-state insight accumulator. These are the four ideas worth carrying forward.
