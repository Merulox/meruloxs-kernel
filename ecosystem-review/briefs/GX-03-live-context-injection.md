# Brief GX-03: Live Context Injection in build_system_prompt()

Status: briefed. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Make Genesis reason from live project state on every call instead of stale conversation history. Modify `build_system_prompt()` in `~/scripts/genesis-core` to read TASKS.md, CONTEXT.md, recent git log, and recent live-state ticks at call time and inject them into the system prompt.

## WHY

The current system prompt says "NOTE: Live state is in live-state.md" but never actually reads it. Genesis is told WHERE to look, not given the content. Under token pressure, or in background ticks, Genesis skips reading these files and reasons from 40-message conversation history that may be hours old. This is why it wrote a product brief with hallucinated schema columns — it had no live data.

Injecting fresh state at call time costs ~1000 tokens per call but eliminates the entire class of "Genesis didn't know X had changed" failures.

## FILES IT OWNS

```
~/scripts/genesis-core   — only file that changes
```

## DO NOT TOUCH

- State files in `~/obsidian/knowledge/projects/genesis/`
- `~/syntra/.agent/` files (read-only)
- `~/.genesis-frozen`
- Any systemd service files

## CHANGES REQUIRED

### Step 1 — Add helper function `_read_project_state()`

Add this function after `_read_clock_state()` (around line 152), before `build_system_prompt()`:

```python
def _read_project_state() -> str:
    """Read authoritative project sources and return a compact summary for injection."""
    sections = []

    # TASKS.md — last 20 data rows (skip header)
    tasks_file = HOME / "syntra/.agent/TASKS.md"
    try:
        lines = tasks_file.read_text().splitlines()
        # Find the table rows (lines starting with | S- or | T- or | B-)
        rows = [l for l in lines if l.startswith("| S-") or l.startswith("| T-") or l.startswith("| B-")]
        if rows:
            sections.append("CURRENT TASKS (~/syntra/.agent/TASKS.md):\n" + "\n".join(rows[-20:]))
    except Exception:
        pass

    # CONTEXT.md — current state summary + what is in flight
    context_file = HOME / "syntra/.agent/CONTEXT.md"
    try:
        content = context_file.read_text()
        # Take first 40 lines (summary + in-flight sections)
        trimmed = "\n".join(content.splitlines()[:40])
        sections.append(f"SPRINT CONTEXT (~/syntra/.agent/CONTEXT.md):\n{trimmed}")
    except Exception:
        pass

    # Git log — last 5 commits from syntra repo
    try:
        import subprocess as _sp
        result = _sp.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, timeout=5,
            cwd=str(HOME / "syntra"),
        )
        if result.returncode == 0 and result.stdout.strip():
            sections.append(f"RECENT COMMITS (~/syntra):\n{result.stdout.strip()}")
    except Exception:
        pass

    # Live-state recent ticks — first 20 lines (tick log)
    live_state = HOME / "obsidian/knowledge/projects/genesis/live-state.md"
    try:
        lines = live_state.read_text().splitlines()
        recent = "\n".join(lines[:20])
        sections.append(f"RECENT TICK LOG (live-state.md):\n{recent}")
    except Exception:
        pass

    if not sections:
        return "(project state unavailable)"
    return "\n\n".join(sections)
```

### Step 2 — Inject into `build_system_prompt()`

In `build_system_prompt()`, after the clock line and before the soul document, add:

```python
    project_state = _read_project_state()
```

Then in the return f-string, add the project state section after the clock line:

Replace:
```python
    return f"""You are Genesis. ...

Current time: {ts}
Background tick: {tick}
Token budget: {clock}

SOUL DOCUMENT:
{soul_text}
```

With:
```python
    return f"""You are Genesis. ...

Current time: {ts}
Background tick: {tick}
Token budget: {clock}

LIVE PROJECT STATE:
{project_state}

SOUL DOCUMENT:
{soul_text}
```

## DONE LOOKS LIKE

1. `_read_project_state()` function exists in genesis-core
2. `build_system_prompt()` calls `_read_project_state()` and injects the result
3. The function handles all read failures gracefully (try/except on each section)
4. `python3 -m py_compile ~/scripts/genesis-core` passes (syntax OK)
5. Manual test: call `_read_project_state()` directly and verify it returns TASKS.md rows

## VERIFY WITH

```bash
# Syntax check
python3 -m py_compile ~/scripts/genesis-core && echo "syntax OK"

# Spot-check: does the function exist and return content?
python3 - << 'EOF'
import sys
sys.path.insert(0, '/home/merulox/scripts')
# Can't import directly due to top-level asyncio.run, so just grep
import subprocess
r = subprocess.run(['grep', '-n', '_read_project_state', '/home/merulox/scripts/genesis-core'], capture_output=True, text=True)
print(r.stdout)
EOF

# Confirm injection in system prompt
grep -n "LIVE PROJECT STATE\|_read_project_state\|project_state" ~/scripts/genesis-core
# Expected: function definition, call in build_system_prompt, and f-string injection
```

## OUT OF SCOPE

- Do not add agent-infra or non-SYNTRA project state (SYNTRA is the active project)
- Do not inject the full TASKS.md (too large) — last 20 rows only
- Do not inject full live-state.md — top 20 lines (recent ticks) only
- Do not start/restart genesis-core to test
