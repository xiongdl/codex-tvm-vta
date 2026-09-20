# Tasks: MLPerf Tiny Keyword Spotting v1 Deployment

Each task is completed and committed independently. Checkpoints are execution
boundaries for a fresh Default implementation pass; they are not additional
human approval gates.

## Checkpoint 1: Assets and model pipeline

### Task 1: Add the fixed KWS model and twelve deterministic samples

**Description:** Create the `keyword_spotting_v1` application asset layout.
Copy the exact MLPerf KWS reference model and license notice, select one
lexicographically deterministic WAV for each of the ten target words, select
one non-target WAV for `Unknown`, derive one fixed one-second `Silence` WAV from
the first background-noise source, and write a manifest with model/sample
hashes and source-relative provenance.

**Acceptance criteria:**

- [ ] The model bytes match the source artifact and the license/provenance
      files identify the MLPerf Tiny v1.4 origin.
- [ ] The manifest has exactly twelve entries in canonical numeric order
      `Down` through `Unknown`, with one local WAV per entry, valid checksums,
      and no duplicate paths.
- [ ] Every committed WAV is readable, mono, 16 kHz, and has the expected
      one-second input contract after deterministic padding/trimming.

**Verification:**

- [ ] Run `test_assets.py` with the pinned environment.
- [ ] Independently recompute all manifest hashes with the pinned Python
      interpreter.

**Dependencies:** None.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/model/kws_ref_model.tflite`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/model/README.md`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/samples/manifest.json`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/samples/*.wav`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_assets.py`

**Estimated scope:** Medium asset slice.

### Task 2: Implement the KWS model pipeline and feature loader

**Description:** Add model FlatBuffer inspection, deterministic WAV-to-MFCC
preprocessing, model-input quantization, TFLite/Relay import, one-time
quantization, VTA partitioning, and routing inspection. Add tests for model
contracts, preprocessing shape/dtype, and exactly-once partitioning.

**Acceptance criteria:**

- [ ] The pipeline asserts the committed model hash, one subgraph, expected
      KWS operator topology, `(1, 49, 10, 1)` int8 input, and `(1, 12)` int8
      output.
- [ ] Each manifest WAV produces deterministic quantized input with the
      expected shape and dtype using only repository-approved dependencies.
- [ ] `prepare_model()` creates reference and mixed modules from one
      quantized module and calls `partition_for_vta()` exactly once, exposing
      non-empty routing symbols.

**Verification:**

- [ ] Run `test_assets.py` and `test_model_pipeline.py`.
- [ ] Run a small pinned-environment script that preprocesses all twelve WAVs
      and checks stable hashes/shapes across two invocations.

**Dependencies:** Task 1.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/model_pipeline.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_model_pipeline.py`

**Estimated scope:** Medium, 2 files.

### Checkpoint 1 verification

- [ ] `test_assets.py` and `test_model_pipeline.py` pass.
- [ ] No implementation code reads `.envs` at runtime.
- [ ] Task 1 and Task 2 have separate commits.

## Checkpoint 2: Graph artifacts and HOST/FSIM execution

### Task 3: Add graph artifact export and structural validation

**Description:** Adapt the neighboring graph bundle contract for KWS model and
VTA symbol identities. Export and reload reference/mixed artifacts with safe
paths, checksummed core files, source metadata, expected/forbidden symbol
checks, and cleanup on failed publication.

**Acceptance criteria:**

- [ ] Reference and mixed bundles contain graph JSON, params, host library,
      manifest, and available generated host source.
- [ ] Reload validates hashes, safe relative paths, simulator/host identity,
      and all expected KWS VTA symbols before execution.
- [ ] Failed export or reload leaves no partial published bundle and preserves
      any previously valid bundle.

**Verification:**

- [ ] Run `test_graph_artifacts.py`.
- [ ] Exercise a tampered graph/params/source case and confirm a clear failure.

