# Capability Map: TSIM Benchmark Validation

| Module id | Responsibility | Depends on |
|---|---|---|
| `benchmark-routing-invariants` | Align VWW, image classification v2, and anomaly detection's asserted model and partition structure with the repository's current model artifacts, retaining meaningful host/VTA routing checks. | — |
| `gemm-accumulator-bounds` | Adjust the VTA GEMM test schedule so the accumulator allocation respects the configured local accumulator capacity while preserving the 128×128 workload. | — |

Build order: `benchmark-routing-invariants` → `gemm-accumulator-bounds`.

The modules have independent implementation and verification paths; the ordered sequence makes all benchmark preflight blockers explicit before the separate GEMM regression is closed.
