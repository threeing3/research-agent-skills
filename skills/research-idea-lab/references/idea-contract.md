# Idea Contract

Create `research_state/ideas/<idea-id>/idea_contract.yaml`:

```yaml
schema_version: research-idea/v3
idea_id: videoqa-example
revision: 1
status: experiment-ready
title: ""
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
blockers: []
decision:
  selected_by_user: false
  selected_at: ""
```

The contract is an evidence-bearing handoff, not a promise of novelty or acceptance. Scores require evidence and cannot override a fatal gate. Any material mechanism change increments its revision and invalidates stale debate judgments and experiment plans.

Treat existing `research-idea/v2` contracts as readable legacy records. Migrate one to v3 only when materially revising that idea; do not bulk-rewrite historical contracts.
