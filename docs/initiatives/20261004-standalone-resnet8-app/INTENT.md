# Confirmed intent

Initiative: `20261004-standalone-resnet8-app`.
User explicitly confirmed the complete intent in this conversation on 2026-10-04.

- Outcome: make image_classification_v1 an independent, complete float ResNet-8 application.
- User: a developer running deployment and tuning from this model directory or repository root.
- Why: simplify vta/apps, with deployment as the core and tuning supplying deployment schedules.
- Success: single-image/single-target deployment, real deployment computation export, separate FSIM search and TSIM selection, and Makefile wrappers work without other vta/apps directories.
- Constraint: tuning consumes exported actual VTA functions and activations and shares deployment lowering; schedules and geometry identities are checked.
- Out of scope: INT8 input models, other application cleanup, removing TVM/VTA/environment/config dependencies, automatic merge.

## Confirmed contracts

run.py: --model (float ResNet-8), --input (one 32x32 RGB PNG/JPEG), --target c|llvm|vta,c|vta,llvm (default vta,llvm), --simulator fsim|tsim (default fsim), --schedule (default scheduling), --output-dir (model build/), --deployment-report PATH (optional Markdown), --export-workloads PATH (optional, VTA only, normal execution continues). Model default model/pretrainedResnet.tflite; input default samples/00-airplane.png. No host-codegen/all/evidence flag or automatic CPU reference comparison. Pure CPU uses the same quantized model preparation. Makefile pairs VTA_BACKEND and simulator.

tune.py: --workloads and --output-logs required; --workload defaults -1 (all), nonnegative is one occurrence; --simulator defaults fsim; --timeout defaults 60 seconds FSIM/120 TSIM; --trial-batch defaults 100 and --min-successful defaults 20, FSIM only; TSIM requires --input-logs from FSIM, measures candidates and selects minimum cycles per occurrence. No resume/output-log/export-candidate/export-best/seed/alignment-report interface.

Makefile: deploy, tune-fsim, tune-tsim, tune. CONFIG defaults repository vta/config/vta_64mac.json. Deploy variables MODEL INPUT TARGET SIMULATOR SCHEDULE OUTPUT_DIR REPORT EXPORT_WORKLOADS. Tuning variables WORKLOADS WORKLOAD TRIAL_BATCH MIN_SUCCESSFUL; split steps INPUT_LOGS OUTPUT_LOGS TIMEOUT; full tune FSIM_TIMEOUT TSIM_TIMEOUT and OUTPUT_DIR. Full tune exports workloads unless WORKLOADS supplied, then FSIM then TSIM; no automatic final optimized deployment.

Persistent tuning files: tune/<config basename without .json>/{config.json,config.sha256,fsim.tmp,fsim.json,best.log,best.json}. SHA-256 of configuration contents, not system cksum. These are versioned, including fsim.tmp. Single-occurrence updates replace that occurrence and preserve others; full updates replace all. Geometry mismatch rejects merging. New validated output replaces old; failures preserve old output. Default paths are model-relative; explicit relative paths are invocation-directory-relative. Reports support CPU/FSIM/TSIM, unavailable cycles/utilization are N/A.

## Confirmed tuning failure policy amendment

User confirmed on 2026-10-04: candidate compilation errors, output mismatches, timeouts, and candidate-caused native worker crashes do not stop search. Reclaim each worker and continue. Report actual attempted trial count, successful count, requested quota, and termination reason for each occurrence. Reaching the quota or exhausting the space with at least one successful candidate is normal completion; export all successes even below quota. Zero successes cannot supply TSIM and retains the existing publication failure rule. Invalid inputs/configuration and environment/library initialization failures remain fatal. Native runtime assertion investigation is separate from completing this tuning fix.

## Legacy cleanup amendment (2026-10-05)

