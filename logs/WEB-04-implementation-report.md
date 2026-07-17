# Implementation Report: WEB-04 — X workflow hardening

Executor: Codex
Date: 2026-06-14
Brief: `ecosystem-review/briefs/WEB-04-x-workflow-hardening.md`

## What was implemented

The X workflow now classifies replies only from explicit parent evidence, clears stale reply metadata, and refuses to publish replies without parent URLs. Media is preserved through both ingest paths. Deletions use a durable retry queue and recent missing posts require explicit unavailable evidence across three separate hourly runs before reconciliation tombstones them.

Local receiver mutations are serialized. Live KV mutations use verified optimistic retries. Local/live contracts now report schema version 6, use a 1000-post storage limit, and expose publishable/unresolved/invalid-reply diagnostics. A permanent API regression test covers media, stale metadata, invalid replies, tombstones, and concurrent overwrite retry.

The previously deleted `said who` post was manually tombstoned in both local and live stores and verified absent.

## Files created or modified

| File | Action | Notes |
|------|--------|-------|
| `~/website/extension/background.js` | modified | Classification, media, deletion queue/retries, reconciliation, mutation serialization |
| `~/website/extension/x_profile.js` | modified | More reliable delete-confirm capture |
| `~/website/extension/popup.js` | modified | Pending-delete and local/live drift diagnostics |
| `~/website/extension/manifest.json` | modified | Version 2.6 |
| `~/website/extension/SETUP.md` | modified | Workflow contract and recovery behavior |
| `~/website/functions/api/tweets.js` | modified | Validation, media, stale metadata clearing, verified mutation retries |
| `~/website/src/pages/thinking.astro` | modified | Draw reply UI only with a real parent URL |
| `~/website/src/pages/work.astro` | modified | PO-requested GitHub link label |
| `~/website/package.json` | modified | Added test:x |
| `~/website/tests/x-workflow.test.mjs` | created | Permanent API regression test |
| `~/scripts/log-ingest-receiver` | modified | Media, schema diagnostics, 1000 limit, serialized writes |
| `~/website/src/data/tweets.json` | generated change | Live observations and manual tombstone sync |

Unrelated existing/generated changes left untouched: `~/website/src/data/log.json`, `~/kernel/CLAUDE.md`.

## Commands run and output

### Regression test

```text
✔ tweet ingest preserves media, rejects incomplete replies, clears stale metadata, and retries collisions
ℹ tests 1
ℹ pass 1
ℹ fail 0
```

### Receiver fixture

```text
receiver fixtures ok {'archived': 2, 'remaining': 1, 'tombstones': 1}
```

### Build

```text
23:38:13 [build] 13 page(s) built in 1.14s
23:38:13 [build] Complete!
```

### Misclassified quote render check

```text
<article class="work-item tweet-item" data-tweet-index="10">
replyContextBeforeText false
```

### Deleted-post production verification

```text
{ saidWhoPresent: false, tombstoneCount: 1, stored: 206 }
```

## Deviations from the brief

- Cloudflare KV has no transaction primitive in the current binding. The implementation uses unique mutation IDs, read-back verification, bounded retries, and extension-side serialization.
- Production deploy, extension reload, and receiver restart were not performed.
- The workspace moved from `~/agent-infra` to `~/kernel` during implementation.

## Verify commands for the architect

```bash
cd ~/website
npm run test:x
npm run build
node --check extension/background.js
node --check extension/x_profile.js
node --check extension/popup.js
node --check functions/api/tweets.js
```

Expected: one passing X test, 13 built pages, all syntax checks clean.

## Apply required

1. Reload extension version 2.6.
2. Restart `log-ingest-receiver.service`.
3. Deploy the website/API after review.

## Blockers or open questions

None.
