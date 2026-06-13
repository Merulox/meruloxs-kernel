# SYS-01 — Manifest generator: fix false "all services stopped"

**Loop:** Neither directly — **PO exception: infra integrity.** A lying manifest mis-routes every session that reads it (this session wasted cycles on a false outage). Justified under the standing rule as a correctness fix to the coordination substrate.
**Priority:** P1 · **Safety:** one script, read-only system queries; no service changes
**Status:** briefed · **Depends on:** none · **Runs through the AP-12-fixed launcher** (owns ~/scripts)

## GOAL
`manifest-update` reports true service state regardless of how it's invoked, and when it genuinely cannot query systemd it says so instead of silently declaring every service stopped.

## WHY
`~/scripts/manifest-update:85` `_running_services()` runs `systemctl --user list-units --state=running`. `systemctl --user` needs the user session bus (`XDG_RUNTIME_DIR` + `DBUS_SESSION_BUS_ADDRESS`). When the generator runs from a context without those env vars (timer/hook/non-login spawn), the call returns empty and **every service is reported `⚪ stopped`** — including impossible ones (picom, dunst, redshift on a live desktop). This session twice saw an all-stopped manifest that was pure fiction; it's the same class of bug already fixed in `claude-ops`. The `except: return set()` also masks failures as "nothing running."

## FILES IT OWNS
- `~/scripts/manifest-update` (the `_running_services()` function and its call site in `build_manifest()`)

## DO NOT TOUCH
- Any other section of the manifest (SCRIPTS, SESSIONS, REGISTERED TOOLS)
- The output path / format beyond the RUNNING SERVICES status tokens
- Any systemd unit or service

## SPEC
1. **Inject the session-bus env** before the `systemctl --user` call (the script already `import os`):
   - `XDG_RUNTIME_DIR` → keep if set, else `/run/user/{os.getuid()}`
   - `DBUS_SESSION_BUS_ADDRESS` → keep if set, else `unix:path=/run/user/{os.getuid()}/bus`
   - Pass the merged env via `subprocess.run(..., env=...)`.
2. **Distinguish failure from empty.** Add `check=True`. On `CalledProcessError`/`TimeoutExpired`/empty-when-it-should-not-be, `_running_services()` returns `None` (query failed), NOT an empty set.
3. **Fail honest, not false.** In `build_manifest()`, when `running is None`:
   - Do not mark services stopped. Render each tracked service as `❓ unknown` and add a one-line banner under `## RUNNING SERVICES`: `> ⚠️ systemd user bus unreachable at generation time — service states unknown (not stopped).`
   - Stronger option if cheap: leave the previously-written RUNNING SERVICES block intact (read the prior manifest, preserve that section) so a transient failure doesn't blank good state. If implementing this, only the services section is preserved; timestamp + other sections regenerate.
4. Keep the green/grey tokens unchanged when the query succeeds.

## DONE LOOKS LIKE
1. Running `manifest-update` from a bare env (no bus vars) produces the SAME correct running-set as an interactive run — not all-stopped.
2. If systemd is truly unreachable, the manifest shows `❓ unknown` + the warning banner (or preserves the prior section), never a false all-stopped wall.
3. A normal interactive run is unchanged.

## VERIFY WITH (paste raw output)
```bash
# Correct under interactive env:
manifest-update && grep -A60 "RUNNING SERVICES" ~/projects/realm/MANIFEST.md | grep -c "🟢"   # > 0, matches reality
# Simulate the broken trigger context (strip the bus env):
env -u XDG_RUNTIME_DIR -u DBUS_SESSION_BUS_ADDRESS manifest-update && grep -A60 "RUNNING SERVICES" ~/projects/realm/MANIFEST.md | grep -cE "🟢"   # still > 0 (env re-derived)
# Hard-fail path (point at a dead bus): expect ❓/warning, NOT all ⚪
DBUS_SESSION_BUS_ADDRESS=unix:path=/nonexistent manifest-update; grep -E "unknown|unreachable|🟢" ~/projects/realm/MANIFEST.md | head
systemctl --user is-active aperture   # ground truth to compare against
```

## OUT OF SCOPE
- Whatever timer/hook invokes manifest-update (find it later if the env fix isn't sufficient; the env re-derivation should make the caller irrelevant)
- The SCRIPTS / REGISTERED TOOLS sections
- claude-ops (already fixed)
