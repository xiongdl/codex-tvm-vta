# Tasks: MLPerf Tiny VWW V1 deployment

## Task 1: Commit the authenticated source model

**Description:** Add the unmodified MLPerf Tiny v1.4 floating VWW model, its
source/license notice, and model provenance documentation.

**Acceptance criteria:**
- [ ] Model SHA-256 is `115bbc094d2119561320a21f01b6500a18bea8cc8589282ab007097bec8af38c`.
- [ ] Provenance states the exact source path, byte-for-byte copy, Apache-2.0
      model status, and TVM quantization policy.
- [ ] No `.envs` path or generated model is staged.

**Verification:** Start the asset test RED, then run `test_assets.py`.

**Dependencies:** None.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/LICENSE.mlperf-tiny`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/model/README.md`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/model/vww_96_float.tflite`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_assets.py`

**Estimated scope:** Medium, 4 files.

## Task 2: Add the five non-person samples

**Description:** Copy the fixed class-0 source JPEG bytes into the application.

**Acceptance criteria:**
- [ ] Exactly the five approved non-person source files are present.
- [ ] Each committed byte hash matches the specification.
- [ ] Each image decodes as 96x96 RGB JPEG.

**Verification:** Run the asset test; it remains RED only for not-yet-added
person samples or manifest behavior.

**Dependencies:** Task 1.

**Files likely touched:** Five JPEG files under
`vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/samples/`.

**Estimated scope:** Medium, 5 files.

## Task 3: Add the five person samples and manifest

**Description:** Copy the fixed class-1 source JPEG bytes and add the ordered
balanced manifest with separate model and dataset provenance.

**Acceptance criteria:**
- [ ] Exactly the five approved person source files are present.
- [ ] Manifest order is five class-0 entries followed by five class-1 entries.
- [ ] Every source path, committed filename, class, and SHA-256 is fixed.

**Verification:** Run `test_assets.py`; all byte, shape, balance, and manifest
assertions pass.

**Dependencies:** Task 2.

**Files likely touched:** Five JPEG files plus
`vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/samples/manifest.json`.
The five images form one mechanical asset set; the manifest is reviewed as the
contract for that set.

**Estimated scope:** Medium asset slice.

## Task 4: Implement the fixed model pipeline

**Description:** Import and validate the model, normalize samples, quantize
once, partition for VTA, and expose an immutable routing summary.

**Acceptance criteria:**
- [ ] Exact float TFLite and Relay contracts are enforced.
- [ ] Sample tensors are `(1,96,96,3)` float32 values in `[0,1]`.
- [ ] Quantization runs once with the approved qconfig and routing is exactly
      12 deterministic VTA regions with the expected host fallback.

**Verification:** Write `test_model_pipeline.py` first, observe RED, implement
`model_pipeline.py`, then run both focused Checkpoint 1 tests.

**Dependencies:** Tasks 1-3.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/model_pipeline.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py`

**Estimated scope:** Small, 2 files.

## Checkpoint 1

- [ ] `test_assets.py` and `test_model_pipeline.py` pass.
- [ ] VTA child candidate contains only Tasks 1-4 files.
- [ ] VTA commit is recorded by an exact parent gitlink commit.

## Task 5: Add authenticated graph bundle export and reload

**Description:** Apply the neighboring application's atomic, authenticated
Graph Executor bundle contract to VWW reference and mixed artifacts.

**Acceptance criteria:**
- [ ] Graph, params, library, manifest, and inspectable host source are exported.
- [ ] Reload verifies hashes, paths, metadata, and expected/forbidden symbols.
- [ ] Partial output and unsafe paths are rejected or cleaned.

**Verification:** Write/adapt `test_graph_artifacts.py` first, observe RED, then
implement `graph_artifacts.py` and run the focused test.

**Dependencies:** Task 4.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_graph_artifacts.py`

**Estimated scope:** Small, 2 files.

## Task 6: Add the VTA depthwise host fallback

**Description:** Extend the VTA Relay convolution strategy with an explicit
host-compatible schedule for unpacked NHWC depthwise convolution so a mixed
module can retain the standard single `Target("vta", host=...)` build.

**Acceptance criteria:**
- [ ] A focused mixed graph with an unpacked NHWC depthwise host operation and
      a VTA region builds with the single VTA target.
- [ ] The depthwise operation remains a host fallback, the VTA region still
      invokes the accelerator, and no graph JSON or device/storage metadata is
      patched after compilation.
- [ ] Existing VTA BYOC runtime tests remain unchanged in meaning and pass.

**Verification:** Extend `test_byoc_runtime.py` first and observe the current
schedule-registration failure, then implement the narrow strategy fallback and
run the focused FSIM runtime test.

**Dependencies:** Task 5.

