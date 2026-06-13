# COMPOUNDING ANALYSIS — 2026-06-11

Assets appreciate with time or use. Liabilities decay and demand maintenance to stand still.

---

## Assets (rank-ordered by compounding rate)

| # | Asset | Why it compounds | Current state |
|---|---|---|---|
| 1 | **Boréal CRM — 98 warm responders** | Each contact cost real SMS spend; a closed install becomes a case study that makes every future close cheaper. **Highest-value AND fastest-decaying asset in the ecosystem** — it compounds only if worked, and it's been idle 25 days. | ⛔ Decaying daily |
| 2 | **SYNTRA Supabase catalog (593 products, audit CLEAN)** | Every brand added makes the site more complete, the SEO surface larger, the curation more credible. Data survives any frontend rewrite. | 🟢 Growing |
| 3 | **SYNTRA ingestion pattern (probe→normalize→ingest→audit)** | Marginal cost per new brand is now ~1 brief. 4 brands prove the pattern. This is process capital, not code. | 🟢 Proven |
| 4 | **Obsidian vault (4,400 notes + claims + ingest pipeline)** | Knowledge graph genuinely accrues; claims feed decisions via injection. | 🟢 Healthy (injection oversized — see B-03) |
| 5 | **agent-infra methodology** | Each brief executed refines the protocol; violation→tightening loop demonstrably works (S-15, B-02, D-010). | 🟢 Mature — compounding has plateaued; further investment is decoration |
| 6 | **merulox.com + automated content feeds** | Public reputation accrues passively; log/reading/music/tweets pipelines feed it without marginal effort. | 🟢 Healthy |
| 7 | **restic→R2 backup chain** | Every snapshot increases recoverable history at near-zero marginal cost. | 🟢 Verified healthy |
| 8 | **Boréal automation templates (missed-call-text-back, follow-up sequences)** | Once one client install exists, the same templates redeploy — the productized-workflow thesis. Currently potential energy only. | 🟡 Built, unproven on a paying client |
| 9 | **DECISIONS.md ledgers (D-001..D-010 etc.)** | Decisions never get re-litigated; each entry permanently cheapens future context recovery. | 🟢 Working |
| 10 | **GitHub remotes (6 repos)** | History + offsite redundancy. | 🟡 30 commits unpushed — an asset only when pushed |

## Liabilities (rank-ordered by carrying cost)

| # | Liability | Decay mode | Carrying cost |
|---|---|---|---|
| 1 | **Per-prompt hook injections (~100KB)** | Stale content auto-injected forever; every session pays it | Tokens + latency + attention, ~25k tokens/turn |
| 2 | **brain-* engine (53 scripts, stopped)** | Bitrot against moving hooks/paths; "load-bearing" labels demand phantom maintenance | Attention + false obligations |
| 3 | **Aperture beyond MVP** | Dashboards depreciate the moment the thing they watch changes; SSE/React surface now needs upkeep | Maintenance burden bought with the week's biggest engineering spend |
| 4 | **Genesis identity/voice/ambient vision** | The unbuilt 90% generates pull ("revival") without a value case; memory files age | Attention gravity |
| 5 | **Stale registries** (instance bus: 5 dead instances; ops_state noise; BRAIN_INDEX labels) | Wrong information injected as truth | Misleads every session that reads it |
| 6 | **NocoDB remnants** (cloud account, nocodb.js, audit CLIs) | Superseded; a second "source of truth" that isn't | Confusion risk |
| 7 | **Executor briefs (30 files)** | One-shot artifacts; valuable as history, dead as guidance | Low — archive after done |
| 8 | **Dead ~/projects dirs** (8 of them) | Pure namespace clutter | Low individually, nonzero in every `ls` and manifest scan |
| 9 | **Dirty working trees** | Uncommitted/unpushed work is unbacked-up work (restic mitigates, git doesn't see it) | Risk, not cost |

## The asymmetry that decides the next 30 days

The top two assets tell the whole story:

- Asset #1 (CRM) **decays** if untouched — it has a half-life measured in weeks.
- Asset #2 (catalog) **keeps** — it appreciates at rest.

So sequencing is forced: **work the decaying asset first** (Boréal pipeline + 98 leads), and let the durable asset grow on executor autopilot (brand ingestion is already a solved, briefable pattern). The current allocation is exactly backwards.

## What "compounding" does NOT include

Aperture features, Genesis prompts, brain revival, new workflows, new templates, new dashboards. These are all *multipliers with no multiplicand*: they multiply product output, and product output is the scarce term. A 10× methodology applied to 0 revenue work is 0.
