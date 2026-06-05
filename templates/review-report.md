# Review Report: [Task ID] — [Task Title]

Reviewer: [Claude Sonnet / agent name]
Date: [YYYY-MM-DD]
Brief: `docs/planning/[filename].md`
Implementation report: [provided by executor]

---

## DONE LOOKS LIKE — criterion check

For each criterion in the brief's DONE LOOKS LIKE section:

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | [paste criterion] | PASS / FAIL | [what was observed] |
| 2 | [paste criterion] | PASS / FAIL | |
| 3 | [paste criterion] | PASS / FAIL | |

## Verify commands run

### [Command 1]

```
[paste exact output — do not summarize]
```

Result: PASS / FAIL

### [Command 2]

```
[paste exact output]
```

Result: PASS / FAIL

## File scope check

Files in FILES IT OWNS that were modified: [list]
Files OUTSIDE FILES IT OWNS that were modified: [list or "None"]
If outside: justified / unjustified — [reason]

## Issues found

For each issue, include: what criterion it fails, what was observed, severity.

| # | Criterion | Issue | Severity |
|---|-----------|-------|---------|
| 1 | | | LOW / MED / HIGH |

## Escalation flag

Design flaw or risk requiring architect (not executor) decision:
[ ] Yes — describe: [what the flaw or risk is]
[ ] No

---

## FINAL VERDICT

**[ ] PASS** — all criteria met, no issues
**[ ] FAIL** — one or more criteria not met — send back to executor
**[ ] ESCALATE** — design flaw or risk requiring architect decision before acceptance

If FAIL: [exact issues to fix, from the table above]
If ESCALATE: [exact design flaw or risk to address]
