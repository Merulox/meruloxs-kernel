# EX-5: Genesis Safety Gates (REQUIRED before revival)

Status: ready. Architect 2026-06-05. Read `~/agent-infra/agents/executor.md`.
**Revival decision = REVIVE (PO, 2026-06-05). This brief is the prerequisite — do not start genesis-core until these land.** Source of truth for the bugs: `~/projects/realm/monitor/genesis-audit.jsonl`.

## GOAL
Implement the four safety fixes that make Genesis safe to bring back online: (A3) bash_exec suicide guard, (A4) hard kill-switch, (B3) raise TOOL_CALL_LIMIT, (B4) raise bash timeout.

## WHY
genesis-core killed itself 2026-04-28 via an unguarded `bash_exec` SIGKILL on its own service. It has no kill-switch, a TOOL_CALL_LIMIT of 3 (silently truncates complex tasks), and a 120s bash timeout (silently fails on >2min scripts). Reviving without these repeats the failure.

## FILES IT OWNS
- `~/scripts/genesis-core` — this is where bash_exec, FORBIDDEN_PATTERNS, FREEZE_FILE, and the agentic loop all live (confirmed by architect)
- A new `~/scripts/genesis-freeze` if it doesn't exist (check first: `ls ~/scripts/genesis-freeze`)

## WHAT ARCHITECT FOUND (read before implementing)
- **A3**: `FORBIDDEN_PATTERNS` list already exists in `exec_tool()` (~line 230) — **extend it**, don't rewrite. Add missing patterns: `systemctl.*stop.*genesis`, `systemctl.*disable.*genesis`, `pkill.*python`, `rm.*-rf.*obsidian`, `> ~/obsidian`, `rm.*genesis-core`.
- **A4**: `FREEZE_FILE` check already exists at startup (~line 822) — **already done**. Skip A4.
- **B3**: Find the agentic loop in genesis-core that calls the Anthropic API. Look for a `while` loop that accumulates tool calls. Add a `MAX_TOOL_CALLS` guard (≥25) that breaks the loop if exceeded, logs a warning, and returns.
- **B4**: `timeout = min(int(inputs.get("timeout", 60)), 300)` — raise the cap from 300 to 600.

## DO NOT TOUCH
- `~/projects/genesis/daemon.py`, `agent.py` — the work is in genesis-core, not these
- Genesis identity/memory files in `~/obsidian/...` (behavior only, not soul)
- genesis.nix service wiring (no service changes in this brief)

## FIXES
1. **A3 — Suicide/sabotage guard:** in the bash_exec tool, reject any command matching a blacklist targeting critical services — `genesis-core`, `genesis-*`, `claude-bridge`, and patterns `systemctl .* (kill|stop|disable) .*genesis`, `kill -9`, `SIGKILL .*genesis`. On match: refuse + log, do not execute. (Doctrine: freeze, never sabotage — now enforced at runtime.)
2. **A4 — Hard kill-switch:** a single command `genesis-freeze` that halts all autonomous sends + sets the freeze flag (`~/.genesis-frozen` already used elsewhere — reuse it) and stops outbound. `genesis-unfreeze` reverses. daemon checks the flag each cycle and no-ops outbound when frozen.
3. **B3 — TOOL_CALL_LIMIT:** raise from 3 to a sane value (≥25). Locate the constant; make it an env/config override with a documented default.
4. **B4 — bash timeout:** raise the 120s cap to ≥600s (configurable). Confirm long scripts (outreach-batch ~3min) no longer silently fail.

## DONE LOOKS LIKE
1. bash_exec refuses a test command like `systemctl --user kill genesis-core` (returns refusal, does NOT execute) — demonstrate with a dry log line
2. `genesis-freeze` sets the flag and a frozen daemon cycle performs no outbound; `genesis-unfreeze` clears it
3. TOOL_CALL_LIMIT ≥ 25 and bash timeout ≥ 600s in the code, override-able
4. Genesis still starts and runs a normal cycle (no regression) — but DO NOT enable autostart

## VERIFY WITH
```bash
python3 -c "import ast; ast.parse(open('/home/merulox/scripts/genesis-core').read()); print('syntax OK')"
grep -n "FORBIDDEN_PATTERNS" ~/scripts/genesis-core
grep -n "timeout.*300\|timeout.*600\|min.*timeout" ~/scripts/genesis-core
grep -n "MAX_TOOL_CALLS\|tool_call.*limit\|tool.*count" ~/scripts/genesis-core
```
Report the FORBIDDEN_PATTERNS list in full (paste the actual list). Confirm B4 timeout cap value.

## OUT OF SCOPE
- Enabling autostart / actually reviving (separate step, after architect verifies these)
- The other ~20 audit bugs (M*/V*/R*, genesis-api endpoints) — log as backlog, fix later
- Voice layer / ambient interface
