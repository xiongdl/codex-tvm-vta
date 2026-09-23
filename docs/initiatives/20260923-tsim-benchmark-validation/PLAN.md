# Implementation Plan: TSIM Benchmark Validation

## Overview

Correct the three stale MLPerf model-structure checks that currently stop before TSIM deployment, reduce the GEMM schedule's accumulator tile to fit the existing VTA memory bound, then rerun all six TSIM benchmark deployments and the focused GEMM test.

## Architecture Decisions

- Keep the corrections in each benchmark's existing `model_pipeline.py` and the associated expectations in its existing tests.
- Preserve model asset, tensor, host-routing, partition-composite, and partition-convolution guarantees; update only assertions contradicted by the current checked-in artifacts and observed partitioner output.
- Fix GEMM at the TE schedule tile level. Leave TVM storage-bound enforcement, VTA geometry, and the 128×128 workload intact.
- Run the six benchmark deployment commands separately so each result identifies the benchmark that passed or failed. Record concise command/result evidence in `VALIDATION.md` without checking in generated model artifacts or temporary simulator output.
- Follow the project workflow: a separate task commit for each implementation task, then a verification-record commit.

## Task List

### Checkpoint 1: Benchmark Routing Invariants

- Task 1: Update VWW expectations for the observed 13 VTA partitions.
- Task 2: Update image classification V2 expectations for the observed 8 VTA partitions.
- Task 3: Update anomaly detection's quantized convolution expectation to the observed count of 10.

### Checkpoint 2: GEMM Accumulator Bound

- Task 4: Tile the GEMM output schedule to fit the configured accumulator capacity while preserving the full workload.

### Checkpoint 3: End-to-End TSIM Verification

- Task 5: Run the focused pipeline/GEMM checks and all six benchmark deployment commands; record results in `VALIDATION.md`.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| A revised partition count masks a real routing regression. | Incorrect model regions could be accepted. | Preserve and run the exact per-partition convolution, host operator, and VTA composite checks; change only expectations supported by observed model output. |
| A smaller GEMM tile still exceeds the accumulator capacity or changes execution. | GEMM remains blocked or becomes incorrect. | Use the focused TSIM GEMM integration test to check lowering, simulator execution, and reference output. |
| One of the six runs has an independent deployment issue. | The six-run goal remains incomplete. | Capture per-run evidence and fix issues only within the approved model/deployment validation scope; escalate if a fix needs an out-of-scope model or platform change. |

## Open Questions

- None. The intent and specifications are approved.
