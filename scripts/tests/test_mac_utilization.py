"""Focused tests for the model-independent MAC utilization CLI."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "mac_utilization.py"
CONFIG = ROOT / "vta" / "config" / "vta_64mac.json"


def load_module():
    spec = importlib.util.spec_from_file_location("mac_utilization", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


if __name__ == "__main__":
    unittest.main()
