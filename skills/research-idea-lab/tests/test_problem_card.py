from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "check_problem_card.py"


def card() -> dict:
    return {
        "schema_version": "research-problem/v1",
        "problem_id": "problem-1",
        "revision": 1,
        "maturity": "solution-ready",
        "status": "open",
        "problem_statement": "Long-video models lose sparse early evidence.",
        "frontier_context": {
            "coverage_end": "2026-08-13",
            "recent_window_start": "2025-02-13",
            "recent_sources": [
                {
                    "source_id": "recent-paper-1",
                    "title": "Question-conditioned long-video memory",
                    "published_at": "2026-04-12",
                    "source_type": "peer-reviewed",
                    "evidence_depth": "full-text",
                    "domain_role": "target-domain",
                },
                {
                    "source_id": "recent-paper-2",
                    "title": "Long-context retention benchmark",
                    "published_at": "2025-11-03",
                    "source_type": "benchmark-update",
                    "evidence_depth": "artifact-verified",
                    "domain_role": "target-domain",
                },
            ],
            "recent_source_fallback_reason": None,
            "active_research_signal": "converging",
            "why_unresolved_now": "recent long-context methods still show position-dependent failures",
            "older_foundational_sources": ["foundation-paper"],
        },
        "target_context": {
            "task": "long-video question answering",
            "problem_setting": "questions requiring sparse early evidence",
            "conditions": ["long context"],
            "affected_capability": "evidence retention",
        },
        "observed_failure": {
            "phenomenon": "accuracy drops when decisive evidence appears early",
            "conditions": ["long distractor context"],
            "consequences": ["incorrect answers despite visible evidence"],
        },
        "evidence": {
            "supporting_sources": ["recent-paper-1", "artifact-1"],
            "counter_evidence": [],
            "evidence_depth": "artifact-verified",
            "cross_method_status": "repeated",
            "cross_dataset_status": "single",
        },
        "current_approaches": {
            "what_they_solve": "increase available context",
            "what_remains_unsolved": "selective preservation of sparse evidence",
            "common_assumptions": ["more context implies better evidence use"],
        },
        "bottleneck_hypotheses": [
            {
                "hypothesis": "uniform compression erases sparse relevant evidence",
                "supporting_evidence": ["artifact-1"],
                "strongest_competing_explanation": "the decoder cannot reason over retained evidence",
                "discriminating_observation": "retention intervention improves evidence recall before decoding",
            }
        ],
        "motivation_insight": {
            "default_interpretation": "the model needs a larger context",
            "proposed_interpretation": "the model needs question-conditioned retention",
            "explanatory_advantage": "explains position-specific loss under equal context size",
            "design_implication": "change selection before compression",
            "status": "evidence-backed",
            "disconfirming_evidence": "equal retained evidence with no downstream improvement",
        },
        "research_value": {
            "scientific": "separates context capacity from evidence retention",
            "practical": "improves long-video evidence use",
            "community": "clarifies why long-context scaling saturates",
            "why_now": "new long-context models expose the failure",
            "value_without_sota_gain": "a diagnostic account of position-dependent failure",
            "survives_first_solution_failure": True,
            "disconfirming_evidence": "recent methods eliminate the failure under fair evaluation",
        },
        "tractability": {
            "observable": "evidence recall by temporal position",
            "measurable": "targeted subset accuracy and recall",
            "available_baselines": ["baseline-1"],
            "available_data": ["dataset-1"],
            "resource_risk": "low",
        },
        "solution_idea_ids": [],
        "uncertainties": [],
        "next_problem_check": "replicate the failure across a second baseline",
    }


def run(value: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "problem.yaml"
        path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            text=True,
            capture_output=True,
            check=False,
        )


class ProblemCardTests(unittest.TestCase):
    def test_solution_ready_problem_passes(self) -> None:
        result = run(card())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"passed": true', result.stdout)

    def test_solution_ready_problem_requires_distinctive_motivation(self) -> None:
        value = card()
        value["motivation_insight"]["explanatory_advantage"] = ""
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("motivation_insight.explanatory_advantage", result.stdout)

    def test_problem_seed_can_remain_incomplete_but_needs_frontier_sources(self) -> None:
        value = card()
        value["maturity"] = "problem-seed"
        value["evidence"]["supporting_sources"] = []
        value["bottleneck_hypotheses"] = []
        value["motivation_insight"]["status"] = "unknown"
        result = run(value)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        value["frontier_context"]["recent_sources"] = []
        value["frontier_context"]["recent_source_fallback_reason"] = None
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("recent_source_fallback_reason", result.stdout)

    def test_schema_required_fields_cannot_bypass_checker(self) -> None:
        value = card()
        del value["target_context"]
        del value["current_approaches"]
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("schema:<root>", result.stdout)
        self.assertIn("target_context", result.stdout)
        self.assertIn("current_approaches", result.stdout)

    def test_recent_source_dates_must_be_inside_declared_window(self) -> None:
        value = card()
        value["frontier_context"]["recent_sources"][0]["published_at"] = "2024-12-31"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("before recent_window_start", result.stdout)

        value = card()
        value["frontier_context"]["recent_sources"][0]["published_at"] = "not-a-date"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("published_at", result.stdout)

    def test_explicit_recent_source_fallback_is_allowed_without_false_signal(self) -> None:
        value = card()
        value["maturity"] = "problem-seed"
        value["frontier_context"]["recent_sources"] = []
        value["frontier_context"]["recent_source_fallback_reason"] = (
            "No inspectable paper was published in the declared niche window."
        )
        value["frontier_context"]["active_research_signal"] = "weak"
        result = run(value)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        value["frontier_context"]["active_research_signal"] = "converging"
        result = run(value)
        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot be converging or newly-exposed", result.stdout)


if __name__ == "__main__":
    unittest.main()
