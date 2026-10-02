#!/usr/bin/env python3
"""Inspect or remove known generated MLPerf Tiny build and tuning files."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
VTA_ROOT = REPO_ROOT / "vta"
sys.path.insert(0, str(VTA_ROOT / "apps"))

from common.artifacts import CATEGORIES, MODEL_IDS, cleanup_artifacts  # noqa: E402


def _read_tracked_paths(vta_root: Path) -> tuple[Path, ...]:
    result = subprocess.run(
        ["git", "-C", str(vta_root), "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return tuple(vta_root / path.decode("utf-8") for path in result.stdout.split(b"\0") if path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("all", *MODEL_IDS), required=True)
    parser.add_argument("--cache", action="store_true", help="remove regenerable compile/debug output")
    parser.add_argument("--tuning-runs", action="store_true", help="remove resumable tuning state")
    parser.add_argument("--dry-run", action="store_true", help="list candidates and byte totals without deleting")
    return parser


def main(
    argv: Iterable[str] | None = None,
    *,
    repo_root: str | Path = REPO_ROOT,
    tracked_paths: Iterable[str | Path] | None = None,
) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    categories = {
        category
        for category, selected in (("cache", args.cache), ("tuning-runs", args.tuning_runs))
        if selected
    }
    if not categories:
        parser.error("choose at least one of --cache or --tuning-runs")

    root = Path(repo_root).absolute()
    vta_root = root / "vta"
    try:
        tracked = tuple(tracked_paths) if tracked_paths is not None else _read_tracked_paths(vta_root)
        result = cleanup_artifacts(
            vta_root / "apps" / "mlperf_tiny_benchmark",
            model=args.model,
            categories=categories,
            tracked_paths=tracked,
            dry_run=args.dry_run,
        )
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    chosen = result.planned
    if args.dry_run:
        for category in CATEGORIES:
            selected = [item for item in chosen if item.category == category]
            if not selected:
                continue
            total = sum(item.size_bytes for item in selected)
            print(f"{category}: {len(selected)} file(s), {total} bytes")
            for item in selected:
                print(f"  {item.path} ({item.size_bytes} bytes)")
    else:
        for item in result.removed:
            print(f"removed: {item.path} ({item.size_bytes} bytes)")

    for path in result.unknown_paths:
        print(f"unknown, retained: {path}")
    for path in result.tracked_paths:
        print(f"tracked, retained: {path}")

    if result.errors:
        for error in result.errors:
            print(f"error: {error}", file=sys.stderr)
        print("No files removed because inventory found a safety error.", file=sys.stderr)
        return 2

    affected = result.planned if args.dry_run else result.removed
    action = "would remove" if args.dry_run else "removed"
    bytes_total = result.total_bytes if args.dry_run else sum(item.size_bytes for item in result.removed)
    print(f"{action}: {len(affected)} file(s), {bytes_total} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
