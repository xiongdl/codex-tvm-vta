# Spec: ResNet8 FSIM LLVM/C Matrix

Module id: `resnet8-fsim-matrix`

## Objective

Build, persist, reload, and completely execute the fixed MLPerf Tiny ResNet-8
Graph Executor deployment on VTA FSIM for both supported host code generators:
LLVM and C. Each host variant contains a pure-host quantized reference and a
mixed host/VTA graph with the existing eight VTA partitions. All ten committed
samples must execute through every artifact, all output tensors must agree
exactly, and both mixed variants must independently demonstrate positive VTA
FSIM activity.

This module consumes the approved `graph-artifact-bundle` and
`vta-c-host-codegen` contracts. It does not add TSIM, AoT, or deployment-result
analysis.

## Fixed Model Contract

The application continues to call `prepare_model(MODEL_PATH)` exactly once per
matrix deployment. The following existing invariants remain unchanged:

- model SHA-256
  `b5c0046d6e0328b4956afd6baa29555a29b1f1c65bdd45aaed75b7cd484d9f79`;
- input `input_1`, shape `(1, 32, 32, 3)`, dtype `float32`;
- output shape `(1, 10)`, dtype `float32`;
- one approved quantization pass and one shared quantized Relay module;
- pure reference and mixed graph forked from that same quantized object;
- exact symbols `tvmgen_mlperf_resnet_vta_main_0` through
  `tvmgen_mlperf_resnet_vta_main_7`;
- one convolution in each VTA partition and the existing host fallback set;
- the ten committed PNG samples in manifest order.

No host variant may re-import, re-quantize, or repartition the model to create
its own semantic reference.

## Host Variant Contract

Host selection is represented by the exact values `llvm` and `c`.

| Variant | Reference target | Mixed target | Reference device | Mixed device |
|---|---|---|---|---|
| LLVM | `Target("llvm")` | `Target("vta", host=Target("llvm"))` | `tvm.cpu(0)` | `tvm.ext_dev(0)` |
| C | `Target("c")` | `Target("vta", host=Target("c"))` | `tvm.cpu(0)` | `tvm.ext_dev(0)` |

Target construction is centralized and rejects every other value before
calling `relay.build`. There is no fallback from C to LLVM.

For each host variant, reference and mixed factories are built from the exact
same prepared model. The mixed factory remains inside `vta.build_config()`.
Build, bundle export, DSO compilation, and DSO reload complete before FSIM is
loaded.

## Artifact Layout

The caller-selected output root contains four approved Graph bundles:

```text
<output-root>/
  llvm-fsim/
    reference/
      manifest.json
      graph.json
      params.bin
      model.<suffix>
      source/
    mixed/
      ...
  c-fsim/
    reference/
      ...
    mixed/
      ...
```

The reference bundle records the legacy artifact identity
`mlperf_resnet_llvm` for LLVM and `mlperf_resnet_c` for C. Mixed identities are
`mlperf_resnet_vta_llvm` and `mlperf_resnet_vta_c`. These identities are
manifest labels; runnable libraries retain the bundle-standard `model` name.

Every bundle contains its own Graph JSON, serialized parameter dictionary,
runnable library, and source tree. LLVM bundles require non-empty `.ll` output;
C bundles require non-empty C-family source. Reference bundles reject all eight
VTA symbols, while mixed bundles require exactly the configured eight-symbol
set. Runtime execution consumes only the final on-disk bundle contents returned
by the artifact loader, never the in-memory factory graph or parameters.

Publishing one bundle follows the approved atomic replacement contract. A
failure does not delete completed bundles for other host/role variants and does
not publish a partial failing bundle.

## Application Interfaces

The existing single-host entry point remains source-compatible and defaults to
LLVM:

```python
deploy(output_dir=DEFAULT_OUTPUT_DIR, host_codegen="llvm") -> DeploymentResult
```

It performs one complete reference/mixed FSIM deployment for the selected host.
Its result gains an explicit `host_codegen` value, and its artifacts expose
bundle paths rather than the previous two flat DSO paths.

A matrix entry point performs the user-requested complete LLVM+C run while
preparing the model only once:

```python
deploy_fsim_matrix(
    output_dir=DEFAULT_OUTPUT_DIR,
    host_codegens=("llvm", "c"),
) -> FsimMatrixResult
```

`FsimMatrixResult` contains the single prepared model and an ordered tuple of
LLVM then C deployment results. Duplicate, empty, reordered, or unsupported
host selections are rejected; the complete matrix is exactly `("llvm", "c")`.
Focused tests may call `deploy(..., host_codegen=...)` independently.

Artifact construction is generalized without embedding simulator behavior:

```python
build_host_artifacts(prepared, output_dir, host_codegen, simulator="fsim")
```

`simulator="fsim"` is recorded in manifests but is not used to load FSIM during
build. The TSIM module may later generalize this validated label.

## CLI Contract

`run.py` accepts:

```text
--output-dir PATH
--host-codegen {llvm,c,all}
```

The default remains `llvm` to preserve the existing invocation. `all` invokes
`deploy_fsim_matrix` and is the required complete-matrix command. `llvm` and `c`
each invoke the single-host deployment. Unsupported values fail in argument
parsing before model preparation.

Successful output names each host variant and reports:

- eight deterministic VTA partitions;
- ten exact reference/mixed comparisons;
- positive FSIM profiler counters for that mixed variant;
- persisted reference and mixed bundle directories;
- overall FSIM matrix success when `all` is selected.

It does not report accuracy, latency, throughput, MAC utilization, traffic, or
MLPerf compliance.

## Execution And Equality Contract

For a complete matrix deployment:

1. Load all ten input arrays once in committed manifest order.
2. Execute both pure-host references before importing `vta.testing.simulator`.
3. Require LLVM-reference and C-reference outputs to have identical shape,
   dtype, and every element for each sample.
