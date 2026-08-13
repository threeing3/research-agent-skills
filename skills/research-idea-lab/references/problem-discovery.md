# Problem Discovery and Motivation

Use this reference before solution generation when the user asks for a direction,
open problem, bottleneck, background research, or an idea without supplying a
well-evidenced problem. The output is a problem portfolio, not a method portfolio.

## Evidence-first stance

Treat absence of papers as a search observation, never as evidence that a research
problem exists. Retain a problem only when at least one inspectable signal supports
it:

- a repeated failure across methods, datasets, operating conditions, or user groups;
- an unmet real constraint, capability, or decision need;
- contradictory findings that cannot be explained by protocol differences alone;
- a changed assumption that invalidates an established solution;
- an evaluation blind spot that prevents the claimed capability from being measured;
- a limitation supported by results, ablations, error analysis, or an inspectable
  artifact rather than an untested sentence in a paper.

Search Background research as problem forensics. Inspect full-text methods,
limitations, ablations, error breakdowns, qualitative failures, robustness and
distribution-shift results, efficiency analysis, negative results, dataset bias,
and follow-up papers. Record counter-evidence and successful cases as carefully as
failures.

## Frontier-first search

Prioritize problems that current papers are actively trying to solve. For every
baseline problem-discovery pass:

1. set `coverage_end` to the actual search date;
2. define a recent frontier window appropriate to the field's publication speed,
   normally the latest 12–18 months rather than a hard universal cutoff;
3. inspect the newest primary papers, accepted conference papers, preprints with
   inspectable methods/results, benchmark updates, and official artifacts;
4. cluster what these papers explicitly attempt to improve and which failures remain
   after their strongest results;
5. use older foundational and failure evidence to determine whether the issue is a
   persistent bottleneck, a newly exposed problem, or a temporary benchmark fashion;
6. record newly published counter-evidence that may show the problem has already
   weakened or changed.

Record each recent source with a stable source identifier, title, publication date,
source type, evidence depth, and whether it belongs to the target or an adjacent
domain. The publication date must fall inside the declared frontier window and may
not be later than `coverage_end`. If no inspectable source exists in that window,
leave `recent_sources` empty and record `recent_source_fallback_reason`; in that case
do not label the frontier signal `converging` or `newly-exposed`.

Prefer a problem when recent independent papers converge on it, a new capability or
setting exposes it, current best methods still show the same targeted failure, or a
new evaluation reveals that an apparently solved capability was mismeasured. Do not
prefer a problem solely because the paper is recent, the title calls it challenging,
or many papers repeat the same motivation.

For incremental passes, search from the previous `coverage_end` with an overlap
window and update the frontier evidence. Every output must state its coverage date
and distinguish peer-reviewed, preprint, abstract-only, and artifact-verified
evidence.

## Separate four layers

Do not collapse these layers:

1. `observed_failure`: the repeatable phenomenon and the conditions under which it
   occurs;
2. `bottleneck_hypothesis`: the proposed explanation for that failure;
3. `motivation_insight`: the non-obvious interpretation that changes what should be
   studied or designed;
4. `solution_route`: a later mechanism or research design derived from the selected
   bottleneck.

A low aggregate score is a phenomenon, not a bottleneck. A paper's limitation is a
lead, not a verified problem. A novel wording of a known failure is not a distinctive
motivation.

## Problem maturity

Track problem maturity independently from idea maturity:

- `problem-seed`: a concrete possible failure with missing confirmation;
- `evidence-backed`: the failure is supported, but its cause remains disputed;
- `bottleneck-framed`: at least one causal bottleneck and a separating observation
  are explicit;
- `solution-ready`: the problem, motivation insight, research value, tractability,
  and solution boundary are sufficient to generate mechanisms.

Incomplete problems remain investigable. Do not mark a problem closed merely because
one solution failed. Use `contested` when evidence conflicts, `parked` when access or
measurement blocks progress, and `closed` only when the stated failure is refuted,
already resolved under the declared conditions, or no longer meaningful.

## Distinctive motivation test

For every serious problem, write:

- the default interpretation a competent reader would infer from the literature;
- the proposed bottleneck interpretation;
- which verified observations the proposed interpretation explains better;
- the strongest competing explanation;
- one observation or intervention that separates them;
- the design implication if the proposed interpretation is correct;
- the evidence that would disconfirm or narrow the motivation.

Call the motivation `distinctive-hypothesis` while the separating evidence is
missing, `evidence-backed` when it survives the declared check, and `contested` when
credible alternatives remain. Never call an interpretation unique merely because
the current search did not find the same wording.

## Research value before solution design

Before `solution-ready`, record scientific, practical, and community value
separately:

- what knowledge changes if the problem is resolved;
- which task, system, stakeholder, or research practice benefits;
- why the issue is actionable now;
- what remains valuable without a state-of-the-art improvement;
- whether the problem survives failure of the first proposed solution;
- which evidence would make the problem no longer worth pursuing.

Weak or uncertain value produces a named evidence task, not an exploration-stage
rejection. The researcher decides whether to pursue a high-risk problem after seeing
the uncertainty.

## Problem card

Save reusable cards as
`research_state/problems/<problem-id>/problem_card.yaml` and validate them against
`schemas/problem-card.schema.json`. Link one problem to zero or more solution ideas;
do not require a method before the problem reaches `solution-ready`.

## Problem portfolio output

Return 3–5 materially different problem cards when the evidence supports them.
Variation must be in the failure, operating condition, affected capability,
bottleneck, stakeholder, or evidence type—not merely terminology. If fewer problems
are supportable, return the honest set plus the exact missing evidence routes.

For each problem, present in this order:

1. observed failure and conditions;
2. evidence and counter-evidence;
3. current approaches and what remains unresolved;
4. bottleneck hypotheses;
5. distinctive motivation insight and confidence;
6. research value and tractability;
7. next problem check;
8. only optional, clearly provisional solution principles.

## Stopping rule

Stop a problem-discovery pass when:

- the retained failures have inspectable evidence or are explicitly marked as
  problem seeds;
- phenomenon, bottleneck, and solution have not been conflated;
- each serious bottleneck has a competing explanation and separating observation;
- research value and tractability are explicit for every `solution-ready` problem;
- the next query is unlikely to change which problems deserve deeper investigation.

Do not stop because a target number of methods has been generated. Do not invent a
solution to make an uncertain problem look complete.
