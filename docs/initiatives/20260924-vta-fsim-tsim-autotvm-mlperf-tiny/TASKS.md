# Tasks: VTA AutoTVM Schedule Tuning for MLPerf Tiny

## Checkpoint 1: AutoTVM Foundation

Fresh Default execution boundary: complete Tasks 1–2 in order. Verify and commit each task separately.

### Task 1: Enable simulator-aware VTA AutoTVM measurements

**Description:** Make the V1 AutoTVM path create and build supported VTA conv/dense tasks for the intended target. Repair task extraction/target normalization or VTA-side TOPI schedule construction where needed, then add the narrowest FSIM/TSIM measurement adapter. Confirm per-trial TSIM `cycle_count` can be reset, collected, and returned as the candidate cost. Keep the work in the VTA repository; do not modify TVM core.

**Acceptance criteria:**
- [ ] V1 AutoTVM task extraction yields supported VTA tasks, and selected conv/dense schedule candidates build without unregistered-target or already-split-iterator errors.
- [ ] A TSIM trial records a positive integer `cycle_count` as its AutoTVM cost and resets profiler state between candidate measurements.
- [ ] FSIM and TSIM backend mismatch, missing libraries, and missing profiler registries fail with clear diagnostics.
- [ ] A bounded V1 trial completes under FSIM and TSIM using current AutoTVM APIs; no TVM core files are changed.

**Verification:** Run focused AutoTVM runner/task-extraction tests and VTA TOPI regression tests for changed behavior, then a one-task/one-trial AutoTVM smoke on FSIM and TSIM in separate processes using `vta_64mac.json`.

**Dependencies:** None.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py`
- `vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py`
- `vta/python/vta/top/vta_conv2d.py` (if the conv schedule is the failing boundary)
- `vta/python/vta/top/vta_dense.py` (if the dense schedule is the failing boundary)

**Estimated scope:** Small.

### Task 2: Add shared tuning orchestration and paired artifacts

**Description:** Extract supported AutoTVM tasks from the selected model graph, tune them with the requested backend, apply backend-specific trial settings, and persist the native AutoTVM log plus deterministic JSON sidecar. Validate config path/content, model identity, backend, and tuning parameters when replaying records.

**Acceptance criteria:**
- [ ] FSIM and TSIM produce different backend-specific native logs and one sidecar per completed tuning run.
- [ ] The sidecar maps model id, backend, geometry-config hash, log path, task/trial counts, and tuning options.
- [ ] Incomplete or mismatched artifacts are rejected before history-best compilation.

**Verification:** Focused artifact and task-extraction tests; bounded V1 tuning smoke on FSIM and TSIM; history-best replay selects records from each generated log.

**Dependencies:** Task 1.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py`
- `vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py`
- `scripts/README.md`

**Estimated scope:** Medium.

### Checkpoint 1 verification

- [ ] Both backends independently tune a bounded V1 task set.
- [ ] VTA-side task extraction and selected schedule templates build successfully for V1.
- [ ] TSIM trial costs are cycle counts, not wall-clock values mislabeled as cycles.
- [ ] Logs and sidecars can be paired and replayed; geometry mismatch is rejected.

## Checkpoint 2: V1 Closed Loop

Fresh Default execution boundary: complete Task 3. Verify and commit the task separately.

### Task 3: Integrate tuned V1 builds and cycle comparison

**Description:** Connect the shared tuner to the existing `image_classification_v1` runtime. Preserve an untuned baseline build, apply the matching AutoTVM log to tuned builds, run the current committed samples, and report both TSIM cycle counts. If the complete tuned graph does not use fewer TSIM cycles after the current finite search space is exhausted, expand the VTA-side TOPI schedule/search space or the VTA TSIM cycle-cost path as needed, then retune. Keep all changes in VTA; do not modify TVM core.

**Acceptance criteria:**
- [ ] The existing V1 FSIM and TSIM commands continue to work; tuned mode requires a matching log/sidecar pair.
- [ ] Baseline and tuned V1 outputs pass the existing equality checks for all ten samples.
- [ ] Tuned TSIM `cycle_count` is strictly lower than baseline, with config, log, and sidecar identities printed in the result.

**Verification:** Run the V1 model-pipeline and deployment tests; run bounded FSIM/TSIM tuned replay; run relevant VTA TOPI regression tests if schedules or measurement hooks change; run the documented V1 TSIM comparison command with the resulting best log. Confirm that AutoTVM applies the selected records during Relay compilation and that the tuned full-model cycle count is strictly lower than baseline.

