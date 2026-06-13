# AP-11 — NOW feed: filter dead/declined leads out of the urgent bucket

**Loop:** A (panel signal quality)
**Priority:** P2 · **Safety:** read-only sources; the UI never writes anything
**Status:** briefed · **Depends on:** none
**RE-SCOPED 2026-06-13:** the job-aware-badge half of this brief moved to **AP-13** (it belongs with the job-status-honesty fix, since badges derive from job status). This brief is now ONLY the NOW-feed noise filter.

## GOAL
The NOW feed's `now` bucket contains only live, actionable lead threads — dead, STOP, and stale (60+ day) replies stop drowning the 2–3 that matter.

## WHY
AP-10's unanswered-leads collector surfaces 60-day-old polite declines ("pas intéressé, bonne journée") as `urgency: now` — 47 noise items burying the genuinely live ones (A.S Électrique). That's the opposite of the panel's purpose: it should make the next real action obvious at a glance.

## FILES IT OWNS
- `~/projects/aperture/src/lib/actions.ts` (collector 1 — unanswered-leads — filter only)
- `~/projects/aperture/src/components/now/*` (the "show filtered" toggle, if needed)

## DO NOT TOUCH
- Job/badge logic (AP-13 owns it), tasks.ts, Taskboard.tsx
- Other collectors, ranking, the active-rule banner
- briefs/README.md and all status sources

## SPEC
Unanswered-leads collector excludes a lead from the `now` bucket when ANY of: lead `stage`/`stage_v2` ∈ (STOP, DEAD); latest inbound `classification` ∈ (STOP, BOUNCE); inbound older than 14 days. Excluded-but-still-unanswered threads fold into ONE summary item: "N older unanswered threads — review in /leads" (urgency `week`). Keep the full list reachable on `/now` behind an expandable "show filtered" toggle. Genuinely recent, non-dead replies stay as individual `now` items.

## DONE LOOKS LIKE
1. NOW `now` bucket today shows A.S Électrique + any genuinely recent replies, not the 47-item wall.
2. One rollup item accounts for the old/declined threads; expanding it (or opening /leads) still reaches them.
3. Badge counts on the index panel match the filtered list.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
systemctl --user restart aperture
curl -s -u <auth> localhost:8788/api/next-actions | python3 -c "import json,sys; a=json.load(sys.stdin)['actions']; print('now:',len([x for x in a if x['urgency']=='now']))"  # expect a small number, not ~47
```

## OUT OF SCOPE
Job badges / launch-button gating (AP-13) · notifications · writing status back to README · any change to job spawning
