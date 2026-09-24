# Capability Map: TSIM Benchmark Validation

| Module id | Responsibility | Depends on |
|---|---|---|
| `benchmark-routing-invariants` | Align VWW, image classification v2, and anomaly detection's asserted model and partition structure with the repository's current model artifacts, retaining meaningful host/VTA routing checks. | — |
| `vww-tsim-runtime` | Diagnose and fix the VWW TSIM graph-execution segmentation fault exposed after the 13-partition graph passes preflight, within VWW deployment runtime and its tests. | `benchmark-routing-invariants` |
| `gemm-accumulator-bounds` | Adjust the VTA GEMM test schedule so the accumulator allocation respects the configured local accumulator capacity while preserving the 128×128 workload. | — |
| `v2-tsim-test-stability` | Diagnose and eliminate the image classification V2 full-module TSIM pytest segmentation fault while preserving the real host-codegen matrix and result checks. | `benchmark-routing-invariants` |
| `anomaly-full-window-coverage` | Run anomaly detection TSIM against every input window and verify that no sampling budget truncates the score run. | `benchmark-routing-invariants` |
| `pipeline-test-collection` | Make the three routing-invariant pytest modules collect and run together using one documented project command. | `benchmark-routing-invariants` |

Build order: `benchmark-routing-invariants` → `vww-tsim-runtime`, `v2-tsim-test-stability`, `anomaly-full-window-coverage`, `pipeline-test-collection`; `gemm-accumulator-bounds` is independent.

The benchmark-specific runtime and coverage modules have independent implementation and verification paths after routing corrections. The pipeline collection module covers the cross-module test invocation. The VWW runtime module follows its routing correction because that correction exposed the runtime failure. The GEMM regression remains independent.
