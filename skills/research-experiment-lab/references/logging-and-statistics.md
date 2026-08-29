# Logging and Statistics

## Required records

Every long run writes both human-readable and machine-readable records.

Autonomous campaigns must also log task-graph transitions, idea-revision
checks, download byte progress and retry state, and AutoDL lifecycle requests
in `events.jsonl` and the project research event log. A lifecycle event includes
the instance identity, reason, plan revision, predicted/actual budget impact,
and protected artifact paths. A download event includes source, target,
expected size, current size, modification time, checksum status, and retry
count.

`run.log` contains the run purpose, idea and plan revisions, exact command,
resolved configuration paths, dataset and split, variant, seed, environment,
hardware, start/end times, periodic progress, warnings, checkpoints, resume or
recovery events, output paths, exit status, and final summary.

For method validation, `run_manifest.json`, `run.log`, recovery events,
`run_index.csv`, and `failures.csv` also carry the frozen
`implementation_branch_id`. A change in the surface symptom does not change
that ID.

`events.jsonl` uses one JSON object per line:

```json
{"timestamp":"RFC3339","event":"checkpoint","step":1000,"path":"...","message":"saved"}
```

`metrics.jsonl` uses tidy observations:

```json
{"timestamp":"RFC3339","name":"accuracy","value":0.812,"step":1000,"split":"val","dataset":"NExT-QA","variant":"ours","seed":42}
```

`resource_usage.jsonl` records GPU utilization, used/total GPU memory, host
memory when available, and free disk. Keep units explicit in field names.

Write formal outputs under the `RESEARCH_OUTPUT_DIR` environment path supplied
to every run. `output_manifest.json` records every output file's relative path,
size, and SHA-256 hash. Large checkpoints may remain remote; download only
selected outputs within the declared byte budget.

Training programs may emit a line beginning with `METRIC_JSON:` followed by a
JSON object. `remote_run.py` copies valid observations into `metrics.jsonl`
while preserving the original line in `run.log`.

## Statistical outputs

Run `aggregate_results.py` after records are local. It produces:

- `run_index.csv`: one row per run, including status, environment, duration,
  variant, dataset, split, seed, snapshot, and failure class;
- `metric_summary.csv`: count, mean, sample standard deviation, minimum, and
  maximum grouped by experiment, variant, dataset, split, and metric;
- `failures.csv`: failed or invalid runs with class, symptom, root-cause
  hypothesis, fix, and parent run.
- `resource_summary.csv`: per-run duration, resource sample counts, mean GPU
  utilization, peak GPU memory, temperature and power maxima, and minimum disk
  and host-memory availability.

Do not average incomparable metrics, datasets, splits, or protocol revisions.
Do not silently drop failed seeds. Record exclusions with reasons.

## Completion

A process exit code of zero proves only technical termination. Before
scientific completion, verify required files, nonempty logs, terminal events,
finite metrics, declared seeds, dataset/split identity, baseline protocol,
uncertainty, and plan thresholds.
