# Research Idea Evaluation Rubric

Use this rubric after field mapping and before experiment handoff. Keep `soundness` and `excitement` independent. Record evidence beside every score; do not average away a fatal gate.

## Decision sequence

Evaluate in this order:

1. **Problem durability**: Is the problem important, real, and likely to remain relevant long enough to finish the work?
2. **Contribution fit**: Is the intended contribution a method, capability, empirical discovery, benchmark/resource, reframing, or theory/analysis contribution? Would the target venue recognize that contribution type?
3. **Mechanism identifiability**: Can an experiment distinguish the claimed mechanism from extra capacity, data, compute, prompting, retrieval, or engineering?
4. **Simple-baseline survival**: Would a cheap heuristic, stronger prompt, larger context, retrieval baseline, or matched-compute baseline plausibly erase the claimed gain?
5. **Novelty and collision resistance**: Is the remaining differentiator meaningful, and would it survive discovery of a near-simultaneous paper?
6. **Soundness**: Are assumptions coherent and claims falsifiable? Is there a credible evaluation path?
7. **Excitement**: If true, would the result change capability, understanding, practice, evaluation, or future research?
8. **Pilot information gain**: Does the cheapest pilot strongly update belief in the mechanism rather than merely produce another metric?

## Scored dimensions

Score each dimension from 0 to 4 with a short evidence note and confidence.

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Problem importance | artificial or negligible | useful but narrow | consequential and well evidenced |
| Problem half-life | likely obsolete before completion | medium-lived | persistent or growing |
| Mechanism clarity | slogan or component list | plausible causal story | explicit, discriminable mechanism |
| Novelty evidence | occupied or unsearched | partial distinction | strong search coverage and clear differentiator |
| Collision resistance | one close paper destroys it | salvageable secondary claim | contribution remains valuable after close work |
| Soundness | contradiction or fatal flaw | plausible with open risks | assumptions and validation path are strong |
| Excitement/significance | metric-only local gain | useful advance | unlocks capability, insight, or research direction |
| Testability | no decisive feasible test | indirect test | cheap falsifying or discriminating test |
| Evaluation completeness | unsuitable evidence | core benchmark only | direct metrics, strong baselines, generalization, failures |
| Feasibility | unavailable data/compute | possible with material risk | feasible within stated resources |
| Salvage value | failed hypothesis yields little | reusable artifact or lesson | multiple publishable outcomes or durable resource |

Scores compare candidates; they are not probabilities or acceptance predictions.

## Fatal gates

Mark a gate `pass`, `unresolved`, or `fail`:

- the complete claimed contribution is already occupied;
- no experiment can identify the proposed mechanism;
- the idea loses to an obvious simple or matched-budget baseline;
- required data, compute, or evaluation access is unavailable;
- the central claim depends on leakage, invalid measurement, or unethical data use;
- the contribution type does not support the intended claims.

An unresolved or failed fatal gate blocks `experiment-ready`.

## Mechanism-identifiability check

Write:

- proposed causal mechanism;
- strongest alternative explanation;
- variable or intervention that separates them;
- expected observation under each explanation;
- result that kills or revises the mechanism.

If the same result is predicted by the proposed mechanism and the strongest alternative, the current experiment is not discriminating.

## Simple-baseline survival test

Construct the cheapest credible competitor before adding method complexity:

- heuristic or rule-based baseline;
- prompt/context/retrieval-only baseline;
- standard method with equal data, parameters, tokens, latency, and compute;
- oracle or upper-bound diagnostic where useful.

State what remains valuable if the simple baseline matches performance. If nothing remains, treat this as a fatal risk.

## Collision-resistance test

Assume a close paper appears tomorrow. Ask:

- Which exact claim becomes occupied?
- Does the idea retain a distinct mechanism, task, evidence, efficiency result, failure analysis, benchmark, or theory?
- Can the work become a stronger comparative or empirical study without misrepresenting novelty?

Record a primary contribution and at least one defensible fallback contribution. Do not invent fallback value after experiments fail.

## Problem and benchmark half-life

Estimate whether the problem, benchmark, and enabling assumptions remain relevant across the project timeline. Check:

- replacement datasets or evaluation protocols;
- rapidly expanding context windows or model access;
- benchmark saturation, leakage, or judge unreliability;
- dependencies on temporary API behavior or unavailable proprietary systems.

Do not reject fast-moving problems automatically; require a plan whose claim survives likely platform changes.

## Pilot information gain

Prefer the pilot that best separates competing explanations per unit of time and compute. Record:

- prior belief and alternatives;
- possible outcomes;
- belief update caused by each outcome;
- cost, duration, and reuse value.

A tiny benchmark run with no mechanism discrimination has low information gain even when cheap.

## Reviewer Attack Matrix

For each serious candidate, create:

| Attack | Why a reviewer may believe it | Current counter-evidence | Required evidence | Severity | Status |
| --- | --- | --- | --- | --- | --- |

Cover at least novelty, soundness, significance, evaluation, reproducibility, efficiency, data integrity, and venue fit. Populate it with close-work analysis and matched public-review patterns when available.

## Promotion rule

Promote only when:

- all fatal gates pass;
- contribution type and primary claim are explicit;
- novelty and recall confidence are recorded;
- a discriminating pilot exists;
- reviewer attacks have named evidence requirements;
- the user explicitly selects the idea.

## Background–Motivation–Method coherence gate

Before promotion, write the idea as a three-part chain: `Background → Motivation → Method`.

Score each link from 0 to 4 with evidence. These are readiness scores, not probabilities.

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Background grounding | vague topic or unsupported setting | real problem with partial field evidence | precise setting, affected users/tasks, close work, and stable evidence boundary |
| Motivation necessity | method is not needed or gap is rhetorical | plausible limitation but weak counterfactual | a concrete failure or unmet need that existing alternatives cannot resolve |
| Method alignment | method is a renamed component or unrelated trick | plausible response with unresolved causal gaps | each method choice directly targets a named failure and yields a falsifiable prediction |
| Method novelty | occupied or unsearched | partial distinction | clear differentiator that survives close-work and collision checks |

Also score `background_to_motivation`, `motivation_to_method`, and `method_to_evaluation` from 0 to 4. Use:

```text
base = 0.20*background + 0.25*motivation + 0.25*method_alignment + 0.15*method_novelty + 0.15*evaluation_fit
coherence = min(background_to_motivation, motivation_to_method, method_to_evaluation)
idea_readiness = 0.70*base + 0.30*coherence
```

Any dimension or mapping below 2 blocks `experiment-ready`. Scores below 2.5 are exploratory only; 2.5–3.2 allows a bounded pilot; ≥3.2 with all links ≥3 and passed fatal gates is eligible for user-selected experiment design. Store the three one-sentence statements, six scores, evidence notes, and weakest link. Never present the index as an acceptance probability.
