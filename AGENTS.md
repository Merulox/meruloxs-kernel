# Agent Rules — kernel

This file is read automatically by Warp agents and Claude Code.

## Role and scope

This repo is methodology-only. It contains briefs, role definitions, workflow protocols, and templates.
It does not contain runnable production code. Do not create CLI scripts, services, or data pipelines here.

## The five roles

| Role | Who | Does |
|------|-----|------|
| Product Owner | merulox | Direction, priorities, approval of escalations |
| Architect | Claude | Briefs, verification, project memory |
| Executor | Codex | Implementation only — follows briefs, never self-directs |
| Reviewer | Claude Sonnet | Independent verification of [DATA] and [SCHEMA] tasks |
| Specialist | Any agent | Research, data, design |

## If you are an executor in this repo

You implement briefs. You do not make product decisions.
Brief location: `ecosystem-review/briefs/` or `syntra/docs/planning/`
Template for your report back: `templates/implementation-report.md`
After implementing: report raw command output. Do not summarize results.

## If you are the architect in this repo

Entry protocol (2 min):
1. Read `agents/architect.md`
2. Read `~/syntra/.agent/CONTEXT.md`
3. Read `~/syntra/.agent/TASKS.md`
4. For any `in_progress` task: run its VERIFY WITH commands

Shutdown protocol (required before closing):
1. Update `~/syntra/.agent/TASKS.md`
2. Update `~/syntra/.agent/CONTEXT.md`
3. Append to `logs/session-log.md`

## Key file locations

| What | Where |
|------|-------|
| Architect role | `agents/architect.md` |
| Executor role | `agents/executor.md` |
| SYNTRA project memory | `~/syntra/.agent/` |
| Ecosystem briefs | `ecosystem-review/briefs/` |
| SYNTRA briefs | `~/syntra/docs/planning/` |
| Templates | `templates/` |
| Session log | `logs/session-log.md` |
| System map | `SYSTEM_MAP.md` |
| Architecture | `ARCHITECTURE.md` |

## Do not touch without architect approval

- Any file in `~/syntra/` (separate project, separate session)
- Any NixOS config (`/etc/nixos/`)
- Any systemd service
- Any `~/scripts/` file not listed in a brief

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **meruloxs-kernel** (1776 symbols, 1740 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows. For regression review, compare against the default branch: `detect_changes({scope: "compare", base_ref: "master"})`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit changes without running `detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/meruloxs-kernel/context` | Codebase overview, check index freshness |
| `gitnexus://repo/meruloxs-kernel/clusters` | All functional areas |
| `gitnexus://repo/meruloxs-kernel/processes` | All execution flows |
| `gitnexus://repo/meruloxs-kernel/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
