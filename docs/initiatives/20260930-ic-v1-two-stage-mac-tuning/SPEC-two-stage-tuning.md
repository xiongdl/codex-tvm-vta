# Spec: IC V1 two-stage tuning

## Objective
Complete an actual AutoTVM search for every IC V1 VTA workload. Use the real prepared model's complete computation and select configurations by measured TSIM cycles.

## Stack and structure
Use existing TVM/VTA AutoTVM, fused_tasks.py, model_pipeline.py and shared simulator helpers, project Conda Python and vta/config/vta_64mac.json. Maintained tuning Python lives under vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/; the prior tune.py entry point may remain as a compatibility wrapper. Tests live in the application's tests/. Update application README.md and scripts/README.md.

Intermediate native FSIM/TSIM logs, candidate records, errors, progress and resume state live under image_classification_v1/build/. Export optimal native records and self-contained validated metadata under image_classification_v1/tune/. Best-result replay must not depend on intermediate files surviving. Do not commit bulk intermediate generated artifacts.

## Behavior and acceptance
- Default operation covers every real VTA workload, retaining a mapping to every fusion occurrence. Identical tasks may share search only when computation and schedule identity match; repeated deployment occurrences remain visible.
- Preserve complete fusion operators, tensor shapes/layouts/dtypes, quantization, padding/stride, arithmetic order and deployment lowering. Compare computation/lowering evidence and runtime outputs; matching convolution shape alone is insufficient. Cover every deployed VTA workload; explicitly report any unsupported operation and never present incomplete coverage as completion.
- Maintain one search's visited configuration state across 100-trial batches; do not remeasure duplicates to satisfy the success quota. Stop after a completed batch when distinct successful configurations reach 20, or when the finite space is exhausted. Final batch may be smaller. Record attempted counts, distinct successes, space size and stop reason.
- FSIM timeout is 60s; TSIM timeout is 120s. Measure every successful distinct FSIM configuration on TSIM, then select minimum valid positive native cycles. Preserve successful and failed measurements. If no TSIM success exists, report failure, not a best result.
- TSIM uses the existing single-formal-invocation protocol with warmup excluded and profiler reset. Preserve native cycle units.
- Local RPC resources are process-owned and cleaned on success, timeout and error. A crashed candidate cannot poison later candidates; infrastructure or permission failures remain distinguishable from invalid configurations. Resolve encountered failures and rerun affected measurements. Request actual missing sandbox permissions through supported escalation, without bypassing policy.
- Save model/geometry hashes, computation/workload identity, occurrence mapping, configuration, protocol, options and native-log hashes. Resume only with matching identities; reject stale or mismatched artifacts.

## Commands
Target command contract (implement and document these options):
```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=fsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" .envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/tune.py --all --trial-batch 100 --min-successful 20 --fsim-timeout 60 --tsim-timeout 120
.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tune.py vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py vta/apps/mlperf_tiny_benchmark/tests/test_autotvm_tuner.py
```
An orchestrator launches backend-specific processes so loaded simulator state cannot leak across backends. Provide workload selection, manifest/resume and bounded smoke options; bounded smoke output is explicitly incomplete.

## Style
Small functions, explicit units and validated JSON boundaries, e.g. `{"successful_config_count": 20, "tsim_cycles": cycles}`. Reuse shared helpers without imposing IC V1 defaults on unrelated model commands.

## Verification
Meaningful tests cover batching, exhaustion, deduplication, candidate handoff, timeout defaults, crash cleanup, identity validation and TSIM-based selection. Run a bounded real smoke before the full search. Full runtime evidence lists every workload's trial counts, successes, failures and selected TSIM cycles.

## Boundaries
Always preserve correctness and required timeouts; document maintained command inputs, outputs and side effects. Ask Root when approved decisions must change or permissions/resources are unavailable. Never change model assets or geometry, fabricate cycles, weaken tests, suppress permission failures or mark partial tuning complete. Optimization gain is measured and reported; no unrequested minimum percentage is invented.

## Open questions
None; exact filenames within the specified directories are implementation details.
