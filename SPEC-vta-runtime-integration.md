# Spec: VTA BYOC Runtime Integration

## Objective

Implement the `vta-runtime-integration` module from
`CAPABILITY_MAP-vta-byoc.md`. The module proves that a capability-partitioned
Relay program can be compiled through `relay.ext.vta`, exported, loaded, and
executed on the existing VTA FSIM runtime with numerically correct results.

This stage closes the first real BYOC execution path:

```text
Relay IRModule
  -> partition_for_vta
  -> relay.build + relay.ext.vta
  -> exported graph executor artifact
  -> rpc.LocalSession load
  -> ext_dev(0) execution on FSIM
  -> numerically verified host/VTA output
```

It reuses the existing VTA device API, simulator runtime, graph executor, and
artifact representation. It does not migrate graphpack callers, remove legacy
APIs, broaden the supported operator domain, add a runtime module format, or
modify the pinned TVM checkout.

## Prerequisite Contract

This module consumes the completed upstream modules without redefining them:

- `vta-pattern-partition` produces typed, deterministic
  `Compiler="vta"` regions while preserving host fallback.
- `vta-relay-lowering` produces a two-buffer VTA PrimFunc whose constants are
  internal and whose target is `ext_dev` with the active host target.
- `vta-external-codegen` explicitly registers `relay.ext.vta`, builds the
  outlined function once, and returns a runtime module implementing the exact
  `global_symbol`.

The runtime integration tests must fail loudly if any of these boundaries no
longer hold. They must not duplicate lowering, compile an outlined function
directly, or reach into private helpers to bypass Relay build.

## Runtime and Device Contract

The initial runtime target is the configured VTA FSIM environment. Execution
uses the repository's established local RPC path:

```python
remote = tvm.rpc.LocalSession()
device = remote.ext_dev(0)
```

The VTA runtime library owns `device_api.ext_dev`; integration code must not
register or replace that device API. The graph executor receives the loaded
Relay build artifact and the `ext_dev(0)` device so its storage allocation,
input copies, host-wrapper calls, VTA calls, and output copies follow the same
lifecycle as existing VTA Relay applications.

Before execution, tests must verify that the simulator runtime is available.
A missing FSIM library is an environment/setup failure and must produce a
clear failure rather than silently skipping the runtime proof.

TSIM, remote FPGA programming, tracker sessions, and hardware RPC are deferred
until the FSIM ABI and artifact lifecycle are stable.

## Build and Execution Contract

The supported fixture is compiled and run through only public boundaries:

```python
env = vta.get_env()
remote = tvm.rpc.LocalSession()
device = remote.ext_dev(0)

vta.register_byoc()
partitioned = vta.relay.partition_for_vta(mod, params=params)
with vta.build_config():
    factory = relay.build(
        partitioned,
        target=tvm.target.Target(env.target, host=env.target_host),
    )

factory.export_library(artifact_path)
remote.upload(artifact_path)
loaded = remote.load_module(artifact_name)
executor = graph_executor.create(factory.get_graph_json(), loaded, device)
executor.set_input("data", input_data)
executor.run()
output = executor.get_output(0).numpy()
```

Tests and implementation must use `vta.relay.partition_for_vta` and must not
introduce another partitioning alias.

The compiled graph must contain host operations before and after the external
region. Runtime success therefore proves both the VTA kernel and the
host/VTA boundary, rather than invoking the generated VTA symbol in isolation.
The outer `vta.build_config()` applies VTA buffer CPU-access rewriting to host
wrappers that operate on `ext_dev` storage. The external compiler's final
runtime-codegen `tvm.build` must suppress inherited VTA lowering passes because
its PrimFunc has already passed through the VTA lowering pipeline exactly once.

## Numerical Contract

Runtime output is compared against the same typed, unpartitioned Relay module
executed with the LLVM host target. The reference and VTA executions receive
identical deterministic integer input.

The initial matrix covers:

