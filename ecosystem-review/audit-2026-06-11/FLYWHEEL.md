# FLYWHEEL — 2026-06-11

## The candidates

Two real loops exist. Everything else in the ecosystem is either support or decoration.

### Loop A — Boréal (cash flywheel)

```
INPUT        outreach (SMS/leads — 98 warm responses ALREADY PAID FOR)
PROCESS   →  reply-agent / close-agent → discovery call → install
ASSET     →  paying client + reusable automation templates + CASE STUDY
DISTRIB.  →  case study → warm-network referrals + credible cold pitch
FEEDBACK  →  each install hardens templates → next install cheaper/faster
MORE      →  2 clients → retainer MRR → Track D gate unlocks
```

- **Cycle time:** weeks. **Revenue per turn:** $1.5–3k setup + $300–500/mo.
- **State:** every component built and proven individually; loop has never completed one full turn (case-study gap). Currently switched off at the wall.

### Loop B — SYNTRA (audience flywheel)

```
INPUT        brand catalogs (ingestion pattern: ~1 brief per brand)
PROCESS   →  normalize → audit → curate (Genesis picks) → publish
ASSET     →  593-product catalog + editorial taste + SEO surface
DISTRIB.  →  organic search (S-14 not shipped) → traffic
FEEDBACK  →  Umami analytics → curation + Phase-2 wholesale decisions
MORE      →  affiliate commissions (0 programs confirmed) → fund more curation
```

- **Cycle time:** months (SEO physics). **Revenue per turn:** affiliate margins on wallets — small even when working.
- **State:** asset side excellent; distribution and monetization legs missing.

## The verdict

**Loop A is the flywheel. Loop B is the savings account.**

Loop A turns in weeks, pays in thousands, and its input asset (warm leads) is *perishable* — it loses value every idle day. Loop B's assets are *durable* — the catalog appreciates at rest and grows on executor autopilot at ~1 brief/brand. Forced sequencing: spin A with human attention now; feed B with executor cycles in the background. The current allocation (all attention on B's tooling and the meta-layer, A unplugged) maximizes neither.

Honest caveat: Loop A has never completed a turn, so it is a hypothesis with strong priors (98 responses from 1012 SMS ≈ 9.7% response rate — genuinely good), not a proven engine. That is the argument for spinning it *immediately*, not for hedging: the only way to price the hypothesis is to finish one turn, and the input decays while you wait.

## Minimum system set for Loop A (everything else is optional)

1. claude-ops **resumed** + sms-webhook, missed-call-bot, reply/close agents, calendly-poller, follow-up-* running
2. crm.db + the 98-responder list, sorted by recency
3. calendly + one discovery-call script (call-prep / call-roster scripts exist)
4. One install kit: missed-call-text-back + lead-capture templates (built)
5. Q-04 credit guardrail (so the wall-switch doesn't flip itself again)
6. The lead-decay clock (G-07) as the daily forcing function

Not required for Loop A: Aperture, Genesis, brain-*, realm, agent-infra changes, any dashboard work beyond the money panel.

## Minimum system set for Loop B (background, executor-driven)

1. PO pushes S-10 → executor ships S-14 (SEO) → sitemap into Search Console
2. Q-06 affiliate truth pass (PO afternoon) — without it the loop structurally cannot pay
3. S-17 Peak Design ingest (briefed) and ~1 brand/week thereafter, all via existing pattern
4. Umami numbers into the money panel

## The flywheel rule (standing)

> Before any brief is written, name which loop it spins — A, B, or neither.
> "Neither" briefs require an explicit PO exception, in writing, in DECISIONS.md.

Applied retroactively to June 5–11: ~24 of 30 briefs were "neither." That is the entire diagnosis of this audit in one number.
