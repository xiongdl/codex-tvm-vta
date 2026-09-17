# Implementation Plan: MLPerf Tiny VWW V1 deployment

## Overview

Build `visual_wake_words_v1` as a fixed, independently testable sibling of
`image_classification_v1`. Work proceeds risk-first: authenticate assets and
prove the MobileNet/Relay/VTA contract, then add graph deployment, then add
simulator matrices and the aggregate gate. Tests precede implementation within
each slice.

## Repository and branch contract

| Repository | Task branch | Original branch | Base HEAD |
|---|---|---|---|
| `/Users/xdl/Projects/codex-tvm-vta` | `codex/vww-v1-deployment` | `dev` | `bb31295f53578e4510edb437c67f38e733443e54` |
| `/Users/xdl/Projects/codex-tvm-vta/vta` | `codex/vww-v1-deployment` | `vta_v0.0.2` | `0ada2482bee9d0b2f6c4ad7a55452c3459b4010a` |

Implementation commits must follow the child-first submodule procedure. Every
checkpoint ends with a verified VTA commit and a parent commit that records the
corresponding gitlink, so the parent worktree is clean before the next fresh
Build agent begins.

## Dependency graph

```text
authenticated model + samples
              |
              v
import + preprocessing + quantization + fixed routing
              |
              v
authenticated graph bundle export/reload
              |
              v
single-target VTA depthwise host fallback
              |
              v
HOST/FSIM runtime + CLI matrix
              |
              v
TSIM matrix + aggregate repository gate
```

## Architecture decisions

- Preserve source JPEG bytes instead of converting them. The manifest binds
  each committed image to its local source relative path and SHA-256.
- Add a focused extractor rather than hand-maintaining sample copies. It
  selects the lexicographically first five images from each class and emits the
  fixed manifest without reading or writing outside explicit arguments.
- Import the floating model and quantize in TVM once, matching ResNet V1. The
  reference and mixed graphs fork from that one quantized module.
- Fix the routing contract at 12 VTA regions. Unsupported MobileNet depthwise
  operations remain on the host; the mixed graph remains a standard Graph
  Executor module.
- Extend the VTA Relay strategy narrowly for unpacked NHWC depthwise
  convolution: use an explicit host-compatible schedule while preserving the
  standard single `Target("vta", host=...)` build. This is a general compiler
  fallback with a focused runtime regression test, not an application-specific
  graph rewrite.
- Treat graph JSON as immutable compiler output. Do not patch `device_index` or
  storage placement after compilation.
- Reuse the proven graph-bundle interface and CLI shape of
  `image_classification_v1`, but keep VWW constants, symbols, preprocessing,
  labels, and tests local to the new application.
- Require identical output shape/dtype, numerical agreement within
  `rtol=1e-6, atol=1e-6`, and correct top-1 labels. The fixed tolerance covers
  the observed host-schedule floating-point reordering while remaining a
  one-part-per-million bound on the two-class output.

## Task list

Detailed acceptance criteria and file allowlists are in `TASKS.md`.

### Checkpoint 1: authenticated inputs and compiler contract

- Tasks 1-4: source assets, deterministic samples, asset tests, model pipeline
- Required focused tests: `test_assets.py`, `test_model_pipeline.py`
- Required result: exact model/sample provenance and deterministic 12-region
  partitioning

### Checkpoint 2: artifacts and HOST/FSIM execution

- Tasks 5-8: graph bundles, VTA depthwise host fallback, HOST/FSIM runtime, CLI
  and user documentation
- Required focused tests: `test_graph_artifacts.py`,
  `test_byoc_runtime.py`, `test_host_deployment.py`
- Required result: the single-target compiler fallback executes without graph
  mutation, and LLVM/C reference and mixed bundles execute ten bounded,
  correctly labelled comparisons with positive FSIM activity

### Checkpoint 3: TSIM and repository integration

- Tasks 9-10: TSIM contract, extractor and aggregate validation automation
- Required focused test/run: `test_tsim_deployment.py`, VWW TSIM CLI matrix
- Required full gate: `bash scripts/test_vta_byoc.sh`
- Required result: all new and existing gates pass

### Final checkpoints

- Fresh Reviewer performs read-only Review after verified implementation.
- Any actionable finding returns to a fresh Build/Fix agent, followed by fresh
  read-only Re-review.
- Integration into `dev` is out of scope until the user separately authorizes
  Ship with an exact merge command.

## Verification environment

All Python invocations use `.envs/tvm-vta-env/bin/python` with
`PYTHONPATH="$PWD/tvm/python:$PWD/vta/python"`. FSIM uses
`vta/config/vta_config.json`; TSIM uses `vta/config/tsim_sample.json`. The
existing TVM, VTA extension, FSIM, TSIM, and hardware libraries must remain
available; no dependency setup or environment recreation is planned.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| VWW MobileNet contains unpacked NHWC depthwise convolutions that the VTA target previously could not schedule on its host fallback | High | Add a narrow host-compatible VTA strategy path and a mixed-runtime regression test; keep 12 accelerator regions and never require depthwise offload |
| Post-build graph placement is manually changed to work around target routing | High | Treat compiler graph JSON as immutable and reject any runtime patching of `device_index` or storage placement |
| Host schedule reordering causes sub-ULP output differences | Medium | Require identical shape/dtype, fixed `rtol=1e-6, atol=1e-6`, exact top-1 labels, and positive accelerator counters |
| Incorrect input scaling produces plausible but wrong predictions | High | Test exact `/255.0` preprocessing and expected labels on both reference and mixed execution |
| JPEG selection becomes nondeterministic | Medium | Sort with a fixed lexical order, bind names and hashes in the manifest, and test extractor reproduction |
| Source image licensing is confused with the model license | Medium | Keep model and dataset provenance separate and avoid asserting an unverified image-data license |
| TSIM matrix is slow or exposes unsupported lowering | High | Execute it as a dedicated fresh-process checkpoint before the aggregate gate |
| Submodule commits leave the parent dirty between agents | Medium | Commit verified child content first, then the exact parent gitlink at every checkpoint |
| Existing ResNet validation regresses | High | Additive aggregate-gate edits only; run the complete existing BYOC gate before review |

## Scope discipline

- No changes to TVM, existing ResNet applications, or environment setup
  dependencies. The only approved shared VTA compiler change is the narrow
  unpacked-NHWC-depthwise host fallback and its focused regression test.
- No changes to the selected assets or deployment contract after Build begins
  without revising and re-approving the full SPEC/PLAN/TASKS batch.
- No generated `build/`, Python cache, `.DS_Store`, complete dataset, or local
  MLPerf source checkout is staged.

## Open questions

None.
