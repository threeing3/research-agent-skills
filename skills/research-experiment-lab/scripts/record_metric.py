#!/usr/bin/env python3
"""Append one validated metric observation to a metrics JSONL file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from experiment_common import append_jsonl, finite_number, now


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics_file", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--value", type=float, required=True)
    parser.add_argument("--step", type=int)
    parser.add_argument("--split", default="")
    parser.add_argument("--dataset", default="")
    parser.add_argument("--variant", default="")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if not finite_number(args.value):
        print("metric value must be finite", file=sys.stderr)
        return 2
    append_jsonl(
        args.metrics_file,
        {
            "timestamp": now(),
            "name": args.name,
            "value": args.value,
            "step": args.step,
            "split": args.split,
            "dataset": args.dataset,
            "variant": args.variant,
            "seed": args.seed,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

