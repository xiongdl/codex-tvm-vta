# Spec: MLPerf Tiny Streaming Wakeword v1 Deployment

## Assumptions

1. The existing deployment directory is `vta/apps/mlperf_tiny_benchmark`
   (singular), despite the plural spelling in the request.
2. The source model is
   `.envs/tiny-v1.4/benchmark/training/streaming_wakeword/trained_models/str_ww_ref_model.tflite`.
3. The model has three classes in the training order: `Marvin`, `Silence`,
   and `Unknown`; the output index order must remain unchanged.
4. The checked-in application owns an immutable copy of the model and exactly
   three selected WAV samples, so runtime execution does not depend on `.envs`.
5. One sample per category means the lexicographically first `marvin` WAV, a
   deterministic one-second segment from the lexicographically first background
   WAV for `Silence`, and the lexicographically first non-`marvin` WAV for
   `Unknown`.
6. The initial acceptance target is HOST and FSIM. TSIM support remains
   compatible with neighboring applications and is verified when the existing
   hardware prerequisites are available.

## Objective

Create a fixed-purpose `streaming_wakeword_v1` application that imports the
committed int8 streaming wakeword model, reproduces its deterministic log-mel
feature input, and builds both a CPU reference graph and a VTA-partitioned
graph. HOST runs the reference graph for the three committed samples. FSIM
runs reference and mixed graphs and compares their int8 outputs exactly. The
application is a deployment and graph-execution example; it does not claim
MLPerf accuracy, performance, energy, or submission results.

## Model and input contract

- Model SHA-256: `3af8550895ba7d5c584277102b5075c52dcfa63ba9d2b2240f37c4e6abd5dd2b`.
- Input tensor: `serving_default_input_1:0`, shape `(1, 30, 1, 40)`, `int8`,
  scale `0.003701042616739869`, zero point `-128`.
- Output tensor: `StatefulPartitionedCall:0`, shape `(1, 3)`, `int8`, scale
  `0.00390625`, zero point `-128`.
- TFLite operator topology:
  `DEPTHWISE_CONV_2D`, `CONV_2D`, `DEPTHWISE_CONV_2D`, `CONV_2D`,
  `DEPTHWISE_CONV_2D`, `CONV_2D`, `DEPTHWISE_CONV_2D`, `CONV_2D`,
  `RESHAPE`, `FULLY_CONNECTED`, `SOFTMAX`.
- Audio inputs are mono, signed 16-bit PCM, 16 kHz, padded or trimmed to one
  second.
- Feature extraction follows the checked-in streaming training code: 64 ms
  frames, 32 ms stride, periodic-false Hamming window, 40-bin linear-to-mel
  filterbank from 0 to 8 kHz, log10 power with the reference scaling and
  clipping, producing exactly 30 frames by 40 features. Features are
  quantized once with the model input scale and zero point.

## Tech Stack

- Python from `.envs/tvm-vta-env/bin/python`.
- The checked-out TVM and VTA Python packages under `tvm/python` and
  `vta/python`.
- TVM Relay TFLite import, VTA Relay partitioning, Graph Executor artifacts,
  and the repository's FSIM/TSIM libraries.
- Python standard-library WAV handling and NumPy for deterministic feature
  preparation. No new runtime dependency is required.

## Commands

Focused tests:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests
```

HOST deployment:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py \
  --simulator host --host-codegen llvm
```

FSIM deployment:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py \
  --simulator fsim --host-codegen all
```

TSIM deployment, in a fresh process:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py \
  --simulator tsim --host-codegen all
```

The complete repository gate remains:

```bash
bash scripts/test_vta_byoc.sh
```

The implementation must add the streaming wakeword focused tests and runtime
invocations to that gate without weakening existing checks.

## Project Structure

```text
vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/
├── README.md
├── LICENSE.mlperf-tiny
├── model/
│   ├── README.md
│   └── str_ww_ref_model.tflite
├── samples/
│   ├── marvin-00176480_nohash_0.wav
│   ├── silence-doing_the_dishes-00000000.wav
│   ├── unknown-0165e0e8_nohash_0.wav
│   └── manifest.json
├── model_pipeline.py
├── graph_artifacts.py
├── runtime.py
├── run.py
└── tests/
    ├── test_assets.py
    ├── test_model_pipeline.py
    ├── test_graph_artifacts.py
    ├── test_host_deployment.py
    └── test_tsim_deployment.py
```

Generated artifacts belong under the application's ignored `build/` directory
and must not be committed. The application must not read from or write to
`.envs` at runtime.

## Interface and behavior

