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


## Initial Checkpoint 3 V2 test failure (superseded below)

The full image classification V2 pytest module sequence segfaulted twice during in-process graph execution in Checkpoint 1. It is not counted as passing here. The accepted V2 evidence remains the focused structural/non-matrix tests (**17 passed, 1 deselected**), the isolated real TSIM matrix (**1 passed, 9 deselected**), and the production CLI result above. The production CLI completed both host-codegen matrices successfully.

## Checkpoint 6 Final Integrated Verification

Date: 2026-09-24
Branch: `codex/20260923-tsim-benchmark-validation`

All commands below used the configured TSIM environment:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python
```

### Combined routing tests

The three model-pipeline modules were collected and run in one pytest process using the approved import mode:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q --import-mode=importlib vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py
```

Result: exit 0, **24 passed** in 14.58 seconds. The documented `--import-mode=importlib` option handled duplicate module basenames; the scoped `vta/apps/mlperf_tiny_benchmark/pytest.ini` also kept collection from shadowing the top-level `vta` package.

### Image classification V2 stability

The complete TSIM deployment module command from `SPEC-v2-tsim-test-stability.md` exited 0: **10 passed** in 182.53 seconds. The real LLVM/C matrix test remained enabled; no segmentation fault occurred.

The production command from that spec also exited 0:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all
```

It completed the LLVM and C TSIM matrices, with **8 VTA partitions**, **10/10 compared samples per host-codegen**, and `cycle_count=217301380` for each. This command was also repeated as the image classification V2 row in the six-runner matrix below, and passed there as well.

### Six-runner TSIM matrix

Each command was run sequentially and exited 0. `--host-codegen all` executes both LLVM and C host-codegen variants.

| Benchmark | Runner command | Result |
| --- | --- | --- |
| Image classification V1 | `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 8 VTA partitions; LLVM and C each compared **10** samples; each reported `cycle_count=38,757,180`. |
| Visual Wake Words V1 | `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 13 VTA partitions; LLVM and C each compared **10** samples; each reported `cycle_count=73,045,290`. |
| Image classification V2 | `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all` | **Pass**; 8 VTA partitions; LLVM and C each compared **10** samples; each reported `cycle_count=217,301,380`. |
| Anomaly detection V1 | `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --simulator tsim --host-codegen all --tsim-window-budget 1` | **Pass**; 10 samples; one representative window executed per sample; `score_scope=representative_windows`; `tsim_window_budget=1`; `cycle_count=1,949,920`. Each input contains 196 windows, so this is representative-window validation and does not claim full-window scoring. |
| Streaming wakeword V1 | `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py --simulator tsim --host-codegen all` | **Pass**; LLVM and C each compared **3** samples with matching reference/mixed top-1 predictions; each reported `cycle_count=523,899`. |
| Keyword spotting V1 | `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 4 VTA partitions; LLVM and C each compared **12** samples with matching reference/mixed top-1 predictions; each reported `cycle_count=28,253,328`. |

### GEMM focused test

The focused command from Task 5 exited 0: **1 passed** in 11.13 seconds. The test retains the 128×128 workload and checks the real GEMM/ALU result against its reference.

### Scope and historical notes

The former V2 full-module segmentation fault is resolved for this checkpoint: the complete module passed with its real TSIM matrix. The earlier Checkpoint 3 failure remains in the historical section above, but is superseded by this successful rerun.

Anomaly TSIM scope remains one deterministic representative window per each of the 10 validation samples. The reported score scope is `representative_windows`; no full-window coverage is claimed or required.

## Checkpoint 8 Post-Fix In-Process Regression Matrix

Date: 2026-09-24
Branch: `codex/20260923-tsim-benchmark-validation`

### Demonstrated root cause and pre-fix reproducer

