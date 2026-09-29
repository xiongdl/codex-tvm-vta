#!/usr/bin/env python3
"""Calculate useful MAC utilization from explicit TSIM measurements."""

import argparse
import json
from pathlib import Path


DEFAULT_CONFIG = (
    Path(__file__).resolve().parents[1] / "vta" / "config" / "vta_64mac.json"
)


def load_peak_macs_per_cycle(config_path):
    """Read VTA geometry and return its peak logical MACs per cycle."""
    path = Path(config_path)
    try:
        with path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read geometry JSON {path}: {error}") from error

    if not isinstance(config, dict):
        raise ValueError("geometry JSON must contain an object")

    exponents = {}
    for key in ("LOG_BATCH", "LOG_BLOCK"):
        value = config.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"geometry field {key} must be a non-negative integer")
        exponents[key] = value

    batch = 2 ** exponents["LOG_BATCH"]
    block = 2 ** exponents["LOG_BLOCK"]
    return batch * block * block


def calculate_utilization(mac_count, cycle_count, peak_macs_per_cycle):
    """Return utilization ratio and percentage for positive integer inputs."""
    for name, value in (
        ("MAC count", mac_count),
        ("TSIM cycle count", cycle_count),
        ("peak MACs per cycle", peak_macs_per_cycle),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")

    ratio = mac_count / (cycle_count * peak_macs_per_cycle)
    return ratio, ratio * 100


def positive_integer(value):
    """argparse type for strictly positive integer inputs."""
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Calculate useful MAC utilization from logical MACs, TSIM cycles, "
            "and VTA geometry."
        )
    )
    parser.add_argument("--macs", required=True, type=positive_integer)
    parser.add_argument("--cycles", required=True, type=positive_integer)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"VTA geometry JSON (default: {DEFAULT_CONFIG})",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        peak = load_peak_macs_per_cycle(args.config)
        ratio, percentage = calculate_utilization(args.macs, args.cycles, peak)
    except ValueError as error:
        parser.error(str(error))

    print(f"MACs: {args.macs}")
    print(f"TSIM cycles: {args.cycles}")
    print(f"Peak throughput: {peak} MAC/cycle")
    print(f"Utilization ratio: {ratio:.12g}")
    print(f"Utilization: {percentage:.12g}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
