# GAPS — Missing Infrastructure (2026-06-11)

Ranked by ROI. Note what is NOT missing first — this ecosystem's instinct is to build, and most classic gaps are already covered:

**Already covered (do not rebuild):** backups (restic→R2, verified), decision logs (DECISIONS.md), session recovery (CLAUDE.md + .agent pattern), agent registry (MANIFEST autogen), workflow registry (agent-infra), code search (gitnexus), observability-of-agents (Aperture + command-center), knowledge search (vault + hooks).

The real gaps are all on the money path:

---

## G-01 — Revenue telemetry · **ROI: 10/10 · Cost: ~half a day**
Three dashboards exist (Aperture, command-center, merulox.com) and none shows a dollar. No MRR figure, no pipeline-stage counts, no affiliate-click→commission view, no SMS-spend tracking. The system optimizes what it measures, and it currently measures agent uptime. **Build: one "MONEY" panel in command-center** (it's already running): Boréal pipeline counts from crm.db, SYNTRA Umami affiliate-click count, API spend, MRR (currently $0 — display it; the zero is the point).

## G-02 — API budget guardrail · **ROI: 9/10 · Cost: ~1h**
Credit exhaustion already caused 3 outages and the 25-day halt. `credit-monitor` exists, stopped. **Restart + wire a Telegram alert at threshold via commander.** Not a build — a restart and ~20 lines.

## G-03 — Affiliate program reconciliation · **ROI: 8/10 · Cost: 1 PO afternoon + tiny config**
No record of which brands actually pay, at what rate, with what attribution. `affiliate.config.json` has the right shape (Secrid's `no_public_program` status proves it) — it's just unpopulated with verified facts for Bellroy, Orbitkey, Peak Design. Gap is admin work, not engineering.

## G-04 — Deploy path that doesn't end at the PO's keyboard · **ROI: 7/10 · Cost: ~1h**
Verified-done work queues behind manual `git push` (30 commits, S-10 hostage). **Build: post-verify auto-push for non-prod repos (agent-infra, aperture, website) via existing timers; keep SYNTRA prod push manual but make it a named PO ritual (daily, 2 minutes).**

## G-05 — Hook budget governance · **ROI: 7/10 · Cost: ~2h**
No cap on what injection hooks may add per prompt; current total ~100KB. **Build: each hook injects ≤2KB (index + paths, not contents); measure once with a one-line byte counter in each hook.** This is negative infrastructure — removing, not adding.

## G-06 — Boréal pipeline resume runbook + dead-man alarm · **ROI: 7/10 (conditional on B-01 decision) · Cost: ~2h**
The pipeline died as a side effect of claude-ops pause and nothing alarmed. `pipeline-integrity-check` exists, stopped. **Restart it + one rule: if sms-webhook is down while boreal-tunnel is up, alert.** Write the resume sequence down once (which units, what order, how to verify Twilio webhook end-to-end).

## G-07 — Lead-decay clock · **ROI: 6/10 · Cost: trivial**
Nothing surfaces "days since last touch" for the 98 CRM responders. One query + a line in the G-01 panel. Makes the cost of limbo visible daily — which is the actual forcing function this ecosystem lacks.

## G-08 — Canonical task/memory declaration · **ROI: 5/10 · Cost: 30min of writing**
Five task queues, six memory layers (B-07). The fix is a paragraph in CLAUDE.md naming the canon (syntra/.agent + briefs/README) and marking the rest frozen. Documentation, not construction.

---

## Explicitly NOT gaps (resist the itch)

- **Multi-machine redundancy** — restic + GitHub is enough at this scale
- **Event sourcing / message bus revival** — brain-bus solved a coordination problem that doesn't exist with 1 active session
- **More observability of agents** — Aperture already exceeds need
- **Error tracking SaaS** — journalctl + the G-06 alarm covers it
- **Asset pipeline / CMS for SYNTRA** — Supabase + ingestion CLIs are the pipeline
- **A new memory system** — the seventh memory system is not the fix for having six
