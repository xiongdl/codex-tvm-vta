# Tasks: MLPerf Tiny Anomaly Detection v1 deployment

## Checkpoint 1: Assets and compiler contract

### Task 1: Add authenticated model and license assets

**Description:** Copy the exact `ad01_fp32.tflite` model from `.envs` into the
new application and preserve the applicable anomaly-detection license notice.

**Acceptance criteria:**

- [ ] The committed model hash is the approved SHA-256 from `SPEC.md`.
- [ ] The model is at `model/ad01_fp32.tflite` and the license is at
      `LICENSE.mlperf-tiny`.
- [ ] No `.envs` path is written into runtime code or Git.

**Verification:** Run the model hash assertions from `test_assets.py` and
confirm `git status --short` has no `.envs` file staged.

**Dependencies:** None

**Files likely touched:** `model/ad01_fp32.tflite`, `LICENSE.mlperf-tiny`

**Estimated scope:** Small

### Task 2: Add the five normal samples and manifest skeleton

**Description:** Copy the first five normal ToyCar WAVs and create the normal
entries in the deterministic manifest.

**Acceptance criteria:**

- [ ] Five regular mono 16-bit 16 kHz normal WAVs are under `samples/`.
- [ ] Manifest entries record order, class, source-relative path, committed
      filename, byte length, and SHA-256.

**Verification:** Validate WAV headers and hashes with the repository Python
environment.

**Dependencies:** Task 1

**Files likely touched:** The five `samples/normal_id_01_*.wav` files and
`samples/manifest.json`

**Estimated scope:** Medium (asset-only)

### Task 3: Add the five anomaly samples and complete the manifest

**Description:** Copy the first five anomaly ToyCar WAVs and complete the
manifest with class `anomaly`, label `1`, and the approved five/five order.

**Acceptance criteria:**

- [ ] Five regular mono 16-bit 16 kHz anomaly WAVs are under `samples/`.
- [ ] The manifest contains exactly ten unique entries: five normal followed
      by five anomaly files.
- [ ] Every committed sample hash matches the `.envs` source byte hash.

**Verification:** Run the complete manifest/hash portion of `test_assets.py`.

**Dependencies:** Task 2

**Files likely touched:** The five `samples/anomaly_id_01_*.wav` files and
`samples/manifest.json`

**Estimated scope:** Medium (asset-only)

### Task 4: Add provenance and audio asset tests

**Description:** Write tests first for model/license/sample provenance,
manifest balance/order, WAV headers, byte hashes, and application-local paths.

**Acceptance criteria:**

- [ ] Tests fail for a missing or altered asset and pass for exact bytes.
- [ ] Tests enforce five normal then five anomaly entries and reject duplicate
      or path-escaping filenames.
- [ ] Tests validate every WAV is mono, 16-bit, 16 kHz, and non-empty.