**Files likely touched:**
- `vta/python/vta/top/op.py`
- `vta/tests/python/unittest/test_byoc_runtime.py`

**Estimated scope:** Small, 2 shared VTA files.

## Task 7: Implement HOST and FSIM deployment

**Description:** Build reference and mixed LLVM/C artifacts, reload each bundle,
run all ten samples, enforce bounded outputs and exact labels, and validate
simulator activity without modifying compiler-produced graph JSON.

**Acceptance criteria:**
- [ ] Both host code generators build independent reference/mixed bundles.
- [ ] All ten mixed outputs have the reference shape/dtype and satisfy
      `numpy.testing.assert_allclose(rtol=1e-6, atol=1e-6)`; top-1 labels equal
      the manifest.
- [ ] Expected 12 VTA symbols are present only in mixed artifacts and required
      FSIM counters are positive.
- [ ] Runtime code never patches graph `device_index`, storage placement, or
      any other compiler-produced graph JSON field.

**Verification:** Write/adapt `test_host_deployment.py` first, observe RED, then
implement `runtime.py` and run the HOST/FSIM focused test.

**Dependencies:** Task 6.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_host_deployment.py`

**Estimated scope:** Small, 2 files.

## Task 8: Add the CLI and application documentation

**Description:** Expose the same safe CLI matrix as ResNet V1 and document
prerequisites, commands, outputs, non-goals, and failure behavior.

**Acceptance criteria:**
- [ ] Defaults are LLVM plus FSIM; `all` runs the ordered LLVM/C matrix.
- [ ] `--simulator` accepts FSIM and TSIM and validates configuration.
- [ ] README commands use only the repository environment and explicit paths.

**Verification:** Run CLI contract assertions in `test_host_deployment.py`, then
execute the FSIM `--host-codegen all` command from the specification.

**Dependencies:** Task 7.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/README.md`

**Estimated scope:** Small, 2 files.

## Checkpoint 2

- [ ] Graph artifact and HOST/FSIM tests pass.
- [ ] The focused VTA mixed-runtime depthwise fallback regression passes.
- [ ] The complete FSIM LLVM/C matrix passes on ten samples.
- [ ] VTA child candidate contains only Tasks 5-8 files.
- [ ] VTA commit is recorded by an exact parent gitlink commit.

## Task 9: Prove the TSIM deployment matrix

**Description:** Add TSIM-specific tests for lazy initialization, hardware
loading, bundle construction, bounded outputs, exact labels, and positive cycle
count.

**Acceptance criteria:**
- [ ] Build/export/reload completes before lazy TSIM initialization.
- [ ] LLVM and C mixed execution satisfies the fixed shape/dtype and
      `rtol=1e-6, atol=1e-6` reference checks and exact manifest labels.
- [ ] Positive TSIM `cycle_count` is required; FSIM-only counters are not.

**Verification:** Write `test_tsim_deployment.py` first, observe RED where the
contract is absent, then run the TSIM `--host-codegen all` command in a fresh
process.

**Dependencies:** Task 8.

**Files likely touched:**
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/README.md`

**Estimated scope:** Medium, 4 files.

## Task 10: Add reproducible extraction and aggregate validation

**Description:** Add the maintained sample extractor, document it, and extend
the parent BYOC gate with focused VWW HOST/FSIM tests and a fresh VWW TSIM
matrix while preserving every existing gate.

**Acceptance criteria:**
- [ ] Extractor recreates the exact ten committed JPEG bytes and manifest from
      an explicit dataset root and refuses invalid inputs.
- [ ] Script documentation lists inputs, prerequisites, outputs, and side effects.
- [ ] Aggregate gate includes VWW assets, model, artifacts, HOST/FSIM, and TSIM
      without altering existing ResNet coverage.

**Verification:** Run extractor-focused asset tests, shell syntax checking, and
`bash scripts/test_vta_byoc.sh`.

**Dependencies:** Task 9.

**Files likely touched:**
- `scripts/extract_mlperf_vww_samples.py`
- `scripts/README.md`
- `scripts/test_vta_byoc.sh`
- Parent `vta` gitlink

**Estimated scope:** Medium, 4 parent paths.

## Checkpoint 3

- [ ] VWW TSIM LLVM/C matrix passes.
- [ ] Full `scripts/test_vta_byoc.sh` gate passes.
- [ ] Both repositories are clean on `codex/vww-v1-deployment`.
- [ ] No `.envs`, generated build output, cache, or unrelated path is tracked.
- [ ] Fresh read-only Review is requested with exact commit IDs.

## Review and Ship

- [ ] Reviewer reports no actionable correctness, test, compatibility,
      security, or maintainability finding.
- [ ] Any finding is fixed by a fresh Fix agent and Re-review passes.
- [ ] User separately authorizes the exact Ship merge command; branch creation
      and Build approval do not authorize integration into `dev`.
