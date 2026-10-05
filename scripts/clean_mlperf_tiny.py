#!/usr/bin/env python3
"""Inspect or remove recognized generated files from migrated MLPerf Tiny apps."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
VTA_ROOT = REPO_ROOT / "vta"
MODEL_IDS = (
    "image_classification_v2",
    "visual_wake_words_v1",
    "keyword_spotting_v1",
    "anomaly_detection_v1",
    "streaming_wakeword_v1",
)
GENERATED_NAMES = {"graph.json", "manifest.json", "params.bin", "model.dylib", "model.so"}
GENERATED_SUFFIXES = {".ll", ".c", ".cc", ".cpp", ".h", ".o", ".a", ".dylib", ".so"}
OUTPUT_ROOTS = {
    "c",
    "llvm",
    "vta_c",
    "vta_llvm",
    "reference",
    "mixed",
    "selected_deployment",
    "fsim",
    "tsim",
}
MATRIX_ROOTS = {"llvm-fsim", "llvm-tsim", "c-fsim", "c-tsim"}


@dataclass(frozen=True)
class Candidate:
    path: Path
    size_bytes: int


@dataclass(frozen=True)
class Inventory:
    candidates: tuple[Candidate, ...]
    unknown: tuple[Path, ...]
    tracked: tuple[Path, ...]
    errors: tuple[str, ...]


def _read_tracked_paths(vta_root: Path) -> set[Path]:
    result = subprocess.run(
        ["git", "-C", str(vta_root), "ls-files", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {(vta_root / path.decode("utf-8")).resolve(strict=False) for path in result.stdout.split(b"\0") if path}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("all", *MODEL_IDS), required=True)
    parser.add_argument("--dry-run", action="store_true", help="list candidates without deleting")
    return parser


def _known_generated_file(path: Path, build_root: Path) -> bool:
    relative = path.relative_to(build_root)
    if relative.parts == ("tune", "workloads.json"):
        return True
    parts = relative.parts
    if parts[:2] == ("tune", "deploy"):
        parts = parts[2:]
    if not parts:
        return False
    if parts[0] in MATRIX_ROOTS:
        if len(parts) < 3 or parts[1] not in {"reference", "mixed"}:
            return False
        bundle_parts = parts[2:]
    elif parts[0] in OUTPUT_ROOTS:
        bundle_parts = parts[1:]
    else:
        return False
    if len(bundle_parts) == 1 and bundle_parts[0] in GENERATED_NAMES:
        return True
    return (
        len(bundle_parts) == 2
        and bundle_parts[0] == "source"
        and Path(bundle_parts[1]).suffix in GENERATED_SUFFIXES
    )


def _inventory(benchmark_root: Path, model: str, tracked_paths: Iterable[str | Path]) -> Inventory:
    tracked = {
        (Path(path) if Path(path).is_absolute() else benchmark_root / Path(path)).resolve(strict=False)
        for path in tracked_paths
    }
    models = MODEL_IDS if model == "all" else (model,)
    candidates: list[Candidate] = []
    unknown: list[Path] = []
    retained_tracked: list[Path] = []
    errors: list[str] = []
    for model_id in models:
        build_root = benchmark_root / model_id / "build"
        if build_root.is_symlink():
            errors.append(f"symlinked build path refused: {build_root}")
            continue
        cursor = build_root.parent
        while cursor != benchmark_root.parent:
            if cursor.is_symlink():
                errors.append(f"symlinked build path refused: {cursor}")
                break
            if cursor == benchmark_root:
                break
            cursor = cursor.parent
        if errors or not build_root.exists():
            continue
        if not build_root.is_dir():
            errors.append(f"build path is not a directory: {build_root}")
            continue
        for current, dirnames, filenames in os.walk(build_root, followlinks=False):
            current_path = Path(current)
            kept_dirs = []
            for dirname in dirnames:
                child = current_path / dirname
                if child.is_symlink():
                    errors.append(f"symlink refused: {child}")
                else:
                    kept_dirs.append(dirname)
            dirnames[:] = kept_dirs
            for filename in filenames:
                path = current_path / filename
                if path.is_symlink():
                    errors.append(f"symlink refused: {path}")
                    continue
                if not path.is_file():
                    continue
                resolved = path.resolve(strict=False)
                if not _known_generated_file(path, build_root):
                    unknown.append(resolved)
                elif resolved in tracked:
                    retained_tracked.append(resolved)
                else:
                    try:
                        candidates.append(Candidate(resolved, path.stat(follow_symlinks=False).st_size))
                    except OSError as error:
                        errors.append(f"cannot stat {path}: {error}")
    return Inventory(
        tuple(sorted(candidates, key=lambda item: str(item.path))),
        tuple(sorted(set(unknown))),
        tuple(sorted(set(retained_tracked))),
        tuple(errors),
    )


def main(
    argv: Iterable[str] | None = None,
    *,
    repo_root: str | Path = REPO_ROOT,
    tracked_paths: Iterable[str | Path] | None = None,
) -> int:
    args = _parser().parse_args(argv)
    root = Path(repo_root).absolute()
    benchmark = root / "vta" / "apps" / "mlperf_tiny_benchmark"
    try:
        tracked = tracked_paths if tracked_paths is not None else _read_tracked_paths(root / "vta")
        inventory = _inventory(benchmark, args.model, tracked)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if inventory.errors:
        for error in inventory.errors:
            print(f"error: {error}", file=sys.stderr)
        print("No files removed because inventory found a safety error.", file=sys.stderr)
        return 2

    removed: list[Candidate] = []
    if not args.dry_run:
        for item in inventory.candidates:
            try:
                if item.path.is_symlink() or not item.path.is_file():
                    raise ValueError("target changed since inventory")
                item.path.unlink()
                removed.append(item)
            except (OSError, ValueError) as error:
                print(f"error: cannot remove {item.path}: {error}", file=sys.stderr)
                return 2

    for item in inventory.candidates:
        action = "would remove" if args.dry_run else "removed"
        print(f"{action}: {item.path} ({item.size_bytes} bytes)")
    for path in inventory.unknown:
        print(f"unknown, retained: {path}")
    for path in inventory.tracked:
        print(f"tracked, retained: {path}")
    affected = inventory.candidates if args.dry_run else removed
    bytes_total = sum(item.size_bytes for item in affected)
    action = "would remove" if args.dry_run else "removed"
    print(f"{action}: {len(affected)} file(s), {bytes_total} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
