# Empirical Experiment Design

Load this reference for novel ML, AI, CV, or NLP method papers before result prose is drafted.

This reference defines the evidence the paper needs. When project-root
`research_state/experiments/` exists, `research-experiment-lab` owns experiment
design, execution, debugging, logs, aggregation, and verification. This writing
skill validates the incoming artifacts and emits `experiment_request.json` for
gaps; it must not run or modify experiments.

## Required design artifacts

Create these files under `notes/design/` only when no upstream experiment
system owns them. Otherwise validate or derive them from the verified
experiment package:

- `baselines.csv`: candidate and selected baselines with provenance and selection reasons.
- `method-components.csv`: pipeline components, novelty boundary, interfaces, replacements, and ablation priority.
- `experiment-matrix.csv`: every main, ablation, robustness, efficiency, and failure-analysis experiment mapped to a claim.

Run:

```bash
python3 scripts/validate_design_csvs.py --project-dir <project> --fail-on-issues
```

Do not draft superiority, robustness, efficiency, or significance claims until the supporting matrix rows are `verified`.

## Baseline contract

Select 4-8 final baselines when the field supports them:

1. Direct competitors: 2-4 recent methods addressing the same task and inputs.
2. Foundational methods: 1-2 established anchors.
3. Ablation anchors: 1-2 simplified or degraded variants of the proposed method.

Prefer official implementations. Record the paper, code URL, exact upstream commit, license, evaluation source, datasets, metrics, and whether each number is rerun or paper-reported. Use identical splits, preprocessing, prompts/tokenization, metrics, and evaluation scripts whenever feasible. Document every unavoidable difference.

## Method and ablation contract

Define a minimum viable innovation with explicit inputs, outputs, replaceability, and testable claims. Mark each component's ablation priority:

- `high`: core novelty; must be ablated.
- `medium`: architecture choice; ablate when space and compute permit.
- `low`: hyperparameter choice; include only when scientifically material.

Default to single-factor ablations. Use removal, simpler replacement, or controlled random replacement. Add combination ablations only when an interaction hypothesis is stated in advance. Always include the full method in the same table.

For a baseline modification or mechanism combination, require the upstream
idea artifact to identify the exact baseline version, target failure, add /
replace / remove / rewire / combine operation, insertion location, before and
after information or training flow, reused and redesigned parts, expected
resource delta, and isolating controls. Do not infer these changes from a
method name or final code diff alone.

Before treating a negative result as mechanism evidence, require upstream
activation evidence that the implementation used the intended mechanism and
intervention evidence showing that disabling, shuffling, or replacing it had
the predicted effect. Otherwise describe the result as an implementation or
measurement limitation.

## Experiment matrix

Map every experiment to one or more claim identifiers. Include:

- Main comparisons across the selected datasets and primary community metrics.
- At least four meaningful ablation factors when the method has enough components.
- Robustness or distribution-shift tests when robustness is claimed.
- Parameter count, FLOPs, latency, throughput, memory, or token budget when efficiency is claimed.
- Stratified failure analysis with a defined sampling and annotation protocol.

Each row uses `planned`, `placeholder`, or `verified`. Expected outcomes are hypotheses, never evidence.

## Statistical rigor

Use at least three random seeds for stochastic experiments when feasible and report mean plus standard deviation or confidence intervals. If fewer runs are possible, record the constraint and weaken uncertainty claims. Consider paired tests, Wilcoxon tests, or bootstrap intervals when gains are small or variance is material; state the test, unit of analysis, threshold, and multiplicity handling.

Keep metric direction and decimal precision consistent. Do not bold a best value until the comparison protocol and value provenance are verified.

## Reproducibility and upstream code

Record Python, CUDA, cuDNN, operating system, driver, GPU model/count, dependency versions, seeds, splits, preprocessing, hyperparameter search, optimizer, schedule, batch size, epochs/steps, stopping rule, training time, and evaluation entrypoint.

When extending upstream code:

- Record repository URL, exact commit, and license.
- Keep the change additive when possible.
- Preserve upstream evaluation scripts for fair comparison.
- Create `CHANGES_FROM_UPSTREAM.md`.
- Separate upstream defaults from new configurations.

## Long-experiment logging

Before every long experiment, declare a persistent UTF-8 log path such as `experiments/logs/<experiment-id>/<timestamp>.log`. The log must remain readable without specialized tooling and contain:

1. Experiment ID, claim IDs, purpose, dataset/split, method variant, and baseline.
2. Exact command, configuration path plus resolved configuration, seed, git commit, environment, hardware, and dependency versions.
3. Start time, periodic progress with step/epoch and key metrics, checkpoint paths, warnings, recovery or resume events, and resource failures.
4. End time, exit status, best/final checkpoint, result-file paths, and a short completion summary.

Do not accept a long experiment if its package lacks an immutable run ID,
readable log, events, metrics, resource usage, environment, command, sync
manifest, status, summary, and verification report. Never overwrite an earlier
run log. Treat a missing, unreadable, or unverified record as a reproducibility
blocker and issue an experiment request rather than repairing the run here.

## VideoQA extension

For video question answering and long-video understanding, consider length-stratified performance, temporal localization or evidence-frame quality, context/token budgets, distractor resistance, memory ablations, question-type breakdowns, cross-dataset transfer, latency, peak memory, and qualitative failure categories. Bind each included analysis to a paper claim; do not add decorative experiments.
