# EX-6: Index the brain-* Engine

Status: ready. Architect 2026-06-05. Read `~/agent-infra/agents/executor.md`.
Lowest urgency of the six; do after EX-1 (which versions ~/scripts).

## GOAL
Produce `~/scripts/BRAIN_INDEX.md` classifying every `brain-*` and `realm-*` script as **load-bearing / utility / experiment / dead**, with a one-line purpose each.

## WHY
~40 brain-* scripts with overlapping names (brain-queue / brain-queue-feed / brain-queue-janitor; brain-bus-router / brain-bus-stop-hook) and no index. Two are live services (brain-bus-router, brain-task-executor). No one can tell what's load-bearing vs an abandoned experiment.

## FILES IT OWNS
- `~/scripts/BRAIN_INDEX.md` (new)

## DO NOT TOUCH
- The scripts themselves (classify only — no edits, no deletes)

## METHOD
1. List `~/scripts/brain-* ~/scripts/realm-*`.
2. For each: read the header/usage comment + check if it's a running systemd --user service (cross-ref `systemctl --user list-units 'brain-*' 'realm-*'`) and whether anything references it (grep ~/scripts + ~/projects/realm for the name).
3. Classify:
   - **load-bearing** = a running service OR referenced by a running service/hook (e.g. brain-bus-router, brain-task-executor, manifest hooks)
   - **utility** = useful on-demand tool, referenced/maintained
   - **experiment** = one-off, unreferenced, from the April burst
   - **dead** = broken / superseded / zero references
4. Write the index grouped by classification: `name — classification — one-line purpose — last-modified`.

## DONE LOOKS LIKE
1. `~/scripts/BRAIN_INDEX.md` exists, covers every brain-*/realm-* script
2. The 2 live services are marked load-bearing
3. Each entry has a one-line purpose + classification
4. A short header notes which ~5 are the real spine

## VERIFY WITH
```bash
test -f ~/scripts/BRAIN_INDEX.md && wc -l ~/scripts/BRAIN_INDEX.md
# every brain-* accounted for:
comm -23 <(ls ~/scripts/brain-* | xargs -n1 basename | sort) <(grep -oE 'brain-[a-z-]+' ~/scripts/BRAIN_INDEX.md | sort -u)   # expect empty
```

## OUT OF SCOPE
- Deleting/archiving the "dead" ones (a follow-up decision after the index exists)
- Refactoring any script
