# Implementation Plan: TSIM Benchmark Validation

## Overview

Keep the completed routing, VWW runtime, GEMM, pytest collection, and benchmark validation work. The V2 test module currently passes by running its real TSIM matrix in a subprocess, but this masks a native crash when `graph_executor.run()` executes within pytest. Identify and fix the underlying in-process failure, restore direct matrix execution in pytest, then rerun regressions. Anomaly detection's accepted TSIM evidence remains one representative window per sample.

## Architecture Decisions

- Preserve the completed per-benchmark model and partition invariants, VWW TSIM deployment, and GEMM accumulator fix.
- Treat the current V2 subprocess test as diagnostic isolation only. First restore direct in-process matrix execution as a failing reproducer and preserve its exit/signal evidence; then identify the specific native ownership, lifecycle, or state error before changing code.
- Fix only the demonstrated V2 graph-execution failure boundary. The approved scope includes relevant shared TVM graph-executor or VTA TSIM runtime code and its focused regression test, but excludes unrelated platform refactors.
- Keep the V2 end-to-end regression test executing the real LLVM/C matrix directly in the pytest process after the fix. Continue to run the production CLI separately as an independent control.
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

### Checkpoint 7: V2 In-Process TSIM Root-Cause Fix

- Task 10: Reproduce, diagnose, and fix the native abort from direct `graph_executor.run()` execution under pytest; restore direct in-process V2 matrix coverage.

### Checkpoint 8: Post-Fix Regression Matrix

- Task 11: Re-run the direct V2 matrix and complete deployment module, production V2 CLI, all six benchmark TSIM runners, focused pipeline tests, and GEMM; record root-cause and regression evidence.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The V2 abort is process-state dependent or lacks a native stack trace. | A superficial test-only workaround could remain and the root bug could recur elsewhere. | Restore the in-process reproducer, compare isolated and full-module order, capture the narrowest available native evidence, and require a demonstrated causal explanation before accepting a fix. |
| The cause is in shared TVM/VTA execution code. | A broad platform change could regress other TSIM workloads. | Limit edits to the proven executor/runtime defect, add a focused failing-before/passing-after regression, and rerun all six deployment paths. |
| Pytest importlib mode does not resolve the duplicate module-name collision or affects test behavior. | Combined pipeline verification remains unavailable. | Try the documented supported mode first; if it fails, use a narrowly scoped naming/configuration fix and verify standalone and combined runs with the same tests. |
| A fix for one validation gap changes another benchmark path. | Previously passing deployments regress. | Run focused affected-module checks after each task and the complete six-run matrix at the final checkpoint. |

## Open Questions

- The exact V2 native root cause remains unknown and is the objective of Task 10. The user confirmed that one representative anomaly window per sample is sufficient.
