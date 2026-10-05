# Tasks

Initiative `20261005-align-mlperf-tiny-benchmarks`.
Reviewed Specify: primary `286772e7269814c3f722076d94f61548c67ca305`, all six
SPEC-*.md and CAPABILITY_MAP.md; INTENT.md confirmed at the same repository OID.
Every task below must reach GREEN, receive one scoped simplification pass,
re-run affected verification and be committed separately through git-workflow.
No Default edits Root-owned lifecycle artifacts. Root owns checkpoint tracking.

## Common execution and verification contract
- Use `.envs/tvm-vta-env/bin/python`, initialized TVM/VTA and built libraries,
  `PYTHONPATH=$PWD/tvm/python:$PWD/vta/python`; VTA uses absolute
  `VTA_CONFIG_FILE=$PWD/vta/config/vta_64mac.json` and matching backend in fresh
  processes. Make sets backend itself. Never install or recreate environments.
- Before every checkpoint verify clean git-workflow status/assigned OID maps.
- Run the complete owned application's pytest suite with pinned Python after
  replacing obsolete tests by meaningful selected-deployment/workload/tuning
  coverage. Include model/asset, artifact integrity, CLI negative, Make
  quoting/order/clean, transaction/candidate isolation tests.
- Real runtime gate: one committed default input on CPU c/llvm and VTA c/llvm
  for both fsim/tsim where actual partitions exist; compare prepared CPU/VTA
  outputs, exact for int8. For zero coverage, verify truthful fallback on
  requested VTA targets and both backend selectors, zero reported coverage/N/A
  cycles, and export/schedule rejection without files, instead of false tuning.
- Real tuning gate where supported: default FSIM workload export, load it after
  source model/input is unavailable in an isolated temporary scenario, one
  occurrence FSIM with trial-batch=1/min-successful=1, TSIM those candidates,
  selected replay and strict under-10-percent same-layer cycle alignment.
  Verify both direct CLI and Make routing; full `make tune` stops after TSIM.
- Snapshot/log/model/config corruption and cross-model selection must reject;
  no-success and publication failure preserve valid prior files. Partial
  occurrence update preserves others and invalidates only its previous best.
- Verify CPU startup with backend/config removed and no VTA import; no runtime
  import from common, benchmark root, neighbor or reference app.
- Update active maintained callers for the migrated app in the same task;
  shell syntax/CLI checks and affected script tests pass, unrelated callers
  remain working. Do not remove still-used shared code until final checkpoint.
- Tests may create ignored build/cache outputs; commit only attributable source,
  docs, samples unchanged and persistent files required by repository contract.
- Run `git -C vta diff 26e9c86035b3ef8d6ff68bbbeb8ee7819a297401 --
  apps/mlperf_tiny_benchmark/image_classification_v1`: must be empty.
- Record commands/results, bounded runtime evidence, known zero-coverage limits
  and exact per-repository commit maps; end clean. No skipped required check is
  GREEN. No Default edits reviewed design to work around a blocker.

## Checkpoint 1: image_classification_v2

### Task 1: Complete standalone image_classification_v2 workflow

**Dependencies:** previous checkpoint must be GREEN; no app runtime dependency.
**Owned paths:** `vta/apps/mlperf_tiny_benchmark/image_classification_v2/` (all application
implementation/tests/README; model/sample/license bytes must remain unchanged),
this app's caller blocks in `scripts/test_vta_byoc.sh`, `scripts/README.md`
and benchmark index README; this app's consumer/parametrization/fixture blocks
in `vta/apps/common/tests/` (deployment_compute, measurement, schedule_artifacts,
schedule_migration, tuning_controller and any further affected shared tests),
benchmark-root model_registry.py/tests registration for this app; narrow needed
app output ignore/pytest config. Preserve other legacy app consumers.
**Specification:** `SPEC-image_classification_v2.md` in this initiative, exact reviewed OID above.
**Acceptance:**
- Complete local structure, CLI/Make, selected deployment, real workload-only
  tuning and report/artifact contract from specification; no forbidden imports.
- Retire old app runtime/run/model_pipeline/graph modules and old contract tests
  only after meaningful replacement coverage; migrate affected callers now.
  Remove this app from old registry/shared-test parameter sets and reroute its
  shared compute/schedule/measurement/tuning checks to app-owned equivalent
  coverage. If a shared test fixture currently uses this app as its example,
  select a still-legacy app with the same tested contract or retire that test
  only when its meaningful contract is already covered by migrated local tests.
  Do not retarget old-contract tests at the new incompatible implementation.
  Preserve remaining legacy contracts until their consumers migrate.
