# Tasks
Reviewed Specify: repository /Users/xdl/Projects/codex-tvm-vta OID 59e060b8aacdf8e683572c74903dd4ed49b29835, docs/initiatives/20261005-image-classification-cleanup/SPEC.md.

## Checkpoint 1: Complete application cleanup
Owner: fresh Default. Branch codex/20261005-image-classification-cleanup.
Owned paths: vta/apps/mlperf_tiny_benchmark/image_classification_v1/**; affected references only in vta/apps/common/tests/test_tuning_controller.py, vta/tests/python/unittest/**, vta documentation or other callers identified by search; primary scripts/test_vta_byoc.sh, scripts/README.md and other documented callers only when they reference this application. No policy or lifecycle artifact edits; no TVM source edits.

### Task 1: Consolidate and migrate application
- Implement exactly SPEC module mapping, deploy.py rename, thin tune.py CLI, empty package init, relative imports, scripts relocation, asset roots and shell roots.
- Migrate all affected production/test/doc references atomically, including common tuner tests, explicit retirement paths and runtime.py discovery. Preserve existing assertions and behavior. Document each module responsibility and CLI migration; document script options/prerequisites/outputs/side effects in scripts/README.md. Inspect duplicate names and merge only equivalent helpers with caller evidence; report any removed code and reason.
- Acceptance: new package/entry/script structure exists, old modules and run.py are absent; model, tuning, graph formats/algorithms/protocols and all existing Make targets/defaults/variables remain functional; CPU startup independent from VTA.
- Verification from root using project environment: set PYTHONPATH=$PWD/tvm/python:$PWD/vta/python VTA_CONFIG_FILE=$PWD/vta/config/vta_64mac.json VTA_BACKEND=fsim; `.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests`. Also run relevant common tuner/retirement/runtime-backend tests after inspecting their requirements. CLI --help on both entries; bash -n relocated script; read-only rg search for retired application references; real make deploy TARGET=llvm and minimal Make FSIM, TSIM and combined two-stage smoke using existing libs/workload=0/TRIAL_BATCH=1/MIN_SUCCESSFUL=1. Use a temporary output/log directory to preserve tune/. Record exact commands/results and prerequisite limitations. The punctuation following `tests` above is prose: the pytest invocation has ONE collection path, never repository `.`.
- Simplify, rerun affected verification, commit this task separately.

### Task 2: Add bounded clean
Depends on Task 1.
- Add phony Make clean routed to scripts/make_tasks.sh, removing application build and Python caches without needing TVM/VTA/config or model imports. Implement SPEC symlink constraints. Document custom output exclusion and persistent data preservation.
- Acceptance: root/internal/test caches and build removed; model/samples/tune and external symlink targets untouched; repeat succeeds; original targets retain behavior.
- Verification: meaningful tests for clean sentinels, missing runtime dependencies, symlink preservation, tuning/model/sample preservation and idempotence; rerun complete Make workflow tests and focused application suite if clean changes shared routing. bash -n and make -n original targets. Simplify/reverify/commit separately.

### Checkpoint verification
Both tasks GREEN, exact per-task OID maps recorded; final managed repositories clean. No uncommitted generated outputs. Return verification evidence and known runtime limitations for complete Implementation Review.
