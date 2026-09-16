# Tasks: ResNet8 Graph LLVM/C FSIM And TSIM

Status: Proposed

All tasks are governed by the approved capability map, four module specs, and
`PLAN.md` in this directory. A checkbox is marked complete only when its
acceptance criteria and verification evidence both pass. Generated bundles,
native build output, and Verilator traces are never staged.

## Task 0: Establish the implementation baseline

**Owner:** Root for lifecycle commit and dispatch; Default for build preflight.

**Description:** Retain the scoped parent/VTA feature branches, create the same
scoped feature branch in TVM, commit exactly the newly approved lifecycle
amendments, record all nested-repository starting OIDs/statuses, and make the
documented TVM/VTA native build prerequisites available before implementation
resumes.

**Acceptance criteria:**

- [ ] Parent, VTA, and pinned TVM OIDs, branches, and statuses are recorded;
  unrelated user changes are absent or explicitly preserved.
- [ ] The approved capability-map, C-host SPEC, PLAN, and TASKS amendments are
  committed in one parent lifecycle commit and its OID is passed downstream
  together with the original lifecycle commit.
- [ ] Required TVM/VTA libraries build or are confirmed current; TVM is clean on
  its scoped task branch before source changes begin.

**Verification:**

- [ ] Run `git status --short`, `git -C vta status --short`, and
  `git -C tvm status --short` before dispatch.
- [ ] Run the documented TVM build script if `tvm/build` is absent, then
  `bash scripts/build_vta_lib.sh --target all`.
- [ ] Confirm no ignored build artifact is staged.

**Dependencies:** Approved `PLAN.md` and this approved task list.

**Files likely touched:**

- `docs/initiatives/resnet8-graph-codegen-sim/CAPABILITY_MAP.md`
- `docs/initiatives/resnet8-graph-codegen-sim/SPEC-vta-c-host-codegen.md`
- `docs/initiatives/resnet8-graph-codegen-sim/PLAN.md`
- `docs/initiatives/resnet8-graph-codegen-sim/TASKS.md`

**Estimated scope:** Small (version-control/lifecycle operation; no behavior
change)

## Task 1: Export exact Graph bundle contents

**Owner:** Default.

**Description:** Add the application-local bundle API and focused tests for
safe output resolution, exact Graph JSON and serialized params, standard DSO
export/reload, hashes, and schema-versioned manifest generation.

**Acceptance criteria:**

- [ ] Valid fake factories produce `graph.json`, `params.bin`, `model.<suffix>`,
  and a stable schema-1 manifest below the selected output root.
- [ ] Absolute, empty, parent-traversal, and symlink-escape artifact paths fail
  before output mutation.
- [ ] The returned immutable result is populated from final on-disk files and
  its hashes validate.

**Verification:**

- [ ] New focused tests fail before implementation and pass afterward.
- [ ] Run the focused `test_graph_artifacts.py` suite.
- [ ] Run `git -C vta diff --check`.

**Dependencies:** Task 0.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_graph_artifacts.py`

**Estimated scope:** Small (2 files)

## Task 2: Add source discovery and transactional publication

**Owner:** Default.

**Description:** Extend the bundle slice with deterministic recursive source
discovery, expected/forbidden symbol validation, sibling staging, atomic
publication, replacement rollback, and cleanup under injected failures.

**Acceptance criteria:**

- [ ] LLVM/C-family source modules are written once in stable pre-order and
  modules without source are recorded without hiding required empty-source
  errors.
- [ ] Expected and forbidden symbol contracts are checked after final DSO reload.
- [ ] Failed validation/publication preserves an existing completed bundle and
  leaves no staging directory.

**Verification:**

- [ ] Run failure-injection, source-order, symbol, and rollback tests in
  `test_graph_artifacts.py`.
- [ ] Repeat an equivalent fake export and compare graph, params, and source
  bytes plus deterministic manifest fields.
- [ ] Run `git -C vta diff --check`.

**Dependencies:** Task 1.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_graph_artifacts.py`

**Estimated scope:** Small (2 files)

## Task 3: Consume LLVM bundles in the existing deployment

**Owner:** Default.

**Description:** Replace the two flat in-memory-backed deployment artifacts
with reference/mixed LLVM bundles while preserving the current single-host
FSIM behavior and proving real LLVM IR plus disk-only Graph Executor reload.

**Acceptance criteria:**

- [ ] Existing `deploy(output_dir)` still selects LLVM and runs the same ten
  samples with exact reference/mixed equality.
- [ ] Reference and mixed bundles contain non-empty `.ll` source and correct
  VTA forbidden/expected symbol evidence.
