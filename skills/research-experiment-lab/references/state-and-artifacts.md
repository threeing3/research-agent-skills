# State and Artifacts

Store project state as:

```text
research_state/
  experiments/
    experiment_program.json
    <experiment-id>/
      experiment_plan.json
      experiment_state.json
      prelaunch_reconciliation.json
      runs/<run-id>/records/
      analysis/
        run_index.csv
        metric_summary.csv
        failures.csv
      verification_report.json
  logs/research_events.jsonl
```

`experiment_state.json` records `admission_mode`, plan revision, active runs,
stage, budget consumption, blockers, and verified evidence paths.
For `method-validation` it also links the idea ID and revision, mechanism family
ID, mechanism-signature hash, and latest passing prelaunch reconciliation
report. For `diagnostic` it instead links the explicit research question and
frozen diagnostic handoff; idea and contract identity may be null.

For autonomously continuing campaigns, `experiment_plan.json` also contains a
durable `tasks` array. Each task records dependencies, required gates, successor
tasks, retry/download/lifecycle limits, exact commands, and its idea revision
and contract hash. `experiment_state.json` records the task cursor, the last
consumed idea-event cursor, and the last fresh gate verification.

Each run ID is immutable. Any code, configuration, seed, dataset, environment,
resume point, or command change creates a new run ID and records `parent_run_id`
plus `change_reason`.

Detailed artifacts are written before the project-root index is updated. Use
atomic JSON writes and optimistic revision checks. Append state changes to
`research_state/logs/research_events.jsonl`; do not rewrite history.

For method validation, when the idea revision or contract hash changes, mark queued tasks stale and
create a new plan revision/run ID. Never mutate an existing formal run to
follow a new hypothesis.

For diagnostic work, a material change to the observed failure, competing
explanations, separating prediction, intervention boundary, measurement, or
sample-selection rule likewise creates a new plan revision. Verified diagnostic
evidence may update problem state but cannot become `paper-ready` directly.

The experiment skill owns `research_state/experiments/`. It may read but not
rewrite literature, idea, or paper-owned state.
