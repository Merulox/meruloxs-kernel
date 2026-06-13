# WEB-01: Fix log-digest — restore daily merulox.com log tab updates

**Status:** briefed  
**Date:** 2026-06-11  
**Touches:** `~/.config/systemd/user/log-digest.service` only  
**Risk gate:** makes one paid Claude API call per day (cheap); auto-deploys to Cloudflare Pages

---

## GOAL

The merulox.com log tab has not updated since 2026-06-06. Restore daily automatic updates including auto-deploy.

---

## WHY

Two separate blockers are compounding:

1. **`claude-ops` has been paused since 2026-05-17.** `log-digest` checks the pause state and skips the Claude API call entirely when paused. The timer fires every day at 19:00 EDT, runs for ~46s, and exits 0 — but writes nothing, because the summarization call is skipped.

2. **Auto-deploy is commented out.** Even when log-digest does produce an entry, the line `Environment=LOG_DIGEST_DEPLOY=1` in the service unit is commented out. Deploys require a manual `cd ~/website && npm run deploy` (Cloudflare Pages via wrangler).

Both fixes are in the same file and take effect after `daemon-reload`.

---

## CURRENT STATE

`~/.config/systemd/user/log-digest.service`:
```
ExecStart=%h/scripts/log-digest
# Environment=LOG_DIGEST_DEPLOY=1
```

`log.json` has 2 entries, both dated 2026-06-06. Last successful write was 5 days ago.

The `--force` flag in `log-digest` is the documented bypass: `if ops_paused() and "--force" not in args: skip`. Log-digest is a publishing pipeline, not a brain service — it should run regardless of the ops pause state.

---

## FILES IT OWNS

- `~/.config/systemd/user/log-digest.service` — two line changes

---

## DO NOT TOUCH

- `~/scripts/log-digest` — no script changes
- `~/website/` — no manual edits; deploy is triggered automatically by LOG_DIGEST_DEPLOY=1
- `claude-ops` state — do NOT run `claude-ops up`; the `--force` flag is the targeted fix

---

## IMPLEMENTATION

Two changes to `~/.config/systemd/user/log-digest.service`:

**1.** Add `--force` to ExecStart:
```
ExecStart=%h/scripts/log-digest --force
```

**2.** Uncomment the deploy line:
```
Environment=LOG_DIGEST_DEPLOY=1
```

Then reload and run one manual pass to catch up:
```bash
systemctl --user daemon-reload
log-digest --force
```

---

## DONE LOOKS LIKE

1. Service unit has `--force` on ExecStart and `LOG_DIGEST_DEPLOY=1` uncommented
2. Manual `log-digest --force` run exits 0 and writes a new dated entry to `~/website/src/data/log.json`
3. Cloudflare Pages deploy completes (wrangler output: "Deployment complete")
4. `curl -s https://merulox.com/log` (or equivalent API) returns an entry dated today
5. `systemctl --user cat log-digest.service` shows the changes in effect

---

## VERIFY WITH

```bash
# Confirm service unit changes
systemctl --user cat log-digest.service | grep -E "ExecStart|DEPLOY"

# Confirm new entry was written
python3 -c "
import json
d = json.load(open('/home/merulox/website/src/data/log.json'))
entries = d.get('entries', d) if isinstance(d, dict) else d
print('total entries:', len(entries))
print('latest date:', entries[-1] if isinstance(entries[-1], str) else entries[-1].get('date','?'))
"

# Confirm timer is healthy for tomorrow
systemctl --user status log-digest.timer
```

---

## OUT OF SCOPE

- Resuming `claude-ops` globally — that affects brain services, separate PO decision
- Backfilling the 5 missing days — one fresh entry is enough; the tab just needs to be alive again
- Changing log-digest logic or signal sources

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/WEB-01-log-digest-fix.md and implement it.
When done: commit nothing (service unit is outside git), set WEB-01 status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
```
