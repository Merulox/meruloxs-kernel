# BX-06 — review-request → crm.db write-path (closes BX-05a)

**Loop:** A (Boréal — the cash pipeline reads/writes one source of truth)
**Priority:** P2 · **Safety:** `[DATA]` (writes rows; reviewer gate) · **Runs through the executor**
**Status:** briefed · **Unblocks:** BX-05a · **Depends on:** BX-02 (crm.db canonical)

## CONTEXT
BX-05a (retire md-as-source-of-truth) is complete except one script: **`~/scripts/review-request`** still **writes** review-request sends to `~/projects/boreal-leads/crm.md` under a `## SENT` heading. That file was retired in BX-05 (crm.db is the sole truth), so the writes go to a dead/orphan file. BX-05a was scoped read-path-only, so it correctly stopped at this write. This brief authorizes the write-path fix.

## GOAL
Make `review-request` record sent review requests in **crm.db** instead of `crm.md`, reusing the existing `crm_lib` schema (no migration), so no script writes lead state to markdown anymore.

## WHY
One source of truth for the cash pipeline. A review-request logged only to a deleted md file is invisible to every crm.db-based tool (dedup, history, reporting). (Stack audit §2; completes BX-05a.)

## FILES IT OWNS
- `~/scripts/review-request` — replace the `crm.md` `## SENT` append with a `crm_lib` call.
- `~/scripts/crm_lib.py` — only if a thin helper is needed; prefer existing functions.

## SPEC
1. **Reuse existing schema — no new table, no [SCHEMA].** A review request is an outbound touch; log it via the existing `crm_lib.add_conversation(phone, direction="out", body=<message>, …)` and/or `add_sent(name, phone, template="review-request")`. Match how other senders record outbound (look at how `boreal-followup` / `outreach-batch` log through `crm_lib`).
2. Remove the `CRM_FILE = …/crm.md` write entirely. Do not recreate crm.md.
3. If the lead isn't in `leads` yet, follow the existing upsert/skip convention in `crm_lib` (don't invent one).
4. **Do not change the SMS send mechanism** in this brief (gateway migration is BX-07's concern) — only the *logging* write-path. If review-request currently sends directly, leave that; flag it for BX-07.
5. `--dry-run` must still work and must NOT write to crm.db.

> If the PO later wants review requests tracked *distinctly* (not folded into conversations), that's a separate `[SCHEMA]` task to add a `review_requests` table. Default here = reuse `conversations` (lighter, no migration).

## DO NOT TOUCH
- crm.db lead rows / schema (no migration) · live SMS services (reply-agent/sms-inbox/sms-webhook) · the SMS send path · `leads.md` scraper staging.

## DONE LOOKS LIKE
1. `grep -n "crm.md" ~/scripts/review-request` → nothing (no md write remains).
2. `review-request --dry-run …` prints the message, writes nothing.
3. A real (or `--self-test`) review-request logs a row to crm.db (`conversations`), verifiable via a `crm_lib` read — paste the row.
4. `grep -rnE "open\([^)]*crm\.md|crm\.md" ~/scripts | grep -v inactive` → empty (BX-05a's closing check across all scripts).

## VERIFY WITH (paste raw output)
```bash
grep -n "crm.md" ~/scripts/review-request || echo "no crm.md write — good"
~/scripts/review-request --name "Test Lead" --phone +15145551234 --trade plombier --dry-run 2>&1 | tail -5
grep -rnE "crm\.md" ~/scripts | grep -v inactive || echo "no script writes crm.md anymore — BX-05a closeable"
```

## OUT OF SCOPE
- Migrating the SMS send to the gateway (BX-07) · a dedicated `review_requests` table (separate [SCHEMA] task only if PO wants distinct tracking) · any crm.db schema change.
