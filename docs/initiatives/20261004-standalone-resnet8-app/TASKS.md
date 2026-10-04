# Tasks and checkpoints

Initiative `20261004-standalone-resnet8-app`; approved main Specify OID `463aa703d816dee95244164445290960f49504c2` (INTENT.md, SPEC.md). Branch `codex/20261004-standalone-resnet8-app`. Each task is one verified commit unit. Do not alter approved lifecycle files or unrelated application providers. Source ownership is assigned below; agents are not alone in the codebase and must preserve others' edits, using the supplied current OID maps rather than reverting unknown work.

## Shared execution contract

All commands from repository root; Python is .envs/tvm-vta-env/bin/python. For VTA checks set VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json", matching VTA_BACKEND, and PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" (retain apps path only while old shared-import behavior still exists during C1). Use pytest --import-mode=importlib. Tests marked actual runtime must run, not be skipped. Every task: test -> implement -> GREEN -> scoped simplify -> affected re-verification -> git-workflow commit. Record exact per-repository commit maps, affected paths and command outputs. Scope size is by coherent working outcome, not a strict file count. New helpers live locally with specific responsibilities. Generated build files ignored narrowly. Shell/path values must not be evaluated as code.

## Checkpoint C1: local application foundation

### T1 — Localize dependencies and unify configuration dispatch
- [ ] Copy/adapt necessary deployment_compute, schedule, deployment, measurement and search implementation into local explicitly named app modules; update runtime/tune imports to local modules. Preserve current public CLI until downstream tasks replace it. Retain common providers untouched for other apps.
- [ ] Use one local per-occurrence dispatch implementation for deployment and candidate measurement; preserve actual function-based compilation, repeated-workload isolation, fallback configs and cache clear behavior. Avoid unused controller/legacy migration infrastructure in local copy.
- [ ] Migrate app tuning/compute tests to local provider and add independence checks; retain existing tests' behavior coverage.
- Acceptance: application imports require no other apps directories; old app deployment/tuning still works; candidate/deployment configuration binding uses one authority.
- Verify: entire IC V1 existing pytest suite under FSIM, plus focused TSIM candidate/compute test in a separate TSIM process; actual default deployment and actual bounded one-layer candidate measurement. Inspect rg for common/other-app imports. Shared common tests relevant to untouched providers remain passing if caller adjustments touch them.
- Ownership: IC V1 Python modules and tests only. No vta/python compiler changes expected; material compiler contract changes escalate.
- Dependencies: none. Cohesive size: local-provider migration across source/tests.

C1 gate: local dependency isolation and retained behavior, tests/runtime verified, clean committed map.

## Checkpoint C2: deployment and actual computation export

### T2 — Single-target, single-input deployment and readable report
- [ ] Implement approved run.py CLI, delayed VTA initialization, float ResNet-8 validation for configurable model paths, same quantization/input policy across targets, only selected target build/run, classification output.
- [ ] Replace automatic matrix/reference comparison workflow and JSON user report with Markdown CPU/FSIM/TSIM report, actual per-layer/whole-cycle measurement and MAC arithmetic defined by SPEC; no all/host-codegen/evidence flags. Preserve bundle validation/rollback.
- [ ] Update relevant existing asset/model/runtime/graph/profile tests to new contract; preserve their correctness, provenance and negative coverage. Migrate scripts/test_vta_byoc.sh IC V1 invocation and test selection in same task so existing integration callers never remain broken; document changed script behavior in scripts/README.md. Old tuning code uses local preparation/capture helpers without automatic dual-model execution; migrate its invocation of changed runtime helpers so it still works until T4.
- Acceptance: c/llvm CPU runs without VTA_BACKEND, VTA c/llvm selects correct backend, no reference build in normal execution, one image accepted/rejected correctly, Markdown counters and N/A honest.
- Verify: full app fast tests plus real CPU c/llvm; real FSIM and TSIM vta,c/vta,llvm on one committed image with reports. Compare selected-target outputs in tests (test-owned reference only), validate reports' math/measurement protocol. Old tune seed/bounded measurement still passes as intermediate API. bash -n scripts/test_vta_byoc.sh and focused caller checks.
- Ownership: app run.py/runtime.py/model_pipeline.py/graph_artifacts.py, affected local helpers/tests/README; scripts/test_vta_byoc.sh, scripts/README.md.
- Dependencies: T1. Cohesive size: deploy API/runtime/test/caller migration.

