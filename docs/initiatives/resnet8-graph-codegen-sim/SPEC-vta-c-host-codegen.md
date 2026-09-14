# Spec: VTA C Host Codegen

Module id: `vta-c-host-codegen`

## Objective

Extend the repository-local VTA target hooks so `relay.build` and the native
VTA `TIRToRuntime` path accept either an LLVM host target or a C host target.
The C path must emit inspectable C source, compile through TVM's standard
library export path, reload as a runnable host DSO, and preserve the existing
VTA runtime ABI, configuration-fingerprint guard, and public partition symbols.

This module establishes host-codegen correctness independently of ResNet-8
simulation. FSIM execution is owned by `resnet8-fsim-matrix`; TSIM execution is
owned by `resnet8-tsim-matrix`.

## Source Basis

This specification targets the repository-pinned TVM `v0.17.0` checkout and
the repository VTA submodule.

- `tvm/src/relay/transforms/target_hooks.cc` invokes each external target's
  `RelayToTIR` pass with that exact compilation target active through
  `Target::Current()`.
- `vta/src/compiler/target.cc` currently ignores that active target's host and
  requires the host already attached to the lowered PrimFunc to be LLVM.
- `vta/src/compiler/tir_to_runtime.cc` currently accepts only LLVM at module,
  routed-function, and packed-function validation boundaries before dispatching
  to `codegen::Build`.
- `tvm/src/target/codegen.cc` dispatches `codegen::Build` by target kind, and
  the pinned checkout registers `target.build.c` in
  `tvm/src/target/source/codegen_c_host.cc`.
- `tvm/tests/python/codegen/test_target_codegen_c_host.py` establishes that a C
  source module can be exported, reloaded, and invoked through the normal TVM
  runtime library mechanism.

No pinned TVM source is changed.

## Supported Host Contract

The VTA compiler supports exactly these host target kinds in this initiative:

| Host kind | Native `TIRToRuntime` result | Inspectable source | Runnable form |
|---|---|---|---|
| `llvm` | LLVM runtime module | LLVM IR from `get_source("ll")` | directly exportable DSO |
| `c` | C source runtime module | C from `get_source("c")` or the module's default source format | DSO produced by `export_library` |

The choice identifies host code generation only. Both variants retain VTA
runtime calls such as `VTATLSCommandHandle`, buffer transfers, micro-op pushes,
dependency operations, synchronization, and `VTACheckConfig`.

A missing host or any other host kind fails before host codegen. Diagnostics
must name the rejected host and state that the supported kinds are `llvm` and
`c`.

## Relay-To-TIR Host Propagation

`ModernRelayToTIR` must use the active VTA target supplied by TVM's target-hook
driver as the authoritative host selection:

1. Read `Target::Current()` while the VTA target hook is executing.
2. Require an active target of kind `vta` with a defined supported host.
3. For each lowered VTA PrimFunc, preserve its body, symbol, Relay metadata,
   and other attributes while replacing its routed target with
   `Target::WithHost(Target("vta"), active_host)`.
4. Mark the function for the existing runtime-routing pass.
5. Leave non-VTA PrimFuncs unchanged.

The host attached by the environment-backed TE lowering is not authoritative;
it exists to support direct legacy lowering. In the modern Relay target-hook
pipeline, the requested compilation target must override it. Thus a build made
with `Target("vta", host="c")` cannot silently produce LLVM VTA partitions.

The existing runtime-routing pass continues to assign
`CallingConv::kDeviceKernelLaunch`; no calling-convention or symbol-name change
is introduced.

## TIR-To-Runtime Validation

`TIRToRuntime(mod, target)` keeps its validate-first transaction boundary. It
must validate the entire module before invoking either host builder.

- The top-level target is kind `vta`, has a host, and that host is `llvm` or
  `c`.
- Every function remains a PrimFunc with a non-empty, unique `global_symbol`
  equal to its `GlobalVar` name.
- Every raw routed VTA function has a VTA target whose host is structurally
  equivalent to the top-level selected host.
- Every already packed function is bound to a host target structurally
  equivalent to the top-level selected host.
- Every function still contains only the recognized VTA runtime calls and at
  least one recognized VTA activity.
- Any invalid or mixed-host module fails before `target.build.llvm` or
  `target.build.c` is called.

The same transformation sequence remains in force: flatten external buffers,
make the packed API, bind the selected host, lower TVM builtins/custom types and
intrinsics, combine context calls, inject `VTACheckConfig`, then invoke
`codegen::Build(lowered, host)` exactly once.

## Generated C Contract

For a valid C-host input, native `TIRToRuntime` returns one standard TVM C
source module containing every input VTA public symbol exactly once. The source
must retain the configuration check before the first VTA activity within each
entry point.

The module is compiled only through the standard TVM `export_library` flow; no
custom compiler wrapper, generated Makefile, embedded compiler command, or
runtime-specific source template is introduced. After export and reload, the
DSO must implement every expected VTA symbol. Compilation and export must not
load FSIM or TSIM and must not execute VTA instructions.

