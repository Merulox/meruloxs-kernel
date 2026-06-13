# AP-14 — Post-BX-02 column cleanup in aperture's crm consumers

**Loop:** A · **Priority:** P1 (two live dashboard features 500/degrade right now) · **Safety:** read-only DB queries; aperture-only
**Status:** briefed · **Depends on:** BX-02 (done) · **Runs through the AP-12/13 executor**

## GOAL
Aperture's `/leads` (AP-09) and NOW feed (AP-10) query only the canonical CRM columns, fixing the 500 that BX-02's column migration introduced.

## WHY
BX-02 Phase 2 renamed `pipeline_stage`→`pipeline_stage_legacy` and promoted `stage_v2`→`stage`, `name_v2`→`name` (those `_v2` columns no longer exist). Aperture's queries were written defensively as `COALESCE(NULLIF(l.stage_v2,''), NULLIF(l.pipeline_stage,''), l.stage)` to tolerate both schemas — but **SQLite raises an error on a missing column** (it doesn't treat it as NULL), so post-migration `/api/leads` returns 500 and the NOW feed's lead collectors fail. The migration made the canonical columns authoritative; the fallbacks are now dead and harmful.

## FILES IT OWNS
- `~/projects/aperture/src/lib/crm.ts` (getLeads query — lines ~83, ~85, ~101)
- `~/projects/aperture/src/lib/actions.ts` (collectors — lines ~104, ~111, ~118)

## DO NOT TOUCH
- crm.db (read-only) and the migration itself
- Any other aperture file, the `_legacy` columns
- No git commit (PO commits)

## SPEC
Replace every reference to the removed columns with the canonical column:
- `COALESCE(NULLIF(l.name_v2, ''), l.name)` → `l.name`  (and the unaliased `COALESCE(NULLIF(name_v2, ''), name)` → `name`)
- `COALESCE(NULLIF(l.stage_v2, ''), NULLIF(l.pipeline_stage, ''), l.stage)` → `l.stage`
- In the ORDER BY CASE (crm.ts ~101) the same `stage` simplification; keep `'RESPONDED'` out is fine but the canonical set is REPLIED/BOOKED — leave existing accepted values, just stop referencing the dead columns.
Grep must come back clean afterward. Do not change logic beyond the column source.

## DONE LOOKS LIKE
1. `grep -rn "stage_v2\|name_v2\|classification_v2\|[^_]pipeline_stage" ~/projects/aperture/src` returns nothing (only `_legacy` allowed, and none exist).
2. `npm run build` clean.
3. After restart: `/api/leads` → 200 with lead JSON; `/api/next-actions` → 200 with A.S Électrique present.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
grep -rn "stage_v2\|name_v2\|pipeline_stage" src/ | grep -v _legacy   # empty
curl -s -o /dev/null -w "leads:%{http_code} next:%{http_code}\n" -u <auth> localhost:8788/api/leads
curl -s -u <auth> localhost:8788/api/leads | python3 -c "import json,sys;d=json.load(sys.stdin);print('leads:',len(d['leads']),'gateway:',d['gatewayInstalled'])"
```

## APPLY
restart-after: 

## OUT OF SCOPE
- Dropping `_legacy` columns (architect, after 30 days) · any crm.db write · new features
