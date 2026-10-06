# Checkpoint 1: Reproducible SWW conversion

Status: **GREEN**

The dedicated `.envs/sww-env` environment was created with Python 3.11 and the
unmodified upstream `streaming_wakeword/requirements.txt`. The maintained
conversion command adapts the upstream `quantize.py` in a temporary file next
to its Python modules, retains its model-loading and TFLite-conversion logic,
and omits calibration loading and the INT8 conversion block. The H5 and the
temporary adapter remain outside the application tree.

The application-owned float32 model is
`vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model/str_ww_ref_model_float32.tflite`.
FlatBuffer checks confirm float32 input/output, float32 weights/activations,
one int32 reshape shape constant, and no quantized tensor or operator. The
existing int8 model is retained until the C2 atomic model migration.

Commands and output hashes are in [RESULTS.md](RESULTS.md). C2 owns both model
deployments and the real VTA workload gate.

## Task 1R reconciliation

Status: **GREEN**. The user corrected the KWS source to the existing
`keyword_spotting/trained_models/kws_ref_model/` SavedModel; the neighboring
README's AWW names are stale and are not used to locate the model. The
existing `.envs/sww-env` exported it with default float conversion to
`kws_ref_model_float32.tflite`. The SavedModel signature and all 56 learned
variables are float32. The TFLite FlatBuffer has float32 input `[1,49,10,1]`,
float32 output `[1,12]`, and no quantization metadata. TVM imported it
successfully as Relay with a float32 `[1,12]` result.

The SWW artifact and every live app/default reference now use
`str_ww_ref_model_float32.tflite`. The asset bytes and SHA-256 are unchanged
from the earlier conversion; its corrected-path suite, CPU deployment, and
FSIM deployment/workload export were rerun. Full hashes and commands are in
[RESULTS.md](RESULTS.md). The former KWS importer failure applies only to the
superseded float-I/O asset; C2 must continue with the replacement and repeat
both-model deployment/workload acceptance.
