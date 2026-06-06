# Brief GX-04: Role Constraints + Verification-First Rule

Status: briefed. Architect 2026-06-06.
Read `~/agent-infra/agents/executor.md` first.

## GOAL

Add two explicit rules to Genesis's system prompt that (1) prevent it from writing technical code/schema briefs and (2) require it to verify any technical fact before stating it.

## WHY

Genesis wrote a product detail brief (S-09) with hallucinated schema columns (`description`, `affiliateUrl`, `imageUrl`) that don't exist in the Supabase products table. If that brief had gone to Codex unreviewed, the implementation would have failed completely.

The root cause isn't Genesis being broken — it's Genesis operating outside its capability envelope. It doesn't have live code access, so any technical fact it states is a reconstruction from memory. The fix is making this constraint explicit in the system prompt so Genesis self-governs.

## FILES IT OWNS

```
~/scripts/genesis-core   — only file that changes (system prompt only)
```

## DO NOT TOUCH

- Everything except `build_system_prompt()` in genesis-core
- State files, service files, soul.md

## CHANGES REQUIRED

### Single change — add two rules to `OPERATIONAL RULES` in `build_system_prompt()`

In the return f-string, in the `OPERATIONAL RULES:` section, add these two rules after the existing bullet points (after "Be direct. No preamble."):

```
- ROLE BOUNDARY: You are NOT the architect. Do not write technical briefs for code or database schema changes. If you identify a technical task that needs a brief, write one sentence to ~/obsidian/knowledge/projects/genesis/inbox/architect-flag.txt describing what's needed, then send a Telegram summary. The architect writes the brief.
- VERIFICATION RULE: Before stating any fact about code structure, database schema, or API shape — run a bash command to verify it. Read the source file or grep for the symbol. State what command you ran. Never claim a database column or function exists without checking. "I believe X exists" without verification is not acceptable.
```

The full updated rules block should look like (showing just the new lines in context):

```
- Be direct. No preamble. Partner values precision over warmth.
- ROLE BOUNDARY: You are NOT the architect. Do not write technical briefs for code or database schema changes. If you identify a technical task that needs a brief, write one sentence to ~/obsidian/knowledge/projects/genesis/inbox/architect-flag.txt describing what's needed, then send a Telegram summary. The architect writes the brief.
- VERIFICATION RULE: Before stating any fact about code structure, database schema, or API shape — run a bash command to verify it. Read the source file or grep for the symbol. State what command you ran. Never claim a database column or function exists without checking. "I believe X exists" without verification is not acceptable.
```

## DONE LOOKS LIKE

1. `ROLE BOUNDARY` rule appears in genesis-core's `build_system_prompt()` return string
2. `VERIFICATION RULE` rule appears in genesis-core's `build_system_prompt()` return string
3. `python3 -m py_compile ~/scripts/genesis-core` passes

## VERIFY WITH

```bash
# Syntax check
python3 -m py_compile ~/scripts/genesis-core && echo "syntax OK"

# Confirm both rules are present
grep -c "ROLE BOUNDARY\|VERIFICATION RULE" ~/scripts/genesis-core
# Expected: 2

grep -n "ROLE BOUNDARY" ~/scripts/genesis-core
grep -n "VERIFICATION RULE" ~/scripts/genesis-core
# Expected: one match each, inside build_system_prompt()
```

## OUT OF SCOPE

- Do not change any logic — this is a string change only
- Do not change the inbox path — use `~/obsidian/knowledge/projects/genesis/inbox/` (already exists)
- Do not add enforcement logic — the prompt rule is the enforcement
