# Brief GX-05: Tick Context Isolation

Status: briefed. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Tick events (background reasoning cycles) should get a fresh context window, not the full rolling conversation history. Telegram/voice events keep their conversational window. This makes ticks cheaper, faster, and more accurate.

## WHY

Currently, every call to `call_api()` receives `context_window` — up to 40 messages of accumulated conversation history. For background ticks, this history is noise: it contains old Telegram exchanges, prior tick responses, and stale decisions from previous sessions. Genesis doesn't need to "remember" last week's conversation to do a heartbeat tick — it needs the current world state, which GX-03 now injects into the system prompt.

The problem is worse under token pressure. When the 40-message context is large, `call_api()` serializes it all into the prompt, burning tokens on irrelevant history and leaving less budget for the actual reasoning. Ticks under budget pressure produce shallow responses or silently skip work.

Fix: background ticks pass an empty context window (just the system prompt). Telegram/voice events pass the last 8 messages (enough for conversational continuity).

## FILES IT OWNS

```
~/scripts/genesis-core   — only file that changes
```

## DO NOT TOUCH

- State files, service files, soul.md
- `call_api()` function — change the callers, not the function itself

## CHANGES REQUIRED

### Single change — in `background_tick()`, pass empty context to `call_api()`

Current code in `background_tick()` (around line 809):
```python
        response_text = await call_api(context_window, model=MODEL_ECONOMY)
```

Replace with:
```python
        # Ticks use a fresh context — system prompt has live state via GX-03.
        # Passing conversation history here costs tokens without adding accuracy.
        response_text = await call_api([], model=MODEL_ECONOMY)
```

And update the append after the response (around line 812–815). Currently:
```python
        if response_text:
            context_window.append({"role": "assistant", "content": response_text})
            log(f"[tick] response: {response_text[:200]}")
        else:
            context_window.append({"role": "assistant", "content": f"[tick:{tick_n}] — no action needed"})
```

Replace with:
```python
        if response_text:
            log(f"[tick] response: {response_text[:200]}")
        # Tick responses are NOT appended to context_window.
        # Ticks are fire-and-forget; their output is in live-state.md, not conversation history.
```

### Also change: `process_event()` — trim context for Telegram events

In `process_event()` (around line 534):
```python
    response_text = await call_api(context_window)
```

Replace with:
```python
    # Keep last 8 messages for conversational continuity.
    # Older history is noise; live state comes from the system prompt (GX-03).
    response_text = await call_api(context_window[-8:])
```

Note: the `context_window` list is still appended after the call (existing code) — this keeps the full history for cases where summarization fires. Only the slice passed to `call_api` is trimmed.

## DONE LOOKS LIKE

1. `background_tick()` calls `call_api([])` (empty list)
2. Tick responses are NOT appended to `context_window`
3. `process_event()` calls `call_api(context_window[-8:])` (last 8 messages)
4. Full `context_window` list still grows (for summarization logic) — only the argument to `call_api` is trimmed
5. `python3 -m py_compile ~/scripts/genesis-core` passes

## VERIFY WITH

```bash
# Syntax check
python3 -m py_compile ~/scripts/genesis-core && echo "syntax OK"

# Confirm tick passes empty context
grep -A2 "Ticks use a fresh context" ~/scripts/genesis-core
# Expected: line with call_api([], ...)

# Confirm process_event passes trimmed context
grep -A1 "conversational continuity" ~/scripts/genesis-core
# Expected: line with call_api(context_window\[-8:\])

# Confirm tick response is NOT appended to context_window
grep -n "context_window.append" ~/scripts/genesis-core
# Expected: no append inside background_tick() — only in process_event and maybe_summarize
```

## OUT OF SCOPE

- Do not change `maybe_summarize()` — it still operates on the full `context_window`
- Do not change the `save_context()` call — still saves full history to disk
- Do not change context window size constants (MAX_CONTEXT_MSGS, SUMMARIZE_AT)
- Do not change `call_api()` signature or behavior
