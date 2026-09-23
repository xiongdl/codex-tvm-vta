# Checkpoint 3 Validation

Date: 2026-09-23
Branch: `codex/20260923-tsim-benchmark-validation`

## Focused tests

The combined focused pipeline command from `SPEC-benchmark-routing-invariants.md` was attempted as written and exited **2** during collection. Pytest imported the duplicate module basename `test_model_pipeline` from the VWW directory, then rejected the image classification V2 and anomaly files with an import-file mismatch. Running the same three test modules separately passed:

| Module | Result |
| --- | --- |
| `visual_wake_words_v1/tests/test_model_pipeline.py` | exit 0; **8 passed** |
| `image_classification_v2/tests/test_model_pipeline.py` | exit 0; **8 passed** |
| `anomaly_detection_v1/tests/test_model_pipeline.py` | exit 0; **8 passed** |

Each was run with the spec's environment (`VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python"`) and the project's `.envs/tvm-vta-env/bin/python -m pytest -q <module>` command.

The focused GEMM command from `SPEC-gemm-accumulator-bounds.md` exited **0**: **1 passed**.

## End-to-end TSIM runners

Each command used the project's configured environment and was run sequentially, as required. All six exited **0** and completed deployment.

| Benchmark | Command suffix | Result |
| --- | --- | --- |
| Image classification V1 | `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 8 VTA partitions; LLVM and C each compared **10** samples; each reported `cycle_count=38,757,180`. |
| Visual Wake Words V1 | `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 13 VTA partitions; LLVM and C each compared **10** samples; each reported `cycle_count=73,045,290`. |
| Image classification V2 | `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all` | **Pass**; 8 VTA partitions; LLVM and C each compared **10** samples; each reported `cycle_count=217,301,380`. |
| Anomaly detection V1 | `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --simulator tsim --host-codegen all --tsim-window-budget 1` | **Pass**; exit 0; one representative window was executed for each of **10** samples with `score_scope=representative_windows`, `tsim_window_budget=1`, and positive `cycle_count=1,949,920`. This is sampled-window validation, not a full-window score run. |
| Streaming wakeword V1 | `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py --simulator tsim --host-codegen all` | **Pass**; LLVM and C each compared **3** samples with matching reference/mixed top-1 predictions; each reported `cycle_count=523,899`. |
| Keyword spotting V1 | `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 4 VTA partitions; LLVM and C each compared **12** samples with matching reference/mixed top-1 predictions; each reported `cycle_count=28,253,328`. |

The runner command prefix for every row above was:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python <command suffix>
```

## Known test limitation

The full image classification V2 pytest module sequence segfaulted twice during in-process graph execution in Checkpoint 1. It is not counted as passing here. The accepted V2 evidence remains the focused structural/non-matrix tests (**17 passed, 1 deselected**), the isolated real TSIM matrix (**1 passed, 9 deselected**), and the production CLI result above. The production CLI completed both host-codegen matrices successfully.
