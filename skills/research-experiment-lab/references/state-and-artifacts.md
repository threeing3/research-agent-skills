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
      validation_alignment_check.json
      runs/<run-id>/records/
      analysis/
        run_index.csv
        metric_summary.csv
        failures.csv
      verification_report.json
  logs/research_events.jsonl
```

`experiment_state.json` links the idea ID and revision, plan revision, active
runs, stage, budget consumption, blockers, and verified evidence paths.
For novel-method work it also links the mechanism family ID,
mechanism-signature hash, and latest passing prelaunch reconciliation report.

For `exploratory-validation`, it instead links the implementation revision,
validation-alignment path and SHA-256, and latest passing alignment check. The
idea contract hash remains empty because the idea has not been formally
promoted.

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

When the idea revision or contract hash changes, mark queued tasks stale and
create a new plan revision/run ID. Never mutate an existing formal run to
follow a new hypothesis.

The experiment skill owns `research_state/experiments/`. It may read but not
rewrite literature, idea, or paper-owned state.
