# Exploratory Validation Before Formal Novelty Admission

Use this protocol for a user-approved low-cost run intended to learn whether an idea's mechanism is feasible or expressed by an implementation. It is not a formal experiment campaign, novelty verdict, leaderboard result, or paper-ready evidence source.

## Entry

Require a frozen `research-idea/validation-alignment-v3` artifact owned by
`research-idea-lab` for new problem-led work. Copy its parent problem identity,
alignment ID, idea revision, implementation revision, and path into an experiment
plan. Historical v1/v2 alignments remain readable but are launch-blocked until
migrated; they do not satisfy the new motivation-to-design and evidence-triad contract. Use:

```json
{
  "schema_version": "research-experiment/plan-v3",
  "admission_mode": "exploratory-validation",
  "idea_id": "",
  "idea_revision": 1,
  "implementation_revision": 1,
  "validation_alignment": {
    "artifact": "research_state/ideas/example/validation/example.yaml",
    "alignment_id": "example",
    "idea_revision": 1,
    "implementation_revision": 1,
    "parent_problem": {
      "problem_id": "example-problem",
      "problem_revision": 1,
      "problem_card": "research_state/problems/example-problem/problem_card.yaml",
      "problem_maturity": "solution-ready",
      "motivation_status": "evidence-backed"
    }
  },
  "method_identity": {
    "method_tier": "simplified",
    "publication_eligible": false,
    "scientific_configuration": "describe the validation implementation",
    "excluded_simplifications": ["list differences from the full proposed method"]
  }
}
```

Run `scripts/check_validation_alignment.py --alignment <path> --plan <path> --report <experiment-dir>/validation_alignment_check.json` before creating compute work. Bind the alignment ID plus idea and implementation revisions; do not require a generic local-file digest. A `not-applicable` idea skips this channel and returns to focused novelty review. A `not-identifiable` idea returns to development.

The lightweight target-domain status may be `no-obvious-collision` or `uncertain`. `collision-needs-revision` blocks only the unchanged version; return it to `research-idea-lab` for a material revision or reframed claim.

## User and resource boundary

The user must have seen the idea, baseline change, validation logic, possible outcomes, time, and cost. One approved round may execute autonomously within the frozen plan. The standing envelope is CNY 100 direct cost and 24 hours. A larger approval must be explicit in the alignment with `resource_override_approved: true`.

Never infer approval from prior interest, a cheap current machine, or a previous validation round. A new scientific question, mechanism revision, implementation revision that changes the approved behavior, dataset, metric, or budget requires a new alignment.

## Mechanism realization contract

Before launch, copy these items from the alignment into the plan or task descriptions:

- the selected problem, distinctive motivation, and derivation from bottleneck to
  module;
- the mechanism question and falsifiable prediction;
- strongest alternative explanation;
- activation evidence showing the program actually realizes and uses the mechanism;
- intervention evidence showing disable, shuffle, replacement, or another controlled perturbation changes the predicted behavior;
- supportive, negative, and inconclusive interpretations;
- quantitative evidence obligations for aggregate and bottleneck-targeted effects;
- qualitative evidence obligations and the predeclared non-cherry-picking case
  selection protocol;
- stop conditions.

Use cheap functional checks where applicable: verify inputs reach the module, outputs affect decisions, training signals update the intended parameters, a small positive-control case can express the behavior, and matched disable/shuffle/replacement controls have the predicted effect. Do not demand every neural diagnostic for a non-neural mechanism; use the smallest checks that establish faithful realization.

## Outcome attribution

Interpret evidence in this order:

1. `implementation-not-confirmed`: the code did not demonstrate activation or causal influence. Repair implementation, interfaces, optimization, or training under a new implementation revision.
2. `measurement-inconclusive`: the run could not distinguish the mechanism from alternatives. Repair sampling, measurement, or controls.
3. `mechanism-counterevidence`: realization passed, but the distinguishing prediction failed. Return counter-evidence to `research-idea-lab` for mechanism revision, scope change, or parking.
4. `supportive-signal`: realization passed and the distinguishing prediction appeared. Prioritize focused target-domain novelty review before a full campaign.

Report the observed metric immediately, but do not call an idea or mechanism failed until the relevant realization and measurement checks pass. A strong metric does not prove novelty.

## Iteration and records

Bind every run to the exact idea and implementation revision. Preserve all negative, mixed, and failed records. An implementation repair remains under the same idea revision; a causal mechanism change requires a new idea revision; a changed failure explanation or solution principle requires a linked derived idea from `research-idea-lab`.

There is no fixed scientific rescue count. Launch another round only when new evidence, a material mechanism change, or a justified implementation repair changes what the run can learn, and only after fresh user alignment. The existing three-fix pause still applies to repeated technical fixes for the same symptom.

Use the normal immutable run and readable logging contracts. Verification may set `verified-diagnostic`; it may not set `paper-ready`, create a writing handoff, or promote the idea to `experiment-ready`.
