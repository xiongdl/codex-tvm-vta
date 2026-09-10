# Spec: VTA Modern Cutover

Module id: `vta-modern-cutover`

Status: Approved by the user on 2026-09-09

## Objective

Complete a compulsory repository-owned migration from the classic Relay VTA
external compiler and GraphPack-era entry points to the approved
`libtvm-vta-ext` target-hook pipeline. The cutover migrates every active Relay
consumer, verifies the modern replacement end to end, and then removes the old
callback implementation, public exports, tests, and documentation.

The cutover is intentionally limited to Relay model compilation. Existing
low-level VTA TE/TIR construction, schedules, intrinsics, hardware tests, and
legacy `ext_dev -device=vta` target helpers continue to serve standalone kernel
and hardware-development workflows.

## Migration Contract

### Replacement path

Every repository-owned Relay VTA consumer uses this structure:

```python
import tvm
import vta

quantized = quantize_with_the_application_policy(mod, params)
partitioned = vta.relay.partition_for_vta(quantized, mod_name="consumer_name")
factory = relay.build(
    partitioned,
    target=[tvm.target.Target("vta"), tvm.target.Target("llvm")],
)
```

`import vta` loads and validates `libtvm-vta-ext`; no consumer calls an explicit
compiler-registration function. Applications remain responsible for their one
explicit, capability-based `partition_for_vta()` invocation.

Consumer-specific model import, quantization, executor, runtime, and deployment
details remain owned by each consumer. The migration must not copy the MLPerf
application's fixed qconfig into unrelated models without validating that it is
their existing policy.

### Removed Relay interfaces

After the approved modern target pipeline and MLPerf HOST deployment pass, the
following are removed rather than retained as warning-only adapters:

- public `vta.register_byoc()`;
- the `relay.ext.vta` global compiler callback and all registration code;
- the `EXTERNAL_COMPILER` public/internal constant;
- the classic per-Relay-function codegen backend used only by that callback;
- tests whose only purpose is to register, invoke, or defend ownership of
  `relay.ext.vta`;
- active documentation and examples that tell callers to use the old entry;
- active GraphPack functions, imports, annotations, operator-range controls,
  and instructions, if any remain at cutover time.

Importing `vta` after cutover must not register `relay.ext.vta`. A lookup with
`tvm.get_global_func("relay.ext.vta", allow_missing=True)` must return `None`.
Calling removed Python attributes fails normally with `AttributeError`; no shim
silently delegates to the new flow.

### Repository-owned consumers

The migration inventory includes, at minimum:

- top-level VTA README and compiler documentation;
- `vta/apps/deploy/resnet_export.py`;
- `vta/tutorials/frontend/deploy_detection.py`;
- VTA Relay partition/lowering/codegen/runtime unit tests;
- the aggregate `scripts/test_vta_byoc.sh` validation gate;
- any additional active occurrence discovered by the final repository search.

Each executable consumer is migrated and verified individually before its old
entry point is deleted. If a consumer's model is outside the approved modern
operator capability, it must preserve a correct LLVM fallback or be explicitly
retired with documentation; it must not regain GraphPack, operator ranges, or
the legacy callback.

### Preserved low-level interfaces

The following are not deprecated by this initiative:

- `vta.build_config()`;
- `vta.build()` and `vta.lower()`;
- VTA TE/TOPI compute and schedule registrations;
- tensor intrinsics and VTA TIR transformation passes;
- low-level GEMM, ALU, DMA, FSIM, TSIM, and hardware tests;
- `Environment.target` and the pinned TVM `tvm.target.vta()` helper, which
  currently describe `ext_dev -device=vta` for low-level workflows;
- existing tuning scripts, although AutoTVM is never run by this initiative.

Modern Relay documentation must distinguish `Target("vta")` from the preserved
low-level `tvm.target.vta()`/`ext_dev` target. The latter must not be presented
as the modern Relay compiler target.

## Migration Sequence And Gate

Cutover occurs only after all preceding module specs have been implemented and
verified:

1. Build and validate `libtvm-vta-ext` automatic import and target registration.
2. Pass Relay partition and RelayToTIR capability tests.
3. Pass TIRToRuntime, fingerprint, artifact export/reload, and HOST FSIM tests.
4. Pass the complete MLPerf ResNet HOST deployment against pure LLVM.
5. Inventory all remaining old-path consumers and classify low-level exceptions.
6. Migrate active Relay consumers one at a time and run their focused checks.
7. Run a repository-wide zero-reference gate for GraphPack and the legacy
   compiler entry, excluding only tests that assert absence and historical
   third-party/vendor content outside initiative ownership.
8. Remove callback implementation, exports, obsolete tests, and migration-only
   compatibility code in a separate final contraction step.
9. Run the full FSIM-focused aggregate gate and repository checks.

No compatibility period or dual compiler selection flag is required. Git
history and the separate final removal change provide the recovery path if the
modern replacement later fails review.

## Tech Stack

- Repository-pinned TVM and VTA Python/C++ APIs.
- Existing repository shell automation and pytest suites.
- `rg`-based source inventory with explicit exclusions for generated, vendored,
  local MLPerf source, and absence-test content.
- No feature-flag framework, telemetry service, new deprecation dependency, or
  external migration tool.

## Commands

The focused modern replacement is built through existing automation:

```bash
./scripts/build_vta_lib.sh --target libtvm-vta-ext
./scripts/build_vta_lib.sh --target libvta_fsim
```

The cutover's final validation entry remains the existing script, updated to
the approved FSIM-only modern scope:

```bash
./scripts/test_vta_byoc.sh
```

