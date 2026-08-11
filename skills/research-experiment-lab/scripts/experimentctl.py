#!/usr/bin/env python3
"""Initialize experiment campaigns and immutable run records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from experiment_common import append_jsonl, atomic_json, now, read_json, require_id


MODES = {"pilot", "full", "ablation", "robustness", "efficiency", "reproduction", "debug"}


def update_project_index(root: Path, experiment_id: str) -> None:
    index_path = root / "research_state.json"
    if not index_path.exists():
        raise ValueError(f"project-root research_state.json does not exist: {index_path}")
    index = read_json(index_path)
    revision = index.get("revision")
    if not isinstance(revision, int) or revision < 0:
        raise ValueError("research_state.json revision must be a non-negative integer")
    paths = index.setdefault("paths", {})
    if not isinstance(paths, dict):
        raise ValueError("research_state.json paths must be an object")
    paths["experiments"] = "research_state/experiments"
    index["active_experiment_id"] = experiment_id
    index["phase"] = "experimentation"
    index["revision"] = revision + 1
    index["updated_at"] = now()
    atomic_json(index_path, index)


def initialize(args: argparse.Namespace) -> None:
    root = args.project_root.resolve()
    experiment_id = require_id(args.experiment_id, "experiment_id")
    if args.mode not in MODES:
        raise ValueError(f"mode must be one of {sorted(MODES)}")
    experiment_dir = root / "research_state" / "experiments" / experiment_id
    if experiment_dir.exists():
        raise ValueError(f"experiment already exists; do not overwrite it: {experiment_dir}")
    for relative in ("runs", "analysis", "logs"):
        (experiment_dir / relative).mkdir(parents=True, exist_ok=False)
    plan: dict[str, Any] = {
        "schema_version": "research-experiment/plan-v2",
        "experiment_id": experiment_id,
        "plan_revision": 1,
        "mode": args.mode,
        "idea_id": args.idea_id,
        "idea_revision": args.idea_revision,
        "idea_contract_sha256": "",
        "mechanism_family_id": "",
        "mechanism_signature_sha256": "",
        "inherited_failure_ids": [],
        "research_question": args.research_question,
        "hypothesis": "",
        "mechanism_prediction": "",
        "null_explanation": "",
        "datasets": [],
        "splits": [],
        "variants": [],
        "baselines": [],
        "metrics": [],
        "seeds": [],
        "success_thresholds": [],
        "failure_thresholds": [],
        "stop_conditions": [],
        "confounders_and_controls": [],
        "prelaunch": {
            "required_gates": [
                "anti-reskin",
                "mechanism-identifiability",
                "simple-baseline-survival",
                "data-feasibility",
            ],
            "constraints": [],
            "lineage_check_report": "",
            "idea_state_consistency_report": "",
            "last_reconciled_at": None,
        },
        "autonomy": {
            "enabled": False,
            "idea_event_cursor": None,
            "auto_start_next_eligible_task": False,
            "autodl_lifecycle": {
                "authorized": False,
                "profile": None,
                "instance_id": None,
                "allow_start": False,
                "allow_stop": False,
                "allow_no_card_mode": False,
                "allow_data_disk_expand": False,
                "max_data_disk_gb": None,
                "max_data_disk_expand_cost": 0,
                "max_idle_minutes": 30,
                "max_lifecycle_budget": 0,
            },
        },
        "tasks": [],
        "resource_policy": {
            "gpu_required_default": True,
            "tasks_may_override_gpu_required": True,
            "data_disk_safety_margin": 0.15,
            "large_download_direct_remote": True,
        },
        "budget": {
            "gpu_types": [],
            "max_parallel_runs": 1,
            "max_wall_time_hours": 24,
            "max_retry_per_failure": 2,
            "max_debug_runs": 6,
            "checkpoint_download_limit_gb": 5,
        },
        "required_outputs": [],
        "required_runs": [],
        "created_at": now(),
    }
    state = {
        "schema_version": "research-experiment/state-v1",
        "experiment_id": experiment_id,
        "idea_id": args.idea_id,
        "idea_revision": args.idea_revision,
        "plan_revision": 1,
        "stage": "designed",
        "active_runs": [],
        "run_ids": [],
        "budget_consumption": {},
        "verified_evidence": [],
        "blockers": [],
        "task_cursor": None,
        "idea_event_cursor": None,
        "created_at": now(),
        "updated_at": now(),
    }
    atomic_json(experiment_dir / "experiment_plan.json", plan)
    atomic_json(experiment_dir / "experiment_state.json", state)
    update_project_index(root, experiment_id)
    append_jsonl(
        root / "research_state" / "logs" / "research_events.jsonl",
        {
            "timestamp": now(),
            "event": "experiment-created",
            "experiment_id": experiment_id,
            "mode": args.mode,
            "idea_id": args.idea_id,
            "idea_revision": args.idea_revision,
        },
    )
    print(experiment_dir)


def new_run(args: argparse.Namespace) -> None:
    root = args.project_root.resolve()
    experiment_id = require_id(args.experiment_id, "experiment_id")
    run_id = require_id(args.run_id, "run_id")
    experiment_dir = root / "research_state" / "experiments" / experiment_id
    plan = read_json(experiment_dir / "experiment_plan.json")
    state_path = experiment_dir / "experiment_state.json"
    state = read_json(state_path)
    run_dir = experiment_dir / "runs" / run_id
    if run_dir.exists():
        raise ValueError(f"run already exists; run IDs are immutable: {run_dir}")
    records = run_dir / "records"
    records.mkdir(parents=True)
    command = read_json(args.command_json.resolve())
    argv = command.get("argv")
    if not isinstance(argv, list) or not argv or any(not isinstance(item, str) or not item for item in argv):
        raise ValueError("command.json argv must be a non-empty list of non-empty strings")
    atomic_json(records / "command.json", command)
    manifest = {
        "schema_version": "research-experiment/run-manifest-v1",
        "experiment_id": experiment_id,
        "run_id": run_id,
        "parent_run_id": args.parent_run_id,
        "change_reason": args.change_reason,
        "plan_revision": plan.get("plan_revision"),
        "idea_id": plan.get("idea_id"),
        "idea_revision": plan.get("idea_revision"),
        "mode": plan.get("mode"),
        "variant": args.variant,
        "dataset": args.dataset,
        "split": args.split,
        "seed": args.seed,
        "snapshot_id": args.snapshot_id,
        "remote_profile": args.remote_profile,
        "status": "planned",
        "failure_class": None,
        "created_at": now(),
    }
    atomic_json(records / "run_manifest.json", manifest)
    atomic_json(
        records / "sync_manifest.json",
        {
            "schema_version": "research-experiment/sync-manifest-v1",
            "timestamp": now(),
            "direction": "not-applicable" if not args.remote_profile else "local-to-remote",
            "operation": "local-run" if not args.remote_profile else "pending-remote-launch",
            "profile": args.remote_profile,
            "status": "not-applicable" if not args.remote_profile else "pending",
        },
    )
    run_ids = state.setdefault("run_ids", [])
    if not isinstance(run_ids, list):
        raise ValueError("experiment_state.json run_ids must be an array")
    run_ids.append(run_id)
    state["updated_at"] = now()
    atomic_json(state_path, state)
    append_jsonl(
        root / "research_state" / "logs" / "research_events.jsonl",
        {
            "timestamp": now(),
            "event": "run-created",
            "experiment_id": experiment_id,
            "run_id": run_id,
            "variant": args.variant,
            "seed": args.seed,
        },
    )
    print(run_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    init_parser = sub.add_parser("init")
    init_parser.add_argument("project_root", type=Path)
    init_parser.add_argument("--experiment-id", required=True)
    init_parser.add_argument("--mode", required=True)
    init_parser.add_argument("--idea-id")
    init_parser.add_argument("--idea-revision", type=int)
    init_parser.add_argument("--research-question", default="")
    init_parser.set_defaults(func=initialize)

    run_parser = sub.add_parser("new-run")
    run_parser.add_argument("project_root", type=Path)
    run_parser.add_argument("--experiment-id", required=True)
    run_parser.add_argument("--run-id", required=True)
    run_parser.add_argument("--command-json", type=Path, required=True)
    run_parser.add_argument("--variant", required=True)
    run_parser.add_argument("--dataset", required=True)
    run_parser.add_argument("--split", required=True)
    run_parser.add_argument("--seed", type=int, required=True)
    run_parser.add_argument("--snapshot-id", required=True)
    run_parser.add_argument("--remote-profile")
    run_parser.add_argument("--parent-run-id")
    run_parser.add_argument("--change-reason", default="initial run")
    run_parser.set_defaults(func=new_run)

    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"experimentctl failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
