# Spec: Image Classification V2 TSIM Test Stability

## Objective

Remove the known failure where the complete image classification V2 TSIM deployment pytest module segfaults during in-process graph execution, even though the isolated matrix case and production CLI complete. The complete module must run to normal pytest completion while retaining the real LLVM/C TSIM deployment matrix and all output/cycle assertions.

## Assumptions

1. The observed failure is order- or process-context-sensitive because the isolated matrix test and production CLI passed while the complete pytest module segfaulted twice.
2. Diagnosis may cover the V2 runtime, test fixtures, test process lifecycle, and the TVM/VTA executor boundary used by this deployment. A shared-platform change is permitted only when a minimal reproducer identifies that boundary as the cause and focused regression coverage proves the fix.
3. The fix must not skip, xfail, weaken, or silently convert the real TSIM matrix into a preflight-only check.

## Tech Stack

Python 3.11 project environment, TVM graph executor, VTA TSIM, pytest, and the checked-in image classification V2 model/sample assets. No new dependency is expected.

## Commands

Run from the repository root with the built project environment and TSIM libraries:

Full V2 deployment test module:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py
```

Production entry point:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all
```

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/runtime.py` owns graph build, load, and TSIM execution.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py` invokes the production deployment matrix.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py` covers runtime contracts and real matrix execution.
- If a shared TVM/VTA executor boundary is implicated, add the narrowest relevant regression test in its owning repository.

## Code Style

Follow the existing runtime and test patterns. Reproduce the crash before changing behavior, then fix the earliest boundary supported by the evidence. Tests must assert observable matrix results rather than private call ordering.

## Testing Strategy

- Capture the failing complete-module command and identify the test/order/process boundary that triggers the crash.
- Add or update a regression test that fails before the fix and passes after it.
- Run the complete module in one pytest process and require a normal exit with no segmentation fault.
- Run the production CLI and preserve ten reference/output comparisons and positive simulator cycle counts for both LLVM and C host-codegen variants.
- Run focused tests for every changed runtime or shared executor boundary.

## Boundaries

- **Always:** Preserve the 8-partition V2 graph contract, real TSIM matrix, output comparisons, and positive cycle checks.
- **Ask first:** Change V2 model weights, quantization, benchmark semantics, or add a new dependency.
- **Never:** Skip or xfail the crashing matrix case, turn it into a HOST/FSIM-only test, or claim the full module passed when only an isolated test or CLI passed.

## Success Criteria

- The complete V2 TSIM deployment pytest module exits 0 without a process crash.
- The production TSIM CLI completes LLVM and C matrices with ten comparisons and positive cycle counts each.
- A regression test covers the diagnosed failure boundary.

## Open Questions

- The crash root cause is unresolved; diagnosis determines whether the fix belongs in V2 test lifecycle/runtime code or the narrowly implicated shared executor boundary.