User accepts the main flows and explicitly requests deleting the IC V1 tune/legacy directory and updating .gitignore. This overrides the earlier historical-evidence retention rule only for this application's tune/legacy. Remove its tracked historical files, legacy-specific ignore exceptions, and current README/test expectations that retain those files; preserve current tune/<config-name> deliverables and their tracking rules. Update live repository documentation referring to retained IC V1 legacy data where necessary; historical initiative records need not be rewritten. Check remaining references before removal. No CLI, computation, tuning, publication or other application behavior changes.

Provide a dependency and redundancy audit: distinguish runtime dependencies (TVM/VTA/config/environment and repository-layout Make defaults) from optional dataset/provenance test dependencies. Identify old runtime reference/matrix deployment paths and their current consumers. The subsequently confirmed minimal-interface amendment below authorizes removal of obsolete code and its dedicated tests. Document the app's independence from apps/common and sibling benchmark applications, with the limits of directory relocation and tests stated accurately.

Acceptance: tune/legacy absent; active docs and tests no longer require it; current saved logs remain tracked; focused asset/Make tests and reference checks pass. No apps/deploy testing, no default tuning rerun needed for file/documentation-only changes. Use existing module boundaries and no new abstraction or dependency.

## Minimal confirmed-interface amendment (2026-10-05)

The user explicitly confirms deleting obsolete tests and implementations, retaining only the minimal design needed by the agreed run.py, tune.py and Makefile interfaces. This supersedes earlier blanket requirements to preserve/migrate every old test, retain old Python compatibility APIs, or merely audit redundant code. Existing CLI flags/defaults, target behavior, float model/single-input policy, workload format, native schedule logs and sidecars, Markdown reports, tuning failure policy and validated publication behavior remain unchanged.

Remove runtime's obsolete reference-plus-mixed deployment chain: deploy/deploy_fsim_matrix/deploy_tsim_matrix, matrix/sample orchestration, build_host_artifacts and their exclusive helpers/data structures/compatibility aliases. Remove dedicated old-interface tests instead of recreating the old interfaces for tests. Before deleting helpers, check current run_selected/workloads/tuning/report and repository caller use; retain shared graph export, symbols, simulator/session/counter validation, schedule lowering and actual computation capture used by current flows. Resolve exclusive duplicate model fields and unused functions/imports locally where grounded; do not impose line-count or test-count targets. Delete unused deployment evidence helpers and test-only legacy compatibility indirection if consumers can disappear with obsolete tests.

Remove app tests of repository setup script, sample extractor recreation and optional original CIFAR dataset. The user authorizes removal rather than migration; no new scripts/tests are required for these checks. Keep meaningful local model/sample/manifest integrity and supported model/input validation. Delete tune/legacy with its tracking exceptions and active references as specified above. Retain current saved schedules. Update existing repository test selectors or current legacy migration checks only as necessary to avoid referring to deleted IC V1 material; other apps/providers remain unchanged. Document local-code independence and continuing TVM/VTA/config/environment/repository-layout requirements.

Ownership: runtime remains the single selected-target deployment owner; tuning/measurement own two-stage search and isolated workers; workloads/schedule/publication/dispatch retain their existing authoritative responsibilities. Test-owned comparisons may invoke current single-target API as needed; no production CPU-reference or matrix implementation. No new public interface, module abstraction, dependency or automatic packaging/relocation feature.

Acceptance: only current supported entrypoints remain; no runtime import of apps/common or siblings; no app-test dependence on original CIFAR data or repository setup/extractor tools; legacy absent; current logs tracked; CLI/defaults and outputs compatible. Verification: current-interface app tests (test quantity may fall), actual CPU c/llvm, FSIM/TSIM with both VTA host codegens, optional report/workloads output, bounded one-layer FSIM-to-TSIM-to-scheduled deployment roundtrip with correct output/config binding, negative failure/publication regressions, Make command mapping and quoting. Earlier completed default 20-success regression remains evidence unless tuning changes invalidate it. Exclude apps/deploy. Retain appropriate required repository checks, update obsolete selectors without masking current failures.
