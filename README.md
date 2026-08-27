# Codex TVM/VTA Workspace

This repository is the project-level workspace for integrating and validating
TVM and VTA. The compiler and accelerator sources remain independent upstream
repositories included here as Git submodules.

## Repository Layout

- `tvm/` — TVM compiler source submodule
- `vta/` — VTA hardware/runtime source submodule
- `docs/` — project architecture, design, decisions, and status
- `integration/` — cross-repository integration assets and tests
- `scripts/` and `tests/` — project-level automation and validation
- `.ai/`, `AGENTS.md`, and `CHATGPT.md` — workspace engineering governance

Workspace governance files must not be added to the TVM or VTA repositories.

## Project Baseline

```text
Template source:
  repository: https://github.com/xiongdl/codex-template
  path: template/
  branch: main
  commit: 37a4d227d0820c733be2bbb9bdfed6d9ec9823a0

TVM:
  repository: https://github.com/xiongdl/tvm.git
  default branch: tvm_v0.17.0
  baseline commit: eeebcfa0ad4a6e9d49cce3ee6718ecbef0ee018f

VTA:
  repository: https://github.com/xiongdl/vta.git
  default branch: vta_v0.0.2
  baseline commit: d4a15f627d5cc9762a82270d1be60a136e6af9c2
```

The submodule gitlinks, rather than branch names, define the reproducible source
baseline. The workspace was instantiated from the recorded template baseline.

## Engineering Goals

Projects instantiated from this template should progressively become:

- Modular
- Extensible
- Testable
- Automated
- Reproducible
- Traceable
- Maintainable
- AI-operable

## Core Workflow

> Understand → Design → Decide → Plan → Implement → Verify → Record → Review → Evolve

## Standard Engineering Entry Point

Where practical:

```bash
./scripts/project setup
./scripts/project build
./scripts/project test
./scripts/project verify
./scripts/project clean
./scripts/project status
```

Human users, Codex, and CI should prefer the same project entry points.

## Verification Hierarchy

```text
components/<component>/tests/
        │
        └── Component-local tests

integration/tests/
        │
        └── Cross-component tests

tests/
        │
        └── Project-level / End-to-End tests
```

A test should live at the narrowest level that fully validates the intended behavior.


## Project Entry Points

```text
README.md   → Human entry point
CHATGPT.md  → ChatGPT explicit bootstrap entry point
AGENTS.md   → Codex entry point
```

Shared AI policy lives under `.ai/`.

The workflow uses ChatGPT as Design Owner, Codex A as Implementation Owner, and Codex B as read-only Review Owner. See `.ai/AI_HANDOFF_PROTOCOL.md` and `.ai/GIT_WORKFLOW.md`; use the four artifact templates for Task, Review Prompt, Review Report, and Engineering Result handoffs.

## Project Versioning

Instantiated projects include:

```text
VERSION
CHANGELOG.md
docs/VERSIONING.md
```

The default version for a new project is `0.1.0`.

Existing projects must preserve and reconcile their existing authoritative versioning rather than being reset.

## AI Task Readiness

Before substantive work, AI agents apply `.ai/TASK_READINESS.md`.

```text
PASS     → continue silently
WARNING  → report risk and continue
BLOCKED  → stop substantive work
```
