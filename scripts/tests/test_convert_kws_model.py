import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/convert_kws_model.py"


def load_converter():
    spec = importlib.util.spec_from_file_location("convert_kws_model", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_kws_source_is_the_confirmed_saved_model_directory():
    converter = load_converter()
    assert converter.SOURCE_MODEL.name == "kws_ref_model"
    assert converter.SOURCE_MODEL.is_dir()
    assert (converter.SOURCE_MODEL / "saved_model.pb").is_file()


def test_converter_defaults_to_float32_model_output():
    converter = load_converter()
    args = converter.build_parser().parse_args([])
    assert args.model == converter.SOURCE_MODEL
    assert args.output.name == "kws_ref_model_float32.tflite"


def test_converter_rejects_missing_saved_model(tmp_path):
    converter = load_converter()
    try:
        converter.convert(tmp_path / "missing", tmp_path / "out.tflite")
    except FileNotFoundError as error:
        assert "SavedModel not found" in str(error)
    else:
        raise AssertionError("missing SavedModel was accepted")


def test_converter_rejects_tflite_file_as_source(tmp_path):
    converter = load_converter()
    source = tmp_path / "model.tflite"
    source.write_bytes(b"not a SavedModel")
    try:
        converter.convert(source, tmp_path / "out.tflite")
    except ValueError as error:
        assert "SavedModel directory" in str(error)
    else:
        raise AssertionError("TFLite source was accepted")
