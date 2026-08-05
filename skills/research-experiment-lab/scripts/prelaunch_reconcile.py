#!/usr/bin/env python3
"""Reconcile idea lineage, plan identity, constraints, and task dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import operator
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


OPS = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq}
REQUIRED_GATES = {"anti-reskin", "mechanism-identifiability", "simple-baseline-survival", "data-feasibility"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return value


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value.strip().lower())
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(value[key]) for key in sorted(value)}
    return value


def mechanism_sha256(contract: dict[str, Any]) -> str:
    payload = {
        "problem_signature": normalized(contract.get("problem_signature", {})),
        "mechanism_signature": normalized(contract.get("mechanism_signature", {})),
        "evaluation_signature": normalized(contract.get("evaluation_signature", {})),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def check_result(name: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "evidence": evidence}


def check_task_graph(tasks: Any) -> tuple[bool, str]:
    if not isinstance(tasks, list):
        return False, "tasks must be an array"
    ids = [task.get("task_id") for task in tasks if isinstance(task, dict)]
    if len(ids) != len(tasks) or any(not isinstance(item, str) or not item for item in ids):
        return False, "every task requires a non-empty task_id"
    if len(set(ids)) != len(ids):
        return False, "task_id values must be unique"
    known = set(ids)
    graph: dict[str, list[str]] = {}
    for task in tasks:
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list) or any(dep not in known for dep in dependencies):
            return False, f"task {task['task_id']} has unknown or invalid dependency"
        graph[task["task_id"]] = dependencies

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return False
        if node in visited:
            return True
        visiting.add(node)
        if any(not visit(parent) for parent in graph[node]):
            return False
        visiting.remove(node)
        visited.add(node)
        return True

    if any(not visit(node) for node in graph):
        return False, "task dependency graph contains a cycle"
    return True, f"{len(tasks)} tasks, acyclic"


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--idea-contract", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    try:
        contract_path = args.idea_contract.resolve()
        plan_path = args.plan.resolve()
        contract = read_yaml(contract_path)
        plan = read_json(plan_path)
        lineage = contract.get("lineage") if isinstance(contract.get("lineage"), dict) else {}
        gate = contract.get("anti_reskin_gate") if isinstance(contract.get("anti_reskin_gate"), dict) else {}
        decision = contract.get("decision") if isinstance(contract.get("decision"), dict) else {}

        checks.append(check_result("idea-schema", contract.get("schema_version") == "research-idea/v4", str(contract.get("schema_version"))))
        checks.append(check_result("idea-experiment-ready", contract.get("status") == "experiment-ready", str(contract.get("status"))))
        checks.append(check_result("idea-user-selected", decision.get("selected_by_user") is True, str(decision.get("selected_by_user"))))
        checks.append(check_result("anti-reskin-gate", gate.get("status") == "pass" and gate.get("independence_valid") is True and gate.get("review_context_policy") == "cold", repr(gate.get("status"))))

        inherited = lineage.get("inherited_failures", []) if isinstance(lineage, dict) else []
        unresolved = [str(item.get("failure_id")) for item in inherited if isinstance(item, dict) and item.get("status") == "unresolved"]
        checks.append(check_result("inherited-failures-resolved", not unresolved, repr(unresolved)))
        if unresolved:
            blockers.append("lineage-blocked")

        contract_hash = file_sha256(contract_path)
        mechanism_hash = mechanism_sha256(contract)
        checks.append(check_result("idea-recorded-mechanism-hash", gate.get("mechanism_signature_sha256") == mechanism_hash, f"recorded={gate.get('mechanism_signature_sha256')!r} computed={mechanism_hash!r}"))
        identities = (
            ("idea-id", plan.get("idea_id"), contract.get("idea_id")),
            ("idea-revision", plan.get("idea_revision"), contract.get("revision")),
            ("idea-contract-sha256", plan.get("idea_contract_sha256"), contract_hash),
            ("mechanism-family-id", plan.get("mechanism_family_id"), lineage.get("family_id")),
            ("mechanism-signature-sha256", plan.get("mechanism_signature_sha256"), mechanism_hash),
        )
        for name, observed, expected in identities:
            checks.append(check_result(name, observed == expected, f"plan={observed!r} idea={expected!r}"))

        expected_failure_ids = sorted(str(item.get("failure_id")) for item in inherited if isinstance(item, dict) and item.get("failure_id"))
        observed_failure_ids = plan.get("inherited_failure_ids")
        checks.append(check_result("failure-ledger-consumed", isinstance(observed_failure_ids, list) and sorted(map(str, observed_failure_ids)) == expected_failure_ids, f"plan={observed_failure_ids!r} idea={expected_failure_ids!r}"))

        prelaunch = plan.get("prelaunch")
        if not isinstance(prelaunch, dict):
            checks.append(check_result("prelaunch-declared", False, "missing prelaunch object"))
            prelaunch = {}
        else:
            checks.append(check_result("prelaunch-declared", True, "present"))
        declared_gates = set(prelaunch.get("required_gates", [])) if isinstance(prelaunch.get("required_gates"), list) else set()
        missing_gates = sorted(REQUIRED_GATES - declared_gates)
        checks.append(check_result("required-gates", not missing_gates, repr(missing_gates)))

        lineage_report_value = prelaunch.get("lineage_check_report")
        lineage_report_path = None
        if isinstance(lineage_report_value, str) and lineage_report_value:
            candidate = Path(lineage_report_value)
            lineage_report_path = candidate if candidate.is_absolute() else plan_path.parent / candidate
        report_valid = False
        report_evidence = repr(lineage_report_value)
        if lineage_report_path and lineage_report_path.is_file():
            lineage_report = read_json(lineage_report_path)
            report_valid = (
                lineage_report.get("passed") is True
                and lineage_report.get("idea_id") == contract.get("idea_id")
                and lineage_report.get("idea_revision") == contract.get("revision")
                and lineage_report.get("mechanism_signature_sha256") == mechanism_hash
            )
            report_evidence = str(lineage_report_path)
        checks.append(check_result("lineage-check-report", report_valid, report_evidence))

        constraints = prelaunch.get("constraints")
        if not isinstance(constraints, list) or not constraints:
            checks.append(check_result("constraints-declared", False, "at least one evidenced constraint is required"))
            blockers.append("scientifically-unsatisfiable")
        else:
            checks.append(check_result("constraints-declared", True, str(len(constraints))))
            for index, constraint in enumerate(constraints, 1):
                name = f"constraint:{constraint.get('constraint_id', index)}" if isinstance(constraint, dict) else f"constraint:{index}"
                if not isinstance(constraint, dict) or constraint.get("op") not in OPS:
                    checks.append(check_result(name, False, repr(constraint)))
                    blockers.append("scientifically-unsatisfiable")
                    continue
                try:
                    available = float(constraint["available"])
                    required = float(constraint["required"])
                    passed = OPS[str(constraint["op"])](available, required)
                except (KeyError, TypeError, ValueError):
                    checks.append(check_result(name, False, "available and required must be numeric"))
                    blockers.append("scientifically-unsatisfiable")
                    continue
                evidence = f"{available} {constraint['op']} {required}; source={constraint.get('evidence')!r}"
                checks.append(check_result(name, passed and bool(constraint.get("evidence")), evidence))
                if not passed:
                    blockers.append("permission-blocked" if constraint.get("resolution_authorized") is False and constraint.get("resolution") else "scientifically-unsatisfiable")

        graph_ok, graph_evidence = check_task_graph(plan.get("tasks"))
        checks.append(check_result("task-graph", graph_ok, graph_evidence))
        if not graph_ok:
            blockers.append("scientifically-unsatisfiable")

        if any(not item["passed"] for item in checks) and not blockers:
            blockers.append("lineage-blocked")
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        checks.append(check_result("prelaunch-readable", False, f"{type(exc).__name__}: {exc}"))
        blockers.append("technically-blocked")

    passed = all(item["passed"] for item in checks)
    report = {
        "schema_version": "research-experiment/prelaunch-reconciliation-v1",
        "reconciled_at": now(),
        "passed": passed,
        "blockers": sorted(set(blockers)) if not passed else [],
        "checks": checks,
    }
    if args.report:
        atomic_json(args.report.resolve(), report)
    for item in checks:
        print(f"[{'PASS' if item['passed'] else 'FAIL'}] {item['name']}: {item['evidence']}")
    print(f"PRELAUNCH RECONCILIATION: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
