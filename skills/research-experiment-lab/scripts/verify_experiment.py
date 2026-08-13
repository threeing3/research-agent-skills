#!/usr/bin/env python3
"""Verify campaign completeness, run evidence, and structured thresholds."""

from __future__ import annotations

import argparse
import csv
import json
import operator
import sys
from pathlib import Path
from typing import Any

from experiment_common import atomic_json, now, read_json


OPS = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq}
STRICT_PLAN_SCHEMA = "research-experiment/plan-v3"
STRICT_REPORT_SCHEMA = "research-experiment/experiment-verification-v3"


def result(name: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"name": name, "passed": passed, "evidence": evidence}


def key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (row.get("variant"), row.get("dataset"), row.get("split"), row.get("seed"))


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def qualitative_protocol_ok(value: Any) -> bool:
    if not isinstance(value, dict) or value.get("frozen_before_results") is not True:
        return False
    categories = value.get("categories")
    outcomes = value.get("required_outcomes")
    views = value.get("comparison_views")
    return (
        isinstance(categories, list) and bool(categories) and all(nonempty(item) for item in categories)
        and isinstance(outcomes, list)
        and {"success", "failure", "unchanged-or-regression"}.issubset(set(outcomes))
        and nonempty(value.get("sampling_rule"))
        and isinstance(views, list) and len(views) >= 2 and all(nonempty(item) for item in views)
        and {"baseline", "full-method"}.issubset(set(views))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment_dir", type=Path)
    parser.add_argument("--promote-paper-ready", action="store_true")
    args = parser.parse_args()
    experiment_dir = args.experiment_dir.resolve()
    checks: list[dict[str, Any]] = []
    plan: dict[str, Any] = {}
    state: dict[str, Any] = {}
    evidence_results: list[dict[str, Any]] = []
    plan_path = experiment_dir / "experiment_plan.json"
    state_path = experiment_dir / "experiment_state.json"
    try:
        plan = read_json(plan_path)
        state = read_json(state_path)
        plan_schema = plan.get("schema_version")
        admission_mode = plan.get("admission_mode")
        if args.promote_paper_ready and plan_schema != STRICT_PLAN_SCHEMA:
            print(
                "[FAIL] plan-v3-migration-required: legacy plan-v2 is read-only and cannot be promoted in place"
            )
            print("EXPERIMENT VERIFICATION: FAIL")
            return 1
        method_identity = plan.get("method_identity") if isinstance(plan.get("method_identity"), dict) else {}
        checks.append(
            result(
                "plan-schema",
                plan_schema in {"research-experiment/plan-v2", STRICT_PLAN_SCHEMA},
                repr(plan_schema),
            )
        )
        publication_identity_ok = (
            not args.promote_paper_ready
            or (
                method_identity.get("method_tier") == "full"
                and method_identity.get("publication_eligible") is True
                and bool(method_identity.get("scientific_configuration"))
            )
        )
        checks.append(result("publication-method-identity", publication_identity_ok, repr(method_identity)))
        checks.append(
            result(
                "state-schema",
                state.get("schema_version") == "research-experiment/state-v1",
                repr(state.get("schema_version")),
            )
        )
        identities = (
            (
                "experiment-id",
                isinstance(plan.get("experiment_id"), str)
                and bool(plan.get("experiment_id"))
                and plan.get("experiment_id") == state.get("experiment_id") == experiment_dir.name,
                f"plan={plan.get('experiment_id')!r} state={state.get('experiment_id')!r} dir={experiment_dir.name!r}",
            ),
            (
                "plan-revision",
                isinstance(plan.get("plan_revision"), int)
                and not isinstance(plan.get("plan_revision"), bool)
                and int(plan["plan_revision"]) >= 1
                and plan.get("plan_revision") == state.get("plan_revision"),
                f"plan={plan.get('plan_revision')!r} state={state.get('plan_revision')!r}",
            ),
            (
                "idea-id",
                isinstance(plan.get("idea_id"), str)
                and bool(plan.get("idea_id"))
                and plan.get("idea_id") == state.get("idea_id"),
                f"plan={plan.get('idea_id')!r} state={state.get('idea_id')!r}",
            ),
            (
                "idea-revision",
                isinstance(plan.get("idea_revision"), int)
                and not isinstance(plan.get("idea_revision"), bool)
                and int(plan["idea_revision"]) >= 1
                and plan.get("idea_revision") == state.get("idea_revision"),
                f"plan={plan.get('idea_revision')!r} state={state.get('idea_revision')!r}",
            ),
        )
        for name, identity_passed, evidence in identities:
            checks.append(result(name, identity_passed, evidence))
        checks.append(
            result(
                "paper-ready-admission",
                not args.promote_paper_ready or admission_mode == "formal",
                f"admission_mode={admission_mode!r} promote={args.promote_paper_ready}",
            )
        )
        evidence_obligations = plan.get("evidence_obligations")
        if not isinstance(evidence_obligations, dict):
            evidence_obligations = {}
        evidence_results = []
        if args.promote_paper_ready:
            seen_obligation_ids: set[str] = set()
            for family in ("mechanism", "quantitative", "qualitative"):
                obligations = evidence_obligations.get(family)
                family_ok = isinstance(obligations, list) and bool(obligations)
                checks.append(
                    result(
                        f"evidence-family:{family}",
                        family_ok,
                        f"declared={len(obligations) if isinstance(obligations, list) else 0}",
                    )
                )
                if not isinstance(obligations, list):
                    continue
                for index, obligation in enumerate(obligations, 1):
                    label = f"evidence:{family}:{index}"
                    if not isinstance(obligation, dict):
                        checks.append(result(label, False, repr(obligation)))
                        continue
                    shape_ok = (
                        nonempty(obligation.get("id"))
                        and nonempty(obligation.get("claim"))
                        and isinstance(obligation.get("required_artifacts"), list)
                        and bool(obligation["required_artifacts"])
                        and all(nonempty(item) for item in obligation["required_artifacts"])
                    )
                    if family == "qualitative":
                        shape_ok = shape_ok and qualitative_protocol_ok(obligation.get("selection_protocol"))
                    obligation_id = str(obligation.get("id", ""))
                    identity_ok = bool(obligation_id) and obligation_id not in seen_obligation_ids
                    if obligation_id:
                        seen_obligation_ids.add(obligation_id)
                    shape_ok = shape_ok and identity_ok
                    checks.append(result(f"{label}:shape", shape_ok, repr(obligation)))
                    artifact_passes: list[bool] = []
                    artifacts = obligation.get("required_artifacts") if isinstance(obligation.get("required_artifacts"), list) else []
                    for relative in artifacts:
                        artifact_ok = isinstance(relative, str) and bool(relative.strip())
                        path = experiment_dir
                        if artifact_ok:
                            path = (experiment_dir / relative).resolve()
                            artifact_ok = (
                                path.is_relative_to(experiment_dir)
                                and path.is_file()
                                and path.stat().st_size > 0
                            )
                        checks.append(
                            result(
                                f"{label}:artifact:{relative}",
                                artifact_ok,
                                str(path),
                            )
                        )
                        artifact_passes.append(artifact_ok)
                    obligation_passed = shape_ok and bool(artifacts) and all(artifact_passes)
                    evidence_results.append(
                        {
                            "family": family,
                            "obligation_id": obligation_id,
                            "passed": obligation_passed,
                            "required_artifacts": artifacts,
                        }
                    )
        required_runs = plan.get("required_runs")
        checks.append(result("required-runs-declared", isinstance(required_runs, list) and bool(required_runs), str(required_runs)))
        manifests: dict[tuple[Any, ...], tuple[dict[str, Any], Path]] = {}
        for run_dir in sorted((experiment_dir / "runs").iterdir()):
            records = run_dir / "records"
            if not records.is_dir():
                continue
            manifest = read_json(records / "run_manifest.json")
            manifests[key(manifest)] = (manifest, records)
        if isinstance(required_runs, list):
            for expected in required_runs:
                if not isinstance(expected, dict):
                    checks.append(result("required-run-shape", False, repr(expected)))
                    continue
                match = manifests.get(key(expected))
                label = "/".join(str(item) for item in key(expected))
                checks.append(result(f"required-run:{label}", match is not None, label))
                if match is not None:
                    verification_path = match[1] / "verification_report.json"
                    passed = False
                    evidence = str(verification_path)
                    if verification_path.is_file():
                        verification = read_json(verification_path)
                        passed = verification.get("passed") is True
                        evidence += f" passed={verification.get('passed')}"
                    checks.append(result(f"run-verification:{label}", passed, evidence))

        analysis = experiment_dir / "analysis"
        for name in ("run_index.csv", "metric_summary.csv", "failures.csv", "resource_summary.csv"):
            path = analysis / name
            checks.append(result(f"analysis:{name}", path.is_file() and path.stat().st_size > 0, str(path)))

        summary_rows: list[dict[str, str]] = []
        summary_path = analysis / "metric_summary.csv"
        if summary_path.is_file():
            with summary_path.open(encoding="utf-8-sig", newline="") as handle:
                summary_rows = list(csv.DictReader(handle))
        thresholds = plan.get("success_thresholds", [])
        if not isinstance(thresholds, list):
            checks.append(result("threshold-shape", False, "success_thresholds must be an array"))
            thresholds = []
        for index, threshold in enumerate(thresholds, 1):
            if not isinstance(threshold, dict):
                checks.append(result(f"threshold:{index}", False, repr(threshold)))
                continue
            needed = ("metric", "variant", "dataset", "split", "op", "value")
            if any(field not in threshold for field in needed) or threshold.get("op") not in OPS:
                checks.append(result(f"threshold:{index}", False, f"invalid structured threshold: {threshold}"))
                continue
            matches = [
                row for row in summary_rows
                if row.get("metric") == str(threshold["metric"])
                and row.get("variant") == str(threshold["variant"])
                and row.get("dataset") == str(threshold["dataset"])
                and row.get("split") == str(threshold["split"])
            ]
            if len(matches) != 1:
                checks.append(result(f"threshold:{index}", False, f"matching groups={len(matches)}"))
                continue
            observed = float(matches[0]["mean"])
            expected = float(threshold["value"])
            passed = OPS[str(threshold["op"])](observed, expected)
            checks.append(
                result(
                    f"threshold:{index}",
                    passed,
                    f"mean {observed} {threshold['op']} {expected}",
                )
            )

        if plan.get("mode") != "pilot":
            for field in ("datasets", "variants", "metrics", "seeds"):
                value = plan.get(field)
                checks.append(result(f"formal-plan:{field}", isinstance(value, list) and bool(value), repr(value)))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        checks.append(result("verification-readable", False, f"{type(exc).__name__}: {exc}"))

    passed = all(item["passed"] for item in checks)
    admission_mode = plan.get("admission_mode")
    stage = (
        "paper-ready"
        if passed and args.promote_paper_ready
        else "verified-diagnostic"
        if passed and admission_mode == "exploratory-validation"
        else "verified-scientific"
        if passed
        else "blocked"
    )
    report = {
        "schema_version": (
            STRICT_REPORT_SCHEMA
            if plan.get("schema_version") == STRICT_PLAN_SCHEMA
            else "research-experiment/experiment-verification-v2"
        ),
        "plan_schema_version": plan.get("schema_version"),
        "admission_mode": admission_mode,
        "verified_at": now(),
        "experiment_id": plan.get("experiment_id"),
        "plan_revision": plan.get("plan_revision"),
        "idea_id": plan.get("idea_id"),
        "idea_revision": plan.get("idea_revision"),
        "method_identity": plan.get("method_identity", {}),
        "evidence_summary": {
            family: sum(1 for item in evidence_results if item["family"] == family and item["passed"])
            for family in ("mechanism", "quantitative", "qualitative")
        },
        "evidence_results": evidence_results,
        "stage": stage,
        "passed": passed,
        "blockers": [item["name"] for item in checks if not item["passed"]],
        "checks": checks,
    }
    atomic_json(experiment_dir / "verification_report.json", report)
    for item in checks:
        print(f"[{'PASS' if item['passed'] else 'FAIL'}] {item['name']}: {item['evidence']}")
    print(f"EXPERIMENT VERIFICATION: {'PASS' if passed else 'FAIL'}")
    if passed:
        state["stage"] = stage
        state["updated_at"] = now()
        state["verified_evidence"] = [
            "verification_report.json",
            "analysis/run_index.csv",
            "analysis/metric_summary.csv",
            "analysis/failures.csv",
            "analysis/resource_summary.csv",
        ]
        atomic_json(experiment_dir / "experiment_state.json", state)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
