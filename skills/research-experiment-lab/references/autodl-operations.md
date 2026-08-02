# AutoDL Operations

For console-only actions, read [`autodl-console-playbook.md`](autodl-console-playbook.md)
before interacting with the instance list. It captures exact-ID row matching,
GPU/no-card decisions, data-disk expansion gates, and slow-console fallbacks.

## Profiles

Copy `assets/autodl_profiles.local.json.template` to
`research_state/config/autodl_profiles.local.json`. Keep it out of version
control. Prefer SSH aliases or identity files. Direct host, port, and user
profiles may set `auth` to `interactive-password`; the backend then prompts on
the attached terminal. Never put a password, password-file path, or private-key
contents in a profile, command, synchronization manifest, or log.

When the user explicitly keeps credentials in a project-local `autodl.md`,
ensure the file is ignored by version control and excluded from code snapshots.
The agent may read it and answer an interactive terminal prompt, but
`autodl_backend.py` must not parse, print, copy, upload, or persist its secret.

Profiles may point to fixed or replacement instances. Record the selected
profile plus observed host, GPU, CUDA, Python, disk, and environment in every
run. Instance identity never substitutes for an environment snapshot.

When a profile declares a console-managed instance, also record its exact
console instance ID, region/name, `gpu_required` policy, lifecycle authorization,
and maximum data-disk expansion. The console row is authoritative for current
power/capacity state; the remote preflight remains authoritative for runtime
environment state.

## Remote roots

Allow experiment writes only inside the declared `remote_root`, normally under
`/root/autodl-tmp`. Treat `data_root` and `weights_root` as read-only inputs.
Create immutable paths:

```text
<remote_root>/
  incoming/
  snapshots/<snapshot-id>/
  experiments/<experiment-id>/runs/<run-id>/
```

Do not use mirror deletion, wildcard deletion, or in-place formal-run edits.

## Transfer

Use content-addressed ZIP snapshots for code. Upload the archive and manifest,
then extract to a new snapshot directory. Pull run records automatically.
Download a selected output with `pull-output`, an explicit relative path, and a
mandatory maximum-byte limit. Generate a sync manifest with direction, source,
destination, file sizes, hashes, timestamp, and status.

Keep datasets and large weights on AutoDL. For files above the plan's
transfer threshold, prefer direct resumable download into the remote data root
rather than downloading to the local workstation and uploading again. Every
download must use a versioned `.part` path, readable progress log, declared
source fallback, retry limit, expected byte size, and SHA-256. Preserve partial
files after failure; only a size-and-hash match permits promotion or
extraction. Do not mirror-delete, overwrite, or silently re-download an
existing partial file.

## Field-tested direct-download pattern

On the designated 西北B区/C25机 profile, the practical default for a large
Hugging Face dataset is a remote `wget -c` download into
`incoming/<dataset>/<version>/`, with the original site attempted once and
`hf-mirror.com` declared as the bounded fallback. A connection can create
zero-byte metadata placeholders while a video shard is still progressing; keep
those failed artifacts for diagnosis and retry into a separate
`meta_retry_<source>/` directory. Accept metadata only after its expected
SHA-256 matches, then point verification/extraction at that validated directory.
For a 2x RTX 5090 C25 instance, dataset acquisition and checksum/extraction are
CPU/disk tasks (`gpu_required=false`) but any frozen-model inference, visual
feature extraction, CUDA check, or training remains `gpu_required=true`.
Record the observed `df -h`, free space, part byte growth, source, retry count,
and exact remote command before changing source or lifecycle state.

## Launch and monitoring

If SSH endpoints refuse connection, do not repeatedly retry the same endpoint.
Use the console playbook to determine whether the instance is stopped, GPU
capacity is unavailable, or the control tab is stale. A console modal such as
“required GPUs > free GPUs” is an infrastructure blocker, not an experiment
failure. No-card startup is permitted only for an explicitly CPU-only task.

Before a large download or extraction, compare peak remote usage against the
data disk. If the frozen plan authorizes expansion, record the requested and
actual capacity, verify the mount with `df -h`, and preserve all existing
partial files and manifests.

Run preflight first. Select `session_backend` as `tmux` or `screen` according to
the remote image, then launch with `remote_run.py`. Query
`status.json`, events, log tail, GPU, and disk using condition-based polling.
An absent status file is `not-reported`, not success or failure.

Do not manage instance purchase, release, resize, reimage, or billing. If the
user explicitly authorizes automatic lifecycle management for a named instance
or profile, the orchestrator may start or stop only that instance under the
bounded conditions in `autonomy-orchestration.md`: a predeclared eligible task
must justify a start; a stop requires flushed logs/checkpoints, resumability or
completed work, no protected process, and a recorded reason. Never expand the
budget or replace the instance automatically. Report lifecycle actions and
predicted/actual cost in structured events.
