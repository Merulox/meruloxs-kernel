# Brief GX-06: Fix Blocking Event Loop in maybe_summarize()

Status: briefed. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Make `maybe_summarize()` async so it no longer blocks the event loop during context window summarization.

## WHY

`maybe_summarize()` is called from async functions (`process_event()` and `background_tick()`) but uses `subprocess.run()` — a synchronous blocking call — internally. When summarization fires, `subprocess.run()` spawns a `claude --print` process and waits for it to complete. This call takes 30–90 seconds.

During those 30–90 seconds, the entire asyncio event loop is blocked. No Telegram messages are processed. No inbox files are handled. If a message arrives from the partner during summarization, it is queued by Telegram but not processed until summarization finishes. The partner sees silence.

After GX-05, ticks no longer append to `context_window`, so summarization only fires during `process_event()` (Telegram/voice/inbox events). This makes the blocking window precisely the worst time — when the partner is actively talking to Genesis.

## FILES IT OWNS

```
~/scripts/genesis-core   — only file that changes
```

## DO NOT TOUCH

- The `_find_safe_summarize_cut()` helper — correct, no changes needed
- `format_messages_as_text()` — no changes needed
- All other functions

## CHANGES REQUIRED

### Step 1 — Make `maybe_summarize()` async

Change the function signature (line 407):

Before:
```python
def maybe_summarize():
    """If context is too long, summarize oldest messages."""
```

After:
```python
async def maybe_summarize():
    """If context is too long, summarize oldest messages."""
```

### Step 2 — Replace `subprocess.run()` with async subprocess

Replace the entire `try` block in `maybe_summarize()` (the part starting with `result = subprocess.run(...)`):

Before:
```python
    try:
        result = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions"],
            input=summary_prompt.encode(),
            capture_output=True,
            timeout=60,
        )
        summary_text = result.stdout.decode().strip()
        if summary_text:
            summary_msg = {"role": "assistant", "content": f"[CONTEXT SUMMARY — replacing {len(to_summarize)} messages]\n{summary_text}"}
            context_window[:cut] = [summary_msg]
            log(f"[context] summarized → now {len(context_window)} messages")
    except Exception as e:
        log(f"[context] summarize failed: {e}")
```

After:
```python
    try:
        proc = await asyncio.create_subprocess_exec(
            "claude", "--print", "--dangerously-skip-permissions",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(
            proc.communicate(input=summary_prompt.encode()),
            timeout=60,
        )
        summary_text = stdout.decode().strip()
        if summary_text:
            summary_msg = {"role": "assistant", "content": f"[CONTEXT SUMMARY — replacing {len(to_summarize)} messages]\n{summary_text}"}
            context_window[:cut] = [summary_msg]
            log(f"[context] summarized → now {len(context_window)} messages")
    except asyncio.TimeoutError:
        log("[context] summarize timed out after 60s — skipping")
    except Exception as e:
        log(f"[context] summarize failed: {e}")
```

### Step 3 — Update all callers to `await maybe_summarize()`

Search for all calls to `maybe_summarize()` in the file and add `await`:

```bash
grep -n "maybe_summarize()" ~/scripts/genesis-core
```

There should be exactly 2 call sites:
1. In `process_event()` (~line 527): change `maybe_summarize()` → `await maybe_summarize()`
2. In `background_tick()` (~line 806): change `maybe_summarize()` → `await maybe_summarize()`

## DONE LOOKS LIKE

1. `maybe_summarize` is defined as `async def`
2. It uses `asyncio.create_subprocess_exec` instead of `subprocess.run`
3. Both call sites use `await maybe_summarize()`
4. `python3 -m py_compile ~/scripts/genesis-core` passes

## VERIFY WITH

```bash
# Syntax check
python3 -m py_compile ~/scripts/genesis-core && echo "syntax OK"

# Confirm async def
grep -n "async def maybe_summarize\|def maybe_summarize" ~/scripts/genesis-core
# Expected: "async def maybe_summarize"

# Confirm no subprocess.run in maybe_summarize (only asyncio subprocess)
grep -n "subprocess.run" ~/scripts/genesis-core
# Expected: subprocess.run should only appear in exec_tool() and _read_project_state(), NOT in maybe_summarize

# Confirm both call sites are awaited
grep -n "await maybe_summarize\|maybe_summarize()" ~/scripts/genesis-core
# Expected: only "await maybe_summarize()" — no bare "maybe_summarize()"
```

## OUT OF SCOPE

- Do not change the summarization logic or prompt
- Do not change SUMMARIZE_AT or MAX_CONTEXT_MSGS constants
- Do not make `_find_safe_summarize_cut()` async — it's pure Python, no I/O
