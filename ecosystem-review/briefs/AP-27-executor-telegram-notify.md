# AP-27: Executor completion → Telegram notify (mirror chamber, Stage 1)

**Status:** briefed
**Depends on:** — (delivery path pre-verified by architect 2026-07-03: getMe ok, test message delivered to PO chat)
**Date:** 2026-07-03
**Touches:** `~/projects/aperture/src/pages/api/launch-codex.ts`, new `~/projects/aperture/src/lib/notify.ts`

<!-- gates: depends=; inputs=; confirms= -->

---

## GOAL

Every executor job completion (done / failed / blocked) sends one Telegram message to the PO via @mirrorchamberbot within seconds — task ID, verdict, exit code, blocked reason, commit — so completed work never again sits invisible until someone opens an architect session.

## WHY

Two incidents in three weeks were presence failures, not judgment failures: prod sat stale for 2.5 weeks because nobody knew merged work hadn't shipped (D-012), and S-24 launched+completed by accident with nobody watching (D-014). The completion signal already exists — `launch-codex.ts:467` `child.once('exit', …)` computes `done | failed | blocked` — it just goes nowhere except the jobs file that only an open dashboard reads. This is Stage 1 of the verification loop (deterministic messenger, no LLM). Stage 2 (headless architect verify agent) is a separate future brief and explicitly out of scope.

**Loop:** kernel-layer — serves both Loop A (Boréal briefs) and Loop B (SYNTRA) identically; every project using the executor pipeline inherits it.

## SECRETS (already in place — do not create, do not commit)

`~/.secrets/mirrorchamber-bot.env` (mode 600, created by architect 2026-07-03):
```
TELEGRAM_BOT_TOKEN=…
TELEGRAM_CHAT_ID=…
```
**The token must never appear in any repo file, log line, or error message.** Read the env file at call time; if it's missing, notification is skipped with one console.warn — never crash.

## FILES IT OWNS

- `src/lib/notify.ts` — **new**: `notifyJobComplete(payload)` + tiny env-file reader (KEY=VALUE parse, no new dependency)
- `src/pages/api/launch-codex.ts` — the `child.once('exit', …)` handler (~line 467) and the pre-spawn failure path (~line 461): fire-and-forget call into notify

## DO NOT TOUCH

- Job status classification (`classifyCompletion`), AP-15 commit logic, AP-16 blocked heuristics — consume their outputs, change nothing
- telegram-commander / birdclaw / any other bot (this is a separate, single-purpose channel)
- The jobs file format, ExPanel/SyntraPanel

## IMPLEMENTATION SPEC

### 1. `src/lib/notify.ts`

```ts
export interface JobCompletePayload {
  taskId: string; taskTitle: string;
  status: 'done' | 'failed' | 'blocked';
  exitCode: number | null;
  blockedReason?: string;
  commit?: string;        // latest commit subject+shorthash in the workroot, if any
  durationMs?: number;
  logPath?: string;
}
export async function notifyJobComplete(p: JobCompletePayload): Promise<void>
```
- Read `~/.secrets/mirrorchamber-bot.env` per call (hot-swappable, no caching needed at this volume).
- POST `https://api.telegram.org/bot<token>/sendMessage` via native `fetch`, `chat_id` from env, plain text (no parse_mode — titles contain characters that break Markdown).
- Message format (keep it scannable on a phone):
```
✅ S-26 done · exit 0 · 4m12s
Product conversion pass: related products + price CTA
commit: a1b2c3d Product conversion pass [executor]
```
`✅ done` / `⛔ failed` / `⚠️ blocked` (+ `reason: <blockedReason>` line when blocked). If no commit: `commit: none — check log`.
- **Failure isolation is the hard requirement:** entire body in try/catch; on any error, `console.warn('[notify] …')` with the error message only (never the token, never the full URL) and return. A Telegram outage must not affect job state, the response, or the process.

### 2. `launch-codex.ts` wiring

- In the `child.once('exit', …)` handler, after the job state write: `void notifyJobComplete({...})` — fire-and-forget, not awaited ahead of state persistence.
- `commit`: `git log -1 --format="%h %s"` in the job's workroot (execFile, try/catch → undefined). Runs after AP-15's auto-commit, so the executor's commit is usually what it finds.
- `durationMs` from the job's start timestamp (already tracked).
- Also notify from the spawn-error path (~line 461, status forced to `failed`) — a job that dies at launch is exactly the kind of silent failure this exists for.

### 3. Register the pipeline

```
commander-register mirror-chamber pipeline "executor completion → Telegram (@mirrorchamberbot)" --log ~/projects/aperture/logs/aperture.log
```

## DONE LOOKS LIKE

1. `npm run build` clean; aperture restarted and active.
2. `node -e` smoke test calling `notifyJobComplete` with a fake payload → Telegram API returns `ok:true` and the message lands in the PO chat.
3. With the env file temporarily renamed, the same call logs one warn line and resolves — no throw.
4. A real executor launch (any trivial task) produces a completion message end-to-end.
5. `grep -r "8741904937\|AAETl" src/` → zero hits (token never in code).
6. `git status` clean, changes committed.

## VERIFY WITH (paste raw output)

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture
node --input-type=module -e "
import('./dist-or-src-path/notify.js').then(async (m) => {
  await m.notifyJobComplete({ taskId: 'AP-27', taskTitle: 'smoke test', status: 'done', exitCode: 0, durationMs: 1234 });
  console.log('sent');
});"   # adjust import path to build layout; expect: sent + message in PO Telegram
mv ~/.secrets/mirrorchamber-bot.env /tmp/ && node <same smoke test> ; mv /tmp/mirrorchamber-bot.env ~/.secrets/
# expect: one [notify] warn, exit 0, no crash
grep -rn "8741904937" src/ | wc -l   # expect 0
git status --short
```

## OUT OF SCOPE (Stage 2 — future AP-28, do not start)

- Headless `claude -p` architect verify agent (runs VERIFY WITH, posts verdict + raw evidence, sets `review-passed`/`review-failed`, never `done`; gated by a `<!-- verify: auto -->` brief marker)
- Two-way Telegram (accepting/replying from the phone)
- Batching, quiet hours, message threading, any other bot integration

## HANDOFF PROMPT

```
Read ~/kernel/agents/executor.md.
Then read ~/kernel/ecosystem-review/briefs/AP-27-executor-telegram-notify.md and implement it.
The secrets file already exists — do not create or modify it, and never write the token anywhere.
Report back using ~/kernel/templates/implementation-report.md. Paste raw command output.
```
