# Implementation Plan: VTA AutoTVM Schedule Tuning for MLPerf Tiny

## Overview

Add a shared VTA AutoTVM tuning entry point for FSIM and TSIM, prove the tuned schedule lowers TSIM cycles on MLPerf Tiny Image Classification V1, then add model adapters for the remaining benchmark applications and an aggregate model selector. The implementation preserves existing model preparation and correctness contracts, uses `vta/config/vta_64mac.json`, and writes one native tuning log plus a matching JSON sidecar per model/backend pair.

## Architecture Decisions

- Keep AutoTVM out of model `model_pipeline.py` modules. Existing pipeline tests assert those modules remain independent of AutoTVM; the tuner will consume their prepared Relay graph through separate adapters.
- Keep schedule search and log/sidecar handling in a shared benchmark tuner. Model-specific adapters provide the Relay module, params, identity, and existing runtime hooks.
- Use AutoTVM history-best while compiling tuned artifacts. Validate log metadata before compilation so a model, backend, or geometry mismatch fails early.
- Make TSIM candidate measurements use `cycle_count` as AutoTVM's cost when the available runner APIs support it. FSIM tuning uses its own backend measurement and remains a separate log. Confirm the cycle-aware runner in the first implementation task before expanding model coverage.
- Repair VTA-side AutoTVM task extraction or TOPI schedule compatibility where needed to enable the approved V1 tuning path. Keep those fixes in the VTA repository and avoid changes to TVM core. If the current TVM APIs require a TVM-core change, stop and return for a scope decision.
- Preserve existing FSIM/TSIM process isolation and lazy simulator loading. Each simulator command runs in a fresh process, with `VTA_BACKEND` matching the CLI backend.
- Keep log files, JSON sidecars, and generated model bundles under ignored build/output directories; do not commit tuning output.

## Task List

### Phase 1: Simulator AutoTVM Foundation

- Task 1: Repair VTA-side V1 task extraction/schedule compatibility as needed, then verify simulator-aware AutoTVM measurement including TSIM cycle cost.
- Task 2: Add shared task extraction, FSIM/TSIM tuning orchestration, and log/sidecar persistence.

### Checkpoint 1: AutoTVM Foundation

- FSIM and TSIM tuning entry points select the requested backend and use the shared geometry.
- V1 VTA AutoTVM tasks and schedules build for the intended VTA target without target-registration or iterator-split failures.
- Native logs and JSON sidecars are separate, correctly paired, and replayable.
- TSIM trial costs contain usable cycle counts.

### Phase 2: Image Classification V1 Closed Loop

- Task 3: Apply V1's matching history-best log during compilation and report tuned-versus-baseline output and TSIM cycle results.

### Checkpoint 2: V1 Closed Loop

- FSIM and TSIM V1 tuning/replay commands complete.
- Existing V1 output comparisons pass.
- Tuned TSIM `cycle_count` is lower than the untuned baseline under the same run conditions.

### Phase 3: Model Rollout, Part A

- Task 4: Add image classification V2 tuning and replay support.
- Task 5: Add anomaly detection V1 tuning and replay support.

### Checkpoint 3: Image V2 and Anomaly

- Each model/backend pair emits its own AutoTVM log and matching sidecar.
- Existing model correctness checks pass with matching tuned records.

### Phase 4: Model Rollout, Part B

- Task 6: Add keyword spotting V1 tuning and replay support.
- Task 7: Add streaming wakeword V1 tuning and replay support.

### Checkpoint 4: Audio Models

- Each model/backend pair emits its own AutoTVM log and matching sidecar.
- Existing preprocessing and output-equivalence checks pass with matching tuned records.

### Phase 5: Model Rollout, Part C

- Task 8: Add visual wake words V1 tuning and replay support.
- Task 9: Add aggregate model selection, coverage reporting, and workflow documentation.

### Checkpoint 5: Complete Rollout

- The tuner enumerates all six repository MLPerf Tiny applications and identifies supported/unsupported VTA tasks explicitly.
- FSIM and TSIM logs/sidecars are separate for every model.
- Existing model correctness gates remain intact; any performance claim includes a tuned-versus-baseline TSIM cycle comparison.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| TVM AutoTVM's standard runner may report only wall time rather than TSIM simulator cycles. | AutoTVM may choose a host-measurement winner that does not minimize VTA cycles. | Prove a cycle-aware TSIM measurement adapter in Task 1; stop before wider integration if it requires out-of-scope TVM-core changes. |
| The initial FSIM smoke's RPC worker exited with `-11`; TSIM task creation reported an unregistered `ext_dev` schedule, and direct VTA conv/dense templates reported already-split iterator errors. | V1 cannot produce valid AutoTVM trials until target selection/task extraction and VTA schedule construction agree. | Resolve the V1 path in VTA-side Python and add regression coverage in Task 1; keep TVM core unchanged. |
| VTA AutoTVM task extraction may not see operations after each benchmark's external-codegen partitioning. | A model may produce no tunable tasks or incomplete task coverage. | Extract from the model's existing quantized Relay graph at the supported pre-partition boundary and report unsupported task families. |
| Benchmark models have different graph, runtime, and profiler contracts. | A single generic integration could break existing correctness gates. | Add one model adapter at a time and keep the current model-specific output checks unchanged. |
| TSIM tuning trials can be slow. | Full search may take a long time. | Keep trial count and early stopping configurable; use bounded smoke runs in checkpoints and full search for performance acceptance. |
| The documented project Python environment and native simulator libraries were not found during initial inspection. | Python integration and end-to-end verification cannot run until prerequisites exist. | Before running verification, use the existing `.envs/tvm-vta-env` and built TVM/VTA libraries; follow `scripts/README.md` if the environment is absent and request the required setup authorization then. |

## Open Questions

- The exact cycle-aware runner hook, per-trial simulator reset sequence, and VTA-side schedule/task-extraction fixes are to be settled in Task 1 using the current AutoTVM and VTA APIs.
- The final CLI options and tuner defaults are to be established while implementing Tasks 1–2; the accepted public behavior is FSIM/TSIM selection, model selection, configurable trial control, and paired output artifacts.
- Some models may have no registered VTA AutoTVM tasks for particular operators. The rollout must report this precisely and must not present those operators as tuned.
