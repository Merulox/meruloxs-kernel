# AP-08: Aperture — swap Anthropic SDK for Ollama in activity summaries

**Status:** briefed  
**Depends on:** AP-03c done (endpoint exists, needs backend swap only)  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/pages/api/summarize-job.ts`, `~/projects/aperture/package.json`

---

## GOAL

Replace the Anthropic SDK call in `summarize-job.ts` with a local Ollama/mistral call so activity summaries work without a paid API key.

---

## WHY

AP-03c is implemented but blocked: the `sk-ant-api03-...` key in `~/.secrets/aperture-env` has zero credits. Claude Code itself runs via OAuth (subscription), not this key. Ollama is already installed and `mistral` is pulled — it's the zero-cost path that works offline.

---

## CURRENT STATE

`src/pages/api/summarize-job.ts` uses `@anthropic-ai/sdk` — installs fine but always returns 500 because the API key has no credits. The file was created by AP-03c executor and is the only consumer of `@anthropic-ai/sdk` in the project.

---

## FILES IT OWNS

- `src/pages/api/summarize-job.ts` — full rewrite of the API call only (keep input/output contract identical)
- `package.json` — remove `@anthropic-ai/sdk` dependency

---

## DO NOT TOUCH

- `src/components/tasks/ExPanel.tsx` — already polls this endpoint correctly
- Any other API endpoint
- `.secrets/aperture-env` — do not touch
- `README.md` in briefs — architect will update statuses

---

## IMPLEMENTATION SPEC

### `summarize-job.ts` — replace SDK call with Ollama fetch

Remove the `@anthropic-ai/sdk` import and top-level `new Anthropic()`. Replace the `client.messages.create()` block with a fetch to Ollama:

```ts
import type { APIRoute } from 'astro';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

const JOBS_DIR = join(homedir(), '.local/share/aperture/jobs');
const OLLAMA_URL = 'http://localhost:11434/api/generate';
const OLLAMA_MODEL = 'mistral';

export const GET: APIRoute = async ({ url }) => {
  const jobId = url.searchParams.get('jobId');
  if (!jobId || !/^[\w-]+$/.test(jobId)) {
    return Response.json({ summary: '' });
  }

  let job: any;
  try {
    job = JSON.parse(await readFile(join(JOBS_DIR, `${jobId}.json`), 'utf8'));
  } catch {
    return Response.json({ summary: '' });
  }

  const raw = await readFile(job.logPath, 'utf8').catch(() => '');
  const lines = raw.split('\n')
    .filter(l => l.trim() && !l.includes('[gitnexus]'))
    .slice(-40)
    .join('\n');

  if (!lines.trim()) {
    return Response.json({ summary: 'starting…' });
  }

  let summary = '';
  try {
    const res = await fetch(OLLAMA_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        model: OLLAMA_MODEL,
        prompt: `Output ONE phrase (max 8 words) describing what this agent is doing right now. No punctuation. No explanation. Just the phrase.\n\n${lines}`,
        stream: false,
      }),
      signal: AbortSignal.timeout(8000),
    });
    if (res.ok) {
      const data = await res.json() as { response?: string };
      summary = data.response?.trim().split('\n')[0] ?? '';
    }
  } catch {
    return Response.json({ summary: 'ollama offline' });
  }

  return Response.json({ summary });
};
```

Key differences from the original:
- `stream: false` — Ollama returns a single JSON object, not a stream
- `AbortSignal.timeout(8000)` — 8s hard timeout; if Ollama is slow or down, returns gracefully
- `.split('\n')[0]` — take only the first line (mistral sometimes adds a newline + explanation)
- Returns `{ summary: 'ollama offline' }` instead of 500 when Ollama is unreachable

### `package.json` — remove `@anthropic-ai/sdk`

```bash
npm uninstall @anthropic-ai/sdk
```

Run this in `~/projects/aperture/` before building.

---

## SETUP NOTE (not executor's job)

Ollama must be running for summaries to work. It's a NixOS system service — start it with:

```bash
systemctl start ollama
```

To enable at boot: `sudo nixos-rebuild switch` with `services.ollama.enable = true` in `configuration.nix`. This is outside the scope of this brief — the endpoint degrades gracefully (`"ollama offline"`) when it's stopped.

---

## DONE LOOKS LIKE

1. `npm run build` clean in `~/projects/aperture/`
2. `package.json` no longer lists `@anthropic-ai/sdk`
3. With `ollama` running: `curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/summarize-job?jobId=<valid-id>"` returns `{"summary":"<non-empty phrase>"}` — phrase is ≤ 8 words, no punctuation
4. With `ollama` stopped: same curl returns `{"summary":"ollama offline"}` (no 500)
5. `git status` clean — committed

---

## VERIFY WITH

```bash
# Build
cd ~/projects/aperture && npm run build 2>&1 | tail -3

# Confirm SDK removed from package.json
grep anthropic ~/projects/aperture/package.json && echo "STILL PRESENT" || echo "removed"

# Restart service
systemctl --user restart aperture && sleep 2 && systemctl --user is-active aperture

# Test with Ollama running
systemctl start ollama && sleep 3
JOB_ID=$(ls ~/.local/share/aperture/jobs/*.json 2>/dev/null | grep -v test | head -1 | xargs basename | sed 's/\.json//')
echo "Using jobId: $JOB_ID"
curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/summarize-job?jobId=$JOB_ID"
echo ""

# Test graceful degradation
systemctl stop ollama
curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/summarize-job?jobId=$JOB_ID"
echo ""

# Git status
cd ~/projects/aperture && git status --short
```

Expected:
- Build output ends with `Complete!`
- `grep anthropic` outputs nothing (removed)
- Service is `active`
- With Ollama: `{"summary":"some phrase here"}` — non-empty
- Without Ollama: `{"summary":"ollama offline"}`
- `git status` clean

---

## OUT OF SCOPE

- Enabling Ollama at boot (NixOS config — PO handles)
- Model selection UI
- Caching summaries between polls
- Switching models (mistral is already pulled and sufficient)

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-08-ollama-summaries.md and implement it.
Working directory: ~/projects/aperture
Run: npm uninstall @anthropic-ai/sdk before building.
When done: commit all changes, paste raw verify output back to the architect.
```
