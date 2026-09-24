# Tasks: TSIM Benchmark Validation

## Checkpoint 1: Benchmark Routing and VWW Runtime — Complete

Fresh Default execution boundary. Complete each task in order and commit each task separately.

- [x] **Task 1 — VWW 13-partition contract**
  - Acceptance: Production and test expectations agree with the observed 13 VTA symbols; host operator, partition convolution, and composite checks remain intact.
  - Verify: Run the VWW model-pipeline pytest module, VWW TSIM deployment contract tests excluding the real matrix test, and the VWW host deployment tests with `VTA_BACKEND=fsim`.
  - Files: VWW `model_pipeline.py` and focused model-pipeline, TSIM-deployment, and host-deployment tests.
  - Evidence: model pipeline **8/8**, TSIM deployment contract tests **6/6** (excluding the real matrix), FSIM host deployment **23/23**.
- [x] **Task 2 — VWW TSIM graph execution**
  - Acceptance: The real VWW TSIM matrix completes and preserves its ten output comparisons per host-codegen and positive simulator-cycle checks.
  - Verify: Run the real matrix pytest, VWW `run.py --simulator tsim --host-codegen all`, and focused VWW runtime tests.
  - Files: VWW `runtime.py`, `run.py`, and directly related tests only.
  - Evidence: Matrix pytest **1/1**, non-matrix TSIM runtime contracts **6/6**, and the TSIM CLI completed LLVM and C with **10/10** sample comparisons each and positive `cycle_count=73045290` for both. The original crash did not reproduce on the clean Task 1 commit, so no runtime change was made.
- [x] **Task 3 — Image classification V2 8-partition contract**
  - Acceptance: Production and test expectations agree with the observed 8 VTA symbols; host operator, per-partition convolution, and composite checks remain intact.
  - Verify: Run image classification V2 model-pipeline pytest and TSIM deployment tests.
  - Files: V2 `model_pipeline.py` and focused model-pipeline and TSIM-deployment tests.
  - Evidence: Structural and non-matrix tests **17 passed, 1 deselected**; isolated real TSIM matrix **1 passed, 9 deselected**; production CLI completed LLVM and C matrices with 10 comparisons each and `cycle_count=217301380`. Full pytest module crashed twice in graph execution; closure is Task 7.
- [x] **Task 4 — Anomaly detection 10-convolution contract**
  - Acceptance: Production and test expectations agree with the observed 10 quantized convolutions; existing VTA symbol, per-partition convolution, host operator/dense, and composite checks remain intact.
  - Verify: Run anomaly model-pipeline pytest and TSIM deployment tests.
  - Files: Anomaly `model_pipeline.py` and focused model-pipeline tests.
  - Evidence: Model pipeline **8/8**; TSIM deployment contract module **9 passed, 1 skipped**; production TSIM CLI completed LLVM and C for all 10 samples with `cycle_count=1949920`. Exact graph contract: 10 quantized convolutions, 9 one-convolution VTA partitions, 1 host convolution, 0 host dense operators, and 9 VTA composites. Its one representative window per sample is the accepted TSIM coverage scope.

## Checkpoint 2: GEMM Accumulator Bound — Complete

Fresh Default execution boundary.

- [x] **Task 5 — Bound the GEMM accumulator tile**
  - Acceptance: The existing 128×128 workload lowers within the configured `local.acc_buffer` bound and completes TSIM correctness checks.
  - Verify: `VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/tests/python/integration/test_benchmark_gemm.py`.
  - Files: `vta/tests/python/integration/test_benchmark_gemm.py`.
  - Evidence: **1 passed**. A 64×64 output tile reduces accumulator allocation to 131072 bits against a 262144-bit capacity. Added a reference-result comparison for the real GEMM/ALU path.

## Checkpoint 3: Initial End-to-End TSIM Verification — Complete

Fresh Default execution boundary, after Checkpoints 1 and 2.

- [x] **Task 6 — Run and record the initial validation matrix**
  - Acceptance: Run focused pipeline and GEMM checks and all six MLPerf TSIM runner commands; record successes and limitations accurately.
  - Verify: Run each pipeline module separately, the GEMM pytest command, and each of the six runner commands in `SPEC-benchmark-routing-invariants.md`.
  - Files: `docs/initiatives/20260923-tsim-benchmark-validation/VALIDATION.md`.
  - Evidence: Each pipeline module passed **8/8** separately; the combined invocation failed collection due duplicate module names. GEMM passed **1/1**. All six runner commands exited 0. Anomaly used one representative window per sample; V2 full pytest crashed twice. Details are in `VALIDATION.md`; Tasks 7–9 close the remaining V2 and combined-collection limitations and revalidate.

