# Research Opportunity Map

Use an opportunity map to turn literature coverage into an evidence-backed problem
space. It is not a novelty verdict, solution portfolio, or kill gate.

## Required reasoning

For each closest-work cluster, distinguish:

- `covered`: problem, mechanism, setting, and evidence already established;
- `observed_failures`: supported failures, contradictions, changed assumptions, or
  evaluation blind spots;
- `under_tested`: conditions, users, constraints, bottlenecks, mechanisms, or outcomes not adequately tested;
- `bottleneck_alternatives`: competing causal explanations and their separating
  observations;
- `motivation_insight`: what the proposed interpretation explains beyond the default
  reading of the literature;
- `research_value`: scientific, practical, and community value independent of
  state-of-the-art gain;
- `why_now`: a changed capability, dataset, cost, platform, theory, or evaluation need that makes the gap actionable;
- `differentiation`: a material route not erased by the closest work;
- `rescue`: a narrower or alternative route if the first claim collides;
- `closure_evidence`: evidence that would show the opportunity is actually occupied or infeasible.

Do not infer an opportunity from paper absence alone. Require a documented failure,
unmet constraint, contradictory result, invalid measurement, changed assumption, or
structurally justified transfer. A limitation sentence without supporting evidence is
a search lead, not an opportunity.

## Artifact

Save reusable maps as `research_state/ideation_sessions/<session-id>/opportunity_map.yaml`:

```yaml
schema_version: research-opportunity-map/v1
session_id: ""
work_mode: problem-discovery
coverage_mode: baseline
coverage_end: ""
scope:
  problem: ""
  tasks: []
  constraints: []
  adjacent_fields: []
source_limits: []
clusters:
  - cluster_id: ""
    representative_sources: []
    evidence_depth: metadata|abstract|full-text
    covered:
      problem: ""
      mechanism: ""
      setting: ""
      evidence: ""
    observed_failures: []
    under_tested: []
    bottleneck_alternatives: []
    motivation_insight:
      default_interpretation: ""
      proposed_interpretation: ""
      explanatory_advantage: ""
      design_implication: ""
      status: unknown
    research_value:
      scientific: ""
      practical: ""
      community: ""
      value_without_sota_gain: ""
    why_now: ""
    differentiation_routes: []
    rescue_routes: []
    closure_evidence: []
    confidence: low|medium|high
candidate_spaces:
  - space_id: ""
    source_clusters: []
    problem_axis: ""
    mechanism_axes: []
    evidence_axes: []
    contribution_axes: []
    candidate_seed_ids: []
problem_card_ids: []
open_queries: []
```

## Search-to-idea handoff

Every retained cluster must contribute at least one of:

- an evidence-backed problem or explicit problem seed;
- a bottleneck hypothesis and separating observation;
- a differentiation route;
- a rescue route;
- a closure condition that prevents wasted development.

If a cluster contributes only “already done,” the map is incomplete. State which
failure, bottleneck, setting, measurement, or contribution remains movable before
concluding that the direction is closed. Do not require every cluster to yield a
solution idea.

## Source scope

Use primary and inspectable sources. The AI venue list may calibrate reviewer patterns and target-venue expectations, but it must not block high-quality adjacent-field sources used for mechanism discovery, theory, datasets, or cross-domain transfer.
