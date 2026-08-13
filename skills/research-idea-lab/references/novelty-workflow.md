# Target-Domain Novelty and Field-Mapping Workflow

Use this workflow for lightweight collision checks during exploration and focused strict novelty review after a promising low-cost validation. Do not import the full scoring, ranking, reviewer-attack, or abandon workflow unless the user explicitly requests `gate` mode.

## Declare the target-domain boundary

Before search, record:

- research task or capability;
- problem setting and affected operating conditions;
- key constraints material to the claim;
- the exact novelty unit, such as an operative mechanism, problem formulation, evaluation protocol, or empirical finding.

Do not define the target domain by venue, one dataset, one model, or terminology. A credible source outside the preferred venue list still occupies novelty when it implements the equivalent mechanism in the declared target domain.

## Baseline search families

Cover task names, benchmark names, dominant method families, recent surveys, current conference/arXiv work, explicit limitations, negative results, and neighboring tasks. Record query, source, date, filters, result count, screened count, retained count, and newly discovered clusters.

## Incremental search

Use the previous `coverage_end` with an overlap window. Search newly published work, new versions of known preprints, citations around closest work, and the saved kill queries of active ideas.

## Source roles

Mechanism discovery may use high-quality primary work from any field or venue. Treat an adjacent-field principle as provenance and mechanism support. It does not occupy target-domain novelty unless target-domain work has already instantiated the equivalent complete mechanism.

Target-domain adoption search must include all credible target-domain papers, artifacts, preprints, theses, and technical reports regardless of venue. Reviewer-pattern and venue-calibration corpora remain venue-scoped and do not define novelty.

## Two search depths

### Lightweight collision check

Use before development or a user-approved exploratory validation. Search the target task plus mechanism names, synonyms, operations, claimed behavior, and closest known work. Its outputs are only:

- `no-obvious-collision`;
- `collision-needs-revision`;
- `uncertain`.

It may block the unchanged version of an obvious duplicate, but must offer a material revision or rescue route. It may not declare formal novelty, reject the whole direction, or require search saturation.

### Focused strict novelty review

Use after a promising low-cost validation and before a full experiment campaign or paper-core novelty claim. If a low-cost probe is `not-applicable`, record why and run this review before formal experimentation. Continue until two materially different target-domain query families add no new close-work cluster, or record the hard access/time limit.

Return exactly one status:

- `supported`: no target-domain work occupying the complete claimed mechanism was found within the recorded search boundary;
- `occupied`: at least one verified target-domain work contains an equivalent complete operative mechanism at the claimed level;
- `uncertain`: evidence access, semantic ambiguity, or search coverage prevents a reliable decision.

Always attach coverage end, query families, evidence depth, closest work, and recall confidence. `supported` is bounded evidence, never proof that nobody has done the idea.

## Complete-mechanism occupation test

Count a mechanism as occupied only when target-domain work matches the material causal structure:

1. the operative mechanism is equivalent rather than merely sharing a goal or name;
2. key components, roles, information flow, and intervention can be completely mapped;
3. the match occupies the novelty unit and core claimed capability.

Shared motivation, one component, a source-domain principle, or separate papers covering different pieces are partial overlap. Record partial overlap and its effect on confidence or contribution strength, but do not call it complete occupation. If the mechanism is occupied but a different empirical or analytical claim remains, mark mechanism novelty occupied and assess the remaining claim separately.

## Independent conclusions

Report these independently:

- target-domain novelty status;
- cross-domain or historical source provenance;
- transfer/adaptation value and contribution strength;
- experimental maturity and evidence readiness.

A direct transfer may be target-domain novel but weakly adapted. An immature implementation may target a genuinely novel mechanism. Neither weakness may be rewritten as “not novel,” and strong empirical performance may not be rewritten as novelty evidence.

## Formal experiment admission

Focused review occurs after low-cost validation and before a full campaign. `uncertain` permits more search and user-approved low-cost validation, but it does not support promotion to a full paper-evidence campaign. `occupied` requires a changed novelty unit, material mechanism revision, or non-novel empirical/reproduction framing. Preserve promising results and offer a rescue route rather than discarding the whole direction.

## Full evaluation gates

Run these only in user-requested `gate` mode after the focused novelty status is recorded:

1. Contribution: the remaining differentiator creates a meaningful capability, explanation, resource, or empirical finding rather than a cosmetic recombination.
2. Feasible: data, compute, baselines, metrics, and a discriminating experiment are realistically available.
3. Identifiable: the proposed mechanism predicts an observation that the strongest alternative explanation does not.
4. Collision-resistant: discovery of one close paper does not erase every defensible contribution.

For failed attempts, separate:

- `genuinely-open`: no attempt found, with recall caveat;
- `partially-attempted`: attempts exist but outcome is inconclusive;
- `stale-blocker`: a named old limitation has a documented successor technology;
- `fundamental-risk`: multiple sources or a survey identify a problem-level barrier.

An isolated lack of recent papers never proves abandonment or impossibility.

## Evidence sources

Rank evidence:

1. verified primary papers, artifacts, and benchmark documentation;
2. official reviewer criteria and public review/meta-review records;
3. systematic syntheses and surveys;
4. informal experience posts.

Use informal sources to discover objections and search terms, not to establish novelty or venue policy.

## Candidate comparison

Only when the user explicitly requests full comparison, use `idea-evaluation-rubric.md`. Keep soundness and excitement separate. Scores summarize evidence; they never replace it, change the target-domain novelty status, or override fatal gates.