- README includes this app's independently executable manual acceptance set,
  prerequisites/options/expected results for every implemented feature,
  positive supported flow and truthful unsupported paths.
**Verification:** all common execution/verification gates above for this app;
run pinned pytest `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests`, documented
CLI/Make runtime/tuning commands with bounded occurrence, and affected caller
validation. Run the full remaining `vta/apps/common/tests` and benchmark-root
registry tests under pinned FSIM, plus relevant TSIM shared measurement checks,
after changes; every retained shared test must pass. Run script cleanup tests,
`bash -n scripts/test_vta_byoc.sh`, and check runner tests/commands contain no
removed app references. Model shape/dtype/topology/preprocessing tests pass.
**Scope:** one coherent full interface migration, larger than five files.
**Checkpoint GREEN:** task committed, exact evidence/map returned, clean state,
reference diff empty; unrelated apps and still-used shared consumers intact.

## Checkpoint 2: visual_wake_words_v1

### Task 2: Complete standalone visual_wake_words_v1 workflow

**Dependencies:** previous checkpoint must be GREEN; no app runtime dependency.
**Owned paths:** `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/` (all application
implementation/tests/README; model/sample/license bytes must remain unchanged),
this app's caller blocks in `scripts/test_vta_byoc.sh`, `scripts/README.md`
and benchmark index README; this app's consumer/parametrization/fixture blocks
in `vta/apps/common/tests/` (deployment_compute, measurement, schedule_artifacts,
schedule_migration, tuning_controller and any further affected shared tests),
benchmark-root model_registry.py/tests registration for this app; narrow needed
app output ignore/pytest config. Preserve other legacy app consumers.
**Specification:** `SPEC-visual_wake_words_v1.md` in this initiative, exact reviewed OID above.
**Acceptance:**
- Complete local structure, CLI/Make, selected deployment, real workload-only
  tuning and report/artifact contract from specification; no forbidden imports.
- Retire old app runtime/run/model_pipeline/graph modules and old contract tests
  only after meaningful replacement coverage; migrate affected callers now.
  Remove this app from old registry/shared-test parameter sets and reroute its
  shared compute/schedule/measurement/tuning checks to app-owned equivalent
  coverage. If a shared test fixture currently uses this app as its example,
  select a still-legacy app with the same tested contract or retire that test
  only when its meaningful contract is already covered by migrated local tests.
  Do not retarget old-contract tests at the new incompatible implementation.
  Preserve remaining legacy contracts until their consumers migrate.
- README includes this app's independently executable manual acceptance set,
  prerequisites/options/expected results for every implemented feature,
  positive supported flow and truthful unsupported paths.
**Verification:** all common execution/verification gates above for this app;
run pinned pytest `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests`, documented
CLI/Make runtime/tuning commands with bounded occurrence, and affected caller
validation. Run the full remaining `vta/apps/common/tests` and benchmark-root
registry tests under pinned FSIM, plus relevant TSIM shared measurement checks,
after changes; every retained shared test must pass. Run script cleanup tests,
`bash -n scripts/test_vta_byoc.sh`, and check runner tests/commands contain no
removed app references. Model shape/dtype/topology/preprocessing tests pass.
**Scope:** one coherent full interface migration, larger than five files.
**Checkpoint GREEN:** task committed, exact evidence/map returned, clean state,
reference diff empty; unrelated apps and still-used shared consumers intact.

## Checkpoint 3: keyword_spotting_v1

### Task 3: Complete standalone keyword_spotting_v1 workflow

**Dependencies:** previous checkpoint must be GREEN; no app runtime dependency.
**Owned paths:** `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/` (all application
implementation/tests/README; model/sample/license bytes must remain unchanged),
this app's caller blocks in `scripts/test_vta_byoc.sh`, `scripts/README.md`
and benchmark index README; this app's consumer/parametrization/fixture blocks
in `vta/apps/common/tests/` (deployment_compute, measurement, schedule_artifacts,
schedule_migration, tuning_controller and any further affected shared tests),
benchmark-root model_registry.py/tests registration for this app; narrow needed
app output ignore/pytest config. Preserve other legacy app consumers.
**Specification:** `SPEC-keyword_spotting_v1.md` in this initiative, exact reviewed OID above.
**Acceptance:**
- Complete local structure, CLI/Make, selected deployment, real workload-only
  tuning and report/artifact contract from specification; no forbidden imports.
