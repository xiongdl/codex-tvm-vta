# Implementation Plan: ResNet8 Graph LLVM/C FSIM And TSIM

Status: Proposed

## Approved Sources Of Truth

- `CAPABILITY_MAP.md`
- `SPEC-graph-artifact-bundle.md`
- `SPEC-vta-c-host-codegen.md`
- `SPEC-resnet8-fsim-matrix.md`
- `SPEC-resnet8-tsim-matrix.md`

This plan implements those approved contracts in dependency order. It preserves
the committed ResNet-8 model, one-time quantization, eight VTA partitions,
Graph Executor, exact output comparison, VTA ABI, and pinned `tvm/` checkout.
AoT and deployment-result analysis remain deferred.

## Architecture Decisions

1. **Application-local Graph bundles.** A focused helper under the ResNet-8
   application persists Graph JSON, serialized params, a standard exported DSO,
   generated LLVM/C source, and a deterministic manifest. Execution reloads
   only final on-disk files.
2. **Standard TVM host codegen only.** LLVM and C both pass through the pinned
   `codegen::Build` and `export_library` paths. No generated-code translator,
   custom runtime module, Makefile, or alternate executor is introduced.
3. **Requested target is authoritative.** The modern VTA Relay target hook uses
   its active `Target::Current()` host, rebinding lowered VTA functions so a C
   request cannot silently retain the environment's LLVM host.
4. **Strict host consistency.** Native `TIRToRuntime` supports exactly LLVM and
   C and rejects missing, unsupported, or mixed function/module hosts before
   either code generator is called.
5. **One deployment engine, two simulator adaptors.** FSIM and TSIM differences
   are represented by validated environment target, registry functions,
   counters, and diagnostics. Model preparation, artifact generation, Graph
   execution, and comparison are shared.
6. **One semantic model per matrix.** A complete LLVM/C matrix imports,
   quantizes, and partitions once, then builds all four reference/mixed
   artifacts from that prepared model.
7. **Lazy simulator initialization.** All factories, source bundles, DSOs, and
   reference outputs complete before importing `vta.testing.simulator`. FSIM
   and TSIM run in separate processes selected by `VTA_CONFIG_FILE`.
8. **Independent accelerator evidence.** Profiler state is reset and verified
   separately for LLVM-mixed and C-mixed. FSIM requires GEMM/weight/output
   counters; TSIM requires its actual supported counter, `cycle_count`.
9. **Nested repository boundaries stay explicit.** Compiler, application, and
   VTA tests are committed in the `vta` submodule. Lifecycle documents and any
   aggregate-script update are committed in the parent repository, followed by
   the intentional VTA gitlink update. The pinned `tvm` submodule stays clean.

## Dependency Graph

```text
Graph bundle contract + tests
          |
          v
atomic export/source/reload helper
          |
          v
VTA active-host propagation
          |
          v
LLVM/C native TIRToRuntime + C DSO proof
          |
          v
ResNet8 LLVM/C FSIM matrix
          |
          v
shared simulator abstraction
          |
          v
ResNet8 LLVM/C TSIM matrix
          |
          v
aggregate verification + independent review
```

## Implementation Phases

### Phase 0: Preflight And Reproducible Baseline

Immediately before implementation dispatch, create scoped `codex/` feature
branches in the parent and VTA repositories, confirm the approved lifecycle
artifact commit, record both starting OIDs, and verify that only the new
initiative documents are pending. Confirm the pinned TVM checkout is clean.

Validate required toolchain paths and rebuild the pinned TVM/VTA libraries with
repository automation if the current build tree is absent or stale. This phase
may change ignored build output but no source behavior.

#### Checkpoint 0

- Parent, VTA, and TVM starting OIDs and statuses are recorded.
- The approved capability map, four specs, plan, and tasks are committed as the
  exact downstream source of truth.
- TVM and VTA native libraries can be built by documented scripts.
- No unrelated user changes are staged, overwritten, or cleaned.

### Phase 1: Graph Artifact Bundle

Begin with focused fake-factory tests for exact graph/param bytes, safe relative
paths, recursive source discovery, deterministic manifests, expected/forbidden
symbols, atomic replacement, rollback, and disk-only reload. Implement the
small application-local helper, then add a real LLVM ResNet factory test that
exports a non-empty `.ll` source tree and reloadable Graph bundle.

