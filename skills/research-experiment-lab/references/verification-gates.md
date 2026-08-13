# Verification Gates

Use fresh evidence for every completion claim.

For novel-method work, first require a passing prelaunch reconciliation tied
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

Declare mandatory combinations in `experiment_plan.json.required_runs`. Use
structured success thresholds with `metric`, `variant`, `dataset`, `split`,
`op`, and `value` when a mean threshold can be evaluated automatically.

## Paper-ready gate

Require non-empty, verified mechanism, quantitative, and qualitative evidence
obligations. Every declared artifact must exist, be readable, and correspond to the
frozen method and idea revision. Qualitative evidence must state its selection
protocol and include failures or counterexamples; a success-only gallery does not
pass.

Require a v3 plan with explicit `admission_mode: formal`. A legacy v2 plan is
read-only and cannot be promoted in place. An `exploratory-validation` plan may pass a
diagnostic verification and reach `verified-diagnostic`, but it must fail any
request to promote it to `paper-ready`.

Require run verification reports, experiment aggregation, experiment
inventory, numeric evidence with selectors, negative and contradictory runs,
limitations, and no blocking novelty or experiment request.

Before saying “passed,” identify the proving command, run it fresh, read full
output and exit code, and make only the claim supported by that output.
`verify_experiment.py` must emit
`research-experiment/experiment-verification-v3`, including experiment and
idea IDs, both revisions, method identity, and formal admission mode. Legacy
idea-contract or experiment-plan hashes may be checked when present,
resulting stage, failed-check blockers, and structured checks. Shared-state
writing accepts only a passed report whose stage is `paper-ready` and whose
identity chain matches current canonical files.
