# MO-02 — Add OpenRouter balance tracking to credit-monitor

## GOAL
`credit-monitor` polls OpenRouter's credit balance every 5 minutes and fires Telegram alerts when the balance is first-funded, low, or exhausted — mirroring the existing Anthropic alerts.

## WHY
OpenRouter is prepaid (you load credits, then spend them). Unlike Anthropic where genesis-core tracks local spend, OpenRouter balance is only readable via their API. Currently there's no visibility into how much is loaded or being burned. When OpenRouter gets funded, we need the same alert coverage we have for Anthropic or we'll burn through it silently.

## FILES IT OWNS
```
~/scripts/credit-monitor    — add OpenRouter polling alongside existing Anthropic loop
```

## DO NOT TOUCH
- `~/obsidian/knowledge/projects/genesis/genesis-core-state.json` — Anthropic spend source, read-only
- Any other genesis state files
- The Anthropic alerting logic — additive only, no changes to existing code paths
- `~/.secrets/openrouter-api-key.txt` — read-only at runtime, never written

## OPENROUTER API
Balance endpoint (verify before implementing — check https://openrouter.ai/docs if this returns 404):
```
GET https://openrouter.ai/api/v1/auth/key
Authorization: Bearer <OPENROUTER_API_KEY>
```
Expected response shape:
```json
{
  "data": {
    "usage": 0.00,
    "limit": null,
    "is_free_tier": false,
    "rate_limit": { ... }
  }
}
```
`usage` = total USD spent against this key. Balance = loaded credits − usage.

If this endpoint doesn't return balance, check `GET https://openrouter.ai/api/v1/credits` as fallback.
The executor must confirm the correct field name before wiring the alert logic.

## IMPLEMENTATION NOTES
- Read key from: `Path.home() / ".secrets/openrouter-api-key.txt"` (same pattern as other secrets)
- If key file doesn't exist or is empty: skip OpenRouter check silently each cycle, log `[openrouter] key not found — skipping`
- If API call fails (network, 401, etc.): log the error, do not alert, do not crash the loop
- State file: `~/obsidian/knowledge/projects/genesis/credit-monitor-state.json` (already exists — add `or_*` prefixed keys to avoid collision with Anthropic keys)
- Poll on the same `CHECK_INTERVAL` (300s) as Anthropic — no separate thread needed, sequential is fine

## ALERTS TO ADD
| Condition | Message |
|---|---|
| Balance transitions from 0 → any positive value (first-funded) | "✅ OpenRouter funded: $X.XX loaded. Monitoring active." |
| Balance < $2.00 (low) | "⚠️ OpenRouter low: $X.XX remaining." |
| Balance ≤ $0.00 (exhausted) | "🚨 OpenRouter exhausted. OpenCode/Hermes calls will fail." |
| Included in end-of-day summary (existing 23:00 summary) | Append: "OpenRouter: $X.XX remaining" |

Alert flags follow same pattern as Anthropic: `or_funded_fired`, `or_low_fired`, `or_exhausted_fired` — reset on day rollover.

## DONE LOOKS LIKE
1. `credit-monitor` starts without error when `openrouter-api-key.txt` is absent
2. When key is present, each poll logs `[openrouter] balance $X.XX` at INFO level
3. A manual test with a zeroed or near-zero balance fires the appropriate Telegram alert
4. End-of-day summary message includes an OpenRouter line
5. Existing Anthropic alert behavior is unchanged (no regressions)

## VERIFY WITH
```bash
# Syntax check
python3 -c "import ast; ast.parse(open('/home/merulox/scripts/credit-monitor').read()); print('syntax OK')"

# Key-absent path (rename key temporarily)
mv ~/.secrets/openrouter-api-key.txt ~/.secrets/openrouter-api-key.txt.bak
timeout 10 python3 ~/scripts/credit-monitor 2>&1 | grep -E "(openrouter|error|start)"
mv ~/.secrets/openrouter-api-key.txt.bak ~/.secrets/openrouter-api-key.txt

# API call returns valid JSON (run live)
python3 -c "
import requests, pathlib
key = pathlib.Path.home() / '.secrets/openrouter-api-key.txt'
r = requests.get('https://openrouter.ai/api/v1/auth/key',
    headers={'Authorization': f'Bearer {key.read_text().strip()}'})
print(r.status_code, r.json())
"

# Restart service and confirm it stays alive for 30s
systemctl --user restart credit-monitor
sleep 30 && systemctl --user is-active credit-monitor
```

## OUT OF SCOPE
- Spend tracking (OpenRouter doesn't expose per-call cost via the key endpoint — balance delta is enough)
- Separate systemd service (extend the existing daemon)
- Daily spend history for OpenRouter (Anthropic tracking is from genesis-core; OpenRouter only gives balance, not daily breakdown)
- Burn rate calculation for OpenRouter (balance delta across 5-min windows would be noisy at low spend)

## EXECUTOR
codex
