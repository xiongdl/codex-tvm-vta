# Spec: MLPerf Tiny Image Classification V1 Schedule Tuning

## Objective

Use the shared FSIM/TSIM AutoTVM flow to find fast schedules for `image_classification_v1` (MLPerf Tiny ResNet-8 V1). Build and run both untuned baseline and history-best tuned artifacts with the existing model preprocessing, partitioning, samples, and output checks unchanged. The tuned TSIM artifact must use fewer simulator cycles than the baseline.

## Assumptions

1. The existing `image_classification_v1` pipeline remains the source of truth for model import, quantization, VTA partitioning, sample data, and output equivalence.
2. The tuning log selected for a run must match `VTA_BACKEND`, model identity, and the SHA-256 of `vta/config/vta_64mac.json`; mismatches fail before compilation.
3. Cycle comparison uses the same host codegen, sample/input, simulator build, and geometry config for baseline and tuned runs.
4. FSIM and TSIM each keep their own tuning outputs; TSIM `cycle_count` determines whether the tuned schedule achieves the target reduction.

## Tech Stack

The existing V1 Relay/TFLite pipeline, Graph Executor, TVM AutoTVM history-best context, VTA FSIM/TSIM profilers, and the pinned Python environment.

## Commands

Tune each backend with the shared entry point:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model image_classification_v1 --backend fsim

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py \
  --model image_classification_v1 --backend tsim
```

Build/replay the tuned TSIM result through the V1 runner using the resulting tuning log. The final option spelling will be specified in Plan and documented in the V1 README.

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/model_pipeline.py`: existing model import, quantization, and partitioning.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`: baseline/tuned build, replay, sample comparison, and simulator-cycle reporting.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`: user-facing mode selection.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/`: focused regression tests for tuning-log validation, history-best application, equivalence, and cycle comparison.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`: reproducible commands and result interpretation.

## Code Style

Preserve the current split between authenticated model preparation, artifact build/reload, and simulator execution. Add tuning-log validation at the run boundary and report explicit baseline/tuned measurements. Keep existing sample and partition assertions intact.

## Testing Strategy

- Unit tests cover matching and mismatching model/backend/config metadata and the comparison contract.
- Existing V1 pipeline and FSIM/TSIM deployment tests remain green.
- An end-to-end FSIM run applies the FSIM record and preserves output equivalence.
- An end-to-end TSIM run compares baseline and tuned artifacts on the same inputs, verifies output equivalence, and asserts tuned `cycle_count` is lower.

## Boundaries

- **Always:** Preserve the committed model checksum, existing quantization policy, VTA routing contract, output comparisons, and positive activity checks; report the exact log and sidecar used for each tuned run.
- **Ask first:** Change the V1 quantization policy, sample set, model asset, or expected routing structure.
- **Never:** Mark success when the tuned TSIM cycle count is equal to or greater than baseline, or weaken existing output checks to get a performance result.

## Success Criteria

- V1 can be tuned and replayed independently under FSIM and TSIM with the matching log/sidecar pair.
- Baseline and tuned V1 output checks pass for all current committed samples.
- Tuned TSIM `cycle_count` is lower than the untuned baseline under the same config and run conditions; the run prints both values and the selected log identity.

## Open Questions

- The exact run CLI for selecting a tuning log is deferred to Plan, after inspecting existing runner arguments and keeping compatibility with the current deployment commands.
