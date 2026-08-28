# Diagnostic Pilots

Use a diagnostic pilot to distinguish explanations for an observed failure. Its purpose is to locate the problem or bottleneck, not to demonstrate that a proposed method is effective.

## Lightweight handoff

The handoff may be prose or structured data, but it must identify:

```yaml
diagnostic_handoff:
  observed_failure: ""
  scope_or_prevalence: ""
  competing_explanations: []
  separating_prediction: ""
  measurement: ""
  intervention_boundary: ""
  outcome_interpretations:
    supports_explanation_a: ""
    supports_explanation_b: ""
    inconclusive: ""
  stop_condition: ""
```

Also declare the data, sample selection, model or baseline, resource envelope, and user authorization required by the actual run.

## Admission boundary

A diagnostic pilot does not require:

- an idea contract or `experiment-ready` status;
- a novelty or anti-reskin gate;
- a named mechanism family or mechanism signature;
- a complete method implementation;
- paper-scale seeds, ablations, robustness, or superiority claims.

It does require a real observed failure, at least two credible explanations, an identifiable measurement, outcome meanings, a feasible sample, and a stop condition.

## Allowed intervention

Prefer an observation or control independent of the proposed method. When pure observation cannot distinguish the explanations, allow the smallest diagnostic intervention that can do so, such as evaluator-side oracle events or states, component substitution, controlled input removal, prefix exposure, or frozen manual audit.

The intervention must expose an information boundary or causal difference. It must not instantiate the complete proposed method and then use the method's success as evidence that its own motivation was correct.

Ground-truth information used for diagnosis stays evaluator-side unless the intervention explicitly studies an oracle-input condition. Mark oracle conditions as upper bounds, not deployable methods.

## Planning and execution

- Set `admission_mode` to `diagnostic`.
- Use an execution `mode` such as `pilot`, `reproduction`, or `debug` according to the run shape.
- An idea ID, idea revision, contract hash, mechanism family, and anti-reskin report may be empty or null.
- Freeze the diagnostic handoff and sample-selection rule before observing the new result.
- Keep the normal immutable run IDs, readable logs, resource records, raw outputs, and verification artifacts.
- Permit engineering repairs only within the frozen measurement and intervention boundary. A repair that changes the scientific question creates a new plan revision and renewed authorization when scope changes materially.

## Interpretation

Return one of:

- `supports-explanation`: the predicted separating behavior appeared;
- `weakens-explanation`: the predicted behavior did not appear under a valid measurement;
- `measurement-inconclusive`: realization or measurement cannot separate the explanations;
- `scope-limited`: the effect exists only in a narrower sample or condition;
- `feasibility-blocked`: required data, labels, intervention, or baseline range is unavailable.

Verified diagnostic evidence updates problem or bottleneck state. It does not set novelty, `experiment-ready`, method validity, or `paper-ready`.

## Transition to method validation

Enter `method-validation` only after diagnostic evidence supports a bottleneck strongly enough to derive a required behavior and method hypothesis. Freeze a new plan linked to the approved idea contract. Do not mutate the diagnostic plan into a method campaign.