- [ ] Build/export/reload completes without importing FSIM.

**Verification:**

- [ ] Run `test_graph_artifacts.py` and `test_host_deployment.py` under the FSIM
  configuration.
- [ ] Run the real existing LLVM deployment and inspect both bundle directories.
- [ ] Require positive existing FSIM counters and a clean pinned TVM checkout.

**Dependencies:** Task 2.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`

**Estimated scope:** Medium (3 files)

## Checkpoint A: Graph artifact bundle

- [ ] Tasks 1-3 meet all acceptance criteria.
- [ ] The Default agent commits the focused VTA artifact-bundle slice.
- [ ] Existing LLVM FSIM deployment passes from reloaded bundle files.
- [ ] No generated output is tracked and pinned TVM remains clean.

## Task 4: Correct TVM C Graph source contracts

**Owner:** Default.

**Description:** Add focused regressions and minimally update the pinned TVM C
host backend so Graph-runtime C modules export a usable module-context slot and
calls represented by `TGlobalSymbol` receive valid forward declarations.

**Acceptance criteria:**

- [ ] Non-AoT Graph C modules emit a `TVM_WEAK` module-context definition;
  existing AoT C output retains its strong definition.
- [ ] Multiple C source modules link into one DSO without duplicate context
  symbols, and TVM's loader populates the context on reload.
- [ ] `TGlobalSymbol` calls are declared before use; no TVM runtime, LLVM,
  executor, target-hook driver, or unrelated backend file changes.

**Verification:**

- [ ] New focused tests fail on the pinned base and pass after implementation.
- [ ] Rebuild TVM with `bash scripts/build_tvm_lib_macos.sh`.
- [ ] Run `tvm/tests/python/codegen/test_target_codegen_c_host.py`, including
  actual multi-module export and reload.

**Dependencies:** Checkpoint A.

**Files likely touched:**

- `tvm/src/target/source/codegen_c_host.cc`
- `tvm/src/target/source/codegen_c_host.h`
- `tvm/tests/python/codegen/test_target_codegen_c_host.py`

**Estimated scope:** Medium (3 files)

## Task 5: Propagate the active LLVM/C host through RelayToTIR

**Owner:** Default.

**Description:** Add target-hook tests and update modern VTA Relay lowering so
the active `Target("vta", host=...)` host is validated and rebound onto every
routed VTA PrimFunc, overriding the environment-carried LLVM host when C is
requested.

**Acceptance criteria:**

- [ ] Active LLVM and C hosts reach every routed PrimFunc with symbols, bodies,
  metadata, and calling convention preserved.
- [ ] Missing/unsupported active hosts fail with supported-kind diagnostics.
- [ ] Non-VTA PrimFuncs remain unchanged and a C request never yields an LLVM
  routed target.

**Verification:**

- [ ] Run focused target-hook/codegen tests for zero, one, and multiple VTA
  regions under both hosts.
- [ ] Run the existing `test_byoc_lowering.py` regression suite.
- [ ] Rebuild `libtvm-vta-ext` before exercising the native change.

**Dependencies:** Task 4.

**Files likely touched:**

- `vta/src/compiler/target.cc`
- `vta/tests/python/unittest/test_byoc_codegen.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Medium (3 files)

## Task 6: Generate ABI-correct scalar C VTA modules

**Owner:** Default.

**Description:** Extend native `TIRToRuntime` for consistent LLVM/C hosts,
correct the existing VTA PassContext configuration merge, scalarize C builds
through `tir.disable_vectorize`, and normalize VTA address operands to the
existing opaque-handle ABI before source generation.

**Acceptance criteria:**

- [ ] Valid LLVM/C modules invoke only the selected builder once and return the
  matching standard TVM module type with every public symbol.
- [ ] Raw/packed host mismatch, missing host, unsupported host, and malformed
  partial modules fail before either builder is called.
- [ ] C source contains no unsupported fixed-length vector aliases or
  incompatible typed-pointer VTA declarations; LLVM vectorization is unchanged.
- [ ] `vta.build_config(config=...)` merges the standard PassContext options
  without changing its default behavior.

**Verification:**

- [ ] Rebuild all VTA native libraries and run `test_byoc_codegen.py`.
- [ ] Compile/reload focused C modules without importing a simulator.
- [ ] Rerun every existing LLVM TIRToRuntime, build-config, lowering, and
  configuration-fingerprint test.

**Dependencies:** Task 5.

**Files likely touched:**

- `vta/python/vta/build_module.py`
- `vta/python/vta/transform.py`
- `vta/src/compiler/tir_to_runtime.cc`
- `vta/tests/python/unittest/test_byoc_codegen.py`