- Retire old app runtime/run/model_pipeline/graph modules and old contract tests
  only after meaningful replacement coverage; migrate affected callers now.
  Remove this app from old registry/shared-test parameter sets and reroute its
  shared compute/schedule/measurement/tuning checks to app-owned equivalent
  coverage. If a shared test fixture currently uses this app as its example,
  select a still-legacy app with the same tested contract or retire that test
  only when its meaningful contract is already covered by migrated local tests.
  Do not retarget old-contract tests at the new incompatible implementation.
  Preserve remaining legacy contracts until their consumers migrate.
- README includes this app's independently executable manual acceptance set,
  prerequisites/options/expected results for every implemented feature,
  positive supported flow and truthful unsupported paths.
- Independently compare imported QNN and prepared CPU graph outputs exactly
  on all committed samples to prove arithmetic preservation. Keep fixed-point
  multipliers/per-axis shifts/zero points; remove non-equivalent old mutators.
  Derive partition count afterward; unsupported arithmetic stays on CPU.
**Verification:** all common execution/verification gates above for this app;
run pinned pytest `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests`, documented
CLI/Make runtime/tuning commands with bounded occurrence, and affected caller
validation. Run the full remaining `vta/apps/common/tests` and benchmark-root
registry tests under pinned FSIM, plus relevant TSIM shared measurement checks,
after changes; every retained shared test must pass. Run script cleanup tests,
`bash -n scripts/test_vta_byoc.sh`, and check runner tests/commands contain no
removed app references. Model shape/dtype/topology/preprocessing tests pass.
**Scope:** one coherent full interface migration, larger than five files.
**Checkpoint GREEN:** task committed, exact evidence/map returned, clean state,
reference diff empty; unrelated apps and still-used shared consumers intact.

## Checkpoint 4: anomaly_detection_v1

### Task 4: Complete standalone anomaly_detection_v1 workflow

**Dependencies:** previous checkpoint must be GREEN; no app runtime dependency.
**Owned paths:** `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/` (all application
implementation/tests/README; model/sample/license bytes must remain unchanged),
this app's caller blocks in `scripts/test_vta_byoc.sh`, `scripts/README.md`
and benchmark index README; this app's consumer/parametrization/fixture blocks
in `vta/apps/common/tests/` (deployment_compute, measurement, schedule_artifacts,
schedule_migration, tuning_controller and any further affected shared tests),
benchmark-root model_registry.py/tests registration for this app; narrow needed
app output ignore/pytest config. Preserve other legacy app consumers.
**Specification:** `SPEC-anomaly_detection_v1.md` in this initiative, exact reviewed OID above.
**Acceptance:**
- Complete local structure, CLI/Make, selected deployment, real workload-only
  tuning and report/artifact contract from specification; no forbidden imports.
- Retire old app runtime/run/model_pipeline/graph modules and old contract tests
  only after meaningful replacement coverage; migrate affected callers now.
  Remove this app from old registry/shared-test parameter sets and reroute its
  shared compute/schedule/measurement/tuning checks to app-owned equivalent
  coverage. If a shared test fixture currently uses this app as its example,
  select a still-legacy app with the same tested contract or retire that test
  only when its meaningful contract is already covered by migrated local tests.
  Do not retarget old-contract tests at the new incompatible implementation.
  Preserve remaining legacy contracts until their consumers migrate.
- README includes this app's independently executable manual acceptance set,
  prerequisites/options/expected results for every implemented feature,
  positive supported flow and truthful unsupported paths.
- Select exactly the first existing preprocessed feature vector from one WAV,
  report total available and one executed window plus reconstruction MSE;
  no threshold, batch windows or multi-sample application behavior.
**Verification:** all common execution/verification gates above for this app;
run pinned pytest `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests`, documented
CLI/Make runtime/tuning commands with bounded occurrence, and affected caller
validation. Run the full remaining `vta/apps/common/tests` and benchmark-root
registry tests under pinned FSIM, plus relevant TSIM shared measurement checks,
after changes; every retained shared test must pass. Run script cleanup tests,
`bash -n scripts/test_vta_byoc.sh`, and check runner tests/commands contain no
removed app references. Model shape/dtype/topology/preprocessing tests pass.
**Scope:** one coherent full interface migration, larger than five files.
**Checkpoint GREEN:** task committed, exact evidence/map returned, clean state,
reference diff empty; unrelated apps and still-used shared consumers intact.

## Checkpoint 5: streaming_wakeword_v1

### Task 5: Complete standalone streaming_wakeword_v1 workflow

