# Spec: IC V2 selected-schedule deployment validation

## Objective
Deploy IC V2 using the exported minimum-cycle configurations and prove every VTA operator occurrence has strictly less than 10% TSIM cycle difference from its corresponding AutoTVM measurement. Produce reviewable evidence from the full tuning and actual deployment run.

## Stack and structure
Use repository TVM/VTA, GraphExecutor, debug_executor and the existing TSIM simulator session. Add V2/tune/deployment.py and focused V2 tests. Consume the self-contained contract in SPEC-two-stage-tuning.md. Keep raw builds and graph bundles under V2/build/; preserve selected native records and final deployment JSON plus a concise results report under V2/tune/. Lifecycle evidence belongs under this initiative directory. Document commands in the V2 and scripts READMEs.

## Required behavior
- Validate complete artifact identity and coverage before building. Map the selected configuration to each deterministic V2 symbol and occurrence, including repeated workloads. Check actual lowering consumes the selected configuration.
- Build untuned baseline and tuned mixed graphs plus the existing quantized pure HOST reference. Preserve model bytes, quantization and host/VTA routing.
- Reload exported graph bundles. First use exactly one committed sample to verify outputs, all eight VTA occurrence cycle pairs and ordinary/debug counter agreement. Only after this performance gate passes, execute the same selected configuration on all ten committed samples to verify output tolerances and predictions. The ten-sample phase is correctness-only: do not repeat per-occurrence performance alignment or baseline/tuned performance profiling for each sample. Performance improvements cannot justify arithmetic changes.
- Measure deployed VTA graph nodes on graph-resident tensors after real graph execution. Use the existing profiler clear/read protocol around one counted node invocation. Exclude warmup and unrelated host nodes. Identify rows by occurrence, symbol, fusion, workload and selected configuration hashes.
- Before trusting node measurements, compare debug complete-run TSIM counters with an ordinary uninstrumented GraphExecutor run on the same input and configuration. Require agreement; investigate any instrumentation effect rather than replacing deployment measurements with isolated task costs.
- For each of the eight current VTA occurrences, require positive integer cycle counts and abs(deployment_cycles - autotvm_cycles) / autotvm_cycles < 0.10. Enforce using exact integer comparison: 10 * abs(deployment_cycles - autotvm_cycles) < autotvm_cycles. Exactly 10%, missing rows and invalid counts fail.
- Preserve failure diagnostics; an invalid run must never publish a passing report. Correct scope/counting/lowering discrepancies without relaxing the threshold or choosing a slower schedule solely to pass it. Any required Root-owned scope change escalates.
- Publish model/geometry/manifest identity, single-call protocol, per-occurrence config and cycle pairs, relative differences and pass status. Report baseline and tuned uninstrumented full-model cycles for the one performance-validation sample separately from isolated costs. Do not require ten-sample performance measurements. Report selected MAC utilization using the existing model-independent calculator when compatible; the hard gate remains per-occurrence cycle agreement.
- V1's current <=10% behavior must not weaken V2's strict contract. If generic shared validators are touched, keep their compatibility or explicitly scope strict validation to V2 and verify regressions.

## Commands
Run from repository root after complete best artifacts exist; replace <run-id> with the actual generated run id:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/deployment.py --best-manifest vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/optimal/<run-id>/best-manifest.json --output vta/apps/mlperf_tiny_benchmark/image_classification_v2/tune/deployment-full.json
```

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python:$PWD/vta/apps/mlperf_tiny_benchmark:$PWD/vta/apps/mlperf_tiny_benchmark/image_classification_v2" ./.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests -q
```
Use the narrowest existing regression commands for shared compiler/runtime changes; rebuild affected libraries only when required by source changes. Use project Python for all validation.

## Code style
Use explicit validation with exact integer threshold arithmetic:

```python
delta = abs(deployment_cycles - autotvm_cycles)
if 10 * delta >= autotvm_cycles:
    raise ValueError("IC V2 deployment cycle difference must be below 10%")
```
Follow V1 artifact structure where compatible; ensure model identity is explicit rather than inferred from a directory or imported module cache.

## Testing strategy
Cover below/exactly/above 10% in both directions, large integers, invalid/nonpositive counts, missing/duplicate occurrences, foreign artifacts, actual selected-config dispatch and instrumentation checks. Integration first verifies all eight real VTA measurements on one committed sample after full search, then verifies all ten real sample outputs using the same selected configurations without repeating performance alignment. If shared helpers change, run the corresponding V1 tuning/deployment regressions. Mocked tests and bounded smoke results do not replace final simulator evidence.

## Success criteria
1. Complete full-search artifacts cover all V2 VTA occurrences and replay without intermediate build files.
2. Tuned real deployment passes reference output checks for all ten samples and selected configurations are attributable to their occurrences.
3. Every measured occurrence satisfies the strict formula; the report includes all cycle pairs, configuration identities and full-run evidence.
4. Relevant regressions pass; no threshold, routing or measurement protocol has been weakened.

## Boundaries
Always retain failure evidence, distinguish full-model cycles from per-node costs and keep artifacts model-specific. Never sum isolated tuning costs and present them as measured full-model performance; never silently skip failing occurrences. Other models' tuning and FPGA performance are out of scope. Missing permissions or approved-contract changes escalate to Root.

## Open questions
None.

## Approved clarification (2026-10-01)

The user explicitly clarified and authorized: one sample suffices for AutoTVM-to-deployment performance alignment for all eight VTA occurrences; after that passes, run the optimal configuration on ten samples solely to verify correctness. This supersedes any earlier requirement to profile ten samples or to execute them before the one-sample performance gate. Strict <10% and single counted invocation with warmup excluded remain unchanged.
