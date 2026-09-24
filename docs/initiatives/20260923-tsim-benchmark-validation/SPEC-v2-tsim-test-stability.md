# Spec: Image Classification V2 In-Process TSIM Crash Fix

## Objective

Identify and fix the native crash observed when the image classification V2 LLVM/C TSIM matrix calls TVM's graph executor from inside the pytest process. The current end-to-end test avoids the crash by launching the production CLI in a child process; this is diagnostic isolation, not an accepted fix. The real matrix must execute directly in pytest after the underlying cause is corrected.

## Current Evidence

- The complete V2 TSIM test module previously aborted twice during in-process graph execution.
- The production CLI completes LLVM and C matrices, compares ten samples per host-codegen, and reports positive simulator cycles.
- Replacing the in-process integration test with a `subprocess.run()` call makes the module pass, but does not explain or fix the native failure.
- Historical logs do not include a native stack trace. The exact failing resource/lifetime or executor/runtime condition is not yet known.

## Assumptions

1. The failure can be reproduced with the V2 real TSIM matrix called in-process, and its likelihood may depend on test order or process state.
2. Diagnosis may cover V2 deployment/test lifecycle plus the shared TVM graph-executor and VTA TSIM runtime boundary directly involved in this crash. The user has explicitly authorized a narrowly scoped shared-platform fix for this failure.
3. Model weights, quantization parameters, benchmark semantics, simulator geometry, and unrelated code paths are not part of the approved scope.
4. A subprocess-only test, skip, xfail, or weakened matrix is not an acceptable resolution.

## Tech Stack

Python 3.11 project environment, TVM graph executor, VTA TSIM, pytest, and the checked-in image classification V2 model/sample assets. No new dependency is expected.

## Commands

Run from the repository root with the built project environment and TSIM libraries.

Full V2 deployment test module, whose real matrix test must invoke the runtime directly in the pytest process:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py
```

Focused direct in-process matrix reproducer/regression test:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python -m pytest -q vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py -k end_to_end_tsim_matrix_with_reloaded_graph_bundles
```

Production CLI remains an independent end-to-end control:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" ./.envs/tvm-vta-env/bin/python vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py --simulator tsim --host-codegen all
```

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/runtime.py` owns model preparation, graph build/load, and in-process TSIM execution.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/tests/test_tsim_deployment.py` must directly call `deploy_tsim_matrix()` for its real matrix test.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v2/run.py` remains the production CLI control path.
- If evidence points to TVM or VTA internals, change only the smallest relevant executor/runtime boundary and add its regression test in that owning repository.

## Code Style

Follow existing Python, TVM, and VTA patterns. Preserve a failing reproducer before changing behavior. Trace the native execution/lifetime path to the first incorrect ownership, state, or API assumption; document the demonstrated cause. Do not replace diagnosis with a broad workaround.

## Testing Strategy

- Reproduce the abort through a direct in-process call and capture exact command, order, signal/exit status, and the narrowest stack or native diagnostic available.
- Reduce the failure to a minimal in-process reproducer that fails before the fix. Compare isolated execution, full-module order, and production CLI behavior to isolate the condition.
- Fix the demonstrated native/executor/runtime cause; do not merely move work to another process.
- Keep the real matrix test as a direct `deploy_tsim_matrix()` call in pytest. It must validate 8 VTA partitions, ten comparisons for each of LLVM and C, and positive cycle counts for both.
- Run the complete V2 TSIM test module, the focused direct-matrix regression, and the production CLI control after the fix.
- Run focused tests for every changed TVM/VTA boundary and preserve evidence explaining why the regression fails on the pre-fix commit and passes on the fix.

## Boundaries

- **Always:** Preserve in-process matrix execution, output comparison behavior, ten samples per host-codegen, and positive cycle checks. Record the concrete root cause and the code path that made pytest-process execution unsafe.
- **Ask first:** Change V2 model weights, quantization, benchmark scoring/semantics, simulator geometry, add dependencies, or modify unrelated TVM/VTA execution paths.
- **Never:** Treat subprocess isolation as the fix, skip/xfail the matrix, weaken assertions, or claim the root cause is known without a reproducible causal explanation.

## Success Criteria

- The native failure is reproduced before the fix in a direct in-process pytest test and its root cause is identified and recorded with supporting evidence.
- The same direct in-process test passes after the minimal fix; it must not use a subprocess to execute the matrix.
- The complete V2 deployment module exits 0 with the real in-process LLVM/C TSIM matrix enabled.
- Both host-codegen variants retain 8 partitions, ten output comparisons, and positive simulator cycle counts.
- The production CLI control continues to pass, and focused tests for every changed shared boundary pass.

## Open Questions

- Which concrete executor/runtime ownership or state condition causes the abort remains unresolved; diagnosis must answer this before the fix is selected.
