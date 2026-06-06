# Agent Rules — agent-infra

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
