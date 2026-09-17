# Tasks: MLPerf Tiny ResNet8 Large V2 Deployment

Status: Proposed

All tasks are governed by `SPEC.md` and `PLAN.md` in this directory. A task is
complete only when its acceptance criteria, verification steps, and the
project-wide Definition of Done pass. Generated output is never staged.

## Task 0: Establish the lifecycle baseline

**Owner:** Root.

**Description:** Create matching parent and VTA task branches from the recorded
clean baselines, commit the complete lifecycle batch, and obtain approval of
that exact commit before Build.

**Acceptance criteria:**

- [ ] Parent and VTA branch names, original branches, base OIDs, and clean
  statuses are recorded.
- [ ] `SPEC.md`, `PLAN.md`, and `TASKS.md` form one candidate-integrity-checked
  parent commit.
- [ ] The exact lifecycle allowlist and commit OID are supplied downstream.

**Verification:**

- [ ] Run parent and VTA branch/HEAD/status/submodule preflight.
- [ ] Compare the staged names byte-for-byte with the three-path allowlist.
- [ ] Run `git diff --cached --check` and lifecycle consistency checks.

**Dependencies:** Explicit user confirmation of intent and execution process.

**Files likely touched:**

- `docs/initiatives/mlperf-tiny-resnet8-large-v2/SPEC.md`
- `docs/initiatives/mlperf-tiny-resnet8-large-v2/PLAN.md`
- `docs/initiatives/mlperf-tiny-resnet8-large-v2/TASKS.md`

**Estimated scope:** Medium (3 files)

## Task 1: Authenticate the Large model and license

**Owner:** Default.

**Description:** Copy the approved floating Large model and MLPerf license into
V2, document exact provenance, and add the model/license portion of the asset
contract before any runtime implementation.

**Acceptance criteria:**

- [ ] The committed model is exactly 1,929,208 bytes with SHA-256
  `fb17ae9c1b6d0e5bd97f0f35024f207556261d7310b249716c87cc0628214b0e`.
- [ ] Provenance records the exact source-relative path, tensor/operator/channel
  contract, quantization policy, and Apache-2.0 license.
- [ ] Model identity/topology and license tests fail before V2 assets exist and
  pass after the authenticated copy.

**Verification:**

- [ ] Compare source and committed model hashes and byte counts.
- [ ] Run the model/license-focused selection from V2 `test_assets.py`.
- [ ] Run `git -C vta diff --check`.

**Dependencies:** Task 0 and approved lifecycle commit.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/model/pretrainedResnet_large_float.tflite`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/model/README.md`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/LICENSE.mlperf-tiny`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_assets.py`

**Estimated scope:** Medium (4 files)

## Task 2: Copy sample bundle part one

**Owner:** Default.

**Description:** Copy samples for labels 0 through 4 byte-for-byte from V1.

**Acceptance criteria:**

- [ ] The five PNGs match their V1 SHA-256 values and decode as 32x32 RGB.
- [ ] No sample is regenerated or read from an unauthenticated dataset.

**Verification:**

- [ ] Compare all five V1/V2 files with `cmp` and SHA-256.
- [ ] Confirm only the five approved paths are staged.

**Dependencies:** Task 1.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/00-airplane.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/01-automobile.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/02-bird.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/03-cat.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/04-deer.png`

**Estimated scope:** Medium (5 static files)

## Task 3: Copy sample bundle part two

**Owner:** Default.

**Description:** Copy samples for labels 5 through 9 byte-for-byte from V1.

**Acceptance criteria:**

- [ ] The five PNGs match their V1 SHA-256 values and decode as 32x32 RGB.
- [ ] No sample is regenerated or read from an unauthenticated dataset.

**Verification:**

- [ ] Compare all five V1/V2 files with `cmp` and SHA-256.
- [ ] Confirm only the five approved paths are staged.

**Dependencies:** Task 2.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/05-dog.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/06-frog.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/07-horse.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/08-ship.png`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/09-truck.png`

**Estimated scope:** Medium (5 static files)

## Task 4: Complete sample provenance tests

**Owner:** Default.

**Description:** Copy the V1 manifest exactly and complete V2 asset tests for
manifest metadata, PNG bytes/pixels, optional local `test_batch` comparison,
and deterministic extractor output.

**Acceptance criteria:**

- [ ] V2 manifest is byte-for-byte identical to V1 and every referenced PNG is
  present.
- [ ] Full V2 asset tests authenticate model, license, manifest, and samples.
- [ ] Optional local CIFAR-10 checks remain conditional exactly as in V1.

**Verification:**

- [ ] Run full V2 `test_assets.py` with the repository Python environment.
- [ ] Run `git -C vta diff --check`.

**Dependencies:** Tasks 1-3.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/samples/manifest.json`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_assets.py`

**Estimated scope:** Small (2 files)

## Task 5: Implement the deterministic Large pipeline

**Owner:** Default.

**Description:** Adapt V1 pipeline tests to the exact Large model contract,
observe their failure without V2 implementation, then implement import,
one-time quantization, sample loading, and strict four-region routing.

**Acceptance criteria:**

- [ ] Exact hash, tensor names, shapes, dtypes, operator sequence, and
  `40/80/160` channels are validated.
- [ ] Quantization retains `global_scale=8.0` and `skip_conv_layers=[0]`.
- [ ] `mlperf_resnet_large` yields four ordered VTA symbols with one
  convolution each, five HOST convolutions, and four VTA composites.

**Verification:**

- [ ] Record a RED focused-test failure before adding `model_pipeline.py`.
- [ ] Run full V2 `test_model_pipeline.py` GREEN.
- [ ] Run V2 asset and pipeline tests together.

**Dependencies:** Task 4.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/model_pipeline.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_model_pipeline.py`

