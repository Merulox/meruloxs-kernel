# AP-03c: Aperture — AI activity summaries for running Codex jobs

**Status:** briefed  
**Depends on:** AP-03b verified and accepted  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/` — one new API endpoint, one component update

---

## GOAL

Add a one-line Claude Haiku activity summary to each running Codex job in the Aperture tasks panel. The summary updates every 15 seconds and describes what the agent is currently doing.

---

## WHY

After AP-03b, you can see the raw log stream in real-time. But the log is verbose — Codex output, git noise, shell commands. A Haiku-generated one-liner ("writing React components for CodexPanel") gives you the signal without reading the noise.

---

## CURRENT STATE (after AP-03b)

- `JobRow.tsx` streams log lines via SSE; no summary display
- No `/api/summarize-job` endpoint exists
- `ANTHROPIC_API_KEY` is set in Aperture's environment (confirm before starting; check `~/projects/aperture/.env` or service env)

---

## FILES IT OWNS

- `src/pages/api/summarize-job.ts` — **new** — calls Claude Haiku with filtered log tail
- `src/components/codex/JobRow.tsx` — **update** — poll summary every 15s, display below log
- `src/styles/global.css` — **update** — add `.job-summary` class

---

## DO NOT TOUCH

- `src/pages/api/log-stream.ts` — no changes
- Any other component or endpoint

---

## IMPLEMENTATION SPEC

### 1. `/api/summarize-job.ts`

```ts
import type { APIRoute } from 'astro';
import Anthropic from '@anthropic-ai/sdk';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { homedir } from 'node:os';

const JOBS_DIR = join(homedir(), '.local/share/aperture/jobs');
const client = new Anthropic();

export const GET: APIRoute = async ({ url }) => {
  const jobId = url.searchParams.get('jobId');
  if (!jobId || !/^[\w-]+$/.test(jobId)) {
    return new Response(JSON.stringify({ summary: '' }), { headers: { 'content-type': 'application/json' } });
  }

  let job: any;
  try {
    job = JSON.parse(await readFile(join(JOBS_DIR, `${jobId}.json`), 'utf8'));
  } catch {
    return new Response(JSON.stringify({ summary: '' }), { headers: { 'content-type': 'application/json' } });
  }

  const raw = await readFile(job.logPath, 'utf8').catch(() => '');
  const lines = raw.split('\n')
    .filter(l => l.trim() && !l.includes('[gitnexus]'))
    .slice(-40)
    .join('\n');

  if (!lines.trim()) {
    return new Response(JSON.stringify({ summary: 'starting…' }), { headers: { 'content-type': 'application/json' } });
  }

  const response = await client.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 30,
    system: 'Output ONE phrase (max 8 words) describing what the agent is doing right now. No punctuation. No filler.',
    messages: [{ role: 'user', content: lines }],
  });

  const summary = (response.content[0] as any).text?.trim() ?? '';
  return new Response(JSON.stringify({ summary }), {
    headers: { 'content-type': 'application/json; charset=utf-8' },
  });
};
```

Install SDK if not present: `npm install @anthropic-ai/sdk`

### 2. JobRow.tsx update

Add a summary poll for running jobs. Display the summary as a small line between the job header and the log.

```tsx
const [summary, setSummary] = useState('');

useEffect(() => {
  if (job.status !== 'running') return;
  const refresh = () =>
    fetch(`/api/summarize-job?jobId=${job.jobId}`)
      .then(r => r.json())
      .then(d => setSummary(d.summary || ''));
  refresh();
  const t = setInterval(refresh, 15_000);
  return () => clearInterval(t);
}, [job.jobId, job.status]);

// In JSX, after the job header badges:
{summary && <span className="job-summary">{summary}</span>}
```

Add to `global.css`:
```css
.job-summary {
  font-size: 0.75rem;
  color: var(--muted);
  font-style: italic;
  padding: 2px 0;
}
```

---

## DONE LOOKS LIKE

1. `npm run build` clean, service active
2. Start a job — after ~15s, a one-line italic summary appears below the job header
3. Summary updates every 15s while the job runs; stops updating when job completes
4. `curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/summarize-job?jobId=VALID_RUNNING_ID"` → `{"summary":"..."}` with 1–8 words
5. `git status` clean — all changes committed
6. AP-03c status set to `review` in `~/agent-infra/ecosystem-review/briefs/README.md`

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture

# Test endpoint with a real running job ID, or any completed job
JOB_ID=$(ls ~/.local/share/aperture/jobs/ | head -1 | sed 's/\.json//')
curl -s -H "Authorization: Basic bTpzdA==" "http://localhost:8788/api/summarize-job?jobId=$JOB_ID"
# Expected: {"summary":"<1-8 word phrase>"}

cd ~/projects/aperture && git status --short
```

---

## OUT OF SCOPE

- Summary history / persistence
- Summaries for completed jobs
- Changing the Haiku model or prompt
- Multiple summary providers

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-03c-haiku-summaries.md and implement it.
Prerequisite: AP-03b must be verified and accepted before starting this brief.
When done: commit all files, set AP-03c status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
```
