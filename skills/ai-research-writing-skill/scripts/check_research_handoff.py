#!/usr/bin/env python3
"""Validate an upstream research-system handoff before paper writing starts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from check_numeric_evidence import load_registry
from paper_contract import ContractError, digest_file, load_json_object, read_utf8


LEGACY_SCHEMA_VERSION = "ai-research-writing/research-handoff-v1"
SHARED_SCHEMA_VERSION = "ai-research-writing/research-handoff-v2"
STRICT_PLAN_SCHEMA = "research-experiment/plan-v3"
STRICT_VERIFICATION_SCHEMA = "research-experiment/experiment-verification-v3"
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{0,95}$")
ROOT_FIELDS = {
    "schema_version",
    "source_idea_id",
    "source_idea_revision",
    "experiment_id",
    "experiment_plan_revision",
    "source_idea_contract_sha256",
    "experiment_plan_sha256",
    "research_question",
    "paper_type",
    "target_venue",
    "quantitative",
    "artifacts",
    "blockers",
}
ARTIFACT_FIELDS = {
    "project_inventory",
    "analysis",
    "decision",
    "experiment_inventory",
    "experiment_verification",
    "run_index",
    "metric_summary",
    "numeric_evidence",
    "literature_inventory",
    "figure_inventory",
}
BASE_ARTIFACTS = {"project_inventory", "analysis", "decision"}


def _artifact_path(root: Path, name: str, raw: object) -> Path:
    if not isinstance(raw, str) or not raw:
        raise ContractError(f"research_handoff.json artifacts.{name} must be a non-empty path")
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError(f"research_handoff.json artifacts.{name} escapes project root: {raw}") from exc
    if not path.is_file():
        raise ContractError(f"research_handoff.json artifacts.{name} does not exist: {raw}")
    if path.stat().st_size == 0:
        raise ContractError(f"research_handoff.json artifacts.{name} is empty: {raw}")
    return path


def _project_file(root: Path, raw: object, label: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise ContractError(f"{label} must be a non-empty project-relative path")
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError(f"{label} escapes project root: {raw}") from exc
    if not path.is_file():
        raise ContractError(f"{label} does not exist: {raw}")
    return path


def _state_file(
    root: Path,
    state_paths: dict[str, object],
    key: str,
    default: str,
    legacy_default: str | None = None,
) -> Path:
    configured = state_paths.get(key)
    if configured is not None:
        return _project_file(root, configured, f"research_state.json paths.{key}")
    canonical = (root / default).resolve()
    if canonical.is_file():
        return canonical
    if legacy_default:
        legacy = (root / legacy_default).resolve()
        if legacy.is_file():
            return legacy
    return _project_file(root, default, f"research_state.json paths.{key}")


def _load_yaml_object(path: Path) -> dict[str, object]:
    try:
        value = yaml.safe_load(read_utf8(path))
    except yaml.YAMLError as exc:
        raise ContractError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"Expected a YAML mapping in {path}")
    return value


def _require_match(label: str, observed: object, expected: object) -> None:
    if observed != expected:
        raise ContractError(f"{label} mismatch: observed={observed!r}, expected={expected!r}")


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _qualitative_protocol_ok(value: object) -> bool:
    if not isinstance(value, dict) or value.get("frozen_before_results") is not True:
        return False
    categories = value.get("categories")
    outcomes = value.get("required_outcomes")
    views = value.get("comparison_views")
    return (
        isinstance(categories, list) and bool(categories) and all(_nonempty(item) for item in categories)
        and isinstance(outcomes, list)
        and {"success", "failure", "unchanged-or-regression"}.issubset(set(outcomes))
        and _nonempty(value.get("sampling_rule"))
        and isinstance(views, list) and len(views) >= 2 and all(_nonempty(item) for item in views)
        and {"baseline", "full-method"}.issubset(set(views))
    )


def _verify_evidence_closure(
    experiment_dir: Path,
    plan: dict[str, object],
    verification: dict[str, object],
) -> None:
    obligations = plan.get("evidence_obligations")
    if not isinstance(obligations, dict):
        raise ContractError("plan-v3 requires evidence_obligations")
    expected: dict[tuple[str, str], list[str]] = {}
    for family in ("mechanism", "quantitative", "qualitative"):
        rows = obligations.get(family)
        if not isinstance(rows, list) or not rows:
            raise ContractError(f"paper-ready plan requires non-empty {family} obligations")
        for row in rows:
            if not isinstance(row, dict) or not _nonempty(row.get("id")) or not _nonempty(row.get("claim")):
                raise ContractError(f"invalid {family} evidence obligation")
            artifacts = row.get("required_artifacts")
            if not isinstance(artifacts, list) or not artifacts or not all(_nonempty(item) for item in artifacts):
                raise ContractError(f"invalid {family} required_artifacts")
            if family == "qualitative" and not _qualitative_protocol_ok(row.get("selection_protocol")):
                raise ContractError("qualitative evidence requires a structured frozen selection protocol")
            key = (family, str(row["id"]))
            if key in expected:
                raise ContractError(f"duplicate evidence obligation identity: {key}")
            expected[key] = list(artifacts)

    results = verification.get("evidence_results")
    if not isinstance(results, list):
        raise ContractError("verification-v3 requires evidence_results")
    observed: dict[tuple[str, str], dict[str, object]] = {}
    for row in results:
        if not isinstance(row, dict):
            raise ContractError("verification evidence result must be an object")
        key = (str(row.get("family")), str(row.get("obligation_id")))
        if key in observed:
            raise ContractError(f"duplicate evidence result identity: {key}")
        observed[key] = row
    if set(observed) != set(expected):
        raise ContractError("verification evidence results do not exactly match plan obligations")

    passed_counts = {family: 0 for family in ("mechanism", "quantitative", "qualitative")}
    for key, artifacts in expected.items():
        row = observed[key]
        if row.get("passed") is not True or row.get("required_artifacts") != artifacts:
            raise ContractError(f"evidence result is not a passing exact match: {key}")
        for raw in artifacts:
            path = (experiment_dir / raw).resolve()
            try:
                path.relative_to(experiment_dir.resolve())
            except ValueError as exc:
                raise ContractError(f"evidence artifact escapes experiment directory: {raw}") from exc
            if not path.is_file() or path.stat().st_size == 0:
                raise ContractError(f"verified evidence artifact is missing or empty: {raw}")
        passed_counts[key[0]] += 1
    _require_match("verification evidence summary", verification.get("evidence_summary"), passed_counts)


def _validate_v2_identity_fields(handoff: dict[str, object]) -> None:
    for field in ("source_idea_id", "experiment_id"):
        if not isinstance(handoff.get(field), str) or not str(handoff[field]).strip():
            raise ContractError(f"handoff v2 requires a non-empty string field: {field}")
    for field in ("source_idea_revision", "experiment_plan_revision"):
        if (
            not isinstance(handoff.get(field), int)
            or isinstance(handoff.get(field), bool)
            or int(handoff[field]) < 1
        ):
            raise ContractError(f"handoff v2 requires a positive integer field: {field}")
    for field in ("source_idea_contract_sha256", "experiment_plan_sha256"):
        value = handoff.get(field)
        if value is not None and (not isinstance(value, str) or not HASH_PATTERN.fullmatch(value)):
            raise ContractError(f"optional legacy digest must be lowercase SHA-256: {field}")


def _validate_shared_state(
    root: Path,
    handoff: dict[str, object],
    artifact_paths: dict[str, Path],
) -> None:
    if handoff.get("schema_version") != SHARED_SCHEMA_VERSION:
        raise ContractError(
            f"shared-state handoff schema_version must be {SHARED_SCHEMA_VERSION}"
        )
    _validate_v2_identity_fields(handoff)

    state = load_json_object(root / "research_state.json")
    state_paths = state.get("paths")
    if not isinstance(state_paths, dict):
        raise ContractError("research_state.json paths must be an object")
    idea_id = str(handoff["source_idea_id"])
    experiment_id = str(handoff["experiment_id"])
    for label, value in (("source_idea_id", idea_id), ("experiment_id", experiment_id)):
        if not ID_PATTERN.fullmatch(value):
            raise ContractError(f"shared-state handoff {label} has an unsafe identifier: {value!r}")
    idea_revision = handoff["source_idea_revision"]
    plan_revision = handoff["experiment_plan_revision"]
    contract_hash = handoff.get("source_idea_contract_sha256")
    plan_hash = handoff.get("experiment_plan_sha256")

    _require_match("active idea", idea_id, state.get("active_idea_id"))
    _require_match("active experiment", experiment_id, state.get("active_experiment_id"))

    idea_pool_path = _state_file(
        root, state_paths, "idea_pool", "research_state/ideas/idea_pool.json"
    )
    idea_pool = load_json_object(idea_pool_path)
    pool_rows = idea_pool.get("ideas")
    if not isinstance(pool_rows, list):
        raise ContractError("idea_pool.json ideas must be an array")
    matching_pool_rows = [
        row for row in pool_rows
        if isinstance(row, dict) and str(row.get("id")) == idea_id
    ]
    if len(matching_pool_rows) != 1:
        raise ContractError(
            f"idea pool must contain exactly one active idea row for {idea_id}; found {len(matching_pool_rows)}"
        )
    pool_status = matching_pool_rows[0].get("status")
    if not isinstance(pool_status, str) or not pool_status.startswith("experiment-ready"):
        raise ContractError(f"active idea pool status is not experiment-ready: {pool_status!r}")

    contract_path = idea_pool_path.parent / idea_id / "idea_contract.yaml"
    if not contract_path.is_file():
        raise ContractError(f"active idea contract does not exist: {contract_path}")
    contract = _load_yaml_object(contract_path)
    _require_match("idea contract schema", contract.get("schema_version"), "research-idea/v4")
    _require_match("idea contract id", contract.get("idea_id"), idea_id)
    _require_match("idea contract revision", contract.get("revision"), idea_revision)
    if contract.get("status") != "experiment-ready":
        raise ContractError(f"idea contract issued status is not experiment-ready: {contract.get('status')!r}")
    lifecycle = contract.get("lifecycle")
    if not isinstance(lifecycle, dict):
        raise ContractError("active idea contract requires lifecycle metadata")
    _require_match("idea lifecycle validity", lifecycle.get("validity"), "active")
    _require_match("idea lifecycle pool status", lifecycle.get("current_pool_status"), pool_status)
    if contract_hash is not None:
        _require_match("idea contract SHA-256", digest_file(contract_path), contract_hash)

    contract_profile = contract.get("contract_profile")
    if contract_profile != "problem-led/v1":
        raise ContractError("formal writing handoff requires problem-led/v1; older profiles are legacy-read-only")
    if contract_profile == "problem-led/v1":
        novelty_review = contract.get("novelty_review")
        target_boundary = contract.get("target_domain_boundary")
        if not isinstance(novelty_review, dict):
            raise ContractError("staged idea contract requires novelty_review")
        if not isinstance(target_boundary, dict):
            raise ContractError("staged idea contract requires target_domain_boundary")
        _require_match("focused target novelty", novelty_review.get("status"), "supported")
        if not isinstance(novelty_review.get("coverage_end"), str) or not novelty_review.get("coverage_end"):
            raise ContractError("staged idea contract requires novelty_review.coverage_end")
        if novelty_review.get("recall_confidence") not in {"low", "medium", "high"}:
            raise ContractError("staged idea contract requires novelty_review.recall_confidence")
        for field in ("task", "problem_setting"):
            if not isinstance(target_boundary.get(field), str) or not target_boundary.get(field):
                raise ContractError(f"staged idea contract requires target_domain_boundary.{field}")

    if contract_profile == "problem-led/v1":
        derivation = contract.get("problem_derivation")
        if not isinstance(derivation, dict):
            raise ContractError("problem-led idea contract requires problem_derivation")
        for field in (
            "problem_id",
            "problem_revision",
            "problem_card",
            "observed_failure",
            "bottleneck_hypothesis",
            "distinctive_motivation_insight",
            "research_value",
            "required_behavior_change",
            "design_principle",
            "module_operation",
            "implementation_location",
        ):
            if derivation.get(field) in (None, ""):
                raise ContractError(f"problem-led idea contract requires problem_derivation.{field}")
        triad = derivation.get("evidence_triad")
        if not isinstance(triad, dict):
            raise ContractError("problem-led idea contract requires evidence_triad")
        for family in ("mechanism", "quantitative", "qualitative"):
            if not isinstance(triad.get(family), list) or not triad[family]:
                raise ContractError(f"problem-led idea contract requires evidence_triad.{family}")
        chain = derivation.get("motivation_to_design_chain")
        if not isinstance(chain, list) or len(chain) < 4 or not all(_nonempty(item) for item in chain):
            raise ContractError("problem-led idea contract requires a four-step motivation_to_design_chain")
        revision = derivation.get("problem_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            raise ContractError("problem-led idea contract requires a positive problem_revision")
        if derivation.get("problem_maturity") not in {"bottleneck-framed", "solution-ready"}:
            raise ContractError("problem-led idea contract has invalid problem_maturity")
        if derivation.get("motivation_status") not in {"distinctive-hypothesis", "evidence-backed", "contested"}:
            raise ContractError("problem-led idea contract has invalid motivation_status")
        problem_card_path = _project_file(root, derivation.get("problem_card"), "problem_derivation.problem_card")
        problem_card = _load_yaml_object(problem_card_path)
        motivation = problem_card.get("motivation_insight")
        motivation_status = motivation.get("status") if isinstance(motivation, dict) else None
        for label, observed_value, expected_value in (
            ("problem card schema", problem_card.get("schema_version"), "research-problem/v1"),
            ("problem card id", problem_card.get("problem_id"), derivation.get("problem_id")),
            ("problem card revision", problem_card.get("revision"), revision),
            ("problem card maturity", problem_card.get("maturity"), derivation.get("problem_maturity")),
            ("problem card motivation", motivation_status, derivation.get("motivation_status")),
        ):
            _require_match(label, observed_value, expected_value)
        if problem_card.get("status") not in {"open", "contested", "parked"}:
            raise ContractError("problem card must remain open, contested, or parked for formal writing handoff")

    consistency_path = _state_file(
        root,
        state_paths,
        "idea_state_consistency",
        "research_state/ideas/state_consistency.json",
        "research_state/ideas/idea_state_consistency.json",
    )
    consistency = load_json_object(consistency_path)
    _require_match(
        "idea-state consistency schema",
        consistency.get("schema_version"),
        "research-idea/state-consistency-v2",
    )
    if consistency.get("passed") is not True:
        raise ContractError("idea-state consistency report must record passed: true")
    records = consistency.get("records")
    matching_records = [
        record for record in records
        if isinstance(record, dict) and record.get("idea_id") == idea_id
    ] if isinstance(records, list) else []
    if len(matching_records) != 1:
        raise ContractError(
            f"idea-state consistency report must contain one record for {idea_id}; found {len(matching_records)}"
        )
    record = matching_records[0]
    for label, observed, expected in (
        ("consistent idea revision", record.get("contract_revision"), idea_revision),
        ("consistent idea lifecycle", record.get("lifecycle_validity"), "active"),
        ("consistent idea pool status", record.get("pool_status"), pool_status),
    ):
        _require_match(label, observed, expected)

    experiments_value = state_paths.get("experiments", "research_state/experiments")
    if not isinstance(experiments_value, str) or not experiments_value:
        raise ContractError("research_state.json paths.experiments must be a non-empty path")
    experiments_root = (root / experiments_value).resolve()
    try:
        experiments_root.relative_to(root.resolve())
    except ValueError as exc:
        raise ContractError("research_state.json paths.experiments escapes project root") from exc
    experiment_dir = (experiments_root / experiment_id).resolve()
    try:
        experiment_dir.relative_to(experiments_root)
    except ValueError as exc:
        raise ContractError("active experiment path escapes experiments root") from exc
    plan_path = experiment_dir / "experiment_plan.json"
    experiment_state_path = experiment_dir / "experiment_state.json"
    for path, label in ((plan_path, "experiment plan"), (experiment_state_path, "experiment state")):
        if not path.is_file():
            raise ContractError(f"active {label} does not exist: {path}")

    plan = load_json_object(plan_path)
    _require_match(
        "experiment plan admission mode",
        plan.get("admission_mode"),
        "formal",
    )
    for label, observed, expected in (
        ("experiment plan schema", plan.get("schema_version"), STRICT_PLAN_SCHEMA),
        ("experiment plan id", plan.get("experiment_id"), experiment_id),
        ("experiment plan revision", plan.get("plan_revision"), plan_revision),
        ("experiment plan idea id", plan.get("idea_id"), idea_id),
        ("experiment plan idea revision", plan.get("idea_revision"), idea_revision),
    ):
        _require_match(label, observed, expected)
    if contract_hash is not None:
        _require_match("experiment plan idea contract SHA-256", plan.get("idea_contract_sha256"), contract_hash)
    if plan_hash is not None:
        _require_match("experiment plan SHA-256", digest_file(plan_path), plan_hash)

    method_identity = plan.get("method_identity")
    if not isinstance(method_identity, dict):
        raise ContractError("formal writing handoff requires method_identity")
    if method_identity.get("method_tier") != "full" or method_identity.get("publication_eligible") is not True:
        raise ContractError("writing handoff requires a publication-eligible full method")
    if not isinstance(method_identity.get("scientific_configuration"), str) or not method_identity.get("scientific_configuration"):
        raise ContractError("writing handoff requires method_identity.scientific_configuration")

    experiment_state = load_json_object(experiment_state_path)
    for label, observed, expected in (
        ("experiment state schema", experiment_state.get("schema_version"), "research-experiment/state-v1"),
        ("experiment state id", experiment_state.get("experiment_id"), experiment_id),
        ("experiment state plan revision", experiment_state.get("plan_revision"), plan_revision),
        ("experiment state idea id", experiment_state.get("idea_id"), idea_id),
        ("experiment state idea revision", experiment_state.get("idea_revision"), idea_revision),
        ("experiment state stage", experiment_state.get("stage"), "paper-ready"),
    ):
        _require_match(label, observed, expected)

    canonical_artifacts = {
        "experiment_verification": experiment_dir / "verification_report.json",
        "run_index": experiment_dir / "analysis" / "run_index.csv",
        "metric_summary": experiment_dir / "analysis" / "metric_summary.csv",
    }
    for name, canonical in canonical_artifacts.items():
        _require_match(f"canonical {name} path", artifact_paths[name], canonical.resolve())

    verification = load_json_object(artifact_paths["experiment_verification"])
    if verification.get("passed") is not True:
        raise ContractError("experiment_verification must record passed: true")
    for label, observed, expected in (
        ("verification admission mode", verification.get("admission_mode"), "formal"),
        ("verification schema", verification.get("schema_version"), STRICT_VERIFICATION_SCHEMA),
        ("verification plan schema", verification.get("plan_schema_version"), STRICT_PLAN_SCHEMA),
        ("verification experiment id", verification.get("experiment_id"), experiment_id),
        ("verification plan revision", verification.get("plan_revision"), plan_revision),
        ("verification idea id", verification.get("idea_id"), idea_id),
        ("verification idea revision", verification.get("idea_revision"), idea_revision),
        ("verification stage", verification.get("stage"), "paper-ready"),
    ):
        _require_match(label, observed, expected)
    _require_match("verification method identity", verification.get("method_identity"), method_identity)
    blockers = verification.get("blockers")
    if blockers != []:
        raise ContractError("paper-ready verification blockers must be empty")
    verification_checks = verification.get("checks")
    if not isinstance(verification_checks, list) or not verification_checks:
        raise ContractError("paper-ready verification requires non-empty checks")
    if any(not isinstance(item, dict) or item.get("passed") is not True for item in verification_checks):
        raise ContractError("paper-ready verification contains a failed or malformed check")
    _verify_evidence_closure(experiment_dir, plan, verification)
    if contract_hash is not None:
        _require_match("verification idea contract SHA-256", verification.get("idea_contract_sha256"), contract_hash)
    if plan_hash is not None:
        _require_match("verification experiment plan SHA-256", verification.get("experiment_plan_sha256"), plan_hash)


def validate_handoff(root: Path, handoff_path: Path) -> list[str]:
    handoff = load_json_object(handoff_path)
    unknown = sorted(set(handoff) - ROOT_FIELDS)
    if unknown:
        raise ContractError("research_handoff.json contains unknown fields: " + ", ".join(unknown))
    schema_version = handoff.get("schema_version")
    if schema_version not in {LEGACY_SCHEMA_VERSION, SHARED_SCHEMA_VERSION}:
        raise ContractError(
            "research_handoff.json schema_version must be one of "
            f"{LEGACY_SCHEMA_VERSION}, {SHARED_SCHEMA_VERSION}"
        )
    if schema_version == SHARED_SCHEMA_VERSION:
        _validate_v2_identity_fields(handoff)
    for field in ("research_question", "paper_type", "target_venue"):
        if not isinstance(handoff.get(field), str) or not str(handoff[field]).strip():
            raise ContractError(f"research_handoff.json requires a non-empty string field: {field}")
    quantitative = handoff.get("quantitative")
    if not isinstance(quantitative, bool):
        raise ContractError("research_handoff.json quantitative must be a boolean")
    blockers = handoff.get("blockers")
    if not isinstance(blockers, list) or any(not isinstance(item, str) or not item for item in blockers):
        raise ContractError("research_handoff.json blockers must be a list of non-empty strings")
    artifacts = handoff.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ContractError("research_handoff.json artifacts must be an object")
    unknown_artifacts = sorted(set(artifacts) - ARTIFACT_FIELDS)
    if unknown_artifacts:
        raise ContractError(
            "research_handoff.json artifacts contains unknown fields: " + ", ".join(unknown_artifacts)
        )
    required = set(BASE_ARTIFACTS)
    if quantitative:
        required.update({"experiment_inventory", "numeric_evidence"})
    shared_state = root / "research_state.json"
    if shared_state.is_file():
        required.update({"experiment_verification", "run_index", "metric_summary"})
    missing = sorted(required - set(artifacts))
    if missing:
        raise ContractError("research_handoff.json is missing required artifacts: " + ", ".join(missing))

    paths = {name: _artifact_path(root, name, raw) for name, raw in artifacts.items()}
    for name, path in paths.items():
        if path.suffix.lower() in {".md", ".txt", ".json", ".csv", ".tsv", ".yaml", ".yml"}:
            read_utf8(path)
    if "numeric_evidence" in paths:
        load_registry(root, paths["numeric_evidence"])
    if shared_state.is_file():
        _validate_shared_state(root, handoff, paths)
    elif "experiment_verification" in paths:
        verification = load_json_object(paths["experiment_verification"])
        if verification.get("passed") is not True:
            raise ContractError("experiment_verification must record passed: true")
    return list(blockers)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", type=Path)
    parser.add_argument("--handoff", default="research_handoff.json", help="Handoff path relative to project")
    parser.add_argument(
        "--require-unblocked", action="store_true",
        help="Fail when the handoff declares blockers instead of only reporting them",
    )
    args = parser.parse_args()
    root = args.project_path.resolve()
    if not root.is_dir():
        print(f"Project directory does not exist: {root}", file=sys.stderr)
        return 2
    try:
        blockers = validate_handoff(root, root / args.handoff)
    except ContractError as exc:
        print(f"Research handoff check failed: {exc}", file=sys.stderr)
        return 2
    if blockers:
        print("Research handoff is structurally valid with declared blockers:")
        for blocker in blockers:
            print(f"  - {blocker}")
        if args.require_unblocked:
            return 1
    else:
        print("Research handoff check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
