# Workflow: Escalation to Product Owner

---

## When to escalate (no exceptions)

Any agent must escalate when the action involves:

| Category | Examples |
|----------|---------|
| Product direction | Changing what the product does or who it's for |
| Scope expansion | New features, new integrations, new user-facing behavior |
| Data model | Schema changes, new fields, field renames with migration |
| Data deletion | Dropping records, truncating tables, archive/purge operations |
| Deployment | Publishing to production, merging to main, releasing |
| Money | Paid APIs, subscriptions, cloud costs, Stripe |
| Security | Auth changes, secret rotation, permission model |
| Agent disagreement | Architect and reviewer cannot resolve — needs a human call |

## Escalation that is NOT required

- Technical implementation choices within a brief's scope
- Picking between two equivalent approaches with no user-visible difference
- Fixing bugs that are clearly in scope
- Asking clarifying questions about a brief

---

## How to escalate

1. **Stop work on the blocked task**
2. **Write a clear escalation note** in CONTEXT.md:
   ```
   ## ESCALATION NEEDED
   Task: [ID + name]
   Reason: [one sentence on what requires PO decision]
   Options: [A] [B] [default if no response by X]
   ```
3. **Log in agent-comms.md** with timestamp
4. **Surface to product owner** in the conversation: "I need a decision before continuing."
5. **Do not unilaterally pick** and proceed

---

## Default behavior during escalation

While waiting for a PO decision:
- Continue work on other tasks that do NOT depend on the decision
- Do not attempt to infer the decision from context
- Do not pick the "safer" option without logging it as a decision

---

## After PO decides

1. Log the decision in DECISIONS.md
2. Clear the escalation flag from CONTEXT.md
3. Update TASKS.md to reflect any scope changes
4. Resume the task or write a new brief if direction changed significantly
