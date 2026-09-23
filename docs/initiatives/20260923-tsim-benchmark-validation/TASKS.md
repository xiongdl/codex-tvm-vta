# Tasks: TSIM Benchmark Validation

## Checkpoint 1: Benchmark Routing and VWW Runtime

Fresh Default execution boundary. Complete each task in order and commit each task separately.

- [x] **Task 1 — VWW 13-partition contract**
  - Acceptance: Production and test expectations agree with the observed 13 VTA symbols; host operator, partition convolution, and composite checks remain intact.
  - Verify: Run the VWW model-pipeline pytest module, VWW TSIM deployment contract tests excluding the real matrix test, and the VWW host deployment tests with `VTA_BACKEND=fsim`.
  - Files: `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_host_deployment.py`.
  - Evidence: model pipeline **8/8**, TSIM deployment contract tests **6/6** (excluding the real matrix), FSIM host deployment **23/23**. Real TSIM matrix execution is Task 2.
- [x] **Task 2 — VWW TSIM graph-execution recovery**
  - Acceptance: The real VWW TSIM matrix completes and preserves its ten output comparisons per host-codegen and positive simulator-cycle checks.
  - Verify: Run the real matrix pytest and VWW `run.py --simulator tsim --host-codegen all` command in `SPEC-vww-tsim-runtime.md`, plus focused VWW runtime tests.
  - Files: VWW `runtime.py`, `run.py`, and directly related tests only; no shared TVM/VTA platform code without another scope decision.
  - Evidence: Matrix pytest **1/1**, non-matrix TSIM runtime contracts **6/6**, and the TSIM CLI completed for LLVM and C with **10/10** sample comparisons each and positive `cycle_count=73045290` for both. The earlier crash did not reproduce on the clean Task 1 commit, so no runtime change was justified.
- [x] **Task 3 — Image classification V2 8-partition contract**
  - Acceptance: Production and test expectations agree with the observed 8 VTA symbols; host operator, per-partition convolution, and composite checks remain intact.
  - Verify: Run image classification V2 model-pipeline pytest and TSIM deployment tests.
  - Files: `vta/apps/mlperf_tiny_benchmark/image_classification_v2/model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py`.
  - Evidence: Structural and non-matrix tests **17 passed, 1 deselected**; isolated real TSIM matrix **1 passed, 9 deselected**; production CLI completed LLVM and C host-codegen matrices with 10 comparisons each and `cycle_count=217301380`. The full pytest module segfaulted twice during in-process graph execution; it is not reported as passing.
- [x] **Task 4 — Anomaly detection 10-convolution contract**
  - Acceptance: Production and test expectations agree with the observed 10 quantized convolutions; existing VTA symbol, per-partition convolution, host operator/dense, and composite checks remain intact.
  - Verify: Run anomaly detection model-pipeline pytest and TSIM deployment tests.
  - Files: `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py`.
  - Evidence: Model pipeline **8/8**; TSIM deployment contract module **9 passed, 1 skipped**; production TSIM CLI completed LLVM and C codegen runs for all 10 samples, with `cycle_count=1949920`. The updated exact graph contract is 10 quantized convolutions, 9 one-convolution VTA partitions, 1 host convolution, 0 host dense operators, and 9 VTA composites.

### Checkpoint 2: GEMM Accumulator Bound

Fresh Default execution boundary.

- [x] **Task 5 — Bound the GEMM accumulator tile**
  - Acceptance: The existing 128×128 test workload lowers without exceeding the configured `local.acc_buffer` bound and completes its existing TSIM correctness checks.
  - Verify: Run `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/tests/python/integration/test_benchmark_gemm.py`.
  - Files: `vta/tests/python/integration/test_benchmark_gemm.py`.
  - Evidence: Focused TSIM pytest **1 passed**. The 128×128 workload now uses a 64×64 output tile, reducing the accumulator tile from 524288 bits to 131072 bits against the existing 262144-bit capacity. Added an explicit reference-result comparison for the real GEMM/ALU path; the existing mock unit paths remain exempt from that output comparison.

### Checkpoint 3: End-to-End TSIM Verification

Fresh Default execution boundary, after Checkpoints 1 and 2 are committed.

- [x] **Task 6 — Run and record the complete validation matrix**
  - Acceptance: All three affected model-pipeline test modules and the GEMM test pass; all six MLPerf benchmark TSIM runner commands in `SPEC-benchmark-routing-invariants.md` complete deployment; `VALIDATION.md` records each command and its result without implying success for a run that did not complete.
  - Verify: Run the focused model-pipeline pytest command and GEMM pytest command in the two approved specs, followed by each of the six TSIM runner commands.
  - Files: `docs/initiatives/20260923-tsim-benchmark-validation/VALIDATION.md`.
  - Evidence: The combined pipeline command exited 2 on pytest's duplicate `test_model_pipeline` import-name collision; each of the three modules passed separately (**8/8 each**). Focused GEMM pytest passed (**1/1**). All six TSIM runner commands exited 0 and completed deployment; per-run sample comparisons and cycle counts, anomaly's one-window scope, and the known V2 full-module segfault limitation are recorded in `VALIDATION.md`.