Adapt existing deployment value objects only far enough to consume the bundle
result. Preserve lazy simulator loading and existing LLVM deployment behavior
at this checkpoint.

#### Checkpoint A

- Reference and mixed LLVM factories publish complete atomic bundles.
- Graph JSON and params match factory outputs byte-for-byte.
- Reload uses only final disk paths and validates hashes and symbols.
- A failed replacement leaves the previous completed bundle untouched.
- Existing LLVM FSIM deployment remains green.

### Phase 2: VTA C Host Codegen

Add failing native-hook tests that expose the current LLVM-only assumptions.
Update `ModernRelayToTIR` to take the host from the active VTA target and update
`TIRToRuntime` to validate and build LLVM or C consistently. Keep the existing
flattening, packed API, VTA runtime-call validation, fingerprint injection, and
single `codegen::Build` transaction.

Prove C support first on a one-region partitioned QNN graph: generated C source
contains every symbol and fingerprint check, standard export compiles a DSO,
and reload exposes the symbol without importing a simulator. Rerun the complete
LLVM codegen suite to guard against regression.

#### Checkpoint B

- Requested LLVM/C host reaches every routed VTA PrimFunc unchanged in kind.
- Missing, unsupported, and inconsistent hosts fail before codegen.
- Native C output is non-empty, standard, exportable, and reloadable.
- VTA runtime calls, public symbols, and fingerprint ordering are preserved.
- The pinned TVM checkout remains clean.

### Phase 3: Complete ResNet8 FSIM Matrix

Generalize target construction and artifact paths by validated host codegen.
Implement single-host deployment compatibility plus the one-prepare LLVM/C
matrix entry point. Update the CLI with
`--host-codegen {llvm,c,all}`, retaining LLVM as the default.

Run all reference graphs before lazy FSIM import. Require exact cross-host
reference equality, then execute LLVM-mixed and C-mixed sequentially with
separate zeroed profiler windows. Persist four FSIM bundles and document their
contents and complete run command.

#### Checkpoint C

- `--host-codegen all` builds four disk-reloadable Graph bundles.
- LLVM/C source formats match their manifest labels.
- Both mixed artifacts expose the exact eight VTA symbols.
- All ten samples execute through both mixed artifacts and agree exactly with
  the common quantized reference.
- Each mixed run independently records positive FSIM GEMM/load/store activity.

### Phase 4: Complete ResNet8 TSIM Matrix

Refactor simulator-specific selection into a small validated adaptor while
preserving the FSIM path. Add `--simulator {fsim,tsim}` with FSIM as the default
and run TSIM only in a fresh process configured with `tsim_sample.json`.

Use the standard lazy simulator import to load `libvta_tsim`, load and retain
`libvta_hw`, and initialize the Verilated hardware module. Validate TSIM through
its actual registry functions rather than `simulator.enabled()`. Build four
TSIM-labeled bundles and execute the same LLVM/C ten-sample matrix sequentially,
with an independent zero-to-positive `cycle_count` window per mixed variant.

Extend the parent aggregate gate so the real ResNet-8 TSIM matrix runs after the
existing standalone TSIM validation in a separate Python process.

#### Checkpoint D

- The full TSIM CLI command initializes the standard Verilated hardware module
  and completes both host variants.
- Four TSIM bundles contain correct Graph, params, DSO, source, manifest, and
  symbol contracts.
- All twenty mixed sample executions match the common reference exactly.
- LLVM-mixed and C-mixed each start at zero and finish with positive cycles.
- The complete FSIM matrix remains green in its separate configured process.

### Phase 5: Full Verification And Review Handoff

Run verification from narrow to broad: artifact tests, VTA codegen/lowering
tests, native rebuild, FSIM application matrix, standalone TSIM gate, TSIM
application matrix, and the aggregate repository gate. Run syntax compilation,
diff checks, source scans, and nested-repository cleanliness checks.

Record actual commands, exit status, artifact layout, source formats, partition
symbols, sample counts, and simulator counters as review evidence. Generated
bundles and Verilator traces remain ignored and unstaged. Dispatch an
independent Reviewer only after all implementation checkpoints pass; address
findings through the Default implementation role and reverify before completion.

#### Checkpoint E

