# Spec: MLPerf Tiny Keyword Spotting v1 Deployment

## Assumptions

1. The repository path is `vta/apps/mlperf_tiny_benchmark` (singular), which
   is the existing deployment-example directory referenced by the project.
2. The source model is the MLPerf Tiny v1.4 reference artifact
   `.envs/tiny-v1.4/benchmark/training/keyword_spotting/trained_models/kws_ref_model.tflite`.
3. The model's canonical label order is `Down`, `Go`, `Left`, `No`, `Off`,
   `On`, `Right`, `Stop`, `Up`, `Yes`, `Silence`, `Unknown`; the application
   may expose a user-friendly lower-case order but must preserve the model
   indices in its manifest and output handling.
4. The checked-in application owns a small, immutable copy of the model and
   twelve selected input WAVs, as the other MLPerf Tiny deployment examples do;
   runtime execution must not depend on `.envs`.
5. MFCC preprocessing follows the MLPerf Tiny KWS reference configuration:
   16 kHz audio, a 1-second clip, 30 ms windows, 20 ms stride, 10 MFCC
   coefficients, and deterministic padding/normalization. The implementation
   must verify the exact model tensor contract rather than silently guessing it.
6. `unknown` is represented by the lexicographically first WAV from a
   non-target-word directory, and `silence` is a deterministic one-second
   PCM segment derived from the lexicographically first background-noise WAV.

## Objective

Create a fixed-purpose `keyword_spotting_v1` application that builds a CPU
reference graph and a VTA-partitioned graph from the committed KWS model. HOST
executes the CPU reference for the same twelve committed samples; FSIM and TSIM
execute both full-model Graph Executor paths and compare their output tensors
exactly, proving accelerator activity. This is a deployment and graph-execution
example; it does not claim MLPerf accuracy, performance, energy, or submission
results.

## Tech Stack

- Python from `.envs/tvm-vta-env/bin/python`.
- The checked-out TVM and VTA Python packages under `tvm/python` and
  `vta/python`.
- TVM Relay/TFLite import and quantization, VTA Relay partitioning, Graph
  Executor artifacts, and the repository's FSIM/TSIM libraries.
- Python standard-library WAV handling plus NumPy for deterministic audio
  sample loading and feature preparation. No new runtime dependency is
  required.

## Commands

All commands run from the repository root and use the pinned environment.

Focused contract tests:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest \
  vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests
```

HOST/FSIM deployment:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py \
  --simulator fsim --host-codegen all
```

TSIM deployment, in a fresh process:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py \
  --simulator tsim --host-codegen all
```

Required build prerequisites, when absent:

```bash
bash scripts/build_vta_lib.sh --target libtvm-vta-ext
bash scripts/build_vta_lib.sh --target libvta_fsim
bash scripts/build_vta_lib.sh --target libvta_hw
```

Repository-wide applicable gate:

```bash
bash scripts/test_vta_byoc.sh
```

## Project Structure

```text
vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/
├── README.md              # preparation and HOST/FSIM/TSIM usage
├── LICENSE.mlperf-tiny    # source-model license notice
├── model/
│   ├── kws_ref_model.tflite
│   └── README.md           # source and checksum provenance
├── samples/
│   ├── *.wav               # ten target words, unknown, and silence
│   └── manifest.json       # fixed order, labels, provenance, checksums
├── model_pipeline.py       # import, quantization, and VTA partition contract
├── graph_artifacts.py      # generated graph/source inspection contract
├── runtime.py              # HOST, FSIM, and TSIM execution
├── run.py                  # CLI dispatch
└── tests/
    ├── test_assets.py
    ├── test_model_pipeline.py
    ├── test_graph_artifacts.py
    ├── test_host_deployment.py
    └── test_tsim_deployment.py
