# Specification: standalone ResNet-8 deployment and tuning

Initiative: `20261004-standalone-resnet8-app`. Baseline: INTENT.md, explicitly confirmed by user.

## Objective and scope

Deliver one cohesive model application: deployment owns model preparation and computation export; tuning consumes that exported computation and supplies schedules. Preserve external TVM/VTA libraries and geometry, but eliminate runtime/test imports from other vta/apps directories. Do not delete shared modules still consumed by other applications or change their interfaces. No INT8 input model support, other-app cleanup, automated merges, or new dependencies.

## Architecture and ownership

All application code and tests reside under vta/apps/mlperf_tiny_benchmark/image_classification_v1. Retain run.py, tune.py, model_pipeline.py, runtime.py, graph_artifacts.py. Place required computation capture, schedule serialization/dispatch, and candidate measurement/search code in explicitly named local modules; do not add generic managers or public extension APIs. Reuse existing implementations where applicable, without carrying legacy migration/controller functionality unused by the new flow.

Dependency direction: entrypoints -> local deployment or tuning functions -> local workload/schedule contracts -> existing VTA compiler. Deployment alone imports/prepares TFLite and captures actual activations; tuning must not import model_pipeline/runtime to reconstruct a model. Shared per-occurrence configuration dispatch has one owner and is used by both measurement and deployment. Existing vta/python/vta/relay/transform.py owns legalization and lowering; both paths compile original outlined Relay functions through that implementation. Local contract code owns validation and publication of files. Makefile owns environment/path translation and sequential orchestration, not computation or selection policy. No imports from common, other model directories, or benchmark registry/wrappers. No framework beyond local functions/data structures is needed.

CPU entrypoint startup must not require VTA_BACKEND or simulator libraries. Defer VTA imports/partition until the target includes VTA. Quantization and input preparation remain the same across targets. c/llvm are CPU codegen destinations, not new VTA partition implementations; vta,c and vta,llvm apply VTA partition first and CPU fallback afterward.

## Deployment CLI

Defaults are absolute model-relative paths: model/pretrainedResnet.tflite, samples/00-airplane.png, build/. Explicit relative paths use invocation cwd. Arguments:

| Argument | Contract |
|---|---|
| --model PATH | float ResNet-8 TFLite; validate supported topology/input/output rather than requiring one asset hash for custom paths |
| --input PATH | one PNG/JPEG, 32x32 RGB; convert to float32 NHWC [1,32,32,3], retain current pixel scale |
| --target | c, llvm, vta,c, vta,llvm; default vta,llvm |
| --simulator | fsim or tsim; default fsim; ignored for CPU |
| --schedule PATH | native records plus same-stem JSON; omitted uses defaults; ignored for CPU |
| --output-dir PATH | compiled graph/library/parameters/source manifests; default model build/ |
| --deployment-report PATH | optional UTF-8 Markdown |
| --export-workloads PATH | optional actual computation export, VTA only; CPU rejects before outputs |

Float quantization uses global_scale=8.0 and skip_conv_layers=[0]. Only selected target is compiled/run, with no automatic reference build. Print predicted CIFAR-10 class/index and raw output scores, explicitly not calibrated probability claims. Native library/graph bundles continue to validate hashes and required symbols. Direct VTA invocations must set matching VTA_BACKEND before importing VTA; run.py never assigns it. CPU ignores simulator/schedule, and never initializes a simulator.

## Workloads file v1

Single UTF-8 JSON object, format=resnet8-vta-workloads and version=1. It stores model SHA-256, quantization parameters, original input byte SHA-256 and decoded tensor description, config basename, raw config bytes in Base64 plus SHA-256, geometry identity, TVM/VTA compatibility information, and ordered workloads. Each workload stores unique nonnegative index, global symbol, serialized original typed Relay Function using tvm.ir.save_json, computation SHA-256, input/output tensor descriptions, activation tensor (dtype, shape, Base64 of contiguous bytes with explicit byte order), and portable configuration-space identity. Constants/weights remain in serialized Relay functions; do not duplicate them in tensor arrays. Store original partition functions before schedule application, not selected TIR. A JSON string can hold TVM serialized IR without assuming its internal schema.

