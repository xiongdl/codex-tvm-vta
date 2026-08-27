# Project Architecture

## Purpose

Describe the system-level architecture and engineering boundaries.

## System Overview

The workspace coordinates two independently versioned source repositories.
Project policy, documentation, automation, integration, and validation live at
the workspace level; product source remains in the submodules.

## Components / Major Areas

| Component / Area | Responsibility | Location | Notes |
|---|---|---|---|
| Workspace | Governance, documentation, integration, validation | repository root | Independent Git repository |
| TVM | Compiler source | `tvm/` | Git submodule |
| VTA | Hardware/runtime source | `vta/` | Git submodule |

## Dependencies

| Dependency | Used By | Purpose | Version / Tracking |
|---|---|---|---|
| TVM | Workspace integration | Compiler stack | Gitlink `eeebcfa` |
| VTA | Workspace integration | Accelerator hardware/runtime | Gitlink `d4a15f6` |

## Integration Boundaries

| Contract / Interface | Participants | Documentation |
|---|---|---|
| TVM/VTA integration | Workspace, TVM, VTA | `docs/integration/` |

## Architecture Invariants

- Workspace governance is owned only by the workspace repository.
- TVM and VTA source histories remain independent and contain no workspace governance.
- Submodule gitlinks define reproducible baselines; configured branches are development defaults only.
