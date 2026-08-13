from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
EXPERIMENT_SKILL = REPO / "skills" / "research-experiment-lab"
WRITING_SKILL = REPO / "skills" / "ai-research-writing-skill"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected JSON object: {path}")
    return value


@unittest.skipUnless(
    (REPO / "schemas" / "idea-contract.schema.json").is_file(),
    "shared-protocol schemas are available only in the monorepo checkout",
)
class SharedProtocolSchemaTests(unittest.TestCase):
    def test_idea_schema_tracks_v4_lifecycle(self) -> None:
        schema = load(REPO / "schemas" / "idea-contract.schema.json")
        properties = schema["properties"]
        self.assertIn("research-idea/v4", properties["schema_version"]["enum"])
        self.assertEqual(
            properties["lifecycle"]["properties"]["validity"]["enum"],
            ["active", "invalidated", "superseded"],
        )
        self.assertIn("problem-led/v1", properties["contract_profile"]["enum"])
        self.assertIn("problem_derivation", properties)

    def test_problem_card_tracks_frontier_motivation_and_value(self) -> None:
        schema = load(REPO / "schemas" / "problem-card.schema.json")
        properties = schema["properties"]
        self.assertEqual(properties["schema_version"]["const"], "research-problem/v1")
        for field in (
            "frontier_context",
            "observed_failure",
            "bottleneck_hypotheses",
            "motivation_insight",
            "research_value",
            "tractability",
            "solution_idea_ids",
        ):
            self.assertIn(field, schema["required"])
        self.assertIn("coverage_end", properties["frontier_context"]["required"])

    def test_experiment_schema_and_template_track_plan_v3(self) -> None:
        schema = load(REPO / "schemas" / "experiment-plan.schema.json")
        template = load(EXPERIMENT_SKILL / "assets" / "experiment_plan.json.template")
        self.assertIn(template["schema_version"], schema["properties"]["schema_version"]["enum"])
        self.assertEqual(template["schema_version"], "research-experiment/plan-v3")
        self.assertIn(
            "idea_state_consistency_report",
            schema["properties"]["prelaunch"]["required"],
        )
        self.assertIn("idea_state_consistency_report", template["prelaunch"])
        self.assertEqual(template["admission_mode"], "formal")
        self.assertIn("validation_alignment", schema["properties"])
        self.assertIn("method_identity", schema["required"])
        formal_rule = schema["allOf"][3]["then"]["properties"]["method_identity"]["properties"]
        self.assertEqual(formal_rule["method_tier"]["const"], "full")
        self.assertTrue(formal_rule["publication_eligible"]["const"])
        self.assertIn("validation_alignment_check_report", template["prelaunch"])
        self.assertIn("evidence_obligations", schema["allOf"][0]["then"]["required"])
        self.assertEqual(
            set(template["evidence_obligations"]),
            {"mechanism", "quantitative", "qualitative"},
        )

    def test_validation_alignment_schema_requires_user_and_realization_evidence(self) -> None:
        schema = load(REPO / "schemas" / "validation-alignment.schema.json")
        self.assertIn(
            "research-idea/validation-alignment-v2",
            schema["properties"]["schema_version"]["enum"],
        )
        self.assertIn(
            "research-idea/validation-alignment-v3",
            schema["properties"]["schema_version"]["enum"],
        )
        validation_required = schema["properties"]["validation"]["required"]
        self.assertIn("activation_evidence", validation_required)
        self.assertIn("intervention_evidence", validation_required)
        self.assertIn("user_alignment", schema["required"])
        v2_rule = schema["allOf"][0]["then"]
        self.assertIn("parent_problem", v2_rule["required"])
        self.assertIn("motivation_design", v2_rule["required"])
        self.assertIn(
            "qualitative_evidence",
            v2_rule["properties"]["validation"]["required"],
        )

    def test_literature_monitor_schema_has_action_signals(self) -> None:
        schema = load(REPO / "schemas" / "literature-monitor.schema.json")
        self.assertEqual(
            schema["properties"]["overall_signal"]["enum"],
            ["RELAX", "RESEARCH", "FOLLOW-UP"],
        )
        self.assertIn("target_domain_boundary", schema["required"])

    def test_claim_evidence_schema_tracks_overstatement_and_next_action(self) -> None:
        schema = load(REPO / "schemas" / "claim-evidence.schema.json")
        statuses = schema["properties"]["status"]["enum"]
        self.assertIn("overstated", statuses)
        self.assertIn("unclear", statuses)
        self.assertIn("required_evidence", schema["properties"])
        self.assertIn("next_action", schema["properties"])

    def test_verification_schema_tracks_emitted_v3_identity(self) -> None:
        schema = load(REPO / "schemas" / "verification-report.schema.json")
        self.assertIn(
            "research-experiment/experiment-verification-v3",
            schema["properties"]["schema_version"]["enum"],
        )
        self.assertIn("verified-diagnostic", schema["properties"]["stage"]["enum"])
        for field in (
            "experiment_id",
            "plan_revision",
            "idea_id",
            "idea_revision",
            "method_identity",
            "stage",
            "passed",
        ):
            self.assertIn(field, schema["required"])
        v3_required = schema["allOf"][0]["then"]["required"]
        self.assertIn("admission_mode", v3_required)
        self.assertIn("evidence_summary", v3_required)
        self.assertIn("evidence_results", v3_required)

    def test_research_state_schema_allows_real_phase_and_current_paths(self) -> None:
        schema = load(REPO / "schemas" / "research-state.schema.json")
        self.assertEqual(schema["properties"]["phase"]["type"], "string")
        paths = schema["properties"]["paths"]["properties"]
        for field in ("idea_pool", "idea_state_consistency", "experiments", "problems"):
            self.assertIn(field, paths)

    def test_shared_writing_handoff_schema_uses_ids_and_revisions(self) -> None:
        schema = load(
            WRITING_SKILL / "references" / "research-handoff.schema.json"
        )
        versions = schema["properties"]["schema_version"]["enum"]
        self.assertIn("ai-research-writing/research-handoff-v2", versions)
        then_required = schema["allOf"][0]["then"]["required"]
        self.assertIn("source_idea_id", then_required)
        self.assertIn("source_idea_revision", then_required)
        self.assertNotIn("source_idea_contract_sha256", then_required)
        self.assertNotIn("experiment_plan_sha256", then_required)


if __name__ == "__main__":
    unittest.main()
