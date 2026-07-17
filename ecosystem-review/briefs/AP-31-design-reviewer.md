# AP-31 — Syntra design reviewer + Telegram sequential confirmation loop

**Loop:** B (SYNTRA compounding — continuous improvement infrastructure)
**Priority:** P1 · **Safety:** — (new scripts + new service only; no prod code touched directly)
**Status:** briefed · **Depends on:** S-30/S-30b (screenshot infra done ✓)

<!-- gates: depends=; inputs=; confirms= -->
<!-- S-30 + S-30b verified done 2026-07-05 (screenshot infra + watch mode) — deps removed from gate since they resolve in syntra TASKS.md not kernel registry -->

## GOAL

`syntra-design-review` runs Claude vision over the latest screenshots, produces a ranked list of design/SEO recommendations, and sends them one-by-one to PO via Telegram with a before-screenshot + confirm/skip buttons. On confirm, a brief is written and a Codex job is launched automatically.

## WHY

Design iteration currently requires PO to manually inspect screenshots and write briefs. This replaces that with a reviewable queue: Claude finds the issues, PO approves or skips from their phone, Codex executes. The loop closes via AP-27 (Codex done → Telegram ping + next screenshot run).

## SYSTEM OVERVIEW

```
PO runs: npm run design:review  (or triggers syntra-design-reviewer service)
  → reads ~/syntra/docs/design/screenshots/<latest>/
  → calls Claude vision (claude-sonnet-4-6) → structured JSON recommendations
  → writes ~/syntra/docs/design/pending.json
  → sends rec #1 via Telegram: [screenshot photo] + caption + [✅ Launch][❌ Skip]

syntra-design-poller (always-on service):
  → long-polls Telegram getUpdates
  → on callback_query "launch:<id>":
       writes brief → POST /api/launch-codex → Codex runs → AP-27 fires
  → on callback_query "skip:<id>":
       marks skipped
  → either way: sends rec #2, then #3, etc.
  → when queue exhausted: sends summary "N launched · M skipped"
```

---

## PHASE 1 — Design reviewer script

### File
`~/syntra/scripts/design-reviewer.js` (new, ESM)

### Package additions
`~/syntra/package.json`:
- Add script: `"design:review": "node scripts/design-reviewer.js"`
- Add devDep: `@anthropic-ai/sdk` (if not already present — check first)

### Logic

1. **Read latest run** from `~/syntra/docs/design/screenshots/` — take the lexicographically last dir; load its `manifest.json`
2. **Base64-encode each PNG** from `manifest.json.screenshots` (all 5)
3. **Call Claude API** — `claude-sonnet-4-6-20251001`, max_tokens 4096:
   - API key from `~/.secrets/aperture-env` (`ANTHROPIC_API_KEY=...`)
   - System prompt: see §Reviewer system prompt below
   - Message: 5 `image` content blocks (base64 + `image/png`) followed by the text instruction
4. **Parse response** — expect JSON array; validate shape; on parse failure log and exit 1
5. **Assign IDs** — `SAR-01`, `SAR-02`, … (scan `~/syntra/docs/planning/` for existing `task-SAR-*.md` to avoid collisions; start from highest + 1)
6. **Write pending.json**: `~/syntra/docs/design/pending.json` (overwrites any prior session)
7. **Send first recommendation** (see §Telegram send below)
8. Exit 0

### pending.json schema
```json
{
  "session": "2026-07-05-1730",
  "run": "<screenshot run id from manifest>",
  "items": [
    {
      "id": "SAR-01",
      "surface": "home",
      "type": "bug",
      "severity": "P0",
      "title": "Remove double SYNTRA wordmark from landing hero",
      "description": "The hero section renders 'SYNTRA' as both a small label and a giant heading. The label is redundant once the shared header is live.",
      "brief_content": "# SAR-01 — ...\n\n## GOAL\n...",
      "screenshot_key": "home",
      "telegram_message_id": null,
      "status": "queued"
    }
  ],
  "offset": 0
}
```