## Public Interfaces

No new public C++ or Python API is introduced. Existing interfaces gain the
following accepted input:

```python
target = tvm.target.Target("vta", host=tvm.target.Target("c"))
factory = relay.build(partitioned_module, target=target, params=params)
```

The corresponding LLVM form remains unchanged. Direct native hook use also
accepts a VTA IRModule consistently rebound to a C host:

```python
hook = target.get_kind_attr("TIRToRuntime")
c_source_module = hook(vta_tir_module, target)
```

## Project Structure

Expected implementation changes are limited to the VTA submodule:

```text
vta/
  src/compiler/target.cc
  src/compiler/tir_to_runtime.cc
  tests/python/unittest/test_byoc_codegen.py
```

If keeping target-hook tests separate materially improves clarity, focused
coverage may instead be added to the existing
`tests/python/unittest/test_byoc_lowering.py`; this does not expand the module
boundary. No application code is changed by this module.

## Commands

Focused codegen tests:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/tests/python/unittest/test_byoc_codegen.py
```

If target-hook coverage is placed in the lowering suite:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/tests/python/unittest/test_byoc_lowering.py
```

VTA libraries must be rebuilt before tests exercise the changed native hooks:

```bash
bash scripts/build_vta_lib.sh --target all
```

The repository aggregate gate remains:

```bash
bash scripts/test_vta_byoc.sh
```

## Testing Strategy

1. Parameterize native `TIRToRuntime` tests over LLVM and C and require one
   standard host module with every requested symbol.
2. Require non-empty LLVM IR for LLVM and non-empty C source for C, with each
   public symbol defined exactly once.
3. For both source forms, prove `VTACheckConfig` precedes the first VTA runtime
   activity in every entry point.
4. Export the C source module through `export_library`, reload its DSO, and
   require every expected symbol without loading a simulator.
5. Build a small partitioned QNN convolution through `relay.build` with an
   active C-host VTA target; require its generated VTA module/source and
   reloaded DSO symbols to be C-host artifacts rather than LLVM artifacts.
6. Prove the modern target hook replaces the environment-carried LLVM host
   with the requested C host on every routed PrimFunc.
7. Reject missing hosts, unsupported hosts, packed/raw function host mismatch,
   wrong target kinds, malformed calls, duplicate symbols, and partial invalid
   modules before either builder is called.
8. Keep all existing LLVM-only codegen, export-without-FSIM, lowering, runtime,
   and aggregate tests green.

## Code Style

- Centralize supported-host and target-equivalence checks; do not scatter raw
  string comparisons through the two compiler files.
- Preserve the existing validate-before-transform-before-codegen structure.
- Error messages identify the module/function symbol and selected host where
  applicable.
- Preserve Apache headers, existing namespace layout, and current C++ style.
- Do not catch or translate standard TVM C/LLVM codegen failures unless adding
  precise VTA boundary context.

## Boundaries

### Always

- Treat the active modern VTA compilation target as authoritative.
- Generate VTA host stubs through the pinned TVM host code generators.
- Preserve exact public symbols and VTA C runtime call ABI.
- Inject and retain the VTA configuration-fingerprint guard.
- Validate all functions before either host builder is invoked.
- Exercise actual C export and DSO reload, not source-text checks alone.

### Ask first

- Add another host target kind beyond LLVM and C.
- Change the VTA runtime ABI, public symbol naming, calling convention, target
  registration, or configuration fingerprint.
- Add custom compiler/linker flags not already required by TVM's standard
  `export_library` path.

### Never

- Modify the pinned `tvm/` checkout.
- Fall back from requested C host codegen to LLVM.
- Implement C support by text-translating LLVM IR or maintaining a separate VTA
  C template.
- Load FSIM/TSIM, run ResNet-8, or claim simulator correctness in this module.
- Weaken existing LLVM validation or skip malformed functions to reach codegen.

## Success Criteria

1. The modern Relay target hook deterministically routes VTA functions to the
   explicitly requested LLVM or C host, regardless of the environment-carried
   host on the initial lowered PrimFunc.
2. Native `TIRToRuntime` returns an LLVM module for LLVM host and a C source
   module for C host, each containing the complete requested symbol set.
3. A C-host partitioned QNN graph builds, exports, reloads, and exposes its VTA
   symbol without importing or initializing a simulator.
4. Both host paths preserve VTA runtime calls and execute `VTACheckConfig`
   before VTA activity.
5. Missing, unsupported, or inconsistent hosts fail before codegen with an
   actionable diagnostic.
6. Focused and aggregate tests pass with no tracked change in the pinned TVM
   checkout.

## Open Questions

None.

## Approval Gate

This specification requires explicit user approval before the next module
specification, `resnet8-fsim-matrix`, is written.
