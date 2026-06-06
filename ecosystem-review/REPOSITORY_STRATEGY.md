# REPOSITORY_STRATEGY.md

**Date:** 2026-06-05 · **Reviewer:** Architect

---

## Recommendation: **multiple focused repos + private-by-default, not a monorepo**

**Why not a monorepo:** these systems have different audiences (public product vs private agent vs personal memory), different lifecycles (SYNTRA shipping vs Realm archiving), and different secrecy levels. A monorepo would force the most-private thing (Genesis memory) to share a boundary with the most-public (merulox.com). Wrong coupling.

**Why not "one repo each for everything":** Realm's frozen bulk and the brain-* sprawl don't deserve polished repos; they deserve archives. Over-repo-ing chaos just preserves chaos with ceremony.

**The rule:** *A repo per coherent, independently-evolving unit. Archive the rest. Keep secrets out of git entirely.*

---

## Proposed GitHub layout

| Repo | Visibility | Contains | Status |
|------|-----------|----------|--------|
| `Merulox/SYNTRA` | **private** (→ public-ready storefront later) | engine, web, storefront, docs | exists ✅ |
| `Merulox/meruloxs-terminal` | **public** | merulox.com (Astro) | exists ✅ |
| `Merulox/agent-infra` | **public** (no secrets) | roles, workflows, templates, MVAOS, ecosystem-review | new — push |
| `Merulox/aperture` | **private** | Genesis/Realm dashboard | new — push (private) |
| `Merulox/genesis` | **private** | daemon, bridge, nix — **code only, NOT memory** | new — push (private) |
| *(no repo)* `realm` | — | archive in place; optionally a private `realm-archive` snapshot | do not polish |

### Hard rules for secrets / personal data
- **Genesis identity & memory** (`~/obsidian/knowledge/projects/genesis/` — soul, autobiography, patterns) → **never in any git repo.** Back up encrypted, separately. The genesis *code* repo must `.gitignore` all vault paths.
- **`.env` / NocoDB tokens / API keys** → never committed (SYNTRA already gitignores `.env`; verify the others).
- **Obsidian vault** → personal; keep in its own private backup (Syncthing/encrypted), not a public repo.
- **CRM / leads / Boréal client data** → private, out of any portfolio repo.

---

## What to do with Realm specifically

Realm is not one coherent unit — it's a frozen substrate + one live monitor + an engine that lives elsewhere. Don't make it a showcase repo. Instead:

1. **Split the live from the dead:**
   - Live: `monitor/`, MANIFEST auto-gen, the 2 brain services → these are *infrastructure*, document them in `agent-infra` or a small private `realm-core`.
   - Dead: Boréal `.py` corpus, empty `agents/`, `nursery/`, `outputs/`, stale commons → move to `realm/_archive/`.
2. **Index the engine:** create `~/scripts/BRAIN_INDEX.md` classifying the ~40 brain-* scripts (load-bearing / utility / experiment / dead). The engine is currently un-repo'd loose scripts — at minimum, version `~/scripts/` in a **private** `Merulox/scripts` repo so the working tooling isn't unbacked.
3. **Decide revive-or-retire** (a real fork — see ARCHITECTURAL_CRITIQUE): if Realm/Genesis is revived, `realm-core` + `genesis` become maintained private repos; if retired, snapshot once to `realm-archive` (private) and stop.

---

## Backup posture (orthogonal to GitHub)

- Private repos cover code. They do **not** cover the Obsidian vault or Genesis memory.
- Ensure those have an **independent encrypted backup** (the existing `backup-r2` / `rclone-backup` services — verify they run; the manifest shows them stopped).
- `~/scripts/` (the engine) currently has no repo and no obvious backup — **highest-priority gap**: one `rm -rf ~/scripts` and the working tooling is gone.

---

## Proposed actions (ordered)

1. **Push existing-but-unpushed:** `agent-infra` (public), `aperture` (private), `genesis` (private, memory excluded). SYNTRA already remote.
2. **Create `Merulox/scripts` (private)** and commit `~/scripts/` — back up the engine. Add `BRAIN_INDEX.md`.
3. **Verify .gitignore hygiene** on genesis (no vault paths) and all repos (no .env/tokens).
4. **Archive Realm's dead 80%** in place (`realm/_archive/`); don't repo it.
5. **Confirm vault + memory have encrypted off-machine backup** (separate from git).

---

## One-paragraph summary

Four maintained repos (`SYNTRA`, `meruloxs-terminal` public; `aperture`, `genesis` private), one public methodology repo (`agent-infra`), one private tooling repo (`scripts`), and Realm left as an in-place archive rather than a polished project. Secrets and personal memory never enter git and get their own encrypted backup. This separates audiences cleanly, backs up the currently-unbacked engine, and stops the frozen bulk from masquerading as maintained projects.
