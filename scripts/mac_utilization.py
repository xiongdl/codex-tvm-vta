#!/usr/bin/env python3
"""Calculate useful MAC utilization from explicit inputs or deployment evidence."""

import argparse
import hashlib
import json
import math
import os
import re
from pathlib import Path


DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "vta" / "config" / "vta_64mac.json"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
PROTOCOL_NAME = "tsim_single_call"
PROTOCOL_VERSION = 1


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
    batch, block = 2 ** exponents["LOG_BATCH"], 2 ** exponents["LOG_BLOCK"]
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


def _positive_integer(obj, name, location):
    value = obj.get(name) if isinstance(obj, dict) else None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{location}.{name} must be a positive integer")
    return value


def _nonnegative_integer(value, location):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{location} must be a non-negative integer")
    return value


def _hash(value, location):
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        raise ValueError(f"{location} must be a lowercase SHA-256 hex digest")
    return value


def _read_json(path, description):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read {description} {path}: {error}") from error


def _file_hash(path, description):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError as error:
        raise ValueError(f"cannot read {description} {path}: {error}") from error


def _safe_artifact_path(directory, name, description):
    if not isinstance(name, str) or not name or Path(name).name != name:
        raise ValueError(f"{description} must be a local filename")
    path = directory / name
    if not path.is_file():
        raise ValueError(f"{description} is missing: {path}")
    return path


def _validate_selected_manifest(report):
    manifest_path = report.get("selected_manifest")
    if not isinstance(manifest_path, str) or not manifest_path:
        raise ValueError("deployment report selected_manifest path is required")
    expected_hash = _hash(report.get("selected_manifest_sha256"), "selected_manifest_sha256")
    if _file_hash(manifest_path, "selected schedule manifest") != expected_hash:
        raise ValueError("selected schedule manifest SHA-256 does not match deployment report")
    manifest_path = Path(manifest_path).resolve(strict=True)
    manifest = _read_json(manifest_path, "selected schedule manifest")
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported selected schedule manifest schema")
    if manifest.get("model_sha256") != report["model_sha256"]:
        raise ValueError("selected schedule manifest model identity does not match deployment report")
    if manifest.get("geometry_sha256") != report["geometry"]["sha256"]:
        raise ValueError("selected schedule manifest geometry does not match deployment report")
    protocol = manifest.get("measurement_protocol")
    if (not isinstance(protocol, dict) or protocol.get("name") != PROTOCOL_NAME
            or protocol.get("version") != PROTOCOL_VERSION
            or protocol.get("warmup_excluded") is not True):
        raise ValueError("selected schedule manifest has a mismatched TSIM measurement protocol")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or len(entries) != manifest.get("workload_count"):
        raise ValueError("selected schedule manifest has incomplete workload coverage")
    by_occurrence = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("selected schedule manifest entries must be objects")
        index = _nonnegative_integer(entry.get("occurrence"), "manifest entry occurrence")
        if index in by_occurrence:
            raise ValueError("selected schedule manifest occurrence identities are duplicated")
        result_path = _safe_artifact_path(manifest_path.parent, entry.get("result_json"), "selected result JSON")
        result = _read_json(result_path, "selected result JSON")
        if result.get("schema_version") != 1 or result.get("model_sha256") != report["model_sha256"]:
            raise ValueError(f"selected result identity is malformed at occurrence {index}")
        if result.get("workload_index") != entry.get("workload_index"):
            raise ValueError(f"selected result workload index mismatch at occurrence {index}")
        if result.get("occurrence") != index or result.get("symbol") != entry.get("symbol"):
            raise ValueError(f"selected result occurrence identity mismatch at occurrence {index}")
        if result.get("fusion_sha256") != entry.get("fusion_sha256"):
            raise ValueError(f"selected result fusion identity mismatch at occurrence {index}")
        if result.get("tsim_cycles") != entry.get("tsim_cycles"):
            raise ValueError(f"selected result AutoTVM cycles mismatch at occurrence {index}")
        config = result.get("conv_config")
        if not isinstance(config, dict):
            raise ValueError(f"selected result config is missing at occurrence {index}")
        config_hash = hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        record = _safe_artifact_path(
            manifest_path.parent, result.get("best_native_record"), "selected native record"
        )
        record_hash = _hash(result.get("best_native_record_sha256"), "best_native_record_sha256")
        if _file_hash(record, "selected native record") != record_hash:
            raise ValueError(f"selected native record SHA-256 mismatch at occurrence {index}")
        by_occurrence[index] = {
            "symbol": entry["symbol"],
            "fusion_sha256": entry["fusion_sha256"],
            "workload_sha256": result.get("workload_sha256"),
            "autotvm_cycles": result["tsim_cycles"],
            "logical_macs": _positive_integer(result, "mac_count", f"selected result {index}"),
            "config_sha256": config_hash,
        }
    return manifest, by_occurrence


