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

    def test_experiment_schema_and_template_track_plan_v2(self) -> None:
        schema = load(REPO / "schemas" / "experiment-plan.schema.json")
        template = load(EXPERIMENT_SKILL / "assets" / "experiment_plan.json.template")
        self.assertEqual(
            schema["properties"]["schema_version"]["const"], template["schema_version"]
        )
        self.assertEqual(template["schema_version"], "research-experiment/plan-v2")
        self.assertIn(
            "idea_state_consistency_report",
            schema["properties"]["prelaunch"]["required"],
        )
        self.assertIn("idea_state_consistency_report", template["prelaunch"])
        self.assertEqual(template["admission_mode"], "formal")
        self.assertIn("validation_alignment", schema["properties"])
        self.assertIn("validation_alignment_check_report", template["prelaunch"])

    def test_validation_alignment_schema_requires_user_and_realization_evidence(self) -> None:
        schema = load(REPO / "schemas" / "validation-alignment.schema.json")
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            "research-idea/validation-alignment-v1",
        )
        validation_required = schema["properties"]["validation"]["required"]
        self.assertIn("activation_evidence", validation_required)
        self.assertIn("intervention_evidence", validation_required)
        self.assertIn("user_alignment", schema["required"])

    def test_verification_schema_tracks_emitted_v2_identity(self) -> None:
        schema = load(REPO / "schemas" / "verification-report.schema.json")
        self.assertEqual(
            schema["properties"]["schema_version"]["const"],
            "research-experiment/experiment-verification-v2",
        )
        self.assertIn("verified-diagnostic", schema["properties"]["stage"]["enum"])
        for field in (
            "experiment_id",
            "plan_revision",
            "idea_id",
            "idea_revision",
            "idea_contract_sha256",
            "experiment_plan_sha256",
            "stage",
            "passed",
        ):
            self.assertIn(field, schema["required"])

    def test_research_state_schema_allows_real_phase_and_current_paths(self) -> None:
        schema = load(REPO / "schemas" / "research-state.schema.json")
        self.assertEqual(schema["properties"]["phase"]["type"], "string")
        paths = schema["properties"]["paths"]["properties"]
        for field in ("idea_pool", "idea_state_consistency", "experiments"):
            self.assertIn(field, paths)

    def test_shared_writing_handoff_schema_requires_v2_hashes(self) -> None:
        schema = load(
            WRITING_SKILL / "references" / "research-handoff.schema.json"
        )
        versions = schema["properties"]["schema_version"]["enum"]
        self.assertIn("ai-research-writing/research-handoff-v2", versions)
        then_required = schema["allOf"][0]["then"]["required"]
        self.assertIn("source_idea_contract_sha256", then_required)
        self.assertIn("experiment_plan_sha256", then_required)


if __name__ == "__main__":
    unittest.main()
