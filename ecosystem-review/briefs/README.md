# Executor Briefs — Post-Review Action Sequence

From the Realm forensic review (2026-06-05). **PO decision: REVIVE Genesis/Realm** (not retire).
Execute in dependency order. Each is a self-contained executor handoff.

| ID | Status | Title | Why | Touches | Risk gate | Depends On |
|----|--------|-------|-----|---------|-----------|------------|
| EX-1 | `done` | Back up the engine | Loss-prevention — do first | ~/scripts | Secret-scan before push | — |
| EX-2 | `done` | Push new repos | After engine is safe | agent-infra, aperture, genesis | Genesis memory must NOT be committed | — |
| EX-3 | `done` | Wire Aperture → live monitor | Activates the crown jewel | aperture (read realm/monitor) | read-only | — |
| EX-4 | `done` | Archive Realm's frozen 80% | Make live ≠ dead legible | realm/_archive | move never delete | — |
| EX-5 | `done` | Genesis safety gates | Prerequisite for revival | ~/scripts/genesis-core | do before genesis-core starts | — |
| EX-6 | `done` | Index the brain-* engine | Cleanup, lowest urgency | scripts (BRAIN_INDEX.md) | classify only | — |
| AP-01 | `done` | Taskboard — /tasks page | Aperture improvement | aperture | read-only | — |
| AP-01b | `done` | Taskboard UX (copy, badges, refresh) | Aperture improvement | aperture | read-only | — |
| AP-02 | `done` | Codex launch buttons + instance monitoring | Launch Codex from Aperture; watch progress in-dashboard | aperture | spawns child processes | — |
| AP-03 | `superseded` | Full SPA migration (original, too large) | Decomposed into AP-03a/b/c after two failed executor runs | — | — | — |
| AP-03a | `done` | React migration + all panels (no SSE) | Foundation — replaces DOM-thrashing substrate; full feature parity first | aperture | full page migration; keep tasks.astro.bak until verified | — |
| AP-03b | `done` | SSE log streaming | Streams log bytes live; depends on AP-03a | aperture/api | requires running job to test | AP-03a |
| AP-03c | `briefed` | Haiku activity summaries | One-line Claude summary per running job; depends on AP-03b | aperture/api | Claude API call per job per 15s | AP-03b |
| AP-04 | `done` | Sequential dependency gates on taskboard | AP-03b/c buttons are indistinguishable from AP-03a — ordering must be enforced visually | aperture | read-only | AP-03a |
| AP-05 | `done` | Fix launch-codex working root + allowed dirs | AP/WEB executor runs sandbox-blocked; Codex writing outside agent-infra is rejected | aperture/api | BLOCKER | — |
| AP-06 | `done` | Backup status in system health panel | backup-r2 runs daily but has no visibility in dashboard | aperture | read-only | — |
| AP-07 | `briefed` | Executor escalation widget | Exit-0-but-blocked jobs are currently invisible; surface them in taskboard | aperture | read-only | — |
| WEB-01 | `done` | Fix log-digest — restore daily merulox.com log tab | claude-ops pause blocks API call since May 17; auto-deploy commented out | log-digest.service | one paid Claude call/day; Cloudflare Pages deploy | — |
| WEB-02 | `briefed` | Media/attachments on /thinking | X posts with images render as plain text — missing visual context | ~/website/extension + thinking.astro | read-only | — |
| GX-01 | `done` | Compact live-state.md | Genesis revival prerequisite — stale knowledge base | genesis live-state only | read/write live-state, no service changes | — |
| GX-02 | `done` | Session-limit detection in genesis-core | Genesis revival prerequisite — silent failure mode | ~/scripts/genesis-core | syntax change only, freeze stays active | — |
| GX-03 | `done` | Live context injection | Fixes stale knowledge — injects TASKS.md + CONTEXT.md + git log into every call | ~/scripts/genesis-core | adds reads to system prompt | — |
| GX-04 | `done` | Role constraints + verification-first rule | Prevents garbage briefs — explicit scope boundary + verify-before-claim rule | ~/scripts/genesis-core | system prompt string only | — |
| GX-05 | `done` | Tick context isolation | Ticks get fresh context, not stale conversation history — cheaper + more accurate | ~/scripts/genesis-core | changes what gets passed to call_api() | — |
| GX-06 | `done` | Async summarize fix | maybe_summarize() blocks the event loop for 30–90s — drops Telegram messages | ~/scripts/genesis-core | async/await change only | — |
| GX-07 | `done` | Health heartbeat file | Write ~/.genesis-heartbeat each tick — external monitors can detect hung processes | ~/scripts/genesis-core | adds 3 lines | — |
| MO-01 | `review` | Money panel in command-center | Audit G-01 — 3 dashboards, none shows a dollar; loop A+B | ~/scripts/command-center | read-only | — |

## Architecture rationale
See `ecosystem-review/GENESIS_ARCHITECTURE.md` for the full design doc.
GX-03 + GX-04 can run in parallel (different functions). GX-05 depends on GX-03 (ticks rely on system prompt for state after history is removed).

## Handoff to executor (per brief)
> Read `~/agent-infra/agents/executor.md`. Then read `~/agent-infra/ecosystem-review/briefs/EX-N-*.md` and implement it. Report raw verify output back to the architect.

## Architect retains
- Verifying each brief against live state before accepting
- The actual genesis-core revival (only after EX-5 verified)
- Review of EX-1/EX-2 (secrets) and EX-5 (safety) — these are the high-stakes ones; recommend a Reviewer pass

## Notes
- EX-1, EX-2 create GitHub repos via `gh` — if `gh` isn't authed, executor stops and PO runs `gh auth login`.
- EX-2 + EX-5 are the two where a mistake is costly (leaked memory / unsafe revival) → Reviewer gate.
