# Spec: VWW TSIM Runtime Recovery

## Objective

Diagnose and fix the Visual Wake Words V1 TSIM matrix segmentation fault that appears after the corrected 13-partition graph passes model preflight. The current full matrix test exits 139 in TVM `graph_executor.run()` through the VWW runtime `_run_graph` path. Success means VWW completes the real TSIM deployment matrix and its existing output comparisons and simulator-cycle checks.

## Assumptions

1. The failure is reproducible with the current VWW TSIM matrix test after the 13-partition routing correction.
2. Investigation may inspect the VWW runner, runtime, tests, and supported runtime API usage; implementation changes remain within VWW deployment code and its tests.
3. If evidence shows the fault requires modifying shared TVM/VTA platform code, that change is outside this module's authorization and requires a separate scope decision.

## Tech Stack

Python 3.11 project environment, TVM graph executor, VTA TSIM runtime, pytest, and the existing VWW model/sample assets. No new dependencies are expected.

## Commands

Run from the repository root with the built project environment and TSIM libraries:

Focused real matrix test:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py -k tsim_matrix_contract_has_ten_comparisons_and_positive_cycles
```

End-to-end VWW TSIM deployment:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py --simulator tsim --host-codegen all
```

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/runtime.py` owns graph build, export, load, and TSIM execution.
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/run.py` selects the deployment mode and matrix runner.
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_tsim_deployment.py` exercises both testable runtime contracts and the real TSIM matrix.
- `vta/apps/mlperf_tiny_benchmark/visual_wake_words_v1/tests/test_host_deployment.py` covers HOST/FSIM deployment contracts.

## Code Style

Use the existing VWW runtime helpers and error-handling patterns. Fix the earliest supported VWW boundary that explains the crash, and keep the test asserting the observable matrix result rather than internal call sequences. Do not suppress or skip the crashing matrix test.

## Testing Strategy

- Re-run the real TSIM matrix pytest after any runtime change.
- Run the VWW deployment CLI to confirm the production entry point completes TSIM execution.
- Preserve the ten sample comparisons per configured host codegen and positive simulator-cycle checks.
- Run focused VWW runtime/host deployment tests for changed behavior.

## Boundaries

- **Always:** Preserve the 13-partition VWW graph contract, output comparisons, and simulator-cycle checks; report a TSIM deployment pass only after the matrix completes.
- **Ask first:** Modify shared TVM/VTA platform code, VWW model weights or quantization, or other benchmark runtimes.
- **Never:** Skip the real TSIM matrix, convert it to HOST/FSIM-only validation, or mask a process crash as a pass.

## Success Criteria

- The focused real TSIM matrix test exits successfully.
- The VWW TSIM runner completes deployment for the configured host-codegen matrix.
- Existing output comparison and positive-cycle assertions pass.

## Open Questions

- The precise crash root cause is unresolved; investigation should determine it before selecting a code change.
