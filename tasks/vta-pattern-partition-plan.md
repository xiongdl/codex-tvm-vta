# Implementation Plan: VTA Capability-Based Relay Partitioning

## Overview

Implement `SPEC-vta-pattern-partition.md` as a sequence of small, testable
increments. The module first proves the composite pattern shape, then closes
the predicate's type and layout domain, exposes the standard BYOC Pass
pipeline, and finally locks partition output and idempotence. It creates valid
`Compiler="vta"` Relay functions but deliberately does not register or fake
`relay.ext.vta`.

Tasks are tracked in `tasks/vta-pattern-partition-todo.md`. Existing plan and
task files remain unchanged.

## Architecture Decisions

- Keep pattern construction and capability policy in `patterns.py`; keep
  public input validation and Pass orchestration in `partition.py`.
- Use the approved `VTACompilerConfig` snapshot rather than reading mutable
  environment values throughout predicate traversal.
- Implement the exact required tail first. Optional bias/add alternatives are
  represented by explicit patterns or a clear optional union, whichever gives
  more reliable `MergeComposite` behavior in the pinned TVM version.
- Parse a matched expression once into a private candidate representation if
  tests show optional-chain traversal would otherwise be duplicated.
- Reject normal capability misses with `False`; reserve exceptions for invalid
  public inputs or violated internal invariants.
- Use TVM's existing pattern and partition APIs without modifying upstream
  TVM or adding dependencies.

## Dependency Graph

```text
exact qnn_conv2d pattern
  -> constant/type predicate
  -> shape/layout/attribute predicate
  -> partition_for_vta Pass pipeline
  -> output invariants + idempotence
  -> module regression gate
```

## Task List

### Phase 1: Pattern and Core Predicate

- Task 1: Match the exact convolution and requantization composite.
- Task 2: Enforce constant and dtype capability constraints.

### Checkpoint A: Composite Domain

- Supported, optional-bias, and optional-add forms merge as
  `vta.qnn_conv2d`.
- Near misses remain unmerged without raising.
- Pattern-table construction has no process-global registration side effect.

### Phase 2: Hardware Capability Boundary

- Task 3: Enforce shape, layout, convolution-attribute, shift, and clip bounds.

### Checkpoint B: Lowering-Safe Predicate

- Every constraint in the approved spec has an accepted and rejected test.
- The predicate accepts no graph outside the documented initial lowering
  domain.
- Existing BYOC contract tests remain green.

### Phase 3: Public Partition Pipeline

- Task 4: Implement validated `partition_for_vta` orchestration.
- Task 5: Lock output structure, host fallback, symbols, and idempotence.

### Checkpoint C: Partitioning Complete

- The supported fixture produces exactly one VTA compiler region.
- The near-miss fixture produces none.
- Repeated partitioning is structurally idempotent.
- No external compiler callback or graphpack marker dependency exists.

### Phase 4: Public Export and Regression Gate

- Task 6: Export the partition API and run module-level verification.

### Checkpoint D: Ready for Relay Lowering

- Focused partition and contract tests pass.
- Python compilation and existing FSIM tests pass.
- TVM remains clean.
- Code review and simplification gates pass.
- Human review approves the increment before the
  `vta-relay-lowering` specification begins.

## Verification Strategy

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_partition.py -q

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_contract.py \
  vta/tests/python/unittest/test_byoc_partition.py -q

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m compileall -q vta/python/vta/relay

./scripts/test_vta_fsim.sh

git -C tvm status --short
git -C vta diff --check
```

No new script is needed. The existing FSIM script remains the regression
entry point.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Optional pattern greedily captures host operators | High | Assert exact composite body and host operations structurally |
| Predicate and later lowering domains drift | High | Parameterize every accepted/rejected boundary and reuse the same fixture in lowering tests |
| Pattern predicate raises on an ordinary near miss | High | Test malformed and unsupported call shapes through `MergeComposite` |
| `AnnotateTarget` absorbs non-candidate host calls | High | Assert host `abs` and `transpose` remain outside the compiler global |
| Repartitioning creates nested functions | Medium | Detect existing VTA compiler globals and test structural idempotence |
| Import registers global state | Medium | Test pattern-table registry before and after importing public partition API |
| Partition tests accidentally invoke missing codegen | Medium | Stop verification at Relay structure; never call `relay.build` in this module |

## Rollback

Each task is additive and independently revertible. Revert the task commit or
remove only its named files/exports. Do not modify TVM, graphpack, or existing
VTA runtime paths during rollback.

## Open Questions

None. The accepted operator and attribute domain is fixed by the approved
specification.