def calculate_deployment_report(report):
    """Validate deployment evidence and calculate per-occurrence/model metrics."""
    if not isinstance(report, dict) or report.get("schema_version") != 1:
        raise ValueError("unsupported deployment report schema_version")
    if report.get("artifact_kind") != "vta_deployment_profile_v1":
        raise ValueError("unsupported deployment report artifact_kind")
    for name in ("model_id",):
        if not isinstance(report.get(name), str) or not report[name].strip():
            raise ValueError(f"deployment report {name} must be a non-empty string")
    model_hash = _hash(report.get("model_sha256"), "model_sha256")
    if report.get("backend") != "tsim":
        raise ValueError("deployment report backend must be tsim")
    geometry = report.get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("deployment report geometry must be an object")
    geometry_hash = _hash(geometry.get("sha256"), "geometry.sha256")
    geometry_path = geometry.get("path")
    if not isinstance(geometry_path, str) or not geometry_path:
        raise ValueError("deployment report geometry.path is required")
    if _file_hash(geometry_path, "geometry JSON") != geometry_hash:
        raise ValueError("deployment report geometry SHA-256 does not match referenced JSON")
    peak = load_peak_macs_per_cycle(geometry_path)
    if _positive_integer(geometry, "peak_macs_per_cycle", "geometry") != peak:
        raise ValueError("deployment report peak MACs/cycle does not match geometry")
    protocol = report.get("measurement_protocol")
    if (not isinstance(protocol, dict) or protocol.get("name") != PROTOCOL_NAME
            or protocol.get("version") != PROTOCOL_VERSION
            or protocol.get("warmup_excluded") is not True):
        raise ValueError("deployment report requires the TSIM single-call v1 protocol")
    operator_invocations = _positive_integer(
        protocol, "operator_counted_invocations", "measurement_protocol"
    )
    full_invocations = _positive_integer(
        protocol, "full_model_counted_invocations", "measurement_protocol"
    )
    full_model = report.get("full_model")
    if not isinstance(full_model, dict):
        raise ValueError("deployment report full_model must be an object")
    if _positive_integer(full_model, "invocation_count", "full_model") != full_invocations:
        raise ValueError("full-model invocation count does not match measurement protocol")
    baseline_cycles = _positive_integer(full_model, "baseline_cycles", "full_model")
    tuned_cycles = _positive_integer(full_model, "tuned_cycles", "full_model")
    scope = report.get("scope")
    if not isinstance(scope, dict) or scope.get("full_model_cycles") != "uninstrumented_complete_deployment":
        raise ValueError("full-model cycles must come from an uninstrumented complete deployment")
    if scope.get("host_operations") != "excluded_from_vta_mac_totals":
        raise ValueError("deployment report must identify host operations as excluded")

    manifest, selected = _validate_selected_manifest(report)
    occurrences = report.get("occurrences")
    if not isinstance(occurrences, list) or not occurrences:
        raise ValueError("deployment report occurrences must be a non-empty list")
    if len(occurrences) != len(selected):
        raise ValueError("deployment report operator coverage does not match selected manifest")
    seen = set()
    rows = []
    per_model_mac_count = 0
    operator_cycle_sum_per_invocation = 0.0
    for position, item in enumerate(occurrences):
        location = f"occurrences[{position}]"
        if not isinstance(item, dict):
            raise ValueError(f"{location} must be an object")
        occurrence = _positive_integer(item, "occurrence", location) - 1
        symbol = item.get("symbol")
        if not isinstance(symbol, str) or not symbol:
            raise ValueError(f"{location}.symbol is required")
        if occurrence in seen:
            raise ValueError("occurrence identity must be unique")
        seen.add(occurrence)
        reference = selected.get(occurrence)
        if reference is None:
            raise ValueError(f"deployment report has unknown occurrence {occurrence}")
        for name in ("fusion_sha256", "workload_sha256", "config_sha256"):
            _hash(item.get(name), f"{location}.{name}")
        if (item["symbol"] != reference["symbol"]
                or item["fusion_sha256"] != reference["fusion_sha256"]
                or item["workload_sha256"] != reference["workload_sha256"]
                or item["config_sha256"] != reference["config_sha256"]):
            raise ValueError(f"deployment and selected config identity mismatch at occurrence {occurrence}")
        macs = _positive_integer(item, "logical_macs_per_invocation", location)
        measured_count = _positive_integer(item, "counted_invocations", location)
        deployed_cycle_count = _positive_integer(item, "deployment_cycles", location)
        autotvm_cycles = _positive_integer(item, "autotvm_cycles", location)
        if measured_count != operator_invocations:
            raise ValueError(f"{location} invocation count does not match measurement protocol")
        if autotvm_cycles != reference["autotvm_cycles"]:
            raise ValueError(f"{location} AutoTVM cycles do not match selected native record")
        if macs != reference["logical_macs"]:
            raise ValueError(f"{location} logical MAC count does not match selected result")
        deployed_per_invocation = deployed_cycle_count / measured_count
        difference = abs(deployed_per_invocation - autotvm_cycles) / autotvm_cycles
        if difference > 0.10:
            raise ValueError(
                f"occurrence {occurrence} deployment versus AutoTVM cycles exceeds 10%: "
                f"deployment={deployed_per_invocation:g}, autotvm={autotvm_cycles}, "
                f"relative={difference:.6%}"
            )
        saved_difference = item.get("relative_cycle_difference")
        if (isinstance(saved_difference, bool) or not isinstance(saved_difference, (int, float))
                or not math.isfinite(saved_difference) or abs(saved_difference - difference) > 1e-12):
            raise ValueError(f"{location}.relative_cycle_difference is inconsistent")
        op_macs = macs * measured_count
        op_ratio, op_percent = calculate_utilization(op_macs, deployed_cycle_count, peak)
        if op_ratio > 1.0 + 1e-12:
            raise ValueError(f"{location} utilization exceeds 100%; check MAC and cycle units")
        per_model_mac_count += macs * full_invocations
        operator_cycle_sum_per_invocation += deployed_per_invocation
        rows.append({
            "occurrence": occurrence,
            "symbol": symbol,
            "workload_sha256": item["workload_sha256"],
            "config_sha256": item["config_sha256"],
            "logical_macs_per_invocation": macs,
            "counted_invocations": measured_count,
            "logical_macs_measured": op_macs,
            "deployment_cycles_measured": deployed_cycle_count,
            "deployment_cycles_per_invocation": deployed_per_invocation,
            "autotvm_cycles_per_invocation": autotvm_cycles,
            "relative_cycle_difference": difference,
            "utilization_ratio": op_ratio,
            "utilization_percent": op_percent,
        })
    if len(seen) != len(selected):
        raise ValueError("deployment report has incomplete occurrence coverage")
    baseline_ratio, baseline_percent = calculate_utilization(per_model_mac_count, baseline_cycles, peak)
    tuned_ratio, tuned_percent = calculate_utilization(per_model_mac_count, tuned_cycles, peak)
    if baseline_ratio > 1.0 + 1e-12 or tuned_ratio > 1.0 + 1e-12:
        raise ValueError("whole-model utilization exceeds 100%; check MAC and cycle units")
    baseline_per_invocation = baseline_cycles / full_invocations
    tuned_per_invocation = tuned_cycles / full_invocations
    if operator_cycle_sum_per_invocation > tuned_per_invocation + 1e-9:
        raise ValueError("tuned operator cycle sum exceeds actual full-model cycles")
    return {
        "schema_version": 1,
        "artifact_kind": "deployment_mac_utilization_v1",
        "model_id": report["model_id"],
        "model_sha256": model_hash,
        "backend": "tsim",
        "geometry": {"sha256": geometry_hash, "peak_macs_per_cycle": peak},
        "scope": scope,
        "measurement_protocol": protocol,
        "whole_model": {
            "invocation_count": full_invocations,
            "logical_macs_per_invocation": per_model_mac_count // full_invocations,
            "logical_macs": per_model_mac_count,
            "baseline_cycles": baseline_cycles,
            "tuned_cycles": tuned_cycles,
            "baseline_cycles_per_invocation": baseline_per_invocation,
            "tuned_cycles_per_invocation": tuned_per_invocation,
            "baseline_utilization_ratio": baseline_ratio,
            "baseline_utilization_percent": baseline_percent,
            "tuned_utilization_ratio": tuned_ratio,
            "tuned_utilization_percent": tuned_percent,
            "tuned_operator_cycle_sum_per_invocation": operator_cycle_sum_per_invocation,
            "tuned_residual_cycles_per_invocation": (
                tuned_per_invocation - operator_cycle_sum_per_invocation
            ),
            "cycle_speedup": baseline_cycles / tuned_cycles,
        },
        "occurrences": rows,
        "selected_manifest": str(Path(report["selected_manifest"]).resolve()),
        "selected_manifest_sha256": report["selected_manifest_sha256"],
    }


