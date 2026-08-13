from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "check_validation_alignment.py"


def alignment() -> dict:
    return {
        "schema_version": "research-idea/validation-alignment-v3",
        "alignment_id": "align-1",
        "idea_id": "idea-1",
        "idea_revision": 2,
        "implementation_revision": 1,
        "maturity": "validation-ready",
        "idea_type": "baseline-modification",
        "title": "Question-conditioned memory",
        "parent_problem": {
            "problem_id": "problem-1",
            "problem_revision": 1,
            "problem_card": "research_state/problems/problem-1/problem_card.yaml",
            "problem_maturity": "solution-ready",
            "motivation_status": "evidence-backed",
        },
        "problem_hypothesis": "The baseline forgets early evidence.",
        "mechanism_hypothesis": "Selective memory preserves relevant early evidence.",
        "motivation_design": {
            "observed_failure": "early visual evidence is lost as context grows",
            "bottleneck_hypothesis": "uniform compression erases question-relevant early evidence",
            "distinctive_motivation_insight": "the bottleneck is selective retention, not context capacity alone",
            "research_value": "separates memory quality from raw context length",
            "required_behavior_change": "retain question-relevant early evidence",
            "design_principle": "condition retention on the question before compression",
            "module_operation": "select and preserve question-relevant tokens",
            "implementation_location": "between video encoder and answer decoder",
            "why_existing_components_are_insufficient": "uniform compression cannot protect sparse early evidence",
        },
        "target_domain_boundary": {
            "task": "long-video question answering",
            "problem_setting": "questions requiring early evidence",
            "key_constraints": ["long context"],
        },
        "baseline_change": {
            "baseline_id": "baseline-repo@abc123",
            "selection_reason": "closest reproducible baseline",
            "target_failure": "early evidence loss",
            "operation": "add",
            "location": "between video encoder and answer decoder",
            "before": "decoder receives compressed video tokens",
            "after": "decoder also receives selected memory tokens",
            "reused_parts": ["video encoder"],
            "redesigned_parts": ["memory selector"],
            "expected_resource_delta": "small",
            "required_ablations": ["remove memory", "shuffle memory"],
        },
        "lightweight_collision_check": {
            "status": "uncertain",
            "checked_at": "2026-08-11T00:00:00Z",
            "target_domain_queries": ["long video selective memory"],
            "closest_target_work": [],
            "note": "No formal novelty verdict has been made.",
        },
        "validation": {
            "applicability": "applicable",
            "applicability_reason": "a controlled early-evidence subset exists",
            "question": "Does the module preserve early evidence?",
            "falsifiable_prediction": "accuracy rises only on early-evidence cases",
            "strongest_alternative": "extra capacity causes any gain",
            "activation_evidence": ["memory reads early tokens and affects decoder logits"],
            "intervention_evidence": ["shuffling memory removes the targeted gain"],
            "quantitative_evidence": ["aggregate and early-evidence subset accuracy"],
            "qualitative_evidence": ["paired baseline/full/ablation cases by failure category"],
            "qualitative_selection_protocol": {
                "frozen_before_results": True,
                "categories": ["early-evidence", "distractor-heavy"],
                "required_outcomes": ["success", "failure", "unchanged-or-regression"],
                "sampling_rule": "sample every category before inspecting method success",
                "comparison_views": ["baseline", "full-method", "ablation"],
            },
            "outcome_interpretation": {
                "supportive": "activation passes and targeted gain appears",
                "negative": "activation passes but targeted gain does not appear",
                "inconclusive": "activation or measurement cannot be established",
            },
            "stop_conditions": ["stop if the module never affects decoder logits"],
        },
        "budget": {"max_direct_cost_cny": 100, "max_wall_time_hours": 24},
        "user_alignment": {
            "status": "approved",
            "approved_at": "2026-08-11T00:01:00Z",
            "approved_scope": "one low-cost validation round",
            "approved_max_direct_cost_cny": 100,
            "approved_max_wall_time_hours": 24,
            "resource_override_approved": False,
        },
    }


def write_fixture(root: Path, value: dict | None = None) -> tuple[Path, Path]:
    alignment_path = root / "alignment.yaml"
    alignment_value = value or alignment()
    alignment_path.write_text(
        yaml.safe_dump(alignment_value, sort_keys=False), encoding="utf-8"
    )
    card_path = root / alignment_value.get("parent_problem", {}).get(
        "problem_card", "research_state/problems/problem-1/problem_card.yaml"
    )
    card_path.parent.mkdir(parents=True, exist_ok=True)
    parent = alignment_value.get("parent_problem", {})
    card_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": "research-problem/v1",
                "problem_id": parent.get("problem_id", "problem-1"),
                "revision": parent.get("problem_revision", 1),
                "maturity": parent.get("problem_maturity", "solution-ready"),
                "status": "open",
                "motivation_insight": {"status": parent.get("motivation_status", "evidence-backed")},
            }
        ),
        encoding="utf-8",
    )
    plan = {
        "schema_version": "research-experiment/plan-v3",
        "admission_mode": "exploratory-validation",
        "idea_id": alignment_value["idea_id"],
        "idea_revision": alignment_value["idea_revision"],
        "implementation_revision": alignment_value["implementation_revision"],
        "validation_alignment": {
            "artifact": "alignment.yaml",
            "alignment_id": alignment_value["alignment_id"],
            "idea_revision": alignment_value["idea_revision"],
            "implementation_revision": alignment_value["implementation_revision"],
        },
        "budget": dict(alignment_value["budget"]),
        "stop_conditions": list(alignment_value["validation"]["stop_conditions"]),
    }
    if "parent_problem" in alignment_value:
        plan["validation_alignment"]["parent_problem"] = dict(alignment_value["parent_problem"])
    plan_path = root / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    return alignment_path, plan_path


