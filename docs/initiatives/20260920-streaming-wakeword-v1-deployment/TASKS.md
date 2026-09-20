# Tasks: MLPerf Tiny Streaming Wakeword v1 Deployment

Each checkpoint is executed by a fresh Default boundary. Tasks within a
checkpoint are completed in order and committed separately after their own
verification. No task may change the approved model, three-class mapping, or
preprocessing contract without Root escalation.

## Checkpoint 1: Assets and contracts

### Task 1.1: Create repository-owned streaming wakeword assets

**Description:** Create the new application directories, copy the exact
`str_ww_ref_model.tflite`, select one deterministic WAV per `Marvin`,
`Silence`, and `Unknown`, and add model provenance/license documentation plus
the manifest with byte lengths and SHA-256 hashes.

**Acceptance criteria:**

- The model checksum is
  `3af8550895ba7d5c584277102b5075c52dcfa63ba9d2b2240f37c4e6abd5dd2b`.
- The manifest contains exactly three entries in class order `Marvin`,
  `Silence`, `Unknown` and records source-relative provenance and hashes.
- The silence sample is a deterministic one-second segment from the selected
  background WAV; all committed WAVs are mono 16-bit 16 kHz inputs.

**Verification:** Inspect hashes and run the focused asset tests after Task
1.2.

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model/str_ww_ref_model.tflite`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model/README.md`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/LICENSE.mlperf-tiny`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/samples/*.wav`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/samples/manifest.json`

**Dependencies:** None.

**Estimated scope:** Medium (asset files plus metadata).

### Task 1.2: Add strict asset tests

**Description:** Add `pytest` tests that authenticate the committed model,
validate the TFLite tensor contract and three WAV assets, and ensure the
manifest is safe and independent of `.envs` at runtime.

**Acceptance criteria:**

- Tests validate model bytes, model input/output names/shapes/dtypes/quantization,
  exact class mapping, file hashes, audio format, and deterministic selection
  provenance.
- Tests reject missing, extra, symlinked, malformed, or `.envs`-dependent
  runtime assets.

**Verification:**

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_assets.py
```

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_assets.py`

**Dependencies:** Task 1.1.

**Estimated scope:** Small (one test module).

### Checkpoint 1 verification

- [ ] Asset tests pass.
- [ ] The three committed samples and model are byte-authenticated.
- [ ] No `.envs` file is modified.

## Checkpoint 2: Feature and Relay model pipeline

### Task 2.1: Implement deterministic streaming feature preparation

**Description:** Implement strict WAV loading and the NumPy equivalent of the
checked-in streaming wakeword log-mel pipeline, producing the model's
`(1, 30, 1, 40)` int8 input tensor using the committed scale and zero point.

**Acceptance criteria:**

- 16 kHz mono PCM is padded/trimmed to one second and transformed with the
  specified preemphasis, 64 ms/32 ms STFT, Hamming window, 40-bin mel filter,
  log scaling, clipping, and int8 quantization.
- Invalid audio and feature shape/range/dtype fail with clear errors.
- The three committed samples produce deterministic tensors across repeated
  calls without TensorFlow or `.envs` access.

**Verification:** Add and run focused preprocessing tests in Task 2.2.

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model_pipeline.py`

**Dependencies:** Checkpoint 1.

**Estimated scope:** Medium (one implementation module).

### Task 2.2: Implement TFLite import and VTA partition contract

**Description:** Extend the model pipeline with authenticated TFLite import,
Relay type checks, graph normalization required by VTA, exactly-once VTA
partitioning, and routing inspection; add tests for the complete pipeline.

**Acceptance criteria:**

- Import validates the committed model checksum, exact operator topology, and
  int8 input/output contract.
- The reference and mixed graphs retain the expected input/output shapes and
  the mixed graph contains convolution-bearing VTA external functions.
- Tests prove partitioning is invoked once and reject missing/invalid regions.

**Verification:**

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_assets.py \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_model_pipeline.py
```

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/model_pipeline.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_model_pipeline.py`

**Dependencies:** Task 2.1.

**Estimated scope:** Medium (implementation plus one test module).

### Checkpoint 2 verification

- [ ] Asset and model-pipeline tests pass.
- [ ] Three sample tensors have the exact input contract.
- [ ] Model import and one-time partitioning are structurally validated.

## Checkpoint 3: Artifacts and HOST/FSIM runtime

### Task 3.1: Add authenticated graph artifact export/reload

**Description:** Add the graph artifact module following neighboring
applications, including atomic publication, file hashes, host source capture,
metadata, and reference/mixed symbol validation.

**Acceptance criteria:**

