# Executor Briefs — Post-Review Action Sequence

From the Realm forensic review (2026-06-05). **PO decision: REVIVE Genesis/Realm** (not retire).
Execute in dependency order. Each is a self-contained executor handoff.

| # | Brief | Why this order | Touches | Risk gate |
|---|-------|---------------|---------|-----------|
| EX-1 | ✅ Back up the engine | Loss-prevention — do first | ~/scripts | Secret-scan before push |
| EX-2 | ✅ Push new repos | After engine is safe | agent-infra, aperture, genesis | **Genesis memory must NOT be committed** |
| EX-3 | ✅ Wire Aperture → live monitor | Activates the crown jewel | aperture (read realm/monitor) | read-only |
| EX-4 | ✅ Archive Realm's frozen 80% | Make live ≠ dead legible | realm/_archive | move never delete |
| EX-5 | 🔄 Genesis safety gates | **Prerequisite for revival** | ~/scripts/genesis-core | do before genesis-core starts |
| EX-6 | ✅ Index the brain-* engine | Cleanup, lowest urgency | scripts (BRAIN_INDEX.md) | classify only |

## Handoff to executor (per brief)
> Read `~/agent-infra/agents/executor.md`. Then read `~/agent-infra/ecosystem-review/briefs/EX-N-*.md` and implement it. Report raw verify output back to the architect.

## Architect retains
- Verifying each brief against live state before accepting
- The actual genesis-core revival (only after EX-5 verified)
- Review of EX-1/EX-2 (secrets) and EX-5 (safety) — these are the high-stakes ones; recommend a Reviewer pass

## Notes
- EX-1, EX-2 create GitHub repos via `gh` — if `gh` isn't authed, executor stops and PO runs `gh auth login`.
- EX-2 + EX-5 are the two where a mistake is costly (leaked memory / unsafe revival) → Reviewer gate.
