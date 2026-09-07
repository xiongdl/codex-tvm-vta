# Implementation Plan: VTA Relay Lowering

## Overview

Implement function-local packed-layout legalization and scheduled Relay-to-TIR
lowering for the already-partitioned `vta.qnn_conv2d` capability slice. The
module ends at a validated VTA `PrimFunc`; external compiler registration and
runtime module creation remain downstream work.

## Architecture Decisions

- Keep host-visible parameters and results in NCHW. Insert pack/unpack Relay
  expressions only inside the outlined VTA function.
- Match a typed `Composite="vta.qnn_conv2d"` function call and rewrite it with
  a `DFPatternCallback`, following the pinned Ethos-U legalization structure.
- Reimplement only the approved layout permutations in `vta.relay.transform`;
  do not import graphpack or its stateful `ExprPack` mutator.
- Use `relay.backend.te_compiler.get().lower` with the full VTA target so the
  packed convolution anchor selects VTA's existing TOPI schedule. Do not use
  UMA's target-less `LowerToTE` plus direct `te.create_prim_func` path.
- Run existing `vta.build_config` TIR passes and preserve symbol, target, and
  Relay attributes for the external-codegen consumer.
- Keep lowering internal; `partition_for_vta` remains the only public Relay API.

## Dependency Graph

```text
outlined-function validator
  -> composite-local Relay legalizer
      -> packed-Relay invariant tests
          -> TE graph + VTA schedule proof
              -> VTA TIR lowering + metadata
                  -> regression/public-boundary gate
```

## Task List

### Phase 1: Validate and Legalize Relay

- Task 1: Define outlined-function validation contract.
- Task 2: Legalize the core packed convolution and host ABI.
- Task 3: Legalize optional constants and quantization tail.

### Checkpoint A: Packed Relay Domain

- Validator and packed-Relay tests pass for all accepted/rejected forms.
- Legalization is local, typed, deterministic, and graphpack-independent.
- Human review approves the packed Relay representation.

### Phase 2: Prove Scheduled TIR

- Task 4: Establish the TE graph and VTA scheduling bridge.
- Task 5: Lower scheduled TE through VTA TIR passes and preserve metadata.

### Checkpoint B: Lowering-Safe TIR

- TIR contains evidence of the expected VTA scheduled/tensorized path.
- Unsupported or unscheduled lowering fails before external codegen.
- Human review approves the Relay-to-TIR boundary.

### Phase 3: Integrate the Module Boundary

- Task 6: Stabilize the internal lowering entry point and run regressions.

### Checkpoint C: Ready for External Codegen

- All lowering acceptance criteria and Definition of Done gates pass.
- No `relay.ext.vta` hook or runtime artifact is produced yet.
- Human review approves starting `vta-external-codegen`.

## Verification Strategy

Each task follows RED/GREEN/REFACTOR with focused tests in
`test_byoc_lowering.py`. Checkpoints run contract, partition, and lowering tests
together, Python compilation, `git diff --check`, and standalone FSIM tests.
The TVM checkout must remain clean throughout.

The highest-risk assertion is not “a PrimFunc exists,” but that the existing
VTA packed-convolution schedule was selected and its tensorization/intrinsic
structure survives to the inspected lowering stage.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| TE lowering fails to select the VTA schedule | High | Use target-aware `TECompiler.lower` and structurally require GEMM tensorization before TIR lowering |
| Relay packing changes the external ABI | High | Lock parameter/return types before and after legalization and keep pack/unpack local |
| Predicate and lowerer drift | High | Reuse composite/config constants and parameterize the same accepted/rejected fixtures |
| Constants are lost or reordered between Relay and TE | Medium | Lock `CachedFunc` input/output/constant ordering before downstream artifact work |
| Import introduces external compiler registration | Medium | Fresh-process registry tests remain in the regression gate |
| TIR assertions become textual and brittle | Medium | Prefer structural node/attribute inspection; limit text checks to stable intrinsic names |

## Rollback

Land each task as an atomic VTA commit. Until the external compiler is
registered, the new internal module is unreachable from normal Relay build, so
any task can be reverted independently without changing `partition_for_vta`.

## Open Questions

None. Task 4 established the target-aware TE scheduling bridge without a TVM patch.
