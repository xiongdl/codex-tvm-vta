# Spec: model-workflow
Inherits CAPABILITY_MAP.md shared contract.

## Objective
All six models have one deployment implementation and one tuning entry point. The same runtime deploys defaults, partial candidates, and best snapshots.

## Models
image_classification_v1, image_classification_v2, anomaly_detection_v1, keyword_spotting_v1, streaming_wakeword_v1, visual_wake_words_v1.

## Behavior and structure
run.py is the sole user deployment entry, delegating to model runtime and apps/common helpers.
tune.py searches actual deployment-compute configuration spaces and exports schedule-artifacts snapshots; remove executable tune/tune.py and tune/deployment.py after callers are migrated.
Extract reused measurement/search/resume/evidence mechanisms out of model-local copies.
Delete generic isolated-operator tuning CLI and workflow; retain internal AutoTVM APIs needed by deployment-compute tuning. Removing autotvm_tuner.py requires relocating needed infrastructure, not deleting dependencies blindly.
Keep MLPerf model registry/sample policies model-aware, outside generic common helpers.
Retain existing search defaults (100 distinct FSIM configs per batch, quota 20 or valid-space exhaustion), isolated worker timeout settings, resume identity checks, one-call TSIM scoring, and correctness filtering unless the approved plan identifies a behavior-neutral consolidation.
The seed-before-full-search gate uses the unified runtime. Deployment cycle-alignment validation is optional for arbitrary candidate execution and required for selected evidence/seed gates where already required.
IC V2's existing strict cycle threshold and ten-output validation remain; other models preserve their sample/validation contracts.
No candidate is described as faster without comparable baseline evidence.

## Commands
Target usage:
```bash
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator fsim --schedule none
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune.py --seed --all
VTA_BACKEND=tsim ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --schedule /tmp/ic-v2-best.log
VTA_BACKEND=fsim ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests --import-mode=importlib -q
```
Final evidence/report flags and candidate export flags are specified concretely in PLAN before implementation; no separate deployment entry is permitted.

## Testing strategy and success criteria
For every model verify baseline, one-layer partial candidate and fully selected snapshot on FSIM plus representative TSIM execution/evidence.
Exercise at least two different configurations on the same occurrence to prove input is honored; report actual config identities.
Preserve model HOST comparisons and relevant simulator gates. Existing evidence validates historical results, not the new path by itself.
Verify seed/search/resume/export/application integration with bounded trials before requiring expensive searches. Exhaustive re-tuning all six models is not required to establish the refactor.
Retire obsolete CLI tests only by replacing their behavior coverage; run complete BYOC gate with maintained callers.
Document one run.py interface, one tune.py workflow, saved-result migration and units.

## Boundaries
Follow shared structure/style/boundaries. Assets/quantization/FPGA and official benchmark submission remain outside scope. No open user choices.
