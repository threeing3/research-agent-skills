# Research Process Metrics

Use these metrics to expose weak research processes before expensive experiments.
They are diagnostic measurements, not paper-quality scores or acceptance
probabilities. Keep raw counts, denominators, evidence IDs, assumptions, and missing
values beside every result. Never average away a fatal gate.

## Contents

- Metric selection
- Rival-separation coverage
- Ranking stability rate and flip radius
- Diagnostic failure-mode coverage
- Reviewer disagreement index
- Baseline resource-parity vector
- Novel-cluster yield curve
- Counter-evidence query coverage
- Practical sensitivity ratio
- Claim-evidence binding rate
- Kill-and-salvage branch coverage
- Candidate-skill provenance

## Metric selection

Use a four-check core instead of a fixed ten-metric form:

- Always inspect DFMC for a serious candidate.
- Inspect BRPV when making a superiority or efficiency claim.
- Inspect RSR only when comparing two or more candidates.
- Inspect RDI only when two or more suitably separated reviewers or roles rate the
  same dimensions.

Treat the remaining metrics as conditional quantifications of existing gates:

- Use RSC only when a central mechanism claim needs a quantified rival audit.
- Use NCY only for a search-saturation audit or unresolved novelty dispute.
- Use CEQC only when auditing the opposition-search protocol.
- Use PSR only after a smallest effect of scientific interest and a defensible minimum
  detectable effect exist; detailed estimation belongs in `research-experiment-lab`.
- Use CEBR only when central background or motivation claims are disputed, numerous,
  or being prepared for promotion.
- Use KSBC only before a costly or long experiment, while the ordinary kill-condition
  and salvage-value fields remain required for all serious candidates.

Use `not_applicable` when a metric has no definition for the current task, such as
ranking stability for a single candidate. Use `not_assessable` when the metric applies
but required evidence or a defensible denominator is missing. At screening depth,
report unweighted raw counts when weights are not yet anchored; do not turn missing
weights into a fabricated decimal. A metric is informative only when its inputs were
declared before inspecting the outcome it is meant to judge.

When weights are useful, predeclare uniform weights or use severity anchors `1=minor`,
`2=material`, and `3=central`. Record the rationale. Central exceptions remain visible
and noncompensatory. A single control may contribute to RSC and DFMC because their
denominators answer different questions: RSC concerns rival explanations of success;
DFMC concerns diagnoses of failure.

## 1. Rival-separation coverage

Measure whether the proposed observations distinguish the focal mechanism from
serious rivals.

```text
RSC = sum(weight_r * separated_r) / sum(weight_r)
```

Set `separated_r=1` only when at least one feasible intervention or observation has
different predeclared predictions under the focal mechanism and rival `r`. Record
indeterminate outcomes separately. Any high-severity rival with `separated_r=0`
keeps mechanism identifiability unresolved regardless of RSC.

Origin: the prediction-rival matrix and falsification controls in
`hypothesis-generation`.

## 2. Ranking stability rate and flip radius

Measure whether candidate ordering depends on contestable weights.

```text
RSR = scenarios_with_same_top_candidate / plausible_weight_scenarios
flip_radius = smallest relative weight perturbation that changes the top candidate
```

Use predeclared one-at-a-time and jointly plausible perturbations. Report rank ranges,
score intervals, and which criterion caused each flip. A stable ranking does not
establish validity; an unstable ranking reveals a value judgment or evidence gap.
Set the metric to `not_applicable` when fewer than two candidates are being compared.

Origin: the weight-sensitivity workflows in `scientific-brainstorming`.

## 3. Diagnostic failure-mode coverage

Measure whether a failed experiment will reveal why it failed.

```text
DFMC = sum(weight_f * observable_f) / sum(weight_f)
```

Enumerate material failure classes before the pilot, including data quality,
measurement, optimization, capacity, retrieval, prompting, implementation,
distribution shift, and mechanism failure. Use `observable_f=0` for no diagnostic,
`0.5` for a signal that narrows but does not isolate the class, and `1` for a
predeclared diagnostic that separates it from the strongest alternatives. List
high-severity blind spots separately; a high aggregate cannot hide one.

Origin: design-validity and bias analysis in `scientific-critical-thinking`, sharpened
by practitioner reports that useful research systems make failure modes inspectable.

## 4. Reviewer disagreement index

Measure independent-review disagreement rather than prematurely averaging it away.
For a 0-4 anchored dimension:

```text
RDI_dimension = mean_pairwise_absolute_difference / 4
```

Also report exact agreement, within-one-step agreement, missing ratings, and the
evidence IDs behind the largest disagreement. Resolve factual errors separately from
preference differences. Agreement is not proof of correctness.

Record independence as a vector: different human reviewers, different model families,
isolated context views, and no exposure to the desired verdict. Do not describe two
roles of the same model as independent without identifying the achieved and missing
forms of independence.

Origin: the agreement and responsible-assessment controls in `scholar-evaluation`.

## 5. Baseline resource-parity vector

Measure whether the proposed method receives an unfair experimental advantage.

```text
BRPV_k = method_resource_k / baseline_resource_k
log_gap_k = abs(log2(BRPV_k))
```

Report a vector, not a single blended score, for training compute, inference compute,
data, context or tokens, parameters, tuning trials, wall-clock time, external calls,
and human intervention. Mark each dimension `matched`, `justified_difference`, or
`unfair_or_unknown`. Use a factor-of-two gap only as a review trigger, never a
universal scientific threshold. An unfair or unknown central baseline comparison
blocks a superiority claim.