**Dependencies:** Task 2.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_graph_artifacts.py`

**Estimated scope:** Medium, 2 files.

### Task 4: Implement HOST and FSIM runtime execution

**Description:** Build both Graph Executor artifacts, reload each with its own
parameters, execute all twelve samples, compare reference/mixed output
tensors, and validate FSIM profiler counters. Keep simulator initialization
lazy and support the LLVM/C matrix used by the reference deployments.

**Acceptance criteria:**

- [ ] HOST execution compares exactly twelve samples with deterministic top-1
      records and no simulator initialization.
- [ ] FSIM execution runs the mixed graph for all twelve samples and requires
      positive GEMM, weight-load, and output-store counters.
- [ ] Partial build failures, output mismatches, missing VTA symbols, and
      zero activity fail with actionable errors.

**Verification:**

- [ ] Run `test_host_deployment.py` with the pinned environment.
- [ ] Run the documented real LLVM FSIM command and save its summary as
      verification evidence.

**Dependencies:** Tasks 2 and 3.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_host_deployment.py`

**Estimated scope:** Medium, 2 files.

### Checkpoint 2 verification

- [ ] `test_assets.py`, `test_model_pipeline.py`,
      `test_graph_artifacts.py`, and `test_host_deployment.py` pass.
- [ ] Real FSIM execution reports twelve comparisons and positive counters.
- [ ] Task 3 and Task 4 have separate commits.

## Checkpoint 3: TSIM, CLI, documentation, and final verification

### Task 5: Add explicit TSIM deployment support

**Description:** Add TSIM registry/target mapping, exact reset and positive
cycle-count validation, one lazy simulator load after both host artifacts are
ready, and a complete twelve-sample LLVM/C TSIM matrix. Add focused TSIM
contract tests.

**Acceptance criteria:**

- [ ] TSIM rejects a non-TSIM target before model preparation and reports the
      `libvta_hw` build requirement when registries are absent.
- [ ] TSIM resets to exactly zero before execution and requires a positive
      integer `cycle_count` afterward.
- [ ] The real TSIM matrix compares all twelve samples for both host codegens
      in a fresh process.

**Verification:**

- [ ] Run `test_tsim_deployment.py`.
- [ ] Run the documented real TSIM command with `tsim_sample.json`.

**Dependencies:** Task 4.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_tsim_deployment.py`

**Estimated scope:** Medium, 2 files.

### Task 6: Add CLI, README, and final application checks

**Description:** Add the command-line dispatcher, model provenance README,
preparation/build instructions, HOST/FSIM/TSIM examples, expected result
semantics, and final focused tests. Keep build outputs ignored and document
that runtime assets are application-owned.

**Acceptance criteria:**

- [ ] `run.py` exposes `--simulator`, `--host-codegen`, and output/build
      directory options with the same operational shape as neighboring apps.
- [ ] README commands are executable from the repository root and explain
      model/sample provenance, twelve-label order, and simulator prerequisites.
- [ ] The complete application test directory passes and Python compilation
      succeeds for all new source files.

**Verification:**

- [ ] Run the full focused pytest command from SPEC.md.
- [ ] Run `compileall` with `.envs/tvm-vta-env/bin/python` on the new app.
- [ ] Re-run the real FSIM and TSIM commands after documentation/CLI changes.

**Dependencies:** Task 5.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/README.md`
- `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/.gitignore`

**Estimated scope:** Small, 3 files.

### Checkpoint 3 verification

- [ ] Full focused pytest suite passes.
- [ ] Real FSIM and TSIM runs pass with twelve comparisons each and positive
      simulator activity.
- [ ] No generated build output, bytecode cache, `.envs` directory, or secret
      is staged.
- [ ] Task 5 and Task 6 have separate commits.

## Completion evidence

The implementation is ready for review when the final committed range contains
the six task commits, the full focused test output, the real FSIM/TSIM command
summaries, and a clean multi-repository `git-workflow status` result.