**Estimated scope:** Medium (4 files)

## Task 7: Prove partitioned Graph build with C host

**Owner:** Default.

**Description:** Add a one-region QNN Graph Executor integration proof that the
modern partitioned Relay path produces scalar, ABI-correct C-host source,
exports/reloads a DSO, and exposes its symbol without simulator initialization.

**Acceptance criteria:**

- [ ] `relay.build(partitioned, Target("vta", host="c"))` succeeds through the
  modern target hooks with the approved standard PassContext option.
- [ ] Generated/imported sources are C-family, contain the expected VTA entry
  point and fingerprint guard, and contain neither LLVM IR nor unsupported
  vector aliases.
- [ ] Standard export/reload succeeds without source post-processing, custom
  compiler/linker flags, FSIM/TSIM import, or VTA execution.

**Verification:**

- [ ] Run the isolated C Graph test in `test_byoc_codegen.py`.
- [ ] Run the complete TVM C host and VTA codegen/lowering suites.
- [ ] Audit TVM and VTA changes against their exact approved path allowlists.

**Dependencies:** Task 6.

**Files likely touched:**

- `vta/tests/python/unittest/test_byoc_codegen.py`
- Approved Task 4-6 implementation files only when the integration proof exposes
  a defect within their existing contracts

**Estimated scope:** Small (normally 1 test file)

## Checkpoint B: C host codegen

- [ ] Tasks 4-7 meet all acceptance criteria.
- [ ] The Default agent commits the focused TVM backend slice, then the dependent
  VTA C-host slice, with exact path allowlists and stable candidate fingerprints.
- [ ] LLVM and C native codegen/export/reload suites pass after TVM and VTA
  rebuilds.
- [ ] No simulator was needed for code-generation acceptance.

## Task 7A: Preserve static VTA micro-op initialization in C source

**Owner:** Default.

**Description:** Extend only the pinned TVM C host backend so capture-free
`coproc_uop_scope` bodies become uniquely named static callbacks registered by
the attribute-selected initializer instead of being flattened into the VTA
entry function. Reject captured scopes explicitly and leave LLVM unchanged.

**Acceptance criteria:**

- [ ] Each capture-free scope emits a distinct module-local null handle and
  `int32_t(void*)` callback; the callback contains the scope body and returns
  zero.
- [ ] The entry function calls the requested initializer with the handle,
  callback, null signature, and zero signature bytes, and propagates nonzero
  return before later VTA commands.
- [ ] Multiple scopes using GEMM or ALU initializers are deterministic and
  collision-free; their bodies do not also execute directly in the entry
  function.
- [ ] A scope with undefined captured values fails C code generation with an
  actionable `coproc_uop_scope` diagnostic.
- [ ] Existing Graph weak context, AoT strong context, multi-C linkage,
  `TGlobalSymbol`, and LLVM static-initialization contracts remain unchanged.

**Verification:**

- [ ] Add focused source tests for one and multiple capture-free scopes,
  initializer declarations/calls, unique handles/callbacks, body placement,
  deterministic output, failure propagation, and captured-scope rejection.
- [ ] Rebuild TVM, run the complete `test_target_codegen_c_host.py` suite, and
  rerun `test_target_codegen_static_init.py` for the unchanged LLVM path.
- [ ] Rebuild VTA and rerun the existing VTA codegen/lowering/runtime suites
  before the application candidate resumes.

**Dependencies:** Checkpoint B.

**Files likely touched:**

- `tvm/src/target/source/codegen_c_host.cc`
- `tvm/src/target/source/codegen_c_host.h`
- `tvm/tests/python/codegen/test_target_codegen_c_host.py`

**Estimated scope:** Medium (3 files)

## Checkpoint B2: C static micro-op initialization recovery

- [ ] Task 7A meets all acceptance criteria.
- [ ] The Default agent commits one focused TVM recovery slice with an exact
  three-path allowlist and stable candidate fingerprint.
- [ ] TVM/VTA rebuilds and C/LLVM regression suites pass without modifying the
  VTA runtime ABI or loading a simulator.
- [ ] An independent Reviewer passes the recovery before the pending FSIM
  application candidate is completed and committed.

## Task 8: Build the four LLVM/C FSIM bundles

**Owner:** Default.

**Description:** Generalize application host target construction and artifact
identity so one prepared model builds LLVM/C reference and mixed bundles under
`llvm-fsim` and `c-fsim`, with no host fallback and no repeated quantization.

**Acceptance criteria:**

- [ ] The complete host selection is exactly ordered `("llvm", "c")`, and
  invalid/duplicate/reordered inputs fail before build.
