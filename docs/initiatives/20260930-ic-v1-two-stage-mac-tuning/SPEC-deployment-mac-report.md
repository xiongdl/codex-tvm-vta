# Spec: generic deployment MAC report

## Objective
Extend the existing repository scripts/mac_utilization.py to report operator and whole-model useful MAC utilization from actual deployment measurement artifacts, independent of model names or model loaders.

## Stack and structure
Use standard-library Python in the project environment. Modify scripts/mac_utilization.py and scripts/tests/test_mac_utilization.py; document options, prerequisites, measurement scope, outputs and side effects in scripts/README.md. Consume the versioned contract supplied by deployment-validation; do not import IC V1 modules in this calculator.

## Behavior and success criteria
- Add deployment JSON input and machine-readable JSON output alongside readable console reporting. Preserve the existing --macs/--cycles/--config scalar calculation interface; scalar values are labeled explicit inputs, not verified model measurements. Reject mixed ambiguous input modes.
- Validate schema, backend, scope, geometry, protocol, positive integral counts/cycles, occurrence identity uniqueness and configuration/reference association. Reject incomplete operator coverage, malformed or stale identity evidence. Model identity is metadata, not a dispatch key or supported-model allowlist.
- Report per-occurrence logical MACs, actual deployment TSIM cycles, selected AutoTVM cycles, relative difference and utilization. Preserve repeated workload occurrences. Report failures of the 10% threshold with nonzero exit status.
- Whole-model utilization is `total_deployed_logical_MACs / (actual_full_model_TSIM_cycles * peak_MACs_per_cycle)`, with both counts covering the same invocation count. Do not average operator percentages or substitute the sum of AutoTVM best cycles. Report measurement scope and host-operation exclusions.
- Report baseline and tuned comparison when provided by the artifact. Reject invalid numeric data rather than clamping utilization to conceal inconsistency. Do not require tuning logs for scalar use; deployment mode validates referenced evidence required by its contract.

## Commands
```bash
.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --deployment-report vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/deployment.json --output-json vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune/mac-utilization.json
.envs/tvm-vta-env/bin/python scripts/mac_utilization.py --macs 1000 --cycles 100 --config vta/config/vta_64mac.json
.envs/tvm-vta-env/bin/python -m pytest scripts/tests/test_mac_utilization.py
```

## Code style
Use small pure validated calculations, e.g. `ratio = total_macs / (model_cycles * peak_macs_per_cycle)`. Keep JSON parsing, calculation and presentation separate; give actionable input errors with units.

## Testing strategy
Use synthetic artifacts with unrelated model identifiers to prove model independence, repeated occurrences, non-average aggregate results, multi-invocation normalization, mismatched geometry/protocol, incomplete coverage and 10% boundary cases. Preserve scalar CLI tests. Finally consume the real IC V1 deployment artifact and reconcile reported values against runtime counters.

## Boundaries
Always use measured deployment cycles for deployment mode and retain scalar compatibility. Ask Root if contract semantics require an approved spec change. Never hardcode IC V1 shapes/names, label isolated trial sums as full-model measurements, or fabricate a deployment report.

## Open questions
None; contract spelling may be finalized during implementation without changing these semantics.
