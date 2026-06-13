# AP-10 — "NOW" panel: live next-actions feed in Aperture

**Loop:** A (primarily) · **Priority:** P1 · **Safety:** read-only everywhere
**Status:** briefed · **Depends on:** none (AP-09 links enhance it but aren't required)
**Note:** Aperture freeze lifted for AP-09/AP-10 by PO order 2026-06-12.

## GOAL
Aperture's index page gets a **NOW** panel (plus a full `/now` page): a constantly-current, priority-ordered list of actionable steps — split by owner (merulox / executor / architect) — computed live from the system's actual state files on every request. The PO opens Aperture and knows exactly what to do next, without asking a session.

## WHY
The priority list currently lives in chat turns and a static gap-audit doc — it goes stale the moment it's written, and it dies with the conversation. Every source of "what's next" already exists on disk as structured state; nobody has joined them into one ranked view.

## FILES IT OWNS
- `~/projects/aperture/src/pages/now.astro` + `src/components/now/*` (new)
- `~/projects/aperture/src/pages/api/next-actions.ts` (new)
- `~/projects/aperture/src/lib/actions.ts` (new — the source collectors)
- Index page: ONLY the addition of the NOW panel slot (top of page)
- `src/styles/global.css` (panel styles only)

## DO NOT TOUCH
- Any source file it reads (all read-only): crm.db, signals.md, briefs/README.md, the gap-audit doc, send-gateway-log
- Other panels, taskboard logic, middleware

## SPEC

### Action item shape
`{ id, title, why (one line), owner: 'merulox'|'executor'|'architect', urgency: 'now'|'today'|'week', source, link? }`

### Collectors (each independent; one failing source must render a single "⚠️ source unreadable: X" item, never crash the panel)
1. **Unanswered leads** (top priority): crm.db — leads whose latest conversations row is direction='in' with no later 'out'. → owner merulox, urgency now, link `/leads?phone=…` (AP-09; plain text if absent). Include hours-since-reply.
2. **Booked/постponed dates due**: leads with `postpone_until <= today+1`; calendly-derived notes if present. → merulox, today.
3. **Stale warm leads**: stage REPLIED/RESPONDED (tolerate both vocabularies until BX-02) with last_outbound >7d. → merulox, week.
4. **Active rule**: the `active_rule:` line from `~/.claude/projects/-home-merulox/memory/signals.md` → pinned banner at panel top, not a list item.
5. **Brief queue**: parse `~/agent-infra/ecosystem-review/briefs/README.md` table — rows `briefed` whose Depends-On is `—` or `done` → "launch executor: <ID>" (executor, today); rows `review` → "verify <ID>" (architect, today); rows mentioning "PO" in risk gate that are blocked → merulox items. Tolerant parser: pipe-split, trim, skip malformed rows.
6. **Gap-audit doc**: `~/obsidian/knowledge/projects/ecosystem/gap-audit-2026-06-11.md` — rows still 🔲 with owner merulox. → merulox, week.
7. **Standing checks**: hardcoded, cheap, honest — uncommitted `~/scripts` changes (`git -C ~/scripts status --porcelain | wc -l`), DRAFT templates awaiting approval (`grep -c "status: DRAFT" .../followup.yaml` if file exists), held sender timers (systemctl is-enabled, listed as "awaiting go/no-go").

### Ranking + render
Sort: owner=merulox first, then urgency (now>today>week), then source order. Sections: **YOU** / **EXECUTORS** / **ARCHITECT**. Each item one line + expandable why. Badge counts in the index panel header ("YOU: 3 · EXEC: 4"). Auto-refresh: refetch every 60s while visible. Computed per-request server-side — no cache, no timer, no state.

## DONE LOOKS LIKE
Opening `/` shows the NOW panel with current real items (today that means: A.S Électrique unanswered/booked, launch BX-02/BX-03, verify MO-01/HK-01, affiliate pass, NocoDB cancel, commit ~/scripts). Editing signals.md's active_rule line changes the banner on next refresh. Killing one source file degrades to a single warning item.

## VERIFY WITH (paste raw output)
```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -2
curl -s -u <basic-auth> localhost:<port>/api/next-actions | python3 -m json.tool | head -40
# Degradation test: temporarily rename the gap-audit doc, re-curl (expect one warning item, panel alive), restore.
# Live check: open / in browser — NOW panel renders, badge counts match API.
```

## OUT OF SCOPE
Writing/completing actions from the UI (read-only v1) · notifications/push · per-item snooze · pulling SYNTRA TASKS.md (add as collector 8 in a follow-up once format proves stable) · any LLM calls
