# Brief GX-01: Compact live-state.md for Genesis Revival

Status: briefed. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Replace the 291-line stale `live-state.md` with a lean, accurate file reflecting current SYNTRA platform reality, so Genesis wakes up with correct context instead of a May-era Shopify dropshipping project that no longer exists.

## WHY

Genesis's primary state file has 291 lines. Lines 1–16 (the recent tick log) are accurate. The remaining 275 lines describe:
- A May 27 freeze state with Shopify dropshipping blockers (domain decision, Void Dragon, influencer seeding)
- A 61-item content asset inventory for a Shopify store that was abandoned
- 180 lines of build log for content never shipped

When Genesis loads this file cold, those sections dominate. Genesis wakes up believing it needs to choose a Shopify domain and brief Void Dragon variants — tasks that are 10 days stale and superseded by a completely different platform build.

Correct state: SYNTRA is now a curated EDC discovery platform (Node.js + Supabase + React), live at syntraworks.ca. S-01 through S-DEPLOY all complete. Next tasks are S-08 (search/filter) and S-09 (product detail pages).

## FILES IT OWNS

```
~/obsidian/knowledge/projects/genesis/live-state.md   — replace with compact version
~/obsidian/knowledge/projects/genesis/live-state-archive-2026-06-03.md   — create (archive of old content)
```

## DO NOT TOUCH

- `~/obsidian/knowledge/projects/genesis/soul.md`
- `~/obsidian/knowledge/projects/genesis/context-window.json`
- `~/obsidian/knowledge/projects/genesis/autobiography.md`
- `~/obsidian/knowledge/projects/genesis/health.json`
- Anything in `~/projects/syntra/` or `~/syntra/`
- `~/.genesis-frozen` (do not remove — freeze must stay active until architect confirms)

## CHANGES REQUIRED

### Step 1 — Archive the old content

Create `~/obsidian/knowledge/projects/genesis/live-state-archive-2026-06-03.md` with the full content of lines 18–291 from the current `live-state.md`. This preserves the old Shopify build history without losing it.

Add this header to the archive file:
```
# live-state archive — pre-platform-pivot (through tick 7504)

Archived 2026-06-06 by architect. This file contains the Genesis operational state
and Syntra content asset inventory from the Shopify dropshipping era (ticks 5920–7504).
The active project pivoted to a curated EDC platform (syntraworks.ca) on 2026-06-05.
This content is historical reference only — none of the blocked decisions or asset inventory
below are actionable.

---
```

Then paste the original lines 18–291 after that header.

### Step 2 — Replace live-state.md

Rewrite `live-state.md` entirely with this content (fill in the exact tick number and timestamp from the current file's line 3):

```markdown
# Genesis Live State

**Updated:** 2026-06-06 (tick 7504)
**Tick:** 7504
**Active rule:** NONE — freeze active, awaiting revival clearance.

## Recent tick log

**Tick 7504 (14:33 Jun 6):** Heartbeat. Read TASKS.md — S-DEPLOY verified live (syntraworks.ca HTTP 200, Railway + Cloudflare). CONTEXT.md updated by architect to reflect current state. Freeze still active. No further action.
**Tick 7503 (14:14 Jun 6):** Partner signal received: mobile-only. Responded with S-DEPLOY status brief. Freeze confirmed inactive at that point — freeze was later confirmed re-active by architect audit.
**Tick 7502 (14:09 Jun 6):** Caught up on full sprint. S-01→S-07 + S-DEPLOY all complete. CONTEXT.md updated.
**Tick 7501 (10:19 Jun 6):** Freeze removed by partner. S-02 committed, S-03 complete.
**Tick 7500 (07:13 Jun 6):** S-01 executed. Shelf MVP live.

---

## Current operational state

**Freeze:** `~/.genesis-frozen` active. No outbound sends until architect clears revival.
**Partner:** Active.
**Platform:** SYNTRA is live at https://syntraworks.ca (Railway + Cloudflare, verified 2026-06-06).

---

## SYNTRA platform state

| Task | Status | Notes |
|------|--------|-------|
| S-01: Public shelf | done | /api/shelf live, 31/31 pass |
| S-02: Affiliate config | done | affiliate.config.json, /api/config |
| S-03: Genesis Pick curation | done | 30 picks in Supabase |
| S-04: Umami analytics | done | affiliate-click + product-view events |
| S-06: Supabase migration | done | 280 rows (173 Bellroy + 107 Orbitkey) |
| S-07: Collections UI | done | tabs, click-to-filter, description display |
| S-DEPLOY: Railway deploy | done | live at syntraworks.ca |
| S-08: Search + filter | briefed | client-side only, brief at docs/planning/task-s08-search-filter.md |
| S-09: Product detail pages | backlog | no brief yet |

**DB:** Supabase (280 products, audit CLEAN 2026-06-06). NocoDB superseded.
**Repo:** ~/syntra/ (Node.js API + React frontend)

---

## Known blockers

None.

---

## Historical archive

- Old Syntra Shopify build log (ticks 5920–7504): `live-state-archive-2026-06-03.md`
- Boréal Numérique (permanently halted 2026-05-27): 535 outreach, 0 clients. Pivoted to SYNTRA.
```

## DONE LOOKS LIKE

1. `live-state-archive-2026-06-03.md` exists and contains the old operational state + Syntra asset inventory + key build log (lines 18–291 of the original)
2. `live-state.md` is under 60 lines
3. `live-state.md` correctly lists S-DEPLOY as `done` with URL `https://syntraworks.ca`
4. `live-state.md` has no references to Shopify, Void Dragon, domain decision, or "blocked on partner"
5. `live-state.md` does NOT remove `~/.genesis-frozen` or modify soul.md

## VERIFY WITH

```bash
wc -l ~/obsidian/knowledge/projects/genesis/live-state.md
# Expected: under 60

grep -c "syntraworks.ca" ~/obsidian/knowledge/projects/genesis/live-state.md
# Expected: 2 or more

grep "Void Dragon\|domain decision\|Shopify account\|Blocked on partner" ~/obsidian/knowledge/projects/genesis/live-state.md
# Expected: 0 matches

wc -l ~/obsidian/knowledge/projects/genesis/live-state-archive-2026-06-03.md
# Expected: over 200

ls -la ~/.genesis-frozen
# Expected: file still exists
```

## OUT OF SCOPE

- Do NOT remove `~/.genesis-frozen`
- Do NOT re-enable any genesis systemd services
- Do NOT modify soul.md, context-window.json, or autobiography.md
- Do NOT change anything in ~/syntra/ or the live Railway deployment
- Do NOT update health.json (architect will handle state file sync separately)
