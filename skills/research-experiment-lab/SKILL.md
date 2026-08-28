---
name: research-experiment-lab
description: Design, execute, debug, revise, verify, and archive complete ML/AI experiment campaigns, from low-cost pilots through paper-ready main results, ablations, robustness, efficiency, reproduction, and failure analysis. Use for local or SSH/AutoDL experiments, remote code and result synchronization, long-run monitoring and recovery, systematic experiment debugging, multi-seed result aggregation, or producing verified evidence for AI research writing, especially VideoQA and long-video understanding.
---

# Research Experiment Lab

Own the experimental lifecycle. Treat every scientific result as a traceable
chain from idea revision to plan, immutable run, raw evidence, verification,
aggregation, and writing handoff.

## Route

Read only the references needed for the task:

| Task | Read first |
|---|---|
| Bottleneck or problem diagnosis | `references/diagnostic-pilots.md`, `references/diagnostic-evidence-handoff.md`, `references/experiment-design.md`, `references/state-and-artifacts.md` |
| New pilot or full campaign | `references/experiment-design.md`, `references/state-and-artifacts.md` |
| Novel-method prelaunch or revised idea | `references/prelaunch-reconciliation.md` plus the new-pilot references |
| AutoDL console, lifecycle, or other SSH execution | `references/autodl-operations.md`, `references/autodl-console-playbook.md`, `references/logging-and-statistics.md` |
| Autonomous multi-step campaign | `references/autonomy-orchestration.md` |
| Failed or anomalous run | `references/systematic-experiment-debugging.md` |
| Verification or paper handoff | `references/verification-gates.md`, `references/writing-handoff.md` |
| VideoQA experiment | the applicable references above plus `references/videoqa-experiments.md` |

## Entry Contract

1. Locate project-root `research_state.json`.
2. Declare `admission_mode` as `diagnostic`, `method-validation`, or
   `reproduction`.
   - `diagnostic` answers where a problem or bottleneck lies. It requires the
     observed failure, competing explanations, separating prediction,
     measurement, outcome meanings, stop condition, and bounded authorization.
     It does not require an idea contract, `experiment-ready` status,
     anti-reskin gate, mechanism family, or mechanism signature. It may use a
     minimal diagnostic intervention, but must not instantiate the full proposed
     method to prove that method's motivation. Read `references/diagnostic-pilots.md`.
   - `method-validation` tests a selected novel method after the problem,
     supported bottleneck, method hypothesis, and distinguishing prediction are
     established. Require a passed `research-idea/v4` anti-reskin gate, an
     `active` lifecycle whose current pool status is `experiment-ready`, a fresh
     passed `research-idea/state-consistency-v2` report, mechanism family ID,
     mechanism-signature hash, and resolved inherited failure ledger.
   - `reproduction` cites an explicit research question and source protocol. It
     makes no novel-method claim unless separately admitted as method validation.
3. Create or update
   `research_state/experiments/<experiment-id>/experiment_plan.json`.
4. Freeze hypothesis, comparisons, datasets, splits, metrics, seeds, success
   and failure thresholds, stop conditions, budget, and confounders before
   observing formal results.
   Declare evidenced minimum prerequisites and verify that they are jointly
   satisfiable. A smaller run that cannot possibly pass the frozen scientific
   gate is not an eligible pilot.
5. For an autonomously continuing campaign, declare a durable task graph in
   `experiment_plan.json.tasks`, including dependencies, gates, successors,
   retry limits, download limits, lifecycle permissions, and exact commands.
   Do not infer future tasks from log text or elapsed time.
6. Create every long run with `scripts/experimentctl.py new-run` before
   launching it. Refuse a long run if its record directory or readable log
   cannot be created.
7. Before the first `method-validation` run and after every idea revision, run
   `scripts/prelaunch_reconcile.py`. Preserve the report and refuse launch when
   lifecycle, idea-state freshness, lineage, identity, inherited-failure,
   constraint, or task-graph checks fail.

Supported modes are `pilot`, `full`, `ablation`, `robustness`, `efficiency`,
`reproduction`, and `debug`. These describe execution shape; `admission_mode`
describes why the experiment is scientifically allowed to run.

## Execute

Keep local code authoritative. Make fixes locally, create a content-addressed
snapshot with `prepare_snapshot.py`, push the immutable snapshot, and launch a
new run ID. Do not edit a formal run in place.

For AutoDL:

1. Keep credentials out of profiles, commands, snapshots, and logs. If the
   user explicitly designates an ignored project-local credential note, read
   it only to answer an attached interactive prompt and never copy or emit it.
2. If SSH is unavailable or the instance is stopped, use the console playbook
   to match the exact instance ID/name, inspect status and capacity, and
   perform only the lifecycle actions authorized in the frozen plan.
3. Classify each queued task as `gpu_required=true/false` before startup. Use
   no-card mode only for explicitly CPU-only tasks; never use it for model
   inference, feature extraction, CUDA checks, or training.
4. If the host reports insufficient free GPUs, preserve the declared instance,
   record the modal, and wait/retry within bounds. Do not clone, switch GPU
   type, or expand budget automatically.
5. Inspect connection, GPU, disk, Python, session manager, and remote roots.
   If the data disk is insufficient, compute peak need and use the authorized
   data-disk expansion flow with a declared capacity/cost ceiling; never
   reformat or delete data.
