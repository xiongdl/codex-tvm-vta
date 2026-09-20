# Spec: MLPerf Tiny Anomaly Detection v1 deployment

## Objective

Add a fixed-purpose `anomaly_detection_v1` application under
`vta/apps/mlperf_tiny_benchmark`. It imports the MLPerf Tiny v1.4 ToyCar
anomaly autoencoder from the local `.envs` assets, extracts the documented
640-element log-mel feature vectors from ten committed WAV samples, and runs
the same reference/mixed Graph Executor deployment flow as the existing MLPerf
Tiny applications.

The deployment must support LLVM and C host code generation, FSIM and TSIM
simulators, authenticated artifact export/reload, and positive VTA activity.
It validates execution equivalence and per-file anomaly scores; it is not a
full-dataset accuracy or MLPerf submission implementation.

## Confirmed assumptions

1. The application directory is
   `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/`.
2. The source model is copied byte-for-byte from
   `.envs/tiny-v1.4/benchmark/training/anomaly_detection/trained_models/ad01_fp32.tflite`.
3. The source model SHA-256 is
   `c66636f4d7f8af8b10518e7be750a22c9d8d46ec97326b40b0d94c097e0aad9b`.
4. The committed samples are the lexicographically first five
   `normal_id_01_*.wav` files followed by the lexicographically first five
   `anomaly_id_01_*.wav` files from `.envs/ToyCar/test`; their source hashes
   are fixed in `samples/manifest.json`. The manifest uses `0=normal` and
   `1=anomaly`.
5. Feature extraction follows the MLPerf Tiny anomaly baseline parameters:
   16 kHz mono PCM, `n_mels=128`, `frames=5`, `n_fft=1024`,
   `hop_length=512`, `power=2.0`, central mel columns `[50:250]`, and
   concatenated sliding windows of shape `(N, 640)`.
6. The committed model contract is TFLite v3, one subgraph, one float32 input
   named `input_1` with shape `(1, 640)`, and one float32 output named
   `Identity` with shape `(1, 640)`.
7. The original graph has ten fully-connected layers. Before TVM quantization,
   eligible dense layers whose input and output channels are multiples of the
   VTA block size are rewritten as equivalent 1x1 NHWC convolutions. This is a
   local Relay deployment transform: it preserves the two bottleneck dense
   layers with channel size 8 on the host while allowing the current VTA
   quantized-convolution compiler path to accelerate eight eligible layers.
   The first eligible convolution is intentionally skipped by the existing
   `skip_conv_layers=[0]` policy, resulting in seven VTA regions.
8. Quantization is applied exactly once with
   `calibrate_mode="global_scale"`, `global_scale=8.0`, and
   `skip_conv_layers=[0]`, then reference and mixed modules fork from that
   same quantized module.
9. The local `.envs` source trees are read-only inputs and remain unmodified
   and absent from Git. Required model and sample bytes are copied into the
   new application so a checked-out repository is self-contained.

## Source contracts

### Model

- TFLite version: 3
- Subgraphs: 1
- TFLite operators: ten ordered `FULLY_CONNECTED` operators
- Input: `input_1`, `(1, 640)`, `float32`
- Output: `Identity`, `(1, 640)`, `float32`
- Original weights: 20 parameter tensors; hidden dimensions include
  `640 -> 128 -> 128 -> 128 -> 128 -> 8 -> 128 -> 128 -> 128 -> 128 -> 640`
- Deployment routing: eight eligible 1x1 convolution regions after the
  dense-to-convolution transform, seven outlined VTA symbols after the first
  convolution is skipped, and two bottleneck dense layers on the host.

### Samples

The manifest contains exactly these ten files in order, with five normal and
five anomalous samples:

| Order | Class | Filename | SHA-256 |
|---:|---|---|---|
| 0 | normal | `normal_id_01_00000000.wav` | `0385da04d6cf8c1f9d0df775f98fda55409a71890c02ed53bb5d2c66171f6828` |
| 1 | normal | `normal_id_01_00000001.wav` | `9288e70692964b005c6247ecb9ce689ad00171f569b1a7752e497f07347fb243` |
| 2 | normal | `normal_id_01_00000002.wav` | `bfb7b845cf3b21e1dc20a47d5b032141da289e959e11c1ecb9f68fd1bf398331` |
| 3 | normal | `normal_id_01_00000003.wav` | `6769c42c426ffedda9ff7ac1ed6da9937b2668d0518ef5e40ae48ee6e8302bd2` |
| 4 | normal | `normal_id_01_00000004.wav` | `e0f1974c00eee5a3793a68f0fcadc15f0b1ddb3c3a751938a00bed9f7c9dd6b1` |
| 5 | anomaly | `anomaly_id_01_00000000.wav` | `bb9d793188bcc1ed7d0f48124cf49a06b082ac14184f683913374182e31df9d8` |
| 6 | anomaly | `anomaly_id_01_00000001.wav` | `e6fde8cf4f2b8b6c8d3956f1ffbe00cebaef21d6a8a1e09e8f27506a87daba23` |
| 7 | anomaly | `anomaly_id_01_00000002.wav` | `a26c520bd0fb0bbf7d8438aa3646729487bcc64ff1f85810411574ed1b36894a` |
| 8 | anomaly | `anomaly_id_01_00000003.wav` | `6f582a6c775b3e97eb8d6c2eb451902d19c336d51c04d7dc04691284ed040c1a` |
| 9 | anomaly | `anomaly_id_01_00000004.wav` | `3baddd82cb4335efed8db89351e735d2c01959e901d6e855efef96d352978c33` |

