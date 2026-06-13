# BX-01 — Single send gateway for all Boréal outbound SMS

**Loop:** A · **Priority:** P1 · **Safety:** `[DATA]` (writes conversations/leads rows) — Reviewer pass required. **Blocks all auto-sender re-enablement.**
**Status:** briefed
**Source:** `~/agent-infra/ecosystem-review/audit-2026-06-11/BOREAL_STACK_AUDIT.md` §4–§5

## GOAL
One mandatory chokepoint — `~/scripts/boreal_send.py` (library) + `~/scripts/boreal-send` (CLI) — through which every Boréal outbound SMS must pass. Migrate the five proactive sender scripts off their inline Twilio calls.

## WHY
Twilio POSTs are currently inlined separately in 4+ scripts. Consequences on record: double-sends 5s apart, the same message sent verbatim 3× to one lead in 5 days, 7 consecutive daily sends generating a harassment complaint, and `outreach-batch` having **zero** STOP checks (CASL exposure). No shared quiet hours, cooldown, dedup, or cap exists. Every one of those bugs is unfixable per-script and trivially fixable at one chokepoint.

## FILES IT OWNS
- `~/scripts/boreal_send.py` (new), `~/scripts/boreal-send` (new CLI wrapper)
- `~/scripts/outreach-batch`, `~/scripts/follow-up-sequence`, `~/scripts/close-agent`, `~/scripts/db-reactivation`, `~/scripts/send-sms` — ONLY the lines that construct/POST to Twilio, replaced by gateway calls. No other logic changes.
- `~/.local/share/boreal-outreach/send-gateway-log.jsonl` (new, the unified log)

## DO NOT TOUCH
- `~/scripts/reply-agent`, `~/scripts/sms-webhook`, `~/scripts/missed-call-bot`, `~/scripts/sms-inbox` — running live; they migrate in a later brief
- `~/projects/boreal-leads/crm.db` **schema** (BX-02 owns schema; you may read all tables and INSERT conversations rows / UPDATE leads.last_outbound_* via `crm_lib.py`)
- systemd units — do NOT enable/start any sender timer; they stay held
- `~/.secrets/*` — read-only (twilio-account-sid.txt, twilio-auth-token.txt, twilio-phone-number.txt or equivalent — discover exact filenames via `ls ~/.secrets | grep -i twilio` and how `send-sms` reads them)

## SPEC

### Gate checks, in order (each refusal logged with reason + distinct exit code)
1. **STOP** (exit 2): refuse if ANY of — `leads.stage='STOP'` OR `leads.pipeline_stage='STOP'` OR any `conversations` row for this phone has `classification='STOP'`. Union of all three signals, deliberately redundant until BX-02 merges the columns. **No override flag exists for this check.**
2. **Quiet hours** (exit 3): send window 08:00–20:00 America/Toronto, Mon–Sat. Constants at top of file.
3. **Cooldown** (exit 4): refuse if any outbound to this phone in the last 72h (`conversations` direction='out'). Override `--human-approved` exists ONLY for human-gated replies (reply-gate flow); the override itself is logged.
4. **Verbatim dedup** (exit 5): refuse if an identical body was EVER sent to this phone (exact match against conversations direction='out').
5. **Idempotency** (exit 0, no-op): caller passes `--idem-key`; default = sha256(phone+body+date). A key seen in the last 24h (tracked in the gateway log) returns success without sending — kills the double-send-5s-apart bug.
6. **Daily cap** (exit 6): global outbound cap across ALL callers, default **20/day** (constant; audit BX-06 — the 150 cap in outreach-batch is dead with this).

### On pass
Send via Twilio REST (same endpoint pattern as `send-sms`), then atomically: INSERT `conversations` row (direction='out', body, ts, twilio_sid, template_bucket from `--bucket` arg), UPDATE `leads.last_outbound_ts/last_outbound_body` via `crm_lib.py`, append JSON line to `send-gateway-log.jsonl` (ts, phone, body, caller, idem_key, result).

### Interface
```
boreal-send --to +1XXXXXXXXXX --body "..." [--bucket followup-48h] [--caller outreach-batch] [--idem-key K] [--human-approved] [--dry-run]
```
Library: `boreal_send.send(to, body, caller, bucket=None, idem_key=None, human_approved=False, dry_run=False) -> SendResult`. `--dry-run` runs every gate and reports the verdict without sending or writing.

### Caller migration
In each of the five owned sender scripts: replace the inline Twilio construction/POST with a call to `boreal_send.send(...)` passing `caller=<script-name>`. Preserve each script's surrounding logic untouched. Each script must treat block exit codes as skip-and-continue (log, don't crash the batch).

## DONE LOOKS LIKE
- `grep -rn "api.twilio.com" ~/scripts/outreach-batch ~/scripts/follow-up-sequence ~/scripts/close-agent ~/scripts/db-reactivation ~/scripts/send-sms` → only matches inside boreal_send.py / boreal-send
- All six gates demonstrably fire (see VERIFY)
- One real SMS sent through the full path to the PO's own phone

## VERIFY WITH (paste raw output)
```bash
# Gate tests against real DB, dry-run (no sends):
boreal-send --dry-run --to <a-known-STOP-lead-phone> --body "test" ; echo "exit=$?"          # exit=2
boreal-send --dry-run --to <a-known-SENT-lead-phone> --body "<a-body-already-in-their-thread>" ; echo "exit=$?"  # exit=5
# (pick real phones via: sqlite3 ~/projects/boreal-leads/crm.db "SELECT phone FROM leads WHERE stage='STOP' LIMIT 1")
# Cooldown: any lead with last_outbound_ts within 72h, or seed via a dry-run-bypassing test entry — document method used.
# Idempotency: run the same --idem-key twice with --dry-run; second run reports duplicate-key no-op.
# Quiet hours: temporarily set window constants to exclude 'now', run, expect exit=3, restore.
# Live path (ONE real send, PO's phone — architect supplies number at handoff):
boreal-send --to <PO_PHONE> --body "BX-01 gateway live test" --caller verify ; echo "exit=$?" # exit=0
sqlite3 ~/projects/boreal-leads/crm.db "SELECT direction,body,ts FROM conversations WHERE lead_phone='<PO_PHONE>' ORDER BY ts DESC LIMIT 1"
tail -1 ~/.local/share/boreal-outreach/send-gateway-log.jsonl
```

## OUT OF SCOPE
- Message copy/templates (BX-04), schema changes (BX-02), classifier (BX-03)
- Migrating reply-agent / missed-call-bot / sms-webhook (later brief — note they still bypass the gateway)
- Enabling any sender timer — **go/no-go remains a PO decision after BX-01+BX-02 are verified**
- Retiring crm.md/leads.md (BX-05)
