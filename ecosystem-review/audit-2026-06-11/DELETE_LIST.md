# DELETE LIST — 2026-06-11

Doctrine-compliant: archive over delete where history has value; delete clones and empties outright. Total execution time: one afternoon. **Nothing here requires a decision beyond reading this file** — except the two PO items at the bottom.

---

## Kill (delete outright)

| Target | Why | Command |
|---|---|---|
| `~/projects/GhostTrack` | Cloned third-party OSINT tool, never integrated, untouched since 04-27. Re-clonable. | `rm -rf ~/projects/GhostTrack` |
| `~/projects/torzu` | Nix packaging experiment, 2 files, 04-17 | `rm -rf ~/projects/torzu` |
| `~/projects/track-dialogue` | A log directory, 04-09 | `rm -rf ~/projects/track-dialogue` |
| `~/projects/_template` | One md file (PRODUCTIZE.md) — move content to vault if wanted, then delete | `rm -rf ~/projects/_template` |
| `~/projects/aperture/src/pages/tasks.astro.bak` | AP-03a verified; backup served its purpose | `rm` |
| Stale instance registry entries (5 dead instances, 60+ days) | Injected as live context every prompt | purge via claude-sessions/workspace.json |

## Archive (move to `~/projects/_archive/`, keep history)

| Target | Why |
|---|---|
| `~/projects/perpetual-optimizer` | April essay experiment; essays may have value, project doesn't |
| `~/projects/fb-poster-workflow` | One orphan n8n workflow.json |
| `~/projects/gumroad-thumbnails` | One PNG; fold into track-c archive |
| `~/projects/track-c` | Gumroad track dormant since 05-06; archive until a deliberate revival decision |
| `~/projects/backup` | One research md; superseded by working restic. Mine the md into vault first if anything's left |
| `~/projects/research` | April-era strategy docs (autonomous-empire.md etc.); move keepers to vault inbox, archive the rest |
| `~/syntra/src/nocodb.js`, `src/cli/nocodb-audit.js`, `nocodb-verify.js`, `add-genesis-pick-field.js` | Supabase is canonical (D-009); keep in git history, move to `~/syntra/src/_archive/` |
| Done executor briefs (EX-1..6, AP-01..07, GX-01..07, WEB-01/02) | History, not guidance → `ecosystem-review/briefs/_done/` |

## Merge / consolidate

| Targets | Into | Why |
|---|---|---|
| 5 task queues | `syntra/.agent/TASKS.md` (project) + `briefs/README.md` (ecosystem) | Declare canon in CLAUDE.md; freeze brain-task queue, Aperture board stays a *viewer* not a source, vault backlog for life-not-engineering only |
| `agent-infra/project/*` | freeze (template exemplar only) | Real state never lived there |
| `agent-infra/mvaos/*` | freeze | Compact duplicates of agents/ |

## Stop pretending (state changes, not deletions)

| Target | Action |
|---|---|
| `boreal-tunnel` | Stop it, OR restart sms-webhook behind it (per B-01 decision). A live tunnel to a dead webhook silently eats real callbacks |
| BRAIN_INDEX "load-bearing" (18 scripts) | Relabel "load-bearing-if-revived"; add revival-requires-brief rule |
| AP-08 brief | Mark `cancelled` in briefs/README — cosmetic |
| ops_state "instance-X online" noise | Silence meta-only bus events |

## Ideas to formally close (attention, not disk)

| Idea | Status to record |
|---|---|
| Genesis voice / ambient interface / identity expansion | Parked indefinitely — revival requires a written value case (DECISIONS.md entry) |
| brain-* engine revival | Same gate |
| Realm doctrine/constitution v2 | Closed — archive is the end state |
| Aperture roadmap beyond AP-07 | Closed — feature-complete |
| Multi-instance Claude bus | Closed — one-human shop |

## Requires PO decision (do not execute unilaterally)

1. **NocoDB cloud account** — cancel/export. Data superseded by Supabase, but it's a paid external account: PO confirms.
2. **Boréal: resume or kill (B-01).** Everything in "Stop pretending" row 1 follows from this.
