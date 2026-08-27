# Project Architecture

## Purpose

Describe the system-level architecture and engineering boundaries.

## System Overview

The project is the combination of workspace governance/integration, the TVM
compiler, and VTA hardware/runtime. The workspace coordinates the two
independently versioned source repositories without absorbing their source or
governance. This is a co-development system, not a general-purpose fork of
either source project.

## Components / Major Areas

| Component / Area | Responsibility | Location | Notes |
|---|---|---|---|
| Workspace | Governance, documentation, integration, validation | repository root | Independent Git repository |
| TVM | Compiler source | `tvm/` | Git submodule |
| VTA | Hardware/runtime source | `vta/` | Git submodule |

## Repository Roles

- The workspace owns Codex governance, project documentation, architecture and
  design, integration contracts, cross-repository validation, project-level
  scripts/tests, reproducibility metadata, and the final integrated state.
- `tvm/` owns compiler source and TVM-side compiler/runtime integration changes.
- `vta/` owns accelerator hardware and hardware/runtime-side changes.
- Workspace governance must remain outside both source repositories.

## Development Model

```text
workspace base branch
        ↓
workspace task branch
        ↓
changes may span workspace, tvm/, and vta/
        ↓
repository-local and project-level validation
        ↓
Independent Review
        ↓
ff-only workspace integration
```

TVM and VTA are developable submodules rather than read-only dependencies. A
cross-repository Engineering Task must state which repository owns each change.
Changes to `tvm/` or `vta/` are committed in that repository first; the
workspace then records the reviewed source commit by updating its gitlink. The
workspace commit is the durable record of the final integrated combination.

## Submodule Development Policy

- Before source changes, confirm the current submodule branch and working-tree
  state.
- Use `tvm_v0.17.0` as TVM's default development branch and `vta_v0.0.2` as
  VTA's default development branch, or create a task branch from the applicable
  default. Do not commit formal development directly from detached `HEAD`.
- Branch names describe development intent; workspace gitlinks pin the exact
  source commits used for reproduction.
- A baseline update requires an explicit workspace gitlink update and relevant
  validation.
- A workspace commit must not point to an incidental or unvalidated local
  submodule `HEAD`.

## Dependencies

| Dependency | Used By | Purpose | Version / Tracking |
|---|---|---|---|
| TVM | Workspace integration | Compiler stack | Gitlink `eeebcfa` |
| VTA | Workspace integration | Accelerator hardware/runtime | Gitlink `d4a15f6` |

## Integration Boundaries

| Contract / Interface | Participants | Documentation |
|---|---|---|
| TVM/VTA integration | Workspace, TVM, VTA | `docs/integration/` |

Compiler/hardware interface changes cross a project integration boundary. The
owning source repositories implement their respective sides, while the
workspace defines the reviewed combination and hosts cross-repository evidence.

## Validation Boundary

```text
Repository-local validation
        ↓
Cross-repository integration validation
        ↓
Workspace reproducibility verification
```

- **TVM-local:** relevant TVM build/tests for compiler-side changes.
- **VTA-local:** relevant build, test, or simulation for hardware/runtime-side
  changes.
- **Workspace integration:** verifies that the pinned TVM/VTA combination and
  affected interfaces operate together.
- **Workspace reproducibility:** checks gitlinks, expected baseline/branch
  metadata, clean repository state, documented environment assumptions, and
  project-level commands.

Project-level source-state status and reproducibility verification are
implemented. Build, test, and integration commands are **Planned / Not Yet
Implemented**. Tasks must report the checks actually available and must not
imply that absent coverage has passed.

## Architecture Invariants

- Workspace governance is owned only by the workspace repository.
- TVM and VTA source histories remain independent and contain no workspace governance.
- Submodule gitlinks define reproducible baselines; configured branches are development defaults only.