Export real activations from the executed default-scheduled partitioned graph before applying an optional selected schedule; use the same prepared module and input, not model reimport. This may require an additional graph build/run when schedule supplied, but not an automatic pure CPU reference. Export does not stop normal deployment. Model/run output and workloads share source identity. Do not store selected backend or host codegen as computation compatibility requirements: this file is reusable for FSIM/TSIM and c/llvm under the same geometry. Requery configuration spaces through shared compiler lowering on load and check portable identities. Require compatible TVM serialization/version and VTA compute contract; reject mismatches with diagnostics before measurement. JSON/IR/tensor fields are validated before use; no pickle or code execution in file loading.

## Tuning CLI and semantics

--workloads PATH and --output-logs PATH required. --workload defaults -1; >=0 indexes the exported ordered VTA occurrences and must exist. --simulator defaults fsim. --timeout positive seconds, defaults 60 fsim/120 tsim. --trial-batch=100 and --min-successful=20 positive, FSIM only; explicitly passing them to TSIM rejects. TSIM requires --input-logs PATH; FSIM rejects that option. Removed flags fail argument parsing. Matching external VTA_BACKEND is required.

FSIM searches unique valid candidate configurations of selected occurrences, using existing random candidate enumeration where suitable. It tests real activation/weights through the original function and shared dispatch/lowering, comparing candidate output exactly with CPU evaluation of that function. Export ALL successful candidates, including configurations and measurement provenance, as native AutoTVM records in fsim.tmp (or requested path); same-stem .json carries occurrence/candidate groups and hashes. Stop at successful quota or space exhaustion. Exhaustion with at least one valid candidate per selected layer permits output and explicitly reports unmet quota; zero successes for any selected layer fails publication. No resume ledgers exposed; temporary execution state stays under build/ and is not a maintained user API.

TSIM validates FSIM native log and sidecar against workloads/geometry, measures each selected successful candidate with a single counted invocation after excluded warmup and bounded timeout. Recheck exact output, read positive cycle_count, choose minimum cycles per selected occurrence; deterministic tie-break by candidate configuration identity. Do not generate/search new configurations. Output best.log contains only selected configurations for each occurrence and TSIM measured provenance in same-stem JSON. If no candidate passes for any requested occurrence, fail publication. Per-candidate errors/timeouts are recorded in diagnostics while other candidates continue. Failure of environment/library initialization is infrastructure failure, not a failed candidate to silently ignore.

A candidate may contain multiple native records for one fusion; JSON groups those records as one candidate. Do not pass fsim.tmp with multiple candidates to deployment as an ambiguous selected schedule. Deployment accepts one selected candidate per covered occurrence, verifies model/quantization/compute/geometry/config space and record hashes, uses defaults for uncovered occurrences. Pure FSIM timings do not imply best-cycle claims. No seed/alignment report parameters. Keep code-level integration verification of per-layer deployment versus tuning measurements and same selected config identities.

## Persistent files and publication

Make defaults resolve tune/<config basename minus .json>/{config.json,config.sha256,fsim.tmp,fsim.json,best.log,best.json} under the model. config.json preserves exact original configuration bytes; config.sha256 contains their SHA-256 hex. Raw-byte differences fail reuse/merge, even if filenames match. Sidecars independently embed/validate configuration SHA, supporting explicitly located logs; default files additionally validate the sibling snapshot/checksum. This strict config validation is separate from backend-portable workload identity.

All model/config/input/computation identities must match before single-occurrence merge. Replace records for requested occurrence only, preserve others; full (-1) replaces all. Each FSIM update invalidates/removes best selections for replaced occurrences (others preserved) so stale winners cannot be replayed. If config identity differs, reject reuse and single-occurrence merging. Full FSIM tuning may replace the entire existing directory result set under the changed configuration: stage the new configuration snapshot/checksum and candidates together, invalidate all old best selections, then publish after validation. A subsequent TSIM step must match the newly published FSIM configuration. Failures preserve the previous validated set. For a fresh directory publish config snapshot/checksum with validated logs. Output helpers stage and validate the whole affected file set, then publish with exception rollback; detect inconsistent hashes after interrupted multi-file publication and refuse use. Guarantee old validated outputs on ordinary caught failures, not crash-proof filesystem transactions. No concurrent writers to one output set; serialize Make stages and reject conflicting writers using a local lock with diagnostic stale-lock handling, no automatic deletion of another process's lock.

Saved schedules/configs under tune/ are tracked deliverables, fsim.tmp is explicitly exempt from ignored-temp patterns and generated-file cleanup. Builds/workloads/debug intermediates stay ignored build/. Do not automatically commit generated schedules merely by running Make; implementation commits only attributable validated deliverables. Preserve historical tuning evidence under an explicitly documented legacy subdirectory; do not delete/represent legacy logs as current-format successes.

