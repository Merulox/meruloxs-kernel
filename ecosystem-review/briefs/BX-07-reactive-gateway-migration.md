# BX-07 — Migrate live reactive senders to the gateway

**Loop:** A · **Priority:** P2 · **Safety:** touches LIVE services (missed-call-bot, reply-agent path) — one at a time, verify between
**Status:** briefed · **Depends on:** BX-01 verified
**Source:** BX-01 OUT OF SCOPE note; `BOREAL_STACK_AUDIT.md` §5.3

## GOAL
The last inline Twilio calls — reply-agent, missed-call-bot, and any send in sms-webhook — go through `boreal_send`, with a `reactive` caller class that fits their timing needs.

## WHY
After BX-01, the held senders are gated but the LIVE reactive paths still bypass STOP checking and unified logging. A lead who opts out can still receive an instant missed-call text-back or an approved reply draft. Compliance and the unified send log must cover 100% of outbound, not 80%.

## FILES IT OWNS
- `~/scripts/boreal_send.py` (add `reactive=True` caller class ONLY — see spec)
- `~/scripts/reply-agent`, `~/scripts/missed-call-bot`, `~/scripts/sms-webhook` (Twilio POST sites only)

## DO NOT TOUCH
- Gateway gate ORDER or STOP logic (immutable), templates, crm.db schema, any timer

## SPEC
1. **`reactive` class in boreal_send:** skips the cooldown gate (4) and quiet-hours gate (3) — an instant missed-call text-back at 21h is the product working, not spam. **STOP (2), verbatim dedup (5), idempotency (5b), and logging still apply. The daily cap (6) applies but reactive sends get a separate cap (default 30/day).**
2. **missed-call-bot:** its instant text-back → `boreal_send.send(..., reactive=True, caller='missed-call-bot')`. A STOP-listed caller gets NO text-back (log the block).
3. **reply-agent:** the post-approval send → `boreal_send.send(..., human_approved=True, caller='reply-agent')`. Human approval already satisfies intent; the gateway adds STOP enforcement + logging. (Edge case: if a human approves a reply to a STOP lead, the gateway still blocks — surface the block back to Telegram so the human knows.)
4. **sms-webhook:** inventory its outbound sends (`grep -n "api.twilio.com" ~/scripts/sms-webhook`); migrate each the same way; if it only forwards to Telegram, report "no sends" and done.
5. **Rollout:** one script at a time — migrate, restart its service, verify with a live test (PO's phone for missed-call-bot: PO calls the Twilio number, hangs up, receives text-back), then next script.

## DONE LOOKS LIKE
`grep -rn "api.twilio.com" ~/scripts/ --include="*" | grep -v boreal_send | grep -v inactive/` → empty. Every outbound SMS in the ecosystem appears in send-gateway-log.jsonl.

## VERIFY WITH (paste raw output)
```bash
grep -rln "api.twilio.com" ~/scripts/ | grep -v "boreal_send\|inactive"        # empty
for u in missed-call-bot sms-webhook sms-inbox; do systemctl --user is-active $u; done
# Live test (PO participates): PO calls Twilio number, hangs up →
tail -2 ~/.local/share/boreal-outreach/send-gateway-log.jsonl                  # reactive send logged, caller=missed-call-bot
```

## OUT OF SCOPE
Reply-agent draft generation/prompts · new features · sms-inbox (no sends; BX-03 owns it)

## APPLY
restart-after: missed-call-bot, sms-webhook

> EXECUTOR: do not run systemctl yourself (step 5 "restart its service" is handled by the restart-after directive above — Aperture restarts each service after a clean run). Verify migrations with --dry-run against the gateway, not by bouncing the live service.
