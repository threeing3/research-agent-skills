#!/usr/bin/env python3
"""Validate a user-approved pre-gate idea validation against its experiment plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


DEFAULT_MAX_DIRECT_COST_CNY = 100.0
DEFAULT_MAX_WALL_TIME_HOURS = 24.0
ALLOWED_LIGHTWEIGHT_STATUSES = {"no-obvious-collision", "uncertain"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def finite_nonnegative(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if number != number or number in (float("inf"), float("-inf")) or number < 0:
        return None
    return number


def check(name: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "evidence": evidence}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--alignment", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    blockers: list[str] = []
    try:
        alignment_path = args.alignment.resolve()
        plan_path = args.plan.resolve()
        alignment = load_yaml(alignment_path)
        plan = load_json(plan_path)
        alignment_hash = sha256_file(alignment_path)

        checks.append(
            check(
                "alignment-schema",
                alignment.get("schema_version") == "research-idea/validation-alignment-v1",
                repr(alignment.get("schema_version")),
            )
        )
        checks.append(
            check(
                "exploratory-admission-mode",
                plan.get("admission_mode") == "exploratory-validation",
                repr(plan.get("admission_mode")),
            )
        )
        checks.append(
            check(
                "alignment-maturity",
                alignment.get("maturity") == "validation-ready",
                repr(alignment.get("maturity")),
            )
        )

        for name, plan_value, alignment_value in (
            ("idea-id", plan.get("idea_id"), alignment.get("idea_id")),
            ("idea-revision", plan.get("idea_revision"), alignment.get("idea_revision")),
            (
                "implementation-revision",
                plan.get("implementation_revision"),
                alignment.get("implementation_revision"),
            ),
        ):
            checks.append(
                check(name, plan_value == alignment_value, f"plan={plan_value!r} alignment={alignment_value!r}")
            )

        alignment_ref = plan.get("validation_alignment")
        if not isinstance(alignment_ref, dict):
            checks.append(check("alignment-reference", False, "missing validation_alignment object"))
        else:
            recorded_hash = alignment_ref.get("sha256")
            checks.append(
                check(
                    "alignment-hash",
                    recorded_hash == alignment_hash,
                    f"plan={recorded_hash!r} computed={alignment_hash!r}",
                )
            )

        collision = alignment.get("lightweight_collision_check")
        collision_status = collision.get("status") if isinstance(collision, dict) else None
        collision_ok = collision_status in ALLOWED_LIGHTWEIGHT_STATUSES
        checks.append(check("lightweight-collision", collision_ok, repr(collision_status)))
        if not collision_ok:
            blockers.append("collision-needs-revision")

        boundary = alignment.get("target_domain_boundary")
        if not isinstance(boundary, dict):
            boundary = {}
        boundary_ok = (
            nonempty(boundary.get("task"))
            and nonempty(boundary.get("problem_setting"))
            and isinstance(boundary.get("key_constraints"), list)
            and bool(boundary.get("key_constraints"))
            and all(nonempty(item) for item in boundary["key_constraints"])
        )
        checks.append(check("target-domain-boundary", boundary_ok, repr(boundary)))

        collision_details_ok = (
            isinstance(collision, dict)
            and nonempty(collision.get("checked_at"))
            and isinstance(collision.get("target_domain_queries"), list)
            and bool(collision.get("target_domain_queries"))
            and all(nonempty(item) for item in collision["target_domain_queries"])
        )
        checks.append(check("lightweight-collision-evidence", collision_details_ok, repr(collision)))

        validation = alignment.get("validation")
        if not isinstance(validation, dict):
            validation = {}
        applicability = validation.get("applicability")
        checks.append(check("probe-applicable", applicability == "applicable", repr(applicability)))
        if applicability == "not-identifiable":
            blockers.append("mechanism-not-identifiable")
        elif applicability != "applicable":
            blockers.append("probe-not-applicable")

        for field in ("applicability_reason", "question", "falsifiable_prediction", "strongest_alternative"):
            checks.append(check(f"validation:{field}", nonempty(validation.get(field)), repr(validation.get(field))))

        for field in ("activation_evidence", "intervention_evidence", "stop_conditions"):
            value = validation.get(field)
            checks.append(check(f"validation:{field}", isinstance(value, list) and bool(value), repr(value)))

        outcomes = validation.get("outcome_interpretation")
        if not isinstance(outcomes, dict):
            outcomes = {}
        for outcome in ("supportive", "negative", "inconclusive"):
            checks.append(check(f"outcome:{outcome}", nonempty(outcomes.get(outcome)), repr(outcomes.get(outcome))))

        idea_type = alignment.get("idea_type")
        if idea_type in {"baseline-modification", "mechanism-combination"}:
            blueprint = alignment.get("baseline_change")
            required_blueprint = (
                "baseline_id",
                "selection_reason",
                "target_failure",
                "operation",
                "location",
                "before",
                "after",
            )
            blueprint_ok = isinstance(blueprint, dict) and all(nonempty(blueprint.get(field)) for field in required_blueprint)
            checks.append(check("baseline-change-blueprint", blueprint_ok, repr(blueprint)))
            ablations = blueprint.get("required_ablations") if isinstance(blueprint, dict) else None
            ablations_ok = isinstance(ablations, list) and bool(ablations) and all(nonempty(item) for item in ablations)
            checks.append(check("baseline-required-ablations", ablations_ok, repr(ablations)))

        approval = alignment.get("user_alignment")
        if not isinstance(approval, dict):
            approval = {}
        approval_ok = (
            approval.get("status") == "approved"
            and nonempty(approval.get("approved_at"))
            and nonempty(approval.get("approved_scope"))
        )
        checks.append(check("user-alignment", approval_ok, repr(approval.get("status"))))
        if not approval_ok:
            blockers.append("user-alignment-required")

        plan_budget = plan.get("budget") if isinstance(plan.get("budget"), dict) else {}
        alignment_budget = alignment.get("budget") if isinstance(alignment.get("budget"), dict) else {}
        plan_cost = finite_nonnegative(plan_budget.get("max_direct_cost_cny"))
        plan_hours = finite_nonnegative(plan_budget.get("max_wall_time_hours"))
        alignment_cost = finite_nonnegative(alignment_budget.get("max_direct_cost_cny"))
        alignment_hours = finite_nonnegative(alignment_budget.get("max_wall_time_hours"))
        approved_cost = finite_nonnegative(approval.get("approved_max_direct_cost_cny"))
        approved_hours = finite_nonnegative(approval.get("approved_max_wall_time_hours"))

        cost_ok = (
            plan_cost is not None
            and alignment_cost is not None
            and approved_cost is not None
            and plan_cost <= alignment_cost <= approved_cost
        )
        hours_ok = (
            plan_hours is not None
            and plan_hours > 0
            and alignment_hours is not None
            and alignment_hours > 0
            and approved_hours is not None
            and approved_hours > 0
            and plan_hours <= alignment_hours <= approved_hours
        )
        checks.append(check("approved-direct-cost", cost_ok, f"plan={plan_cost} alignment={alignment_cost} approved={approved_cost}"))
        checks.append(check("approved-wall-time", hours_ok, f"plan={plan_hours} alignment={alignment_hours} approved={approved_hours}"))

        exceeds_default = (
            (approved_cost is not None and approved_cost > DEFAULT_MAX_DIRECT_COST_CNY)
            or (approved_hours is not None and approved_hours > DEFAULT_MAX_WALL_TIME_HOURS)
        )
        override_ok = not exceeds_default or approval.get("resource_override_approved") is True
        checks.append(check("resource-override", override_ok, f"exceeds_default={exceeds_default} approved={approval.get('resource_override_approved')!r}"))
        if not cost_ok or not hours_ok or not override_ok:
            blockers.append("budget-not-approved")

        plan_stops = plan.get("stop_conditions")
        alignment_stops = validation.get("stop_conditions")
        stops_ok = (
            isinstance(plan_stops, list)
            and bool(plan_stops)
            and plan_stops == alignment_stops
        )
        checks.append(
            check(
                "plan-stop-conditions",
                stops_ok,
                f"plan={plan_stops!r} alignment={alignment_stops!r}",
            )
        )

        if any(not item["passed"] for item in checks) and not blockers:
            blockers.append("alignment-incomplete")
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        checks.append(check("alignment-readable", False, f"{type(exc).__name__}: {exc}"))
        blockers.append("alignment-unreadable")

    passed = all(item["passed"] for item in checks)
    report = {
        "schema_version": "research-experiment/validation-alignment-check-v1",
        "checked_at": now(),
        "passed": passed,
        "blockers": sorted(set(blockers)) if not passed else [],
        "checks": checks,
    }
    if args.report:
        atomic_json(args.report.resolve(), report)
    for item in checks:
        print(f"[{'PASS' if item['passed'] else 'FAIL'}] {item['name']}: {item['evidence']}")
    print(f"VALIDATION ALIGNMENT: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