1. Quantized 3x3 convolution without bias.
2. Quantized 3x3 convolution with constant `nn.bias_add`.
3. Quantized 3x3 convolution with right-hand broadcast constant `add`.
4. Host `abs` before the VTA region and host `transpose` after it.

Because the supported graph uses integer convolution, shift, clip, cast, and
transpose operations, output comparison is exact with no floating-point
tolerance. The test input must include negative and positive values and be
generated from a fixed seed or an explicit deterministic array.

The near-miss non-constant-weight fixture remains a host-only build check. It
must execute correctly with LLVM and must not invoke the VTA compiler callback;
it is not sent to `ext_dev` as a VTA runtime proof.

## Artifact Lifecycle Contract

The Relay build artifact must survive the lifecycle used by existing VTA
applications:

1. Export to a temporary directory managed by TVM's test utility.
2. Upload through `rpc.LocalSession`.
3. Load by artifact basename from the session.
4. Create a graph executor from the original graph JSON and the loaded module.
5. Execute and retrieve output.

The loaded module must still implement the deterministic VTA external symbol,
including through imported modules. Constants must remain available after
reload without caller-managed weight or bias inputs.

Temporary artifacts are test-scoped and are not checked into the repository.
No new serialization format, cache directory, global artifact registry, or
manual module reconstruction is introduced.

## ABI and Ownership Invariants

- The external VTA function retains exactly one input buffer and one output
  buffer at runtime.
- Convolution weights and optional bias constants remain internal to the
  compiled artifact.
- The graph executor owns graph-level inputs, outputs, and storage planning.
- `device_api.ext_dev` owns VTA allocation and copies; Python integration code
  does not manually allocate workspace.
- Host and VTA functions preserve the partitioned Relay tensor shapes and
  dtypes across their call boundary.
- The exported and reloaded artifact preserves the exact external
  `global_symbol`.
- Compilation performs no simulator execution; simulator activity begins only
  when the graph executor runs.

## Error Semantics

- Missing FSIM runtime/device registration: `RuntimeError` naming the required
  build/setup command.
- Missing `relay.ext.vta` registration: existing Relay build error; tests must
  call `vta.register_byoc()` explicitly rather than masking it.
- Export, upload, or load failure: propagate the TVM/runtime error with the
  artifact stage visible in test context.
- Loaded artifact missing the expected symbol: `RuntimeError` naming the
  symbol.
- Output shape or dtype mismatch: assertion failure showing expected and
  actual metadata before numerical comparison.
- Numerical mismatch: exact NumPy/TVM testing assertion with the approved
  variant identified by test parametrization.

Ordinary unsupported Relay remains a host fallback and is not a runtime error.
Public error paths must not use Python `assert` in production code.

## Tech Stack and Primary Sources

- TVM source revision pinned by the `tvm/` submodule.
- Python 3.11 from `.envs/tvm-vta-env`.
- VTA FSIM library built by `scripts/build_vta_lib.sh --target libvta_fsim`.
- `vta/python/vta/testing/utils.py`: canonical FSIM test execution through
  `rpc.LocalSession`.
- `vta/tests/python/unittest/test_vta_insn.py`: established VTA artifact save,
  upload, load, `ext_dev(0)`, execute, and output-copy lifecycle.
- `vta/tutorials/frontend/deploy_detection.py`: existing Relay graph executor
  export/load/execution path for VTA.
- `vta/src/runtime/device_api.cc`: ownership of `device_api.ext_dev`, workspace,
  and buffer copies.
- `tvm/tests/python/relay/utils/external_codegen.py`: upstream external-codegen
  graph executor export/reload verification pattern.

No new dependency or upstream TVM modification is permitted.

## Commands

Use the existing repository scripts and environment:

```bash
./scripts/build_vta_lib.sh --target libvta_fsim

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_runtime.py -q

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m pytest \
  vta/tests/python/unittest/test_byoc_contract.py \
  vta/tests/python/unittest/test_byoc_partition.py \
  vta/tests/python/unittest/test_byoc_lowering.py \
  vta/tests/python/unittest/test_byoc_codegen.py \
  vta/tests/python/unittest/test_byoc_runtime.py -q

PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  .envs/tvm-vta-env/bin/python -m compileall -q vta/python/vta/relay

./scripts/test_vta_fsim.sh
git -C tvm status --short
git -C vta diff --check
```