### T3 — Export and recover actual deployment workloads
- [ ] Add --export-workloads PATH, optional and CPU-invalid, export original outlined functions/constants/real activations before optional schedule application, continue normal deployment.
- [ ] Local workloads contract serializes format/version, raw config+SHA, provenance/compatibility, per-layer original TVM IR, tensor bytes/metadata and portable config identity; validate loading and requery configuration spaces.
- [ ] Tests prove no input/model access needed after export, FSIM/TSIM and host portability under same geometry, malformed/oversize or inconsistent tensors fail before execution, model/config/IR/hash/version/space mismatches reject. Record integrity, not just JSON parsing.
- Acceptance: recovered function/constant/activation computes identical output; actual-layer inventory/order matches deploy graph; CPU rejects export before outputs; export works with default and supplied schedules.
- Verify: local workload unit/roundtrip tests; actual deployment export and recovered layer execution in FSIM/TSIM; deploy scheduled export with a bounded validated fixture generated by local measurement; full app tests.
- Ownership: app workload contract module, runtime/run, local capture helper, app tests/README.
- Dependencies: T2. Scope: one export/recovery capability.

C2 gate: four target flows, reports and workloads roundtrip pass; complete app suite GREEN, migrated callers valid, clean maps.

## Checkpoint C3: independent tuning stages and durable schedules

### T4 — FSIM candidates, TSIM selection and validated publication
- [ ] Replace tune.py with approved --workloads/--workload/--simulator/--timeout/FSIM search controls/--input-logs/--output-logs contract. No model import/reconstruction; removed args rejected. FSIM all successful candidates, TSIM reads those candidates only and emits minimum measured cycles per layer with deterministic ties.
- [ ] Extend local schedule contract for grouped native FSIM records and separate selected TSIM records; identity/provenance/hash validation; default/missing occurrence schedule replay remains valid. Measurement uses shared dispatch/compiler, real weights/activations and CPU function output check, bounded isolated processes and correct infrastructure failure behavior.
- [ ] Implement raw-config snapshot/SHA and per-layer merging/full replacement, stale best invalidation, file-set staging/validation/rollback and single-writer lock. Single merge validates all identities; full FSIM permits changed config and replaces old complete state. No-success prevents publication; exhaustion semantics per SPEC.
- [ ] Migrate old tuning tests to new stage contracts; preserve bounded search, candidate correctness/timeout/identity/selection coverage. Old seed/alignment/resume migration user APIs disappear together with their app-specific tests/callers, retaining equivalent internal alignment integration coverage.
- Acceptance: exported workload is sole compute input; FSIM -> TSIM -> deployment preserves selected identities and exact output; durable candidates/best cannot be confused; per-layer merge preserves others and invalidates replaced winners; failures preserve old files.
- Verify: full app unit tests including candidate grouping, timeout/infrastructure error, zero-success, corruption, single merge, full changed-config replacement, rollback/lock and removed flags. Real one-layer FSIM/TSIM/replay with 1 candidate quota; real all-occurrence roundtrip with 1 candidate quota. Compare selected config identity and graph-resident cycles with standalone TSIM strict <10% alignment check; do not put old flags back. Separate backends/processes. No model access in tuning roundtrip fixture.
- Ownership: app tune.py, local tuning/measurement/workload/schedule/publication modules, related tests/README. No common/other app provider modifications.
- Dependencies: T3. Cohesive size: stage API and persisted schedule lifecycle must ship together to remain GREEN.

C3 gate: both independent CLI stages, schedule replay and publication negatives validated; full app suite and real roundtrip GREEN, clean map.

## Checkpoint C4: Make workflow, persistent layout and final integration

### T5 — Make wrappers and safe persistent assets
- [ ] Implement deploy, tune-fsim, tune-tsim, tune with approved variables/defaults. CONFIG resolves config and per-config tune directory. Pair environment/backend separately per step. Full tune exports only if WORKLOADS absent, then FSIM/TSIM; stops on failure and never deploys optimized result automatically. Defaults model-relative, explicit values cwd-relative with robust spaces/metacharacter handling.
- [ ] Versioned config snapshot/checksum, fsim.tmp/sidecar and best.log/sidecar defaults; build-only intermediate files. Ensure ignore rules permit saved fsim.tmp. Preserve legacy evidence under documented legacy subdirectory, update relevant app asset expectations to moved paths; no deletion of other apps or providers.
- [ ] Update local README and scripts README with interfaces, commands, prerequisites, side effects and tracked output rules. Add Make orchestration tests using a harmless command-recording test double and real bounded smoke to validate defaults/environment and quoting, including make from app and make -C from repo.
- Acceptance: all four commands expose confirmed API, default/specified paths correct, full orchestration agrees with split stages, no auto Git commit or final deploy.
- Verify: Make command-recording negative/quoting/order tests, real deploy CPU/VTA plus bounded split/full tune. rg/git check-ignore verify persistent files aren't excluded; app suite. Generated validated saved schedules may be committed only if ownership/evidence is clear; no speculative placeholder schedules.
- Ownership: app Makefile, optional focused local Make launcher, README/.gitignore/tune legacy paths and related tests; scripts/README.md. Maintain local independence.
- Dependencies: T4. Scope: user wrapper plus artifact layout.

