# Implementation Plan: VTA BYOC Runtime Integration

## Overview

Prove the first complete VTA BYOC runtime path on local FSIM: partition a
supported Relay graph through capability patterns, compile it through the
registered external compiler, export and reload the resulting graph executor
artifact, execute it on `ext_dev(0)`, and compare its output exactly with an
LLVM reference. Build the riskiest no-bias execution slice first, then lock
artifact/ABI invariants, expand to all approved bias forms, and integrate the
runtime proof into the standard regression gate.

## Architecture Decisions

- Runtime integration enters only through the public
  `partition_for_vta`/`register_byoc`/`relay.build` path; private lowering and
  compiler helpers are not runtime entry points.
- The outer Relay build uses `vta.build_config()` so host wrappers safely
  access `ext_dev` storage; external runtime codegen suppresses inherited VTA
  passes to preserve the single-lowering boundary.
- Local FSIM through `rpc.LocalSession()` and `ext_dev(0)` is the first
  mandatory execution target; TSIM, FPGA, tracker RPC, and hardware remain out
  of scope.
- The existing graph executor artifact and VTA `device_api.ext_dev` lifecycle
  are reused unchanged. No new runtime module, ABI, cache, or public API is
  planned.
- The first vertical slice includes export and reload before numerical
  execution so success cannot hide serialization/import defects.
- Numerical correctness is exact against the same unpartitioned Relay graph
  compiled for LLVM with deterministic signed integer input.
- Production changes are not assumed. Any runtime defect discovered by the
  RED test is fixed at its owning boundary only after the failure is localized
  and the specification is updated if the ABI or artifact contract changes.

## Dependency Graph

```text
Task 1: no-bias public-path FSIM execution
  -> Task 2: artifact, symbol, ABI, and lifecycle invariants
      -> Task 3: all approved bias variants
          -> Task 4: host fallback and failure semantics
              -> Task 5: standard regression and review gate
```

The tasks are sequential because each expands assertions around the same
runtime fixture, process-global compiler registration, and FSIM lifecycle.
Parallel implementation would increase registry and shared-build-state risk
without reducing the critical path.

## Task List

### Phase 1: First Executable Vertical Slice

- Task 1: Build, export, reload, and numerically execute the no-bias fixture
  through the public VTA BYOC path.
- Task 2: Lock the reloaded symbol, two-buffer external ABI, internal constants,
  output metadata, and compilation-versus-execution lifecycle.

### Checkpoint A: Real FSIM artifact

- The no-bias graph executes after export and reload on local `ext_dev(0)`.
- Its output exactly equals the LLVM reference.
- Host operations remain around one VTA partition.
- Artifact, symbol, constants, and runtime ABI match the approved upstream
  contracts.
- Human review approves the observed runtime lifecycle before expanding the
  variant matrix.

### Phase 2: Capability Matrix and Fallback

- Task 3: Run the full numerical lifecycle for no-bias, `nn.bias_add`, and
  broadcast-constant `add` variants with deterministic signed inputs.
- Task 4: Lock host-only near-miss execution and stable failures for missing
  FSIM/device registration or malformed reloaded artifacts where they can be
  induced without changing production APIs.

### Checkpoint B: Runtime contract complete

- Every approved variant executes exactly and without skipped tests.
- Unsupported non-constant-weight Relay remains host-only and never reaches
  VTA codegen or `ext_dev` execution.
- Setup and artifact failures identify the failing lifecycle boundary.
- No capability predicate, lowering domain, runtime ABI, or public API has
  broadened.
- Human review approves numerical and fallback coverage.

### Phase 3: Regression Integration

- Task 5: Add the runtime test to the canonical FSIM gate if appropriate, run
  the complete BYOC and FSIM suites, perform code review/simplification, and
  document the verified current behavior.

### Checkpoint C: Ready for graphpack retirement

- Runtime integration success criteria and the project Definition of Done
  correctness, quality, integration, and documentation sections pass.
- The standard FSIM command exercises the BYOC numerical path without changing
  existing command-line options.
- No test is skipped, weakened, or deleted.
- The pinned TVM checkout remains clean and no runtime format, dependency, or
  unrelated VTA change is introduced.
- Human review approves the module before repository graphpack migration.

## Verification Strategy

Use focused TDD beginning with one no-bias end-to-end test. A failing run is
classified before implementation changes as one of: build, export, upload,
reload, device allocation, graph executor creation, input copy, external
kernel call, output copy, or numerical mismatch. This keeps any correction in
the component that owns the failure.

After each task, run the focused runtime test and the upstream BYOC tests most
likely to expose boundary regressions. At Checkpoint C, run:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_contract.py \
  vta/tests/python/unittest/test_byoc_partition.py \
  vta/tests/python/unittest/test_byoc_lowering.py \
  vta/tests/python/unittest/test_byoc_codegen.py \
  vta/tests/python/unittest/test_byoc_runtime.py -q

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m compileall -q vta/python/vta/relay

./scripts/test_vta_fsim.sh
git -C vta diff --check
git -C tvm status --short
```

Assertions inspect outcomes and stable contracts rather than fixed runtime
module nesting. Temporary artifact paths are created through TVM test
utilities and disappear with the test process.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Host operations and VTA functions receive incompatible device storage | High | Make the first task a real mixed host/VTA graph executor run on `ext_dev(0)` and inspect the failing lifecycle stage before changing code |
| Exported host/device module imports lose the external symbol | High | Export and reload in the first slice; query imported modules rather than assume a fixed nesting layout |
| Internal weight/bias constants become runtime parameters after reload | High | Assert external PrimFunc ABI and graph input names before and after artifact lifecycle expansion |
| Simulator tests accidentally pass without invoking VTA | High | Require one outlined VTA symbol, inspect simulator activity around execution where stable, and retain host/VTA partition structure assertions |
| Process-global `relay.ext.vta` registration contaminates test order | Medium | Use one explicit idempotent registration path or isolated subprocesses for collision/error cases |
| LLVM reference differs because of layout or signed arithmetic assumptions | Medium | Compile the exact same typed unpartitioned Relay fixture and compare exact shape, dtype, and values |
| Missing FSIM build causes silent loss of runtime coverage | High | Fail with the documented build command; do not add skip markers |
| Runtime stage expands into graphpack migration or TSIM work | Medium | Keep those modules out of touched files and stop for approval if a new ABI, executor, or target is required |

## Rollback

Each task is committed as an atomic VTA submodule change after focused tests
pass. Runtime test and any narrowly required production correction remain in
separate commits when they represent different concerns. The top-level
repository records approved specification/plan/task documents and the VTA
submodule pointer separately. Reverting the runtime-test series restores the
external-codegen state without altering graphpack callers or public APIs.

## Open Questions

None. If Task 1 proves that the existing graph executor artifact cannot
represent the mixed host/VTA lifecycle, stop and revise the approved spec
rather than introducing a new runtime representation implicitly.
