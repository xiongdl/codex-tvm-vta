# Implementation Plan: MLPerf Tiny Streaming Wakeword v1 Deployment

## Overview

Build `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1` as a sibling of
the existing MLPerf Tiny deployment applications. The implementation will
progress from authenticated, repository-owned assets to deterministic feature
preparation, then graph artifacts/runtime execution, and finally the CLI,
documentation, and repository validation gate.

## Architecture Decisions

1. Keep the application self-contained: copy the exact TFLite model and three
   selected WAV-derived samples into the VTA application; runtime never reads
   `.envs`.
2. Use NumPy and the Python standard library for deterministic log-mel feature
   preparation. Do not add TensorFlow as a runtime dependency.
3. Preserve the source model's int8 input/output contracts instead of applying
   a second calibration or quantization pass.
4. Fork one validated Relay module into a CPU reference graph and one VTA
   partitioned graph. Partition exactly once and validate the resulting
   convolution regions.
5. Reuse the neighboring application's authenticated graph artifact format,
   lazy simulator loading, HOST/FSIM/TSIM separation, and LLVM/C matrix CLI.
6. Add the focused streaming tests and deployment commands to the existing
   BYOC gate without changing the gate's existing checks.

## Dependency Graph and Build Order

```text
Repository-owned model/samples/manifest
                │
                ▼
Deterministic feature preparation + model contract
                │
                ▼
Reference/VTA Relay graphs
                │
                ▼
Graph artifacts + HOST/FSIM runtime
                │
                ▼
CLI, README, TSIM compatibility, BYOC gate
```

## Checkpoint Plan

### Checkpoint 1: Assets and contracts

Add the application skeleton, exact model copy, three selected sample files,
model provenance, license notice, manifest, and asset tests. Prove that all
runtime inputs are repository-owned and match the fixed class/audio/model
contracts before compiler work begins.

Verification:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_assets.py
```

### Checkpoint 2: Feature and Relay model pipeline

Implement the streaming log-mel preprocessing, TFLite authentication/import,
contract validation, Relay normalization, and exactly-once VTA partitioning.
Add focused tests for deterministic shapes/quantization and routing.

Verification:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_assets.py \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_model_pipeline.py
```

### Checkpoint 3: Artifacts and HOST/FSIM runtime

Implement graph artifact export/reload and runtime execution by adapting the
established artifact integrity and simulator-session boundaries. Add tests for
graph metadata, reference-only HOST behavior, exact FSIM comparisons, and
failure handling.

Verification:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_assets.py \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_model_pipeline.py \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_graph_artifacts.py \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_host_deployment.py
```

When build prerequisites exist, run the real HOST and FSIM commands from
`SPEC.md` and record their output in the implementation handoff.

### Checkpoint 4: CLI, docs, TSIM compatibility, and repository gate

Add `run.py`, README usage, TSIM registry/target checks, TSIM deployment tests,
and the streaming application entries in `scripts/test_vta_byoc.sh`. Verify the
full focused suite, CLI behavior, Python compilation, and the complete BYOC
gate when the environment permits it.

Verification:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests
```

```bash
bash scripts/test_vta_byoc.sh
```

If TSIM libraries are available, also run the exact TSIM command in `SPEC.md`.
If they are unavailable, report the precise prerequisite blocker without
weakening or skipping the contract tests.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Training feature code uses TensorFlow-only operations | Input mismatch | Translate the checked-in STFT/mel/log scaling to NumPy and test exact shape, range, and quantization boundaries. |
| TFLite int8 graph is not directly accepted by the VTA partitioner | Model build failure | Validate Relay import first, preserve qnn operators, and isolate only the small normalization needed by the neighboring VTA pipeline. |
| Depthwise and pointwise convolution partitioning differs from KWS | Missing accelerator regions | Inspect external functions and require non-empty convolution-containing VTA partitions before artifact export. |
| FSIM/TSIM global registries leak across matrix runs | Nondeterministic or invalid simulator results | Keep simulator loading lazy, clear counters before execution, and use fresh TSIM process guidance. |
| Selected source WAVs change or have incompatible format | Non-reproducible samples | Commit bytes, hashes, source-relative provenance, and strict 16 kHz mono PCM validation. |
| Full BYOC environment lacks a library | Verification cannot complete | Run focused tests and structural checks, then report missing build prerequisites explicitly. |

## Files and Repository Boundaries

- Main repository: initiative documents under
  `docs/initiatives/20260920-streaming-wakeword-v1-deployment/` and the shared
  `scripts/test_vta_byoc.sh` gate.
- VTA repository: the complete new application under
  `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/`.
- Do not modify TVM/VTA vendor implementation files, existing MLPerf Tiny
  applications, or the model/data under `.envs`.

## Completion Criteria

All four checkpoints are committed separately, the complete focused suite is
green, the final Reviewer passes the committed main-to-tip range, and any
unavailable real simulator verification is documented with exact evidence.