def _write_json(path, value):
    output = Path(path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    return output


def build_parser():
    parser = argparse.ArgumentParser(
        description="Calculate useful MAC utilization from a TSIM deployment report or explicit scalar inputs."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--deployment-report", type=Path, help="versioned real-deployment JSON artifact")
    source.add_argument("--macs", type=positive_integer, help="explicit logical MAC count")
    parser.add_argument("--cycles", type=positive_integer, help="explicit positive TSIM cycle count")
    parser.add_argument("--config", type=Path, help="VTA geometry JSON for scalar mode")
    parser.add_argument("--output-json", type=Path, help="write a machine-readable JSON result")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.deployment_report is not None:
            if args.cycles is not None or args.config is not None:
                raise ValueError("--deployment-report cannot be combined with --cycles or --config")
            source = _read_json(args.deployment_report, "deployment report")
            result = calculate_deployment_report(source)
            model = result["whole_model"]
            print(f"Model: {result['model_id']} ({result['model_sha256']})")
            print("Scope: actual full-model TSIM cycles; host operations excluded")
            print(f"Occurrences: {len(result['occurrences'])}")
            for item in result["occurrences"]:
                print(
                    f"Occurrence {item['occurrence']} ({item['symbol']}): "
                    f"MACs={item['logical_macs_per_invocation']}, "
                    f"deployment cycles/invocation={item['deployment_cycles_per_invocation']:g}, "
                    f"AutoTVM cycles={item['autotvm_cycles_per_invocation']}, "
                    f"difference={item['relative_cycle_difference']:.6%}, "
                    f"utilization={item['utilization_percent']:.12g}%"
                )
            print(f"Baseline full-model cycles: {model['baseline_cycles']}")
            print(f"Baseline whole-model utilization: {model['baseline_utilization_percent']:.12g}%")
            print(f"Tuned full-model cycles: {model['tuned_cycles']}")
            print(f"Tuned whole-model utilization: {model['tuned_utilization_percent']:.12g}%")
            print(f"Tuned/baseline cycle speedup: {model['cycle_speedup']:.12g}x")
            print("JSON:")
        else:
            if args.cycles is None:
                raise ValueError("scalar mode requires --cycles with --macs")
            peak = load_peak_macs_per_cycle(args.config or DEFAULT_CONFIG)
            ratio, percentage = calculate_utilization(args.macs, args.cycles, peak)
            result = {
                "artifact_kind": "explicit_scalar_calculation_v1",
                "measurement_scope": "explicit user-provided scalar inputs",
                "macs": args.macs,
                "cycles": args.cycles,
                "peak_macs_per_cycle": peak,
                "utilization_ratio": ratio,
                "utilization_percent": percentage,
            }
            print(f"MACs: {args.macs}")
            print(f"TSIM cycles: {args.cycles}")
            print(f"Peak throughput: {peak} MAC/cycle")
            print(f"Utilization ratio: {ratio:.12g}")
            print(f"Utilization: {percentage:.12g}%")
            if args.output_json:
                print("JSON:")
        if args.output_json:
            _write_json(args.output_json, result)
        if args.output_json or args.deployment_report:
            print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
