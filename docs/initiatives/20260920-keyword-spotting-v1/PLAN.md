# Implementation Plan: MLPerf Tiny Keyword Spotting v1 Deployment

## Overview

Implement one self-contained MLPerf Tiny KWS v1 application under
`vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1`. The work proceeds from
immutable assets and preprocessing, through Relay/VTA graph preparation and
artifact export, to HOST/FSIM/TSIM execution and reproducible documentation.
The existing image-classification and anomaly-detection applications are the
structural references; no unrelated application or shared build script is
changed.

## Architecture decisions

1. **Fixed committed inputs.** Copy the exact MLPerf KWS reference model and
   twelve selected WAV inputs into the application. Runtime code reads only
   application-owned assets, while the manifest records `.envs` provenance and
   SHA-256 values.
2. **Canonical model order.** Preserve the source model's numeric order:
   `Down`, `Go`, `Left`, `No`, `Off`, `On`, `Right`, `Stop`, `Up`, `Yes`,
   `Silence`, `Unknown`. User-facing names may be lower-case, but numeric
   labels remain stable.
3. **Reference preprocessing.** Implement the KWS MFCC preparation locally
   using the pinned environment's standard-library WAV reader and NumPy. Use
   the MLPerf reference settings and explicitly quantize to the model's input
   contract `(1, 49, 10, 1)` int8.
4. **Single preparation path.** Import once, quantize once, fork a reference
   module and one VTA-partitioned module, and inspect the routing before build.
5. **Reusable artifact contract.** Mirror neighboring applications' bundle
   export/reload behavior: each reference/mixed bundle owns graph JSON,
   serialized parameters, host library, manifest, and source metadata.
6. **Lazy simulator loading.** HOST and artifact building do not initialize a
   simulator. FSIM and TSIM load only after all artifacts are built and
   reloaded; TSIM uses its own target, registries, configuration, and
   positive `cycle_count` check.
7. **Focused tests first.** Each implementation slice adds/updates its focused
   pytest contracts before the corresponding runtime code is completed, then
   runs the complete application test directory before its task commit.

## Dependency graph and build order

```text
committed model + samples + manifest
             |
             v
   WAV/MFCC + TFLite pipeline
             |
             v
   Relay routing + graph artifacts
             |
             v
 HOST build/reload/compare + FSIM execution
             |
             v
 TSIM adaptor + CLI + documentation
```

## Task list

### Checkpoint 1: Assets and model pipeline

- Task 1: Add the exact KWS model, license/provenance metadata, deterministic
  twelve-sample WAV set, and manifest; add asset-contract tests.
- Task 2: Implement deterministic WAV/MFCC loading, model FlatBuffer contract
  validation, quantization, and one-time Relay preparation; add pipeline tests.

Checkpoint exit criteria:

- Asset tests pass with exact byte hashes and canonical 12-label order.
- Pipeline tests pass and validate `(1, 49, 10, 1)` int8 input, `(1, 12)`
  int8 output, and one VTA partition call.

### Checkpoint 2: Graph artifacts and HOST/FSIM execution

- Task 3: Implement graph bundle export/reload validation and graph-structure
  checks; add graph artifact tests.
- Task 4: Implement HOST and FSIM runtime execution, output equivalence,
  profiler validation, and matrix handling; add host deployment tests.

Checkpoint exit criteria:

- The focused application suite passes through HOST/FSIM contracts.
- A real LLVM FSIM run compares all twelve samples and reports positive VTA
  activity.

### Checkpoint 3: TSIM, CLI, documentation, and final verification

- Task 5: Add explicit TSIM session handling, lazy loading, matrix execution,
  positive cycle validation, and TSIM tests.
- Task 6: Add the CLI dispatcher and README usage/provenance instructions,
  then run the complete focused suite and real TSIM deployment.

Checkpoint exit criteria:

- The complete focused test directory passes.
- A fresh-process LLVM/C TSIM run compares all twelve samples and reports a
  positive `cycle_count`.
- README commands reproduce HOST, FSIM, and TSIM from repository-owned assets.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| KWS model's quantization or tensor metadata differs from assumptions | High | Inspect the FlatBuffer before implementation; assert exact input/output contracts in asset and pipeline tests. |
| MFCC implementation drifts from MLPerf reference preprocessing | High | Port only the documented fixed settings, test tensor shape/dtype/range, and compare host output deterministically. |
| Some KWS operators do not partition cleanly to VTA | High | Inspect partition symbols and host operator boundary before build; fail with a structural diagnostic rather than silently accepting zero regions. |
| TSIM matrix is slow or has a different profiler API | Medium | Build both host variants before one lazy TSIM load; use the existing registry adapter pattern and run TSIM in a fresh process. |
| Source samples have inconsistent WAV properties | Medium | Select deterministically, normalize/pad in the loader, and validate sample rate/channel/bit depth in `test_assets.py`. |
| Large binary assets obscure review | Low | Keep model/sample addition isolated in Task 1 and record every source/hash in the manifest and README. |

## Verification matrix

| Stage | Command | Evidence |
|---|---|---|
| Task 1–2 | `PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_assets.py vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_model_pipeline.py` | Fixed assets and pipeline contracts |
| Task 3–4 | Same environment with `test_graph_artifacts.py` and `test_host_deployment.py` | Bundle integrity, HOST/FSIM behavior |
| Task 5–6 | Full application `pytest` directory | Complete focused suite |
| Final FSIM | `run.py --simulator fsim --host-codegen all` with `vta_config.json` | Twelve comparisons and positive FSIM counters |
| Final TSIM | `run.py --simulator tsim --host-codegen all` with `tsim_sample.json` in a fresh process | Twelve comparisons and positive TSIM cycle count |

## Out of scope

- Retraining or modifying the upstream KWS model.
- Accuracy, latency, energy, or MLPerf submission reporting.
- Changes to TVM/VTA vendor source.
- New third-party dependencies.
- Adding the feature to shared CI gates unless separately requested.
