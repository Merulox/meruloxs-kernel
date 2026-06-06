# Merulox's Kernel

**A governance layer for multi-agent AI development.**

When you build software with AI agents — Claude as architect, Codex as executor, another Claude as reviewer — you get a new class of failure: agents that trust each other's reports without verifying live state, drift into each other's roles, make silent decisions, and leave sessions in unrecoverable states. This repo is the operating system that prevents those failures.

It defines five roles, a task lifecycle, a brief format, session recovery protocols, and verification discipline — enough structure to run coherent multi-agent projects without enough overhead to slow them down.

---

## The core insight

**"The executor said it's done" is not done.**

The most common failure in multi-agent development is trust drift: an architect accepts an implementation report at face value and marks the task complete, while the live system is in a different state entirely. This framework makes verification non-optional. Every task brief requires `VERIFY WITH` — exact commands the architect runs against live state before acceptance. No commands, no brief.

---

## The five roles

```
Product Owner  ──  direction, priorities, escalations
Architect      ──  briefs, project memory, verification  (Claude Opus/Sonnet)
Executor       ──  implementation only                    (Codex / Claude)
Reviewer       ──  independent QA, does not trust reports (Claude Sonnet)
Specialist     ──  research, design, data work
```

The Architect is the only role that can mark work done. The Reviewer is the only role whose QA holds. The Executor cannot expand scope. These constraints are what make the system work.

---

## Task lifecycle

```
backlog → briefed → in_progress → [review] → done
                                       ↓
                                     fail → fix brief → in_progress → ...
```

Nothing moves from `backlog` to an executor without a brief. A brief is not a bullet list — it has seven required sections, including explicit file ownership (`FILES IT OWNS`), hard exclusions (`DO NOT TOUCH`), and runnable verification commands (`VERIFY WITH`). A brief without `VERIFY WITH` is a wish, not a task.

---

## Session recovery

The project state lives in files, not in conversation history. When a session ends — cleanly or not — the next session reads two files and is operational in under two minutes:

```
Read ~/agent-infra/agents/architect.md        # role restoration
Read <project>/.agent/CONTEXT.md              # what was in flight
Read <project>/.agent/TASKS.md               # what to do next
```

Every session ends with CONTEXT.md updated. Skipping this is how agents freeze — a long-running session that exits without writing recovery state leaves the next session blind, rediscovering context that should have been preserved.

---

## What's in this repo

```
agents/           Role definitions: architect, executor, reviewer, specialist
mvaos/            Compact role docs (Minimum Viable Agent OS)
workflows/        Session start, shutdown, handoff, escalation, task lifecycle
templates/        Blank forms: brief, implementation report, review report, decision record
ecosystem-review/ Forensic architecture audit (9 docs + 6 executor briefs)
logs/             Session log + agent communications log
project/          Project memory templates (copy to <project>/.agent/)
```

The `mvaos/` directory is the minimal version — if you want to drop this governance layer into an existing project in five minutes, copy those files and start there.

---

## Brief format

Every task brief has exactly these sections:

| Section | What it contains |
|---------|-----------------|
| `GOAL` | One sentence: what changes in the world when this is done |
| `WHY` | Motivation, why now, what it unblocks |
| `FILES IT OWNS` | Explicit list — executor touches nothing else |
| `DO NOT TOUCH` | Hard exclusions |
| `DONE LOOKS LIKE` | Numbered, observable, testable criteria |
| `VERIFY WITH` | Exact commands. Architect runs these. |
| `OUT OF SCOPE` | Explicit deferrals to prevent scope creep |

The format is non-negotiable. A brief that skips `VERIFY WITH` will be rejected and rewritten before handoff.

---

## Session recovery in practice

**Starting a session:**
```
Read ~/agent-infra/agents/architect.md.
Read .agent/CONTEXT.md.
Read .agent/TASKS.md.
Find any in_progress tasks — run their VERIFY WITH commands before assuming they're done.
Resume as architect.
```

**Ending a session (5 minutes — do not skip):**
1. Update TASKS.md — mark completed tasks `done`
2. Update CONTEXT.md — what finished, what's in flight, what's next
3. Append new decisions to DECISIONS.md
4. Append a line to session-log.md

**The minimum viable session end:** one sentence in CONTEXT.md — where you stopped and the exact next action.

---

## Failure modes this prevents

| Failure | What happens without governance | How this stops it |
|---------|--------------------------------|-------------------|
| Trust drift | Architect accepts executor's "it's done" without verifying | `VERIFY WITH` is mandatory; architect runs commands |
| Role drift | Architect starts writing code instead of briefs | Role definition makes the line explicit; brief-first rule |
| Context loss | New session has no idea what was happening | CONTEXT.md is the recovery artifact; shutdown protocol is mandatory |
| Scope creep | Executor adds improvements outside the brief | `FILES IT OWNS` + `DO NOT TOUCH` define the boundary |
| Silent decisions | Architecture changes without a record | Every decision goes to DECISIONS.md before acting |
| Frozen sessions | Long-running session exits without cleanup | Session shutdown protocol + CONTEXT.md make re-entry cheap |

---

## Adopting it in a project

```bash
# Copy project memory templates
mkdir -p ~/myproject/.agent/logs
cp ~/agent-infra/project/* ~/myproject/.agent/
cp ~/agent-infra/logs/* ~/myproject/.agent/logs/

# Fill in .agent/PROJECT.md first — everything follows from there
```

Then start an architect session with:
```
Read ~/agent-infra/agents/architect.md.
Read .agent/CONTEXT.md.
Read .agent/TASKS.md.
Resume as architect.
```

The project currently using this in production: [SYNTRA](https://github.com/Merulox/SYNTRA) — a product cataloguing and discovery engine with 280+ products across two brand sources, built entirely via architect↔executor↔reviewer cycles.

---

## Name

This is **Merulox's Kernel** — the kernel layer of a personal software stack. Everything else (SYNTRA, Genesis, Aperture) runs on top of it. The name reflects function, not scale.

---

## Ecosystem context

This repo is the methodology layer of a broader system:

```
meruloxs-kernel  ──  how we build (this repo — governs all)
SYNTRA       ──  what we build (curated EDC retail product engine)
merulox.com  ──  public portfolio
```

The `ecosystem-review/` directory contains a forensic architecture audit that maps the full system: what exists, what was intended, where documentation and implementation diverged, and a prioritised recovery plan. It's worth reading if you're building a similar AI-assisted software operation and want to understand what breaks at scale.

---

## License

MIT. The methodology is the thing — take it, adapt it, use it.