6. Keep datasets and large weights under declared remote data roots. Prefer
   direct resumable remote downloads for large files; preserve `.part` files,
   logs, manifests, and checksums across network failures, and promote or
   extract only after exact size and SHA-256 verification.
   Before launching any local or remote command, resolve every input path and
   assert that required files exist; record the resolved path in `command.json`
   and emit a structured input-missing event instead of allowing an opaque
   `FileNotFoundError`. After an idea or contract revision, create a fresh
   immutable run ID for verification, extraction, inference, and training.
   Older acquisition runs may supply verified bytes, but their manifests and
   contract hashes must remain historical and must not be reused as the new
   run's identity.
7. Use `autodl_backend.py` for preflight, snapshot upload, launch, status,
   record download, and budget-bounded selected-output download. It performs
   no remote deletion.
8. Run long jobs through the profile-selected `tmux` or `screen` backend and
   `remote_run.py`, so SSH disconnection does not terminate training and
   records remain complete.
9. Poll conditions and status artifacts; do not infer state from elapsed time.
   Use scheduled condition-based heartbeats for long downloads or experiments;
   do not hold an attached terminal listener for the whole duration.

Once the user authorizes an experiment campaign, autonomously run, monitor,
diagnose, make implementation-level fixes, and retry within the frozen plan and
budget. After every fresh gate verification, automatically launch the next
eligible predeclared task instead of stopping at an intermediate milestone.
Pause for hypothesis changes, metric or dataset changes, budget expansion,
destructive actions, credentials, or three failed fixes for the same symptom.
For `method-validation`, before every launch and scheduled check, reconcile the
active idea ID, revision, and contract hash with `research-idea-lab`; a material
idea revision stales queued tasks, preserves prior evidence, and requires a new
plan revision and immutable run IDs rather than an in-place change. Also
reconcile the mechanism family and signature hash. A renamed idea with the same
failed mechanism remains blocked until `research-idea-lab` resolves the family
failure; do not treat it as a fresh campaign. Diagnostic and reproduction work
reconcile their frozen question, inputs, intervention boundary, and measurement
instead of inventing an idea identity.

## Logging Contract

Every run must preserve:

- `run.log`: readable chronological command output and lifecycle summary;
- `events.jsonl`: structured state, warning, recovery, and checkpoint events;
- `metrics.jsonl`: tidy metric observations with step, split, and context;
- `resource_usage.jsonl`: timestamped GPU, memory, and disk observations;
- `command.json`, `run_manifest.json`, `environment.json`;
- `pip_freeze.txt`, `nvidia_smi.txt`, `status.json`, `run_summary.json`;
- `output_manifest.json` with relative paths, sizes, and content hashes;
- `sync_manifest.json` for every uploaded or downloaded artifact set;
- `verification_report.json` before any success claim.

Never overwrite an earlier run. Preserve failed, interrupted, mixed, and
negative results. Read `references/logging-and-statistics.md` for schemas and
instrumentation.

## Debug

Apply `references/systematic-experiment-debugging.md` before changing code:

1. Capture and reproduce the symptom.
2. Classify infrastructure, environment, data, implementation, resource,
   numerical, evaluation, or scientific-hypothesis failure.
3. Trace the first bad boundary and compare with a working case.
4. Record one root-cause hypothesis and run the smallest discriminating test.
5. Implement one fix locally and create a new run.

Do not tune away a negative scientific result. After three failed fixes for
one symptom, stop and request architectural discussion. Do not count renaming,
backbone swaps, optimizer swaps, or adding a training wrapper around the same
target as architectural progress. Return these as an `idea-revision-request`
with the inherited family evidence.

## Verify and Aggregate

Run `verify_run.py` for each run, `aggregate_results.py` for statistics, and
`verify_experiment.py` for declared-run and threshold completeness.
Technical completion is not scientific verification. Require the declared
seeds, fair baselines, stable dataset/split identifiers, recomputable metrics,
uncertainty, mechanism-specific comparisons, and relevant robustness or
efficiency evidence.

Use these stages exactly:

`draft`, `designed`, `preflight-passed`, `code-synced`, `queued`, `running`,
`completed-technical`, `verified-diagnostic`, `verified-scientific`,
`paper-ready`, `blocked`.

`verified-diagnostic` evidence may update the problem or bottleneck record but
cannot be promoted directly to `paper-ready`. Only `paper-ready` evidence with
a v2 verification report and matching method-validation idea contract and
experiment-plan hashes may enter an unblocked shared-state writing handoff.

After a diagnostic experiment reaches `verified-diagnostic`, write
`diagnostic_evidence_handoff.json` from the verified report and inspectable
result artifacts. The handoff states what the evidence supports, weakens, or
leaves inconclusive; its scope and limitations; and a recommended next update.
Do not infer an interpretation from aggregate performance alone, and do not
write the recommendation directly into idea-owned state. Read
`references/diagnostic-evidence-handoff.md`.

## Ownership and Safety

- Own experiment design, execution, debugging, result verification,
  aggregation, experimental evidence, and diagnostic evidence handoffs.
- Let `research-idea-lab` own novelty and idea revisions. Emit an idea revision
  request rather than silently changing the mechanism.
- Let `ai-research-writing-skill` own claims, prose, publication tables, and
  submission. Accept its experiment requests, but independently design runs.
- Never purchase, release, or reimage an AutoDL instance. Data-disk expansion
  is allowed only when explicitly authorized and bounded by the plan; it must
  be verified with `df -h` and must not reformat or delete data. Starting or
  stopping a named instance is allowed only when the user has explicitly
  authorized automatic lifecycle management for that instance/profile and the
  bounded conditions in `references/autonomy-orchestration.md` are satisfied.
  Log every lifecycle action and never expand the budget.
- Never delete local or remote datasets, weights, snapshots, runs, or logs.
- Never claim success without fresh verification output that proves the exact
  claim.
