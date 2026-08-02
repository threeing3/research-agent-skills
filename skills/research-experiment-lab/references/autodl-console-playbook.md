# AutoDL Console Playbook

Use this playbook when SSH（安全终端连接） is unavailable, the instance is
stopped, the console must be used to start it, or the data disk needs a safe
capacity change. The console is a control surface, not an experiment result
source: every action must still be reflected in the experiment state and
structured events.

## Contents

- [1. Find the intended instance](#1-find-the-intended-instance)
- [2. Start and verify](#2-start-and-verify)
- [3. Decide whether GPU is required](#3-decide-whether-gpu-is-required)
- [4. Handle insufficient GPU capacity](#4-handle-insufficient-gpu-capacity)
- [5. Expand the data disk](#5-expand-the-data-disk)
- [6. Keep browser control fast](#6-keep-browser-control-fast)
- [7. Record the action](#7-record-the-action)

## 1. Find the intended instance

1. Open the AutoDL container-instance list and read one fresh page snapshot.
2. Match the exact declared instance ID first, then region and user-visible
   machine name. For example, `xzb715mwbw-9d69a00c` plus `西北B区/C25机` is a
   stronger identity than a row position or GPU type alone.
3. Read the row's status, GPU count/type, system/data disk usage, health,
   billing warning, and release deadline before any action.
4. Do not use a guessed row index when multiple pages or virtualized tables are
   present. If the table is horizontally clipped, scroll the table once to
   expose the operation column and keep the exact ID as the row anchor.
5. If the ID is absent or two rows match, stop and record an ambiguous-instance
   blocker; never start a neighboring instance by accident.

## 2. Start and verify

For a predeclared task with lifecycle authorization:

1. Write an `instance-start-requested` event before pressing 开机, including
   experiment/task ID, instance ID, profile, GPU requirement, expected
   duration, cost ceiling, and reason.
2. Press the operation control in the matched row. Treat a modal as a state
   report, not as a success signal. Read its exact text.
3. After the action, refresh or perform one targeted row check. Accept
   `运行中` only after the console reports it; then connect through the fresh
   SSH/Jupyter/terminal endpoint shown for that running instance.
4. Run the remote preflight (`nvidia-smi`, `df -h`, Python/CUDA import checks,
   and session-manager check) before uploading code or starting a run.
5. Emit `instance-started` only after the running state and preflight agree.
   If startup is rejected, emit `campaign-blocked` or a bounded recovery event
   with the modal text and do not claim that a process launched.

## 3. Decide whether GPU is required

Classify the queued task before opening the instance:

| Task | `gpu_required` | Allowed action |
|---|---:|---|
| Model inference, feature extraction, training, CUDA smoke test | true | Require the declared GPU; do not use no-card mode. |
| Dataset download, checksum, archive inspection, text preprocessing, code packaging | false | No-card mode may be used if the environment and disk are sufficient. |
| Mixed task with a later GPU phase | true for the campaign | Split into explicit CPU and GPU tasks; never hide the GPU dependency. |

No-card mode is a CPU-only continuation, not a cheaper GPU substitute. It is
allowed only when the current task is explicitly `gpu_required=false` and the
plan records that no CUDA result will be produced. Before a later GPU task,
stop or keep the instance according to its task graph and acquire GPU capacity
again.

## 4. Handle insufficient GPU capacity

The console can report that the host has fewer free GPUs than the instance
requires (for example, `需求量 2 卡 / 空闲 0 卡`). Apply this order:

1. If the task is GPU-required, preserve the instance choice and wait or use a
   condition-based retry. Do not select 克隆实例, a different machine, or a
   larger budget unless the user explicitly changes the plan.
2. If the queued task is CPU-only, no-card mode is eligible only after the
   task classification and remote CPU/disk preflight pass. Record the mode in
   the run manifest and metrics context.
3. If a modal offers no-card mode but the task will import CUDA, load a GPU
   model, or run a GPU metric, decline it and mark the task blocked.
4. Retry only on the plan's bounded schedule. Record the first modal text,
   retry count, and next check time; do not click repeatedly while the console
   is slow.

## 5. Expand the data disk

Capacity expansion is a lifecycle mutation and needs explicit authorization
and a plan ceiling. It is not a reason to delete files or reformat a disk.

1. Estimate peak need as existing usage + `.part` download + unpacked data +
   temporary extraction/cache space + at least 15% safety margin. Keep source
   archives and immutable manifests in the estimate.
2. Compare this estimate with `df -h`/`du` from the remote data root and the
   console's data-disk capacity. If the data disk is insufficient and the plan
   allows expansion, choose only the data-disk expansion control for the
   declared instance. Never expand the system disk by guesswork.
3. Before confirming, record current capacity, target capacity, predicted
   cost, task ID, and reason in `instance-disk-expand-requested`. Do not expand
   when the target size or cost is not visible.
4. After the console reports success, reconnect and verify the mount and free
   bytes with `df -h`, then append `instance-disk-expanded`. Keep all paths
   unchanged; expansion must not trigger extraction or a new download by
   itself.
5. If expansion is unavailable, ambiguous, or would exceed the plan ceiling,
   preserve partial files and mark the task blocked rather than deleting data.

## 6. Keep browser control fast

- Reuse one selected browser and one tab; do not open duplicate AutoDL tabs.
- Take one DOM snapshot to locate the row, then use a targeted row/button
  check. Use a screenshot only when the table is clipped or a modal is visual.
- Reuse the latest snapshot after each action. Do not loop over all rows or
  repeatedly call full-page snapshots.
- A wide table may require one horizontal scroll before the operation column is
  visible. Use the exact instance ID as the anchor, not the vertical position.
- If a browser action takes unusually long, check the current row/modal once,
  then fall back to the fresh SSH/Jupyter endpoint or a scheduled retry. Do
  not issue parallel clicks or reload a page containing an in-progress action.
- A stale/empty user-tab list does not prove the instance is unavailable. Use a
  fresh console tab only after the current controlled tab is known stale.
- Keep the console tab as a handoff only when a user must continue the action;
  otherwise finalize it without multiplying tabs.

## 7. Record the action

Every console action must include timestamp, experiment ID, task/run ID, plan
revision, profile, instance ID, pre-action state, action, result/modal text,
capacity or cost observation, and artifact/log paths. Required event names are
`instance-start-requested`, `instance-started`, `instance-start-rejected`,
`instance-disk-expand-requested`, `instance-disk-expanded`, and
`campaign-blocked` where applicable. Console state never replaces
`status.json`, `run.log`, `resource_usage.jsonl`, or a fresh remote preflight.