The CLI must expose `--simulator {host,fsim,tsim}`,
`--host-codegen {llvm,c,all}`, and `--output-dir PATH`, following neighboring
applications. The default is one LLVM FSIM deployment; `all` runs LLVM and C
host variants in deterministic order.

The runtime must:

1. Validate the manifest's exactly three samples, fixed class order, paths,
   audio format, byte lengths, and SHA-256 hashes.
2. Import and authenticate the int8 TFLite model, validate its tensor and
   operator contracts, and preserve the model's quantized input/output types.
3. Produce the exact `(1, 30, 1, 40)` int8 feature tensor without TensorFlow
   or external dataset access.
4. Create a reference graph and call `vta.relay.partition_for_vta()` exactly
   once for the mixed graph; require non-empty VTA convolution partitions and
   preserve the `(1, 3)` int8 output contract.
5. Export and reload authenticated graph, params, library, source, and
   metadata artifacts for each host codegen.
6. On HOST, execute only the reference bundle for all three samples and report
   class indices; simulator libraries must not be loaded.
7. On FSIM and TSIM, execute both bundles for all three samples, compare output
   tensors elementwise, report class indices, and require positive simulator
   activity. TSIM must validate its target and positive `cycle_count`.
8. Fail clearly on malformed assets, missing libraries, changed tensor
   contracts, missing partitions, output mismatches, or zero simulator
   activity.

Illustrative result record:

```python
{
    "sample": "marvin-00176480_nohash_0.wav",
    "label": 0,
    "reference_top1": 0,
    "mixed_top1": 0,
    "outputs_equal": True,
}
```

## Code Style

Follow the neighboring MLPerf Tiny applications: `pathlib.Path` for paths,
small frozen dataclasses for result records, explicit validation at boundaries,
lazy simulator initialization, deterministic lexical asset selection, and
clear errors containing the failing asset or simulator.

```python
def quantize_features(features: np.ndarray) -> np.ndarray:
    if features.shape != (30, 40) or not np.isfinite(features).all():
        raise ValueError(f"unexpected streaming feature matrix: {features.shape}")
    values = np.rint(features / INPUT_SCALE + INPUT_ZERO_POINT)
    return np.clip(values, -128, 127).astype(np.int8)[None, :, None, :]
```

Use lower-case `snake_case` names, upper-case constants for fixed contracts,
and avoid modifying unrelated MLPerf Tiny applications.

## Testing Strategy

Tests use `pytest` and are colocated with the application.

- `test_assets.py` verifies the model checksum, TFLite contract, three sample
  files, manifest class order, audio format, hashes, and absence of `.envs`
  runtime dependencies.
- `test_model_pipeline.py` verifies deterministic feature shape/quantization,
  model import, int8 output contract, and exactly-once VTA partitioning with
  focused test doubles where compilation is unnecessary.
- `test_graph_artifacts.py` verifies graph/source/partition metadata and safe
  artifact reload behavior.
- `test_host_deployment.py` verifies three reference-only HOST results and
  deterministic FSIM comparisons, including failure paths.
- `test_tsim_deployment.py` verifies target/registry checks, fresh-process
  configuration, three-sample dispatch, and positive cycle validation.

The focused suite runs before each implementation commit. When build
prerequisites exist, final verification runs HOST, FSIM, and TSIM; missing
prerequisites are reported as environment blockers rather than hidden by
skips.

## Boundaries

- Always: keep source model/sample bytes immutable after selection, validate
  all assets, keep preprocessing deterministic, run focused tests after each
  slice, and keep generated output ignored.
- Ask first: changing the three class definitions or selected samples,
  changing the model/preprocessing contract, adding dependencies, changing
  shared build/test scripts beyond this gate, or editing TVM/VTA vendor source.
- Never: commit credentials or local environments, read `.envs` at runtime,
  weaken or delete failing tests, or claim benchmark accuracy/performance.

## Success Criteria

1. The application and focused tests exist at the specified path.
2. The committed manifest contains exactly one deterministic sample for each of
   `Marvin`, `Silence`, and `Unknown`, with source provenance and hashes.
3. The model pipeline validates the committed TFLite contract and produces the
   expected int8 feature tensor and output contract.
4. HOST produces three reference results without loading simulator libraries.
5. FSIM compares reference and VTA-partitioned outputs exactly for all three
   samples with positive accelerator activity.
6. TSIM remains supported and passes with positive `cycle_count` when its
   documented libraries/configuration are available.
7. README instructions and `scripts/test_vta_byoc.sh` make the deployment
   reproducible using repository files and the documented environment.

## Open Questions

None. The user confirmed the HOST/FSIM-first target and one sample per model
category.
