# Implementation Plan: VTA Geometry and Backend Decoupling

## Overview

Introduce a canonical `VTA_BACKEND` selector and make the same geometry-only
configuration usable for FSIM and TSIM. Remove legacy simulator target loading,
update build/runtime selection layers, and verify that
benchmark model/partition source remains unchanged.

## Architecture Decisions

- Do not add `VTA_PLATFORM`; backend is the single selector namespace.
- Keep backend selection outside the geometry JSON so one file can build both
  FSIM and TSIM.
- Reject `TARGET=sim`/`TARGET=tsim` at the boundary with an actionable
  migration error; do not maintain compatibility aliases.
- Pass one explicit config path into all CMake targets and hardware generation;
  never hardcode separate FSIM/TSIM geometry files.
- Keep benchmark and partition implementations unchanged.
- Make `--backend fsim|tsim|all` the only documented and supported interface.

## Task List

### Phase 1: Backend contract and configuration normalization

- Task 1: Define and test canonical backend normalization and geometry-only
  config loading, including rejection of legacy target fields.
- Task 2: Convert `vta_64mac.json` to the geometry-only canonical schema while
  preserving all requested values and documenting the legacy-config rejection.

### Checkpoint: Contract

- Valid backends normalize deterministically.
- Invalid backends fail at the boundary with one clear error.
- Legacy `sim`/`tsim` inputs fail with a migration error.
- Geometry ABI/fingerprint is identical regardless of selected backend.

### Phase 2: Build and runtime selection

- Task 3: Update build scripts/CMake invocation to pass one config path and
  select `fsim`, `tsim`, or `all` explicitly.
- Task 4: Update benchmark/runtime backend selection and diagnostics without
  changing model or partition behavior.

### Checkpoint: Backend plumbing

- Same config path is visible in FSIM and TSIM build commands.
- FSIM and TSIM select different libraries/registries without target-value
  coupling.
- Unsupported legacy target flags fail clearly.

### Phase 3: Verification and migration documentation

- Task 5: Run focused backend/config tests and all available MLPerf Tiny
  verification paths; record exact blockers and confirm no benchmark/partition
  source changes.
- Task 6: Update maintained script and benchmark documentation for the new
  backend contract and explicit migration errors.

### Checkpoint: Complete

- FSIM verification is green where prerequisites are present.
- TSIM is green when its toolchain is present, otherwise explicitly blocked.
- FPGA backends remain unchanged and clearly deferred.
- All changes pass final review.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Removing `TARGET` breaks hidden consumers | High | Reject legacy fields with a clear migration error and update all in-repository callers. |
| FSIM/TSIM accidentally use different geometry | High | Compare config paths and ABI fingerprints in build tests. |
| Backend changes leak into model/partition behavior | High | Keep model/partition files out of the write set and run source-diff checks. |
| TSIM remains unavailable due host toolchain | Medium | Separate plumbing tests from hardware execution and record JDK/Verilator blockers. |

## Open Questions

None for the approved FSIM/TSIM phase.
