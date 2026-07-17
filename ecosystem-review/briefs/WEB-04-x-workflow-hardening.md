# WEB-04 — X workflow hardening

**Loop:** Public website reliability — PO-directed 2026-06-14  
**Priority:** P1 · **Safety:** live public feed and local generated archive  
**Status:** review

## Goal

Make the merulox.com X workflow accurately classify posts, preserve attachments,
reliably remove deleted posts, and keep its local and live stores consistent.

## Audit Findings

Audit run 2026-06-14 across `~/website/extension`, Cloudflare `/api/tweets`,
`~/scripts/log-ingest-receiver`, the generated local archive, and `/thinking`.

1. **High — deletion sync is incomplete.** The delete hook depends on one exact
   desktop-X DOM flow. Mobile/other-browser deletions and missed hooks remain
   published indefinitely. Failed tombstones have no durable retry queue.
2. **High — reply classification has unsafe heuristics.** Adjacent ascending
   timeline posts are treated as self-threads, and permalink inspection treats
   any earlier rendered article as a parent. Quote posts have no explicit
   representation. This caused a quote post to visually attach to an unrelated
   reply.
3. **High — local and live stores drift.** At audit time: local 206 posts, live
   202 posts, four local-only posts, and two reply-metadata disagreements.
4. **Medium — media is dropped at ingestion.** The content script captures
   `media`, and `/thinking` renders it, but both local and Cloudflare ingest paths
   discard it. Local and live media count were both zero.
5. **Medium — Cloudflare KV mutations race.** POST and DELETE are independent
   read-modify-write operations with no conflict detection or reconciliation.
6. **Low — contracts and limits differ.** Extension cache/local archive/live KV
   have different limits and validation rules, making drift difficult to explain.

## Files It Owns

- `~/website/extension/background.js`
- `~/website/extension/x_profile.js`
- `~/website/extension/popup.js`
- `~/website/extension/popup.html`
- `~/website/extension/manifest.json`
- `~/website/extension/SETUP.md`
- `~/website/functions/api/tweets.js`
- `~/website/src/pages/thinking.astro`
- `~/scripts/log-ingest-receiver`
- `~/kernel/ecosystem-review/briefs/README.md`
- `~/kernel/logs/WEB-04-implementation-report.md`

Generated data (`~/website/src/data/tweets.json` and local tombstones) may change
only through the existing receiver workflow.

## Implementation

1. Remove timeline adjacency as an authoritative thread classification.
2. Resolve reply metadata only from explicit reply signals/API/permalink parent
   evidence; standalone resolution must clear stale reply fields.
3. Preserve normalized X media URLs through extension, local receiver, live API,
   and rendering.
4. Persist deletion jobs in extension storage, retry failed local/live targets,
   and make delete-confirm capture independent of mutation timing.
5. Reconcile a bounded set of recent cached posts against logged-in X permalink
   pages; only tombstone after repeated explicit unavailable/deleted evidence.
6. Serialize Cloudflare KV mutations using optimistic revision checks/retries
   where supported by the current endpoint model; expose revision/count metadata.
7. Use one documented post limit and add diagnostics for local/live drift.

## Done Looks Like

- Quote/standalone posts cannot render as replies without a real parent URL.
- Media survives both ingest paths.
- A failed deletion remains queued and retries automatically.
- Recently deleted posts can be reconciled even if deletion happened outside the
  hooked browser flow.
- Local and live feed diagnostics report drift clearly.
- `npm run build`, JS syntax checks, and receiver syntax checks pass.
- No production deploy is performed automatically.

## Verify With

```bash
cd ~/website
node --check extension/background.js
node --check extension/x_profile.js
node --check functions/api/tweets.js
npm run build
python3 -m py_compile ~/scripts/log-ingest-receiver
```
