# Tasks: VTA Geometry and Backend Decoupling

## Checkpoint 1: Backend Contract

### Task 1: Add canonical backend normalization and tests

**Description:** Define one boundary-level backend contract for `fsim` and
`tsim`, reject legacy `TARGET=sim`/`TARGET=tsim` fields with an actionable
migration error, reject unknown values, and prove backend choice does not
change the geometry ABI.

**Acceptance criteria:**

- [ ] `fsim` and `tsim` normalize to themselves.
- [ ] Legacy `TARGET=sim`/`TARGET=tsim` inputs fail with a migration error.
- [ ] Unknown values fail with one clear supported-values error.
- [ ] ABI/fingerprint inputs exclude backend selection.

**Verification:** Focused unit tests for normalization, errors, aliases, and
ABI equivalence.

**Files likely touched:** VTA environment/config module and its focused tests.

**Estimated scope:** M.

### Task 2: Convert `vta_64mac.json` to geometry-only schema

**Description:** Remove simulator-specific target coupling from the new config,
retain all geometry fields and requested values, and make the new loader reject
old simulator target fields clearly.

**Acceptance criteria:**

- [ ] The new config has no `TARGET=sim`/`TARGET=tsim` selector.
- [ ] All five requested values remain exact.
- [ ] Existing default/sample configs are unchanged unless explicitly migrated
      as part of this contract change.

**Verification:** Parse/load tests, field comparison, and legacy-config
rejection tests.

**Files likely touched:** `vta/config/vta_64mac.json` and config tests.

**Estimated scope:** S.

## Checkpoint 2: Backend Plumbing

### Task 3: Make build selection explicit and shared-config based

**Description:** Add `--config` and `--backend {fsim,tsim,all}` to the build
entry point, pass one config path to CMake and hardware generation, and remove
legacy target aliases.

**Acceptance criteria:**

- [ ] FSIM, TSIM, and all builds use the same selected config path.
- [ ] FSIM and TSIM output libraries remain distinct.
- [ ] The old `--target libvta_fsim` style is rejected with a clear migration
      message.

**Verification:** Shell/CMake contract tests and dry-run or configured build
checks using the project environment.

**Files likely touched:** `scripts/build_vta_lib.sh`, CMake/build tests.

**Estimated scope:** M.

### Task 4: Decouple benchmark runtime selection

**Description:** Make benchmark simulator sessions select backend explicitly and
validate backend/library registries rather than comparing simulator names to
config `TARGET` values. Keep model and partition code unchanged.

**Acceptance criteria:**

- [ ] FSIM uses `libvta_fsim` and FSIM registries.
- [ ] TSIM uses `libvta_tsim/libvta_hw` and TSIM registries.
- [ ] Backend mismatch errors identify the selected backend and required
      library.
- [ ] No benchmark model/partition source changes.

**Verification:** Focused runtime tests for both backends and legacy rejection.

**Files likely touched:** shared VTA runtime/config module and benchmark
runtime adapters/tests; no model or partition implementation files.

**Estimated scope:** M.

## Checkpoint 3: Verification and Documentation

### Task 5: Run backend and MLPerf Tiny verification

**Description:** Rebuild FSIM/TSIM artifacts from one geometry config where the
toolchain exists, run all six MLPerf Tiny suites/modes, and record exact
results and blockers without changing benchmark/partition logic.

**Acceptance criteria:**

- [ ] FSIM results are recorded for all six benchmarks.
- [ ] TSIM is run when its JDK/Verilator/hardware artifacts exist, otherwise
      the blocker is explicit.
- [ ] No topology assertion is weakened to hide a geometry incompatibility.

**Verification:** Project test scripts, focused pytest suites, and documented
benchmark commands with `VTA_BACKEND` and the selected config.

**Files likely touched:** `VERIFICATION.md` only, plus ignored build output.

**Estimated scope:** S.

### Task 6: Update backend documentation and maintained script contracts

**Description:** Document `VTA_BACKEND`, canonical `fsim` naming, shared config
selection, removal of legacy target names, and the deferred FPGA backend
migration.

**Acceptance criteria:**

- [ ] `scripts/README.md` documents new flags, prerequisites, outputs, and
      side effects.
- [ ] Relevant benchmark/config READMEs use `fsim`/`tsim` consistently.
- [ ] Legacy aliases and FPGA deferral are documented.

**Verification:** Documentation command examples are syntactically checked;
repository retired-reference checks pass.

**Files likely touched:** `scripts/README.md`, `vta/config/README.md`, and
relevant benchmark READMEs.

**Estimated scope:** M.

## Checkpoint: Complete

- [ ] All task acceptance criteria are satisfied.
- [ ] Benchmark/partition implementations are unchanged.
- [ ] Verification evidence and migration documentation are committed.
- [ ] The complete range is ready for Reviewer re-review.
