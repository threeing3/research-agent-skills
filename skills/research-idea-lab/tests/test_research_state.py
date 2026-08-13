from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "research_state.py"


def run_init(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), "--init"],
        text=True,
        capture_output=True,
        check=False,
    )


class ResearchStateTests(unittest.TestCase):
    def test_new_index_uses_canonical_consistency_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = run_init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            state = json.loads((root / "research_state.json").read_text(encoding="utf-8"))
            self.assertEqual(
                state["paths"]["idea_state_consistency"],
                "research_state/ideas/state_consistency.json",
            )
            self.assertEqual(state["paths"]["problems"], "research_state/problems")
            self.assertTrue((root / "research_state/problems").is_dir())

    def test_legacy_index_path_is_migrated_without_deleting_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "research_state" / "ideas" / "idea_state_consistency.json"
            legacy.parent.mkdir(parents=True)
            legacy.write_text('{"legacy":true}\n', encoding="utf-8")
            (root / "research_state.json").write_text(
                json.dumps(
                    {
                        "schema_version": "research-state/v1",
                        "revision": 4,
                        "phase": "ideation",
                        "active_idea_id": None,
                        "paths": {
                            "idea_state_consistency": "research_state/ideas/idea_state_consistency.json"
                        },
                        "updated_at": "fixture",
                    }
                ),
                encoding="utf-8",
            )
            result = run_init(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            state = json.loads((root / "research_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["revision"], 5)
            self.assertEqual(
                state["paths"]["idea_state_consistency"],
                "research_state/ideas/state_consistency.json",
            )
            self.assertEqual(state["paths"]["problems"], "research_state/problems")
            self.assertTrue((root / "research_state/problems").is_dir())
            self.assertTrue(legacy.is_file())
            event = json.loads(
                (root / "research_state/logs/research_events.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )
            self.assertEqual(event["event"], "state-paths-updated")


if __name__ == "__main__":
    unittest.main()
