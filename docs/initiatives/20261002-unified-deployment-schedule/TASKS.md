# Tasks
Initiative: 20261002-unified-deployment-schedule
Branch: codex/20261002-unified-deployment-schedule
Approval pending. All tasks inherit PLAN.md, approved specs and repository policies.

## Execution contract
One fresh Default per checkpoint, strictly sequential. Each task is separately implemented, verified and committed through git-workflow. Defaults own listed paths and needed tests inside their delegated module, not Root-owned intent/spec/plan/task decisions. Do not revert others' changes. No delegation by Default. Each task is Small/Medium (at most five listed files); additional integration files require a separate task-sized attributable commit within the same responsibility, or escalation if approved scope changes.
T32 evidence files are explicitly delegated output paths, not immutable design decisions.

Verification setup from root:
```bash
export VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json"
export PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps"
```
Use VTA_BACKEND=fsim or tsim on every project execution; all Python commands use ./.envs/tvm-vta-env/bin/python. Use pytest -q --import-mode=importlib with listed test paths. Add model directory to PYTHONPATH only as needed for its transitional imports. Build scripts are used only if source/ABI changes require a rebuild, following scripts/README.md. Every task ends with verified commit and recorded per-repository OIDs.

## Checkpoint C1: T1, T2
Fresh Default owns exactly these tasks, in order.

### [ ] T1: Capture actual IC V2 deployment computation
- Dependencies: None.
- Acceptance: Expose ordered real layer identities, normal-default compute and config space without reconstructing fusion arithmetic; preserve default VTA ABI/packing/constants.
- Verification: Shared capture tests plus IC V2 default FSIM reference comparisons; inspect captured shapes/constants against real outlined functions.
- Files owned: `vta/apps/common/__init__.py`, `vta/apps/common/deployment_compute.py`, `vta/apps/common/tests/test_deployment_compute.py`, `vta/python/vta/relay/transform.py`.
- Scope: Medium.

### [ ] T2: Measure an IC V2 candidate through actual lowering
- Dependencies: T1.
- Acceptance: Compile a candidate from the actual layer compute; two valid configs demonstrably select different config identities; isolate caches and workers.
- Verification: Real activation layer output comparison on FSIM and one-call TSIM cycle measurement, including invalid candidate and exception/cache cases.
- Files owned: `vta/apps/common/measurement.py`, `vta/apps/common/tests/test_deployment_compute_tsim.py`, `vta/apps/common/tests/test_measurement.py`.
- Scope: Medium.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C2: T3, T4
Fresh Default owns exactly these tasks, in order.

### [ ] T3: Export and load one schedule snapshot
- Dependencies: T2.
- Acceptance: Atomic log/same-stem metadata pair supports unmeasured/measured candidates, partial/complete coverage, exact model/geometry/compute binding.
- Verification: pytest shared artifact tests: no-input/none, partial, repeats, duplicates, missing/swapped/tampered records and invalid configs.
- Files owned: `vta/apps/common/schedule.py`, `vta/apps/common/tests/test_schedule_artifacts.py`.
- Scope: Small.

### [ ] T4: Apply snapshots through the IC V2 runtime
- Dependencies: T3.
- Acceptance: One --schedule interface; no-input/none equivalent; missing occurrences default explicitly; old dual log CLI removed; application uses actual shared lowering.
- Verification: IC V2 default, single-occurrence partial and complete snapshots on FSIM, representative TSIM; invalid identity fails before execution.
- Files owned: `vta/apps/common/deployment.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/runtime.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_host_deployment.py`.
- Scope: Medium.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C3: T5, T6, T7, T8
Fresh Default owns exactly these tasks, in order.

### [ ] T5: Unify IC V2 deployment evidence
- Dependencies: T4.
- Acceptance: Move former deployment command responsibilities into shared runtime; add report/evidence flags; remove second deployment command; preserve strict threshold and ten outputs.
- Verification: IC V2 TSIM evidence test: one performance sample, all ten correctness samples, graph-resident counters/protocol and threshold failure cases.
- Files owned: `vta/apps/common/deployment.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/runtime.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/deployment.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_deployment_profile.py`.
- Scope: Medium.

