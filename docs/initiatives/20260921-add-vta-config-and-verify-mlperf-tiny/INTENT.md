# Confirmed Intent: VTA 64mac Configuration

## Outcome

Add an independent VTA configuration named `vta_64mac.json` as a complete copy
of `vta_config.json`, changing only the five requested geometry fields.

## Inputs

- Preserve all existing files under `vta/config/` unchanged.
- Copy every field from `vta/config/vta_config.json`; fields not explicitly
  changed must retain their existing values.
- Treat all six benchmark directories currently under
  `vta/apps/mlperf_tiny_benchmark/` as the deployment verification scope.

## Acceptance Direction

- The new file contains `LOG_BLOCK=3`, `LOG_UOP_BUFF_SIZE=12`,
  `LOG_INP_BUFF_SIZE=13`, `LOG_WGT_BUFF_SIZE=14`, and
  `LOG_ACC_BUFF_SIZE=15`.
- The JSON is accepted by the VTA configuration loader.
- Every MLPerf Tiny benchmark can complete its documented deployment path with
  the new configuration when the repository's build prerequisites are present.

## Out of Scope

- Replacing or modifying the current default/sample configurations.
- Changing benchmark model code, runtime code, or shared build scripts.
- Claiming MLPerf accuracy, performance, energy, or submission results.

## Confirmation

The user explicitly requested creation of `vta_64mac.json` on 2026-09-21.
