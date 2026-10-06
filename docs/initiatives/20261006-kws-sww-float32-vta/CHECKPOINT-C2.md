# Checkpoint 2: Float deployments and workload gate

Status: **ROOT ESCALATION — KWS model import is unsupported by the pinned TVM frontend**

SWW C2 is verified independently. Overall C2 cannot finish until Root resolves
the KWS importer blocker below. This is not a zero-workload finding; C3 and
tuning search have not started.

## SWW evidence

The application stores only
`model/str_ww_ref_model_floag32.tflite` (191,428 bytes, SHA-256
`c735ab47248df7648d9cb4397c0e7d161fe2e88ede17ad900f34a4163d89b267`). Its
FlatBuffer has float32 input `[1, 30, 1, 40]`, float32 output `[1, 3]`, and the
expected 11-operator topology. WAV preprocessing yields float32 features; no
old int8 input scaling is applied. The model is the input to both `deploy.py`
and `tune.py`; Make forwards `MODEL` to both. The workload loader binds the
snapshot to model SHA-256, float32 decoded feature contract, and the TVM policy
`global_scale=8.0, skip_conv_layers=[0]`.

The CPU and mixed graphs are the same TVM global-scale quantized Relay graph.
With the committed Marvin sample, LLVM CPU and FSIM mixed deployment produced
identical float32 scores:

```text
[0.9999833106994629, 1.5706149714134199e-09, 1.6730595234548673e-05]
```

Partitioning produced four actual VTA convolution occurrences. The FSIM
deployment compiled and executed all four regions, exported their serialized
Relay functions and captured activations, and reported 20 actual VTA operation
rows across those regions. The resulting workload snapshot SHA-256 is
`4aed1f204c755434eea23378c43f4ee1328ab3c27974fc519420e26d111841f7`; its
four captured VTA activations are int8, after the documented quantized graph
boundary. The report recorded the model SHA above, Marvin WAV SHA
`b95e103110b89a0d4dff88023edd537a92834f565cb8e3f38b16f725f3d58451`, VTA
geometry config SHA `23b338eacdf5747610d90fd17296e3d0d4236ce416191b7c1cfc597cd67991fa`,
and class 0 (Marvin). FSIM has no cycle count, which remains N/A.

The app's focused suite passed: 23 tests. It covers the float FlatBuffer and
feature contract, no-VTA CPU preparation, quantization policy, four genuine
regions, CPU/mixed FSIM output equivalence, real workload export, Make model
forwarding, and model/snapshot mismatch rejection. Direct tuning validation
rejected a float model with a mismatched hash and rejected the old int8 TFLite
input. No FSIM candidate search or TSIM winner/replay was run because the
initiative-wide two-model gate is still blocked on KWS.

Reproduction commands from the repository root:

```bash
APP=vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1
make -C "$APP" deploy TARGET=llvm
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/$APP" \
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
  .envs/tvm-vta-env/bin/python "$APP/deploy.py" \
  --model "$APP/model/str_ww_ref_model_floag32.tflite" \
  --input "$APP/samples/marvin-00176480_nohash_0.wav" \
  --target vta,llvm --simulator fsim \
  --export-workloads /tmp/sww-float-workloads.json \
  --deployment-report /tmp/sww-float-report.md
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/$APP" \
  .envs/tvm-vta-env/bin/python -m pytest "$APP/tests" -q
```

## KWS blocker

The requested KWS model was copied to
`vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/model/kws_ref_model_float32.tflite`.
Its SHA-256 is `e5004c6f1012246e33fa068d8488325538e0444073cd361f5a7edb40c73f12d2`
(43,392 bytes). It has float32 input `input_1` `[1, 49, 10, 1]`, float32
output `Identity` `[1, 12]`, and the expected 13-operator topology. The graph
also contains five int8 Conv2D weight tensors with quantization metadata,
making those dynamic-range quantized convolutions despite float32 model I/O.

The repository TVM environment fails at `relay.frontend.from_tflite` before
Relay import or quantization:

```text
tvm.error.OpNotImplemented: The following operators are likely to have dynamic range quantization: 'CONV_2D'. If you are running an optimized graph, please turn off dynamic range quantization or use full integer quantization
```

KWS CPU/mixed deployment and output equivalence are not verified. Root must
resolve how to handle KWS dynamic-range Conv2D semantics under the approved
constraints before overall C2 can continue. The old KWS app model remains
while the requested model has not passed deployment verification.
