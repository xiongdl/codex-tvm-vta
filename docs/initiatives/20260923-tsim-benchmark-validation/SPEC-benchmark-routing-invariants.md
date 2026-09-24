# Spec: Benchmark Routing Invariants

## Objective

Update the structural validation for Visual Wake Words V1, image classification V2, and anomaly detection V1 so the current checked-in model artifacts can proceed through TSIM deployment. The checkpoint3 logs show 13 VWW partition symbols versus an assertion of 12, 8 image classification V2 symbols versus 7, and anomaly detection's quantized reference has 10 `nn.conv2d` operators versus an assertion of 8. The user is validating VTA TSIM support; success for this module means structural preflight validates the real graph and still catches routing regressions. The VWW end-to-end TSIM runtime failure is handled by the dependent `vww-tsim-runtime` module.

## Assumptions

1. The checkpoint3 model artifacts and current VTA partitioner output are the intended deployment inputs.
2. Symbol counts are not arbitrary pass thresholds: the expected symbols, partition convolution counts, composites, and host operators should describe the observed graph and preserve existing routing guarantees.
3. The focused pipeline and structural tests are the verification for this module; VWW end-to-end TSIM execution is verified by the dependent runtime module, and all six end-to-end TSIM runner invocations remain the initiative-level acceptance gate.

## Tech Stack

Python 3.11 project environment, TVM Relay, VTA, pytest, and the existing MLPerf Tiny model assets. No new dependencies are expected.

## Commands

Run from the repository root. The project environment and built TVM/VTA libraries must already be available.

Focused model-pipeline verification:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py
```

End-to-end TSIM verification for all six runners:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py --simulator tsim --host-codegen all
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py --simulator tsim --host-codegen all
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --simulator tsim --host-codegen all --tsim-window-budget 1
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py --simulator tsim --host-codegen all
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py --simulator tsim --host-codegen all
```

The commands follow the established checkpoint3 invocation matrix. Anomaly detection intentionally uses one representative TSIM window per validation sample (`--tsim-window-budget 1`); that is the accepted validation scope and is not presented as full-window scoring.

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/<benchmark>/model_pipeline.py` contains import, quantization, and routing invariants.
- `vta/apps/mlperf_tiny_benchmark/<benchmark>/tests/test_model_pipeline.py` verifies model and partition summaries.
- Each benchmark's `run.py` and `runtime.py` perform HOST/FSIM/TSIM deployment.

## Code Style

Preserve the existing explicit Relay-operator and symbol checks. Derive symbol expectations from the known model contract where the existing code already uses indexed symbol tuples:

```python
EXPECTED_VTA_SYMBOLS = tuple(
    f"tvmgen_mlperf_vww_vta_main_{index}" for index in range(expected_partition_count)
)
```

Update production expectations and corresponding focused tests together. Keep error messages precise about which observed invariant failed.

## Testing Strategy

- Use the existing pytest model-pipeline tests for the three affected benchmark modules.
- Run each of the six TSIM benchmark deployment commands at the initiative-level acceptance checkpoint and record whether it completed simulator execution; a preflight-only pass does not count as deployment success.
- For anomaly detection, preserve the representative-window budget of one per sample and report `score_scope=representative_windows`; exhaustive window coverage is not required for this initiative.
- Do not weaken unrelated asset hashes, tensor contracts, host operator checks, or partition composite checks to make a run pass.
- No new testing framework or coverage threshold is introduced.

## Boundaries

- **Always:** Keep expected symbols, per-partition convolution counts, host operator counts, and composites internally consistent with each model's actual quantized and partitioned graph. Update affected test expectations in the same change.
- **Ask first:** Modify model weights, quantization parameters, the partitioning algorithm, or unrelated benchmark contracts.
- **Never:** Replace structural checks with only non-empty checks or report TSIM deployment success if the runner did not complete deployment.

## Success Criteria

- VWW's quantized reference and partition assertions accept the observed 13-symbol partition graph while retaining its host operator and composite requirements.
- Image classification V2's assertions accept its observed 8-symbol partition graph while retaining its host operator and composite requirements.
- Anomaly detection's quantized reference convolution check matches the current model's observed count of 10; partition convolution, host dense/convolution, symbol, and composite checks remain meaningful and pass against the actual graph.
- Anomaly detection TSIM completes the configured representative-window run for each validation sample and reports its sampled scope accurately.
- All three focused pipeline test modules pass.
- VWW, image classification V2, and anomaly detection focused pipeline tests pass. End-to-end deployment completion for all six runners is verified at the initiative-level acceptance checkpoint after the dependent VWW runtime fix.

## Open Questions

- None. The anomaly detection quantized graph was inspected with the project environment and contains 10 `nn.conv2d` operators.
