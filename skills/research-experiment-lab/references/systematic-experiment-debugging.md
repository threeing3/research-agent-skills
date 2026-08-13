# Systematic Experiment Debugging

Adapt the root-cause-first discipline from `obra/superpowers`
`systematic-debugging` to scientific experiments.

## Phase 1: Evidence

Read the complete error, run log, events, status, environment, resource trace,
configuration, and recent code/plan changes. Reproduce with the smallest case
or add diagnostics at data, model, loss, optimizer, evaluator, and remote
boundaries. Do not propose a fix before locating the first bad boundary.

Classify the failure:

- infrastructure or SSH;
- environment, driver, or dependency;
- data path, format, split, corruption, or leakage;
- implementation;
- GPU memory, host memory, disk, or throughput;
- numerical instability;
- evaluation or aggregation;
- scientific hypothesis contradicted.

For a new mechanism, split the last category further. Check whether the
program actually implements and activates the intended idea before treating a
negative metric as scientific counter-evidence. Use the activation and
intervention evidence frozen in the validation alignment. If realization is
not confirmed, classify the result as implementation failure; if the test
cannot distinguish the mechanism, classify it as measurement-inconclusive.
Only a faithfully realized, discriminating negative is mechanism
counter-evidence.

## Phase 2: Pattern

Compare a working run, official baseline, prior checkpoint, or smaller
configuration. List every relevant difference. Verify configuration and state
propagation between local snapshot, remote workspace, launcher, trainer, and
evaluator.

## Phase 3: Hypothesis

Write one statement: “X is the root cause because Y evidence.” Test one
variable with the smallest run. If disproved, record it and form a new
hypothesis; do not stack speculative fixes.

## Phase 4: Fix and regression

Create a failing reproduction when possible, fix locally, make a new snapshot
and run ID, then verify the original symptom and relevant regressions.

After three failed fixes for the same symptom, stop and discuss architecture.
Do not relabel a correctly executed negative result as a software failure or
continue tuning until it becomes positive.

The three-fix pause applies to repeated technical fixes for one symptom, not
to the lifetime of an evolving scientific idea. A new scientific validation
still requires new evidence or a material revision and fresh user alignment.