## Markdown reports

Include model/input/config hashes, target/backend/schedule coverage, predicted class and scores, per-layer device/operation/logical MACs, cycles, peak MAC/cycle, utilization, and whole-model measurement. Conv logical MACs derive from model operation extents; count multiply-accumulates once, do not count packing/padding work as logical MACs. Other non-MAC operations show zero logical MACs with utilization N/A. CPU/FSIM cycles and MAC utilization are N/A with explanation. TSIM report measures one sample, excludes warmup, resets counters per measured invocation. Per-layer reporting includes CPU fallback rows (cycle/utilization N/A); use graph-resident VTA node measurements. Peak=BATCH*BLOCK_IN*BLOCK_OUT. VTA row utilization=logical_MACs/(cycles*peak); whole-model VTA utilization uses VTA logical MAC sum divided by uninstrumented whole-model TSIM cycles*peak, clearly labels scope. Report layer-cycle sum and residual separately, never asserts sum equals whole-model cycles. No CPU reference comparison requirement. Do not claim official MLPerf performance.

## Makefile

Discover absolute repository/model roots from Makefile location. Use repository .envs/tvm-vta-env/bin/python; no downloads/build/environment creation. Set PYTHONPATH for TVM/VTA and local app, never apps/common. CONFIG defaults repo vta/config/vta_64mac.json; validate absolute resolved config. Preserve invocation cwd for explicit relative paths (including make -C semantics).

- deploy: MODEL INPUT TARGET SIMULATOR SCHEDULE OUTPUT_DIR REPORT EXPORT_WORKLOADS. Defaults as run.py. VTA_BACKEND set only for VTA target, matched to SIMULATOR.
- tune-fsim: required WORKLOADS, optional WORKLOAD=-1 TRIAL_BATCH=100 MIN_SUCCESSFUL=20 TIMEOUT=60 OUTPUT_LOGS (default config tune/fsim.tmp).
- tune-tsim: required WORKLOADS INPUT_LOGS, optional WORKLOAD=-1 TIMEOUT=120 OUTPUT_LOGS (default config tune/best.log).
- tune: MODEL INPUT WORKLOAD=-1 TRIAL_BATCH MIN_SUCCESSFUL FSIM_TIMEOUT=60 TSIM_TIMEOUT=120 OUTPUT_DIR (default model build/tune/) and optional WORKLOADS. Without WORKLOADS run deployment vta,llvm/fsim exporting OUTPUT_DIR/workloads.json, then FSIM, then TSIM. With WORKLOADS skip export. Persistent outputs default config tune directory; OUTPUT_DIR affects only intermediate build files. Stop on failed stage, no final optimized deployment.

Quote user paths robustly; no shell evaluation of values. Document examples including path spaces. CLI stderr gives concise invalid-argument/identity/environment diagnostics and nonzero exit; no false successful report. Model and input are not tune CLI arguments: workloads is authoritative.

## Verification, commands, style, and success

Use existing project pytest environment and actual existing simulator libraries; do not install dependencies. From repo root:

```sh
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" .envs/tvm-vta-env/bin/python -m pytest --import-mode=importlib vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests
make -C vta/apps/mlperf_tiny_benchmark/image_classification_v1 deploy TARGET=llvm
make -C vta/apps/mlperf_tiny_benchmark/image_classification_v1 deploy TARGET=c
make -C vta/apps/mlperf_tiny_benchmark/image_classification_v1 deploy TARGET=vta,llvm EXPORT_WORKLOADS=build/workloads.json
make -C vta/apps/mlperf_tiny_benchmark/image_classification_v1 tune-fsim WORKLOADS=build/workloads.json WORKLOAD=0 TRIAL_BATCH=1 MIN_SUCCESSFUL=1
make -C vta/apps/mlperf_tiny_benchmark/image_classification_v1 tune-tsim WORKLOADS=build/workloads.json INPUT_LOGS=tune/vta_64mac/fsim.tmp WORKLOAD=0
make -C vta/apps/mlperf_tiny_benchmark/image_classification_v1 deploy SIMULATOR=tsim SCHEDULE=tune/vta_64mac/best.log REPORT=build/deployment-report.md
```

