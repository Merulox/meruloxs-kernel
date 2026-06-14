# AP-19 — Add a Boréal category to the /tasks board

**Loop:** B (SYNTRA/infra compounding — the taskboard is the ops cockpit) · **Priority:** P3 · **Safety:** none (read-only UI)
**Status:** briefed · **Depends on:** AP-12, AP-15 (so launches commit correctly)

## GOAL
On Aperture's `/tasks`, give Boréal (`BX-*`) work its **own panel**, separate from the rest of the ecosystem tasks. Today `BX-*` rows render mixed into the Ecosystem panel; Boréal is now a distinct workstream (its own monorepo, cash loop) and deserves its own section.

## WHY
Boréal is Loop A (cash) and has its own repo + lifecycle; burying its tasks among `AP-*`/`EX-*`/`GX-*` makes it hard to see pipeline state at a glance. No new task file is needed — `BX-*` already live in the ecosystem README; this is purely a **grouping/rendering** change.

## FILES IT OWNS
- `src/lib/tasks.ts` — split the parsed ecosystem rows into two arrays by ID prefix: `borealTasks` = rows whose ID matches `^BX-`, `exTasks` = the rest. Keep all existing fields/logic (status, dependsOn gate, prompt, preview) identical — only partition the output. Expose `borealTasks` wherever `exTasks`/`syntraTasks` are surfaced.
- The taskboard data API (whatever route returns `exTasks`/`syntraTasks` JSON to the client) — add `borealTasks` to the payload.
- `src/components/tasks/BorealPanel.tsx` — new; mirror `ExPanel.tsx` exactly (same props: `tasks`, `jobs`, `launchingTaskId`, `onLaunch`; same launch/escalation/overlay behavior). Heading: "Boréal".
- `src/components/Taskboard.tsx` — render `<BorealPanel ...>` (suggest order: Boréal, Ecosystem, SYNTRA, or place Boréal first since it's the cash loop).

## DO NOT TOUCH
- `getSyntraTasks` / SyntraPanel · the launch-codex pipeline · the ecosystem README content (do NOT move `BX-*` rows out of it — they stay; this is display-only) · task status semantics.

## DONE LOOKS LIKE
1. `npm run build` clean.
2. `/tasks` shows three panels: **Boréal** (all `BX-*`), **Ecosystem** (everything else), **SYNTRA**. No `BX-*` appears under Ecosystem.
3. Launch buttons + dependency gates + job overlay work identically in the new panel (launch a `briefed` BX task to confirm, or confirm a `done` one renders correctly).
4. Counts add up: Boréal panel count + Ecosystem panel count == old Ecosystem count.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
# the API now returns a borealTasks array containing only BX-*:
curl -s localhost:8788/api/<taskboard-route> | python3 -c "import json,sys;d=json.load(sys.stdin);b=d['borealTasks'];e=d['exTasks'];print('boreal:',[t['id'] for t in b]);print('any BX in ex?', [t['id'] for t in e if t['id'].startswith('BX-')])"
```
Expected: `borealTasks` = the BX-* set; no BX-* left in `exTasks`.

## OUT OF SCOPE
- Moving `BX-*` to a separate task file / new canon (not wanted — README stays the source) · finer sub-categories · any change to how tasks are launched or committed.
