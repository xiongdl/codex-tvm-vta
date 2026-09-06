# Tasks: VTA Relay Lowering

## Task 1: Validate outlined VTA functions

**Description:** Add the internal lowering entry contract and validation for
function type, compiler/composite attributes, symbol, static types, and explicit
compiler configuration.

**Acceptance criteria:**

- [ ] The approved partitioned function passes validation.
- [ ] Wrong Python types and missing/mismatched attributes raise stable errors.
- [ ] Malformed composite bodies and config mismatches fail before TE lowering.

**Verification:**

- [ ] Focused validation tests fail before implementation and pass afterward.
- [ ] Importing the module does not register `relay.ext.vta`.

**Dependencies:** Completed `vta-pattern-partition`

**Files likely touched:**

- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Small (2 files)

## Task 2: Legalize packed convolution and host ABI

**Description:** Rewrite the composite call into locally packed input/weight,
packed `nn.conv2d`, and an unpacked NCHW result without graphpack dependencies.

**Acceptance criteria:**

- [ ] Data and constant weight use the specified reshape/transpose mappings.
- [ ] Packed convolution layouts and attributes match VTA TOPI requirements.
- [ ] External parameter/return types remain the original NCHW ABI.

**Verification:**

- [ ] Structural Relay tests pass for packed shapes, layouts, and constant ownership.
- [ ] No graphpack marker, start/stop, model, or operator-index reference exists.

**Dependencies:** Task 1

**Files likely touched:**

- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Small (2 files)

## Task 3: Preserve fused constants and quantization tail

**Description:** Handle the no-bias, `nn.bias_add`, and right-hand constant
`add` variants, followed by scalar right shift, clip, cast, and output unpack.

**Acceptance criteria:**

- [ ] All three approved composite variants legalize deterministically.
- [ ] Bias/add constants broadcast in the packed output layout.
- [ ] Shift, clip bounds, output dtype, and numerical Relay behavior are preserved.

**Verification:**

- [ ] Parameterized structure tests pass without skips.
- [ ] Relay executor comparison matches the original fixture for representative inputs.

**Dependencies:** Task 2

**Files likely touched:**

- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/byoc_utils.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Medium (3 files)

## Checkpoint A: Packed Relay domain

- [ ] Tasks 1-3 acceptance criteria pass.
- [ ] Legalized Relay is typed, deterministic, local, and graphpack-independent.
- [ ] Predicate acceptance equals legalization acceptance.
- [ ] Human review approves the packed Relay representation.

## Task 4: Prove the VTA TE scheduling bridge

**Description:** Lower legalized Relay with the pinned `LowerToTE` API, apply
the existing packed convolution schedule, and prove schedule/tensorization
evidence before committing to the final TIR pipeline.

**Acceptance criteria:**

- [ ] The TE graph selects the existing VTA packed convolution compute domain.
- [ ] `schedule_conv2d_packed` accepts the graph including the fused tail.
- [ ] Scheduled output contains stable evidence of the VTA GEMM tensorization path.

**Verification:**

- [ ] Focused schedule tests fail for an unscheduled graph and pass for VTA scheduling.
- [ ] If the bridge requires a TVM patch, implementation stops for user approval.

**Dependencies:** Checkpoint A

**Files likely touched:**

- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Small (2 files)

## Task 5: Produce validated VTA TIR

**Description:** Run scheduled TE through the existing VTA build-pass context,
select the requested PrimFunc, and attach deterministic symbol, target, and
Relay metadata for downstream codegen.

**Acceptance criteria:**

- [ ] Lowering returns exactly one VTA-compatible `tir.PrimFunc`.
- [ ] Symbol, target, buffer ordering, and Relay attributes satisfy the spec.
- [ ] Required VTA intrinsic/coprocessor structure remains after lowering.

**Verification:**

- [ ] Structural TIR and metadata tests pass for every approved composite variant.
- [ ] Repeated lowering is structurally deterministic.

**Dependencies:** Task 4

**Files likely touched:**

- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Small (2 files)

## Checkpoint B: Lowering-safe TIR

- [ ] Tasks 4-5 acceptance criteria pass.
- [ ] No unscheduled fallback or graphpack dependency exists.
- [ ] TIR validation fails before downstream codegen for contract violations.
- [ ] Human review approves the Relay-to-TIR output.

## Task 6: Stabilize lowering boundary and run regressions

**Description:** Document the internal consumer contract, confirm it does not
expand `vta.relay.__all__`, and run the complete module regression gate.

**Acceptance criteria:**

- [ ] `lower_vta_function` is documented for the external-codegen consumer.
- [ ] The public `vta.relay` surface remains unchanged.
- [ ] No unrelated VTA API or scheduling behavior changes are introduced.

**Verification:**

- [ ] Contract, partition, and lowering tests pass together.
- [ ] Python compilation and `./scripts/test_vta_fsim.sh` pass.
- [ ] `git -C tvm status --short` remains empty.
- [ ] Code review and simplification checks find no unresolved required issue.

**Dependencies:** Checkpoint B

**Files likely touched:**

- `vta/python/vta/relay/transform.py`
- `vta/tests/python/unittest/test_byoc_lowering.py`

**Estimated scope:** Small (2 files)

## Checkpoint C: Ready for external codegen

- [ ] Tasks 1-6 acceptance criteria pass.
- [ ] Project Definition of Done correctness, quality, integration, and documentation pass.
- [ ] No tests are skipped, weakened, or deleted.
- [ ] No `relay.ext.vta` hook or runtime artifact exists in this module.
- [ ] Human review approves implementation before `vta-external-codegen` begins.
