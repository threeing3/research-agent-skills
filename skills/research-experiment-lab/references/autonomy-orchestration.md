# Autonomous Experiment Orchestration

Use this protocol whenever the user authorizes a campaign to continue without
turn-by-turn confirmation. Autonomy is bounded by the frozen experiment plan,
the declared budget ceiling, the selected AutoDL profile, and the idea revision
currently owned by `research-idea-lab`.

## Campaign task graph

Every campaign must declare a durable task graph in
`experiment_plan.json.tasks`. Each task has:

- `task_id`, `kind`, `run_id` or artifact target;
- `depends_on` and `required_gates`;
- `on_success`, `on_failure`, and `on_blocked` transitions;
- resource, wall-time, retry, and download budgets;
- whether it may start automatically after fresh verification;
- the exact command, snapshot, dataset/split, seed, and output paths.

Typical task kinds are `preflight`, `download`, `verify-download`, `extract`,
`environment`, `smoke`, `formal-run`, `aggregate`, `robustness`, and
`paper-handoff`. A task graph must never infer a new scientific task from an
elapsed time or an informal log message.

## Automatic next-step rule

After every condition-based check:

1. Read the current `research_state.json`, experiment state, plan revision,
   idea ID, idea revision, mechanism family, and mechanism-signature hash.
   Read the latest prelaunch reconciliation report and require it to match the
   current plan and idea contract.
2. Verify the active task with fresh artifacts and the proving command for its
   gate.
3. If the task is technically and scientifically allowed to advance, select
   the next predeclared task whose dependencies and budget gates are satisfied.
4. Create its immutable run or artifact record before launching it, append a
   `task-transition` event, and launch it through the configured backend.
5. If no task is eligible, record `no-eligible-task` once and stop polling until
   the next scheduled check.

Before step 3, reject any graph whose prerequisites are unsatisfied or cyclic.
Classify the block using `references/prelaunch-reconciliation.md`; do not keep
polling an external system for a contradiction that only a plan revision or
user authorization can resolve.

Never stop merely because a pilot, seed, or gate passed when the task graph has
an eligible successor. Never invent a successor, change a hypothesis, or
silently enlarge a run because a task failed.

## Idea-revision synchronization

Before launching every task and at every scheduled check, compare the plan's
`idea_id`, `idea_revision`, and `idea_contract_sha256` with the canonical idea
state. Consume new `research_events.jsonl` entries from the last cursor.

- A non-material idea note may be recorded and acknowledged automatically.
- A material revision to the hypothesis, mechanism, primary dataset, split,
  metric, threshold, or contribution claim immediately marks queued tasks
  `stale-by-idea-revision`.
- Preserve old plans and completed runs. Create a new plan revision and new
  run IDs after the idea skill approves the handoff.
- Do not continue a queued formal run against a stale hypothesis. Emit an
  `idea-revision-request` event with the affected tasks, evidence paths, and
  the last safe checkpoint.

## Large-data acquisition

Prefer direct AutoDL download for datasets and weights above the plan's
declared transfer threshold. Before starting, verify the remote data root,
free disk, expected unpacked size, checksum, source license, and resumability.

Use versioned paths such as:

```text
<remote_root>/incoming/<dataset>/<version>/<file>.part
<remote_root>/incoming/<dataset>/<version>/<file>
<remote_root>/data/raw/<dataset>/<version>/
<remote_root>/preflight/<dataset>/<version>.manifest.tsv
<remote_root>/logs/system/downloads/<dataset>_<version>.log
```

The protocol is:

1. Download to `.part` with a resumable command and a readable log.
2. Preserve partial files on every interruption; never restart from zero by
   default and never delete a partial file automatically.
3. Record byte count, modification time, transfer rate, source, retry count,
   and failure class in `events.jsonl`.
4. Treat a stalled byte count, repeated connection errors, checksum mismatch,
   disk pressure, or an unavailable source as a recoverable download failure.
