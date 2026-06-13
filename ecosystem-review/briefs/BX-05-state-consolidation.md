# BX-05 — Retire markdown state + delete decoy databases

**Loop:** A · **Priority:** P2 · **Safety:** `[DATA]` (imports leads into crm.db; deletes empty files) — Reviewer pass
**Status:** briefed · **Depends on:** BX-02 COMMIT (don't churn the DB mid-migration)
**Source:** `BOREAL_STACK_AUDIT.md` §2.1, §2.3

## GOAL
`~/projects/boreal-leads/crm.db` becomes the ONLY Boréal state. The markdown files stop being writable state, the ten 0-byte decoy .db files disappear, and `outreach-batch` selects leads from the DB.

## WHY
`outreach-batch` reads `leads.md` + `crm.md` — and crm.md froze 2026-05-27. A lead who texted STOP after that date still looks fresh in markdown. Ten empty .db files (including `~/scripts/crm.db`) keep misleading every tool and audit that touches the stack — this audit itself, and the MO-01 brief, initially pointed at a decoy.

## FILES IT OWNS
- `~/scripts/outreach-batch` (lead-selection section only — swap md parsing for DB query)
- `~/projects/boreal-leads/leads.md`, `crm.md` (import + retire)
- The ten decoy files (delete): `~/scripts/crm.db`, `~/scripts/boreal.db`, `~/.local/share/boreal-outreach/{conversations,boreal,crm}.db`, `~/projects/boreal-leads/{outreach,boreal,sms,leads,boreal-leads}.db`
- `~/projects/boreal-leads/_retired/` (new home for the md files)

## DO NOT TOUCH
- `~/projects/boreal-leads/crm.db` schema; the real DB and its .bak files
- Templates, send logic (BX-01 owns the send path — outreach-batch should already be gateway-migrated when this runs)
- The weekly lead-scraping flow INPUT: if scraping writes new leads to leads.md, the importer below becomes its bridge — do not break scraping; identify what writes leads.md first (`grep -rln "leads.md" ~/scripts ~/projects/boreal-leads`) and report findings before changing anything

## SPEC
1. **Import:** parse `leads.md` (reuse outreach-batch's existing parser); every lead not in crm.db → INSERT with stage DRAFTED. Leads present in both: DB wins, report differences (especially any md-fresh/DB-STOP conflicts — count them; they're the §2.3 bug made visible).
2. **Importer becomes a tool:** `~/scripts/boreal-import-leads <file>` — the scraper's output path into the DB from now on. Idempotent (re-runs safe).
3. **outreach-batch:** replace md-based selection with `SELECT ... WHERE stage='DRAFTED'` via crm_lib (untouched leads = DRAFTED with zero conversations).
4. **Verify each decoy is truly 0 bytes immediately before deleting it** (`stat -c %s` = 0, else ABORT and report). Then delete all ten.
5. **Retire md:** move `leads.md` + `crm.md` → `_retired/` with a header line prepended: "RETIRED 2026-06 — state lives in crm.db; import new leads via boreal-import-leads".

## DONE LOOKS LIKE
Zero .db files exist outside `~/projects/boreal-leads/crm.db*`; outreach-batch dry-run selects from the DB; leads.md content is in the DB; the md files are visibly retired.

## VERIFY WITH (paste raw output)
```bash
find ~ -maxdepth 4 \( -name "*.db" \) -path "*boreal*" -o -name "crm.db" -o -name "boreal.db" 2>/dev/null | grep -v node_modules | grep -v ".bak"   # only the real one
sqlite3 ~/projects/boreal-leads/crm.db "SELECT COUNT(*) FROM leads"            # >= pre-import count; report delta
~/scripts/boreal-import-leads --help && ~/scripts/boreal-import-leads ~/projects/boreal-leads/_retired/leads.md && echo "idempotent-rerun-ok"
grep -n "leads.md\|crm.md" ~/scripts/outreach-batch                            # no state reads remain
ls ~/projects/boreal-leads/_retired/
```

## OUT OF SCOPE
Outreach copy · enabling outreach-batch.timer · the scraper itself (only its handoff point) · signals.md/rules.md (decision layer, stays)
