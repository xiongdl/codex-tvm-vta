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
