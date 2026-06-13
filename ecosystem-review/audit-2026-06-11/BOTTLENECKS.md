# BOTTLENECKS — 2026-06-11

Ranked by (severity × ROI-if-solved) / cost-to-solve. Severity 1–10. Cost in real units (hours or decisions).

---

## B-01 — The 25-day halt nobody decided to extend
**Type:** human + economic · **Severity: 10** · **ROI if solved: 10** · **Cost: 1 decision + ~2h ops**

claude-ops was paused 2026-05-17 (credit depletion). The pause took down the entire Boréal pipeline. Credits came back (log-digest, executors, and Genesis ticks all spend API money daily now) — but the pause was never lifted and `rules.md` still reads "system halted, awaiting new direction." This is not a strategic pivot; it's an un-made decision compounding at the rate the 98 warm CRM responses go cold. Solving it costs one decision: **resume Boréal or formally kill Track A.** Either answer beats limbo.

## B-02 — Meta-work ratio: 80% of engineering feeds the machine that watches the machine
**Type:** human · **Severity: 9** · **ROI if solved: 9** · **Cost: discipline, $0**

Of ~30 briefs executed June 5–11, ~24 were Aperture/Genesis/repo/log plumbing. Aperture alone got a React SPA migration, SSE streaming, dependency gates, an escalation widget, and launch buttons — to monitor executors whose total product output this week was 6 SYNTRA tasks. The methodology is good; the allocation it's pointed at is inverted. Fix: hard rule — **no new meta-brief while a revenue brief is open.**

## B-03 — Per-prompt context tax (~100KB injected into every prompt, every session)
**Type:** technical + economic · **Severity: 7** · **ROI if solved: 8** · **Cost: ~2h**

Verified this session: obsidian_vault (~76KB) + vault_claims (~18KB) + system_manifest + instance_context + ops_state fire on EVERY prompt. That's ~25k tokens of overhead per turn across all sessions — paid in API cost, latency, and attention dilution (the model reads stale instance registries and full vault dumps before reading your question). Fix: inject indexes + paths, not contents; cap each hook at ~2KB; let the session read full files on demand. This one fix discounts every future hour of agent work.

## B-04 — SYNTRA has a product but no distribution and no confirmed payer
**Type:** economic · **Severity: 8** · **ROI if solved: 8** · **Cost: S-14 (briefed) + ~3h PO admin**

593 clean products, live site, zero traffic engine (S-14 SEO just briefed, S-10 prerequisite undeployed) and **zero confirmed affiliate programs**: Secrid has none, Peak Design unconfirmed, Bellroy/Orbitkey never verified. Best case today: traffic arrives, clicks happen, $0 accrues. Fix order: push S-10 → ship S-14 → PO spends one afternoon confirming/joining affiliate programs for Bellroy + Orbitkey + Peak Design (Impact.com) → swap real params.

## B-05 — PO-as-deploy-button
**Type:** human · **Severity: 6** · **ROI if solved: 7** · **Cost: ~1h**

30 unpushed commits across 4 repos; S-10 (the SEO prerequisite) finished 06-11 and sits local. Every executor sprint dead-ends at a manual push. Fix: push now; then either grant executor push-after-verify on non-prod repos, or a daily auto-push timer for agent-infra/aperture (docs and internal tools don't need deploy ceremony).

## B-06 — Credit fragility with the monitor switched off
**Type:** technical · **Severity: 6** · **ROI if solved: 7** · **Cost: ~1h**

API credit exhaustion already caused three outages (claude-ops pause, AP-03c block, log-digest 3-week silence). `credit-monitor` exists and is stopped. Fix: restart it, add a hard alert (Telegram via commander) at a balance threshold, and make claude-ops auto-resume a conscious choice with an owner.

## B-07 — Memory fragmentation (6 layers) and task fragmentation (5 queues)
**Type:** technical · **Severity: 5** · **ROI if solved: 5** · **Cost: ~3h consolidation**

Memory: vault, Claude memory dirs, syntra/.agent, agent-infra/project, realm/commons (archived), genesis live-state. Tasks: syntra TASKS.md, briefs/README table, brain-task queue, Aperture taskboard, vault backlog.md. The working pair is clear — **syntra/.agent for project state, briefs/README for ecosystem work** — the rest is drift surface. Fix: declare those two canonical in CLAUDE.md; freeze agent-infra/project/; stop appending to vault backlog for engineering tasks.

## B-08 — "Load-bearing" labels on a dead runtime
**Type:** technical/attention · **Severity: 4** · **ROI if solved: 4** · **Cost: 30min**

BRAIN_INDEX marks 18 brain-* scripts load-bearing while every brain unit has been stopped since 06-03. The label invites maintenance work on a system with no revival case. Fix: reclassify "load-bearing-if-revived"; add one line: *revival requires a written brief with a value case.*

## B-09 — Zombie infrastructure (looks alive, does nothing)
**Type:** technical · **Severity: 4** · **ROI if solved: 4** · **Cost: 1h**

boreal-tunnel runs against a dead webhook (an inbound Twilio callback today would vanish silently). Instance registry shows 5 dead instances from April. ops_state broadcasts "instance-X online" noise every 30min. Fix: stop the tunnel (or restart its webhook with B-01), purge the registry, silence the meta-noise.

## B-10 — Architectural perfectionism as a failure mode with a paper trail
**Type:** human · **Severity: 6** · **ROI if solved: high but unenforceable by tooling** · **Cost: $0**

The pattern across realm (empire doctrine), genesis (identity/voice/ambient vision), brain (53 scripts), aperture (SPA rewrite of a working dashboard): each is a beautifully-governed system one level more abstract than the problem. The 06-05 audit said "subtract and ship" — and the following week shipped mostly governance and dashboards. This audit's only structural defense: the flywheel rule in FLYWHEEL.md and the open-revenue-brief rule in B-02.

---

## Ranking summary

| # | Bottleneck | Sev | ROI | Cost | Priority |
|---|---|---|---|---|---|
| B-01 | Boréal halt un-decision | 10 | 10 | 1 decision | **NOW** |
| B-02 | Meta-work ratio | 9 | 9 | $0, discipline | **NOW** |
| B-04 | SYNTRA distribution + affiliate gap | 8 | 8 | ~1 day | **NOW** |
| B-03 | Per-prompt context tax | 7 | 8 | 2h | **NOW** |
| B-05 | PO deploy bottleneck | 6 | 7 | 1h | NOW |
| B-06 | Credit fragility | 6 | 7 | 1h | NOW |
| B-07 | Memory/task fragmentation | 5 | 5 | 3h | Later |
| B-10 | Perfectionism pattern | 6 | — | $0 | Standing rule |
| B-08 | Dead "load-bearing" labels | 4 | 4 | 30m | Later |
| B-09 | Zombie infra | 4 | 4 | 1h | Later |
