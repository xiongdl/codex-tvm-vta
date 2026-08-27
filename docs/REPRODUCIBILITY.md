# Reproducibility

## Supported Environment

## Dependencies

Source baselines:

```text
Template: https://github.com/xiongdl/codex-template, template/, main, 37a4d227d0820c733be2bbb9bdfed6d9ec9823a0
TVM:      https://github.com/xiongdl/tvm.git, tvm_v0.17.0, eeebcfa0ad4a6e9d49cce3ee6718ecbef0ee018f
VTA:      https://github.com/xiongdl/vta.git, vta_v0.0.2, d4a15f627d5cc9762a82270d1be60a136e6af9c2
```

Clone with submodules or run `git submodule update --init --recursive` after
cloning. Branch metadata identifies the default development branches; the
workspace gitlinks are authoritative for reproduction.

The branch metadata is a development default, not a floating version selector.
Reproduction uses the exact gitlink commits recorded by the workspace. A
baseline change must update the relevant gitlink explicitly and must not record
an incidental, unvalidated local submodule `HEAD`.

## Reproducibility Boundary

Workspace reproducibility verification is expected to cover:

- workspace and submodule gitlinks,
- expected source baseline and default-branch metadata,
- clean workspace, TVM, and VTA working trees,
- documented toolchain, dependency, and environment assumptions, and
- the available project-level setup/build/test/status/verify commands.

This layer complements, but does not replace, TVM-local, VTA-local, and
cross-repository integration validation.

## Project Lifecycle Contract

The intended common interface is:

| Command | Contract |
|---|---|
| `setup` | Prepare or check the project development environment and required dependencies. |
| `build` | Build the required TVM, VTA, and project integration targets. |
| `test` | Run project-relevant unit, functional, and integration tests. |
| `status` | Report workspace, submodule, baseline, and environment readiness. |
| `verify` | Run the required reproducibility and project validation gates. |

These operations are **Planned / Not Yet Implemented**. The current
`scripts/project` is a template stub: `help` documents suggested operations,
while project commands report that they are not configured. The sections below
state the future entry points, not currently passing procedures.

## Setup

**Status: Planned / Not Yet Implemented**

```bash
./scripts/project setup
```

## Build

**Status: Planned / Not Yet Implemented**

```bash
./scripts/project build
```

## Test

**Status: Planned / Not Yet Implemented**

```bash
./scripts/project test
```

## Verify

**Status: Planned / Not Yet Implemented**

```bash
./scripts/project verify
```

## Configuration

Required configuration, environment variables, defaults, generated
configuration, and secret-handling expectations have not yet been
characterized.

## Artifacts

Generated outputs, source-controlled artifacts, external assets, and temporary
outputs have not yet been characterized.

## Reproducing Important Results

No project-level reproducible result procedure has yet been established.

## Known Reproducibility Gaps

- Build and test dependencies are not yet characterized at workspace level.
- Project-specific setup, build, and test commands are not yet implemented.
