# Checkpoint 1: Reproducible SWW conversion

Status: **GREEN**

The dedicated `.envs/sww-env` environment was created with Python 3.11 and the
unmodified upstream `streaming_wakeword/requirements.txt`. The maintained
conversion command adapts the upstream `quantize.py` in a temporary file next
to its Python modules, retains its model-loading and TFLite-conversion logic,
and omits calibration loading and the INT8 conversion block. The H5 and the
temporary adapter remain outside the application tree.

The application-owned float32 model is
`vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model/str_ww_ref_model_floag32.tflite`.
FlatBuffer checks confirm float32 input/output, float32 weights/activations,
one int32 reshape shape constant, and no quantized tensor or operator. The
existing int8 model is retained until the C2 atomic model migration.

Commands and output hashes are in [RESULTS.md](RESULTS.md). C2 owns both model
deployments and the real VTA workload gate.
