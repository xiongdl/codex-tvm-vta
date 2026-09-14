# Spec: ResNet8 Graph Artifact Bundle

Module id: `graph-artifact-bundle`

## Objective

Persist every ResNet-8 Graph Executor build as an inspectable and reloadable
artifact bundle instead of leaving only a dynamic library in the application
`build/` directory. A bundle keeps the Graph JSON, serialized parameters,
runnable host library, and every available generated host-source module
together. It provides the artifact boundary used later by LLVM/C FSIM and TSIM
execution without changing model semantics, codegen selection, or simulator
behavior itself.

Success means a user can inspect the generated LLVM or C source in the build
tree and a fresh loader can reconstruct and execute the Graph Executor solely
from the bundle plus the normal TVM/VTA runtime dependencies.

## Source Basis

This specification targets the repository-pinned TVM `v0.17.0` checkout.

- `GraphExecutorFactoryModule` exposes `get_graph_json()`, `get_params()`, and
  `get_lib()` independently in
  `tvm/python/tvm/relay/backend/executor_factory.py`.
- `runtime.Module.get_source(fmt)` exposes source when the module type supports
  it, while `export_library()` compiles DSO-exportable LLVM/C modules and their
  import tree in `tvm/python/tvm/runtime/module.py`.
- TVM's documented Model Library Format separates executor configuration,
  parameters, source, and metadata in `tvm/docs/arch/model_library_format.rst`.
  This module uses the same separation principles but does not claim to emit
  standard MLF.

## Artifact Contract

Each Graph Executor artifact is exported into one exact directory supplied by
its caller:

```text
<artifact-dir>/
  manifest.json
  graph.json
  params.bin
  model.<platform-shared-library-suffix>
  source/
    00-<module-type>.<source-format>
    01-<module-type>.<source-format>
    ...
```

The later simulator-matrix modules assign directories such as
`build/llvm-fsim/reference/` and `build/llvm-fsim/mixed/`. This module does not
hard-code variant names.

`graph.json` is the exact string returned by `factory.get_graph_json()`.
`params.bin` is the exact byte sequence returned by
`relay.save_param_dict(factory.get_params())`. `model.<suffix>` is exported by
the standard TVM module API and then reloaded before the bundle is accepted.

The source directory recursively walks the factory library's module import tree
in stable pre-order. Every module for which source is available is written once.
LLVM modules are requested as LLVM IR (`ll`); C source modules use their declared
`c`, `cc`, or `cpp` format. A module that legitimately has no source does not
fail export, but its type and absence reason are recorded in the manifest. An
empty source directory is an error for the ResNet LLVM and C callers introduced
by this initiative.

The bundle contains generated host code. It does not contain a standalone VTA
instruction blob: VTA instructions and micro-ops continue to be materialized by
the runtime command queue during execution.

## Manifest Contract

`manifest.json` is UTF-8 JSON with stable key ordering and schema version `1`.
It records at least:

- artifact name and `reference` or `mixed` role;
- model SHA-256 and deterministic VTA symbol list supplied by the caller;
- requested host codegen and simulator labels supplied by the caller;
- platform shared-library suffix;
- ordered source entries with module type, source format, relative path, and
  SHA-256;
- relative paths and SHA-256 values for the graph, parameters, and library;
- whether the reloaded library implements every expected VTA symbol.

The manifest must not contain absolute workspace paths, timestamps, temporary
directory names, Python object identities, or other machine-specific noise.
Repeated equivalent builds in the same supported environment must produce the
same graph, parameter, and source content. The manifest has stable schema and
key ordering, but its recorded library SHA-256 may differ when the platform
linker adds non-deterministic metadata; byte-identical DSO output is not
required.

## Python Interface

Artifact persistence is implemented as a focused application-local helper. Its
public application interface accepts:

```python
export_graph_bundle(
    factory,
    output_root,
    relative_artifact_dir,
    *,
    artifact_name,
    artifact_role,
    model_sha256,
    host_codegen,
    simulator,
    expected_vta_symbols=(),
    forbidden_vta_symbols=(),
)
```

It returns an immutable value containing the final paths, exact in-memory Graph
JSON and parameter bytes, reloaded `tvm.runtime.Module`, device-independent
manifest data, and source-file paths. It does not load FSIM/TSIM, choose a TVM
target, create a Graph Executor, or execute inference.

`relative_artifact_dir` is a safe relative path below the resolved
`output_root`; absolute paths, parent traversal, and symlink escapes are
rejected.

The existing deployment dataclasses may be adapted to consume this return value,
but simulator execution and target selection remain owned by later modules.

