# BX-05a — Make crm.db the sole lead source-of-truth (retire md reads)

**Loop:** A (Boréal cash — every tool must read the real pipeline, not a frozen file)
**Priority:** P2 · **Safety:** `[DATA]` (read-path repointing; reviewer gate) · **Runs through the executor**
**Status:** briefed · **Depends on:** BX-02 (done) · **Split from:** BX-05

## CONTEXT — what's already true (verified 2026-06-13)
The acute BX-05 problems are resolved, so this brief is narrower than the parent:
- **Decoy DBs deleted** (BX-05b, architect): 9 zero-byte boreal `*.db` decoys removed; the only DB left is the real `~/projects/boreal-leads/crm.db` (618 leads).
- **`crm.md` / `leads.md` no longer exist** as state files anywhere.
- **`outreach-batch` already reads `crm.db`** (not crm.md).
- The lead-acquisition pipeline is: scrapers (`lead-gen`, `lead-scraper`) → write `~/projects/boreal-leads/leads.md` (ephemeral staging) → `boreal-import-leads` parses it → `crm.db`. **This staging flow is fine and stays.**

So `leads.md` is allowed to exist transiently as a scraper→importer handoff. What's NOT allowed: any tool treating a `.md` file as a **source of truth** for lead state (stage, replies, notes). That truth is `crm.db` only.

## GOAL
Audit every `~/scripts` file that references `crm.md`/`leads.md`, classify each reference, and fix the ones that **read md as a source of truth** to read `crm.db` (via `crm_lib`/`boreal_db.py`). Leave the scraper→importer staging use of `leads.md` intact. **Do not touch live SMS services** (see DO NOT TOUCH).

## WHY
~18 scripts still reference `crm.md`/`leads.md`. With those files now absent, any script that *read* them as truth is silently broken or running on empty/fallback data — a correctness hole in the cash pipeline. Repointing them to `crm.db` closes it. (Stack audit §2.1/§2.3.)

## FILES IT OWNS
Audit scope (read all, classify each): every file from
`grep -rlE "crm\.md|leads\.md" ~/scripts` (excluding BRAIN_INDEX).
Fix scope (edit only those that **read md as source of truth**), expected to include:
- `~/scripts/lead-followup-check`
- `~/scripts/signals-updater`
- `~/scripts/outreach-optimizer`
- `~/scripts/lead-inbox`
- `~/scripts/conversations`
- `~/scripts/track-dialogue`
- `~/scripts/night-ops`
- `~/scripts/outreach`
…and any other read-as-truth case the audit finds. Repoint reads to `crm_lib`/`boreal_db.py` against `crm.db`.

## DO NOT TOUCH (live services — separate live-tested task, like BX-07)
- `~/scripts/reply-agent`, `~/scripts/sms-inbox`, `~/scripts/sms-webhook` — **live and running.** If they reference md, log it in the audit table but DO NOT edit here.
- `~/scripts/lead-gen`, `~/scripts/lead-scraper` — keep writing `leads.md` as staging (the importer consumes it). Do not redirect them.
- `~/scripts/boreal-import-leads` — it's the legitimate md→db bridge. Leave it.
- `crm.db` itself / `crm_lib.py` schema. No migrations. No sends.

## SPEC
1. **Audit first.** Produce a table (in the implementation report) of every md-referencing script: `path | reference | classification (reads-as-truth / writes-staging / dead-comment / live-service-deferred) | action taken`.
2. For each **reads-as-truth** (and not a DO-NOT-TOUCH file): replace the md read with the equivalent `crm.db` query via `crm_lib`/`boreal_db.py`. Match existing helpers; don't invent a new access layer.
3. For dead references in comments/docstrings: update the comment to say `crm.db`; no logic change.
4. Each edited script must still run: add/verify a `--self-test` or `--dry-run` path and exercise it (no live sends, no service restarts).
5. No writes to `crm.db` data rows; this is read-path repointing only.

## DONE LOOKS LIKE
1. The audit table covers 100% of `grep -rlE "crm\.md|leads\.md" ~/scripts` results.
2. No non-deferred script reads a `.md` file as lead source-of-truth; those now read `crm.db`.
3. Live services (reply-agent/sms-inbox/sms-webhook) untouched but listed as deferred.
4. Every edited script's `--self-test`/`--dry-run` passes (paste output).
5. `leads.md` staging path (scrapers → boreal-import-leads → crm.db) still intact.

## VERIFY WITH (paste raw output)
```bash
grep -rlE "crm\.md|leads\.md" ~/scripts | grep -v BRAIN_INDEX
# For each edited script:
~/scripts/<script> --self-test 2>&1 | tail -5   # or --dry-run
# Confirm no script still treats md as truth (no read of a .md for stage/notes):
grep -rnE "open\([^)]*(crm|leads)\.md|read_text\(\).*\.md" ~/scripts | grep -v BRAIN_INDEX
# Confirm the importer path is untouched:
head -3 ~/scripts/boreal-import-leads
```

## OUT OF SCOPE
- Live SMS services' md references (→ a BX-07-style live-tested task)
- Eliminating `leads.md` staging (the importer pattern stays)
- Any `crm.db` schema change or data write · any send · BX-04 follow-up engine
