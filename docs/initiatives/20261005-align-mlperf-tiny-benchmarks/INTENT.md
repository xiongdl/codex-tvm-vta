# Confirmed Intent

Initiative: `20261005-align-mlperf-tiny-benchmarks`
Confirmed by the user on 2026-10-05 after scope, single-window anomaly,
real-computation-only VTA, and manual acceptance clarification.

## Outcome
Use `image_classification_v1` as a read-only model deployment template.
Migrate `image_classification_v2`, `visual_wake_words_v1`,
`keyword_spotting_v1`, `anomaly_detection_v1`, and `streaming_wakeword_v1`
to self-contained applications with local Python implementation, `deploy.py`,
`tune.py`, and the template Make workflow. One input and one selected target
per deployment. Preserve necessary model preprocessing and quantization
semantics. Anomaly supports one deterministic window first. Only computation
contributing to model output may be offloaded or tuned; remove neutral VTA
activity probes and report actual CPU fallback and VTA coverage.

Use deployment workload export, FSIM search, TSIM cycle selection, and selected
schedule replay with template artifact validation. Replace old deployment and
seed/resume interfaces; historical schedule compatibility is not required.
After consumers are migrated, delete all code in `vta/apps/common` and shared
code at the root of `vta/apps/mlperf_tiny_benchmark`; retain application
subdirectories, models, samples, and licenses. Update affected scripts, tests,
and documentation.

## Priorities and boundaries
The priority is deployment and tuning workflow, not application precision or
accuracy. Do not expand anomaly to multiple windows, implement continuous
streaming, change the reference app, or create a generic shared runtime.
Do not change TVM or VTA compiler/hardware merely to expand operator support.

## Manual Acceptance
Provide a separate complete, executable acceptance instruction set for each
of the five migrated applications, including prerequisites, commands, expected
results, all implemented deployment/tuning features, artifact/report checks,
and cleanup behavior. Bounded tuning is sufficient to validate the workflow.
The reference app is excluded from changes and manual acceptance.
The user runs the applicable instructions per application and reports their
acceptance result before manually merging. Accuracy is not an acceptance gate.
