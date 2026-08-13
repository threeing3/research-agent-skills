from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "check_idea_state_consistency.py"


def write_fixture(
    root: Path,
    *,
    pool_status: str,
    lifecycle: dict | None,
    include_contract: bool = True,
) -> None:
    ideas = root / "research_state" / "ideas"
    ideas.mkdir(parents=True)
    (ideas / "idea_pool.json").write_text(
        json.dumps(
            {
                "schema_version": "research-idea-pool/v1",
                "updated_at": "2026-08-11T00:00:00+08:00",
                "ideas": [{"id": "idea-1", "status": pool_status}],
            }
        ),
        encoding="utf-8",
    )
    if include_contract:
        contract_dir = ideas / "idea-1"
        contract_dir.mkdir()
        contract = {
            "schema_version": "research-idea/v4",
            "idea_id": "idea-1",
            "revision": 1,
            "status": "experiment-ready",
        }
        if lifecycle is not None:
            contract["lifecycle"] = lifecycle
        (contract_dir / "idea_contract.yaml").write_text(
            yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
        )


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root)],
        text=True,
        capture_output=True,
        check=False,
    )


class IdeaStateConsistencyTests(unittest.TestCase):
    def test_active_contract_matches_ready_pool(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(
                root,
                pool_status="experiment-ready",
                lifecycle={
                    "validity": "active",
                    "current_pool_status": "experiment-ready",
                    "invalidation_reason": None,
                    "superseded_by_revision": None,
                },
            )
            result = run(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('"passed": true', result.stdout)
            report = json.loads(result.stdout)
            self.assertEqual(
                report["schema_version"], "research-idea/state-consistency-v2"
            )
            self.assertNotIn("pool_sha256", report)
            self.assertEqual(report["records"][0]["contract_revision"], 1)
            self.assertNotIn("contract_sha256", report["records"][0])

    def test_legacy_ready_contract_conflicts_with_rejected_pool(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, pool_status="rejected", lifecycle=None)
            result = run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("record invalidation or supersession", result.stdout)

    def test_legacy_ready_variant_conflicts_with_rejected_pool(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(root, pool_status="rejected", lifecycle=None)
            contract_path = (
                root
                / "research_state"
                / "ideas"
                / "idea-1"
                / "idea_contract.yaml"
            )
            contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
            contract["status"] = "experiment-ready-after-cpu-geometry"
            contract_path.write_text(
                yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
            )
            result = run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("record invalidation or supersession", result.stdout)

    def test_invalidated_contract_matches_rejected_pool(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(
                root,
                pool_status="rejected",
                lifecycle={
                    "validity": "invalidated",
                    "current_pool_status": "rejected",
                    "invalidation_reason": "verified pilot contradicted the mechanism",
                    "superseded_by_revision": None,
                },
            )
            result = run(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ready_pool_requires_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(
                root,
                pool_status="experiment-ready",
                lifecycle=None,
                include_contract=False,
            )
            result = run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("has no idea_contract.yaml", result.stdout)

    def test_malformed_contract_is_reported_without_aborting_scan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_fixture(
                root,
                pool_status="rejected",
                lifecycle=None,
            )
            contract_path = (
                root
                / "research_state"
                / "ideas"
                / "idea-1"
                / "idea_contract.yaml"
            )
            contract_path.write_text(
                "idea_id: idea-1\ntitle: broken: unquoted\n", encoding="utf-8"
            )
            result = run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("cannot parse contract idea-1", result.stdout)
            self.assertIn('"records"', result.stdout)


if __name__ == "__main__":
    unittest.main()
