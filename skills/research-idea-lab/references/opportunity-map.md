# Research Opportunity Map

Use an opportunity map to turn literature coverage into candidate space. It is not a novelty verdict or kill gate.

## Required reasoning

For each closest-work cluster, distinguish:

- `covered`: problem, mechanism, setting, and evidence already established;
- `under_tested`: conditions, users, constraints, mechanisms, or outcomes not adequately tested;
- `why_now`: a changed capability, dataset, cost, platform, theory, or evaluation need that makes the gap actionable;
- `differentiation`: a material route not erased by the closest work;
- `rescue`: a narrower or alternative route if the first claim collides;
- `closure_evidence`: evidence that would show the opportunity is actually occupied or infeasible.

Do not infer an opportunity from paper absence alone. Require a documented failure, unmet constraint, contradictory result, missing comparison, changed assumption, or structurally justified transfer.

## Artifact

Save reusable maps as `research_state/ideation_sessions/<session-id>/opportunity_map.yaml`:

```yaml
schema_version: research-opportunity-map/v1
session_id: ""
work_mode: explore
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
    under_tested: []
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
open_queries: []
```

## Search-to-idea handoff

Every retained cluster must contribute at least one of:

- a candidate seed;
- a differentiation route;
- a rescue route;
- a closure condition that prevents wasted development.

If a cluster contributes only “already done,” the map is incomplete. State which problem, mechanism, setting, evidence type, or contribution remains movable before concluding that the direction is closed.

## Source scope

Use primary and inspectable sources. The AI venue list may calibrate reviewer patterns and target-venue expectations, but it must not block high-quality adjacent-field sources used for mechanism discovery, theory, datasets, or cross-domain transfer.
