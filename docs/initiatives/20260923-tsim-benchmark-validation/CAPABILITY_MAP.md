# Capability Map: TSIM Benchmark Validation

| Module id | Responsibility | Depends on |
|---|---|---|
| `benchmark-routing-invariants` | Align VWW, image classification v2, and anomaly detection's asserted model and partition structure with the repository's current model artifacts, retaining meaningful host/VTA routing checks. | — |
| `vww-tsim-runtime` | Diagnose and fix the VWW TSIM graph-execution segmentation fault exposed after the 13-partition graph passes preflight, within VWW deployment runtime and its tests. | `benchmark-routing-invariants` |
| `gemm-accumulator-bounds` | Adjust the VTA GEMM test schedule so the accumulator allocation respects the configured local accumulator capacity while preserving the 128×128 workload. | — |

Build order: `benchmark-routing-invariants` → `vww-tsim-runtime`; `gemm-accumulator-bounds` is independent.

The modules have independent implementation and verification paths; the VWW runtime module follows its routing correction because that correction exposed the runtime failure. The GEMM regression remains independent.
