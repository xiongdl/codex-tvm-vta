# Spec: real deployment validation

## Objective
Apply the TSIM-selected configurations to real IC V1 deployment and establish computation correctness, per-operator cycle agreement and baseline-versus-tuned efficiency evidence.

## Stack and structure
Extend IC V1 runtime.py, run.py and/or focused helpers under tune/, using existing model preparation, BYOC lowering, committed samples and TSIM profiling. Tests remain in image_classification_v1/tests/. Deployment builds and intermediate reports live in image_classification_v1/build/; export the final validated optimal result and report under tune/.

## Behavior and success criteria
- Apply every selected configuration to its intended deployed fusion. Verify model, geometry, workload and configuration identity before building. Clear stale compiler caches where configuration changes require it.
- Execute actual baseline and tuned model deployments on committed IC V1 samples. Preserve existing output correctness checks against the host reference. Do not replace full deployment with isolated operator replay.
- Obtain per-occurrence cycles from operators executing within the real deployed model. Instrumentation must preserve arithmetic, fusion boundaries and selected scheduling. Exclude warmup, reset counters, and document invocation count and instrumentation overhead. If profiling alters cycles, establish its equivalence against the uninstrumented full deployment.
- Compare each deployment occurrence to the same selected configuration's isolated complete-computation TSIM AutoTVM measurement. Report `abs(deployment_cycles - autotvm_cycles) / autotvm_cycles`. Every occurrence must be <= 0.10; missing, zero or mismatched measurements fail validation. Investigate and fix larger discrepancies without relaxing the threshold or rescaling cycles to force agreement.
- Report baseline and tuned full-model TSIM cycles, logical MACs, geometry peak, per-operator utilization and whole-model utilization. Use full-model measured cycles as the whole-model denominator, with repeat count normalization applied equally to MACs and cycles. Show summed operator cycles separately, including any residual VTA overhead.
- Logical MACs count mathematical multiply-accumulates, excluding padding lanes and ALU-only operations. Preserve repeated occurrences. Whole-model VTA MAC efficiency covers MAC work actually deployed on VTA; identify host computation separately rather than mixing host MACs into a VTA-only denominator. TSIM cycles measure VTA simulator activity, not host wall time.
- Export a versioned deployment JSON contract containing model identity as data, model/geometry hashes, peak or verifiable geometry reference, backend and invocation protocol, measured model cycles, occurrence IDs/symbols, workload/configuration identities, logical MAC counts, deployment cycles and matching AutoTVM cycles. Record measurement scope and provenance. Best-result artifact remains usable without intermediate files.

## Commands
Document and implement an explicit deployment validation mode:
```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" .envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/tune.py --validate-deployment --best-manifest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/best.json
.envs/tvm-vta-env/bin/python -m pytest vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tsim_deployment.py vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_fused_tuning.py
```

## Style
Keep units and source explicit: `{"deployment_cycles": cycles, "autotvm_cycles": reference, "relative_cycle_difference": difference}`. Separate measurement collection from artifact validation and formatting.

## Testing strategy
Controlled tests cover configuration application, occurrence mapping, repeated workloads, counter reset, invocation normalization, mismatched identity and 10% boundary failures. Real TSIM deployment provides final acceptance evidence, with baseline and tuned outputs checked on committed samples. Verify the exported report against raw measurement records.

## Boundaries
Always compare identical computations/configurations and retain full-model measurements. Ask Root for changed approved semantics or unavailable resources. Never use a sum of isolated AutoTVM cycles as measured full-model cycles, change quantization/assets, drop failing operators or weaken the 10% requirement.

## Open questions
None. Implementation chooses the smallest reliable in-deployment profiling mechanism and documents evidence.
