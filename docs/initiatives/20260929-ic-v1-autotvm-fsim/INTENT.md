# Intent: Single-Layer IC V1 FSIM AutoTVM Tuning

## Confirmed Outcome

Add a command-line workflow under the MLPerf Tiny `image_classification_v1`
application that tunes one selected AutoTVM workload with FSIM, then measures
the chosen schedule with TSIM to obtain its cycle count. Add a model-independent
script under `scripts/` that calculates useful MAC utilization from MAC count,
TSIM cycles, and configured VTA peak MAC throughput.

## User and Why

The VTA benchmark developer wants to tune one IC V1 layer at a time and measure
its cycle cost, then calculate how much of the VTA MAC throughput that layer
uses.

## Confirmed Workflow and Defaults

- Select one workload by its zero-based position in the supported AutoTVM task
  extraction order.
- Search that workload with the AutoTVM random tuner and the local FSIM runner.
- Use 32 trials per workload and a 120-second timeout for each measurement.
- Run the best schedule found by FSIM with TSIM and report its cycle count.
- Compute utilization as `MAC_count / (TSIM_cycles * peak_MACs_per_cycle)`;
  derive peak throughput from the selected VTA geometry configuration.

## Boundaries

- Tune one selected workload per invocation; do not run a whole-model or
  all-workload sweep.
- Keep the utilization calculator model-independent: it accepts MAC count,
  cycle count, and geometry configuration as inputs rather than loading IC V1
  or another model.
- Do not interpret FSIM wall-clock duration as hardware cycles.
- Do not change model weights, quantization, graph partitioning, or TVM core
  behavior.
