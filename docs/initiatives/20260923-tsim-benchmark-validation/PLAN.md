# Implementation Plan: TSIM Benchmark Validation

## Overview

Keep the completed routing, VWW runtime, and GEMM fixes; close the three remaining validation gaps by stabilizing the complete image classification V2 TSIM pytest module, running anomaly detection over every checked-in validation window, and making the three model-pipeline test modules collect and run together. Finish with the complete six-benchmark TSIM matrix, focused GEMM verification, and an evidence-based `VALIDATION.md`.

## Architecture Decisions

- Preserve the completed per-benchmark model and partition invariants, VWW TSIM deployment, and GEMM accumulator fix.
- Diagnose the image classification V2 process crash before selecting a repair. Preserve the full LLVM/C TSIM matrix and its output/cycle assertions. A minimal shared TVM/VTA executor-boundary change is in scope only if a reproducer identifies it and focused regression coverage verifies it.
- Derive anomaly's full-window budget from the checked-in validation records and existing windowing contract. Require every per-sample executed count to equal its total count; do not infer full coverage from a successful exit code alone.
- Resolve duplicate pytest module names with the narrowest supported solution, preferring the documented `--import-mode=importlib` command before broader pytest configuration or test-file renames.
- Run each required deployment separately so evidence remains attributable. Do not check in generated model artifacts, output bundles, or temporary simulator files.
- Give each implementation task its own commit. Record the completed integrated verification in a separate evidence commit.

## Task List

### Completed Checkpoint 1: Benchmark Routing and VWW Runtime

- Task 1: Update VWW expectations for the observed 13 VTA partitions.
- Task 2: Diagnose and verify the VWW TSIM matrix graph execution.
- Task 3: Update image classification V2 expectations for the observed 8 VTA partitions.
- Task 4: Update anomaly detection's quantized graph and routing expectations.

### Completed Checkpoint 2: GEMM Accumulator Bound

- Task 5: Tile the GEMM output schedule to fit the configured accumulator capacity while preserving the full workload.

### Completed Checkpoint 3: Initial End-to-End TSIM Verification

- Task 6: Run and record the six runner commands, focused pipeline tests, and GEMM test, noting the V2, anomaly-window, and combined-collection limitations accurately.

### Checkpoint 4: Image Classification V2 TSIM Test Stability

- Task 7: Reproduce and fix the full-module V2 TSIM pytest crash without weakening the real matrix.

### Checkpoint 5: Anomaly Detection Full-Window Coverage

- Task 8: Execute every window for every checked-in anomaly validation record and assert full coverage.

### Checkpoint 6: Combined Pipeline Test Collection

- Task 9: Make the three benchmark model-pipeline pytest modules run together in one process.

### Checkpoint 7: Final Integrated Verification

- Task 10: Re-run focused checks, all six TSIM runner paths, full anomaly windows, and GEMM; update `VALIDATION.md` with exact command and result evidence.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The V2 segmentation fault is order-sensitive or originates at the shared executor boundary. | Full-module pytest remains unstable or a broad repair causes regressions. | Reproduce with the full module, isolate the failing boundary, permit shared changes only with a minimal reproducer, add targeted regression coverage, and retain both the real matrix pytest and production CLI checks. |
| Full anomaly window execution is materially more expensive than representative sampling. | The final matrix may take substantially longer or expose a simulator/resource limit. | Derive and record the exact expected window total first; execute all windows without silent truncation; report any real resource blocker with evidence rather than calling a subset complete. |
| Pytest importlib mode does not resolve the duplicate module-name collision or affects test behavior. | Combined pipeline verification remains unavailable. | Try the documented supported mode first; if it fails, use a narrowly scoped naming/configuration fix and verify standalone and combined runs with the same tests. |
| A fix for one validation gap changes another benchmark path. | Previously passing deployments regress. | Run focused affected-module checks after each task and the complete six-run matrix at the final checkpoint. |

## Open Questions

- None. The user approved the updated specifications; Task 7 diagnosis will determine the narrowest code location, and Task 8 will measure the exact full-window count from the checked-in inputs.
