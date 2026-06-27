# BX-08 — Campaign engine

**Loop:** A (Boréal cash) · **Priority:** P1 (unblocks all automated outreach) · **Safety:** `[SCHEMA]` (additive columns + new table) + `[DATA]` (writes leads + conversations); no sends during implementation
**Status:** briefed · **Depends on:** BX-01 live-verified ✅, BX-02 Phase 2 ✅, BX-03 ✅
**Source:** STRATEGY.md §6 + §5C

Written by: architect, 2026-06-26

Read `~/kernel/agents/executor.md` before starting.

---

## GOAL

A `boreal-campaign` script reads `campaigns.yaml`, selects eligible leads per segment, sends via the gateway, records metrics per campaign cycle, and auto-disables campaigns that miss their kill threshold — all on a weekly timer that starts disabled.

## WHY

The send gateway (BX-01) and CRM (BX-02) are live. The machine has no re-outreach mechanism for the 450 SENT leads and 83 DRAFTED leads sitting in crm.db. Every week without a campaign engine is a week of dead pipeline. STRATEGY.md §6 made this the next required brief after BX-04.

Three side-effects this brief must also close:
- **Consent gap (§5C):** crm.db has no `source` column recording where each lead came from. CASL implied-consent basis requires this. Additive ALTER TABLE.
- **Campaign metrics visibility:** without recorded results per campaign angle, kill-criteria cannot be enforced and the machine runs blind.

## PREREQUISITE

- `~/scripts/boreal-send` live-verified (BX-01 ✅)
- `crm.db` canonical schema post-BX-02 (BX-02 ✅)
- `sms-inbox` classifier live (BX-03 ✅)
- PO has NOT yet given go/no-go on timer — that is a post-build PO action

## FILES IT OWNS

```
~/scripts/boreal-campaign              — campaign runner (new)
~/projects/boreal-leads/campaigns.yaml — campaign definitions (new)
~/projects/boreal-leads/crm_lib.py    — add campaign_run logging helper only
```

systemd (create disabled, do NOT enable):
```
~/.config/systemd/user/boreal-campaign.service
~/.config/systemd/user/boreal-campaign.timer
```

Schema changes (additive only, no column renames):
```
crm.db :: leads table         — ADD COLUMN source TEXT DEFAULT 'unknown'
crm.db :: campaign_runs table — CREATE TABLE (new, defined below)
```

## DO NOT TOUCH

- `~/scripts/boreal-send` (gateway) — read the send contract, call it, do not change it
- `sms-inbox`, `sms-webhook`, `reply-agent` — live services; do not restart them
- `followup.yaml` / `boreal-followup` — separate sequence, separate timer
- `leads.md`, `soumission-leads.md`, `sr-leads.md` — frozen legacy; do not write to them
- Any existing crm.db column — additive only, no renames

## SPEC

### Schema changes

**ALTER TABLE leads (additive):**
```sql
ALTER TABLE leads ADD COLUMN source TEXT DEFAULT 'unknown';
```
Backfill best-effort from existing data:
- Leads whose phone appears in `soumission-leads.md` → `'soumission-renovation'`
- Leads whose phone appears in `sr-leads.md` → `'sr-leads'`
- Leads whose phone appears in `leads.md` → `'pages-jaunes'`
- Everything else → leave `'unknown'`
Do the backfill via a Python script block; do not require manual input.

**CREATE TABLE campaign_runs:**
```sql
CREATE TABLE IF NOT EXISTS campaign_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT NOT NULL,
    run_date TEXT NOT NULL,          -- ISO date
    segment_count INTEGER,           -- leads matched segment query
    sends_attempted INTEGER,
    sends_blocked INTEGER,           -- gateway rejected (STOP/cooldown/cap)
    hand_raises_before INTEGER,      -- REPLIED count for segment at run start
    kill_triggered INTEGER DEFAULT 0 -- 1 if this run triggered kill
);
```

### campaigns.yaml format