### Reviewer system prompt
```
You are a design and SEO reviewer for SYNTRA, a curated everyday carry editorial site (syntraworks.ca). You will receive screenshots of 5 key pages. Your job is to identify actionable improvements an executor can implement.

For each finding, produce a brief_content field in this exact format (markdown, fill all sections):

---
# <ID> — <title>

**Loop:** B
**Priority:** <P0/P1/P2> · **Safety:** —
**Status:** briefed

### GOAL
One sentence: what changes in the world.

### WHY
2-3 sentences: why this matters, why now.

### FILES IT OWNS
- Exact file paths (web/src/styles.css, web/src/LandingPage.jsx, etc.)

### DO NOT TOUCH
- List explicitly.

### DONE LOOKS LIKE
Numbered, observable, testable criteria.

### VERIFY WITH
```bash
# exact commands
```

### OUT OF SCOPE
- Explicit deferrals.
---

Return a JSON array (no markdown wrapper). Each item:
{
  "surface": "home|shelf|collection-wallets|collection-peak-design|product-sample",
  "type": "bug|aesthetic|seo",
  "severity": "P0|P1|P2",
  "title": "one-line title",
  "description": "2-3 sentences for the Telegram caption",
  "brief_content": "full markdown brief as a string",
  "screenshot_key": "home|shelf|collection-wallets|collection-peak-design|product-sample"
}

Order: P0 bugs first, then P1 by type (aesthetic before seo), then P2. Return 4-8 items maximum — quality over quantity. Only actionable findings that an executor can implement in CSS/JSX/copy.
```

---

## PHASE 2 — Callback poller service

### File
`~/scripts/syntra-design-poller` (new, executable Node.js ESM script)

### Systemd service
Wire to the existing `syntra-design-poller` systemd user unit (already registered in manifest as stopped). The unit's `ExecStart` should point to this script.

### Credentials
- Telegram: `~/.secrets/mirrorchamber-bot.env` → `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- Aperture: `~/.secrets/web-auth.txt` → `user:password` (Basic auth)
- Claude (if needed for brief gen): `~/.secrets/aperture-env` → `ANTHROPIC_API_KEY`

### Logic

**Startup:**
1. Load credentials
2. Read `~/syntra/docs/design/pending.json` (if missing or no queued items: log "no pending session" + exit 0)
3. Begin long-poll loop

**Long-poll loop:**
```
GET https://api.telegram.org/bot<TOKEN>/getUpdates?offset=<pending.offset>&timeout=30
```
- On network error: log + retry with 5s backoff
- On each update: filter for `callback_query` only (ignore messages)
- Track `update_id` → set `pending.offset = max(update_id) + 1` after each batch; write back to pending.json

**On callback_query:**
1. `answerCallbackQuery(callback_query_id)` — dismisses the spinner on PO's phone
2. Parse `callback_data`: `"launch:<id>"` or `"skip:<id>"`
3. Find item in `pending.items` by id
4. If `launch`:
   a. Write `~/syntra/docs/planning/task-<id>.md` with `item.brief_content`
   b. POST to `http://localhost:8788/api/launch-codex` with Basic auth:
      ```json
      {
        "taskId": "<item.id>",
        "taskTitle": "<item.title>",
        "briefPath": "~/syntra/docs/planning/task-<item.id>.md",
        "prompt": "Read ~/kernel/agents/executor.md.\nThen read ~/syntra/docs/planning/task-<item.id>.md and implement the task.\nReport back using ~/kernel/templates/implementation-report.md.\nPaste raw command output — do not summarize."
      }
      ```
   c. Update `item.status = 'launched'`
5. If `skip`:
   a. Update `item.status = 'skipped'`
6. Write pending.json
7. **Advance queue**: find next item with `status === 'queued'`
   - If found: call `sendRecommendation(item)`
   - If none: call `sendSummary()` + exit 0

