# EX-5b: Genesis Active-Path Guard (A3 real fix + B4 residual)

Status: ready. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.
This brief directly follows EX-5. Two targeted fixes — do not touch anything else.

## WHAT EX-5 LEFT INCOMPLETE

EX-5 implemented A3 (FORBIDDEN_PATTERNS) in `exec_tool()`, but `exec_tool()` has no callers.
The active code path is `claude --print --dangerously-skip-permissions --allowedTools Bash`
at line ~307 in genesis-core. This path bypasses exec_tool entirely.

Additionally, `asyncio.wait_for(consume_stream(), timeout=120)` (B4 residual) was not updated
to use `BASH_TIMEOUT_MAX`.

## GOAL

Guard the active `claude --print` path against self-killing commands, and fix the stream timeout.

## FILES IT OWNS

```
~/projects/genesis/.claude/settings.json    — create (new file)
~/scripts/genesis-core                      — one-line change (stream timeout)
```

## DO NOT TOUCH

- Any other section of genesis-core
- FORBIDDEN_PATTERNS / exec_tool() (keep as-is — it guards the legacy API path)
- Any file in ~/obsidian/

## FIX 1 — A3 active path: settings.json deny list

Create `~/projects/genesis/.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Bash(systemctl*stop*genesis*)",
      "Bash(systemctl*kill*genesis*)",
      "Bash(systemctl*disable*genesis*)",
      "Bash(systemctl*(kill|stop|disable)*claude-bridge*)",
      "Bash(kill*genesis-core*)",
      "Bash(pkill*python*)",
      "Bash(kill -9*)",
      "Bash(rm -rf ~*)",
      "Bash(rm -rf /home*)",
      "Bash(*> ~/.secrets*)"
    ]
  }
}
```

**Why this works:** Claude Code enforces `deny` rules from settings.json even when
`--dangerously-skip-permissions` is active. The flag skips interactive prompts;
the deny list is a hard block that cannot be overridden.

When genesis-core runs `claude --print` from `~/projects/genesis/`, Claude Code
reads `~/projects/genesis/.claude/settings.json` and applies the deny rules to
every Bash tool call in that session.

## FIX 2 — B4 stream timeout

In genesis-core, find the line:
```python
final_text = await asyncio.wait_for(consume_stream(), timeout=120)
```
And the log line just below:
```python
log("[api] claude --print timed out after 120s")
```

Change to:
```python
final_text = await asyncio.wait_for(consume_stream(), timeout=BASH_TIMEOUT_MAX)
```
```python
log(f"[api] claude --print timed out after {BASH_TIMEOUT_MAX}s")
```

`BASH_TIMEOUT_MAX` is already defined at the top of the file (added in EX-5). Do not redefine it.

## DONE LOOKS LIKE

1. `~/projects/genesis/.claude/settings.json` exists and contains the deny list
2. Stream timeout line uses `BASH_TIMEOUT_MAX` not the literal `120`
3. Syntax check passes

## VERIFY WITH

```bash
python3 -c "import ast; ast.parse(open('/home/merulox/scripts/genesis-core').read()); print('syntax OK')"
cat ~/projects/genesis/.claude/settings.json
grep -n "BASH_TIMEOUT_MAX\|timeout=120" ~/scripts/genesis-core
```

Expected:
- settings.json contains the deny list with at least 8 entries
- `timeout=120` does NOT appear in genesis-core
- `BASH_TIMEOUT_MAX` appears in the wait_for line

## OUT OF SCOPE

- Starting genesis-core (architect step, after this is verified)
- Modifying exec_tool() further
- Any change to genesis.nix or service files