### T6 — Repository caller and cleanup integration, final gate
- [ ] Complete scripts/test_vta_byoc.sh new app test/CLI coverage without reducing other model tests. Update scripts/clean_mlperf_tiny.py and its tests only if needed for new build artifacts; saved tune files must be retained even untracked. If classification changes require common/artifacts.py edits, only cleanup ownership for IC V1 is allowed, preserving other apps' behavior and tests; no app dependency on common is reintroduced.
- [ ] Finalize independent test discovery/config, remove obsolete local imports/files/contracts only after new paths are verified. Check no common/other model import in app; preserve externally consumed providers. Document remaining external dependencies and intentional CLI breaks.
- [ ] Run required integrated checks once on final state, fix in-scope failures and record complete verification evidence. Do not silently lower gates or report unavailable runtime as passing.
- Acceptance: complete approved SPEC fulfilled, callers and cleanup respect new tracked output, no retired app flags/references, existing other apps remain covered.
- Verify: full app suite FSIM and separate TSIM integration; scripts/tests/test_clean_mlperf_tiny.py and common/tests/test_artifacts.py if touched; complete bash scripts/test_vta_byoc.sh with documented prerequisites, plus bash .agents/custom/scripts/test-role-workflow (policy files unchanged). Python compilation with project environment; read-only git diff --check for managed repositories; git-workflow status clean after attributable commits. No broadened repeated test runs after pass without new cause.
- Ownership: app code/tests/docs for final fixes, scripts/test_vta_byoc.sh/scripts/clean_mlperf_tiny.py/scripts/tests/test_clean_mlperf_tiny.py/scripts/README.md; narrowly necessary common/artifacts.py/common/tests/test_artifacts.py cleanup integration only.
- Dependencies: T5. Scope: final integration and end-state verification.

C4 gate: approved end state, complete evidence and clean committed repository maps. Return GREEN to Root for fresh Implementation Review, not an automatic merge.

## Checkpoint C5: resilient candidate search and accurate completion report

Approved amended Specify: main `782ca393b7e07658fdaddf6858a7264f72dea995`, explicitly approved by user. Original task history remains unchanged.

### T7 — Continue candidate failures and report actual search outcome
- [ ] Distinguish environment/library initialization errors from candidate build/run crashes using the existing measurement boundary; candidate compile/output/timeout/native-abort failures continue FSIM/TSIM, infrastructure and protocol failures stop. Reclaim every worker.
- [ ] Report per-occurrence attempted trials, successes, requested quota and termination reason. Trials include failed attempts. Exhaustion with at least one success completes normally and exports all successes even below quota. Zero-success fails publication and preserves old results. Failed candidates never enter the FSIM log.
- [ ] Update affected regression tests and app documentation, preserving successful log compatibility and previous worker protocol fixes. Do not weaken initialization-failure or zero-success checks.
- Acceptance: default user command completes both stages despite native candidate aborts, counts are accurate, and the saved best schedule replays with correct model output.
- Verify: meaningful regression tests for real isolated-worker crash continuation/reclamation, initialization failure propagation, quota and exhaustion counters and zero-success preservation; full app suite; actual `make tune WORKLOAD=0` from app cwd with default controls; actual TSIM deployment using resulting best.log. Do not test apps/deploy. Avoid unrelated broad repeated gates.
- Ownership: VTA repo apps/mlperf_tiny_benchmark/image_classification_v1 measurement.py/tune.py/tuning.py and directly affected tests/docs/saved validated tune outputs; main scripts/README.md only if documentation requires it. Root-owned lifecycle artifacts read-only. No VTA runtime/compiler or other app changes.
- Dependencies: prior C1–C4 and protocol/crash-classification fixes, current VTA `4e22eb6ef352a63bce6358fc049af4cfaa6db8ec`.
- Execution: one fresh Default, test/implement/GREEN/simplify/re-verify/git-workflow commit, return exact commit maps and commands/results for independent implementation review.
