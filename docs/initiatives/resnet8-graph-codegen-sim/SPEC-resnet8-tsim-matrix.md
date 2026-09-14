# Spec: ResNet8 TSIM LLVM/C Matrix

Module id: `resnet8-tsim-matrix`

## Objective

Build, persist, reload, initialize, and completely execute the fixed MLPerf
Tiny ResNet-8 Graph Executor deployment on the Verilated VTA TSIM hardware model
for both LLVM and C host code generators. Both mixed variants must retain the
same eight VTA partitions, execute all ten committed samples, agree exactly
with the quantized pure-host reference, and independently produce a positive
TSIM hardware cycle count.

This module follows the completed FSIM matrix. It generalizes simulator
selection without changing the approved model, host-codegen, artifact, or
Graph Executor contracts.

## Source Basis

This specification targets the repository VTA implementation and its pinned
TVM checkout.

- `vta/python/vta/testing/simulator.py` loads `libvta_tsim` globally when the
  active environment target is `tsim`, loads `libvta_hw` as a `vta-tsim`
  runtime module, and calls `vta.tsim.init` during lazy module import.
- `vta/src/tsim/tsim_driver.cc` registers `vta.tsim.init`,
  `vta.tsim.profiler_clear`, and `vta.tsim.profiler_status`; its profiler
  exposes only `cycle_count`.
- `scripts/test_vta_tsim.sh` validates `libtvm`, `libvta_tsim`, and `libvta_hw`
  presence and exercises TSIM initialization under
  `vta/config/tsim_sample.json`.
- `vta/tests/python/unittest/test_byoc_runtime.py` establishes the existing
  simulator-specific registry checks and positive-cycle TSIM activity rule.

The existing `simulator.enabled()` helper checks the FSIM registry function and
is therefore not a valid TSIM availability check. This application must not use
it for TSIM.

## Configuration Contract

TSIM execution runs in a fresh process configured before importing `vta`:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json"
```

The application maps public simulator labels to required environment targets:

| Public label | Required `vta.get_env().TARGET` | Driver registry | Activity counter |
|---|---|---|---|
| `fsim` | `sim` | `vta.simulator.*` | `gemm_counter`, `wgt_load_nbytes`, `out_store_nbytes` |
| `tsim` | `tsim` | `vta.tsim.*` | `cycle_count` |

An explicit simulator label that does not match the active environment target
fails before artifact build. Switching FSIM and TSIM inside one Python process
is unsupported because the VTA environment is initialized from
`VTA_CONFIG_FILE` at import time.

Only `fsim` and `tsim` are accepted. No automatic fallback or configuration
file mutation is allowed.

## TSIM Initialization Contract

TSIM remains lazily initialized after reference/mixed build, bundle export, and
DSO reload have completed. Initialization performs the standard repository
flow by importing `vta.testing.simulator`, which must:

1. load `libvta_tsim` with global symbol visibility;
2. expose `vta.tsim.init`, `vta.tsim.profiler_clear`, and
   `vta.tsim.profiler_status`;
3. expose `runtime.module.loadfile_vta-tsim`;
4. locate and load `libvta_hw` with runtime format `vta-tsim`;
5. call `vta.tsim.init` with the loaded hardware module;
6. preserve the initialized module for all subsequent model executions.

The application verifies the required registry functions after import and
reports the missing library pair plus the exact build command:

```bash
bash scripts/build_vta_lib.sh --target libvta_hw
```

It must not call `simulator.enabled()` for TSIM and must not manually duplicate
the library loader or hardware initialization implemented by the standard
simulator module.

## Artifact And Host Matrix

The approved host targets remain unchanged:

- pure LLVM reference and `vta` with LLVM host;
- pure C reference and `vta` with C host.

TSIM adds four separate bundles:

```text
<output-root>/
  llvm-tsim/
    reference/
      manifest.json
      graph.json
      params.bin
      model.<suffix>
      source/
    mixed/
      ...
  c-tsim/
    reference/
      ...
    mixed/
      ...
