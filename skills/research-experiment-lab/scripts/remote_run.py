#!/usr/bin/env python3
"""Execute one immutable experiment run with complete durable records."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

from experiment_common import append_jsonl, atomic_json, finite_number, now, read_json, sha256_file


METRIC_PREFIX = "METRIC_JSON:"


def capture(command: list[str], timeout: int = 60) -> tuple[int, str]:
    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode, output
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, f"{type(exc).__name__}: {exc}\n"


def write_environment(records: Path, workspace: Path) -> dict[str, Any]:
    environment = {
        "captured_at": now(),
        "platform": platform.platform(),
        "python": sys.version,
        "python_executable": sys.executable,
        "hostname": platform.node(),
        "workspace": str(workspace),
        "cwd": os.getcwd(),
        "environment_keys": sorted(
            key for key in os.environ
            if not any(token in key.upper() for token in ("TOKEN", "PASSWORD", "SECRET", "KEY"))
        ),
    }
    atomic_json(records / "environment.json", environment)
    pip_code, pip_output = capture([sys.executable, "-m", "pip", "freeze"], timeout=120)
    (records / "pip_freeze.txt").write_text(
        f"# exit_code={pip_code}\n" + (pip_output or "# no packages reported\n"),
        encoding="utf-8",
    )
    nvidia_code, nvidia_output = capture(["nvidia-smi"], timeout=30)
    (records / "nvidia_smi.txt").write_text(
        f"# exit_code={nvidia_code}\n" + (nvidia_output or "# no GPU output reported\n"),
        encoding="utf-8",
    )
    return environment


def host_memory() -> dict[str, int]:
    memory: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            name, raw = line.split(":", 1)
            if name in {"MemTotal", "MemAvailable"}:
                memory[name.lower() + "_bytes"] = int(raw.strip().split()[0]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return memory


def parse_gpus(output: str) -> list[dict[str, Any]]:
    gpus: list[dict[str, Any]] = []
    for line in output.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 7:
            continue
        try:
            gpus.append(
                {
                    "index": int(parts[0]),
                    "name": parts[1],
                    "utilization_gpu_percent": float(parts[2]),
                    "memory_used_mib": float(parts[3]),
                    "memory_total_mib": float(parts[4]),
                    "temperature_c": float(parts[5]),
                    "power_draw_w": float(parts[6]),
                }
            )
        except ValueError:
            continue
    return gpus


def sample_resources(records: Path, stop: threading.Event, interval: int) -> None:
    resource_path = records / "resource_usage.jsonl"
    query = [
        "nvidia-smi",
        "--query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
        "--format=csv,noheader,nounits",
    ]
    while True:
        disk = shutil.disk_usage(records)
        code, output = capture(query, timeout=15)
        row: dict[str, Any] = {
            "timestamp": now(),
            "disk_free_bytes": disk.free,
            "disk_used_bytes": disk.used,
            "nvidia_smi_exit_code": code,
            "gpus": parse_gpus(output) if code == 0 else [],
        }
        row.update(host_memory())
        if code != 0:
            row["gpu_error"] = output.strip()
        append_jsonl(resource_path, row)
        if stop.wait(interval):
            break


def metric_from_line(line: str, manifest: dict[str, Any]) -> Optional[dict[str, Any]]:
    if not line.startswith(METRIC_PREFIX):
        return None
    try:
        value = json.loads(line[len(METRIC_PREFIX):].strip())
    except json.JSONDecodeError:
        return {"_invalid": "metric payload is not JSON"}
    if not isinstance(value, dict) or not isinstance(value.get("name"), str):
        return {"_invalid": "metric payload requires string name"}
    if not finite_number(value.get("value")):
        return {"_invalid": "metric payload requires finite numeric value"}
    return {
        "timestamp": value.get("timestamp") or now(),
        "name": value["name"],
        "value": value["value"],
        "step": value.get("step"),
        "split": value.get("split", manifest.get("split", "")),
        "dataset": value.get("dataset", manifest.get("dataset", "")),
        "variant": value.get("variant", manifest.get("variant", "")),
        "seed": value.get("seed", manifest.get("seed")),
        "context": value.get("context", {}),
    }


def inventory_outputs(outputs: Path, records: Path) -> dict[str, Any]:
    files = []
    for path in sorted(outputs.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        files.append(
            {
                "path": path.relative_to(outputs).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "schema_version": "research-experiment/output-manifest-v1",
        "captured_at": now(),
        "output_root": str(outputs),
        "file_count": len(files),
        "total_bytes": sum(item["size_bytes"] for item in files),
        "files": files,
    }
    atomic_json(records / "output_manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--command-json", type=Path, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    records = run_dir / "records"
    records.mkdir(parents=True, exist_ok=True)
    log_path = records / "run.log"
    events_path = records / "events.jsonl"
    metrics_path = records / "metrics.jsonl"
    status_path = records / "status.json"
    summary_path = records / "run_summary.json"
    start = now()
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    try:
        command = read_json(args.command_json.resolve())
        manifest = read_json(records / "run_manifest.json")
        argv = command.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(item, str) or not item for item in argv):
            raise ValueError("command argv must be a non-empty string array")
        relative_cwd = command.get("cwd", ".")
        if not isinstance(relative_cwd, str):
            raise ValueError("command cwd must be a string")
        workspace = args.workspace.resolve()
        cwd = (workspace / relative_cwd).resolve()
        try:
            cwd.relative_to(workspace)
        except ValueError as exc:
            raise ValueError("command cwd escapes immutable workspace") from exc
        if not cwd.is_dir():
            raise ValueError(f"command cwd does not exist: {cwd}")
        raw_env = command.get("env", {})
        if not isinstance(raw_env, dict) or any(
            not isinstance(key, str) or not isinstance(value, str) for key, value in raw_env.items()
        ):
            raise ValueError("command env must be a string-to-string object")
        interval = command.get("resource_interval_seconds", 30)
        if not isinstance(interval, int) or interval < 1:
            raise ValueError("resource_interval_seconds must be a positive integer")

        environment = write_environment(records, workspace)
        status = {
            "schema_version": "research-experiment/run-status-v1",
            "run_id": manifest.get("run_id"),
            "state": "running",
            "started_at": start,
            "updated_at": start,
            "exit_code": None,
        }
        atomic_json(status_path, status)
        append_jsonl(
            events_path,
            {
                "timestamp": start,
                "event": "run-started",
                "implementation_branch_id": manifest.get("implementation_branch_id"),
                "argv": argv,
            },
        )
        stop = threading.Event()
        monitor = threading.Thread(
            target=sample_resources,
            args=(records, stop, interval),
            daemon=True,
        )
        monitor.start()
        metric_count = 0
        invalid_metric_count = 0
        child_env = os.environ.copy()
        child_env.update(raw_env)
        child_env["RESEARCH_RUN_DIR"] = str(run_dir)
        child_env["RESEARCH_OUTPUT_DIR"] = str(outputs)
        with log_path.open("a", encoding="utf-8", newline="\n", buffering=1) as log:
            log.write(f"[{start}] RUN START\n")
            log.write(f"run_id: {manifest.get('run_id')}\n")
            log.write(f"experiment_id: {manifest.get('experiment_id')}\n")
            log.write(f"plan_revision: {manifest.get('plan_revision')}\n")
            log.write(f"idea_revision: {manifest.get('idea_revision')}\n")
            log.write(
                f"implementation_branch_id: {manifest.get('implementation_branch_id')}\n"
            )
            log.write(f"variant: {manifest.get('variant')}\n")
            log.write(f"dataset: {manifest.get('dataset')}\n")
            log.write(f"split: {manifest.get('split')}\n")
            log.write(f"seed: {manifest.get('seed')}\n")
            log.write(f"snapshot_id: {manifest.get('snapshot_id')}\n")
            log.write(f"workspace: {workspace}\n")
            log.write("argv_json: " + json.dumps(argv, ensure_ascii=False) + "\n")
            log.write(f"python: {environment['python_executable']}\n")
            log.write("--- process output ---\n")
            try:
                process = subprocess.Popen(
                    argv,
                    cwd=cwd,
                    env=child_env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    errors="replace",
                    bufsize=1,
                )
                assert process.stdout is not None
                for line in process.stdout:
                    log.write(line)
                    metric = metric_from_line(line.rstrip("\r\n"), manifest)
                    if metric is not None:
                        if "_invalid" in metric:
                            invalid_metric_count += 1
                            append_jsonl(
                                events_path,
                                {"timestamp": now(), "event": "invalid-metric", "message": metric["_invalid"]},
                            )
                        else:
                            append_jsonl(metrics_path, metric)
                            metric_count += 1
                exit_code = process.wait()
            except OSError as exc:
                log.write(f"\nlauncher error: {type(exc).__name__}: {exc}\n")
                exit_code = 127
            end = now()
            log.write("--- end process output ---\n")
            log.write(f"[{end}] RUN END exit_code={exit_code}\n")
        stop.set()
        monitor.join(timeout=max(5, interval + 2))
        terminal_state = "completed" if exit_code == 0 else "failed"
        append_jsonl(
            events_path,
            {
                "timestamp": end,
                "event": "run-ended",
                "implementation_branch_id": manifest.get("implementation_branch_id"),
                "state": terminal_state,
                "exit_code": exit_code,
                "metric_count": metric_count,
                "invalid_metric_count": invalid_metric_count,
            },
        )
        status.update(
            {
                "state": terminal_state,
                "updated_at": end,
                "ended_at": end,
                "exit_code": exit_code,
            }
        )
        atomic_json(status_path, status)
        output_manifest = inventory_outputs(outputs, records)
        atomic_json(
            summary_path,
            {
                "schema_version": "research-experiment/run-summary-v1",
                "experiment_id": manifest.get("experiment_id"),
                "run_id": manifest.get("run_id"),
                "started_at": start,
                "ended_at": end,
                "exit_code": exit_code,
                "technical_status": terminal_state,
                "metric_count": metric_count,
                "invalid_metric_count": invalid_metric_count,
                "output_file_count": output_manifest["file_count"],
                "output_total_bytes": output_manifest["total_bytes"],
                "records": {
                    "log": "run.log",
                    "events": "events.jsonl",
                    "metrics": "metrics.jsonl",
                    "resources": "resource_usage.jsonl",
                },
            },
        )
        return exit_code
    except (OSError, ValueError) as exc:
        end = now()
        with log_path.open("a", encoding="utf-8", newline="\n") as log:
            log.write(f"[{start}] RUN START\n[{end}] PRELAUNCH FAILURE: {type(exc).__name__}: {exc}\n")
        append_jsonl(
            events_path,
            {"timestamp": end, "event": "run-ended", "state": "invalid", "exit_code": 126, "message": str(exc)},
        )
        atomic_json(
            status_path,
            {
                "schema_version": "research-experiment/run-status-v1",
                "state": "invalid",
                "started_at": start,
                "ended_at": end,
                "updated_at": end,
                "exit_code": 126,
                "error": str(exc),
            },
        )
        output_manifest = inventory_outputs(outputs, records)
        atomic_json(
            summary_path,
            {
                "schema_version": "research-experiment/run-summary-v1",
                "started_at": start,
                "ended_at": end,
                "exit_code": 126,
                "technical_status": "invalid",
                "metric_count": 0,
                "invalid_metric_count": 0,
                "output_file_count": output_manifest["file_count"],
                "output_total_bytes": output_manifest["total_bytes"],
                "error": str(exc),
            },
        )
        print(f"remote_run failed: {exc}", file=sys.stderr)
        return 126


if __name__ == "__main__":
    raise SystemExit(main())