Tests cover all CLI choices/defaults/removals, CPU startup without backend, custom paths, malformed model/image/JSON/tensors, version/config/model/compute/config-space mismatches, IR/activation roundtrip, native candidate grouping, FSIM-to-TSIM handoff, deterministic selection, timeout/zero-success errors, per-layer merge/stale-best invalidation, rollback and corrupted publication rejection, Markdown arithmetic and N/A, Make orchestration/environment quoting, direct local invocation without apps path. Actual end-to-end checks exercise c/llvm and both VTA host codegens, one-layer bounded FSIM/TSIM tuning and replay. A complete all-occurrence roundtrip is an integration gate, using minimal candidate counts rather than costly full search. Existing old-interface tests/callers in scripts/test_vta_byoc.sh and cleaner are migrated to new app contract without weakening checks for other apps. Scripts README and app README describe prerequisites, side effects, output semantics and intentional CLI breaks.

Follow current Python style: snake_case, pathlib, frozen dataclasses where useful, small functions. Example boundary: `def load_workloads(path, compiler_config):` returns validated occurrence data; configuration application is `with occurrence_config_context(layer, selected):` around normal lowering. Always validate inputs/publish and run relevant checks before commits; never suppress failing checks, commit credentials/build intermediates, or alter unrelated apps. Material changes to confirmed contract require Root escalation. No new coverage threshold invented.

Success requires demonstrated local independence, all selected-target output correctness, actual computation recovery without model access, matching selected configs during standalone/full deployment, validated persistent schedules and readable measurements, with no legacy user flags or automatic CPU reference workflow. Specification is one cohesive application boundary, not independently shipped capabilities; no capability map is needed.

## Tuning failure policy amendment (2026-10-04)

This amendment governs candidate failure classification and completion reporting. Measurement owns isolated worker lifecycle and distinguishes environment/library initialization failure from a failure during candidate compilation/execution. Candidate compilation errors, output mismatches, timeouts, and candidate-caused native worker crashes are failed trials: reclaim the worker, retain diagnostic context, and continue FSIM search (or the remaining TSIM candidates). Invalid workloads/configuration and environment/library initialization errors stop tuning. Do not broadly swallow infrastructure/protocol failures. No runtime/compiler assertion changes are required by this amendment.

Tuning orchestration owns per-occurrence counters and termination: actual trials count every attempted unique candidate, including failures; successes count only candidates passing correctness checks. On quota reached or configuration space exhausted, print actual trials, successes, requested quota, and termination reason. Space exhaustion with at least one success per selected occurrence completes normally and exports all successful schedules, including when below quota; describe this as space exhaustion rather than quota reached. Zero successes for a selected occurrence keeps the existing publication failure rule and preserves old saved output. No new CLI flags or dependencies. The successful candidate log remains authoritative for TSIM; failed trials never enter it.

Acceptance: regression tests cover candidate crash continuation and worker reclamation, genuine initialization failure stopping, quota completion counters, exhausted-space completion counters, and zero-success preservation. Verify the user command `make tune WORKLOAD=0` with default search controls and replay the resulting TSIM schedule. Exclude apps/deploy from verification as the user instructed.

## Legacy cleanup amendment (2026-10-05)

User accepts the main flows and explicitly requests deleting the IC V1 tune/legacy directory and updating .gitignore. This overrides the earlier historical-evidence retention rule only for this application's tune/legacy. Remove its tracked historical files, legacy-specific ignore exceptions, and current README/test expectations that retain those files; preserve current tune/<config-name> deliverables and their tracking rules. Update live repository documentation referring to retained IC V1 legacy data where necessary; historical initiative records need not be rewritten. Check remaining references before removal. No CLI, computation, tuning, publication or other application behavior changes.

Provide a dependency and redundancy audit: distinguish runtime dependencies (TVM/VTA/config/environment and repository-layout Make defaults) from optional dataset/provenance test dependencies. Identify old runtime reference/matrix deployment paths and their current consumers. Audit only in this cleanup: do not remove these code paths or weaken their tests without a separate confirmed refactor scope. Document the app's independence from apps/common and sibling benchmark applications, with the limits of directory relocation and tests stated accurately.

Acceptance: tune/legacy absent; active docs and tests no longer require it; current saved logs remain tracked; focused asset/Make tests and reference checks pass. No apps/deploy testing, no default tuning rerun needed for file/documentation-only changes. Use existing module boundaries and no new abstraction or dependency.
