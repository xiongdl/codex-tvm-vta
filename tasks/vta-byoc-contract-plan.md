# Implementation Plan: VTA BYOC Contract

## Overview

Implement the executable foundation defined by `SPEC-vta-byoc-contract.md`
without pretending that partitioning or external code generation already
exists. The increment centralizes the stable compiler identity and active VTA
configuration snapshot, validates that contract at its public boundary, and
adds reusable Relay fixtures that later modules extend from structural
partition tests through FSIM execution.

Tasks are tracked in `tasks/vta-byoc-contract-todo.md`. The default
`tasks/plan.md` and `tasks/todo.md` remain owned by the unfinished VTA source
migration plan and are not modified.

## Architecture Decisions

- Add a focused `vta.relay` package because BYOC integration does not belong
  to the existing TOPI-oriented `vta.top` namespace.
- Define `COMPILER_NAME = "vta"` and `EXTERNAL_COMPILER = "relay.ext.vta"` in
  one module; downstream pattern and backend modules import these values.
- Represent hardware-dependent compilation state as an immutable snapshot
  derived from the active `vta.Environment`. Do not introduce duplicate user
  configuration or PassContext options in this increment.
- Validate the environment when the snapshot is created. Internal lowering
  code may trust a successfully constructed snapshot.
- Keep test graph construction in test code. Production code must not depend
  on fixtures, and no temporary helper script is needed.
- Do not register placeholder patterns or compiler callbacks. A missing hook is
  more honest and diagnosable than a stub that claims the backend is usable.

## Dependency Graph

```text
contract constants + immutable environment snapshot
  -> public package export + boundary validation tests
  -> reusable supported/near-miss Relay fixtures
  -> contract checkpoint
```

## Task List

### Phase 1: Compiler Contract Foundation

- Task 1: Implement compiler identity and environment snapshot.
- Task 2: Export and verify the stable contract boundary.

### Checkpoint A: Contract Foundation

- Focused contract tests pass.
- Invalid environments fail with stable public exceptions.
- Importing `vta.relay` performs no registration, compilation, hardware
  access, or filesystem writes.

### Phase 2: Shared BYOC Test Fixture

- Task 3: Add supported and near-miss Relay module builders.
- Task 4: Verify fixture types, determinism, and host/VTA boundary shape.

### Checkpoint B: Ready for Pattern Partitioning

- The fixture contains a statically typed candidate region and host-only
  operators on both sides.
- The near-miss fixture differs by one explicit unsupported capability.
- Existing VTA FSIM unit tests remain green.
- TVM remains clean and no placeholder external compiler is registered.
- Human review approves the increment before the
  `vta-pattern-partition` specification begins.

## Verification Strategy

Use the existing environment and test scripts discovered under `scripts/`:

```bash
.envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_contract.py -q

.envs/tvm-vta-env/bin/python -m compileall -q vta/python/vta/relay

./scripts/test_vta_fsim.sh

git -C tvm status --short
git -C vta status --short
```

`./scripts/test_vta_fsim.sh` remains unchanged unless the new focused test is
later promoted into its canonical test list. This contract increment does not
need a new repository script.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Contract snapshot duplicates `Environment` state | High | Snapshot is derived only from `Environment`; it has no independent defaults |
| Import side effects make tests order-dependent | High | Do not register hooks at package import; test registry state explicitly |
| Fixture encodes behavior lowering cannot support | High | Build it from the smallest existing VTA convolution path and require later predicate/lowering specs to use the same fixture |
| UMA `kDLCPU` assumptions leak into VTA | High | Keep `kDLExtDev` and `ext_dev -device=vta` explicit in contract assertions |
| New package becomes an abstraction shell | Medium | Add only values and validation used by the immediately following partition module |
| Existing source-migration work is disturbed | High | Use module-specific plan files and touch only VTA BYOC paths |

## Rollback

Before commit, revert only the files named in this module's task list. After an
atomic commit, revert that commit. No TVM or source-migration files need to be
removed or rewritten.

## Open Questions

None. The user approved the contract specification and explicitly authorized
module-specific plan and task-list filenames.