### [ ] T6: Provide actual-compute search and resume
- Dependencies: T5.
- Acceptance: Single tune.py uses actual-compute tasks; retain search/quota/timeouts and seed report gate; ledger/resume identities and failures are explicit.
- Verification: Bounded seed/search fixture and representative real run; resume matching succeeds and mismatched identities/options fail.
- Files owned: `vta/apps/common/tuning.py`, `vta/apps/common/measurement.py`, `vta/apps/common/tests/test_tuning.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_two_stage_tuning.py`.
- Scope: Medium.

### [ ] T7: Export IC V2 candidate and best snapshots
- Dependencies: T6.
- Acceptance: Implement concrete candidate/best export options; selected failures never claim success; both exports load through run.py; no complete-only restriction.
- Verification: Export a single-layer ledger candidate and best snapshot, execute each through run.py, compare provenance/coverage and validate malformed requests.
- Files owned: `vta/apps/common/tuning.py`, `vta/apps/common/schedule.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_two_stage_tuning.py`.
- Scope: Medium.

### [ ] T8: Retire IC V2 duplicate tuning implementation
- Dependencies: T7.
- Acceptance: Remove obsolete executable/reconstructed computation implementation after dependent tests move to shared equivalents; preserve saved tune artifacts.
- Verification: Reference audit plus IC V2/common tests and full IC V2 bounded seed→report→search→export→run integration.
- Files owned: `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/tune.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/artifacts.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/measurement.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/search.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/fused_tasks.py`.
- Scope: Medium.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C4: T9, T10, T11
Fresh Default owns exactly these tasks, in order.

### [ ] T9: Migrate image_classification_v1 deployment
- Dependencies: T8.
- Acceptance: Default/partial/complete snapshots use one runtime and --schedule interface; report/evidence flags retain model-specific samples, HOST reference checks and cycle gates; remove second deployment command.
- Verification: Run model default/partial/complete FSIM cases and representative TSIM profile/evidence cases; assert selected config identities and explicit default coverage.
- Files owned: `vta/apps/mlperf_tiny_benchmark/image_classification_v1/runtime.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/deployment.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_deployment_profile.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tsim_deployment.py`.
- Scope: Medium.

### [ ] T10: Migrate image_classification_v1 tuning
- Dependencies: T9.
- Acceptance: One model tune.py delegates actual-compute search, seed/report gate, resume and candidate/best export to common providers; remove duplicate tuning entry.
- Verification: Bounded real seed and matching unified seed deployment, bounded search/resume; export and execute a partial candidate and selected snapshot.
- Files owned: `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/tune.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_two_stage_tuning.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py`.
- Scope: Medium.

