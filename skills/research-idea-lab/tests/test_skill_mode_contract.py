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


class SkillModeContractTests(unittest.TestCase):
    def test_interaction_policy_limits_questions_and_silent_escalation(self) -> None:
        self.assertIn("Ask at most one blocking question in a turn", SKILL_TEXT)
        self.assertIn("Do not ask for routine mode changes or skill handoffs", SKILL_TEXT)
        self.assertIn("never silently escalate to `gate`", SKILL_TEXT)

    def test_explore_cannot_run_strict_rejection(self) -> None:
        explore = section("### `explore`", "### `develop`")
        self.assertIn("Do not score, rank, reject", explore)
        self.assertIn("A literature collision creates a differentiation", explore)

    def test_develop_separates_potential_and_cannot_reject(self) -> None:
        develop = section("### `develop`", "### `gate`")
        self.assertIn("Separate current weakness from development potential", develop)
        self.assertIn("Do not write `rejected`", develop)

    def test_gate_requires_explicit_user_intent(self) -> None:
        gate = section("### `gate`", "## Start")
        self.assertIn("only when the user explicitly requests", gate)
        self.assertIn("Only this mode may set `rejected` or `experiment-ready`", gate)

    def test_exploration_has_positive_output_contract(self) -> None:
        self.assertIn("return 3–5 coherent candidates", SKILL_TEXT)
        self.assertIn("never return an empty rejection-only answer", SKILL_TEXT)
        self.assertIn("at least one attempted material rescue route", SKILL_TEXT)

    def test_all_direct_references_exist(self) -> None:
        paths = set(re.findall(r"(?:references|scripts)/[A-Za-z0-9._-]+", SKILL_TEXT))
        self.assertTrue(paths)
        missing = [path for path in sorted(paths) if not (SKILL_ROOT / path).exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
