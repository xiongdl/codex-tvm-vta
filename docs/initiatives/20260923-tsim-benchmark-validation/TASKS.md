# Tasks: TSIM Benchmark Validation

## Checkpoint 1: Benchmark Routing Invariants

Fresh Default execution boundary. Complete each task in order and commit each task separately.

- [ ] **Task 1 — VWW 13-partition contract**
  - Acceptance: Production and test expectations agree with the observed 13 VTA symbols; host operator, partition convolution, and composite checks remain intact.
  - Verify: Run the VWW model-pipeline pytest module and VWW TSIM deployment tests.
  - Files: `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_host_deployment.py`.
- [ ] **Task 2 — Image classification V2 8-partition contract**
  - Acceptance: Production and test expectations agree with the observed 8 VTA symbols; host operator, per-partition convolution, and composite checks remain intact.
  - Verify: Run image classification V2 model-pipeline pytest and TSIM deployment tests.
  - Files: `vta/apps/mlperf_tiny_benchmark/image_classification_v2/model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py`.
- [ ] **Task 3 — Anomaly detection 10-convolution contract**
  - Acceptance: Production and test expectations agree with the observed 10 quantized convolutions; existing VTA symbol, per-partition convolution, host operator/dense, and composite checks remain intact.
  - Verify: Run anomaly detection model-pipeline pytest and TSIM deployment tests.
  - Files: `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/model_pipeline.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py`.

### Checkpoint 2: GEMM Accumulator Bound

Fresh Default execution boundary.

- [ ] **Task 4 — Bound the GEMM accumulator tile**
  - Acceptance: The existing 128×128 test workload lowers without exceeding the configured `local.acc_buffer` bound and completes its existing TSIM correctness checks.
  - Verify: Run `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/tests/python/integration/test_benchmark_gemm.py`.
  - Files: `vta/tests/python/integration/test_benchmark_gemm.py`.

### Checkpoint 3: End-to-End TSIM Verification

Fresh Default execution boundary, after Checkpoints 1 and 2 are committed.

- [ ] **Task 5 — Run and record the complete validation matrix**
  - Acceptance: All three affected model-pipeline test modules and the GEMM test pass; all six MLPerf benchmark TSIM runner commands in `SPEC-benchmark-routing-invariants.md` complete deployment; `VALIDATION.md` records each command and its result without implying success for a run that did not complete.
  - Verify: Run the focused model-pipeline pytest command and GEMM pytest command in the two approved specs, followed by each of the six TSIM runner commands.
  - Files: `docs/initiatives/20260923-tsim-benchmark-validation/VALIDATION.md`.
