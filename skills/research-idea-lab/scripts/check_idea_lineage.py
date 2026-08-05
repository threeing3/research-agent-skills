#!/usr/bin/env python3
"""Validate idea handoff gates and emit a deterministic readiness report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml


RELATIONS = {
    "new-family",
    "same-family-material-revision",
    "adjacent-family",
    "cosmetic-variant",
}
MECHANISM_FIELDS = (
    "state",
    "observation",
    "action",
    "learning_signal",
    "supervision_source",
    "causal_operator",
    "intervention",
    "claimed_capability",
)
PROBLEM_FIELDS = ("task", "documented_failure", "target_variable", "operating_setting")
EVALUATION_FIELDS = (
    "unit_of_analysis",
    "dataset_access",
    "primary_outcome",
    "required_counterfactual",
    "strongest_simple_baseline",
)


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("idea contract must be a YAML mapping")
    return value


def normalized(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value.strip().lower())
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(value[key]) for key in sorted(value)}
    return value


def signature(contract: dict[str, Any]) -> str:
    payload = {
        "problem_signature": normalized(contract.get("problem_signature", {})),
        "mechanism_signature": normalized(contract.get("mechanism_signature", {})),
        "evaluation_signature": normalized(contract.get("evaluation_signature", {})),
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def nonempty_mapping_fields(value: Any, fields: tuple[str, ...], prefix: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{prefix} must be a mapping"]
    failures = []
    for field in fields:
        item = value.get(field)
        if item is None or item == "" or item == []:
            failures.append(f"{prefix}.{field} is required")
    return failures


def validate(contract: dict[str, Any]) -> tuple[list[str], list[str], str]:
    failures: list[str] = []
    warnings: list[str] = []
    schema = contract.get("schema_version")
    if schema != "research-idea/v5":
        failures.append(f"schema_version must be research-idea/v5, found {schema!r}")

    lineage = contract.get("lineage")
    if not isinstance(lineage, dict):
        failures.append("lineage must be a mapping")
        lineage = {}
    if not lineage.get("family_id"):
        failures.append("lineage.family_id is required")
    relation = lineage.get("relation_to_family")
    if relation not in RELATIONS:
        failures.append(f"lineage.relation_to_family must be one of {sorted(RELATIONS)}")
    if relation == "cosmetic-variant":
        failures.append("cosmetic-variant cannot pass the anti-reskin gate")

    failures.extend(nonempty_mapping_fields(contract.get("problem_signature"), PROBLEM_FIELDS, "problem_signature"))
    failures.extend(nonempty_mapping_fields(contract.get("mechanism_signature"), MECHANISM_FIELDS, "mechanism_signature"))
    failures.extend(nonempty_mapping_fields(contract.get("evaluation_signature"), EVALUATION_FIELDS, "evaluation_signature"))

    delta = lineage.get("delta_from_parent")
    if relation == "same-family-material-revision":
        if not lineage.get("parent_idea_id") or not isinstance(lineage.get("parent_revision"), int):
            failures.append("same-family revision requires parent_idea_id and integer parent_revision")
        if not isinstance(delta, dict):
            failures.append("same-family revision requires lineage.delta_from_parent")
            delta = {}
        changed = delta.get("causal_axes_changed")
        if not isinstance(changed, list) or not changed:
            failures.append("same-family revision requires at least one causal_axes_changed entry")
        if not delta.get("new_discriminating_prediction"):
            failures.append("same-family revision requires new_discriminating_prediction")
    elif isinstance(delta, dict) and delta.get("causal_axes_changed"):
        warnings.append("delta_from_parent is populated outside a same-family material revision")

    inherited = lineage.get("inherited_failures", [])
    unresolved: list[str] = []
    if not isinstance(inherited, list):
        failures.append("lineage.inherited_failures must be a list")
        inherited = []
    for index, item in enumerate(inherited):
        if not isinstance(item, dict) or not item.get("failure_id"):
            failures.append(f"lineage.inherited_failures[{index}] requires failure_id")
            continue
        if item.get("status") not in {"resolved", "not-applicable", "unresolved"}:
            failures.append(f"failure {item['failure_id']} has invalid status")
        if item.get("status") == "unresolved":
            unresolved.append(str(item["failure_id"]))
    if unresolved:
        failures.append("unresolved inherited failures: " + ", ".join(unresolved))

    gate = contract.get("anti_reskin_gate")
    if not isinstance(gate, dict):
        failures.append("anti_reskin_gate must be a mapping")
        gate = {}
    if gate.get("status") != "pass":
        failures.append("anti_reskin_gate.status must be pass")
    if gate.get("review_context_policy") != "cold":
        failures.append("anti_reskin_gate.review_context_policy must be cold")
    if gate.get("independence_valid") is not True:
        failures.append("anti_reskin_gate.independence_valid must be true")
    if gate.get("unresolved_failure_ids") not in ([], None):
        failures.append("anti_reskin_gate.unresolved_failure_ids must be empty")

    publication = contract.get("publication_case")
    if not isinstance(publication, dict):
        failures.append("publication_case must be a mapping")
        publication = {}
    if publication.get("status") != "pass":
        failures.append("publication_case.status must be pass")
    for field in (
        "submission_horizon",
        "contribution_type",
        "one_sentence_knowledge_claim",
        "exact_difference_from_closest_work",
        "public_reproduction_or_artifact_path",
        "collision_resistant_claim",
    ):
        if not publication.get(field):
            failures.append(f"publication_case.{field} is required")
    for field in (
        "target_venues_or_tracks",
        "minimum_publishable_evidence",
    ):
        value = publication.get(field)
        if not isinstance(value, list) or not value:
            failures.append(f"publication_case.{field} must be a non-empty list")
    attacks = publication.get("strongest_reviewer_attacks")
    if not isinstance(attacks, list) or len(attacks) < 2:
        failures.append(
            "publication_case.strongest_reviewer_attacks must contain at least two attacks"
        )
    if publication.get("blockers") not in ([], None):
        failures.append("publication_case.blockers must be empty")

    industry = contract.get("industry_problem")
    if not isinstance(industry, dict):
        failures.append("industry_problem must be a mapping")
        industry = {}
    industry_status = industry.get("status")
    if industry_status not in {"not_applicable", "supported", "unresolved"}:
        failures.append(
            "industry_problem.status must be not_applicable, supported, or unresolved"
        )
    if industry_status == "unresolved":
        failures.append("industry_problem.status cannot be unresolved at handoff")
    if industry_status == "supported":
        for field in (
            "normalized_failure",
            "system_boundary",
            "public_reproduction_path",
            "scientific_question",
        ):
            if not industry.get(field):
                failures.append(f"industry_problem.{field} is required when supported")
        signal_ids = industry.get("signal_ids")
        if not isinstance(signal_ids, list) or not signal_ids:
            failures.append("industry_problem.signal_ids must be a non-empty list when supported")
        organizations = industry.get("independent_organizations")
        if not isinstance(organizations, list) or not organizations:
            failures.append(
                "industry_problem.independent_organizations must be non-empty when supported"
            )
        elif len(organizations) < 2 and not industry.get("single_source_exception"):
            failures.append(
                "industry_problem.single_source_exception is required with fewer than two independent organizations"
            )
        recurrence = industry.get("independent_recurrence_count")
        if type(recurrence) is not int or recurrence < 1:
            failures.append(
                "industry_problem.independent_recurrence_count must be a positive integer"
            )
        elif isinstance(organizations, list) and recurrence != len(set(organizations)):
            failures.append(
                "industry_problem.independent_recurrence_count must match unique independent_organizations"
            )
        readiness = industry.get("reproduction_readiness")
        if type(readiness) is not int or not 0 <= readiness <= 4:
            failures.append("industry_problem.reproduction_readiness must be an integer from 0 to 4")

    digest = signature(contract)
    recorded = gate.get("mechanism_signature_sha256")
    if recorded and recorded != digest:
        failures.append(f"recorded mechanism signature hash does not match computed {digest}")
    if not recorded:
        failures.append(f"record anti_reskin_gate.mechanism_signature_sha256 as {digest}")
    return failures, warnings, digest


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        contract_path = args.contract.resolve()
        contract = load_yaml(contract_path)
        failures, warnings, digest = validate(contract)
        report = {
            "schema_version": "research-idea/lineage-check-v2",
            "contract": str(contract_path),
            "idea_id": contract.get("idea_id"),
            "idea_revision": contract.get("revision"),
            "family_id": (contract.get("lineage") or {}).get("family_id"),
            "mechanism_signature_sha256": digest,
            "passed": not failures,
            "failures": failures,
            "warnings": warnings,
        }
        if args.report:
            atomic_json(args.report.resolve(), report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if not failures else 1
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"check_idea_lineage failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
