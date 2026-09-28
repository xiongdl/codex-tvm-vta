# Spec: Per-Layer VTA MAC Utilization

## Objective

Provide one maintained command-line script that reports the useful MAC
utilization of every VTA Conv/Dense layer occurrence in each of the six MLPerf
Tiny models. The primary consumer is a benchmark developer inspecting the
effect of AutoTVM schedule choices. Success means the script validates its
inputs, maps each supported layer occurrence to a matching TSIM AutoTVM
workload record, calculates utilization with documented units, and writes
machine-readable output.

## Metric and Semantics

For a layer occurrence with `M` logical MACs, best-trial TSIM cost `C` cycles,
and configured peak `P` MACs/cycle:

```text
useful_mac_utilization = M / (C * P)
```

Report both the ratio and percentage. One MAC means one multiply-accumulate;
where AutoTVM records FLOPs, convert FLOPs to MACs by dividing by two. Derive
`P` from the active VTA geometry (`BATCH * BLOCK_IN * BLOCK_OUT`) and reject
configs that cannot be interpreted. Name the field `useful_mac_utilization`
because logical MACs do not count padded lanes or non-MAC simulator cycles.

TSIM currently exposes whole-run cycles, while AutoTVM's TSIM runner records
cycle cost for an isolated task/workload. Therefore `C` is the lowest
successful, integral TSIM trial cost for the layer's workload in the validated
native log. This is a task-level schedule estimate associated with the layer,
not a profiler measurement of that layer inside full-model execution. If a
workload occurs multiple times in a graph, emit one row per occurrence and
reuse its best-trial cost.

## Command

Maintain the script at:

```text
vta/apps/mlperf_tiny_benchmark/mac_utilization.py
```

The command supports one model or all six:

```text
--model MODEL_ID|all                 required
--backend tsim                       required; reject fsim
--config ABS_PATH                    default: repository vta/config/vta_64mac.json
--log PATH --sidecar PATH            required for one model
--summary PATH                       required for --model all; TSIM aggregate summary
--output-dir PATH                    default: benchmark build/autotvm/mac-utilization/
```

`--log` and `--sidecar` are mutually exclusive with `--summary`. For `all`,
the script consumes the existing aggregate TSIM summary and each model's
matching artifact pair; it does not tune or compile models. Output files use a
stable run stem and include one CSV detail file and one JSON metadata summary.

Example commands:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/mac_utilization.py \
  --model image_classification_v1 --backend tsim \
  --log PATH_TO_V1_TSIM_LOG --sidecar PATH_TO_V1_TSIM_JSON

VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/mac_utilization.py \
  --model all --backend tsim --summary PATH_TO_TSIM_AGGREGATE_JSON
```

## Project Structure

- Script: `vta/apps/mlperf_tiny_benchmark/mac_utilization.py`
- Focused tests: `vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py`
- Usage and formula: `scripts/README.md` and
  `vta/apps/mlperf_tiny_benchmark/README.md`
- Default generated output: ignored
  `vta/apps/mlperf_tiny_benchmark/build/autotvm/mac-utilization/`

## Output Contract

CSV has one row per VTA Conv/Dense layer occurrence and at least these fields:

- model id, stable layer ordinal/identity, AutoTVM template, workload hash;
- layer MAC count, best-trial TSIM cycles, peak MACs/cycle;
- utilization ratio and percent;
- source log and sidecar paths/hashes, plus geometry-config hash.

If a useful graph-level layer name cannot be preserved by the existing task
extraction APIs, use a deterministic per-model layer ordinal plus template and
workload hash. Do not silently merge repeated layer occurrences.

The JSON summary records script/schema version, model/backend, metric formula,
geometry identity and peak, validated artifact identities, row count,
unsupported VTA task coverage, and output CSV path. Unsupported task templates
are summarized separately and do not receive fabricated MAC utilization.

## Code Style

Keep record parsing, validation, calculation, and writing in small functions;
reuse the benchmark tuner's existing identity and sidecar validation helpers
instead of duplicating their contracts. A utilization row should retain its
units and source identity:

```python
utilization = mac_count / (best_trial_cycles * peak_macs_per_cycle)
row = {
    "best_trial_cycles": best_trial_cycles,
    "peak_macs_per_cycle": peak_macs_per_cycle,
    "useful_mac_utilization": utilization,
    "useful_mac_utilization_percent": 100.0 * utilization,
}
```

## Validation

Before computing, reject:

- any backend other than TSIM;
- an unknown model or aggregate summary missing any of the six models;
- a log/sidecar model, backend, geometry, or hash mismatch;
- unsuccessful/missing best-trial records for a mapped workload;
- non-positive/non-integral cycle costs, invalid geometry, or unavailable MAC
  counts;
- an ambiguous mapping between graph occurrences and logged workloads.

The script must use the existing prepared Relay graph and AutoTVM extraction
path without importing AutoTVM into any `model_pipeline.py`. It must not load
weights differently, tune schedules, modify model state, or change runtime
behavior.

## Testing Strategy

Use focused tests with synthetic task/log/sidecar data for the formula, peak
derivation, duplicate workload occurrences, deterministic identities, and each
rejection path. Validate the six-model mapping against prepared graphs and
native TSIM AutoTVM logs. Run a bounded smoke report for one model and for all
six models, then inspect CSV and JSON pairing. Tests and commands must use the
existing `.envs/tvm-vta-env` project environment; do not create or replace it.

Focused tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" VTA_BACKEND=tsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest \
  vta/apps/mlperf_tiny_benchmark/tests/test_mac_utilization.py
```

## Boundaries

- **Always:** use matched native TSIM logs and sidecars; preserve per-occurrence
  rows; report units and the isolated-task estimate semantics; write generated
  reports under ignored build output by default.
- **Ask first:** changing the utilization formula, modifying model/runtime or
  TVM core for new profiling instrumentation, adding dependencies, or changing
  the supported model set.
- **Never:** claim the estimate is FPGA utilization, label FSIM cost as TSIM
  cycles, or alter weights/quantization to make the result look better.

## Success Criteria

- One invocation can report each of the six models from validated TSIM
  aggregate artifacts, and one-model mode can report a matching single pair.
- Every mapped VTA Conv/Dense occurrence has a deterministic row with valid
  MAC count, best-trial TSIM cycles, geometry peak, and a correct ratio.
- Repeated same-workload occurrences remain separate while referencing the
  same workload record.
- All input mismatch and unsupported/ambiguous cases fail clearly.
- Focused unit tests and bounded one-model/all-model report generation pass.

## Open Questions

- None. CLI defaults and stable ordinal identities are implementation details
  chosen to preserve the confirmed output contract.