```yaml
# campaigns.yaml — each entry is one outreach angle.
# status: DRAFT | ACTIVE | KILLED
# kill_threshold: min hand_raise_rate (%) after min_cycles before auto-kill
campaigns:
  - id: "missed-call-pain-v1"
    status: DRAFT                          # PO flips to ACTIVE to enable
    segment_query: |
      SELECT phone FROM leads
      WHERE stage IN ('SENT','DRAFTED')
      AND stage NOT IN ('STOP','DEAD','REPLIED','RESPONDED')
      AND (last_campaign_touch IS NULL OR last_campaign_touch < date('now','-14 days'))
      LIMIT 100
    body: "Cette semaine, combien d'appels manqués ont été des soumissions qui sont allées ailleurs? Si ça t'arrive souvent, réponds OUI."
    stop_footer: true                      # append STOP to opt out on campaign sends
    min_cycles: 2
    kill_threshold_pct: 1.0               # kill if < 1% hand-raise after 2 cycles
    consent_basis: "b2b-implied-published-phone"
```

Ship exactly 1 starter campaign (`missed-call-pain-v1`) in DRAFT status. PO flips to ACTIVE. No other campaigns in the initial file.

### boreal-campaign runner logic

1. Load `campaigns.yaml`, filter `status == ACTIVE`.
2. For each active campaign:
   a. Run segment_query → list of phones
   b. Skip any phone already in this campaign cycle (check `campaign_runs` + conversations)
   c. Call `boreal-send --body "…" --to <phone> --tag "campaign:<campaign_id>"` for each
   d. Record results in `campaign_runs`
   e. Compute `hand_raise_rate = hand_raises_delta / sends_attempted * 100`
   f. If `min_cycles` reached AND `hand_raise_rate < kill_threshold_pct`: flip campaign `status: KILLED` in campaigns.yaml + Telegram alert: `🔴 Campaign {id} killed — {rate}% hand-raise below {threshold}% threshold`
3. Telegram summary at end of run: `📊 Campaign run: {campaign_id} — {sends_attempted} sent, {sends_blocked} blocked, {hand_raise_rate:.1f}% hand-raise`
4. `--dry-run`: print plan, zero sends, zero DB writes.

**Critical:** `boreal-send` already enforces STOP/quiet-hours/cooldown/cap/dedup. The campaign engine must NOT duplicate those checks — trust the gateway.

### Timer spec (create disabled)

`boreal-campaign.timer` fires Monday 09:15 (after any weekly cron maintenance window).
Timer stays disabled until PO issues go/no-go after reviewing the starter campaign copy.

## DO NOT TOUCH (repeat for clarity)

`boreal-send` send path · live services (sms-inbox, sms-webhook, reply-agent) · followup.yaml · any column that already exists in crm.db

## DONE LOOKS LIKE

1. `campaigns.yaml` exists with 1 campaign in `status: DRAFT`.
2. `boreal-campaign --dry-run` prints: segment query result count, body preview, estimated sends, zero actual sends.
3. `sqlite3 ~/projects/boreal-leads/crm.db ".schema leads"` shows `source` column.
4. `sqlite3 ~/projects/boreal-leads/crm.db ".schema campaign_runs"` shows all columns.
5. `systemctl --user is-enabled boreal-campaign.timer` → `disabled`
6. No new rows in gateway log (`~/.local/share/boreal-outreach/send-gateway-log.jsonl`) from this brief.
7. Telegram token test: dry-run prints campaign summary to stdout only (no Telegram call in dry-run mode).

## VERIFY WITH

```bash
~/scripts/boreal-campaign --dry-run 2>&1 | head -30
sqlite3 ~/projects/boreal-leads/crm.db "SELECT source, COUNT(*) FROM leads GROUP BY source ORDER BY COUNT(*) DESC;"
sqlite3 ~/projects/boreal-leads/crm.db ".schema campaign_runs"
systemctl --user is-enabled boreal-campaign.timer
tail -3 ~/.local/share/boreal-outreach/send-gateway-log.jsonl  # must NOT show new sends
grep -c "DRAFT" ~/projects/boreal-leads/campaigns.yaml          # at least 1
```

## OUT OF SCOPE

- More than 1 starter campaign (write more after the first is proven)
- Delivery receipt tracking from Twilio (gateway logs SID; Twilio callback → sms-webhook; correlate as a separate brief)
- A/B variant rotation within a campaign (separate brief after kill-criteria is proven)
- Any UI in Aperture for campaign management
- Enabling the timer (PO action after reviewing the starter campaign body)

## EXECUTOR
codex
