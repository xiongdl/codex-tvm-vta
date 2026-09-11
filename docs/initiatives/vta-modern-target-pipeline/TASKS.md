# Tasks: VTA Modern Target Pipeline

Status: Complete

All tasks are governed by the approved specs in this directory. Checkboxes are
updated only when acceptance and verification evidence both pass.

## Task 1: Lock target and automatic-import contracts

**Description:** Add isolated-process tests for native `vta` TargetKind
registration, deterministic import behavior, runtime-only bypass, and loader
failure diagnostics before implementing the loader.

**Acceptance criteria:**

- [x] Tests distinguish full TVM and runtime-only imports.
- [x] Tests require one native `vta` target registration and actionable missing
  or unloadable library errors.
- [x] Tests do not register or invoke `relay.ext.vta`.

**Verification:**

- [x] New focused tests fail for the expected missing modern behavior.
- [x] Existing Python package import tests remain attributable and deterministic.

**Dependencies:** None

**Files likely touched:**

- `vta/tests/python/unittest/test_target_extension.py`
- `vta/tests/python/unittest/test_byoc_contract.py`
- `vta/tests/python/unittest/byoc_utils.py`

**Estimated scope:** Medium (3 files)

## Task 2: Build and auto-load the native target extension

**Description:** Add the native target skeleton and extend existing build and
library-location paths so full `import vta` automatically loads it while
runtime-only import skips it.

**Acceptance criteria:**

- [x] `build_vta_lib.sh --target libtvm-vta-ext` produces the platform library.
- [x] `import vta` registers `Target("vta")` once; reload is safe.
- [x] Runtime-only import does not search for or load the compiler library.

**Verification:**

- [x] Run the Task 1 isolated tests.
- [x] Build the target on the current macOS host.
- [x] Confirm `git -C tvm status --short` is empty.

**Dependencies:** Task 1

**Files likely touched:**

- `vta/CMakeLists.txt`
- `vta/src/compiler/target.cc`
- `vta/python/vta/libinfo.py`
- `vta/python/vta/__init__.py`
- `scripts/build_vta_lib.sh`

**Estimated scope:** Medium (5 files)

## Checkpoint A: Target extension foundation

- [x] Tasks 1-2 acceptance evidence passes.
- [x] Build/load errors name the failing artifact and recovery command.
- [x] No old external compiler callback was added as an intermediate bridge.

## Task 3: Implement the approved single-convolution partition matrix

**Description:** Extend patterns and partitioning for 1x1/3x3, stride 1/2,
aligned static shapes, and one composite per outlined VTA function while
preserving LLVM fallback for every near miss.

**Acceptance criteria:**

- [x] The full supported/rejected capability matrix is parameterized in tests.
- [x] Adjacent supported candidates produce separate deterministic VTA symbols.
- [x] Repeated partitioning is structurally stable and GraphPack-free.

**Verification:**

- [x] Run focused contract and partition tests under the default VTA config.
- [x] Inspect outlined functions for exactly one composite each.

**Dependencies:** Task 2

**Files likely touched:**

- `vta/python/vta/relay/patterns.py`
- `vta/python/vta/relay/partition.py`
- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_partition.py`
- `vta/tests/python/unittest/test_byoc_contract.py`

**Estimated scope:** Medium (5 files)

## Task 4: Legalize both standard layouts and convolution variants

**Description:** Make region-local legalization accept NHWC/HWIO and
NCHW/OIHW, compile-time pack constants, lower approved kernels/strides, and
restore the exact original boundary layout.

**Acceptance criteria:**

- [x] Both layout pairs lower for all approved kernel/stride variants.
- [x] Packed layouts and constants remain internal to one VTA function.
- [x] Output shape, dtype, layout, and integer values match equivalent Relay.

**Verification:**

- [x] Run legalization and lowering matrix tests.
- [x] Assert GEMM tensorization and expected VTA TIR structure.

**Dependencies:** Task 3

**Files likely touched:**

- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`
- `vta/tests/python/unittest/test_byoc_partition.py`

**Estimated scope:** Medium (4 files)

