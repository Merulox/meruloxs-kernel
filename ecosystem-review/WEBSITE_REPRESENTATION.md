# WEBSITE_REPRESENTATION.md — How merulox.com Should Tell This Story

**Date:** 2026-06-05 · **Reviewer:** Architect

Principle: **show what's real, frame what's in progress as in progress, never claim vision as capability.** Employers and collaborators reward demonstrated systems and honest framing; they punish detectable exaggeration. The grandiose "empire" language is a reputation risk — strip it.

---

## What to feature (and how)

### 1. SYNTRA — lead with this
- **Employers see:** a full-stack build — custom ingestion engine (reverse-engineered a non-Shopify brand API), data normalization with an audit/invariant test suite, a React discovery UI, and a real product thesis. This demonstrates range: backend, data, frontend, and product judgment.
- **Collaborators see:** the architecture (engine → NocoDB → discovery → storefront) and the multi-source adapter pattern.
- **Keep private:** affiliate economics, sourcing/margin strategy, NocoDB token.
- **Wording (safe):** "A curated everyday-carry storefront backed by a product-intelligence engine that ingests and normalizes catalogs from multiple brands."
- **Avoid:** revenue claims, "AI-powered" unless a model is actually in the loop, "thousands of products" (it's 280).
- **Demo that helps:** screenshot of the discovery mosaic + a short clip of filtering/saving; a diagram of the ingestion pipeline.

### 2. Agent Infra — the methodology writeup
- **Employers see:** systems thinking — a documented architect/executor/reviewer workflow with safety gates, recovery protocols, and verification discipline. This is rare and senior-signal.
- **Collaborators see:** reusable templates they could adopt.
- **Keep private:** which client projects use it.
- **Wording (safe):** "A lightweight operating system for running AI coding agents as a coordinated team — with durable memory and recovery across interruptions."
- **Demo:** the role/workflow diagram; the task-brief → implementation-report → review-report loop.

### 3. Genesis — as a research project, carefully
- **Employers see:** ambition + engineering depth — a persistent agent with heartbeat scheduling, memory accumulation, and a monitoring/audit layer. Framed as an *experiment*, this is impressive.
- **Keep private (hard rule):** soul.md, autobiography, partner-patterns, any conversation memory, the Telegram identity. These are personal and must never be public.
- **Wording (safe):** "An experiment in a persistent, memory-accumulating personal AI agent — exploring heartbeat scheduling, self-monitoring, and long-horizon continuity."
- **Avoid:** "conscious," "alive," "empire," anthropomorphic claims, the consciousness-assessment doc. These read as red flags to technical reviewers.
- **Demo:** the *architecture diagram* and the *monitoring/audit* concept — not the agent's "personality."

### 4. merulox.com itself
- It's live and on-brand (dark terminal aesthetic). Keep. Add a concise "what I'm building" section linking the above with honest status badges (Live / In progress / Research).

---

## What to keep entirely private

| Asset | Why |
|-------|-----|
| Aperture dashboard | Internal ops view; auth-gated; shows raw system state |
| Realm internals | Mostly obsolete; the "empire/Faith/tracks" framing reads as grandiose |
| Genesis identity & memory | Personal, intimate, not portfolio material |
| brain-* engine | Undocumented sprawl; would confuse more than impress |
| Obsidian vault | Personal knowledge graph |
| Boréal client data, CRM, leads | Third-party / commercial |

---

## Honest status badges (use these verbatim)

| Project | Badge | Caption |
|---------|-------|---------|
| SYNTRA | **In progress** | "Engine + catalog working; storefront launching." |
| Agent Infra | **Live (methodology)** | "Documented and in use." |
| merulox.com | **Live** | — |
| Genesis | **Research** | "Personal experiment, ongoing." |
| Aperture | *(unlisted)* | private |
| Realm | *(unlisted)* | private/archive |

---

## Wording that avoids exaggeration (replace-these table)

| Don't say | Say instead |
|-----------|-------------|
| "An autonomous AI agent empire" | "An experiment in persistent autonomous agents" |
| "58 agents across 5 tiers" | (don't — it isn't true; the agents are scaffolds) |
| "Self-expanding system that funds itself" | "Exploring self-monitoring and continuity" |
| "AI-powered curation" (no model in loop) | "A product-intelligence engine" (ingestion/normalization) |
| "Living system / conscious" | "Long-horizon agent experiment" |
| "Thousands of products" | "280 products across two brands, growing" |

---

## Screenshots / demos worth producing

1. SYNTRA discovery mosaic (hero shot) + 10-sec filter/save clip.
2. SYNTRA ingestion pipeline diagram (brand API → normalize → NocoDB → UI).
3. Agent Infra role/workflow diagram.
4. Genesis architecture diagram (heartbeat loop + monitor) — architecture only.
5. (Optional, later) a sanitized monitor/health view — *if* Genesis is revived and the bug ledger is cleared.

---

## The reputation-risk summary

The biggest public risk is **the grandiosity gap** — if a technical reviewer reads "AI agent empire / 58 agents / self-funding" and then finds empty directories, it damages credibility more than showing less would. **Underclaim relative to the chaos; let the genuinely-strong work (SYNTRA full-stack, Agent Infra methodology, Genesis-as-experiment) speak.** Real, demonstrable, modestly-framed beats visionary-but-unfalsifiable every time with the audiences that matter.
