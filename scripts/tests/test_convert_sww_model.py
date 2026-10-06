import importlib.util
from pathlib import Path
import shutil
import subprocess
import uuid


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/convert_sww_model.py"
SETUP = ROOT / "scripts/setup_sww_env.sh"
PROJECT_PYTHON = ROOT / ".envs/tvm-vta-env/bin/python"


def load_converter():
    spec = importlib.util.spec_from_file_location("convert_sww_model", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_upstream_adaptation_uses_float_defaults_without_calibration():
    converter = load_converter()
    adapted = converter.adapt_upstream(converter.UPSTREAM_SCRIPT.read_text(encoding="utf-8"))

    assert 'parser.add_argument("--saved_model_path", required=True)' in adapted
    assert 'parser.add_argument("--tfl_file_name", required=True)' in adapted
    assert 'np.load("calibration_samples.npz")' not in adapted
    assert "converter.optimizations" not in adapted
    assert "TFLITE_BUILTINS_INT8" not in adapted


def test_converter_uses_the_corrected_float32_output_name():
    converter = load_converter()
    args = converter.build_parser().parse_args([])
    assert args.output.name == "str_ww_ref_model_float32.tflite"
    assert converter.FLOAT_OUTPUT_NAME == args.output.name


def test_converter_rejects_non_h5_input_before_running_tensorflow(tmp_path):
    converter = load_converter()
    try:
        converter.convert(tmp_path / "model.tflite", tmp_path / "out.tflite")
    except ValueError as error:
        assert "must name an H5 file" in str(error)
    else:
        raise AssertionError("non-H5 source was accepted")


def test_converter_reports_missing_h5_source(tmp_path):
    converter = load_converter()
    try:
        converter.convert(tmp_path / "missing.h5", tmp_path / "out.tflite")
    except FileNotFoundError as error:
        assert "source model not found" in str(error)
    else:
        raise AssertionError("missing source was accepted")


def test_setup_help_and_invalid_environment_name():
    help_result = subprocess.run(["bash", str(SETUP), "--help"], capture_output=True, text=True)
    assert help_result.returncode == 0
    assert "--env-name NAME" in help_result.stdout

    invalid = subprocess.run(
        ["bash", str(SETUP), "--env-name", "../outside"], capture_output=True, text=True
    )
    assert invalid.returncode != 0
    assert "invalid environment name" in invalid.stderr

    for args, message in ((["--env-name"], "requires a value"), (["--unknown"], "unknown option")):
        rejected = subprocess.run(["bash", str(SETUP), *args], capture_output=True, text=True)
        assert rejected.returncode != 0
        assert message in rejected.stderr


def test_setup_reuses_existing_prefix_without_removing_contents():
    env_name = f"sww-reuse-test-{uuid.uuid4().hex}"
    prefix = ROOT / ".envs" / env_name
    python = prefix / "bin/python"
    sentinel = prefix / "sentinel"
    try:
        python.parent.mkdir(parents=True)
        python.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        python.chmod(0o755)
        sentinel.write_text("keep", encoding="utf-8")

        result = subprocess.run(
            ["bash", str(SETUP), "--env-name", env_name], capture_output=True, text=True
        )

        assert result.returncode == 0, result.stderr
        assert "Reusing existing environment" in result.stdout
        assert sentinel.read_text(encoding="utf-8") == "keep"
    finally:
        shutil.rmtree(prefix, ignore_errors=True)
