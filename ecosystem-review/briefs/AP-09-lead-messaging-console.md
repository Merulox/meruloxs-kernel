# AP-09 — Lead messaging console in Aperture

**Loop:** A · **Priority:** P1 · **Safety:** sends real SMS (via BX-01 gateway only, human-initiated) — Reviewer pass on the send path
**Status:** briefed · **Depends on:** BX-01 verified (send button stays disabled until `~/scripts/boreal-send` exists)
**Note:** Aperture's feature freeze (audit, 2026-06-12) is LIFTED for AP-09/AP-10 by PO order — these serve Loop A directly: the PO has no SMS access except Telegram and must be able to work leads from a browser.

## GOAL
A `/leads` page in Aperture: pick a lead, read the full SMS thread, type a reply, send it through the BX-01 gateway. Usable from a phone browser (aperture.merulox.com is already tunneled + basic-auth'd).

## WHY
A live lead (A.S Électrique) proposed a meeting time and the PO had no way to reply — no SMS device, only the Telegram commander. Human-driven conversation is the active Boréal mode (auto-senders held); it currently has no interface at all.

## FILES IT OWNS
- `~/projects/aperture/src/pages/leads.astro` (shell) + `src/components/leads/*` (new React components)
- `~/projects/aperture/src/pages/api/leads.ts`, `api/lead-thread.ts`, `api/lead-send.ts` (new)
- `~/projects/aperture/src/lib/crm.ts` (new — read-only crm.db access)
- `src/styles/global.css` (console styles only) — explicitly owned, learn from AP-04's clarification round

## DO NOT TOUCH
- `~/scripts/*` (call `boreal-send`, never reimplement its logic; no direct Twilio anywhere in Aperture)
- crm.db WRITES — the API reads sqlite directly (`better-sqlite3` or shell-out to `sqlite3`, match existing aperture patterns in `src/lib/data.ts`); ALL writes happen inside boreal-send
- Existing pages/panels, tasks board, middleware/auth

## SPEC
1. **GET /api/leads** — list with: name (entity-decoded for display until BX-02 fixes data), phone, stage, last message snippet + direction + ts, unanswered flag (last message is inbound). Sort: unanswered first, then REPLIED/BOOKED, then last_inbound_ts desc. Filter box client-side.
2. **GET /api/lead-thread?phone=** — full conversations for the lead, chronological, direction-styled (in/out bubbles), classification badges.
3. **POST /api/lead-send** `{phone, body}` — execs `~/scripts/boreal-send --to <phone> --body <body> --human-approved --caller aperture-console`. Map exit codes to UI: 0 sent (append to thread optimistically), 2 "⛔ lead opted out (STOP) — send refused", 3/4/5/6 their reasons verbatim. **If `~/scripts/boreal-send` doesn't exist: send button disabled with tooltip "BX-01 gateway not installed".** Shell-escape body safely (no injection via message text).
4. **Thread polling:** while a thread is open, refetch every 10s. No SSE needed.
5. **Compose box:** char counter (SMS segments), Enter-to-newline / button-to-send (no accidental sends), last-sent confirmation inline.
6. Mobile: single-column collapse below 700px (list → thread drill-in, back button).

## DONE LOOKS LIKE
On a phone browser: open aperture.merulox.com/leads → A.S Électrique at top (unanswered) → tap → full thread since 04-11 visible → type reply → send → message appears in thread AND in `send-gateway-log.jsonl` AND as a conversations row. A STOP lead shows the refusal clearly.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
curl -s -u <basic-auth> localhost:<port>/api/leads | python3 -m json.tool | head -20
curl -s -u <basic-auth> "localhost:<port>/api/lead-thread?phone=%2B18199961171" | python3 -m json.tool | tail -10
# Send-path test (gateway dry-run only — executor must NOT live-send to leads):
# temporarily point lead-send at boreal-send --dry-run, POST a test body, paste the gate verdict JSON, then remove the dry-run flag.
# Live send test is performed by PO/architect to the PO phone (~/.secrets/po-phone.txt — NOTE: it is one digit from a real lead's number; never type it manually).
```

## OUT OF SCOPE
Templates/canned replies (post-BX-04) · auto-suggested drafts (reply-agent integration, later) · lead editing/stage changes · outbound to numbers not in crm.db (console replies only, v1) · SSE
