#!/usr/bin/env python3
"""Check idea-pool status against idea-contract lifecycle metadata."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml


VALID_LIFECYCLE_STATES = {"active", "invalidated", "superseded"}


def is_experiment_ready(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("experiment-ready")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def resolve_state_root(path: Path) -> Path:
    resolved = path.resolve()
    if (resolved / "ideas" / "idea_pool.json").is_file():
        return resolved
    candidate = resolved / "research_state"
    if (candidate / "ideas" / "idea_pool.json").is_file():
        return candidate
    raise ValueError(
        f"cannot find research_state/ideas/idea_pool.json under {resolved}"
    )


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def validate(state_root: Path) -> dict[str, Any]:
    ideas_root = state_root / "ideas"
    pool_path = ideas_root / "idea_pool.json"
    pool_document = load_json(pool_path)
    pool_rows = pool_document.get("ideas")
    if not isinstance(pool_rows, list):
        raise ValueError("idea_pool.json field 'ideas' must be a list")

    failures: list[str] = []
    warnings: list[str] = []
    records: list[dict[str, Any]] = []
    pool: dict[str, dict[str, Any]] = {}

    for index, row in enumerate(pool_rows):
        if not isinstance(row, dict) or not row.get("id"):
            failures.append(f"idea_pool.ideas[{index}] requires a non-empty id")
            continue
        idea_id = str(row["id"])
        if idea_id in pool:
            failures.append(f"duplicate idea id in pool: {idea_id}")
            continue
        pool[idea_id] = row

    contracts_by_idea: dict[str, Path] = {}
    for contract_path in sorted(ideas_root.glob("*/idea_contract.yaml")):
        try:
            contract = load_yaml(contract_path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            fallback_id = contract_path.parent.name
            contracts_by_idea[fallback_id] = contract_path
            failures.append(
                f"cannot parse contract {fallback_id} at {contract_path}: {exc}"
            )
            records.append(
                {
                    "idea_id": fallback_id,
                    "pool_status": (pool.get(fallback_id) or {}).get("status"),
                    "contract_status": None,
                    "contract_revision": None,
                    "lifecycle_validity": None,
                    "lifecycle_pool_status": None,
                    "contract": str(contract_path.relative_to(state_root.parent)),
                    "parse_error": str(exc),
                }
            )
            continue
        idea_id = str(contract.get("idea_id") or contract_path.parent.name)
        if idea_id in contracts_by_idea:
            failures.append(
                f"multiple active-path contracts found for {idea_id}: "
                f"{contracts_by_idea[idea_id]} and {contract_path}"
            )
            continue
        contracts_by_idea[idea_id] = contract_path

        pool_row = pool.get(idea_id)
        pool_status = pool_row.get("status") if pool_row else None
        issued_status = contract.get("status")
        lifecycle = contract.get("lifecycle")
        validity: str | None = None
        lifecycle_pool_status: str | None = None

        if pool_row is None:
            failures.append(f"contract {idea_id} has no matching idea-pool entry")

        if lifecycle is None:
            if is_experiment_ready(issued_status) and not is_experiment_ready(pool_status):
                failures.append(
                    f"legacy contract {idea_id} remains experiment-ready while "
                    f"the idea pool says {pool_status!r}; record invalidation or supersession"
                )
            else:
                warnings.append(
                    f"contract {idea_id} has no lifecycle metadata; add it on the next "
                    "material revision or promotion"
                )
        elif not isinstance(lifecycle, dict):
            failures.append(f"contract {idea_id} lifecycle must be a mapping")
        else:
            validity_value = lifecycle.get("validity")
            validity = str(validity_value) if validity_value is not None else None
            lifecycle_pool_value = lifecycle.get("current_pool_status")
            lifecycle_pool_status = (
                str(lifecycle_pool_value) if lifecycle_pool_value is not None else None
            )

            if validity not in VALID_LIFECYCLE_STATES:
                failures.append(
                    f"contract {idea_id} lifecycle.validity must be one of "
                    f"{sorted(VALID_LIFECYCLE_STATES)}, found {validity!r}"
                )
            if lifecycle_pool_status != pool_status:
                failures.append(
                    f"contract {idea_id} lifecycle.current_pool_status "
                    f"{lifecycle_pool_status!r} does not match pool status {pool_status!r}"
                )

            if validity == "active":
                if not is_experiment_ready(issued_status):
                    failures.append(
                        f"active contract {idea_id} must have issued status experiment-ready"
                    )
                if not is_experiment_ready(pool_status):
                    failures.append(
                        f"active contract {idea_id} cannot be used while pool status is "
                        f"{pool_status!r}"
                    )
            elif validity in {"invalidated", "superseded"}:
                if is_experiment_ready(pool_status):
                    failures.append(
                        f"idea {idea_id} is experiment-ready in the pool but its current "
                        f"contract is {validity}"
                    )
                if validity == "invalidated" and not lifecycle.get("invalidation_reason"):
                    failures.append(
                        f"invalidated contract {idea_id} requires invalidation_reason"
                    )
                if validity == "superseded" and lifecycle.get(
                    "superseded_by_revision"
                ) in (None, ""):
                    failures.append(
                        f"superseded contract {idea_id} requires superseded_by_revision"
                    )

        records.append(
            {
                "idea_id": idea_id,
                "pool_status": pool_status,
                "contract_status": issued_status,
                "contract_revision": contract.get("revision"),
                "lifecycle_validity": validity,
                "lifecycle_pool_status": lifecycle_pool_status,
                "contract": str(contract_path.relative_to(state_root.parent)),
            }
        )

    for idea_id, row in sorted(pool.items()):
        if is_experiment_ready(row.get("status")) and idea_id not in contracts_by_idea:
            failures.append(
                f"idea {idea_id} is experiment-ready but has no idea_contract.yaml"
            )

    return {
        "schema_version": "research-idea/state-consistency-v2",
        "state_root": str(state_root),
        "pool": str(pool_path.relative_to(state_root.parent)),
        "pool_updated_at": pool_document.get("updated_at"),
        "passed": not failures,
        "counts": {
            "pool_ideas": len(pool),
            "contracts": len(contracts_by_idea),
            "failures": len(failures),
            "warnings": len(warnings),
        },
        "failures": failures,
        "warnings": warnings,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_or_state_root",
        type=Path,
        help="Project root or its research_state directory",
    )
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        state_root = resolve_state_root(args.project_or_state_root)
        report = validate(state_root)
        if args.report:
            atomic_json(args.report.resolve(), report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["passed"] else 1
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"check_idea_state_consistency failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