`SimulatorSession.validate_environment()` imported `vta.testing.simulator` to normalize the requested simulator. Importing that module evaluates its module-level `LIBS = load_backend()`, which eagerly loads the environment-selected backend. The wrong-environment regression sets `VTA_BACKEND=fsim`, so the rejected preflight loaded FSIM before raising the backend-mismatch error. FSIM and TSIM export overlapping VTA symbols with global dynamic-loader visibility; when the same pytest process then ran the valid TSIM matrix, it loaded TSIM after FSIM and the native graph execution aborted. This made the process-local import/load order unsafe even though the mismatch was rejected.

Before the fix, the focused RED pair selected `test_tsim_rejects_wrong_environment_before_model_preparation` followed by `test_end_to_end_tsim_matrix_with_reloaded_graph_bundles`. The first test passed its expected mismatch exception; the direct matrix then terminated with `Fatal Python error: Aborted` during `graph_executor.run()` (native abort/SIGABRT; no Python exception or pytest summary). The captured reproducer is `/private/tmp/v2-tsim-vmem-env-reject.log`. The companion unloaded-simulator assertion also failed before the fix because `vta.testing.simulator` was already present in `sys.modules` after wrong-backend validation.

Task 10 fixed the cause by importing the pure `vta.backend.normalize_backend` function in V2 runtime validation. A rejected FSIM/TSIM mismatch now raises without importing the simulator module or loading its native library. The wrong-environment regression asserts `vta.testing.simulator` remains absent, and the real matrix test directly invokes `deploy_tsim_matrix(tmp_path)` in pytest; it does not use a subprocess.

### Direct in-process regression and V2 checks

The exact commands below used the configured project Python and TSIM libraries (the existing workspace libraries, without rebuilding or aliasing them). The focused direct matrix command exited 0: **1 passed, 9 deselected** in 184.11 seconds. Both LLVM and C executions validated 8 VTA partitions, compared 10 samples each, and reported positive `cycle_count=217301380`.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py -k end_to_end_tsim_matrix_with_reloaded_graph_bundles
```

The complete V2 TSIM deployment module also exited 0: **10 passed** in 184.09 seconds, with its matrix test executing in the pytest process.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py
```

The independent production CLI control exited 0 and completed both host-codegen variants: **8 partitions**, **10 compared samples per host-codegen**, and `cycle_count=217301380` for LLVM and C.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all
```

### Six-runner TSIM matrix

Each command used `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python`, ran sequentially, and exited 0 after simulator execution.

| Benchmark | Command suffix | Result |
| --- | --- | --- |
| Image classification V1 | `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 8 partitions; LLVM and C each compared 10 samples; each reported `cycle_count=38,757,180`. |
| Visual Wake Words V1 | `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 13 partitions; LLVM and C each compared 10 samples; each reported `cycle_count=73,045,290`. |
| Image classification V2 | `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all` | **Pass**; 8 partitions; LLVM and C each compared 10 samples; each reported `cycle_count=217,301,380`. |
| Anomaly detection V1 | `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py --simulator tsim --host-codegen all --tsim-window-budget 1` | **Pass**; 10 samples, one representative window per sample; `score_scope=representative_windows`; positive `cycle_count=1,949,920` for LLVM and C. This does not claim full-window scoring. |
| Streaming wakeword V1 | `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py --simulator tsim --host-codegen all` | **Pass**; LLVM and C each compared 3 samples; each reported `cycle_count=523,899`. |
| Keyword spotting V1 | `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py --simulator tsim --host-codegen all` | **Pass**; 4 partitions; LLVM and C each compared 12 samples; each reported `cycle_count=28,253,328`. |

### Combined routing tests and GEMM

The combined VWW, image classification V2, and anomaly model-pipeline command exited 0: **24 passed** in 15.87 seconds. Each module also passed standalone: **8 passed** for VWW, **8 passed** for image classification V2, and **8 passed** for anomaly detection.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q --import-mode=importlib vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py
```

The focused GEMM command exited 0: **1 passed** in 10.26 seconds.

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/tests/python/integration/test_benchmark_gemm.py
```
