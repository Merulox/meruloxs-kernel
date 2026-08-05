# Harness Learning

## Objective

Kernel improves when failures become enforceable capabilities. More documentation alone is not learning.

## Hypothesis selection

Before converting an incident into a permanent control, separate induction from enforcement:

1. Record the observation: the exact input, action, outcome, and evidence reference.
2. Generate plausible hypotheses consistent with that observation.
3. Apply Bennett's Razor: choose the weakest sufficient hypothesis — the least-specific
   explanation supported by the evidence that still identifies an invariant worth protecting.
4. Record its scope, assumptions, evidence count, and a future observation that would falsify
   or narrow it.
5. Only then choose an enforcement layer.

Weakness is breadth of extension, not brevity, vagueness, or low confidence. Do not encode
incidental tools, paths, models, values, or timing into a permanent rule unless evidence shows
they are necessary. A single incident may justify a narrow regression check for the observed
failure while leaving the broader explanatory hypothesis unpromoted.

Security, authority, legal, and explicit safety invariants are not empirical hypotheses to
weaken. When the cost of recurrence is high, a specific preventive control may be warranted
before the causal explanation is settled; record that distinction.

## Failure conversion

For every escaped defect, repeated correction, verifier finding, or avoidable blocker, first
record the weakest sufficient failure hypothesis, then ask in order:

1. Can a deterministic test or state check prevent recurrence?
2. Can a lint, architecture rule, permission, or tool guard prevent it earlier?
3. Is the missing capability a reusable skill or tool contract?
4. Is the environment missing data, dependency, fixture, or observability?
5. Should topology selection change for this task shape?
6. Is it a calibrated eval case rather than a hard rule?
7. Is it truly one-off context that should remain only in the decision record?

Choose the earliest enforceable layer. Do not turn every incident into permanent prompt text.

The control must enforce the supported invariant, not an incident-specific story. Promote a
more specific explanation only when additional evidence excludes the weaker one.

## Eval corpus

Build a Kernel eval corpus from real work, not synthetic trivia. Each case should include:

- frozen intent contract;
- isolated environment fixture;
- reference outcome, not necessarily reference implementation;
- deterministic final-state grader;
- optional calibrated rubric for judgment-heavy dimensions;
- known failure mode and provenance;
- cost, latency, retry, and escalation capture.

Start with 20–50 cases only after v2 has produced enough representative runs.

## Metrics

Track by mode and risk tier:

| Metric | Meaning |
|---|---|
| pass@1 | Probability one run satisfies the outcome |
| pass^k | Consistency across repeated runs |
| human interventions | Scarce attention consumed after approval |
| repair attempts | Harness friction or weak contracts |
| escaped defects | False acceptance rate |
| verifier false rejects | Oracle calibration cost |
| wall time | Operational latency |
| tokens/cost | Economic viability |
| merge/integration conflicts | Topology quality |
| gate weakening attempts | Pressure against oracle integrity |
| incident-to-regression rate | Whether failures compound into protection |

Do not optimize throughput without escaped-defect and human-attention metrics.

## Model routing

Route by capability and economics, never brand identity:

- frontier model for accountable lead, architecture, ambiguous debugging, and Mission planning;
- cheaper/fast model for mechanical bounded leaves with strong deterministic checks;
- independent model or context for verification where shared blind spots matter;
- deterministic code instead of a model when the path is known.

Record the effective model in every persistent run record so results remain comparable.

## Verifier calibration

- Fully review Tier 2–3 outcomes.
- Randomly sample Tier 0–1 completions.
- Track false acceptance and false rejection.
- Preserve disputed oracle cases.
- Promote probabilistic findings to blocking only after deterministic reproduction or human confirmation.
- Revisit thresholds using measured evidence, not confidence in a model family.

## Quality garbage collection

Run small scheduled audits only after recurring signal exists. Candidate audits:

- stale or contradictory rules and research;
- architecture dependency drift;
- flaky or weakened tests;
- complexity and CRAP hotspots;
- mutation-score regressions;
- repeated reviewer comments;
- orphaned flags, adapters, skills, and dependencies;
- controls that never trigger or always require exceptions.

Delete or simplify controls that do not prevent measured failures. Harness complexity carries coordination cost too.
