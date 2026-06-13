# DEPENDENCY GRAPH — 2026-06-11

## Value chain (who actually creates value vs. who supports whom)

```
                        ┌─ CREATES VALUE ─────────────────────────────┐
                        │ Boréal pipeline ──→ clients ──→ MRR   [OFF] │
                        │ SYNTRA catalog ──→ traffic ──→ affiliate $  │
                        │                    [traffic engine missing] │
                        │ merulox.com ──→ reputation/distribution     │
                        │ Obsidian vault ──→ better decisions         │
                        └──────────────▲──────────────────────────────┘
                                       │ supports
        ┌──────────────────────────────┴───────────────────────────┐
        │ agent-infra (methodology) — multiplies executor output   │
        │ Aperture — launches/monitors executors                   │
        │ Genesis — cheap architect-verifier ticks                 │
        │ backup-r2, GitHub — loss prevention                      │
        │ commander — ops visibility                               │
        └──────────────────────────────▲───────────────────────────┘
                                       │ supports the supporters
        ┌──────────────────────────────┴───────────────────────────┐
        │ brain-* engine [OFF], instance bus, realm monitor,       │
        │ session hooks, MANIFEST autogen, gitnexus                │
        └──────────────────────────────────────────────────────────┘
```

**Rule of thumb exposed by the graph:** value flows DOWN the page in attention and UP the page in dollars. June's engineering hours went almost entirely to rows 2–3. Row 1 is where every dollar lives, and half of it is off.

## Attention economics per system

| System | Creates value directly? | Compounds? | June attention consumed | Verdict |
|---|---|---|---|---|
| Boréal pipeline | YES (only MRR path) | YES (templates → next client cheaper) | ~0 | Starved |
| SYNTRA | YES (eventually) | YES (catalog + pattern) | Medium | Correctly fed |
| merulox.com | Indirect | YES (content accrues) | Low | Correct |
| agent-infra | No (multiplier) | YES, but diminishing — methodology is complete | Medium | Overfed; freeze |
| Aperture | No (meta) | NO — dashboards don't compound, they depreciate | **HIGH (8 briefs, SPA rewrite)** | Heavily overfed |
| Genesis/brain/realm | No | NO while off | Medium (7 GX briefs) | Overfed relative to return |
| Vault + hooks | Indirect | YES | Low | Correct, needs a trim |

## Single points of failure

| SPOF | Blast radius | Mitigation state |
|---|---|---|
| **Anthropic API credits** | Proven, not hypothetical: depletion paused claude-ops (05-17) → killed Boréal pipeline, broke log-digest for 3 weeks (WEB-01), blocked AP-03c. One billing event silently turned off the business. | ⛔ credit-monitor service exists and is STOPPED. Worst SPOF because it already fired once. |
| **PO-as-deploy-button** | S-10 (path routing + SEO prerequisite) done since 06-11, undeployed. 30 unpushed commits across 4 repos. Every executor sprint dead-ends at a manual `git push`. | ⛔ No mitigation. Trivial to fix. |
| **merulox attention** | Every decision routes through one human. `rules.md` = "NONE — system halted, awaiting new direction" for 25 days. The whole agent layer idles when the PO does. | Partially by design; the halt-decision gap is the cost. |
| `navi` (single machine) | Everything local | 🟢 Mitigated: restic→R2 nightly verified + GitHub remotes |
| Supabase (single DB) | SYNTRA catalog | 🟡 593 rows reproducible via ingestion scripts; acceptable |
| Railway + Cloudflare | syntraworks.ca uptime | 🟡 Acceptable for pre-revenue |
| Genesis-as-architect | Verification ticks ran via Genesis; if it stays down, verification reverts to manual | 🟡 Acceptable; architect (Claude session) can verify |

## Fragile dependencies

1. **Hooks → every prompt.** 5 injection hooks (vault_claims, obsidian_vault, system_manifest, instance_context, ops_state) fire on every prompt in every session. A bug or bloat in any one taxes ALL work everywhere. Currently injecting ~100KB/prompt including 60+-day-stale instance registry data.
2. **BRAIN_INDEX "load-bearing" labels** → create the illusion that 18 scripts must be maintained. Nothing depends on them while the runtime is off.
3. **boreal-tunnel running against a dead webhook** → a Twilio callback arriving today hits a tunnel that forwards to nothing. Worse than fully off: it looks alive.
4. **affiliate.config.json defaultParam fallbacks** → SYNTRA links carry `?ref=syntra` params that no program recognizes. Clicks generate $0 silently. No reconciliation exists to notice.
