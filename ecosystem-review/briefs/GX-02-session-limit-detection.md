# Brief GX-02: Session-Limit Detection in genesis-core

Status: briefed. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Add session-limit detection to genesis-core so that when `claude --print` returns a rate-limit error string, genesis-core: (1) suppresses the error as a response, (2) sends a Telegram alert, and (3) stops burning ticks until the limit resets.

## WHY

On 2026-06-03, genesis-core received `"You've hit your session limit · resets 9:20pm"` from `claude --print` and treated it as a normal response. It logged it, went dormant on schedule, and restarted 5 minutes later — only to receive the same error again. This continued for 3+ hours with no Telegram notification, no escalation, and no tick throttling. The partner saw silence instead of a clear "I'm rate-limited, back at 9:20pm."

This is a missing guard. EX-5 and EX-5b covered safety gates and tool call limits, but not session-limit handling.

## FILES IT OWNS

```
~/scripts/genesis-core   — the only file that needs changes
```

## DO NOT TOUCH

- `~/obsidian/knowledge/projects/genesis/` — no state files
- `~/projects/genesis/` — no daemon files
- `~/.genesis-frozen` — do not remove
- Any systemd service files

## CHANGES REQUIRED

All changes are in `~/scripts/genesis-core`. There are three parts.

### Part 1 — Session-limit sentinel file path (add near other path constants, ~line 46)

Add this constant after the existing path declarations:

```python
SESSION_LIMIT_FILE = HOME / ".genesis-session-limit"
```

### Part 2 — Detect session-limit in call_api() (~line 356–361)

The current return statement at the end of the `try` block in `call_api()` is:

```python
        final_text = await asyncio.wait_for(consume_stream(), timeout=BASH_TIMEOUT_MAX)
        await proc.wait()
        stderr = await stderr_task
        if stderr:
            log(f"[api] claude stderr: {stderr.decode()[:200]}")
        return final_text.strip() if final_text and final_text.strip() else None
```

Replace the last line with:

```python
        final_text = await asyncio.wait_for(consume_stream(), timeout=BASH_TIMEOUT_MAX)
        await proc.wait()
        stderr = await stderr_task
        if stderr:
            log(f"[api] claude stderr: {stderr.decode()[:200]}")
        if final_text:
            stripped = final_text.strip()
            SESSION_LIMIT_PHRASES = [
                "you've hit your session limit",
                "usage credits required",
                "/usage-credits",
                "session limit",
            ]
            if any(p.lower() in stripped.lower() for p in SESSION_LIMIT_PHRASES):
                log(f"[api] session limit detected — suppressing response, writing sentinel")
                SESSION_LIMIT_FILE.write_text(datetime.now().isoformat())
                return None
            return stripped if stripped else None
        return None
```

### Part 3 — Check sentinel in background_tick() and send alert (~line 809)

In `background_tick()`, after:
```python
        response_text = await call_api(context_window, model=MODEL_ECONOMY)
```

Add the following block immediately after (before the `if response_text:` check):

```python
        # Session-limit guard: if call_api wrote the sentinel, alert and back off
        if SESSION_LIMIT_FILE.exists():
            try:
                limit_ts = SESSION_LIMIT_FILE.read_text().strip()
                log(f"[tick] session limit active since {limit_ts} — pausing ticks for 3600s")
                # Send one Telegram alert (fire and forget via subprocess)
                alert_msg = f"⚠️ Claude session limit hit at {limit_ts}. Ticks paused ~1h. No action until reset."
                subprocess.run(
                    [str(HOME / "scripts/genesis-send"), alert_msg],
                    capture_output=True, timeout=10,
                )
                SESSION_LIMIT_FILE.unlink(missing_ok=True)
                # Back off — wait 3600s before next tick instead of normal interval
                try:
                    await asyncio.wait_for(_force_wake.wait(), timeout=3600)
                    _force_wake.clear()
                except asyncio.TimeoutError:
                    pass
                continue
            except Exception as e:
                log(f"[tick] session-limit guard error: {e}")
                SESSION_LIMIT_FILE.unlink(missing_ok=True)
```

Also add the same sentinel check in `process_event()` — after:
```python
    response_text = await call_api(context_window)
```

Add:
```python
    # If call_api detected a session limit, don't send the error as a Telegram response
    if response_text is None and SESSION_LIMIT_FILE.exists():
        log(f"[event] session limit active — suppressing response to {source}")
        return
```

## DONE LOOKS LIKE

1. `SESSION_LIMIT_FILE = HOME / ".genesis-session-limit"` exists as a path constant in genesis-core
2. `call_api()` returns `None` (not the error string) when `claude --print` outputs any of the session-limit phrases
3. When `background_tick()` receives `None` from `call_api()` AND `.genesis-session-limit` exists: a Telegram message is sent via `genesis-send`, the sentinel file is deleted, and the tick sleeps 3600s before continuing
4. `process_event()` does not forward a session-limit `None` response to Telegram
5. Normal responses (no session-limit phrases) are unaffected — return behaviour is identical to before

## VERIFY WITH

```bash
# Static check — confirm SESSION_LIMIT_FILE constant is present
grep "SESSION_LIMIT_FILE" ~/scripts/genesis-core
# Expected: SESSION_LIMIT_FILE = HOME / ".genesis-session-limit"

# Confirm session-limit phrases list is present
grep "session limit" ~/scripts/genesis-core
# Expected: matches in both the phrase list and the log line

# Confirm sentinel unlink is present (cleanup after alert)
grep "SESSION_LIMIT_FILE.unlink" ~/scripts/genesis-core
# Expected: at least 2 matches (background_tick + process_event path)

# Syntax check
python3 -m py_compile ~/scripts/genesis-core && echo "syntax OK"
# Expected: syntax OK
```

Do NOT start genesis-core or remove `~/.genesis-frozen` to test this. Static verification is sufficient — the freeze guard must stay in place.

## OUT OF SCOPE

- Do NOT remove `~/.genesis-frozen`
- Do NOT start or enable genesis-core.service
- Do NOT change tick interval constants (TICK_INTERVAL stays 300)
- Do NOT add rate-limit detection to `maybe_summarize()` (different subprocess path, lower priority)
- Do NOT add retry logic — backing off cleanly is enough
