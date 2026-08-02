#!/usr/bin/env python3
"""Ingest downloaded remote records without overwriting conflicting evidence."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from experiment_common import atomic_json, now, sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("download_dir", type=Path)
    parser.add_argument("local_run_dir", type=Path)
    args = parser.parse_args()
    source = args.download_dir.resolve()
    if (source / "records").is_dir():
        source = source / "records"
    destination = args.local_run_dir.resolve()
    if (destination / "records").is_dir():
        destination = destination / "records"
    try:
        if not source.is_dir() or not destination.is_dir():
            raise ValueError("source and destination record directories must exist")
        copied = []
        identical = []
        for path in sorted(source.rglob("*")):
            if not path.is_file() or path.name == "sync_manifest.json":
                continue
            relative = path.relative_to(source)
            target = destination / relative
            if target.exists():
                if not target.is_file() or sha256_file(target) != sha256_file(path):
                    raise ValueError(f"evidence conflict; refusing overwrite: {target}")
                identical.append(relative.as_posix())
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            copied.append(relative.as_posix())
        manifest = {
            "schema_version": "research-experiment/ingest-v1",
            "timestamp": now(),
            "source": str(source),
            "destination": str(destination),
            "copied": copied,
            "identical_existing": identical,
            "status": "completed",
        }
        atomic_json(destination / "ingest_manifest.json", manifest)
        print(f"ingested={len(copied)} identical={len(identical)}")
    except (OSError, ValueError) as exc:
        print(f"ingest_records failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

