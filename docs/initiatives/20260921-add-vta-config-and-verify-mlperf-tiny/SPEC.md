# Spec: VTA Geometry Configuration and Backend Decoupling

## Assumptions

1. `vta_64mac.json` remains under `vta/config/` and contains geometry/data
   parameters, not a simulator-specific target.
2. `VTA_BACKEND` is the canonical external selector. Supported values in this
   change are `fsim` and `tsim`; `pynq`, `zcu104`, and other FPGA values are
   reserved for later backend migrations.
3. `host` remains a benchmark execution mode for the CPU reference graph and
   is not a VTA backend.
4. `TARGET=sim` and `TARGET=tsim` are not supported by the new contract; old
   configurations must fail clearly and instruct callers to use `VTA_BACKEND`.
5. The six checked-in MLPerf Tiny applications remain verification consumers,
   but their model and partition implementations are out of scope.

## Objective

Make VTA geometry reusable across FSIM and TSIM. Remove the current coupling in
which `TARGET=sim`/`TARGET=tsim` is embedded in configuration files and build
scripts choose different geometry files for the two simulator backends. The
same `vta_64mac.json` must be selectable with `VTA_BACKEND=fsim` or
`VTA_BACKEND=tsim`; backend-specific libraries and registries remain distinct.

## Contract

Canonical selection:

```text
VTA_CONFIG_FILE=/absolute/path/to/vta_64mac.json
VTA_BACKEND=fsim|tsim
```

The configuration file contains the geometry contract, including:

```json
{
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

`TARGET` must not be used to distinguish FSIM from TSIM. Files containing
`TARGET=sim` or `TARGET=tsim` are rejected by the new loader with a clear
migration error directing callers to `VTA_BACKEND=fsim` or `VTA_BACKEND=tsim`.
Legacy FPGA target values are outside this migration and remain untouched.

## Backend behavior

| Backend | Library/artifacts | Current scope |
|---|---|---|
| `fsim` | `libvta_fsim`, `tvm_vta_ext` | Implement and verify |
| `tsim` | `libvta_tsim`, `libvta_hw`, Chisel/Verilator artifacts | Implement selection/build plumbing; verify when JDK/toolchain exists |
| `pynq`, `zcu104`, ... | Existing FPGA drivers and bitstreams | Preserve for later migration |

The backend is not included in the geometry ABI fingerprint. Two backend
libraries built from the same geometry must use the same VTA geometry/ABI
values while exposing backend-specific runtime registries.

## Tech Stack

- JSON configuration and Python VTA environment loader.
- Bash/CMake build and test entry points.
- Python MLPerf Tiny runners with existing `--simulator fsim|tsim` behavior
  migrated to the canonical backend contract.
- Existing C++ FSIM/TSIM runtimes and Verilator/Chisel hardware model.

## Commands

Canonical build interface:

```bash
bash scripts/build_vta_lib.sh \
  --config "$PWD/vta/config/vta_64mac.json" \
  --backend all
```

Selective build:

```bash
bash scripts/build_vta_lib.sh \
  --config "$PWD/vta/config/vta_64mac.json" \
  --backend fsim
```

Canonical runtime selection:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_64mac.json" \
VTA_BACKEND=fsim \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/keyword_spotting_v1/run.py \
  --simulator fsim --host-codegen all
```

The existing `--target libvta_fsim` style is removed from the active interface;
documentation and tests use `--backend` and `fsim`.

## Project Structure

```text
vta/config/vta_64mac.json
vta/python/vta/environment.py
vta/config/pkg_config.py
scripts/build_vta_lib.sh
scripts/test_vta_byoc.sh
scripts/test_vta_tsim.sh
vta/apps/mlperf_tiny_benchmark/*/runtime.py
vta/apps/mlperf_tiny_benchmark/*/run.py
```

Generated build artifacts remain ignored and are not committed.

## Code Style and interface rules

- Use `fsim` consistently in public CLI, environment variables, artifact
  directory names, diagnostics, and documentation.
- Use one backend normalization function at the configuration/runtime boundary;
  do not scatter `sim`/`tsim` aliases through benchmark code.
- Validate `VTA_BACKEND` at process/build boundaries and report one consistent
  error listing supported values.
- Keep geometry fields and backend selection separate in fingerprints,
  manifests, and cache keys.
- Backend-specific runtime sessions may require different registries, but they
  consume the same geometry environment.

## Testing Strategy

- Unit-test backend normalization, invalid values, rejection of legacy target
  fields, and the guarantee that backend choice does not change geometry/ABI
  fingerprint.
- Test build command selection: `fsim`, `tsim`, and `all` pass the same config
  path; FPGA backend names are rejected or explicitly reported unsupported in
  this phase.
- Run focused configuration and backend tests before each implementation
  commit.
- Rebuild FSIM with `vta_64mac.json` and run all six benchmark suites/modes
  that are available.
- Run TSIM only after a usable JDK, Verilator, Chisel build, and matching
  `libvta_tsim/libvta_hw` exist. Record blockers precisely.
- Do not loosen benchmark/partition topology assertions or alter model graphs
  to make this migration green.

## Boundaries

- Always: preserve geometry values, keep backend selection explicit, reject
  legacy target fields clearly, test ABI consistency, and keep build outputs
  ignored.
- Ask first: implementing FPGA backends, adding dependencies, changing
  model/partition logic, or changing CI policy.
- Never: silently map an unknown backend, make TSIM use an FSIM library, or
  report a blocked backend as passed.

## Success Criteria

1. `vta_64mac.json` is geometry-only and retains the five requested values.
2. `VTA_BACKEND=fsim` and `VTA_BACKEND=tsim` select backend behavior without
   changing the geometry ABI.
3. Default build selection can generate both FSIM and TSIM artifacts from the
   same config path; selective backend builds work.
4. `TARGET=sim`/`TARGET=tsim` are rejected with an actionable migration error.
5. Benchmark/partition source is unchanged by this migration.
6. Available FSIM verification passes; TSIM results are either passing with a
   matching toolchain or explicitly blocked with actionable evidence.

## Open Questions

None for the current FSIM/TSIM migration. FPGA backend semantics are deferred.
