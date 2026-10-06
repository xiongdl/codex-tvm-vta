#!/usr/bin/env python3
"""Export the MLPerf Tiny KWS SavedModel as an unquantized float32 TFLite model."""

import argparse
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MODEL = (
    ROOT
    / ".envs/tiny-v1.4/benchmark/training/keyword_spotting/trained_models/kws_ref_model"
)
OUTPUT_MODEL = (
    ROOT
    / "vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/model/kws_ref_model_float32.tflite"
)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def saved_model_files(path):
    path = Path(path)
    if path.is_file():
        raise ValueError(f"--model must be a SavedModel directory, not a file: {path}")
    if not path.is_dir() or not (path / "saved_model.pb").is_file():
        raise FileNotFoundError(f"KWS SavedModel not found: {path}")
    files = sorted(file for file in path.rglob("*") if file.is_file())
    if not files:
        raise ValueError(f"KWS SavedModel directory is empty: {path}")
    return files


def validate_signature(loaded):
    signatures = loaded.signatures
    if "serving_default" not in signatures:
        raise ValueError("KWS SavedModel has no serving_default signature")
    function = signatures["serving_default"]
    inputs = function.structured_input_signature[1]
    outputs = function.structured_outputs
    if len(inputs) != 1 or len(outputs) != 1:
        raise ValueError("KWS serving_default must expose exactly one input and one output")
    input_spec = next(iter(inputs.values()))
    output_spec = next(iter(outputs.values()))
    if input_spec.dtype.name != "float32" or input_spec.shape.as_list() != [None, 49, 10, 1]:
        raise ValueError(f"unexpected KWS SavedModel input: {input_spec}")
    if output_spec.dtype.name != "float32" or output_spec.shape.as_list() != [None, 12]:
        raise ValueError(f"unexpected KWS SavedModel output: {output_spec}")
    variables = list(loaded.variables)
    if not variables or any(variable.dtype.name != "float32" for variable in variables):
        dtypes = sorted({variable.dtype.name for variable in variables})
        raise ValueError(f"KWS SavedModel learned variables must all be float32, got {dtypes}")
    return input_spec, output_spec, len(variables)


def validate_tflite(path):
    import numpy as np
    import tensorflow as tf

    interpreter = tf.lite.Interpreter(model_path=str(path))
    interpreter.allocate_tensors()
    inputs = interpreter.get_input_details()
    outputs = interpreter.get_output_details()
    if len(inputs) != 1 or len(outputs) != 1:
        raise ValueError("converted KWS TFLite must expose exactly one input and one output")
    input_detail, output_detail = inputs[0], outputs[0]
    if input_detail["dtype"] != np.float32 or input_detail["shape"].tolist() != [1, 49, 10, 1]:
        raise ValueError(f"unexpected converted KWS input: {input_detail}")
    if output_detail["dtype"] != np.float32 or output_detail["shape"].tolist() != [1, 12]:
        raise ValueError(f"unexpected converted KWS output: {output_detail}")
    details = interpreter.get_tensor_details()
    invalid = [(item["name"], item["dtype"].__name__) for item in details
               if item["dtype"] not in (np.dtype("float32"), np.dtype("int32"))]
    if invalid:
        raise ValueError(f"converted KWS contains non-float learned/activation tensors: {invalid}")
    if any(item["quantization_parameters"]["scales"].size for item in details):
        raise ValueError("converted KWS contains quantization metadata")
    return input_detail["name"], output_detail["name"], len(details)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=SOURCE_MODEL, help="KWS SavedModel directory")
    parser.add_argument("--output", type=Path, default=OUTPUT_MODEL, help="float32 TFLite output path")
    return parser


def convert(model, output):
    model = Path(model).resolve()
    output = Path(output).resolve()
    files = saved_model_files(model)
    import tensorflow as tf

    loaded = tf.saved_model.load(str(model))
    input_spec, output_spec, variable_count = validate_signature(loaded)
    converter = tf.lite.TFLiteConverter.from_saved_model(str(model))
    # Keep TensorFlow Lite's default float conversion: no Optimize.DEFAULT,
    # representative dataset, training, or weight rewriting.
    data = converter.convert()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    input_name, output_name, tensor_count = validate_tflite(output)
    return {
        "source_files": files,
        "output": output,
        "input_signature": input_spec,
        "output_signature": output_spec,
        "variable_count": variable_count,
        "input_name": input_name,
        "output_name": output_name,
        "tensor_count": tensor_count,
    }


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        result = convert(args.model, args.output)
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"source={args.model.resolve()}")
    for source in result["source_files"]:
        print(f"source_file_sha256={source.relative_to(args.model.resolve())} {sha256(source)}")
    print(f"output={result['output']}")
    print(f"output_sha256={sha256(result['output'])}")
    print(f"saved_variables_float32={result['variable_count']}")
    print(f"input={result['input_name']} float32 [1, 49, 10, 1]")
    print(f"output_tensor={result['output_name']} float32 [1, 12]")
    print(f"tflite_tensor_count={result['tensor_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
