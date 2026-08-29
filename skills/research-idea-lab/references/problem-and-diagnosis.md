# Problem and Bottleneck Diagnosis

Use this reference when a project has a topic, benchmark failure, rough method, or repeated implementation history but lacks an independently supported bottleneck.

## Purpose

The output is a research problem and a separating evidence plan, not a method proposal. A method may be discussed provisionally, but it must not be used as the evidence that its target problem exists.

## Minimal problem record

Keep the record as small as the task permits:

```yaml
problem:
  one_sentence: ""
  observed_failure: ""
  conditions: []
  scope_or_prevalence: ""
  evidence: []
  counter_evidence: []
  competing_explanations: []
  separating_check: ""
  research_value: ""
  feasibility_blockers: []
```

This is a semantic checklist, not a mandatory file format. Use prose when that is clearer. Save a structured card only when the result will be reused or handed off.

## One-sentence clarity test

State the problem without a new acronym, branded module, or implementation detail. A useful form is:

> Under [conditions], systems can do [capability A] but repeatedly fail at [capability B], and current evidence does not distinguish [explanation 1] from [explanation 2].

If a domain reader must first understand the proposed method to understand the problem, the framing is method-led and should be rewritten.

## Evidence for the phenomenon

Retain a problem only when at least one inspectable signal exists, such as:

- repeated failure across methods, samples, conditions, or datasets;
- an official artifact or error analysis exposing a missing capability;
- a contradiction between controlled conditions;
- an evaluation blind spot that changes the interpretation of reported results;
- an operational constraint that current systems demonstrably fail to satisfy.

A low aggregate score is a starting observation, not a causal diagnosis. A limitation sentence and an absence of papers are search leads, not problem evidence.

## Scope and prevalence

Estimate how broadly the phenomenon appears before developing a paper-scale method. The estimate may be lightweight, such as a frozen sample audit with counts by task or condition. Distinguish an isolated case, a recurring subgroup failure, and a broad capability failure. State uncertainty when the sample is small; do not turn one compelling example into a general problem claim.

## Competing explanations

Name the strongest simple explanation before introducing a new one. For a pipeline failure, useful alternatives often include:

- the input evidence is missing or ambiguous;
- the model did not perceive the relevant event;
- the model perceived it but lost order or memory;
- the representation was sufficient but the update rule failed;
- the state was correct but the query or output reasoning failed;
- the evaluator or annotation does not measure the intended behavior.

Do not require this list when it does not fit the task. Its purpose is to prevent one favorite explanation from becoming the default without evidence.

## Separating checks

A separating check makes competing explanations predict different observations. Prefer checks that:

- use existing data or official metadata;
- do not require the full proposed method to work;
- isolate one information boundary at a time;
- expose both supportive and disconfirming outcomes;
- remain interpretable when aggregate accuracy is near the floor or ceiling.

Examples include controlled input conditions, local versus cumulative probes, prefix evaluations, component substitution, oracle information at the evaluator side, and manual audit of a frozen sample. A minimal diagnostic intervention is valid when pure observation cannot identify the bottleneck, but the complete proposed method must not become the evidence for its own motivation. These are examples, not required stages.

## Feasibility before solution generation

Record blockers that could make the question unanswerable in the intended setting:

- unavailable labels, timestamps, data, code, or model access;
- a required latent variable that cannot be observed or approximated credibly;
- a baseline at the floor or ceiling;
- an evaluator that cannot distinguish the proposed outcomes;
- compute or annotation requirements outside the available envelope.

If the separating evidence is not obtainable, narrow the claim, choose another setting, or park the problem. Do not build a method whose central claim cannot be identified.

## Readiness for method design

A problem is ready to derive solutions when:

- the phenomenon is inspectable;
- its value survives failure of the first solution;
- at least one bottleneck and a credible alternative are explicit;
- a feasible observation can distinguish them;
- the intended dataset and evaluation can support the claim.

These are decision criteria, not a demand for a particular document, candidate count, or sequence of work.