```

Every manifest records `simulator: "tsim"`; FSIM bundles and labels remain
unchanged. LLVM bundles require LLVM IR and C bundles require C-family source.
Each mixed bundle requires the exact eight deterministic VTA symbols, and each
reference bundle rejects them.

TSIM builds use the active `tsim_sample.json` VTA configuration so the generated
configuration fingerprint matches the loaded TSIM driver and Verilated hardware
module. An FSIM-labeled bundle is never relabeled or reused as a TSIM bundle.

## Application Interfaces

The single-host deployment becomes simulator-aware while preserving both prior
defaults:

```python
deploy(
    output_dir=DEFAULT_OUTPUT_DIR,
    host_codegen="llvm",
    simulator="fsim",
) -> DeploymentResult
```

The approved FSIM entry point remains:

```python
deploy_fsim_matrix(
    output_dir=DEFAULT_OUTPUT_DIR,
    host_codegens=("llvm", "c"),
) -> SimulationMatrixResult
```

TSIM adds:

```python
deploy_tsim_matrix(
    output_dir=DEFAULT_OUTPUT_DIR,
    host_codegens=("llvm", "c"),
) -> SimulationMatrixResult
```

Both wrappers use one internal simulator-parameterized matrix implementation.
`SimulationMatrixResult` records the simulator label, the single prepared
model, and ordered LLVM then C deployment results. There is no duplicated TSIM
model pipeline or host build path.

A small immutable simulator session/adaptor may centralize label, environment
target, required registry functions, clear operation, stats operation, activity
validation, and setup diagnostic. It delegates actual loading and initialization
to `vta.testing.simulator`.

## CLI Contract

`run.py` gains:

```text
--simulator {fsim,tsim}
```

The default is `fsim`, preserving the existing command. The previously approved
`--host-codegen {llvm,c,all}` remains. Complete TSIM execution is:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py \
  --simulator tsim --host-codegen all
```

Successful output names TSIM and each host variant, reports four artifact
directories, eight VTA partitions per mixed graph, ten exact comparisons per
host, positive `cycle_count` for both mixed variants, and final TSIM matrix
success. It does not present the cycle count as latency, throughput, or an
MLPerf metric.

## Execution And Equality Contract

For one complete TSIM matrix process:

1. Validate `simulator="tsim"` against active environment target `tsim`.
2. Prepare and quantize the committed model exactly once.
3. Build, export, and reload all LLVM/C reference and mixed bundles without
   importing the simulator module.
4. Load the ten committed samples once.
5. Execute both pure-host references on CPU and require exact cross-host shape,
   dtype, element, and top-1 equality.
6. Lazily initialize the standard TSIM driver and Verilated hardware module
   once.
7. For LLVM-mixed and then C-mixed independently:
   - validate the exact eight VTA symbols;
   - clear TSIM stats and require `{"cycle_count": 0}`;
   - execute all ten samples through the reloaded mixed Graph Executor on
     `tvm.ext_dev(0)`;
   - require exact output equality with the common quantized reference for
     every sample;
   - require integer `cycle_count > 0` after execution.

The two mixed variants share the initialized TSIM hardware session sequentially;
they do not run concurrently. Counter reset separates their evidence.

## Profiler Contract

Simulator-specific validation is explicit:

- FSIM continues to require positive `gemm_counter`, `wgt_load_nbytes`, and
  `out_store_nbytes`.
- TSIM requires exactly the available `cycle_count` counter to exist, be an
  integer, reset to zero, and become positive after each mixed variant.

This module does not synthesize unsupported TSIM traffic counters, estimate
MAC utilization, or infer instruction/micro-op traffic from `cycle_count`.
Those remain part of the deferred analysis initiative.

## Failure Behavior

- Wrong configuration target, missing `libvta_tsim`, missing `libvta_hw`,
  missing registry functions, initialization failure, counter reset failure,
  timeout surfaced by the existing driver, nonpositive cycles, missing VTA
  symbols, or output mismatch makes the deployment fail nonzero.
- Diagnostics name TSIM, the host variant, sample/artifact where applicable,
  and the required build command for missing simulator libraries.
- C failure never falls back to LLVM; TSIM failure never falls back to FSIM.
- Completed bundles remain available for inspection after execution failure.
- The application does not catch hardware-driver failures merely to continue
  with the next host variant.

## Project Structure

Expected changes:

```text
vta/apps/mlperf_tiny_benchmark/image_classification_v1/
  runtime.py
  run.py
  README.md
  tests/
    test_host_deployment.py
    test_tsim_deployment.py
scripts/
  test_vta_byoc.sh
```

`graph_artifacts.py` should require no TSIM-specific logic beyond consuming the
validated manifest label. `scripts/test_vta_tsim.sh` already owns standalone
TSIM initialization and instruction tests; it requires no semantic change.

## Commands

Build required simulator and hardware libraries:

```bash
bash scripts/build_vta_lib.sh --target libvta_hw
```

Standalone TSIM validation:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
  bash scripts/test_vta_tsim.sh
