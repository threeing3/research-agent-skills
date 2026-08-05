from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "research_state.py"


def initialize(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root), "--init"],
        text=True,
        capture_output=True,
        check=False,
    )


class ResearchStateTests(unittest.TestCase):
    def test_init_creates_industry_signal_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = initialize(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "research_state" / "industry").is_dir())
            state = json.loads((root / "research_state.json").read_text(encoding="utf-8"))
            self.assertEqual(
                state["paths"]["industry_signals"],
                "research_state/industry/signals.jsonl",
            )
            self.assertEqual(
                state["paths"]["industry_scan_manifest"],
                "research_state/industry/scan_manifest.json",
            )

    def test_init_migrates_legacy_index_without_overwriting_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_path = root / "research_state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "schema_version": "research-state/v1",
                        "revision": 4,
                        "phase": "ideation",
                        "active_idea_id": "idea-existing",
                        "paths": {},
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            result = initialize(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["revision"], 5)
            self.assertEqual(state["active_idea_id"], "idea-existing")
            self.assertEqual(
                state["paths"]["industry_signals"],
                "research_state/industry/signals.jsonl",
            )
            event_path = root / "research_state" / "logs" / "research_events.jsonl"
            self.assertIn("state-paths-added", event_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
