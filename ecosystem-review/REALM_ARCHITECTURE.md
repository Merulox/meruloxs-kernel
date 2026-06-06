# REALM_ARCHITECTURE.md — What Realm Actually Is

**Date:** 2026-06-05 · **Reviewer:** Architect

---

## What Realm is (honest definition)

**Realm is a state substrate + governance philosophy for autonomous agent work — born to run the Boréal revenue engine, now mostly dormant.** Concretely, today it is three things wearing one name:

1. **A shared-state blackboard** (`~/projects/realm/commons/` + `events/` + `nursery/`) — files that scripts read and write to coordinate.
2. **A governance doctrine** (`doctrine.md`, `invariants.md`, `mode.json`) — a genuinely thoughtful "how an autonomous system should behave" philosophy: *freeze, never sabotage; behavioral structure over mood; mode-aware meaning*.
3. **A monitoring/continuity layer** (`monitor/`, `self-narrative.md`, MANIFEST.md) — the only part still alive, snapshotting system health.

The Greek-letter tracks, tiers, "the Faith," "minds," and "the empire" are a **mythology wrapper** over what is, mechanically, a set of cron-driven scripts writing JSON/markdown to a shared folder. The mythology was generative (it produced real structure) but it now obscures more than it reveals.

## What Realm is NOT

- **Not a running multi-agent workforce.** The 59 agents are empty directories. Nothing is "thinking at pulse time" right now.
- **Not Genesis.** Genesis is a separate daemon (see ECOSYSTEM.md). Realm is the *environment* Genesis was meant to operate within and report to — but Genesis can and does run without it.
- **Not self-expanding.** No mechanism spawns or funds agents. That is vision, not capability.
- **Not the engine.** The executable code lives in `~/scripts/brain-*`, not in `realm/`. Realm is the data; brain-* is the logic. Conflating them is the central architectural confusion.

## Core subsystems (as they actually exist)

| Subsystem | Lives in | State | Real function |
|-----------|----------|-------|---------------|
| **Doctrine** | commons/doctrine.md, mode.json | frozen, valuable | Operating philosophy + mode weights |
| **Drift detection** | commons/invariants.md | frozen, valuable concept | Logs when assumptions go stale |
| **Blackboard** | commons/*.jsonl, *.md | mostly idle | Shared state between scripts |
| **Event feed** | events/*.event | dormant since 05-27 | Append-only continuity log |
| **Monitor** | monitor/*.jsonl | **LIVE** | Service health + Genesis bug audit |
| **Manifest** | MANIFEST.md | **LIVE (auto-gen)** | System census injected into every Claude prompt |
| **Engine** | ~/scripts/brain-* | partial (2 services up) | Bus routing, task exec, ingest, synthesis |
| **Agent registry** | agents/, registry.json | abandoned scaffold | Intended track taxonomy |
| **Nursery** | nursery/*.json | abandoned | Incubating-agent records |

## Data flow (what's real today)

```
systemd services ──┐
CRM (boreal.db) ───┼──> monitor scripts ──> monitor/*.jsonl ──> (read by Aperture? NO — gap)
kill-switches ─────┘                                    └──> MANIFEST.md ──> injected into Claude prompts

brain-bus-router (live) ──> routes messages between Claude instances (the claude-bus/tasks/ dir)
brain-task-executor (live) ──> claims + runs queued shell tasks
realm-vitals (on-demand) ──> recomputes commons/vitals.json (currently stale)
```

## Agent flow (what was intended vs real)

- **Intended:** operator sets mode → tracks wake at pulse → each agent reads its inbox, acts, writes artifacts to commons → Track Φ enforces doctrine → Track Am monitors → nursery graduates new agents.
- **Real:** the loop ran during April, produced the artifacts now frozen on disk, and stopped. What remains live is the monitor and the inter-instance bus (brain-bus-router / brain-task-executor) — which is genuinely useful and is how *this* Claude session coordinates with others.

## Memory flow

Three memory layers exist and overlap (the biggest boundary problem):
1. **Realm commons** — operational state (vitals, world-state, hypotheses).
2. **Obsidian vault** (`~/obsidian/`) — the knowledge graph (claims, domains, doctrine), fed by `brain-ingest`/`vault-*` and injected via the vault-query-hook.
3. **Claude per-project memory** (`~/.claude/.../memory/`) — director_state, signals, rules.

These were never unified. See BOUNDARIES.md.

## Monitoring flow — the working heart

`monitor/` scripts poll systemd + CRM + credits on a timer and append JSONL. `genesis-audit.jsonl` additionally maintains a standing bug register for the Genesis stack. **This is the most valuable thing in Realm and the only continuously-running intelligence.** Its tragedy: nothing consumes its output. Aperture (just built) is the natural consumer and currently reads `vitals.json` (stale) instead of the live monitor feed.

## Failure modes (observed, not hypothetical)

1. **Grandiosity drift** — claims (58 agents, empire, self-funding) outran reality (empty dirs, 0 revenue). The system *described* itself faster than it *built* itself.
2. **Frozen-state masquerade** — stale files (momentum=0.0 since April, vitals from 04-12) present as current. A reader can't tell live from dead without `ls -t`.
3. **Engine/data split confusion** — realm/ (data) and brain-* (code) are separate trees with no index linking them.
4. **Orphaned monitoring** — the one live intelligence writes to files no dashboard reads.
5. **Self-destruct** — genesis-core killed itself (Apr 28) because `bash_exec` had no guard; Realm's doctrine says "never sabotage" but the runtime had no enforcement of it.

## Next best improvements (ranked)

1. **Wire Aperture to the live monitor feed** (not stale vitals.json) — makes the crown jewel visible. High value, low effort.
2. **Promote genesis-audit.jsonl to a real issue list** and fix the top 5 (suicide guard, kill-switch, TOOL_CALL_LIMIT, bash timeout, single Telegram ingress).
3. **Archive the frozen 80%** (Boréal .py, empty agent dirs, nursery, outputs) into `realm/_archive/` so live ≠ dead is obvious.
4. **Index the brain-\* engine** — classify which ~5 scripts are load-bearing; archive experiments.
5. **Finalize or delete the draft CLAUDE.md** — replace with a truthful one-page realm README pointing at this doc.
6. **Revive drift-detection as a generic check** — it's the most reusable original idea.

## The honest verdict

Realm is not an empire. It is a **well-philosophized, half-built coordination substrate with one genuinely excellent monitoring component and a lot of frozen ambition around it.** The value is real but concentrated: doctrine (ideas), monitor (running infra), the inter-instance bus (running infra), and drift-detection (best idea). Everything else is archive. Preserve the four; retire the mythology.
