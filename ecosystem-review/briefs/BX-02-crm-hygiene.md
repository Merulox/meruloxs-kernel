# BX-02 — CRM data hygiene migration

**Loop:** A · **Priority:** P1 · **Safety:** `[DATA][SCHEMA]` — Reviewer pass required; PO approval for schema change granted 2026-06-12 (this brief is the record). **Blocks all auto-sender re-enablement.**
**Status:** briefed
**Source:** `~/agent-infra/ecosystem-review/audit-2026-06-11/BOREAL_STACK_AUDIT.md` §0, §2, §3

## GOAL
Make `~/projects/boreal-leads/crm.db` trustworthy: one stage column with one vocabulary, classifications that mean something, no junk threads, no HTML-entity names — and a before/after report that establishes the true pipeline counts.

## WHY
The DB currently cannot answer "who is warm?": `stage` and `pipeline_stage` disagree on 149/617 leads, 96% of inbound is rubber-stamped ENGAGED (classifier exception-fallback ran through a credit-dead month), Tinder OTP shortcodes live in the funnel, and names render as `A.S &Eacute;lectrique`. Every sender, follow-up, and dashboard built on this data inherits the corruption.

## FILES IT OWNS
- `~/scripts/bx02-crm-migrate` (new migration script). **First read `~/scripts/crm-migrate` and `~/scripts/crm_lib.py`** — reuse their patterns/helpers where suitable; do not duplicate crm_lib logic.
- `~/projects/boreal-leads/crm.db` (the migration target)
- `~/projects/boreal-leads/bx02-report.md` (the before/after report)
- `~/scripts/boreal_send.py` (Phase 2 only — the STOP-query coordination, per ARCHITECT REVIEW §1)
- `~/scripts/crm_lib.py` (Phase 2 only — the `pipeline_stage` removal, per ARCHITECT REVIEW §5; this is the ONLY authorized edit to it)

