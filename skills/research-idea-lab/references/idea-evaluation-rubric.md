# Research Idea Evaluation Rubric

Use this rubric only in user-requested full `gate` mode for scoring, ranking, investment, or abandon decisions. Focused target-domain novelty review and user-approved pre-gate validation do not load or require this rubric. Keep `soundness` and `excitement` independent. Record evidence beside every score; do not average away a fatal gate.

## Decision sequence

Evaluate in this order:

1. **Problem durability**: Is the problem important, real, and likely to remain relevant long enough to finish the work?
2. **Contribution fit**: Is the intended contribution a method, capability, empirical discovery, benchmark/resource, reframing, or theory/analysis contribution? Would the target venue recognize that contribution type?
3. **Mechanism identifiability**: Can an experiment distinguish the claimed mechanism from extra capacity, data, compute, prompting, retrieval, or engineering?
4. **Simple-baseline survival**: Would a cheap heuristic, stronger prompt, larger context, retrieval baseline, or matched-compute baseline plausibly erase the claimed gain?
5. **Novelty and collision resistance**: Is the remaining differentiator meaningful, and would it survive discovery of a near-simultaneous paper?
6. **Mechanism lineage**: Is this a genuinely new family or material causal revision, and are prior family failures still active?
7. **Soundness**: Are assumptions coherent and claims falsifiable? Is there a credible evaluation path?
8. **Excitement**: If true, would the result change capability, understanding, practice, evaluation, or future research?
9. **Pilot information gain**: Does the cheapest pilot strongly update belief in the mechanism rather than merely produce another metric?

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
- the proposal is a cosmetic variant of a failed or occupied mechanism family;
- an inherited family failure remains unresolved;
- the pilot's minimum prerequisites are mutually unsatisfiable under current data, compute, budget, or permissions.

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

This section governs promotion through a user-requested full `gate`. A focused
`novelty` review may separately prepare a selected idea for formal experiments
under the staged contract in `idea-contract.md`; it must still satisfy focused
novelty, lineage, identifiability, feasibility, and user-selection requirements
but need not manufacture numeric comparison scores.

Promote only when:

- all fatal gates pass;
- contribution type and primary claim are explicit;
- novelty and recall confidence are recorded;
- a discriminating pilot exists;
- reviewer attacks have named evidence requirements;
- the mechanism family, structured signatures, material delta, inherited failures, and cold anti-reskin verdict are recorded;
- `scripts/check_idea_lineage.py` passes and the pilot prerequisites are jointly satisfiable;
- the user explicitly selects the idea.
- the four core process checks and only the triggered conditional metrics in
  `research-process-metrics.md` include raw counts, denominators, evidence,
  assumptions, and missingness;
- no high-severity rival lacks a separating test, no central failure mode lacks a
  diagnostic, no superiority claim relies on an unfair or unknown baseline, every
  central background/motivation claim is evidence-bound, and the central negative
  outcome has a kill or revision rule.

## Research-process metric dashboard

Use `research-process-metrics.md` after the fatal gates and before promotion. Always
inspect DFMC; inspect BRPV for superiority or efficiency claims, RSR/flip radius for
multi-candidate comparisons, and RDI for multi-reviewer ratings. Report RSC, NCY,
CEQC, PSR, CEBR, or KSBC only when its documented trigger applies. Do not sum or
average them. Interpret each metric beside its raw inputs and high-severity exceptions.
A perfect aggregate cannot repair one unresolved central exception.

## Background–Motivation–Method coherence gate

Before promotion, write the idea as a three-part chain:

`Background → Motivation → Method`

Score each link from 0 to 4 with evidence. These are readiness scores, not probabilities.

| Dimension | 0 | 2 | 4 |
| --- | --- | --- | --- |
| Background grounding | vague topic or unsupported setting | real problem with partial field evidence | precise setting, affected users/tasks, close work, and stable evidence boundary |
| Motivation necessity | method is not needed or gap is rhetorical | plausible limitation but weak counterfactual | a concrete failure or unmet need that existing alternatives cannot resolve |
| Method alignment | method is a renamed component or unrelated trick | plausible response with unresolved causal gaps | each method choice directly targets a named failure and yields a falsifiable prediction |
| Method novelty | occupied or unsearched | partial distinction | clear differentiator that survives close-work and collision checks |

Also score three mappings from 0 to 4:

- `background_to_motivation`: does the background evidence make the motivation necessary?
- `motivation_to_method`: does the method address the stated motivation rather than a different problem?
- `method_to_evaluation`: can the planned experiment distinguish the method from capacity, data, prompting, retrieval, or implementation confounds?

Use the following readiness index only after the fatal gates pass:

```text
base = 0.20*background + 0.25*motivation + 0.25*method_alignment + 0.15*method_novelty + 0.15*evaluation_fit
coherence = min(background_to_motivation, motivation_to_method, method_to_evaluation)
idea_readiness = 0.70*base + 0.30*coherence
```

`evaluation_fit` is the existing evaluation-completeness score normalized to 0–4. The minimum-link rule is intentional: a polished method cannot compensate for an invented background, and a strong motivation cannot compensate for a method that does not test it.

Promotion guidance:

- Any of the four dimensions below 2: `revise` or `park`, never `experiment-ready`.
- Any mapping below 2: rewrite the chain and specify the missing evidence or intervention.
- `idea_readiness < 2.5`: exploratory only; allow a user-approved low-cost validation under `iterative-development.md`, but do not start a full experiment campaign.
- `2.5 ≤ idea_readiness < 3.2`: allow a bounded pilot with explicit kill criteria.
- `idea_readiness ≥ 3.2`, all links ≥ 3, and fatal gates pass: eligible for user-selected experiment design.

Always store the one-sentence background, one-sentence motivation, one-sentence method, the six scores, evidence notes, and the weakest link beside the numeric index. Do not report the index as a probability of acceptance.

Never use these readiness scores to convert a target-domain novelty conclusion
into “not novel.” Contribution strength, adaptation value, and experimental
maturity remain separate from novelty occupation.
