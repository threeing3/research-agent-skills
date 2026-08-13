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
sys.path.insert(0, str(SCRIPT.parent))
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


def problem_card(problem_id: str = "problem-1", revision: int = 1) -> dict:
    return {
        "schema_version": "research-problem/v1",
        "problem_id": problem_id,
        "revision": revision,
        "maturity": "solution-ready",
        "status": "open",
        "problem_statement": "Long-video models lose sparse early evidence.",
        "frontier_context": {
            "coverage_end": "2026-08-13",
            "recent_window_start": "2025-02-13",
            "recent_sources": [{
                "source_id": "paper-1",
                "title": "Long-video selective retention",
                "published_at": "2026-03-01",
                "source_type": "peer-reviewed",
                "evidence_depth": "full-text",
                "domain_role": "target-domain",
            }],
            "recent_source_fallback_reason": None,
            "active_research_signal": "converging",
            "why_unresolved_now": "recent systems still lose sparse evidence",
            "older_foundational_sources": [],
        },
        "target_context": {
            "task": "VideoQA", "problem_setting": "long-video evidence reasoning",
            "conditions": ["long context"], "affected_capability": "evidence retention",
        },
        "observed_failure": {
            "phenomenon": "early evidence is lost as context grows",
            "conditions": ["long context"], "consequences": ["wrong answer"],
        },
        "evidence": {
            "supporting_sources": ["paper-1"], "counter_evidence": [],
            "evidence_depth": "full-text", "cross_method_status": "repeated",
            "cross_dataset_status": "single",
        },
        "current_approaches": {
            "what_they_solve": "longer context",
            "what_remains_unsolved": "selective evidence retention",
            "common_assumptions": ["capacity is sufficient"],
        },
        "bottleneck_hypotheses": [{
            "hypothesis": "uniform compression erases sparse evidence",
            "supporting_evidence": ["paper-1"],
            "strongest_competing_explanation": "decoder reasoning failure",
            "discriminating_observation": "retention intervention changes recall",
        }],
        "motivation_insight": {
            "default_interpretation": "more context is required",
            "proposed_interpretation": "selective retention is required",
            "explanatory_advantage": "explains positional failures",
            "design_implication": "select before compression", "status": "evidence-backed",
            "disconfirming_evidence": "matched retention does not change recall",
        },
        "research_value": {
            "scientific": "separates capacity and retention",
            "practical": "improves evidence use", "community": "improves diagnosis",
            "why_now": "new long contexts expose the failure",
            "value_without_sota_gain": "diagnostic insight",
            "survives_first_solution_failure": True,
            "disconfirming_evidence": "recent methods eliminate the failure",
        },
        "tractability": {
            "observable": "position-conditioned recall", "measurable": "targeted recall",
            "available_baselines": ["baseline-1"], "available_data": ["dataset-1"],
            "resource_risk": "low",
        },
        "solution_idea_ids": ["idea-1"], "uncertainties": [],
        "next_problem_check": "replicate on another model",
    }


def run(payload: dict, card_payload: dict | None = None) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        path = root / "research_state/ideas/idea-1/idea_contract.yaml"
        path.parent.mkdir(parents=True)
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        if card_payload is not None:
            card_path = root / "research_state/problems/problem-1/problem_card.yaml"
            card_path.parent.mkdir(parents=True)
            card_path.write_text(yaml.safe_dump(card_payload, sort_keys=False), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(path)], text=True, capture_output=True, check=False)


def problem_led_contract() -> dict:
    payload = contract()
    payload.update(
        {
            "contract_profile": "problem-led/v1",
            "problem_derivation": {
                "problem_id": "problem-1",
                "problem_revision": 1,
                "problem_card": "research_state/problems/problem-1/problem_card.yaml",
                "problem_maturity": "solution-ready",
                "observed_failure": "early evidence is lost as video context grows",
                "bottleneck_hypothesis": "uniform compression erases sparse evidence",
                "distinctive_motivation_insight": "selective retention matters more than raw context size",
                "motivation_status": "evidence-backed",
                "research_value": "clarifies memory quality in long-video reasoning",
                "required_behavior_change": "preserve question-relevant early evidence",
                "design_principle": "condition retention on the question",
                "module_operation": "select and preserve sparse relevant tokens",
                "implementation_location": "between encoder and decoder",
                "motivation_to_design_chain": [
                    "failure to bottleneck",
                    "bottleneck to motivation",
                    "motivation to behavior",
                    "behavior to module",
                ],
                "evidence_triad": {
                    "mechanism": ["activation and shuffle intervention"],
                    "quantitative": ["aggregate and targeted accuracy"],
                    "qualitative": ["preselected paired failure cases"],
                },
            },
            "target_domain_boundary": {
                "task": "VideoQA",
                "problem_setting": "long-video evidence reasoning",
                "key_constraints": ["long context"],
            },
            "novelty_review": {
                "status": "supported",
                "coverage_end": "2026-08-13",
                "recall_confidence": "medium",
            },
            "decision": {"selected_by_user": True},
        }
    )
    return payload


class IdeaLineageTests(unittest.TestCase):
    def test_problem_led_contract_passes_with_complete_derivation(self) -> None:
        result = run(problem_led_contract(), problem_card())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_problem_led_contract_requires_qualitative_evidence(self) -> None:
        payload = problem_led_contract()
        payload["problem_derivation"]["evidence_triad"]["qualitative"] = []
        result = run(payload, problem_card())
        self.assertEqual(result.returncode, 1)
        self.assertIn("evidence_triad.qualitative", result.stdout)

    def test_problem_led_contract_requires_positive_problem_revision(self) -> None:
        payload = problem_led_contract()
        payload["problem_derivation"]["problem_revision"] = 0
        result = run(payload, problem_card())
        self.assertEqual(result.returncode, 1)
        self.assertIn("problem_derivation.problem_revision", result.stdout)

    def test_new_family_passes_and_emits_signature(self) -> None:
        result = run(problem_led_contract(), problem_card())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"passed": true', result.stdout)
        self.assertIn("mechanism_signature_sha256", result.stdout)

    def test_v4_contract_without_profile_is_not_handoff_eligible(self) -> None:
        payload = problem_led_contract()
        del payload["contract_profile"]
        result = run(payload, problem_card())
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires contract_profile problem-led/v1", result.stdout)

    def test_legacy_contract_is_read_only(self) -> None:
        payload = problem_led_contract()
        payload["contract_profile"] = "legacy-read-only/v1"
        result = run(payload, problem_card())
        self.assertEqual(result.returncode, 1)
        self.assertIn("legacy-read-only", result.stdout)

    def test_problem_card_must_exist_and_match_revision(self) -> None:
        payload = problem_led_contract()
        result = run(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("problem_card does not exist", result.stdout)

        result = run(payload, problem_card(revision=2))
        self.assertEqual(result.returncode, 1)
        self.assertIn("problem_revision does not match", result.stdout)

    def test_closed_problem_card_blocks_handoff(self) -> None:
        value = problem_card()
        value["status"] = "closed"
        result = run(problem_led_contract(), value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("status is closed", result.stdout)

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

    def test_staged_contract_with_supported_target_novelty_is_read_only(self) -> None:
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
        self.assertEqual(result.returncode, 1)
        self.assertIn("legacy-read-only", result.stdout)

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
