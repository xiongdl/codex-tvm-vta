# Checkpoint 1 results

## Task 1R reconciliation (current)

KWS was regenerated from the actual upstream SavedModel directory
`.envs/tiny-v1.4/benchmark/training/keyword_spotting/trained_models/kws_ref_model/`.
The adjacent `trained_models/README.md` describes the model under stale AWW
names; the deployed source is the `kws_ref_model/` SavedModel. Using the
existing `.envs/sww-env`:

```bash
.envs/sww-env/bin/python scripts/convert_kws_model.py
```

The export used `TFLiteConverter.from_saved_model` defaults. No training,
`Optimize.DEFAULT`, calibration, representative data, or weight rewriting was
used. The SavedModel signature is float32 `[None,49,10,1]` to float32
`[None,12]`; all 56 learned variables are float32. Conversion produced a
105,296-byte TFLite model with SHA-256
`738a9f29d175aaa3928db9c8281265be5ec3406598fd3d30018b26084a3d5536`.
FlatBuffer inspection found 35 tensors, 13 operators, only float32 learned
weights/activations plus one int32 reshape shape constant, and no quantization
metadata. TVM `relay.frontend.from_tflite` and `InferType` succeeded; Relay
output is float32 `[1,12]`.

The TFLite frontend import check used the project TVM environment and pinned
TFLite schema:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" .envs/tvm-vta-env/bin/python - <<'PY'
from pathlib import Path
import tflite
from tvm import relay
path = Path('vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/model/kws_ref_model_float32.tflite')
model = tflite.Model.GetRootAsModel(path.read_bytes(), 0)
mod, params = relay.frontend.from_tflite(
    model, shape_dict={'serving_default_input_1:0': (1, 49, 10, 1)},
    dtype_dict={'serving_default_input_1:0': 'float32'})
mod = relay.transform.InferType()(mod)
assert mod['main'].ret_type.dtype == 'float32'
assert tuple(int(d) for d in mod['main'].ret_type.shape) == (1, 12)
print('TVM import passed; params', len(params))
PY
```

SavedModel file hashes:

| File | SHA-256 |
| --- | --- |
| `saved_model.pb` | `80665dd19eeb03d1152fdc098b5635261731b23478d09f6ff2166da799f98138` |
| `variables/variables.data-00000-of-00001` | `5ebfddd34e85a2d35e87e27a8a803353534019bb460907b16db5fa72d757e8c5` |
| `variables/variables.index` | `3f21dd9ea6736e20e70c5ed2f40ed9d8a7d12b98316ac0e4ab8f4eb7e303d738` |

The SWW output was renamed to
`str_ww_ref_model_float32.tflite`; its SHA-256 remains
`c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267`.
There is no duplicate misspelled artifact or live `floag32` reference. Using
the corrected path, the SWW suite passed (23 tests), CPU deploy returned class
0 (Marvin), and FSIM deploy exported four actual VTA workloads / 20 actual VTA
operation rows. CPU and FSIM scores both were
`[0.9999833106994629, 1.5706149714134199e-09, 1.6730595234548673e-05]`.
FSIM workload snapshot SHA-256 remains
`4aed1f204c755434eea23378c43f4ee1328ab3c27974fc519420e26d111841f7`; the
corrected path has been recorded in the report.

Corrected-name FSIM command:

```bash
APP=vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/$APP" \
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
  .envs/tvm-vta-env/bin/python "$APP/deploy.py" \
  --model "$APP/model/str_ww_ref_model_float32.tflite" \
  --input "$APP/samples/marvin-00176480_nohash_0.wav" \
  --target vta,llvm --simulator fsim \
  --export-workloads /tmp/sww-float32-workloads.json \
  --deployment-report /tmp/sww-float32-report.md
