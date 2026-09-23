# Tasks: Fix TSIM Unknown-Instruction Blocking

## Common constraints

- Initiative: `20260923-fix-tsim-unknown-instruction`
- Base commit map at approval: root `d21c13079b1f2bc4c40580c2ad32ff5527e4221e`, TVM
  `9f2472d8637a4aa1f2f0c0ef2595dc8043bf3aca`, VTA
  `1612eb31bc7ac49d20130e0410e21991624a7339`
- Shared config: `vta/config/vta_64mac.json`
- Backend: `VTA_BACKEND=tsim`; no `TARGET`, old `--target`, or `VTA_PLATFORM`
- Every implementation behavior change requires a regression test before it is considered done.
- Do not modify benchmark model, Relay partition, topology, samples, or accuracy assertions.

## Checkpoint 1 — Instruction decode correctness

Fresh Default boundary. Owns the Chisel decoder and its direct tests.

### Tasks

1. Reproduce the current failure or isolate it with a minimal instruction vector containing
   non-zero legal fields; capture the exact decode/unknown behavior.
2. Add RED tests for all legal dispatch classes: input load, weight load, uop load, accumulator
   load, store output, GEMM, finish, and supported ALU operations. Include non-zero fields in
   each instruction family.
3. Add RED tests for unsupported opcode/subtype encodings and assert that they remain invalid.
4. Implement the smallest field-aware `FetchDecode` fix. Preserve the full instruction on all
   queue outputs and keep `Fetch64Bit`/`FetchWideVME` on the same decoder contract.
5. Run the focused Chisel tests and relevant compile/lint checks. Commit implementation and tests
   separately where the repository workflow permits, then report commit OIDs and evidence.

### Acceptance

- New decode tests pass.
- Legal non-zero-field instructions route to the expected queue.
- Invalid encodings remain rejected.
- No benchmark or config geometry files are changed.

### Owned paths

- `vta/hardware/chisel/src/main/scala/core/Decode.scala`
- `vta/hardware/chisel/src/main/scala/core/FetchVME64.scala`
- `vta/hardware/chisel/src/main/scala/core/FetchWideVME.scala`
- `vta/hardware/chisel/src/test/**` and directly related test fixtures

## Checkpoint 2 — TSIM artifact integration

Fresh Default boundary after Checkpoint 1 is committed. Owns rebuild and runtime artifact
validation; may fix only TSIM build/runtime integration issues exposed by the new decoder.

### Tasks

1. Rebuild TSIM/hardware artifacts with the maintained build command and the shared absolute
   `vta_64mac.json` path.
2. Verify generated geometry properties, `libvta_tsim`, and `libvta_hw` are present and reflect
   the shared geometry.
3. Run a fresh-process TSIM load/init check and `scripts/test_vta_tsim.sh --smoke-only`.
4. If the new hardware exposes a direct runtime integration defect, add a failing regression test,
   apply the minimal fix, rerun the focused gate, and commit it separately.
5. Report all command exit statuses and distinguish build/environment failures from functional
   TSIM failures.

### Acceptance

- TSIM artifacts are freshly generated from the approved config.
- TSIM library loading, initialization, and smoke tests pass.
- No old target compatibility or platform selector is reintroduced.

### Owned paths

- `vta/hardware/chisel/**` build-facing code/tests if required
- `scripts/build_vta_lib.sh` and `scripts/test_vta_tsim.sh` only if required
- `vta/CMakeLists.txt` and TSIM runtime files only if required

## Checkpoint 3 — MLPerf Tiny TSIM matrix

Fresh Default boundary after Checkpoint 2 is committed. Owns end-to-end validation and only
TSIM-specific fixes that remain within the approved scope.

### Tasks

1. Run the maintained TSIM focused/integration gate on fresh artifacts.
2. Run the six existing MLPerf Tiny TSIM runners without changing their model, partition,
   topology, samples, or assertions:
   - image classification v1
   - visual wake words v1
   - image classification v2
   - anomaly detection v1
   - streaming wakeword v1
   - keyword spotting v1
3. For each runner, record exact command, config/backend environment, host codegen variant,
   timeout/window budget if used, exit status, and key success/failure evidence.
4. If a failure is proven to be a TSIM hardware/runtime defect, create a regression test and
   route the minimal fix through a new implementation checkpoint; do not edit benchmark logic
   to bypass it.
5. Produce a matrix summary that marks all six as pass only when their real mixed execution and
   existing output assertions pass.

### Acceptance

- All six TSIM benchmark runs pass end to end with existing assertions.
- No FSIM-only or library-load-only result is counted as TSIM success.
- The final report is reproducible and includes failures if any remain.

### Owned paths

- Existing MLPerf runner/test entry points only for invocation and diagnosis
- TSIM-specific runtime/hardware paths if a minimal, tested fix is required
- Verification report/log location agreed by the project

## Final review handoff

After all checkpoint commits, Root dispatches a fresh Reviewer with the approved INTENT, capability
map, specs, this plan, full commit map, exact base-to-tip ranges, and the complete TSIM matrix
evidence. Reviewer must check both scope compliance and the claim that all six benchmarks truly
passed.
