#!/usr/bin/env python3
"""Validate the evidence, frontier, motivation, and maturity of a problem card."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


MATURITY = {
    "problem-seed": 0,
    "evidence-backed": 1,
    "bottleneck-framed": 2,
    "solution-ready": 3,
}
MOTIVATION_STATUS = {
    "unknown",
    "distinctive-hypothesis",
    "evidence-backed",
    "contested",
}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def find_schema_path(start: Path | None = None) -> Path:
    """Find the shared schema in either a repository or an installed skill tree."""
    origin = (start or Path(__file__)).resolve()
    for ancestor in origin.parents:
        candidate = ancestor / "schemas" / "problem-card.schema.json"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "cannot find schemas/problem-card.schema.json in any script ancestor"
    )


def schema_failures(
    card: dict[str, Any], schema_path: Path | None = None
) -> tuple[list[str], Path]:
    resolved_schema = (schema_path or find_schema_path()).resolve()
    schema = json.loads(resolved_schema.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures: list[str] = []
    for error in sorted(validator.iter_errors(card), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        failures.append(f"schema:{location}: {error.message}")
    return failures, resolved_schema


def iso_date(value: Any, field: str, failures: list[str]) -> date | None:
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        failures.append(f"{field} must use ISO date format YYYY-MM-DD")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        failures.append(f"{field} must be a valid calendar date")
        return None


def validate_semantics(card: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if card.get("schema_version") != "research-problem/v1":
        failures.append("schema_version must be research-problem/v1")
    if not nonempty(card.get("problem_id")):
        failures.append("problem_id is required")
    revision = card.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        failures.append("revision must be a positive integer")
    maturity = card.get("maturity")
    if maturity not in MATURITY:
        failures.append(f"maturity must be one of {sorted(MATURITY)}")
        maturity_level = -1
    else:
        maturity_level = MATURITY[maturity]
    if not nonempty(card.get("problem_statement")):
        failures.append("problem_statement is required")

    frontier = mapping(card.get("frontier_context"))
    for field in ("coverage_end", "recent_window_start", "why_unresolved_now"):
        if not nonempty(frontier.get(field)):
            failures.append(f"frontier_context.{field} is required")
    coverage_end = iso_date(
        frontier.get("coverage_end"), "frontier_context.coverage_end", failures
    )
    recent_window_start = iso_date(
        frontier.get("recent_window_start"),
        "frontier_context.recent_window_start",
        failures,
    )
    if coverage_end and coverage_end > date.today():
        failures.append("frontier_context.coverage_end cannot be later than today")
    if coverage_end and recent_window_start and recent_window_start > coverage_end:
        failures.append(
            "frontier_context.recent_window_start cannot be later than coverage_end"
        )

    recent_sources = frontier.get("recent_sources")
    if not isinstance(recent_sources, list):
        recent_sources = []
    for index, source in enumerate(recent_sources, 1):
        if not isinstance(source, dict):
            continue
        published_at = iso_date(
            source.get("published_at"),
            f"frontier_context.recent_sources[{index}].published_at",
            failures,
        )
        if published_at and recent_window_start and published_at < recent_window_start:
            failures.append(
                f"frontier_context.recent_sources[{index}].published_at is before "
                "recent_window_start"
            )
        if published_at and coverage_end and published_at > coverage_end:
            failures.append(
                f"frontier_context.recent_sources[{index}].published_at is later than "
                "coverage_end"
            )

    active_signal = frontier.get("active_research_signal")
    if active_signal not in {
        "converging",
        "newly-exposed",
        "persistent",
        "contested",
        "weak",
    }:
        failures.append("frontier_context.active_research_signal is invalid")
    fallback_reason = frontier.get("recent_source_fallback_reason")
    if not recent_sources:
        if not nonempty(fallback_reason):
            failures.append(
                "empty frontier_context.recent_sources requires "
                "recent_source_fallback_reason"
            )
        if active_signal in {"converging", "newly-exposed"}:
            failures.append(
                "without recent sources, active_research_signal cannot be "
                "converging or newly-exposed"
            )

    observed = mapping(card.get("observed_failure"))
    if not nonempty(observed.get("phenomenon")):
        failures.append("observed_failure.phenomenon is required")

    evidence = mapping(card.get("evidence"))
    if maturity_level >= 1:
        if not nonempty_list(evidence.get("supporting_sources")):
            failures.append("evidence-backed problems require supporting_sources")
        if evidence.get("evidence_depth") in {None, "metadata"}:
            failures.append("evidence-backed problems require evidence deeper than metadata")

    bottlenecks = card.get("bottleneck_hypotheses")
    if maturity_level >= 2:
        if not nonempty_list(bottlenecks):
            failures.append("bottleneck-framed problems require bottleneck_hypotheses")
        else:
            for index, item in enumerate(bottlenecks, 1):
                item = mapping(item)
                for field in (
                    "hypothesis",
                    "strongest_competing_explanation",
                    "discriminating_observation",
                ):
                    if not nonempty(item.get(field)):
                        failures.append(f"bottleneck_hypotheses[{index}].{field} is required")
                if not nonempty_list(item.get("supporting_evidence")):
                    failures.append(
                        f"bottleneck_hypotheses[{index}].supporting_evidence is required"
                    )

    motivation = mapping(card.get("motivation_insight"))
    status = motivation.get("status")
    if status not in MOTIVATION_STATUS:
        failures.append("motivation_insight.status is invalid")
    if maturity_level >= 3:
        for field in (
            "default_interpretation",
            "proposed_interpretation",
            "explanatory_advantage",
            "design_implication",
            "disconfirming_evidence",
        ):
            if not nonempty(motivation.get(field)):
                failures.append(f"solution-ready problems require motivation_insight.{field}")
        if status == "unknown":
            failures.append("solution-ready problems require a testable motivation status")

        value = mapping(card.get("research_value"))
        for field in (
            "scientific",
            "practical",
            "community",
            "why_now",
            "value_without_sota_gain",
            "disconfirming_evidence",
        ):
            if not nonempty(value.get(field)):
                failures.append(f"solution-ready problems require research_value.{field}")

        tractability = mapping(card.get("tractability"))
        for field in ("observable", "measurable"):
            if not nonempty(tractability.get(field)):
                failures.append(f"solution-ready problems require tractability.{field}")

    if not nonempty(card.get("next_problem_check")):
        failures.append("next_problem_check is required")
    return failures


def validate(
    card: dict[str, Any], schema_path: Path | None = None
) -> tuple[list[str], Path]:
    structural, resolved_schema = schema_failures(card, schema_path)
    semantic = validate_semantics(card)
    return structural + semantic, resolved_schema


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem_card", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--schema", type=Path)
    args = parser.parse_args()
    resolved_schema: Path | None = None
    try:
        card = yaml.safe_load(args.problem_card.read_text(encoding="utf-8"))
        if not isinstance(card, dict):
            raise ValueError("problem card must be a YAML mapping")
        failures, resolved_schema = validate(card, args.schema)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        failures = [f"{type(exc).__name__}: {exc}"]
    report = {
        "schema_version": "research-problem/check-v1",
        "passed": not failures,
        "problem_schema": str(resolved_schema) if resolved_schema else None,
        "failures": failures,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
