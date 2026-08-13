# Idea Contract

Create `research_state/ideas/<idea-id>/idea_contract.yaml`:

```yaml
schema_version: research-idea/v4
contract_profile: problem-led/v1
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
problem_derivation:
  problem_id: ""
  problem_revision: 1
  problem_card: "research_state/problems/<problem-id>/problem_card.yaml"
  problem_maturity: solution-ready
  observed_failure: ""
  bottleneck_hypothesis: ""
  distinctive_motivation_insight: ""
  motivation_status: evidence-backed
  research_value: ""
  required_behavior_change: ""
  design_principle: ""
  module_operation: ""
  implementation_location: ""
  motivation_to_design_chain: []
  evidence_triad:
    mechanism: []
    quantitative: []
    qualitative: []
development:
  maturity: formal-experiment-ready
  idea_type: mechanism-invention
  implementation_revision: 1
  probe_applicability: applicable
  probe_applicability_reason: ""
  validation_alignment_ids: []
  validation_evidence_paths: []
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
target_domain_boundary:
  task: ""
  problem_setting: ""
  key_constraints: []
  novelty_unit: operative-mechanism
ideation:
  session_id: ""
  execution_mode: isolated-agent
  origin: native
  proposer_role: native_innovator
  evidence_freeze_date: ""
  evidence_packet: ""
  candidate_cluster: ""
debate:
  status: not-requested
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
novelty_review:
  status: supported
  claim_unit: operative-mechanism
  coverage_end: ""
  recall_confidence: low
  query_families: []
  closest_target_work: []
  complete_mechanism_mapping: []
  source_provenance: ""
  transfer_adaptation_value: ""
  contribution_strength: ""
  experimental_maturity: ""
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
  selected_by_user: true
  selected_at: ""
```

The contract is an evidence-bearing formal-experiment handoff snapshot, not a promise
of acceptance and not the canonical current status. New pre-gate exploratory
validation uses `research-idea/validation-alignment-v3` instead and must not create an
active idea contract. Historical v1/v2 alignments remain read-only. `status` records the
state at issuance. `lifecycle` records whether that snapshot remains usable:

- `active`: the idea pool still says `experiment-ready`; the contract may be handed to experiments after all checks pass.
- `invalidated`: later literature, evidence, permissions, ethics, or experiment results block the issued handoff.
- `superseded`: a newer contract revision replaces this one.

When invalidating or superseding a contract, update only its lifecycle metadata and preserve the historical scientific content. Set `current_pool_status`, timestamp and event identifier, the concrete reason, and the replacement revision when applicable. Append the same transition to `logs/research_events.jsonl`.

Scores require evidence and cannot override a fatal gate. Any material mechanism change increments its revision and invalidates stale debate judgments and experiment plans. Before experiment handoff, require an `active` lifecycle, run `scripts/check_idea_lineage.py`, then run `scripts/check_idea_state_consistency.py` against the project state.

Every new `research-idea/v4` formal handoff must use
`contract_profile: problem-led/v1`. A historical staged contract may be relabeled
`legacy-read-only/v1` for inspection, but it cannot enter experiment handoff. Require the parent
problem ID and revision, evidence-backed failure, distinctive motivation, research
value, complete motivation-to-design derivation, and mechanism/quantitative/
qualitative evidence triad. Also require
`novelty_review.status: supported`, the predeclared target-domain boundary,
coverage end, recall confidence, complete-mechanism comparison, separate source
provenance/transfer-value/contribution/readiness conclusions, and explicit user
selection. `debate.status: not-requested` is valid when only focused novelty
review was needed. Full rubric scores, candidate ranking, reviewer simulation,
and an abandon decision remain optional unless the user explicitly requested
`gate` mode.

Existing staged contracts remain readable historical records but are not eligible for
new experiment admission. Do not rewrite their scientific content merely to add
problem-led fields. Materially revise and validate the idea against its current
problem card before issuing a new formal handoff.

Keep idea and implementation revisions distinct. Bug fixes, interfaces,
optimization, and other realization repairs increment the implementation
revision in validation artifacts without changing this contract revision. A
material causal change increments the idea revision; a change to the central
failure explanation or solution principle creates a linked idea ID.

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

Existing v4 contracts without `contract_profile`, `development`, or
`novelty_review` remain readable legacy snapshots. Add staged fields only when
materially revising or newly promoting the idea; do not bulk-rewrite history.