## DO NOT TOUCH
- Any sender script, `sms-inbox` (its fallback bug is BX-03's file), any systemd unit
- `crm.md` / `leads.md` (BX-05), the 0-byte decoy .db files (BX-05 deletes them)
- No SMS may be sent by anything in this brief. No Twilio imports.

## SPEC — two-phase: STAGE then COMMIT. Architect reviews between phases.

### Phase 0 — Backup (mandatory, first action)
```
cp ~/projects/boreal-leads/crm.db ~/projects/boreal-leads/crm.db.bak-$(date +%Y%m%d)
```
Verify the copy is >1MB before proceeding. Abort if not.

### Phase 1 — STAGE (no destructive writes; everything goes to new columns/tables)
1. **Stage merge → new column `stage_v2`.** Canonical vocabulary: `DRAFTED / SENT / REPLIED / BOOKED / CLIENT / POSTPONED / DEAD / STOP`.
   Per-lead resolution, deterministic, in this order:
   - If either old column = STOP, or any inbound classified STOP → `STOP` (compliance always wins)
   - Else if either ∈ {RESPONDED, REPLIED} → `REPLIED`
   - Else if stage = POSTPONED → `POSTPONED`
   - Else if either = DEAD or stage = IGNORED → `DEAD`
   - Else if stage = DRAFTED AND zero outbound rows in conversations → `DRAFTED`; if outbound exists → `SENT` (DRAFTED with sends is a lie)
   - Else → `SENT`
2. **Junk identification → new column `conversations.junk` (0/1).** Mark 1 where: lead_phone is a shortcode (<10 digits), OR lead_phone has no row in `leads`, OR body matches OTP patterns (`code|verification|vérification` + digits, no other content). List every match in the report — **no deletions in this phase**.
3. **Reclassification → new column `conversations.classification_v2`.** Target set: all direction='in', junk=0, classification='ENGAGED' rows (~2,316 minus junk). Reuse the classification prompt from `sms-inbox` (the STOP/READY/INTERESTED/QUESTION/ENGAGED/BOUNCE taxonomy with "doubt→STOP") via the Anthropic API with **model `claude-haiku-4-5-20251001`**, batched.
   - **Budget constraint:** credit-monitor alerts at 80% of $5/day. Estimate ≈2,200 short calls ≈ $1–2 at Haiku pricing — fine, but checkpoint progress to a state file every 100 rows so an interruption resumes, and on ANY API failure write `UNCLASSIFIED` (never a real class — the old fallback bug is exactly what we're cleaning).
4. **Name fix → new column `leads.name_v2`** = `html.unescape(name)`, whitespace-normalized.
5. **Generate `bx02-report.md`:** stage_v2 distribution vs old columns (with the 149-disagreement resolution breakdown), classification_v2 distribution vs old, junk row count + samples, names changed count + samples, and the headline: **true warm pipeline (stage_v2 ∈ REPLIED/BOOKED) as a named list**.

**STOP HERE. Report to architect. Phase 2 only after architect approves the report.**

### Phase 2 — COMMIT (after approval)
1. Rename old columns out of the way: `stage`→`stage_legacy`, `pipeline_stage`→`pipeline_stage_legacy`, `classification`→`classification_legacy`, `name`→`name_legacy`; promote `_v2` columns to the canonical names. (SQLite: use `ALTER TABLE ... RENAME COLUMN`; table-rebuild only if version forbids it.)
2. DELETE conversations rows where junk=1 (they're cataloged in the report; leads table untouched by deletion).
3. Re-run the report against final state; append "POST-COMMIT" section.

## DONE LOOKS LIKE
One stage column with the canonical vocabulary; zero ENGAGED-by-fallback rows (every inbound is a real class or UNCLASSIFIED); zero junk threads; zero HTML entities in names; legacy columns preserved with `_legacy` suffix; backup file intact; report tells the truth about the pipeline.

## VERIFY WITH (paste raw output)
```bash
ls -la ~/projects/boreal-leads/crm.db.bak-*                                    # backup exists, >1MB
sqlite3 ~/projects/boreal-leads/crm.db "SELECT stage, COUNT(*) FROM leads GROUP BY stage"     # canonical vocab only
sqlite3 ~/projects/boreal-leads/crm.db "SELECT COUNT(*) FROM leads WHERE stage IS NULL"       # 0
sqlite3 ~/projects/boreal-leads/crm.db "SELECT classification, COUNT(*) FROM conversations WHERE direction='in' GROUP BY classification ORDER BY 2 DESC"
sqlite3 ~/projects/boreal-leads/crm.db "SELECT COUNT(*) FROM leads WHERE name LIKE '%&%;%'"   # 0
sqlite3 ~/projects/boreal-leads/crm.db "SELECT name, phone, stage FROM leads WHERE stage IN ('REPLIED','BOOKED')"  # the real pipeline, named
```

## OUT OF SCOPE
- sms-inbox code fix (BX-03 — until it lands, NEW inbound may still misclassify; note this in the report)
- crm.md/leads.md retirement and decoy-DB deletion (BX-05)
- Any send, any template, any service change
- Dropping `_legacy` columns or the .bak file (architect decides after 30 days)

## NOTES FOR EXECUTOR
- DB is LIVE — `sms-inbox` writes to it on every inbound SMS. Do Phase 2 column renames in a single transaction; check `sms-inbox` column references (`grep -n "stage\|pipeline_stage\|classification" ~/scripts/sms-inbox`) and report any that would break BEFORE Phase 2 — if sms-inbox writes to renamed columns, Phase 2 must include a coordinated stop/start of sms-inbox.service (the ONE permitted service action, restart-only, with architect notified).
- A.S Électrique (+18199961171) must come out of this migration as REPLIED — sanity-check row.

---

## ARCHITECT REVIEW — Phase 1 APPROVED 2026-06-12 (with amendments)

Verified against live DB: `_v2` columns staged (617/617 leads), legacy columns untouched, backup `crm.db.bak-20260612` present, junk criteria sound (<10 digits / orphan / OTP — the "real-looking" junk rows 2478/2490/2491/2492/2500 are orphan sends to garbled numbers, fossils of the broken sender; they're cataloged above, deletion approved). UNCLASSIFIED-instead-of-fabricated is correct behavior (Anthropic credits were too low — honest beats invented).

**Phase 2 is GO with these amendments (binding):**

1. **Gateway coordination (new since brief was written):** `~/scripts/boreal_send.py` now exists and its STOP query reads `stage`, `pipeline_stage`, and `classification`. After the renames, `pipeline_stage` ceases to exist → every send throws OperationalError. In the SAME transaction as the renames, update the STOP query to:
   `WHERE phone=? AND stage='STOP'` + `classification='STOP'` on conversations (drop the pipeline_stage clause — its STOP rows are folded into stage_v2). Run `boreal-send --dry-run` against a STOP lead immediately after commit; expect exit=2.
2. Extend the pre-Phase-2 column-reference grep to BOTH `~/scripts/sms-inbox` AND `~/scripts/boreal_send.py` + `~/scripts/crm_lib.py`. Report any other reference that would break BEFORE executing.
3. sms-inbox stop/start brackets the transaction as already specified. boreal-send needs no service action (invoked per-call).
4. Post-commit sanity rows: A.S Électrique (+18199961171) = REPLIED with clean name "A.S Électrique Inc."; the 44 STOP leads return exit=2 from a dry-run spot-check of 3.

## APPLY
restart-after: sms-inbox

> EXECUTOR: do not run systemctl yourself — the `restart-after: sms-inbox` directive above is applied by Aperture after a clean run. The brief mentions a coordinated sms-inbox stop/start; that coordination is the restart-after, not a manual systemctl call (which the sandbox forbids and which falsely flags the job blocked).

5. **crm_lib.py — AUTHORIZED Phase-2 edit (the executor blocked on this; it is now in FILES IT OWNS).** After the renames, `pipeline_stage` ceases to exist and the `_v2` promotion keeps `stage`/`name`/`classification` as canonical names (so ONLY `pipeline_stage` refs break). Make exactly these two changes IN THE SAME Phase-2 transaction/commit, nothing else in this file:
   - **`set_field()` allowlist (~line 240):** remove `"pipeline_stage"` from `ALLOWED`. (Nothing should write that column post-migration; canonical stage is set via `add_stage`/`upsert`.)
   - **`get_pipeline_leads()` query (~line 516):** delete the now-obsolete clause `OR (stage = 'IGNORED' AND pipeline_stage = 'REPLIED' AND fu_bucket IS NOT NULL AND fu_bucket != '')`. Rationale: the migration folds those exact IGNORED+REPLIED-disagreement rows (17, per bx02-report) into canonical `stage='REPLIED'`, which the main `stage NOT IN (...)` clause already includes. Leave the rest of the query untouched.
   - After the edit, sanity: `python3 -c "import crm_lib"` imports clean; `grep -c pipeline_stage ~/scripts/crm_lib.py` returns only the header-comment count (0 in code).
   Do NOT touch any other crm_lib function. If you find a THIRD breaking ref not listed here, STOP and report (do not improvise).
