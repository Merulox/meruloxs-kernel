# Agent Ecosystem Architecture

Last updated: 2026-06-06
Author: Architect (instance X)
Basis: Warp capability reconnaissance + live system state

---

## The five pieces

```
RUNTIME          Warp Terminal       — session UI, agent execution, MCP client
SOURCE OF TRUTH  GitHub              — versioned code and briefs
COGNITION        Claude (Architect)  — planning, verification, brief writing
EXECUTION        Codex (Executor)    — implementation only
OBSERVABILITY    Aperture            — ops dashboard, task board
```

No piece is redundant today. Each has a distinct function that the others cannot cover.

---

## What Warp already provides (do not rebuild)

### Stable features — rely on these

| Capability | Warp's answer |
|---|---|
| Terminal session layout | Tabs, panes, blocks |
| Session restoration (layout) | SQLite-backed, on by default |
| Model switching | Mid-session, persistent, all major providers |
| Desktop notifications | OS-native, fires on agent completion or password prompt |
| Agent execution (local) | Interactive, multi-step, tool-calling |
| Agent execution (cloud) | Oz — containerized, continues without Warp open |
| Cloud scheduling/triggers | Cron, webhooks, GitHub, Linear, Slack, API |
| MCP integrations | First-class client — GitHub, Sentry, Grafana, Linear, Slack, etc. |
| REST API + SDKs | `oz` CLI, Python/TS SDKs, `POST /agent/run` |
| Workflow templates | Parameterized, team-shared via Warp Drive |
| Per-project agent rules | `AGENTS.md` in repo root or subdirectories |
| Team knowledge sharing | Warp Drive — workflows, prompts, notebooks, env vars |
| Multiple parallel agents | Separate tabs/panes; manual git-worktree coordination |
| Agent handoff local→cloud | Conversation context carried forward |
| Cloud agent observability | Full run records, shareable links, API-accessible |

### Coming but not stable — do not depend on yet

| Feature | Status |
|---|---|
| Agent Memory | Research preview, waitlist-gated. Cross-session/cross-agent shared context. Do not build around it — wait for GA. |
| Auto-compaction | Open issue only. Not implemented. Manual `/compact` is the current answer. |
| Persistent local agent sessions | Open issue only. Local agents die when Warp closes. Cloud is the answer for persistence. |

---

## What Warp does NOT provide (real gaps)

These are the only things worth building infrastructure for:

### 1. Local process persistence without cloud

