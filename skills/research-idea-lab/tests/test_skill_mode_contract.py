from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_TEXT = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
ANTI_RESKIN_TEXT = (SKILL_ROOT / "references/anti-reskin-protocol.md").read_text(encoding="utf-8")
NOVELTY_TEXT = (SKILL_ROOT / "references/novelty-workflow.md").read_text(encoding="utf-8")


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
        self.assertIn("never silently escalate to the full `gate`", SKILL_TEXT)
        self.assertIn("Before every validation round", SKILL_TEXT)

    def test_explore_cannot_run_strict_rejection(self) -> None:
        explore = section("### `explore`", "### `develop`")
        self.assertIn("Do not score, rank, reject", explore)
        self.assertIn("A literature collision creates a differentiation", explore)

    def test_develop_separates_potential_and_cannot_reject(self) -> None:
        develop = section("### `develop`", "### `novelty`")
        self.assertIn("Separate current weakness from development potential", develop)
        self.assertIn("Do not write `rejected`", develop)

    def test_novelty_mode_is_focused_and_tri_state(self) -> None:
        novelty = section("### `novelty`", "### `gate`")
        self.assertIn("`supported`, `occupied`, or `uncertain`", novelty)
        self.assertIn("Do not score, rank", novelty)
        self.assertIn("independent conclusions", novelty)

    def test_gate_requires_explicit_user_intent(self) -> None:
        gate = section("### `gate`", "## Start")
        self.assertIn("only when the user explicitly requests", gate)
        self.assertIn("Only this mode may set `rejected`", gate)

    def test_exploration_has_positive_output_contract(self) -> None:
        self.assertIn("return 3–5 candidates across", SKILL_TEXT)
        self.assertIn("never return an empty rejection-only answer", SKILL_TEXT)
        self.assertIn("at least one attempted material rescue route", SKILL_TEXT)

    def test_portfolio_includes_baseline_changes_and_maturity(self) -> None:
        self.assertIn("`baseline-modification`", SKILL_TEXT)
        self.assertIn("include at least one", SKILL_TEXT)
        self.assertIn("`seed`, `developing`, and `validation-ready`", SKILL_TEXT)

    def test_source_scope_and_target_domain_are_separate(self) -> None:
        self.assertIn("Mechanism discovery may use high-quality primary sources from any field or venue", SKILL_TEXT)
        self.assertIn("regardless of venue", SKILL_TEXT)
        self.assertIn("does not occupy target-domain novelty by itself", SKILL_TEXT)

    def test_full_anti_reskin_is_not_an_exploration_prerequisite(self) -> None:
        self.assertIn("Use the full protocol only for a stable selected idea", ANTI_RESKIN_TEXT)
        self.assertNotIn("Use this protocol before creating a candidate", ANTI_RESKIN_TEXT)
        self.assertIn("Do not impose a fixed scientific rescue count", ANTI_RESKIN_TEXT)

    def test_novelty_workflow_uses_complete_target_mechanism_occupation(self) -> None:
        self.assertIn("Return exactly one status", NOVELTY_TEXT)
        self.assertIn("complete operative mechanism", NOVELTY_TEXT)
        self.assertIn("regardless of venue", NOVELTY_TEXT)
        self.assertIn("Report these independently", NOVELTY_TEXT)

    def test_all_direct_references_exist(self) -> None:
        paths = set(re.findall(r"(?:references|scripts)/[A-Za-z0-9._-]+", SKILL_TEXT))
        self.assertTrue(paths)
        missing = [path for path in sorted(paths) if not (SKILL_ROOT / path).exists()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
