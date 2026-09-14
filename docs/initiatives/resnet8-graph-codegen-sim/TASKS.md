# Tasks: ResNet8 Graph LLVM/C FSIM And TSIM

Status: Proposed

All tasks are governed by the approved capability map, four module specs, and
`PLAN.md` in this directory. A checkbox is marked complete only when its
acceptance criteria and verification evidence both pass. Generated bundles,
native build output, and Verilator traces are never staged.

## Task 0: Establish the implementation baseline

**Owner:** Root for lifecycle commit and dispatch; Default for build preflight.

**Description:** Create scoped parent/VTA feature branches, commit exactly the
approved lifecycle artifacts, record nested-repository starting OIDs/statuses,
and make the documented TVM/VTA native build prerequisites available before
source implementation begins.

**Acceptance criteria:**

- [ ] Parent, VTA, and pinned TVM OIDs, branches, and statuses are recorded;
  unrelated user changes are absent or explicitly preserved.
- [ ] The approved capability map, four specs, plan, and tasks are committed in
  one parent lifecycle commit and its OID is passed to implementation.
- [ ] Required TVM/VTA libraries build or are confirmed current; the pinned TVM
  checkout remains clean.

**Verification:**

- [ ] Run `git status --short`, `git -C vta status --short`, and
  `git -C tvm status --short` before dispatch.
- [ ] Run the documented TVM build script if `tvm/build` is absent, then
  `bash scripts/build_vta_lib.sh --target all`.
- [ ] Confirm no ignored build artifact is staged.

**Dependencies:** Approved `PLAN.md` and this approved task list.

**Files likely touched:**

- `docs/initiatives/resnet8-graph-codegen-sim/CAPABILITY_MAP.md`
- `docs/initiatives/resnet8-graph-codegen-sim/SPEC-*.md`
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

## Task 4: Propagate the active LLVM/C host through RelayToTIR

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

**Dependencies:** Checkpoint A.

**Files likely touched:**

- `vta/src/compiler/target.cc`
- `vta/tests/python/unittest/test_byoc_codegen.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Medium (3 files)

## Task 5: Generate and reload native C VTA host modules

**Owner:** Default.

**Description:** Extend native `TIRToRuntime` validation and dispatch to support
consistent LLVM/C module and function hosts, then prove actual C source,
standard DSO export/reload, symbol completeness, and fingerprint ordering.

**Acceptance criteria:**

- [ ] Valid LLVM/C modules invoke only the selected builder once and return the
  matching standard TVM module type with every public symbol.
- [ ] Raw/packed host mismatch, missing host, unsupported host, and malformed
  partial modules fail before either builder is called.
- [ ] Exported C DSO reloads and exposes all symbols while retaining
  `VTACheckConfig` before VTA activity.

**Verification:**

- [ ] Rebuild all VTA native libraries and run `test_byoc_codegen.py`.
- [ ] Compile/reload the focused C artifact without importing a simulator.
- [ ] Rerun every existing LLVM TIRToRuntime and configuration-fingerprint test.

**Dependencies:** Task 4.

**Files likely touched:**

- `vta/src/compiler/tir_to_runtime.cc`
- `vta/tests/python/unittest/test_byoc_codegen.py`

**Estimated scope:** Small (2 files)

## Task 6: Prove partitioned Graph build with C host

**Owner:** Default.

**Description:** Add a one-region QNN Graph Executor integration proof that the
modern partitioned Relay path produces C-host VTA source, exports/reloads a DSO,
and exposes its symbol without simulator initialization.

**Acceptance criteria:**

- [ ] `relay.build(partitioned, Target("vta", host="c"))` succeeds through the
  modern target hooks.
- [ ] Generated/imported module sources are C-family and contain the expected
  VTA entry point rather than LLVM IR.
- [ ] Standard export/reload succeeds without FSIM/TSIM import or execution.

**Verification:**

- [ ] Run the isolated C Graph test in `test_byoc_codegen.py`.
- [ ] Run the complete VTA codegen and lowering suites.
- [ ] Confirm `git -C tvm status --short` is empty.

**Dependencies:** Task 5.

**Files likely touched:**

- `vta/tests/python/unittest/test_byoc_codegen.py`
- `vta/src/compiler/target.cc` only if a test exposes an approved propagation defect
- `vta/src/compiler/tir_to_runtime.cc` only if a test exposes an approved validation defect

**Estimated scope:** Small (normally 1 test file)

## Checkpoint B: C host codegen

- [ ] Tasks 4-6 meet all acceptance criteria.
- [ ] The Default agent commits the focused VTA C-host slice.
- [ ] LLVM and C native codegen/export/reload suites pass.
- [ ] No simulator was needed for code-generation acceptance.

## Task 7: Build the four LLVM/C FSIM bundles

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

**Verification:**

- [ ] Run focused target, build-order, source-format, and bundle-layout tests.
- [ ] Build the real four ResNet-8 factories and reload all four DSOs.
- [ ] Confirm exact eight-symbol manifests for both mixed bundles.

**Dependencies:** Checkpoint B.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_graph_artifacts.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`

