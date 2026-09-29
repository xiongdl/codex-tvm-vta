# Spec: IC V1 Single-Workload FSIM AutoTVM Tuning

## Objective

Provide a focused command for tuning one supported VTA AutoTVM workload
extracted from MLPerf Tiny Image Classification V1. A benchmark developer can
select a zero-based workload index, run random search on FSIM with bounded
defaults, then run the selected best schedule with TSIM and see its cycle
count. The flow must identify the selected workload and its logical MAC count
so the separate model-independent calculator can use those inputs.

## Tech Stack

Reuse the repository's V1 model preparation pipeline, shared AutoTVM task
extraction and simulator runner helpers, TVM AutoTVM random tuner, VTA FSIM and
TSIM backends, and the existing `.envs/tvm-vta-env` environment. Use the
configured geometry at `vta/config/vta_64mac.json` unless the existing VTA
configuration contract supplies another explicit path.

## Command

Maintain the entry point at:

```text
vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py
```

It accepts a required zero-based workload index and optional output location.
The defaults are random search, local runner, 32 trials for the selected
workload, and 120 seconds per measurement. Invalid, negative, and out-of-range
indices fail with an error that reports the valid workload range. The command
uses the existing explicit `VTA_CONFIG_FILE` and backend environment contract;
the workflow must clearly require any backend selection needed for its FSIM
search and TSIM measurement.

Example shape (final option spelling is selected during implementation):

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py \
  --workload-index 0
```

## Project Structure

- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tune.py`: focused
  single-workload command.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/`:
  selection, defaults, error paths, FSIM-to-TSIM result association, and output
  contract checks.
- `vta/apps/mlperf_tiny_benchmark/image_classification_v1/README.md` and
  `scripts/README.md`: maintained command usage and prerequisites.
- Default generated AutoTVM artifacts: ignored build output under the existing
  MLPerf Tiny benchmark `build/autotvm/` tree.

## Code Style

Keep task enumeration, index validation, tuning, TSIM measurement, and result
formatting in small functions. Reuse shared V1 preparation and simulator
helpers rather than copying model logic. Keep units explicit in user-facing
output:

```python
result = {
    "workload_index": workload_index,
    "workload_sha256": workload_sha256,
    "mac_count": logical_mac_count,
    "tsim_cycles": cycle_count,
}
```

## Testing Strategy

- Focused tests verify stable zero-based workload selection, the 32-trial and
  120-second defaults, and clear invalid-index failures.
- A controlled runner test verifies that FSIM search selects the schedule
  subsequently measured by TSIM and that the reported cycle count is from
  TSIM, not FSIM wall-clock time.
- A bounded integration run selects one IC V1 workload, tunes it with FSIM,
  and confirms the TSIM cycle result and MAC count are emitted.
- Commands use the existing project environment and built FSIM/TSIM libraries;
  do not bootstrap or replace the environment as part of the command.

## Boundaries

- **Always:** use the prepared IC V1 graph and shared supported-task
  extraction; make the workload index and identity visible; use random search,
  local runner, 32 trials, and 120 seconds by default; measure the selected
  schedule with TSIM and label the resulting cycles explicitly.
- **Ask first:** change the selected model, default search policy, default
  trial/timeout values, VTA geometry contract, or existing graph preparation.
- **Never:** tune every workload implicitly, report FSIM elapsed time as
  TSIM cycles, change model assets or quantization, or weaken existing runtime
  correctness behavior.

## Success Criteria

- A caller can select exactly one supported IC V1 workload by zero-based
  extraction index; invalid selections fail before measurement.
- The default run uses AutoTVM random search, a local FSIM runner, 32 trials,
  and a 120-second per-measurement timeout.
- The best selected FSIM schedule is measured on TSIM and its positive cycle
  count is clearly associated with the selected workload.
- Output includes the workload identity and logical MAC count needed by the
  generic utilization calculator.
- Existing untuned IC V1 commands and behavior remain usable.

## Open Questions

- None. Exact CLI option names and artifact naming are implementation details.
