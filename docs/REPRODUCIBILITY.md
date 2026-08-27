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

## Setup

```bash
./scripts/project setup
```

## Build

```bash
./scripts/project build
```

## Test

```bash
./scripts/project test
```

## Verify

```bash
./scripts/project verify
```

## Configuration

Document required configuration, environment variables, defaults, generated configuration, and secret-handling expectations.

## Artifacts

Document generated outputs, source-controlled artifacts, external assets, and temporary outputs.

## Reproducing Important Results

## Known Reproducibility Gaps

- Build and test dependencies are not yet characterized at workspace level.
- Project-specific setup, build, and test commands are not yet implemented.
