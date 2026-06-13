# Boréal Pipeline — Resume Runbook

Written 2026-06-12 during the actual resume (PO decision superseding the 2026-05-27 halt). This is the repeatable sequence if it ever goes down again.

## What "down" looked like (for recognition)
- All boreal units `inactive/dead`; `boreal-tunnel` still running (live tunnel → dead webhook = inbound silently lost)
- 19 scripts moved to `~/scripts/inactive/` (commit `b67703a`, 2026-06-06)
- `claude-ops` state `paused: true` — and **both claude-ops bugs meant resume was impossible**: snapshot recorded all-"unknown" (env vars not exported before snapshotting) and `cmd_up`'s Python had a syntax error. Both fixed 2026-06-12 in `~/scripts/claude-ops`.
- `rules.md` active_rule: halt notice

## Resume sequence (as executed 2026-06-12)

1. **Restore scripts:** `cd ~/scripts && git mv inactive/<each> .` — watch for traps:
   - `sms-inbox` in `~/scripts` was a SYMLINK into `inactive/` — replace with the real file
   - `outreach-batch` had a NEWER active copy — keep active, leave `inactive/outreach-batch.superseded-by-active`
2. **Flip claude-ops state:** set `paused: false` in `~/.local/state/claude-ops/state.json` (or `claude-ops up` now that it's fixed)
3. **Start inbound + guardrails** (enable + start):
   - `sms-webhook.service` (port 8765, Twilio inbound)
   - `sms-inbox.service` (poller daemon)
   - `missed-call-bot.service` (port 8766) + `missed-call-tunnel.service`
   - `calendly-poller.timer`, `callback-reminder.timer` (Mon–Fri 08:30, PO reminder)
   - `follow-up-brief.timer` (08:30 Telegram brief to PO)
   - `credit-monitor.service` (alerts at 80% of $5/day + $1/hr burn)
   - `pipeline-integrity-check.timer` (07:00 daily)
4. **Verify end-to-end:**
   ```
   systemctl --user is-active sms-webhook sms-inbox missed-call-bot missed-call-tunnel credit-monitor
   curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:8765/        # 200
   curl -s -o /dev/null -w "%{http_code}" -X POST https://webhook.borealnumerique.ca/   # 200
   journalctl --user -u sms-webhook --since "5 min ago"                          # no errors
   ```
5. **Update decision layer:** `~/.claude/projects/-home-merulox/memory/rules.md` active rule + `signals.md` if state changed.

## ⚠️ HELD — proactive SMS senders (NOT auto-started; PO go/no-go required)

These message real prospects. After a long dark period, review message content + target list before enabling:

| Unit | Schedule | What it does |
|---|---|---|
| `follow-up-auto.timer` | 08,12,16,20:00 daily | `follow-up-sequence --send` — follow-up SMS to prospects |
| `follow-up-sequence.timer` | 08:00 daily | same script — **check overlap with follow-up-auto before enabling both** |
| `outreach-batch.timer` | Mon–Fri 10:00 | 10 NEW cold outreach SMS per day |
| `db-reactivation.timer` | 10:00 daily | reactivation messages to dormant DB contacts |
| `close-agent.timer` | 09:00 daily | close-sequence messages to warm leads |

Enable with: `systemctl --user enable --now <unit>`. Recommended order once approved: close-agent (warmest) → follow-up sequence (pick ONE of the two timers) → db-reactivation → outreach-batch (coldest).

## Known leftovers
- `genesis-core` was stripped of the pipeline integration in commit `b67703a` (−19 lines). NOT restored — genesis-core is frozen anyway; if Genesis revival ever happens, re-add from git history.
- `~/scripts` changes (restores + claude-ops fixes) staged but uncommitted — PO commits.
