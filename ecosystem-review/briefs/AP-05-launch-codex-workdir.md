# AP-05: Fix launch-codex working root and allowed dirs

**Status:** briefed  
**Depends on:** none — independent  
**Date:** 2026-06-11  
**Touches:** `~/projects/aperture/src/pages/api/launch-codex.ts` only  
**Priority:** BLOCKER — all AP and WEB executor runs are currently sandbox-blocked

---

## GOAL

When Codex is launched via Aperture's "Send to Codex" button, pass the correct working root (`-C`) and any additional writable directories (`--add-dir`) so the executor can write to the files described in its brief.

---

## WHY

`codex exec` sandboxes writes to the project's working root. `launch-codex.ts` currently spawns Codex with `cwd = ~/agent-infra` for all EX/AP/WEB briefs (because that's where the brief files live). Any brief that touches a different directory gets its writes rejected:

- AP-03a needed `~/projects/aperture` → blocked
- WEB-01 needed `~/.config/systemd/user` → blocked
- All future AP/WEB executor runs have the same problem

`codex exec` has two relevant flags:
- `-C <DIR>` — sets the agent's working root (affects sandbox)
- `--add-dir <DIR>` — adds an additional writable directory (can repeat)

---

## CURRENT STATE

`projectRootForBrief()` in `launch-codex.ts` (line 30–37):
```ts
function projectRootForBrief(briefPath: string): string {
  const resolved = normalizePath(briefPath);
  const knownRoots = [join(HOME, 'syntra'), join(HOME, 'agent-infra')];
  for (const root of knownRoots) {
    if (resolved === root || resolved.startsWith(`${root}/`)) return root;
  }
  return dirname(resolved);
}
```

It returns a single string used as both `cwd` in `spawn()` and nothing else — no `-C` or `--add-dir` flags are passed.

The spawn call (line 79):
```ts
child = spawn(CODEX_CLI, ['exec', '-'], {
  cwd,
  detached: true,
  stdio: ['pipe', logHandle.fd, logHandle.fd],
});
```

---

## FILES IT OWNS

- `src/pages/api/launch-codex.ts` — update `projectRootForBrief()` + spawn call only

---

## DO NOT TOUCH

- Any other file in this repo

---

## IMPLEMENTATION SPEC

### 1. Replace `projectRootForBrief()` with `briefWorkContext()`

Remove the old function. Add a new one that returns `{ cwd, addDirs }`:

```ts
interface WorkContext {
  cwd: string;
  addDirs: string[];
}

function briefWorkContext(briefPath: string): WorkContext {
  const resolved = normalizePath(briefPath);
  const agentInfra = join(HOME, 'agent-infra');
  const syntra = join(HOME, 'syntra');
  const aperture = join(HOME, 'projects/aperture');
  const briefName = basename(resolved);

  if (resolved.startsWith(`${agentInfra}/`) || resolved === agentInfra) {
    // AP-* briefs work in aperture; all others work in agent-infra
    if (/^AP-\d/.test(briefName)) {
      return { cwd: aperture, addDirs: [agentInfra] };
    }
    // WEB-* briefs need ~/.config writable
    if (/^WEB-/.test(briefName)) {
      return { cwd: agentInfra, addDirs: [join(HOME, '.config')] };
    }
    return { cwd: agentInfra, addDirs: [] };
  }

  if (resolved.startsWith(`${syntra}/`) || resolved === syntra) {
    return { cwd: syntra, addDirs: [] };
  }

  return { cwd: dirname(resolved), addDirs: [] };
}
```

### 2. Update the spawn call

In `export const POST: APIRoute`, replace:
```ts
const cwd = projectRootForBrief(briefPath);
```
with:
```ts
const { cwd, addDirs } = briefWorkContext(briefPath);
```

Update the spawn args to include `-C cwd` and `--add-dir` for each extra dir:
```ts
const codexArgs = ['exec', '-', '-C', cwd];
for (const dir of addDirs) {
  codexArgs.push('--add-dir', dir);
}

child = spawn(CODEX_CLI, codexArgs, {
  cwd,
  detached: true,
  stdio: ['pipe', logHandle.fd, logHandle.fd],
});
```

---

## DONE LOOKS LIKE

1. `npm run build` clean, service active
2. `curl -s -H "Authorization: Basic bTpzdA==" -X POST http://localhost:8788/api/launch-codex -H "Content-Type: application/json" -d '{"taskId":"TEST","taskTitle":"test","briefPath":"~/agent-infra/ecosystem-review/briefs/AP-03a-react-migration.md","prompt":"echo hello"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d)"` — returns `{"ok": true, "jobId": "...", "pid": ...}`
3. `cat ~/.local/share/aperture/jobs/<that-jobId>.log` — shows `hello` (Codex ran the echo in `~/projects/aperture`)
4. `git status` clean — all changes committed
5. AP-05 status set to `review` in `~/agent-infra/ecosystem-review/briefs/README.md`

---

## VERIFY WITH

```bash
cd ~/projects/aperture && npm run build 2>&1 | tail -3
systemctl --user restart aperture && systemctl --user is-active aperture

# Confirm the spawn args include -C and --add-dir for an AP brief
grep -n "codexArgs\|add-dir\|briefWorkContext" src/pages/api/launch-codex.ts

cd ~/projects/aperture && git status --short
```

---

## OUT OF SCOPE

- Changing the sandbox mode (`--sandbox`) — `workspace-write` (default) is correct
- Adding support for briefs in other locations
- Changes to any other file

---

## HANDOFF PROMPT

```
Read ~/agent-infra/agents/executor.md.
Then read ~/agent-infra/ecosystem-review/briefs/AP-05-launch-codex-workdir.md and implement it.
The working directory for this task is ~/projects/aperture.
When done: commit all files, set AP-05 status to `review` in ~/agent-infra/ecosystem-review/briefs/README.md.
```
