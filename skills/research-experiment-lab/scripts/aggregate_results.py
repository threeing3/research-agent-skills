#!/usr/bin/env python3
"""Aggregate immutable run records into analysis-ready CSV files."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from experiment_common import finite_number, load_jsonl, read_json


RUN_FIELDS = (
    "experiment_id", "run_id", "parent_run_id", "plan_revision", "idea_id",
    "idea_revision", "mode", "variant", "dataset", "split", "seed",
    "snapshot_id", "remote_profile", "status", "exit_code", "started_at",
    "ended_at", "duration_seconds", "metric_count", "output_file_count",
    "output_total_bytes", "failure_class", "change_reason",
)
SUMMARY_FIELDS = (
    "experiment_id", "plan_revision", "variant", "dataset", "split", "metric",
    "n", "mean", "sample_std", "min", "max", "seeds", "run_ids",
)
FAILURE_FIELDS = (
    "experiment_id", "run_id", "parent_run_id", "variant", "dataset", "seed",
    "technical_status", "exit_code", "failure_class", "symptom",
    "root_cause_hypothesis", "fix", "change_reason",
)
RESOURCE_FIELDS = (
    "experiment_id", "run_id", "variant", "dataset", "seed", "sample_count",
    "gpu_sample_count", "mean_gpu_utilization_percent", "max_gpu_memory_used_mib",
    "max_gpu_memory_total_mib", "max_temperature_c", "max_power_draw_w",
    "min_disk_free_bytes", "min_host_memory_available_bytes",
)


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def duration_seconds(started: Any, ended: Any) -> Any:
    if not isinstance(started, str) or not isinstance(ended, str):
        return ""
    try:
        return (datetime.fromisoformat(ended) - datetime.fromisoformat(started)).total_seconds()
    except ValueError:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment_dir", type=Path)
    args = parser.parse_args()
    experiment_dir = args.experiment_dir.resolve()
    try:
        plan = read_json(experiment_dir / "experiment_plan.json")
        run_rows: list[dict[str, Any]] = []
        failure_rows: list[dict[str, Any]] = []
        resource_rows: list[dict[str, Any]] = []
        groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)

        for run_dir in sorted((experiment_dir / "runs").iterdir()):
            records = run_dir / "records"
            if not records.is_dir():
                continue
            manifest = read_json(records / "run_manifest.json")
            status = read_json(records / "status.json") if (records / "status.json").is_file() else {}
            summary = read_json(records / "run_summary.json") if (records / "run_summary.json").is_file() else {}
            row = dict(manifest)
            row.update(
                {
                    "status": status.get("state", manifest.get("status")),
                    "exit_code": status.get("exit_code"),
                    "started_at": status.get("started_at"),
                    "ended_at": status.get("ended_at"),
                    "duration_seconds": duration_seconds(status.get("started_at"), status.get("ended_at")),
                    "metric_count": summary.get("metric_count", 0),
                    "output_file_count": summary.get("output_file_count", 0),
                    "output_total_bytes": summary.get("output_total_bytes", 0),
                    "failure_class": manifest.get("failure_class") or summary.get("failure_class"),
                }
            )
            run_rows.append(row)
            if row["status"] not in {"completed"} or row["exit_code"] != 0:
                failure_rows.append(
                    {
                        **row,
                        "technical_status": row["status"],
                        "symptom": summary.get("symptom", ""),
                        "root_cause_hypothesis": summary.get("root_cause_hypothesis", ""),
                        "fix": summary.get("fix", ""),
                    }
                )
            resource_path = records / "resource_usage.jsonl"
            samples = load_jsonl(resource_path) if resource_path.is_file() else []
            gpu_rows = [
                gpu
                for sample in samples
                for gpu in (sample.get("gpus") if isinstance(sample.get("gpus"), list) else [])
                if isinstance(gpu, dict)
            ]
            utilizations = [
                float(gpu["utilization_gpu_percent"])
                for gpu in gpu_rows if finite_number(gpu.get("utilization_gpu_percent"))
            ]
            memories = [
                float(gpu["memory_used_mib"])
                for gpu in gpu_rows if finite_number(gpu.get("memory_used_mib"))
            ]
            totals = [
                float(gpu["memory_total_mib"])
                for gpu in gpu_rows if finite_number(gpu.get("memory_total_mib"))
            ]
            temperatures = [
                float(gpu["temperature_c"])
                for gpu in gpu_rows if finite_number(gpu.get("temperature_c"))
            ]
            powers = [
                float(gpu["power_draw_w"])
                for gpu in gpu_rows if finite_number(gpu.get("power_draw_w"))
            ]
            disks = [
                int(sample["disk_free_bytes"])
                for sample in samples if finite_number(sample.get("disk_free_bytes"))
            ]
            host_memory = [
                int(sample["memavailable_bytes"])
                for sample in samples if finite_number(sample.get("memavailable_bytes"))
            ]
            resource_rows.append(
                {
                    "experiment_id": manifest.get("experiment_id"),
                    "run_id": manifest.get("run_id"),
                    "variant": manifest.get("variant"),
                    "dataset": manifest.get("dataset"),
                    "seed": manifest.get("seed"),
                    "sample_count": len(samples),
                    "gpu_sample_count": len(gpu_rows),
                    "mean_gpu_utilization_percent": statistics.fmean(utilizations) if utilizations else "",
                    "max_gpu_memory_used_mib": max(memories) if memories else "",
                    "max_gpu_memory_total_mib": max(totals) if totals else "",
                    "max_temperature_c": max(temperatures) if temperatures else "",
                    "max_power_draw_w": max(powers) if powers else "",
                    "min_disk_free_bytes": min(disks) if disks else "",
                    "min_host_memory_available_bytes": min(host_memory) if host_memory else "",
                }
            )
            metrics_path = records / "metrics.jsonl"
            if metrics_path.is_file():
                for metric in load_jsonl(metrics_path):
                    if not isinstance(metric.get("name"), str) or not finite_number(metric.get("value")):
                        raise ValueError(f"non-finite or unnamed metric in {metrics_path}")
                    key = (
                        manifest.get("experiment_id"),
                        manifest.get("plan_revision"),
                        metric.get("variant", manifest.get("variant")),
                        metric.get("dataset", manifest.get("dataset")),
                        metric.get("split", manifest.get("split")),
                        metric["name"],
                    )
                    groups[key].append(
                        {
                            "value": float(metric["value"]),
                            "seed": metric.get("seed", manifest.get("seed")),
                            "run_id": manifest.get("run_id"),
                        }
                    )

        metric_rows: list[dict[str, Any]] = []
        for key, observations in sorted(groups.items(), key=lambda item: tuple(str(value) for value in item[0])):
            values = [row["value"] for row in observations]
            seeds = sorted({str(row["seed"]) for row in observations})
            run_ids = sorted({str(row["run_id"]) for row in observations})
            metric_rows.append(
                {
                    "experiment_id": key[0],
                    "plan_revision": key[1],
                    "variant": key[2],
                    "dataset": key[3],
                    "split": key[4],
                    "metric": key[5],
                    "n": len(values),
                    "mean": statistics.fmean(values),
                    "sample_std": statistics.stdev(values) if len(values) > 1 else "",
                    "min": min(values),
                    "max": max(values),
                    "seeds": ";".join(seeds),
                    "run_ids": ";".join(run_ids),
                }
            )

        analysis = experiment_dir / "analysis"
        write_csv(analysis / "run_index.csv", RUN_FIELDS, run_rows)
        write_csv(analysis / "metric_summary.csv", SUMMARY_FIELDS, metric_rows)
        write_csv(analysis / "failures.csv", FAILURE_FIELDS, failure_rows)
        write_csv(analysis / "resource_summary.csv", RESOURCE_FIELDS, resource_rows)
        output = {
            "experiment_id": plan.get("experiment_id"),
            "runs": len(run_rows),
            "metric_groups": len(metric_rows),
            "failures": len(failure_rows),
            "resource_rows": len(resource_rows),
            "outputs": [
                str(analysis / "run_index.csv"),
                str(analysis / "metric_summary.csv"),
                str(analysis / "failures.csv"),
                str(analysis / "resource_summary.csv"),
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"aggregate_results failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
