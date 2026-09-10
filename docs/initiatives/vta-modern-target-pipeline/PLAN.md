# Implementation Plan: VTA Modern Target Pipeline

Status: Proposed

## Approved Sources Of Truth

- `CAPABILITY_MAP.md`
- `SPEC-vta-target-extension.md`
- `SPEC-vta-relay-to-tir.md`
- `SPEC-vta-tir-to-runtime.md`
- `SPEC-mlperf-resnet-host-deployment.md`
- `SPEC-vta-modern-cutover.md`

This plan implements the approved specs in dependency order. It does not modify
the pinned `tvm/` source tree and does not broaden operator, target, deployment,
or performance scope.

## Architecture Decisions

1. **One separately built compiler library.** CMake builds
   `vta/build/libtvm-vta-ext.{dylib,so}` from VTA-owned native compiler sources.
   TargetKind registration and both modern hooks live in this artifact.
2. **Two target identities remain intentional.** Modern Relay uses native
   `Target("vta")`; preserved low-level TE/TIR code may continue using the
   pinned TVM helper that creates `ext_dev -device=vta`.
3. **Python owns preparation, native hooks own TVM dispatch.** The public
   capability partition API and existing TE/TOPI schedule registrations remain
   in the VTA Python package. `libtvm-vta-ext` owns native TargetKind and
   IRModule-at-a-time target hooks. The first checkpoint proves that the native
   hook can consume the approved Python-prepared IR without restoring
   `relay.ext.vta`.
4. **One composite per VTA function.** Partitioning deliberately prevents
   adjacent VTA composites from becoming a multi-convolution region.
5. **Region-local layouts.** NHWC/HWIO and NCHW/OIHW inputs are packed inside a
   VTA function and unpacked back to its original ABI at the boundary.
6. **Standard host artifact.** TIRToRuntime validates all VTA PrimFuncs, inserts
   configuration checks, and invokes LLVM host codegen directly to return one
   ordinary DSO-exportable TVM module.
7. **Configuration safety is in-band.** Generated VTA entries call
   `VTACheckConfig(expected_fingerprint)` before any VTA activity. Compiler and
   FSIM derive the fingerprint from the same canonical ABI definition set and
   schema version.
8. **One quantized reference graph.** The MLPerf application imports the
   committed float model, quantizes once with `global_scale=8.0` and
   `skip_conv_layers=[0]`, then forks pure LLVM and mixed builds from that exact
   IRModule.
9. **Replacement before contraction.** Legacy Relay consumers migrate and all
   modern gates pass before `register_byoc`/`relay.ext.vta` code is removed.

## Dependency Graph

```text
native target skeleton + Python autoload
          |
          v
partition capability matrix
          |
          v
layout legalization + scheduled PrimFuncs
          |
          v
native RelayToTIR hook
          |
          +--------------------+
          |                    |
          v                    v
fingerprint contract      native TIRToRuntime
          |                    |
          +----------+---------+
                     v
          export/reload HOST FSIM slice
                     |
                     v
        MLPerf model/data deployment
                     |
                     v
       consumer migration + old-path removal
```

## Implementation Phases

### Phase 1: Target Extension Foundation

Deliver a loadable native target skeleton before implementing full hooks. The
intermediate loader validates the target identity; hook-presence validation is
strengthened after both hooks land. No temporary legacy callback is introduced.

- Task 1: Lock native target and loader contracts with isolated tests.
- Task 2: Build `libtvm-vta-ext` and auto-load it from full `import vta`.

#### Checkpoint A

- The shared library builds through existing automation.
- Full imports register native `Target("vta")` once.
- Runtime-only imports do not search for the compiler library.
- Missing/unloadable library diagnostics are actionable.
- The pinned TVM checkout is clean.

### Phase 2: Relay Partition And Lowering

Expand the proven current VTA partition/lowering code to the approved capability
matrix, remove contradictory compiler-region merging, add dual-layout region
legalization, and connect all VTA functions to one native RelayToTIR hook.

- Task 3: Implement the single-convolution capability and partition matrix.
- Task 4: Implement dual-layout legalization and approved convolution variants.
- Task 5: Implement and register the native IRModule RelayToTIR hook.

#### Checkpoint B

- Every supported matrix case partitions and every near miss remains on LLVM.
- Adjacent candidates become separate deterministic functions.
- NHWC/HWIO and NCHW/OIHW lower to tensorized VTA PrimFuncs.
- One native hook invocation handles every VTA function in an IRModule.
- No `relay.ext.vta` is invoked.
- Replacement strictly follows the pinned Ethos-U module-level pattern: a
  private module bridge updates every existing VTA GlobalVar from Relay
  Function to PrimFunc before ordinary `LowerTE`; no exact-name
  `relay.ext.vta` sentinel is allowed.

### Phase 3: Runtime Artifact And Configuration Safety

Create one canonical ABI fingerprint source, enforce it through the VTA C
runtime, and implement native TIRToRuntime host codegen and artifact lifecycle.

- Task 6: Define and test canonical VTA ABI fingerprint generation.
- Task 7: Implement `VTACheckConfig` in the VTA runtime and FSIM.
- Task 8: Implement native TIRToRuntime and export/reload execution.
- Task 9: Finalize automatic-import validation for both target hooks.

