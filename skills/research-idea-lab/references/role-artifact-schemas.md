# Role and Debate Artifact Schemas

Use these schemas with `role-debate-protocol.md`. Keep artifacts concise, source-linked, revisioned, and readable. Fields may be extended, but required meanings must not be removed.

## Contents

- Directory layout
- Session manifest
- Evidence packet
- Candidate proposal
- Cross-examination
- Adversarial review
- Rebuttal
- Chair verdict
- Event log
- State ownership and compatibility

## Directory layout

```text
research_state/
  ideation_sessions/
    <session-id>/
      session.json
      evidence_packet.json
      native_candidates.yaml
      cross_domain_candidates.yaml
      candidate_clusters.yaml
      events.jsonl
  ideas/
    <idea-id>/
      idea_contract.yaml
      debate/
        debate_state.json
        cross_examination.yaml
        adversarial_review.yaml
        rebuttal.yaml
        chair_verdict.yaml
        events.jsonl
```

Use the session directory for divergent generation and clustering across multiple candidates. Use the idea directory after a stable candidate ID exists.

## Session manifest

```json
{
  "schema_version": "ideation-session/v1",
  "session_id": "20260731-videoqa-memory",
  "revision": 1,
  "status": "evidence-frozen",
  "execution_mode": "isolated-agent",
  "research_question": "",
  "target_domains": ["VideoQA"],
  "target_contribution_types": [],
  "coverage_start": "",
  "coverage_end": "",
  "evidence_frozen_at": "",
  "compute_constraints": {},
  "role_runs": {
    "native_innovator": {"status": "pending", "artifact": "native_candidates.yaml"},
    "cross_domain_researcher": {"status": "pending", "artifact": "cross_domain_candidates.yaml"},
    "adversarial_reviewer": {"status": "pending"},
    "chair": {"status": "active"}
  },
  "candidate_ids": [],
  "blocked_reasons": [],
  "updated_at": ""
}
```

Allowed session statuses:

`framing`, `evidence-frozen`, `divergent-generation`, `clustering`, `cross-examination`, `adversarial-review`, `rebuttal`, `chair-adjudication`, `user-decision`, `completed`, `blocked`.

## Evidence packet

```json
{
  "schema_version": "ideation-evidence/v1",
  "session_id": "",
  "freeze_timestamp": "",
  "research_boundary": {},
  "user_claims": [],
  "system_assumptions": [],
  "compute_constraints": {},
  "field_snapshot": {"path": "", "coverage_end": ""},
  "evidence": [
    {
      "evidence_id": "E001",
      "type": "primary-paper",
      "verification": "full-text",
      "identifier": "",
      "claim_supported": "",
      "source_url": ""
    }
  ],
  "coverage_limits": [],
  "refreshes": []
}
```

Use verification values `metadata`, `abstract`, or `full-text`. A refresh entry must state why it occurred and which artifacts became stale.

## Candidate proposal

Use this common envelope in both proposer files:

```yaml
schema_version: role-proposals/v1
session_id: ""
role: native_innovator
evidence_freeze: ""
candidates:
  - idea_id: ""
    revision: 1
    origin: native
    title: ""
    family_id: ""
    relation_to_family: new-family
    problem_signature: {}
    mechanism_signature: {}
    evaluation_signature: {}
    target_problem: ""
    documented_failure: ""
    importance: ""
    mechanism: ""
    causal_story: ""
    claimed_capability: ""
    contribution_type: ""
    evidence_ids: []
    closest_native_baseline: ""
    falsifiable_prediction: ""
    negative_control: ""
    simple_pilot_concept: ""
    kill_condition: ""
    expected_reviewer_attack: ""
    uncertainty: []
    transfer_card: null
```

For `cross_domain_researcher`, set `origin: cross-domain` and populate `transfer_card` using `cross-domain-transfer.md`.

## Cross-examination

