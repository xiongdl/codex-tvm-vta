# Spec: VTA 64mac Configuration and MLPerf Tiny Deployment Verification

## Assumptions

1. `vta_64mac.json` belongs under `vta/config/` beside the existing VTA JSON
   configurations.
2. The requested file is an exact field-preserving copy of `vta_config.json`,
   except for the five requested geometry fields.
3. “All MLPerf Tiny benchmarks” means the six currently checked-in benchmark
   applications: anomaly detection v1, image classification v1 and v2,
   keyword spotting v1, streaming wakeword v1, and visual wake words v1.
4. Existing focused tests and documented HOST/FSIM/TSIM runners are the source
   of truth for deployment verification; hardware-specific execution is only
   possible when the documented libraries and tools are available.

## Objective

Add `vta/config/vta_64mac.json` without changing existing VTA configurations.
The file must contain every field from `vta/config/vta_config.json`, with only
the requested geometry changed: block size 3, UOP buffer size 12, input buffer
size 13, weight buffer size 14, and accumulator buffer size 15. Use the file to
verify each checked-in MLPerf Tiny benchmark through its existing deployment
tests and documented runtime paths.

## Tech Stack

- JSON configuration consumed by `vta.config.vta_config`.
- Python from `.envs/tvm-vta-env/bin/python`.
- Checked-out TVM and VTA Python packages under `tvm/python` and `vta/python`.
- Existing MLPerf Tiny pytest suites and HOST/FSIM/TSIM deployment runners.

## Commands

Configuration validation:

```bash
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -c \
  'import json, pathlib; from vta.config import vta_config; p=pathlib.Path("vta/config/vta_64mac.json"); json.load(p.open()); env=vta_config.load_vta_config(str(p)); assert env.LOG_BLOCK == 3; assert env.LOG_UOP_BUFF_SIZE == 12; assert env.LOG_INP_BUFF_SIZE == 13; assert env.LOG_WGT_BUFF_SIZE == 14; assert env.LOG_ACC_BUFF_SIZE == 15'
```

Focused benchmark tests, with the new configuration selected where the test
process reads `VTA_CONFIG_FILE`:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest \
  vta/apps/mlperf_tiny_benchmark/*/tests
```

When the built libraries and toolchain are available, run each benchmark's
documented HOST and FSIM deployment commands with
`VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json"`; run TSIM similarly only
after building `libvta_hw` and confirming the new configuration is compatible
with the TSIM target.

## Project Structure

```text
vta/config/vta_64mac.json
docs/initiatives/20260921-add-vta-config-and-verify-mlperf-tiny/
├── INTENT.md
└── SPEC.md
vta/apps/mlperf_tiny_benchmark/*/tests/
```

Generated benchmark artifacts remain in each benchmark's ignored `build/`
directory and must not be committed.

## Code Style

Follow the existing VTA configuration JSON layout, including uppercase field
names and the repository's spacing style:

```json
{
  "TARGET" : "sim",
  "HW_VER" : "0.0.2",
  "LOG_INP_WIDTH" : 3,
  "LOG_WGT_WIDTH" : 3,
  "LOG_ACC_WIDTH" : 5,
  "LOG_BATCH" : 0,
  "LOG_BLOCK" : 3,
  "LOG_UOP_BUFF_SIZE" : 12,
  "LOG_INP_BUFF_SIZE" : 13,
  "LOG_WGT_BUFF_SIZE" : 14,
  "LOG_ACC_BUFF_SIZE" : 15
}
```

The final file must also retain the existing width and batch fields required by
the loader.

## Testing Strategy

- Parse the JSON and load it through the VTA configuration loader.
- Assert all five requested values exactly and assert existing configurations
  remain unchanged.
- Run the six benchmark test directories with `pytest` using the new config.
- If build prerequisites exist, run the documented HOST/FSIM deployment paths
  for all six benchmarks and TSIM paths where the required hardware library is
  available. Record any environment-only blocker precisely rather than hiding
  it with a skip.

## Boundaries

- Always: preserve existing configs, use the project Python environment, run
  focused validation before committing, and keep generated artifacts ignored.
- Ask first: changing shared benchmark scripts, changing the default config,
  adding dependencies, or changing benchmark behavior.
- Never: edit TVM/VTA vendor source for this config-only request, weaken tests,
  or commit local environments/generated build outputs.

## Success Criteria

1. `vta/config/vta_64mac.json` exists and loads successfully.
2. Its five requested numeric fields equal `3`, `12`, `13`, `14`, and `15`.
3. Existing VTA configuration files are unchanged.
4. All six MLPerf Tiny benchmark test suites pass with the new config selected.
5. All deployment modes supported by the available local prerequisites pass,
   with unavailable modes reported as explicit environment blockers.

## Open Questions

None; the user requested the file be generated for inspection before further
verification.
