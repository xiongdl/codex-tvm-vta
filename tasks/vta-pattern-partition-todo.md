# Tasks: VTA Capability-Based Relay Partitioning

## Task 1: Match the exact convolution composite

**Description:** Add the `vta.qnn_conv2d` dataflow pattern and tests for the
required convolution/requantization tail plus optional constant bias/add.

**Acceptance criteria:**

- [x] The supported fixture merges into exactly one `vta.qnn_conv2d`
  composite.
- [x] Optional `nn.bias_add` and right-hand constant `add` forms match.
- [x] Host producer and consumer operators remain outside the composite.

**Verification:**

- [x] Focused pattern tests fail before implementation and pass afterward.
- [x] Pattern-table construction does not alter TVM's global table registry.

**Dependencies:** None

**Files likely touched:**

- `vta/python/vta/relay/patterns.py`
- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_partition.py`

**Estimated scope:** Medium (3 files)

## Task 2: Enforce constants and dtypes

**Description:** Implement the core capability predicate for constant
ownership, input/weight/accumulator/output dtypes, optional bias/add dtype, and
static inferred types.

**Acceptance criteria:**

- [x] Approved constant and dtype forms return `True`.
- [x] Each wrong dtype and non-constant required operand returns `False`.
- [x] Ordinary malformed/unsupported candidates do not raise.

**Verification:**

- [x] Parameterized predicate and `MergeComposite` tests pass.
- [x] Existing BYOC contract tests pass.

**Dependencies:** Task 1

**Files likely touched:**

- `vta/python/vta/relay/patterns.py`
- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_partition.py`

**Estimated scope:** Medium (3 files)

## Checkpoint A: Composite domain

- [x] Tasks 1-2 acceptance criteria pass.
- [x] Pattern matching is local and contains no model/start/stop knowledge.
- [x] No process-global compiler or pattern registration occurs on import.
- [x] Human review approves the composite boundary.

## Task 3: Enforce hardware capability boundaries

**Description:** Complete the predicate for static shapes, block divisibility,
layouts, convolution attributes, weight consistency, scalar shift range,
optional broadcast constant, and clip bounds.

**Acceptance criteria:**

- [x] Every supported boundary in the spec has an acceptance test.
- [x] Every unsupported shape/layout/attribute boundary returns `False`.
- [x] Predicate behavior is deterministic for an explicit compiler config.

**Verification:**

- [x] Parameterized focused tests pass without skips.
- [x] Contract tests pass unchanged.

**Dependencies:** Checkpoint A

**Files likely touched:**

- `vta/python/vta/relay/patterns.py`
- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_partition.py`

**Estimated scope:** Medium (3 files)

## Checkpoint B: Lowering-safe predicate

- [x] Task 3 acceptance criteria pass.
- [x] Predicate acceptance equals the approved initial lowering domain.
- [x] No assertions handle public or ordinary capability failures.
- [x] Human review approves predicate completeness.

## Task 4: Implement partition_for_vta

**Description:** Add public argument validation, parameter binding, existing-
partition detection, and the approved standard BYOC Sequential pipeline.

**Acceptance criteria:**

- [x] Valid input returns a typed partitioned `IRModule`.
- [x] Invalid `mod`, `params`, and `mod_name` values raise approved errors.
- [x] Pass order exactly matches the specification.

**Verification:**

- [x] Public API tests fail before implementation and pass afterward.
- [x] Parameter binding is verified with a constant-weight input parameter.

**Dependencies:** Checkpoint B

**Files likely touched:**

- `vta/python/vta/relay/partition.py`
- `vta/tests/python/unittest/test_byoc_partition.py`

**Estimated scope:** Small (2 files)

## Task 5: Lock partition structure and idempotence

**Description:** Verify outlined attributes, deterministic symbols, constant
ownership, host fallback, typed boundaries, near-miss behavior, and repeated-
partition idempotence.

**Acceptance criteria:**

- [x] Supported fixture creates exactly one correctly attributed VTA global.
- [x] Host operations and constants remain at the specified boundaries.
- [x] A second partition call is structurally equivalent to the first.

**Verification:**

- [x] Structural partition tests pass.
- [x] Near-miss module contains no VTA compiler globals.

**Dependencies:** Task 4

**Files likely touched:**

- `vta/python/vta/relay/partition.py`
- `vta/tests/python/unittest/test_byoc_partition.py`

**Estimated scope:** Small (2 files)

## Checkpoint C: Partitioning complete

- [x] Tasks 4-5 acceptance criteria pass.
- [x] No `relay.ext.vta` callback is registered.
- [x] No graphpack markers or start/stop selection are referenced.
- [ ] Human review approves Relay partition output.

## Task 6: Export API and run regression gate

**Description:** Add `partition_for_vta` to the public `vta.relay` surface,
document it, and run the complete module verification without expanding scope.

**Acceptance criteria:**

- [x] `from vta.relay import partition_for_vta` is supported.
- [x] Public docs and `__all__` match the implemented surface.
- [x] No unrelated VTA API changes are introduced.

**Verification:**

- [x] Partition and contract tests pass together.
- [x] Python compilation and `./scripts/test_vta_fsim.sh` pass.
- [x] `git -C tvm status --short` remains empty.
- [x] Code review and simplification checks find no unresolved required issue.

**Dependencies:** Checkpoint C

**Files likely touched:**

- `vta/python/vta/relay/__init__.py`
- `vta/tests/python/unittest/test_byoc_contract.py`
- `vta/tests/python/unittest/test_byoc_partition.py`

**Estimated scope:** Medium (3 files)

## Checkpoint D: Ready for Relay lowering

- [x] Tasks 1-6 acceptance criteria pass.
- [x] Project Definition of Done correctness, quality, integration, and
  documentation sections pass for this module.
- [x] No tests are skipped, weakened, or deleted.
- [ ] Human review approves the module before `vta-relay-lowering` begins.
