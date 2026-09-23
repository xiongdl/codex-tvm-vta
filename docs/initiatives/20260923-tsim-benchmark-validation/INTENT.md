# Intent: TSIM Benchmark Validation

- **Outcome:** Make all six MLPerf Tiny benchmarks pass TSIM deployment, and fix the separate `test_benchmark_gemm` TVM storage bound failure.
- **User:** Developers validating VTA TSIM benchmark deployments.
- **Why now:** The checkpoint3 run showed three benchmark preflight assertions rejecting the actual model structure, while the GEMM benchmark independently hits a TVM storage bound error.
- **Success:** VWW and image classification v2 validate their observed 13 and 8 partition symbols; anomaly detection validates its actual convolution structure; all six TSIM benchmark deployment runs pass; and `test_benchmark_gemm` passes its storage bound check.
- **Scope:** Inspect and adjust benchmark partition/model structural checks only where they conflict with the model artifacts; diagnose and fix the GEMM storage bound issue at its source; run the narrowest validations that establish these criteria.
- **Always:** Preserve checks that validate real deployment assumptions and keep the distinction between benchmark preflight and TSIM deployment explicit in results.
- **Ask first:** Any broader model changes, TVM/VTA submodule changes outside the identified GEMM issue, or changes to benchmark scope and success criteria.
- **Never:** Claim a benchmark passed TSIM deployment if it did not reach and complete the TSIM deployment step.