- [ ] Four bundles contain their own graph, params, DSO, manifest, matching
  source format, and reference/mixed symbol contract.
- [ ] A matrix build calls model preparation once and does not load FSIM.
- [ ] Reloaded C mixed source contains both `VTAPushGEMMOp` and
  `VTAPushALUOp` static initializer calls, unique callback/handle evidence, and
  no entry-function flattening of their recording bodies.

**Verification:**

- [ ] Run focused target, build-order, source-format, and bundle-layout tests.
- [ ] Build the real four ResNet-8 factories and reload all four DSOs.
- [ ] Confirm exact eight-symbol manifests for both mixed bundles.
- [ ] Inspect the real C mixed source for the static micro-op initialization
  contract before importing FSIM.

**Dependencies:** Checkpoint B2.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`

**Estimated scope:** Medium (3 files)

## Task 9: Execute the complete LLVM/C FSIM matrix

**Owner:** Default.

**Description:** Implement shared-reference execution, independently profiled
LLVM/C mixed runs, the compatible single-host entry point, the complete matrix
entry point, CLI selection, and user documentation.

**Acceptance criteria:**

- [ ] Both references and both mixed graphs execute all ten committed samples
  and agree exactly in shape, dtype, elements, and top-1.
- [ ] Each mixed host starts from verified zero stats and independently produces
  positive FSIM GEMM, weight-load, and output-store counters.
- [ ] Default CLI remains LLVM; `--host-codegen all` completes the full matrix
  and reports bundle paths and per-host evidence.

**Verification:**

- [ ] Run all application tests under `vta_config.json`.
- [ ] Run the real `run.py --host-codegen all` command and require exit zero.
- [ ] Inspect four FSIM bundles and record ten comparisons plus positive
  counters for each mixed host.
- [ ] Require the first C mixed sample to execute without an uninitialized VTA
  recording kernel before accepting the remaining comparisons.

**Dependencies:** Task 8.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`

**Estimated scope:** Medium (4 files)

## Checkpoint C: Complete FSIM matrix

- [ ] Tasks 8-9 meet all acceptance criteria.
- [ ] The Default agent commits the focused VTA FSIM matrix slice.
- [ ] The complete real LLVM/C FSIM command passes all ten samples.
- [ ] Four inspectable FSIM bundles exist only as ignored build output.

## Task 10: Introduce validated simulator selection

**Owner:** Default.

**Description:** Refactor FSIM-specific loading and counter checks into a small
simulator-aware boundary supporting `fsim` and `tsim`, validating the immutable
VTA environment before model preparation while preserving lazy initialization.

**Acceptance criteria:**

- [ ] Simulator labels map exactly to environment target, registry functions,
  counter schema, and setup command; mismatches fail before build.
- [ ] TSIM checks `vta.tsim.*` and never uses `simulator.enabled()`.
- [ ] Existing FSIM behavior and profiler validation remain unchanged.

**Verification:**

- [ ] Run mock-based FSIM/TSIM mapping, lazy-import, missing-registry, and
  malformed-counter tests.
- [ ] Run the complete FSIM deployment suite after refactoring.
- [ ] Run standalone `scripts/test_vta_tsim.sh --smoke-only` under
  `tsim_sample.json`.

**Dependencies:** Checkpoint C.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tsim_deployment.py`

**Estimated scope:** Medium (3 files)

## Task 11: Execute the complete LLVM/C TSIM matrix

**Owner:** Default.

**Description:** Add TSIM bundles, standard lazy hardware initialization,
sequential LLVM/C mixed execution, independent cycle evidence, CLI simulator
selection, and TSIM user documentation.

**Acceptance criteria:**

- [ ] Four TSIM bundles build/reload before simulator import and contain correct
  TSIM labels, sources, and eight-symbol contracts.
- [ ] LLVM/C mixed Graph Executors each run all ten samples on the initialized
  Verilated hardware model and match the common reference exactly.
- [ ] Each host begins at `cycle_count == 0`, ends with its own positive integer
  count, and no FSIM fallback or synthetic counter is used.

**Verification:**

- [ ] Run focused `test_tsim_deployment.py` under `tsim_sample.json`.
- [ ] Run standalone `scripts/test_vta_tsim.sh`, then the real
  `run.py --simulator tsim --host-codegen all` command.
- [ ] Inspect four TSIM bundles and record twenty comparisons plus two positive
  cycle snapshots.

**Dependencies:** Task 10.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`

**Estimated scope:** Medium (4 files)

## Task 12: Add TSIM matrix to the aggregate gate

**Owner:** Default.

