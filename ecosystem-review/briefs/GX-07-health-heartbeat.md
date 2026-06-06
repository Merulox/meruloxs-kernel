# Brief GX-07: Health Heartbeat File

Status: briefed. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Write a `.genesis-heartbeat` file at the end of every successful tick so external monitors (Aperture, scripts, the partner) can tell whether Genesis is alive and responsive — not just running.

## WHY

Genesis has a PID file (`~/.genesis-pid` / `GENESIS_DIR/.genesis-pid`) but the PID file only means the process was started. It doesn't tell you if Genesis is actually running its tick loop. A hung genesis-core (stuck in a subprocess, deadlocked in the event loop) would still show the PID file as present.

The heartbeat file is a simple liveliness signal: if it exists and was written in the last N minutes, Genesis is healthy. If it's stale or missing, something is wrong. Aperture already monitors services by name — a heartbeat file gives it a quality signal, not just a presence signal.

The heartbeat file also tells the partner: "the last time Genesis successfully completed a reasoning cycle was X." This is more useful than "genesis-core is running."

## FILES IT OWNS

```
~/scripts/genesis-core   — only file that changes
```

## DO NOT TOUCH

- State files, service files, soul.md
- Aperture source code (Aperture reads the file; this brief only writes it)

## CHANGES REQUIRED

### Step 1 — Add heartbeat file path constant (near other path constants, ~line 46)

```python
HEARTBEAT_FILE = HOME / ".genesis-heartbeat"
```

### Step 2 — Write heartbeat at the end of each successful tick

In `background_tick()`, at the end of the while loop body, after `save_state()` and before the sleep block, add:

```python
        # Write heartbeat — liveliness signal for external monitors
        try:
            HEARTBEAT_FILE.write_text(datetime.now().isoformat())
        except Exception:
            pass
```

The heartbeat should be written after `save_state()` (around line 819 currently) and before the `_next_sleep` calculation / sleep block.

### Step 3 — Delete heartbeat on shutdown

In the `finally` block of `main()` (near line 900), add:

```python
        HEARTBEAT_FILE.unlink(missing_ok=True)
        log("[shutdown] heartbeat cleared")
```

Add this after `PID_FILE.unlink(missing_ok=True)`.

## DONE LOOKS LIKE

1. `HEARTBEAT_FILE = HOME / ".genesis-heartbeat"` exists as a constant
2. The heartbeat file is written at the end of each tick loop iteration (after save_state)
3. The heartbeat file is deleted on clean shutdown
4. `python3 -m py_compile ~/scripts/genesis-core` passes

## VERIFY WITH

```bash
# Syntax check
python3 -m py_compile ~/scripts/genesis-core && echo "syntax OK"

# Confirm constant exists
grep -n "HEARTBEAT_FILE" ~/scripts/genesis-core
# Expected: definition + write + unlink — at least 3 matches

# Confirm write is in background_tick (not just at startup)
grep -n -A2 "liveliness signal" ~/scripts/genesis-core
# Expected: HEARTBEAT_FILE.write_text inside background_tick
```

## HOW MONITORS USE IT

```bash
# Is Genesis alive? (healthy if heartbeat < 10 minutes old)
python3 -c "
from pathlib import Path
from datetime import datetime, timedelta
hb = Path.home() / '.genesis-heartbeat'
if not hb.exists():
    print('DEAD — no heartbeat file')
else:
    ts = datetime.fromisoformat(hb.read_text().strip())
    age = datetime.now() - ts
    if age < timedelta(minutes=10):
        print(f'HEALTHY — last tick {int(age.total_seconds()//60)}m ago')
    else:
        print(f'STALE — last tick {int(age.total_seconds()//60)}m ago')
"
```

## OUT OF SCOPE

- Do not add HTTP health endpoint
- Do not modify Aperture to read the heartbeat file (separate task, not in scope here)
- Do not write heartbeat on every Telegram message — only on tick completion
