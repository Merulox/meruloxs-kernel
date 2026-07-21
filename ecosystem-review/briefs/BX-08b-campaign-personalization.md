# BX-08b — Campaign runner: [PRÉNOM] substitution

**Loop:** A (Boréal cash) · **Priority:** P1 (prerequisite for BX-08c) · **Safety:** no sends, script-only change
**Status:** briefed · **Depends on:** BX-08 ✅
**Source:** Architect assessment 2026-07-19 — message library uses [PRÉNOM] but runner sends static body verbatim

Read `~/kernel/agents/executor.md` before starting.

---

## GOAL

`boreal-campaign` substitutes `[PRÉNOM]` in a campaign body with the lead's `name` field from crm.db before sending. If name is NULL or empty string, strip `[PRÉNOM]` cleanly (no literal bracket artifact).

## WHY

The message library (`~/projects/boreal/outreach/message-library/variants/`) uses `[PRÉNOM]` throughout. Without substitution, campaigns either can't use these variants (limiting copy options) or send the literal string `[PRÉNOM]` to every lead — which is worse than no name at all and immediately identifies the message as automated.

The fix is 5–8 lines in `run_campaign()`. The name column is already in crm.db (`leads.name`, populated for the majority of leads). Substitution at send-time, not at campaign definition time.

## PREREQUISITE

- BX-08 done ✅ (`~/scripts/boreal-campaign` exists and dry-run verified)
- No timer enabled — boreal-campaign.timer remains disabled after this brief

## FILES IT OWNS

```
~/scripts/boreal-campaign    — add substitution logic in run_campaign() only
```

## DO NOT TOUCH

- campaigns.yaml (no campaign changes in this brief)
- crm.db schema (name column already exists)
- boreal_send, crm_lib, systemd units
- Any other script

## DONE LOOKS LIKE

1. `boreal-campaign --dry-run` with a campaign body containing `[PRÉNOM]` prints a substituted `body_preview` for a sampled phone (e.g. "Salut Jean —" not "Salut [PRÉNOM] —")
2. A lead where `name` is NULL or `''` produces a clean body — no `[PRÉNOM]` artifact. If the campaign body was `"Salut [PRÉNOM] — Brad."`, the output for a nameless lead is `"Salut — Brad."` (not `"Salut  — Brad."` with double space — strip cleanly)
3. No actual sends, no DB writes — this brief does not activate the timer

## VERIFY WITH

```bash
# Add a test campaign body with [PRÉNOM] to campaigns.yaml (dry-run safe — status DRAFT is never run live):
# body: "Salut [PRÉNOM] — Brad, Boréal Numérique. [diagnostic question]"
boreal-campaign --dry-run 2>&1 | grep body_preview

# Verify a NULL-name lead produces clean output — check a lead with empty name:
sqlite3 ~/projects/boreal-leads/crm.db "SELECT phone, name FROM leads WHERE (name IS NULL OR name='') AND stage IN ('SENT','DRAFTED') LIMIT 1"
# Then confirm body_preview for that phone has no [PRÉNOM] artifact
```

## OUT OF SCOPE

- Owner name (`[NOM]` or similar) substitution
- Multi-variable template support
- Claude-powered personalization
- Enabling boreal-campaign.timer (that is BX-08c)