def run(alignment_path: Path, plan_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--alignment",
            str(alignment_path),
            "--plan",
            str(plan_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


class ValidationAlignmentTests(unittest.TestCase):
    def test_approved_bounded_alignment_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run(*write_fixture(Path(directory)))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("VALIDATION ALIGNMENT: PASS", result.stdout)

    def test_missing_user_approval_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["user_alignment"]["status"] = "pending"
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("user-alignment", result.stdout)

    def test_known_collision_blocks_unchanged_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["lightweight_collision_check"]["status"] = "collision-needs-revision"
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("lightweight-collision", result.stdout)

    def test_realization_evidence_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["validation"]["activation_evidence"] = []
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("validation:activation_evidence", result.stdout)

    def test_problem_led_derivation_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["motivation_design"]["distinctive_motivation_insight"] = ""
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("motivation-design:distinctive_motivation_insight", result.stdout)

    def test_quantitative_and_qualitative_evidence_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["validation"]["qualitative_evidence"] = []
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("validation:qualitative_evidence", result.stdout)

    def test_budget_above_standing_envelope_requires_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["budget"] = {"max_direct_cost_cny": 120, "max_wall_time_hours": 30}
            value["user_alignment"]["approved_max_direct_cost_cny"] = 120
            value["user_alignment"]["approved_max_wall_time_hours"] = 30
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("resource-override", result.stdout)

    def test_explicit_resource_override_allows_larger_round(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["budget"] = {"max_direct_cost_cny": 120, "max_wall_time_hours": 30}
            value["user_alignment"]["approved_max_direct_cost_cny"] = 120
            value["user_alignment"]["approved_max_wall_time_hours"] = 30
            value["user_alignment"]["resource_override_approved"] = True
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_alignment_revision_mismatch_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            alignment_path, plan_path = write_fixture(Path(directory))
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["validation_alignment"]["implementation_revision"] = 99
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = run(alignment_path, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("alignment-implementation-revision", result.stdout)

    def test_empty_target_boundary_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["target_domain_boundary"]["key_constraints"] = []
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("target-domain-boundary", result.stdout)

    def test_plan_cannot_silently_change_approved_stop_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            alignment_path, plan_path = write_fixture(Path(directory))
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["stop_conditions"] = ["keep running regardless of activation"]
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = run(alignment_path, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("plan-stop-conditions", result.stdout)

    def test_baseline_change_requires_an_ablation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["baseline_change"]["required_ablations"] = []
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("baseline-required-ablations", result.stdout)

    def test_alignment_artifact_must_match_checked_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment_path, plan_path = write_fixture(root)
            other = root / "other.yaml"
            other.write_text(alignment_path.read_text(encoding="utf-8"), encoding="utf-8")
            result = run(other, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("alignment-artifact-binding", result.stdout)

    def test_problem_card_identity_mismatch_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment_path, plan_path = write_fixture(root)
            card_path = root / "research_state/problems/problem-1/problem_card.yaml"
            card = yaml.safe_load(card_path.read_text(encoding="utf-8"))
            card["revision"] = 99
            card_path.write_text(yaml.safe_dump(card), encoding="utf-8")
            result = run(alignment_path, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("parent-problem:card-identity", result.stdout)

    def test_closed_problem_card_blocks_new_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alignment_path, plan_path = write_fixture(root)
            card_path = root / "research_state/problems/problem-1/problem_card.yaml"
            card = yaml.safe_load(card_path.read_text(encoding="utf-8"))
            card["status"] = "closed"
            card_path.write_text(yaml.safe_dump(card), encoding="utf-8")
            result = run(alignment_path, plan_path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("parent-problem:card-identity", result.stdout)

    def test_legacy_v1_is_readable_but_launch_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            value = alignment()
            value["schema_version"] = "research-idea/validation-alignment-v1"
            value.pop("parent_problem")
            value.pop("motivation_design")
            value["validation"].pop("quantitative_evidence")
            value["validation"].pop("qualitative_evidence")
            value["validation"].pop("qualitative_selection_protocol")
            result = run(*write_fixture(Path(directory), value))
            self.assertEqual(result.returncode, 1)
            self.assertIn("launch-contract-version", result.stdout)


if __name__ == "__main__":
    unittest.main()
