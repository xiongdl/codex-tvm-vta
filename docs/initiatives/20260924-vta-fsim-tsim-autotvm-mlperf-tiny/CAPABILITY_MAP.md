# Capability Map: VTA AutoTVM Schedule Tuning for MLPerf Tiny

| Module id | Responsibility | Depends on |
|---|---|---|
| `simulator-autotvm` | Run AutoTVM schedule search and apply-history-best with the FSIM or TSIM backend; retain backend-specific logs and JSON sidecars. | — |
| `image-classification-v1-tuning` | Connect the existing ResNet-8 V1 import, partition, build, and deployment flow to AutoTVM; compare tuned and untuned results and TSIM cycles. | `simulator-autotvm` |
| `mlperf-tiny-rollout` | Extend the working tuner and artifact contract to every MLPerf Tiny model in this repository. | `simulator-autotvm`, `image-classification-v1-tuning` |

Build order: `simulator-autotvm` → `image-classification-v1-tuning` → `mlperf-tiny-rollout`
