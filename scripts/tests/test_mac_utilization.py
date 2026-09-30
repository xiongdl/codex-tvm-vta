"""Focused tests for the model-independent MAC utilization CLI."""

import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "mac_utilization.py"
CONFIG = ROOT / "vta" / "config" / "vta_64mac.json"
PROJECT_PYTHON = ROOT / ".envs" / "tvm-vta-env" / "bin" / "python"


def load_module():
    spec = importlib.util.spec_from_file_location("mac_utilization", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_deployment_fixture(directory, deployment_cycles=(180, 202)):
    """Write a generic model report and the referenced selected-schedule evidence."""
    directory = Path(directory)
    geometry = directory / "geometry.json"
    geometry.write_text(json.dumps({"LOG_BATCH": 0, "LOG_BLOCK": 3}), encoding="utf-8")
    geometry_hash = hashlib.sha256(geometry.read_bytes()).hexdigest()
    entries = []
    occurrences = []
    for index, cycles in enumerate(deployment_cycles):
        config = {"tile": index + 1}
        config_hash = hashlib.sha256(
            json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        native = directory / f"best-{index}.log"
        native.write_text(f"native record {index}", encoding="utf-8")
        native_hash = hashlib.sha256(native.read_bytes()).hexdigest()
        result = {
            "schema_version": 1,
            "model": "unrelated-model-id",
            "model_sha256": "a" * 64,
            "workload_index": index,
            "occurrence": index,
            "symbol": f"fusion_{index}",
            "fusion_sha256": hashlib.sha256(f"fusion-{index}".encode()).hexdigest(),
            "workload_sha256": hashlib.sha256(b"same-repeated-workload").hexdigest(),
            "conv_config": config,
            "tsim_cycles": 100,
            "mac_count": 1000,
            "best_native_record": native.name,
            "best_native_record_sha256": native_hash,
        }
        result_path = directory / f"result-{index}.json"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        entries.append({
            "workload_index": index,
            "occurrence": index,
            "symbol": f"fusion_{index}",
            "fusion_sha256": hashlib.sha256(f"fusion-{index}".encode()).hexdigest(),
            "result_json": result_path.name,
            "tsim_cycles": 100,
        })
        occurrences.append({
            "occurrence": index + 1,
            "symbol": f"fusion_{index}",
            "fusion_sha256": hashlib.sha256(f"fusion-{index}".encode()).hexdigest(),
            "workload_sha256": hashlib.sha256(b"same-repeated-workload").hexdigest(),
            "config_sha256": config_hash,
            "logical_macs_per_invocation": 1000,
            "counted_invocations": 2,
            "deployment_cycles": cycles,
            "autotvm_cycles": 100,
            "relative_cycle_difference": abs(cycles / 2 - 100) / 100,
        })
    manifest = {
        "schema_version": 1,
        "model": "unrelated-model-id",
        "model_sha256": "a" * 64,
        "geometry_sha256": geometry_hash,
        "measurement_protocol": {
            "name": "tsim_single_call", "version": 1, "warmup_excluded": True
        },
        "workload_count": len(entries),
        "entries": entries,
    }
    manifest_path = directory / "best-manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    report = {
        "schema_version": 1,
        "artifact_kind": "vta_deployment_profile_v1",
        "model_id": "unrelated-model-id",
        "model_sha256": "a" * 64,
        "geometry": {
            "path": str(geometry), "sha256": geometry_hash, "peak_macs_per_cycle": 64
        },
        "backend": "tsim",
        "measurement_protocol": {
            "name": "tsim_single_call", "version": 1, "warmup_excluded": True,
            "operator_counted_invocations": 2, "full_model_counted_invocations": 2,
        },
        "full_model": {
            "invocation_count": 2, "baseline_cycles": 2000, "tuned_cycles": 1000
        },
        "occurrences": occurrences,
        "scope": {
            "full_model_cycles": "uninstrumented_complete_deployment",
            "host_operations": "excluded_from_vta_mac_totals",
        },
        "selected_manifest": str(manifest_path),
        "selected_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
    }
    report_path = directory / "deployment.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    return report_path


class MacUtilizationTests(unittest.TestCase):
    def test_standard_geometry_has_64_macs_per_cycle(self):
        module = load_module()

        self.assertEqual(module.load_peak_macs_per_cycle(CONFIG), 64)

    def test_calculation_returns_ratio_and_percentage(self):
        module = load_module()

        ratio, percentage = module.calculate_utilization(128, 4, 64)

        self.assertEqual(ratio, 0.5)
        self.assertEqual(percentage, 50.0)

    def test_cli_prints_inputs_peak_ratio_and_percentage_with_units(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--macs", "128", "--cycles", "4"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MACs: 128", result.stdout)
        self.assertIn("TSIM cycles: 4", result.stdout)
        self.assertIn("Peak throughput: 64 MAC/cycle", result.stdout)
        self.assertIn("Utilization ratio: 0.5", result.stdout)
        self.assertIn("Utilization: 50%", result.stdout)

    def test_import_does_not_load_tvm_or_model_modules(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import runpy, sys; runpy.run_path(sys.argv[1]); "
                "assert not any(name == 'tvm' or name.startswith('tvm.') "
                "for name in sys.modules); "
                "assert not any('mlperf' in name or 'autotvm' in name "
                "for name in sys.modules)",
                str(SCRIPT),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_invalid_integer_arguments_without_result(self):
        for args in (
            ("--macs", "0", "--cycles", "1"),
            ("--macs", "-1", "--cycles", "1"),
            ("--macs", "1.5", "--cycles", "1"),
            ("--macs", "1", "--cycles", "0"),
            ("--macs", "1", "--cycles", "-1"),
            ("--macs", "1", "--cycles", "2.5"),
        ):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), *args],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Utilization ratio:", result.stdout)
                self.assertNotIn("Utilization:", result.stdout)

    def test_rejects_malformed_or_incomplete_geometry(self):
        invalid_configs = ("{not json", '{"LOG_BATCH": 0}', '{"LOG_BATCH": -1, '
                           '"LOG_BLOCK": 3}')

        for config_text in invalid_configs:
            with self.subTest(config_text=config_text):
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
                    f.write(config_text)
                    f.flush()
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(SCRIPT),
                            "--macs",
                            "1",
                            "--cycles",
                            "1",
                            "--config",
                            f.name,
                        ],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Utilization ratio:", result.stdout)
                self.assertNotIn("Utilization:", result.stdout)

    def test_rejects_geometry_with_non_integer_exponents(self):
        module = load_module()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            json.dump({"LOG_BATCH": 0, "LOG_BLOCK": 3.5}, f)
            f.flush()
            with self.assertRaises(ValueError):
                module.load_peak_macs_per_cycle(f.name)

    def test_deployment_report_supports_unrelated_models_repeated_workloads_and_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = build_deployment_fixture(directory)
            result = subprocess.run(
                [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = json.loads(result.stdout[result.stdout.index("{\n"):])
        self.assertEqual(parsed["model_id"], "unrelated-model-id")
        self.assertEqual(len(parsed["occurrences"]), 2)
        self.assertEqual(parsed["whole_model"]["logical_macs"], 4000)
        self.assertEqual(parsed["whole_model"]["tuned_cycles"], 1000)
        self.assertEqual(parsed["whole_model"]["tuned_utilization_ratio"], 4000 / (1000 * 64))
        self.assertEqual(parsed["occurrences"][0]["deployment_cycles_per_invocation"], 90)
        self.assertEqual(parsed["occurrences"][0]["relative_cycle_difference"], 0.1)

    def test_deployment_mode_writes_machine_readable_json(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = build_deployment_fixture(directory)
            output_path = Path(directory) / "utilization.json"
            result = subprocess.run(
                [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path),
                 "--output-json", str(output_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output_path.read_text()), json.loads(result.stdout[result.stdout.index("{\n"):]))

    def test_deployment_report_rejects_over_ten_percent_and_mixed_modes(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = build_deployment_fixture(directory, deployment_cycles=(222, 202))
            result = subprocess.run(
                [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            mixed = subprocess.run(
                [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path),
                 "--macs", "10", "--cycles", "1"],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceeds 10%", result.stderr)
        self.assertNotEqual(mixed.returncode, 0)

    def test_deployment_report_rejects_stale_manifest_and_incomplete_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = build_deployment_fixture(directory)
            report = json.loads(report_path.read_text())
            manifest_path = Path(report["selected_manifest"])
            manifest_path.write_text("{}", encoding="utf-8")
            stale = subprocess.run(
                [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
            report_path = build_deployment_fixture(directory)
            report = json.loads(report_path.read_text())
            report["occurrences"].pop()
            report_path.write_text(json.dumps(report), encoding="utf-8")
            incomplete = subprocess.run(
                [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )

        self.assertNotEqual(stale.returncode, 0)
        self.assertNotEqual(incomplete.returncode, 0)

    def test_deployment_report_rejects_config_or_cycle_association_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = build_deployment_fixture(directory)
            original = json.loads(report_path.read_text())
            for field, value in (("config_sha256", "f" * 64), ("autotvm_cycles", 101)):
                with self.subTest(field=field):
                    report = json.loads(json.dumps(original))
                    report["occurrences"][0][field] = value
                    report_path.write_text(json.dumps(report), encoding="utf-8")
                    result = subprocess.run(
                        [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path)],
                        cwd=ROOT, capture_output=True, text=True, check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("selected", result.stderr)

    def test_deployment_report_rejects_utilization_over_one_hundred_percent(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = build_deployment_fixture(directory)
            report = json.loads(report_path.read_text())
            report["occurrences"][0]["logical_macs_per_invocation"] = 10**9
            manifest_path = Path(report["selected_manifest"])
            manifest = json.loads(manifest_path.read_text())
            result_path = manifest_path.parent / manifest["entries"][0]["result_json"]
            selected_result = json.loads(result_path.read_text())
            selected_result["mac_count"] = 10**9
            result_path.write_text(json.dumps(selected_result), encoding="utf-8")
            report_path.write_text(json.dumps(report), encoding="utf-8")
            result = subprocess.run(
                [str(PROJECT_PYTHON), str(SCRIPT), "--deployment-report", str(report_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("utilization exceeds 100%", result.stderr)

    def test_deployment_help_exposes_report_and_json_options(self):
        result = subprocess.run(
            [str(PROJECT_PYTHON), str(SCRIPT), "--help"], cwd=ROOT,
            capture_output=True, text=True, check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--deployment-report", result.stdout)
        self.assertIn("--output-json", result.stdout)


if __name__ == "__main__":
    unittest.main()
