#!/usr/bin/env python3
"""Run upstream SWW quantize.py's floating-point TFLite conversion branch."""

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
TRAINING = ROOT / ".envs/tiny-v1.4/benchmark/training/streaming_wakeword"
SOURCE_MODEL = TRAINING / "trained_models/str_ww_ref_model.h5"
UPSTREAM_SCRIPT = TRAINING / "quantize.py"
OUTPUT_MODEL = (
    ROOT
    / "vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model/str_ww_ref_model_float32.tflite"
)
FLOAT_OUTPUT_NAME = "str_ww_ref_model_float32.tflite"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def adapt_upstream(source):
    """Disable calibration and the upstream INT8 block while retaining its converter path."""
    source = source.replace("import str_ww_util as util\n", "", 1)
    parser_block = '''Flags = util.parse_command("quantize")
pretrained_model_path = Flags.saved_model_path
tfl_file_name = Flags.tfl_file_name
'''
    adapted_parser = '''parser = argparse.ArgumentParser()
parser.add_argument("--saved_model_path", required=True)
parser.add_argument("--tfl_file_name", required=True)
Flags = parser.parse_args()
pretrained_model_path = Flags.saved_model_path
tfl_file_name = Flags.tfl_file_name
'''
    if source.count(parser_block) != 1:
        raise ValueError("upstream quantize.py CLI block changed; refusing an unreviewed adaptation")
    source = source.replace(parser_block, adapted_parser, 1)
    source = source.replace("import os\n", "import os\nimport argparse\n", 1)

    calibration = '''cal_set = np.load("calibration_samples.npz")
cal_specs = cal_set["specs"]
cal_labels = cal_set["labels"]
'''
    if source.count(calibration) != 1:
        raise ValueError("upstream calibration-loading block changed; refusing an unreviewed adaptation")
    source = source.replace(calibration, "", 1)

    int8_start = "if True: \n  # If we omit this block"
    int8_end = "\ntflite_quant_model = converter.convert()"
    if source.count(int8_start) != 1 or source.count(int8_end) != 1:
        raise ValueError("upstream INT8 conversion block changed; refusing an unreviewed adaptation")
    start = source.index(int8_start)
    end = source.index(int8_end, start)
    source = (
        source[:start]
        + "# Float32 branch: keep TensorFlow Lite converter defaults.\n"
        + source[end + 1 :]
    )
    return source


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=SOURCE_MODEL, help="upstream SWW H5 model")
    parser.add_argument("--output", type=Path, default=OUTPUT_MODEL, help="float32 TFLite output path")
    parser.add_argument(
        "--upstream-script", type=Path, default=UPSTREAM_SCRIPT,
        help="upstream quantize.py source used as the adaptation template",
    )
    return parser


def convert(model, output, upstream_script=UPSTREAM_SCRIPT):
    model = Path(model).resolve()
    output = Path(output).resolve()
    upstream_script = Path(upstream_script).resolve()
    if model.suffix.lower() != ".h5":
        raise ValueError(f"--model must name an H5 file: {model}")
    if not model.is_file():
        raise FileNotFoundError(f"SWW source model not found: {model}")
    if not upstream_script.is_file():
        raise FileNotFoundError(f"upstream quantize.py not found: {upstream_script}")
    output.parent.mkdir(parents=True, exist_ok=True)

    adapted = adapt_upstream(upstream_script.read_text(encoding="utf-8"))
    with tempfile.NamedTemporaryFile(
        prefix=".quantize_float32_", suffix=".py", dir=upstream_script.parent, delete=False
    ) as staging:
        adapted_script = Path(staging.name)
    try:
        adapted_script.write_text(adapted, encoding="utf-8")
        command = [
            sys.executable,
            str(adapted_script),
            "--saved_model_path",
            str(model),
            "--tfl_file_name",
            str(output),
        ]
        subprocess.run(command, cwd=upstream_script.parent, check=True)
    finally:
        adapted_script.unlink(missing_ok=True)
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f"upstream conversion did not produce a non-empty model: {output}")
    return output


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        output = convert(args.model, args.output, args.upstream_script)
    except (FileNotFoundError, ValueError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"source_sha256={sha256(args.model)}")
    print(f"upstream_sha256={sha256(args.upstream_script)}")
    print(f"output={output}")
    print(f"output_sha256={sha256(output)}")
    print(f"output_name_matches_request={output.name == FLOAT_OUTPUT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
