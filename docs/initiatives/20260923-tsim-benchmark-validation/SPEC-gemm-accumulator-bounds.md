# Spec: GEMM Accumulator Bounds

## Objective

Fix `vta/tests/python/integration/test_benchmark_gemm.py::test_gemm`, which currently fails during TVM `StorageFlattener` because `local.acc_buffer` requests 524288 bits while the configured maximum is 262144 bits. Preserve the existing 128×128 GEMM workload and make its schedule fit the configured accumulator capacity.

## Assumptions

1. The existing `vta_64mac.json` geometry and TVM's declared local accumulator capacity are correct and must not be enlarged to silence the failure.
2. The failure is caused by the test schedule's accumulator tile footprint, not by a missing runtime library or stale build; checkpoint3 reaches TIR storage flattening before remote execution.
3. It is acceptable to split the output computation into smaller schedule tiles as long as the full workload and reference result are preserved.

## Tech Stack

Python 3.11, TVM TE/TIR, VTA scheduling and simulator tooling, pytest. No new dependencies are expected.

## Commands

Run the focused test from the repository root:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/tests/python/integration/test_benchmark_gemm.py
```

## Project Structure

- `vta/tests/python/integration/test_benchmark_gemm.py` defines the test workload and TE schedule.
- `vta/config/vta_64mac.json` defines hardware geometry and memory capacities; this task does not change it.
- `tvm/src/tir/transforms/storage_flatten.cc` reports the capacity check that currently fails; this task does not modify TVM.

## Code Style

Keep the existing workload dimensions and schedule-local values explicit. A tiling adjustment should remain local to the test schedule, for example:

```python
output_tile = ...  # chosen so the acc_scope tile fits env.acc_scope capacity
```

Do not change VTA memory limits or suppress TVM's storage-bound assertion.

## Testing Strategy

- Run the focused `test_benchmark_gemm.py` pytest module with the project environment and TSIM configuration.
- Verify the original 128×128 workload reaches remote execution and produces the existing simulator/result checks.
- The test must not pass by skipping GEMM, switching to HOST, or reducing the tested problem dimensions.

## Boundaries

- **Always:** Preserve the workload, simulator execution, and output validation while keeping the generated `local.acc_buffer` within the existing capacity.
- **Ask first:** Change shared VTA geometry, accumulator capacity, TVM storage-bound behavior, or GEMM workload dimensions.
- **Never:** Disable the storage bound check, mark the test xfail/skip, or substitute a CPU-only calculation.

## Success Criteria

- TVM storage flattening completes without a `local.acc_buffer` bound error.
- The existing 128×128 GEMM workload completes under the configured TSIM backend and its output/reference checks pass.
- The focused GEMM pytest module passes.

## Open Questions

- None. The failure and configured capacity are explicit in checkpoint3; schedule tiling is the scoped correction.
