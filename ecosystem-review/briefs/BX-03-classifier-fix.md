# BX-03 — Classifier fallback fix + hot-lead routing in sms-inbox

**Loop:** A · **Priority:** P1 · **Safety:** touches a LIVE service (sms-inbox) — restart required, verify after
**Status:** briefed · **Depends on:** none (parallel-safe with BX-01/BX-02)
**Source:** `BOREAL_STACK_AUDIT.md` §3

## GOAL
sms-inbox never fabricates a classification, junk never enters the funnel, and booking-intent replies reach merulox as a hot alert instead of a bus log line.

## WHY
The current fallback returns `"ENGAGED"` on ANY exception or unexpected LLM output (sms-inbox ~lines 317–322) — it manufactured 2,316 bogus rows during the credit-dead month. Tinder OTP shortcodes were ingested as conversations. And today's hottest signal ("Vendredi 3:00h pm" = a booking) was classified ENGAGED and surfaced only as a bus event — it deserved a phone-buzzing alert.

## FILES IT OWNS
- `~/scripts/sms-inbox`
- `~/.local/share/boreal-outreach/classify-retry.jsonl` (new retry queue)

## DO NOT TOUCH
- crm.db schema (BX-02 owns it — write only to existing columns/whatever BX-02 has made canonical; check which migration phase has run before assuming column names)
- Any sender script, reply-agent, sms-webhook, hot-lead-alert internals (CALL it, don't edit it)

## SPEC
1. **Fallback:** exception or invalid LLM output → classification `UNCLASSIFIED` (never a real class). Append the row id + phone + body to `classify-retry.jsonl`.
2. **Retry pass:** on daemon startup and every 6h, re-attempt classification for queued UNCLASSIFIED rows; on success, update the row and remove from queue. Cap 50 retries/pass (budget).
3. **Ingest junk filter:** inbound from shortcodes (<10-digit sender) or matching OTP patterns (verification-code bodies) → log to a `junk.jsonl`, do NOT create conversations rows or leads.
4. **Hot routing:** classification ∈ {READY, INTERESTED} → invoke `~/scripts/hot-lead-alert` (it exists — read it first; if its interface doesn't fit, call telegram via the same mechanism sms-inbox already uses for its Telegram pushes) with name, phone, body, and last 3 thread messages. Additionally, a reply containing a day/time pattern (e.g. `lundi|mardi|...|vendredi.*\d{1,2}` or `\d{1,2}h(\d{2})?|\d{1,2}\s*(am|pm)`) escalates to READY regardless of LLM output.
5. **Restart:** `systemctl --user restart sms-inbox` is permitted (the one service action); verify active + no errors after.

## DONE LOOKS LIKE
A junk OTP never reaches the DB; an API failure yields UNCLASSIFIED + queue entry, retried later; "vendredi 15h" in a reply triggers hot-lead-alert within seconds.

## VERIFY WITH (paste raw output)
```bash
grep -n "UNCLASSIFIED" ~/scripts/sms-inbox | head                       # fallback present
grep -n "ENGAGED" ~/scripts/sms-inbox | grep -i "fallback\|except\|valid"  # no ENGAGED fallback remains
systemctl --user restart sms-inbox && sleep 3 && systemctl --user is-active sms-inbox
journalctl --user -u sms-inbox --since "2 min ago" --no-pager | tail -5  # clean start
# Unit-test the classify + day/time escalation functions directly (python -c importing the script's functions, or a --self-test flag you add):
~/scripts/sms-inbox --self-test   # add this flag: runs classify fallback, junk filter, daytime-escalation cases, prints PASS/FAIL per case
```

## OUT OF SCOPE
Reclassifying historical rows (BX-02 does that) · sender code · template copy · gateway migration (BX-07)

## APPLY
restart-after: sms-inbox
