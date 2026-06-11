# merulox's kernel

An operating model for building software with AI agents. Five roles, a task lifecycle, a brief format, and session recovery protocols — enough structure to keep a multi-agent project coherent across cold starts without enough overhead to slow anything down.

This is what I actually use. [Aperture](https://github.com/merulox/aperture) is built with it.

---

## The model

Five roles that do not overlap:

| Role | Who | Does |
|------|-----|------|
| Product Owner | me | direction, priorities, escalations |
| Architect | Claude | briefs, verification, project memory |
| Executor | Codex | implementation only |
| Reviewer | Claude (separate session) | independent verification |
| Specialist | any agent | research, data, design |

A task moves through: `backlog → briefed → in_progress → review → done`. Nothing is "done" until the architect has run the VERIFY commands and confirmed live state.

## The brief format

Every executor handoff has:

```
GOAL
WHY
FILES IT OWNS
DO NOT TOUCH
DONE LOOKS LIKE
VERIFY WITH
OUT OF SCOPE
```

The last three are the important ones. "Done looks like" is specific and falsifiable. "Verify with" is exact shell commands the architect runs. "Out of scope" is a firewall against scope creep mid-execution.

## What's in here

```
agents/         role definitions — architect, executor, reviewer, specialist
workflows/      session start, shutdown, handoff, task lifecycle protocols
templates/      blank brief, report, review, decision, handoff forms
mvaos/          compact role docs for smaller contexts
ecosystem-review/  forensic audit of a live system + executor brief sequence
```

## Caveats

This repo is a periodic snapshot. The live version lives locally and evolves faster than I push it.
