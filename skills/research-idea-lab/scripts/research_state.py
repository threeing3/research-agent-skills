#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def init(root: Path) -> None:
    base = root / "research_state"
    for relative in (
        "literature",
        "ideation_sessions",
        "review_patterns",
        "ideas",
        "experiments",
        "paper",
        "logs",
    ):
        (base / relative).mkdir(parents=True, exist_ok=True)
    index = root / "research_state.json"
    if not index.exists():
        atomic_json(index, {
            "schema_version": "research-state/v1",
            "revision": 0,
            "phase": "ideation",
            "active_idea_id": None,
            "paths": {
                "field_snapshot": "research_state/literature/field_snapshot.json",
                "ideation_sessions": "research_state/ideation_sessions",
                "review_patterns": "research_state/review_patterns",
                "idea_pool": "research_state/ideas/idea_pool.json",
                "idea_state_consistency": "research_state/ideas/state_consistency.json",
                "experiments": "research_state/experiments",
                "paper_state": "research_state/paper/paper_state.json",
                "events": "research_state/logs/research_events.jsonl"
            },
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        return

    state = json.loads(index.read_text(encoding="utf-8"))
    paths = state.setdefault("paths", {})
    required_paths = {
        "ideation_sessions": "research_state/ideation_sessions",
        "review_patterns": "research_state/review_patterns",
        "idea_state_consistency": "research_state/ideas/state_consistency.json",
    }
    missing_paths = {
        key: value for key, value in required_paths.items() if key not in paths
    }
    if missing_paths:
        previous_revision = state.get("revision", 0)
        paths.update(missing_paths)
        state["revision"] = previous_revision + 1
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        atomic_json(index, state)
        event_path = base / "logs" / "research_events.jsonl"
        event = {
            "event": "state-paths-added",
            "paths": missing_paths,
            "revision_before": previous_revision,
            "revision_after": state["revision"],
            "timestamp": state["updated_at"]
        }
        with event_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def update(root: Path, expected: int, phase: str, idea_id: Optional[str]) -> None:
    index_path = root / "research_state.json"
    state = json.loads(index_path.read_text(encoding="utf-8"))
    if state["revision"] != expected:
        raise SystemExit(f"revision conflict: expected {expected}, found {state['revision']}")
    state["revision"] += 1
    state["phase"] = phase
    if idea_id is not None:
        state["active_idea_id"] = idea_id
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    atomic_json(index_path, state)


parser = argparse.ArgumentParser()
parser.add_argument("root", type=Path)
parser.add_argument("--init", action="store_true")
parser.add_argument("--expected-revision", type=int)
parser.add_argument("--phase")
parser.add_argument("--idea-id")
args = parser.parse_args()
if args.init:
    init(args.root.resolve())
else:
    if args.expected_revision is None or not args.phase:
        parser.error("update requires --expected-revision and --phase")
    update(args.root.resolve(), args.expected_revision, args.phase, args.idea_id)