If the runtime test belongs in the standard FSIM gate, minimally extend
`scripts/test_vta_fsim.sh` after the focused test is stable. Preserve the
script's existing options and default behavior.

## Project Structure

```text
vta/tests/python/unittest/
├── byoc_utils.py             # shared deterministic Relay fixture
└── test_byoc_runtime.py      # compile/export/reload/FSIM numerical tests

scripts/test_vta_fsim.sh      # canonical FSIM gate; extend only if needed
```

No production runtime module is expected initially. If testing exposes a real
production lifecycle gap, update this spec before adding a narrowly owned
helper under `vta/python/vta/relay/`.

## Code Style

Keep the runtime flow visible in the test instead of hiding it behind a
general framework. Small fixture helpers may isolate reference execution and
artifact loading:

```python
def _run_vta_graph(mod, input_data, artifact_dir):
    env = vta.get_env()
    vta.register_byoc()
    partitioned = vta.relay.partition_for_vta(mod, mod_name="runtime")
    with vta.build_config():
        factory = relay.build(
            partitioned,
            target=tvm.target.Target(env.target, host=env.target_host),
        )
    return _export_load_and_run(factory, input_data, artifact_dir)
```

Helpers return observable results or artifacts. They do not mutate global
configuration, swallow TVM errors, perform hidden registration, or select
operators by graph position.

## Testing Strategy

1. Start with a focused RED test that compiles the supported fixture through
   the public BYOC path, creates a graph executor on FSIM, and attempts one
   numerical run.
2. Localize any failure to build, export, reload, device allocation, executor
   creation, input copy, kernel invocation, or output copy before changing
   production code.
3. Make the smallest correction at the owning boundary; do not weaken the
   lowering or artifact contracts.
4. Parameterize the passing end-to-end test across all approved bias forms.
5. Assert exact output, metadata, symbol survival, constant ownership, and
   host/VTA boundary structure.
6. Run the complete BYOC suite and standalone FSIM suite without skips.

Runtime tests may use temporary filesystem artifacts because export/reload is
the behavior under test. They must not use network RPC, hardware, downloads,
or persistent paths.

## Boundaries

- Always:
  - Enter through `partition_for_vta`, `register_byoc`, and `relay.build`.
  - Use the configured FSIM `ext_dev` runtime and graph executor.
  - Compare with a deterministic LLVM reference exactly.
  - Exercise export and reload before the required numerical assertion.
  - Preserve host operations on both sides of the VTA partition.
  - Keep weights and optional bias constants internal to the artifact.
- Ask first:
  - Add or change a public API.
  - Add a runtime module format, C++ source, build option, or dependency.
  - Change the host/VTA ABI, device type, executor, or constant ownership.
  - Add TSIM, tracker RPC, FPGA programming, or hardware requirements.
- Never:
  - Call `graph_pack` or select regions using start/stop names or indices.
  - Invoke private lowering/codegen helpers instead of the public build path.
  - Modify the pinned TVM checkout.
  - Skip runtime tests because FSIM setup is missing.
  - Treat successful compilation as evidence of numerical correctness.

## Success Criteria

- Every approved convolution variant compiles through `relay.ext.vta`, exports,
  reloads, and executes on local FSIM.
- Reloaded artifacts retain the deterministic external symbol and internal
  constants.
- Graph executor outputs exactly equal the LLVM reference for deterministic
  signed integer inputs.
- Host pre/post operations and the VTA region execute correctly as one graph.
- No new runtime format, public API, graphpack dependency, or upstream TVM
  modification is introduced.
- Focused runtime, complete BYOC, Python compilation, and FSIM regression tests
  pass without skips.
- Human review approves this spec before implementation planning begins.

## Open Questions

None under the stated initial scope. TSIM and hardware execution remain later
validation extensions after the FSIM lifecycle is proven.