Warp local agents require the app to be open. `export`-set env vars are lost on restart (known bug #8508). If you need agents or services running headlessly:
- **Existing answer:** systemd --user (already used by `aperture`, `telegram-commander`, etc.)
- **Don't build:** a custom session manager. You already have one.

### 2. Per-project env var auto-loading

No native Warp primitive for per-project `.env` loading.
- **Existing answer:** `direnv` or `.envrc` hooks in shell profile
- **Don't build:** a Warp-specific wrapper for this

### 3. Cross-agent shared context (today)

No automatic shared memory between parallel local agents. You coordinate via:
- Git artifacts / worktree outputs
- Shared files on disk
- Explicit task descriptions
- The existing `brain-bus` event bus (already built)

Agent Memory (waitlist) will eventually cover this. **Don't pre-build a competing memory layer** — it will be obsoleted by Warp's own.

### 4. Output streaming from cloud agents

Oz API is polling-based, not streaming. If you need live output tailing from a cloud run in an external tool, you must build that polling loop yourself. This is a narrow need — don't build it speculatively.

### 5. External notification delivery

Warp notifications are desktop-only. For Slack/Telegram alerts on agent completion, you must call those APIs from within the agent task or a custom Oz integration. **This is already handled** by `telegram-commander` + custom hooks where needed.

---

## Infrastructure that should NOT be built

The purpose of this section is to prevent work. Each item is something that looks like a gap but isn't.

| Do not build | Why |
|---|---|
| A custom session naming/recovery system | Warp Drive + SQLite session restore already covers this. The gap (env vars) is solved by shell profile, not a new tool. |
| A custom model router / provider abstraction | Warp's model picker + Agent Profiles cover multi-model selection. Adding a wrapper adds indirection without capability. |
| A custom agent scheduler | Oz cloud agents have cron, webhooks, GitHub, Linear, Slack triggers. You have zero scheduling infrastructure gaps right now. |
| A cross-agent shared context store | Agent Memory is coming. Building a competing layer now means migrating off it later. Wait. |
| A custom MCP server for internal tools | Only build an MCP server if you have a tool that (a) multiple agents need, (b) has a stable interface, and (c) is not already exposed via an existing integration. Do not speculatively MCP-ify things. |
| A custom observability pipeline for agent runs | Cloud agent runs are already observable via Oz API + run records. Aperture reads from systemd/monitor data. Don't add a layer between them. |
| A local notification system beyond OS desktop | Desktop notifications work. Telegram works. Email is overkill. Pick one path and stay there. |

---

## Infrastructure worth building

These are genuine gaps where the benefit justifies the cost.

### 1. `oz`-native cloud agent wrappers for critical automations (future)

When a brain-* automation outgrows systemd (needs real background continuation across machine restarts, better observability, multi-step planning), migrate it to a cloud Oz agent. Don't pre-migrate — only do this when a specific automation breaks under the systemd model.

### 2. Aperture: Oz run feed

Aperture currently reads from systemd and realm monitor data. A future improvement: pull completed Oz cloud agent runs into the dashboard via the REST API. This closes the visibility gap between local systemd services and cloud agent runs. **Not urgent** — build when cloud agents are regularly used.

### 3. Per-project `AGENTS.md` for SYNTRA and agent-infra

Warp's rules system (`AGENTS.md`) is stable and production-ready. A 20-line `AGENTS.md` in each project root gives any Warp agent (or Claude Code) project-specific conventions without needing the architect to re-brief every session.

Cost: low. Benefit: every future agent session starts with accurate context.
**Build this soon.**

### 4. Explicit git worktree protocol for parallel executors

When running multiple Codex instances on the same repository simultaneously, there is no automatic conflict prevention. Warp provides tabs/panes for parallelism but not git isolation. The current workaround is manual coordination via TASKS.md + CONTEXT.md claiming.

A documented worktree protocol (brief-driven: executor creates `git worktree add` before starting, PR merges back) would prevent the class of collision bugs seen today without requiring any new tooling.
**Write the protocol. Don't build a tool.**

---

## Session lifecycle — what survives what

| Event | Survives | Lost |
|---|---|---|
| Clean Warp restart | Layout, recent blocks, shell history, Warp Drive, MCP configs, agent profiles, cloud transcripts | env vars (`export`), local agent conversations, running processes |
| Warp crash | Same as restart but SQLite may be stale snapshot | Same + potentially stale layout |
| `/compact` | Summarized conversation; model-dependent fidelity | Raw conversation history |
| Context window exceeded (no compact) | Model may truncate or halt | Uncompacted history |
| Cloud agent disconnect | Agent continues running; transcript persists | Nothing (by design) |
| Closing cloud tab | Grace-period undo-close; transcript always accessible | Live view after grace period |

**Takeaway for this system:** Local architect sessions must run the shutdown protocol (update CONTEXT.md + TASKS.md) before closing — not because Warp loses state, but because CONTEXT.md is the project memory layer that survives across all agent types. Warp's SQLite is for layout; CONTEXT.md is for cognition.

---

## Where orchestration should live

| Concern | Lives in |
|---|---|
| Which task to do next | Aperture (taskboard) + TASKS.md |
| How to execute the task | Codex (executor, inside Warp) |
| Whether execution was correct | Architect (verification, inside Warp or Claude Code) |
| Parallel task execution | Multiple Warp panes/tabs, manual worktree coordination |
| Background/headless execution | Oz cloud agents or systemd --user |
| Shared project conventions | `AGENTS.md` in repo root |
| Long-term project memory | CONTEXT.md + TASKS.md + Obsidian vault |

Warp handles runtime. GitHub + project docs handle source of truth. Aperture handles visibility. Claude handles judgment. Codex handles implementation. These boundaries are correct and should be maintained.

---

## Summary judgment

The terrain is well-covered. The gaps are narrow and mostly solvable with process (worktree protocol, shutdown discipline) rather than new infrastructure.

The two concrete build items with immediate ROI:
1. **`AGENTS.md` per project** — 20 minutes of work, permanent benefit
2. **Git worktree protocol brief** — prevents the next collision, no new tooling

Everything else: wait, observe, build only when a specific pain point is proven.