Every file is a regular mono 16-bit, 16 kHz WAV. The manifest records the
class, source-relative path, committed filename, byte length, and SHA-256.
Each file produces a deterministic non-empty `(N, 640)` feature matrix.
Runtime execution computes one mean squared reconstruction error per WAV file
and compares reference and mixed scores within the fixed numerical tolerance.

## Tech stack

- Python from `.envs/tvm-vta-env`
- TVM Relay and Graph Executor from the checked-out `tvm` submodule
- VTA BYOC and FSIM/TSIM from the checked-out `vta` submodule
- `tflite==2.10.0`, NumPy, and pytest from the pinned environment
- Python standard-library `wave` plus NumPy FFT/filter-bank code for audio
  preprocessing; no TensorFlow or librosa runtime dependency is added

## Commands

Focused asset and model tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_assets.py \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py
```

Focused artifact and HOST/FSIM tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_graph_artifacts.py \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_host_deployment.py
```

FSIM matrix:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py \
  --simulator fsim --host-codegen all
```

TSIM matrix:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py \
  --simulator tsim --host-codegen all
```

Complete repository gate, after the aggregate script is extended:

```bash
bash scripts/test_vta_byoc.sh
```

## Project structure

```text
vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/
  README.md                 usage, provenance, and deployment behavior
  LICENSE.mlperf-tiny       source-model license notice
  model_pipeline.py        model import, dense transform, quantization, audio features
  graph_artifacts.py        authenticated Graph Executor bundle export/reload
  runtime.py                LLVM/C, HOST, FSIM, and TSIM build/execute flow
  run.py                    CLI entry point
  model/ad01_fp32.tflite   authenticated source model copied from .envs
  samples/*.wav             ten committed ToyCar test samples
  samples/manifest.json     sample order, provenance, and SHA-256 metadata
  tests/                    asset, pipeline, artifact, HOST/FSIM, and TSIM tests
```

The new `graph_artifacts.py` is copied from the established sibling contract
and adjusted only for anomaly-specific artifact identity and symbols. The
aggregate `scripts/test_vta_byoc.sh` gains additive anomaly asset/model/HOST
and TSIM invocations; existing gates remain unchanged.

## Code style

Use immutable dataclasses for observable results, `pathlib.Path` for paths,
explicit constants for authenticated contracts, and narrow validation at every
boundary. The dense transform must be local and deterministic:

```python
def _dense_to_conv(data, weight, units):
    batch, input_channels = _static_shape(data)
    packed_data = relay.reshape(data, (batch, 1, 1, input_channels))
    packed_weight = relay.reshape(
        relay.transpose(weight, axes=(1, 0)),
        (1, 1, input_channels, units),
    )
    conv = relay.nn.conv2d(
        packed_data,
        packed_weight,
        channels=units,
        kernel_size=(1, 1),
        data_layout="NHWC",
        kernel_layout="HWIO",
        out_layout="NHWC",
    )
    return relay.reshape(conv, (batch, units))
```

## Testing strategy

- Asset tests authenticate the model, license, manifest, WAV properties, and
  every committed sample byte; they also assert `.envs` was not modified by
  the asset preparation workflow.
- Model tests prove the exact TFLite/Relay input-output contract, deterministic
  audio feature shape, dense-to-convolution rewrite policy, one-time
  quantization, and seven-region VTA routing.
- Artifact tests reuse the sibling atomic authenticated bundle contract for
  LLVM and C host code generators, including reload and partial-export cleanup.
- HOST/FSIM tests compare reference/mixed tensor shape and dtype, require
  ten per-file comparisons with five normal and five anomalous labels and
  reconstruction scores within `rtol=1e-6, atol=1e-6`, validate seven VTA
  symbols, and require positive FSIM counters.
- TSIM tests validate lazy initialization, target/config mapping, ten score
  comparisons with the same five/five class balance, and positive
  `cycle_count` in a fresh process.
- The final repository gate runs the focused anomaly tests and both simulator
  matrices without weakening existing ResNet or VWW gates.

## Boundaries

- Always: use the pinned repository Python environment; authenticate source
  bytes; keep the model transform deterministic; fork reference and mixed
  graphs from one quantized module; preserve compiler-produced graph JSON;
  run focused tests before each commit.
- Ask first: changing the ten samples, model variant, feature parameters,
  quantization policy, VTA-region count, application name, dependencies, or
  aggregate-gate scope.
- Never: modify or commit `.envs`; download data; train the model; add a
  TensorFlow/librosa runtime dependency; patch graph JSON device placement;
  weaken or skip tests; claim dataset licensing not established by the source.

## Success criteria

1. The model, license, ten WAV samples, and manifest pass byte-level and
   structural provenance tests.
2. The model imports as the fixed float32 `(1, 640) -> (1, 640)` graph, audio
   preprocessing produces deterministic `(N, 640)` inputs, and the dense
   transform/quantization produces the approved seven-region VTA route.
3. LLVM and C HOST/FSIM matrices build, export, reload, and execute five
   normal plus five anomalous WAV files; reference and mixed per-file scores
   agree within the fixed tolerance and FSIM activity is positive.
4. LLVM and C HOST/TSIM matrices satisfy the same ten-score, five/five class
   contract and report positive TSIM cycle activity.
5. Bundles contain authenticated graph, params, library, manifest, and
   inspectable host source; partial exports are removed on failure.
6. `bash scripts/test_vta_byoc.sh` passes with all existing gates retained.
7. `.envs` remains unchanged and absent from Git.

## Open questions

None.