```

Focused ResNet-8 TSIM tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/tests/test_tsim_deployment.py
```

Required full CLI run:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/tsim_sample.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python \
  vta/apps/mlperf_tiny_benchmark/image_classification_v1/run.py \
  --simulator tsim --host-codegen all
```

Final aggregate gate:

```bash
bash scripts/test_vta_byoc.sh
```

The aggregate script must execute the ResNet-8 TSIM matrix in a fresh Python
process under `tsim_sample.json`, after the existing standalone TSIM gate.

## Testing Strategy

1. Unit-test public simulator-label to environment-target, registry-function,
   activity-counter, and setup-command mappings.
2. Reject FSIM/TSIM label/config mismatches before model preparation or build.
3. Prove TSIM build/export/reload finishes before lazy simulator import.
4. Mock the standard simulator module to prove exactly one TSIM initialization,
   zero-reset checks, sequential LLVM/C mixed execution, and independent cycle
   snapshots.
5. Prove TSIM availability checks use `vta.tsim.*` registry functions and never
   `simulator.enabled()`.
6. Exercise missing driver, missing hardware module, missing registry function,
   malformed/missing/nonzero-reset/nonpositive cycle counter, symbol failure,
   and exact-output failure diagnostics.
7. Under the real `tsim_sample.json`, require the committed model still produces
   exactly eight routed partitions before hardware execution.
8. Run a real LLVM-host TSIM deployment for all ten committed samples.
9. Run a real C-host TSIM deployment for all ten committed samples.
10. Run the real complete TSIM matrix entry point/CLI and require four complete
    bundles, exact cross-host/reference equality, twenty mixed comparisons, and
    positive independent cycle counts.
11. Keep the complete FSIM LLVM/C matrix, standalone TSIM tests, codegen tests,
    and aggregate gate green.

## Code Style

- Express simulator differences as validated data or a small immutable adaptor,
  not duplicated FSIM and TSIM deployment functions.
- Keep library initialization lazy and isolated from artifact construction.
- Preserve deterministic host ordering and sequential hardware execution.
- Keep simulator-specific error messages and counter validation explicit.
- Do not introduce global environment mutation or module reload tricks.

## Boundaries

### Always

- Use `tsim_sample.json`, standard `vta.testing.simulator` initialization, and
  the repository-built `libvta_tsim` plus `libvta_hw`.
- Use Graph Executor for LLVM/C reference and mixed artifacts.
- Execute all ten committed samples through both mixed host variants.
- Require exactly eight VTA partitions and exact common-reference equality.
- Reset and independently validate positive TSIM cycles for LLVM and C.
- Run TSIM in a process isolated from FSIM configuration.

### Ask first

- Change the Verilator hardware module, TSIM configuration, driver timeout, or
  trace mode.
- Change sample count/order, output equality, host matrix, or default simulator.
- Extend TSIM profiler implementation beyond its existing `cycle_count`.
- Add concurrent execution or simulator reuse across processes.

### Never

- Use `simulator.enabled()` as TSIM availability evidence.
- Substitute FSIM results for TSIM hardware execution.
- Treat source generation, library loading, smoke initialization, or a single
  VTA instruction test as complete ResNet-8 TSIM success.
- Relabel FSIM artifacts as TSIM artifacts.
- Infer MAC utilization or traffic statistics from cycle count.
- Modify the pinned TVM checkout, committed model, samples, quantization, or
  partitioning.
- Commit generated bundles or Verilator trace files.

## Success Criteria

1. The full CLI command with `--simulator tsim --host-codegen all` exits zero
   after both LLVM-host and C-host mixed Graph Executors run all ten samples on
   the initialized Verilated VTA hardware model.
2. The output root contains four TSIM-labeled reloadable bundles with Graph JSON,
   parameters, runnable libraries, manifests, matching LLVM/C source, and exact
   VTA symbol contracts.
3. LLVM and C pure-host reference outputs agree exactly, and both TSIM mixed
   variants agree exactly with that common reference for every sample.
4. Each mixed variant starts from verified zero TSIM stats and ends with its own
   positive `cycle_count`.
5. Wrong configuration, missing TSIM components, initialization failure,
   inactive hardware, or any output difference fails loudly without fallback.
6. FSIM matrix tests, focused TSIM tests, the complete real TSIM CLI run, and the
   aggregate gate pass without tracked changes in the pinned TVM checkout.

## Open Questions

None.

## Approval Gate

This specification requires explicit user approval before implementation PLAN
and TASKS artifacts are written.