```

Focused command results:

```text
.envs/tvm-vta-env/bin/python -m pytest scripts/tests/test_convert_kws_model.py -q: 4 passed
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1" .envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests -q: 23 passed
make -C vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1 deploy TARGET=llvm: class 0 (Marvin)
corrected-name FSIM deploy: four workloads exported; 20 VTA operation rows; class 0 (Marvin)
```

The prior C2 importer failure applied to the superseded hybrid float-I/O
artifact. The replacement all-float SavedModel export passed KWS import,
deployment, and the two-model workload gate; final C2 evidence is recorded in
[CHECKPOINT-C2.md](CHECKPOINT-C2.md).

## Environment and conversion

Created `.envs/sww-env` with Conda and installed the supplied requirements
without edits:

```bash
bash scripts/setup_sww_env.sh --help
bash scripts/setup_sww_env.sh
.envs/sww-env/bin/python -m pip check
.envs/sww-env/bin/python -c 'import tensorflow, tensorflow_model_optimization, scipy, matplotlib, seaborn, notebook; print("tensorflow", tensorflow.__version__); print("tensorflow_model_optimization", tensorflow_model_optimization.__version__); print("scipy", scipy.__version__); print("notebook", notebook.__version__)'
.envs/sww-env/bin/python scripts/convert_sww_model.py
```

Results: `pip check` reported `No broken requirements found`; imports succeeded
with TensorFlow 2.15.0, TensorFlow Model Optimization 0.7.5, SciPy 1.11.4,
and Notebook 7.6.3. Conversion completed through the adapted upstream
quantizer's float branch.

| Artifact | SHA-256 | Size |
| --- | --- | ---: |
| H5 source `str_ww_ref_model.h5` | `b0f267a8ba0bcb911c1098229c32fac21996e4191c9c60d1fda80adaa70a8add` | 684,056 bytes |
| Upstream `quantize.py` | `6303e820a13ce6d50ea26f2e6d19ee3cbbfac2fae99cb520c0737afc578742f2` | 2,617 bytes |
| Output `str_ww_ref_model_float32.tflite` | `c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267` | 191,428 bytes |

The source H5 and upstream script are read from the ignored MLPerf Tiny v1.4
tree. No H5 or conversion intermediate is stored in the app directory. The
application output keeps the requested `float32` spelling.

## FlatBuffer verification

Ran the following with the repository's TVM environment and TFLite schema:

```bash
.envs/tvm-vta-env/bin/python - <<'PY'
from pathlib import Path
import tflite
path = Path('vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model/str_ww_ref_model_float32.tflite')
model = tflite.Model.GetRootAsModel(path.read_bytes(), 0)
assert model.SubgraphsLength() == 1
subgraph = model.Subgraphs(0)
input_tensor = subgraph.Tensors(subgraph.Inputs(0))
output_tensor = subgraph.Tensors(subgraph.Outputs(0))
assert input_tensor.Type() == output_tensor.Type() == tflite.TensorType.FLOAT32
assert input_tensor.ShapeAsNumpy().tolist() == [1, 30, 1, 40]
assert output_tensor.ShapeAsNumpy().tolist() == [1, 3]
types = [subgraph.Tensors(i).Type() for i in range(subgraph.TensorsLength())]
assert not any(t in types for t in (tflite.TensorType.INT8, tflite.TensorType.UINT8, tflite.TensorType.INT16))
assert types.count(tflite.TensorType.INT32) == 1
codes = [model.OperatorCodes(subgraph.Operators(i).OpcodeIndex()).BuiltinCode() for i in range(subgraph.OperatorsLength())]
assert tflite.BuiltinOperator.QUANTIZE not in codes
assert tflite.BuiltinOperator.DEQUANTIZE not in codes
print('input', input_tensor.Name().decode(), input_tensor.Type(), input_tensor.ShapeAsNumpy().tolist())
print('output', output_tensor.Name().decode(), output_tensor.Type(), output_tensor.ShapeAsNumpy().tolist())
print('tensor_count', len(types), 'float32', types.count(tflite.TensorType.FLOAT32), 'int32', types.count(tflite.TensorType.INT32))
print('operator_count', len(codes), 'builtin_codes', sorted(set(codes)), 'quantized_ops', False)
PY
```

Output: float32 input `serving_default_input_1:0`, shape `[1, 30, 1, 40]`;
float32 output `StatefulPartitionedCall:0`, shape `[1, 3]`; 29 tensors (28
float32 and one int32 reshape shape constant); 11 operators with builtin codes
`[3, 4, 9, 22, 25]`; no quantize/dequantize op and no INT8, UINT8, or INT16
tensors.

## Focused tooling checks

```bash
bash -n scripts/setup_sww_env.sh
.envs/tvm-vta-env/bin/python -m pytest scripts/tests/test_convert_sww_model.py -q
```

Result: 5 tests passed, covering CLI help and invalid environment names,
preservation of an existing environment prefix, converter input boundaries,
and the calibration-free float conversion adaptation. Actual conversion,
`pip check`, imports, and FlatBuffer validation were also run as recorded
above.

## Checkpoint 2

C2 is **GREEN** for both apps. KWS and SWW use verified all-float TFLite assets,
each has four real VTA regions, and both CPU and FSIM mixed deployments produce
identical float32 scores on their committed sample. Both FSIM runs exported
four actual workload occurrences and captured activations. KWS passed 69 tests;
SWW passed 23. No C3 tuning search or TSIM winner/replay has started. Complete
commands, outputs, score vectors, and model/WAV/snapshot/config hashes are in
[CHECKPOINT-C2.md](CHECKPOINT-C2.md).

## Checkpoint 3: Deployment and bounded tuning

C3 is **GREEN** for both models. Each standalone app now documents and exposes
the complete `deploy`, `tune-fsim`, `tune-tsim`, `tune`, and `clean` workflow
with float32 TFLite passed as the model input. The actual `make tune` command
exported the model's four real workloads, verified one FSIM candidate per
occurrence (`TRIAL_BATCH=1`, `MIN_SUCCESSFUL=1`), and selected candidates from
measured TSIM cycles. Both VTA host-codegen replays passed on TSIM. All four
deployment targets (`c`, `llvm`, `vta,c`, `vta,llvm`) passed on FSIM for each
app. Corrupt workload seals, mismatched model content, and tampered schedule
logs were rejected. The KWS suite passed 70 tests and SWW passed 23, including
clean preservation of model/sample/license/tune evidence.

See [CHECKPOINT-C3.md](CHECKPOINT-C3.md) for model, sample, snapshot and config
hashes; per-occurrence TSIM cycles; persistent candidate/schedule hashes; exact
commands; and output predictions. The smoke search used one candidate per
occurrence and does not claim exhaustive tuning or comparative performance.
