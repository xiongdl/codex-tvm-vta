# Implementation Plan: TSIM Benchmark Validation

## Overview

Keep the completed routing, VWW runtime, and GEMM fixes; close the remaining validation gaps by stabilizing the complete image classification V2 TSIM pytest module and making the three model-pipeline test modules collect and run together. Anomaly detection's accepted TSIM evidence is one representative window per sample. Finish with the six-benchmark TSIM matrix, focused GEMM verification, and an evidence-based `VALIDATION.md`.

## Architecture Decisions

- Preserve the completed per-benchmark model and partition invariants, VWW TSIM deployment, and GEMM accumulator fix.
- Diagnose the image classification V2 process crash before selecting a repair. Preserve the full LLVM/C TSIM matrix and its output/cycle assertions. A minimal shared TVM/VTA executor-boundary change is in scope only if a reproducer identifies it and focused regression coverage verifies it.
- Keep anomaly TSIM validation at the approved representative-window scope: one window for each checked-in validation sample. Report `score_scope=representative_windows`; exhaustive window scoring is not required.
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

- Task 6: Run and record the six runner commands, focused pipeline tests, and GEMM test, noting the V2 and combined-collection limitations accurately. Anomaly uses its accepted representative-window budget.

### Checkpoint 4: Image Classification V2 TSIM Test Stability

- Task 7: Reproduce and fix the full-module V2 TSIM pytest crash without weakening the real matrix.

### Checkpoint 5: Combined Pipeline Test Collection

- Task 8: Make the three benchmark model-pipeline pytest modules collect and run together in one process.

### Checkpoint 6: Final Integrated Verification

- Task 9: Re-run focused checks, all six TSIM runner paths at their specified scope, and GEMM; update `VALIDATION.md` with exact command and result evidence.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The V2 segmentation fault is order-sensitive or originates at the shared executor boundary. | Full-module pytest remains unstable or a broad repair causes regressions. | Reproduce with the full module, isolate the failing boundary, permit shared changes only with a minimal reproducer, add targeted regression coverage, and retain both the real matrix pytest and production CLI checks. |
| Pytest importlib mode does not resolve the duplicate module-name collision or affects test behavior. | Combined pipeline verification remains unavailable. | Try the documented supported mode first; if it fails, use a narrowly scoped naming/configuration fix and verify standalone and combined runs with the same tests. |
| A fix for one validation gap changes another benchmark path. | Previously passing deployments regress. | Run focused affected-module checks after each task and the complete six-run matrix at the final checkpoint. |

## Open Questions

- None. The user confirmed that one representative anomaly window per sample is sufficient. Task 7 and Task 8 implement the remaining requested validation fixes.
