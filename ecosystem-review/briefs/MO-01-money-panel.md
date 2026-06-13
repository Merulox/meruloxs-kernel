# MO-01 — Money panel in command-center

**Loop:** A + B (the panel measures both — flywheel rule satisfied)
**Status:** briefed · **Priority:** P1 · **Safety:** read-only (no writes to any data source)

## GOAL
Add a `MONEY` view to command-center (`~/scripts/command-center`, localhost:8800) that shows, on one screen: MRR, Boréal pipeline counts, lead-decay clock, SYNTRA affiliate clicks, and daily API spend.

## WHY
Three dashboards exist and none shows a dollar (audit gap G-01). The system optimizes what it measures; it currently measures agent uptime. The zero-MRR figure being visible daily is the forcing function.

## FILES IT OWNS
- `~/scripts/command-center` (single-file app — add the view, register it in the existing view/feature system alongside HEALTH/MAP)

## DO NOT TOUCH
- Any data source it reads (crm.db, signals.md, *.jsonl logs, registry.json) — read-only
- `~/scripts/credit-monitor`, any systemd unit, any other script

## SPEC
Panel sections (reuse existing collapsible-view UI conventions in the file):
1. **MRR** — parse from `~/.claude/projects/-home-merulox/memory/signals.md` (`mrr_a`, `mrr_b`); display prominently even when $0.
2. **Boréal pipeline** — counts from `~/projects/boreal-leads/crm.db` (the ONLY real DB — `~/scripts/crm.db` is a 0-byte decoy, see BOREAL_STACK_AUDIT.md §2.1). Read-only sqlite3: total leads, responded, discovery booked, clients signed. ⚠️ `stage` and `pipeline_stage` disagree on 24% of rows — show BOTH counts until BX-02 merges them; use `crm_lib.py` for field semantics.
3. **Lead-decay clock** — for leads with status responded-or-warmer: days since last outbound touch (max over sms-sent-log.jsonl + reply-sent-log.jsonl per phone number). Show top-10 stalest warm leads with day counts, red if >14d.
4. **SYNTRA** — affiliate-click + product-view counts via Umami API if `UMAMI_*` env/config is discoverable in `~/syntra`; otherwise render the section with "wire Umami key" placeholder — do not block the panel on this.
5. **API spend** — today's total from credit-monitor's log/state (find its output path by reading `~/scripts/credit-monitor`; it tracks daily Anthropic spend).

## DONE LOOKS LIKE
`curl -s localhost:8800/?view=money` (or the file's existing view-routing equivalent) returns HTML containing: an MRR figure, 4 pipeline counts, a stalest-leads list with day counts, and an API-spend-today figure. Panel renders without error when crm.db is locked or a log file is missing (graceful empty states).

## VERIFY WITH
```
systemctl --user restart command-center && sleep 2
curl -s "localhost:8800/?view=money" | grep -ciE 'mrr|pipeline|decay|spend'   # expect >= 4
journalctl --user -u command-center --since "2 min ago" | grep -i error       # expect empty
```

## OUT OF SCOPE
- Writing to any database or log
- New services, timers, or scripts
- Charts/history — counts and day-numbers only, v1
- Aperture (frozen) — this panel lives in command-center only
