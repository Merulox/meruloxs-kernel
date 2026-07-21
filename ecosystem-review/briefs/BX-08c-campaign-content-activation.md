# BX-08c — Campaign content + activation

**Loop:** A (Boréal cash) · **Priority:** P1 (unblocks automated re-outreach) · **Safety:** `[DATA]` — sends live SMS to real leads once timer enabled; PO must review copy before enabling
**Status:** briefed · **Depends on:** BX-08 ✅, BX-08b ✅
**Source:** Architect assessment 2026-07-19 + PO copy approval 2026-07-19

Read `~/kernel/agents/executor.md` before starting.

---

## GOAL

Three new ACTIVE campaigns land in `campaigns.yaml`. The boreal-campaign timer is enabled. Monday 09:15 the machine fires its first cycle against 527+ contactable leads.

## WHY

BX-08 built and verified the engine. `campaigns.yaml` has exactly one entry: `missed-call-pain-v1`, status `KILLED` after 2 cycles with 0% hand-raise. The engine has been sitting idle since June 29. 527 SENT/DRAFTED leads and 25 REPLIED leads are going cold every week without a re-touch.

Root cause of the killed campaign: "réponds OUI" CTA is too binary — it asks nothing about the lead's situation and generates no conversation. The winning opener pattern (proven by 14.2% cold response rate on the original send) is **narrative + diagnostic question**. The new campaigns use that pattern.

## PREREQUISITE

- BX-08 done ✅
- BX-08b done ✅ ([PRÉNOM] substitution live in boreal-campaign)
- PO has reviewed and approved the 3 campaign bodies below (confirmed 2026-07-19)

## FILES IT OWNS

```
~/projects/boreal-leads/campaigns.yaml    — add 3 new campaigns (ACTIVE status)
```

systemd (enable after VERIFY WITH passes):
```
boreal-campaign.timer    — enable with: systemctl --user enable --now boreal-campaign.timer
```

## DO NOT TOUCH

- ~/scripts/boreal-campaign (no code changes in this brief)
- crm.db schema
- followup.yaml or boreal-followup
- Any other script or service

## THE THREE CAMPAIGNS (PO-approved 2026-07-19)

**Campaign A — replied-reengagement-v1** (REPLIED segment, ~25 leads)

These leads replied at least once. They know the brand. Warmer tone — re-open conversation, no pitch.

```yaml
  - id: "replied-reengagement-v1"
    status: "ACTIVE"
    segment_query: |
      SELECT phone FROM leads
      WHERE stage = 'REPLIED'
      AND (last_campaign_touch IS NULL OR last_campaign_touch < date('now','-21 days'))
      LIMIT 25
    body: "Salut — c'est Brad de Boréal. J'avais pensé à toi. Est-ce que le problème de leads manqués est encore là pour toi en ce moment?"
    stop_footer: true
    min_cycles: 1
    kill_threshold_pct: 2.0
    consent_basis: "b2b-implied-published-phone"
```

**Campaign B — narrative-diagnostic-v1** (SENT/DRAFTED cold re-touch, ~527 leads)

Narrative + diagnostic question — matches the proven opener pattern. No "réponds OUI".

```yaml
  - id: "narrative-diagnostic-v1"
    status: "ACTIVE"
    segment_query: |
      SELECT phone FROM leads
      WHERE stage IN ('SENT','DRAFTED')
      AND stage NOT IN ('STOP','DEAD')
      AND (last_campaign_touch IS NULL OR last_campaign_touch < date('now','-14 days'))
      LIMIT 80
    body: "En Mauricie, un plombier a récupéré 4 leads cette semaine — y'étaient allés au voicemail. Son seul changement: une réponse auto en 2 minutes. Ça ressemble à quelque chose que tu vis?"
    stop_footer: true
    min_cycles: 2
    kill_threshold_pct: 0.8
    consent_basis: "b2b-implied-published-phone"
```

**Campaign C — soumission-angle-v1** (SoumissionRenovation-sourced leads only)

Source-specific angle. These leads came from SoumissionRenovation — name the platform, it's contextually accurate.

```yaml
  - id: "soumission-angle-v1"
    status: "ACTIVE"
    segment_query: |
      SELECT phone FROM leads
      WHERE stage IN ('SENT','DRAFTED')
      AND stage NOT IN ('STOP','DEAD')
      AND source LIKE '%soumission%'
      AND (last_campaign_touch IS NULL OR last_campaign_touch < date('now','-14 days'))
      LIMIT 40
    body: "Salut — c'est Brad. T'annonces sur SoumissionRenovation? Combien de demandes tu rates quand t'es sur le chantier?"
    stop_footer: true
    min_cycles: 2
    kill_threshold_pct: 0.8
    consent_basis: "b2b-implied-published-phone"
```

Note: Campaign B and C will overlap on soumission-sourced leads. The idem-key in boreal-campaign deduplicates per campaign — a lead can receive both if they haven't been touched by either. This is acceptable; if the same lead receives both campaigns in one week, that is a content decision to revisit, not a bug.

## DONE LOOKS LIKE

1. `boreal-campaign --dry-run` shows all 3 campaigns with realistic segment counts:
   - `replied-reengagement-v1`: segment_count ~25
   - `narrative-diagnostic-v1`: segment_count ~527
   - `soumission-angle-v1`: segment_count ~89 (architect's count: 89 soumission-sourced leads)
2. body_preview for each campaign shows [PRÉNOM] substituted or cleanly stripped
3. `systemctl --user enable --now boreal-campaign.timer` exits 0
4. `systemctl --user list-timers | grep boreal-campaign` shows next Monday 09:15
5. **No sends occur during implementation** — dry-run only until PO gives explicit go-live

## VERIFY WITH

```bash
# Verify segment counts
boreal-campaign --dry-run 2>&1

# Verify timer installed
systemctl --user list-timers | grep boreal-campaign

# Confirm soumission source count matches expectations
sqlite3 ~/projects/boreal-leads/crm.db \
  "SELECT COUNT(*) FROM leads WHERE stage IN ('SENT','DRAFTED') AND source LIKE '%soumission%'"

# Confirm REPLIED contactable count
sqlite3 ~/projects/boreal-leads/crm.db \
  "SELECT COUNT(*) FROM leads WHERE stage='REPLIED' AND (last_campaign_touch IS NULL OR last_campaign_touch < date('now','-21 days'))"
```

**PO GO-LIVE ACTION** (after executor verifies): The timer is installed but you still need to confirm the first live run. Check Telegram Monday ~09:15 for the campaign summary notification. First send cycle is observable before kill-criteria can trigger.

## OUT OF SCOPE

- Intelligence layer: auto-generating new campaign angles from response data (deferred — needs hand-raise tracking + at least 2 cycles of data before a learning loop is meaningful). Brief: BX-09 when data exists.
- Claude personalization beyond [PRÉNOM]
- followup.yaml / boreal-followup activation (separate PO decision)
- New message variants (iterate after first cycle results land in campaign_runs)