The zero-reference check must cover active VTA Python, apps, tutorials, tests,
documentation, and repository automation. Its exact command and narrow
exclusion list are fixed during planning and documented in the aggregate gate;
it must detect at least:

```text
graph_pack
get_subgraph
start_name / stop_name
bitpack_start / bitpack_end
register_byoc
relay.ext.vta
EXTERNAL_COMPILER
```

## Project Structure

```text
vta/python/vta/
    Modern automatic extension import and preserved low-level VTA APIs.

vta/python/vta/relay/
    partition_for_vta and modern RelayToTIR support; no legacy callback backend.

vta/apps/ and vta/tutorials/
    Migrated active Relay consumers and the approved MLPerf HOST example.

vta/tests/python/
    Modern target-hook, partition, lowering, runtime, and preserved low-level
    regression tests.

scripts/test_vta_byoc.sh
    Aggregate modern FSIM validation and zero-reference gate.

vta/README.md and initiative docs
    Modern usage, migration mapping, and low-level target distinction.
```

## Code And Documentation Style

Modern Relay examples use one consistent vocabulary and call sequence:

```python
partitioned = vta.relay.partition_for_vta(quantized)
factory = relay.build(partitioned, target=["vta", "llvm"])
```

Documentation says “target extension”, “capability-based partition”,
“RelayToTIR”, and “TIRToRuntime”. It does not label the new path as the old BYOC
callback or imply that listing a target automatically partitions unannotated
Relay.

Migration changes preserve existing consumer behavior outside the compiler
entry being replaced. Do not combine unrelated formatting or low-level API
refactors with cutover edits.

## Testing Strategy

### Consumer migration tests

- Each migrated application/tutorial imports `vta`, explicitly partitions, and
  uses `Target("vta")` with its host target.
- No migrated consumer calls `register_byoc`, looks up `relay.ext.vta`, or uses
  GraphPack/range annotations.
- Consumers with unsupported regions prove LLVM fallback rather than failing
  inside VTA lowering.
- Documentation snippets are syntax checked or exercised where repository
  conventions permit.

### Removal tests

- `vta.register_byoc` and `vta.relay.EXTERNAL_COMPILER` are absent.
- `tvm.get_global_func("relay.ext.vta", allow_missing=True)` remains `None` after
  `import vta` and after a modern build.
- No production callback backend is importable.
- Repository-wide source scanning reports no active legacy reference.
- Absence tests are narrowly excluded from their own literal-string scan.

### Preserved-interface regression tests

- Representative `vta.build_config`, `vta.build`, and `vta.lower` low-level
  tests continue to pass.
- Existing FSIM instruction and TOPI/TE tests retain their `ext_dev` workflow.
- `tvm.target.vta()` and `Environment.target` remain usable for preserved
  low-level callers.
- Runtime-only/RPC imports remain free of compiler-extension dependencies.

### Final gate

- Automatic extension loading and TargetKind contract pass.
- RelayToTIR and TIRToRuntime focused suites pass.
- Export/reload and configuration-fingerprint tests pass.
- MLPerf ten-image HOST FSIM deployment passes against pure LLVM.
- Python compile checks, `git diff --check`, and a clean pinned TVM checkout pass.

## Boundaries

### Always

- Prove the modern replacement before removing the old callback.
- Inventory and migrate every repository-owned active Relay consumer.
- Delete old implementation, tests, exports, and instructions after zero active
  usage is established.
- Preserve low-level VTA workflows and document their separate target identity.
- Keep the final legacy-reference gate in repository automation.

### Ask first

- Remove or change a preserved low-level VTA API or `ext_dev` workflow.
- Retain a compatibility shim, dual compiler path, or feature flag.
- Retire an active consumer rather than migrate it.
- Exclude additional repository paths or reference forms from the zero-reference
  gate.
- Modify any pinned TVM source or its `tvm.target.vta()` helper.

### Never

- Remove the old compiler before the modern MLPerf and runtime gates pass.
- Restore GraphPack or operator-range annotations to migrate a difficult model.
- Route modern Relay through `relay.ext.vta` behind a new wrapper.
- Describe `tvm.target.vta()` as equivalent to the modern `Target("vta")` while
  it still constructs the low-level `ext_dev` target.
- Delete tests merely because they expose a modern implementation regression.

## Success Criteria

1. Every repository-owned active Relay VTA consumer uses automatic
   `libtvm-vta-ext` import, explicit capability partitioning, and the modern
   `Target("vta")` hooks.
2. The modern replacement, including the MLPerf HOST deployment, passes before
   removal begins.
3. `register_byoc`, `relay.ext.vta`, `EXTERNAL_COMPILER`, the callback backend,
   active GraphPack/range usage, and their obsolete documentation/tests are
   absent after cutover.
4. A permanent aggregate source gate prevents those active legacy paths from
   returning.
5. Representative low-level TE/TIR, TOPI, instruction, FSIM, and runtime-only
   workflows remain green with their preserved `ext_dev` target semantics.
6. The final FSIM-focused aggregate validation and repository checks pass with
   no modification to the pinned TVM checkout.

## Dependencies And Deferred Work

- Depends on successful implementation and verification of
  `vta-target-extension`, `vta-relay-to-tir`, `vta-tir-to-runtime`, and
  `mlperf-resnet-host-deployment`.
- General TVMC/CLI discovery, automatic partitioning from target listing alone,
  AutoTVM execution, TVM `c` target, AOT/CRT, FVP, CMSIS-NN, multi-convolution
  fusion, and physical hardware are out of scope.
- Unifying preserved low-level `ext_dev` callers with the modern `vta`
  TargetKind requires a separately approved migration.

## Open Questions

None.

## Approval Gate

The user must approve this spec before planning begins. Approval does not
authorize implementation.
