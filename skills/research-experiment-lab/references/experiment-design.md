# Experiment Design

## Campaign contract

Declare `admission_mode` first. For `exploratory-validation`, follow
`exploratory-validation.md` and bind the user-approved validation alignment.
For `formal`, bind the active idea contract and formal prelaunch evidence. Do
not let a cheap validation silently become a full campaign.

Define one campaign around an idea revision or reproduction question. Record:

- research question and falsifiable mechanism prediction;
- null or trivial explanation;
- mode and evidence claims;
- datasets, immutable split identifiers, preprocessing, and evaluation code;
- direct competitors, foundations, and ablation anchors;
- variants, seeds, metrics, uncertainty method, and comparison unit;
- robustness, efficiency, and failure-analysis obligations;
- a three-part evidence plan covering mechanism causality, quantitative improvement,
  and qualitative behavior change;
- success, failure, and stop thresholds set before formal results;
- compute, wall-time, retry, parallelism, and download budgets;
- confounders and controls.
- mechanism family, mechanism-signature hash, inherited failure IDs, and the
  passed anti-reskin report;
- evidenced prerequisite constraints whose available values make every frozen
  scientific threshold attainable.

For campaigns authorized to continue automatically, additionally define a task
graph with explicit dependencies, required verification gates, next-step
commands, retry limits, download budgets, and AutoDL lifecycle permissions.
Intermediate success must lead to a predeclared successor when eligible; a
failure must lead to a predeclared recovery, block, or review transition.

Use at least three random seeds for stochastic formal comparisons when feasible.
If fewer are possible, record the constraint and weaken statistical claims.
Keep pilots diagnostic; keep full campaigns paper-complete.

An exploratory validation may use one seed or a narrow controlled subset when
that is sufficient for its frozen diagnostic question. Do not present that
choice as formal uncertainty evidence. A full campaign still follows the
multi-seed and paper-completeness requirements.

## Motivation-to-evidence contract

Bind the plan to the parent problem, distinctive motivation, and exact module
derivation from the idea alignment or contract. Translate the motivation into:

- a targeted subset, condition, or diagnostic on which the bottleneck should appear;
- a mechanism intervention that distinguishes the module from capacity, data,
  prompting, retrieval, or optimization effects;
- an aggregate quantitative comparison and a bottleneck-targeted quantitative
  comparison;
- a qualitative analysis with categories and case-selection rules declared before
  inspecting favorable examples.

Qualitative evidence should compare the same cases across baseline, full method, and
relevant ablation when possible. Include failures, regressions, and unchanged cases.
Do not select examples only because the proposed method succeeds.

## Autonomy envelope

Within the frozen plan, allow autonomous path fixes, environment fixes, memory
optimizations, resumption, invalid-seed reruns, diagnostic runs, and
predeclared hyperparameter adjustments. Record the reason before each run.

Require human review before changing the hypothesis, primary dataset, main
metric, success threshold, core method, baseline set, or budget ceiling.
`research-idea-lab` revisions must be detected before launch; results observed
before such a change remain attached to the prior plan revision, and queued
tasks become stale until a new plan revision is created.

Before allocating compute, run the lineage and satisfiability checks in
`prelaunch-reconciliation.md`. If a required sample count, action class,
intervention, access permission, or resource minimum cannot be met, mark the
campaign blocked. Do not reinterpret an undersized diagnostic as a formal test.

## Fairness

Prefer official baseline implementations. Record repository URL, commit,
license, checkpoint, prompt or preprocessing, evaluation entrypoint, and every
protocol difference. Do not call a comparison fair from matching metric names
alone.