## Task 5: Connect the native IRModule RelayToTIR hook

**Description:** Implement the registered typed module pass that validates and
lowers every VTA function in one invocation, using the approved VTA-owned
lowering components without the legacy external compiler callback.

**Acceptance criteria:**

- [x] The target exposes a typed non-null RelayToTIR hook.
- [x] One hook invocation lowers all VTA functions and preserves non-VTA IR.
- [x] Malformed annotated functions fail before partial module mutation.

**Verification:**

- [x] Run isolated native-hook tests for zero, one, and multiple VTA regions.
- [x] Prove `relay.ext.vta` is absent and not invoked.
- [x] Prove Ethos-U-equivalent module replacement: every existing VTA
  GlobalVar is updated in place to a PrimFunc and no global or nested Relay
  Function retaining `Compiler="vta"` reaches `LowerTE`.
- [x] Run Task 3-4 focused suites.

**Dependencies:** Task 4

**Files likely touched:**

- `vta/src/compiler/relay_to_tir.cc`
- `vta/src/compiler/target.cc`
- `vta/CMakeLists.txt`
- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/test_target_hooks.py`

**Estimated scope:** Medium (5 files)

## Checkpoint B: Relay partition and lowering

- [x] Tasks 3-5 acceptance evidence passes.
- [x] Both layouts and all approved convolution variants tensorize.
- [x] Unsupported candidates remain buildable for LLVM.
- [x] The pinned TVM checkout is clean.

## Task 6: Define canonical VTA ABI fingerprint generation

**Description:** Generate one stable fingerprint from normalized ABI-relevant
VTA definitions plus an explicit schema version and expose compile-time values
to compiler and runtime builds.

**Acceptance criteria:**

- [x] Ordering, JSON formatting, path, and timestamp do not alter the result.
- [x] Every ABI-relevant definition and schema version alters the result.
- [x] Compiler extension and FSIM consume generated values from one source.

**Verification:**

- [x] Run deterministic and sensitivity tests across generated fixtures.
- [x] Build extension and FSIM with the default config and compare fingerprints.

**Dependencies:** Task 2

**Files likely touched:**

- `vta/config/vta_config.py`
- `vta/include/vta/runtime.h`
- `vta/CMakeLists.txt`
- `vta/tests/python/unittest/test_abi_fingerprint.py`

**Estimated scope:** Medium (4 files)

## Task 7: Enforce configuration checks in FSIM runtime

**Description:** Add `VTACheckConfig(uint64_t)` to the stable VTA C runtime and
make matching calls idempotent while mismatches fail before any allocation or
command/profiler activity.

**Acceptance criteria:**

- [x] Matching checks succeed repeatedly without side effects.
- [x] Mismatch diagnostics contain expected and actual fingerprints.
- [x] No VTA activity occurs after a failed check.

**Verification:**

- [x] Run focused C/Python FSIM fingerprint tests.
- [x] Run existing VTA instruction and FSIM smoke tests.

**Dependencies:** Task 6

**Files likely touched:**

- `vta/include/vta/runtime.h`
- `vta/src/runtime/runtime.cc`
- `vta/src/sim/sim_driver.cc`
- `vta/tests/python/unittest/test_abi_fingerprint.py`

**Estimated scope:** Medium (4 files)

## Task 8: Build standard LLVM modules through native TIRToRuntime

**Description:** Validate all VTA PrimFuncs, inject configuration checks, invoke
host LLVM codegen directly, return one standard module, and prove its complete
export/reload/FSIM lifecycle.

**Acceptance criteria:**

- [x] One/many valid PrimFuncs produce one module with every expected symbol.
- [x] Invalid input fails before partial codegen and no public `tvm.build` recurs.
- [x] Exported/reloaded fixture executes on FSIM and equals pure LLVM exactly.

**Verification:**

- [x] Run codegen and runtime tests for symbols, malformed input, and lifecycle.
- [x] Run matched/mismatched fingerprint execution tests.
- [x] Require positive GEMM/load/store profiler counters.

**Dependencies:** Tasks 5 and 7

**Files likely touched:**

- `vta/src/compiler/tir_to_runtime.cc`
- `vta/src/compiler/target.cc`
- `vta/CMakeLists.txt`
- `vta/tests/python/unittest/test_byoc_codegen.py`
- `vta/tests/python/unittest/test_byoc_runtime.py`

**Estimated scope:** Medium (5 files)

## Task 9: Finalize import validation for complete target hooks

**Description:** Strengthen automatic import validation so a full TVM import
requires both correctly typed modern hooks while preserving runtime-only bypass
and clear diagnostics.

**Acceptance criteria:**

- [x] Full import validates TargetKind, RelayToTIR, and TIRToRuntime.
- [x] Re-import/reload preserves one hook identity.
- [x] Incomplete or incompatible extension fails immediately and clearly.

**Verification:**

- [x] Run all target-extension isolated tests.
- [x] Import in full and simulated runtime-only subprocesses.

**Dependencies:** Task 8

**Files likely touched:**

- `vta/python/vta/__init__.py`
- `vta/python/vta/libinfo.py`
- `vta/tests/python/unittest/test_target_extension.py`

**Estimated scope:** Medium (3 files)

## Checkpoint C: Runtime artifact

- [x] Tasks 6-9 acceptance evidence passes.
- [x] Compile/export is independent of simulator loading.
- [x] Reloaded artifact resolves FSIM ABI and executes accelerator work.
- [x] Configuration mismatch fails before profiler activity.

## Task 10: Add lightweight dependencies and licensed deterministic assets

**Description:** Verify/pin compatible `tflite` and Pillow packages, copy the
approved unmodified model and license/provenance, and generate the fixed ten PNG
samples plus manifest from user-supplied CIFAR-10.

**Acceptance criteria:**

- [x] Setup automation installs only the approved additional dependencies.
- [x] Model and PNG hashes/provenance/license are committed and verified.
- [x] Samples are the first `test_batch` occurrence of labels 0 through 9.

**Verification:**

- [x] Recreate hashes and validate manifest uniqueness/completeness.
- [x] Decode PNGs and compare exact pixels with local `test_batch` when present.
- [x] Confirm local full datasets and `tiny-v1.4` remain untracked.

**Dependencies:** Checkpoint C

**Files likely touched:**

- `scripts/setup_tvm_vta_env.sh`
- `scripts/extract_mlperf_resnet_samples.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/model/README.md`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/samples/manifest.json`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/LICENSE.mlperf-tiny`

Binary model/PNG assets are additional approved outputs of this task.

**Estimated scope:** Medium (5 source/metadata files plus approved assets)

## Task 11: Import, quantize, and validate ResNet routing

**Description:** Implement deterministic model import, fixed one-time Relay
quantization, preprocessing, and exact structural validation for pure and mixed
branches.

**Acceptance criteria:**

- [x] Model input/output/topology assertions match the committed artifact.
- [x] Quantization runs once with global scale 8.0 and skipped first convolution.
- [x] Partitioning produces exactly eight one-convolution VTA functions and LLVM
  fallback from the shared quantized module.

**Verification:**

- [x] Run fast model, preprocessing, quantization, and routing tests.
- [x] Confirm no TensorFlow, calibration, GraphPack, or AutoTVM import/call.

**Dependencies:** Task 10

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/model_pipeline.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_model_pipeline.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`