### [ ] T11: Remove image_classification_v1 shadow tuning helpers
- Dependencies: T10.
- Acceptance: Remove unused model-local helpers/shadow arithmetic, adapting remaining tests to retained contract coverage; saved artifacts remain intact.
- Verification: Model/common focused tests and reference audit for removed imports; checkpoint proves end-to-end bounded tuning/deployment.
- Files owned: `vta/apps/mlperf_tiny_benchmark/image_classification_v1/fused_tasks.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/artifacts.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/measurement.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/search.py`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py`.
- Scope: Medium.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C5: T12, T13, T14
Fresh Default owns exactly these tasks, in order.

### [ ] T12: Migrate anomaly_detection_v1 deployment
- Dependencies: T11.
- Acceptance: Default/partial/complete snapshots use one runtime and --schedule interface; report/evidence flags retain model-specific samples, HOST reference checks and cycle gates; remove second deployment command.
- Verification: Run model default/partial/complete FSIM cases and representative TSIM profile/evidence cases; assert selected config identities and explicit default coverage.
- Files owned: `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/runtime.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/run.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune/deployment.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_deployment_profile.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_tsim_deployment.py`.
- Scope: Medium.

### [ ] T13: Migrate anomaly_detection_v1 tuning
- Dependencies: T12.
- Acceptance: One model tune.py delegates actual-compute search, seed/report gate, resume and candidate/best export to common providers; remove duplicate tuning entry.
- Verification: Bounded real seed and matching unified seed deployment, bounded search/resume; export and execute a partial candidate and selected snapshot.
- Files owned: `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tune/tune.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_two_stage_tuning.py`.
- Scope: Medium.

### [ ] T14: Remove anomaly_detection_v1 shadow tuning helpers
- Dependencies: T13.
- Acceptance: Remove unused model-local helpers/shadow arithmetic, adapting remaining tests to retained contract coverage; saved artifacts remain intact.
- Verification: Model/common focused tests and reference audit for removed imports; checkpoint proves end-to-end bounded tuning/deployment.
- Files owned: `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_two_stage_tuning.py`, `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/tests/test_model_pipeline.py`.
- Scope: Small.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C6: T15, T16, T17
Fresh Default owns exactly these tasks, in order.

### [ ] T15: Migrate keyword_spotting_v1 deployment
- Dependencies: T14.
- Acceptance: Default/partial/complete snapshots use one runtime and --schedule interface; report/evidence flags retain model-specific samples, HOST reference checks and cycle gates; remove second deployment command.
- Verification: Run model default/partial/complete FSIM cases and representative TSIM profile/evidence cases; assert selected config identities and explicit default coverage.
- Files owned: `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/runtime.py`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tune/deployment.py`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_deployment_profile.py`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_tsim_deployment.py`.
- Scope: Medium.

### [ ] T16: Migrate keyword_spotting_v1 tuning
- Dependencies: T15.
- Acceptance: One model tune.py delegates actual-compute search, seed/report gate, resume and candidate/best export to common providers; remove duplicate tuning entry.
- Verification: Bounded real seed and matching unified seed deployment, bounded search/resume; export and execute a partial candidate and selected snapshot.
- Files owned: `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tune.py`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tune/tune.py`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_two_stage_tuning.py`.
- Scope: Medium.

### [ ] T17: Remove keyword_spotting_v1 shadow tuning helpers
- Dependencies: T16.
- Acceptance: Remove unused model-local helpers/shadow arithmetic, adapting remaining tests to retained contract coverage; saved artifacts remain intact.
- Verification: Model/common focused tests and reference audit for removed imports; checkpoint proves end-to-end bounded tuning/deployment.
- Files owned: `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_two_stage_tuning.py`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/tests/test_model_pipeline.py`.
- Scope: Small.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C7: T18, T19, T20
Fresh Default owns exactly these tasks, in order.

### [ ] T18: Migrate streaming_wakeword_v1 deployment
- Dependencies: T17.
- Acceptance: Default/partial/complete snapshots use one runtime and --schedule interface; report/evidence flags retain model-specific samples, HOST reference checks and cycle gates; remove second deployment command.
- Verification: Run model default/partial/complete FSIM cases and representative TSIM profile/evidence cases; assert selected config identities and explicit default coverage.
- Files owned: `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/runtime.py`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/run.py`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tune/deployment.py`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_deployment_profile.py`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_tsim_deployment.py`.
- Scope: Medium.

### [ ] T19: Migrate streaming_wakeword_v1 tuning
- Dependencies: T18.
- Acceptance: One model tune.py delegates actual-compute search, seed/report gate, resume and candidate/best export to common providers; remove duplicate tuning entry.
- Verification: Bounded real seed and matching unified seed deployment, bounded search/resume; export and execute a partial candidate and selected snapshot.
- Files owned: `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tune.py`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tune/tune.py`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_two_stage_tuning.py`.
- Scope: Medium.

### [ ] T20: Remove streaming_wakeword_v1 shadow tuning helpers
- Dependencies: T19.
- Acceptance: Remove unused model-local helpers/shadow arithmetic, adapting remaining tests to retained contract coverage; saved artifacts remain intact.
- Verification: Model/common focused tests and reference audit for removed imports; checkpoint proves end-to-end bounded tuning/deployment.
- Files owned: `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_two_stage_tuning.py`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/tests/test_model_pipeline.py`.
- Scope: Small.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C8: T21, T22, T23
Fresh Default owns exactly these tasks, in order.

