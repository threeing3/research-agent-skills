# Verification Gates

Use fresh evidence for every completion claim.

For novel-method work, first require a passing prelaunch reconciliation tied
to the exact idea-contract hash, mechanism family, mechanism-signature hash,
and experiment-plan revision. A later rename or idea revision never repairs a
failed gate retroactively.

For autonomously continuing campaigns, the proving evidence must also show that
the task graph, idea revision, dataset/split identity, and lifecycle permission
were current at launch. A successor may start only after the predecessor's
declared gate has been freshly verified.

## Run gate

Require a completed status, exit code, nonempty readable log, start and end
events, command and environment snapshots, no unresolved fatal warning, and
all declared output paths. Require finite metrics when metrics are expected.

## Experiment gate

Require all mandatory variants and seeds, stable dataset and split IDs,
consistent evaluator version, fair baseline protocol, declared uncertainty,
documented exclusions, and mechanism-specific tests. Recompute reported
aggregates from run-level records.

Declare mandatory combinations in `experiment_plan.json.required_runs`. Use
structured success thresholds with `metric`, `variant`, `dataset`, `split`,
`op`, and `value` when a mean threshold can be evaluated automatically.

## Paper-ready gate

Require run verification reports, experiment aggregation, experiment
inventory, numeric evidence with selectors, negative and contradictory runs,
limitations, and no blocking novelty or experiment request.

Before saying “passed,” identify the proving command, run it fresh, read full
output and exit code, and make only the claim supported by that output.