5. Pause the downloader, retain the partial file and log, switch only to a
   predeclared alternate source, and retry no more than the plan allows.
6. Accept the download only after both exact byte size and SHA-256 match.
7. Extract into a new versioned target only after acceptance; keep the source
   archive and manifest. Never promote an unchecked archive.

For very large files, the orchestrator may use a local checkpoint heartbeat
instead of a continuous terminal listener. The heartbeat checks process state,
size/mtime, log tail, disk, budget, and last byte growth, then exits.

## AutoDL lifecycle authorization

If the user has explicitly authorized automatic lifecycle management for a
named instance/profile, the campaign may start or stop that declared instance
only under these conditions:

### Start

- a predeclared task is queued and its dependencies are verified;
- the selected instance, GPU type, image, data root, and budget ceiling match
  the plan;
- preflight predicts enough disk, GPU memory, time, and remaining budget;
- the start command, reason, predicted duration/cost, and instance identity are
  written before the action.

### Stop

- no protected process is running, or the active task is explicitly resumable;
- all required checkpoints, partial downloads, logs, and manifests are flushed;
- selected records are synchronized or their remote paths are recorded;
- the stop reason is budget exhaustion, scheduled idle window, recoverable
  infrastructure failure, or a completed task graph;
- the action does not delete, release, reimage, resize, or change the budget.

Never stop an instance merely because a check found low utilization while a
declared task is still making progress. Never start a replacement instance,
change GPU type, expand budget, or release data without a separate explicit
authorization. If lifecycle state is ambiguous, report and pause.

### Console decision rules

When using the AutoDL web console, follow
`references/autodl-console-playbook.md`: identify the exact instance ID/name,
read the current row and modal, and verify the remote state after the action.
Treat a host-capacity rejection (`required GPUs > free GPUs`) as a bounded
infrastructure blocker. A queued CPU-only task may use no-card mode; a task
that imports CUDA, decodes model features, performs inference, or trains may
not.

Data-disk expansion is allowed only when the user has authorized it and the
plan declares a maximum target capacity and cost ceiling. It must be preceded
by a peak-space calculation and followed by `df -h` verification. Expansion
does not permit changing remote roots, reformatting, deleting data, or
implicitly downloading/extracting anything.

Slow console operations require targeted checks and bounded retries rather than
parallel clicks, duplicate tabs, or repeated full-page snapshots.

## Monitoring and recovery

Long tasks use condition-based monitoring rather than an attached long-lived
terminal session. A scheduled check must inspect:

- PID/session and exit code;
- `status.json`, `run.log` tail, and recent structured events;
- output counts, file sizes, modification times, and checksums where declared;
- GPU, host memory, disk, and budget;
- idea revision and task-graph eligibility.

Recovery is bounded:

- resume the same immutable run only when the plan explicitly permits resume;
- otherwise create a child run with `parent_run_id` and `change_reason`;
- apply one root-cause fix at a time;
- after three failed fixes for the same symptom, mark the task blocked and
  request architectural review;
- never convert a verified negative scientific result into an infrastructure
  failure merely to keep the graph moving.

## Required orchestration events

Append at least these events when applicable:

`task-created`, `task-transition`, `idea-revision-seen`,
`task-stale-by-idea-revision`, `instance-start-requested`,
`instance-started`, `instance-start-rejected`, `instance-stop-requested`,
`instance-stopped`, `instance-disk-expand-requested`,
`instance-disk-expanded`,
`download-progress`, `download-stalled`, `download-resumed`,
`download-accepted`, `download-retry-exhausted`, `task-recovery`,
`prelaunch-reconciled`, `prelaunch-blocked`, `family-failure-inherited`,
`no-eligible-task`, and `campaign-blocked`.

Every lifecycle or recovery event must include timestamp, experiment ID,
task/run ID, plan revision, instance identity if applicable, reason, and
artifact/log paths.
