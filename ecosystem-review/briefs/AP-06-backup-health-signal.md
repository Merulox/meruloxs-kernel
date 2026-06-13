# AP-06: Aperture — backup status in system health panel

**Status:** briefed  
**Depends on:** none — independent  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/` — two files

---

## GOAL

Show the last backup run time, result (OK / FAILED), and next scheduled run in Aperture's system health panel, alongside the existing service rows.

---

## WHY

`backup-r2` runs daily via systemd timer. Currently there's no visibility into whether it succeeded or when it last ran. The system health panel is the right place — it already shows service statuses from realm's monitor feed.

---

## CURRENT STATE

- `src/lib/data.ts` exports `getDashboardData()` which returns `DashboardData` (includes `monitor.services`)
- `src/pages/index.astro` renders `monitor.services` as a `.service-table` with rows: name | badge | action
- `backup-r2.service` and `backup-r2.timer` exist as systemd user units
- `systemctl --user show backup-r2.timer --property=LastTriggerUSec,NextElapseUSecRealtime` returns microsecond timestamps
- `systemctl --user show backup-r2.service --property=ExecMainStatus,ActiveEnterTimestamp` returns last exit code and start time

---

## FILES IT OWNS

- `src/lib/data.ts` — add `BackupStatus` type, `readBackupStatus()`, and `backupStatus` field to `DashboardData`
- `src/pages/index.astro` — add backup row to system health panel

---

## DO NOT TOUCH

- Any other file

---

## IMPLEMENTATION SPEC

### 1. `src/lib/data.ts` — add backup status

Add import at top:
```ts
import { execSync } from 'node:child_process';
```

Add type:
```ts
export type BackupStatus = {
  lastRun: string;      // human-readable, e.g. "2026-06-11 00:00"
  nextRun: string;      // human-readable
  ok: boolean;          // true if last exit code was 0
  exitCode: number | null;
};
```

Add to `DashboardData`:
```ts
export type DashboardData = {
  // ...existing fields...
  backup: BackupStatus;
};
```

Add function:
```ts
function readBackupStatus(): BackupStatus {
  const fallback: BackupStatus = { lastRun: 'unknown', nextRun: 'unknown', ok: true, exitCode: null };
  try {
    const timerOut = execSync(
      'systemctl --user show backup-r2.timer --property=LastTriggerUSec,NextElapseUSecRealtime',
      { encoding: 'utf8', timeout: 3000 }
    );
    const svcOut = execSync(
      'systemctl --user show backup-r2.service --property=ExecMainStatus,ActiveEnterTimestamp',
      { encoding: 'utf8', timeout: 3000 }
    );

    const props = Object.fromEntries(
      [...timerOut, ...svcOut].split('\n')
        .filter(l => l.includes('='))
        .map(l => l.split('=', 2) as [string, string])
    );

    const parseUsec = (usec: string): string => {
      const n = Number(usec);
      if (!n) return 'never';
      return new Date(n / 1000).toLocaleString('en-CA', {
        timeZone: 'America/Toronto',
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', hour12: false,
      });
    };

    const exitCode = props['ExecMainStatus'] ? Number(props['ExecMainStatus']) : null;

    return {
      lastRun: parseUsec(props['LastTriggerUSec'] ?? '0'),
      nextRun: parseUsec(props['NextElapseUSecRealtime'] ?? '0'),
      ok: exitCode === null || exitCode === 0,
      exitCode,
    };
  } catch {
    return fallback;
  }
}
```

Fix the `props` construction (the spread of strings is wrong above — use this instead):
```ts
const lines = [...timerOut.split('\n'), ...svcOut.split('\n')];
const props = Object.fromEntries(
  lines
    .filter(l => l.includes('='))
    .map(l => l.split('=', 2) as [string, string])
);
```

Wire into `getDashboardData()`:
```ts
export async function getDashboardData(): Promise<DashboardData> {
  const [health, liveState, vitals, mode, monitor] = await Promise.all([...]);
  return {
    health,
    genesis: liveState,
    vitals,
    mode: { ... },
    monitor,
    backup: readBackupStatus(),  // synchronous, fast (<100ms)
  };
}
```

### 2. `src/pages/index.astro` — add backup row

In the system health panel, after the service-table or as a dedicated row before it, add:

```astro
<div class="service-row">
  <span class="service-name">backup-r2</span>
  <span class={`badge badge-${backup.ok ? 'green' : 'red'}`}>{backup.ok ? 'OK' : `FAILED (exit ${backup.exitCode})`}</span>
  <span class="service-action">last: {backup.lastRun} · next: {backup.nextRun}</span>
</div>
```

Place it as the **first** row inside the `.service-table` block, before the `monitor.services.map(...)` rows. If `monitor.services` is empty, the backup row should still appear — extract the backup row outside the conditional:

```astro
<div class="service-table">
  <div class="service-row">
    <span class="service-name">backup-r2</span>
    <span class={`badge badge-${backup.ok ? 'green' : 'red'}`}>
      {backup.ok ? 'OK' : `FAILED (exit ${backup.exitCode})`}
    </span>
    <span class="service-action">last: {backup.lastRun} · next: {backup.nextRun}</span>
  </div>
  {monitor.services.length > 0 && monitor.services.map((service) => (
    <div class="service-row">
      <span class="service-name">{service.service}</span>
      <span class={`badge badge-${serviceTone(service.status)}`}>{service.status}</span>
      <span class="service-action">{service.action || 'audit snapshot'}</span>
    </div>
  ))}
</div>
```

Remove the old conditional `{monitor.services.length > 0 ? (...) : <p>— monitor feed unavailable —</p>}` and replace with the above.

---

## DONE LOOKS LIKE

1. `npm run build` clean, service active
2. `curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/ | grep "backup-r2"` → returns the backup row HTML
3. The dashboard shows a `backup-r2` row with green OK badge, last run timestamp, and next scheduled time
4. `git status` clean — all changes committed
5. AP-06 status set to `review` in `~/agent-infra/ecosystem-review/briefs/README.md`

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture

curl -s -H "Authorization: Basic bTpzdA==" http://localhost:8788/ | grep -o 'backup-r2.*</div>' | head -1

cd ~/projects/aperture && git status --short
```

---

## OUT OF SCOPE

- Tracking `backup-dotfiles` timer (add later if wanted)
- Restic snapshot count or size
- Click-to-run backup from the dashboard
- Any changes to `backup-now.sh`

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-06-backup-health-signal.md and implement it.
The working directory for this task is ~/projects/aperture.
When done: commit all files, set AP-06 status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
```