## Export And Replacement Semantics

- Build into a temporary sibling directory and publish the completed directory
  only after all files, hashes, source checks, DSO reload, and symbol checks
  succeed.
- Replace only the exact generated artifact directory selected by the caller.
- On failure, remove the temporary partial output and preserve any previously
  completed artifact directory unchanged.
- Reject absolute paths, parent traversal, and symlink escapes outside the
  caller-selected application output root, as well as unsafe empty targets.
- Generated bundles remain ignored by Git and are never staged automatically.

## Tech Stack

- Python 3.11 from `.envs/tvm-vta-env`.
- Repository-pinned TVM Graph Executor factory, runtime Module, parameter
  serializer, and host compiler/export APIs.
- `pathlib`, `hashlib`, `json`, and standard filesystem operations only; no new
  dependency.
- Platform DSO suffix `.dylib` on Darwin and `.so` elsewhere, matching the
  existing application policy.

## Commands

Focused structural and artifact tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_graph_artifacts.py
```

Existing application regression tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests
```

The repository aggregate gate remains:

```bash
bash scripts/test_vta_byoc.sh
```

## Project Structure

```text
vta/apps/mlperf_tiny_benchmark/image_classification_v1/
  graph_artifacts.py              Bundle export/reload implementation
  runtime.py                      Existing deployment consumer
  tests/test_graph_artifacts.py   Focused unit and real-factory tests
  build/                          Ignored generated bundles
docs/initiatives/resnet8-graph-codegen-sim/
  CAPABILITY_MAP.md
  SPEC-graph-artifact-bundle.md
```

## Code Style

- Preserve Apache license headers and existing application-local dataclass and
  `pathlib.Path` conventions.
- Keep serialization, hashing, source discovery, publication, and validation in
  small functions with explicit inputs.
- Raise errors that name the artifact, stage, and exact missing or invalid path.
- Do not catch an exception unless adding artifact-stage context or performing
  bounded cleanup before re-raising.

## Testing Strategy

1. Unit tests use fake factories/modules to cover exact bytes, deterministic
   manifests, recursive source ordering, modules without source, malformed
   arguments, hash validation, and failure cleanup.
2. Replacement tests prove that a failed new export leaves a previously complete
   bundle unchanged and no temporary sibling remains.
3. Real-factory tests build the existing fixed ResNet reference and mixed LLVM
   artifacts and require non-empty LLVM IR plus successful DSO reload.
4. Symbol tests require every expected mixed VTA entry point after reload and
   reject every configured forbidden VTA entry point for the reference artifact.
5. Reload tests reconstruct Graph Executor inputs from on-disk `graph.json`,
   `params.bin`, and `model.<suffix>` rather than retained factory state.
6. Existing host-deployment and aggregate suites must remain green.

## Boundaries

### Always

- Persist exact factory graph and serialized parameters alongside the library.
- Use standard TVM source and export APIs from the pinned checkout.
- Preserve deterministic VTA symbol validation and configuration fingerprinting.
- Verify a bundle from its final on-disk files before reporting success.
- Keep previous completed output intact when replacement fails.

### Ask first

- Change the bundle schema after version `1` is consumed by another module.
- Change existing model, quantization, partitioning, output-comparison, or DSO
  naming compatibility behavior.
- Add standard MLF export or another artifact format.

### Never

- Treat generated LLVM IR or C source as the runnable library without compiling
  and reloading the DSO.
- Claim the custom directory is TVM Model Library Format.
- Embed absolute paths, credentials, timestamps, or local environment contents
  in the manifest.
- Load a simulator or execute VTA work during artifact export.
- Commit generated build output or modify the pinned TVM checkout.

## Success Criteria

1. A reference or mixed Graph factory exports atomically into the specified
   bundle layout with exact Graph JSON, serialized parameters, DSO, source, and
   deterministic manifest.
2. LLVM ResNet artifacts contain non-empty inspectable `.ll` source files.
3. A fresh loader reconstructs each Graph Executor artifact using only bundle
   files and normal TVM/VTA runtime dependencies, with no retained factory state.
4. Reloaded mixed bundles implement all eight deterministic VTA symbols;
   reference bundles reject that same configured symbol set.
5. Failed export or validation leaves an older completed bundle unchanged and
   leaves no partial published bundle.
6. Focused tests, existing ResNet deployment tests, and the repository aggregate
   gate pass without tracked changes in the pinned TVM checkout.

## Open Questions

None.

## Approval Gate

This specification requires explicit user approval before the next module
specification, `vta-c-host-codegen`, is written.
