# Cross-Domain Research Idea Transfer

Treat another discipline as a mechanism library, not a vocabulary source. Search source fields without venue restrictions. A source-field precedent establishes provenance, not target-domain occupation. Target-domain novelty is supported when a bounded adoption search across all credible target-domain sources finds no equivalent complete operative mechanism; whether the transfer adds enough adaptation or contribution value is a separate judgment.

## Source discovery

Start from a target-domain bottleneck or failure. Search fields that solve the same structural problem under different names:

- bounded memory or streaming constraints;
- delayed, sparse, or noisy evidence;
- causal attribution and counterfactual intervention;
- query planning and adaptive computation;
- partial observability and state estimation;
- compression with sufficient-statistic preservation;
- verification, provenance, and uncertainty;
- hierarchical temporal abstraction.

For VideoQA, inspect information retrieval, databases, streaming algorithms, control theory, cognitive memory, causal inference, program analysis, active perception, information theory, and sequential decision-making. Expand beyond this list when the problem structure suggests it.

## Transfer card

Create one card per source mechanism:

```yaml
source_domain: ""
source_problem: ""
source_mechanism: ""
source_evidence: []
target_problem: ""
structural_mapping:
  - source_entity: ""
    target_entity: ""
    shared_role: ""
conserved_invariant: ""
broken_assumptions: []
adaptations_required: []
target_adoption_queries: []
closest_target_work: []
new_capability_or_insight: ""
falsifiable_prediction: ""
negative_control: ""
transfer_risks: []
```

## Required tests

### Structural equivalence

Explain why source and target share relations, constraints, or invariants. Shared words, diagrams, or high-level goals are insufficient.

### Adoption search

Search:

- the source mechanism name plus target task;
- synonyms and predecessor names;
- source authors or citations appearing in target work;
- target methods implementing the same operations without the source terminology;
- partial transfers and failed attempts.

Report adoption-search recall limits. “No matching title found” is not evidence of non-adoption.

Predeclare the target domain by task, problem setting, and key constraints rather than venue, dataset, model, or terminology. A target-domain paper outside the preferred AI venue list still counts. A source-domain paper that never instantiates the mechanism in the target task does not count as target-domain occupation.

### Assumption audit

List assumptions that fail during transfer. Examples include stationarity, observability, differentiability, exact state, clean supervision, bounded delay, or known dynamics. Specify the required adaptation rather than importing the source method unchanged.

### Added-value test

Compare against the nearest native target-domain method. The transfer must add at least one of:

- a capability unavailable to native methods;
- a cleaner or more efficient mechanism;
- a testable explanatory framework;
- a new evaluation or diagnostic;
- a principled solution to a documented failure.

Renaming components or combining modules without necessity fails this added-value test, but it does not retroactively change a supported target-domain novelty conclusion into “not novel.” Report novelty and contribution strength independently.

### Falsifiable prediction

Name a condition where the transferred mechanism and the strongest native baseline predict different behavior. Prefer a negative control that disables the conserved mechanism while matching capacity and compute.

## Cross-field triangulation

When possible, generate candidates from at least two independent source fields. Favor principles supported under different assumptions over a fashionable technique from one field. Record conflicts rather than forcing convergence.

## Reporting

For each transferred candidate, state:

- source principle and verified source evidence;
- structural mapping;
- exact difference from target-domain work;
- broken assumptions and adaptations;
- prediction, negative control, and kill condition;
- novelty confidence in both source and target searches.

Do not describe a cross-domain origin itself as novelty. The novelty claim belongs to the unoccupied target-domain mechanism at the declared claim level. Report source provenance, target-domain novelty, transfer/adaptation value, and experimental maturity as separate conclusions.
