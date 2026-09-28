# Intent: Per-Layer VTA MAC Utilization

## Confirmed Outcome

Add a maintained script that reports per-layer MAC utilization for the six
MLPerf Tiny models in this repository. The report covers each VTA Conv/Dense
layer occurrence, uses the matching TSIM AutoTVM best-trial cycle cost for its
workload, and writes CSV detail plus a JSON summary.

## User and Why

The benchmark developer needs to see which VTA compute layers use the available
MAC throughput efficiently after schedule tuning, so low-utilization layers
can guide later optimization.

## Confirmed Metric

For each layer occurrence:

```text
MAC utilization = layer MAC count / (best-trial TSIM cycles * peak MACs per cycle)
```

Use `vta/config/vta_64mac.json` to derive peak MACs per cycle. Count one
multiply-accumulate as one MAC. Take the cycle cost from the best successful
TSIM AutoTVM record matching that workload. Repeated graph occurrences of one
workload are separate rows and reference the same best-trial record.

## Boundaries

- Include the six current MLPerf Tiny benchmark models and VTA Conv/Dense
  layer occurrences.
- Validate model, TSIM backend, geometry, native log, and JSON sidecar pairing.
- Report the result as an estimate based on an isolated AutoTVM task trial;
  it is not an end-to-end per-layer profiler reading, FPGA measurement, or
  official MLPerf result.
- Do not modify model graphs, weights, quantization, TVM core, or the existing
  tuning and deployment behavior.