**Verification:**

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_assets.py
```

**Dependencies:** Task 3

**Files likely touched:** `tests/test_assets.py`

**Estimated scope:** Small

### Task 5: Implement audio features and Relay model pipeline

**Description:** Add RED tests and the minimal implementation for WAV feature
extraction, TFLite contract validation, deterministic dense-to-1x1-conv
rewriting, one-time quantization, and seven-region VTA routing.

**Acceptance criteria:**

- [ ] `load_sample` returns a finite non-empty float32 `(N, 640)` matrix using
      the approved baseline constants.
- [ ] The exact TFLite/Relay input-output contract and model hash are checked.
- [ ] Only block-compatible dense layers are rewritten, the two 8-channel
      bottleneck layers remain host dense operations, and seven VTA symbols are
      produced after quantization.

**Verification:** Observe RED tests before implementation; run
`test_assets.py` and `test_model_pipeline.py`; build reference and mixed Relay
modules under FSIM config without loading a simulator during preparation.

**Dependencies:** Task 4

**Files likely touched:** `model_pipeline.py`, `tests/test_model_pipeline.py`

**Estimated scope:** Medium

### Checkpoint 1 verification

- [ ] Assets are exact and manifest balance is five normal/five anomaly.
- [ ] Focused asset and model tests pass.
- [ ] Model preparation reports seven VTA regions and no unexpected rewrite.
- [ ] The checkpoint is committed through `git-workflow`.

## Checkpoint 2: Artifacts and HOST/FSIM execution

### Task 6: Add authenticated graph bundle export/reload

**Description:** Port the established graph-artifact implementation into the
new application and bind it to anomaly artifact names, model hash, simulator
metadata, source manifests, and seven VTA symbols.

**Acceptance criteria:**

- [ ] Reference and mixed bundles export atomically with graph, params, DSO,
      manifest, and inspectable host source.
- [ ] Reload validates hashes, safe paths, source availability, and symbols.
- [ ] Partial exports are removed on failure.

**Verification:** Write RED export/reload and cleanup tests, then run
`tests/test_graph_artifacts.py`.

**Dependencies:** Task 5

**Files likely touched:** `graph_artifacts.py`, `tests/test_graph_artifacts.py`

**Estimated scope:** Medium

### Task 7: Implement HOST/FSIM runtime and score execution

**Description:** Build LLVM/C reference and mixed bundles, reload them, execute
all frame vectors from the ten WAVs, compute one reconstruction score per file,
and validate FSIM activity.

**Acceptance criteria:**

- [ ] Reference and mixed graphs use their own params and the same ordered
      ten-sample manifest.
- [ ] Runs record ten comparisons in five normal/five anomaly order; tensor
      shape/dtype and score agreement meet the fixed tolerance.
- [ ] FSIM counters are reset, positive after execution, and tied to seven
      expected VTA symbols.

**Verification:** Write RED tests; run focused HOST/FSIM tests; run the LLVM
FSIM CLI and then the complete LLVM/C FSIM matrix.

**Dependencies:** Task 6

**Files likely touched:** `runtime.py`, `tests/test_host_deployment.py`

**Estimated scope:** Medium

### Task 8: Add CLI and application documentation

**Description:** Add `run.py` and README with prerequisites, provenance,
sample order, FSIM/TSIM commands, score semantics, and non-goals.

**Acceptance criteria:**

- [ ] CLI supports `--output-dir`, `--host-codegen llvm|c|all`, and
      `--simulator fsim|tsim` with sibling-compatible defaults.
- [ ] README commands are executable from the repository root with the pinned
      Python environment.
- [ ] Documentation states each WAV produces one score and the set is five
      normal plus five anomaly files.

**Verification:** Run `run.py --help` and an LLVM FSIM CLI execution that
reports ten comparisons.

**Dependencies:** Task 7

**Files likely touched:** `run.py`, `README.md`

**Estimated scope:** Small

### Checkpoint 2 verification

- [ ] Artifact and HOST/FSIM tests pass.
- [ ] LLVM/C FSIM matrix builds, reloads, scores ten files, and reports
      positive counters.
- [ ] CLI help and README commands agree with implementation.
- [ ] The checkpoint is committed through `git-workflow`.

## Checkpoint 3: TSIM and repository integration

### Task 9: Add TSIM contract and matrix validation

**Description:** Add TSIM validation for lazy initialization, exact target/config
mapping, positive cycle activity, and the same ten score comparisons.

**Acceptance criteria:**

- [ ] TSIM rejects a wrong environment before model preparation.
- [ ] All LLVM/C bundles build before one lazy TSIM load in a fresh process.
- [ ] Each host variant reports ten five/five comparisons and positive integer
      `cycle_count`.

**Verification:** Run focused TSIM contract tests and the complete anomaly TSIM
matrix with `tsim_sample.json`.

**Dependencies:** Task 8

**Files likely touched:** `tests/test_tsim_deployment.py`, `runtime.py`

**Estimated scope:** Medium

### Task 10: Integrate the anomaly deployment into the aggregate gate

**Description:** Add anomaly asset/model/HOST/FSIM and HOST/TSIM commands to
`scripts/test_vta_byoc.sh`, preserving all existing gates and documenting any
maintained script interface change.

**Acceptance criteria:**

- [ ] Aggregate script invokes new focused tests under FSIM config.
- [ ] Aggregate script invokes the new TSIM CLI matrix under TSIM config.
- [ ] Existing ResNet, VWW, simulator, compilation, and retired-reference
      checks remain present and unchanged in behavior.

**Verification:** Run `bash scripts/test_vta_byoc.sh`,
`bash .agents/custom/scripts/test-role-workflow`, and inspect staged changes
for secrets, `.envs` paths, and build artifacts.

**Dependencies:** Task 9

**Files likely touched:** `scripts/test_vta_byoc.sh`, `scripts/README.md`

**Estimated scope:** Small

### Checkpoint 3 verification

- [ ] Anomaly TSIM matrix passes with positive cycles.
- [ ] Complete BYOC gate passes with all existing gates retained.
- [ ] Python compilation passes for the new application.
- [ ] The checkpoint is committed through `git-workflow`.

## Final review checklist

- [ ] All implementation commits are recorded in the per-repository commit map.
- [ ] Reviewer receives approved `INTENT.md`, `SPEC.md`, `PLAN.md`, and
      `TASKS.md`, verification outputs, and exact base-to-tip range.
- [ ] Any actionable review finding is fixed and re-reviewed before completion.
