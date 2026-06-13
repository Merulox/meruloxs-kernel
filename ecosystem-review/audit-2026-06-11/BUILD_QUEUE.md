# BUILD QUEUE — 2026-06-11

Estimates: Effort (hours), Impact (1–10), Maintenance (ongoing burden), Compounding (does it get more valuable with use).

---

## Must build immediately

| ID | Build | Effort | Impact | Maint | Compounds | Notes |
|---|---|---|---|---|---|---|
| Q-01 | **Boréal resume** (decision + claude-ops resume + service restart + end-to-end Twilio test + resume runbook) | 2h + 1 decision | 10 | low | YES — every worked lead compounds | Not a build; an op. Gated only on the B-01 decision. If decision = kill, do Q-01b instead: stop boreal-tunnel, archive, write the post-mortem |
| Q-02 | **Push everything** (30 commits; deploy S-10 to Railway) | 1h | 8 | none | — | Unblocks S-14 SEO, closes backup gap |
| Q-03 | **Money panel in command-center** (MRR, pipeline counts, affiliate clicks, API spend, lead-decay clock) | 4h | 8 | low | YES — measurement redirects all future allocation | G-01 + G-07. One brief, executor-able |
| Q-04 | **Credit guardrail** (restart credit-monitor + Telegram threshold alert) | 1h | 7 | none | — | G-02. Prevents repeat of the May 17 cascade |
| Q-05 | **Hook diet** (cap all 5 injection hooks at ~2KB each; index+paths not contents; purge stale instance registry) | 2h | 7 | none | YES — discounts every future agent-hour | G-05 + B-09 cleanup |
| Q-06 | **Affiliate truth pass** (PO: confirm/join Bellroy, Orbitkey, Peak Design programs; record status + rates in affiliate.config.json) | 3h PO admin | 8 | none | YES | G-03. Without this SYNTRA's revenue is structurally $0 |

Total: ~1.5 working days + one strategic decision. Everything above either turns revenue on or stops a known failure from repeating.

## Build later (after the must-list is done)

| ID | Build | Effort | Impact | Maint | Notes |
|---|---|---|---|---|---|
| Q-10 | S-14 SEO metadata (already briefed) | brief | 7 | low | Ship after S-10 deploys |
| Q-11 | S-17 Peak Design ingest (already briefed) | brief | 6 | low | Gate on Q-06 confirming the affiliate path |
| Q-12 | SYNTRA editorial/collection pages (the "taste" moat) | days | 7 | med | Only after traffic exists to read them |
| Q-13 | Boréal case-study writeup (after first install) | 4h | 9 | none | The single highest-leverage marketing asset possible; blocked on a client |
| Q-14 | Canonical task/memory declaration (G-08) + brief archive | 1h | 5 | none | Housekeeping sweep |
| Q-15 | Genesis as scheduled verifier (cron tick that runs VERIFY WITH on open tasks, nothing else) | 2h | 5 | low | The one Genesis use with proven value (ticks 7502–7546). Scope-locked: no identity, no voice |

## Nice but unnecessary (do not let these into a sprint)

- AP-08 Ollama summaries — cosmetic. **Recommend: cancel the brief.**
- Aperture anything further — feature-complete for its actual job
- brain-* selective revival — no consumer for its output exists
- Genesis voice / ambient interface / identity work — vision without a value case
- compounder/commander feature growth — keep as-is
- agent-infra new workflows/templates — methodology is complete; usage, not authorship, improves it now

## Delete forever (anti-queue — ideas that must not be built)

- A seventh memory system / "unified memory layer" rewrite — consolidation by declaration (Q-14), not construction
- A new dashboard of any kind — three exist; none shows money; fix that (Q-03), add nothing
- Realm doctrine v2 / constitution work — archived correctly; leave it
- Multi-agent bus revival for parallel Claude instances — coordination overhead for a one-human shop
- SYNTRA cart/checkout/inventory (Phase 2) before affiliate revenue proves demand — D-006/D-007 already decided this; re-deciding it is drift