4. Load and validate FSIM once.
5. For each mixed variant in LLVM then C order:
   - validate all eight reloaded VTA symbols;
   - clear FSIM counters and require an all-zero reset snapshot;
   - execute all ten samples through the reloaded Graph Executor bundle;
   - require exact equality to the shared reference output for every sample;
   - capture counters and require positive `gemm_counter`,
     `wgt_load_nbytes`, and `out_store_nbytes`.
6. Require identical top-1 indices as a consequence of exact tensor equality.

The shared comparison baseline is the exact output agreed by both pure-host
implementations, not a separately transformed or floating-point model.

Each Graph Executor is reconstructed with its own on-disk Graph JSON, DSO,
parameter bytes, and declared device. Parameters may not be shared or retained
from the factory.

## Failure Behavior

- Model, partition, bundle, symbol, FSIM availability, counter reset, counter
  activity, shape, dtype, element, or top-1 mismatches raise an actionable
  exception and make the CLI exit nonzero.
- Error messages include the host variant and sample or artifact where
  applicable.
- A C build/codegen/export failure is surfaced directly; LLVM is never used as
  a recovery path.
- Simulator import remains lazy so build-only APIs work when FSIM is absent.
- Completed artifact bundles remain inspectable after a later execution failure.

## Project Structure

Expected application changes:

```text
vta/apps/mlperf_tiny_benchmark/image_classification_v1/
  graph_artifacts.py
  runtime.py
  run.py
  README.md
  tests/
    test_graph_artifacts.py
    test_host_deployment.py
```

No model, sample, quantization, partitioning, TVM checkout, or simulator source
file changes are expected. `scripts/test_vta_byoc.sh` already executes the
application test module, so it needs no change unless implementation proves its
current invocation cannot express the approved matrix gate.

## Commands

Focused application tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_graph_artifacts.py \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_host_deployment.py
```

Required full CLI run:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py \
  --host-codegen all
```

The repository aggregate gate remains:

```bash
bash scripts/test_vta_byoc.sh
```

## Testing Strategy

1. Unit-test exact LLVM/C target construction and rejection of unsupported
   host values without calling `relay.build`.
2. Prove both factories for each host use the same prepared reference/mixed
   module objects and build before lazy FSIM import.
3. Reuse artifact-bundle tests for exact bytes, source presence, atomic export,
   final-file reload, and expected/forbidden symbol validation.
4. Prove each Graph Executor loads only its own on-disk parameters before its
   first run.
5. Prove both reference variants finish before FSIM import and agree exactly on
   all ten outputs.
6. Prove FSIM counters are cleared, checked at zero, and then independently
   positive for LLVM-mixed and C-mixed execution.
7. Exercise failures for each comparison dimension, missing symbols, invalid
   matrix selection, FSIM absence, nonzero reset state, and inactive counters.
8. Run a real end-to-end LLVM FSIM deployment and a real end-to-end C FSIM
   deployment using the committed model and ten samples.
9. Run the real `--host-codegen all` command and require four complete bundles,
   eight VTA symbols in each mixed bundle, twenty mixed comparisons in total,
   cross-host reference equality, and positive counters for both mixed variants.
10. Keep existing asset, model-pipeline, VTA codegen, and aggregate suites green.

## Code Style

- Use immutable result dataclasses with explicit `host_codegen` and simulator
  labels.
- Keep target construction, artifact building, reference execution, simulator
  execution, comparison, and CLI presentation as separate functions.
- Preserve lazy simulator import and application-local `pathlib.Path` style.
- Avoid duplicating LLVM and C control flow; host behavior differs through
  validated data and target construction.
- Do not store runtime modules, devices, arrays, or absolute paths in manifests.

## Boundaries

### Always

- Use Graph Executor for all four artifacts.
- Prepare and quantize the committed model once for a complete matrix run.
- Build both pure reference and mixed artifact with the selected host codegen.
- Reload every runnable library and Graph configuration from disk.
- Execute all ten committed samples for LLVM and C.
- Require the existing eight VTA partitions and positive FSIM activity for each
  mixed variant.
- Require exact cross-reference and reference/mixed output equality.

### Ask first

- Change the default CLI host away from LLVM.
- Change the sample count/order, reference definition, output equality rule, or
  required profiler counters.
- Add a host target beyond LLVM/C or a simulator beyond FSIM in this module.
- Remove compatibility of the existing `deploy(output_dir)` call.

### Never

- Modify or replace the committed model or samples.
- Re-quantize or repartition per host variant.
- Use LLVM artifacts while labeling them as C.
- Execute an in-memory factory instead of the reloaded bundle.
- Load FSIM during build/export/reload.
- Claim TSIM, AoT, accuracy, performance, MAC-utilization, or traffic results.
- Commit generated build bundles or modify the pinned TVM checkout.

## Success Criteria

1. `run.py --host-codegen all` exits zero after complete LLVM and C Graph
   Executor FSIM execution of all ten committed samples.
2. The output root contains four reloadable bundles with exact Graph JSON,
   parameters, libraries, manifests, and non-empty matching LLVM/C source.
3. Both mixed bundles expose the exact eight deterministic VTA symbols and both
   reference bundles reject them.
4. LLVM and C pure-host references agree exactly, and every mixed output agrees
   exactly with that common reference for every sample.
5. LLVM-mixed and C-mixed runs independently produce positive GEMM, weight-load,
   and output-store FSIM counters after verified zero resets.
6. Focused tests, the real complete CLI command, and the aggregate gate pass
   without tracked changes in the pinned TVM checkout.

## Open Questions

None.

## Approval Gate

This specification requires explicit user approval before the next module
specification, `resnet8-tsim-matrix`, is written.
