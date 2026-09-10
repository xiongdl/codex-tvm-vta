# Spec: VTA TIRToRuntime

Module id: `vta-tir-to-runtime`

Status: Approved by the user on 2026-09-09

## Objective

Implement the `vta` TargetKind's modern `TIRToRuntime` hook. The hook accepts
all scheduled VTA PrimFuncs produced by `vta-relay-to-tir`, validates their
runtime boundary, and compiles them with the selected LLVM host code generator
into one standard TVM runtime module.

The generated host functions drive VTA through the existing VTA C runtime ABI.
For the first deployment, `libvta_fsim` implements that ABI and executes the
accelerator model on the host. The artifact must remain exportable and
reloadable through standard TVM module facilities and must not depend on the
legacy `relay.ext.vta` callback or Python compiler state after it is built.

## Public Contract

### TIRToRuntime hook

`libtvm-vta-ext` registers a typed `FTVMTIRToRuntime` callback on the `vta`
TargetKind. TVM invokes it with one IRModule containing all VTA PrimFuncs for a
target and the associated `Target("vta")`.

The hook must:

1. Reject non-PrimFunc entries, missing symbols, duplicate symbols, unexpected
   target attributes, or functions lacking the approved VTA runtime form.
2. Verify that every VTA PrimFunc has a unique deterministic `global_symbol`
   matching the Relay partition boundary.
3. Add or validate a hardware-configuration check before any VTA runtime command
   can be issued.
4. Compile the validated functions with the target's LLVM host code generator,
   not with a recursive call to public `tvm.build`.
5. Return one defined, DSO-exportable standard TVM LLVM runtime module that
   implements every expected VTA symbol.
6. Preserve standard TVM module import, serialization, export, and reload
   behavior without introducing a custom `runtime::ModuleNode`.

An empty VTA IRModule is invalid input to this hook. Relay graphs with no VTA
partitions never invoke it and compile entirely for LLVM.

### Generated host ABI

Each generated VTA function is a normal TVM packed-callable function with the
unpacked Relay region ABI established by `vta-relay-to-tir`. Its lowered body
uses VTA runtime calls such as buffer access, DMA, command queue, GEMM/ALU, and
synchronization operations defined by the existing VTA C runtime boundary.

The artifact contains host machine code, not a standalone VTA executable or an
instruction-blob file. At execution time, VTA C ABI calls are resolved from the
explicitly loaded VTA runtime implementation; for this initiative that
implementation is `libvta_fsim`.

The hook must not load FSIM, initialize a simulator, execute a VTA command, or
depend on `vta.testing.simulator`. Compilation and simulator execution remain
separate responsibilities.

### Configuration fingerprint ABI

Compiler and runtime configuration mismatch is a hard error. The canonical
fingerprint input is:

- the normalized, sorted VTA compile definitions emitted from
  `VTA_CONFIG_FILE` that affect instruction encoding, tensor blocking, integer
  widths, or memory/buffer interpretation; and
- an explicit VTA runtime-ABI/ISA schema version owned by VTA.

Presentation-only JSON formatting, source path, host target, and build timestamp
must not affect the fingerprint. Changing an ABI-relevant field or the schema
version must change it.

The generated artifact records the expected fingerprint as a constant and,
before the first VTA command in each entry function, invokes this stable runtime
boundary:

```c
int VTACheckConfig(uint64_t expected_fingerprint);
```

`libvta_fsim` compares the expected value with its own build-bound fingerprint.
A mismatch must report both values and fail before buffer allocation, command
recording, or accelerator activity. A match returns success. The check is safe
to repeat for multiple VTA entry functions and may be cached internally only
after a successful comparison.

This ABI does not select configurations and does not permit multiple active VTA
hardware configurations in one process.

### Runtime loading

`import vta` automatically loads only `libtvm-vta-ext` in a full TVM process.
An application that executes HOST FSIM explicitly loads it with:

```python
from vta.testing import simulator
```

This import must make `libvta_fsim` symbols globally available. A compile-only
process may build and export an artifact without loading FSIM.

## Tech Stack

- Repository-pinned TVM target-hook, TIR, LLVM codegen, runtime Module, module
  serializer, and export APIs.
- C++17 in `libtvm-vta-ext`.
- Existing VTA C runtime and FSIM implementation, extended only for the approved
  configuration-check ABI.
- Existing Python simulator loader and standard `ctypes.RTLD_GLOBAL` behavior.
- No custom runtime module type and no new third-party dependency.

## Commands

Build the compiler extension and FSIM through existing automation:

```bash
./scripts/build_vta_lib.sh --target libtvm-vta-ext
./scripts/build_vta_lib.sh --target libvta_fsim
```

Focused runtime validation follows the existing environment convention:

```bash
VTA_CONFIG_FILE="$PWD/vta/config/vta_config.json" \
PYTHONPATH="$PWD/tvm/python:$PWD/vta/python" \
  ./.envs/tvm-vta-env/bin/python -m pytest -q \
  vta/tests/python/unittest/test_byoc_codegen.py \
  vta/tests/python/unittest/test_byoc_runtime.py
```

The final initiative gate remains `./scripts/test_vta_byoc.sh` after later
modules migrate that existing script to the modern pipeline.

## Project Structure

