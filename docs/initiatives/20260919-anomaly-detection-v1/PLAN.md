# Implementation Plan: MLPerf Tiny Anomaly Detection v1 deployment

## Overview

Build a self-contained `anomaly_detection_v1` sibling application that imports
the ToyCar anomaly autoencoder, extracts 640-element audio feature vectors,
rewrites VTA-compatible dense layers into 1x1 convolutions, and executes ten
fixed samples (five normal, five anomalous) through reference and mixed Graph
Executor bundles on LLVM/C host codegen with FSIM/TSIM validation.

## Repository and branch contract

| Repository | Task branch | Original branch | Base HEAD |
|---|---|---|---|
| `/Users/xdl/Projects/codex-tvm-vta` | `codex/20260919-anomaly-detection-v1` | `dev` | `52876c48257c4a3a8c577efbb6b7d83d81a86336` |
| `/Users/xdl/Projects/codex-tvm-vta/tvm` | `codex/20260919-anomaly-detection-v1` | `tvm_v0.17.0` | `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca` |
| `/Users/xdl/Projects/codex-tvm-vta/vta` | `codex/20260919-anomaly-detection-v1` | `vta_v0.0.2` | `456b9ecffe92c9ba02082c12a99909ceedabca81` |

No `tvm` or `vta` submodule source change is planned. The dense-to-convolution
adaptation remains local to the new application because the existing VTA
compiler already lowers the resulting quantized convolution regions.

## Dependency graph

```text
copied model/license + ten WAVs + manifest
                    |
                    v
asset authentication and audio feature contract
                    |
                    v
Relay import + dense-to-1x1-conv transform + quantization + routing
                    |
                    v
Graph bundle export/reload
                    |
                    v
HOST/FSIM runtime + CLI
                    |
                    v
TSIM runtime contract + aggregate repository gate
```

## Architecture decisions

- Copy the exact model and ten source WAV bytes into the application; keep
  `.envs` read-only and uncommitted.
- Fix sample order as five normal files followed by five anomaly files, with
  `0=normal` and `1=anomaly` in the manifest.
- Implement audio preprocessing with `wave` and NumPy so runtime validation
  does not add a librosa dependency. Keep MLPerf feature parameters explicit
  and test deterministic output shape.
- Import the floating TFLite model and quantize once with the established TVM
  global-scale policy. Rewrite only dense layers whose input/output channels
  are VTA-block compatible into equivalent 1x1 NHWC convolutions before
  quantization. Keep the two 8-channel bottleneck dense layers on host.
- Reuse the established authenticated graph-bundle format and simulator
  session contract, with anomaly-specific artifact names and seven symbols.
- Treat compiler-produced graph JSON as immutable and require positive FSIM
  counters or TSIM `cycle_count`.
- Extend `scripts/test_vta_byoc.sh` additively after the local application
  passes; retain every existing gate.

## Task List

Detailed acceptance criteria, verification commands, dependencies, and owned
paths are in `TASKS.md`.

### Checkpoint 1: Assets and compiler contract

Tasks 1-5 add/authenticate assets and implement audio preprocessing, model
import, dense rewriting, quantization, and routing. Required focused tests are
`test_assets.py` and `test_model_pipeline.py`; the result is exact provenance,
a five/five sample balance, deterministic `(N, 640)` features, and seven VTA
regions.

### Checkpoint 2: Artifacts and HOST/FSIM execution

Tasks 6-8 add graph bundle export/reload, runtime, CLI, documentation, and
HOST/FSIM validation. The result is LLVM/C reference and mixed bundles that
execute all ten samples, agree on scores, and report positive FSIM activity.

### Checkpoint 3: TSIM and repository integration

Tasks 9-10 add TSIM validation and aggregate-gate automation. The result is
positive TSIM cycles and no regression in existing gates.

### Final review checkpoint

A fresh Reviewer checks the complete committed range. Actionable findings are
fixed by a fresh Default and followed by fresh Reviewer re-review. Merging into
`dev` remains out of scope until separately authorized.

## Verification environment

All Python invocations use `.envs/tvm-vta-env/bin/python` with
`PYTHONPATH="$PWD/tvm/python:$PWD/vta/python"`. FSIM uses
`vta/config/vta_config.json`; TSIM uses `vta/config/tsim_sample.json`. Existing
TVM, VTA extension, FSIM, TSIM, and hardware libraries are required; no
environment recreation or network download is planned.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Dense layers are not directly matched by current VTA patterns | High | Rewrite only block-compatible dense layers to 1x1 NHWC convolutions before quantization; test exact shapes and seven symbols |
| Audio preprocessing deviates from the MLPerf baseline | High | Fix baseline constants, implement deterministic filter-bank/windowing, and test finite `(N, 640)` features |
| Per-file execution requires many frame calls | Medium | Extract each WAV once, reuse feature matrices, and compare one score per file |
| Host/mixed numerical differences change scores | Medium | Require tensor shape/dtype equality and `rtol=1e-6, atol=1e-6` |
| TSIM initialization is stateful or slow | High | Build all bundles before one lazy TSIM load in a fresh process |
| Provenance or symlink handling is unsafe | High | Byte-authenticate committed files and reject invalid manifest paths |
| Aggregate gate regresses or omits the app | High | Add explicit anomaly FSIM/TSIM invocations and run the complete gate |
| Generated binaries pollute Git | Medium | Keep `build/` ignored and inspect status/diff before every commit |

## Definition of done

- All task and Checkpoint checklists are complete.
- Focused tests, FSIM matrix, TSIM matrix, Python compilation, and the full
  BYOC gate pass in the pinned environment.
- Every implementation increment is committed through `git-workflow`.
- Reviewer passes the complete base-to-tip range.
