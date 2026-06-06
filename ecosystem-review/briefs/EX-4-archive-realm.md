# EX-4: Archive Realm's Frozen 80% + Truthful README

Status: ready. Architect 2026-06-05. Read `~/agent-infra/agents/executor.md`.
Doctrine-compliant: **archive, never destroy** (move into `_archive/`, don't `rm`).

## GOAL
Separate Realm's live parts from its frozen bulk by moving dead components into `~/projects/realm/_archive/`, then replace the unapproved-draft `CLAUDE.md` with a truthful 1-page `README.md`.

## WHY
Right now live and dead are indistinguishable; stale files (momentum=0.0, April vitals, empty agents) read as current. Make live ≠ dead legible.

## FILES IT OWNS
- `~/projects/realm/_archive/` (new dir)
- Moves of the dead components (below)
- `~/projects/realm/README.md` (new)
- `~/projects/realm/CLAUDE.md` (delete after README exists)

## DO NOT TOUCH (these are LIVE — leave in place)
- `monitor/` (live telemetry)
- `MANIFEST.md` (auto-generated)
- `commons/doctrine.md`, `commons/invariants.md`, `commons/mode.json` (keep — philosophy/concept)
- `commons/prompt-log.md`, `commons/hook-health.jsonl` (recently written)

## MOVES (into _archive/, preserve subpaths)
1. `_archive/boreal-engine/` ← all root `*.py` (analyze_*, audit_*, p_*, build_*, lead_*, etc.) + `crmstate.json`, `*.csv`, boreal/, builds/, data/, outputs/
2. `_archive/agents/` ← the `agents/track-*` dirs (KEEP `agents/am.md pf.md sl.md te.md` + `registry.json` in place as design history)
3. `_archive/nursery/` ← `nursery/`
4. `_archive/events/` ← `events/`
5. `_archive/commons-stale/` ← `commons/self-narrative.md`, `commons/world-state.md`, `commons/agent-momentum.json`, `commons/vitals.json` (BUT first: copy world-state.md's distinct insights into README "Insights worth keeping" before archiving)

## README.md must contain (truthful)
- What Realm actually is (1 para — cite ECOSYSTEM.md / REALM_ARCHITECTURE.md)
- What's LIVE (monitor, manifest, doctrine, the brain-* engine in ~/scripts)
- What's ARCHIVED and why (frozen April Boréal era)
- Pointer to `~/agent-infra/ecosystem-review/` as the canonical map
- "Insights worth keeping" (mined from world-state.md)
- NO empire/Faith/58-agents language

## DONE LOOKS LIKE
1. `realm/_archive/` holds the 5 groups; `ls ~/projects/realm` shows a clean root (live files + _archive + README)
2. `realm/CLAUDE.md` gone; `realm/README.md` present and truthful
3. monitor/ + doctrine + invariants untouched and still in place
4. Nothing deleted — everything moved (`find _archive -type f | wc -l` is large)

## VERIFY WITH
```bash
ls ~/projects/realm                          # clean root, _archive present, README.md, no CLAUDE.md
test -f ~/projects/realm/monitor/service-health.jsonl && echo "monitor intact"
test -f ~/projects/realm/commons/doctrine.md && echo "doctrine intact"
find ~/projects/realm/_archive -type f | wc -l    # large number
```

## OUT OF SCOPE
- Deleting anything (move only)
- Touching ~/scripts (EX-6)
- The 4 meta-agent files + registry.json (keep in place)
