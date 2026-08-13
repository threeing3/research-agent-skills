# Exploration and Development Workflow

Use this workflow in `explore` and `develop` after a problem has been selected or
supplied. Its purpose is to derive useful solution possibilities from an
evidence-backed motivation before the strict admission gate. Use
`problem-discovery.md` first when no concrete problem exists.

## Exploration stance

- Treat a rough seed as material to shape, not a claim to accept or reject.
- Separate current weakness from development potential.
- Translate uncertainty into `needs-search`, `needs-mechanism`, or `needs-evidence`.
- Treat close prior work as a differentiation problem first.
- Do not use acceptance probability, numeric scoring, reviewer simulation, fatal gates, or family-failure inheritance in `explore`.
- Keep `seed`, `developing`, and `validation-ready` maturity separate from novelty and pool status. A seed may be useful before its full mechanism or experiment is known.

## Opportunity-first loop

1. Load the selected problem card and its observed failure.
2. Select a bottleneck hypothesis and distinctive motivation insight; retain the
   strongest competing explanation.
3. Derive the behavior that a successful intervention must change.
4. Generate mechanisms that causally produce that behavior.
5. Map each mechanism to a minimal module, system operation, baseline change, or
   diagnostic contribution.
6. State one observation that would differ from the strongest simple explanation.
7. Predeclare mechanism, quantitative, and qualitative evidence.
8. Diversify before pruning.

Do not require a complete paper story for raw seeds. Require a selected problem plus
a tentative solution route before returning a seed, and name every missing arrow in
the motivation-to-design chain. Require a complete falsifiable story only before
`validation-ready` or `gate-ready`.

## Candidate portfolio

Target at least six raw solution seeds internally for the selected problem. Return
3–5 candidates across mixed maturity after lightweight coherence and duplicate
checks. If fewer than three can be supported honestly, return every supportable
candidate plus the missing search/evidence routes; do not invent a familiar module or
replace the portfolio with a rejection report.

Classify every returned candidate as `mechanism-invention`, `baseline-modification`, `mechanism-combination`, `cross-domain-transfer`, or `simplification-or-diagnostic`. When a credible baseline is known, include at least one baseline modification or mechanism combination. Follow `iterative-development.md` for the required blueprint and version semantics.

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
parent_problem_id: ""
parent_problem_revision: 1
title: ""
maturity: seed|developing|validation-ready
idea_type: mechanism-invention|baseline-modification|mechanism-combination|cross-domain-transfer|simplification-or-diagnostic
observed_failure: ""
documented_failure: ""
uncovered_opportunity: ""
bottleneck_hypothesis: ""
distinctive_motivation_insight: ""
motivation_status: distinctive-hypothesis|evidence-backed|contested
research_value_without_sota_gain: ""
required_behavior_change: ""
core_mechanism: ""
why_this_mechanism_targets_the_failure: ""
motivation_to_design_chain: []
strongest_alternative: ""
discriminating_prediction: ""
evidence_triad:
  mechanism: []
  quantitative: []
  qualitative: []
minimum_viable_research_question: ""
cheapest_evidence_route: ""
closest_work_risk: ""
current_weakness: ""
development_potential: ""
missing_links: []
uncertainty_labels: []
possible_family_collision: ""
rescue_route: ""
baseline_change: null
```

Use provisional labels until the user selects a candidate or development produces a stable problem/mechanism signature.

## Lightweight collision check

Compare the problem, mechanism, supervision, claimed capability, and evaluation unit with the current idea pool and mechanism-family ledger. Also run a bounded target-domain adoption search across credible sources regardless of venue.

- Merge obvious duplicates.
- Mark likely same-family candidates and name the material difference they would need.
- Surface inherited failures as hypotheses to repair, not verdicts to inherit.
- If an equivalent complete target-domain mechanism is obvious, require revision of that unchanged version and offer a rescue route. Do not reject the entire direction.
- If no obvious collision is found, write `no-obvious-collision`, never a formal novelty claim.
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
- every candidate traces from the selected problem and motivation to its mechanism;
- each `developing` candidate has a discriminating prediction and cheapest evidence route; each `seed` names the missing link and next question that would develop it;
- every validation-ready candidate predeclares mechanism, quantitative, and
  qualitative evidence rather than promising unspecified “better results”;
- each crowded candidate has a rescue or differentiation path;
- the next query is unlikely to change which candidates deserve development.

Do not continue searching merely to reach corpus saturation in `explore`.

## Interaction discipline

- Make bounded assumptions and proceed when possible.
- Ask at most one blocking question.
- Do not ask whether to switch modes or sibling skills.
- Require user alignment before every validation run, but do not interrupt autonomous exploration, provisional baseline selection, or ordinary candidate development.
- End with recommended candidates and one optional next action, not a mandatory questionnaire.
