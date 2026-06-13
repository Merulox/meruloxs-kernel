# HK-01 — Hook diet: cap per-prompt context injection

**Loop:** neither — PO exception granted 2026-06-12 (audit Q-05: discounts every future agent-hour; ~25k tokens of overhead per prompt across all sessions)
**Status:** briefed · **Priority:** P1 · **Safety:** touches hooks used by ALL Claude sessions — test in a throwaway session before declaring done

## GOAL
Reduce total UserPromptSubmit hook injection from ~100KB/prompt to ≤10KB/prompt by switching content-dump hooks to index+path injection.

## WHY
Measured 2026-06-11: obsidian_vault (~76KB) + vault_claims (~18KB) + system_manifest + instance_context + ops_state fire on every prompt of every session. Cost: API tokens, latency, and attention dilution. Sessions can read full files on demand; they don't need them pre-dumped.

## FILES IT OWNS
- The vault/obsidian injection hook script (locate via `~/.claude/settings.json` hooks array — likely `vault-query-hook` and/or a hook injecting `<obsidian_vault>`)
- `~/scripts/brain-session-hook` (instance_context block only)
- `~/scripts/realm-context-hook` (ops_state block only)
- The system_manifest generator hook (SCRIPTS list section only)

## DO NOT TOUCH
- `~/.claude/settings.json` hook *registrations* (which hooks fire) — only what they emit
- `~/scripts/brain-bus-stop-hook`, any systemd unit, the vault itself
- The `<vault_claims mode=...>` strategic/technical mode logic — keep modes, shrink payloads

## SPEC (per hook, in priority order)
1. **obsidian_vault** (~76KB → ≤2KB): inject only `index.md` + the four `moc/*.md` sphere files' *titles and link lists* (no claim bodies), plus one line: "full domain files at ~/obsidian/context-bundle/domain-{name}.md — read on demand."
2. **vault_claims** (~18KB → ≤4KB): keep `mode` attribute; cap at the N most relevant claims that fit 4KB; append "more: <domain file path>".
3. **system_manifest**: drop the full SCRIPTS listing (~150 lines) — replace with "run `ls ~/scripts/` or read `~/scripts/BRAIN_INDEX.md` before writing a new script." Keep RUNNING SERVICES (genuinely useful, compact) and ACTIVE SESSIONS.
4. **instance_context**: drop "Other Claude windows" entries older than 24h (registry was purged 2026-06-12 but make the filter permanent); drop the IN PROGRESS block when the task list is empty/stale (>7 days).
5. **ops_state**: drop `bus_events` that are `[meta] instance-X online` heartbeats; keep active_rule + real events.
6. Add to each modified hook a `MAX_BYTES` constant and a hard truncation guard so regrowth is impossible.

## DONE LOOKS LIKE
A fresh prompt in a new session carries ≤10KB total injected hook content (measure: each hook's stdout piped through `wc -c`, summed), and a session can still locate (a) the active decision rule, (b) vault domain file paths, (c) running services.

## VERIFY WITH
```
for h in <each modified hook>; do echo "test" | $h | wc -c; done   # sum ≤ 10240
echo "test" | <vault hook> | grep -c "context-bundle"              # ≥1 (paths preserved)
# then: open a throwaway claude session, confirm hooks fire without error
```

## OUT OF SCOPE
- Deleting or disabling any hook entirely
- Vault restructuring, claim editing, ingest-queue changes
- settings.json hook registration changes
