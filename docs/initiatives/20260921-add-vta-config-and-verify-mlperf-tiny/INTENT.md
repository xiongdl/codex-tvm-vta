# Confirmed Intent: VTA Backend and Configuration Decoupling

## Outcome

Decouple VTA hardware geometry configuration from runtime/build backend
selection. Use one canonical backend selector whose values are `fsim`, `tsim`,
and future FPGA backends such as `pynq` and `zcu104`.

## Inputs

- Keep `vta_64mac.json` as the requested geometry configuration:
  `LOG_BLOCK=3`, `LOG_UOP_BUFF_SIZE=12`, `LOG_INP_BUFF_SIZE=13`,
  `LOG_WGT_BUFF_SIZE=14`, and `LOG_ACC_BUFF_SIZE=15`.
- Do not introduce `VTA_PLATFORM`.
- Use `VTA_BACKEND` (and matching CLI options) as the single backend selector.
- Implement `fsim` and `tsim` now; leave FPGA backend behavior for a later
  migration without changing benchmark/partition algorithms in this task.

## Acceptance Direction

- The same geometry configuration can build both FSIM and TSIM artifacts.
- Backend selection is explicit and consistent across configuration loading,
  library building, benchmark runners, and verification scripts.
- `sim` is no longer the canonical user-facing name; `fsim` is used
  consistently.
- `TARGET=sim`/`TARGET=tsim` are removed from the active contract; callers must
  select a backend explicitly through `VTA_BACKEND` or the canonical CLI flag.
- No benchmark model or partition implementation is changed to hide geometry
  incompatibilities.

## Out of Scope

- Implementing or validating FPGA backends such as `pynq` and `zcu104`.
- Changing benchmark models, partition algorithms, or topology expectations to
  force a pass.
- Installing a JDK or changing the host environment outside the repository.
- Claiming all MLPerf Tiny deployment modes pass before the required backend
  artifacts and toolchains exist.

## Confirmation

The user approved this decoupled-backend direction on 2026-09-21.
