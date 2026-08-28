# Verification Gates

Use fresh evidence for every completion claim.

For `method-validation`, first require a passing prelaunch reconciliation tied
to an active idea lifecycle, a fresh idea-state consistency report, the exact
idea-contract hash, mechanism family, mechanism-signature hash, and
experiment-plan revision. A later rename or idea revision never repairs a
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

For `diagnostic` admission, require the frozen competing explanations,
separating prediction, measurement, intervention boundary, outcome meanings,
scope estimate, and stop condition. A passed diagnostic receives
`verified-diagnostic`; it updates problem evidence but cannot be promoted
directly to `paper-ready`.

Declare mandatory combinations in `experiment_plan.json.required_runs`. Use
structured success thresholds with `metric`, `variant`, `dataset`, `split`,
`op`, and `value` when a mean threshold can be evaluated automatically.

## Paper-ready gate

Require run verification reports, experiment aggregation, experiment
inventory, numeric evidence with selectors, negative and contradictory runs,
limitations, and no blocking novelty or experiment request.

Before saying “passed,” identify the proving command, run it fresh, read full
output and exit code, and make only the claim supported by that output.
`verify_experiment.py` must emit
`research-experiment/experiment-verification-v2`, including experiment and
idea IDs, both revisions, the idea-contract SHA-256, experiment-plan SHA-256,
resulting stage, failed-check blockers, and structured checks. Shared-state
writing accepts only a passed report whose stage is `paper-ready` and whose
identity chain matches current canonical files.