**Dependencies:** previous checkpoint must be GREEN; no app runtime dependency.
**Owned paths:** `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/` (all application
implementation/tests/README; model/sample/license bytes must remain unchanged),
this app's caller blocks in `scripts/test_vta_byoc.sh`, `scripts/README.md`
and benchmark index README; this app's consumer/parametrization/fixture blocks
in `vta/apps/common/tests/` (deployment_compute, measurement, schedule_artifacts,
schedule_migration, tuning_controller and any further affected shared tests),
benchmark-root model_registry.py/tests registration for this app; narrow needed
app output ignore/pytest config. Preserve other legacy app consumers.
**Specification:** `SPEC-streaming_wakeword_v1.md` in this initiative, exact reviewed OID above.
**Acceptance:**
- Complete local structure, CLI/Make, selected deployment, real workload-only
  tuning and report/artifact contract from specification; no forbidden imports.
- Retire old app runtime/run/model_pipeline/graph modules and old contract tests
  only after meaningful replacement coverage; migrate affected callers now.
  Remove this app from old registry/shared-test parameter sets and reroute its
  shared compute/schedule/measurement/tuning checks to app-owned equivalent
  coverage. If a shared test fixture currently uses this app as its example,
  select a still-legacy app with the same tested contract or retire that test
  only when its meaningful contract is already covered by migrated local tests.
  Do not retarget old-contract tests at the new incompatible implementation.
  Preserve remaining legacy contracts until their consumers migrate.
- README includes this app's independently executable manual acceptance set,
  prerequisites/options/expected results for every implemented feature,
  positive supported flow and truthful unsupported paths.
- Independently compare imported QNN and prepared CPU graph outputs exactly
  on all committed samples to prove arithmetic preservation. Keep fixed-point
  multipliers/per-axis shifts/zero points; remove non-equivalent old mutators.
  Derive partition count afterward; unsupported arithmetic stays on CPU.
**Verification:** all common execution/verification gates above for this app;
run pinned pytest `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests`, documented
CLI/Make runtime/tuning commands with bounded occurrence, and affected caller
validation. Run the full remaining `vta/apps/common/tests` and benchmark-root
registry tests under pinned FSIM, plus relevant TSIM shared measurement checks,
after changes; every retained shared test must pass. Run script cleanup tests,
`bash -n scripts/test_vta_byoc.sh`, and check runner tests/commands contain no
removed app references. Model shape/dtype/topology/preprocessing tests pass.
**Scope:** one coherent full interface migration, larger than five files.
**Checkpoint GREEN:** task committed, exact evidence/map returned, clean state,
reference diff empty; unrelated apps and still-used shared consumers intact.

## Checkpoint 6: Integration and shared-code retirement

### Task 6: Remove obsolete shared code after consumer migration

**Dependencies:** Checkpoints 1–5 GREEN and committed.
**Owned paths:** all tracked `vta/apps/common/`; benchmark-root shared Python
files/root tests and needed pytest.ini, benchmark README; `scripts/test_vta_byoc.sh`,
`scripts/clean_mlperf_tiny.py`, `scripts/tests/test_clean_mlperf_tiny.py`,
`scripts/README.md`; narrow output ignore rules and focused migration contract
tests under `scripts/tests/`. All five app docs only for proven integration
corrections. Never modify reference app/assets/compiler/hardware/policy.
**Specification:** SPEC-integration.md at reviewed OID above.
**Acceptance:**
- Search all active runtime/test/script consumers before deletion; none relies
  on shared app code or obsolete interfaces after task. Retain benchmark index,
  configuration as needed, app dirs/assets/licenses/saved tune evidence.
- Maintained clean script owns its local safe inventory/removal; --model one
  of five or all, --dry-run. No relocated generic application common runtime.
  Preserve tracked/unknown/persistent data and external symlink targets.
- Updated maintained runner exercises retained core BYOC and local app contracts;
  docs index links five complete manual acceptance sets. Reference unchanged.
**Verification:** pinned pytest on scripts/tests including cleanup/migration;
all five app test suites with unique imports, updated
`VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" bash scripts/test_vta_byoc.sh --env-name tvm-vta-env` (the existing runner covers both backends). Functional/model normalization evidence and bounded tuning from
prior checkpoints remain valid unless content changed. Rerun affected real
checks for any corrections. Search retired import/caller paths, verify pinned
CPU startup and exact empty reference diff. Review git diff and final clean
status, return full evidence and exact commit maps.
**Checkpoint GREEN:** all replacements verified, no active shared dependency,
shared code absent, full migrated outcome follows and manual docs ready.