- Reference and mixed bundles contain graph JSON, params, shared library,
  source metadata, and a validated manifest.
- Reload rejects path traversal, symlinks, missing files, hash mismatches,
  wrong model metadata, and wrong VTA symbol contracts.

**Verification:**

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_graph_artifacts.py
```

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_graph_artifacts.py`

**Dependencies:** Checkpoint 2.

**Estimated scope:** Medium (implementation plus one test module).

### Task 3.2: Implement HOST and FSIM runtime execution

**Description:** Build and reload reference/mixed graphs for LLVM or C host
codegen, execute the three samples, keep HOST reference-only, and compare
reference/mixed FSIM results with positive profiler activity.

**Acceptance criteria:**

- HOST executes exactly three reference samples without loading FSIM/TSIM.
- FSIM executes both bundles, compares output tensors elementwise, reports
  class indices for all samples, and rejects zero or malformed activity.
- Runtime validates manifest order, input/output shape/dtype, and artifact
  symbol contracts before execution.

**Verification:**

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_host_deployment.py
```

When available:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py \
  --simulator host --host-codegen llvm
```

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py \
  --simulator fsim --host-codegen all
```

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_host_deployment.py`

**Dependencies:** Task 3.1.

**Estimated scope:** Medium (implementation plus one test module).

### Checkpoint 3 verification

- [ ] Asset, pipeline, artifact, and HOST/FSIM contract tests pass.
- [ ] HOST does not initialize a simulator.
- [ ] Real HOST/FSIM runs are recorded when build libraries are present.

## Checkpoint 4: CLI, docs, TSIM compatibility, and repository gate

### Task 4.1: Add CLI and reproducible deployment documentation

**Description:** Add the `run.py` CLI and README covering model/sample
provenance, prerequisites, HOST/FSIM/TSIM commands, output interpretation, and
the non-benchmark nature of the check.

**Acceptance criteria:**

- CLI exposes the approved simulator, host-codegen, and output-directory
  options with deterministic LLVM/C matrix behavior.
- README commands are executable from the repository root with the pinned
  environment and do not instruct runtime reads from `.envs`.

**Verification:** Run CLI parser tests and compile the new Python modules.

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/README.md`

**Dependencies:** Task 3.2.

**Estimated scope:** Small (two files).

### Task 4.2: Add TSIM checks and deployment tests

**Description:** Extend the runtime with explicit TSIM target/registry/session
checks and add the three-sample TSIM contract tests, preserving fresh-process
and positive-cycle requirements.

**Acceptance criteria:**

- TSIM refuses the wrong VTA target or missing `libvta_hw` registries with
  actionable diagnostics.
- TSIM clears counters before execution, runs all three samples, and requires
  a positive integer `cycle_count`.

**Verification:**

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_tsim_deployment.py
```

When available:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py \
  --simulator tsim --host-codegen all
```

**Files:**

- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_tsim_deployment.py`

**Dependencies:** Task 4.1.

**Estimated scope:** Medium (three files, with runtime/CLI integration).

### Task 4.3: Register the deployment in the complete BYOC gate

**Description:** Add the streaming asset/pipeline/artifact/runtime tests and
HOST/FSIM plus HOST/TSIM invocations to `scripts/test_vta_byoc.sh`, preserving
all existing commands and failure behavior.

**Acceptance criteria:**

- The complete gate runs the streaming focused tests and both simulator
  deployment commands in the same style as the neighboring applications.
- Existing gate commands and required environment validation remain unchanged.

**Verification:** Run the script's shell syntax check, the complete focused
  streaming suite, and `bash scripts/test_vta_byoc.sh` when prerequisites exist.

**Files:**

- `scripts/test_vta_byoc.sh`

**Dependencies:** Tasks 4.1 and 4.2.

**Estimated scope:** Small (one shared script).

### Checkpoint 4 verification

- [ ] The complete focused suite passes.
- [ ] New modules compile successfully.
- [ ] BYOC gate includes streaming HOST/FSIM/TSIM coverage without weakening
      existing checks.
- [ ] Real TSIM run is recorded when `libvta_hw` and configuration are present.

## Final verification and review handoff

- [ ] Check repository status and per-repository commit map through
      `./.agents/custom/scripts/git-workflow status`.
- [ ] Run the complete focused suite and applicable real HOST/FSIM/TSIM runs.
- [ ] Run `bash .agents/custom/scripts/test-role-workflow`.
- [ ] Provide Reviewer the approved `INTENT.md`, `SPEC.md`, `PLAN.md`, and
      `TASKS.md`, all checkpoint/fix commit OIDs, verification output, and the
      exact base-to-tip range.
