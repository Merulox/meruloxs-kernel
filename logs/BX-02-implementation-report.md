# Implementation Report: BX-02 — CRM data hygiene migration Phase 2

Executor: Codex
Date: 2026-06-13
Brief: `~/agent-infra/ecosystem-review/briefs/BX-02-crm-hygiene.md`

---

## What was implemented

No Phase 2 writes were executed. The binding pre-rename column-reference grep found two additional `crm_lib.py` references that would break after `pipeline_stage` is renamed, and `crm_lib.py` is outside the brief's owned files with no amendment authorizing changes to it.

## Files created or modified

| File | Action | Notes |
|------|--------|-------|
| `~/agent-infra/logs/BX-02-implementation-report.md` | created | Blocked implementation report |

Files outside FILES IT OWNS that were touched (with justification):
- `~/agent-infra/logs/BX-02-implementation-report.md` — required blocked implementation report.

## Commands run and output

### Pre-Phase-2 `pipeline_stage` reference grep

```text
/home/merulox/scripts/boreal_send.py:180:                WHERE phone=? AND (stage='STOP' OR pipeline_stage='STOP')
/home/merulox/scripts/crm_lib.py:242:    ALLOWED = {"booked_nudge_sent", "postpone_until", "postpone_note", "notes", "fu_bucket", "pipeline_stage"}
/home/merulox/scripts/crm_lib.py:490:    IGNORED leads are included if pipeline_stage='REPLIED' and fu_bucket is set —
/home/merulox/scripts/crm_lib.py:517:                OR (stage = 'IGNORED' AND pipeline_stage = 'REPLIED' AND fu_bucket IS NOT NULL AND fu_bucket != '')
EXIT=0
```

### Confirm staged DB and backup remain intact

```text
/home/merulox/projects/boreal-leads/crm.db 1384448 bytes
/home/merulox/projects/boreal-leads/crm.db.bak-20260612 1277952 bytes
A.S &Eacute;lectrique Inc.|+18199961171|RESPONDED|REPLIED|REPLIED|A.S Électrique Inc.
18
```

### Confirm owned implementation state and task status

```text
TM sms-inbox
?? bx02-report.md
?? crm.db
38:| BX-02 | `briefed` | CRM hygiene — **Phase 2 COMMIT approved, relaunch executor** | Phase 1 done + architect-approved 2026-06-12 with amendments (see brief §ARCHITECT REVIEW — gateway column coordination added). bx02-report.md verified against DB | bx02-crm-migrate + crm.db (+ boreal_send.py STOP query) | [DATA][SCHEMA] Phase 2 only — single transaction; coordinate sms-inbox restart | — |
```

### Required Aperture blocked marker write

```text
patch rejected: writing outside of the project; rejected by user approval settings
```

## Assumptions made that were not in the brief

None.

## Deviations from the brief

- Phase 2 was not executed because renaming `pipeline_stage` would make `crm_lib.set_field(..., "pipeline_stage", ...)` and `crm_lib.get_pipeline_leads()` raise `sqlite3.OperationalError`.
- The required Aperture `.blocked` marker could not be written because `~/.local/share/aperture/jobs` is outside this job's writable roots.

## Verify commands for the architect

Run these to confirm the blocker and unchanged staged state:

```bash
grep -n 'pipeline_stage' ~/scripts/sms-inbox ~/scripts/boreal_send.py ~/scripts/crm_lib.py
sqlite3 ~/projects/boreal-leads/crm.db "PRAGMA table_info(leads);"
sqlite3 ~/projects/boreal-leads/crm.db "SELECT COUNT(*) FROM conversations WHERE junk=1;"
```

Expected: `crm_lib.py` references `pipeline_stage` at lines 242 and 517; staged `_v2` columns still exist; junk count remains 18.

## Blockers or open questions

Architect must explicitly authorize the required `crm_lib.py` changes or amend the migration plan before `pipeline_stage` can be renamed without leaving shared CRM code broken.
