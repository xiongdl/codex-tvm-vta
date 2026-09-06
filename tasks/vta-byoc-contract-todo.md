# Tasks: VTA BYOC Contract

## Task 1: Implement compiler identity and environment snapshot

**Description:** Add the minimal production module that owns the VTA compiler
tag, registry name, and immutable snapshot of compilation-relevant values from
the active `vta.Environment`.

**Acceptance criteria:**

- [x] Compiler and registry names have one definition.
- [x] Snapshot fields cover batch/block factors, dtypes, execution target,
  host target, model, and runtime device type.
- [x] Invalid or missing environment values raise `TypeError` or `ValueError`
  at snapshot construction.

**Verification:**

- [x] Focused unit tests fail before implementation and pass afterward.
- [x] Python compilation succeeds for the new package.

**Dependencies:** None

**Files likely touched:**

- `vta/python/vta/relay/__init__.py`
- `vta/python/vta/relay/contract.py`
- `vta/tests/python/unittest/test_byoc_contract.py`

**Estimated scope:** Medium (3 files)

## Task 2: Verify the public contract boundary

**Description:** Add tests proving that contract values are exported from
`vta.relay`, environment snapshots are immutable and deterministic, and
importing the package has no backend-registration side effects.

**Acceptance criteria:**

- [x] `vta.relay` exports only the approved contract surface for this module.
- [x] Equivalent active environments produce equal snapshots that cannot be
  mutated.
- [x] Importing `vta.relay` does not register `relay.ext.vta`.

**Verification:**

- [x] Focused contract test module passes in a fresh Python process.
- [x] Existing VTA environment unit tests pass.

**Dependencies:** Task 1

**Files likely touched:**

- `vta/python/vta/relay/__init__.py`
- `vta/tests/python/unittest/test_byoc_contract.py`

**Estimated scope:** Small (2 files)

## Checkpoint A: Contract foundation

- [x] Tasks 1-2 acceptance criteria pass.
- [x] `relay.ext.vta` remains absent until the external-codegen module owns it.
- [x] No upstream TVM file is modified.
- [x] Human review confirms the compiler/device boundary remains correct.

## Task 3: Add reusable Relay BYOC fixtures

**Description:** Add test-only builders for a deterministic typed Relay module
containing host pre/post operations around the initial quantized convolution
candidate, plus a near-miss graph differing by one unsupported capability.

**Acceptance criteria:**

- [x] The supported fixture contains static shapes, constant weights, and
  dtypes derived from the active environment.
- [x] Host-only operations exist before and after the candidate region.
- [x] The near-miss builder names and isolates its unsupported attribute.

**Verification:**

- [x] Fixture construction and `InferType` pass in the configured TVM build.
- [x] Repeated construction yields structurally equal modules.

**Dependencies:** Checkpoint A

**Files likely touched:**

- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_contract.py`

**Estimated scope:** Small (2 files)

## Task 4: Lock the fixture contract

**Description:** Add structural assertions that make later partitioning,
lowering, and runtime tests share exactly the same supported-domain fixture
instead of inventing incompatible graphs in each phase.

**Acceptance criteria:**

- [x] Tests assert operator order, constant ownership, inferred dtypes, and
  expected host/VTA region boundaries.
- [x] Tests prove the near-miss differs from the supported fixture only in its
  declared unsupported capability.
- [x] No production module imports test fixtures.

**Verification:**

- [x] Focused contract tests pass.
- [x] `./scripts/test_vta_fsim.sh` passes.
- [x] `git -C tvm status --short` remains empty.

**Dependencies:** Task 3

**Files likely touched:**

- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_contract.py`

**Estimated scope:** Small (2 files)

## Checkpoint B: Ready for pattern partitioning

- [x] Tasks 1-4 acceptance criteria pass.
- [x] Correctness and quality sections of the project Definition of Done pass.
- [x] No tests are skipped, weakened, or deleted.
- [x] No placeholder pattern table or external compiler callback exists.
- [ ] Human review approves implementation before work begins.