**Description:** Extend the parent validation script so the complete ResNet-8
TSIM matrix executes in a fresh process with `tsim_sample.json` after standalone
TSIM validation, without weakening any existing FSIM, codegen, or repository
checks.

**Acceptance criteria:**

- [ ] Aggregate validation invokes the full TSIM application test/command with
  the exact TSIM configuration and fails on any nonzero result.
- [ ] Existing structural, FSIM, standalone TSIM, compile, source-scan, and
  nested-repository gates retain their prior coverage.
- [ ] The VTA and TVM gitlinks reference their verified implementation commits;
  TVM paths are confined to the approved C host backend and focused tests.

**Verification:**

- [ ] Run `bash scripts/test_vta_byoc.sh` to completion.
- [ ] Run `git diff --check`, `git -C vta diff --check`, and all three status
  checks.
- [ ] Inspect parent, VTA, and TVM staged diffs before their attributable
  commits.

**Dependencies:** Task 11.

**Files likely touched:**

- `scripts/test_vta_byoc.sh`
- `vta` gitlink in the parent repository
- `tvm` gitlink in the parent repository

**Estimated scope:** Small (1 script plus two intentional gitlink updates)

## Checkpoint D: Complete simulator matrices

- [ ] Tasks 10-12 meet all acceptance criteria.
- [ ] The Default agent commits the VTA TSIM slice and parent aggregate/gitlink
  changes separately.
- [ ] Real complete FSIM and TSIM LLVM/C commands both pass.
- [ ] The aggregate repository gate passes with committed TVM/VTA worktrees
  clean and exact approved path scope.

## Task 13: Record verification evidence

**Owner:** Default for verification execution and evidence draft; Root for
acceptance audit.

**Description:** Run the final narrow-to-broad matrix from clean committed
implementation state and record attributable commands, artifact/source
inspection, partition/sample counts, simulator counters, and repository status.

**Acceptance criteria:**

- [ ] Evidence covers every success criterion from all four specs with actual
  command results rather than inferred or smoke-only claims.
- [ ] Generated artifacts demonstrate LLVM/C source, Graph JSON, params, DSOs,
  manifests, exact eight-symbol mixed contracts, and forbidden reference symbols.
- [ ] Final parent/VTA/TVM diffs and commits are scoped, generated output is
  ignored, and all three worktrees are clean.

**Verification:**

- [ ] Rerun focused artifact/codegen tests, full application suites, both real
  CLI matrices, and `bash scripts/test_vta_byoc.sh`.
- [ ] Run Python compilation and nested `diff --check`/status commands.
- [ ] Audit the evidence against every unchecked task/checkpoint item.

**Dependencies:** Checkpoint D.

**Files likely touched:**

- `docs/initiatives/resnet8-graph-codegen-sim/VERIFICATION.md`

**Estimated scope:** Small (1 evidence document)

## Task 14: Complete independent review and fixes

**Owner:** Reviewer for read-only review; Default for any fixes; Root for final
acceptance.

**Description:** Review the committed implementation against the approved
artifacts and verification evidence, fix any blocking findings through the
implementation role, rerun proportionate/full gates, and close only when no
blocking finding remains.

**Acceptance criteria:**

- [ ] Reviewer checks correctness, contract fidelity, failure safety, tests,
  nested-repository scope, and generated-artifact handling.
- [ ] Every blocking finding is fixed in an attributable commit and reverified;
  reviewer confirms closure.
- [ ] Root confirms all tasks/checkpoints complete and reports results without
  pushing, merging, or releasing.

**Verification:**

- [ ] Review exact parent, VTA, and TVM commit ranges from the recorded
  baselines.
- [ ] Rerun focused tests for fixes and the full aggregate gate after any
  behavior-affecting fix.
- [ ] Confirm final parent/VTA/TVM status is expected and TVM changes remain
  inside the approved C host allowlist.

**Dependencies:** Task 13.

**Files likely touched:**

- None for review itself; approved implementation/test files only if Default
  must address findings.

**Estimated scope:** Small review plus finding-dependent fixes

## Final Checkpoint: Ready For User Acceptance

- [ ] All tasks and checkpoints are complete with recorded evidence.
- [ ] Graph+LLVM/C runs fully on FSIM and TSIM for the committed ResNet-8 model.
- [ ] Analysis reporting and AoT remain unimplemented as approved.
- [ ] No unresolved review finding remains.
- [ ] No push, merge, release, or other ship action has occurred.

## Approval Gate

The user must explicitly approve this amended task list before Checkpoint B
implementation resumes. Approval authorizes implementation, local verification,
and scoped local commits under the approved artifacts. It does not authorize
push, merge, release, or any other external ship action.
