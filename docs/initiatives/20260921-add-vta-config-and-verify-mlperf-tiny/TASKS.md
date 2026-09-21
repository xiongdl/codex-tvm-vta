# Tasks: VTA 64mac Configuration and MLPerf Tiny Verification

## Checkpoint 1: Configuration

### Task 1: Add and validate the complete `vta_64mac.json`

**Description:** Create `vta/config/vta_64mac.json` by preserving every field
from `vta/config/vta_config.json` and changing only the five approved geometry
values. Validate both JSON syntax and loading through the VTA configuration
loader.

**Acceptance criteria:**

- [ ] `vta/config/vta_64mac.json` exists with all fields from
      `vta/config/vta_config.json`.
- [ ] The five requested values are `3`, `12`, `13`, `14`, and `15` in the
      requested field order.
- [ ] Existing VTA configuration files are unchanged.

**Verification:**

- [ ] Parse the new JSON with the project Python environment.
- [ ] Load it through `vta.config.vta_config`.
- [ ] Compare parsed objects and assert the only differences are the five
      approved keys.

**Dependencies:** None.

**Files likely touched:**

- `vta/config/vta_64mac.json`

**Estimated scope:** XS (one file).

## Checkpoint 2: MLPerf Tiny Deployment Verification

### Task 2: Run all MLPerf Tiny benchmark verification paths

**Description:** Select `vta/config/vta_64mac.json` through `VTA_CONFIG_FILE`
and run all six checked-in MLPerf Tiny test suites. When the required built
libraries and tools exist, run each benchmark's documented HOST/FSIM path and
the TSIM path where its hardware library is available. Record commands,
pass/fail results, and explicit environment blockers in a verification report.

**Acceptance criteria:**

- [ ] Anomaly detection v1, image classification v1, image classification v2,
      keyword spotting v1, streaming wakeword v1, and visual wake words v1 are
      all covered.
- [ ] The focused test suite passes with the new configuration selected.
- [ ] Available deployment modes pass, and unavailable modes have exact
      prerequisite evidence recorded.

**Verification:**

- [ ] Run the repository Python/pytest commands from the approved spec.
- [ ] Run documented benchmark deployment commands using the new config when
      prerequisites are present.
- [ ] Inspect the final working tree for unrelated or generated changes.

**Dependencies:** Task 1.

**Files likely touched:**

- `docs/initiatives/20260921-add-vta-config-and-verify-mlperf-tiny/VERIFICATION.md`

**Estimated scope:** S (one report file, plus generated ignored artifacts).

## Checkpoint: Complete

- [ ] All task acceptance criteria are satisfied.
- [ ] Verification evidence is recorded.
- [ ] The complete committed change is ready for Reviewer inspection.
