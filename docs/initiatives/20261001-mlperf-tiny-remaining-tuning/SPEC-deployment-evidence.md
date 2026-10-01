# Spec: seed alignment and selected deployment evidence

## Objective
For all four models, prove seed AutoTVM arithmetic and cycles represent actual deployment before full search. Then deploy minimum-cycle schedules, verify one sample and publish real per-operator cycles and useful-MAC utilization.

## Stack and structure
Use repository GraphExecutor/debug_executor, existing model runtime/reference checks and TSIM session. Model-local tune/deployment.py adapters may share validated profiling helpers. Builds and graph bundles stay under model/build/; seed/selected reports, native records and concise final reports live under model/tune/. Lifecycle evidence lives in this initiative. Extend scripts/mac_utilization.py's versioned report compatibility only if necessary, preserving existing contracts. Document maintained commands in scripts/README.md and model READMEs.

## Required behavior
- Consume validated complete seed or optimal manifests from operator-tuning. Apply exact configs to deterministic graph symbols and confirm actual lowering uses them. Preserve HOST/VTA routing, model arithmetic and existing correctness tolerances.
- For each model, use exactly one committed representative sample through its existing preprocessing. AD keeps its existing representative-window convention and records the chosen window. Streaming execution preserves required state initialization and invocation accounting. Do not run ten samples. Verify against the existing model's HOST reference and task-specific correctness checks; do not invent new relaxed tolerances.
- Measure real mixed-model execution and VTA nodes on graph-resident inputs after execution. Clear/read TSIM around one counted node invocation, excluding warmup and HOST nodes. Compare debug full-run counters with an ordinary GraphExecutor run of the same graph/input/state; require agreement before trusting per-node measurements.
- Seed gate requires all deployed VTA occurrences to have positive integer AutoTVM/deployment cycles and `10 * abs(deployment_cycles - autotvm_cycles) <= autotvm_cycles`. Exactly 10% passes, as requested. Missing/duplicate rows, invalid costs, configuration mismatches or changed arithmetic fail. Full search is blocked until this report passes for the complete model.
- After full search, deploy the actual minimum-cycle selected configurations and repeat the same <=10% occurrence gate and one-sample correctness check. Investigate failed scope/counting/lowering rather than masking a discrepancy with a slower schedule. Keep diagnostics; do not publish a passing report on failure.
- Publish per-occurrence symbol, fusion/workload/config hashes, logical MAC count, AutoTVM TSIM cycles, deployed TSIM cycles, absolute/relative deviation and gate result. Repeated occurrences stay separate. Also report measured untuned baseline and tuned full-model cycles separately from isolated operator costs.
- Compute operator useful-MAC utilization as `logical_MACs / (measured_deployment_cycles * peak_MACs_per_cycle)` for one invocation. Derive logical Conv/Dense MACs from real tensor arithmetic, excluding padding-only and HOST work; record derivation. Geometry peak is `2**LOG_BATCH * 2**LOG_BLOCK * 2**LOG_BLOCK` (64 for current geometry). Account consistently for any multiple invocations. Never substitute AutoTVM cycles for deployment utilization or sum isolated costs and label them measured whole-model cycles.
- Reports bind model/geometry/sample identity, selected manifest hash, measurement protocol, occurrence coverage and invocation counts. Emit a versioned deployment artifact consumable by scripts/mac_utilization.py and publish CSV/JSON plus a concise four-model summary with failures and exhaustion visible. Artifacts replay independently of intermediate builds.

## Commands
Implementation target interfaces from repository root; MODEL and paths identify the actual model/run:

```bash
MODEL=anomaly_detection_v1
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/$MODEL" ./.envs/tvm-vta-env/bin/python "vta/apps/mlperf_tiny_benchmark/$MODEL/tune/deployment.py" --best-manifest <seed-or-optimal-manifest.json> --output <deployment.json>
./.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --deployment-report <deployment.json>
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/$MODEL" ./.envs/tvm-vta-env/bin/python -m pytest "vta/apps/mlperf_tiny_benchmark/$MODEL/tests/test_tsim_deployment.py" -q
```

## Code style
Use exact integer gates and explicit validation:

```python
if 10 * abs(deployment_cycles - autotvm_cycles) > autotvm_cycles:
    raise ValueError("deployment cycle difference exceeds 10%")
```

## Testing and success criteria
Test below/exactly/above 10% in both directions, invalid/large integer counts, identity/coverage failures, actual config dispatch, reference output checks, instrumentation agreement and MAC arithmetic/report compatibility. Real integration must pass complete seed coverage before each model's full search and complete selected coverage afterwards, using one sample in each phase. All four final reports must contain measured cycle pairs, utilization and self-contained selected artifacts. Run affected IC and calculator regressions; do not alter IC V2's existing strict threshold or ten-sample default contract.

## Boundaries
Always preserve reference tolerances, measurements and failure evidence. Ask Root for missing permissions/data/environment or changes to approved decisions. Never skip failed operators, silently replace measurements or weaken thresholds. IC retuning and ten-sample runs are outside this initiative. No unresolved user choices.
