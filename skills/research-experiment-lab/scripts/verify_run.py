#!/usr/bin/env python3
"""Verify one run from fresh durable evidence before completion claims."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from experiment_common import atomic_json, finite_number, load_jsonl, now, read_json


REQUIRED_FILES = (
    "run_manifest.json",
    "command.json",
    "sync_manifest.json",
    "environment.json",
    "pip_freeze.txt",
    "nvidia_smi.txt",
    "run.log",
    "events.jsonl",
    "resource_usage.jsonl",
    "status.json",
    "run_summary.json",
    "output_manifest.json",
)


def check(name: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"name": name, "passed": passed, "evidence": evidence}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--require-metrics", action="store_true")
    args = parser.parse_args()
    records = args.run_dir.resolve()
    if (records / "records").is_dir():
        records = records / "records"
    checks: list[dict[str, Any]] = []
    try:
        for name in REQUIRED_FILES:
            path = records / name
            checks.append(check(f"required:{name}", path.is_file() and path.stat().st_size > 0, str(path)))

        status = read_json(records / "status.json")
        summary = read_json(records / "run_summary.json")
        events = load_jsonl(records / "events.jsonl")
        checks.append(check("terminal-status", status.get("state") == "completed", str(status.get("state"))))
        checks.append(check("zero-exit-code", status.get("exit_code") == 0, str(status.get("exit_code"))))
        checks.append(
            check(
                "summary-agrees",
                summary.get("exit_code") == status.get("exit_code")
                and summary.get("technical_status") == status.get("state"),
                f"summary={summary.get('technical_status')}/{summary.get('exit_code')}",
            )
        )
        event_names = [row.get("event") for row in events]
        checks.append(check("start-event", "run-started" in event_names, str(event_names)))
        checks.append(check("end-event", "run-ended" in event_names, str(event_names)))
        log = (records / "run.log").read_text(encoding="utf-8")
        checks.append(check("readable-log-start", "RUN START" in log, "RUN START marker"))
        checks.append(check("readable-log-end", "RUN END" in log, "RUN END marker"))
        metrics_path = records / "metrics.jsonl"
        metrics = load_jsonl(metrics_path) if metrics_path.is_file() else []
        finite = all(
            isinstance(row.get("name"), str) and finite_number(row.get("value"))
            for row in metrics
        )
        checks.append(check("finite-metrics", finite, f"{len(metrics)} observations"))
        if args.require_metrics:
            checks.append(check("metrics-present", len(metrics) > 0, f"{len(metrics)} observations"))
        checks.append(
            check(
                "no-invalid-metrics",
                summary.get("invalid_metric_count", 0) == 0,
                str(summary.get("invalid_metric_count", 0)),
            )
        )
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        checks.append(check("verification-readable", False, f"{type(exc).__name__}: {exc}"))

    passed = all(item["passed"] for item in checks)
    report = {
        "schema_version": "research-experiment/run-verification-v1",
        "verified_at": now(),
        "passed": passed,
        "checks": checks,
    }
    atomic_json(records / "verification_report.json", report)
    for item in checks:
        print(f"[{'PASS' if item['passed'] else 'FAIL'}] {item['name']}: {item['evidence']}")
    print(f"RUN VERIFICATION: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
