# Implementation Plan: VTA 64mac Configuration and MLPerf Tiny Verification

## Overview

Create `vta/config/vta_64mac.json` from the complete current
`vta/config/vta_config.json` schema, changing only the five approved geometry
values, then validate the configuration and run the six checked-in MLPerf Tiny
benchmark suites and available deployment paths with that file selected.

## Architecture Decisions

- Keep the new configuration as a separate JSON file; do not change the
  existing default or sample configurations.
- Preserve all existing fields and values except `LOG_BLOCK`,
  `LOG_UOP_BUFF_SIZE`, `LOG_INP_BUFF_SIZE`, `LOG_WGT_BUFF_SIZE`, and
  `LOG_ACC_BUFF_SIZE`.
- Reuse the existing benchmark runners and test suites instead of adding a new
  deployment framework or changing benchmark code.
- Report unavailable HOST/FSIM/TSIM prerequisites explicitly; do not turn
  environment failures into passing or skipped results.

## Task List

### Phase 1: Configuration

- Task 1: Add and validate the complete `vta_64mac.json` configuration.

### Checkpoint: Configuration

- The JSON parses and loads through the VTA configuration loader.
- All five requested values match exactly.
- A field-by-field comparison confirms only the five approved values differ
  from `vta_config.json`.

### Phase 2: Deployment Verification

- Task 2: Run all MLPerf Tiny focused suites and available deployment paths with
  `vta_64mac.json`, and record the evidence.

### Checkpoint: Complete

- All six benchmark suites pass with the new configuration selected.
- Every locally available documented deployment mode passes, or its missing
  prerequisite is recorded precisely in the verification report.
- No unrelated source, configuration, or generated build output is changed.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| The smaller buffers are incompatible with one benchmark graph | High | Run every focused suite and deployment mode using the new config; stop on the first concrete failure and fix only within approved scope. |
| Required TVM/VTA libraries or simulator tools are absent | Medium | Check prerequisites before execution and record exact blockers instead of masking them. |
| A copied field is accidentally omitted or changed | High | Compare parsed JSON objects and assert the difference set is exactly the five approved keys. |

## Open Questions

None.
