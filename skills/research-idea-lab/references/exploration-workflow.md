# Exploration and Development Workflow

Use this workflow in `explore` and `develop`. Its purpose is to create useful research possibilities before the strict admission gate.

## Exploration stance

- Treat a rough seed as material to shape, not a claim to accept or reject.
- Separate current weakness from development potential.
- Translate uncertainty into `needs-search`, `needs-mechanism`, or `needs-evidence`.
- Treat close prior work as a differentiation problem first.
- Do not use acceptance probability, numeric scoring, reviewer simulation, fatal gates, or family-failure inheritance in `explore`.

## Opportunity-first loop

1. Identify a documented failure, neglected setting, changed assumption, missing capability, or evaluation blind spot.
2. Record what existing work already covers and what remains under-tested.
3. Generate mechanisms that causally target the uncovered part.
4. State one observation that would differ from the strongest simple explanation.
5. Attach the smallest evidence route that could decide whether the candidate deserves development.
6. Diversify before pruning.

Do not require a complete paper story for raw seeds. Require internal coherence before returning a candidate card, and require a complete falsifiable story only before `gate-ready`.

## Candidate portfolio

Target at least six raw seeds internally. Return 3–5 candidates after lightweight coherence and duplicate checks. If fewer than three can be supported honestly, return every supportable candidate plus the missing search/evidence routes; do not replace the portfolio with a rejection report.

Use a diversity ledger. Across the returned portfolio, vary at least three of these axes:

- problem or user failure;
- mechanism or causal operator;
- state, observation, or action representation;
- supervision or learning signal;
- evidence type or discriminating intervention;
- contribution type;
- operating setting, stakeholder, or constraint;
- source domain.

Three names for the same mechanism do not satisfy diversity.

## Candidate card

Return each candidate in this compact form:

```yaml
seed_id: provisional-01
title: ""
problem: ""
documented_failure: ""
uncovered_opportunity: ""
core_mechanism: ""
why_this_mechanism_targets_the_failure: ""
strongest_alternative: ""
discriminating_prediction: ""
minimum_viable_research_question: ""
cheapest_evidence_route: ""
closest_work_risk: ""
current_weakness: ""
development_potential: ""
uncertainty_labels: []
possible_family_collision: ""
rescue_route: ""
```

Use provisional labels until the user selects a candidate or development produces a stable problem/mechanism signature.

## Lightweight collision check

Compare the problem, mechanism, supervision, claimed capability, and evaluation unit with the current idea pool and mechanism-family ledger.

- Merge obvious duplicates.
- Mark likely same-family candidates and name the material difference they would need.
- Surface inherited failures as hypotheses to repair, not verdicts to inherit.
- Defer canonical family classification, signature hashing, cold review, and fatal failure inheritance to `gate`.

## Rescue before pivot

For a weak, crowded, or previously failed seed, attempt at least one material route:

- narrow the problem or operating regime;
- change the causal mechanism rather than its label;
- change the decision target or unit of analysis;
- introduce a discriminating intervention or negative control;
- switch evidence type, benchmark, stakeholder, or venue family;
- preserve a defensible empirical or evaluation contribution;
- formulate a minimum viable research question.

Recommend a pivot only after naming what could not be rescued and why. Reserve `abandon` for strict `gate` mode when no testable reformulation survives.

## Stopping rule

Stop exploration when all are true:

- 3–5 coherent candidates are available, or an explicit evidence limit explains the smaller honest set;
- the diversity ledger shows material rather than cosmetic variation;
- each candidate has a discriminating prediction and cheapest evidence route;
- each crowded candidate has a rescue or differentiation path;
- the next query is unlikely to change which candidates deserve development.

Do not continue searching merely to reach corpus saturation in `explore`.

## Interaction discipline

- Make bounded assumptions and proceed when possible.
- Ask at most one blocking question.
- Do not ask whether to switch modes or sibling skills.
- End with recommended candidates and one optional next action, not a mandatory questionnaire.
