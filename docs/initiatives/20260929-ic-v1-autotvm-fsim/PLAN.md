# Implementation Plan: IC V1 Single-Layer FSIM AutoTVM Tuning

## Overview

Add two independent command-line capabilities: a V1-local AutoTVM entry point
that tunes one indexed workload with random FSIM search and measures its
selected schedule on TSIM, and a model-independent script that calculates
useful MAC utilization from MAC count, TSIM cycles, and VTA geometry.

## Architecture Decisions

- Keep `tune.py` inside `image_classification_v1/` so its model-specific task
  selection is explicit. Reuse the existing prepared V1 graph and supported
  AutoTVM task extraction path.
- Use the zero-based index in extracted supported workload order as the
  selection contract. Validate the index before opening runners or creating
  output artifacts.
- Use AutoTVM `RandomTuner` with a local FSIM measurement runner by default;
  cap the selected task at 32 trials and each measurement at 120 seconds.
- Measure the best FSIM schedule on TSIM and report its positive TSIM
  `cycle_count`, workload identity, and logical MAC count. Keep backend and
  geometry selection explicit and preserve existing simulator environment
  contracts.
- Keep `scripts/mac_utilization.py` independent from all models and benchmark
  app modules. Accept MAC count and TSIM cycles as inputs and derive peak
  throughput from the configured VTA `LOG_BATCH` and `LOG_BLOCK` fields.
- Write generated AutoTVM artifacts only below ignored build output. Do not
  change model preparation, quantization, routing, or TVM core behavior.

## Task List

### Checkpoint 1: IC V1 Single-Workload FSIM and TSIM Flow

- [ ] Task 1: Implement the `image_classification_v1/tune.py` CLI for
  zero-based workload selection, random FSIM tuning, TSIM measurement of the
  selected schedule, and explicit result reporting. Add focused tests and
  document invocation and prerequisites in the IC V1 README and `scripts/README.md`.

### Checkpoint 1 Verification

- The focused tests cover workload ordering/selection, invalid indices,
  defaults, and association of TSIM cycles with the best FSIM schedule.
- A bounded one-workload invocation uses the selected FSIM and TSIM libraries,
  reports the workload MAC count and TSIM cycles, and writes artifacts only to
  the documented build output location.
- Existing IC V1 untuned command examples remain unchanged.

### Checkpoint 2: Model-Independent MAC Utilization CLI

- [ ] Task 2: Implement `scripts/mac_utilization.py` with validated geometry,
  MAC/cycle inputs, ratio and percentage output, focused tests, and complete
  script documentation in `scripts/README.md`.

### Checkpoint 2 Verification

- Focused tests cover the formula, 64-MAC geometry, input validation, and
  malformed or incomplete configuration.
- A representative CLI invocation prints MAC count, TSIM cycles, peak
  MACs/cycle, utilization ratio, and percentage.
- Inspection confirms the calculator imports no model, AutoTVM log, or
  MLPerf Tiny application module.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Workload extraction order changes as graph preparation evolves. | A saved index could select a different layer. | Print the selected template, workload hash, index, and shape/workload summary before or with the result. |
| The best FSIM schedule cannot be directly reused for a separate TSIM measurement. | The workflow could report cycles for a different config than the one selected. | Preserve the selected config identity explicitly and verify the TSIM path measures that config. |
| FSIM and TSIM have different cost semantics. | Wall time could be mistaken for hardware cycles. | Keep FSIM solely as search signal and report only TSIM profiler `cycle_count` as cycles. |
| Geometry values are stored as log2 fields. | Incorrect peak throughput would invalidate utilization. | Derive dimensions as powers of two and check the standard geometry is 64 MAC/cycle. |
| Calculator inputs may be inconsistent or invalid. | The result could be meaningless. | Require positive integer MAC/cycle counts and validated configuration before calculating. |

## Open Questions

- None. Requirements are confirmed in `INTENT.md` and both module specs.
