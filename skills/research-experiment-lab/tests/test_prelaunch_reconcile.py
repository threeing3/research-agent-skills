from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "prelaunch_reconcile.py"
IDEA_STATE_SCRIPT = (
    SKILL.parent
    / "research-idea-lab"
    / "scripts"
    / "check_idea_state_consistency.py"
)
SPEC = importlib.util.spec_from_file_location("prelaunch_reconcile", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def idea_contract(validity: str = "active", pool_status: str = "experiment-ready") -> dict:
    return {
        "schema_version": "research-idea/v4",
        "idea_id": "idea-1",
        "revision": 2,
        "status": "experiment-ready",
        "lifecycle": {
            "validity": validity,
            "current_pool_status": pool_status,
            "invalidation_reason": "pilot contradicted the mechanism" if validity == "invalidated" else None,
            "superseded_by_revision": 3 if validity == "superseded" else None,
        },
        "decision": {"selected_by_user": True},
        "lineage": {
            "family_id": "family-1",
            "relation_to_family": "same-family-material-revision",
            "inherited_failures": [{"failure_id": "F1", "status": "resolved"}],
        },
        "problem_signature": {"task": "VideoQA"},
        "mechanism_signature": {"action": "temporal query", "intervention": "matched substitution"},
        "evaluation_signature": {"unit_of_analysis": "video-question"},
        "anti_reskin_gate": {"status": "pass", "independence_valid": True},
    }


def write_fixture(
    root: Path,
    available: int = 64,
    cyclic: bool = False,
    *,
    validity: str = "active",
    pool_status: str = "experiment-ready",
    include_lifecycle: bool = True,
) -> tuple[Path, Path]:
    ideas_root = root / "research_state" / "ideas"
    contract_path = ideas_root / "idea-1" / "idea_contract.yaml"
    contract_path.parent.mkdir(parents=True)
    pool_path = ideas_root / "idea_pool.json"
    pool_path.write_text(
        json.dumps(
            {
                "schema_version": "research-idea-pool/v1",
                "updated_at": "fixture",
                "ideas": [{"id": "idea-1", "status": pool_status}],
            }
        ),
        encoding="utf-8",
    )
    contract = idea_contract(validity=validity, pool_status=pool_status)
    if not include_lifecycle:
        contract.pop("lifecycle")
    contract["anti_reskin_gate"]["review_context_policy"] = "cold"
    contract["anti_reskin_gate"]["mechanism_signature_sha256"] = MODULE.mechanism_sha256(contract)
    contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
    contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
    tasks = [
        {"task_id": "smoke", "depends_on": ["train"] if cyclic else []},
        {"task_id": "train", "depends_on": ["smoke"]},
    ]
    lineage_report = {
        "passed": True,
        "idea_id": "idea-1",
        "idea_revision": 2,
        "mechanism_signature_sha256": MODULE.mechanism_sha256(contract),
    }
    lineage_report_path = root / "lineage_check.json"
    lineage_report_path.write_text(json.dumps(lineage_report), encoding="utf-8")
    consistency_report = {
        "schema_version": "research-idea/state-consistency-v2",
        "passed": True,
        "pool_sha256": hashlib.sha256(pool_path.read_bytes()).hexdigest(),
        "records": [
            {
                "idea_id": "idea-1",
                "pool_status": pool_status,
                "contract_status": "experiment-ready",
                "contract_revision": 2,
                "contract_sha256": contract_hash,
                "lifecycle_validity": validity if include_lifecycle else None,
                "lifecycle_pool_status": pool_status if include_lifecycle else None,
            }
        ],
    }
    consistency_path = ideas_root / "idea_state_consistency.json"
    consistency_path.write_text(json.dumps(consistency_report), encoding="utf-8")
    plan = {
        "schema_version": "research-experiment/plan-v2",
        "idea_id": "idea-1",
        "idea_revision": 2,
        "idea_contract_sha256": contract_hash,
        "mechanism_family_id": "family-1",
        "mechanism_signature_sha256": MODULE.mechanism_sha256(contract),
        "inherited_failure_ids": ["F1"],
        "prelaunch": {
            "required_gates": sorted(MODULE.REQUIRED_GATES),
            "lineage_check_report": "lineage_check.json",
            "idea_state_consistency_report": "research_state/ideas/idea_state_consistency.json",
            "constraints": [
                {
                    "constraint_id": "video-count",
                    "available": available,
                    "op": ">=",
                    "required": 64,
                    "evidence": "manifest.json",
                    "resolution": "expand replay",
                    "resolution_authorized": False,
                }
            ],
        },
        "tasks": tasks,
    }
    plan_path = root / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    return contract_path, plan_path


def run(contract_path: Path, plan_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--idea-contract", str(contract_path), "--plan", str(plan_path)],
        text=True,
        capture_output=True,
        check=False,
    )


class PrelaunchReconcileTests(unittest.TestCase):
    def test_satisfiable_plan_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(*write_fixture(Path(directory)))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PRELAUNCH RECONCILIATION: PASS", result.stdout)

    def test_generated_idea_state_report_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path, plan_path = write_fixture(root)
            report_path = root / "research_state" / "ideas" / "idea_state_consistency.json"
            consistency = subprocess.run(
                [
                    sys.executable,
                    str(IDEA_STATE_SCRIPT),
                    str(root),
                    "--report",
                    str(report_path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                consistency.returncode, 0, consistency.stdout + consistency.stderr
            )
            result = run(contract_path, plan_path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unattainable_sample_gate_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(*write_fixture(Path(directory), available=16))
            self.assertEqual(result.returncode, 1)
            self.assertIn("constraint:video-count", result.stdout)
            self.assertIn("PRELAUNCH RECONCILIATION: FAIL", result.stdout)

    def test_cyclic_task_graph_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(*write_fixture(Path(directory), cyclic=True))
            self.assertEqual(result.returncode, 1)
            self.assertIn("contains a cycle", result.stdout)

    def test_invalidated_contract_blocks_even_when_consistency_report_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(
                *write_fixture(
                    Path(directory), validity="invalidated", pool_status="rejected"
                )
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("idea-lifecycle-active", result.stdout)
            self.assertIn("PRELAUNCH RECONCILIATION: FAIL", result.stdout)

    def test_superseded_contract_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(
                *write_fixture(
                    Path(directory), validity="superseded", pool_status="parked"
                )
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("validity='superseded'", result.stdout)

    def test_missing_lifecycle_blocks_new_experiment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(*write_fixture(Path(directory), include_lifecycle=False))
            self.assertEqual(result.returncode, 1)
            self.assertIn("idea-lifecycle-declared", result.stdout)

    def test_stale_consistency_contract_hash_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path, plan_path = write_fixture(root)
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            contract["title"] = "materially revised after consistency check"
            contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["idea_contract_sha256"] = hashlib.sha256(contract_path.read_bytes()).hexdigest()
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = run(contract_path, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("idea-state-consistency-report", result.stdout)
            self.assertIn("matching_records=1", result.stdout)

    def test_pool_change_after_consistency_check_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path, plan_path = write_fixture(root)
            pool_path = root / "research_state" / "ideas" / "idea_pool.json"
            pool = json.loads(pool_path.read_text(encoding="utf-8"))
            pool["ideas"][0]["status"] = "rejected"
            pool_path.write_text(json.dumps(pool), encoding="utf-8")
            result = run(contract_path, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("pool_hash_matches=False", result.stdout)


if __name__ == "__main__":
    unittest.main()