#### Checkpoint C

- One/many VTA PrimFuncs produce one LLVM runtime module with all symbols.
- Compile/export does not require FSIM to be loaded.
- Reloaded execution uses explicitly loaded FSIM and shows accelerator activity.
- Matched fingerprints run; mismatches fail before VTA activity.
- Mixed output equals the pure-LLVM quantized fixture elementwise.

### Phase 4: MLPerf ResNet HOST Deployment

Make the application self-contained, add only lightweight import/image
dependencies, curate deterministic licensed assets, and prove the complete
double-build workflow.

- Task 10: Add verified lightweight dependencies and licensed deterministic
  model/sample assets.
- Task 11: Implement model import, fixed quantization, and routing validation.
- Task 12: Implement dual artifact export/reload and ten-image FSIM comparison.

#### Checkpoint D

- The app runs without TensorFlow, TFLite Runtime, full CIFAR-10, or local
  `tiny-v1.4` source.
- The source model imports with the asserted ResNet-8 contract.
- Quantization occurs once and routing yields exactly eight VTA functions.
- Both artifacts reload; all ten outputs and top-1 indices agree.
- FSIM counters prove VTA GEMM/load/store activity.

### Phase 5: Modern Cutover

Migrate repository-owned Relay consumers, validate preserved low-level APIs,
then remove the classic callback in a separate contraction task.

- Task 13: Migrate Relay consumers and documentation to the modern path.
- Task 14: Remove the legacy callback and install the permanent zero-reference
  gate.
- Task 15: Run the complete verification matrix and prepare review evidence.

#### Checkpoint E

- All active Relay consumers use explicit capability partitioning and
  `Target("vta")`.
- `register_byoc`, `relay.ext.vta`, `EXTERNAL_COMPILER`, and active GraphPack
  range controls are absent.
- Preserved low-level TE/TIR and `ext_dev` workflows remain green.
- All approved module success criteria and the aggregate FSIM-only gate pass.
- The change is ready for independent review; no ship action is implied.

## Verification Strategy

Each task begins with or extends a failing focused test, implements the smallest
approved vertical slice, and reruns that test before broader checkpoints. Tests
requiring global TVM registration execute in isolated subprocesses. Runtime
tests clear profiler state and distinguish compilation from accelerator
execution.

Verification layers are:

1. Pure Python contract and capability tests.
2. Native build/load and TargetKind introspection tests.
3. Relay partition/legalization and TIR structural tests.
4. Runtime module symbol, fingerprint, export/reload, and fixture execution.
5. Full MLPerf ten-image pure-LLVM versus mixed execution.
6. Preserved low-level regression tests and legacy zero-reference scan.
7. `compileall`, `git diff --check`, and clean pinned TVM checkout.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The pinned native target-hook API cannot directly reuse current Python VTA lowering without an internal bridge | High | Make Task 5 the earliest integration proof after deterministic PrimFuncs exist; use TVM's typed pass/registry mechanisms only, keep any internal bridge private and module-at-a-time, and stop for spec escalation rather than restoring `relay.ext.vta` |
| Native TargetKind registration is process-global and cannot be cleanly reset in tests | Medium | Run import and registration cases in isolated subprocesses and test idempotency by handle identity |
| TFLite import or Relay quantization emits a form outside the approved pattern | High | Task 11 inspects and asserts the actual committed artifact before end-to-end work; add only semantics-preserving normalization already allowed by the RelayToTIR spec, otherwise escalate |
| Model topology differs from the expected 16/32/64, nine-convolution artifact | High | Verify model SHA-256 and imported shapes/operators; fail rather than padding, swapping, or editing the model |
| LLVM codegen cannot directly emit/reload VTA extern-call wrappers under the new target hook | High | Prove a one-region export/reload vertical slice in Task 8 before MLPerf integration; use standard TVM LLVM module APIs and no custom ModuleNode |
| Fingerprint fields drift between compiler and runtime | High | Generate both from one canonical normalized descriptor/schema version and test every ABI-relevant field for sensitivity |
| Exact output equality is broken by layout or integer semantics | High | Compare small fixtures at each legalization/lowering step before ResNet; keep host fallback for unsupported candidates and never loosen equality silently |
| Cutover breaks low-level VTA users | Medium | Maintain an explicit preserved-interface inventory and run representative TE/TIR, instruction, FSIM, and runtime-only tests before contraction |
| Existing user-owned untracked benchmark/data files overlap app paths | Medium | Treat `tiny-v1.4` and full CIFAR-10 as read-only sources; create only the approved `image_classification_v1` subtree and never clean unrelated files |

## Parallelization

Implementation is intentionally mostly sequential because all slices modify the
same VTA compiler/runtime boundary. After Checkpoint C, asset/provenance work in
Task 10 can proceed independently of application compiler logic, but repository
instructions assign Build/Verify to one implementation agent to avoid shared
file conflicts. Review occurs only after Task 15.

## Open Questions

None. Any implementation discovery that requires changing an approved public
contract, operator capability, artifact type, numerical comparison, dependency,
or preserved-interface boundary returns to the root specification gate.

## Approval Gate

The user must approve this plan and its task ordering before Build begins.
Approval authorizes task execution only within the five approved specs; it does
not authorize commit, push, release, or another external ship action.
