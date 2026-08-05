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
SPEC = importlib.util.spec_from_file_location("prelaunch_reconcile", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def idea_contract() -> dict:
    return {
        "schema_version": "research-idea/v5",
        "idea_id": "idea-1",
        "revision": 2,
        "status": "experiment-ready",
        "decision": {"selected_by_user": True},
        "lineage": {
            "family_id": "family-1",
            "relation_to_family": "same-family-material-revision",
            "inherited_failures": [{"failure_id": "F1", "status": "resolved"}],
        },
        "problem_signature": {"task": "VideoQA"},
        "mechanism_signature": {"action": "temporal query", "intervention": "matched substitution"},
        "evaluation_signature": {"unit_of_analysis": "video-question"},
        "publication_case": {"status": "pass", "blockers": []},
        "anti_reskin_gate": {"status": "pass", "independence_valid": True},
    }


def write_fixture(root: Path, available: int = 64, cyclic: bool = False) -> tuple[Path, Path]:
    contract_path = root / "idea.yaml"
    contract = idea_contract()
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

    def test_unresolved_publication_case_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contract_path, plan_path = write_fixture(root)
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            contract["publication_case"]["status"] = "unresolved"
            contract_path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
            result = run(contract_path, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("publication-first-gate", result.stdout)


if __name__ == "__main__":
    unittest.main()
