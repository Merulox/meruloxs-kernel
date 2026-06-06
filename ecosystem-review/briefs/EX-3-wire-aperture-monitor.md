# EX-3: Wire Aperture to the Live Monitor Feed

Status: ready. Architect 2026-06-05. Read `~/agent-infra/agents/executor.md`.
This activates the crown jewel — Aperture currently reads stale `vitals.json`; point it at the live monitor.

## GOAL
Make the Aperture dashboard read the **live** `realm/monitor/*.jsonl` feeds (service health + the Genesis bug ledger) instead of (or in addition to) the stale `commons/vitals.json`, and add a "System Health" + "Genesis Bug Ledger" section.

## WHY
`realm/monitor/service-health.jsonl` and `genesis-audit.jsonl` are written continuously and hold the most valuable live intelligence in the stack (service states, kill-switch states, ~25 standing bugs). Nothing consumes them. Aperture is the natural consumer.

## FILES IT OWNS
- `~/projects/aperture/src/lib/data.ts` (extend readers)
- `~/projects/aperture/src/pages/index.astro` (add 2 sections)
- `~/projects/aperture/src/styles/global.css` (styling for new sections)

## DO NOT TOUCH
- `src/middleware.ts` (auth), `astro.config.mjs`, `package.json`
- The existing working sections (mode, health, pending decisions, vitals) — ADD, don't break
- Any realm/ file (read-only consumption)

## DATA SOURCES (read at request time, newest line)
- `~/projects/realm/monitor/service-health.jsonl` — each line `{ts, service, status, action}`; show the most recent status per service.
- `~/projects/realm/monitor/genesis-audit.jsonl` — newest line has `services{}`, `kill_switches{}`, `crm{}`, `api_credits{}`, and `pending_items[]` (the bug ledger as markdown-table strings — parse the `| ID | text | 🔲 |` rows into {id, text}).

## NEW SECTIONS
1. **System Health** — table of services from the latest genesis-audit `services{}` map, colored by active/inactive; show `kill_switches`.
2. **Genesis Bug Ledger** — count badge + list of `pending_items` (id + text), grouped by prefix (B/M/V/A/R). These are the unresolved audit findings.

## DONE LOOKS LIKE
1. `npm run build` clean; `npm start` serves on 8788
2. Dashboard (auth m/st) shows the two new sections populated from the live JSONL
3. Bug ledger lists the real items (B1 genesis-core dead, A3 suicide guard, etc.)
4. If a monitor file is missing/empty, the section degrades gracefully (no crash)

## VERIFY WITH
```bash
cd ~/projects/aperture && npm run build && npm start &
sleep 2
curl -s -u m:st http://127.0.0.1:8788/ | grep -oE 'genesis-core|kill_switch|suicide|Bug Ledger|service' | sort -u
kill %1
```
Expect: new section markers + real bug text present.

## OUT OF SCOPE
- Auto-refresh / websockets (manual reload fine for v1)
- Writing to any monitor file (read-only)
- Fixing the bugs (that's EX-5)