```text
vta/src/compiler/
    Native TIRToRuntime validation, fingerprint insertion, and host-codegen
    dispatch compiled into libtvm-vta-ext.

vta/src/runtime/
    Stable VTA C runtime ABI, including VTACheckConfig.

vta/src/sim/
    FSIM implementation and diagnostics for configuration checking.

vta/python/vta/testing/simulator.py
    Explicit HOST FSIM dynamic-library loading and profiler access.

vta/tests/python/unittest/
    Hook validation, module-symbol, fingerprint, export/reload, and FSIM tests.
```

Exact compiler source filenames are a planning decision. Existing runtime ABI
headers remain the authoritative declarations for generated extern calls.

## Code Style

The hook validates before code generation and returns one conventional module:

```cpp
runtime::Module TIRToRuntime(IRModule mod, Target target) {
  ValidateVtaPrimFuncs(mod, target);
  IRModule checked = InjectVtaConfigChecks(mod, VtaAbiFingerprint());
  return BuildWithHostLLVM(checked, RequireLLVMHost(target));
}
```

The example is structural, not a commitment to helper names. Validation and
transformation must be separated, typed TVM APIs must be used, and failures must
identify the offending function or configuration. Do not hide errors behind
broad catches or fall back to another code generator.

## Testing Strategy

### Hook contract tests

- One and multiple valid VTA PrimFuncs produce one defined LLVM runtime module.
- The module implements every expected symbol exactly once.
- Invalid module contents, absent/duplicate symbols, wrong target, missing LLVM
  host, and malformed VTA runtime calls fail before host code generation.
- The hook does not recursively invoke public `tvm.build` and does not consult
  `relay.ext.vta`.
- No-VTA Relay graphs compile through LLVM without invoking this hook.

### Fingerprint tests

- Identical normalized ABI definitions produce the same fingerprint regardless
  of JSON formatting, ordering, path, or timestamp.
- Every ABI-relevant hardware definition and the schema version affects the
  fingerprint.
- Matching compiler-artifact and FSIM fingerprints allow execution.
- A deliberately mismatched FSIM fixture fails before profiler counters,
  allocations, or command activity and reports both fingerprints.
- Multiple VTA functions may repeat the successful check without changing
  results or runtime state.

### Artifact lifecycle tests

The mandatory integration path is:

```text
relay.build
  -> factory.export_library
  -> tvm.runtime.load_module
  -> GraphExecutor
  -> explicit libvta_fsim execution
```

Tests must prove:

- compilation and export can complete before FSIM is loaded;
- the reloaded artifact resolves the expected VTA symbols after FSIM is loaded;
- all VTA region symbols remain callable through the exported module;
- execution output is elementwise identical to the same quantized Relay module
  built for pure LLVM;
- FSIM GEMM, weight-load, and output-store counters show accelerator activity;
- execution does not require the compiler callback or Python lowering objects.

### Regression

- Existing standalone FSIM and VTA instruction tests remain green.
- Runtime-only imports do not load `libtvm-vta-ext`.
- The pinned TVM checkout remains clean.
- Python compilation and `git diff --check` pass.

## Boundaries

### Always

- Validate the entire VTA IRModule before generating a partial runtime module.
- Use the target's LLVM host for HOST FSIM artifacts.
- Emit and enforce the configuration fingerprint check before VTA activity.
- Return a standard exportable TVM LLVM module with deterministic symbols.
- Keep compiler-library loading separate from simulator loading.
- Preserve the existing VTA runtime calls unless this spec explicitly extends
  them.

### Ask first

- Add, remove, or change a public VTA C runtime function other than the approved
  `VTACheckConfig` addition.
- Generate a standalone instruction blob or introduce a custom runtime module.
- Permit fingerprint mismatch, multiple active configurations, or a non-LLVM
  host code generator.
- Change function calling convention, symbol ownership, constant ownership, or
  region boundary layouts.
- Automatically load FSIM from `import vta` or from the compiler hook.

### Never

- Recursively invoke public `tvm.build` from `TIRToRuntime`.
- Invoke or register `relay.ext.vta`.
- Depend on Python callbacks after the runtime artifact has been built.
- Execute VTA work during compilation.
- Continue after detecting a compiler/runtime configuration mismatch.
- Modify the pinned TVM source tree.

## Success Criteria

1. The registered hook converts all valid VTA PrimFuncs for one target into one
   standard LLVM runtime module implementing every deterministic region symbol.
2. The hook rejects malformed input before partial code generation and never
   recursively invokes `tvm.build` or the legacy external compiler callback.
3. Exporting and reloading a mixed `VTA + LLVM` artifact works through standard
   TVM APIs.
4. Explicitly loaded FSIM resolves the generated VTA C ABI and shows real VTA
   command activity during execution.
5. A canonical build-bound fingerprint is embedded in the artifact and checked
   against FSIM before any VTA activity; mismatch is an actionable hard error.
6. Reloaded mixed execution is elementwise identical to the pure-LLVM build of
   the same quantized Relay module.
7. Focused and regression tests pass with no change in the pinned TVM checkout.

## Dependencies And Deferred Work

- Depends on `vta-relay-to-tir` for validated, scheduled VTA PrimFuncs and on
  `vta-target-extension` for hook registration.
- Provides the artifact boundary required by `mlperf-resnet-host-deployment`.
- Model import, quantization orchestration, sample curation, full ResNet routing,
  and application packaging are outside this module.
- Custom runtime modules, standalone instruction blobs, AutoTVM, performance
  targets, FVP, CMSIS-NN, and physical-board drivers are out of scope.

## Open Questions

None.

## Approval Gate

The user must approve this spec before planning begins. Approval does not
authorize implementation.
