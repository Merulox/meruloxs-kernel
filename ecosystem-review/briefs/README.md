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
| AP-03c | `superseded` | Haiku activity summaries | Implemented but blocked on depleted API key — superseded by AP-08 | aperture/api | — | AP-03b |
| AP-04 | `done` | Sequential dependency gates on taskboard | AP-03b/c buttons are indistinguishable from AP-03a — ordering must be enforced visually | aperture | read-only | AP-03a |
| AP-05 | `done` | Fix launch-codex working root + allowed dirs | AP/WEB executor runs sandbox-blocked; Codex writing outside agent-infra is rejected | aperture/api | BLOCKER | — |
| AP-06 | `done` | Backup status in system health panel | backup-r2 runs daily but has no visibility in dashboard | aperture | read-only | — |
| AP-07 | `done` | Executor escalation widget | Exit-0-but-blocked jobs are currently invisible; surface them in taskboard | aperture | read-only | — |
| AP-08 | `cancelled` | Swap Anthropic SDK → Ollama in activity summaries | Cancelled 2026-06-12 (ecosystem audit): cosmetic; Aperture is feature-complete and frozen | aperture/api | — | AP-03c |
| WEB-01 | `done` | Fix log-digest — restore daily merulox.com log tab | claude-ops pause blocks API call since May 17; auto-deploy commented out | log-digest.service | one paid Claude call/day; Cloudflare Pages deploy | — |
| WEB-02 | `done` | Media/attachments on /thinking | X posts with images render as plain text — missing visual context | ~/website/extension + thinking.astro | read-only | — |
| GX-01 | `done` | Compact live-state.md | Genesis revival prerequisite — stale knowledge base | genesis live-state only | read/write live-state, no service changes | — |
| GX-02 | `done` | Session-limit detection in genesis-core | Genesis revival prerequisite — silent failure mode | ~/scripts/genesis-core | syntax change only, freeze stays active | — |
| GX-03 | `done` | Live context injection | Fixes stale knowledge — injects TASKS.md + CONTEXT.md + git log into every call | ~/scripts/genesis-core | adds reads to system prompt | — |
| GX-04 | `done` | Role constraints + verification-first rule | Prevents garbage briefs — explicit scope boundary + verify-before-claim rule | ~/scripts/genesis-core | system prompt string only | — |
| GX-05 | `done` | Tick context isolation | Ticks get fresh context, not stale conversation history — cheaper + more accurate | ~/scripts/genesis-core | changes what gets passed to call_api() | — |
| GX-06 | `done` | Async summarize fix | maybe_summarize() blocks the event loop for 30–90s — drops Telegram messages | ~/scripts/genesis-core | async/await change only | — |
| GX-07 | `done` | Health heartbeat file | Write ~/.genesis-heartbeat each tick — external monitors can detect hung processes | ~/scripts/genesis-core | adds 3 lines | — |
| MO-01 | `done` | Money panel in command-center | Audit G-01 — 3 dashboards, none shows a dollar; loop A+B | ~/scripts/command-center | read-only | — |
| HK-01 | `done` | Hook diet — cap per-prompt injection ≤10KB | Audit G-05 — ~100KB/prompt tax on every session; PO exception granted | hook scripts (emit only) | all sessions affected — test in throwaway session | — |
| BX-01 | `done` | Single send gateway for Boréal outbound SMS | **Live test PASSED 2026-06-13 11:04** — real Twilio send (SID SMb928a8…) to PO phone, exit 0, DB row + gateway log written, all 6 gates proven against live DB. Unblocks AP-09 send button + sender re-enable (still pending BX-02 + PO go/no-go) | boreal_send.py + boreal-send | [DATA] live test done | — |
| BX-02 | `done` | CRM hygiene — Phase 2 COMMIT | **Verified 2026-06-13:** pipeline_stage→_legacy, stage_v2 promoted, 20 junk deleted, 0 NULL, canonical vocab only, A.S=REPLIED (architect fixed 1 RESPONDED stray), gateway STOP dry-run=exit 2, crm_lib imports clean, sms-inbox restarted. Job flagged `blocked` only on a git-commit attempt (false positive) | crm.db + crm_lib.py + boreal_send.py | done | — |
| BX-03 | `done` | Classifier fallback fix + hot-lead routing | **Verified 2026-06-13 via the AP-12/13 executor** (first real end-to-end run): sms-inbox written (+208/-7), ENGAGED-on-exception → UNCLASSIFIED, retry queue + 🔥 hot-lead Telegram alert landed, `--self-test` PASS, service restarted live & healthy. Job auto-classified `blocked` (executor's sandbox-forbidden self-restart) — architect completed the restart | sms-inbox + retry queue | live restart done | — |
| BX-04 | `briefed` | One follow-up engine + copy rewrite | Stack audit §4–5 — 7 scripts/3 generations, presumptive-call copy, STOP-as-decline, verbatim repeats | boreal-followup (new) + followup.yaml; retires 7 scripts + 2 timers | no sends; templates DRAFT until PO approves; new timer stays disabled | BX-01 |
| BX-05 | `briefed` | Retire md state + delete 10 decoy DBs | Stack audit §2.1/§2.3 — outreach-batch reads crm.md frozen 05-27; decoys mislead every tool | outreach-batch selection + leads.md/crm.md + decoys | [DATA] Reviewer gate; verify 0-byte before each delete; don't break lead scraping | BX-02 |
| BX-07 | `review` | Migrate live reactive senders to gateway | 100% of outbound must pass STOP check + unified log; reactive class (no cooldown/quiet-hours, separate cap) | boreal_send reactive class + reply-agent/missed-call-bot/sms-webhook send sites | live services, one at a time; live missed-call test with PO | BX-01 |
| AP-09 | `review` | Lead messaging console (/leads) | Files landed + build clean + /leads renders (200). /api/leads 500s on removed _v2 columns → **fixed by AP-14**. After AP-14: verify page + dry-run send | aperture (new page+API) + crm.db read-only | sends ONLY via boreal-send --human-approved; executor tests dry-run only | BX-01, AP-14 |
| AP-10 | `done` | NOW panel — live next-actions feed | Verified 2026-06-12: API live, 7 collectors, owner split, /now + index panel render, degradation handling present | aperture (new page+API), all sources read-only | read-only | — |
| AP-11 | `done` | NOW feed: filter dead/declined leads from urgent bucket | **Verified 2026-06-13:** "now" bucket cut from ~47 to 1 (A.S still present), /next-actions 200. Work landed pre-AP-16 (uncommitted — in the manual pile) | aperture actions.ts + now/* | read-only | — |
| AP-12 | `done` | **Executor work-roots — grant writes where the brief works** (verified 2026-06-13: deriver correct for BX-02/BX-03/AP-13, args emit --add-dir + --skip-git-repo-check, build live) | ROOT CAUSE of silent failures: BX-* run cwd=agent-infra, no --add-dir → all writes to ~/scripts, crm.db, boreal-leads denied. Derive writable roots from each brief's FILES IT OWNS | aperture launch-codex.ts | workspace-write only (no full-access); aperture-only | — |
| AP-13 | `done` | **Executor honest completion — never mark a blocked job done** | Verified 2026-06-13: detector flags real BX-02/BX-03 corpses as blocked + clean→done; restart allowlist excludes aperture; syntra flag fixed; build live (commit ead04d2) | aperture launch-codex.ts + tasks.ts + Taskboard.tsx | changes job-status meaning; allowlisted user-service restarts | AP-12 |
| SYS-01 | `done` | Manifest generator: fix false "all services stopped" | **Verified 2026-06-13:** fix landed (XDG/DBUS re-derived); with bus env stripped manifest-update now reports 14 running services, not all-stopped. Job flagged `blocked` only because its self-test wrote ~/projects/realm (outside owned roots) — code fix is correct | ~/scripts/manifest-update | done | — |
| AP-14 | `done` | Post-BX-02 column cleanup in aperture crm consumers | **Verified 2026-06-13:** zero _v2/pipeline_stage refs remain, build clean, /api/leads → 200 (297 leads), /api/next-actions → 200 with A.S present. (Job flagged `blocked` only because sandbox couldn't curl localhost) | aperture crm.ts + actions.ts | done | BX-02 |
| AP-15 | `done` | Orchestrator commits each task's work on a clean run (no push) | Executors can't/shouldn't commit; today every task's changes pile up entangled. Aperture commits owned files per task (task-tagged, NEVER pushed), like restart-after. Reconciles "don't auto-commit" = don't auto-push | aperture launch-codex.ts + executor.md | local commits only, never push; aperture-only | AP-12, AP-13 |
| AP-16 | `review` | Recalibrate blocked-detection (expected sandbox limits ≠ blocked) | Every job this session false-blocked on "can't verify live endpoint/git/systemctl" → nothing reached `done` → AP-15 commit + restart-after NEVER fired. Bias to done; architect remains the gate | aperture launch-codex.ts + executor.md | classification only | AP-13, AP-15 |

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
