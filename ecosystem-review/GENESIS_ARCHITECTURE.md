# Genesis Architecture — Ideal Design

Written: 2026-06-06. Architect.

---

## The core problem

Genesis reasons from stale cached state, not live world state.

Every call to `call_api()` passes a rolling conversation window of up to 40 old messages. The system prompt tells Genesis "live state is in live-state.md" but does NOT inject its contents — so unless Genesis explicitly reads it in a bash command, it reasons from conversation history that may be hours or sessions old.

This is why Genesis wrote a product detail brief with hallucinated schema columns, why it recommended tasks that were already done, and why its TASKS.md entries lag reality. It literally does not know what's true unless someone tells it.

---

## What Genesis is

A **watchdog + ambient assistant**. Not an architect. Not an executor.

| Good at | Bad at |
|---------|--------|
| Monitoring filesystem changes | Introspecting live DB schema |
| Sending Telegram alerts | Writing accurate code briefs |
| Heartbeat / state updates | Knowing what code actually does |
| Responding to partner messages | Staying current with rapid sprints |
| Zero-approval content/admin tasks | Any task requiring live code read |

The failure mode is Genesis operating outside this table. The fix is not rebuilding Genesis — it's constraining its scope and giving it live data.

---

## The ideal Genesis

Three properties:

### 1. Context-first reasoning

Before every LLM call, `build_system_prompt()` reads authoritative sources and injects them fresh:
- `~/syntra/.agent/TASKS.md` — last 20 task rows (current truth on what's done/in progress)
- `~/syntra/.agent/CONTEXT.md` — sprint summary
- `git log --oneline -5` from ~/syntra — recent commits
- `live-state.md` top 30 lines — recent tick log

This replaces the current model where Genesis is told "state is in live-state.md" but has to proactively read it (which it often skips under token pressure).

### 2. Explicit scope constraint

System prompt explicitly says:
- "You are NOT the architect. Do not write technical briefs for code or schema."
- "For code/schema work: write one inbox file flagging the need, alert via Telegram. The architect writes the brief."
- "You MAY write content, Telegram messages, state file updates, and zero-approval automation."

This prevents Genesis from trying to be helpful in ways it structurally cannot be.

### 3. Verification-first for technical claims

System prompt rule: "Before stating any fact about code structure, DB schema, or API shape — run a bash command to read the source. State what you ran. Never assume a column exists without checking."

This gates Genesis's most dangerous failure mode: confident wrong statements that become the basis for executor briefs.

### Bonus: Tick context isolation

Tick events (background reasoning cycles) don't need conversation history. Each tick should get a fresh system prompt with live state, not 40 messages of stale conversation. This makes ticks cheaper, faster, and more accurate.

Telegram/voice events keep a short conversational window (5–10 messages) for continuity.

---

## What does NOT need to change

- The daemon architecture (async Telegram + inbox + tick) is sound
- EX-5/EX-5b safety gates are in place and working
- Session-limit detection (GX-02) is now in place
- The live-state.md compaction (GX-01) is done

---

## Builds required

| # | Brief | What it fixes | Risk |
|---|-------|--------------|------|
| GX-03 | Fresh state injection | Stale knowledge, hallucinated facts | Low — adds reads to system prompt |
| GX-04 | Role + verification rules | Garbage briefs, overreach | None — system prompt only |
| GX-05 | Tick context isolation | Stale conversation bleeding into ticks | Low — changes what gets passed per event type |

Execute in order. GX-03 and GX-04 can run in parallel (different functions).

---

## What "done" looks like

After GX-03 + GX-04 + GX-05:
- Genesis's tick responses accurately reflect current TASKS.md state without being told
- Genesis never again writes a product brief with hallucinated columns
- Ticks are faster (less context to serialize)
- When Genesis doesn't know something technical, it says "I'll verify" and runs the command before claiming
