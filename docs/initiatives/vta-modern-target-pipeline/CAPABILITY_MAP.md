# Capability Map: Standalone VTA Modern Compiler Pipeline
## Goal

Migrate VTA from the classic per-function `relay.ext.vta` compiler callback to
the modern two-stage `RelayToTIR -> TIRToRuntime` lifecycle while keeping all
VTA-specific compiler integration in the standalone `vta/` project.

The pinned `tvm/` checkout remains unmodified. VTA builds and loads a compiler
plugin library which registers its TargetKind and TVM hooks at runtime using
TVM's public C++ extension interfaces.

## Modules

| Module id | Responsibility | Depends on |
|---|---|---|
| `vta-compiler-plugin` | Build and load a standalone VTA compiler plugin that registers the `vta` TargetKind and modern hook boundary | — |
| `vta-relay-to-tir` | Convert all `Compiler="vta"` Relay functions in an IRModule into scheduled VTA PrimFuncs | `vta-compiler-plugin` |
| `vta-tir-to-runtime` | Compile VTA TIR IRModules into importable and serializable runtime modules | `vta-relay-to-tir` |
| `vta-byoc-migration` | Atomically switch the public target/build lifecycle, retire the classic callback, document migration, and gate FSIM/TSIM | `vta-tir-to-runtime` |

## Build Order

```text
vta-compiler-plugin
  -> vta-relay-to-tir
  -> vta-tir-to-runtime
  -> vta-byoc-migration
```

## Ownership Boundary

- VTA-specific C++, Python, CMake, tests, and documentation live under `vta/`
  or repository-level VTA automation.
- `tvm/` is a pinned upstream dependency and must remain clean.
- The compiler plugin links against the built TVM compiler library; it is
  separate from FSIM, TSIM, and hardware runtime libraries.
- Loading the plugin registers TargetKind/hooks into the current compiler
  process. Runtime-only deployments do not require compiler registration.
- If public TVM APIs cannot support the plugin cleanly, stop and propose a
  generic upstream extension API; do not add VTA-specific code to TVM.

## Stable Contracts

- Relay compiler identity remains `vta`.
- Runtime device identity remains `kDLExtDev`; execution continues to use
  `ext_dev(0)` and the existing VTA DeviceAPI.
- The future canonical Target retains `device=vta`, keys `vta,cpu`, and model
  metadata for AutoTVM and existing deployment consumers.
- `partition_for_vta()` remains source- and behavior-compatible.
- Existing VTA TOPI schedules, TIR passes, constants, and unpacked host ABI
  remain authoritative.
- Operator coverage does not expand during this architecture migration.

## Migration Policy

The plugin and both modern stages are built and proven before public cutover.
The classic callback remains the active path at every intermediate checkpoint.
`vta.register_byoc()` evolves into an idempotent plugin/hook loader and is not
removed until all repository consumers have migrated and a separate removal is
approved.

## Acceptance Evidence

- `git -C tvm status --short` is empty throughout the initiative.
- Plugin build/load tests prove registration ownership and clear missing-library
  diagnostics.
- Relay-to-TIR tests cover symbols, targets, constants, multiple partitions,
  host fallback, and malformed input.
- TIR-to-runtime tests cover runtime symbols, serialization, and loading.
- FSIM and TSIM execute exported modern-pipeline artifacts with numerical
  equality and non-zero accelerator activity.
- No active build path depends on bare `relay.ext.vta` after final cutover.

## Non-Goals

- Embedding VTA under `tvm/src/relay/backend/contrib/`.
- Changing TVM core or adding VTA-specific TVM CMake options.
- Expanding supported operators or redesigning AutoTVM/MetaSchedule.
- Changing VTA RPC, bitstream programming, instruction semantics, or runtime
  device type.
- Adding third-party dependencies.