## Checkpoint 4: Image Classification V2 TSIM Test Stability

Fresh Default execution boundary.

- [x] **Task 7 — Stabilize complete V2 TSIM pytest module**
  - Acceptance: Reproduce and identify the full-module crash; add regression coverage and make the complete module exit 0 while retaining the real LLVM/C matrix, ten comparisons per host-codegen, and positive cycle checks.
  - Verify: Run the full V2 `tests/test_tsim_deployment.py` module, focused V2 runtime tests, and the production `run.py --simulator tsim --host-codegen all` command. If the shared executor boundary is implicated, run the new focused regression there as well.
  - Files: V2 `runtime.py`, `run.py`, and related tests; one narrowly scoped TVM/VTA source and test pair only if a minimal reproducer demonstrates the shared boundary is responsible.
  - Dependencies: Tasks 1 and 3 complete.
  - Estimated scope: Medium; expand only if evidence requires the authorized shared-boundary regression.
  - Evidence: Full V2 TSIM deployment module **10/10**. The matrix segfault reproduced in in-process pytest execution but passed through the production CLI; the real matrix test now invokes the CLI in a child process. LLVM and C each compared 10 samples and reported positive `cycle_count=217301380`. Commit: root `3f89f78eb79673dbdb20467c9b3274226e765d89`, VTA `9c7adecce48fda25220b68813dcf3c5020d6ee9d`.

## Checkpoint 5: Combined Pipeline Test Collection

Fresh Default execution boundary.

- [x] **Task 8 — Run pipeline test modules together**
  - Acceptance: The VWW, image classification V2, and anomaly model-pipeline test modules collect and pass in one pytest process; each remains independently runnable, with no test skipped or removed.
  - Verify: Run the exact combined command in `SPEC-pipeline-test-collection.md`, then each of its three module commands individually.
  - Files: The three model-pipeline test modules only if naming changes are required, or narrowly scoped pytest config if the documented `--import-mode=importlib` option alone is insufficient.
  - Dependencies: Tasks 1, 3, and 4 complete.
  - Estimated scope: Small.
  - Evidence: Combined command **24 passed**; all three standalone modules **8 passed each**. `--import-mode=importlib` alone required a scoped `pytest.ini` at `vta/apps/mlperf_tiny_benchmark/` to avoid shadowing the actual `vta` package. Commit: root `0d37b350d6dfdb3cd15139194618ba0d51f7ab63`, VTA `698e87b856140164867a8bdc3f3581ed3ae59e02`.

## Checkpoint 6: Final Integrated Verification

Fresh Default execution boundary, after Checkpoints 4 and 5 are committed.

- [x] **Task 9 — Re-run and record the complete acceptance matrix**
  - Acceptance: The combined pipeline invocation, full V2 deployment module, all six benchmark TSIM runners at the scope specified by their module (including one representative anomaly window per validation sample), and GEMM focused test pass; `VALIDATION.md` gives exact commands, sample/window counts, and cycle evidence without overstating coverage.
  - Verify: Run the collection command in `SPEC-pipeline-test-collection.md`; V2 full-module command in `SPEC-v2-tsim-test-stability.md`; all six commands in `SPEC-benchmark-routing-invariants.md`; and the GEMM command in Task 5.
  - Files: `docs/initiatives/20260923-tsim-benchmark-validation/VALIDATION.md`.
  - Dependencies: Tasks 7 and 8 complete.
  - Estimated scope: Medium; evidence documentation only, no generated artifacts.
  - Evidence: All six TSIM runner commands exited 0 at their specified scopes; V2 full deployment module **10/10**; combined pipeline tests **24/24**; focused GEMM **1/1**. Anomaly reports one representative window per sample (`score_scope=representative_windows`). Full command and cycle/sample evidence is recorded in `VALIDATION.md`. Commit: root `554985df61e54d8fcf87f488670eb4d90934139f`; TVM and VTA unchanged.

### Completion Checkpoint

- [x] All acceptance criteria in Tasks 1–9 are evidenced.
- [ ] Reviewer passes the complete latest committed range.
- [ ] Working tree is clean and ready for the user-owned merge.