**Estimated scope:** Medium (3 files)

## Task 8: Execute the complete LLVM/C FSIM matrix

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

**Dependencies:** Task 7.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`

**Estimated scope:** Medium (4 files)

## Checkpoint C: Complete FSIM matrix

- [ ] Tasks 7-8 meet all acceptance criteria.
- [ ] The Default agent commits the focused VTA FSIM matrix slice.
- [ ] The complete real LLVM/C FSIM command passes all ten samples.
- [ ] Four inspectable FSIM bundles exist only as ignored build output.

## Task 9: Introduce validated simulator selection

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

## Task 10: Execute the complete LLVM/C TSIM matrix

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

**Dependencies:** Task 9.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tsim_deployment.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`

**Estimated scope:** Medium (4 files)

## Task 11: Add TSIM matrix to the aggregate gate

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
- [ ] The VTA gitlink references the verified implementation commits and pinned
  TVM remains unchanged.

**Verification:**

- [ ] Run `bash scripts/test_vta_byoc.sh` to completion.
- [ ] Run `git diff --check`, `git -C vta diff --check`, and all three status
  checks.
- [ ] Inspect parent and VTA staged diffs before their attributable commits.

**Dependencies:** Task 10.

**Files likely touched:**

- `scripts/test_vta_byoc.sh`
- `vta` gitlink in the parent repository

**Estimated scope:** Small (1 script plus intentional gitlink update)

## Checkpoint D: Complete simulator matrices

- [ ] Tasks 9-11 meet all acceptance criteria.
- [ ] The Default agent commits the VTA TSIM slice and parent aggregate/gitlink
  changes separately.
- [ ] Real complete FSIM and TSIM LLVM/C commands both pass.
- [ ] The aggregate repository gate passes with pinned TVM clean.

## Task 12: Record verification evidence

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
- [ ] Final parent/VTA diffs and commits are scoped, generated output is ignored,
  and pinned TVM is clean.

**Verification:**

- [ ] Rerun focused artifact/codegen tests, full application suites, both real
  CLI matrices, and `bash scripts/test_vta_byoc.sh`.
- [ ] Run Python compilation and nested `diff --check`/status commands.
- [ ] Audit the evidence against every unchecked task/checkpoint item.

**Dependencies:** Checkpoint D.

**Files likely touched:**

- `docs/initiatives/resnet8-graph-codegen-sim/VERIFICATION.md`

**Estimated scope:** Small (1 evidence document)

## Task 13: Complete independent review and fixes

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

- [ ] Review exact parent and VTA commit ranges from the recorded baselines.
- [ ] Rerun focused tests for fixes and the full aggregate gate after any
  behavior-affecting fix.
- [ ] Confirm final parent/VTA status is expected and pinned TVM is clean.

**Dependencies:** Task 12.

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

The user must explicitly approve this task list before Task 0 begins. Approval
authorizes implementation, local verification, and scoped local commits under
the approved artifacts. It does not authorize push, merge, release, or any
other external ship action.