**Estimated scope:** Small (2 files)

## Checkpoint A: Assets and model pipeline

- [ ] Tasks 1-5 meet all acceptance criteria.
- [ ] Focused tests pass from the frozen candidate.
- [ ] The VTA commit contains only the approved V2 asset/pipeline paths.
- [ ] An independent Reviewer returns Pass, or all required findings are fixed,
  reverified, recommitted, and re-reviewed.

## Task 6: Add V2 Graph artifact bundles

**Owner:** Default.

**Description:** Adapt Graph bundle tests for `resnet8_large`, observe their V2
failure, then copy the verified V1 bundle helper without unrelated changes.

**Acceptance criteria:**

- [ ] Graph JSON, params, DSO, source, hashes, manifest, atomic replacement,
  rollback, path safety, and disk-only reload contracts match V1.
- [ ] Manifest identity is `resnet8_large`; mixed bundles require exactly the
  four Large VTA symbols.

**Verification:**

- [ ] Record RED before `graph_artifacts.py` exists.
- [ ] Run full V2 `test_graph_artifacts.py` GREEN.
- [ ] Run `git -C vta diff --check`.

**Dependencies:** Checkpoint A.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_graph_artifacts.py`

**Estimated scope:** Small (2 files)

## Task 7: Add HOST and FSIM deployment

**Owner:** Default.

**Description:** Adapt HOST/FSIM tests first, then copy and minimally specialize
the V1 runtime for the V2 model path, four symbols, and Large artifact identity.

**Acceptance criteria:**

- [ ] LLVM/C reference and mixed bundles build, export, reload, and validate.
- [ ] All ten samples have exact reference/mixed equality and cross-host
  reference equality.
- [ ] Each mixed FSIM run independently reports positive GEMM/load/store
  activity.

**Verification:**

- [ ] Record RED before `runtime.py` exists.
- [ ] Run V2 `test_graph_artifacts.py` and `test_host_deployment.py` GREEN.
- [ ] Run the real V2 FSIM LLVM/C matrix.

**Dependencies:** Task 6.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_host_deployment.py`

**Estimated scope:** Small (2 files)

## Task 8: Add CLI, TSIM deployment, and user documentation

**Owner:** Default.

**Description:** Adapt TSIM/CLI tests first, then add the V1-compatible CLI and
V2 README with accurate Large model and four-region commands/results.

**Acceptance criteria:**

- [ ] CLI preserves all V1 options/defaults and routes to V2-local runtime.
- [ ] TSIM remains lazy, executes LLVM/C matrices, compares all outputs exactly,
  and independently records positive cycles.
- [ ] README documents prerequisites, FSIM/TSIM commands, artifact layout,
  four regions, and non-claims.

**Verification:**

- [ ] Record RED before `run.py` exists.
- [ ] Run V2 `test_tsim_deployment.py` GREEN.
- [ ] Run the real V2 TSIM LLVM/C matrix in a fresh configured process.

**Dependencies:** Task 7.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/README.md`

**Estimated scope:** Medium (3 files)

## Checkpoint B: Complete V2 application

- [ ] Tasks 6-8 meet all acceptance criteria.
- [ ] Focused tests plus real FSIM and TSIM matrices pass from the frozen
  candidate.
- [ ] V1 files, TVM, and shared VTA compiler/runtime code remain unchanged.
- [ ] An independent Reviewer returns Pass, or all required findings are fixed,
  reverified, recommitted, and re-reviewed.

## Task 9: Integrate V2 into the aggregate gate

**Owner:** Default.

**Description:** Append explicit V2 HOST/FSIM and fresh-process TSIM stages to
the maintained full gate and update its documentation without changing the
script CLI or weakening V1 coverage.

**Acceptance criteria:**

- [ ] V1 structural, FSIM, HOST/FSIM, TSIM, and retired-reference stages remain
  intact.
- [ ] V2 assets, model pipeline, HOST/FSIM, and real TSIM matrix run in a stable
  documented order.
- [ ] `scripts/README.md` describes both deployments and unchanged
  prerequisites.

**Verification:**

- [ ] Run `bash scripts/test_vta_byoc.sh` from the frozen staged candidate.
- [ ] Require no tracked changes after verification and a stable candidate
  fingerprint.
- [ ] Commit the reviewed VTA child first, validate its parent pointer, then
  commit exactly `scripts/test_vta_byoc.sh`, `scripts/README.md`, and `vta` in
  the parent.

**Dependencies:** Checkpoint B.

**Files likely touched:**

- `scripts/test_vta_byoc.sh`
- `scripts/README.md`
- `vta` (gitlink only, after the verified child commit)

**Estimated scope:** Medium (2 files plus one gitlink)

## Checkpoint C: Full gate and final review

- [ ] Task 9 meets all acceptance criteria and the complete gate exits zero.
- [ ] V1 is unchanged and passes in the same gate.
- [ ] Parent and VTA branches are clean at their verified commits.
- [ ] Final independent Reviewer returns Pass with no unresolved required
  findings.
- [ ] Integration into `dev` / `vta_v0.0.2` remains pending separate user Ship
  authorization.
