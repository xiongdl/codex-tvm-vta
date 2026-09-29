# Tasks: IC V1 Single-Layer FSIM AutoTVM Tuning

Tasks are executed in checkpoint order. Each checkpoint is a fresh Default
execution boundary; tasks within a checkpoint are completed and committed
separately. These are execution boundaries, not additional human approval
gates.

## Checkpoint 1: IC V1 Single-Workload FSIM and TSIM Flow

### Task 1: Add the single-workload tuning command

**Description:** Add a V1-local CLI that selects one supported task by its
zero-based extraction index, uses AutoTVM random search with a local FSIM
runner, applies the 32-trial and 120-second defaults, then measures the chosen
schedule on TSIM. Report workload identity, MAC count, and TSIM cycles. Add
focused coverage and user documentation.

**Acceptance criteria:**

- [ ] Exactly one workload is selected per invocation; invalid indices fail
  before runner creation or output writes.
- [ ] Defaults are RandomTuner, local FSIM runner, 32 trials, and a 120-second
  per-measurement timeout.
- [ ] The TSIM cycle result is associated with the best selected FSIM schedule
  and is not derived from FSIM wall-clock cost.
- [ ] Output identifies the selected workload and MAC count; generated files
  go under ignored build output.
- [ ] Existing IC V1 untuned behavior and command remain usable.

**Verification:**

- Run the focused tests for workload selection, default values, error cases,
  and the FSIM-to-TSIM selected-config handoff.
- Run a bounded selected-workload command with matching built FSIM and TSIM
  libraries and inspect the reported workload, MAC count, cycles, and artifact
  paths.
- Review the diff for changes outside the owned paths.

**Dependencies:** None.

**Files likely touched:**

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py`
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`
- `scripts/README.md`

**Estimated scope:** Medium.

### Checkpoint 1 Exit Conditions

- Task 1 is verified and committed.
- The documented CLI accurately reflects the implemented backend environment,
  artifact, and output contracts.

## Checkpoint 2: Model-Independent MAC Utilization CLI

### Task 2: Add a generic MAC utilization calculator

**Description:** Add a model-independent script under `scripts/` that accepts
logical MAC count and TSIM cycle count, derives VTA peak MACs/cycle from a
geometry JSON file, calculates the utilization ratio and percentage, and
documents the maintained command.

**Acceptance criteria:**

- [ ] Valid inputs calculate `MACs / (TSIM cycles * peak MACs/cycle)` and print
  the ratio and percentage with units.
- [ ] The shared `vta_64mac.json` derives 64 MAC/cycle.
- [ ] Zero, negative, non-integral inputs, malformed JSON, and invalid geometry
  fail clearly before printing a result.
- [ ] The script has no model, AutoTVM log, or MLPerf Tiny application
  dependency.
- [ ] The script's inputs, options, prerequisites, outputs, side effects, and
  example are documented in `scripts/README.md`.

**Verification:**

- Run focused tests for the formula, standard geometry, invalid numbers, and
  malformed or incomplete config.
- Run a representative command using the project Python environment and check
  all reported values and units.
- Inspect imports and documentation for model independence.

**Dependencies:** Checkpoint 1.

**Files likely touched:**

- `scripts/mac_utilization.py`
- `scripts/tests/test_mac_utilization.py`
- `scripts/README.md`

**Estimated scope:** Small to medium.

### Checkpoint 2 Exit Conditions

- Task 2 is verified and committed.
- Both capabilities and their defaults are documented and the task branch is
  clean for review.
