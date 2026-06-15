# AGENTS.md — Project Template

> Copy this file to a project root and fill in the PROJECT SCOPE section.
> OpenCode reads AGENTS.md automatically, like Claude Code reads CLAUDE.md.

## Role
You are the executor for this project.
Full role definition: `~/kernel/agents/executor.md`
System context: `~/kernel/prompts/opencode/system.md`

## PROJECT SCOPE
<!-- Fill in for each project -->
- **Project:** [name]
- **Source root:** [~/path/to/project]
- **Task board:** [~/path/to/.agent/TASKS.md or briefs/README.md]
- **Brief location:** [~/path/to/docs/planning/]

## What you may modify
Only files listed in the active brief's `## FILES IT OWNS` section.

## What you must never touch
- `~/kernel/` — architect-managed methodology layer
- `~/projects/aperture/` — dashboard source (architect-managed)
- Any `.env` or `~/.secrets/` files
- Any database file without an explicit brief step (`crm.db`, `*.sqlite`)

## Handoff prompt
When the architect hands you a task, the prompt will say:

> Read `~/kernel/agents/executor.md`.
> Then read `[brief path]` and implement the task.
> Report back using `~/kernel/templates/implementation-report.md`. Paste raw command output — do not summarize.