**Dependencies:** Checkpoint 1.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`
- `vta/python/vta/top/vta_conv2d.py` and `vta/python/vta/top/vta_dense.py` (if additional VTA schedule/search-space changes are needed)
- `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py` (if the VTA-side TSIM cycle-cost path needs adjustment)

**Estimated scope:** Medium.

### Checkpoint 2 verification

- [ ] Tuned and baseline V1 outputs remain equivalent.
- [ ] Tuned TSIM cycle count is lower than baseline.
- [ ] A fresh process using each backend can replay its matching log.

## Checkpoint 3: Image V2 and Anomaly

Fresh Default execution boundary: complete Tasks 4–5 in order. Verify and commit each task separately.

### Task 4: Add image classification V2 tuning adapter

**Description:** Add V2 model identity and prepared-graph support to the shared tuner, replay matching FSIM/TSIM logs in its runtime, and preserve V2's current output/routing checks.

**Acceptance criteria:**
- [ ] V2 task extraction reports supported and unsupported VTA tasks explicitly.
- [ ] V2 can tune/replay independently on FSIM and TSIM with paired logs and sidecars.
- [ ] Existing V2 correctness checks pass when matching tuned records are applied.

**Verification:** Run focused V2 tuner adapter tests and the V2 model-pipeline, FSIM deployment, and TSIM deployment tests with bounded tuning records.

**Dependencies:** Checkpoint 2.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/README.md`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_host_deployment.py`

**Estimated scope:** Medium.

### Task 5: Add anomaly detection V1 tuning adapter

**Description:** Add anomaly V1 model identity and prepared-graph support to the shared tuner, replay matching backend logs, and preserve its current sequence/window execution and TSIM safeguards.

**Acceptance criteria:**
- [ ] Anomaly V1 task extraction reports supported and unsupported VTA tasks explicitly.
- [ ] Anomaly V1 can tune/replay independently on FSIM and TSIM with paired logs and sidecars.
- [ ] Existing anomaly output and bounded-window TSIM correctness checks pass with matching tuned records.

**Verification:** Run focused anomaly adapter tests and the anomaly model-pipeline, FSIM deployment, and TSIM deployment tests with bounded tuning records.

**Dependencies:** Task 4.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/README.md`
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_runtime.py`

**Estimated scope:** Medium.

### Checkpoint 3 verification

- [ ] V2 and anomaly each use model/backend-specific logs and sidecars.
- [ ] Existing output comparisons and simulator activity checks remain intact.
- [ ] Unsupported task families are reported rather than silently skipped.

## Checkpoint 4: Audio Models

Fresh Default execution boundary: complete Tasks 6–7 in order. Verify and commit each task separately.

### Task 6: Add keyword spotting V1 tuning adapter

**Description:** Add keyword spotting V1 model identity and prepared-graph support, backend-specific tuned replay, and output/cycle reporting while preserving MFCC preprocessing and its 12-sample output contract.

**Acceptance criteria:**
- [ ] KWS task extraction reports supported and unsupported VTA tasks explicitly.
- [ ] KWS can tune/replay independently on FSIM and TSIM with paired logs and sidecars.
- [ ] Existing sample and output-equivalence checks pass with matching tuned records.

**Verification:** Run focused KWS adapter tests and the KWS pipeline, host deployment, and TSIM deployment tests with bounded tuning records.

**Dependencies:** Checkpoint 3.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/README.md`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_host_deployment.py`

**Estimated scope:** Medium.

### Task 7: Add streaming wakeword V1 tuning adapter

**Description:** Add streaming wakeword V1 model identity and prepared-graph support, backend-specific tuned replay, and output/cycle reporting while preserving its streaming state and chunk boundaries.

**Acceptance criteria:**
- [ ] Streaming wakeword task extraction reports supported and unsupported VTA tasks explicitly.
- [ ] Streaming wakeword can tune/replay independently on FSIM and TSIM with paired logs and sidecars.
- [ ] Existing streaming input/state and output checks pass with matching tuned records.

**Verification:** Run focused streaming adapter tests and its model-pipeline, host deployment, and TSIM deployment tests with bounded tuning records.

**Dependencies:** Task 6.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/README.md`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_host_deployment.py`

**Estimated scope:** Medium.

### Checkpoint 4 verification

- [ ] Both audio models preserve their existing preprocessing and output checks.
- [ ] Each model/backend has distinct replayable records and a matching sidecar.
- [ ] TSIM cycle reporting is associated with the correct model and tuning log.

## Checkpoint 5: VWW and Aggregate Rollout

Fresh Default execution boundary: complete Tasks 8–9 in order. Verify and commit each task separately.

### Task 8: Add visual wake words V1 tuning adapter

**Description:** Add VWW model identity and prepared-graph support, backend-specific tuned replay, and cycle reporting while preserving its CPU/VTA routing contract and 10-sample output comparisons.

**Acceptance criteria:**
- [ ] VWW task extraction reports supported and unsupported VTA tasks explicitly.
- [ ] VWW can tune/replay independently on FSIM and TSIM with paired logs and sidecars.
- [ ] Existing VWW output and routing checks pass with matching tuned records.

**Verification:** Run focused VWW adapter tests and its model-pipeline, host deployment, and TSIM deployment tests with bounded tuning records.

**Dependencies:** Checkpoint 4.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/README.md`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_host_deployment.py`

**Estimated scope:** Medium.

### Task 9: Add aggregate model selection and document complete workflow

**Description:** Add an `all` model selector that enumerates the six repository applications, runs backend-specific tuning in a resume-safe order, summarizes tunable task coverage and artifact paths, and documents setup, commands, result interpretation, and output side effects.

**Acceptance criteria:**
- [ ] The aggregate selector includes exactly the six current repository models and can target FSIM or TSIM.
- [ ] Per-model failures and unsupported tasks remain visible; later models do not silently inherit another model's tuning log.
- [ ] Root and model documentation explain the paired log/JSON contract, trial controls, TSIM cycle comparison, and simulator prerequisites.

**Verification:** Run aggregate CLI contract tests; execute bounded aggregate tuning/replay on FSIM and TSIM; confirm every model reports its own log, sidecar, task coverage, and correctness result.

**Dependencies:** Task 8.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py`
- `vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py`
- `scripts/README.md`
- `vta/apps/mlperf_tiny_benchmark/README.md`

**Estimated scope:** Medium.

### Checkpoint 5 verification

- [ ] All six repository models are included and all model/backend log pairs are distinct.
- [ ] Existing model correctness tests remain intact and the bounded aggregate smoke completes.
- [ ] V1 tuned TSIM cycle count remains lower than its recorded baseline; other models report cycles without claiming speedups unless compared to baselines.