```yaml
schema_version: cross-examination/v1
idea_id: ""
idea_revision: 1
evidence_freeze: ""
reviews:
  - reviewer_role: native_innovator
    disposition: revise
    claim: ""
    evidence_ids: []
    target_necessity: ""
    native_alternative: ""
    broken_assumptions: []
    proposed_change: ""
  - reviewer_role: cross_domain_researcher
    disposition: challenge
    claim: ""
    evidence_ids: []
    analogous_mechanisms: []
    missing_invariants: []
    proposed_change: ""
unresolved_disputes: []
```

Allowed dispositions are `support`, `revise`, `challenge`, and `replace`.

## Adversarial review

```yaml
schema_version: adversarial-review/v1
idea_id: ""
idea_revision: 1
strongest_rejection: ""
evidence_ids: []
closest_work:
  occupied_components: []
  remaining_differentiator: ""
  recall_confidence: low
mechanism:
  strongest_alternative: ""
  separating_intervention: ""
  predicted_observations: []
simple_baseline_threats: []
collision_scenario: ""
salvage_value: ""
reviewer_pattern_ids: []
fatal_gates:
  - gate: novelty
    status: unresolved
    evidence_ids: []
    repair_required: ""
anti_reskin:
  review_context_policy: cold
  independence_valid: false
  family_id: ""
  relation_to_family: ""
  causal_axes_changed: []
  inherited_failure_ids: []
  unresolved_failure_ids: []
  mechanism_signature_sha256: ""
  verdict: unresolved
attacks:
  - attack_id: A001
    dimension: novelty
    severity: major
    claim: ""
    evidence_ids: []
    required_evidence: ""
    repair_path: ""
counterproposal: null
verdict: revise
```

## Rebuttal

```yaml
schema_version: role-rebuttal/v1
idea_id: ""
from_revision: 1
to_revision: 1
responses:
  - attack_id: A001
    action: concede
    response: ""
    evidence_ids: []
    claim_change: ""
    mechanism_change: ""
withdrawn: false
stale_artifacts: []
```

Allowed actions are `concede`, `revise`, `counter-evidence`, and `withdraw`. Increment `to_revision` when the mechanism or primary claim changes.

## Chair verdict

```yaml
schema_version: chair-verdict/v1
idea_id: ""
idea_revision: 1
decision: revise
verified_evidence_ids: []
fatal_gates:
  passed: []
  unresolved: []
  failed: []
resolved_attacks: []
unresolved_attacks: []
minority_arguments: []
required_next_evidence: []
cheapest_discriminating_pilot_concept: ""
anti_reskin_gate:
  status: unresolved
  family_id: ""
  relation_to_family: ""
  unresolved_failure_ids: []
  report: ""
kill_conditions: []
fallback_contribution: ""
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
user_selection_required: true
decided_at: ""
```

Allowed decisions are `survive`, `revise`, `park`, `reject`, and `novelty-risk`.

## Event log

Write one JSON object per line:

```json
{"timestamp":"","event":"phase-changed","session_id":"","idea_id":null,"revision":1,"actor":"chair","from":"clustering","to":"cross-examination","artifact":"","summary":""}
```

Log evidence refreshes, role starts and completions, candidate creation, merges, revisions, concessions, gate changes, chair decisions, and user selections. Keep summaries readable and do not include private reasoning.

## State ownership and compatibility

- The Chair is the sole canonical writer for ideation sessions, idea-pool transitions, debate state, and the research-state index.
- Worker agents may create temporary outputs only when the Chair provides a bounded path; the Chair validates and promotes them.
- `idea_pool.json` remains the complete candidate registry, including parked and rejected candidates.
- New idea contracts use `research-idea/v3`. Treat existing `research-idea/v2` contracts as readable legacy records and migrate only when materially revising that idea.
- A debate decision does not set `experiment-ready`. That transition requires passed fatal gates and explicit user selection.
