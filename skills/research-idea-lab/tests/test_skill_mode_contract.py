from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    match = re.search(
        rf"{re.escape(start)}(?P<body>.*?){re.escape(end)}",
        SKILL_TEXT,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError(f"cannot find section between {start!r} and {end!r}")
    return match.group("body")


class SkillEvidenceLoopContractTests(unittest.TestCase):
    def test_problem_mechanism_and_implementation_are_separate_layers(self) -> None:
        core = section("## Core distinction", "## Minimal evidence loop")
        for concept in (
            "observed failure",
            "bottleneck hypothesis",
            "method hypothesis",
            "implementation realization",
        ):
            self.assertIn(concept, core)
        self.assertIn("does not prove the problem exists", core)

    def test_primary_intent_is_not_a_rigid_workflow_fence(self) -> None:
        intent = section(
            "## Choose a primary intent, not a rigid mode",
            "## Start lightly",
        )
        self.assertIn("use adjacent capabilities", intent)
        self.assertIn("Do not force a request", intent)
        self.assertNotIn("Select exactly one primary mode", SKILL_TEXT)

    def test_problem_diagnosis_allows_minimal_intervention_without_circular_proof(self) -> None:
        problem = section(
            "## Establish the problem before building the method",
            "## Derive methods from supported bottlenecks",
        )
        self.assertIn("minimal diagnostic intervention", problem)
        self.assertIn("does not instantiate the complete proposed solution", problem)
        self.assertIn("Do not use the full proposed method's performance", problem)

    def test_iteration_requires_new_discriminating_information(self) -> None:
        iteration = section(
            "## Control iteration by information gain",
            "## Interpret results at the right layer",
        )
        for concept in (
            "What uncertainty changed",
            "What new variable or behavior",
            "Which competing explanations",
            "If the result repeats",
            "engineering repair",
            "scientific iteration",
        ):
            self.assertIn(concept, iteration)
        self.assertIn("do not create another scientific revision", iteration)

    def test_natural_intermediate_interface_is_checked_before_long_runs(self) -> None:
        iteration = section(
            "## Control iteration by information gain",
            "## Interpret results at the right layer",
        )
        self.assertIn("intermediate artifact", iteration)
        self.assertIn("naturally at useful quality and coverage", iteration)
        self.assertIn("do not use a universal pass rate", iteration)

    def test_candidate_generation_has_no_fixed_portfolio_count(self) -> None:
        development = section(
            "## Derive methods from supported bottlenecks",
            "## Control iteration by information gain",
        )
        self.assertIn("Do not require a fixed number of candidates", development)
        self.assertNotRegex(SKILL_TEXT, r"return\s+3[–-]5")
        self.assertNotIn("Target at least six raw", SKILL_TEXT)

    def test_all_direct_references_exist(self) -> None:
        paths = set(re.findall(r"(?:references|scripts)/[A-Za-z0-9._-]+", SKILL_TEXT))
        self.assertTrue(paths)
        missing = [path for path in sorted(paths) if not (SKILL_ROOT / path).exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