Predeclare the accounting window. Prefer hardware-independent quantities such as
FLOPs, tokens, examples, calls, and tuning trials; report hardware and wall time
separately. Keep inherited pretraining cost separate from experiment-specific cost.
When the baseline uses zero of a resource, do not divide by zero: report the absolute
method amount and mark the dimension `not_comparable_zero_baseline`.

Origin: matched-budget review in `peer-review` and recurring ML practitioner complaints
about tuning the proposed method more heavily than baselines.

## 6. Novel-cluster yield curve

Measure the marginal return of each materially different novelty-query family.

```text
NCY_q = newly_discovered_close_work_clusters_q / screened_relevant_records_q
```

Plot or tabulate cumulative close-work clusters against query families. Preserve
zero-result queries and distinguish retrieval failure from genuine zero yield. The
existing saturation rule remains: two consecutive materially different query families
with zero new close-work clusters permit stopping, subject to recorded access and recall
limits.

Before screening, define what makes query families materially different, such as a
different mechanism synonym set, target task alias, stronger/weaker variant,
source-domain vocabulary, citation neighborhood, or failure-oriented framing. Cluster
papers by shared operative mechanism and claimed capability, preserve stable cluster
IDs, and record merge/split decisions.

Origin: documented multi-database search and screening in `literature-review`.

## 7. Counter-evidence query coverage

Measure whether the search deliberately looked for evidence against the idea.

```text
CEQC = opposition_query_families_with_verified_evidence /
       predeclared_opposition_query_families
```

Opposition families should cover contradictory results, null results, failed
replications, limitations, negative controls, and stronger native alternatives when
applicable. A family may count when it yields verified evidence or a documented,
adequately screened zero result. Report the two cases separately. CEQC measures search
discipline, not whether the idea is true.

Count a zero-result family only when databases or indexes, exact queries, date,
filters, result count, screened count, terminology expansion, and access limits are
recorded. A blocked source or unscreened result set never counts as adequate zero
evidence. Do not impose one universal minimum database or record count; justify recall
against the domain and query family.

Origin: the contradictory/null evidence pass in `research-lookup`.

## 8. Practical sensitivity ratio

Measure whether the planned study can detect an effect small enough to matter.

```text
PSR = minimum_detectable_effect / smallest_effect_of_scientific_interest
```

Under the declared design assumptions, `PSR <= 1` means the study is sensitive enough
to detect the smallest effect considered meaningful; `PSR > 1` means a null result may
remain practically inconclusive. Report uncertainty and sensitivity to variance,
attrition, seed variance, multiplicity, and design effect. Do not compute observed
post-hoc power.

Origin: effect-size, power, and sensitivity analysis in `statistical-analysis`.

## 9. Claim-evidence binding rate

Measure traceable support for the factual background and motivation.

```text
CEBR = sum(weight_c * verified_binding_c) / sum(weight_c)
```

Assign larger predeclared weights to claims central to problem existence, importance,
and the alleged limitation. Set `verified_binding_c=1` only when the claim points to a
source ID whose exact support and locator were checked. Report metadata-only,
abstract-verified, and full-text-verified coverage separately. Unsupported central
claims keep the Background-Motivation-Method chain unresolved.

Origin: the claim/evidence registries in `scientific-writing`.

## 10. Kill-and-salvage branch coverage

Measure whether plausible outcomes lead to a predeclared decision and reusable value.

```text
KSBC = branches_with_threshold_decision_and_salvage / plausible_outcome_branches
```

For each positive, null, contradictory, and indeterminate branch, require: measurable
observation, threshold or decision rule, `continue/revise/kill` action, owner, and a
credible salvage artifact or lesson. Do not invent publishable fallback value. A
missing kill rule for the central failure branch blocks a long experiment.

At minimum enumerate positive, null, contradictory, and indeterminate branches, then
split them when different mechanisms or actions are possible. A salvage item is
credible only when its artifact, user, reuse path, and required evidence were named
before seeing the result.

Origin: milestone and contingency discipline in `research-grants`, combined with the
existing salvage-value and pilot-information-gain gates.

## Candidate-skill provenance

The metric designs were adapted from ten MIT-licensed Agent Skills reviewed at their
source, not copied as installation requirements:

1. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/hypothesis-generation/SKILL.md>
2. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-brainstorming/SKILL.md>
3. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-critical-thinking/SKILL.md>
4. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scholar-evaluation/SKILL.md>
5. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/peer-review/SKILL.md>
6. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/literature-review/SKILL.md>
7. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/research-lookup/SKILL.md>
8. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/statistical-analysis/SKILL.md>
9. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/scientific-writing/SKILL.md>
10. <https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/research-grants/SKILL.md>

Informal practitioner sources motivated DFMC and BRPV but do not establish their
validity or thresholds:

- <https://www.reddit.com/r/MachineLearning/comments/1qu4f9e/d_how_do_you_do_great_ml_research/>
- <https://www.reddit.com/r/MachineLearning/comments/1qu7voe/d_your_pet_peeves_in_ml_research/>
- <https://www.reddit.com/r/MachineLearning/comments/1fshhor/r_i_feel_underconfident_about_the_baselines_i/>
- <https://www.reddit.com/r/MachineLearning/comments/p4pv17/d_how_to_bring_novelty_in_machine_learning/>
- <https://www.reddit.com/r/MachineLearning/comments/1qu1tug/d_looking_for_advice_regarding_shortage_of/>
- <https://www.reddit.com/r/MachineLearning/comments/slov83/d_r_how_to_getextend_an_idea_from_toptier_ml_paper/>
- <https://colah.github.io/notes/taste/>
- <https://researchhowto.wordpress.com/blog/>

Treat all experience-post claims as search hypotheses. Calibrate them against primary
papers, official venue criteria, public reviews, and verified project evidence before
using them to block or promote an idea.
