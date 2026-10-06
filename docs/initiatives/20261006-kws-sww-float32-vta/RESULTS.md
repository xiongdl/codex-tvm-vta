# Checkpoint 1 results

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
| Output `str_ww_ref_model_floag32.tflite` | `c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267` | 191,428 bytes |

The source H5 and upstream script are read from the ignored MLPerf Tiny v1.4
tree. No H5 or conversion intermediate is stored in the app directory. The
application output keeps the requested `floag32` spelling.

## FlatBuffer verification

Ran the following with the repository's TVM environment and TFLite schema:

```bash
.envs/tvm-vta-env/bin/python - <<'PY'
from pathlib import Path
import tflite
path = Path('vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model/str_ww_ref_model_floag32.tflite')
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
