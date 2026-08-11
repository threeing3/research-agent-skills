# Idea Contract

Create `research_state/ideas/<idea-id>/idea_contract.yaml`:

```yaml
schema_version: research-idea/v4
idea_id: videoqa-example
revision: 1
status: experiment-ready
lifecycle:
  validity: active
  current_pool_status: experiment-ready
  invalidated_at: null
  invalidated_by_event_id: null
  invalidation_reason: null
  superseded_by_revision: null
title: ""
lineage:
  family_id: ""
  relation_to_family: new-family
  parent_idea_id: null
  parent_revision: null
  delta_from_parent:
    causal_axes_changed: []
    unchanged_axes: []
    new_discriminating_prediction: ""
  inherited_failures: []
problem_signature:
  task: ""
  documented_failure: ""
  target_variable: ""
  operating_setting: ""
mechanism_signature:
  state: ""
  observation: ""
  action: ""
  learning_signal: ""
  supervision_source: ""
  causal_operator: ""
  intervention: ""
  claimed_capability: ""
evaluation_signature:
  unit_of_analysis: ""
  dataset_access: []
  primary_outcome: ""
  required_counterfactual: ""
  strongest_simple_baseline: ""
problem: ""
problem_half_life: ""
core_hypothesis: ""
mechanism: ""
contribution:
  type: ""
  primary_claim: ""
  fallback_claim: ""
  venue_fit: ""
source_domain:
  field: ""
  transferable_principle: ""
  structural_mapping: []
  conserved_invariant: ""
  broken_assumptions: []
  adaptations_required: []
  target_adoption_queries: []
  falsifiable_prediction: ""
  negative_control: ""
target_domain: ""
ideation:
  session_id: ""
  execution_mode: isolated-agent
  origin: native
  proposer_role: native_innovator
  evidence_freeze_date: ""
  evidence_packet: ""
  candidate_cluster: ""
debate:
  status: completed
  idea_revision_reviewed: 1
  cross_examination: ""
  adversarial_review: ""
  rebuttal: ""
  chair_verdict: ""
  fatal_attacks: []
  resolved_attacks: []
  unresolved_attacks: []
  minority_arguments: []
closest_work:
  - id: ""
    relation: ""
    difference: ""
novelty:
  confidence: low
  recall_confidence: low
  occupied_components: []
  remaining_differentiator: ""
  kill_queries: []
  collision_scenario: ""
  collision_resistant_contribution: ""
evaluation_rubric:
  fatal_gates:
    - gate: ""
      status: pass
      evidence: ""
  dimensions:
    problem_importance: {score: 0, confidence: low, evidence: ""}
    problem_half_life: {score: 0, confidence: low, evidence: ""}
    mechanism_clarity: {score: 0, confidence: low, evidence: ""}
    novelty_evidence: {score: 0, confidence: low, evidence: ""}
    collision_resistance: {score: 0, confidence: low, evidence: ""}
    soundness: {score: 0, confidence: low, evidence: ""}
    excitement: {score: 0, confidence: low, evidence: ""}
    testability: {score: 0, confidence: low, evidence: ""}
    evaluation_completeness: {score: 0, confidence: low, evidence: ""}
    feasibility: {score: 0, confidence: low, evidence: ""}
    salvage_value: {score: 0, confidence: low, evidence: ""}
mechanism_identifiability:
  strongest_alternative: ""
  separating_intervention: ""
  predicted_observations: []
  kill_or_revision_result: ""
simple_baseline_survival:
  baselines: []
  matched_resources: []
  value_if_matched: ""
reviewer_patterns:
  coverage_date: ""
  matched_accepts: []
  matched_rejects: []
  applicable_patterns: []
  fatal_risks: []
  required_evidence: []
  limitations: []
reviewer_attack_matrix:
  - attack: ""
    rationale: ""
    current_counter_evidence: ""
    required_evidence: ""
    severity: major
    status: open
evaluation:
  datasets: []
  baselines: []
  metrics: []
experiment_entry:
  recommended_mode: pilot
  cheapest_test: ""
  success_thresholds: []
  failure_thresholds: []
  confounders: []
  compute_budget: ""
  information_gain: ""
process_metrics:
  profile: core-plus-conditional/v1
  core_checks:
    diagnostic_failure_mode_coverage: {status: not_assessable, value: null, numerator: null, denominator: null, blind_spots: []}
    baseline_resource_parity: {status: not_applicable, dimensions: {}}
    ranking_stability_rate: {status: not_applicable, value: null, scenarios: 0, flip_radius: null}
    reviewer_disagreement_index: {status: not_applicable, by_dimension: {}}
  conditional_metrics:
    rival_separation_coverage: {status: not_applicable, value: null, numerator: null, denominator: null, exceptions: []}
    novel_cluster_yield: {status: not_applicable, by_query_family: []}
    counter_evidence_query_coverage: {status: not_applicable, value: null, numerator: null, denominator: null}
    practical_sensitivity_ratio: {status: not_applicable, value: null, assumptions: []}
    claim_evidence_binding_rate: {status: not_applicable, value: null, numerator: null, denominator: null}
    kill_and_salvage_branch_coverage: {status: not_applicable, value: null, numerator: null, denominator: null, missing_branches: []}
blockers: []
anti_reskin_gate:
  status: pass
  review_context_policy: cold
  proposer_model_family: ""
  reviewer_model_family: ""
  independence_valid: true
  mechanism_signature_sha256: ""
  unresolved_failure_ids: []
  verdict: new-family
  report: ""
decision:
  selected_by_user: false
  selected_at: ""
```

The contract is an evidence-bearing handoff snapshot, not a promise of novelty or acceptance and not the canonical current status. `status` records the state at issuance. `lifecycle` records whether that snapshot remains usable:

- `active`: the idea pool still says `experiment-ready`; the contract may be handed to experiments after all checks pass.
- `invalidated`: later literature, evidence, permissions, ethics, or experiment results block the issued handoff.
- `superseded`: a newer contract revision replaces this one.

When invalidating or superseding a contract, update only its lifecycle metadata and preserve the historical scientific content. Set `current_pool_status`, timestamp and event identifier, the concrete reason, and the replacement revision when applicable. Append the same transition to `logs/research_events.jsonl`.

Scores require evidence and cannot override a fatal gate. Any material mechanism change increments its revision and invalidates stale debate judgments and experiment plans. Before experiment handoff, require an `active` lifecycle, run `scripts/check_idea_lineage.py`, then run `scripts/check_idea_state_consistency.py` against the project state.

Preserve its `research-idea/state-consistency-v2` report. The report binds the
current idea pool and every discovered contract by SHA-256 and records each
contract revision; any later file change makes that report stale for experiment
prelaunch and writing handoff.

Treat existing `research-idea/v2` and `research-idea/v3` contracts as readable
legacy records. Migrate one to v4 only when materially revising or promoting
that idea; do not bulk-rewrite historical contracts. Run
`scripts/check_idea_lineage.py` before experiment handoff and store its report
beside the contract.

Existing v4 contracts without `lifecycle` are also readable legacy snapshots. Do not bulk-rewrite them. If the current pool no longer says `experiment-ready`, the state-consistency check must fail until an explicit lifecycle decision is recorded.
