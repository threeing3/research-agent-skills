# Information-Gain Iteration Control

Use this reference after a failed, inconclusive, or repeated implementation round, or whenever the next proposed step is another version of the same mechanism.

## Goal

Iteration is useful when it changes what can be learned. A new version number, cleaner code, more tolerant parsing, or a larger sample is not automatically a new scientific iteration.

## Four-question continuation note

Before recommending another round, record briefly:

```yaml
continuation:
  previous_uncertainty_change: ""
  new_observation: ""
  separating_predictions: ""
  repeated_result_action: "stop | narrow | return-to-diagnosis | revise-mechanism | other"
```

Use prose instead of this form when convenient. What matters is whether the answers are real.

If the previous result changed no scientific uncertainty and the next round exposes no new discriminating observation, do not continue the implementation branch merely because another repair is possible.

Give the branch a stable description based on the interface or scientific role
being repaired. A shift from parser failure to empty output, format instability,
low coverage, threshold failure, or fallback behavior does not start a new
branch when the fixes still serve the same realization. Surface symptom names
must not reset the low-information history.

## Classify what failed

### Engineering blocker

The intended mechanism or measurement never ran. Examples include a missing field, incompatible interface, device failure, empty output, invalid syntax, or evaluator bug.

Repairing it may be worthwhile when the intended behavior remains feasible and the repair has a clear completion condition. The failed run supplies engineering evidence, not mechanism evidence.

### Measurement failure

The mechanism ran, but the metric or sample cannot distinguish the central claim from alternatives. Repair the measurement before interpreting the mechanism.

### Mechanism counterevidence

The implementation is active and the isolating prediction fails. Continued work requires a material mechanism change, new evidence that invalidates the test, or a narrower claim. Prompt, parser, threshold, and fallback tuning under the same causal story are not enough by themselves.

### Problem counterevidence

The observed failure or proposed bottleneck weakens under a method-independent check. Return to problem discovery, narrow the conditions, or park the problem.

### Supportive signal

The intended mechanism is active and the distinguishing behavior appears. This supports further validation but does not by itself establish novelty, generality, or paper readiness.

## Natural interface viability

If the method requires a generated intermediate artifact, first check whether it naturally appears with useful coverage and quality. Examples include executable traces, grounded timestamps, retrieved evidence, pseudo-labels, uncertainty scores, or structured states.

When the interface repeatedly yields empty, invalid, or non-identifiable samples:

1. verify that the implementation matches the declared interface;
2. perform the cheapest representative feasibility check;
3. decide whether the interface itself is unsuitable;
4. avoid expanding the repair stack merely to manufacture evaluable cases.

Choose viability criteria from the scientific claim and intended analysis. Do not impose a universal threshold.

## Low-information warning

Two consecutive low-information rounds are a useful default warning, not an absolute stop. Continue only when at least one of the following is true:

- newly verified evidence changes a premise;
- a bounded engineering repair is likely to activate the originally declared mechanism;
- a material mechanism revision changes the separating prediction;
- a new control or measurement makes the result identifiable.

State why continuation is informative and what will end the branch. User preference, project risk, and resource cost may justify an earlier or later checkpoint.

If the parent problem and bottleneck remain supported but the current interface
or realization is infeasible, close that implementation branch and return to
solution exploration. Preserve the scientific problem without redefining it as
the task of making the failed interface work.

## Scope of an approved campaign

A user may approve a bounded validation campaign rather than every small engineering repair. The approved scope should identify the research question, model or baseline family, data, resource envelope, and allowed repair class.

Renew approval when cost, data, model, external system, central claim, or risk changes materially. Do not treat approval as permission for unrelated experiments or open-ended iteration.

## Handoff information

When a new experimental round is genuinely informative, hand off:

- the exact uncertainty being reduced;
- the method and implementation revisions;
- the new observation and competing predictions;
- evidence that the implementation can realize the mechanism;
- supportive, negative, and inconclusive outcomes;
- stopping conditions, resource envelope, and logging requirements.

The experiment workflow owns execution and verification. This reference controls the scientific reason to run, not the operational details.
