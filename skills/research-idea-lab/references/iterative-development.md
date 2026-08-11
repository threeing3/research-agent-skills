# Iterative Idea Development and Validation Alignment

Use this protocol to keep rough ideas alive without confusing a failed implementation with a failed mechanism. Exploration may return incomplete seeds; only a user-approved validation run requires a complete alignment artifact.

## Maturity ladder

Track maturity separately from novelty and pool status:

- `seed`: records a concrete problem and a tentative way to address it. Missing mechanism, interface, search, or evidence links are allowed when named explicitly.
- `developing`: records the problem hypothesis, mechanism hypothesis, closest baseline, material unknowns, and at least one distinguishing prediction.
- `validation-ready`: records the exact idea and implementation revisions, validation question, realization checks, outcome interpretations, stop conditions, budget, and user approval.

A weak or incomplete seed is not a rejection. Move it forward by resolving the next decision-relevant unknown. Do not label it `validation-ready` merely because code can be written.

## Candidate types and portfolio coverage

Classify each returned candidate as one of:

- `mechanism-invention`;
- `baseline-modification`;
- `mechanism-combination`;
- `cross-domain-transfer`;
- `simplification-or-diagnostic`.

When a credible baseline is known, every returned portfolio of 3–5 candidates must contain at least one `baseline-modification` or `mechanism-combination` candidate. If the user names a baseline, prefer it. Otherwise select a provisional reproducible baseline, state why, and continue without blocking on routine confirmation.

An incomplete module idea may appear as a `seed`. It becomes `developing` only after the causal chain is explicit:

`baseline failure -> mechanism intervention -> implementation location -> predicted behavior -> isolating control`

## Baseline change blueprint

For `baseline-modification` and `mechanism-combination`, record:

```yaml
baseline_change:
  baseline_id: "paper, repository, commit, and configuration"
  selection_reason: ""
  target_failure: ""
  operation: add|replace|remove|rewire|combine
  location: "exact pipeline component or code boundary"
  before: "relevant original data/control/training flow"
  after: "flow after the proposed change"
  reused_parts: []
  redesigned_parts: []
  expected_resource_delta: ""
  required_ablations: []
```

Do not present “add module X” as a mature candidate without the target failure, insertion point, mechanism prediction, and isolating comparison. A known module may still support target-domain novelty when the complete target-domain mechanism is unoccupied; judge directness and adaptation value separately.

## Version rules

- An `implementation-revision` fixes code, interfaces, optimization, configuration, or measurement while leaving the problem and causal mechanism unchanged.
- A `mechanism-revision` keeps the problem and central solution principle but materially changes a causal operator, information flow, condition, or distinguishing prediction. Increment the idea revision.
- A `derived-idea` changes the central failure explanation or solution principle. Create a new idea ID and preserve the parent idea, revision, evidence, and reason for derivation.

Bind every validation and result to an exact idea revision and implementation revision. Results from one revision do not silently transfer to another.

## Probe applicability

Classify applicability before proposing a pre-gate validation:

- `applicable`: a low-cost observation can distinguish the mechanism from a strong alternative;
- `not-applicable`: only a formal-scale, real-environment, longitudinal, theoretical, or otherwise non-probe test can address the claim; record why and proceed to focused novelty review before formal work;
- `not-identifiable`: no observation at any realistic scale separates the mechanism from alternatives; revise the idea rather than skipping the problem.

The classification is mandatory even when the probe is skipped.

## Validation alignment artifact

Before any exploratory validation, create and freeze:

`research_state/ideas/<idea-id>/validation/<alignment-id>.yaml`

Use `research-idea/validation-alignment-v1` and validate it against the shared schema. The artifact must include:

```yaml
schema_version: research-idea/validation-alignment-v1
alignment_id: ""
idea_id: ""
idea_revision: 1
implementation_revision: 1
maturity: validation-ready
idea_type: baseline-modification
title: ""
problem_hypothesis: ""
mechanism_hypothesis: ""
target_domain_boundary:
  task: ""
  problem_setting: ""
  key_constraints: []
baseline_change: null
lightweight_collision_check:
  status: no-obvious-collision
  checked_at: ""
  target_domain_queries: []
  closest_target_work: []
  note: "No formal novelty verdict has been made."
validation:
  applicability: applicable
  applicability_reason: ""
  question: ""
  falsifiable_prediction: ""
  strongest_alternative: ""
  activation_evidence: []
  intervention_evidence: []
  outcome_interpretation:
    supportive: ""
    negative: ""
    inconclusive: ""
  stop_conditions: []
budget:
  max_direct_cost_cny: 100
  max_wall_time_hours: 24
user_alignment:
  status: approved
  approved_at: ""
  approved_scope: ""
  approved_max_direct_cost_cny: 100
  approved_max_wall_time_hours: 24
  resource_override_approved: false
```

The user must see the idea, baseline change, validation logic, cost, and time before `status: approved` is recorded. The standing envelope is at most CNY 100 and 24 hours per approved round. Exceeding either limit requires a new explicit approval and `resource_override_approved: true`.

## Realization and outcome semantics

The alignment must answer two questions before launch:

1. What observation shows that the program actually implements and activates the intended mechanism?
2. What behavior should change when the mechanism is disabled, shuffled, or replaced?

Interpret the run in this order:

- `implementation-not-confirmed`: realization evidence failed; update the implementation, not the mechanism claim;
- `measurement-inconclusive`: the test could not distinguish the mechanism; repair the measurement or control;
- `mechanism-counterevidence`: realization passed but the distinguishing prediction failed;
- `supportive-signal`: realization passed and the distinguishing prediction appeared.

A negative or inconclusive run never deletes the idea automatically. Continue only when new evidence, a material mechanism change, or a justified implementation repair changes what the next run can learn. Every new run requires a fresh user-approved alignment; there is no fixed scientific rescue count.

## Handoff boundary

`research-idea-lab` owns the idea revision and frozen alignment artifact. `research-experiment-lab` copies its SHA-256 into an `exploratory-validation` plan, validates the alignment, and owns execution and logs. Exploratory validation may prioritize development, but it cannot prove novelty, set `experiment-ready`, or enter a paper-ready writing handoff.