### Telegram send functions

**sendRecommendation(item):**
```
POST /sendPhoto
  chat_id: <CHAT_ID>
  photo: <PNG bytes from ~/syntra/docs/design/screenshots/<run>/<item.screenshot_key>.png>
  caption: "<item.severity> · <item.type>\n<item.title>\n\n<item.description>"
  reply_markup: InlineKeyboardMarkup {
    inline_keyboard: [[
      { text: "✅ Launch", callback_data: "launch:<item.id>" },
      { text: "❌ Skip",   callback_data: "skip:<item.id>"   }
    ]]
  }
```
Store returned `message_id` in `item.telegram_message_id` + write pending.json.

**sendSummary():**
```
POST /sendMessage
  text: "SYNTRA review complete\nLaunched: N · Skipped: M\n<list of launched IDs>"
```

---

## FILES IT OWNS

| File | Repo |
|------|------|
| `~/syntra/scripts/design-reviewer.js` | syntra |
| `~/syntra/package.json` | syntra (add script + dep) |
| `~/syntra/docs/design/pending.json` | syntra (runtime, gitignored) |
| `~/syntra/docs/design/.gitignore` | syntra (add `pending.json`) |
| `~/scripts/syntra-design-poller` | system scripts |

## DO NOT TOUCH
- `~/projects/aperture/src/lib/notify.ts` — poller has its own Telegram calls, no changes to notify.ts
- `~/projects/aperture/src/pages/api/launch-codex.ts` — called as-is via HTTP, no changes
- Any syntra production code (`web/`, `src/`, `storefront/`)
- `~/syntra/scripts/screenshot.js` — leave untouched

---

## DONE LOOKS LIKE

1. `npm run design:review` completes: `pending.json` written with ≥1 item; first recommendation appears on PO's Telegram as a photo message with two inline buttons
2. Tapping ✅ on a recommendation: `answerCallbackQuery` fires (spinner clears), brief file written to `~/syntra/docs/planning/task-SAR-01.md`, Aperture job created (check Aperture taskboard), next recommendation photo appears on Telegram
3. Tapping ❌: item marked skipped, next recommendation appears
4. After last item: summary message sent "SYNTRA review complete · Launched: N · Skipped: M"
5. `syntra-design-poller` service starts and stays running (`systemctl --user status syntra-design-poller` → active)
6. Brief files written by the poller are valid markdown and pass the brief quality checklist (GOAL, WHY, FILES IT OWNS, DO NOT TOUCH, DONE LOOKS LIKE, VERIFY WITH, OUT OF SCOPE all present)

---

## VERIFY WITH (paste raw output)

```bash
# Phase 1 — reviewer
cd ~/syntra
npm run design:review 2>&1 | tail -5
cat docs/design/pending.json | python3 -m json.tool | head -30
# expect: valid JSON with items array, first item status=waiting_confirm

# Phase 2 — poller service
systemctl --user status syntra-design-poller | head -5
# expect: active (running)

# Manual end-to-end (architect verifies by inspection):
# 1. Photo appears on PO Telegram with two buttons
# 2. Tap ✅ → brief appears at ~/syntra/docs/planning/task-SAR-01.md
# 3. Aperture taskboard shows new job
# 4. Tap ❌ on rec #2 → rec #3 photo appears
# 5. After last rec → summary message
ls ~/syntra/docs/planning/task-SAR-*.md 2>/dev/null
# expect: one file per launched recommendation
```

---

## OUT OF SCOPE

- Multi-project support (only SYNTRA screenshots for now)
- Editing or cancelling a launched brief after confirmation
- Rate limiting / cooldown between review sessions
- Screenshot capture trigger (still manual: `npm run screenshot` or `npm run screenshot:watch`)
- Reviewer output for Aperture's own UI (separate AP brief if needed)
- Any intelligence about which recommendations were already implemented (future: cross-check pending.json against git log)
