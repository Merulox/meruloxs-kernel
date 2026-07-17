# Task [ID]: [Short Title]

Status: ready for a builder / draft
Written by: architect, [YYYY-MM-DD]

<!-- gates: depends=[TASK-IDs or empty]; inputs=[text values PO must provide, or empty]; confirms=[manual out-of-band actions, or empty] -->
<!-- Machine-readable launch gate (AP-26). Aperture blocks "Send to Codex" until: every `depends` ID is done, every `inputs` value is provided (collected via textbox, written into this brief), every `confirms` box is ticked. Secrets go in `confirms` (checkbox that the manual step happened) — never in `inputs`. -->

Read `~/kernel/agents/executor.md` before starting.

---

## GOAL

One sentence: what changes in the world when this task is done?

## WHY

Why this task, why now. What depends on it. What it unblocks.

## PREREQUISITE

What must be true or done before this task starts. If nothing: write "None."

## FILES IT OWNS

Explicit list of files this task may create or modify.

```
src/[file].js           — [what changes]
src/[other-file].js     — [what changes]
```

Nothing not listed here. If the task genuinely needs another file, stop and ask the architect.

## DO NOT TOUCH

Explicit exclusions — files and systems that must not change.

- `src/[protected-file].js` — owned by another task / must stay stable
- `docs/` — read-only
- NocoDB schema — requires manual change, do not attempt via API
- Root `package.json` unless the brief explicitly adds a script

## DONE LOOKS LIKE

Numbered, observable, testable. Each item can be checked by someone who wasn't there.

1. [Observable state 1]
2. [Observable state 2]
3. [Command runs and produces expected output]

## VERIFY WITH

Exact commands to run. Architect will run these — output must match expectations.

```bash
node [script] [flags]
npm run nocodb:audit
npm test
```

Expected output or exit code for each command.

## OUT OF SCOPE

Things explicitly deferred — write them here to prevent scope drift.

- [deferred feature or work]
- [deferred feature or work]

## EXECUTOR
codex | opencode | either

<!-- codex = launched via Aperture (default if field absent) -->
<!-- opencode = run manually from terminal: cd <workroot> && opencode -->
<!-- either = architect's choice at runtime -->
