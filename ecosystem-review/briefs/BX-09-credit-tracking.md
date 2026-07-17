# BX-09: Real API Spend Tracking

**Loop:** A (Boréal cash — you can't top up credits intelligently without knowing burn rate)

## EXECUTOR
codex

---

## GOAL

Every service that calls the Anthropic API logs its spend to a shared JSONL file. `credit-monitor` aggregates that file into per-service $/day stats. The APIMAP panel in `command-center` renders those actuals instead of the current $0 (genesis-core-state is dead).

---

## WHY

Credits went low with zero visibility into which service was draining them. The existing APIMAP panel reads `~/obsidian/knowledge/projects/genesis/genesis-core-state.json` which only tracked Genesis spending — Genesis is stopped, so it shows $0. The Anthropic balance API is not accessible with this key type. The drain rates in APIMAP are hardcoded estimates, not measured actuals. The result: blind top-ups, no triage.

Note: AP-21 added a toggle map and daily estimates — this brief adds the *real* measured spend layer on top.

---

## FILES IT OWNS

### New file (create if absent)
```
~/.local/share/boreal/api-spend.jsonl
```
One JSON object per line, appended after every Anthropic API call:
```json
{"ts": "2026-06-27T15:23:01Z", "service": "missed-call-bot", "model": "claude-sonnet-4-6", "input_tokens": 812, "output_tokens": 95, "cost_usd": 0.003861}
```

### Services to modify (add spend logging after every Anthropic API call)

**`~/scripts/missed-call-bot`**
- Model: `claude-sonnet-4-6` — $3.00/$15.00 per MTok in/out
- Where: after the `client.messages.create(...)` call in `generate_sms()` (successful response path only, not the fallback)
- Extract: `response.usage.input_tokens`, `response.usage.output_tokens`
- Compute: `cost = (input_tokens * 3.00 + output_tokens * 15.00) / 1_000_000`
- Append to `~/.local/share/boreal/api-spend.jsonl`
- Skip logging on the HTTP 400 / credit-exhausted path (no API call completed)

**`~/scripts/reply-agent`**
- Read the file first to determine which model it uses and where the API call lives
- Same logging pattern: append to the shared JSONL after a successful response

**`~/scripts/sms-inbox`**
- Read the file first — likely uses `claude-haiku-4-5-20251001` ($1.00/$5.00 per MTok) for classification
- Same logging pattern

### `~/scripts/credit-monitor`
- Currently reads `~/obsidian/knowledge/projects/genesis/genesis-core-state.json`
- Replace the data source: read `~/.local/share/boreal/api-spend.jsonl` instead
- Compute per-service totals (last 24h, last 7d, all-time) by summing `cost_usd` grouped by `service`
- Write output to wherever credit-monitor currently writes its state file (read the script to find it)
- Keep the existing write path and format so APIMAP's existing fetch still works — or update both in sync

### `~/scripts/command-center`
- Add a Python data function `get_api_spend()` that reads `~/.local/share/boreal/api-spend.jsonl` and returns per-service spend grouped by day
- Add route `GET /api/api-spend` → `_json(get_api_spend())`
- Add `HOME / ".local/share/boreal/api-spend.jsonl"` as a module-level Path constant (`API_SPEND_LOG`)
- Update the APIMAP render function to fetch `/api/api-spend` and display:
  - Per service row: name | model | calls last 24h | $/day (last 24h) | $/7d total
  - Grand total $/day across all services
  - Last log entry timestamp so it's obvious when the data is fresh
- Use `_json()` not `_json_sensitive()` — spend data contains no PII

---

## DO NOT TOUCH

- `~/scripts/boreal_send.py` — verbatim-dedup logic, send gates, CRM writes
- `~/projects/boreal-leads/crm.db` — no schema changes
- Any outreach flow (outreach-send, close-agent, boreal-campaign)
- `~/obsidian/knowledge/projects/genesis/genesis-core-state.json` — leave as-is
- credit-monitor's Telegram alert logic — only change the data source, preserve alerts
- AP-21's toggle/gate logic in `boreal_api_gate.py` — additive only

---

## DONE LOOKS LIKE

1. Call the missed-call-bot number (or trigger any inbound SMS)
2. `tail -1 ~/.local/share/boreal/api-spend.jsonl` shows a new entry with `service`, `model`, `input_tokens`, `output_tokens`, `cost_usd`
3. Open command-center APIMAP tab → non-zero $/day row for at least `missed-call-bot`
4. credit-monitor no longer reads genesis-core-state

---

## VERIFY WITH

```bash
# After triggering a missed-call-bot API call:
tail -5 ~/.local/share/boreal/api-spend.jsonl

# Check command-center returns data:
curl -s http://localhost:8800/api/api-spend | python3 -m json.tool

# Confirm credit-monitor no longer references genesis path:
grep -n "genesis-core-state" ~/scripts/credit-monitor

# Restart command-center and reload APIMAP:
systemctl --user restart command-center
```

---

## OUT OF SCOPE

- Fetching live Anthropic balance (no API available for this key type)
- Twilio spend tracking
- Historical spend before this change (log starts fresh)
- OpenRouter or any other provider
- Any UI changes outside the APIMAP render function
- Alert thresholds or notifications
