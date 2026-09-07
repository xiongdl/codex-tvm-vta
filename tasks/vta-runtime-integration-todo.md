# Tasks: VTA BYOC Runtime Integration

## Task 1: Execute one exported BYOC graph on FSIM

**Description:** Add the first no-bias vertical-slice test that builds the
shared fixture through `partition_for_vta`, explicit `register_byoc`, and
`relay.build`; exports and reloads the graph executor artifact through a local
RPC session; runs it on `ext_dev(0)`; and compares it exactly with the same
unpartitioned Relay graph executed on LLVM.

**Acceptance criteria:**

- [x] The compiled graph contains one VTA external region with host `abs` and
  `transpose` outside it.
- [x] The exported and reloaded artifact creates a graph executor and completes
  one FSIM run through the public BYOC path.
- [x] Output shape, dtype, and values exactly equal the deterministic LLVM
  reference for signed input containing negative and positive values.

**Verification:**

- [x] The focused runtime test fails before the runtime path is established
  and passes afterward.
- [x] Any initial failure is localized to a named lifecycle stage before a
  production code change is made.

**Dependencies:** Completed `vta-external-codegen`

**Files likely touched:**

- `vta/tests/python/unittest/test_byoc_runtime.py`
- A narrowly owning production file only if the RED test exposes a real defect

**Estimated scope:** Small (1-2 files)

## Task 2: Lock artifact and runtime ABI invariants

**Description:** Extend the executable slice with assertions for exact symbol
survival after reload, graph input ownership, the external two-buffer ABI,
internal convolution constants, boundary metadata, and the separation between
compile time and simulator execution.

**Acceptance criteria:**

- [x] The reloaded module implements the exact deterministic external symbol,
  including through imports.
- [x] Runtime inputs contain graph data only; weight and bias constants remain
  internal and the external function ABI remains input then output.
- [x] Compilation/export does not execute the simulator, while executor run
  produces observable simulator activity where the FSIM counters support it.

**Verification:**

- [x] Focused invariant tests pass together with Task 1.
- [x] Existing partition, lowering, and codegen structure tests pass unchanged.

**Dependencies:** Task 1

**Files likely touched:**

- `vta/tests/python/unittest/test_byoc_runtime.py`
- `vta/tests/python/unittest/byoc_utils.py` only if a shared observation helper
  is justified

**Estimated scope:** Small (1-2 files)

## Checkpoint A: Real FSIM artifact

- [x] Tasks 1-2 acceptance criteria pass.
- [x] The no-bias graph executes after export and reload on local FSIM.
- [x] Artifact symbol, constants, ABI, metadata, and host/VTA boundaries match
  the approved upstream contracts.
- [x] No new runtime representation or public API was introduced.
- [x] Human review approves the observed lifecycle before variant expansion.

## Task 3: Execute every approved bias variant

**Description:** Parameterize the complete build/export/reload/execute/reference
flow across no bias, constant `nn.bias_add`, and right-hand broadcast constant
`add`, using deterministic signed inputs that exercise absolute value, shift,
clip, cast, and transpose behavior.

**Acceptance criteria:**

- [x] All three approved composite variants execute through the same public
  runtime path without special-case compilation logic.
- [x] Each output exactly matches its LLVM reference in shape, dtype, and
  values.
- [x] Bias constants remain internal after export and reload and do not expand
  graph or external-function inputs.

**Verification:**

- [x] Parameterized focused runtime tests pass without skips.
- [x] Existing capability predicates still accept exactly the approved domain.

**Dependencies:** Checkpoint A

**Files likely touched:**

- `vta/tests/python/unittest/test_byoc_runtime.py`

**Estimated scope:** Extra small (1 file)

## Task 4: Lock host fallback and runtime failures

**Description:** Verify the non-constant-weight near miss builds and executes as
host-only Relay without invoking VTA codegen, and add stable diagnostics for
missing FSIM/device registration or missing reloaded symbols when those states
can be induced without changing public APIs or depending on test order.

**Acceptance criteria:**

- [x] The near-miss graph executes correctly on LLVM and invokes no VTA
  compiler or `ext_dev` runtime path.
- [x] Missing runtime prerequisites fail with a diagnostic naming the required
  FSIM setup rather than being skipped.
- [x] Missing expected symbols or invalid loaded artifacts fail at the artifact
  boundary with the symbol/stage identified.

**Verification:**

- [x] Fallback and failure tests pass in isolated processes where global
  registry state could otherwise leak.
- [x] No production assertion, silent fallback, or test skip is introduced.

**Dependencies:** Task 3

**Files likely touched:**

- `vta/tests/python/unittest/test_byoc_runtime.py`
- `vta/python/vta/relay/backend.py` only if a production artifact diagnostic is
  missing

**Estimated scope:** Small (1-2 files)

## Checkpoint B: Runtime contract complete

- [x] Tasks 3-4 acceptance criteria pass.
- [x] Approved graphs execute exactly; unsupported Relay remains host-only.
- [x] Setup and artifact failures identify the failing lifecycle boundary.
- [x] No capability, ABI, executor, target, or public API expansion occurred.
- [x] Human review approves numerical and fallback coverage.

## Task 5: Integrate the runtime regression gate

**Description:** Add the BYOC runtime test to the canonical FSIM test command
if it can run reliably under the existing default environment, document the
verified public lifecycle, and run the complete regression, compilation,
cleanliness, review, and simplification gates.

**Acceptance criteria:**

- [x] `./scripts/test_vta_fsim.sh` exercises the BYOC numerical runtime path
  without changing existing options or excluding existing tests.
- [x] Runtime documentation describes the current public workflow and does not
  expose internal lowering/codegen helpers.
- [x] No unrelated VTA runtime, scheduling, graphpack, dependency, or upstream
  TVM change is introduced.

**Verification:**

- [x] Contract, partition, lowering, codegen, and runtime tests pass together
  without skips.
- [x] Python compilation, `./scripts/test_vta_fsim.sh`, diff checks, and TVM
  cleanliness pass.
- [x] Code review and simplification checks find no unresolved required issue.

**Dependencies:** Checkpoint B

**Files likely touched:**

- `scripts/test_vta_fsim.sh`
- `vta/tests/python/unittest/test_byoc_runtime.py`
- Runtime documentation only if the public lifecycle is not fully covered by
  the approved specification/docstrings

**Estimated scope:** Medium (2-3 files)

## Checkpoint C: Ready for graphpack retirement

- [x] Tasks 1-5 acceptance criteria pass.
- [x] Project Definition of Done correctness, quality, integration, and
  documentation sections pass for runtime integration.
- [x] No tests are skipped, weakened, or deleted.
- [x] The pinned TVM checkout remains clean and no new runtime format,
  dependency, public API, or graphpack coupling exists.
- [ ] Human review approves the module before `vta-graphpack-retirement` begins.