**Estimated scope:** Medium (4 files)

## Task 12: Execute and compare both reloaded HOST artifacts

**Description:** Complete the application with Graph Executor export/reload,
ten-image reference comparison, symbol/fingerprint validation, and FSIM profiler
proof.

**Acceptance criteria:**

- [x] Both non-committed artifacts export and reload through standard TVM APIs.
- [x] All ten tensors and top-1 indices agree exactly.
- [x] Expected VTA symbols exist and FSIM GEMM/load/store counters are positive.

**Verification:**

- [x] Run the documented application command from a clean build-output state.
- [x] Run the end-to-end pytest without full CIFAR-10 or local `tiny-v1.4`.

**Dependencies:** Task 11

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/.gitignore`

**Estimated scope:** Medium (5 files)

## Checkpoint D: MLPerf HOST deployment

- [x] Tasks 10-12 acceptance evidence passes.
- [x] App is self-contained within approved committed assets/dependencies.
- [x] Exact routing and ten-image equality pass after artifact reload.
- [x] No FVP, CMSIS-NN, TVM `c` target, AOT/CRT, TSIM, or AutoTVM is used.

## Task 13: Migrate active Relay consumers and documentation

**Description:** Replace old compiler registration in README, deployment app,
frontend tutorial, and tests with automatic extension import, explicit
partitioning, and modern `Target("vta")`, preserving host fallback.

**Acceptance criteria:**

- [x] Every inventoried active Relay consumer uses the modern call sequence.
- [x] Documentation distinguishes modern `vta` from low-level `ext_dev`.
- [x] Each migrated executable consumer passes its focused validation or is
  escalated rather than silently retired.

**Verification:**

- [x] Run focused consumer/tutorial compile checks.
- [x] Re-run modern partition/runtime and MLPerf gates.

**Dependencies:** Checkpoint D

**Files likely touched:**

- `vta/README.md`
- `vta/apps/deploy/resnet_export.py`
- `vta/tutorials/frontend/deploy_detection.py`
- `vta/tests/python/unittest/test_byoc_contract.py`
- `vta/tests/python/unittest/test_byoc_graphpack_retirement.py`

**Estimated scope:** Medium (5 files)

## Task 14: Remove the classic callback and enforce zero active references

**Description:** After all consumers pass, delete the old callback backend and
exports/tests, and update the existing aggregate gate with a narrow permanent
legacy-reference scan while preserving low-level APIs.

**Acceptance criteria:**

- [x] `register_byoc`, `relay.ext.vta`, `EXTERNAL_COMPILER`, and production
  callback code are absent.
- [x] Active GraphPack/range references are absent and permanently checked.
- [x] Representative low-level `vta.build*`, TE/TIR, FSIM, and `ext_dev` tests
  remain green.

**Verification:**

- [x] Run the zero-reference scan with only approved narrow exclusions.
- [x] Run modern suites and preserved low-level regression tests.
- [x] Confirm runtime-only import behavior.

**Dependencies:** Task 13

**Files likely touched:**

- `vta/python/vta/__init__.py`
- `vta/python/vta/relay/__init__.py`
- `vta/python/vta/relay/contract.py`
- `vta/python/vta/relay/backend.py` (removed)
- `scripts/test_vta_byoc.sh`

Obsolete callback-only test removal is an additional approved contraction after
replacement evidence passes.

**Estimated scope:** Medium (5 primary files plus obsolete tests removed)

## Task 15: Run final verification and assemble review evidence

**Description:** Execute the complete approved matrix, capture concise evidence,
inspect repository scope, and prepare the implementation for independent review
without committing, pushing, or releasing.

**Acceptance criteria:**

- [x] Every module success criterion traces to passing evidence.
- [x] Aggregate FSIM-only gate, MLPerf app, low-level regressions, and repository
  checks pass.
- [x] No unapproved dependency, target, model, generated artifact, or TVM source
  change is present.

**Verification:**

- [x] Run `./scripts/test_vta_byoc.sh`.
- [x] Run the documented MLPerf application command.
- [x] Run `python -m compileall`, `git diff --check`, and inspect both root and
  nested VTA/TVM status.

**Dependencies:** Task 14

**Files likely touched:**

- `docs/initiatives/vta-modern-target-pipeline/TASKS.md`
- `docs/initiatives/vta-modern-target-pipeline/VERIFICATION.md`

**Estimated scope:** Small (2 files)

## Checkpoint E: Ready for independent review

- [x] Tasks 1-15 are complete with recorded verification.
- [x] All approved specs remain satisfied without amendment.
- [x] Implementation is ready for reviewer verdict.
- [x] No Ship action has been performed or implied.

## Approval Gate

The user must approve this task list with `PLAN.md` before Task 1 begins.