- Every approved success criterion has command-backed evidence.
- `bash scripts/test_vta_byoc.sh` passes including the ResNet-8 TSIM matrix.
- The pinned TVM checkout is unchanged and clean.
- Parent/VTA diffs contain only approved source, test, docs, script, and gitlink
  changes; generated build output is untracked/ignored.
- Independent review has no unresolved blocking findings.
- No push, merge, release, or other ship action is implied.

## Verification Strategy

Implementation uses tests-first vertical slices and stops at each checkpoint
before broadening scope. Required verification layers are:

1. Artifact helper unit tests using fake factories/modules and failure injection.
2. Real LLVM/C source, export, reload, and target-hook tests.
3. VTA native library rebuild and existing codegen/lowering regressions.
4. ResNet-8 structural model and exact eight-partition tests.
5. Complete ten-sample LLVM/C FSIM Graph Executor execution.
6. Standalone TSIM initialization/instruction validation.
7. Complete ten-sample LLVM/C TSIM Graph Executor execution.
8. Parent aggregate gate, Python `compileall`, `git diff --check`, and clean
   pinned TVM status.

FSIM and TSIM evidence is collected from separate processes with their approved
configuration files. A source-only test, successful build, DSO reload, simulator
smoke test, or one-layer VTA test never substitutes for full model execution.

## Version-Control And Handoff Strategy

- Commit approved lifecycle artifacts in the parent immediately before the first
  implementation dispatch and pass the exact paths and commit OID downstream.
- Use small VTA commits aligned with artifact bundle, C host codegen, FSIM, and
  TSIM checkpoints. Do not mix generated output into commits.
- Update the parent VTA gitlink only to reviewed VTA commits; keep any parent
  aggregate-script change in an attributable parent commit.
- Default agents own Build/Fix/Verify and commits. Root owns lifecycle gates,
  acceptance audit, reviewer dispatch, and completion. Reviewer agents do not
  modify code.
- Do not push or merge without separate explicit user authorization.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| C Graph Executor host codegen exposes a pinned-TVM limitation only at full-model build | High | Prove native one-region C export/reload in Phase 2, then build the C reference and mixed ResNet bundles before touching simulator logic; escalate rather than falling back to LLVM |
| C DSO resolution of VTA extern symbols differs by platform linker | High | Use only TVM's standard `export_library`, test actual DSO reload on the current platform, keep simulator loading lazy, and avoid custom flags unless returned through the spec gate |
| LLVM and C pure-host floating operators differ bitwise | High | Test cross-host references before accelerator execution; inspect generated operations if they differ and fix semantics without loosening the approved exact-equality rule |
| Atomic directory replacement is not rollback-safe across platforms | Medium | Use a sibling staging directory, validate before publication, test failure injection against an existing completed bundle, and constrain all operations below the resolved output root |
| FSIM and TSIM singleton environments contaminate one another | High | Run each simulator in a fresh process, validate label-to-environment mapping before build, and never mutate `VTA_CONFIG_FILE` at runtime |
| TSIM profiler is mistaken for FSIM or queried through `simulator.enabled()` | Medium | Select exact registry names by simulator and validate only the actual TSIM `cycle_count` contract |
| Full ResNet-8 TSIM execution is long-running or reaches driver timeout | High | Run standalone TSIM and one-host vertical slices before the full matrix, retain sequential execution and existing driver timeout semantics, and report a real timeout rather than substituting smoke evidence |
| Existing native builds are absent or stale | Medium | Use the documented TVM/VTA build scripts during preflight, record toolchain failures, and do not patch source to mask an environment prerequisite |
| Nested VTA/parent commits accidentally include unrelated state | Medium | Record starting OIDs, stage explicit paths only, inspect both diffs/statuses at every checkpoint, and keep the pinned TVM checkout read-only |

## Parallelization

The implementation path is intentionally sequential. Artifact integration,
target propagation, application runtime, CLI, and simulator work share the same
VTA compiler/application boundaries, and TSIM depends on the proven FSIM path.
Independent review begins only after full verification. No concurrent code
owners are planned for these phases.

## Open Questions

None. If implementation requires changing the artifact schema, adding custom
link flags, weakening exact equality, altering model/partitioning, changing the
TSIM driver or timeout, or modifying pinned TVM source, work returns to the
relevant specification approval gate.

## Approval Gate

The user must approve this implementation plan before the detailed `TASKS.md`
artifact is written. Plan approval does not authorize implementation, commit of
implementation code, push, merge, or release.
