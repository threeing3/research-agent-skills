#!/usr/bin/env python3
"""Create an explicit, content-addressed ZIP snapshot for remote execution."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import zipfile
from pathlib import Path

from experiment_common import atomic_json, now, safe_relative, sha256_file


DEFAULT_EXCLUDES = (
    ".git/**",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "**/__pycache__/**",
    "**/*.pyc",
    "research_state/**",
    ".codex-skill-staging/**",
    ".codex-skill-sources/**",
    "**/id_rsa",
    "**/id_ed25519",
    "**/*.pem",
    "**/*.key",
)


def matches(path: str, patterns: tuple[str, ...]) -> bool:
    normalized = path.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


def collect(root: Path, includes: list[str], excludes: tuple[str, ...]) -> list[Path]:
    files: dict[str, Path] = {}
    for raw in includes:
        candidate = (root / raw).resolve()
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"include escapes project root: {raw}") from exc
        if not candidate.exists():
            raise ValueError(f"include does not exist: {raw}")
        paths = [candidate] if candidate.is_file() else candidate.rglob("*")
        for path in paths:
            if not path.is_file() or path.is_symlink():
                continue
            relative = safe_relative(path, root)
            if not matches(relative, excludes):
                files[relative] = path
    return [files[name] for name in sorted(files)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--include", action="append", required=True)
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.project_root.resolve()
        if not root.is_dir():
            raise ValueError(f"project root is not a directory: {root}")
        excludes = tuple(DEFAULT_EXCLUDES) + tuple(args.exclude)
        files = collect(root, args.include, excludes)
        if not files:
            raise ValueError("snapshot contains no files after exclusions")
        entries = [
            {
                "path": safe_relative(path, root),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        ]
        canonical = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
        import hashlib

        snapshot_id = hashlib.sha256(canonical).hexdigest()[:20]
        output = args.output_dir.resolve()
        output.mkdir(parents=True, exist_ok=True)
        manifest_path = output / f"snapshot-{snapshot_id}.manifest.json"
        archive_path = output / f"snapshot-{snapshot_id}.zip"
        if manifest_path.exists() or archive_path.exists():
            raise ValueError(f"snapshot output already exists: {snapshot_id}")
        manifest = {
            "schema_version": "research-experiment/snapshot-v1",
            "snapshot_id": snapshot_id,
            "project_root_name": root.name,
            "created_at": now(),
            "includes": args.include,
            "excludes": list(excludes),
            "file_count": len(entries),
            "total_bytes": sum(entry["size_bytes"] for entry in entries),
            "files": entries,
        }
        atomic_json(manifest_path, manifest)
        with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            for path, entry in zip(files, entries):
                archive.write(path, entry["path"])
        result = {
            "snapshot_id": snapshot_id,
            "archive": str(archive_path),
            "manifest": str(manifest_path),
            "archive_sha256": sha256_file(archive_path),
            "file_count": len(entries),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        print(f"prepare_snapshot failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