### [ ] T21: Migrate visual_wake_words_v1 deployment
- Dependencies: T20.
- Acceptance: Default/partial/complete snapshots use one runtime and --schedule interface; report/evidence flags retain model-specific samples, HOST reference checks and cycle gates; remove second deployment command.
- Verification: Run model default/partial/complete FSIM cases and representative TSIM profile/evidence cases; assert selected config identities and explicit default coverage.
- Files owned: `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/runtime.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/deployment.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_deployment_profile.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py`.
- Scope: Medium.

### [ ] T22: Migrate visual_wake_words_v1 tuning
- Dependencies: T21.
- Acceptance: One model tune.py delegates actual-compute search, seed/report gate, resume and candidate/best export to common providers; remove duplicate tuning entry.
- Verification: Bounded real seed and matching unified seed deployment, bounded search/resume; export and execute a partial candidate and selected snapshot.
- Files owned: `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tune/tune.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_two_stage_tuning.py`.
- Scope: Medium.

### [ ] T23: Remove visual_wake_words_v1 shadow tuning helpers
- Dependencies: T22.
- Acceptance: Remove unused model-local helpers/shadow arithmetic, adapting remaining tests to retained contract coverage; saved artifacts remain intact.
- Verification: Model/common focused tests and reference audit for removed imports; checkpoint proves end-to-end bounded tuning/deployment.
- Files owned: `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_two_stage_tuning.py`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_model_pipeline.py`.
- Scope: Small.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C9: T24, T25, T26
Fresh Default owns exactly these tasks, in order.

### [ ] T24: Relocate needed shared measurement/controller helpers
- Dependencies: T23.
- Acceptance: All used common infrastructure lives in apps/common; MLPerf registry remains model-aware; no surviving _load_legacy import dependency.
- Verification: Common/controller/evidence tests and complete reference audit; all six bounded adapter contracts still pass.
- Files owned: `vta/apps/common/measurement.py`, `vta/apps/common/tuning.py`, `vta/apps/common/deployment.py`, `vta/apps/mlperf_tiny_benchmark/tuning_controller.py`, `vta/apps/mlperf_tiny_benchmark/deployment_evidence.py`.
- Scope: Medium.

### [ ] T25: Remove generic operator tuning and isolated-cost reporting
- Dependencies: T24.
- Acceptance: Retire generic CLI, handwritten shared fusion tasks and generic isolated-cost reporting; retain deployment-evidence MAC calculator in scripts; replace meaningful migrated test coverage.
- Verification: Static import/CLI reference audit and common/all-model integration tests; calculator continues to accept new deployment reports.
- Files owned: `vta/apps/mlperf_tiny_benchmark/autotvm_tuner.py`, `vta/apps/mlperf_tiny_benchmark/fused_tasks.py`, `vta/apps/mlperf_tiny_benchmark/mac_utilization.py`, `vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py`, `vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py`.
- Scope: Medium.

### [ ] T26: Validate historical artifact migration
- Dependencies: T25.
- Acceptance: Compatible old full-fusion artifacts convert only with real compute identity/config validation; incompatible records give precise error; no fabricated new measurements.
- Verification: Tests over representative committed manifests/native records, tampered entries and missing protocol; calculator schema interoperability.
- Files owned: `vta/apps/common/schedule.py`, `vta/apps/common/tests/test_schedule_migration.py`, `scripts/mac_utilization.py`, `scripts/tests/test_mac_utilization.py`.
- Scope: Medium.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C10: T27, T28
Fresh Default owns exactly these tasks, in order.

### [ ] T27: Classify generated application artifacts
- Dependencies: T26.
- Acceptance: Inventory explicit cache/search-state ownership for shared and six model build dirs; unknown files retained; simplify ignores while retaining all committed evidence.
- Verification: Fixture inventory and git read-only tracked/ignored comparison; no historical assets/results removed or unexpectedly tracked.
- Files owned: `vta/apps/common/artifacts.py`, `vta/apps/common/tests/test_artifacts.py`, `vta/.gitignore`.
- Scope: Medium.

### [ ] T28: Implement scoped cleanup wrapper
- Dependencies: T27.
- Acceptance: Explicit category/model filters, dry-run paths/bytes, preservation of tracked/saved files and symlink escape rejection.
- Verification: Fixture tests for all categories/models, absent dirs, tracked files, symlinks and dry-run immutability; never clean current user artifacts.
- Files owned: `scripts/clean_mlperf_tiny.py`, `scripts/tests/test_clean_mlperf_tiny.py`, `vta/apps/common/artifacts.py`.
- Scope: Medium.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Checkpoint C11: T29, T30, T31, T32
Fresh Default owns exactly these tasks, in order.

### [ ] T29: Document unified commands
- Dependencies: T28.
- Acceptance: Document default/partial/candidate/best, auto metadata, provenance/migration, search/resume and cleanup; remove generic/dual-deployment instructions.
- Verification: Check documented --help contracts and runnable command prerequisites; reference audit.
- Files owned: `scripts/README.md`, `vta/apps/mlperf_tiny_benchmark/README.md`, `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md`, `vta/apps/mlperf_tiny_benchmark/image_classification_v2/README.md`.
- Scope: Medium.

### [ ] T30: Document remaining model workflows
- Dependencies: T29.
- Acceptance: All four model READMEs use unique run.py/tune.py and reflect preserved sample/evidence policies.
- Verification: Check each CLI --help and sample policy against docs; no remaining retired entry-point commands.
- Files owned: `vta/apps/mlperf_tiny_benchmark/anomaly_detection_v1/README.md`, `vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/README.md`, `vta/apps/mlperf_tiny_benchmark/streaming_wakeword_v1/README.md`, `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/README.md`.
- Scope: Medium.

### [ ] T31: Update maintained validation gate
- Dependencies: T30.
- Acceptance: Validation invokes retained providers and six unified workflows, preserving meaningful old correctness/protocol checks without skipped tests/suppression.
- Verification: Focused replacement tests, bash syntax, retired-reference audit, then full scripts/test_vta_byoc.sh.
- Files owned: `scripts/test_vta_byoc.sh`, `vta/apps/mlperf_tiny_benchmark/tests/test_deployment_evidence.py`, `vta/apps/mlperf_tiny_benchmark/tests/test_tuning_controller.py`, `vta/apps/mlperf_tiny_benchmark/tests/test_fused_tasks.py`.
- Scope: Medium.

### [ ] T32: Record six-model integration evidence
- Dependencies: T31.
- Acceptance: Committed report records actual defaults/partial/candidate/best behavior, config identities, output checks, cycles/units, migration and cleanup fixture verification; distinguish newly tested results from historical evidence.
- Verification: Read-only inspect final evidence and successful focused/full gates, git-workflow status clean after each commit; provide exact base-to-tip maps for Reviewer.
- Files owned: `docs/initiatives/20261002-unified-deployment-schedule/RESULTS.md`, `docs/initiatives/20261002-unified-deployment-schedule/VERIFICATION.md`.
- Scope: Small.

Checkpoint verification: relevant provider/model tests pass, documented feature path works, each task has its own commit map, and git-workflow status is clean. Return GREEN with commands/results, config/output evidence and risks before the next checkpoint.

## Final independent review
After C11, Reviewer checks committed implementation against all approved specs, the complete base-to-tip ranges and T32 evidence. Required findings trigger a fresh Default fix boundary, verification, commits and a fresh re-review; no additional routine human gate.