```

Generated build output belongs under the application `build/` directory and
must remain ignored. The application must not write into `.envs`.

## Interface and behavior

The CLI must support `--simulator {fsim,tsim}`, `--host-codegen {llvm,c,all}`,
and an output/build directory option consistent with the neighboring MLPerf
Tiny applications. The default invocation is a single LLVM FSIM deployment;
`all` runs LLVM and C host variants in deterministic order.

The runtime must:

1. Load and validate the manifest's exactly twelve samples and label indices.
2. Load WAV files, enforce the 16 kHz/one-second input contract, and produce
   the model's quantized MFCC tensor deterministically.
3. Import the TFLite model, apply the documented quantization policy exactly
   once, and partition supported Relay regions with
   `vta.relay.partition_for_vta()` exactly once.
4. Build reference and mixed Graph Executor bundles containing graph JSON,
   parameters, host library, and an inspectable manifest/source artifact.
5. On HOST, reload and execute only the reference bundle for all twelve samples,
   reporting reference top-1 indices. On FSIM and TSIM, reload and execute both
   bundles for all twelve samples and compare outputs elementwise, reporting
   sample names and top-1 indices.
6. For FSIM, require positive accelerator profiler counters. For TSIM, require
   a positive `cycle_count` and validate the TSIM target/configuration before
   execution.
7. Fail clearly on missing libraries, malformed assets, unexpected tensor
   shapes/dtypes, output differences, missing VTA partitions, or zero
   simulator activity.

Illustrative result record:

```python
{
    "sample": "yes-00000000.wav",
    "label": 9,
    "reference_top1": 9,
    "mixed_top1": 9,
    "outputs_equal": True,
}
```

## Code Style

Follow the neighboring applications: small dataclasses for immutable runtime
results, `pathlib.Path` for paths, explicit validation at boundaries, and
clear exceptions that include the failing asset or simulator. Keep simulator
initialization lazy so HOST runs do not require FSIM/TSIM imports.

```python
def validate_manifest(manifest_path: Path) -> tuple[Sample, ...]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    samples = tuple(Sample.from_json(item) for item in payload["samples"])
    if len(samples) != 12 or tuple(sample.label for sample in samples) != EXPECTED_LABELS:
        raise ValueError("KWS manifest must contain the fixed twelve-label order")
    return samples
```

Use lower-case `snake_case` for Python names, upper-case constants for fixed
contracts, and deterministic lexical ordering for source-file selection. Do
not add broad abstractions or modify unrelated MLPerf Tiny applications.

## Testing Strategy

Tests use `pytest` and are colocated with the application.

- `test_assets.py` verifies model/sample existence, checksums, WAV format,
  exact twelve-entry manifest order, label mapping, and no `.envs` runtime
  dependency.
- `test_model_pipeline.py` verifies model import, input/output contracts,
  quantization, and exactly-once VTA partitioning with lightweight test
  doubles where compiler libraries are not needed.
- `test_graph_artifacts.py` verifies generated graph/source structure,
  partition symbols, and artifact manifest contents.
- `test_host_deployment.py` verifies twelve HOST reference results with no mixed
  execution, and deterministic FSIM result summaries, using the real host path
  where available and focused fakes for failure cases.
- `test_tsim_deployment.py` verifies simulator selection, fresh-process
  configuration, twelve-sample dispatch, and positive-activity checks; the
  real TSIM matrix is run explicitly by the documented command.

The focused suite must pass before each implementation commit. The final
verification must also run both real FSIM and real TSIM commands when their
documented libraries are available; missing prerequisites are reported as
environment blockers rather than hidden by test skips.

## Boundaries

- Always: preserve the exact source model bytes, validate every input asset,
  keep sample selection deterministic, run focused tests after each slice, and
  keep generated outputs ignored.
- Ask first: changing the selected twelve categories, changing the model or
  preprocessing contract, adding a third-party dependency, changing shared
  build/test scripts, or changing CI gates.
- Never: commit credentials or local environments, read input assets from
  `.envs` at runtime, edit TVM/VTA vendor source for this feature, weaken or
  remove failing tests, or claim benchmark accuracy/performance from this
  deployment check.

## Success Criteria

1. The application and its focused tests exist under the specified directory.
2. The committed manifest contains exactly one deterministic sample for each
   of the twelve model classes, with checksums and source provenance.
3. The model pipeline imports the source model, produces the expected KWS
   tensor contract, and partitions VTA regions without duplicate partitioning.
4. HOST execution produces exactly twelve reference results with mixed unset and
   without simulator initialization.
5. FSIM execution succeeds with positive accelerator counters.
6. FSIM and TSIM compare reference and mixed outputs exactly for all twelve
   samples; TSIM succeeds in a fresh configured process with positive
   `cycle_count`.
7. README instructions are sufficient to reproduce the three deployment modes
   using only repository files and the documented environment.

## Open Questions

None. The user confirmed the twelve-class fixed sample matrix and real HOST,
FSIM, and TSIM verification.
