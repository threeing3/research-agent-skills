from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "check_idea_lineage.py"
SPEC = importlib.util.spec_from_file_location("check_idea_lineage", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def contract() -> dict:
    payload = {
        "schema_version": "research-idea/v4",
        "idea_id": "idea-1",
        "revision": 1,
        "status": "experiment-ready",
        "lifecycle": {
            "validity": "active",
            "current_pool_status": "experiment-ready",
            "invalidated_at": None,
            "invalidated_by_event_id": None,
            "invalidation_reason": None,
            "superseded_by_revision": None,
        },
        "lineage": {
            "family_id": "family-1",
            "relation_to_family": "new-family",
            "parent_idea_id": None,
            "parent_revision": None,
            "delta_from_parent": {
                "causal_axes_changed": [],
                "unchanged_axes": [],
                "new_discriminating_prediction": "",
            },
            "inherited_failures": [],
        },
        "problem_signature": {
            "task": "VideoQA",
            "documented_failure": "search wastes evidence calls",
            "target_variable": "action value",
            "operating_setting": "fixed query budget",
        },
        "mechanism_signature": {
            "state": "answer belief",
            "observation": "queried clip feature",
            "action": "temporal query",
            "learning_signal": "answer improvement",
            "supervision_source": "paired replay",
            "causal_operator": "controlled contrast",
            "intervention": "matched evidence substitution",
            "claimed_capability": "efficient evidence search",
        },
        "evaluation_signature": {
            "unit_of_analysis": "video-question",
            "dataset_access": ["fixture"],
            "primary_outcome": "fixed-budget accuracy",
            "required_counterfactual": "matched alternative action",
            "strongest_simple_baseline": "temporal distance",
        },
        "anti_reskin_gate": {
            "status": "pass",
            "review_context_policy": "cold",
            "independence_valid": True,
            "mechanism_signature_sha256": "",
            "unresolved_failure_ids": [],
        },
    }
    payload["anti_reskin_gate"]["mechanism_signature_sha256"] = MODULE.signature(payload)
    return payload


def run(payload: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "idea.yaml"
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(path)], text=True, capture_output=True, check=False)


class IdeaLineageTests(unittest.TestCase):
    def test_new_family_passes_and_emits_signature(self) -> None:
        result = run(contract())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"passed": true', result.stdout)
        self.assertIn("mechanism_signature_sha256", result.stdout)

    def test_unresolved_failure_blocks(self) -> None:
        payload = contract()
        payload["lineage"]["inherited_failures"] = [
            {"failure_id": "F1", "status": "unresolved"}
        ]
        result = run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved inherited failures", result.stdout)

    def test_cosmetic_variant_blocks(self) -> None:
        payload = contract()
        payload["lineage"]["relation_to_family"] = "cosmetic-variant"
        result = run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("cosmetic-variant cannot pass", result.stdout)

    def test_invalidated_contract_blocks_handoff(self) -> None:
        payload = contract()
        payload["lifecycle"]["validity"] = "invalidated"
        payload["lifecycle"]["current_pool_status"] = "rejected"
        result = run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("only an active contract can be handed off", result.stdout)

    def test_staged_contract_with_supported_target_novelty_passes(self) -> None:
        payload = contract()
        payload.update(
            {
                "contract_profile": "staged-novelty/v1",
                "target_domain_boundary": {
                    "task": "VideoQA",
                    "problem_setting": "long-video evidence reasoning",
                    "key_constraints": ["long context"],
                },
                "novelty_review": {
                    "status": "supported",
                    "coverage_end": "2026-08-11",
                    "recall_confidence": "medium",
                },
                "decision": {"selected_by_user": True},
            }
        )
        result = run(payload)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_staged_contract_with_uncertain_target_novelty_blocks(self) -> None:
        payload = contract()
        payload.update(
            {
                "contract_profile": "staged-novelty/v1",
                "target_domain_boundary": {
                    "task": "VideoQA",
                    "problem_setting": "long-video evidence reasoning",
                },
                "novelty_review": {
                    "status": "uncertain",
                    "coverage_end": "2026-08-11",
                    "recall_confidence": "low",
                },
                "decision": {"selected_by_user": True},
            }
        )
        result = run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("target-domain novelty status supported", result.stdout)


if __name__ == "__main__":
    unittest.main()
